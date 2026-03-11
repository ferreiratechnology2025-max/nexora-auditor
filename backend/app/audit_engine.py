"""
audit_engine.py — Motor de Auditoria de Segurança
===================================================
Analisa projetos de código-fonte detectando vulnerabilidades comuns,
classifica por severidade e calcula um Health Score.

Linguagens suportadas: Python, JavaScript/TypeScript, PHP, Java, Ruby, Go, C#
"""

import ast
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


# =============================================================================
# TIPOS
# =============================================================================

@dataclass
class Finding:
    severity:    str   # CRITICAL | HIGH | MEDIUM | LOW
    category:    str   # sql_injection | xss | hardcoded_secret | dangerous_eval | auth_weak
    file:        str
    line:        int
    description: str
    suggestion:  str


# Mapeamento extensão → linguagem
_EXT_LANG: dict[str, str] = {
    ".py":   "Python",
    ".js":   "JavaScript",
    ".ts":   "JavaScript",
    ".jsx":  "JavaScript",
    ".tsx":  "JavaScript",
    ".php":  "PHP",
    ".java": "Java",
    ".rb":   "Ruby",
    ".go":   "Go",
    ".cs":   "C#",
}

# Arquivos e diretórios a ignorar
_SKIP_DIRS  = {".git", ".venv", "venv", "node_modules", "__pycache__", ".tox", "dist", "build"}
_SKIP_FILES = {".env", ".env.example"}


# =============================================================================
# REGRAS GENÉRICAS (qualquer linguagem)
# =============================================================================

_GENERIC_RULES: list[dict] = [
    # Senhas / secrets hardcoded
    {
        "pattern":  re.compile(
            r'(?i)(password|passwd|secret|api_key|apikey|token|auth_key)\s*=\s*["\'][^"\']{3,}["\']'
        ),
        "severity": "CRITICAL",
        "category": "hardcoded_secret",
        "description": "Credencial hardcoded detectada: {match}",
        "suggestion":  "Use variáveis de ambiente (os.getenv / dotenv) em vez de valores literais no código.",
    },
    # URLs com credenciais embutidas
    {
        "pattern":  re.compile(
            r'(?i)(https?|ftp)://[^@\s]+:[^@\s]+@'
        ),
        "severity": "HIGH",
        "category": "hardcoded_secret",
        "description": "URL com credenciais embutidas: {match}",
        "suggestion":  "Remova usuário/senha da URL. Use variáveis de ambiente ou gerenciador de segredos.",
    },
]


# =============================================================================
# ANALISADOR PYTHON — AST + regex
# =============================================================================

class _PythonAnalyzer:
    # Chamadas perigosas detectadas via AST
    _DANGEROUS_CALLS = {
        "eval":       ("dangerous_eval",   "CRITICAL", "eval() executa código arbitrário.",
                       "Nunca avalie input do usuário. Use ast.literal_eval() para dados simples."),
        "exec":       ("dangerous_eval",   "CRITICAL", "exec() executa código arbitrário.",
                       "Evite exec(). Refatore para funções explícitas."),
        "os.system":  ("dangerous_eval",   "HIGH",     "os.system() pode executar comandos do SO.",
                       "Use subprocess.run() com lista de argumentos e shell=False."),
        "marshal.loads": ("dangerous_eval","HIGH",     "marshal.loads() pode deserializar código malicioso.",
                          "Evite deserialização de dados não confiáveis com marshal."),
    }

    # Imports perigosos
    _DANGEROUS_IMPORTS = {
        "pickle":  ("dangerous_eval", "HIGH",
                    "Import de 'pickle' detectado — deserialização insegura.",
                    "Não deserialize dados não confiáveis com pickle. Use JSON ou protobuf."),
        "marshal": ("dangerous_eval", "MEDIUM",
                    "Import de 'marshal' detectado.",
                    "Marshal é inseguro para dados externos. Prefira formatos seguros."),
    }

    # Padrões regex adicionais
    _REGEX_RULES: list[dict] = [
        {
            "pattern":  re.compile(
                r'(?i)(SELECT|INSERT|UPDATE|DELETE|DROP)\s+.{0,60}\+\s*\w+'
            ),
            "severity": "CRITICAL",
            "category": "sql_injection",
            "description": "SQL construído por concatenação: {match}",
            "suggestion":  "Use queries parametrizadas (cursor.execute(sql, params)) ou um ORM.",
        },
        {
            "pattern":  re.compile(
                r'subprocess\.(call|Popen|run)\s*\([^)]*shell\s*=\s*True'
            ),
            "severity": "HIGH",
            "category": "dangerous_eval",
            "description": "subprocess com shell=True: {match}",
            "suggestion":  "Use shell=False e passe argumentos como lista.",
        },
    ]

    def analyze(self, path: Path, source: str) -> list[Finding]:
        findings: list[Finding] = []
        findings += self._ast_scan(path, source)
        findings += self._regex_scan(path, source)
        return findings

    def _ast_scan(self, path: Path, source: str) -> list[Finding]:
        findings: list[Finding] = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return findings

        for node in ast.walk(tree):
            # Imports perigosos
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = (
                    [a.name for a in node.names] if isinstance(node, ast.Import)
                    else ([node.module] if node.module else [])
                )
                for name in names:
                    base = name.split(".")[0] if name else ""
                    if base in self._DANGEROUS_IMPORTS:
                        cat, sev, desc, sug = self._DANGEROUS_IMPORTS[base]
                        findings.append(Finding(
                            severity=sev, category=cat,
                            file=str(path), line=node.lineno,
                            description=desc, suggestion=sug,
                        ))

            # Chamadas perigosas
            if isinstance(node, ast.Call):
                name = self._call_name(node)
                if name in self._DANGEROUS_CALLS:
                    cat, sev, desc, sug = self._DANGEROUS_CALLS[name]
                    findings.append(Finding(
                        severity=sev, category=cat,
                        file=str(path), line=node.lineno,
                        description=desc, suggestion=sug,
                    ))

        return findings

    @staticmethod
    def _call_name(node: ast.Call) -> Optional[str]:
        if isinstance(node.func, ast.Name):
            return node.func.id
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                return f"{node.func.value.id}.{node.func.attr}"
        return None

    def _regex_scan(self, path: Path, source: str) -> list[Finding]:
        findings: list[Finding] = []
        lines = source.splitlines()
        for rule in self._REGEX_RULES:
            for i, line in enumerate(lines, 1):
                m = rule["pattern"].search(line)
                if m:
                    findings.append(Finding(
                        severity=rule["severity"],
                        category=rule["category"],
                        file=str(path), line=i,
                        description=rule["description"].format(match=m.group()[:120]),
                        suggestion=rule["suggestion"],
                    ))
        return findings


