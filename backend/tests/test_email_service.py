"""
test_email_service.py — Testa EmailService sem envio real (mock smtplib.SMTP_SSL)
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.email_service import EmailService, _build_email_body

# ── fixtures ──────────────────────────────────────────────────────────────────

AUDIT_ID      = "aabbccdd-1122-3344-5566-778899aabbcc"
SCORE_INITIAL = 40
SCORE_FINAL   = 90
PROJECT       = "meu-projeto-saas"

MOCK_ENV = {
    "SMTP_HOST":      "smtp.hostinger.com",
    "SMTP_PORT":      "465",
    "SMTP_USER":      "auditx@nexora360.cloud",
    "SMTP_PASSWORD":  "senha-teste",
    "SMTP_FROM_NAME": "AUDITX — Nexora",
}


def _make_service() -> EmailService:
    with patch.dict(os.environ, MOCK_ENV):
        return EmailService()


# =============================================================================
# Testes de _build_email_body
# =============================================================================

class TestBuildEmailBody:

    def test_security_body_contains_score(self):
        html = _build_email_body(AUDIT_ID, PROJECT, SCORE_INITIAL, SCORE_FINAL, "security")
        assert str(SCORE_INITIAL) in html
        assert str(SCORE_FINAL)   in html

    def test_security_body_contains_audit_id(self):
        html = _build_email_body(AUDIT_ID, PROJECT, SCORE_INITIAL, SCORE_FINAL, "security")
        assert AUDIT_ID[:16] in html

    def test_security_body_contains_project(self):
        html = _build_email_body(AUDIT_ID, PROJECT, SCORE_INITIAL, SCORE_FINAL, "security")
        assert PROJECT in html

    def test_performance_body_label(self):
        html = _build_email_body(AUDIT_ID, PROJECT, SCORE_INITIAL, SCORE_FINAL, "performance")
        assert "Performance" in html

    def test_certificate_body_label(self):
        html = _build_email_body(AUDIT_ID, PROJECT, SCORE_INITIAL, SCORE_FINAL, "certificate")
        assert "Certificado" in html

    def test_body_has_cta_button(self):
        html = _build_email_body(AUDIT_ID, PROJECT, SCORE_INITIAL, SCORE_FINAL, "security")
        assert "Ver Laudo Completo" in html

    def test_body_has_unsubscribe_link(self):
        html = _build_email_body(AUDIT_ID, PROJECT, SCORE_INITIAL, SCORE_FINAL, "security")
        assert "Remover-me" in html

    def test_delta_positive(self):
        html = _build_email_body(AUDIT_ID, PROJECT, 40, 90, "security")
        assert "+50" in html

    def test_delta_negative(self):
        html = _build_email_body(AUDIT_ID, PROJECT, 80, 60, "security")
        assert "-20" in html


# =============================================================================
# Testes de EmailService.send_report (mock SMTP_SSL)
# =============================================================================

class TestEmailServiceSend:

    def _call_send(self, report_type: str = "security") -> tuple[bool, MagicMock]:
        mock_smtp = MagicMock()
        smtp_ctx  = MagicMock()
        smtp_ctx.__enter__ = MagicMock(return_value=mock_smtp)
        smtp_ctx.__exit__  = MagicMock(return_value=False)

        with patch.dict(os.environ, MOCK_ENV):
            svc = EmailService()
            with patch("smtplib.SMTP_SSL", return_value=smtp_ctx) as smtp_cls:
                result = svc.send_report(
                    to_email="cliente@empresa.com",
                    audit_id=AUDIT_ID,
                    score_initial=SCORE_INITIAL,
                    score_final=SCORE_FINAL,
                    report_type=report_type,
                    html_report="<html><body>Laudo</body></html>",
                    project_name=PROJECT,
                )
        return result, mock_smtp

    def test_returns_true_on_success(self):
        ok, _ = self._call_send()
        assert ok is True

    def test_smtp_ssl_called_with_correct_host_port(self):
        mock_smtp = MagicMock()
        smtp_ctx  = MagicMock()
        smtp_ctx.__enter__ = MagicMock(return_value=mock_smtp)
        smtp_ctx.__exit__  = MagicMock(return_value=False)

        with patch.dict(os.environ, MOCK_ENV):
            svc = EmailService()
            with patch("smtplib.SMTP_SSL", return_value=smtp_ctx) as smtp_cls:
                svc.send_report(
                    to_email="x@y.com", audit_id=AUDIT_ID,
                    score_initial=40, score_final=90, report_type="security",
                    html_report="<html/>", project_name=PROJECT,
                )
                smtp_cls.assert_called_once_with("smtp.hostinger.com", 465, timeout=15)

    def test_login_called_with_credentials(self):
        _, mock_smtp = self._call_send()
        mock_smtp.login.assert_called_once_with(
            "auditx@nexora360.cloud", "senha-teste"
        )

    def test_sendmail_called(self):
        _, mock_smtp = self._call_send()
        assert mock_smtp.sendmail.called

    def test_sendmail_to_correct_address(self):
        _, mock_smtp = self._call_send()
        args = mock_smtp.sendmail.call_args[0]
        assert "cliente@empresa.com" in args[1]

    def test_email_subject_security(self):
        _, mock_smtp = self._call_send("security")
        raw_email = mock_smtp.sendmail.call_args[0][2]
        assert "Seguran" in raw_email   # "Segurança" (pode ter encoding)
        assert PROJECT in raw_email

    def test_email_subject_performance(self):
        _, mock_smtp = self._call_send("performance")
        raw_email = mock_smtp.sendmail.call_args[0][2]
        assert "Performance" in raw_email

    def test_email_subject_certificate(self):
        _, mock_smtp = self._call_send("certificate")
        raw_email = mock_smtp.sendmail.call_args[0][2]
        assert "Certificado" in raw_email

    def test_attachment_present(self):
        _, mock_smtp = self._call_send()
        raw_email = mock_smtp.sendmail.call_args[0][2]
        assert "auditx_security_" in raw_email
        assert "attachment" in raw_email.lower()

    def test_raises_valueerror_without_credentials(self):
        with patch.dict(os.environ, {"SMTP_USER": "", "SMTP_PASSWORD": ""}, clear=False):
            svc = EmailService()
            with pytest.raises(ValueError, match="SMTP_USER"):
                svc.send_report(
                    to_email="x@y.com", audit_id=AUDIT_ID,
                    score_initial=40, score_final=90,
                    report_type="security", html_report="<html/>",
                )
