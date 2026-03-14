"""
AIAdvisor — IA conversacional que prepara o contexto para o AuditOrchestrator.
Coleta informações do cliente em 3-4 perguntas e conduz ao resultado.
"""
import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

from core.llm_client import NexoraLLM


load_dotenv()

SYSTEM_PROMPT = """Você é o AuditX, especialista sênior em segurança de software da plataforma Nexora.

Sua missão em uma conversa:
1. Entender o projeto do cliente em 3-4 perguntas DIRETAS e objetivas
2. Coletar: linguagem, framework, preocupação principal, contexto do deploy
3. Quando tiver contexto suficiente, encerrar a coleta (ready_to_audit: true)
4. Após a auditoria, apresentar resultados com impacto de negócio real

Regras de ouro:
- Seja técnico mas acessível — evite jargões sem explicação
- Uma pergunta por vez — nunca faça duas perguntas juntas
- Destaque SEMPRE o impacto de negócio (perda de dados, LGPD, downtime, etc.)
- Nunca mencione detalhes internos do sistema (modelos LLM, Docker, genoma, etc.)
- Quando apresentar resultados, sempre conecte a solução ao valor de negócio

Sequência ideal de perguntas:
1. "Qual a linguagem e framework principal do projeto?"
2. "Qual é a maior preocupação de segurança — dados de usuários, autenticação, APIs externas, ou algo específico?"
3. "O projeto já está em produção ou é pré-lançamento?" (contexto de urgência)
4. Se necessário: "Há algum requisito de compliance específico? (LGPD, PCI-DSS, SOC 2...)"

Após 3 respostas informativas, defina ready_to_audit: true e peça o arquivo.

Formato de resposta OBRIGATÓRIO (sempre JSON):
{
  "response": "Sua mensagem para o cliente",
  "ready_to_audit": false,
  "context": {
    "language": null,
    "framework": null,
    "concern": null,
    "stage": null,
    "compliance": null
  },
  "action": "chat"
}

Quando pronto para auditar:
  "ready_to_audit": true,
  "action": "request_file"

Quando apresentando resultados pós-auditoria:
  "action": "show_results"

IMPORTANTE: Retorne SOMENTE JSON válido, sem markdown, sem texto fora do JSON."""


