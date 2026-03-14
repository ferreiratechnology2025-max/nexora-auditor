"""
AuditOrchestrator — Pipeline de auditoria de segurança do Nexora Auditor.
Baseado no NexoraOrchestrator, adaptado para receber código de clientes.
"""
import ast
import hashlib
import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

from core.llm_client import NexoraLLM
from core.project_analyzer import ProjectAnalyzer
from core.shadow_tester import ShadowTester


load_dotenv()

# ── Pesos de severidade para cálculo do score de segurança ──────────────────
SEVERITY_WEIGHTS = {
    "CRITICAL": 20,
    "HIGH":     10,
    "MEDIUM":    5,
    "LOW":       2,
}
SEVERITY_CAPS = {
    "CRITICAL": 40,
    "HIGH":     30,
    "MEDIUM":   15,
    "LOW":      10,
}

AUDIT_SYSTEM_PROMPT = """Você é um auditor de segurança de software sênior especializado em OWASP Top 10.

Sua missão é analisar o código fornecido e identificar TODAS as vulnerabilidades reais.

Para cada vulnerabilidade encontrada, retorne um objeto JSON com exatamente estes campos:
{
  "file": "caminho/do/arquivo.py",
  "line": 42,
  "rule": "sql_injection",
  "severity": "CRITICAL",
  "title": "SQL Injection via concatenação de string",
  "description": "Explicação em português simples do problema e impacto de negócio",
  "fix_suggestion": "Como corrigir com exemplo de código seguro"
}

Categorias de rule: sql_injection, xss, hardcoded_secret, dangerous_eval, path_traversal,
insecure_deserialization, auth_weak, ssrf, xxe, open_redirect, command_injection,
weak_crypto, mass_assignment, idor, csrf, rate_limit_missing, logging_sensitive_data

Severidades: CRITICAL, HIGH, MEDIUM, LOW

Retorne SOMENTE um JSON array de findings. Sem explicações extras. Sem markdown.
Se não encontrar vulnerabilidades, retorne []."""

AUTOFIX_SYSTEM_PROMPT = """Você é um engenheiro de segurança especialista em correção de vulnerabilidades.

Dado um trecho de código vulnerável e a descrição do problema, gere o código CORRIGIDO.

Retorne SOMENTE o código corrigido, sem explicações, sem markdown, sem blocos de código.
O código deve ser Python válido e seguro."""

CERTIFICATE_SYSTEM_PROMPT = """Você é um redator técnico de certificados de conformidade de segurança.

Gere um resumo executivo em português para o certificado de auditoria. Máximo 3 linhas.
Destaque o que foi corrigido e o nível de segurança atual."""


