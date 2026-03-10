import json
import os
import re
from pathlib import Path

PAYLOADS = [
    "' OR '1'='1",
    "<script>alert(1)</script>",
    "../../../../etc/passwd",
    "{{7*7}}",
    "; DROP TABLE users; --",
]

RISK_PATTERNS = {
    'sql_injection_risk': [r"SELECT.+\{", r"INSERT.+\{", r"UPDATE.+\{"],
    'xss_risk': [r"<script>", r"return\s+f\"<"],
    'code_execution_risk': [r"eval\(", r"exec\(", r"shell=True", r"os\.system\("],
}


root = Path('.').resolve()
ignored = {'.git', '__pycache__', '.pytest_cache', '.venv', 'venv', 'node_modules'}
py_files = [
    p for p in root.rglob('*.py')
    if not any(part in ignored for part in p.parts)
]

attempts = []
vulnerabilities = []

for py_file in py_files:
    rel = str(py_file.relative_to(root)).replace('\\\\', '/')
    try:
        content = py_file.read_text(encoding='utf-8').lower()
    except Exception as exc:
        attempts.append({
            'file': rel,
            'payload': 'read_error',
            'result': f'erro: {exc}',
            'blocked': False,
        })
        continue

    for payload in PAYLOADS:
        blocked = True
        evidence = []
        for risk_name, patterns in RISK_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern.lower(), content):
                    blocked = False
                    evidence.append(risk_name)
                    vulnerabilities.append({
                        'file': rel,
                        'payload': payload,
                        'risk': risk_name,
                    })
                    break

        attempts.append({
            'file': rel,
            'payload': payload,
            'result': 'blocked' if blocked else 'suspicious',
            'blocked': blocked,
            'evidence': sorted(set(evidence)),
        })

report = {
    'ok': len(vulnerabilities) == 0,
    'attempt_count': len(attempts),
    'vulnerability_count': len(vulnerabilities),
    'attempts': attempts[:60],
    'vulnerabilities': vulnerabilities[:20],
}

print('NEXORA_SHADOW_REPORT=' + json.dumps(report, ensure_ascii=False))
raise SystemExit(0 if report['ok'] else 1)
