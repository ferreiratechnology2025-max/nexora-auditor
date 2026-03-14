import io
import re
import shutil
import subprocess
import tempfile
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel, EmailStr
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.audit_engine import AuditEngine
from app.autofix_engine import AutoFixEngine
from app.reports import ReportGenerator
from app.email_service import EmailService

router = APIRouter()

limiter = Limiter(key_func=get_remote_address)

_store: dict[str, dict[str, Any]] = {}

_audit_engine = AuditEngine()
_fix_engine   = AutoFixEngine()
_reports      = ReportGenerator()

_REPO_URL_RE = re.compile(
    r'^https?://(github\.com|gitlab\.com|bitbucket\.org)/[\w.\-]+/[\w.\-]+(\.git)?/?$'
)

_IP_UPLOAD_SIZE_TRACKER: dict[str, dict[str, Any]] = {}
_MAX_UPLOAD_SIZE_PER_IP_PER_HOUR = 500 * 1024 * 1024  # 500MB por IP por hora
_MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB por arquivo


class GithubRequest(BaseModel):
    repo_url: str


class SendReportRequest(BaseModel):
    email:       str
    report_type: str = "security"


def _new_audit_id() -> str:
    return str(uuid.uuid4())


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_ip_upload_total(ip: str) -> int:
    now = datetime.now(timezone.utc)
    if ip not in _IP_UPLOAD_SIZE_TRACKER:
        return 0
    tracker = _IP_UPLOAD_SIZE_TRACKER[ip]
    window_start = tracker.get("window_start")
    if window_start is None:
        return 0
    elapsed = (now - window_start).total_seconds()
    if elapsed > 3600:
        _IP_UPLOAD_SIZE_TRACKER[ip] = {"total": 0, "window_start": now}
        return 0
    return tracker.get("total", 0)


def _record_ip_upload_size(ip: str, size: int) -> None:
    now = datetime.now(timezone.utc)
    if ip not in _IP_UPLOAD_SIZE_TRACKER:
        _IP_UPLOAD_SIZE_TRACKER[ip] = {"total": 0, "window_start": now}
    tracker = _IP_UPLOAD_SIZE_TRACKER[ip]
    window_start = tracker.get("window_start")
    if window_start is None or (now - window_start).total_seconds() > 3600:
        _IP_UPLOAD_SIZE_TRACKER[ip] = {"total": size, "window_start": now}
    else:
        _IP_UPLOAD_SIZE_TRACKER[ip]["total"] = tracker.get("total", 0) + size


def _run_full_pipeline(project_path: str, source_name: str) -> dict[str, Any]:
    audit_result = _audit_engine.audit(project_path)
    fix_result   = _fix_engine.fix(project_path, audit_result["findings"])

    audit_id = _new_audit_id()
    record = {
        "audit_id":             audit_id,
        "project":              source_name,
        "date":                 _utcnow(),
        "status":               "completed",
        "health_score_initial": audit_result["health_score_initial"],
        "health_score_final":   fix_result["health_score_final"],
        "findings":             audit_result["findings"],
        "total_findings":       audit_result["total"],
        "by_severity":          audit_result["by_severity"],
        "fixed":                fix_result["fixed"],
        "skipped":              fix_result["skipped"],
        "patch_summary":        fix_result["patch_summary"],
        "languages_detected":   audit_result["languages_detected"],
        "files_scanned":        audit_result["files_scanned"],
        "project_path":         project_path,
    }
    _store[audit_id] = record
    return record


def _get_or_404(audit_id: str) -> dict[str, Any]:
    record = _store.get(audit_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Auditoria '{audit_id}' não encontrada.",
        )
    return record


def _zip_directory(root: Path) -> io.BytesIO:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(root.rglob("*")):
            if file_path.is_file():
                zf.write(file_path, file_path.relative_to(root))
    buf.seek(0)
    return buf


def _validate_zip_contents(zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            member_path = Path(member.filename)
            parts = member_path.parts
            for part in parts:
                if part == "..":
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="ZIP contém caminhos inválidos (path traversal detectado).",
                    )
            if member.file_size > _MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Arquivo '{member.filename}' excede o tamanho máximo permitido de 50MB.",
                )


