import os
import sys
import sqlite3
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Garante que o projeto root esta no path (ex.: streamlit run app.py)
_root = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

load_dotenv(os.path.join(_root, '.env'))

import streamlit as st
from core.orchestrator import NexoraOrchestrator
from core.tester_agent import NexoraTester


def _ensure_memory_tables():
    project_root = Path(_root)
    memory_root = os.getenv('MEMORY_ROOT') or str(project_root / 'memory')
    db_path = os.path.join(memory_root, 'sqlite', 'nexora_memory.db')

    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute(
            '''
            CREATE VIRTUAL TABLE IF NOT EXISTS decisions USING fts5(
                timestamp,
                agent,
                task,
                decision,
                outcome,
                tokens_used,
                cost
            );
            '''
        )
    except Exception:
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS decisions (
                timestamp TEXT,
                agent TEXT,
                task TEXT,
                decision TEXT,
                outcome TEXT,
                tokens_used TEXT,
                cost TEXT
            );
            '''
        )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS genes (
            id TEXT PRIMARY KEY,
            name TEXT,
            path TEXT,
            tags TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        '''
    )

    conn.commit()
    conn.close()


# Auto-setup de banco antes de abrir interface
_ensure_memory_tables()

# Inicializacao do Orquestrador
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = NexoraOrchestrator()
orchestrator = st.session_state.orchestrator

if 'approved_refactors' not in st.session_state:
    st.session_state.approved_refactors = []

st.set_page_config(page_title='Nexora Agente - Supervisor', layout='wide')


def _extract_advisor_data(result):
    result = result or {}
    advisor = result.get('advisor') or {}

    verification = result.get('verification') or {}
    if not advisor and isinstance(verification, dict):
        advisor = verification.get('advisor') or {}

    advice_items = advisor.get('advice') if isinstance(advisor, dict) else []
    if not isinstance(advice_items, list):
        advice_items = []

    hard_stop = bool(advisor.get('hard_stop')) if isinstance(advisor, dict) else False
    return advice_items, hard_stop


def _extract_health_score(result):
    result = result or {}
    health = result.get('project_health') or {}
    if not health:
        self_improvement = result.get('self_improvement') or {}
        health = self_improvement.get('health') or {}

    score = health.get('score') if isinstance(health, dict) else None
    if isinstance(score, (int, float)):
        return max(0, min(100, int(score)))
    return None


def _extract_refactor_tasks(result):
    result = result or {}
    tasks = result.get('refactoring_suggestions')
    if not isinstance(tasks, list):
        self_improvement = result.get('self_improvement') or {}
        tasks = self_improvement.get('refactoring_suggestions', [])

    return [task for task in (tasks or []) if isinstance(task, str) and task.strip()]


def _extract_shadow_data(result):
    result = result or {}
    shadow = result.get('shadow_test') or {}
    attempts = shadow.get('attempts') if isinstance(shadow, dict) else []
    if not isinstance(attempts, list):
        attempts = []

    return shadow, attempts


def _render_advisor_panel(result):
    advice_items, hard_stop = _extract_advisor_data(result)

    st.write('### Conselhos do Advisor')
    if advice_items:
        for item in advice_items:
            st.warning(item)
    else:
        st.caption('Nenhum conselho emitido nesta execucao.')

    if hard_stop or (result or {}).get('manual_approval_required'):
        st.error('Aprovacao manual obrigatoria: alerta CRITICAL/SECURITY detectado pelo Advisor.')
        st.info('A geracao foi interrompida para revisao do Supervisor no Dashboard.')


def _render_refactor_card(result):
    tasks = _extract_refactor_tasks(result)

    st.write('### Sugestoes de Refatoracao')
    if tasks:
        for idx, task in enumerate(tasks):
            row = st.columns([8, 2])
            row[0].info(task)
            key = f'approve_refactor_{idx}_{abs(hash(task))}'
            if row[1].button('Aprovar', key=key):
                if task not in st.session_state.approved_refactors:
                    st.session_state.approved_refactors.append(task)

        if st.session_state.approved_refactors:
            st.success(f'Sugestoes aprovadas: {len(st.session_state.approved_refactors)}')
    else:
        st.caption('Nenhuma sugestao disponivel para o ultimo pipeline.')


def _render_shadow_log(result):
    shadow, attempts = _extract_shadow_data(result)
    st.write('### Log do Shadow Test')

    if not shadow:
        st.caption('Shadow Test ainda nao executado.')
        return

    status = shadow.get('status', 'unknown')
    mode = shadow.get('mode', 'docker')
    attempt_count = shadow.get('attempt_count', len(attempts))
    vul_count = shadow.get('vulnerability_count', 0)

    c1, c2, c3 = st.columns(3)
    c1.metric('Status', str(status).upper())
    c2.metric('Tentativas', str(attempt_count))
    c3.metric('Vulnerabilidades', str(vul_count))
    st.caption(f'Modo: {mode}')

    if attempts:
        st.dataframe(attempts[:30], use_container_width=True)


def _show_generation_result_feedback(result):
    status = result.get('status')
    if status == 'success':
        st.success(f"Projeto preparado em: {result.get('workspace', '')}")
    elif status == 'manual_approval_required':
        st.warning('Geracao interrompida: aprovacao manual obrigatoria no Dashboard.')
        st.error(result.get('error', 'Hard stop do Advisor acionado.'))
    else:
        st.error(result.get('error', 'Falha na geracao do projeto.'))

    promotion = result.get('gene_promotion') or {}
    if promotion.get('status') == 'promoted':
        st.success(
            f"Expertise Extraida: Novo Gene [{promotion.get('gene_name')}] adicionado ao Genoma."
        )


