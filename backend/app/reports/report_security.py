"""
report_security.py — Laudo de Segurança (Blindagem)
Gera HTML interativo com score de risco, mapa de calor, achados e checklist LGPD.
"""

from __future__ import annotations
import math
from datetime import datetime, timezone


# ── helpers visuais ───────────────────────────────────────────────────────────

def _score_color(score: int) -> str:
    if score >= 80:  return "#30d158"
    if score >= 50:  return "#ffd60a"
    return "#ff453a"


def _score_label(score: int) -> str:
    if score >= 80:  return "SEGURO"
    if score >= 50:  return "ATENÇÃO"
    return "CRÍTICO"


def _svg_gauge(score: int) -> str:
    color = _score_color(score)
    label = _score_label(score)
    r     = 70
    circ  = 2 * math.pi * r
    off   = circ * (1 - score / 100)
    label_color = color
    return f"""
<div class="gauge-wrap">
  <svg width="180" height="180" viewBox="0 0 180 180">
    <circle cx="90" cy="90" r="{r}" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="14"/>
    <circle cx="90" cy="90" r="{r}" fill="none" stroke="{color}" stroke-width="14"
            stroke-dasharray="{circ:.2f}" stroke-dashoffset="{circ:.2f}"
            stroke-linecap="round" transform="rotate(-90 90 90)"
            style="transition:stroke-dashoffset 1.4s cubic-bezier(.4,0,.2,1);"
            data-target="{off:.2f}" id="gaugeCircle"/>
    <text x="90" y="83" text-anchor="middle" fill="white"
          font-size="28" font-weight="800" font-family="Inter,sans-serif">{score}</text>
    <text x="90" y="103" text-anchor="middle" fill="rgba(255,255,255,0.4)"
          font-size="11" font-family="Inter,sans-serif">/100</text>
  </svg>
  <div class="gauge-label" style="color:{label_color}">{label}</div>
</div>
<script>
  (function(){{
    var c=document.getElementById('gaugeCircle');
    if(!c) return;
    var target=parseFloat(c.getAttribute('data-target'));
    setTimeout(function(){{ c.style.strokeDashoffset=target; }}, 200);
  }})();
</script>"""


def _heatmap_row(label: str, color: str, count: int, max_count: int) -> str:
    if max_count == 0:
        pct = 0
    else:
        pct = min(100, int((count / max_count) * 100))
    return f"""
<tr>
  <td class="sev-label" style="color:{color}">{label}</td>
  <td class="bar-cell">
    <div class="bar-bg">
      <div class="bar-fill" style="width:{pct}%;background:{color};"></div>
    </div>
  </td>
  <td class="count-cell" style="color:{color}">{count}</td>
</tr>"""


def _finding_card(f: dict, fixed_keys: set) -> str:
    key      = (f["file"], f["line"], f["category"])
    is_fixed = key in fixed_keys
    badge    = ('<span class="badge green">CORRIGIDO ✅</span>'
                if is_fixed else '<span class="badge red">MANUAL ⚠️</span>')
    short_file = f["file"].replace("\\", "/").split("/")[-1]
    diff_html  = ""
    return f"""
<div class="finding-card">
  <div class="finding-header">
    <span class="finding-file">📄 {short_file}</span>
    <span class="finding-line">linha {f["line"]}</span>
    {badge}
  </div>
  <div class="finding-desc">{f["description"]}</div>
  <div class="finding-suggestion">💡 {f["suggestion"]}</div>
  {diff_html}
</div>"""


def _finding_card_with_diff(f: dict, fixed: list) -> str:
    key = (f["file"], f["line"], f["category"])
    matched = next((fx for fx in fixed
                    if fx["file"] == f["file"] and fx["line"] == f["line"]
                    and fx["category"] == f["category"]), None)

    is_fixed  = matched is not None
    badge     = ('<span class="badge green">CORRIGIDO ✅</span>'
                 if is_fixed else '<span class="badge red">MANUAL ⚠️</span>')
    short_file = f["file"].replace("\\", "/").split("/")[-1]

    diff_html = ""
    if matched and matched.get("diff"):
        lines_html = []
        for line in matched["diff"].splitlines():
            if line.startswith("+++") or line.startswith("---"):
                lines_html.append(f'<span class="diff-meta">{line}</span>')
            elif line.startswith("+"):
                lines_html.append(f'<span class="diff-add">{line}</span>')
            elif line.startswith("-"):
                lines_html.append(f'<span class="diff-del">{line}</span>')
            else:
                lines_html.append(f'<span class="diff-ctx">{line}</span>')
        diff_html = f'<div class="diff-block"><pre>{"<br>".join(lines_html)}</pre></div>'

    return f"""
<div class="finding-card">
  <div class="finding-header">
    <span class="finding-file">📄 {short_file}</span>
    <span class="finding-line">linha {f["line"]}</span>
    {badge}
  </div>
  <div class="finding-desc">{f["description"]}</div>
  <div class="finding-suggestion">💡 {f["suggestion"]}</div>
  {diff_html}
</div>"""


