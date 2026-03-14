import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { Mail, Loader2, AlertCircle, CheckCircle, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";

/**
 * AUDITX Verify Email Page
 * Design: Minimalismo Cirúrgico
 * - Verificação de e-mail com token
 * - Reenvio de e-mail
 * - Confirmação de sucesso
 */

export default function VerifyEmail() {
  const [, setLocation] = useLocation();
  const { verifyEmail, verifyEmailToken, resendVerificationEmail, isLoading, user } = useAuth();

  // Extrair token da URL
  const searchParams = new URLSearchParams(window.location.search);
  const token = searchParams.get("token") || "";
  const email = searchParams.get("email") || user?.email || "";

  const [tokenValid, setTokenValid] = useState<boolean | null>(null);
  const [verified, setVerified] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);
  const [error, setError] = useState<string>("");

  // Verificar token ao carregar
  useEffect(() => {
    const checkAndVerify = async () => {
      if (!token) {
        setTokenValid(false);
        setError("Token não encontrado na URL");
        return;
      }

      try {
        const isValid = await verifyEmailToken(token);
        if (!isValid) {
          setTokenValid(false);
          setError("Token inválido ou expirado. Solicite um novo link de verificação.");
          return;
        }

        setTokenValid(true);

        // Verificar e-mail automaticamente
        try {
          await verifyEmail(token);
          setVerified(true);
          toast.success("E-mail verificado com sucesso!");
        } catch (err) {
          const message = err instanceof Error ? err.message : "Erro ao verificar e-mail";
          setError(message);
          setTokenValid(false);
          toast.error(message);
        }
      } catch (err) {
        setTokenValid(false);
        setError("Erro ao verificar token");
      }
    };

    checkAndVerify();
  }, [token, verifyEmail, verifyEmailToken]);

  const handleResendEmail = async () => {
    if (!email) {
      setError("E-mail não encontrado");
      return;
    }

    setResendLoading(true);
    try {
      await resendVerificationEmail(email);
      toast.success("E-mail de verificação reenviado!");
      setError("");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Erro ao reenviar e-mail";
      setError(message);
      toast.error(message);
    } finally {
      setResendLoading(false);
    }
  };

  if (tokenValid === null) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Verificando e-mail...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">AUDITX</h1>
          <p className="text-muted-foreground">
            {verified ? "E-mail Verificado" : "Verificar E-mail"}
          </p>
        </div>

        {/* Card */}
        <div className="bg-card border border-border rounded-lg p-8 space-y-6">
          {verified ? (
            <>
              {/* Success State */}
              <div className="text-center space-y-4">
                <div className="flex justify-center mb-4">
                  <div className="w-16 h-16 bg-safe/10 border border-safe/20 rounded-full flex items-center justify-center">
                    <CheckCircle className="w-8 h-8 text-safe" />
                  </div>
                </div>

                <h2 className="text-xl font-bold text-foreground">
                  E-mail Verificado com Sucesso!
                </h2>

                <p className="text-muted-foreground">
                  Sua conta foi ativada. Você pode fazer login agora.
                </p>

                {/* Info Box */}
                <div className="bg-secondary/30 border border-border rounded-lg p-4 text-sm text-foreground">
                  <p className="font-semibold mb-2">Próximos passos:</p>
                  <ul className="space-y-1 text-left text-xs text-muted-foreground">
                    <li>• Faça login com suas credenciais</li>
                    <li>• Acesse o dashboard</li>
                    <li>• Comece a auditar seus projetos</li>
                  </ul>
                </div>
              </div>

              {/* Login Button */}
              <Button
                onClick={() => setLocation("/login")}
                className="w-full bg-primary hover:bg-primary/90 text-white"
              >
                Ir para Login
              </Button>
            </>
          ) : (
            <>
              {/* Error State */}
              <div className="flex items-start gap-3 p-4 bg-critical/10 border border-critical/20 rounded-lg">
                <AlertCircle className="w-5 h-5 text-critical flex-shrink-0 mt-0.5" />
                <p className="text-sm text-critical">
                  {error || "Erro ao verificar e-mail"}
                </p>
              </div>

              {/* Info Box */}
              <div className="bg-secondary/30 border border-border rounded-lg p-4 text-sm text-foreground">
                <p className="font-semibold mb-2">O que fazer:</p>
                <ul className="space-y-1 text-left text-xs text-muted-foreground">
                  <li>• Verifique se o link foi copiado corretamente</li>
                  <li>• O link expira em 24 horas</li>
                  <li>• Solicite um novo link de verificação</li>
                </ul>
              </div>

              {/* Resend Button */}
              <Button
                onClick={handleResendEmail}
                disabled={resendLoading || isLoading}
                variant="outline"
                className="w-full border-border text-foreground hover:bg-secondary"
              >
                {resendLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Reenviando...
                  </>
                ) : (
                  <>
                    <Mail className="w-4 h-4 mr-2" />
                    Reenviar E-mail de Verificação
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
