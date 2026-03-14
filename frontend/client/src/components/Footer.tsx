import { Shield } from "lucide-react";
import { Link } from "wouter";
import { Button } from "@/components/ui/button";
import { useState } from "react";

/**
 * AUDITX Footer
 * Design: Minimalismo Cirúrgico
 * - Links institucionais
 * - Selos de segurança
 * - Informações de contato
 */
export default function Footer() {
  const [guideSent, setGuideSent] = useState(false);
  const handleGuide = () => {
    setGuideSent(true);
    setTimeout(() => setGuideSent(false), 4000);
  };

  return (
    <footer className="bg-card border-t border-border">
      <div className="container mx-auto px-4 py-16 border-b border-border">
        <div className="max-w-4xl mx-auto flex flex-col md:flex-row items-center justify-between gap-8 bg-primary/5 rounded-3xl p-8 border border-primary/10">
          <div className="text-left">
            <h3 className="text-lg font-bold text-foreground mb-2">Não quer auditar agora?</h3>
            <p className="text-sm text-muted-foreground">Receba nosso <strong>Guia OWASP 2026</strong> para Blindagem de Código diretamente no seu e-mail.</p>
          </div>
          <div className="flex w-full md:w-auto gap-2">
            <input
              type="email"
              placeholder="seu@email.com"
              className="bg-background border border-border rounded-xl px-4 py-2 text-sm outline-none focus:ring-2 ring-primary/20 w-full md:w-64"
            />
            <Button size="sm" className="bg-primary text-white font-bold whitespace-nowrap" onClick={handleGuide}>Me enviar o guia</Button>
          </div>
          {guideSent && (
            <p className="text-xs text-safe font-semibold mt-2 md:mt-0">Guia enviado! Verifique seu e-mail em instantes.</p>
          )}
        </div>
      </div>

      <div className="container mx-auto px-4 py-12">
        <div className="grid md:grid-cols-4 gap-8 mb-8">
          {/* Sobre */}
          <div>
            <h4 className="font-semibold text-foreground mb-4">AUDITX</h4>
            <p className="text-sm text-muted-foreground mb-4">
              Autopsia Digital de Código — Detecte vulnerabilidades em segundos.
            </p>
            <div className="flex items-center gap-2 text-[10px] font-bold text-safe uppercase tracking-widest bg-safe/10 px-3 py-1 rounded-full w-fit">
              <Shield className="w-3 h-3" /> Data Safe & Purged
            </div>
          </div>

          {/* Produto */}
          <div>
            <h4 className="font-semibold text-foreground mb-4">Produto</h4>
            <ul className="space-y-2">
              <li>
                <Link href="/como-funciona" className="text-sm text-muted-foreground hover:text-foreground transition-colors cursor-pointer">
                  Como Funciona
                </Link>
              </li>
              <li>
                <Link href="/planos" className="text-sm text-muted-foreground hover:text-foreground transition-colors cursor-pointer">
                  Planos
                </Link>
              </li>
              <li>
                <Link href="/certificacoes" className="text-sm text-muted-foreground hover:text-foreground transition-colors cursor-pointer">
                  Certificações
                </Link>
              </li>
              <li>
                <Link href="/depoimentos" className="text-sm text-muted-foreground hover:text-foreground transition-colors cursor-pointer">
                  Depoimentos
                </Link>
              </li>
            </ul>
          </div>

          {/* Empresa */}
          <div>
            <h4 className="font-semibold text-foreground mb-4">Empresa</h4>
            <ul className="space-y-2">
              <li>
                <Link href="/como-funciona" className="text-sm text-muted-foreground hover:text-foreground transition-colors cursor-pointer">
                  Sobre Nós
                </Link>
              </li>
              <li>
                <Link href="/depoimentos" className="text-sm text-muted-foreground hover:text-foreground transition-colors cursor-pointer">
                  Blog
                </Link>
              </li>
              <li>
                <a href="mailto:contato@auditx.ai" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  Contato
                </a>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className="font-semibold text-foreground mb-4">Legal</h4>
            <ul className="space-y-2">
              <li>
                <a href="/privacy" target="_blank" rel="noopener" className="text-sm text-muted-foreground hover:text-foreground transition-colors cursor-pointer">
                  Privacidade (LGPD)
                </a>
              </li>
              <li>
                <a href="/privacy#terms" target="_blank" rel="noopener" className="text-sm text-muted-foreground hover:text-foreground transition-colors cursor-pointer">
                  Termos de Serviço
                </a>
              </li>
              <li>
                <Link href="/como-funciona" className="text-sm text-muted-foreground hover:text-foreground transition-colors cursor-pointer">
                  Segurança
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-border pt-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex flex-wrap items-center gap-6">
              <div className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-primary" />
                <span className="text-sm text-muted-foreground">
                  OWASP Compliant
                </span>
              </div>
              <div className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-primary" />
                <span className="text-sm text-muted-foreground">
                  ISO 27001 Certified
                </span>
              </div>
            </div>

            <div className="text-center md:text-right">
              <p className="text-sm text-muted-foreground">
                © 2026 AUDITX. Todos os direitos reservados.
              </p>
              <p className="text-[10px] text-muted-foreground mt-1">
                Seu código é deletado permanentemente após a análise (Compliance LGPD).
              </p>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
