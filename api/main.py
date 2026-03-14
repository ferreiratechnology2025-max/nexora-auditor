from fastapi import FastAPI, WebSocket, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import sys, os, tempfile, zipfile, uuid, json, subprocess, io, base64, asyncio

sys.path.insert(0, '/app')
from dotenv import load_dotenv
load_dotenv()

from core.audit_orchestrator import AuditOrchestrator
from core.ai_advisor import AIAdvisor

app = FastAPI(title='Nexora Auditor — Motor Inteligente')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

advisor = AIAdvisor()
orchestrator = AuditOrchestrator()

_REPORTS_DIR   = '/tmp/auditx/reports'
_BASE_URL       = 'https://auditor.nexora360.cloud'
_SCAN_SEM       = asyncio.Semaphore(2)   # máx 2 scans simultâneos
_SCAN_QUEUED    = 0                       # aguardando semáforo
_SCAN_MAX_QUEUE = 5                       # rejeita acima disto


def _qr_base64(url: str) -> str:
    """Gera QR Code PNG como string base64 para embed no HTML."""
    try:
        import qrcode
        qr = qrcode.QRCode(version=1, box_size=5, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color='#1d4ed8', back_color='white')
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        print(f'[QR] Erro ao gerar QR Code: {e}')
        return ''


