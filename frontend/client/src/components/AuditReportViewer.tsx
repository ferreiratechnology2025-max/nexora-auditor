import { Download, Share2, X, AlertCircle, CheckCircle, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { QRCodeSVG } from "qrcode.react";
import { useState } from "react";
import ShareReportModal from "./ShareReportModal";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";

/**
 * AUDITX Audit Report Viewer
 * Design: Minimalismo Cirúrgico
 * - Score visual com círculo colorido
 * - Gráficos de vulnerabilidades (bar + pie)
 * - Lista de vulnerabilidades encontradas
 * - Recomendações de correção
 * - QR Code verificável
 * - Download de PDF
 */

interface AuditReport {
  id: string;
  projectName: string;
  date: string;
  score: number;
  vulnerabilities: {
    critical: number;
    medium: number;
    low: number;
  };
  languages: string[];
  recommendations: {
    title: string;
    severity: "critical" | "medium" | "low";
    description: string;
    file: string;
  }[];
}

interface AuditReportViewerProps {
  report: AuditReport;
  onClose: () => void;
}

const mockReport: AuditReport = {
  id: "audit-001",
  projectName: "e-commerce-api",
  date: "2026-03-11",
  score: 72,
  vulnerabilities: {
    critical: 2,
    medium: 4,
    low: 8,
  },
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
    {
      title: "Dependência Vulnerável",
      severity: "medium",
      description:
        "lodash@4.17.15 possui CVE-2021-23337. Atualize para versão 4.17.21 ou superior.",
      file: "package.json:45",
    },
  ],
};

