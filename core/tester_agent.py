import os

try:
    from core.test_runner import TestRunner
    _runner_available = True
except Exception:
    TestRunner = None  # type: ignore
    _runner_available = False


class NexoraTester:
    def __init__(self):
        self.runner = None
        if _runner_available and TestRunner is not None:
            try:
                self.runner = TestRunner()
            except Exception:
                self.runner = None

    def validate_deployment(self, project_path):
        """
        Tenta validar a integridade do workspace gerado.
        """
        if not project_path or str(project_path).startswith("[ERRO]"):
            return "[ERRO] Caminho do projeto invalido."

        print(f"[INFO] Iniciando validacao tecnica em: {project_path}")

        # Verifica se o Dockerfile existe (deve ser criado pelo Assembler/Coder)
        dockerfile_path = os.path.join(project_path, "infra", "docker", "backend.dockerfile")

        if not os.path.exists(dockerfile_path):
            # Cria um Dockerfile basico se o Assembler ainda nao o fez
            self._generate_basic_dockerfile(project_path, dockerfile_path)

        if self.runner is None:
            return "[AVISO] Docker nao disponivel. Instale o pacote 'docker' e abra o Docker Desktop."

        # Chama o runner para validar o container
        success = self.runner.run_workspace_test(project_path)

        if success:
            return "[OK] Container buildado e validado com sucesso."
        return "[ERRO] Falha na validacao do ambiente Docker."

    def _generate_basic_dockerfile(self, project_root, path):
        # Paths no COPY sao relativos ao contexto de build (project_root)
        content = """FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[INFO] Dockerfile basico criado em: {path}")
