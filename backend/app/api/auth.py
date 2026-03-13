from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.database import get_db, init_db
from app.models.user import User, PlanType
from app.core.security import hash_password, verify_password, create_token, get_current_user
from app.core.plans import PLANS

router = APIRouter()


class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    name: str = ""


class LoginIn(BaseModel):
    email: EmailStr
    password: str


def _user_out(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "plan": user.plan,
        "scans_this_month": user.scans_this_month,
        "plan_info": PLANS.get(user.plan, PLANS["free"]),
    }


@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    init_db()
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="Senha deve ter no mínimo 6 caracteres")
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
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Conta desativada")
    return {"token": create_token(user.id), "user": _user_out(user)}


@router.get("/auth/me")
def me(current_user: User = Depends(get_current_user)):
    return _user_out(current_user)


@router.get("/plans")
def list_plans():
    return PLANS
