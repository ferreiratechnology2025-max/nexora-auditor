"""
audit.py — Router FastAPI para o motor de auditoria AUDITX
============================================================
Fluxo completo: ingestão → análise estática → auto-correção → laudo → download

Endpoints:
  POST /api/audit/zip                      — upload de ZIP
  POST /api/audit/github                   — clone de repositório GitHub
  GET  /api/audit/{id}                     — resultado completo
  GET  /api/audit/{id}/report              — laudo JSON (score inicial vs final)
  GET  /api/audit/{id}/report/security     — HTML: Laudo de Segurança
  GET  /api/audit/{id}/report/performance  — HTML: Laudo de Performance
  GET  /api/audit/{id}/report/certificate  — HTML: Certificado de Qualidade
  GET  /api/audit/{id}/download            — ZIP com projeto corrigido
  POST /api/audit/{id}/send-report         — envia laudo por email

Ciclo de vida do diretório temporário:
  • Criado em ingestão (mkdtemp)
  • Mantido vivo após sucesso (project_path guardado em _store)
  • Deletado por BackgroundTask após streaming do /download
  • Deletado imediatamente em caso de erro (bloco except)
"""

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

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile, status
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel, EmailStr

from app.audit_engine import AuditEngine
from app.autofix_engine import AutoFixEngine
from app.reports import ReportGenerator
from app.email_service import EmailService

router = APIRouter()

# Storage em memória — substituível por SQLAlchemy quando DB estiver configurado
_store: dict[str, dict[str, Any]] = {}

_audit_engine = AuditEngine()
_fix_engine   = AutoFixEngine()
_reports      = ReportGenerator()

_REPO_URL_RE = re.compile(
    r'^https?://(github\.com|gitlab\.com|bitbucket\.org)/[\w.\-]+/[\w.\-]+(\.git)?/?$'
)


# =============================================================================
# SCHEMAS
# =============================================================================

class GithubRequest(BaseModel):
    repo_url: str


class SendReportRequest(BaseModel):
    email:       str
    report_type: str = "security"   # security | performance | certificate


# =============================================================================
# HELPERS
# =============================================================================