export default function AuditReportViewer({
  report = mockReport,
  onClose,
}: AuditReportViewerProps) {
  const [showShareModal, setShowShareModal] = useState(false);
  const vulnerabilityData = [
    { name: "Críticas", value: report.vulnerabilities.critical, color: "#DC2626" },
    { name: "Médias", value: report.vulnerabilities.medium, color: "#F59E0B" },
    { name: "Baixas", value: report.vulnerabilities.low, color: "#10B981" },
  ];

  const barChartData = [
    {
      name: "Vulnerabilidades",
      Críticas: report.vulnerabilities.critical,
      Médias: report.vulnerabilities.medium,
      Baixas: report.vulnerabilities.low,
    },
  ];

  const qrCodeValue = `https://auditx.com/v/${report.id}`;

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "bg-critical/10 text-critical border-critical/20";
      case "medium":
        return "bg-warning/10 text-warning border-warning/20";
      case "low":
        return "bg-safe/10 text-safe border-safe/20";
      default:
        return "bg-muted/10 text-muted-foreground border-muted/20";
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "critical":
        return <AlertCircle className="w-5 h-5" />;
      case "medium":
        return <AlertTriangle className="w-5 h-5" />;
      case "low":
        return <CheckCircle className="w-5 h-5" />;
      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-background border border-border rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-card border-b border-border p-6 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-foreground">
              Laudo de Auditoria
            </h2>
            <p className="text-sm text-muted-foreground mt-1">
              {report.projectName} • {new Date(report.date).toLocaleDateString("pt-BR")}
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-8 space-y-8">
          {/* Score Section */}
          <div className="grid md:grid-cols-3 gap-8">
            {/* Score Circle */}
            <div className="flex flex-col items-center justify-center">
              <div className="relative w-48 h-48 mb-4">
                <svg className="w-full h-full" viewBox="0 0 200 200">
                  {/* Background circle */}
                  <circle
                    cx="100"
                    cy="100"
                    r="90"
                    fill="none"
                    stroke="#E5E7EB"
                    strokeWidth="8"
                  />
                  {/* Score circle */}
                  <circle
                    cx="100"
                    cy="100"
                    r="90"
                    fill="none"
                    stroke={
                      report.score >= 80
                        ? "#10B981"
                        : report.score >= 60
                        ? "#F59E0B"
                        : "#DC2626"
                    }
                    strokeWidth="8"
                    strokeDasharray={`${(report.score / 100) * 565} 565`}
                    strokeLinecap="round"
                    transform="rotate(-90 100 100)"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-5xl font-bold text-foreground">
                    {report.score}
                  </span>
                  <span className="text-xs text-muted-foreground">/100</span>
                </div>
              </div>
              <p className="text-center text-sm text-muted-foreground">
                {report.score >= 80
                  ? "Excelente"
                  : report.score >= 60
                  ? "Bom"
                  : "Precisa Melhorias"}
              </p>
            </div>

            {/* Vulnerability Summary */}
            <div className="space-y-4">
              <h3 className="font-semibold text-foreground mb-4">
                Resumo de Vulnerabilidades
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-critical/5 rounded-lg border border-critical/20">
                  <span className="text-sm font-medium text-foreground">
                    Críticas
                  </span>
                  <span className="text-lg font-bold text-critical">
                    {report.vulnerabilities.critical}
                  </span>
                </div>
                <div className="flex items-center justify-between p-3 bg-warning/5 rounded-lg border border-warning/20">
                  <span className="text-sm font-medium text-foreground">
                    Médias
                  </span>
                  <span className="text-lg font-bold text-warning">
                    {report.vulnerabilities.medium}
                  </span>
                </div>
                <div className="flex items-center justify-between p-3 bg-safe/5 rounded-lg border border-safe/20">
                  <span className="text-sm font-medium text-foreground">
                    Baixas
                  </span>
                  <span className="text-lg font-bold text-safe">
                    {report.vulnerabilities.low}
                  </span>
                </div>
              </div>
            </div>

            {/* QR Code */}
            <div className="flex flex-col items-center justify-center">
              <div className="bg-white p-4 rounded-lg border border-border mb-4">
                <QRCodeSVG
                  value={qrCodeValue}
                  size={150}
                  level="H"
                  includeMargin={true}
                />
              </div>
              <p className="text-xs text-muted-foreground text-center">
                QR Code Verificável
              </p>
              <p className="text-xs text-muted-foreground text-center mt-2 break-all">
                {qrCodeValue}
              </p>
            </div>
          </div>

          {/* Charts */}
          <div className="grid md:grid-cols-2 gap-8">
            {/* Bar Chart */}
            <div className="bg-card border border-border rounded-lg p-6">
              <h3 className="font-semibold text-foreground mb-4">
                Distribuição de Vulnerabilidades
              </h3>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={barChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="Críticas" fill="#DC2626" />
                  <Bar dataKey="Médias" fill="#F59E0B" />
                  <Bar dataKey="Baixas" fill="#10B981" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Pie Chart */}
            <div className="bg-card border border-border rounded-lg p-6">
              <h3 className="font-semibold text-foreground mb-4">
                Proporção de Severidade
              </h3>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={vulnerabilityData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {vulnerabilityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Recommendations */}
          <div>
            <h3 className="text-xl font-bold text-foreground mb-4">
              Recomendações de Correção
            </h3>
            <div className="space-y-4">
              {report.recommendations.map((rec, index) => (
                <div
                  key={index}
                  className={`border rounded-lg p-4 ${getSeverityColor(
                    rec.severity
                  )}`}
                >
                  <div className="flex items-start gap-3 mb-2">
                    {getSeverityIcon(rec.severity)}
                    <div className="flex-1">
                      <h4 className="font-semibold">{rec.title}</h4>
                      <p className="text-xs opacity-75 mt-1">{rec.file}</p>
                    </div>
                  </div>
                  <p className="text-sm mt-3">{rec.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Metadata */}
          <div className="bg-secondary/30 border border-border rounded-lg p-4">
            <div className="grid md:grid-cols-3 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Linguagens Detectadas</p>
                <p className="font-semibold text-foreground">
                  {report.languages.join(", ")}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">ID do Laudo</p>
                <p className="font-semibold text-foreground font-mono">
                  {report.id}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Data da Análise</p>
                <p className="font-semibold text-foreground">
                  {new Date(report.date).toLocaleDateString("pt-BR")}
                </p>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t border-border">
            <Button
              onClick={() => window.print()}
              className="flex-1 bg-primary hover:bg-primary/90 text-white"
            >
              <Download className="w-4 h-4 mr-2" />
              Baixar PDF
            </Button>
            <Button
              onClick={() => setShowShareModal(true)}
              variant="outline"
              className="flex-1 border-primary text-primary hover:bg-primary/10"
            >
              <Share2 className="w-4 h-4 mr-2" />
              Compartilhar
            </Button>
          </div>
        </div>
      </div>

      {/* Share Modal */}
      {showShareModal && (
        <ShareReportModal
          reportId={report.id}
          projectName={report.projectName}
          score={report.score}
          onClose={() => setShowShareModal(false)}
        />
      )}
    </div>
  );
}
