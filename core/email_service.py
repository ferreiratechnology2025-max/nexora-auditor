"""
email_service.py — Envio de laudos AUDITX via SMTP Hostinger
=============================================================
Monta email HTML profissional com laudo como anexo .html.
Usa smtplib nativo — sem dependências externas.
"""

from __future__ import annotations
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


_SUBJECTS = {
    "security":    "🛡️ Laudo de Segurança AUDITX — {project} | Score {score_final}/100",
    "performance": "⚡ Laudo de Performance AUDITX — {project}",
    "certificate": "🏆 Certificado de Qualidade AUDITX — {project}",
}

_REPORT_LABELS = {
    "security":    "Segurança",
    "performance": "Performance",
    "certificate": "Certificado",
}

_BASE_URL = os.getenv("AUDITX_BASE_URL", "https://auditor.nexora360.cloud")


def _build_email_body(
    audit_id: str,
    project: str,
    score_initial: int,
    score_final: int,
    report_type: str,
    findings_summary: str = "",
) -> str:
    label       = _REPORT_LABELS.get(report_type, report_type.title())
    delta       = score_final - score_initial
    delta_str   = f"+{delta}" if delta >= 0 else str(delta)
    delta_color = "#30d158" if delta >= 0 else "#ff453a"
    score_color = ("#30d158" if score_final >= 80
                   else "#ffd60a" if score_final >= 50 else "#ff453a")
    report_url  = f"{_BASE_URL}/api/v2/audit/{audit_id}/report"

    bullets = findings_summary or (
        "• Auditoria estática completa executada com sucesso.<br/>"
        "• Auto-correção aplicada nos achados compatíveis.<br/>"
        "• Laudo completo disponível em anexo e no link abaixo."
    )

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
</head>
<body style="margin:0;padding:0;background:#0a0a0a;font-family:'Helvetica Neue',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" border="0"
       style="background:#0a0a0a;padding:40px 0;">
  <tr>
    <td align="center">
      <table width="600" cellpadding="0" cellspacing="0" border="0"
             style="max-width:600px;width:100%;">

        <!-- header -->
        <tr>
          <td style="background:linear-gradient(135deg,#1a0505,#0a0a0a);
                     border:1px solid rgba(255,255,255,.1);
                     border-radius:16px 16px 0 0;padding:32px;text-align:center;">
            <div style="font-size:32px;font-weight:900;letter-spacing:-1px;color:#fff;">
              AUDIT<span style="color:#ff453a;">X</span>
            </div>
            <div style="font-size:13px;color:rgba(255,255,255,.4);
                        margin-top:4px;letter-spacing:2px;text-transform:uppercase;">
              Laudo de {label}
            </div>
            <div style="font-size:15px;color:rgba(255,255,255,.7);
                        margin-top:10px;font-weight:600;">
              {project}
            </div>
          </td>
        </tr>

        <!-- score band -->
        <tr>
          <td style="background:rgba(255,255,255,.04);border-left:1px solid rgba(255,255,255,.1);
                     border-right:1px solid rgba(255,255,255,.1);padding:28px 32px;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td style="text-align:center;padding:0 16px;">
                  <div style="font-size:13px;color:rgba(255,255,255,.4);
                              text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">
                    Score Inicial
                  </div>
                  <div style="font-size:42px;font-weight:900;color:#888;">{score_initial}</div>
                </td>
                <td style="text-align:center;font-size:28px;color:rgba(255,255,255,.2);">→</td>
                <td style="text-align:center;padding:0 16px;">
                  <div style="font-size:13px;color:rgba(255,255,255,.4);
                              text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">
                    Score Final
                  </div>
                  <div style="font-size:42px;font-weight:900;color:{score_color};">{score_final}</div>
                </td>
                <td style="text-align:center;padding:0 16px;">
                  <div style="font-size:13px;color:rgba(255,255,255,.4);margin-bottom:6px;">Melhoria</div>
                  <div style="font-size:28px;font-weight:900;color:{delta_color};">{delta_str}</div>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- findings -->
        <tr>
          <td style="background:rgba(255,255,255,.03);border-left:1px solid rgba(255,255,255,.1);
                     border-right:1px solid rgba(255,255,255,.1);padding:24px 32px;">
            <div style="font-size:13px;font-weight:700;color:rgba(255,255,255,.5);
                        text-transform:uppercase;letter-spacing:1px;margin-bottom:14px;">
              Principais Achados
            </div>
            <div style="font-size:14px;color:rgba(255,255,255,.8);line-height:2;">
              {bullets}
            </div>
          </td>
        </tr>

        <!-- cta -->
        <tr>
          <td style="background:rgba(255,255,255,.04);border-left:1px solid rgba(255,255,255,.1);
                     border-right:1px solid rgba(255,255,255,.1);
                     padding:28px 32px;text-align:center;">
            <a href="{report_url}"
               style="display:inline-block;background:#ff453a;color:#fff;
                      text-decoration:none;font-weight:700;font-size:14px;
                      padding:14px 32px;border-radius:8px;letter-spacing:.5px;">
              Ver Laudo Completo →
            </a>
            <div style="font-size:11px;color:rgba(255,255,255,.3);margin-top:10px;">
              O laudo completo também está anexado a este email.
            </div>
          </td>
        </tr>

        <!-- footer -->
        <tr>
          <td style="background:#080808;border:1px solid rgba(255,255,255,.1);
                     border-radius:0 0 16px 16px;padding:20px 32px;text-align:center;">
            <div style="font-size:12px;color:rgba(255,255,255,.25);line-height:1.8;">
              <strong style="color:rgba(255,255,255,.4);">AUDITX</strong>
              &nbsp;|&nbsp; auditor.nexora360.cloud<br/>
              Auditoria ID: <code style="font-size:11px;">{audit_id[:16]}…</code><br/>
              <a href="{_BASE_URL}/unsubscribe" style="color:rgba(255,255,255,.2);">Remover-me</a>
            </div>
          </td>
        </tr>

      </table>
    </td>
  </tr>
