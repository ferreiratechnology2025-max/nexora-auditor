import { Check, X } from "lucide-react";
import { Button } from "@/components/ui/button";

/**
 * AUDITX Plans Comparison Table
 * Design: Minimalismo Cirúrgico
 * - Tabela comparativa com 3 planos (Dev, Pro, Scale)
 * - Destaque visual para o plano recomendado (Pro)
 * - Features com ícones de check/x
 * - CTA para cada plano
 */

interface Plan {
  id: string;
  name: string;
  price: number;
  period: string;
  description: string;
  profile: string;
  recommended?: boolean;
  features: {
    name: string;
    included: boolean;
  }[];
  cta: string;
}

const plans: Plan[] = [
  {
    id: "dev",
    name: "Plano Dev",
    price: 99,
    period: "mês",
    description: "Para freelancers e desenvolvedores independentes",
    profile: "Freelancers",
    features: [
      { name: "Até 5 auditorias/mês", included: true },
      { name: "Limite de 50MB por upload", included: true },
      { name: "Sugestões de correção em texto", included: true },
      { name: "Certificado com QR Code", included: true },
      { name: "10 Auto-Fixes automáticos", included: false },
      { name: "Integração CI/CD", included: false },
      { name: "Suporte prioritário", included: false },
    ],
    cta: "Começar com Dev",
  },
  {
    id: "pro",
    name: "Plano Pro",
    price: 299,
    period: "mês",
    description: "Para startups e agências em crescimento",
    profile: "Startups / Agências",
    recommended: true,
    features: [
      { name: "Até 20 auditorias/mês", included: true },
      { name: "Limite de 200MB por upload", included: true },
      { name: "10 Auto-Fixes automáticos", included: true },
      { name: "Certificado + Relatório Técnico", included: true },
      { name: "Análise de Dependências (Em breve)", included: true },
      { name: "Suporte por email", included: true },
      { name: "Integração CI/CD", included: false },
    ],
    cta: "Escolher Pro",
  },
  {
    id: "scale",
    name: "Plano Scale",
    price: 899,
    period: "mês",
    description: "Para empresas e software houses",
    profile: "Enterprise / Software Houses",
    features: [
      { name: "Auditorias ilimitadas", included: true },
      { name: "Limite de 1GB por upload", included: true },
      { name: "Auto-Fixes ilimitados", included: true },
      { name: "Certificado + Integração CI/CD", included: true },
      { name: "Análise de Dependências Avançada (Em breve)", included: true },
      { name: "Suporte prioritário 24/7", included: true },
      { name: "Gestor de conta dedicado", included: true },
    ],
    cta: "Contatar Sales",
  },
];

interface PlansComparisonProps {
  onSelectPlan?: (planId: string) => void;
}

export default function PlansComparison({ onSelectPlan }: PlansComparisonProps) {
  return (
    <section className="py-20 md:py-32 bg-background">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-16 animate-slideUp">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            Escolha sua autopsia
          </h2>
          <p className="text-lg text-muted-foreground">
            Diagnóstico gratuito. Pague pelo laudo que precisa.
          </p>
        </div>

        {/* Plans Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          {plans.map((plan, index) => (
            <div
              key={plan.id}
              className={`relative border rounded-lg transition-all animate-fadeIn ${
                plan.recommended
                  ? "border-primary shadow-xl md:scale-105 bg-primary/5"
                  : "border-border bg-card hover:shadow-lg"
              }`}
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              {/* Recommended Badge */}
              {plan.recommended && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <span className="bg-primary text-white px-4 py-1 rounded-full text-sm font-semibold">
                    Recomendado
                  </span>
                </div>
              )}

              <div className="p-8">
                {/* Plan Name */}
                <h3 className="text-2xl font-bold text-foreground mb-2">
                  {plan.name}
                </h3>
                <p className="text-sm text-muted-foreground mb-4">
                  {plan.profile}
                </p>

                {/* Price */}
                <div className="mb-6">
                  <div className="flex items-baseline gap-1">
                    <span className="text-4xl font-bold text-primary">
                      R${plan.price}
                    </span>
                    <span className="text-muted-foreground">/{plan.period}</span>
                  </div>
                  <p className="text-sm text-muted-foreground mt-2">
                    {plan.description}
                  </p>
                </div>

                {/* CTA Button */}
                <Button
                  onClick={() => onSelectPlan?.(plan.id)}
                  className={`w-full mb-8 ${
                    plan.recommended
                      ? "bg-primary hover:bg-primary/90 text-white"
                      : "border border-primary text-primary hover:bg-primary/10"
                  }`}
                  variant={plan.recommended ? "default" : "outline"}
                >
                  {plan.cta}
                </Button>

                {/* Features List */}
                <div className="space-y-3 border-t border-border pt-6">
                  {plan.features.map((feature, featureIndex) => (
                    <div key={featureIndex} className="flex items-start gap-3">
                      {feature.included ? (
                        <Check className="w-5 h-5 text-safe flex-shrink-0 mt-0.5" />
                      ) : (
                        <X className="w-5 h-5 text-muted-foreground flex-shrink-0 mt-0.5" />
                      )}
                      <span
                        className={`text-sm ${
                          feature.included
                            ? "text-foreground"
                            : "text-muted-foreground line-through"
                        }`}
                      >
                        {feature.name}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Additional Info */}
        <div className="bg-secondary/30 border border-border rounded-lg p-8 text-center animate-slideUp">
          <p className="text-foreground mb-4">
            <strong>Não tem certeza qual plano escolher?</strong>
          </p>
          <p className="text-muted-foreground">
            Comece com o Diagnóstico Gratuito. Você verá exatamente o que precisa e qual plano se adequa melhor ao seu projeto.
          </p>
        </div>
      </div>
    </section>
  );
}
