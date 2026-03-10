class PromptOptimizer:
    def optimize(self, prompt, context_type):
        """
        Aplica regras de reducao de tokens baseadas no contexto.
        """
        strategies = {
            "architecture": self.architecture_optimizer,
            "coding": self.coding_optimizer,
            "docs": self.docs_optimizer,
        }
        return strategies.get(context_type, lambda x: x)(prompt)

    def coding_optimizer(self, prompt):
        # Regras fixas para codigo multi-tenant e leitura pelo NexoraDocs.
        guardrails = """
You are a senior backend engineer. Return ONLY raw Python code.
Mandatory rules:
- Use tenant_id as a required field whenever applicable.
- Enforce tenant_id in every data access filter/query path.
- Reuse TenantMixin for multi-tenant isolation.
- Respect assembler structure (backend/app/models, backend/app/api, backend/app/services).
- Add concise comments prefixed with "NEXORADOCS:" for module purpose and business rules.
- Do not output markdown fences or prose.
""".strip()
        return f"{guardrails}\n\nTask:\n{prompt}"

    def architecture_optimizer(self, prompt):
        # Forca JSON e arquitetura compativel com o Assembler.
        guardrails = """
Return ONLY one valid JSON object.
Mandatory architecture constraints:
- Use folders: backend/app/models, backend/app/api, backend/app/services, infra/docker.
- Include multi-tenant strategy with TenantMixin and tenant_id mandatory filtering.
- Keep output directly parsable by Python json.loads.
No prose, no markdown.
""".strip()
        return f"{guardrails}\n\nRequest:\n{prompt}"

    def docs_optimizer(self, prompt):
        return f"Write concise technical documentation.\n\n{prompt}"