# =============================================================================
# ANALISADOR JAVASCRIPT / TYPESCRIPT
# =============================================================================

class _JavaScriptAnalyzer:
    _RULES: list[dict] = [
        {
            "pattern":  re.compile(r'innerHTML\s*='),
            "severity": "HIGH",
            "category": "xss",
            "description": "innerHTML assignment detectado: {match}",
            "suggestion":  "Use textContent em vez de innerHTML. Se HTML for necessário, sanitize com DOMPurify.",
        },
        {
            "pattern":  re.compile(r'\beval\s*\('),
            "severity": "CRITICAL",
            "category": "dangerous_eval",
            "description": "eval() detectado em JS: {match}",
            "suggestion":  "Remova o eval(). Refatore para código explícito ou use JSON.parse() para dados.",
        },
        {
            "pattern":  re.compile(r'document\.write\s*\('),
            "severity": "HIGH",
            "category": "xss",
            "description": "document.write() detectado: {match}",
            "suggestion":  "Evite document.write(). Manipule o DOM com createElement/appendChild.",
        },
        {
            "pattern":  re.compile(r'dangerouslySetInnerHTML'),
            "severity": "HIGH",
            "category": "xss",
            "description": "dangerouslySetInnerHTML detectado: {match}",
            "suggestion":  "Sanitize o HTML com DOMPurify antes de usar dangerouslySetInnerHTML.",
        },
        {
            "pattern":  re.compile(
                r'(?i)["\']?\s*(SELECT|INSERT|UPDATE|DELETE)\s+.{0,60}\+\s*\w+'
            ),
            "severity": "CRITICAL",
            "category": "sql_injection",
            "description": "SQL concatenado detectado em JS: {match}",
            "suggestion":  "Use queries parametrizadas ou um ORM (Sequelize, Prisma, Knex).",
        },
    ]

    def analyze(self, path: Path, source: str) -> list[Finding]:
        findings: list[Finding] = []
        lines = source.splitlines()
        for rule in self._RULES:
            for i, line in enumerate(lines, 1):
                m = rule["pattern"].search(line)
                if m:
                    findings.append(Finding(
                        severity=rule["severity"],
                        category=rule["category"],
                        file=str(path), line=i,
                        description=rule["description"].format(match=m.group()[:120]),
                        suggestion=rule["suggestion"],
                    ))
        return findings


# =============================================================================
# ANALISADOR PHP
# =============================================================================

class _PhpAnalyzer:
    _RULES: list[dict] = [
        {
            "pattern":  re.compile(r'mysql_query\s*\(\s*\$'),
            "severity": "CRITICAL",
            "category": "sql_injection",
            "description": "mysql_query() com variável: {match}",
            "suggestion":  "Use PDO ou MySQLi com prepared statements.",
        },
        {
            "pattern":  re.compile(r'\$_(GET|POST|REQUEST|COOKIE)\s*\['),
            "severity": "HIGH",
            "category": "auth_weak",
            "description": "Input não sanitizado de superglobal: {match}",
            "suggestion":  "Filtre e valide inputs com filter_input() ou htmlspecialchars().",
        },
        {
            "pattern":  re.compile(r'\b(system|exec|passthru|shell_exec)\s*\('),
            "severity": "CRITICAL",
            "category": "dangerous_eval",
            "description": "Execução de comando do SO detectada: {match}",
            "suggestion":  "Evite funções de execução de sistema com input do usuário. Use escapeshellarg().",
        },
        {
            "pattern":  re.compile(r'eval\s*\('),
            "severity": "CRITICAL",
            "category": "dangerous_eval",
            "description": "eval() em PHP: {match}",
            "suggestion":  "Remova o eval(). É uma das funções mais perigosas do PHP.",
        },
    ]

    def analyze(self, path: Path, source: str) -> list[Finding]:
        findings: list[Finding] = []
        lines = source.splitlines()
        for rule in self._RULES:
            for i, line in enumerate(lines, 1):
                m = rule["pattern"].search(line)
                if m:
                    findings.append(Finding(
                        severity=rule["severity"],
                        category=rule["category"],
                        file=str(path), line=i,
                        description=rule["description"].format(match=m.group()[:120]),
                        suggestion=rule["suggestion"],
                    ))
        return findings


