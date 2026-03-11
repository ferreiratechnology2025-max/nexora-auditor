from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import audit

STATIC_DIR = Path(__file__).parent.parent.parent / "static"

app = FastAPI(title="AUDITX — Nexora Audit API")


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(audit.router, prefix="/api", tags=["audit"])

# Páginas de retorno do pagamento
@app.get("/obrigado")
def obrigado():
    return FileResponse(STATIC_DIR / "obrigado.html")


@app.get("/erro")
def erro():
    return FileResponse(STATIC_DIR / "erro.html")


@app.get("/pendente")
def pendente():
    return FileResponse(STATIC_DIR / "obrigado.html")


# Arquivos estáticos (CSS, JS, imagens se houver)
if (STATIC_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(STATIC_DIR / "assets")), name="assets")


# Landing Page na raiz — deve vir por último
@app.get("/")
def landing():
    return FileResponse(STATIC_DIR / "index.html")