</table>
</body>
</html>"""


class EmailService:
    """Serviço de envio de laudos AUDITX via SMTP Hostinger (SSL porta 465)."""

    def __init__(self):
        self.host      = os.getenv("SMTP_HOST",      "smtp.hostinger.com")
        self.port      = int(os.getenv("SMTP_PORT",  "465"))
        self.user      = os.getenv("SMTP_USER",      "")
        self.password  = os.getenv("SMTP_PASSWORD",  "")
        self.from_name = os.getenv("SMTP_FROM_NAME", "AUDITX — Nexora")

    def send_report(
        self,
        to_email:     str,
        audit_id:     str,
        score_initial: int,
        score_final:  int,
        report_type:  str,
        html_report:  str,
        project_name: str = "seu projeto",
        findings_summary: str = "",
    ) -> bool:
        """
        Envia laudo por email.

        Returns:
            True se enviado com sucesso, False caso contrário.
        """
        if not self.user or not self.password:
            raise ValueError(
                "SMTP_USER e SMTP_PASSWORD devem estar definidos no .env"
            )

        subj_tmpl = _SUBJECTS.get(report_type, "📋 Laudo AUDITX — {project}")
        subject   = subj_tmpl.format(project=project_name, score_final=score_final)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"{self.from_name} <{self.user}>"
        msg["To"]      = to_email

        # Corpo HTML
        body_html = _build_email_body(
            audit_id=audit_id,
            project=project_name,
            score_initial=score_initial,
            score_final=score_final,
            report_type=report_type,
            findings_summary=findings_summary,
        )
        msg.attach(MIMEText(body_html, "html", "utf-8"))

        # Anexo: laudo completo como .html
        attachment = MIMEApplication(html_report.encode("utf-8"), Name="")
        filename   = f"auditx_{report_type}_{audit_id[:8]}.html"
        attachment["Content-Disposition"] = f'attachment; filename="{filename}"'
        attachment["Content-Type"]        = "text/html; charset=utf-8"
        msg.attach(attachment)

        try:
            with smtplib.SMTP_SSL(self.host, self.port, timeout=15) as smtp:
                smtp.login(self.user, self.password)
                smtp.sendmail(self.user, to_email, msg.as_string())
            return True
        except smtplib.SMTPException as exc:
            raise RuntimeError(f"Falha SMTP: {exc}") from exc