class AIAdvisor:
    """
    IA conversacional que conversa com o cliente antes e depois da auditoria.
    Usa sessões em memória. Integrar com WebSocket ou REST conforme necessidade.
    """

    # Sessões em memória: session_id → {history, context, state}
    _sessions: Dict[str, Dict[str, Any]] = {}

    def __init__(self):
        self.llm = NexoraLLM()
        self.model = self._load_model()

    def _load_model(self) -> str:
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "model_stack.json")
        try:
            with open(config_path, encoding="utf-8") as f:
                data = json.load(f)
            return data.get("roles", {}).get("advisor", "anthropic/claude-sonnet-4-6")
        except Exception:
            return "anthropic/claude-sonnet-4-6"

    # ── API pública ──────────────────────────────────────────────────────────

    def start_conversation(self, session_id: str) -> str:
        """
        Inicia uma nova conversa. Retorna a primeira mensagem do AuditX.
        """
        self._sessions[session_id] = {
            "history":  [],
            "context":  {
                "language":   None,
                "framework":  None,
                "concern":    None,
                "stage":      None,
                "compliance": None,
            },
            "state":       "collecting",
            "started_at":  datetime.utcnow().isoformat(),
            "turn_count":  0,
        }

        opening = {
            "response": (
                "Olá! Sou o AuditX, seu especialista em segurança de código. "
                "Vou analisar seu projeto e identificar vulnerabilidades reais — "
                "não alertas genéricos.\n\n"
                "Para começar: qual é a linguagem e o framework principal do seu projeto?"
            ),
            "ready_to_audit": False,
            "context": self._sessions[session_id]["context"],
            "action": "chat",
        }

        self._sessions[session_id]["history"].append({
            "role":    "assistant",
            "content": opening["response"],
        })

        return json.dumps(opening, ensure_ascii=False)

    def chat(self, session_id: str, message: str) -> dict:
        """
        Processa uma mensagem do cliente.

        Retorna:
        {
            "response": str,
            "ready_to_audit": bool,
            "context": dict,
            "action": "chat" | "request_file" | "show_results"
        }
        """
        if session_id not in self._sessions:
            self.start_conversation(session_id)

        session = self._sessions[session_id]
        session["turn_count"] += 1

        # Adiciona mensagem do usuário ao histórico
        session["history"].append({"role": "user", "content": message})

        # Constrói prompt com histórico
        messages = self._build_messages(session)

        # Chama o LLM
        try:
            raw = self.llm.client.chat.completions.create(
                model=self.model,
                messages=messages,
            ).choices[0].message.content or "{}"
        except Exception as e:
            return {
                "response": "Desculpe, houve um problema temporário. Pode repetir?",
                "ready_to_audit": False,
                "context": session["context"],
                "action": "chat",
                "error": str(e),
            }

        # Parse da resposta estruturada
        result = self._parse_response(raw)

        # Atualiza contexto acumulado
        if result.get("context"):
            for key, value in result["context"].items():
                if value and not session["context"].get(key):
                    session["context"][key] = value

        result["context"] = session["context"]

        # Salva resposta no histórico
        session["history"].append({
            "role":    "assistant",
            "content": result.get("response", ""),
        })

        # Atualiza estado da sessão
        if result.get("ready_to_audit"):
            session["state"] = "ready"

        return result

    def present_results(self, session_id: str, audit_result: dict) -> str:
        """
        Apresenta os resultados da auditoria em linguagem humana.
        Destaca impacto de negócio e conduz ao pagamento.
        """
        if session_id not in self._sessions:
            self.start_conversation(session_id)

        session = self._sessions[session_id]
        context = session.get("context", {})

        score_i = audit_result.get("score_initial", 0)
        score_f = audit_result.get("score_final", 0)
        total   = audit_result.get("total_findings", 0)
        by_sev  = audit_result.get("by_severity", {})
        fixed   = audit_result.get("fixed_count", 0)
        cert    = audit_result.get("certificate")

        # Monta prompt para apresentação personalizada
        summary_prompt = f"""O cliente tem um projeto {context.get('language', 'N/A')} / {context.get('framework', 'N/A')}.
Preocupação: {context.get('concern', 'segurança geral')}.
Stage: {context.get('stage', 'não informado')}.

Resultado da auditoria:
- Score de segurança: {score_i}/100 → {score_f}/100
- Total de vulnerabilidades: {total}
- CRITICAL: {by_sev.get('CRITICAL', 0)} | HIGH: {by_sev.get('HIGH', 0)} | MEDIUM: {by_sev.get('MEDIUM', 0)} | LOW: {by_sev.get('LOW', 0)}
- Corrigidas automaticamente: {fixed}
- Certificado: {"emitido — " + cert.get('number', '') if cert else "não emitido (score insuficiente)"}

Apresente os resultados ao cliente:
1. Resuma o que foi encontrado (3-4 linhas, impacto de negócio real)
2. Destaque as 2-3 vulnerabilidades mais críticas com impacto concreto
3. Explique o que foi corrigido automaticamente
4. Conduza ao próximo passo (baixar laudo completo / certificado)

Retorne JSON com: response, ready_to_audit: true, action: "show_results", context: {{}}.
Seja direto, sem texto genérico. Fale sobre o projeto específico do cliente."""

        session["history"].append({"role": "user", "content": summary_prompt})
        messages = self._build_messages(session)

        try:
            raw = self.llm.client.chat.completions.create(
                model=self.model,
                messages=messages,
            ).choices[0].message.content or "{}"
        except Exception:
            # Fallback manual
            raw_text = self._fallback_results(score_i, score_f, total, by_sev, fixed, cert)
            return raw_text

        result = self._parse_response(raw)
        result["context"] = session["context"]
        result["action"] = "show_results"
        result["ready_to_audit"] = True

        session["history"].append({
            "role": "assistant",
            "content": result.get("response", ""),
        })
        session["state"] = "completed"

        return json.dumps(result, ensure_ascii=False)

    def get_session(self, session_id: str) -> Optional[dict]:
        """Retorna estado atual da sessão."""
        return self._sessions.get(session_id)

    def clear_session(self, session_id: str) -> None:
        """Remove sessão da memória."""
        self._sessions.pop(session_id, None)

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _build_messages(self, session: dict) -> List[dict]:
        """Constrói lista de mensagens para o LLM com histórico."""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Injeta contexto já coletado se houver
        ctx = session.get("context", {})
        filled = {k: v for k, v in ctx.items() if v}
        if filled:
            ctx_note = f"\n\n[CONTEXTO JÁ COLETADO]: {json.dumps(filled, ensure_ascii=False)}"
            messages[0]["content"] += ctx_note

        messages.extend(session.get("history", []))
        return messages

    def _parse_response(self, raw: str) -> dict:
        """Parse robusto da resposta JSON do LLM."""
        import re

        # Remove markdown
        clean = re.sub(r"```[a-z]*\n?", "", raw.strip())
        clean = re.sub(r"\n?```", "", clean).strip()

        # Tenta parse direto
        try:
            data = json.loads(clean)
            return self._normalize_response(data)
        except json.JSONDecodeError:
            pass

        # Tenta extrair JSON do texto
        match = re.search(r"\{.*\}", clean, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                return self._normalize_response(data)
            except json.JSONDecodeError:
                pass

        # Fallback: retorna o texto bruto como response
        return {
            "response":       clean or "Como posso ajudar?",
            "ready_to_audit": False,
            "context":        {},
            "action":         "chat",
        }

    def _normalize_response(self, data: dict) -> dict:
        """Garante campos obrigatórios na resposta."""
        return {
            "response":       str(data.get("response", "")),
            "ready_to_audit": bool(data.get("ready_to_audit", False)),
            "context":        data.get("context") or {},
            "action":         str(data.get("action", "chat")),
        }

    def _fallback_results(
        self, score_i: int, score_f: int, total: int,
        by_sev: dict, fixed: int, cert: Optional[dict]
    ) -> str:
        """Apresentação de resultados sem LLM (fallback)."""
        critical = by_sev.get("CRITICAL", 0)
        high = by_sev.get("HIGH", 0)
        delta = score_f - score_i

        lines = [
            f"Auditoria concluída. Score de segurança: {score_i} → {score_f}/100 (+{delta} pontos).",
            f"Encontrei {total} vulnerabilidades: {critical} críticas, {high} altas.",
            f"{fixed} foram corrigidas automaticamente pelo motor de autofix.",
        ]
        if cert:
            lines.append(f"Certificado emitido: {cert['number']}. Verifique em {cert['verify_url']}")
        else:
            lines.append("Certificado não emitido — score mínimo de 70/100 necessário.")

        result = {
            "response":       " ".join(lines),
            "ready_to_audit": True,
            "context":        {},
            "action":         "show_results",
        }
        return json.dumps(result, ensure_ascii=False)
