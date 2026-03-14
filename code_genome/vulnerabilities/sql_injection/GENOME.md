# Gene: sql_injection

**Categoria:** Injeção de SQL
**Severidade padrão:** CRITICAL
**OWASP:** A03:2021 — Injection

## Descrição

SQL Injection ocorre quando entradas do usuário são concatenadas diretamente em queries SQL
sem sanitização, permitindo que um atacante execute comandos SQL arbitrários no banco de dados.

## Padrões de detecção

```python
# Vulnerável — concatenação direta
query = "SELECT * FROM users WHERE id=" + user_id
cursor.execute("SELECT * FROM users WHERE name='" + name + "'")
f"DELETE FROM orders WHERE id={request.args.get('id')}"
```

## Impacto de negócio

- Extração de todos os dados do banco (senha, dados pessoais, financeiros)
- Violação de LGPD / GDPR — multas de até 2% do faturamento
- Bypass de autenticação — qualquer usuário pode virar admin
- Deleção ou corrupção de dados

## Correção padrão

```python
# Correto — parametrização
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
# SQLAlchemy
result = db.execute(select(User).where(User.id == user_id))
```

## Aprendizados

Ver pasta `learned/` para exemplos coletados de projetos reais auditados.
