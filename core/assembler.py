import os
import json
import shutil
from pathlib import Path


class NexoraAssembler:
    def __init__(self):
        project_root = Path(__file__).resolve().parents[1]
        self.workspace = os.getenv('WORKSPACE_ROOT') or str(project_root / 'workspace')
        self.genome_path = os.getenv('GENOME_ROOT') or str(project_root / 'code_genome')

    def assemble_project(self, arch_file):
        """
        Le o architecture.json e monta a estrutura de pastas e arquivos.
        """
        try:
            with open(arch_file, 'r', encoding='utf-8') as f:
                plan = json.load(f)

            project_name = plan.get('project_name', 'new_saas_project')
            project_root = os.path.join(self.workspace, project_name)

            # 1. Criar estrutura base conforme CONTEXT_TRANSFER.md
            folders = ['backend/app/api', 'backend/app/models', 'backend/app/services', 'infra/docker']
            for folder in folders:
                os.makedirs(os.path.join(project_root, folder), exist_ok=True)

            # 1.1 Scaffold minimo para build Docker real
            self._ensure_scaffold_files(project_root)

            print(f'[INFO] Estrutura base criada em: {project_root}')

            # 2. Injetar Genes (Copiar do code_genome)
            for gene in plan.get('needed_genes', []):
                self._inject_gene(gene, project_root)

            return project_root
        except Exception as e:
            return f'[ERRO] Falha na montagem: {str(e)}'

    def _ensure_scaffold_files(self, project_root):
        backend_root = os.path.join(project_root, 'backend')
        os.makedirs(backend_root, exist_ok=True)

        requirements_path = os.path.join(backend_root, 'requirements.txt')
        if not os.path.exists(requirements_path):
            with open(requirements_path, 'w', encoding='utf-8') as f:
                f.write('fastapi==0.115.0\n')
                f.write('uvicorn==0.30.6\n')
                f.write('sqlalchemy==2.0.36\n')
                f.write('pydantic==2.9.2\n')

        main_path = os.path.join(backend_root, 'app', 'main.py')
        if not os.path.exists(main_path):
            os.makedirs(os.path.dirname(main_path), exist_ok=True)
            with open(main_path, 'w', encoding='utf-8') as f:
                f.write('from fastapi import FastAPI\n\n')
                f.write("app = FastAPI(title='Nexora Generated API')\n\n")
                f.write("@app.get('/health')\n")
                f.write('def health():\n')
                f.write("    return {'status': 'ok'}\n")

    def _inject_gene(self, gene_id, project_root):
        """Busca o gene e copia para o backend do projeto."""
        # gene_id e o nome da pasta em code_genome/core/ (ex: auth, multi_tenant)
        gene_source = os.path.join(self.genome_path, 'core', gene_id)
        target_path = os.path.join(project_root, 'backend', 'app', 'core', gene_id)

        if os.path.exists(gene_source):
            shutil.copytree(gene_source, target_path, dirs_exist_ok=True)
            print(f'[OK] Gene {gene_id} injetado com sucesso.')
        else:
            print(f'[AVISO] Gene {gene_id} nao encontrado em {gene_source}.')