def _secret_row(f: dict, fixed: list) -> str:
    matched = next((fx for fx in fixed
                    if fx["file"] == f["file"] and fx["line"] == f["line"]), None)
    is_fixed   = matched is not None
    badge      = ('<span class="badge green">CORRIGIDO ✅</span>'
                  if is_fixed else '<span class="badge exposed">EXPOSTO 🔴</span>')
    short_file = f["file"].replace("\\", "/").split("/")[-1]
    desc_low   = f["description"].lower()
    kind = ("TOKEN"   if "token" in desc_low
            else "API_KEY" if "api_key" in desc_low or "apikey" in desc_low
            else "PASSWORD")
    return f"""
<tr>
  <td>📄 {short_file}:{f["line"]}</td>
  <td><code>{kind}</code></td>
  <td>{badge}</td>
</tr>"""


def _lgpd_checklist(findings: list, fixed: list) -> str:
    categories = {f["category"] for f in findings}
    fixed_cats = {fx["category"] for fx in fixed if fx["status"] == "fixed"}

    sql_found    = "sql_injection" in categories
    secret_found = "hardcoded_secret" in categories
    xss_found    = "xss" in categories
    sql_fixed    = sql_found and "sql_injection" in fixed_cats
    secret_fixed = secret_found and "hardcoded_secret" in fixed_cats

    rows = []

    if not secret_found:
        rows.append(("✅", "green",  "Sem senhas hardcoded detectadas"))
        rows.append(("✅", "green",  "Sem tokens de API expostos"))
    elif secret_fixed:
        rows.append(("✅", "green",  "Senhas hardcoded corrigidas via auto-fix"))
    else:
        rows.append(("❌", "red",    "Segredos hardcoded detectados — corrija manualmente"))

    rows.append(("⚠️",  "yellow", "Verificar criptografia de dados pessoais em repouso"))
    rows.append(("⚠️",  "yellow", "Verificar logs — garantir ausência de dados sensíveis"))

    if not sql_found:
        rows.append(("✅", "green",  "SQL injection não detectado"))
    elif sql_fixed:
        rows.append(("✅", "green",  "SQL injection corrigido com queries parametrizadas"))
    else:
        rows.append(("❌", "red",    "SQL injection detectado — risco de vazamento de dados"))

    if xss_found:
        rows.append(("❌", "red",    "XSS detectado — risco de execução de scripts maliciosos"))
    else:
        rows.append(("✅", "green",  "XSS não detectado"))

    rows.append(("⚠️",  "yellow", "Revisar política de retenção e exclusão de dados (LGPD Art. 15)"))

    items = "\n".join(
        f'<li class="lgpd-{color}"><span class="lgpd-icon">{icon}</span>{text}</li>'
        for icon, color, text in rows
    )
    return f"<ul class='lgpd-list'>{items}</ul>"


# ── gerador principal ─────────────────────────────────────────────────────────