# Auto-Run via URL: localhost:8501/?idea=ERP+Oficina
try:
    params = st.experimental_get_query_params()
except Exception:
    params = {}
if isinstance(params, dict) and 'idea' in params:
    idea_val = params['idea']
    idea_from_url = (idea_val[0] if isinstance(idea_val, list) else idea_val) or ''
    if idea_from_url and not st.session_state.get('auto_run_executed'):
        st.session_state.auto_run_executed = True
        st.session_state.last_idea = idea_from_url
        st.info(f'Executando geracao automatica para: {idea_from_url}')
        with st.spinner('Pipeline em execucao...'):
            result = orchestrator.run_pipeline(idea_from_url)
        st.session_state.last_result = result
        st.session_state.last_workspace = result.get('workspace')
        _show_generation_result_feedback(result)

# Estilo iOS Dark Abstract
st.markdown(
    '''
<style>
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d1117 100%); }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #161b22 0%, #0d1117 100%); }
    .main .block-container { padding-top: 1.25rem; padding-bottom: 1.25rem; }
    .stMarkdown h1 { color: #f0f6fc !important; font-weight: 600; }
    .stMarkdown h2, .stMarkdown h3 { color: #8b949e !important; }
    div[data-testid="stTextArea"] textarea {
        background: #21262d !important;
        color: #f0f6fc !important;
        border-color: #30363d;
        border-radius: 12px !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #238636 0%, #2ea043) !important;
        color: white !important;
        border: none;
        font-weight: 500;
        border-radius: 12px !important;
    }
</style>
''',
    unsafe_allow_html=True,
)

# Sidebar - Status do Sistema
st.sidebar.title('Nexora Agente')
st.sidebar.info(f"Diretorio: {os.getenv('WORKSPACE_ROOT')}")
st.sidebar.success('Modo: Desenvolvimento Local')

_last_result_sidebar = st.session_state.get('last_result', {})
_health_score = _extract_health_score(_last_result_sidebar)
st.sidebar.markdown('---')
st.sidebar.subheader('Saude do Projeto')
if _health_score is None:
    st.sidebar.caption('Sem dados de saude ainda. Execute uma geracao para calcular.')
else:
    st.sidebar.progress(_health_score / 100.0, text=f'{_health_score}%')

if st.sidebar.button('Atualizar Genoma'):
    try:
        subprocess.run(['python', 'scripts/update_genome.py'], check=True)
        st.sidebar.success('Genoma indexado com sucesso!')
    except Exception as e:
        st.sidebar.error(f'Erro ao atualizar: {e}')

st.sidebar.markdown('---')
st.sidebar.subheader('Engenharia de DNA')

with st.sidebar.expander('Novo Superpoder'):
    g_nome = st.text_input('Nome do Gene', placeholder='ex: gateway_pagamento')
    g_desc = st.text_area('Descricao Tecnica')

    if st.button('Executar Evolucao'):
        if not g_nome.strip() or not g_desc.strip():
            st.warning('Preencha o nome e a descricao tecnica do gene.')
        else:
            with st.spinner('O Agente esta escrevendo o proprio codigo...'):
                try:
                    success = orchestrator.create_internal_gene(g_nome, g_desc)
                    if success:
                        st.success(f"Gene '{g_nome}' integrado e indexado!")
                except Exception as e:
                    st.error(f'Falha ao evoluir gene: {e}')

# Corpo Principal
st.title('Desenvolvimento Automatizado')
st.subheader('Sistemas Inteligentes, Engenharia Modular')

score_for_main = _extract_health_score(st.session_state.get('last_result', {}))
if score_for_main is not None:
    st.metric('Score de Saude do Projeto', f'{score_for_main}%')

_default = st.session_state.get('last_idea', '')
user_idea = st.text_area(
    'Descreva o SaaS que deseja criar:',
    value=_default if _default else None,
    placeholder='Ex: Um sistema de agendamento para barbearias com integracao Stripe',
)

col1, col2 = st.columns([1, 4])

with col1:
    if st.button('Iniciar Geracao'):
        if user_idea:
            with st.status('Executando Pipeline Nexora...', expanded=True) as status:
                st.write('Buscando Genes no Drive D:...')
                result = orchestrator.run_pipeline(user_idea)
                st.write('Montando Arquitetura...')
                status.update(label='Geracao Concluida!', state='complete', expanded=False)

            st.session_state.last_result = result
            st.session_state.last_workspace = result.get('workspace')
            _show_generation_result_feedback(result)
        else:
            st.warning('Por favor, descreva sua ideia primeiro.')

    if st.session_state.get('last_workspace'):
        if st.button('Validar com Docker'):
            tester = NexoraTester()
            project_path = st.session_state.last_workspace
            with st.spinner('Subindo container de teste...'):
                status_test = tester.validate_deployment(project_path)
                if '[OK]' in status_test:
                    st.success(status_test)
                elif '[ERRO]' in status_test:
                    st.error(status_test)
                else:
                    st.warning(status_test)

with col2:
    st.write('### Genes Detectados para esta Ideia')
    _idea_for_search = user_idea or st.session_state.get('last_idea', '')
    if _idea_for_search:
        matches = orchestrator.search.find_matches(_idea_for_search)
        if matches:
            for m in matches:
                st.code(f"Gene: {m['name']} | Path: {m['path']}")
        else:
            st.write('Nenhum gene especifico encontrado. A IA gerara codigo do zero.')

    _last_result = st.session_state.get('last_result', {})
    _render_advisor_panel(_last_result)
    _render_refactor_card(_last_result)
    _render_shadow_log(_last_result)
