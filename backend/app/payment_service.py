"""payment_service.py — Integração Mercado Pago para AUDITX"""
import os

import mercadopago

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


class PaymentService:
    def __init__(self):
        token = os.getenv("MP_ACCESS_TOKEN", "")
        if not token:
            raise RuntimeError("MP_ACCESS_TOKEN n\u00e3o configurado no .env")
        self.sdk = mercadopago.SDK(token)

    def create_preference(self, plan: str, audit_id: str, email: str) -> dict:
        if plan not in PLANS:
            raise ValueError(f"Plano inv\u00e1lido: {plan!r}. Use laudo | correcao")

        p    = PLANS[plan]
        base = os.getenv("AUDITX_BASE_URL", "https://auditor.nexora360.cloud")

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
