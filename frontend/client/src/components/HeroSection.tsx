import { Button } from "@/components/ui/button";
import { Upload, Github, AlertCircle, Trash2, CheckCircle2, Loader2, ShieldAlert, ShieldCheck } from "lucide-react";
import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { api } from "@/lib/api";

interface AuditPreview {
  audit_id: string;
  health_score_initial: number;
  total_findings: number;
  by_severity: { CRITICAL?: number; HIGH?: number; MEDIUM?: number; LOW?: number };
  files_scanned: number;
  languages_detected: string[];
}

interface HeroSectionProps {
  onAnalyzeStart: (type: "upload" | "github", value: string) => void;
  isAnalyzing?: boolean;
}

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function formatSize(bytes: number): string {
  if (bytes >= 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  return Math.round(bytes / 1024) + " KB";
}

export default function HeroSection({ onAnalyzeStart, isAnalyzing }: HeroSectionProps) {
  const [, setLocation] = useLocation();
  const [githubUrl, setGithubUrl] = useState("");
  const [email, setEmail] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [auditPreview, setAuditPreview] = useState<AuditPreview | null>(null);

  // Restaura resultado salvo ao voltar da página de pagamento
  useEffect(() => {
    const saved = sessionStorage.getItem("auditPreview");
    if (saved) {
      try { setAuditPreview(JSON.parse(saved)); } catch {}
    }
  }, []);

  const validateEmail = (val: string) => EMAIL_RE.test(val.trim());

  const handleFileSelect = (file: File) => {
    setError(null);
    if (!file.name.toLowerCase().endsWith(".zip")) {
      setError("Formato inválido. Apenas arquivos .ZIP contendo código-fonte são aceitos.");
      setSelectedFile(null);
      return;
    }
    if (file.size < 10 * 1024) {
      setError("Arquivo muito pequeno (mínimo 10KB). Certifique-se de que o ZIP contém o código-fonte completo.");
      setSelectedFile(null);
      return;
    }
    if (file.size > 50 * 1024 * 1024) {
      setError("O arquivo excede o limite de 50MB do plano gratuito. Faça upgrade para o Plano Pro.");
      setSelectedFile(null);
      return;
    }
    setSelectedFile(file);
  };

  const handleSubmitZip = async () => {
    if (!selectedFile) {
      setError("Selecione um arquivo .ZIP antes de continuar.");
      return;
    }
    if (!validateEmail(email)) {
      setError("Por favor, insira um e-mail válido (ex: nome@hotmail.com).");
      return;
    }
    setError(null);
    setAuditPreview(null);
    setIsSubmitting(true);
    try {
      const result = await api.audit.zip(selectedFile);
      if (result?.audit_id) {
        onAnalyzeStart("upload", result.audit_id);
        sessionStorage.setItem("auditPreview", JSON.stringify(result));
        setAuditPreview(result); // ← mostra preview, NÃO redireciona
      } else {
        setError("Erro ao processar auditoria. Tente novamente.");
      }
    } catch (err) {
      const msg = (err instanceof Error ? err.message : String(err)).toLowerCase();
      if (msg.includes("senha") || msg.includes("password") || msg.includes("encrypted")) {
        setError("ZIP protegido por senha. Envie um arquivo ZIP sem proteção.");
      } else if (msg.includes("size") || msg.includes("large") || msg.includes("50mb") || msg.includes("limite")) {
        setError("Arquivo muito grande. Limite: 50MB no plano gratuito.");
      } else if (msg.includes("inválido") || msg.includes("corrompido") || msg.includes("bad")) {
        setError("Arquivo ZIP inválido ou corrompido. Verifique o arquivo e tente novamente.");
      } else {
        setError("Erro ao processar arquivo. Verifique se é um ZIP válido sem senha.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleGithubAnalyze = async () => {
    if (!githubUrl.trim()) return;
    if (!validateEmail(email)) {
      setError("Por favor, insira um e-mail válido antes de continuar.");
      return;
    }
    setError(null);
    setIsSubmitting(true);
    try {
      const result = await api.audit.github(githubUrl.trim());
      if (result?.audit_id) {
        onAnalyzeStart("github", result.audit_id);
        setLocation(`/checkout?auditId=${result.audit_id}&plan=laudo&price=119`);
      } else {
        setError(result?.detail || "Erro ao processar repositório. Verifique a URL.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao clonar repositório.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") setDragActive(true);
    else if (e.type === "dragleave") setDragActive(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) handleFileSelect(e.dataTransfer.files[0]);
  };

  const busy = isAnalyzing || isSubmitting;

  return (
    <section
      className="relative py-20 md:py-32 overflow-hidden"
      style={{
        backgroundImage: `url('https://d2xsxph8kpxj0f.cloudfront.net/310519663164530750/hAiZVAW7TJTkrx5StRRrr5/auditx-hero-background-MY5Hxz9zFCFmGbF5hAokwS.webp')`,
        backgroundSize: "cover",
        backgroundPosition: "center",
      }}
    >
      <div className="absolute inset-0 bg-white/80"></div>

      <div className="container mx-auto px-4 relative z-10">
        {/* Live Audit Counter */}
        <div className="flex justify-center mb-8">
          <div className="bg-background/40 backdrop-blur-md border border-border px-4 py-1.5 rounded-full flex items-center gap-2 animate-pulse shadow-sm">
            <span className="w-1.5 h-1.5 rounded-full bg-safe"></span>
            <span className="text-[10px] font-bold text-foreground/70 uppercase tracking-widest">
              Auditoria em tempo real
            </span>
          </div>
        </div>

        {/* Headline */}
        <div className="text-center mb-12 max-w-4xl mx-auto animate-slideUp">
          <div className="inline-flex items-center gap-3 px-6 py-2.5 rounded-full bg-primary/10 border border-primary/20 mb-12 hover:scale-105 transition-transform cursor-default">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-primary"></span>
            </span>
            <span className="text-xs font-black uppercase tracking-[0.3em] text-primary">Plataforma DevSecOps Autônoma</span>
          </div>

          <h1 className="text-xl md:text-2xl lg:text-3xl font-bold text-foreground mb-6 leading-snug tracking-tight uppercase">
            Plataforma DevSecOps Autônoma com Auditoria de Código por IA
          </h1>


          <h2 className="text-base md:text-lg text-foreground font-black mb-8 max-w-4xl mx-auto uppercase tracking-tight">
            Não apenas escaneie. Conserte automaticamente.
          </h2>
          <p className="text-base md:text-xl text-muted-foreground max-w-3xl mx-auto font-medium leading-relaxed border-l-4 border-primary pl-6 py-2 text-left italic">
            A primeira auditoria completa e autônoma para softwares de alto valor. Proteja seu ativo mais precioso. O AuditX aplica análise estática avançada com IA, blindando sistemas críticos com correções automáticas definitivas e garantindo <strong>OWASP compliance</strong>.
          </p>
        </div>

        {/* Email */}
        <div className="max-w-xl mx-auto mb-8 animate-slideUp" style={{ animationDelay: "0.05s" }}>
          <div className="relative group">
            <input
              type="email"
              placeholder="Seu e-mail para receber o laudo (gmail, hotmail, etc.)"
              value={email}
              onChange={(e) => { setEmail(e.target.value); setError(null); }}
              className={`w-full px-6 py-4 rounded-xl border bg-background/50 backdrop-blur-md transition-all outline-none text-center text-lg font-medium shadow-sm ${
                error ? "border-critical ring-2 ring-critical/20" : "border-border focus:border-primary focus:ring-4 focus:ring-primary/10"
              }`}
            />
            {!email && (
              <span className="absolute right-4 top-1/2 -translate-y-1/2 text-[10px] font-black uppercase tracking-widest text-primary/40 group-hover:text-primary transition-colors">
                Obrigatório
              </span>
            )}
          </div>

          {error && (
            <div className="mt-4 p-4 bg-critical/10 border border-critical/20 rounded-lg flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-critical flex-shrink-0" />
              <p className="text-sm font-bold text-critical">{error}</p>
            </div>
          )}
        </div>

        {/* Upload Area */}
        <div className="max-w-2xl mx-auto animate-slideUp" style={{ animationDelay: "0.1s" }}>
          <div
            className={`border-2 border-dashed rounded-lg p-12 text-center transition-all cursor-pointer relative overflow-hidden ${
              dragActive ? "border-primary bg-primary/5" : "border-border bg-secondary/30 hover:border-primary/50"
            }`}
            onClick={() => {
              if (!busy) document.getElementById("file-upload")?.click();
            }}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            {busy && (
              <div className="absolute inset-0 bg-background/80 backdrop-blur-sm z-20 flex flex-col items-center justify-center p-6 text-center">
                <div className="w-full max-w-md">
                  <div className="flex justify-between text-xs font-bold text-primary mb-2 uppercase tracking-widest">
                    <span className="animate-pulse">Deep Scan Ativo</span>
                    <span>Aguarde...</span>
                  </div>
                  <div className="w-full h-1.5 bg-secondary rounded-full overflow-hidden">
                    <div className="h-full bg-primary animate-progress-fill"></div>
                  </div>
                  <p className="mt-4 text-xs text-muted-foreground font-mono">
                    Verificando assinaturas de vulnerabilidade...
                  </p>
                </div>
              </div>
            )}

            <Upload className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
            <p className="text-foreground font-semibold mb-2">
              Arraste seu código aqui (.ZIP)
            </p>
            <p className="text-sm text-muted-foreground mb-4 font-mono">
              Suporta: Node.js, Python, Go, PHP, Java
            </p>

            <input
              type="file"
              accept=".zip"
              className="hidden"
              id="file-upload"
              onClick={(e) => { (e.target as HTMLInputElement).value = ""; }}
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) handleFileSelect(file);
              }}
            />

            <div className="flex justify-center mt-4">
              <Button
                variant="outline"
                size="sm"
                disabled={busy}
                onClick={(e) => { e.stopPropagation(); document.getElementById("file-upload")?.click(); }}
                className="gap-2"
              >
                Selecionar ZIP
                <span className="text-[10px] uppercase font-black text-muted-foreground">Upload seguro</span>
              </Button>
            </div>

            {/* Feedback do arquivo selecionado */}
            {selectedFile && (
              <div className="mt-4 flex items-center justify-center gap-2 px-4 py-2 bg-safe/10 border border-safe/30 rounded-lg">
                <CheckCircle2 className="w-4 h-4 text-safe flex-shrink-0" />
                <span className="text-sm font-semibold text-safe">
                  {selectedFile.name} — {formatSize(selectedFile.size)} pronto para análise
                </span>
              </div>
            )}

            <div className="mt-3 flex items-center justify-center gap-2 text-xs text-muted-foreground font-semibold">
              <Trash2 className="w-4 h-4 text-primary" />
              Código deletado permanentemente 10 min após a análise
            </div>
            <p className="text-[10px] text-muted-foreground mt-4 uppercase tracking-[0.2em] font-black opacity-50">
              Criptografia AES-256 ativa
            </p>
          </div>

          {/* Botão Iniciar Auditoria */}
          {selectedFile && (
            <div className="mt-4">
              <Button
                className="w-full h-14 bg-primary hover:bg-primary/90 text-white font-black text-lg shadow-xl"
                disabled={busy}
                onClick={handleSubmitZip}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Analisando...
                  </>
                ) : (
                  "Iniciar Auditoria Agora"
                )}
              </Button>
            </div>
          )}

          {/* Preview do resultado da auditoria */}
          {auditPreview && (
            <div className="mt-6 p-6 bg-red-50 border-2 border-red-200 rounded-xl animate-slideUp">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <ShieldAlert className="w-6 h-6 text-red-600" />
                  <h3 className="font-black text-lg text-foreground uppercase tracking-tight">Diagnóstico Concluído</h3>
                </div>
                <span className={`text-2xl font-black ${
                  auditPreview.health_score_initial < 40 ? "text-red-600" :
                  auditPreview.health_score_initial < 70 ? "text-orange-500" : "text-yellow-500"
                }`}>
                  Score: {auditPreview.health_score_initial}/100
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-4">
                {[
                  { label: "CRÍTICOS", count: auditPreview.by_severity.CRITICAL ?? 0, color: "bg-red-100 text-red-600" },
                  { label: "ALTOS",    count: auditPreview.by_severity.HIGH ?? 0,     color: "bg-orange-100 text-orange-500" },
                  { label: "MÉDIOS",   count: auditPreview.by_severity.MEDIUM ?? 0,   color: "bg-yellow-100 text-yellow-600" },
                  { label: "BAIXOS",   count: auditPreview.by_severity.LOW ?? 0,      color: "bg-blue-100 text-blue-500" },
                ].map(({ label, count, color }) => (
                  <div key={label} className={`${color} rounded-lg p-3 text-center`}>
                    <div className="text-2xl font-black">{count}</div>
                    <div className="text-[10px] font-black uppercase tracking-widest opacity-80">{label}</div>
                  </div>
                ))}
              </div>

              <p className="text-sm text-gray-600 mb-4 font-medium">
                🔐 <strong>{auditPreview.total_findings} vulnerabilidades</strong> encontradas em {auditPreview.files_scanned} arquivos
                ({auditPreview.languages_detected.join(", ")}). Os detalhes estão classificados — escolha como agir:
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <button
                  onClick={() => setLocation(`/checkout?auditId=${auditPreview.audit_id}&plan=laudo&price=119`)}
                  className="bg-primary hover:bg-primary/90 text-white rounded-xl p-4 font-bold text-sm text-left transition-all shadow-md hover:shadow-lg"
                >
                  <ShieldCheck className="w-5 h-5 mb-1" />
                  Ver Laudo Completo
                  <div className="text-primary-foreground/70 font-normal text-xs mt-1">Relatório técnico + certificado — R$ 119,00</div>
                </button>
                <button
                  onClick={() => setLocation(`/checkout?auditId=${auditPreview.audit_id}&plan=correcao&price=299`)}
                  className="bg-green-600 hover:bg-green-700 text-white rounded-xl p-4 font-bold text-sm text-left transition-all shadow-md hover:shadow-lg"
                >
                  <ShieldAlert className="w-5 h-5 mb-1" />
                  Laudo + Correção Automática
                  <div className="text-green-100 font-normal text-xs mt-1">Auto-Fix aplicado + projeto corrigido — R$ 299,00</div>
                </button>
              </div>
            </div>
          )}

          {/* Divider */}
          <div className="flex items-center gap-4 my-8">
            <div className="flex-1 h-px bg-border"></div>
            <span className="text-xs font-bold text-muted-foreground uppercase tracking-widest">ou use link público</span>
            <div className="flex-1 h-px bg-border"></div>
          </div>

          {/* GitHub URL Input */}
          <div className="flex flex-col sm:flex-row gap-2">
            <div className="flex-1 relative">
              <Github className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                type="text"
                placeholder="URL do Repositório (Ex: github.com/user/repo)"
                value={githubUrl}
                onChange={(e) => setGithubUrl(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-border rounded-xl bg-background text-foreground placeholder-muted-foreground outline-none focus:ring-2 focus:ring-primary/50 transition-all font-mono text-sm"
              />
            </div>
            <Button
              onClick={handleGithubAnalyze}
              disabled={!githubUrl.trim() || busy}
              className="bg-primary hover:bg-primary/90 rounded-xl px-8 h-12 font-bold"
            >
              {isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : "Autopsia GitHub"}
            </Button>
          </div>

          {/* Footer badges */}
          <div className="mt-12 text-center">
            <p className="text-[10px] font-bold text-muted-foreground flex items-center justify-center gap-2 uppercase tracking-widest mb-12">
              <span className="w-2 h-2 rounded-full bg-safe animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.5)]"></span>
              Infraestrutura Cloud monitorada em tempo real
            </p>

            <div className="pt-8 border-t border-border/50">
              <p className="text-[10px] font-black uppercase tracking-[0.3em] text-muted-foreground mb-6">🔒 Preparado para Compliance Global</p>
              <div className="flex flex-wrap justify-center gap-6 md:gap-12 opacity-50 grayscale hover:grayscale-0 transition-all duration-500">
                {[
                  { name: "OWASP Top 10", desc: "Security Standard" },
                  { name: "ISO 27001", desc: "Information Security" },
                  { name: "LGPD/GDPR", desc: "Data Privacy" },
                  { name: "PCI-DSS", desc: "Payment Security" },
                ].map((badge) => (
                  <div key={badge.name} className="flex flex-col items-center">
                    <span className="text-xs font-black text-foreground">{badge.name}</span>
                    <span className="text-[8px] font-bold uppercase tracking-tighter">{badge.desc}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
