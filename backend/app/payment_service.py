"""payment_service.py — Integração Mercado Pago para AUDITX"""
import hashlib
import hmac
import os
from urllib.parse import urlparse

import mercadopago

ALLOWED_HOSTS = {
    "auditor.nexora360.cloud",
    "www.nexora360.cloud",
    "nexora360.cloud",
}

PLANS = {
    "laudo": {
        "title": "AUDITX \u2014 Acesso \u00danico",
        "price": 119.00,
        "description": "Laudo Blindagem + Efici\u00eancia + Certificado com QR Code",
    },
    "correcao": {
        "title": "AUDITX \u2014 Laudo + Corre\u00e7\u00e3o Autom\u00e1tica",
        "price": 299.00,
        "description": "Laudo completo + Auto-Fix aplicado + Projeto corrigido",
    },
    "dev": {
        "title": "AUDITX \u2014 Plano Dev (Mensal)",
        "price": 99.00,
        "description": "At\u00e9 5 auditorias/m\u00eas, 50MB, certificado com QR Code",
    },
    "pro": {
        "title": "AUDITX \u2014 Plano Pro (Mensal)",
        "price": 299.00,
        "description": "At\u00e9 20 auditorias/m\u00eas, 200MB, Auto-Fix, Suporte email",
    },
    "scale": {
        "title": "AUDITX \u2014 Plano Scale (Mensal)",
        "price": 899.00,
        "description": "Auditorias ilimitadas, 1GB, Auto-Fix ilimitado, CI/CD, Suporte 24/7",
    },
}


def _validate_base_url(base_url: str) -> str:
    parsed = urlparse(base_url)

    if parsed.scheme not in ("https", "http"):
        raise ValueError(
            f"AUDITX_BASE_URL possui esquema inválido: {parsed.scheme!r}. "
            "Apenas 'https' ou 'http' são permitidos."
        )

    hostname = parsed.hostname
    if hostname not in ALLOWED_HOSTS:
        raise ValueError(
            f"AUDITX_BASE_URL possui hostname não permitido: {hostname!r}. "
            f"Hosts permitidos: {ALLOWED_HOSTS}"
        )

    normalized = base_url.rstrip("/")
    return normalized


def validate_mercadopago_signature(
    x_signature: str,
    x_request_id: str,
    data_id: str,
    raw_body: bytes,
) -> bool:
    """
    Valida a assinatura HMAC-SHA256 enviada pelo Mercado Pago no header X-Signature.

    O Mercado Pago envia o header X-Signature no formato:
        ts=<timestamp>,v1=<hash>

    O template da mensagem assinada é:
        id:<data.id>;request-id:<x-request-id>;ts:<ts>;

    Referência: https://www.mercadopago.com.br/developers/pt/docs/your-integrations/notifications/webhooks

    Parâmetros:
        x_signature:  Valor do header X-Signature recebido na requisição.
        x_request_id: Valor do header X-Request-Id recebido na requisição.
        data_id:      Valor do parâmetro data.id recebido na query string.
        raw_body:     Corpo bruto da requisição (bytes), usado como fallback
                      caso o MP venha a incluir o body na assinatura futuramente.

    Retorna True se a assinatura for válida, False caso contrário.
    """
    secret = os.getenv("MP_WEBHOOK_SECRET", "")
    if not secret:
        raise RuntimeError("MP_WEBHOOK_SECRET não configurado no .env")

    ts = None
    v1 = None

    for part in x_signature.split(","):
        part = part.strip()
        if part.startswith("ts="):
            ts = part[3:]
        elif part.startswith("v1="):
            v1 = part[3:]

    if not ts or not v1:
        return False

    # Monta a string que o MP assina
    signed_template = f"id:{data_id};request-id:{x_request_id};ts:{ts};"

    expected = hmac.new(
        secret.encode("utf-8"),
        signed_template.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, v1)


class PaymentService:
    def __init__(self):
        token = os.getenv("MP_ACCESS_TOKEN", "")
        if not token:
            raise RuntimeError("MP_ACCESS_TOKEN n\u00e3o configurado no .env")
        self.sdk = mercadopago.SDK(token)

    def create_preference(self, plan: str, audit_id: str, email: str) -> dict:
        if plan not in PLANS:
            raise ValueError(f"Plano inv\u00e1lido: {plan!r}. Use laudo | correcao")

        p = PLANS[plan]
        raw_base = os.getenv("AUDITX_BASE_URL", "https://auditor.nexora360.cloud")

        try:
            base = _validate_base_url(raw_base)
        except ValueError as exc:
            raise RuntimeError(
                f"Configuração inválida de AUDITX_BASE_URL: {exc}"
            ) from exc

        preference_data = {
            "items": [{
                "title":       p["title"],
                "quantity":    1,
                "currency_id": "BRL",
                "unit_price":  p["price"],
                "description": p["description"],
            }],
            "payer": {"email": email},
            "back_urls": {
                "success": f"{base}/obrigado?audit_id={audit_id}&plan={plan}",
                "failure": f"{base}/erro?audit_id={audit_id}",
                "pending": f"{base}/pendente?audit_id={audit_id}",
            },
            "auto_return": "approved",
            "notification_url": f"{base}/api/webhook/mercadopago",
            "external_reference": f"{audit_id}|{plan}|{email}",
            "statement_descriptor": "AUDITX NEXORA",
        }

        result = self.sdk.preference().create(preference_data)
        resp   = result["response"]

        if "id" not in resp:
            raise RuntimeError(f"MP erro: {resp}")

        return {
            "preference_id":      resp["id"],
            "init_point":         resp["init_point"],
            "sandbox_init_point": resp.get("sandbox_init_point"),
        }

    def get_payment(self, payment_id: str) -> dict:
        result = self.sdk.payment().get(payment_id)
        return result["response"]

    def process_webhook(
        self,
        x_signature: str,
        x_request_id: str,
        data_id: str,
        raw_body: bytes,
        payload: dict,
    ) -> dict:
        """
        Processa uma notificação de webhook do Mercado Pago após validar
        a assinatura criptográfica.

        Lança ValueError se a assinatura for inválida, impedindo o
        processamento de notificações forjadas.

        Parâmetros:
            x_signature:  Header X-Signature da requisição.
            x_request_id: Header X-Request-Id da requisição.
            data_id:      Parâmetro data.id da query string.
            raw_body:     Corpo bruto da requisição em bytes.
            payload:      Corpo da requisição já deserializado (dict).

        Retorna o dict com os dados do pagamento consultado na API do MP.
        """
        if not x_signature:
            raise ValueError(
                "Notificação rejeitada: header X-Signature ausente."
            )

        if not validate_mercadopago_signature(
            x_signature=x_signature,
            x_request_id=x_request_id,
            data_id=data_id,
            raw_body=raw_body,
        ):
            raise ValueError(
                "Notificação rejeitada: assinatura X-Signature inválida."
            )

        payment_id = (
            payload.get("data", {}).get("id")
            or payload.get("id")
            or data_id
        )

        if not payment_id:
            raise ValueError(
                "Notificação rejeitada: payment_id não encontrado no payload."
            )

        return self.get_payment(str(payment_id))