@router.post(
    "/audit/zip",
    summary="Audita e corrige um projeto enviado como arquivo ZIP",
    status_code=status.HTTP_200_OK,
)
@limiter.limit("10/hour")
async def audit_zip(request: Request, file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Apenas arquivos .zip são aceitos.",
        )

    client_ip = get_remote_address(request)

    file_bytes = await file.read()
    file_size = len(file_bytes)

    if file_size > _MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Arquivo excede o tamanho máximo permitido de 50MB.",
        )

    current_ip_total = _get_ip_upload_total(client_ip)
    if current_ip_total + file_size > _MAX_UPLOAD_SIZE_PER_IP_PER_HOUR:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Limite de upload por hora excedido para este IP. Tente novamente mais tarde.",
        )

    tmp_dir = tempfile.mkdtemp(prefix="auditx_zip_")
    try:
        zip_path = Path(tmp_dir) / "upload.zip"
        zip_path.write_bytes(file_bytes)

        try:
            _validate_zip_contents(zip_path)
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(tmp_dir)
            zip_path.unlink()
        except HTTPException:
            raise
        except zipfile.BadZipFile:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Arquivo ZIP inválido ou corrompido.",
            )
        except RuntimeError as exc:
            msg = str(exc).lower()
            if "password" in msg or "encrypted" in msg:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="ZIPs protegidos por senha não são suportados.",
                )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Erro ao extrair ZIP: {exc}",
            )

        _record_ip_upload_size(client_ip, file_size)

        record = _run_full_pipeline(tmp_dir, file.filename)
        return record

    except HTTPException:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise
    except Exception as exc:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno durante auditoria: {exc}",
        )


@router.post(
    "/audit/github",
    summary="Audita e corrige um repositório GitHub/GitLab/Bitbucket",
    status_code=status.HTTP_200_OK,
)
@limiter.limit("10/hour")
async def audit_github(request: Request, body: GithubRequest):
    if not _REPO_URL_RE.match(body.repo_url):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="URL de repositório inválida. Apenas GitHub, GitLab e Bitbucket são suportados.",
        )

    tmp_dir = tempfile.mkdtemp(prefix="auditx_git_")
    try:
        result = subprocess.run(
            ["git", "clone", "--depth", "1", body.repo_url, tmp_dir],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Falha ao clonar repositório: {result.stderr.strip()}",
            )

        record = _run_full_pipeline(tmp_dir, body.repo_url)
        return record

    except HTTPException:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise
    except subprocess.TimeoutExpired:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="Timeout ao clonar repositório.",
        )
    except Exception as exc:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno durante auditoria: {exc}",
        )


@router.get(
    "/audit/{audit_id}",
    summary="Retorna resultado completo de uma auditoria",
    status_code=status.HTTP_200_OK,
)
async def get_audit(audit_id: str):
    return _get_or_404(audit_id)


@router.get(
    "/audit/{audit_id}/report",
    summary="Laudo JSON com score inicial vs final",
    status_code=status.HTTP_200_OK,
)
async def get_report(audit_id: str):
    record = _get_or_404(audit_id)
    return {
        "audit_id":             record["audit_id"],
        "project":              record["project"],
        "date":                 record["date"],
        "health_score_initial": record["health_score_initial"],
        "health_score_final":   record["health_score_final"],
        "total_findings":       record["total_findings"],
        "by_severity":          record["by_severity"],
        "fixed":                record["fixed"],
        "skipped":              record["skipped"],
    }


@router.get(
    "/audit/{audit_id}/report/security",
    summary="Laudo de Segurança em HTML",
    status_code=status.HTTP_200_OK,
)
async def get_report_security(audit_id: str):
    record = _get_or_404(audit_id)
    html = _reports.security_html(record)
    return Response(content=html, media_type="text/html")


@router.get(
    "/audit/{audit_id}/report/performance",
    summary="Laudo de Performance em HTML",
    status_code=status.HTTP_200_OK,
)
async def get_report_performance(audit_id: str):
    record = _get_or_404(audit_id)
    html = _reports.performance_html(record)
    return Response(content=html, media_type="text/html")


@router.get(
    "/audit/{audit_id}/report/certificate",
    summary="Certificado de Qualidade em HTML",
    status_code=status.HTTP_200_OK,
)
async def get_report_certificate(audit_id: str):
    record = _get_or_404(audit_id)
    html = _reports.certificate_html(record)
    return Response(content=html, media_type="text/html")


@router.get(
    "/audit/{audit_id}/download",
    summary="Download do projeto corrigido como ZIP",
    status_code=status.HTTP_200_OK,
)
async def download_fixed(audit_id: str, background_tasks: BackgroundTasks):
    record = _get_or_404(audit_id)
    project_path = record.get("project_path")

    if not project_path or not Path(project_path).exists():
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Arquivos do projeto não estão mais disponíveis.",
        )

    buf = _zip_directory(Path(project_path))
    background_tasks.add_task(shutil.rmtree, project_path, True)

    filename = f"auditx_fixed_{audit_id[:8]}.zip"
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post(
    "/audit/{audit_id}/send-report",
    summary="Envia laudo por email",
    status_code=status.HTTP_200_OK,
)
@limiter.limit("5/hour")
async def send_report(request: Request, audit_id: str, body: SendReportRequest):
    record = _get_or_404(audit_id)

    valid_types = {"security", "performance", "certificate"}
    if body.report_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"report_type inválido. Use: {', '.join(valid_types)}",
        )

    try:
        email_service = EmailService()
        email_service.send_report(
            to=body.email,
            report_type=body.report_type,
            record=record,
            reports=_reports,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao enviar email: {exc}",
        )

    return {"message": f"Laudo enviado para {body.email} com sucesso."}