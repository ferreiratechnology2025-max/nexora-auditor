from celery import Celery
import os
import re
from pathlib import Path

redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
celery_app = Celery("auditx", broker=redis_url, backend=redis_url)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="America/Sao_Paulo",
    enable_utc=True,
)

ALLOWED_BASE_DIR = Path(os.getenv("AUDITX_UPLOADS_DIR", "/tmp/auditx/uploads")).resolve()

SHELL_SPECIAL_CHARS_PATTERN = re.compile(r'[;|&$`\\<>!\'"()\[\]{}*?~#]')


def validate_project_path(project_path: str) -> Path:
    """
    Valida que project_path está dentro do diretório base permitido.
    Lança ValueError se o caminho tentar escapar do diretório de uploads
    ou contiver caracteres especiais de shell.
    """
    try:
        if SHELL_SPECIAL_CHARS_PATTERN.search(project_path):
            raise ValueError(
                f"Caminho inválido: '{project_path}' contém caracteres especiais de shell não permitidos."
            )

        base = ALLOWED_BASE_DIR
        path = Path(project_path).resolve()

        try:
            path.relative_to(base)
        except ValueError:
            raise ValueError(
                f"Caminho inválido: '{project_path}' está fora do diretório permitido."
            )

        if not path.exists():
            raise ValueError(f"Caminho não existe: '{project_path}'")

        return path
    except (TypeError, ValueError) as e:
        raise ValueError(f"project_path inválido: {e}") from e


def safe_path_to_str(path: Path) -> str:
    """
    Converte Path para string e valida novamente a ausência de caracteres especiais.
    Garante que o caminho final passado para engines externos seja seguro.
    """
    path_str = str(path)
    if SHELL_SPECIAL_CHARS_PATTERN.search(path_str):
        raise ValueError(
            f"Caminho resolvido contém caracteres especiais de shell: '{path_str}'"
        )
    return path_str


@celery_app.task(bind=True, max_retries=3, name="workers.tasks.run_scan")
def run_scan(self, scan_id: int, project_path: str):
    """Task assíncrona — executa scan sem travar a API."""
    import hashlib
    import secrets
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

        try:
            safe_path = validate_project_path(project_path)
            safe_path_str = safe_path_to_str(safe_path)
        except ValueError as e:
            scan.status = ScanStatus.failed
            db.commit()
            return {"error": str(e), "scan_id": scan_id}

        audit = AuditEngine().audit(safe_path_str)
        fix = AutoFixEngine().fix(safe_path_str, audit["findings"])

        salt = secrets.token_hex(16)
        report_hash = hashlib.sha256(f"{scan_id}{scan.email}{salt}".encode()).hexdigest()[:32]

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