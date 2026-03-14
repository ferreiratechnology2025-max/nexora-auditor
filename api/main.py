from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys, os, tempfile, zipfile, uuid, json, subprocess

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


@app.get('/health')
@app.get('/api/v2/health')
def health():
    return {'status': 'ok', 'motor': 'nexora-auditor-engine', 'version': '2.0'}


@app.post('/api/v2/audit/zip')
async def audit_zip(file: UploadFile = File(...), email: str = ''):
    audit_id = str(uuid.uuid4())

    with tempfile.TemporaryDirectory() as tmp:
        zip_path = os.path.join(tmp, 'project.zip')
        with open(zip_path, 'wb') as f:
            f.write(await file.read())

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
                'email': email,
                'audit_id': audit_id,
                'source': 'zip',
                'filename': file.filename,
            },
        )

    return result


@app.post('/api/v2/audit/github')
async def audit_github(payload: dict):
    repo_url = payload.get('repo_url', '')
    email = payload.get('email', '')
    audit_id = str(uuid.uuid4())

    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            ['git', 'clone', '--depth', '1', repo_url, tmp + '/repo'],
            capture_output=True,
            timeout=60,
        )
        if result.returncode != 0:
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

    return audit_result


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
        'valid': True,
        'certificate_number': cert.get('number'),
        'project': cert.get('project_name'),
        'score_initial': cert.get('score_initial'),
        'score_final': cert.get('score_final'),
        'date': cert.get('date'),
        'audited_by': 'Nexora Auditor v2.0',
    }
