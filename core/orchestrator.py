import os
import sys
import subprocess
from pathlib import Path

# Garante que o projeto root esta no path ao rodar como script (ex.: python core/orchestrator.py)
_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
if _root not in sys.path:
    sys.path.insert(0, _root)

import json
from core.advice_engine import AdviceEngine
from core.assembler import NexoraAssembler
from core.cleaner import Cleaner
from core.coder import NexoraCoder
from core.docs_agent import NexoraDocs
from core.genome_factory import GenomeFactory
from core.genome_search import GenomeSearch
from core.llm_client import NexoraLLM
from core.prompt_optimizer import PromptOptimizer
from core.self_improvement import SelfImprovementEngine
from core.shadow_tester import ShadowTester
from core.tester import find_python_files, run_workspace_tests, validate_syntax


class NexoraOrchestrator:
    def __init__(self):
        self.search = GenomeSearch()
        self.llm = NexoraLLM()
        self.optimizer = PromptOptimizer()
        self.coder = NexoraCoder()
        self.advisor = AdviceEngine()
        self.self_improvement_engine = SelfImprovementEngine()
        self.genome_factory = GenomeFactory()
        self.shadow_tester = ShadowTester()
        self.cleaner = Cleaner()
        project_root = Path(__file__).resolve().parents[1]
        config_path = project_root / 'config' / 'model_stack.json'
        with open(config_path, 'r', encoding='utf-8') as f:
            self.model_stack = json.load(f)

    def create_internal_gene(self, gene_name, description):
        """
        Comando Codex: O Agente cria uma nova capacidade para o seu proprio genoma.
        """
        gene_name = (gene_name or '').strip()
        description = (description or '').strip()
        if not gene_name or not description:
            raise ValueError('gene_name e description sao obrigatorios.')

        genome_root = os.getenv('GENOME_ROOT')
        if not genome_root:
            raise RuntimeError('GENOME_ROOT nao configurado no ambiente.')

        gene_path = os.path.join(genome_root, 'core', gene_name)
        os.makedirs(gene_path, exist_ok=True)

        prompt = f"""
        OBJETIVO: Criar um GENE REUTILIZAVEL para o Nexora Agente.
        NOME: {gene_name}
        FUNCAO: {description}
        REQUISITOS:
        - Criar um arquivo template.py com logica generica.
        - Criar um GENOME.md detalhando como o Architect deve usar este gene.
        - Incluir tags # NEXORADOCS: para auto-documentacao.
        """

        self.coder.generate_gene_files(gene_path, prompt)
        subprocess.run(['python', 'scripts/update_genome.py'], check=True)
        return True

    def _run_self_improvement(self, project_path):
        if not project_path or not os.path.isdir(project_path):
            return {
                'status': 'skipped',
                'health': {'score': 0, 'metrics': {}},
                'dependencies': {'dependencies': {}, 'potential_cycles': []},
                'refactoring_suggestions': ['Workspace invalido para analise de saude do projeto.'],
            }

        try:
            output = self.self_improvement_engine.run(project_path)
            output['status'] = 'completed'
            return output
        except Exception as exc:
            return {
                'status': 'error',
                'health': {'score': 0, 'metrics': {}},
                'dependencies': {'dependencies': {}, 'potential_cycles': []},
                'refactoring_suggestions': [f'Falha no self-improvement loop: {exc}'],
            }

    def _attach_cleanup(self, payload, project_path, skip=False, reason=''):
        if skip:
            payload['cleanup'] = {'status': 'skipped', 'reason': reason, 'removed_items': 0}
            return payload

        payload['cleanup'] = self.cleaner.sanitize_workspace(project_path)
        return payload

    def verification_loop(self, workspace_path):
        """Valida sintaxe e executa testes; em caso de erro, pede correcao ao executor."""
        if not workspace_path or not os.path.isdir(workspace_path):
            return {
                'status': 'error',
                'reason': 'Workspace invalido para verificacao.',
                'workspace': workspace_path,
                'syntax_errors': [],
                'tests': None,
                'executor_feedback': None,
                'advisor': {'advice': [], 'hard_stop': False, 'saved_count': 0},
            }

        syntax_errors = []
        for py_file in find_python_files(workspace_path):
            result = validate_syntax(py_file)
            if not result.get('ok'):
                syntax_errors.append(result)

        if syntax_errors:
            error_lines = []
            for err in syntax_errors:
                error_lines.append(
                    f"{err.get('file_path')}:{err.get('line')}:{err.get('offset')} - {err.get('error')}"
                )
                if err.get('text'):
                    error_lines.append(f"Trecho: {err.get('text')}")

            error_text = '\n'.join(error_lines)
            correction_prompt = (
                f"O código gerado falhou nos testes com o seguinte erro: {error_text}. "
                "Por favor, aplique a correção."
            )
            executor_model = self.model_stack['roles']['executor']
            feedback = self.llm.call(executor_model, correction_prompt, role='executor')
            advisor_report = self.advisor.analyze_and_record(feedback, task='verification_syntax')

            status = 'manual_approval_required' if advisor_report.get('hard_stop') else 'error'
            reason = (
                'Hard stop do Advisor: alerta CRITICAL/SECURITY detectado.'
                if advisor_report.get('hard_stop')
                else 'Falha de sintaxe detectada.'
            )

            return {
                'status': status,
                'reason': reason,
                'workspace': workspace_path,
                'syntax_errors': syntax_errors,
                'tests': None,
                'executor_feedback': feedback,
                'advisor': advisor_report,
            }

        tests_result = run_workspace_tests(workspace_path)
        if tests_result.get('ok'):
            return {
                'status': 'success',
                'reason': 'Sintaxe e testes aprovados.',
                'workspace': workspace_path,
                'syntax_errors': [],
                'tests': tests_result,
                'executor_feedback': None,
                'advisor': {'advice': [], 'hard_stop': False, 'saved_count': 0},
            }

        report = tests_result.get('error_report') or {}
        traceback_text = report.get('traceback') or ''
        error_lines = report.get('error_lines') or []
        fallback_err = tests_result.get('stderr') or tests_result.get('stdout') or 'Erro nao identificado.'
        error_text = traceback_text if traceback_text else '\n'.join(error_lines) if error_lines else fallback_err

        correction_prompt = (
            f"O código gerado falhou nos testes com o seguinte erro: {error_text}. "
            "Por favor, aplique a correção."
        )
        executor_model = self.model_stack['roles']['executor']
        feedback = self.llm.call(executor_model, correction_prompt, role='executor')
        advisor_report = self.advisor.analyze_and_record(feedback, task='verification_tests')

        status = 'manual_approval_required' if advisor_report.get('hard_stop') else 'error'
        reason = (
            'Hard stop do Advisor: alerta CRITICAL/SECURITY detectado.'
            if advisor_report.get('hard_stop')
            else 'Falha em testes do workspace.'
        )

        return {
            'status': status,
            'reason': reason,
            'workspace': workspace_path,
            'syntax_errors': [],
            'tests': tests_result,
            'executor_feedback': feedback,
            'advisor': advisor_report,
        }

    def save_to_workspace(self, arch_response):
        workspace = os.getenv('WORKSPACE_ROOT')

        if not workspace:
            return {
                'status': 'error',
                'workspace': None,
                'architecture': None,
                'error': 'WORKSPACE_ROOT nao configurado no ambiente.',
            }

        if not isinstance(arch_response, str) or not arch_response.strip():
            return {
                'status': 'error',
                'workspace': workspace,
                'architecture': None,
                'error': 'Resposta da IA vazia ou invalida.',
            }

        if arch_response.strip().startswith('[ERRO]'):
            return {
                'status': 'error',
                'workspace': workspace,
                'architecture': None,
                'error': arch_response.strip(),
            }

        try:
            clean_json = arch_response.replace('```json', '').replace('```', '').strip()
            arch_json = json.loads(clean_json)
        except Exception as e:
            return {
                'status': 'error',
                'workspace': workspace,
                'architecture': None,
                'error': f'Falha ao processar JSON da IA: {e}',
            }

        os.makedirs(workspace, exist_ok=True)
        arch_path = os.path.join(workspace, 'architecture.json')
        try:
            with open(arch_path, 'w', encoding='utf-8') as f:
                json.dump(arch_json, f, indent=2, ensure_ascii=False)
            print(f'[INFO] Arquitetura salva em: {arch_path}')
        except Exception as e:
            return {
                'status': 'error',
                'workspace': workspace,
                'architecture': arch_json,
                'error': f'Nao foi possivel salvar architecture.json: {e}',
            }

        return {'status': 'success', 'workspace': workspace, 'architecture': arch_json}

    def run_pipeline(self, user_idea):
        print(f'[INFO] Analisando ideia: {user_idea}')

        subprocess.run(['python', 'core/genome_rag.py'], check=False)

        candidates = self.search.find_matches(user_idea)
        if 'erp' in user_idea.lower():
            candidates.append({'name': 'Multi-tenant Logic', 'id': 'multi_tenant'})

        genes_found = [g['name'] for g in candidates]
        print(f'[INFO] Genes que serao usados: {genes_found}')

        model = self.model_stack['roles']['planner']
        prompt = self.optimizer.optimize(
            f'Desenhe a arquitetura de um {user_idea}. '
            f'Use OBRIGATORIAMENTE os genes: {genes_found}. '
            'Responda apenas com o JSON de rotas e tabelas.',
            'architecture',
        )

        print(f'[INFO] Chamando {model} para arquitetura...')
        arch_response = self.llm.call(model, prompt)
        result = self.save_to_workspace(arch_response)
        if result.get('status') != 'success':
            return result

        workspace = result.get('workspace')
        arch_file = os.path.join(workspace, 'architecture.json') if workspace else ''
        if not (arch_file and os.path.isfile(arch_file)):
            return {
                'status': 'error',
                'workspace': workspace,
                'architecture': result.get('architecture'),
                'error': 'architecture.json nao encontrado apos parse da arquitetura.',
            }

        print('[INFO] Iniciando montagem fisica do projeto...')
        assembler = NexoraAssembler()
        project_path = assembler.assemble_project(arch_file)

        if not project_path or project_path.startswith('[ERRO]'):
            return {
                'status': 'error',
                'workspace': workspace,
                'architecture': result.get('architecture'),
                'error': project_path or 'Falha na montagem do projeto.',
            }

        print('[INFO] Iniciando Agente Coder para logica de negocio...')
        self.coder.write_business_logic(project_path, result.get('architecture') or {})

        os.environ['DOCKER_ENABLED'] = 'True'

        print('[INFO] Executando verification loop...')
        verification = self.verification_loop(project_path)

        should_run_self_improvement = (
            verification.get('status') == 'success'
            and isinstance(verification.get('tests'), dict)
            and verification.get('tests', {}).get('ok') is True
            and verification.get('tests', {}).get('mode') == 'docker'
        )

        if should_run_self_improvement:
            print('[INFO] Executando shadow test...')
            shadow_test = self.shadow_tester.run(project_path)

            print('[INFO] Executando self-improvement loop...')
            self_improvement = self._run_self_improvement(project_path)
        else:
            shadow_test = {
                'ok': False,
                'status': 'skipped',
                'mode': 'docker',
                'attempt_count': 0,
                'vulnerability_count': 0,
                'attempts': [],
                'vulnerabilities': [],
                'stdout': '',
                'stderr': 'Shadow test nao executado: depende de teste Docker aprovado.',
            }
            self_improvement = {
                'status': 'skipped',
                'health': {'score': 0, 'metrics': {}},
                'dependencies': {'dependencies': {}, 'potential_cycles': []},
                'refactoring_suggestions': [
                    'Self-improvement nao executado: requer testes Docker com status de sucesso.'
                ],
            }

        health = self_improvement.get('health', {})
        health_score = int(health.get('score', 0)) if isinstance(health, dict) else 0
        refactoring_suggestions = self_improvement.get('refactoring_suggestions', [])

        # Regra: score 100 so se sobreviver ao Shadow Test.
        if not shadow_test.get('ok') and health_score >= 100:
            health['score'] = 95
            health_score = 95
            refactoring_suggestions = list(refactoring_suggestions) + [
                'Shadow Test reprovado: reforcar validacao de entrada contra SQLi/XSS antes de buscar score 100.'
            ]

        promoted_gene = {'status': 'skipped', 'reason': 'Criterios de promocao nao atendidos.'}
        preferred_gene_name = 'crypto_vault_v1' if any(token in user_idea.lower() for token in ('cofre', 'vault', 'crypto', 'criptografia', 'aes')) else None
        if shadow_test.get('ok') and health_score >= 90:
            print('[INFO] Promovendo expertise para gene...')
            promoted_gene = self.genome_factory.promote_to_gene(project_path, health_score=health_score, min_health=90, preferred_name=preferred_gene_name)

        base_payload = {
            'workspace': project_path,
            'architecture': result.get('architecture'),
            'verification': verification,
            'advisor': verification.get('advisor', {}),
            'shadow_test': shadow_test,
            'self_improvement': self_improvement,
            'project_health': health,
            'refactoring_suggestions': refactoring_suggestions,
            'gene_promotion': promoted_gene,
            'expertise_extracted': promoted_gene.get('status') == 'promoted',
        }

        if verification.get('status') == 'manual_approval_required':
            payload = {
                'status': 'manual_approval_required',
                'error': verification.get('reason'),
                'manual_approval_required': True,
                **base_payload,
            }
            return self._attach_cleanup(
                payload,
                project_path,
                skip=True,
                reason='Hard stop CRITICAL/SECURITY: limpeza suspensa para auditoria.',
            )

        if verification.get('status') != 'success':
            payload = {
                'status': 'error',
                'error': verification.get('reason'),
                **base_payload,
            }
            return self._attach_cleanup(payload, project_path)

        print('[INFO] Gerando documentacao do projeto...')
        docs = NexoraDocs()
        docs.generate_readme(project_path, result.get('architecture') or {})

        payload = {
            'status': 'success',
            **base_payload,
        }
        return self._attach_cleanup(payload, project_path)


if __name__ == '__main__':
    orc = NexoraOrchestrator()
    orc.run_pipeline('Um sistema de afiliados com checkout Stripe')

