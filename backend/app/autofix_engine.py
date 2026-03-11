"""
autofix_engine.py — Motor de Auto-Correção AUDITX
===================================================
Recebe findings do AuditEngine e aplica patches de correção automática.

Estratégias por categoria:
  hardcoded_secret → substitui literal por os.environ.get()
  dangerous_eval   → comenta a linha com aviso
  sql_injection    → converte concatenação em query parametrizada
  xss / outros     → marca como manual_required

Regras de segurança:
  - Corrige bottom-up (preserva números de linha durante o processamento)
  - Valida ast.parse() após cada fix em arquivos .py — reverte se inválido
  - Nunca sobrescreve sem confirmar que o resultado é parseável
"""

import ast
import difflib
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional


# =============================================================================
# TIPOS
# =============================================================================

@dataclass
class FixResult:
    category:   str
    file:       str
    line:       int
    status:     str   # fixed | skipped | manual_required
    diff:       str = ""
    suggestion: str = ""


_SEVERITY_PENALTY: dict[str, int] = {
    "CRITICAL": 20, "HIGH": 10, "MEDIUM": 5, "LOW": 2
}

# Padrão de arquivo Python
_IS_PY = lambda path: str(path).endswith(".py")


# =============================================================================
# FIXERS POR CATEGORIA
# =============================================================================

# ── hardcoded_secret ──────────────────────────────────────────────────────────
_SECRET_RE = re.compile(
    r'^(\s*)([\w]+)\s*=\s*(["\'])([^"\']*)\3(.*?)$'
)

def _fix_hardcoded_secret(line: str) -> Optional[str]:
    """Substitui literal por os.environ.get('VAR', '')."""
    eol  = "\n" if line.endswith("\n") else ""
    body = line.rstrip("\n")
    m    = _SECRET_RE.match(body)
    if not m:
        return None
    indent, varname = m.group(1), m.group(2)
    env_key = varname.upper()
    return (
        f"{indent}{varname} = os.environ.get('{env_key}', '')"
        f"  # [AUDITX] segredo movido para variável de ambiente{eol}"
    )


# ── dangerous_eval ────────────────────────────────────────────────────────────
def _fix_dangerous_eval(line: str) -> str:
    """Comenta a linha e adiciona aviso."""
    eol  = "\n" if line.endswith("\n") else ""
    body = line.rstrip("\n")
    indent    = len(body) - len(body.lstrip())
    pad       = body[:indent]
    code_part = body.lstrip()
    return (
        f"{pad}# [AUDITX] REMOVIDO: {code_part}"
        f" — eval() é perigoso. Use ast.literal_eval() para dados simples{eol}"
    )


# ── sql_injection ─────────────────────────────────────────────────────────────
_SQL_CONCAT_RE = re.compile(
    r'^(\s*)([\w]+)\s*=\s*(["\'])'          # indent + varname = quote
    r'((?:SELECT|INSERT|UPDATE|DELETE|DROP)[^"\']*)'  # SQL text
    r'\3\s*\+\s*([\w.]+)'                   # closing quote + + variable
    r'(.*?)$',
    re.IGNORECASE,
)

def _fix_sql_injection(line: str) -> Optional[str]:
    """Converte concatenação SQL em query parametrizada."""
    eol  = "\n" if line.endswith("\n") else ""
    body = line.rstrip("\n")
    m    = _SQL_CONCAT_RE.match(body)
    if not m:
        return None

    indent     = m.group(1)
    varname    = m.group(2)
    sql_text   = m.group(4)
    concat_var = m.group(5)

    # Deriva nome do parâmetro a partir do nome da variável concatenada
    param = re.sub(r'^(user_|input_|req_|the_)', '', concat_var.lower()) or "param"

    # Injeta :param no final do SQL (após operador de comparação)
    sql_param = re.sub(r'([=<>!]+\s*)$', lambda mo: mo.group(1) + f":{param}", sql_text.rstrip())
    if f":{param}" not in sql_param:                     # fallback se sem operador final
        sql_param = sql_text.rstrip() + f" :{param}"

    return (
        f'{indent}{varname} = ("{sql_param}", {{"{param}": {concat_var}}})'
        f'  # [AUDITX] parametrizado{eol}'
    )


# Mapa categoria → fixer
_FIXERS = {
    "hardcoded_secret": _fix_hardcoded_secret,
    "dangerous_eval":   _fix_dangerous_eval,
    "sql_injection":    _fix_sql_injection,
}


# =============================================================================
# AUTO-FIX ENGINE
# =============================================================================

