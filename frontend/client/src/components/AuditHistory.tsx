import { Download, Eye, QrCode, Copy, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import AuditReportViewer from "./AuditReportViewer";

/**
 * AUDITX Audit History
 * Design: Minimalismo Cirúrgico
 * - Tabela de auditorias realizadas
 * - Status com cores de severidade
 * - Downloads de laudos PDF
 * - QR Code verificável
 * - Compartilhamento de link público
 */

interface Audit {
  id: string;
  projectName: string;
  date: string;
  score: number;
  status: "completed" | "processing" | "failed";
  vulnerabilities: {
    critical: number;
    medium: number;
    low: number;
  };
  size: string;
  plan: string;
}

const mockAudits: Audit[] = [
  {
    id: "audit-001",
    projectName: "e-commerce-api",
    date: "2026-03-11",
    score: 72,
    status: "completed",
    vulnerabilities: { critical: 2, medium: 4, low: 8 },
    size: "125MB",
    plan: "Pro",
  },
  {
    id: "audit-002",
    projectName: "mobile-app",
    date: "2026-03-10",
    score: 58,
    status: "completed",
    vulnerabilities: { critical: 5, medium: 6, low: 12 },
    size: "85MB",
    plan: "Pro",
  },
  {
    id: "audit-003",
    projectName: "dashboard-frontend",
    date: "2026-03-09",
    score: 89,
    status: "completed",
    vulnerabilities: { critical: 0, medium: 2, low: 5 },
    size: "45MB",
    plan: "Dev",
  },
  {
    id: "audit-004",
    projectName: "legacy-system",
    date: "2026-03-08",
    score: 42,
    status: "completed",
    vulnerabilities: { critical: 8, medium: 10, low: 15 },
    size: "320MB",
    plan: "Scale",
  },
];

export default function AuditHistory() {
  const [copied, setCopied] = useState<string | null>(null);
  const [selectedAuditId, setSelectedAuditId] = useState<string | null>(null);

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-safe";
    if (score >= 60) return "text-warning";
    return "text-critical";
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "completed":
        return "Concluído";
      case "processing":
        return "Processando";
      case "failed":
        return "Falhou";
      default:
        return status;
    }
  };

  const handleCopyLink = (auditId: string) => {
    const link = `https://auditx.com/v/${auditId}`;
    navigator.clipboard.writeText(link);
    setCopied(auditId);
    setTimeout(() => setCopied(null), 2000);
  };

  const selectedAudit = mockAudits.find((a) => a.id === selectedAuditId);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-foreground mb-2">
          Minhas Auditorias
        </h2>
        <p className="text-muted-foreground">
          Histórico de todas as auditorias realizadas. Total: {mockAudits.length}
        </p>
      </div>

      {/* Table */}
      <div className="bg-card border border-border rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border bg-secondary/30">
                <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">
                  Projeto
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">
                  Data
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">
                  Score
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">
                  Vulnerabilidades
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">
                  Tamanho
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody>
              {mockAudits.map((audit) => (
                <tr
                  key={audit.id}
                  className="border-b border-border hover:bg-secondary/20 transition-colors"
                >
                  <td className="px-6 py-4">
                    <div>
                      <p className="font-semibold text-foreground">
                        {audit.projectName}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        ID: {audit.id}
                      </p>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-foreground">
                    {new Date(audit.date).toLocaleDateString("pt-BR")}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-lg font-bold ${getScoreColor(
                          audit.score
                        )}`}
                      >
                        {audit.score}
                      </span>
                      <span className="text-xs text-muted-foreground">/100</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <div className="flex gap-2">
                      {audit.vulnerabilities.critical > 0 && (
                        <span className="px-2 py-1 rounded bg-critical/10 text-critical text-xs font-semibold">
                          {audit.vulnerabilities.critical} críticas
                        </span>
                      )}
                      {audit.vulnerabilities.medium > 0 && (
                        <span className="px-2 py-1 rounded bg-warning/10 text-warning text-xs font-semibold">
                          {audit.vulnerabilities.medium} médias
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-foreground">
                    {audit.size}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      {/* View */}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setSelectedAuditId(audit.id)}
                        className="text-muted-foreground hover:text-foreground"
                        title="Visualizar Laudo"
                      >
                        <Eye className="w-4 h-4" />
                      </Button>

                      {/* Download */}
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-muted-foreground hover:text-foreground"
                        title="Baixar PDF"
                      >
                        <Download className="w-4 h-4" />
                      </Button>

                      {/* QR Code */}
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-muted-foreground hover:text-foreground"
                        title="QR Code"
                      >
                        <QrCode className="w-4 h-4" />
                      </Button>

                      {/* Share */}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleCopyLink(audit.id)}
                        className="text-muted-foreground hover:text-foreground"
                        title="Copiar Link"
                      >
                        {copied === audit.id ? (
                          <CheckCircle className="w-4 h-4 text-safe" />
                        ) : (
                          <Copy className="w-4 h-4" />
                        )}
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Mostrando 1-{mockAudits.length} de {mockAudits.length} auditorias
        </p>
        <div className="flex gap-2">
          <Button variant="outline" disabled>
            Anterior
          </Button>
          <Button variant="outline">Próximo</Button>
        </div>
      </div>

      {/* Info Box */}
      <div className="bg-primary/5 border border-primary/20 rounded-lg p-4">
        <p className="text-sm text-foreground">
          <strong>Dica:</strong> Cada laudo possui um link público único com QR
          Code verificável. Compartilhe com seus clientes para comprovar a
          qualidade do seu código.
        </p>
      </div>

      {/* Report Viewer Modal */}
      {selectedAuditId && selectedAudit && (
        <AuditReportViewer
          report={{
            id: selectedAuditId,
            projectName: selectedAudit.projectName,
            date: selectedAudit.date,
            score: selectedAudit.score,
            vulnerabilities: selectedAudit.vulnerabilities,
            languages: ["JavaScript", "TypeScript", "Python"],
            recommendations: [
              {
                title: "SQL Injection em db_config.php",
                severity: "critical",
                description:
                  "Query não parametrizada detectada. Use prepared statements para evitar injeção SQL.",
                file: "src/database/db_config.php:45",
              },
              {
                title: "XSS em user_input.js",
                severity: "medium",
                description:
                  "Input do usuário não sanitizado. Implemente validação e escape de caracteres especiais.",
                file: "src/utils/user_input.js:12",
              },
              {
                title: "Secrets Expostos",
                severity: "critical",
                description:
                  "API keys encontradas em .env.example. Remova dados sensíveis de arquivos versionados.",
                file: ".env.example:3",
              },
            ],
          }}
          onClose={() => setSelectedAuditId(null)}
        />
      )}
    </div>
  );
}
