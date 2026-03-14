import { useState } from "react";
import { Button } from "@/components/ui/button";
import { AlertCircle, Code, Layout, Cpu, Check } from "lucide-react";

/**
 * AUDITX Dynamic Pricing Calculator
 * Design: Minimalismo Cirúrgico
 * - Exibição de métricas detectadas automaticamente
 * - Cálculo de preço baseado no diagnóstico real
 * - Recomendação de plano baseada na complexidade
 */

interface PricingTier {
  name: string;
  minSize: number;
  maxSize: number;
  basePrice: number;
  label: string;
}

const pricingTiers: PricingTier[] = [
  {
    name: "Padrão",
    minSize: 0,
    maxSize: 50,
    basePrice: 119,
    label: "Até 50MB",
  },
  {
    name: "Médio",
    minSize: 50,
    maxSize: 200,
    basePrice: 199,
    label: "50MB - 200MB",
  },
  {
    name: "Grande",
    minSize: 200,
    maxSize: 500,
    basePrice: 299,
    label: "+200MB",
  },
];

export default function DynamicPricingCalculator() {
  // Valores fixos baseados no diagnóstico do projeto (Simulação conforme solicitado)
  const projectSize = 30; // MB
  const linesOfCode = "5k";
  const complexity = 50; // %

  // Calcular preço baseado em tamanho e complexidade (Base: Plano Dev R$99 para 50MB)
  const calculatePrice = () => {
    let basePrice = 99; // Base para até 50MB

    if (projectSize > 150) {
      basePrice = 399;
    } else if (projectSize > 50) {
      basePrice = 199;
    }

    const complexityMultiplier = 1 + (complexity / 100) * 0.4; // Ajuste fino
    return Math.round(basePrice * complexityMultiplier);
  };

  const getRecommendedPlan = () => {
    return {
      name: "Plano Pro",
      price: 299,
      reason: "Para empresas com múltiplos deploys semanais.",
    };
  };

  const calculatedPrice = calculatePrice();
  const recommendedPlan = getRecommendedPlan();

  return (
    <section className="py-20 md:py-32 bg-secondary/30 border-y border-border">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-16 animate-slideUp">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4 font-mono uppercase tracking-tighter">
            Diagnóstico Confirmado
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Seu código foi analisado com sucesso. Selecione o modelo de investimento para desbloquear a solução.
          </p>
        </div>

        {/* Calculator Grid */}
        <div className="grid md:grid-cols-2 gap-12 max-w-5xl mx-auto">
          {/* Left: Auto-Detected Metrics */}
          <div className="space-y-6 animate-slideUp">
            <h3 className="text-xs font-black uppercase tracking-[0.2em] text-primary mb-6">Autopsia do Sistema</h3>

            <div className="grid gap-4">
              <div className="bg-card border border-border p-6 rounded-xl flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-primary/5 rounded-lg">
                    <Layout className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-foreground">Payload Sanitizado</p>
                    <p className="text-xs text-muted-foreground">Volume de arquivos</p>
                  </div>
                </div>
                <p className="text-xl font-black text-foreground">{projectSize}MB</p>
              </div>

              <div className="bg-card border border-border p-6 rounded-xl flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-primary/5 rounded-lg">
                    <Code className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-foreground">Escopo de Análise</p>
                    <p className="text-xs text-muted-foreground">Linhas totais</p>
                  </div>
                </div>
                <p className="text-xl font-black text-foreground uppercase">{linesOfCode}</p>
              </div>

              <div className="bg-card border border-border p-6 rounded-xl flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-primary/5 rounded-lg">
                    <Cpu className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-foreground">Complexidade Heurística</p>
                    <p className="text-xs text-muted-foreground">Grau de acoplamento</p>
                  </div>
                </div>
                <p className="text-xl font-black text-foreground">{complexity}%</p>
              </div>
            </div>

            <div className="bg-primary/5 border border-primary/10 rounded-xl p-6 flex gap-4">
              <AlertCircle className="w-6 h-6 text-primary flex-shrink-0" />
              <p className="text-xs text-muted-foreground leading-relaxed">
                Este diagnóstico é exclusivo para este repositório. O valor abaixo garante a correção total de todas as falhas detectadas na sessão atual.
              </p>
            </div>
          </div>

          {/* Right: Price Options */}
          <div className="space-y-6 animate-slideUp" style={{ animationDelay: "0.1s" }}>
            {/* Option 1: One-time Unlock */}
            <div className="bg-card border-2 border-primary rounded-xl p-8 relative overflow-hidden group">
              <div className="absolute top-0 right-0 bg-primary text-white text-[10px] font-bold px-3 py-1 rounded-bl-lg uppercase tracking-widest">
                Indicado hoje
              </div>
              <p className="text-xs font-black text-primary uppercase tracking-[0.2em] mb-4">Acesso Único</p>
              <div className="mb-6">
                <div className="flex items-baseline gap-1">
                  <span className="text-sm font-bold text-foreground align-top mt-1">R$</span>
                  <span className="text-6xl font-black text-foreground tracking-tighter">
                    {calculatedPrice}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground mt-2">Pagamento único para desbloqueio imediato</p>
              </div>

              <Button className="w-full bg-primary hover:bg-primary/90 text-white font-bold h-12 shadow-lg shadow-primary/20 transition-all text-base">
                Liberar Acesso Agora
              </Button>

              {/* Deliverables List */}
              <div className="mt-8 pt-8 border-t border-border/50">
                <ul className="grid grid-cols-1 gap-3">
                  {[
                    "Código corrigido em arquivo .ZIP",
                    "Laudo PDF certificado (5-10 páginas)",
                    "Link público verificável com QR Code",
                    "Acesso vitalício a este histórico",
                  ].map((item, i) => (
                    <li key={i} className="flex items-center gap-3 text-xs font-medium text-muted-foreground">
                      <Check className="w-4 h-4 text-safe flex-shrink-0" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Option 2: Subscription Upsell */}
            <div className="bg-foreground text-background border border-foreground rounded-xl p-8 transition-transform hover:scale-[1.02]">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <p className="text-xs font-black uppercase tracking-widest text-background/60 mb-1">Economia Recorrente</p>
                  <h3 className="text-xl font-bold">Assinar Plano Pro</h3>
                </div>
                <div className="bg-safe text-foreground text-[10px] font-black px-2 py-0.5 rounded uppercase">Melhor Valor</div>
              </div>

              <p className="text-sm text-background/80 mb-6">
                Audite repositórios ilimitados e pague somente <span className="text-safe font-bold">R${recommendedPlan.price}/mês</span>.
                Ideal para squads que deployam código diariamente.
              </p>

              <Button variant="outline" className="w-full bg-transparent border-background/20 text-background hover:bg-background hover:text-foreground font-bold h-12">
                Migrar para Assinatura
              </Button>
            </div>
          </div>
        </div>

        {/* Pricing Tiers Info */}
        <div className="bg-secondary/50 rounded-lg p-4 space-y-2">
          <p className="text-xs font-semibold text-foreground uppercase">
            Faixas de Preço
          </p>
          {pricingTiers.map((tier) => (
            <div key={tier.name} className="text-xs text-muted-foreground">
              <span className="font-medium text-foreground">{tier.name}:</span> {tier.label} — R${tier.basePrice}
            </div>
          ))}
        </div>
        {/* FAQ Section */}
        <div className="mt-16 max-w-2xl mx-auto">
          <h3 className="text-xl font-bold text-foreground mb-6 text-center">
            Perguntas Frequentes
          </h3>
          <div className="space-y-4">
            <details className="bg-card border border-border rounded-lg p-4 cursor-pointer group">
              <summary className="font-semibold text-foreground flex items-center justify-between">
                Como o preço é calculado?
                <span className="text-muted-foreground group-open:rotate-180 transition-transform">
                  ▼
                </span>
              </summary>
              <p className="text-sm text-muted-foreground mt-3">
                O preço base é determinado pelo tamanho do seu projeto. A complexidade do código e o volume de linhas também influenciam no esforço de análise e correção.
              </p>
            </details>

            <details className="bg-card border border-border rounded-lg p-4 cursor-pointer group">
              <summary className="font-semibold text-foreground flex items-center justify-between">
                Posso mudar de plano depois?
                <span className="text-muted-foreground group-open:rotate-180 transition-transform">
                  ▼
                </span>
              </summary>
              <p className="text-sm text-muted-foreground mt-3">
                Sim! Você pode fazer upgrade ou downgrade do seu plano a qualquer momento. As mudanças entram em vigor no próximo ciclo de faturamento.
              </p>
            </details>

            <details className="bg-card border border-border rounded-lg p-4 cursor-pointer group">
              <summary className="font-semibold text-foreground flex items-center justify-between">
                E se meu projeto for muito grande?
                <span className="text-muted-foreground group-open:rotate-180 transition-transform">
                  ▼
                </span>
              </summary>
              <p className="text-sm text-muted-foreground mt-3">
                Para projetos acima de 500MB, recomendamos entrar em contato conosco para um orçamento personalizado. Oferecemos soluções enterprise customizadas.
              </p>
            </details>
          </div>
        </div>
      </div>
    </section>
  );
}
