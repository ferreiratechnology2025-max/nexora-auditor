import { createContext, useState, useEffect, ReactNode } from "react";
import { api } from "@/lib/api";

/**
 * AUDITX Auth Context
 * Design: Minimalismo Cirúrgico
 * - Gerenciamento de estado de autenticação
 * - Persistência em localStorage
 * - Integração com Manus OAuth
 * - Verificação de e-mail
 */

interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  plan: "dev" | "pro" | "scale";
  createdAt: string;
  emailVerified: boolean;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
  loginWithOAuth: (provider: "google" | "github") => Promise<void>;
  requestPasswordReset: (email: string) => Promise<void>;
  resetPassword: (token: string, newPassword: string) => Promise<void>;
  verifyResetToken: (token: string) => Promise<boolean>;
  sendVerificationEmail: (email: string) => Promise<void>;
  verifyEmail: (token: string) => Promise<void>;
  verifyEmailToken: (token: string) => Promise<boolean>;
  resendVerificationEmail: (email: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("auditx_token");
    if (token) {
      api.auth.me()
        .then((apiUser) => {
          setUser({
            id: String(apiUser.id),
            email: apiUser.email,
            name: apiUser.name,
            plan: apiUser.plan === "enterprise" ? "scale" : apiUser.plan === "pro" ? "pro" : "dev",
            createdAt: new Date().toISOString(),
            emailVerified: true,
          });
        })
        .catch(() => {
          localStorage.removeItem("auditx_token");
          localStorage.removeItem("auditx_user");
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const { token, user: apiUser } = await api.auth.login(email, password);
      localStorage.setItem("auditx_token", token);
      const u: User = {
        id: String(apiUser.id),
        email: apiUser.email,
        name: apiUser.name,
        plan: apiUser.plan === "enterprise" ? "scale" : apiUser.plan === "pro" ? "pro" : "dev",
        createdAt: new Date().toISOString(),
        emailVerified: true,
      };
      setUser(u);
      localStorage.setItem("auditx_user", JSON.stringify(u));
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, password: string, name: string) => {
    setIsLoading(true);
    try {
      const { token, user: apiUser } = await api.auth.register(email, password, name);
      localStorage.setItem("auditx_token", token);
      const u: User = {
        id: String(apiUser.id),
        email: apiUser.email,
        name: apiUser.name,
        plan: "dev",
        createdAt: new Date().toISOString(),
        emailVerified: true,
      };
      setUser(u);
      localStorage.setItem("auditx_user", JSON.stringify(u));
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("auditx_user");
    localStorage.removeItem("auditx_token");
  };

  const loginWithOAuth = async (_provider: "google" | "github") => {
    throw new Error("Login social em breve. Use email e senha por enquanto.");
  };

  const requestPasswordReset = async (email: string) => {
    setIsLoading(true);
    try {
      // Simular chamada à API
      await new Promise((resolve) => setTimeout(resolve, 1000));

      if (!email || !email.includes("@")) {
        throw new Error("Email inválido");
      }

      // Mock: gerar token de reset
      const resetToken = "reset_" + Math.random().toString(36).substr(2, 20);
      localStorage.setItem(`auditx_reset_token_${email}`, resetToken);
      localStorage.setItem(`auditx_reset_token_time_${email}`, Date.now().toString());

      // Aqui você faria uma chamada à API para enviar e-mail
      console.log(`E-mail de recuperação enviado para ${email}`);
      console.log(`Token (mock): ${resetToken}`);
    } finally {
      setIsLoading(false);
    }
  };

  const verifyResetToken = async (token: string): Promise<boolean> => {
    try {
      // Simular validação de token
      await new Promise((resolve) => setTimeout(resolve, 500));

      // Verificar se o token existe e não expirou (1 hora)
      const entries = Object.entries(localStorage);
      for (const [key, value] of entries) {
        if (key.startsWith("auditx_reset_token_") && value === token) {
          const timeKey = key.replace("auditx_reset_token_", "auditx_reset_token_time_");
          const createdTime = parseInt(localStorage.getItem(timeKey) || "0");
          const isExpired = Date.now() - createdTime > 3600000; // 1 hora
          return !isExpired;
        }
      }
      return false;
    } catch (error) {
      console.error("Erro ao verificar token:", error);
      return false;
    }
  };

  const resetPassword = async (token: string, newPassword: string) => {
    setIsLoading(true);
    try {
      // Simular chamada à API
      await new Promise((resolve) => setTimeout(resolve, 1200));

      if (!newPassword || newPassword.length < 6) {
        throw new Error("Senha deve ter no mínimo 6 caracteres");
      }

      // Verificar token
      const isValid = await verifyResetToken(token);
      if (!isValid) {
        throw new Error("Token inválido ou expirado");
      }

      // Limpar tokens de reset
      const entries = Object.entries(localStorage);
      for (const [key] of entries) {
        if (key.startsWith("auditx_reset_token_") && localStorage.getItem(key) === token) {
          const email = key.replace("auditx_reset_token_", "");
          localStorage.removeItem(key);
          localStorage.removeItem(`auditx_reset_token_time_${email}`);
          break;
        }
      }

      // Aqui você faria uma chamada à API para atualizar a senha
      console.log("Senha redefinida com sucesso");
    } finally {
      setIsLoading(false);
    }
  };

  const sendVerificationEmail = async (email: string) => {
    setIsLoading(true);
    try {
      // Simular chamada à API
      await new Promise((resolve) => setTimeout(resolve, 1000));

      if (!email || !email.includes("@")) {
        throw new Error("Email inválido");
      }

      // Mock: gerar token de verificação
      const verificationToken = "verify_" + Math.random().toString(36).substr(2, 20);
      localStorage.setItem(`auditx_verify_token_${email}`, verificationToken);
      localStorage.setItem(`auditx_verify_token_time_${email}`, Date.now().toString());

      // Aqui você faria uma chamada à API para enviar e-mail
      console.log(`E-mail de verificação enviado para ${email}`);
      console.log(`Token (mock): ${verificationToken}`);
    } finally {
      setIsLoading(false);
    }
  };

  const verifyEmailToken = async (token: string): Promise<boolean> => {
    try {
      // Simular validação de token
      await new Promise((resolve) => setTimeout(resolve, 500));

      // Verificar se o token existe e não expirou (24 horas)
      const entries = Object.entries(localStorage);
      for (const [key, value] of entries) {
        if (key.startsWith("auditx_verify_token_") && value === token) {
          const timeKey = key.replace("auditx_verify_token_", "auditx_verify_token_time_");
          const createdTime = parseInt(localStorage.getItem(timeKey) || "0");
          const isExpired = Date.now() - createdTime > 86400000; // 24 horas
          return !isExpired;
        }
      }
      return false;
    } catch (error) {
      console.error("Erro ao verificar token:", error);
      return false;
    }
  };

  const verifyEmail = async (token: string) => {
    setIsLoading(true);
    try {
      // Simular chamada à API
      await new Promise((resolve) => setTimeout(resolve, 1200));

      // Verificar token
      const isValid = await verifyEmailToken(token);
      if (!isValid) {
        throw new Error("Token inválido ou expirado");
      }

      // Atualizar usuário com e-mail verificado
      if (user) {
        const updatedUser = { ...user, emailVerified: true };
        setUser(updatedUser);
        localStorage.setItem("auditx_user", JSON.stringify(updatedUser));
      }

      // Limpar tokens de verificação
      const entries = Object.entries(localStorage);
      for (const [key] of entries) {
        if (key.startsWith("auditx_verify_token_") && localStorage.getItem(key) === token) {
          const email = key.replace("auditx_verify_token_", "");
          localStorage.removeItem(key);
          localStorage.removeItem(`auditx_verify_token_time_${email}`);
          break;
        }
      }

      console.log("E-mail verificado com sucesso");
    } finally {
      setIsLoading(false);
    }
  };

  const resendVerificationEmail = async (email: string) => {
    setIsLoading(true);
    try {
      // Simular chamada à API
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Limpar token antigo
      localStorage.removeItem(`auditx_verify_token_${email}`);
      localStorage.removeItem(`auditx_verify_token_time_${email}`);

      // Enviar novo e-mail
      await sendVerificationEmail(email);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user && user.emailVerified,
        isLoading,
        login,
        register,
        logout,
        loginWithOAuth,
        requestPasswordReset,
        resetPassword,
        verifyResetToken,
        sendVerificationEmail,
        verifyEmail,
        verifyEmailToken,
        resendVerificationEmail,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth deve ser usado dentro de um AuthProvider");
  }
  return context;
}

import { useContext } from "react";
