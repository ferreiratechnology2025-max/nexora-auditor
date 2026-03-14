import { useState } from "react";
import { useLocation } from "wouter";
import { Mail, ArrowLeft, Loader2, AlertCircle, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";

/**
 * AUDITX Forgot Password Page
 * Design: Minimalismo Cirúrgico
 * - Solicitação de recuperação por e-mail
 * - Validação de e-mail
 * - Confirmação de envio
 */

export default function ForgotPassword() {
  const [, setLocation] = useLocation();
  const { requestPasswordReset, isLoading } = useAuth();
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string>("");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email) {
      setError("Por favor, insira seu e-mail");
      return;
    }

    if (!email.includes("@")) {
      setError("E-mail inválido");
      return;
    }

    try {
      await requestPasswordReset(email);
      setSubmitted(true);
      toast.success("E-mail de recuperação enviado com sucesso!");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Erro ao solicitar recuperação";
      setError(message);
      toast.error(message);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">AUDITX</h1>
          <p className="text-muted-foreground">
            Recupere o acesso à sua conta
          </p>
        </div>

        {/* Card */}
        <div className="bg-card border border-border rounded-lg p-8 space-y-6">
          {!submitted ? (
            <>
              {/* Error Alert */}
              {error && (
                <div className="flex items-start gap-3 p-4 bg-critical/10 border border-critical/20 rounded-lg">
                  <AlertCircle className="w-5 h-5 text-critical flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-critical">{error}</p>
                </div>
              )}

              {/* Info Box */}
              <div className="bg-primary/5 border border-primary/20 rounded-lg p-4">
                <p className="text-sm text-foreground">
                  Insira o e-mail associado à sua conta e enviaremos um link de recuperação.
                </p>
              </div>

              {/* Email Input */}
              <div>
                <label className="block text-sm font-semibold text-foreground mb-2">
                  E-mail
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 w-5 h-5 text-muted-foreground" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => {
                      setEmail(e.target.value);
                      setError("");
                    }}
                    placeholder="seu@email.com"
                    className="w-full pl-10 pr-4 py-2 border border-border rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>

              {/* Submit Button */}
              <Button
                onClick={handleSubmit}
                disabled={isLoading}
                className="w-full bg-primary hover:bg-primary/90 text-white"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Enviando...
                  </>
                ) : (
                  <>
                    <Mail className="w-4 h-4 mr-2" />
                    Enviar Link de Recuperação
                  </>
                )}
              </Button>

              {/* Back Link */}
              <button
                onClick={() => setLocation("/login")}
                className="w-full flex items-center justify-center gap-2 text-sm text-primary hover:underline"
              >
                <ArrowLeft className="w-4 h-4" />
                Voltar para Login
              </button>
            </>
          ) : (
            <>
              {/* Success State */}
              <div className="text-center space-y-4">
                <div className="flex justify-center mb-4">
                  <div className="w-16 h-16 bg-safe/10 border border-safe/20 rounded-full flex items-center justify-center">
                    <CheckCircle className="w-8 h-8 text-safe" />
                  </div>
                </div>

                <h2 className="text-xl font-bold text-foreground">
                  E-mail Enviado com Sucesso!
                </h2>

                <p className="text-muted-foreground">
                  Verificamos o e-mail <strong>{email}</strong>. Se a conta existir, você receberá um link de recuperação em breve.
                </p>

                {/* Info Box */}
                <div className="bg-secondary/30 border border-border rounded-lg p-4 text-sm text-foreground">
                  <p className="font-semibold mb-2">Próximos passos:</p>
                  <ul className="space-y-1 text-left text-xs text-muted-foreground">
                    <li>• Verifique sua caixa de entrada</li>
                    <li>• Clique no link de recuperação</li>
                    <li>• Defina uma nova senha</li>
                    <li>• Faça login com a nova senha</li>
                  </ul>
                </div>

                {/* Warning */}
                <div className="bg-warning/5 border border-warning/20 rounded-lg p-4 text-xs text-warning">
                  <p>
                    <strong>Nota:</strong> O link de recuperação expira em 1 hora. Se não receber o e-mail, verifique a pasta de spam.
                  </p>
                </div>
              </div>

              {/* Back Button */}
              <Button
                onClick={() => setLocation("/login")}
                variant="outline"
                className="w-full border-border text-foreground hover:bg-secondary"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Voltar para Login
              </Button>
            </>
          )}
        </div>

        {/* Help Text */}
        <p className="text-center text-xs text-muted-foreground mt-6">
          Precisa de ajuda?{" "}
          <a href="mailto:suporte@auditx.ai" className="text-primary hover:underline">
            Entre em contato com o suporte
          </a>
        </p>
      </div>
    </div>
  );
}
