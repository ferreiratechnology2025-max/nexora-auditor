from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

ALGORITHM = 'HS256'
DEFAULT_EXPIRE_MINUTES = 60


class AuthError(Exception):
    """Erro de autenticação para falhas de validação/login/token."""


def hash_password(password: str) -> str:
    if not password or not isinstance(password, str):
        raise ValueError('password obrigatória.')
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str,
    secret_key: str,
    expires_minutes: int = DEFAULT_EXPIRE_MINUTES,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    if not subject:
        raise ValueError('subject obrigatório para gerar token.')
    if not secret_key:
        raise ValueError('secret_key obrigatória para gerar token.')

    now = datetime.now(timezone.utc)
    payload: Dict[str, Any] = {
        'sub': subject,
        'iat': int(now.timestamp()),
        'exp': int((now + timedelta(minutes=expires_minutes)).timestamp()),
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str, secret_key: str) -> Dict[str, Any]:
    if not token:
        raise AuthError('token não informado.')
    if not secret_key:
        raise AuthError('secret_key não informada.')

    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise AuthError(f'token inválido: {exc}') from exc

    if not payload.get('sub'):
        raise AuthError('token sem subject (sub).')

    return payload


def authenticate_user(user_record: Optional[Dict[str, Any]], password: str) -> bool:
    """Valida se o registro de usuário existe e se a senha confere."""
    if not user_record:
        return False

    password_hash = user_record.get('password_hash')
    return verify_password(password, password_hash)


def login_user(
    user_record: Optional[Dict[str, Any]],
    password: str,
    secret_key: str,
    expires_minutes: int = DEFAULT_EXPIRE_MINUTES,
) -> str:
    """Executa fluxo de login e retorna JWT quando credenciais são válidas."""
    if not authenticate_user(user_record, password):
        raise AuthError('credenciais inválidas.')

    username = user_record.get('username') or user_record.get('email')
    if not username:
        raise AuthError('usuário sem identificador para emissão de token.')

    return create_access_token(
        subject=str(username),
        secret_key=secret_key,
        expires_minutes=expires_minutes,
        extra_claims={'role': user_record.get('role', 'user')},
    )
