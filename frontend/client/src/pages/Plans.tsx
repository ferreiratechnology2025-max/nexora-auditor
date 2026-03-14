import Header from "@/components/Header";
import Footer from "@/components/Footer";
import PlansComparison from "@/components/PlansComparison";
import DynamicPricingCalculator from "@/components/DynamicPricingCalculator";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import { useLocation } from "wouter";

/**
 * AUDITX Plans Page
 * Design: Minimalismo Cirúrgico
 * - Tabela comparativa de planos
 * - Calculadora de preços dinâmica
 * - CTAs para seleção de plano
 */
export default function Plans() {
  const [, setLocation] = useLocation();

  const handleSelectPlan = (planId: string) => {
    if (planId === "scale") {
      window.location.href = "mailto:suporte@api-plataforma.com?subject=Plano Scale - AuditX";
      return;
    }
    const prices: Record<string, number> = { dev: 99, pro: 299 };
    const price = prices[planId] ?? 99;
    setLocation(`/checkout?plan=${planId}&price=${price}`);
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header />
      
      <main className="flex-1">
        {/* Hero Section */}
        <section className="py-12 md:py-16 bg-secondary/30 border-b border-border">
          <div className="container mx-auto px-4">
            <button
              onClick={() => setLocation("/")}
              className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors mb-6"
            >
              <ArrowLeft className="w-5 h-5" />
              Voltar para Home
            </button>
            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
              Planos de Auditoria
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl">
              Escolha o plano que melhor se adequa ao seu projeto. Todos incluem diagnóstico gratuito e suporte técnico.
            </p>
          </div>
        </section>

        {/* Plans Comparison */}
        <PlansComparison onSelectPlan={handleSelectPlan} />

        {/* Acesso Único */}
        <section className="py-12 bg-secondary/20 border-y border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-3xl mx-auto bg-card border-2 border-primary rounded-2xl p-8 shadow-xl md:flex md:items-center md:justify-between gap-8">
              <div>
                <p className="text-xs font-black uppercase tracking-[0.3em] text-primary mb-2">Acesso Único</p>
                <h3 className="text-3xl font-bold text-foreground mb-2">Laudo certificado em minutos</h3>
                <p className="text-muted-foreground">Ideal para uma única entrega ou POC. Mesmo rigor do Plano Pro, sem assinatura.</p>
              </div>
              <div className="text-center md:text-right">
                <div className="text-4xl font-black text-primary">R$ 119</div>
                <p className="text-xs uppercase tracking-widest text-muted-foreground mb-4">pagamento único</p>
                <Button className="bg-primary hover:bg-primary/90 text-white w-full md:w-auto" onClick={() => setLocation('/checkout?plan=laudo&price=119&auditId=AUD-UNICO')}>
                  Desbloquear meu laudo agora
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* Dynamic Pricing Calculator */}
        <DynamicPricingCalculator />

        {/* CTA Section */}
        <section className="py-16 md:py-24 bg-background">
          <div className="container mx-auto px-4 text-center max-w-2xl">
            <h2 className="text-3xl font-bold text-foreground mb-4">
              Ainda tem dúvidas?
            </h2>
            <p className="text-lg text-muted-foreground mb-8">
              Entre em contato com nosso time de vendas. Estamos aqui para ajudar você a escolher o plano perfeito.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                variant="outline"
                className="border-primary text-primary hover:bg-primary/10"
              >
                Enviar Email
              </Button>
              <Button className="bg-primary hover:bg-primary/90 text-white">
                Agendar Demo
              </Button>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
