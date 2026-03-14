import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { Lock, Loader2, AlertCircle, CheckCircle, Eye, EyeOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";

/**
 * AUDITX Reset Password Page
 * Design: Minimalismo Cirúrgico
 * - Redefinição de senha com token
 * - Validação de força de senha
 * - Confirmação de sucesso
 */

export default function ResetPassword() {
  const [, setLocation] = useLocation();
  const { resetPassword, verifyResetToken, isLoading } = useAuth();
  
  // Extrair token da URL
  const searchParams = new URLSearchParams(window.location.search);
  const token = searchParams.get("token") || "";

  const [formData, setFormData] = useState({
    password: "",
    confirmPassword: "",
  });
  const [error, setError] = useState<string>("");
  const [tokenValid, setTokenValid] = useState<boolean | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState(0);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // Verificar token ao carregar
  useEffect(() => {
    const checkToken = async () => {
      if (!token) {
        setTokenValid(false);
        setError("Token não encontrado na URL");
        return;
      }

      try {
        const isValid = await verifyResetToken(token);
        setTokenValid(isValid);
        if (!isValid) {
          setError("Token inválido ou expirado. Solicite um novo link de recuperação.");
        }
      } catch (err) {
        setTokenValid(false);
        setError("Erro ao verificar token");
      }
    };

    checkToken();
  }, [token, verifyResetToken]);

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

    if (!formData.password || !formData.confirmPassword) {
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
      await resetPassword(token, formData.password);
      setSubmitted(true);
      toast.success("Senha redefinida com sucesso!");
      setTimeout(() => setLocation("/login"), 2000);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Erro ao redefinir senha";
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

  if (tokenValid === null) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Verificando link de recuperação...</p>
        </div>
      </div>
    );
  }

  if (!tokenValid) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="bg-card border border-border rounded-lg p-8 space-y-6 text-center">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 bg-critical/10 border border-critical/20 rounded-full flex items-center justify-center">
                <AlertCircle className="w-8 h-8 text-critical" />
              </div>
            </div>

            <h2 className="text-xl font-bold text-foreground">
              Link Inválido ou Expirado
            </h2>

            <p className="text-muted-foreground">
              {error || "O link de recuperação não é válido ou expirou."}
            </p>

            <div className="bg-secondary/30 border border-border rounded-lg p-4 text-sm text-foreground">
              <p className="font-semibold mb-2">O que fazer:</p>
              <ul className="space-y-1 text-left text-xs text-muted-foreground">
                <li>• Solicite um novo link de recuperação</li>
                <li>• Verifique se o link foi copiado corretamente</li>
                <li>• Tente novamente em alguns minutos</li>
              </ul>
            </div>

            <Button
              onClick={() => setLocation("/forgot-password")}
              className="w-full bg-primary hover:bg-primary/90 text-white"
            >
              Solicitar Novo Link
            </Button>
          </div>
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
            Defina uma nova senha
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
                  Escolha uma senha forte com pelo menos 6 caracteres.
                </p>
              </div>

              {/* Password Input */}
              <div>
                <label className="block text-sm font-semibold text-foreground mb-2">
                  Nova Senha
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 w-5 h-5 text-muted-foreground" />
                  <input
                    type={showPassword ? "text" : "password"}
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="••••••••"
                    className="w-full pl-10 pr-10 py-2 border border-border rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-3 text-muted-foreground hover:text-foreground"
                  >
                    {showPassword ? (
                      <EyeOff className="w-5 h-5" />
                    ) : (
                      <Eye className="w-5 h-5" />
                    )}
                  </button>
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
                    type={showConfirmPassword ? "text" : "password"}
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    placeholder="••••••••"
                    className="w-full pl-10 pr-10 py-2 border border-border rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-3 text-muted-foreground hover:text-foreground"
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="w-5 h-5" />
                    ) : (
                      <Eye className="w-5 h-5" />
                    )}
                  </button>
                  {formData.password && formData.confirmPassword && (
                    <div className="absolute right-10 top-3">
                      {formData.password === formData.confirmPassword ? (
                        <CheckCircle className="w-5 h-5 text-safe" />
                      ) : (
                        <AlertCircle className="w-5 h-5 text-critical" />
                      )}
                    </div>
                  )}
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
                    Redefinindo...
                  </>
                ) : (
                  <>
                    <Lock className="w-4 h-4 mr-2" />
                    Redefinir Senha
                  </>
                )}
              </Button>
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
                  Senha Redefinida com Sucesso!
                </h2>

                <p className="text-muted-foreground">
                  Sua senha foi atualizada. Você será redirecionado para o login em breve.
                </p>

                <Button
                  onClick={() => setLocation("/login")}
                  className="w-full bg-primary hover:bg-primary/90 text-white"
                >
                  Ir para Login
                </Button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
