"""
Gene Auth JWT - Lógica de criptografia e geração de tokens.
Reutilizável pelo orquestrador para evitar geração repetitiva (economia de tokens).
"""
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

try:
    import jwt
except ImportError:
    jwt = None  # type: ignore

DEFAULT_ALGORITHM = "HS256"
DEFAULT_EXP_HOURS = 24
SALT_ENV = "NEXORA_AUTH_SALT"


def _get_secret() -> str:
    """Obtém secret para assinatura; em produção usar variável de ambiente."""
    return os.environ.get("JWT_SECRET", "nexora-dev-secret-change-in-production")


def hash_password(password: str, salt: Optional[str] = None) -> str:
    """Gera hash do password com salt (SHA-256)."""
    s = salt or os.environ.get(SALT_ENV, "nexora-default-salt")
    return hashlib.sha256(f"{s}{password}".encode()).hexdigest()


def verify_password(password: str, hashed: str, salt: Optional[str] = None) -> bool:
    """Verifica se o password confere com o hash armazenado."""
    return hmac.compare_digest(hash_password(password, salt), hashed)


def create_token(
    payload: dict[str, Any],
    secret: Optional[str] = None,
    exp_hours: float = DEFAULT_EXP_HOURS,
    algorithm: str = DEFAULT_ALGORITHM,
) -> str:
    """Gera JWT com expiração. payload não deve conter 'exp' (será sobrescrito)."""
    if jwt is None:
        raise RuntimeError("PyJWT não instalado. Execute: pip install pyjwt")
    secret = secret or _get_secret()
    now = datetime.now(timezone.utc)
    data = {**payload, "iat": now, "exp": now + timedelta(hours=exp_hours)}
    return jwt.encode(data, secret, algorithm=algorithm)


def verify_token(
    token: str,
    secret: Optional[str] = None,
    algorithm: str = DEFAULT_ALGORITHM,
) -> dict[str, Any]:
    """Valida JWT e retorna o payload. Levanta exceção se inválido ou expirado."""
    if jwt is None:
        raise RuntimeError("PyJWT não instalado. Execute: pip install pyjwt")
    secret = secret or _get_secret()
    return jwt.decode(token, secret, algorithms=[algorithm])

