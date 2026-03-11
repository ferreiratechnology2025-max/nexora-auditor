"""
report_performance.py — Laudo de Eficiência (Performance & Code Quality)
Analisa code smells, complexidade ciclomática e gargalos de memória.
"""

from __future__ import annotations
import ast
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


# =============================================================================
# TIPOS
# =============================================================================

@dataclass
class CodeSmell:
    type:       str    # long_function | no_docstring | short_varname | large_file
    file:       str
    line:       int
    detail:     str
    suggestion: str


@dataclass
class ComplexityEntry:
    file:     str
    function: str
    line:     int
    score:    int
    level:    str    # SIMPLE | MODERATE | COMPLEX


@dataclass
class MemoryIssue:
    file:    str
    line:    int
    type:    str
    detail:  str


# =============================================================================
# ANALISADOR DE PERFORMANCE
# =============================================================================

class PerformanceAnalyzer:

    def analyze(self, project_path: str) -> dict:
        smells:      list[CodeSmell]       = []
        complexity:  list[ComplexityEntry] = []
        mem_issues:  list[MemoryIssue]     = []

        for py_file in sorted(Path(project_path).rglob("*.py")):
            if any(p in py_file.parts for p in
                   {".git", ".venv", "venv", "node_modules", "__pycache__"}):
                continue
            try:
                source = py_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            lines = source.splitlines()
            n_lines = len(lines)

            # Arquivo grande
            if n_lines > 300:
                smells.append(CodeSmell(
                    type="large_file", file=str(py_file), line=1,
                    detail=f"Arquivo com {n_lines} linhas (máx. recomendado: 300)",
                    suggestion="Divida em módulos menores com responsabilidades únicas (SRP).",
                ))

            # Análise AST
            try:
                tree = ast.parse(source)
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    self._check_function(node, py_file, lines, smells, complexity)

            # Variáveis com nome curto (fora de loops)
            self._check_short_varnames(tree, py_file, smells)

            # Gargalos de memória (regex sobre linhas)
            self._check_memory(lines, py_file, mem_issues)

        return {
            "smells":     [vars(s) for s in smells],
            "complexity": [vars(c) for c in complexity],
            "mem_issues": [vars(m) for m in mem_issues],
            "summary": {
                "total_smells":     len(smells),
                "total_complex":    sum(1 for c in complexity if c.level == "COMPLEX"),
                "total_mem_issues": len(mem_issues),
            },
        }

    def _check_function(
        self, node: ast.FunctionDef, path: Path,
        lines: list[str], smells: list, complexity: list
    ) -> None:
        end_line   = getattr(node, "end_lineno", node.lineno + 10)
        func_lines = end_line - node.lineno + 1

        if func_lines > 50:
            smells.append(CodeSmell(
                type="long_function", file=str(path), line=node.lineno,
                detail=f"Função '{node.name}' tem {func_lines} linhas (máx. recomendado: 50)",
                suggestion=(
                    f"Extraia sub-funções de '{node.name}'. "
                    "Cada função deve fazer exatamente uma coisa."
                ),
            ))

        has_docstring = (
            node.body and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        )
        if not has_docstring and not node.name.startswith("_test"):
            smells.append(CodeSmell(
                type="no_docstring", file=str(path), line=node.lineno,
                detail=f"Função '{node.name}' sem docstring",
                suggestion=f"Adicione uma docstring descrevendo propósito, parâmetros e retorno de '{node.name}'.",
            ))

        cc = self._cyclomatic(node)
        if cc > 3:
            level = ("COMPLEXO" if cc >= 11 else "MODERADO" if cc >= 6 else "SIMPLES")
            complexity.append(ComplexityEntry(
                file=str(path), function=node.name,
                line=node.lineno, score=cc, level=level,
            ))

    @staticmethod
    def _cyclomatic(node: ast.FunctionDef) -> int:
        score = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For,
                                  ast.ExceptHandler, ast.With,
                                  ast.comprehension)):
                score += 1
            elif isinstance(child, ast.BoolOp):
                score += len(child.values) - 1
        return score

    @staticmethod
    def _check_short_varnames(tree: ast.AST, path: Path, smells: list) -> None:
        loop_vars: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.For,)):
                if isinstance(node.target, ast.Name):
                    loop_vars.add(node.target.id)

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if (isinstance(t, ast.Name)
                            and len(t.id) <= 2
                            and t.id not in loop_vars
                            and not t.id.startswith("_")):
                        smells.append(CodeSmell(
                            type="short_varname", file=str(path), line=node.lineno,
                            detail=f"Variável '{t.id}' com nome muito curto",
                            suggestion=f"Use um nome descritivo em vez de '{t.id}'.",
                        ))

    @staticmethod
    def _check_memory(lines: list[str], path: Path, issues: list) -> None:
        append_re  = re.compile(r'\.append\(')
        listcomp_re = re.compile(r'\[.*for\s+\w+\s+in\b')
        open_re    = re.compile(r'\bopen\s*\(')
        with_re    = re.compile(r'\bwith\s+open\s*\(')
        global_re  = re.compile(r'^\s*([A-Z_][A-Z0-9_]*)\s*=\s*([\[\{])')

        in_loop = False
        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            if re.match(r'^\s*(for|while)\b', line):
                in_loop = True
            if in_loop and append_re.search(line) and not listcomp_re.search(line):
                issues.append(MemoryIssue(
                    file=str(path), line=i, type="list_append_in_loop",
                    detail=f"append() em loop — linha {i}",
                ))
                in_loop = False

            if open_re.search(line) and not with_re.search(line):
                issues.append(MemoryIssue(
                    file=str(path), line=i, type="open_without_context",
                    detail=f"open() sem context manager (with) — linha {i}",
                ))

            m = global_re.match(line)
            if m:
                issues.append(MemoryIssue(
                    file=str(path), line=i, type="mutable_global",
                    detail=f"Variável global mutável '{m.group(1)}' — linha {i}",
                ))


