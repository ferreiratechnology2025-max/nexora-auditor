import { useState } from "react";
import { useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { ShieldCheck, ChevronRight, Lock, ArrowLeft, CheckCircle2, Mail, Loader2 } from "lucide-react";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { toast } from "sonner";
import { api } from "@/lib/api";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const PLAN_LABELS: Record<string, string> = {
  laudo: "Laudo Completo de Segurança",
  correcao: "Laudo + Correção Automática",
  dev: "Plano Dev (Mensal)",
  pro: "Plano Pro (Mensal)",
  scale: "Plano Scale (Mensal)",
};

export default function Checkout() {
  const [, setLocation] = useLocation();
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [email, setEmail] = useState("");

  const params = new URLSearchParams(window.location.search);
  const auditId = params.get("auditId") || "AUD-UNICO";
  const price = params.get("price") || "119";
  const plan = params.get("plan") || "laudo";

  const handleBack = () => {
    if (window.history.length > 1) {
      window.history.back();
    } else {
      setLocation("/");
    }
  };

  const handlePayment = async () => {
    if (!EMAIL_RE.test(email.trim())) {
      toast.error("Insira um e-mail válido para receber o laudo.");
      return;
    }
    setIsProcessing(true);
    try {
      const result = await api.payment.create(auditId, plan, email.trim());
      if (result.init_point) {
        window.location.href = result.init_point;
      } else {
        throw new Error("Link de pagamento não gerado pelo servidor.");
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Erro ao criar pagamento";
      toast.error(msg);
      setIsProcessing(false);
    }
  };

  if (isSuccess) {
    return (
      <div className="min-h-screen flex flex-col bg-background">
        <Header />
        <main className="flex-1 flex items-center justify-center p-6">
          <div className="max-w-md w-full text-center space-y-8 animate-fadeIn">
            <div className="w-24 h-24 bg-safe/10 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle2 className="w-12 h-12 text-safe" />
            </div>
            <div className="space-y-2">
              <h1 className="text-3xl font-bold text-foreground">Acesso Liberado!</h1>
              <p className="text-muted-foreground">
                O pagamento do laudo <strong>{auditId}</strong> foi processado. Suas correções e certificados estão prontos para download.
              </p>
            </div>
            <Button
              size="lg"
              className="w-full bg-primary hover:bg-primary/90 text-white font-bold h-14"
              onClick={() => setLocation("/")}
            >
              Ver Meu Laudo Completo
              <ChevronRight className="ml-2 w-5 h-5" />
            </Button>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header />
      <main className="flex-1 py-12 md:py-20">
        <div className="container mx-auto px-4 max-w-2xl">

          <button
            onClick={handleBack}
            className="flex items-center gap-2 text-muted-foreground hover:text-foreground mb-8 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Voltar para o laudo
          </button>

          <div className="space-y-2 mb-8">
            <h1 className="text-3xl font-bold text-foreground font-mono">Finalizar Compra</h1>
            <p className="text-muted-foreground">
              Você será redirecionado para o Mercado Pago — escolha PIX, cartão ou boleto lá.
            </p>
          </div>

          {/* Resumo do Pedido */}
          <div className="bg-card border border-border rounded-xl p-8 mb-6 shadow-sm">
            <div className="flex items-center gap-2 mb-6 pb-4 border-b border-border">
              <ShieldCheck className="w-6 h-6 text-primary" />
              <h2 className="font-bold text-lg">Resumo do Pedido</h2>
            </div>

            <div className="space-y-3 mb-6">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">{PLAN_LABELS[plan] ?? "Laudo de Auditoria"}</span>
                <span className="font-semibold text-foreground">R$ {price},00</span>
              </div>
              <div className="flex justify-between text-xs font-mono">
                <span className="text-muted-foreground">ID da Auditoria</span>
                <span className="text-foreground truncate max-w-[180px]">{auditId}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Certificado Digital</span>
                <span className="text-safe font-bold">Incluso</span>
              </div>
              {(plan === "correcao") && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Auto-Fix (IA)</span>
                  <span className="text-safe font-bold">Incluso</span>
                </div>
              )}
            </div>

            <div className="flex justify-between items-baseline pt-4 border-t border-border">
              <span className="font-bold text-lg">Total</span>
              <span className="text-3xl font-black text-primary font-mono">R$ {price},00</span>
            </div>
          </div>

          {/* Email */}
          <div className="mb-6">
            <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-2">
              E-mail para receber o laudo
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handlePayment()}
                placeholder="seu@email.com"
                className="w-full pl-10 pr-4 py-3 border border-border rounded-xl bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
              />
            </div>
          </div>

          {/* CTA */}
          <Button
            className="w-full h-14 bg-primary hover:bg-primary/90 text-white font-black text-lg shadow-xl transition-all disabled:opacity-50"
            onClick={handlePayment}
            disabled={isProcessing}
          >
            {isProcessing ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Redirecionando para Mercado Pago...
              </>
            ) : (
              <>
                Confirmar e Pagar — R$ {price},00
                <ChevronRight className="ml-2 w-5 h-5" />
              </>
            )}
          </Button>

          <div className="flex items-center gap-3 mt-4 p-4 bg-secondary/50 border border-border rounded-lg">
            <Lock className="w-4 h-4 text-muted-foreground flex-shrink-0" />
            <p className="text-xs text-muted-foreground">
              Pagamento processado pelo Mercado Pago com criptografia SSL. Aceita PIX, cartão de crédito e boleto. Garantia de 7 dias.
            </p>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