# =============================================================================
# ANALISADOR GENÉRICO (Java, Ruby, Go, C# e fallback)
# =============================================================================

class _GenericAnalyzer:
    _RULES: list[dict] = [
        {
            "pattern":  re.compile(
                r'(?i)(SELECT|INSERT|UPDATE|DELETE|DROP)\s+.{0,60}\+\s*\w+'
            ),
            "severity": "CRITICAL",
            "category": "sql_injection",
            "description": "SQL concatenado detectado: {match}",
            "suggestion":  "Use prepared statements / queries parametrizadas.",
        },
        {
            "pattern":  re.compile(r'(?i)\bRuntime\.exec\s*\('),
            "severity": "HIGH",
            "category": "dangerous_eval",
            "description": "Runtime.exec() detectado (Java): {match}",
            "suggestion":  "Use ProcessBuilder com lista de argumentos em vez de Runtime.exec().",
        },
    ]

    def analyze(self, path: Path, source: str) -> list[Finding]:
        findings: list[Finding] = []
        lines = source.splitlines()
        for rule in self._RULES:
            for i, line in enumerate(lines, 1):
                m = rule["pattern"].search(line)
                if m:
                    findings.append(Finding(
                        severity=rule["severity"],
                        category=rule["category"],
                        file=str(path), line=i,
                        description=rule["description"].format(match=m.group()[:120]),
                        suggestion=rule["suggestion"],
                    ))
        return findings


# =============================================================================
# AUDIT ENGINE — interface pública
# =============================================================================

_SEVERITY_PENALTY = {"CRITICAL": 20, "HIGH": 10, "MEDIUM": 5, "LOW": 2}

_ANALYZERS = {
    "Python":     _PythonAnalyzer(),
    "JavaScript": _JavaScriptAnalyzer(),
    "PHP":        _PhpAnalyzer(),
}
_GENERIC = _GenericAnalyzer()


class AuditEngine:
    """
    Motor de auditoria estática de segurança.

    Uso:
        result = AuditEngine().audit("/path/to/extracted/project")
    """

    def audit(self, project_path: str) -> dict:
        root = Path(project_path)
        findings: list[Finding] = []
        files_scanned = 0
        languages_seen: set[str] = set()

        for file_path in self._iter_files(root):
            lang = _EXT_LANG.get(file_path.suffix.lower())
            if lang is None:
                continue

            try:
                source = file_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            files_scanned += 1
            languages_seen.add(lang)

            # Regras genéricas (todas as linguagens)
            findings += self._apply_generic(file_path, source)

            # Analisador específico da linguagem
            analyzer = _ANALYZERS.get(lang, _GENERIC)
            findings += analyzer.analyze(file_path, source)

        # Deduplica por (file, line, category)
        findings = self._deduplicate(findings)

        by_severity: dict[str, int] = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for f in findings:
            by_severity[f.severity] = by_severity.get(f.severity, 0) + 1

        score = 100
        for sev, count in by_severity.items():
            score -= _SEVERITY_PENALTY.get(sev, 0) * count
        score = max(0, score)

        return {
            "health_score_initial": score,
            "findings":             [asdict(f) for f in findings],
            "total":                len(findings),
            "by_severity":          by_severity,
            "files_scanned":        files_scanned,
            "languages_detected":   sorted(languages_seen),
        }

    # ── helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _iter_files(root: Path):
        for p in root.rglob("*"):
            if p.is_file() and not any(d in p.parts for d in _SKIP_DIRS):
                if p.name not in _SKIP_FILES:
                    yield p

    @staticmethod
    def _apply_generic(path: Path, source: str) -> list[Finding]:
        findings: list[Finding] = []
        lines = source.splitlines()
        for rule in _GENERIC_RULES:
            for i, line in enumerate(lines, 1):
                m = rule["pattern"].search(line)
                if m:
                    findings.append(Finding(
                        severity=rule["severity"],
                        category=rule["category"],
                        file=str(path), line=i,
                        description=rule["description"].format(match=m.group()[:120]),
                        suggestion=rule["suggestion"],
                    ))
        return findings

    @staticmethod
    def _deduplicate(findings: list[Finding]) -> list[Finding]:
        seen: set[tuple] = set()
        result: list[Finding] = []
        for f in findings:
            key = (f.file, f.line, f.category)
            if key not in seen:
                seen.add(key)
                result.append(f)
        return result
