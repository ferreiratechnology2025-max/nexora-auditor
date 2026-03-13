from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import audit
from app.api import auth
from app.database import init_db

STATIC_DIR = Path(__file__).parent.parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="AUDITX — Nexora Audit API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(audit.router, prefix="/api", tags=["audit"])
app.include_router(auth.router, prefix="/api", tags=["auth"])


@app.get("/obrigado")
def obrigado():
    return FileResponse(STATIC_DIR / "obrigado.html")


@app.get("/erro")
def erro():
    return FileResponse(STATIC_DIR / "erro.html")


@app.get("/pendente")
def pendente():
    return FileResponse(STATIC_DIR / "obrigado.html")


if (STATIC_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(STATIC_DIR / "assets")), name="assets")


@app.get("/")
def landing():
    return FileResponse(STATIC_DIR / "index.html")