def _save_result(audit_id: str, result: dict) -> None:
    """Persiste o resultado da auditoria para o endpoint de laudo."""
    try:
        os.makedirs(_REPORTS_DIR, exist_ok=True)
        with open(f'{_REPORTS_DIR}/{audit_id}.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False)
    except Exception as e:
        print(f'[SAVE] Erro ao salvar resultado {audit_id}: {e}')


def _render_report_html(data: dict) -> str:
    """Gera o HTML público do laudo a partir do resultado da auditoria."""
    audit_id      = data.get('audit_id', '')
    score_initial = data.get('score_initial', 0)
    score_final   = data.get('score_final', 0)
    total         = data.get('total_findings', 0)
    findings      = data.get('findings', []) or []
    fixed_count   = data.get('fixed_count', 0)
    ingest        = data.get('ingest', {}) or {}
    cert          = data.get('certificate', {}) or {}
    langs         = ', '.join(ingest.get('languages', []))

    sev_colors = {
        'CRITICAL': ('#fef2f2', '#ef4444', '#fecaca', '#dc2626'),
        'HIGH':     ('#fff7ed', '#f97316', '#fed7aa', '#ea580c'),
        'MEDIUM':   ('#fffbeb', '#eab308', '#fef08a', '#ca8a04'),
        'LOW':      ('#f0fdf4', '#22c55e', '#bbf7d0', '#16a34a'),
    }

    finding_rows = ''
    for f in findings:
        sev = f.get('severity', 'LOW')
        bg, border, badge_bg, badge_fg = sev_colors.get(sev, sev_colors['LOW'])
        title = f.get('title', f.get('category', '').replace('_', ' ').title())
        desc  = f.get('description') or f.get('explanation', '')
        loc   = f.get('file', '')
        if f.get('line'):
            loc += f':{f["line"]}'
        finding_rows += f'''
        <div style="background:{bg};border-left:4px solid {border};border-radius:8px;padding:12px;margin-bottom:8px">
          <div style="display:flex;justify-content:space-between;margin-bottom:4px">
            <span style="font-weight:700;font-size:14px">{title}</span>
            <span style="background:{badge_bg};color:{badge_fg};font-size:11px;font-weight:700;padding:2px 8px;border-radius:4px">{sev}</span>
          </div>
          <div style="font-family:monospace;font-size:12px;color:#64748b">{loc}</div>
          <div style="font-size:13px;color:#475569;margin-top:6px">{desc}</div>
        </div>'''

    cert_block = ''
    if cert.get('number'):
        cert_hash  = cert.get('hash_short') or cert.get('hash', audit_id)
        verify_url = f"{_BASE_URL}/verify/{cert_hash}"
        qr_b64     = _qr_base64(verify_url)
        qr_img_tag = (
            f'<img src="data:image/png;base64,{qr_b64}" '
            f'style="width:120px;height:120px;display:block;margin:12px auto;border-radius:8px" '
            f'alt="QR Code de verificação">'
        ) if qr_b64 else ''
        cert_block = f'''
        <div style="background:#1d4ed8;color:white;border-radius:16px;padding:24px;text-align:center;margin-top:24px">
          <div style="font-size:20px;font-weight:900;letter-spacing:2px;margin-bottom:4px">{cert["number"]}</div>
          <div style="font-size:13px;opacity:0.8;margin-bottom:4px">Certificado de Segurança Digital · AUDITX</div>
          {qr_img_tag}
          <div style="font-size:11px;opacity:0.6;margin-bottom:12px;font-family:monospace">
            {verify_url}
          </div>
          <a href="{verify_url}" target="_blank"
             style="display:inline-block;background:white;color:#1d4ed8;padding:10px 24px;border-radius:8px;font-weight:700;text-decoration:none">
            Verificar Autenticidade
          </a>
        </div>'''

    improvement = score_final - score_initial
    imp_color = '#16a34a' if improvement > 0 else '#64748b'

    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Laudo AUDITX — {audit_id[:8].upper()}</title>
</head>
<body style="margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#f8fafc;color:#1e293b">

<div style="background:#1d4ed8;padding:32px;text-align:center">
  <div style="font-size:28px;font-weight:900;letter-spacing:3px;color:white;margin-bottom:6px">🛡️ AUDITX</div>
  <div style="color:#93c5fd;font-size:14px">Laudo de Segurança Digital — {audit_id[:8].upper()}</div>
</div>

<div style="max-width:800px;margin:32px auto;padding:0 16px">

  <div style="background:white;border-radius:16px;padding:32px;box-shadow:0 1px 3px rgba(0,0,0,0.1);margin-bottom:24px;display:flex;gap:24px;align-items:center;justify-content:space-around;flex-wrap:wrap">
    <div style="text-align:center">
      <div style="font-size:56px;font-weight:900;color:#ef4444;line-height:1">{score_initial}</div>
      <div style="font-size:11px;color:#64748b;margin-top:4px;text-transform:uppercase;letter-spacing:1px">Score Inicial</div>
    </div>
    <div style="font-size:32px;color:#94a3b8">→</div>
    <div style="text-align:center">
      <div style="font-size:56px;font-weight:900;color:#22c55e;line-height:1">{score_final}</div>
      <div style="font-size:11px;color:#64748b;margin-top:4px;text-transform:uppercase;letter-spacing:1px">Score Final</div>
    </div>
    <div style="text-align:center">
      <div style="background:#dcfce7;color:{imp_color};font-size:24px;font-weight:900;padding:8px 20px;border-radius:10px">+{improvement} pts</div>
      <div style="font-size:11px;color:#64748b;margin-top:4px;text-transform:uppercase;letter-spacing:1px">Melhoria</div>
    </div>
  </div>

  <div style="background:white;border-radius:16px;padding:24px;box-shadow:0 1px 3px rgba(0,0,0,0.1);margin-bottom:24px">
    <p style="color:#374151;margin:0">
      <strong>{total} vulnerabilidades</strong> encontradas em
      <strong>{ingest.get("file_count", 0)} arquivos</strong>
      {f"({langs})" if langs else ""}
      · <strong>{fixed_count} corrigidas automaticamente</strong>
    </p>
  </div>

  <div style="background:white;border-radius:16px;padding:24px;box-shadow:0 1px 3px rgba(0,0,0,0.1);margin-bottom:24px">
    <h2 style="font-size:16px;font-weight:700;margin-bottom:16px">🔍 Vulnerabilidades ({total})</h2>
    {finding_rows if finding_rows else '<p style="color:#64748b">Nenhuma vulnerabilidade encontrada.</p>'}
  </div>

  {cert_block}

</div>

<div style="text-align:center;padding:32px;color:#94a3b8;font-size:12px">
  AUDITX — auditor.nexora360.cloud<br>
  Laudo ID: {audit_id} · Gerado pelo motor Nexora v2.0
</div>

</body>
</html>'''


@app.get('/health')
@app.get('/api/v2/health')
def health():
    return {'status': 'ok', 'motor': 'nexora-auditor-engine', 'version': '2.0'}


@app.get('/api/v2/queue')
async def queue_status():
    """Status da fila de processamento."""
    return {
        'queued':         _SCAN_QUEUED,
        'running':        2 - _SCAN_SEM._value,
        'max_concurrent': 2,
        'max_queue':      _SCAN_MAX_QUEUE,
        'accepting':      _SCAN_QUEUED < _SCAN_MAX_QUEUE,
    }


@app.post('/api/v2/audit/zip')
async def audit_zip(file: UploadFile = File(...), email: str = Form('')):
    global _SCAN_QUEUED

    if _SCAN_QUEUED >= _SCAN_MAX_QUEUE:
        raise HTTPException(503, 'Sistema ocupado. Tente novamente em alguns minutos.')

    # Lê o arquivo antes de entrar na fila (libera socket do cliente)
    file_bytes = await file.read()
    filename   = file.filename
    audit_id   = str(uuid.uuid4())

    _SCAN_QUEUED += 1
    try:
        async with _SCAN_SEM:
            _SCAN_QUEUED -= 1
            print(f'[QUEUE] Iniciando scan {audit_id[:8]} | queued={_SCAN_QUEUED} running={2 - _SCAN_SEM._value}')

            with tempfile.TemporaryDirectory() as tmp:
                zip_path = os.path.join(tmp, 'project.zip')
                with open(zip_path, 'wb') as f:
                    f.write(file_bytes)

                extract_path = os.path.join(tmp, 'project')
                os.makedirs(extract_path)

                try:
                    with zipfile.ZipFile(zip_path, 'r') as z:
                        z.extractall(extract_path)
                except RuntimeError as e:
                    if 'password' in str(e).lower():
                        raise HTTPException(400, 'ZIP protegido por senha.')
                    raise HTTPException(400, f'ZIP inválido: {e}')

                result = orchestrator.run_audit(
                    project_path=extract_path,
                    context={
                        'email':    email,
                        'audit_id': audit_id,
                        'source':   'zip',
                        'filename': filename,
                    },
                )

            _save_result(audit_id, result)
            return result
    except HTTPException:
        raise
    except Exception:
        _SCAN_QUEUED = max(0, _SCAN_QUEUED - 1)
        raise


@app.post('/api/v2/audit/github')
async def audit_github(payload: dict):
    repo_url = payload.get('repo_url', '')
    email    = payload.get('email', '')
    audit_id = str(uuid.uuid4())

    with tempfile.TemporaryDirectory() as tmp:
        proc = subprocess.run(
            ['git', 'clone', '--depth', '1', repo_url, tmp + '/repo'],
            capture_output=True,
            timeout=60,
        )
        if proc.returncode != 0:
            raise HTTPException(400, 'Erro ao clonar repositório.')

        audit_result = orchestrator.run_audit(
            project_path=tmp + '/repo',
            context={
                'email': email,
                'audit_id': audit_id,
                'source': 'github',
                'repo_url': repo_url,
            },
        )

    _save_result(audit_id, audit_result)
    return audit_result


@app.get('/api/v2/audit/{audit_id}/report', response_class=HTMLResponse)
async def get_report(audit_id: str):
    """Laudo HTML público — acessível pelo link do email."""
    report_path = f'{_REPORTS_DIR}/{audit_id}.json'
    if not os.path.exists(report_path):
        raise HTTPException(404, f'Laudo {audit_id} não encontrado ou expirado.')
    with open(report_path, encoding='utf-8') as f:
        data = json.load(f)
    return HTMLResponse(content=_render_report_html(data))


@app.websocket('/ws/advisor/{session_id}')
async def advisor_ws(websocket: WebSocket, session_id: str):
    await websocket.accept()

    intro = advisor.start_conversation(session_id)
    await websocket.send_json({'type': 'message', 'content': intro})

    try:
        while True:
            data = await websocket.receive_json()
            msg = data.get('message', '')
            response = advisor.chat(session_id, msg)
            await websocket.send_json({
                'type': 'message',
                'content': response['response'],
                'ready_to_audit': response.get('ready_to_audit', False),
                'action': response.get('action', 'chat'),
            })
    except Exception:
        pass


@app.get('/api/v2/verify/{report_hash}')
def verify_certificate(report_hash: str):
    cert_path = f'/opt/nexora-auditor-engine/certificates/{report_hash}.json'
    if not os.path.exists(cert_path):
        raise HTTPException(404, 'Certificado não encontrado.')
    with open(cert_path) as f:
        cert = json.load(f)
    return {
        'valid':              True,
        'certificate_number': cert.get('number'),
        'project':            cert.get('project_name'),
        'score_initial':      cert.get('score_initial'),
        'score_final':        cert.get('score_final'),
        'date':               cert.get('date'),
        'audited_by':         'Nexora Auditor v2.0',
    }
