"""
reports/__init__.py — ReportGenerator
Fachada que unifica os 3 tipos de laudo AUDITX.
"""

from app.reports import report_security, report_performance, report_certificate


class ReportGenerator:
    def security(self, audit_data: dict) -> str:
        """Laudo de Segurança (Blindagem) — score, vulns, LGPD."""
        return report_security.generate(audit_data)

    def performance(self, audit_data: dict) -> str:
        """Laudo de Eficiência — code smells, complexidade, memória."""
        return report_performance.generate(audit_data)

    def certificate(self, audit_data: dict) -> str:
        """Certificado de Qualidade — docs, PEP8, QR de validação."""
        return report_certificate.generate(audit_data)