# =============================================================================
# GERADOR HTML
# =============================================================================

def _smell_icon(t: str) -> str:
    return {"long_function": "📏", "no_docstring": "📝",
            "short_varname": "🔤", "large_file": "📦"}.get(t, "⚠️")


def _smell_label(t: str) -> str:
    return {"long_function": "Função Gigante", "no_docstring": "Sem Documentação",
            "short_varname": "Nome Confuso",   "large_file":   "Arquivo Grande"}.get(t, t)


def _mem_icon(t: str) -> str:
    return {"list_append_in_loop": "🔁", "open_without_context": "📂",
            "mutable_global": "🌐"}.get(t, "⚠️")


def _mem_label(t: str) -> str:
    return {
        "list_append_in_loop":   "append() em loop — prefira list comprehension",
        "open_without_context":  "open() sem 'with' — risco de file descriptor leak",
        "mutable_global":        "Variável global mutável — dificulta teste e concorrência",
    }.get(t, t)


def _cc_color(level: str) -> str:
    return {"SIMPLES": "#30d158", "MODERADO": "#ffd60a", "COMPLEXO": "#ff453a"}.get(level, "#fff")


def generate(audit_data: dict) -> str:
    audit_id = audit_data.get("audit_id", "—")
    project  = audit_data.get("project", "Projeto")
    date_str = audit_data.get("date", datetime.now(timezone.utc).isoformat())
    try:
        date_fmt = datetime.fromisoformat(date_str).strftime("%d/%m/%Y %H:%M UTC")
    except Exception:
        date_fmt = date_str

    project_path = audit_data.get("project_path")
    if project_path and Path(project_path).exists():
        perf = PerformanceAnalyzer().analyze(project_path)
    else:
        perf = {"smells": [], "complexity": [], "mem_issues": [],
                "summary": {"total_smells": 0, "total_complex": 0, "total_mem_issues": 0}}

    smells    = perf["smells"]
    complexity = sorted(perf["complexity"], key=lambda c: c["score"], reverse=True)
    mem_issues = perf["mem_issues"]
    summary   = perf["summary"]

    # ── build HTML sections ──────────────────────────────────────────────────

    # Code smells
    smells_by_type: dict[str, list] = {}
    for s in smells:
        smells_by_type.setdefault(s["type"], []).append(s)

    smells_html = ""
    for stype, items in smells_by_type.items():
        cards = ""
        for s in items:
            short = s["file"].replace("\\", "/").split("/")[-1]
            before_hint = ""
            if stype == "long_function":
                before_hint = f'<div class="code-before">def {s["detail"].split("\'")[1]}(): # {s["detail"].split(" ")[2]} linhas</div>'
                after_hint  = f'<div class="code-after">def {s["detail"].split("\'")[1]}_part1(): # dividir em funções menores</div>'
            elif stype == "no_docstring":
                fname = s["detail"].split("'")[1]
                before_hint = f'<div class="code-before">def {fname}():\n    pass  # sem documentação</div>'
                after_hint  = f'<div class="code-after">def {fname}():\n    """Descreva o propósito aqui."""\n    pass</div>'
            else:
                after_hint = f'<div class="code-after"># {s["suggestion"]}</div>'

            cards += f"""
<div class="smell-card">
  <div class="smell-header">
    <span>{_smell_icon(stype)} {_smell_label(stype)}</span>
    <span class="smell-loc">📄 {short}:{s["line"]}</span>
  </div>
  <div class="smell-detail">{s["detail"]}</div>
  <div class="refactor-wrap">
    {before_hint}
    {after_hint}
  </div>
</div>"""
        smells_html += f'<div class="smell-group"><h4>{_smell_icon(stype)} {_smell_label(stype)} ({len(items)})</h4>{cards}</div>'

    if not smells_html:
        smells_html = '<p class="empty-msg">✅ Nenhum code smell detectado nos arquivos Python.</p>'

    # Complexidade ciclomática
    if complexity:
        rows = "".join(f"""
<tr>
  <td style="color:#60c0ff;">{e["file"].replace(chr(92),"/").split("/")[-1]}</td>
  <td>{e["function"]}</td>
  <td style="text-align:center;">{e["line"]}</td>
  <td style="text-align:center;font-weight:700;color:{_cc_color(e["level"])};">{e["score"]}</td>
  <td><span class="cc-badge cc-{e['level'].lower()}">{e["level"]}</span></td>
</tr>""" for e in complexity[:20])
        cc_html = f"""
<table class="cc-table">
  <thead><tr>
    <th>Arquivo</th><th>Função</th><th>Linha</th><th>CC</th><th>Nível</th>
  </tr></thead>
  <tbody>{rows}</tbody>
</table>"""
    else:
        cc_html = '<p class="empty-msg">✅ Sem funções de alta complexidade detectadas.</p>'

    # Memória
    if mem_issues:
        mem_html = "".join(f"""
<div class="mem-card">
  <span>{_mem_icon(m["type"])}</span>
  <div>
    <div class="mem-label">{_mem_label(m["type"])}</div>
    <div class="mem-loc">📄 {m["file"].replace(chr(92),"/").split("/")[-1]}:{m["line"]}</div>
  </div>
</div>""" for m in mem_issues[:20])
    else:
        mem_html = '<p class="empty-msg">✅ Nenhum gargalo de memória detectado.</p>'

    # Stat cards
    def stat_card(label: str, value: int, color: str) -> str:
        return f'<div class="stat-card"><div class="stat-val" style="color:{color}">{value}</div><div class="stat-lbl">{label}</div></div>'

    stats_html = (
        stat_card("Code Smells",       summary["total_smells"],      "#ffd60a") +
        stat_card("Funções Complexas", summary["total_complex"],     "#ff453a") +
        stat_card("Gargalos Memória",  summary["total_mem_issues"],  "#ff9f0a")
    )

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Laudo de Performance AUDITX — {project}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet"/>
<style>
:root{{--bg:#0a0a0a;--surf:rgba(255,255,255,.05);--border:rgba(255,255,255,.10);
  --text:#f0f0f0;--muted:rgba(255,255,255,.45);--accent:#ff9f0a;}}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;line-height:1.6;padding:0 0 60px;}}
.page{{max-width:900px;margin:0 auto;padding:0 24px;}}
.report-header{{background:linear-gradient(135deg,#0f0a00 0%,#0a0a0a 100%);
  border-bottom:1px solid var(--border);padding:40px 0 32px;margin-bottom:40px;}}
.report-header .page{{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px;}}
.brand{{font-size:26px;font-weight:900;letter-spacing:-1px;}}
.brand span{{color:#ff9f0a;}}
.report-type{{font-size:13px;color:var(--muted);margin-top:4px;}}
.meta{{text-align:right;font-size:12px;color:var(--muted);line-height:1.8;}}
.section{{margin-bottom:36px;}}
.section-title{{font-size:14px;font-weight:700;text-transform:uppercase;
  letter-spacing:1.5px;color:var(--muted);margin-bottom:16px;
  padding-bottom:8px;border-bottom:1px solid var(--border);}}
.card{{background:var(--surf);border:1px solid var(--border);border-radius:14px;padding:24px;}}
/* stats */
.stats-row{{display:flex;gap:16px;flex-wrap:wrap;}}
.stat-card{{flex:1;min-width:140px;background:var(--surf);border:1px solid var(--border);
  border-radius:12px;padding:20px;text-align:center;}}
.stat-val{{font-size:40px;font-weight:900;line-height:1;}}
.stat-lbl{{font-size:12px;color:var(--muted);margin-top:6px;}}
/* smells */
.smell-group{{margin-bottom:24px;}}
.smell-group h4{{font-size:13px;font-weight:700;color:var(--muted);
  text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;}}
.smell-card{{background:rgba(255,255,255,.03);border:1px solid var(--border);
  border-radius:10px;padding:14px;margin-bottom:8px;}}
.smell-header{{display:flex;justify-content:space-between;align-items:center;
  margin-bottom:6px;font-size:13px;font-weight:600;}}
.smell-loc{{font-size:11px;color:#60c0ff;}}
.smell-detail{{font-size:12px;color:var(--muted);margin-bottom:8px;}}
.refactor-wrap{{display:flex;gap:8px;flex-wrap:wrap;}}
.code-before,.code-after{{flex:1;min-width:200px;font-family:'Courier New',monospace;
  font-size:11px;padding:8px 12px;border-radius:6px;white-space:pre-wrap;line-height:1.6;}}
.code-before{{background:rgba(255,69,58,.1);border:1px solid rgba(255,69,58,.3);color:#ff8080;}}
.code-after{{background:rgba(48,209,88,.1);border:1px solid rgba(48,209,88,.3);color:#80ff80;}}
/* complexity table */
.cc-table{{width:100%;border-collapse:collapse;font-size:13px;}}
.cc-table th{{text-align:left;padding:10px 12px;border-bottom:2px solid var(--border);
  color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:1px;}}
.cc-table td{{padding:10px 12px;border-bottom:1px solid rgba(255,255,255,.05);}}
.cc-badge{{font-size:10px;font-weight:700;padding:3px 8px;border-radius:20px;}}
.cc-simples{{background:rgba(48,209,88,.15);color:#30d158;border:1px solid rgba(48,209,88,.3);}}
.cc-moderado{{background:rgba(255,214,10,.15);color:#ffd60a;border:1px solid rgba(255,214,10,.3);}}
.cc-complexo{{background:rgba(255,69,58,.15);color:#ff453a;border:1px solid rgba(255,69,58,.3);}}
/* memory */
.mem-card{{display:flex;gap:12px;align-items:flex-start;padding:12px;
  background:rgba(255,159,10,.06);border:1px solid rgba(255,159,10,.2);
  border-radius:8px;margin-bottom:8px;font-size:13px;}}
.mem-label{{font-weight:500;}}
.mem-loc{{font-size:11px;color:#60c0ff;margin-top:2px;}}
.empty-msg{{font-size:13px;color:var(--muted);font-style:italic;text-align:center;padding:16px;}}
.report-footer{{margin-top:48px;padding-top:24px;border-top:1px solid var(--border);
  text-align:center;font-size:12px;color:var(--muted);}}
</style>
</head>
<body>

<div class="report-header">
  <div class="page">
    <div>
      <div class="brand">AUDIT<span>X</span></div>
      <div class="report-type">⚡ Laudo de Performance — Eficiência</div>
    </div>
    <div class="meta">
      <div><strong>Projeto:</strong> {project}</div>
      <div><strong>Auditoria:</strong> {audit_id[:16]}…</div>
      <div><strong>Data:</strong> {date_fmt}</div>
    </div>
  </div>
</div>

<div class="page">

  <div class="section">
    <div class="section-title">Resumo de Qualidade</div>
    <div class="stats-row">{stats_html}</div>
  </div>

  <div class="section">
    <div class="section-title">Code Smells Detectados</div>
    {smells_html}
  </div>

  <div class="section">
    <div class="section-title">Complexidade Ciclomática por Função</div>
    <div class="card">{cc_html}</div>
  </div>

  <div class="section">
    <div class="section-title">Gargalos de Memória & I/O</div>
    {mem_html}
  </div>

</div>

<div class="page">
  <div class="report-footer">
    Gerado por <strong>AUDITX</strong> — auditor.nexora360.cloud &nbsp;·&nbsp;
    {datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")}
  </div>
</div>

</body>
</html>"""
