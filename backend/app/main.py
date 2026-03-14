from contextlib import asynccontextmanager
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import audit
from app.api import auth
from app.database import init_db

STATIC_DIR = Path(os.getenv("STATIC_DIR", "/app/static")).resolve()

DEFAULT_ALLOWED_ORIGINS = "https://auditor.nexora360.cloud"

# SECURITY NOTE: Esta API utiliza exclusivamente Bearer tokens para autenticação
# (via cabeçalho Authorization), não utilizando cookies de sessão para autenticação.
# Por essa razão, o risco de CSRF é baixo, pois ataques CSRF dependem do envio
# automático de cookies pelo browser. O uso de allow_credentials=True é necessário
# para suportar o cabeçalho Authorization em requisições cross-origin.
#
# IMPORTANTE: Caso no futuro cookies de autenticação sejam introduzidos, é mandatório
# implementar proteção CSRF via Double Submit Cookie pattern e configurar
# SameSite=Strict nos cookies de sessão para mitigar ataques CSRF.
#
# Decisão documentada em: [data de revisão de segurança]

def get_allowed_origins() -> list[str]:
    raw = os.environ.get("ALLOWED_ORIGINS", DEFAULT_ALLOWED_ORIGINS)
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def safe_static_file(filename: str) -> Path:
    resolved = (STATIC_DIR / filename).resolve()
    if not str(resolved).startswith(str(STATIC_DIR)):
        raise HTTPException(status_code=403, detail="Acesso negado.")
    if not resolved.exists() or not resolved.is_file():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
    return resolved


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not STATIC_DIR.exists() or not STATIC_DIR.is_dir():
        raise RuntimeError(
            f"STATIC_DIR '{STATIC_DIR}' does not exist or is not a directory. "
            "Set the STATIC_DIR environment variable to a valid path."
        )
    init_db()
    yield


app = FastAPI(title="AUDITX — Nexora Audit API", lifespan=lifespan)

# Origens permitidas são explicitamente configuradas via variável de ambiente.
# allow_credentials=True é necessário para suporte a Bearer tokens em requisições
# cross-origin. Cookies de autenticação NÃO são utilizados nesta API.
# Se cookies de autenticação forem introduzidos no futuro, implemente CSRF protection.
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
    expose_headers=["Content-Type"],
)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """
    Adiciona cabeçalhos de segurança em todas as respostas.
    X-Frame-Options e X-Content-Type-Options ajudam a mitigar ataques relacionados.
    """
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    # Garante que a API não seja usada em contextos não esperados
    response.headers["Content-Security-Policy"] = "default-src 'none'"
    return response


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(audit.router, prefix="/api", tags=["audit"])
app.include_router(auth.router, prefix="/api", tags=["auth"])


@app.get("/obrigado")
def obrigado():
    return FileResponse(safe_static_file("obrigado.html"))


@app.get("/erro")
def erro():
    return FileResponse(safe_static_file("erro.html"))


@app.get("/pendente")
def pendente():
    return FileResponse(safe_static_file("obrigado.html"))


if (STATIC_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(safe_static_file("assets"))), name="assets")


@app.get("/")
def landing():
    return FileResponse(safe_static_file("index.html"))