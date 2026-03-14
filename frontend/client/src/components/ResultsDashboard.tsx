import { Button } from "@/components/ui/button";
import {
  AlertCircle,
  CheckCircle,
  AlertTriangle,
  Download,
  ArrowLeft,
  Lock,
  FileText,
  CheckCircle2,
  StickyNote,
  Plus,
  Trash2,
  Send,
  ShieldCheck,
  Award,
  Share2,
  Copy,
  ArrowRight,
  Play,
  Terminal,
  Activity,
  ShieldAlert,
  Bot,
  MessageSquareText,
  Sparkles,
  User,
  Loader2
} from "lucide-react";
import { useLocation } from "wouter";
import { useState, useEffect } from "react";

/**
 * AUDITX Results Dashboard
 * Design: Minimalismo Cirúrgico
 * - Score visual com círculo colorido
 * - Lista de vulnerabilidades com badges de severidade
 * - Código borrado com overlay "Bloqueado"
 * - CTAs para compra e assinatura
 */
interface ResultsDashboardProps {
  onBack: () => void;
  isUnlocked?: boolean;
}

export default function ResultsDashboard({ onBack, isUnlocked = false }: ResultsDashboardProps) {
  const [, setLocation] = useLocation();
  const [notes, setNotes] = useState<string[]>(() => {
    const saved = localStorage.getItem(`audit_notes_${"AUD-8829"}`);
    return saved ? JSON.parse(saved) : [];
  });
  const [newNote, setNewNote] = useState("");
  const [includeNotesInPdf, setIncludeNotesInPdf] = useState(true);
  const [isSimulating, setIsSimulating] = useState(false);
  const [simLogs, setSimLogs] = useState<string[]>([]);
  const [simStep, setSimStep] = useState(0);

  // Security Copilot States
  const [isCopilotOpen, setIsCopilotOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState<{ role: 'user' | 'bot', content: string }[]>([
    { role: 'bot', content: "Olá! Sou seu Security Copilot. Encontrei 14 vulnerabilidades no seu código. Como posso ajudar com a blindagem hoje?" }
  ]);
  const [chatInput, setChatInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  const simulateCopilotResponse = (query: string) => {
    setIsTyping(true);

    setTimeout(() => {
      let response = "Desculpe, ainda estou processando sua requisição técnica. Deseja que eu analise um arquivo específico?";

      if (query.toLowerCase().includes("vulnerabilidades")) {
        response = "Seu projeto possui 3 vulnerabilidades CRÍTICAS. A mais perigosa é um SQL Injection no arquivo 'db_config.php'. Recomendo focar nela primeiro.";
      } else if (query.toLowerCase().includes("explique")) {
        response = "O SQL Injection ocorre porque a variável 'id' está sendo concatenada diretamente na query. Um invasor pode usar isso para deletar todo o banco de dados.";
      } else if (query.toLowerCase().includes("corrija")) {
        response = "Claro! Para corrigir, estou aplicando 'Prepared Statements'. Substituímos a concatenação direta por placeholders (?) que neutralizam o ataque.";
      }

      setChatMessages(prev => [...prev, { role: 'bot', content: response }]);
      setIsTyping(false);
    }, 1500);
  };

  const handleSendMessage = () => {
    if (!chatInput.trim()) return;
    const userMsg = chatInput.trim();
    setChatMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setChatInput("");
    simulateCopilotResponse(userMsg);
  };

  const startSimulation = () => {
    setIsSimulating(true);
    setSimLogs([]);
    setSimStep(0);

    const logs = [
      "> Inicializando ambiente sandbox (Docker Container #8829)...",
      "> Montando volume de código em modo 'readonly'...",
      "> Identificando endpoint vulnerável: db_config.php",
      "> Preparando payload inofensivo: ' OR 1=1; --",
      "> Executando vetor de ataque: SQL Injection (Auth Bypass)",
      "> [!] EXPLORAÇÃO BEM-SUCEDIDA: Acesso administrativo obtido em sandbox.",
      "> Analisando logs de erro do contêiner...",
      "> CONCLUSÃO: Vulnerabilidade confirmada. Falso positivo descartado.",
      "> [OK] Ambiente sandbox destruído com segurança."
    ];

    let current = 0;
    const interval = setInterval(() => {
      if (current >= logs.length) {
        clearInterval(interval);
        setIsSimulating(false);
        return;
      }
      const nextLog = logs[current];
      if (nextLog) {
        setSimLogs(prev => [...prev, nextLog]);
      }
      current++;
      setSimStep(current);
    }, 800);
  };

  // Persistir notas
  useEffect(() => {
    localStorage.setItem(`audit_notes_${"AUD-8829"}`, JSON.stringify(notes));
  }, [notes]);

  const addNote = () => {
    if (newNote.trim()) {
      setNotes([...notes, newNote.trim()]);
      setNewNote("");
    }
  };

  const removeNote = (index: number) => {
    setNotes(notes.filter((_, i) => i !== index));
  };

  // Dados simulados de análise
  const analysisData = {
    score: 42,
    totalVulnerabilities: 14,
    critical: 3,
    medium: 5,
    low: 6,
    projectName: "meu-projeto-12mb",
    id: "AUD-8829",
    price: 119,
    sha256: "f7c3bc1d808e04732adf679965ccc34ca7ae3441f4ed1e8f5d8f9e8b5a6c2c7f"
  };

  const handleCheckout = () => {
    setLocation(`/checkout?auditId=${analysisData.id}&price=${analysisData.price}`);
  };

  const vulnerabilities = analysisData.score === 100 ? [] : [
    { name: "SQL Injection", severity: "critical", file: "db_config.php" },
    { name: "XSS", severity: "medium", file: "auth.js" },
    { name: "Secrets Expostos", severity: "medium", file: ".env.example" },
  ];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "bg-critical text-white";
      case "medium":
        return "bg-warning text-white";
      case "low":
        return "bg-safe text-white";
      default:
        return "bg-muted text-foreground";
    }
  };

  const getSeverityLabel = (severity: string) => {
    switch (severity) {
      case "critical":
        return "Alta";
      case "medium":
        return "Média";
      case "low":
        return "Baixa";
      default:
        return severity;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header com botão voltar */}
      <div className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4 flex items-center gap-4">
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            Voltar
          </button>
          <div>
            <h1 className="text-lg font-semibold text-foreground">
              Autopsia Concluída
            </h1>
            <p className="text-sm text-muted-foreground">
              {analysisData.totalVulnerabilities} vulnerabilidades encontradas
            </p>
          </div>
        </div>
      </div>

      {/* Conteúdo Principal */}
      <div className="container mx-auto px-4 py-12">
        <div className="grid md:grid-cols-3 gap-8">
          {/* Coluna Esquerda: Score */}
          <div className="md:col-span-1">
            <div className="bg-card border border-border rounded-lg p-8 text-center sticky top-24">
              {/* Score Circle */}
              <div className="relative w-40 h-40 mx-auto mb-6">
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
                  {/* Score circle - red for low score */}
                  <circle
                    cx="100"
                    cy="100"
                    r="90"
                    fill="none"
                    stroke={analysisData.score > 70 ? "#10B981" : analysisData.score > 40 ? "#F59E0B" : "#DC2626"}
                    strokeWidth="8"
                    strokeDasharray={`${(analysisData.score / 100) * 565} 565`}
                    strokeLinecap="round"
                    transform="rotate(-90 100 100)"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className={`text-4xl font-bold ${analysisData.score > 70 ? "text-safe" : analysisData.score > 40 ? "text-warning" : "text-critical"}`}>
                    {analysisData.score}
                  </span>
                  <span className="text-xs text-muted-foreground">/100</span>
                </div>
              </div>

              {/* Resumo */}
              <div className="space-y-2 text-left">
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-critical" />
                  <span className="text-sm text-foreground">
                    {analysisData.critical} Críticas
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-warning" />
                  <span className="text-sm text-foreground">
                    {analysisData.medium} Médias
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-safe" />
                  <span className="text-sm text-foreground">
                    {analysisData.low} Baixas
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Coluna Direita: Vulnerabilidades e CTA */}
          <div className="md:col-span-2 space-y-6">
            {/* Lista de Vulnerabilidades */}
            <div className="bg-card border border-border rounded-lg p-6 space-y-4">
              <h3 className="text-lg font-semibold text-foreground">
                Vulnerabilidades Detectadas
              </h3>

              {vulnerabilities.length === 0 ? (
                <div className="text-center border border-border/60 rounded-xl p-8 bg-secondary/30">
                  <ShieldCheck className="w-10 h-10 text-safe mx-auto mb-3" />
                  <p className="text-lg font-bold text-foreground mb-1">Parabéns! Nenhuma vulnerabilidade encontrada.</p>
                  <p className="text-sm text-muted-foreground">Score perfeito (100). Certificado e hash gerados para seu compliance.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {vulnerabilities.map((vuln, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-secondary/30 rounded">
                      <div>
                        <p className="text-sm font-medium text-foreground">
                          {vuln.name}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {vuln.file}
                        </p>
                      </div>
                      <span
                        className={`px-3 py-1 rounded text-xs font-semibold ${getSeverityColor(
                          vuln.severity
                        )}`}
                      >
                        {getSeverityLabel(vuln.severity)}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Modo Diff Pro: Antes vs Depois */}
            <div className="bg-card border border-border rounded-lg overflow-hidden">
              <div className="flex items-center justify-between px-6 py-4 border-b border-border bg-muted/20">
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-primary" />
                  <span className="text-sm font-mono font-bold uppercase tracking-widest">Diff View: Heuristic Correction</span>
                </div>
                {!isUnlocked && (
                  <span className="text-[10px] bg-primary/10 text-primary px-2 py-1 rounded-full font-bold animate-pulse">
                    MODO PROTEGIDO
                  </span>
                )}
              </div>

              <div className="grid md:grid-cols-2 divide-x divide-border">
                {/* Lado Esquerdo: ANTES (Vulnerável) */}
                <div className="p-6 space-y-3 relative">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold text-critical uppercase tracking-tighter">Vulnerável (Original)</span>
                    <span className="text-[10px] font-mono text-muted-foreground">db_handler.js:42</span>
                  </div>
                  <div className={`transition-all duration-1000 ${!isUnlocked ? 'blur-md select-none pointer-events-none' : ''}`}>
                    <pre className="text-[11px] font-mono leading-relaxed text-muted-foreground">
                      {`function getUser(id) {
  // SQL INJECTION RISK
  const sql = "SELECT * FROM users 
               WHERE id = " + id;
  return db.query(sql);
}`}
                    </pre>
                  </div>
                  {!isUnlocked && (
                    <div className="absolute inset-0 flex items-center justify-center p-6 text-center">
                      <p className="text-[10px] text-foreground font-medium bg-background/80 px-3 py-2 rounded border border-border">
                        O conteúdo original está oculto para sua proteção.
                      </p>
                    </div>
                  )}
                </div>

                {/* Lado Direito: DEPOIS (Corrigido) */}
                <div className="p-6 space-y-3 relative bg-safe/5">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold text-safe uppercase tracking-tighter">Auto-Fix (Sanitizado)</span>
                    <CheckCircle2 className="w-3 h-3 text-safe" />
                  </div>
                  <pre className={`text-[11px] font-mono leading-relaxed transition-all duration-700 ${!isUnlocked ? 'blur-[3px] opacity-40 select-none' : 'text-foreground'}`}>
                    {`function getUser(id) {
  // SECURE QUERY
  const sql = "SELECT * FROM users 
               WHERE id = ?";
  return db.execute(sql, [id]);
}`}
                  </pre>
                  {!isUnlocked && (
                    <div className="absolute inset-0 flex items-center justify-center">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-[10px] font-bold text-primary hover:bg-primary/10"
                        onClick={handleCheckout}
                      >
                        <Lock className="w-3 h-3 mr-2" />
                        Ver Correção Completa
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Certificado de Segurança Compartilhável */}
            <div className={`bg-gradient-to-br from-card to-background border-2 ${isUnlocked ? 'border-safe/30' : 'border-border'} rounded-xl p-8 relative overflow-hidden transition-all duration-1000`}>
              {/* Watermark Logo */}
              <ShieldCheck className="absolute -bottom-10 -right-10 w-48 h-48 text-primary/5 rotate-12" />

              <div className="relative z-10 flex flex-col md:flex-row items-center gap-8 text-center md:text-left">
                <div className={`p-4 rounded-2xl bg-background border shadow-2xl transition-transform duration-700 ${isUnlocked ? 'scale-110 rotate-0' : 'rotate-3'}`}>
                  <div className="border-4 border-double border-primary/20 p-2 rounded-xl">
                    <Award className={`w-16 h-16 ${isUnlocked ? 'text-safe animate-pulse' : 'text-muted-foreground'}`} />
                  </div>
                </div>

                <div className="flex-1 space-y-2">
                  <h3 className="text-xl font-bold font-mono tracking-tight">Certificado de Conformidade AuditX</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    Este projeto foi auditado heuristicamente contra os vetores de ataque mais comuns (OWASP Top 10).
                    {isUnlocked ? ' A validação final está disponível para compartilhamento público.' : ' Desbloqueie o acesso para validar este certificado.'}
                  </p>

                  <div className="pt-4 flex flex-wrap gap-3 justify-center md:justify-start">
                    <Button
                      disabled={!isUnlocked}
                      variant={isUnlocked ? "default" : "outline"}
                      className={`h-10 px-6 font-bold ${isUnlocked ? 'bg-safe hover:bg-safe/90 text-white' : ''}`}
                    >
                      <Share2 className="w-4 h-4 mr-2" />
                      Compartilhar Selo
                    </Button>
                    <Button
                      disabled={!isUnlocked}
                      variant="outline"
                      className="h-10 px-6 font-bold border-primary text-primary hover:bg-primary/5"
                    >
                      <Copy className="w-4 h-4 mr-2" />
                      Copiar Badge MD
                    </Button>
                  </div>
                </div>
              </div>

              {isUnlocked && (
                <div className="absolute top-4 right-4 animate-bounce">
                  <div className="bg-safe text-white text-[8px] font-black px-2 py-1 rounded shadow-lg uppercase">
                    Verificado ✓
                  </div>
                </div>
              )}
            </div>

            {/* CTAs Dinâmicos */}
            <div className="space-y-3 bg-card border border-border rounded-lg p-6">
              {isUnlocked ? (
                <div className="space-y-6">
                  <div className="flex items-center gap-3 p-4 bg-safe/10 border border-safe/20 rounded-lg">
                    <CheckCircle2 className="w-6 h-6 text-safe" />
                    <div>
                      <p className="font-bold text-safe">Acesso Total Liberado</p>
                      <p className="text-xs text-muted-foreground">Você já pode baixar os arquivos e aplicar as correções.</p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 bg-secondary/20 p-3 rounded-lg border border-border/50">
                    <input
                      type="checkbox"
                      id="include-notes"
                      checked={includeNotesInPdf}
                      onChange={(e) => setIncludeNotesInPdf(e.target.checked)}
                      className="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary"
                    />
                    <label htmlFor="include-notes" className="text-xs text-muted-foreground cursor-pointer select-none">
                      Incluir notas privadas no relatório PDF e JSON
                    </label>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <Button
                      className="h-12 bg-primary hover:bg-primary/90 text-white font-bold"
                      onClick={() => {
                        const msg = includeNotesInPdf && notes.length > 0
                          ? "Gerando PDF com notas privadas inclusas..."
                          : "Gerando PDF do relatório...";
                        alert(msg); // Em um app real, usaria sonner
                      }}
                    >
                      <Download className="w-4 h-4 mr-2" />
                      Baixar Relatório PDF
                    </Button>
                    <Button
                      variant="outline"
                      className="h-12 border-primary text-primary hover:bg-primary/5 font-bold"
                      onClick={() => alert("Dados exportados para a área de transferência.")}
                    >
                      <FileText className="w-4 h-4 mr-2" />
                      Exportar JSON (CI/CD)
                    </Button>
                  </div>

                  <Button className="w-full h-14 bg-safe hover:bg-safe/90 text-white font-black text-lg">
                    Aplicar Auto-Fix no GitHub
                  </Button>
                </div>
              ) : (
                <>
                  <h3 className="text-lg font-semibold text-foreground mb-4 font-mono">
                    AUTÓPSIA COMPLETA DISPONÍVEL
                  </h3>

                  {/* Opção A: Compra Única */}
                  <div className="border border-primary/20 rounded-lg p-4 bg-primary/5">
                    <p className="text-sm text-foreground mb-4">
                      <strong>Desbloquear este projeto</strong>
                      <br />
                      Auto-Fix + Laudo PDF certificado + Exportação JSON
                    </p>
                    <Button
                      className="w-full h-12 bg-primary hover:bg-primary/90 text-white font-bold shadow-lg"
                      onClick={handleCheckout}
                    >
                      <Lock className="w-4 h-4 mr-2" />
                    Liberar Acesso — R$ {analysisData.price}
                  </Button>
                  <p className="text-[10px] text-muted-foreground mt-3 uppercase tracking-tighter">
                    Projeto: {analysisData.projectName} • Tamanho: 12MB
                  </p>
                  <div className="text-left text-[11px] font-mono bg-secondary/40 border border-border rounded-lg p-3 mt-3 break-all">
                    <p className="text-muted-foreground uppercase font-bold text-[10px]">SHA-256 do arquivo enviado</p>
                    <p className="text-foreground">{analysisData.sha256}</p>
                  </div>
                </div>

                  {/* Opção B: Assinatura */}
                  <div className="border border-border rounded-lg p-4">
                    <p className="text-sm text-foreground mb-3">
                      <strong>Assine o Plano Dev</strong>
                      <br />
                      R$ 99/mês — Inclui este e mais 4 laudos mensais
                    </p>
                    <Button variant="outline" className="w-full h-11 border-primary text-primary hover:bg-primary/5">
                      Ver Todos os Planos
                    </Button>
                  </div>
                </>
              )}
            </div>

            {/* Seção de Notas Privadas (Nova) */}
            <div className="bg-card border border-border rounded-lg p-6 space-y-4">
              <div className="flex items-center justify-between border-b border-border pb-4">
                <div className="flex items-center gap-2">
                  <StickyNote className="w-5 h-5 text-primary" />
                  <h3 className="text-lg font-semibold text-foreground">Notas Privadas</h3>
                </div>
                <span className="text-[10px] uppercase tracking-widest text-muted-foreground font-bold">Apenas você vê isso</span>
              </div>

              {/* Lista de Notas */}
              <div className="space-y-3 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
                {notes.length === 0 ? (
                  <div className="text-center py-8 border-2 border-dashed border-border rounded-lg">
                    <p className="text-sm text-muted-foreground italic">Nenhuma observação técnica adicionada.</p>
                  </div>
                ) : (
                  notes.map((note, index) => (
                    <div key={index} className="group p-3 bg-secondary/20 border border-border/50 rounded-lg relative hover:border-primary/30 transition-all">
                      <p className="text-sm text-foreground leading-relaxed pr-8">{note}</p>
                      <button
                        onClick={() => removeNote(index)}
                        className="absolute top-2 right-2 p-1 text-muted-foreground hover:text-critical opacity-0 group-hover:opacity-100 transition-all"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))
                )}
              </div>

              {/* Input de Nova Nota */}
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addNote()}
                  placeholder="Adicionar observação técnica..."
                  className="flex-1 bg-background border border-border rounded-lg px-4 py-2 text-sm focus:ring-2 ring-primary/20 outline-none transition-all"
                />
                <Button
                  size="sm"
                  className="bg-primary hover:bg-primary/90 text-white px-3"
                  onClick={addNote}
                >
                  <Plus className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>

          {/* Security Copilot - Floating Interface */}
          <div className={`fixed bottom-6 right-6 z-50 transition-all duration-300 ${isCopilotOpen ? 'w-80 sm:w-96' : 'w-16 h-16'}`}>
            {!isCopilotOpen ? (
              <Button
                onClick={() => setIsCopilotOpen(true)}
                className="w-16 h-16 rounded-full bg-primary shadow-2xl hover:scale-110 transition-transform flex items-center justify-center p-0"
              >
                <Bot className="w-8 h-8 text-white" />
                <span className="absolute -top-1 -right-1 flex h-4 w-4">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-safe opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-4 w-4 bg-safe border-2 border-white"></span>
                </span>
              </Button>
            ) : (
              <div className="bg-card border border-border rounded-2xl shadow-2xl flex flex-col h-[500px] overflow-hidden animate-in fade-in zoom-in duration-200">
                {/* Copilot Header */}
                <div className="p-4 bg-primary text-white flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-white/10 rounded-lg">
                      <Bot className="w-5 h-5" />
                    </div>
                    <div>
                      <p className="font-bold text-sm">Security Copilot</p>
                      <div className="flex items-center gap-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-safe"></span>
                        <span className="text-[10px] opacity-70 uppercase font-bold tracking-widest">IA Consultiva Ativa</span>
                      </div>
                    </div>
                  </div>
                  <button onClick={() => setIsCopilotOpen(false)} className="hover:bg-white/10 p-1 rounded transition-colors">
                    <ArrowLeft className="w-4 h-4 rotate-180" />
                  </button>
                </div>

                {/* Chat Body */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar bg-secondary/5">
                  {chatMessages.map((msg, i) => (
                    <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-[85%] p-3 rounded-2xl text-xs leading-relaxed shadow-sm ${msg.role === 'user'
                        ? 'bg-primary text-white rounded-br-none'
                        : 'bg-background border border-border text-foreground rounded-bl-none'
                        }`}>
                        {msg.content}
                      </div>
                    </div>
                  ))}
                  {isTyping && (
                    <div className="flex justify-start">
                      <div className="bg-background border border-border p-3 rounded-2xl rounded-bl-none shadow-sm flex gap-1">
                        <span className="w-1.5 h-1.5 bg-muted-foreground rounded-full animate-bounce"></span>
                        <span className="w-1.5 h-1.5 bg-muted-foreground rounded-full animate-bounce delay-150"></span>
                        <span className="w-1.5 h-1.5 bg-muted-foreground rounded-full animate-bounce delay-300"></span>
                      </div>
                    </div>
                  )}
                </div>

                {/* Copilot Suggested Questions */}
                <div className="p-2 bg-muted/20 border-t border-border flex gap-2 overflow-x-auto no-scrollbar">
                  {[
                    "Meu projeto tem riscos críticos?",
                    "Explique o erro no arquivo db_config",
                    "Como corrigir SQL Injection?"
                  ].map((q, i) => (
                    <button
                      key={i}
                      onClick={() => {
                        setChatInput(q);
                        setTimeout(() => handleSendMessage(), 100);
                      }}
                      className="whitespace-nowrap bg-background border border-border px-3 py-1.5 rounded-full text-[10px] font-bold text-muted-foreground hover:border-primary hover:text-primary transition-all shadow-sm"
                    >
                      <Sparkles className="w-3 h-3 inline mr-1" />
                      {q}
                    </button>
                  ))}
                </div>

                {/* Chat Input */}
                <div className="p-4 border-t border-border bg-card">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                      placeholder="Pergunte sobre sua auditoria..."
                      className="flex-1 bg-background border border-border rounded-xl px-4 py-2 text-xs outline-none focus:ring-2 ring-primary/20 transition-all"
                    />
                    <Button
                      size="sm"
                      onClick={handleSendMessage}
                      className="bg-primary hover:bg-primary/90 text-white rounded-xl"
                    >
                      <Send className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
