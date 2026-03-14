from fastapi import APIRouter, HTTPException, Depends, Request, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.database import get_db
from app.models.user import User, PlanType
from app.core.security import hash_password, verify_password, create_token, get_current_user
from app.core.plans import PLANS
import time
import re
import redis
import os

router = APIRouter()

limiter = Limiter(key_func=get_remote_address)

LOGIN_FAILURE_WINDOW = 300  # 5 minutos
LOGIN_FAILURE_MAX = 10
BLOCK_DURATION = 900  # 15 minutos

# Inicializa cliente Redis
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Lista de senhas comuns para bloqueio local
COMMON_PASSWORDS = {
    "123456789012", "password123!", "Password123!", "Passw0rd123!",
    "123456789012!", "Senha@123456", "Admin@123456", "Abcd1234!@#$",
    "qwerty123456!", "Qwerty123456!", "letmein12345!", "Welcome123!@",
    "monkey123456!", "dragon123456!", "master123456!", "shadow123456!",
    "iloveyou1234!", "sunshine1234!", "princess123!@", "football123!@",
}

# Hash dummy usado para garantir tempo de resposta constante quando usuário não existe
_DUMMY_HASH = hash_password("dummy_password_for_timing_protection_!@#$%^&*()")


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Valida a força da senha.
    Retorna (True, "") se válida ou (False, mensagem_erro) se inválida.
    """
    if len(password) < 12:
        return False, "Senha deve ter no mínimo 12 caracteres"

    if not re.search(r"[A-Z]", password):
        return False, "Senha deve conter pelo menos uma letra maiúscula"

    if not re.search(r"[a-z]", password):
        return False, "Senha deve conter pelo menos uma letra minúscula"

    if not re.search(r"\d", password):
        return False, "Senha deve conter pelo menos um número"

    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?`~]", password):
        return False, "Senha deve conter pelo menos um caractere especial (!@#$%^&*...)"

    if password.lower() in {p.lower() for p in COMMON_PASSWORDS}:
        return False, "Senha muito comum. Por favor, escolha uma senha mais segura"

    return True, ""


class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    name: str = ""


class LoginIn(BaseModel):
    email: EmailStr
    password: str


def _user_out(user: User) -> dict:
    """
    Retorna apenas os dados mínimos necessários do usuário para o response de login/registro.
    Dados internos como price_brl, features e scans_this_month são omitidos para evitar
    exposição de estrutura interna e inconsistências de controle de acesso no frontend.
    scans_this_month deve ser buscado com dados frescos apenas nos endpoints que precisam.
    """
    plan_name = user.plan if user.plan else "free"
    plan_data = PLANS.get(plan_name, PLANS["free"])

    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "plan": plan_name,
        "plan_info": {
            "name": plan_data.get("name", plan_name),
            "scans_per_month": plan_data.get("scans_per_month"),
        },
    }


def _get_client_ip(request: Request) -> str:
    # Confia apenas no IP real da conexão TCP, ignorando headers fornecidos pelo cliente.
    # Headers como X-Forwarded-For podem ser falsificados e não devem ser usados
    # para decisões de segurança, a menos que venham de um proxy reverso confiável
    # configurado explicitamente na infraestrutura.
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _is_ip_blocked(ip: str) -> bool:
    blocked_key = f"login_blocked:{ip}"
    try:
        is_blocked = redis_client.get(blocked_key)
        return is_blocked is not None
    except redis.RedisError:
        # Em caso de falha do Redis, permite o acesso para não bloquear usuários legítimos
        # mas registra o problema (em produção, use logging adequado)
        return False


def _record_login_failure(ip: str) -> int:
    failures_key = f"login_failures:{ip}"
    blocked_key = f"login_blocked:{ip}"
    try:
        pipe = redis_client.pipeline()
        pipe.incr(failures_key)
        pipe.expire(failures_key, LOGIN_FAILURE_WINDOW)
        results = pipe.execute()
        failure_count = results[0]

        if failure_count >= LOGIN_FAILURE_MAX:
            redis_client.setex(blocked_key, BLOCK_DURATION, "1")
            redis_client.delete(failures_key)

        return failure_count
    except redis.RedisError:
        # Em caso de falha do Redis, retorna 0 para não bloquear indevidamente
        return 0


def _clear_login_failures(ip: str) -> None:
    failures_key = f"login_failures:{ip}"
    blocked_key = f"login_blocked:{ip}"
    try:
        redis_client.delete(failures_key)
        redis_client.delete(blocked_key)
    except redis.RedisError:
        pass


@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, data: RegisterIn, db: Session = Depends(get_db)):
    client_ip = _get_client_ip(request)

    if _is_ip_blocked(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Muitas tentativas. Tente novamente mais tarde."
        )

    is_valid, error_message = validate_password_strength(data.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)

    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        # Retorna mensagem genérica para evitar enumeração de emails
        # Não revelamos se o email já existe ou não na plataforma
        return {
            "message": "Se este email não estiver cadastrado, você receberá um email de confirmação em breve."
        }

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        name=data.name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"token": create_token(user.id), "user": _user_out(user)}


@router.post("/auth/login")
@limiter.limit("5/minute")
def login(request: Request, data: LoginIn, db: Session = Depends(get_db)):
    client_ip = _get_client_ip(request)

    if _is_ip_blocked(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Conta temporariamente bloqueada por muitas tentativas. Tente novamente mais tarde."
        )

    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        # Executa hash dummy para manter tempo de resposta constante (proteção contra timing attack)
        verify_password(data.password, _DUMMY_HASH)
        _record_login_failure(client_ip)
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    if not verify_password(data.password, user.password_hash):
        _record_login_failure(client_ip)
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    _clear_login_failures(client_ip)
    return {"token": create_token(user.id), "user": _user_out(user)}


@router.get("/auth/me")
def me(current_user: User = Depends(get_current_user)):
    return _user_out(current_user)