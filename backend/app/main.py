from fastapi import FastAPI

from app.api import audit

app = FastAPI(title="AUDITX — Nexora Audit API")


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(audit.router, prefix="/api", tags=["audit"])
