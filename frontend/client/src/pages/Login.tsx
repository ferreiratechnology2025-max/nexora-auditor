import { useState } from "react";
import { useLocation } from "wouter";
import { Mail, Lock, Loader2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";

/**
 * AUDITX Login Page
 * Design: Minimalismo Cirúrgico
 * - Login com email/senha
 * - Integração com OAuth (Google, GitHub)
 * - Validação de formulário
 * - Redirecionamento automático
 */

export default function Login() {
  const [, setLocation] = useLocation();
  const { login, loginWithOAuth, isLoading } = useAuth();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [error, setError] = useState<string>("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setError("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.email || !formData.password) {
      setError("Email e senha são obrigatórios");
      return;
    }

    try {
      await login(formData.email, formData.password);
      toast.success("Login realizado com sucesso!");
      setLocation("/dashboard");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Erro ao fazer login";
      setError(message);
      toast.error(message);
    }
  };

  const handleOAuthLogin = async (provider: "google" | "github") => {
    try {
      await loginWithOAuth(provider);
      toast.success(`Login com ${provider} realizado com sucesso!`);
      setLocation("/dashboard");
    } catch (err) {
      const message =
        err instanceof Error ? err.message : `Erro ao fazer login com ${provider}`;
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
            Faça login para acessar seu dashboard
          </p>
        </div>

        {/* Login Card */}
        <div className="bg-card border border-border rounded-lg p-8 space-y-6">
          {/* Error Alert */}
          {error && (
            <div className="flex items-start gap-3 p-4 bg-critical/10 border border-critical/20 rounded-lg">
              <AlertCircle className="w-5 h-5 text-critical flex-shrink-0 mt-0.5" />
              <p className="text-sm text-critical">{error}</p>
            </div>
          )}

          {/* Email Input */}
          <div>
            <label className="block text-sm font-semibold text-foreground mb-2">
              Email
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 w-5 h-5 text-muted-foreground" />
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="seu@email.com"
                className="w-full pl-10 pr-4 py-2 border border-border rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>

          {/* Password Input */}
          <div>
            <label className="block text-sm font-semibold text-foreground mb-2">
              Senha
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 w-5 h-5 text-muted-foreground" />
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                className="w-full pl-10 pr-4 py-2 border border-border rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>

          {/* Remember & Forgot */}
          <div className="flex items-center justify-between text-sm">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                className="w-4 h-4 rounded border-border"
              />
              <span className="text-muted-foreground">Lembrar-me</span>
            </label>
            <button
              onClick={() => setLocation("/forgot-password")}
              className="text-primary hover:underline"
            >
              Esqueci a senha
            </button>
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
                Entrando...
              </>
            ) : (
              "Entrar"
            )}
          </Button>

          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-border"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-card text-muted-foreground">
                Ou continue com
              </span>
            </div>
          </div>

          {/* OAuth Buttons */}
          <div className="grid grid-cols-2 gap-3">
            <Button
              onClick={() => handleOAuthLogin("google")}
              disabled={isLoading}
              variant="outline"
              className="border-border text-foreground hover:bg-secondary"
            >
              Google
            </Button>
            <Button
              onClick={() => handleOAuthLogin("github")}
              disabled={isLoading}
              variant="outline"
              className="border-border text-foreground hover:bg-secondary"
            >
              GitHub
            </Button>
          </div>

          {/* Sign Up Link */}
          <p className="text-center text-sm text-muted-foreground">
            Não tem conta?{" "}
            <button
              onClick={() => setLocation("/register")}
              className="text-primary hover:underline font-semibold"
            >
              Registre-se aqui
            </button>
          </p>
        </div>

        {/* Demo Credentials */}
        <div className="mt-6 p-4 bg-secondary/30 border border-border rounded-lg text-xs text-muted-foreground">
          <p className="font-semibold mb-2">Credenciais de Demonstração:</p>
          <p>Email: demo@auditx.com</p>
          <p>Senha: demo123456</p>
        </div>
      </div>
    </div>
  );
}
