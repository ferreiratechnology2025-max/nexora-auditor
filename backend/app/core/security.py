from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.database import get_db
import os
import redis
import uuid
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

def _load_private_key():
    key_path = os.getenv("JWT_PRIVATE_KEY_PATH")
    key_pem = os.getenv("JWT_PRIVATE_KEY")
    if key_path:
        with open(key_path, "rb") as f:
            return f.read().decode("utf-8")
    elif key_pem:
        return key_pem.replace("\\n", "\n")
    else:
        raise RuntimeError(
            "JWT_PRIVATE_KEY ou JWT_PRIVATE_KEY_PATH não configurado. "
            "Gere um par de chaves RSA: openssl genrsa -out private.pem 2048"
        )

def _load_public_key():
    key_path = os.getenv("JWT_PUBLIC_KEY_PATH")
    key_pem = os.getenv("JWT_PUBLIC_KEY")
    if key_path:
        with open(key_path, "rb") as f:
            return f.read().decode("utf-8")
    elif key_pem:
        return key_pem.replace("\\n", "\n")
    else:
        raise RuntimeError(
            "JWT_PUBLIC_KEY ou JWT_PUBLIC_KEY_PATH não configurado. "
            "Derive a chave pública: openssl rsa -in private.pem -pubout -out public.pem"
        )

PRIVATE_KEY = _load_private_key()
PUBLIC_KEY = _load_public_key()

KEY_ID = os.getenv("JWT_KEY_ID", "v1")

ALGORITHM = "RS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

TOKEN_ISSUER = "auditx"
TOKEN_AUDIENCE = "auditx-api"

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
except Exception as e:
    raise RuntimeError(f"Falha ao conectar ao Redis: {e}. Redis é obrigatório para gerenciamento de tokens.")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer(auto_error=False)

AUTH_RATE_LIMIT = "5/minute"
REFRESH_RATE_LIMIT = "5/minute"
LOGOUT_RATE_LIMIT = "10/minute"
REGISTER_RATE_LIMIT = "3/minute"


def _check_rate_limit(request: Request, key_prefix: str, limit: int, window: int) -> None:
    """
    Aplica rate limiting manual usando Redis para operações de autenticação.
    
    :param request: objeto Request do FastAPI
    :param key_prefix: prefixo para a chave Redis
    :param limit: número máximo de requisições permitidas
    :param window: janela de tempo em segundos
    """
    client_ip = get_remote_address(request)
    redis_key = f"rate_limit:{key_prefix}:{client_ip}"
    
    try:
        pipe = redis_client.pipeline()
        pipe.incr(redis_key)
        pipe.expire(redis_key, window)
        results = pipe.execute()
        current_count = results[0]
    except redis.RedisError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço temporariamente indisponível"
        )
    
    if current_count > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Muitas requisições. Tente novamente em {window} segundos.",
            headers={"Retry-After": str(window)}
        )


def apply_auth_rate_limit(request: Request) -> None:
    _check_rate_limit(request, "auth_login", limit=5, window=60)


def apply_register_rate_limit(request: Request) -> None:
    _check_rate_limit(request, "auth_register", limit=3, window=60)


def apply_refresh_rate_limit(request: Request) -> None:
    _check_rate_limit(request, "auth_refresh", limit=5, window=60)


def apply_logout_rate_limit(request: Request) -> None:
    _check_rate_limit(request, "auth_logout", limit=10, window=60)


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _make_headers() -> dict:
    return {"kid": KEY_ID}


def create_access_token(user_id: int) -> str:
    jti = str(uuid.uuid4())
    exp = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "exp": exp,
        "jti": jti,
        "type": "access",
        "iss": TOKEN_ISSUER,
        "aud": TOKEN_AUDIENCE
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm=ALGORITHM, headers=_make_headers())


def create_refresh_token(user_id: int) -> str:
    jti = str(uuid.uuid4())
    exp = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "exp": exp,
        "jti": jti,
        "type": "refresh",
        "iss": TOKEN_ISSUER,
        "aud": TOKEN_AUDIENCE
    }
    token = jwt.encode(payload, PRIVATE_KEY, algorithm=ALGORITHM, headers=_make_headers())
    try:
        redis_client.setex(
            f"refresh_token:{user_id}:{jti}",
            timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            "valid"
        )
    except redis.RedisError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço temporariamente indisponível"
        )
    return token


def _decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        PUBLIC_KEY,
        algorithms=[ALGORITHM],
        audience=TOKEN_AUDIENCE,
        issuer=TOKEN_ISSUER
    )


def revoke_token(token: str) -> None:
    try:
        payload = _decode_token(token)
        jti = payload.get("jti")
        exp = payload.get("exp")
        token_type = payload.get("type", "access")
        user_id = payload.get("sub")

        if not jti or not exp:
            return

        expire_at = datetime.fromtimestamp(exp, tz=timezone.utc)
        ttl = expire_at - datetime.now(timezone.utc)

        if ttl.total_seconds() > 0:
            try:
                redis_client.setex(
                    f"blacklist:{jti}",
                    ttl,
                    "revoked"
                )
            except redis.RedisError:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Serviço temporariamente indisponível"
                )

        if token_type == "refresh" and user_id:
            try:
                redis_client.delete(f"refresh_token:{user_id}:{jti}")
            except redis.RedisError:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Serviço temporariamente indisponível"
                )

    except JWTError:
        pass


def is_token_revoked(jti: str) -> bool:
    try:
        is_blacklisted = redis_client.exists(f"blacklist:{jti}")
        return bool(is_blacklisted)
    except redis.RedisError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço temporariamente indisponível"
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db)
):
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais não fornecidas",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials

    try:
        payload = _decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )

    jti = payload.get("jti")
    token_type = payload.get("type")

    if not jti or token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if is_token_revoked(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revogado",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"}
        )

    from app.models import User
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user