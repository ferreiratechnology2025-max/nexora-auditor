import { useState } from "react";
import { X, Mail, Copy, CheckCircle, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

/**
 * AUDITX Share Report Modal
 * Design: Minimalismo Cirúrgico
 * - Modal para compartilhamento por e-mail
 * - Validação de e-mail
 * - Personalização de mensagem
 * - Opções de destinatários múltiplos
 */

interface ShareReportModalProps {
  reportId: string;
  projectName: string;
  score: number;
  onClose: () => void;
}

export default function ShareReportModal({
  reportId,
  projectName,
  score,
  onClose,
}: ShareReportModalProps) {
  const [emails, setEmails] = useState<string>("");
  const [message, setMessage] = useState<string>(
    `Olá,\n\nCompartilho o laudo de auditoria do projeto "${projectName}" realizado em ${new Date().toLocaleDateString("pt-BR")}.\n\nScore: ${score}/100\n\nClique no link abaixo para visualizar o laudo completo com gráficos e recomendações.\n\nAtenciosamente`
  );
  const [isLoading, setIsLoading] = useState(false);
  const [emailError, setEmailError] = useState<string>("");

  const reportLink = `${window.location.origin}/v/${reportId}`;

  const validateEmails = (emailString: string): boolean => {
    if (!emailString.trim()) {
      setEmailError("Por favor, insira pelo menos um e-mail");
      return false;
    }

    const emailList = emailString
      .split(",")
      .map((e) => e.trim())
      .filter((e) => e.length > 0);

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const invalidEmails = emailList.filter((e) => !emailRegex.test(e));

    if (invalidEmails.length > 0) {
      setEmailError(
        `E-mails inválidos: ${invalidEmails.join(", ")}`
      );
      return false;
    }

    setEmailError("");
    return true;
  };

  const handleShare = async () => {
    if (!validateEmails(emails)) {
      return;
    }

    setIsLoading(true);

    try {
      // Simular envio de e-mail
      await new Promise((resolve) => setTimeout(resolve, 1500));

      const emailList = emails
        .split(",")
        .map((e) => e.trim())
        .filter((e) => e.length > 0);

      // Aqui você faria uma chamada à API real
      console.log("Enviando laudo para:", emailList);
      console.log("Mensagem:", message);
      console.log("Link:", reportLink);

      toast.success(
        `Laudo compartilhado com sucesso! Enviado para ${emailList.length} destinatário(s).`
      );

      onClose();
    } catch (error) {
      toast.error("Erro ao compartilhar laudo. Tente novamente.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopyLink = () => {
    navigator.clipboard.writeText(reportLink);
    toast.success("Link copiado para a área de transferência!");
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-background border border-border rounded-lg max-w-2xl w-full">
        {/* Header */}
        <div className="bg-card border-b border-border p-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Mail className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-bold text-foreground">
              Compartilhar Laudo por E-mail
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Project Info */}
          <div className="bg-secondary/30 border border-border rounded-lg p-4">
            <p className="text-sm text-muted-foreground mb-1">Projeto</p>
            <p className="font-semibold text-foreground">{projectName}</p>
            <p className="text-sm text-muted-foreground mt-3">Score</p>
            <p className="font-semibold text-foreground">{score}/100</p>
          </div>

          {/* Email Input */}
          <div>
            <label className="block text-sm font-semibold text-foreground mb-2">
              Destinatários (separados por vírgula)
            </label>
            <textarea
              value={emails}
              onChange={(e) => {
                setEmails(e.target.value);
                setEmailError("");
              }}
              placeholder="exemplo@email.com, outro@email.com"
              className="w-full px-4 py-3 border border-border rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              rows={3}
            />
            {emailError && (
              <div className="flex items-center gap-2 mt-2 text-critical text-sm">
                <AlertCircle className="w-4 h-4" />
                {emailError}
              </div>
            )}
            <p className="text-xs text-muted-foreground mt-2">
              Você pode inserir múltiplos e-mails separados por vírgula
            </p>
          </div>

          {/* Message */}
          <div>
            <label className="block text-sm font-semibold text-foreground mb-2">
              Mensagem Personalizada
            </label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              className="w-full px-4 py-3 border border-border rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              rows={6}
            />
            <p className="text-xs text-muted-foreground mt-2">
              O link do laudo será adicionado automaticamente ao final da mensagem
            </p>
          </div>

          {/* Link Preview */}
          <div>
            <label className="block text-sm font-semibold text-foreground mb-2">
              Link do Laudo
            </label>
            <div className="flex items-center gap-2 bg-secondary/30 border border-border rounded-lg p-3">
              <code className="flex-1 text-xs text-foreground break-all font-mono">
                {reportLink}
              </code>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleCopyLink}
                className="text-primary hover:bg-primary/10 flex-shrink-0"
              >
                <Copy className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Info Box */}
          <div className="bg-primary/5 border border-primary/20 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
              <div className="text-sm text-foreground">
                <p className="font-semibold mb-1">O que será enviado:</p>
                <ul className="space-y-1 text-xs text-muted-foreground">
                  <li>• Sua mensagem personalizada</li>
                  <li>• Link público do laudo com QR Code</li>
                  <li>• Score e resumo de vulnerabilidades</li>
                  <li>• Acesso a gráficos e recomendações</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t border-border">
            <Button
              variant="outline"
              onClick={onClose}
              className="flex-1"
            >
              Cancelar
            </Button>
            <Button
              onClick={handleShare}
              disabled={isLoading || !emails.trim()}
              className="flex-1 bg-primary hover:bg-primary/90 text-white"
            >
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  Enviando...
                </>
              ) : (
                <>
                  <Mail className="w-4 h-4 mr-2" />
                  Compartilhar por E-mail
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