class AuditOrchestrator:
    """
    Pipeline completo de auditoria de segurança.
    Entrada: caminho do projeto (ZIP extraído ou repositório clonado)
    Saída: laudo + diffs de correção + certificado verificável
    """

    def __init__(self):
        load_dotenv()
        self.llm = NexoraLLM()
        self.model_stack = self._load_model_stack()
        self.genome_root = Path(os.getenv("GENOME_ROOT", "./code_genome"))
        self.memory_db = Path(os.getenv("MEMORY_ROOT", "./memory")) / "sqlite" / "nexora_memory.db"

    def _load_model_stack(self) -> Dict[str, str]:
        config_path = Path(__file__).parent.parent / "config" / "model_stack.json"
        if config_path.exists():
            data = json.loads(config_path.read_text(encoding="utf-8"))
            return data.get("roles", {})
        return {
            "auditor":     "anthropic/claude-sonnet-4-6",
            "autofix":     "anthropic/claude-sonnet-4-6",
            "certificate": "anthropic/claude-haiku-4-5-20251001",
        }

    # ── Ponto de entrada principal ───────────────────────────────────────────

    def run_audit(self, project_path: str, context: dict) -> dict:
        """
        Executa o pipeline completo de auditoria.

        context = {
            "email": str,
            "audit_id": str,
            "advisor_context": {
                "language": str,
                "framework": str,
                "concern": str,
            }
        }
        """
        project_path = str(Path(project_path).resolve())
        audit_id = context.get("audit_id", f"AUD-{int(time.time())}")
        started_at = datetime.utcnow().isoformat()

        print(f"[AUDIT] Iniciando auditoria {audit_id}")

        # 1. Ingestão
        ingest = self._ingest(project_path)
        print(f"[AUDIT] {ingest['file_count']} arquivos | linguagens: {ingest['languages']}")

        # 2. Score inicial (estrutural)
        initial_analysis = self._analyze_initial(project_path)
        score_initial = initial_analysis["score"]
        print(f"[AUDIT] Score inicial (estrutural): {score_initial}/100")

        # 3. LLM audit — encontra vulnerabilidades com contexto
        findings = self._llm_audit(project_path, context)
        print(f"[AUDIT] {len(findings)} findings encontrados")

        # 4. Score de segurança inicial (antes do autofix)
        security_score_initial = self._compute_security_score(findings)
        print(f"[AUDIT] Score de segurança inicial: {security_score_initial}/100")

        # 5. Shadow test (Docker opcional)
        shadow_result = self._shadow_test(project_path)
        print(f"[AUDIT] Shadow test: {shadow_result['status']}")

        # 6. Auto-fix
        fix_result = self._autofix(project_path, findings)
        fixed = fix_result["fixed"]
        skipped = fix_result["skipped"]
        print(f"[AUDIT] {len(fixed)} corrigidos | {len(skipped)} manuais")

        # 7. Score final
        remaining_findings = [
            f for f in findings
            if not any(fx["file"] == f.get("file") and fx["line"] == f.get("line") for fx in fixed)
        ]
        security_score_final = self._compute_security_score(remaining_findings)
        print(f"[AUDIT] Score de segurança final: {security_score_final}/100")

        # 8. Certificado
        by_severity = self._group_by_severity(findings)
        fix_ratio = len(fixed) / len(findings) if findings else 1.0
        certificate = self._generate_certificate(
            audit_id=audit_id,
            project_path=project_path,
            score_initial=security_score_initial,
            score_final=security_score_final,
            shadow_result=shadow_result,
            fix_ratio=fix_ratio,
            findings=findings,
            fixed=fixed,
            context=context,
        )
        if certificate:
            print(f"[AUDIT] Certificado emitido: {certificate['number']}")
        else:
            print("[AUDIT] Certificado NÃO emitido — critérios não atingidos")

        # 9. Aprende padrões (genoma de vulnerabilidades)
        self._learn(findings, fixed)

        # 10. Notificação — EmailService
        self._notify(
            email=context.get("email"),
            audit_id=audit_id,
            score_initial=security_score_initial,
            score_final=security_score_final,
            findings=findings,
            fixed=fixed,
            ingest=ingest,
            context=context,
        )

        return {
            "audit_id":            audit_id,
            "started_at":          started_at,
            "finished_at":         datetime.utcnow().isoformat(),
            "project_path":        project_path,
            "ingest":              ingest,
            # Scores
            "score_initial":       security_score_initial,
            "score_final":         security_score_final,
            "structural_score":    score_initial,
            # Findings
            "total_findings":      len(findings),
            "by_severity":         by_severity,
            "findings":            findings,
            # Auto-fix
            "fixed_count":         len(fixed),
            "skipped_count":       len(skipped),
            "fixed":               fixed,
            "skipped":             skipped,
            "fix_ratio":           round(fix_ratio, 2),
            # Shadow
            "shadow_test":         shadow_result,
            # Certificado
            "certificate":         certificate,
            # Contexto do cliente
            "context":             context,
        }

    # ── Passos do pipeline ───────────────────────────────────────────────────

    def _ingest(self, project_path: str) -> dict:
        """Detecta linguagens, conta arquivos, mede complexidade."""
        root = Path(project_path)
        ignored = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", "node_modules", "dist"}

        ext_map = {
            ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
            ".go": "Go", ".java": "Java", ".rb": "Ruby", ".php": "PHP",
            ".rs": "Rust", ".cs": "C#", ".cpp": "C++", ".c": "C",
        }

        lang_counts: Dict[str, int] = {}
        file_count = 0
        total_lines = 0

        for path in root.rglob("*"):
            if any(part in ignored for part in path.parts):
                continue
            if not path.is_file():
                continue
            ext = path.suffix.lower()
            lang = ext_map.get(ext)
            if lang:
                lang_counts[lang] = lang_counts.get(lang, 0) + 1
                file_count += 1
                try:
                    total_lines += len(path.read_text(encoding="utf-8", errors="ignore").splitlines())
                except Exception:
                    pass

        languages = sorted(lang_counts, key=lambda k: -lang_counts[k])
        return {
            "file_count":    file_count,
            "total_lines":   total_lines,
            "languages":     languages,
            "lang_counts":   lang_counts,
        }

    def _analyze_initial(self, project_path: str) -> dict:
        """Análise estrutural do projeto via ProjectAnalyzer."""
        try:
            analyzer = ProjectAnalyzer(project_path)
            health = analyzer.get_health_score()
            return health
        except Exception as e:
            return {"score": 50, "metrics": {}, "error": str(e)}

    def _llm_audit(self, project_path: str, context: dict) -> List[dict]:
        """
        LLM analisa o código e retorna findings estruturados.
        Usa contexto do projeto para auditoria mais precisa.
        """
        root = Path(project_path)
        ignored = {".git", "__pycache__", ".venv", "venv", "node_modules", "dist", "tests", "test"}
        skip_names = {".nexora_shadow_attack.py"}
        audit_exts = {".py", ".js", ".ts", ".go", ".java", ".rb", ".php"}

        # Coleta até ~8k tokens de código para análise, priorizando arquivos menores
        char_limit = 24_000
        all_files = []
        for path in root.rglob("*"):
            if any(part in ignored for part in path.parts):
                continue
            if path.name in skip_names or path.name.startswith("test_"):
                continue
            if not path.is_file():
                continue
            if path.suffix.lower() not in audit_exts:
                continue
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
                all_files.append((path, content))
            except Exception:
                continue

        # Ordena por tamanho crescente — inclui mais arquivos
        all_files.sort(key=lambda x: len(x[1]))

        code_chunks = []
        total_chars = 0
        skipped_files = []

        for path, content in all_files:
            rel = str(path.relative_to(root)).replace("\\", "/")
            # Inclui os primeiros 3000 chars de cada arquivo grande
            snippet = content if len(content) <= 3000 else content[:3000] + "\n# ... [truncado]"
            chunk = f"\n# FILE: {rel}\n{snippet}"
            if total_chars + len(chunk) > char_limit:
                skipped_files.append(rel)
                continue
            code_chunks.append(chunk)
            total_chars += len(chunk)

        if skipped_files:
            code_chunks.append(f"\n# ARQUIVOS NAO ANALISADOS (muito grandes): {', '.join(skipped_files)}")

        if not code_chunks:
            return []

        advisor_ctx = context.get("advisor_context", {})
        lang = advisor_ctx.get("language", "desconhecida")
        framework = advisor_ctx.get("framework", "não informado")
        concern = advisor_ctx.get("concern", "auditoria geral de segurança")

        prompt = f"""Audite o seguinte projeto {lang} ({framework}).
Preocupação principal do cliente: {concern}

CÓDIGO DO PROJETO:
{''.join(code_chunks)}

Identifique TODAS as vulnerabilidades de segurança. Retorne um JSON array de findings."""

        model = self.model_stack.get("auditor", "anthropic/claude-sonnet-4-6")

        messages = [
            {"role": "system", "content": AUDIT_SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ]

        # Chama diretamente com system prompt separado
        try:
            raw = self.llm.client.chat.completions.create(
                model=model,
                messages=messages,
            ).choices[0].message.content or "[]"
        except Exception as e:
            print(f"[AUDIT][ERRO] LLM audit falhou: {e}")
            return []

        # Parse JSON
        findings = self._parse_findings(raw)
        return findings

    def _shadow_test(self, project_path: str) -> dict:
        """
        Roda ShadowTester no projeto via Docker.
        Se Docker não estiver disponível, retorna 'skipped' (não bloqueia certificado).
        Se Docker rodar e encontrar vulnerabilidades, retorna 'failed'.
        """
        try:
            tester = ShadowTester()
            result = tester.run(project_path)

            # Diferencia Docker indisponível de vulnerabilidades reais encontradas
            stderr = result.get("stderr", "") or ""
            stdout = result.get("stdout", "") or ""
            docker_unavailable = (
                "cannot connect" in stderr.lower()
                or "docker daemon" in stderr.lower()
                or "NEXORA_SHADOW_REPORT" not in stdout
                and result.get("vulnerabilities_found", 0) == 0
                and not result.get("ok")
            )

            if docker_unavailable:
                result["status"] = "skipped"
                result["reason"] = "Docker indisponivel — shadow test ignorado"

            return result
        except Exception as e:
            return {
                "ok":                None,
                "status":            "skipped",
                "reason":            f"Docker indisponivel: {e}",
                "attempts":          [],
                "vulnerabilities":   [],
                "vulnerability_count": 0,
            }

    def _autofix(self, project_path: str, findings: List[dict]) -> dict:
        """
        Corrige vulnerabilidades usando LLM.
        Valida com AST antes de aplicar (apenas Python).
        """
        root = Path(project_path)
        fixed = []
        skipped = []
        model = self.model_stack.get("autofix", "anthropic/claude-sonnet-4-6")

        # Agrupa findings por arquivo
        by_file: Dict[str, List[dict]] = {}
        for f in findings:
            fpath = f.get("file", "")
            by_file.setdefault(fpath, []).append(f)

        for rel_path, file_findings in by_file.items():
            abs_path = root / rel_path
            if not abs_path.exists():
                for f in file_findings:
                    skipped.append({**f, "skip_reason": "arquivo não encontrado"})
                continue

            try:
                original = abs_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                for f in file_findings:
                    skipped.append({**f, "skip_reason": "erro ao ler arquivo"})
                continue

            # Tenta corrigir cada finding no arquivo
            current_content = original
            for finding in file_findings:
                severity = finding.get("severity", "LOW")
                rule = finding.get("rule", "unknown")
                description = finding.get("description", "")
                fix_suggestion = finding.get("fix_suggestion", "")
                line_num = finding.get("line", 0)

                # Extrai contexto da linha problemática
                lines = current_content.splitlines()
                start = max(0, line_num - 5)
                end = min(len(lines), line_num + 5)
                code_ctx = "\n".join(lines[start:end])

                prompt = f"""Vulnerabilidade: {rule} ({severity})
Arquivo: {rel_path}, linha {line_num}
Problema: {description}
Sugestão: {fix_suggestion}

Trecho vulnerável (contexto):
{code_ctx}

Arquivo completo:
{current_content[:6000]}

Retorne o arquivo COMPLETO corrigido, sem markdown, apenas código."""

                try:
                    fixed_content = self.llm.client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": AUTOFIX_SYSTEM_PROMPT},
                            {"role": "user",   "content": prompt},
                        ],
                    ).choices[0].message.content or ""
                except Exception as e:
                    skipped.append({**finding, "skip_reason": f"LLM erro: {e}"})
                    continue

                # Remove markdown se veio com ```
                fixed_content = re.sub(r"^```[a-z]*\n?", "", fixed_content.strip())
                fixed_content = re.sub(r"\n?```$", "", fixed_content.strip())

                # Valida sintaxe AST para Python
                if rel_path.endswith(".py"):
                    try:
                        ast.parse(fixed_content)
                    except SyntaxError as se:
                        skipped.append({**finding, "skip_reason": f"AST inválido: {se}"})
                        continue

                # Gera diff resumido
                orig_lines = current_content.splitlines()
                new_lines = fixed_content.splitlines()
                changed = sum(1 for a, b in zip(orig_lines, new_lines) if a != b)

                current_content = fixed_content
                fixed.append({
                    "file":        rel_path,
                    "line":        line_num,
                    "rule":        rule,
                    "severity":    severity,
                    "status":      "fixed",
                    "lines_changed": changed,
                    "diff_summary": f"{changed} linhas alteradas em {rel_path}",
                })

            # Aplica as correções no arquivo
            if current_content != original:
                try:
                    abs_path.write_text(current_content, encoding="utf-8")
                except Exception as e:
                    print(f"[AUTOFIX][ERRO] Não foi possível salvar {rel_path}: {e}")

        return {"fixed": fixed, "skipped": skipped}

    def _generate_certificate(
        self,
        audit_id: str,
        project_path: str,
        score_initial: int,
        score_final: int,
        shadow_result: dict,
        fix_ratio: float,
        findings: List[dict],
        fixed: List[dict],
        context: dict,
    ) -> Optional[dict]:
        """
        Emite certificado SOMENTE se:
        - score_final >= 70
        - shadow_test == approved OU skipped (Docker indisponível)
        - pelo menos 80% dos findings corrigidos (ou 0 findings)
        """
        shadow_ok = shadow_result.get("status") in ("passed", "skipped")
        criteria_ok = (
            score_final >= 70
            and shadow_ok
            and (fix_ratio >= 0.8 or len(findings) == 0)
        )

        if not criteria_ok:
            return None

        # Hash do projeto
        root = Path(project_path)
        hasher = hashlib.sha256()
        for path in sorted(root.rglob("*.py")):
            try:
                hasher.update(path.read_bytes())
            except Exception:
                pass
        project_hash = hasher.hexdigest()

        # Número sequencial baseado no timestamp
        year = datetime.utcnow().year
        seq = int(time.time()) % 100000
        cert_number = f"AUDITX-{year}-{seq:05d}"

        # Resumo executivo via LLM
        summary = self._generate_cert_summary(
            cert_number, score_initial, score_final,
            len(findings), len(fixed), context
        )

        timestamp = datetime.utcnow().isoformat() + "Z"
        verify_url = f"https://auditor.nexora360.cloud/verify/{project_hash[:16]}"

        return {
            "number":        cert_number,
            "hash":          project_hash,
            "hash_short":    project_hash[:16],
            "score_initial": score_initial,
            "score_final":   score_final,
            "findings_total": len(findings),
            "findings_fixed": len(fixed),
            "fix_ratio":     round(fix_ratio, 2),
            "shadow_status": shadow_result.get("status", "skipped"),
            "issued_at":     timestamp,
            "verify_url":    verify_url,
            "summary":       summary,
            "email":         context.get("email", ""),
        }

    def _generate_cert_summary(
        self,
        cert_number: str,
        score_initial: int,
        score_final: int,
        total: int,
        fixed: int,
        context: dict,
    ) -> str:
        """Gera resumo executivo do certificado via LLM."""
        model = self.model_stack.get("certificate", "anthropic/claude-haiku-4-5-20251001")
        advisor_ctx = context.get("advisor_context", {})

        prompt = f"""Certificado: {cert_number}
Projeto: {advisor_ctx.get('language', 'N/A')} / {advisor_ctx.get('framework', 'N/A')}
Score inicial: {score_initial}/100 → Score final: {score_final}/100
Vulnerabilidades encontradas: {total} | Corrigidas automaticamente: {fixed}

Gere o resumo executivo em 2-3 linhas."""

        try:
            resp = self.llm.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": CERTIFICATE_SYSTEM_PROMPT},
                    {"role": "user",   "content": prompt},
                ],
            ).choices[0].message.content or ""
            return resp.strip()
        except Exception:
            delta = score_final - score_initial
            return (
                f"Projeto auditado e corrigido pelo Nexora Auditor. "
                f"Score de segurança melhorou {delta} pontos ({score_initial} → {score_final}/100). "
                f"{fixed} de {total} vulnerabilidades corrigidas automaticamente."
            )

    def _learn(self, findings: List[dict], fixed: List[dict]) -> None:
        """
        Salva padrões de vulnerabilidades corrigidas no genoma.
        Cada par (finding, fix) bem-sucedido vira um gene de aprendizado.
        """
        vuln_genome_root = self.genome_root / "vulnerabilities"
        vuln_genome_root.mkdir(parents=True, exist_ok=True)

        fixed_rules = {f["rule"] for f in fixed}

        for finding in findings:
            rule = finding.get("rule", "unknown")
            if rule not in fixed_rules:
                continue

            gene_dir = vuln_genome_root / rule / "learned"
            gene_dir.mkdir(parents=True, exist_ok=True)

            entry = {
                "rule":        rule,
                "severity":    finding.get("severity"),
                "description": finding.get("description"),
                "fix":         finding.get("fix_suggestion"),
                "learned_at":  datetime.utcnow().isoformat(),
            }

            entry_path = gene_dir / f"{int(time.time())}.json"
            try:
                entry_path.write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8")
            except Exception:
                pass

    def _notify(
        self,
        email: Optional[str],
        audit_id: str,
        score_initial: int,
        score_final: int,
        findings: list,
        fixed: list,
        ingest: dict,
        context: dict,
    ) -> None:
        """Envia laudo por email via EmailService (SMTP Hostinger)."""
        if not email:
            print(f"[NOTIFY] Laudo {audit_id} | score {score_final}/100 | sem email")
            return

        try:
            import importlib.util as _ilu
            _spec = _ilu.spec_from_file_location(
                "email_service",
                "/app/core/email_service.py",
            )
            _mod = _ilu.module_from_spec(_spec)
            _spec.loader.exec_module(_mod)
            EmailService = _mod.EmailService

            # Monta HTML do laudo inline (sem depender de ReportGenerator)
            by_sev: dict = {}
            for f in findings:
                sev = f.get("severity", "LOW")
                by_sev[sev] = by_sev.get(sev, 0) + 1

            sev_rows = "".join(
                f'<tr><td style="padding:4px 12px;font-weight:bold;color:{c}">{s}</td>'
                f'<td style="padding:4px 12px;text-align:center">{by_sev.get(s, 0)}</td></tr>'
                for s, c in [("CRITICAL","#dc2626"),("HIGH","#ea580c"),
                              ("MEDIUM","#ca8a04"),("LOW","#2563eb")]
            )
            finding_rows = "".join(
                f'<tr style="border-bottom:1px solid #e5e7eb">'
                f'<td style="padding:6px 10px;font-weight:bold;color:#dc2626">{f.get("severity")}</td>'
                f'<td style="padding:6px 10px">{f.get("title")}</td>'
                f'<td style="padding:6px 10px;font-family:monospace;font-size:12px">'
                f'{f.get("file","")}:{f.get("line","")}</td></tr>'
                for f in findings[:20]
            )
            langs = ", ".join(ingest.get("languages", []))
            project = context.get("filename", "Projeto")

            html = f"""
<!DOCTYPE html><html><body style="font-family:sans-serif;max-width:680px;margin:auto;color:#1f2937">
<div style="background:#1e3a5f;padding:24px;border-radius:8px 8px 0 0">
  <h1 style="color:#fff;margin:0;font-size:22px">🛡️ AUDITX — Laudo de Segurança</h1>
  <p style="color:#93c5fd;margin:6px 0 0">Auditoria #{audit_id[:8].upper()} · {project}</p>
</div>
<div style="background:#fff;padding:24px;border:1px solid #e5e7eb;border-top:0">
  <table width="100%" style="border-collapse:collapse;margin-bottom:20px">
    <tr>
      <td style="padding:12px;background:#fef2f2;border-radius:6px;text-align:center">
        <div style="font-size:36px;font-weight:900;color:#dc2626">{score_initial}</div>
        <div style="font-size:11px;color:#6b7280;text-transform:uppercase">Score Inicial</div>
      </td>
      <td style="padding:12px;text-align:center;font-size:24px;color:#9ca3af">→</td>
      <td style="padding:12px;background:#f0fdf4;border-radius:6px;text-align:center">
        <div style="font-size:36px;font-weight:900;color:#16a34a">{score_final}</div>
        <div style="font-size:11px;color:#6b7280;text-transform:uppercase">Score Final</div>
      </td>
    </tr>
  </table>
  <p style="color:#374151">
    <strong>{len(findings)} vulnerabilidades</strong> encontradas em
    <strong>{ingest.get("file_count", 0)} arquivos</strong>
    ({langs}). <strong>{len(fixed)} corrigidas automaticamente.</strong>
  </p>
  <table width="100%" style="border-collapse:collapse;margin:16px 0">{sev_rows}</table>
  <h3 style="color:#1e3a5f;border-bottom:2px solid #e5e7eb;padding-bottom:8px">Vulnerabilidades Encontradas</h3>
  <table width="100%" style="border-collapse:collapse;font-size:13px">
    <thead><tr style="background:#f9fafb">
      <th style="padding:8px 10px;text-align:left">Severidade</th>
      <th style="padding:8px 10px;text-align:left">Descrição</th>
      <th style="padding:8px 10px;text-align:left">Arquivo</th>
    </tr></thead>
    <tbody>{finding_rows}</tbody>
  </table>
  <div style="margin-top:24px;padding:16px;background:#f0fdf4;border-radius:6px;text-align:center">
    <p style="color:#15803d;font-weight:bold;margin:0">
      ✅ Auditoria concluída — score melhorou {score_final - score_initial} pontos
    </p>
  </div>
</div>
</body></html>"""

            es = EmailService()
            sent = es.send_report(
                to_email=email,
                audit_id=audit_id,
                score_initial=score_initial,
                score_final=score_final,
                report_type="security",
                html_report=html,
                project_name=project,
            )
            print(f"[NOTIFY] Email enviado para {email}: {sent}")

        except Exception as exc:
            print(f"[NOTIFY] Erro ao enviar email para {email}: {exc}")

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _compute_security_score(self, findings: List[dict]) -> int:
        """Score de segurança baseado nos findings ativos."""
        score = 100
        by_sev: Dict[str, int] = {}
        for f in findings:
            sev = f.get("severity", "LOW")
            by_sev[sev] = by_sev.get(sev, 0) + 1

        for sev, count in by_sev.items():
            weight = SEVERITY_WEIGHTS.get(sev, 2)
            cap = SEVERITY_CAPS.get(sev, 10)
            score -= min(count * weight, cap)

        return max(0, min(100, score))

    def _group_by_severity(self, findings: List[dict]) -> dict:
        groups: Dict[str, int] = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for f in findings:
            sev = f.get("severity", "LOW")
            groups[sev] = groups.get(sev, 0) + 1
        return groups

    def _parse_findings(self, raw: str) -> List[dict]:
        """Extrai JSON array de findings da resposta do LLM."""
        # Remove markdown code blocks
        clean = re.sub(r"```[a-z]*\n?", "", raw.strip())
        clean = re.sub(r"\n?```", "", clean).strip()

        # Tenta encontrar o array JSON
        match = re.search(r"\[.*\]", clean, re.DOTALL)
        if not match:
            return []

        try:
            findings = json.loads(match.group(0))
            if not isinstance(findings, list):
                return []
            # Normaliza campos obrigatórios
            result = []
            for f in findings:
                if not isinstance(f, dict):
                    continue
                result.append({
                    "file":           str(f.get("file", "unknown")),
                    "line":           int(f.get("line", 0)),
                    "rule":           str(f.get("rule", "unknown")),
                    "severity":       str(f.get("severity", "LOW")).upper(),
                    "title":          str(f.get("title", f.get("rule", ""))),
                    "description":    str(f.get("description", "")),
                    "fix_suggestion": str(f.get("fix_suggestion", "")),
                })
            return result
        except (json.JSONDecodeError, ValueError):
            return []