def _new_audit_id() -> str:
    return str(uuid.uuid4())


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run_full_pipeline(project_path: str, source_name: str) -> dict[str, Any]:
    """Executa audit + autofix e salva resultado em _store. Não apaga project_path."""
    audit_result = _audit_engine.audit(project_path)
    fix_result   = _fix_engine.fix(project_path, audit_result["findings"])

    audit_id = _new_audit_id()
    record = {
        "audit_id":             audit_id,
        "project":              source_name,
        "date":                 _utcnow(),
        "status":               "completed",
        # scores
        "health_score_initial": audit_result["health_score_initial"],
        "health_score_final":   fix_result["health_score_final"],
        # findings originais
        "findings":             audit_result["findings"],
        "total_findings":       audit_result["total"],
        "by_severity":          audit_result["by_severity"],
        # correções
        "fixed":                fix_result["fixed"],
        "skipped":              fix_result["skipped"],
        "patch_summary":        fix_result["patch_summary"],
        # metadados
        "languages_detected":   audit_result["languages_detected"],
        "files_scanned":        audit_result["files_scanned"],
        # path mantido para /download — apagado após streaming
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
    """Compacta root recursivamente em um BytesIO ZIP."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(root.rglob("*")):
            if file_path.is_file():
                zf.write(file_path, file_path.relative_to(root))
    buf.seek(0)
    return buf


# =============================================================================
# ENDPOINTS — INGESTÃO
# =============================================================================

@router.post(
    "/audit/zip",
    summary="Audita e corrige um projeto enviado como arquivo ZIP",
    status_code=status.HTTP_200_OK,
)
async def audit_zip(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Apenas arquivos .zip são aceitos.",
        )

    tmp_dir = tempfile.mkdtemp(prefix="auditx_zip_")
    try:
        zip_path = Path(tmp_dir) / "upload.zip"
        zip_path.write_bytes(await file.read())

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(tmp_dir)
            zip_path.unlink()
        except zipfile.BadZipFile:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Arquivo ZIP inválido ou corrompido.",
            )

        record = _run_full_pipeline(tmp_dir, file.filename)

    except HTTPException:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise
    except Exception as exc:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno durante a auditoria: {exc}",
        ) from exc
    # Sem finally — tmp_dir é mantido vivo para /download

    return {
        "audit_id":             record["audit_id"],
        "status":               record["status"],
        "health_score_initial": record["health_score_initial"],
        "health_score_final":   record["health_score_final"],
        "total_findings":       record["total_findings"],
        "by_severity":          record["by_severity"],
        "fixed_count":          len(record["fixed"]),
        "skipped_count":        len(record["skipped"]),
        "languages_detected":   record["languages_detected"],
        "files_scanned":        record["files_scanned"],
        "findings":             record["findings"],
    }


@router.post(
    "/audit/github",
    summary="Audita e corrige um repositório GitHub",
    status_code=status.HTTP_200_OK,
)
async def audit_github(body: GithubRequest):
    if not _REPO_URL_RE.match(body.repo_url):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="repo_url deve ser uma URL válida de GitHub, GitLab ou Bitbucket.",
        )

    tmp_dir = tempfile.mkdtemp(prefix="auditx_git_")
    try:
        clone = subprocess.run(
            ["git", "clone", "--depth", "1", body.repo_url, tmp_dir],
            capture_output=True, text=True, timeout=30,
        )
        if clone.returncode != 0:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Falha ao clonar repositório: {clone.stderr[:300]}",
            )

        project_name = body.repo_url.rstrip("/").split("/")[-1].removesuffix(".git")
        record = _run_full_pipeline(tmp_dir, project_name)

    except subprocess.TimeoutExpired:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Timeout ao clonar o repositório (limite: 30s).",
        )
    except HTTPException:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise
    except Exception as exc:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno durante a auditoria: {exc}",
        ) from exc

    return {
        "audit_id":             record["audit_id"],
        "project":              record["project"],
        "status":               record["status"],
        "health_score_initial": record["health_score_initial"],
        "health_score_final":   record["health_score_final"],
        "total_findings":       record["total_findings"],
        "by_severity":          record["by_severity"],
        "fixed_count":          len(record["fixed"]),
        "skipped_count":        len(record["skipped"]),
        "languages_detected":   record["languages_detected"],
        "files_scanned":        record["files_scanned"],
        "findings":             record["findings"],
    }


# =============================================================================
# ENDPOINTS — CONSULTA
# =============================================================================

@router.get(
    "/audit/{audit_id}",
    summary="Resultado completo de uma auditoria salva",
    status_code=status.HTTP_200_OK,
)
async def get_audit(audit_id: str):
    record = _get_or_404(audit_id)
    # Não expõe project_path internamente
    return {k: v for k, v in record.items() if k != "project_path"}


@router.get(
    "/audit/{audit_id}/report",
    summary="Laudo formatado com score inicial vs final e diffs",
    status_code=status.HTTP_200_OK,
)
async def get_report(audit_id: str):
    r = _get_or_404(audit_id)
    score_delta = r["health_score_final"] - r["health_score_initial"]
    return {
        "audit_id":             r["audit_id"],
        "project":              r["project"],
        "date":                 r["date"],
        "status":               r["status"],
        # scores
        "health_score_initial": r["health_score_initial"],
        "health_score_final":   r["health_score_final"],
        "score_improvement":    score_delta,
        # findings
        "total_findings":       r["total_findings"],
        "by_severity":          r["by_severity"],
        "findings":             r["findings"],
        # correções
        "fixed":                r["fixed"],
        "skipped":              r["skipped"],
        "patch_summary":        r["patch_summary"],
        # metadados
        "languages_detected":   r["languages_detected"],
        "files_scanned":        r["files_scanned"],
    }


# =============================================================================
# ENDPOINTS — DOWNLOAD
# =============================================================================

@router.get(
    "/audit/{audit_id}/download",
    summary="Baixa o projeto corrigido como ZIP",
)
async def download_fixed(audit_id: str, background_tasks: BackgroundTasks):
    record = _get_or_404(audit_id)

    project_path = record.get("project_path")
    if not project_path or not Path(project_path).exists():
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Projeto corrigido não está mais disponível. Reenvie o arquivo para uma nova auditoria.",
        )

    try:
        buf = _zip_directory(Path(project_path))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao compactar projeto: {exc}",
        ) from exc

    # Apaga project_path e remove referência do store após streaming
    background_tasks.add_task(shutil.rmtree, project_path, True)
    record.pop("project_path", None)

    filename = f"auditx_{audit_id[:8]}_fixed.zip"
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# =============================================================================
# ENDPOINTS — LAUDOS HTML
# =============================================================================

def _html_report(audit_id: str, kind: str) -> Response:
    record = _get_or_404(audit_id)
    gen = {"security": _reports.security,
           "performance": _reports.performance,
           "certificate": _reports.certificate}.get(kind)
    if gen is None:
        raise HTTPException(status_code=404,
                            detail=f"Tipo de laudo '{kind}' inválido.")
    html = gen(record)
    return Response(content=html, media_type="text/html; charset=utf-8")


@router.get("/audit/{audit_id}/report/security",
            summary="Laudo HTML de Segurança (Blindagem)")
async def report_security(audit_id: str):
    return _html_report(audit_id, "security")


@router.get("/audit/{audit_id}/report/performance",
            summary="Laudo HTML de Performance (Eficiência)")
async def report_performance(audit_id: str):
    return _html_report(audit_id, "performance")


@router.get("/audit/{audit_id}/report/certificate",
            summary="Certificado HTML de Qualidade")
async def report_certificate(audit_id: str):
    return _html_report(audit_id, "certificate")


# =============================================================================
# ENDPOINTS — ENVIO POR EMAIL
# =============================================================================

@router.post("/audit/{audit_id}/send-report",
             summary="Envia laudo por email (SMTP Hostinger)")
async def send_report(audit_id: str, body: SendReportRequest):
    record = _get_or_404(audit_id)

    if body.report_type not in ("security", "performance", "certificate"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="report_type deve ser: security | performance | certificate",
        )

    gen = {"security": _reports.security,
           "performance": _reports.performance,
           "certificate": _reports.certificate}[body.report_type]
    html_report = gen(record)

    # Monta bullets com resumo dos achados
    n_crit = record.get("by_severity", {}).get("CRITICAL", 0)
    n_high = record.get("by_severity", {}).get("HIGH", 0)
    n_fixed = len(record.get("fixed", []))
    bullets = (
        f"• {record.get('total_findings', 0)} vulnerabilidade(s) detectada(s) "
        f"({n_crit} crítica(s), {n_high} alta(s)).<br/>"
        f"• {n_fixed} correção(ões) aplicada(s) automaticamente.<br/>"
        f"• Score: {record.get('health_score_initial',0)} → "
        f"{record.get('health_score_final',0)} "
        f"(+{record.get('health_score_final',0) - record.get('health_score_initial',0)})."
    )

    try:
        svc = EmailService()
        svc.send_report(
            to_email=body.email,
            audit_id=audit_id,
            score_initial=record.get("health_score_initial", 0),
            score_final=record.get("health_score_final", 0),
            report_type=body.report_type,
            html_report=html_report,
            project_name=record.get("project", "Projeto"),
            findings_summary=bullets,
        )
        return {"sent": True, "to": body.email, "report_type": body.report_type}
    except (ValueError, RuntimeError) as exc:
        return {"sent": False, "error": str(exc)}