def generate(audit_data: dict) -> str:
    score_i = audit_data.get("health_score_initial", 0)
    score_f = audit_data.get("health_score_final", score_i)
    audit_id = audit_data.get("audit_id", "—")
    project  = audit_data.get("project", "Projeto")
    date_str = audit_data.get("date", datetime.now(timezone.utc).isoformat())
    try:
        date_fmt = datetime.fromisoformat(date_str).strftime("%d/%m/%Y %H:%M UTC")
    except Exception:
        date_fmt = date_str

    findings = audit_data.get("findings", [])
    fixed    = audit_data.get("fixed", [])
    skipped  = audit_data.get("skipped", [])

    by_sev   = audit_data.get("by_severity", {})
    n_crit   = by_sev.get("CRITICAL", 0)
    n_high   = by_sev.get("HIGH", 0)
    n_med    = by_sev.get("MEDIUM", 0)
    n_low    = by_sev.get("LOW", 0)
    max_n    = max(n_crit, n_high, n_med, n_low, 1)

    # Seções de achados
    injection_cats = {"sql_injection", "dangerous_eval", "xss"}
    injection_findings = [f for f in findings if f["category"] in injection_cats]
    secret_findings    = [f for f in findings if f["category"] == "hardcoded_secret"]

    injection_html = (
        "".join(_finding_card_with_diff(f, fixed) for f in injection_findings)
        or '<p class="empty-msg">✅ Nenhum achado de injeção detectado.</p>'
    )
    secrets_rows = (
        "".join(_secret_row(f, fixed) for f in secret_findings)
        or '<tr><td colspan="3" class="empty-msg">✅ Nenhum segredo exposto detectado.</td></tr>'
    )

    gauge_html    = _svg_gauge(score_f)
    heatmap_html  = (
        _heatmap_row("Crítico",  "#ff453a", n_crit, max_n) +
        _heatmap_row("Alto",     "#ff9f0a", n_high, max_n) +
        _heatmap_row("Médio",    "#ffd60a", n_med,  max_n) +
        _heatmap_row("Baixo",    "#30d158", n_low,  max_n)
    )
    lgpd_html = _lgpd_checklist(findings, fixed)

    delta      = score_f - score_i
    delta_sign = f"+{delta}" if delta >= 0 else str(delta)
    delta_col  = "#30d158" if delta >= 0 else "#ff453a"

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Laudo de Segurança AUDITX — {project}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet"/>
<style>
:root{{--bg:#0a0a0a;--surf:rgba(255,255,255,.05);--border:rgba(255,255,255,.10);
--text:#f0f0f0;--muted:rgba(255,255,255,.45);--accent:#ff453a;
--green:#30d158;--yellow:#ffd60a;--red:#ff453a;--orange:#ff9f0a;}}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;
      line-height:1.6;padding:0 0 60px;}}
