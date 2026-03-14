# Gene: hardcoded_secret

**Categoria:** Exposição de segredos
**Severidade padrão:** CRITICAL
**OWASP:** A02:2021 — Cryptographic Failures

## Descrição

Segredos (senhas, API keys, tokens, chaves JWT) embutidos diretamente no código-fonte
ficam expostos em repositórios git, logs e processos.

## Padrões de detecção

```python
password = "admin123"
API_KEY = "sk-secret-abc123"
SECRET_KEY = "minha-chave-super-secreta"
JWT_SECRET = "hardcoded"
database_url = "postgresql://admin:senha123@localhost/db"
```

## Impacto de negócio

- Acesso total ao banco de dados se a connection string vazar
- Comprometimento de APIs externas (pagamentos, email, SMS)
- Vazamento em histórico git — impossível apagar completamente
- Violação de LGPD e certificações de segurança

## Correção padrão

```python
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
API_KEY = os.getenv("PAYMENT_API_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY não configurada no ambiente")
```

## Aprendizados

Ver pasta `learned/` para exemplos coletados de projetos reais auditados.
