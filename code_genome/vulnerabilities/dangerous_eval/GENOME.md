# Gene: dangerous_eval

**Categoria:** Execução de código arbitrário
**Severidade padrão:** CRITICAL
**OWASP:** A03:2021 — Injection

## Descrição

`eval()`, `exec()` e `pickle.loads()` com dados não confiáveis permitem
execução de código arbitrário no servidor.

## Padrões de detecção

```python
eval(user_input)           # CRÍTICO
exec(request.body)         # CRÍTICO
pickle.loads(data)         # CRÍTICO se data vier de fonte externa
__import__(module_name)    # Alto risco
```

## Impacto de negócio

- RCE (Remote Code Execution) — atacante executa qualquer comando no servidor
- Acesso a todos os arquivos do sistema
- Instalação de malware / backdoor
- Comprometimento total da infraestrutura

## Correção padrão

```python
# Em vez de eval() para expressões matemáticas:
import ast
def safe_eval(expr: str) -> float:
    tree = ast.parse(expr, mode="eval")
    # Valida que só contém operações numéricas
    allowed = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
               ast.Add, ast.Sub, ast.Mult, ast.Div)
    for node in ast.walk(tree):
        if not isinstance(node, allowed):
            raise ValueError(f"Operação não permitida: {type(node).__name__}")
    return eval(compile(tree, "<string>", "eval"))

# Em vez de pickle para dados externos:
import json
data = json.loads(raw_data)  # Seguro para dados estruturados
```

## Aprendizados

Ver pasta `learned/` para exemplos coletados de projetos reais auditados.
