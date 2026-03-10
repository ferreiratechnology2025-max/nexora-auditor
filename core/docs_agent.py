import os
import json
from pathlib import Path
from core.llm_client import NexoraLLM


class NexoraDocs:
    def __init__(self):
        self.llm = NexoraLLM()
        self.docs_model = 'deepseek/deepseek-v3.2'
        try:
            project_root = Path(__file__).resolve().parents[1]
            config_path = project_root / 'config' / 'model_stack.json'
            with open(config_path, 'r', encoding='utf-8') as f:
                stack = json.load(f)
            self.docs_model = stack.get('agents', {}).get('planner', {}).get('model', self.docs_model)
        except Exception:
            pass

    def _collect_nexoradocs_notes(self, project_path):
        notes = []
        search_root = os.path.join(project_path, 'backend', 'app')
        if not os.path.isdir(search_root):
            return notes

        for root, _, files in os.walk(search_root):
            for name in files:
                if not name.endswith('.py'):
                    continue
                file_path = os.path.join(root, name)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if 'NEXORADOCS:' in line:
                                note = line.split('NEXORADOCS:', 1)[1].strip()
                                if note:
                                    notes.append(note)
                except Exception:
                    continue

        seen = set()
        unique_notes = []
        for note in notes:
            if note not in seen:
                seen.add(note)
                unique_notes.append(note)

        return unique_notes[:30]

    def generate_readme(self, project_path, architecture):
        """
        Gera o README.md e documentacao tecnica do SaaS.
        """
        project_name = architecture.get('project_name', 'Nexora SaaS')
        tabelas = architecture.get('tabelas', [])
        notes = self._collect_nexoradocs_notes(project_path)

        notes_text = '\n'.join(f'- {n}' for n in notes) if notes else '- Sem notas NEXORADOCS detectadas.'

        prompt = f"""
Escreva um README.md profissional para o projeto '{project_name}'.
Inclua:
1. Descricao do ERP Multi-tenant.
2. Stack: FastAPI, PostgreSQL, Docker.
3. Lista de Tabelas Geradas: {', '.join(tabelas)}.
4. Instrucoes de Deploy via Docker.
5. Secao 'Notas Tecnicas (NexoraDocs)' baseada nestes comentarios do codigo:
{notes_text}
"""

        readme_content = self.llm.call(self.docs_model, prompt)
        if readme_content:
            for marker in ('```markdown', '```'):
                readme_content = readme_content.replace(marker, '')
            readme_content = readme_content.strip()

        if readme_content and str(readme_content).startswith('[ERRO]'):
            readme_content = ''

        os.makedirs(project_path, exist_ok=True)
        readme_path = os.path.join(project_path, 'README.md')
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content or '# ' + project_name + '\n\nDocumentacao gerada pelo Nexora Agente.')
        print(f'[INFO] README.md gravado em: {readme_path}')
        return '[OK] Documentacao README.md gerada.'
