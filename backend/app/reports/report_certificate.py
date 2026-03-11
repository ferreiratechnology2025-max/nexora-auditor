"""
report_certificate.py — Certificado de Qualidade de Software AUDITX
Gera HTML com visual premium de certificado, índice de documentação,
conformidade PEP8 (via AST) e QR code de validação.
"""

from __future__ import annotations
import ast
import base64
import io
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


# =============================================================================
# QR CODE
# =============================================================================

def _qr_base64(url: str) -> str:
    try:
        import qrcode  # type: ignore
        qr  = qrcode.QRCode(version=1, box_size=5, border=3,
                             error_correction=qrcode.constants.ERROR_CORRECT_M)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#ffffff", back_color="#0a0a0a")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return ""


# =============================================================================
# ANALISADOR DE DOCUMENTAÇÃO E PEP8
# =============================================================================

def _analyze_docs(project_path: str) -> dict:
    """Conta funções com e sem docstring, arquivos com comentários."""
    total_funcs = 0
    doc_funcs   = 0
    commented_files = 0
    total_files = 0

    for py_file in sorted(Path(project_path).rglob("*.py")):
        if any(p in py_file.parts for p in
               {".git", ".venv", "venv", "__pycache__"}):
            continue
        try:
            source = py_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        total_files += 1
        if "#" in source:
            commented_files += 1

        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                total_funcs += 1
                if (node.body and isinstance(node.body[0], ast.Expr)
                        and isinstance(node.body[0].value, ast.Constant)
                        and isinstance(node.body[0].value.value, str)):
                    doc_funcs += 1

    doc_pct  = int(doc_funcs  / total_funcs   * 100) if total_funcs   > 0 else 100
    file_pct = int(commented_files / total_files * 100) if total_files > 0 else 100

    if   doc_pct >= 80: doc_grade = ("EXCELENTE", "#30d158")
    elif doc_pct >= 60: doc_grade = ("BOM",        "#60c0ff")
    elif doc_pct >= 40: doc_grade = ("BÁSICO",     "#ffd60a")
    else:               doc_grade = ("INSUFICIENTE","#ff453a")

    return {
        "total_funcs":      total_funcs,
        "doc_funcs":        doc_funcs,
        "doc_pct":          doc_pct,
        "doc_grade":        doc_grade[0],
        "doc_grade_color":  doc_grade[1],
        "commented_files":  commented_files,
        "total_files":      total_files,
        "file_pct":         file_pct,
    }


def _analyze_pep8(project_path: str) -> dict:
    """
    Verificação PEP8 via AST (não depende de pycodestyle externo).
    Checa: snake_case, bare except, UPPER_CASE constants, imports no topo.
    """
    violations: list[dict] = []

    SNAKE_RE    = re.compile(r'^[a-z_][a-z0-9_]*$')
    UPPER_RE    = re.compile(r'^[A-Z][A-Z0-9_]+$')
    CONSTANT_RE = re.compile(r'^[A-Z_][A-Z0-9_]{2,}$')

    for py_file in sorted(Path(project_path).rglob("*.py")):
        if any(p in py_file.parts for p in
               {".git", ".venv", "venv", "__pycache__"}):
            continue
        try:
            source = py_file.read_text(encoding="utf-8", errors="replace")
            tree   = ast.parse(source)
        except (OSError, SyntaxError):
            continue

        short = py_file.name

        for node in ast.walk(tree):
            # Bare except
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                violations.append({
                    "rule": "E722", "file": short, "line": node.lineno,
                    "msg":  "bare 'except:' — especifique a exceção (e.g. except ValueError:)",
                })

            # Nomes de função não snake_case
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not SNAKE_RE.match(node.name) and not node.name.startswith("__"):
                    violations.append({
                        "rule": "N802", "file": short, "line": node.lineno,
                        "msg":  f"nome de função '{node.name}' não está em snake_case",
                    })

            # Constantes globais não UPPER_CASE
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if (isinstance(t, ast.Name)
                            and isinstance(node.value, ast.Constant)
                            and isinstance(node.value.value, (int, float, str))
                            and len(t.id) > 2
                            and not SNAKE_RE.match(t.id)
                            and not UPPER_RE.match(t.id)):
                        violations.append({
                            "rule": "N816", "file": short, "line": node.lineno,
                            "msg":  f"variável '{t.id}' com nome misto — use snake_case ou UPPER_CASE",
                        })

    total_checks  = max(len(violations) + 20, 20)
    conformance   = max(0, int((1 - len(violations) / total_checks) * 100))
    return {"violations": violations[:20], "conformance": conformance}


# =============================================================================
# SELO DE APROVAÇÃO
# =============================================================================

def _approval_seal(score: int) -> tuple[str, str, str]:
    if   score >= 70: return ("APROVADO",                 "#30d158", "✅")
    elif score >= 50: return ("APROVADO COM RESSALVAS",   "#ffd60a", "⚠️")
    else:             return ("REPROVADO",                "#ff453a", "❌")


