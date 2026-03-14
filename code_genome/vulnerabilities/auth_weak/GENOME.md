# Gene: auth_weak

**Categoria:** Autenticação fraca
**Severidade padrão:** HIGH
**OWASP:** A07:2021 — Identification and Authentication Failures

## Descrição

Falhas na implementação de autenticação: senhas fracas sem hash, tokens previsíveis,
falta de rate limiting, JWT sem validação de expiração.

## Padrões de detecção

```python
# Hash fraco
hashlib.md5(password.encode()).hexdigest()     # INSEGURO
hashlib.sha1(password.encode()).hexdigest()    # INSEGURO

# Sem rate limiting no login
@app.post("/login")
def login(data: LoginForm):  # sem throttle → brute force livre

# JWT sem verificação de expiração
jwt.decode(token, key, algorithms=["HS256"], options={"verify_exp": False})

# Senha hardcoded como válida
if password == "admin123": return True
```

## Impacto de negócio

- Brute force de contas de usuário
- Sequestro de sessão via JWT inválido
- Acesso não autorizado a dados de outros usuários (IDOR)
- Violação de LGPD por acesso indevido a dados pessoais

## Correção padrão

```python
from passlib.context import CryptContext
from fastapi_limiter.depends import RateLimiter
from jose import jwt, JWTError
from datetime import datetime, timedelta

# Hash seguro com bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# JWT com expiração obrigatória
def create_token(subject: str, secret: str, expires_min: int = 60) -> str:
    payload = {
        "sub": subject,
        "exp": datetime.utcnow() + timedelta(minutes=expires_min),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, secret, algorithm="HS256")

# Rate limiting no endpoint de login
@app.post("/login", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def login(data: LoginForm, db: Session = Depends(get_db)):
    ...
```

## Aprendizados

Ver pasta `learned/` para exemplos coletados de projetos reais auditados.
