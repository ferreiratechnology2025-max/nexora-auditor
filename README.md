# AUDITX — Plataforma DevSecOps Autônoma

Auditoria de código com IA, auto-correção automática e certificado digital.

**Produção:** https://auditor.nexora360.cloud

## Estrutura

```
auditx/
├── backend/
│   ├── app/
│   │   ├── audit_engine.py      # Motor de análise estática (456 linhas)
│   │   ├── autofix_engine.py    # Motor de correção automática (339 linhas)
│   │   ├── payment_service.py   # Integração Mercado Pago
│   │   ├── email_service.py     # SMTP Hostinger
│   │   ├── api/                 # Routers FastAPI
│   │   ├── core/                # Auth JWT, Planos
│   │   └── models/              # User, Scan (SQLAlchemy)
│   ├── workers/tasks.py         # Celery worker assíncrono
│   ├── requirements.txt
│   ├── Dockerfile.api
│   └── Dockerfile.worker
├── frontend/
│   ├── client/src/
│   │   ├── components/          # HeroSection, Checkout, ResultsDashboard
│   │   ├── pages/               # Plans, Login, Dashboard
│   │   ├── contexts/            # AuthContext
│   │   └── lib/api.ts           # Cliente HTTP
│   ├── package.json
│   └── vite.config.ts
├── static/                      # Frontend buildado (servido pelo nginx)
├── docker-compose.yml
└── README.md
```

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | FastAPI + Python 3.11 |
| Banco | PostgreSQL 15 + SQLAlchemy 2.0 |
| Cache/Queue | Redis 7 + Celery |
| Auth | JWT (python-jose + passlib/bcrypt) |
| Pagamento | Mercado Pago SDK |
| Email | SMTP Hostinger |
| Frontend | React 19 + TypeScript + Vite + shadcn/ui |
| CSS | Tailwind CSS v4 |
| Deploy | Docker Compose + Nginx + Let's Encrypt |

## Planos

| Plano | Preco | Scans |
|---|---|---|
| Laudo avulso | R$ 119 | 1 |
| Laudo + Correcao | R$ 299 | 1 + auto-fix |
| Dev (mensal) | R$ 99/mes | 5 |
| Pro (mensal) | R$ 299/mes | 20 |
| Scale (mensal) | R$ 899/mes | Ilimitado |

## Deploy local

```bash
cp .env.example .env
docker compose up -d
```

## Deploy producao (VPS)

```bash
git pull origin main
cd /opt/auditx
docker compose build api
docker compose up -d
```
