import ast
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from core.sandbox import DockerSandbox


def validate_syntax(file_path: str) -> Dict[str, Any]:
    """Valida sintaxe de um arquivo Python usando AST."""
    target = Path(file_path)
    if not target.exists():
        return {
            'ok': False,
            'file_path': str(target),
            'error': 'Arquivo nao encontrado.',
            'line': None,
            'offset': None,
            'text': None,
        }

    try:
        source = target.read_text(encoding='utf-8')
        ast.parse(source, filename=str(target))
        return {
            'ok': True,
            'file_path': str(target),
            'error': None,
            'line': None,
            'offset': None,
            'text': None,
        }
    except SyntaxError as exc:
        return {
            'ok': False,
            'file_path': str(target),
            'error': exc.msg,
            'line': exc.lineno,
            'offset': exc.offset,
            'text': (exc.text or '').strip() if exc.text else None,
        }
    except Exception as exc:
        return {
            'ok': False,
            'file_path': str(target),
            'error': str(exc),
            'line': None,
            'offset': None,
            'text': None,
        }


def _extract_traceback(output: str) -> Dict[str, Any]:
    """Extrai traceback e linhas de erro em formato estruturado."""
    lines = output.splitlines()
    traceback_start = next((i for i, line in enumerate(lines) if 'Traceback (most recent call last):' in line), None)
    traceback_lines = lines[traceback_start:] if traceback_start is not None else []
    error_lines = [line for line in lines if line.startswith('E   ') or 'Error' in line or 'Exception' in line]

    return {
        'traceback': '\n'.join(traceback_lines).strip(),
        'error_lines': error_lines,
    }


def _is_docker_enabled() -> bool:
    raw = os.getenv('DOCKER_ENABLED', 'False').strip().lower()
    return raw in {'1', 'true', 'yes', 'on'}


def _run_tests_local(target: Path) -> Dict[str, Any]:
    process = subprocess.run(
        ['python', '-m', 'pytest'],
        cwd=str(target),
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
    )

    return {
        'ok': process.returncode == 0,
        'returncode': process.returncode,
        'stdout': process.stdout,
        'stderr': process.stderr,
        'mode': 'local',
    }


def _run_tests_docker(target: Path) -> Dict[str, Any]:
    sandbox = DockerSandbox(project_path=str(target))
    result = sandbox.run_in_sandbox('python -m pytest')
    result['mode'] = 'docker'
    return result


def run_workspace_tests(workspace_path: str) -> Dict[str, Any]:
    """Executa pytest no workspace (Docker opcional) e retorna relatorio estruturado."""
    target = Path(workspace_path)
    if not target.exists() or not target.is_dir():
        return {
            'ok': False,
            'workspace_path': str(target),
            'returncode': None,
            'stdout': '',
            'stderr': f'Workspace invalido: {target}',
            'mode': 'local',
            'error_report': {
                'traceback': '',
                'error_lines': [f'Workspace invalido: {target}'],
            },
        }

    if _is_docker_enabled():
        run_result = _run_tests_docker(target)
    else:
        run_result = _run_tests_local(target)

    combined_output = '\n'.join([run_result.get('stdout') or '', run_result.get('stderr') or '']).strip()
    report = _extract_traceback(combined_output)

    return {
        'ok': run_result.get('ok', False),
        'workspace_path': str(target),
        'returncode': run_result.get('returncode'),
        'stdout': run_result.get('stdout', ''),
        'stderr': run_result.get('stderr', ''),
        'mode': run_result.get('mode', 'local'),
        'sandbox': run_result if run_result.get('mode') == 'docker' else None,
        'error_report': report,
    }


def find_python_files(workspace_path: str) -> List[str]:
    """Retorna todos os arquivos .py do workspace."""
    target = Path(workspace_path)
    if not target.exists() or not target.is_dir():
        return []
    return [str(path) for path in target.rglob('*.py')]