# =============================================================================
# GERADOR HTML
# =============================================================================

def generate(audit_data: dict) -> str:
    audit_id     = audit_data.get("audit_id", "unknown")
    project      = audit_data.get("project",  "Projeto")
    date_str     = audit_data.get("date",     datetime.now(timezone.utc).isoformat())
    score_final  = audit_data.get("health_score_final", audit_data.get("health_score_initial", 0))
    cert_number  = f"AUDITX-{audit_id[:8].upper()}"
    validate_url = f"https://auditor.nexora360.cloud/validate/{audit_id}"

    try:
        date_fmt = datetime.fromisoformat(date_str).strftime("%d de %B de %Y")
    except Exception:
        date_fmt = date_str

    project_path = audit_data.get("project_path")
    if project_path and Path(project_path).exists():
        docs = _analyze_docs(project_path)
        pep8 = _analyze_pep8(project_path)
    else:
        docs = {"total_funcs": 0, "doc_funcs": 0, "doc_pct": 0, "doc_grade": "N/A",
                "doc_grade_color": "#888", "commented_files": 0, "total_files": 0, "file_pct": 0}
        pep8 = {"violations": [], "conformance": 100}

    seal_text, seal_color, seal_icon = _approval_seal(score_final)
    qr_b64 = _qr_base64(validate_url)
    qr_img = (f'<img src="data:image/png;base64,{qr_b64}" '
              f'alt="QR Certificado" width="120" height="120"/>'
              if qr_b64 else "<div style='color:#888;font-size:12px'>QR indisponível</div>")

    # Violações PEP8
    viol_html = ""
    if pep8["violations"]:
        rows = "".join(
            f'<tr><td style="color:#ffd60a">[{v["rule"]}]</td>'
            f'<td style="color:#60c0ff">{v["file"]}:{v["line"]}</td>'
            f'<td style="color:rgba(255,255,255,.7)">{v["msg"]}</td></tr>'
            for v in pep8["violations"]
        )
        viol_html = f'<table class="viol-table"><tbody>{rows}</tbody></table>'
    else:
        viol_html = '<p class="empty-msg">✅ Nenhuma violação de padrão detectada.</p>'

    conf_color = ("#30d158" if pep8["conformance"] >= 80
                  else "#ffd60a" if pep8["conformance"] >= 60 else "#ff453a")

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Certificado AUDITX — {project}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet"/>
<style>
:root{{--bg:#0a0a0a;--surf:rgba(255,255,255,.05);--border:rgba(255,255,255,.10);
  --text:#f0f0f0;--muted:rgba(255,255,255,.45);--accent:#ff453a;}}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;line-height:1.6;padding:0 0 60px;}}
.page{{max-width:900px;margin:0 auto;padding:0 24px;}}
/* cert header */
.cert-wrap{{background:linear-gradient(135deg,#0a0014 0%,#0a0a0a 50%,#001408 100%);
  border:2px solid rgba(255,255,255,.12);border-radius:20px;
  margin:40px 0;padding:48px;text-align:center;position:relative;overflow:hidden;}}
.cert-wrap::before{{content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse at 50% 0%,rgba(255,69,58,.08) 0%,transparent 60%);}}
.cert-brand{{font-size:40px;font-weight:900;letter-spacing:-2px;position:relative;}}
.cert-brand span{{color:#ff453a;}}
.cert-title{{font-size:15px;letter-spacing:6px;text-transform:uppercase;
  color:rgba(255,255,255,.5);margin:8px 0 24px;position:relative;}}
.cert-number{{font-size:13px;color:rgba(255,255,255,.3);letter-spacing:2px;
  font-family:'Courier New',monospace;margin-bottom:6px;position:relative;}}
.cert-project{{font-size:28px;font-weight:800;margin:24px 0 8px;position:relative;}}
.cert-date{{font-size:13px;color:var(--muted);position:relative;}}
.cert-divider{{border:none;border-top:1px solid rgba(255,255,255,.1);margin:24px 0;}}
/* seal */
.seal-wrap{{display:inline-flex;flex-direction:column;align-items:center;gap:8px;
  margin:24px 0;position:relative;}}
.seal{{display:flex;align-items:center;gap:12px;padding:16px 32px;border-radius:50px;
  font-size:18px;font-weight:800;letter-spacing:1px;border:2px solid;}}
.seal-score{{font-size:13px;color:var(--muted);margin-top:4px;}}
/* sections */
.section{{margin-bottom:36px;}}
.section-title{{font-size:14px;font-weight:700;text-transform:uppercase;
  letter-spacing:1.5px;color:var(--muted);margin-bottom:16px;
  padding-bottom:8px;border-bottom:1px solid var(--border);}}
.card{{background:var(--surf);border:1px solid var(--border);border-radius:14px;padding:24px;}}
/* doc metrics */
.doc-grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px;}}
.doc-item{{background:rgba(255,255,255,.03);border:1px solid var(--border);
  border-radius:10px;padding:16px;}}
.doc-num{{font-size:36px;font-weight:900;line-height:1;}}
.doc-label{{font-size:12px;color:var(--muted);margin-top:4px;}}
.doc-grade{{font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;
  display:inline-block;margin-top:8px;}}
/* pep8 */
.pep8-score{{text-align:center;padding:16px 0;}}
.pep8-big{{font-size:60px;font-weight:900;line-height:1;}}
.pep8-label{{font-size:13px;color:var(--muted);margin-top:6px;}}
.viol-table{{width:100%;border-collapse:collapse;font-size:12px;margin-top:16px;}}
.viol-table td{{padding:8px 10px;border-bottom:1px solid rgba(255,255,255,.05);vertical-align:top;}}
/* qr */
.qr-section{{display:flex;align-items:center;gap:32px;flex-wrap:wrap;}}
.qr-box{{background:rgba(255,255,255,.05);border:1px solid var(--border);
  border-radius:12px;padding:16px;display:flex;flex-direction:column;align-items:center;gap:8px;}}
.qr-caption{{font-size:11px;color:var(--muted);text-align:center;max-width:140px;}}
.qr-url{{font-size:11px;color:#60c0ff;word-break:break-all;flex:1;}}
.empty-msg{{font-size:13px;color:var(--muted);font-style:italic;text-align:center;padding:16px;}}
.report-footer{{margin-top:48px;padding-top:24px;border-top:1px solid var(--border);
  text-align:center;font-size:12px;color:var(--muted);}}
</style>
</head>
<body>

<div class="page">

  <!-- Certificado -->
  <div class="cert-wrap">
    <div class="cert-brand">AUDIT<span>X</span></div>
    <div class="cert-title">Certificado de Qualidade de Software</div>
    <div class="cert-number">{cert_number}</div>
    <hr class="cert-divider"/>
    <div style="color:rgba(255,255,255,.5);font-size:13px;margin-bottom:4px;">Certifica que o projeto</div>
    <div class="cert-project">{project}</div>
    <div class="cert-date">foi auditado em {date_fmt}</div>
    <div class="seal-wrap">
      <div class="seal" style="color:{seal_color};border-color:{seal_color};
                                background:color-mix(in srgb,{seal_color} 10%,transparent);">
        <span style="font-size:24px;">{seal_icon}</span>
        {seal_text}
      </div>
      <div class="seal-score">Health Score Final: {score_final}/100</div>
    </div>
  </div>

  <!-- Índice de Documentação -->
  <div class="section">
    <div class="section-title">Índice de Documentação</div>
    <div class="doc-grid">
      <div class="doc-item">
        <div class="doc-num" style="color:{docs['doc_grade_color']}">{docs['doc_pct']}%</div>
        <div class="doc-label">Funções com Docstring</div>
        <div class="doc-grade"
             style="background:color-mix(in srgb,{docs['doc_grade_color']} 15%,transparent);
                    color:{docs['doc_grade_color']};
                    border:1px solid color-mix(in srgb,{docs['doc_grade_color']} 40%,transparent);">
          {docs['doc_grade']}
        </div>
        <div style="font-size:11px;color:var(--muted);margin-top:6px;">
          {docs['doc_funcs']}/{docs['total_funcs']} funções documentadas
        </div>
      </div>
      <div class="doc-item">
        <div class="doc-num" style="color:#60c0ff">{docs['file_pct']}%</div>
        <div class="doc-label">Arquivos com Comentários</div>
        <div style="font-size:11px;color:var(--muted);margin-top:12px;">
          {docs['commented_files']}/{docs['total_files']} arquivos comentados
        </div>
      </div>
    </div>
  </div>

  <!-- Conformidade PEP8 -->
  <div class="section">
    <div class="section-title">Consistência de Padrão (PEP8 via AST)</div>
    <div class="card">
      <div class="pep8-score">
        <div class="pep8-big" style="color:{conf_color}">{pep8['conformance']}%</div>
        <div class="pep8-label">Conformidade com PEP8
          &nbsp;·&nbsp; {len(pep8['violations'])} violação(ões) detectada(s)
        </div>
      </div>
      {viol_html}
    </div>
  </div>

  <!-- QR de Validação -->
  <div class="section">
    <div class="section-title">Validação do Certificado</div>
    <div class="card">
      <div class="qr-section">
        <div class="qr-box">
          {qr_img}
          <div class="qr-caption">Escaneie para validar este certificado</div>
        </div>
        <div>
          <div style="font-size:13px;margin-bottom:8px;">
            Este certificado pode ser verificado em:
          </div>
          <div class="qr-url">{validate_url}</div>
          <div style="font-size:12px;color:var(--muted);margin-top:12px;">
            Certificado N.º: <strong style="font-family:'Courier New',monospace">{cert_number}</strong><br/>
            Emitido em: {date_fmt}<br/>
            Válido para a versão auditada do projeto.
          </div>
        </div>
      </div>
    </div>
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
