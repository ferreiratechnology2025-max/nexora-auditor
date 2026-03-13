from celery import Celery
import os

redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
celery_app = Celery("auditx", broker=redis_url, backend=redis_url)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="America/Sao_Paulo",
    enable_utc=True,
)


@celery_app.task(bind=True, max_retries=3, name="workers.tasks.run_scan")
def run_scan(self, scan_id: int, project_path: str):
    """Task assíncrona — executa scan sem travar a API."""
    import hashlib
    from datetime import datetime
    from app.audit_engine import AuditEngine
    from app.autofix_engine import AutoFixEngine
    from app.database import SessionLocal
    from app.models.scan import Scan, ScanStatus

    db = SessionLocal()
    try:
        scan = db.query(Scan).get(scan_id)
        if not scan:
            return {"error": f"Scan {scan_id} não encontrado"}

        scan.status = ScanStatus.processing
        db.commit()

        audit = AuditEngine().audit(project_path)
        fix = AutoFixEngine().fix(project_path, audit["findings"])

        report_hash = hashlib.sha256(f"{scan_id}{scan.email}".encode()).hexdigest()[:16]

        scan.status = ScanStatus.completed
        scan.health_score_initial = audit["health_score_initial"]
        scan.health_score_final = fix["health_score_final"]
        scan.findings_json = audit["findings"]
        scan.report_hash = report_hash
        scan.completed_at = datetime.utcnow()
        db.commit()

        return {"scan_id": scan_id, "status": "completed", "score": audit["health_score_initial"]}

    except Exception as exc:
        if db:
            scan = db.query(Scan).get(scan_id)
            if scan:
                scan.status = ScanStatus.failed
                db.commit()
        db.close()
        raise self.retry(exc=exc, countdown=60)
    finally:
        db.close()
