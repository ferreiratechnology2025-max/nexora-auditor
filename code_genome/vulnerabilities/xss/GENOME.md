# Gene: xss

**Categoria:** Cross-Site Scripting
**Severidade padrão:** HIGH
**OWASP:** A03:2021 — Injection

## Descrição

XSS ocorre quando dados do usuário são inseridos no HTML sem escape,
permitindo execução de JavaScript malicioso no navegador da vítima.

## Padrões de detecção

```python
# Jinja2 sem escape
return render_template_string("<div>" + user_input + "</div>")  # CRÍTICO
# mark_safe sem validação
mark_safe(request.GET.get("message"))
# innerHTML via JS
element.innerHTML = userInput  # XSS refletido
```

## Impacto de negócio

- Roubo de cookies de sessão → sequestro de conta
- Redirecionamento para phishing
- Keyloggers no navegador da vítima
- Defacement do site

## Correção padrão

```python
import html

# Escape manual
safe = html.escape(user_input)

# Jinja2 com autoescape (padrão)
return render_template("page.html", message=user_input)  # escaped automaticamente

# bleach para HTML permitido
import bleach
safe = bleach.clean(user_input, tags=["b", "i", "u"], strip=True)
```

## Aprendizados

Ver pasta `learned/` para exemplos coletados de projetos reais auditados.