class AutoFixEngine:
    """
    Aplica correções automáticas nos arquivos do projeto com base nos findings.
    """

    def fix(self, project_path: str, findings: list) -> dict:
        """
        Parâmetros:
            project_path — raiz do projeto (mesmo path passado ao AuditEngine)
            findings     — lista de dicts retornada por AuditEngine().audit()

        Retorna:
            {
                "fixed":              List[FixResult],
                "skipped":            List[FixResult],
                "health_score_final": int,
                "patch_summary":      str,
            }
        """
        # Agrupa por arquivo
        by_file: dict[str, list] = {}
        for f in findings:
            by_file.setdefault(f["file"], []).append(f)

        all_fixed:   list[FixResult] = []
        all_skipped: list[FixResult] = []

        for filepath, file_findings in by_file.items():
            fixed, skipped = self._fix_file(Path(filepath), file_findings)
            all_fixed.extend(fixed)
            all_skipped.extend(skipped)

        # Recalcula health score: apenas findings não corrigidos contam
        fixed_keys = {(r.file, r.line, r.category) for r in all_fixed}
        remaining  = [
            f for f in findings
            if (f["file"], f["line"], f["category"]) not in fixed_keys
        ]
        score = max(0, 100 - sum(_SEVERITY_PENALTY.get(f["severity"], 0) for f in remaining))

        return {
            "fixed":              [asdict(r) for r in all_fixed],
            "skipped":            [asdict(r) for r in all_skipped],
            "health_score_final": score,
            "patch_summary":      self._build_summary(all_fixed, all_skipped),
        }

    # ── private ───────────────────────────────────────────────────────────────

    def _fix_file(
        self, path: Path, file_findings: list
    ) -> tuple[list[FixResult], list[FixResult]]:
        fixed:   list[FixResult] = []
        skipped: list[FixResult] = []

        if not path.exists():
            for f in file_findings:
                skipped.append(FixResult(
                    category=f["category"], file=str(path),
                    line=f["line"], status="skipped",
                    suggestion="Arquivo não encontrado no disco.",
                ))
            return fixed, skipped

        try:
            original_source = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            for f in file_findings:
                skipped.append(FixResult(
                    category=f["category"], file=str(path),
                    line=f["line"], status="skipped",
                    suggestion=f"Erro ao ler o arquivo: {exc}",
                ))
            return fixed, skipped

        lines = original_source.splitlines(keepends=True)

        # Processa bottom-up para preservar números de linha
        sorted_findings = sorted(file_findings, key=lambda x: x["line"], reverse=True)
        needs_import_os = False

        for finding in sorted_findings:
            idx = finding["line"] - 1   # 0-based
            category = finding["category"]

            if idx < 0 or idx >= len(lines):
                skipped.append(FixResult(
                    category=category, file=str(path),
                    line=finding["line"], status="skipped",
                    suggestion="Número de linha fora do intervalo do arquivo.",
                ))
                continue

            fixer = _FIXERS.get(category)
            if fixer is None:
                skipped.append(FixResult(
                    category=category, file=str(path),
                    line=finding["line"], status="manual_required",
                    suggestion=finding.get("suggestion", "Sem correção automática — revise manualmente."),
                ))
                continue

            original_line = lines[idx]
            fixed_line    = fixer(original_line)

            if fixed_line is None:
                skipped.append(FixResult(
                    category=category, file=str(path),
                    line=finding["line"], status="skipped",
                    suggestion=f"Padrão não reconhecido para auto-fix. {finding.get('suggestion', '')}",
                ))
                continue

            # Testa a linha isolada (validação parcial)
            test_lines = lines.copy()
            test_lines[idx] = fixed_line

            # Validação de sintaxe para Python (com import os provisório)
            if _IS_PY(path):
                probe_src = "import os\n" + "".join(test_lines)
                try:
                    ast.parse(probe_src)
                except SyntaxError as exc:
                    skipped.append(FixResult(
                        category=category, file=str(path),
                        line=finding["line"], status="skipped",
                        suggestion=(
                            f"Fix gerou SyntaxError ({exc.msg}) — revertido. "
                            f"{finding.get('suggestion', '')}"
                        ),
                    ))
                    continue

            # Gera diff legível
            diff_text = "".join(difflib.unified_diff(
                [original_line],
                [fixed_line],
                fromfile=f"a/{path.name}",
                tofile=f"b/{path.name}",
                lineterm="\n",
            ))

            # Aplica
            lines[idx] = fixed_line
            if category == "hardcoded_secret" and _IS_PY(path):
                needs_import_os = True

            fixed.append(FixResult(
                category=category, file=str(path),
                line=finding["line"], status="fixed",
                diff=diff_text,
            ))

        # Adiciona `import os` uma única vez no topo, depois de todos os fixes de linha
        if needs_import_os:
            lines = self._ensure_import_os(lines)

        # Valida o arquivo completo final (Python)
        if _IS_PY(path) and fixed:
            final_source = "".join(lines)
            try:
                ast.parse(final_source)
            except SyntaxError:
                # Algo saiu errado — reverte tudo para este arquivo
                for r in fixed[:]:
                    r.status = "skipped"
                    r.suggestion = "Arquivo final com SyntaxError — todos os fixes revertidos."
                    skipped.append(r)
                fixed.clear()
                return fixed, skipped

        if fixed:
            path.write_text("".join(lines), encoding="utf-8")

        return fixed, skipped

    @staticmethod
    def _ensure_import_os(lines: list[str]) -> list[str]:
        """Insere `import os` no topo se ainda não existir."""
        for line in lines:
            if re.match(r'^\s*import\s+os\b', line):
                return lines   # já importado

        insert_at = 0
        for i, line in enumerate(lines):
            if re.match(r'^\s*(import |from )', line):
                insert_at = i + 1   # depois do último import existente

        lines.insert(insert_at, "import os  # [AUDITX] adicionado para variáveis de ambiente\n")
        return lines

    @staticmethod
    def _build_summary(fixed: list[FixResult], skipped: list[FixResult]) -> str:
        parts = [
            f"AutoFix AUDITX — {len(fixed)} correção(ões) aplicada(s), "
            f"{len(skipped)} pendente(s) de revisão manual."
        ]
        if fixed:
            parts.append("\nCorrigidos automaticamente:")
            for r in fixed:
                parts.append(f"  [FIXED]   [{r.category}] {r.file}:{r.line}")
        if skipped:
            parts.append("\nRequerem atenção manual:")
            for r in skipped:
                parts.append(f"  [MANUAL]  [{r.category}] {r.file}:{r.line} — {r.suggestion}")
        return "\n".join(parts)
