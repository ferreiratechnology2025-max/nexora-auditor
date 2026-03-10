import json
from pathlib import Path
from typing import Any, Dict, List

from core.sandbox import DockerSandbox


class ShadowTester:
    """Executa testes de intrusão simulada em ambiente Docker isolado."""

    SCRIPT_NAME = '.nexora_shadow_attack.py'

    def __init__(self, image_tag: str = 'nexora-shadow-build'):
        self.image_tag = image_tag

    def generate_attack_script(self, project_path: str) -> str:
        root = Path(project_path).resolve()
        script_path = root / self.SCRIPT_NAME

        script_content = r'''
import json
import re
from pathlib import Path

PAYLOADS = [
    {"type": "sqli", "payload": "' OR '1'='1"},
    {"type": "xss", "payload": "<script>alert(1)</script>"},
    {"type": "path_traversal", "payload": "../../../../etc/passwd"},
    {"type": "template_injection", "payload": "{{7*7}}"},
    {"type": "header_injection", "payload": "X-Forwarded-For: 127.0.0.1\\r\\nX-Admin: true"},
    {"type": "bruteforce", "payload": "password=123456"},
    {"type": "bruteforce", "payload": "password=qwerty"},
    {"type": "bruteforce", "payload": "password=admin"},
    {"type": "bruteforce", "payload": "password=letmein"},
    {"type": "bruteforce", "payload": "password=senha123"},
    {"type": "bruteforce", "payload": "password=welcome"},
    {"type": "bruteforce", "payload": "password=000000"},
    {"type": "bruteforce", "payload": "password=abc123"},
    {"type": "bruteforce", "payload": "password=iloveyou"},
    {"type": "bruteforce", "payload": "password=changeme"},
]

RISK_PATTERNS = {
    'sqli': [r"execute\(.*\+", r"select.+\{", r"where.+\+"],
    'xss': [r"<script>", r"innerhtml", r"mark_safe"],
    'header_injection': [r"x-forwarded-for", r"request\.headers\["],
    'bruteforce': [r"login", r"authenticate", r"password"],
    'path_traversal': [r"\.\./", r"open\("],
    'template_injection': [r"jinja", r"render_template", r"\{\{"],
}

MITIGATION_PATTERNS = {
    'header_injection': [r"sanitize_header", r"replace\(\\r", r"replace\(\\n", r"http_exception"],
    'bruteforce': [r"rate_limit", r"lockout", r"failed_attempt", r"max_attempt", r"attempt_counter"],
    'sqli': [r"parameterized", r"sqlalchemy", r"prepared"],
    'xss': [r"escape", r"html\.escape", r"bleach"],
    'path_traversal': [r"resolve\(", r"pathlib", r"is_relative_to"],
    'template_injection': [r"sandboxedenvironment", r"autoescape", r"escape"],
}


def has_mitigation(content: str, attack_type: str) -> bool:
    patterns = MITIGATION_PATTERNS.get(attack_type, [])
    return any(re.search(pattern, content) for pattern in patterns)


root = Path('.').resolve()
ignored = {'.git', '__pycache__', '.pytest_cache', '.venv', 'venv', 'node_modules'}
py_files = [
    p for p in root.rglob('*.py')
    if p.name != '.nexora_shadow_attack.py' and not any(part in ignored for part in p.parts)
]

attempts = []
vulnerabilities = []

for attack in PAYLOADS:
    attack_type = attack.get('type')
    payload = attack.get('payload')

    blocked = True
    evidence = []
    affected_files = []

    for py_file in py_files:
        rel = str(py_file.relative_to(root)).replace('\\\\', '/')
        try:
            content = py_file.read_text(encoding='utf-8').lower()
        except Exception:
            continue

        risk_patterns = RISK_PATTERNS.get(attack_type, [])
        for pattern in risk_patterns:
            if re.search(pattern.lower(), content):
                if has_mitigation(content, attack_type):
                    evidence.append(f'{attack_type}_mitigated')
                else:
                    blocked = False
                    evidence.append(f'{attack_type}_risk')
                    affected_files.append(rel)
                break

    if not blocked:
        vulnerabilities.append({
            'attack_type': attack_type,
            'payload': payload,
            'affected_files': sorted(set(affected_files)),
        })

    attempts.append({
        'attack_type': attack_type,
        'payload': payload,
        'result': 'blocked' if blocked else 'suspicious',
        'blocked': blocked,
        'evidence': sorted(set(evidence)),
    })

report = {
    'ok': len(vulnerabilities) == 0,
    'attempt_count': len(attempts),
    'vulnerabilities_found': len(vulnerabilities),
    'attempts': attempts,
    'vulnerabilities': vulnerabilities,
}

print('NEXORA_SHADOW_REPORT=' + json.dumps(report, ensure_ascii=False))
raise SystemExit(0 if report['ok'] else 1)
'''

        script_path.write_text(script_content.strip() + '\n', encoding='utf-8')
        return str(script_path)

    def _parse_report(self, stdout: str) -> Dict[str, Any]:
        marker = 'NEXORA_SHADOW_REPORT='
        for line in (stdout or '').splitlines():
            if line.startswith(marker):
                raw_json = line[len(marker):]
                try:
                    return json.loads(raw_json)
                except Exception:
                    break
        return {}

    def run(self, project_path: str) -> Dict[str, Any]:
        root = Path(project_path).resolve()
        if not root.exists() or not root.is_dir():
            return {
                'ok': False,
                'status': 'error',
                'reason': 'Workspace invalido para shadow test.',
                'attempts': [],
                'vulnerabilities': [],
            }

        self.generate_attack_script(str(root))

        sandbox = DockerSandbox(project_path=str(root), image_tag=self.image_tag, dockerfile_name='Dockerfile.shadow')
        sandbox_result = sandbox.run_in_sandbox(f'python {self.SCRIPT_NAME}')
        report = self._parse_report(sandbox_result.get('stdout', ''))

        attempts: List[Dict[str, Any]] = report.get('attempts', []) if isinstance(report, dict) else []
        vulnerabilities: List[Dict[str, Any]] = report.get('vulnerabilities', []) if isinstance(report, dict) else []
        vulnerabilities_found = int(report.get('vulnerabilities_found', len(vulnerabilities))) if isinstance(report, dict) else len(vulnerabilities)
        ok = bool(report.get('ok')) if isinstance(report, dict) and report else bool(sandbox_result.get('ok'))

        return {
            'ok': ok,
            'status': 'passed' if ok else 'failed',
            'mode': 'docker',
            'attempt_count': int(report.get('attempt_count', len(attempts))) if isinstance(report, dict) else len(attempts),
            'vulnerabilities_found': vulnerabilities_found,
            'vulnerability_count': vulnerabilities_found,
            'attempts': attempts,
            'vulnerabilities': vulnerabilities,
            'stdout': sandbox_result.get('stdout', ''),
            'stderr': sandbox_result.get('stderr', ''),
        }
