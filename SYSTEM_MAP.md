# SYSTEM_MAP — Nexora Agente

Mapa da infraestrutura e fluxo atual do agente de geração de SaaS.

---

## 1. Estrutura de pastas (D:/Nexora_Agente/)

```
Nexora_Agente/
├── .env                    # Config local (paths, auth/JWT, chaves externas)
├── requirements.txt        # Dependências Python do supervisor
├── SYSTEM_MAP.md           # Este arquivo
├── app.py                  # Dashboard Streamlit (carrega .env)
├── core/                   # Orquestração, montagem, geração de código/docs, testes
├── code_genome/            # Genes reutilizáveis e testes de genes
├── config/
│   └── model_stack.json    # Stack de modelos por papel (architect/backend/planner)
├── scripts/                # init_db, update_genome, utilitários
├── memory/
│   └── sqlite/             # Banco local (genome_index, decisions, prompt_cache)
└── workspace/              # Projetos gerados (ex.: new_saas_project)
```

---

## 2. Variáveis de ambiente (.env)

Obrigatórias para operação segura:

- `WORKSPACE_ROOT`: raiz dos projetos gerados
- `GENOME_ROOT`: raiz dos genes (`code_genome`)
- `MEMORY_ROOT`: raiz da memória local (`memory`)
- `JWT_SECRET_KEY`: segredo de assinatura JWT (obrigatório, sem fallback fraco)
- `AUTH_DEMO_PASSWORD`: senha de emissão de token no backend gerado (obrigatória)

Opcionais:

- `JWT_EXPIRE_MINUTES` (default `60`)
- `OPENROUTER_API_KEY` (integrações externas, quando aplicável)
- `DEFAULT_MODEL`, `MAX_DAILY_BUDGET`

---

## 3. Fluxo de execução

1. Entrada de ideia no `app.py`.
2. `NexoraOrchestrator` consulta genes via `core/genome_search.py` (SQLite local).
3. Prompt de arquitetura é otimizado e enviado ao LLM (`core/llm_client.py`).
4. Resposta é validada/parseada em `save_to_workspace`.
5. `NexoraAssembler` monta estrutura física do projeto no `WORKSPACE_ROOT`.
6. `NexoraCoder` gera lógica de negócio (`backend/app/models`).
7. `NexoraDocs` gera README técnico do projeto.
8. `NexoraTester` pode validar build Docker do workspace.

---

## 4. Regras de robustez e segurança

- Paths absolutos hardcoded foram removidos dos módulos centrais; uso de env + fallback local.
- Falha de LLM/JSON inválido agora retorna `status: error` (sem falso sucesso).
- Backend gerado não usa mais credenciais default inseguras:
  - sem `AUTH_DEMO_PASSWORD` -> `503`
  - sem `JWT_SECRET_KEY` -> erro explícito ao gerar/validar token

---

## 5. Banco local (SQLite)

`memory/sqlite/nexora_memory.db` contém:

- `genome_index`: índice dos genes disponíveis
- `decisions` (FTS5): histórico textual de decisões
- `prompt_cache`: cache de prompts/respostas

---

## 6. Status de validação atual

- `python -m compileall -q .` -> OK
- `python -m pytest -q` -> 11 testes passando

---

*Documento vivo — atualizar quando houver mudança de fluxo, segurança ou estrutura de pastas.*
