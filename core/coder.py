import os
import json
from pathlib import Path
from core.llm_client import NexoraLLM
from core.prompt_optimizer import PromptOptimizer


class NexoraCoder:
    def __init__(self):
        self.llm = NexoraLLM()
        self.optimizer = PromptOptimizer()
        project_root = Path(__file__).resolve().parents[1]
        config_path = project_root / 'config' / 'model_stack.json'
        with open(config_path, 'r', encoding='utf-8') as f:
            self.model_stack = json.load(f)

    def generate_gene_files(self, gene_path, prompt):
        """Gera arquivos base de um gene interno em code_genome/core."""
        model_name = self.model_stack['roles']['executor']
        os.makedirs(gene_path, exist_ok=True)

        template_prompt = f"""
{prompt}

Entregue apenas codigo Python puro para template.py, sem markdown.
""".strip()
        template_code = self.llm.call(model_name, self.optimizer.optimize(template_prompt, 'coding'), role='executor')
        if template_code:
            for marker in ('```python', '```'):
                template_code = template_code.replace(marker, '')
        template_code = (template_code or '').strip()

        if 'NEXORADOCS:' not in template_code:
            template_code = '# NEXORADOCS: Template base do gene reutilizavel.\n' + template_code

        md_prompt = f"""
{prompt}

Escreva apenas o conteudo de GENOME.md em Markdown, sem cercas de codigo.
""".strip()
        genome_md = self.llm.call(model_name, self.optimizer.optimize(md_prompt, 'docs'), role='executor')
        if genome_md:
            genome_md = genome_md.replace('```markdown', '').replace('```', '')
        genome_md = (genome_md or '').strip()
        if 'NEXORADOCS:' not in genome_md:
            genome_md = '<!-- NEXORADOCS: Guia de uso do gene pelo Architect. -->\n\n' + genome_md

        with open(os.path.join(gene_path, 'template.py'), 'w', encoding='utf-8') as f:
            f.write(template_code)

        with open(os.path.join(gene_path, 'GENOME.md'), 'w', encoding='utf-8') as f:
            f.write(genome_md)

        print(f'[OK] Gene interno gerado em: {gene_path}')

    def write_business_logic(self, project_path, architecture_data):
        """
        Gera os arquivos de modelos para os componentes de negocio.
        """
        model_name = self.model_stack['roles']['executor']

        # Foco: Service Orders e Products (baseado no CONTEXT_TRANSFER.md)
        components = architecture_data.get('tabelas', ['service_orders', 'products'])

        for component in components:
            print(f'[INFO] Programando logica para: {component}...')

            raw_prompt = f"""
Crie um arquivo Python completo para backend/app/models/{component}.py.
Contexto: ERP multi-tenant para oficinas.
Projeto: {architecture_data.get('project_name')}

Regras obrigatorias:
1. Use TenantMixin para isolamento entre tenants.
2. tenant_id deve ser campo obrigatorio do modelo quando aplicavel.
3. Toda operacao de consulta/atualizacao/exclusao deve filtrar por tenant_id.
4. Adicione comentarios curtos com prefixo "NEXORADOCS:" explicando regras de negocio.
5. Entregue apenas codigo Python puro, sem markdown.
""".strip()
            prompt = self.optimizer.optimize(raw_prompt, 'coding')

            code = self.llm.call(model_name, prompt, role='executor')

            if code:
                for marker in ('```python', '```'):
                    code = code.replace(marker, '')
            code = (code or '').strip()

            if 'tenant_id' not in code.lower():
                print(f'[AVISO] {component}.py foi gerado sem tenant_id explicito.')

            if 'NEXORADOCS:' not in code:
                code = (
                    '# NEXORADOCS: Modulo de dominio com isolamento multi-tenant por tenant_id.\n'
                    + code
                )

            models_dir = os.path.join(project_path, 'backend', 'app', 'models')
            os.makedirs(models_dir, exist_ok=True)
            file_path = os.path.join(models_dir, f'{component}.py')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)

            print(f'[OK] {component}.py gerado.')


