import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


class DockerSandbox:
    """Executa comandos de teste em container Docker efemero."""

    def __init__(
        self,
        project_path: str,
        image_tag: str = 'nexora-temp-build',
        dockerfile_name: str = 'Dockerfile.nexora',
    ):
        self.project_path = Path(project_path).resolve()
        self.image_tag = image_tag
        self.dockerfile_name = dockerfile_name
        self.dockerfile_path = self.project_path / dockerfile_name

    def _detect_requirements_file(self) -> Optional[Path]:
        candidates = [
            self.project_path / 'requirements.txt',
            self.project_path / 'backend' / 'requirements.txt',
        ]
        for candidate in candidates:
            if candidate.exists() and candidate.is_file():
                return candidate
        return None

    def generate_dockerfile(self, project_path: str, requirements: Optional[Iterable[str] | str] = None) -> str:
        """Gera Dockerfile dinamico baseado no requirements informado."""
        root = Path(project_path).resolve()
        root.mkdir(parents=True, exist_ok=True)

        requirements_ref = ''

        if isinstance(requirements, str) and requirements.strip():
            possible_file = root / requirements
            if possible_file.exists() and possible_file.is_file():
                requirements_ref = requirements.replace('\\', '/').strip()
            else:
                req_file = root / '.nexora_requirements.txt'
                req_file.write_text(requirements.strip() + '\n', encoding='utf-8')
                requirements_ref = req_file.name
        elif requirements:
            req_file = root / '.nexora_requirements.txt'
            req_file.write_text('\n'.join(requirements) + '\n', encoding='utf-8')
            requirements_ref = req_file.name
        else:
            detected = self._detect_requirements_file()
            if detected:
                requirements_ref = str(detected.relative_to(root)).replace('\\', '/')

        lines = [
            'FROM python:3.12-slim',
            'ENV PYTHONDONTWRITEBYTECODE=1',
            'ENV PYTHONUNBUFFERED=1',
            'WORKDIR /workspace',
            'COPY . /workspace',
        ]

        if requirements_ref:
            lines.append(f'RUN pip install --no-cache-dir -r {requirements_ref}')

        lines.append('RUN pip install --no-cache-dir pytest')
        lines.append('CMD ["python", "-m", "pytest"]')

        dockerfile_content = '\n'.join(lines)

        dockerfile_path = root / self.dockerfile_name
        dockerfile_path.write_text(dockerfile_content + '\n', encoding='utf-8')
        self.dockerfile_path = dockerfile_path

        return str(dockerfile_path)

    def run_in_sandbox(self, command: str) -> Dict[str, Any]:
        """Builda imagem temporaria e executa comando dentro do conteiner (--rm)."""
        if not self.project_path.exists() or not self.project_path.is_dir():
            return {
                'ok': False,
                'returncode': None,
                'stdout': '',
                'stderr': f'Projeto invalido para sandbox: {self.project_path}',
            }

        self.generate_dockerfile(str(self.project_path))

        build = subprocess.run(
            [
                'docker',
                'build',
                '-f',
                str(self.dockerfile_path),
                '-t',
                self.image_tag,
                str(self.project_path),
            ],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
        )

        if build.returncode != 0:
            return {
                'ok': False,
                'returncode': build.returncode,
                'stdout': build.stdout,
                'stderr': build.stderr,
                'stage': 'build',
            }

        run = subprocess.run(
            [
                'docker',
                'run',
                '--rm',
                '-v',
                f'{self.project_path}:/workspace',
                '-w',
                '/workspace',
                self.image_tag,
                'sh',
                '-lc',
                command,
            ],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
        )

        return {
            'ok': run.returncode == 0,
            'returncode': run.returncode,
            'stdout': run.stdout,
            'stderr': run.stderr,
            'build_stdout': build.stdout,
            'build_stderr': build.stderr,
            'stage': 'run' if run.returncode != 0 else 'completed',
        }
