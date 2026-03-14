import { useState } from "react";
import { useLocation } from "wouter";
import { Mail, Lock, User, Loader2, AlertCircle, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";

/**
 * AUDITX Register Page
 * Design: Minimalismo Cirúrgico
 * - Registro com email/senha/nome
 * - Validação de força de senha
 * - Integração com OAuth
 * - Redirecionamento automático
 */

export default function Register() {
  const [, setLocation] = useLocation();
  const { register, loginWithOAuth, isLoading } = useAuth();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [error, setError] = useState<string>("");
  const [passwordStrength, setPasswordStrength] = useState(0);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setError("");

    // Calcular força de senha
    if (name === "password") {
      let strength = 0;
      if (value.length >= 8) strength++;
      if (/[A-Z]/.test(value)) strength++;
      if (/[0-9]/.test(value)) strength++;
      if (/[^A-Za-z0-9]/.test(value)) strength++;
      setPasswordStrength(strength);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name || !formData.email || !formData.password) {
      setError("Todos os campos são obrigatórios");
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError("As senhas não coincidem");
      return;
    }

    if (formData.password.length < 6) {
      setError("Senha deve ter no mínimo 6 caracteres");
      return;
    }

    try {
      await register(formData.email, formData.password, formData.name);
      toast.success("Conta criada! Verifique seu e-mail para ativar a conta.");
      // Redirecionar para página de verificação de e-mail
      setLocation(`/verify-email?email=${encodeURIComponent(formData.email)}`);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Erro ao registrar";
      setError(message);
      toast.error(message);
    }
  };

  const handleOAuthRegister = async (provider: "google" | "github") => {
    try {
      await loginWithOAuth(provider);
      toast.success(`Conta criada com ${provider} com sucesso!`);
      // OAuth geralmente vem com e-mail verificado, então vai direto para dashboard
      setLocation("/dashboard");
    } catch (err) {
      const message =
        err instanceof Error ? err.message : `Erro ao registrar com ${provider}`;
      setError(message);
      toast.error(message);
    }
  };

  const getPasswordStrengthColor = () => {
    if (passwordStrength === 0) return "bg-muted";
    if (passwordStrength === 1) return "bg-critical";
    if (passwordStrength === 2) return "bg-warning";
    if (passwordStrength === 3) return "bg-warning";
    return "bg-safe";
  };

  const getPasswordStrengthLabel = () => {
    if (passwordStrength === 0) return "Muito fraca";
    if (passwordStrength === 1) return "Fraca";
    if (passwordStrength === 2) return "Média";
    if (passwordStrength === 3) return "Forte";
    return "Muito forte";
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">AUDITX</h1>
          <p className="text-muted-foreground">
            Crie sua conta para começar
          </p>
        </div>

        {/* Register Card */}
        <div className="bg-card border border-border rounded-lg p-8 space-y-6">
          {/* Error Alert */}
          {error && (
            <div className="flex items-start gap-3 p-4 bg-critical/10 border border-critical/20 rounded-lg">
              <AlertCircle className="w-5 h-5 text-critical flex-shrink-0 mt-0.5" />
              <p className="text-sm text-critical">{error}</p>
            </div>
          )}

          {/* Name Input */}
          <div>
            <label className="block text-sm font-semibold text-foreground mb-2">
              Nome Completo
            </label>
            <div className="relative">
              <User className="absolute left-3 top-3 w-5 h-5 text-muted-foreground" />
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="João Silva"
                className="w-full pl-10 pr-4 py-2 border border-border rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>

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
            {formData.password && (
              <div className="mt-2">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-muted-foreground">
                    Força da senha
                  </span>
                  <span className="text-xs font-semibold text-foreground">
                    {getPasswordStrengthLabel()}
                  </span>
                </div>
                <div className="w-full h-2 bg-secondary rounded-full overflow-hidden">
                  <div
                    className={`h-full ${getPasswordStrengthColor()} transition-all`}
                    style={{ width: `${(passwordStrength / 4) * 100}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>

          {/* Confirm Password Input */}
          <div>
            <label className="block text-sm font-semibold text-foreground mb-2">
              Confirmar Senha
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 w-5 h-5 text-muted-foreground" />
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="••••••••"
                className="w-full pl-10 pr-4 py-2 border border-border rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              />
              {formData.password && formData.confirmPassword && (
                <div className="absolute right-3 top-3">
                  {formData.password === formData.confirmPassword ? (
                    <CheckCircle className="w-5 h-5 text-safe" />
                  ) : (
                    <AlertCircle className="w-5 h-5 text-critical" />
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Terms */}
          <label className="flex items-start gap-2 cursor-pointer">
            <input
              type="checkbox"
              className="w-4 h-4 rounded border-border mt-1"
            />
            <span className="text-sm text-muted-foreground">
              Concordo com os{" "}
              <a href="/privacy#terms" className="text-primary hover:underline">
                Termos de Serviço
              </a>{" "}
              e{" "}
              <a href="/privacy" className="text-primary hover:underline">
                Política de Privacidade
              </a>
            </span>
          </label>

          {/* Submit Button */}
          <Button
            onClick={handleSubmit}
            disabled={isLoading}
            className="w-full bg-primary hover:bg-primary/90 text-white"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Criando conta...
              </>
            ) : (
              "Criar Conta"
            )}
          </Button>

          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-border"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-card text-muted-foreground">
                Ou registre-se com
              </span>
            </div>
          </div>

          {/* OAuth Buttons */}
          <div className="grid grid-cols-2 gap-3">
            <Button
              onClick={() => handleOAuthRegister("google")}
              disabled={isLoading}
              variant="outline"
              className="border-border text-foreground hover:bg-secondary"
            >
              Google
            </Button>
            <Button
              onClick={() => handleOAuthRegister("github")}
              disabled={isLoading}
              variant="outline"
              className="border-border text-foreground hover:bg-secondary"
            >
              GitHub
            </Button>
          </div>

          {/* Login Link */}
          <p className="text-center text-sm text-muted-foreground">
            Já tem conta?{" "}
            <button
              onClick={() => setLocation("/login")}
              className="text-primary hover:underline font-semibold"
            >
              Faça login aqui
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