.page{{max-width:900px;margin:0 auto;padding:0 24px;}}
/* ── header ── */
.report-header{{background:linear-gradient(135deg,#1a0a0a 0%,#0a0a0a 100%);
  border-bottom:1px solid var(--border);padding:40px 0 32px;margin-bottom:40px;}}
.report-header .page{{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px;}}
.brand{{font-size:26px;font-weight:900;letter-spacing:-1px;}}
.brand span{{color:var(--accent);}}
.report-type{{font-size:13px;color:var(--muted);margin-top:4px;}}
.meta{{text-align:right;font-size:12px;color:var(--muted);line-height:1.8;}}
/* ── section ── */
.section{{margin-bottom:36px;}}
.section-title{{font-size:14px;font-weight:700;text-transform:uppercase;
  letter-spacing:1.5px;color:var(--muted);margin-bottom:16px;
  padding-bottom:8px;border-bottom:1px solid var(--border);}}
/* ── glass card ── */
.card{{background:var(--surf);border:1px solid var(--border);border-radius:14px;padding:24px;}}
/* ── score band ── */
.score-band{{display:flex;align-items:center;gap:40px;flex-wrap:wrap;}}
.gauge-wrap{{text-align:center;}}
.gauge-label{{font-size:13px;font-weight:700;letter-spacing:1px;margin-top:8px;}}
.score-meta{{flex:1;}}
.score-row{{display:flex;align-items:baseline;gap:8px;margin-bottom:6px;}}
.score-big{{font-size:48px;font-weight:900;line-height:1;}}
.score-arrow{{font-size:20px;color:var(--muted);}}
.score-delta{{font-size:20px;font-weight:700;}}
.score-sub{{font-size:13px;color:var(--muted);}}
/* ── heatmap ── */
.heatmap{{width:100%;border-collapse:collapse;}}
.heatmap td{{padding:10px 12px;}}
.sev-label{{font-size:13px;font-weight:600;width:90px;}}
.bar-cell{{width:100%;}}
.bar-bg{{background:rgba(255,255,255,.08);border-radius:4px;height:18px;overflow:hidden;}}
.bar-fill{{height:100%;border-radius:4px;transition:width 1s ease;}}
.count-cell{{font-size:15px;font-weight:700;width:50px;text-align:right;}}
/* ── findings ── */
.finding-card{{background:rgba(255,255,255,.03);border:1px solid var(--border);
  border-radius:10px;padding:16px;margin-bottom:12px;}}
.finding-header{{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:8px;}}
.finding-file{{font-size:13px;font-weight:600;color:#60c0ff;}}
.finding-line{{font-size:12px;color:var(--muted);background:rgba(255,255,255,.06);
  padding:2px 8px;border-radius:20px;}}
.finding-desc{{font-size:13px;color:var(--text);margin-bottom:6px;}}
.finding-suggestion{{font-size:12px;color:var(--muted);font-style:italic;}}
.badge{{font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;}}
.badge.green{{background:rgba(48,209,88,.15);color:#30d158;border:1px solid rgba(48,209,88,.3);}}
.badge.red{{background:rgba(255,69,58,.15);color:#ff453a;border:1px solid rgba(255,69,58,.3);}}
.badge.exposed{{background:rgba(255,69,58,.2);color:#ff453a;border:1px solid rgba(255,69,58,.4);}}
/* ── diff ── */
.diff-block{{margin-top:10px;background:#0d1117;border:1px solid #30363d;
  border-radius:6px;overflow:hidden;}}
.diff-block pre{{font-size:11px;font-family:'Courier New',monospace;line-height:1.7;padding:10px 14px;overflow-x:auto;}}
.diff-add{{display:block;background:rgba(48,209,88,.12);color:#30d158;}}
.diff-del{{display:block;background:rgba(255,69,58,.12);color:#ff453a;}}
.diff-meta{{display:block;color:rgba(255,255,255,.3);}}
.diff-ctx{{display:block;color:rgba(255,255,255,.5);}}
/* ── secrets table ── */
.secrets-table{{width:100%;border-collapse:collapse;font-size:13px;}}
.secrets-table td{{padding:10px 12px;border-bottom:1px solid var(--border);}}
.secrets-table td:first-child{{color:#60c0ff;}}
.secrets-table code{{background:rgba(255,255,255,.08);padding:2px 8px;
  border-radius:4px;font-size:11px;}}
/* ── lgpd ── */
.lgpd-list{{list-style:none;display:flex;flex-direction:column;gap:10px;}}
.lgpd-list li{{display:flex;align-items:flex-start;gap:10px;font-size:13px;padding:10px 14px;border-radius:8px;}}
.lgpd-green{{background:rgba(48,209,88,.08);border:1px solid rgba(48,209,88,.2);}}
.lgpd-yellow{{background:rgba(255,214,10,.06);border:1px solid rgba(255,214,10,.2);}}
.lgpd-red{{background:rgba(255,69,58,.08);border:1px solid rgba(255,69,58,.2);}}
.lgpd-icon{{font-size:15px;flex-shrink:0;margin-top:1px;}}
/* ── footer ── */
.report-footer{{margin-top:48px;padding-top:24px;border-top:1px solid var(--border);
  text-align:center;font-size:12px;color:var(--muted);}}
.empty-msg{{font-size:13px;color:var(--muted);font-style:italic;text-align:center;padding:16px;}}
@media print{{body{{background:#fff;color:#000;}}
  .card{{border:1px solid #ccc;background:#f9f9f9;}}}}
</style>
</head>
<body>

<div class="report-header">
  <div class="page">
    <div>
      <div class="brand">AUDIT<span>X</span></div>
      <div class="report-type">🛡️ Laudo de Segurança — Blindagem</div>
    </div>
    <div class="meta">
      <div><strong>Projeto:</strong> {project}</div>
      <div><strong>Auditoria:</strong> {audit_id[:16]}…</div>
      <div><strong>Data:</strong> {date_fmt}</div>
    </div>
  </div>
</div>

<div class="page">

  <!-- Score -->
  <div class="section">
    <div class="section-title">Score de Risco</div>
    <div class="card">
      <div class="score-band">
        {gauge_html}
        <div class="score-meta">
          <div class="score-row">
            <span class="score-big" style="color:{_score_color(score_i)}">{score_i}</span>
            <span class="score-arrow">→</span>
            <span class="score-big" style="color:{_score_color(score_f)}">{score_f}</span>
            <span class="score-delta" style="color:{delta_col}">({delta_sign})</span>
          </div>
          <div class="score-sub">Score Inicial → Score Final após auto-correção</div>
          <div class="score-sub" style="margin-top:8px;">
            {audit_data.get('files_scanned',0)} arquivo(s) analisado(s) &nbsp;·&nbsp;
            {audit_data.get('total_findings',0)} finding(s) &nbsp;·&nbsp;
            {len(fixed)} corrigido(s) automaticamente
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Mapa de Calor -->
  <div class="section">
    <div class="section-title">Mapa de Calor de Vulnerabilidades</div>
    <div class="card">
      <table class="heatmap">{heatmap_html}</table>
    </div>
  </div>

  <!-- Achados de Injeção -->
  <div class="section">
    <div class="section-title">Achados de Injeção (SQL / XSS / Eval)</div>
    {injection_html}
  </div>

  <!-- Exposição de Segredos -->
  <div class="section">
    <div class="section-title">Exposição de Segredos & Credenciais</div>
    <div class="card">
      <table class="secrets-table">{secrets_rows}</table>
    </div>
  </div>

  <!-- Checklist LGPD -->
  <div class="section">
    <div class="section-title">Checklist LGPD / Compliance</div>
    <div class="card">{lgpd_html}</div>
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
