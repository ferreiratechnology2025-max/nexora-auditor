import { Button } from "@/components/ui/button";
import { Menu, X, LogOut, User } from "lucide-react";
import { useState } from "react";
import { useLocation } from "wouter";
import { useAuth } from "@/contexts/AuthContext";

/**
 * AUDITX Header Component
 * Design: Minimalismo Cirúrgico
 * - Logo e navegação limpa
 * - CTA "Entrar / Cadastro" no canto direito
 * - Menu de usuário autenticado
 * - Responsivo com menu mobile
 */
export default function Header() {
  const [, setLocation] = useLocation();
  const { isAuthenticated, user, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    setLocation("/");
  };

  return (
    <header className="sticky top-0 z-50 bg-background border-b border-border">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        {/* Logo */}
        <div
          className="flex items-center gap-2 cursor-pointer"
          onClick={() => setLocation("/")}
        >
          <div className="w-8 h-8 bg-primary rounded flex items-center justify-center">
            <span className="text-white font-bold text-sm">AX</span>
          </div>
          <span className="font-bold text-lg text-foreground hidden sm:inline">
            AUDITX
          </span>
        </div>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-8">
          <button
            onClick={() => setLocation("/como-funciona")}
            className="text-sm text-foreground hover:text-primary transition-colors"
          >
            Como Funciona
          </button>
          <button
            onClick={() => setLocation("/planos")}
            className="text-sm text-foreground hover:text-primary transition-colors"
          >
            Planos
          </button>
          <button
            onClick={() => setLocation("/certificacoes")}
            className="text-sm text-foreground hover:text-primary transition-colors"
          >
            Certificações
          </button>
          <button
            onClick={() => setLocation("/depoimentos")}
            className="text-sm text-foreground hover:text-primary transition-colors"
          >
            Depoimentos
          </button>
        </nav>

        {/* Desktop CTA */}
        <div className="hidden md:flex gap-4 items-center">
          <Button
            size="sm"
            className="bg-primary hover:bg-primary/90 text-white font-bold px-6 shadow-lg shadow-primary/20 animate-in fade-in slide-in-from-right-4 duration-500"
            onClick={() => {
              setLocation("/");
              setTimeout(() => window.scrollTo({ top: 0, behavior: 'smooth' }), 100);
            }}
          >
            Auditoria Gratuita
          </Button>

          {isAuthenticated ? (
            <>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setLocation("/dashboard")}
                className="text-foreground hover:bg-secondary"
              >
                <User className="w-4 h-4 mr-2" />
                {user?.name}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleLogout}
                className="border-border text-foreground hover:bg-secondary"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Sair
              </Button>
            </>
          ) : (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setLocation("/login")}
              >
                Entrar
              </Button>
              <Button
                size="sm"
                className="bg-primary hover:bg-primary/90"
                onClick={() => setLocation("/register")}
              >
                Cadastro
              </Button>
            </>
          )}
        </div>

        {/* Mobile Menu Button */}
        <button
          className="md:hidden"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          {mobileMenuOpen ? (
            <X className="w-6 h-6" />
          ) : (
            <Menu className="w-6 h-6" />
          )}
        </button>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-border bg-background">
          <nav className="container mx-auto px-4 py-4 flex flex-col gap-4">
            <button
              onClick={() => { setLocation("/como-funciona"); setMobileMenuOpen(false); }}
              className="text-sm text-foreground hover:text-primary text-left"
            >
              Como Funciona
            </button>
            <button
              onClick={() => { setLocation("/planos"); setMobileMenuOpen(false); }}
              className="text-sm text-foreground hover:text-primary text-left"
            >
              Planos
            </button>
            <button
              onClick={() => { setLocation("/certificacoes"); setMobileMenuOpen(false); }}
              className="text-sm text-foreground hover:text-primary text-left"
            >
              Certificações
            </button>
            <button
              onClick={() => { setLocation("/depoimentos"); setMobileMenuOpen(false); }}
              className="text-sm text-foreground hover:text-primary text-left"
            >
              Depoimentos
            </button>
            <div className="flex gap-2 pt-2 flex-col">
              {isAuthenticated ? (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setLocation("/dashboard")}
                    className="border-border text-foreground hover:bg-secondary"
                  >
                    <User className="w-4 h-4 mr-2" />
                    {user?.name}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleLogout}
                    className="border-border text-foreground hover:bg-secondary"
                  >
                    <LogOut className="w-4 h-4 mr-2" />
                    Sair
                  </Button>
                </>
              ) : (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setLocation("/login")}
                  >
                    Entrar
                  </Button>
                  <Button
                    size="sm"
                    className="bg-primary hover:bg-primary/90"
                    onClick={() => setLocation("/register")}
                  >
                    Cadastro
                  </Button>
                </>
              )}
            </div>
          </nav>
        </div>
      )}
    </header>
  );
}
