import { Check, AlertCircle, CreditCard, Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";

/**
 * AUDITX Subscription Management
 * Design: Minimalismo Cirúrgico
 * - Informações do plano atual
 * - Uso de auditorias
 * - Data de renovação
 * - Upgrade/Downgrade
 * - Histórico de faturas
 */

interface SubscriptionInfo {
  plan: string;
  price: number;
  period: string;
  status: string;
  renewalDate: string;
  auditsUsed: number;
  auditsLimit: number;
  uploadLimit: string;
  features: string[];
}

const currentSubscription: SubscriptionInfo = {
  plan: "Plano Pro",
  price: 299,
  period: "mês",
  status: "ativo",
  renewalDate: "2026-04-11",
  auditsUsed: 12,
  auditsLimit: 20,
  uploadLimit: "200MB",
  features: [
    "Até 20 auditorias/mês",
    "Limite de 200MB por upload",
    "10 Auto-Fixes automáticos",
    "Certificado + Relatório Técnico",
    "Análise de Dependências (Em breve)",
    "Suporte por email",
  ],
};

const availablePlans = [
  {
    name: "Plano Dev",
    price: 99,
    description: "Para freelancers",
  },
  {
    name: "Plano Scale",
    price: 899,
    description: "Para enterprise",
  },
];

const invoices = [
  {
    id: "INV-001",
    date: "2026-02-11",
    amount: 299,
    status: "pago",
  },
  {
    id: "INV-002",
    date: "2026-01-11",
    amount: 299,
    status: "pago",
  },
  {
    id: "INV-003",
    date: "2025-12-11",
    amount: 99,
    status: "pago",
  },
];

export default function SubscriptionManagement() {
  const usagePercentage =
    (currentSubscription.auditsUsed / currentSubscription.auditsLimit) * 100;

  return (
    <div className="space-y-8">
      {/* Current Subscription */}
      <div>
        <h2 className="text-2xl font-bold text-foreground mb-6">
          Minha Assinatura
        </h2>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Plan Card */}
          <div className="bg-card border-2 border-primary rounded-lg p-8">
            <div className="flex items-start justify-between mb-6">
              <div>
                <h3 className="text-2xl font-bold text-foreground">
                  {currentSubscription.plan}
                </h3>
                <p className="text-sm text-muted-foreground mt-1">
                  Ativo desde 2025-12-11
                </p>
              </div>
              <span className="px-3 py-1 rounded-full bg-safe/10 text-safe text-xs font-semibold">
                Ativo
              </span>
            </div>

            <div className="mb-6">
              <div className="flex items-baseline gap-1 mb-2">
                <span className="text-4xl font-bold text-primary">
                  R${currentSubscription.price}
                </span>
                <span className="text-muted-foreground">
                  /{currentSubscription.period}
                </span>
              </div>
              <p className="text-sm text-muted-foreground">
                Próxima renovação em{" "}
                {new Date(currentSubscription.renewalDate).toLocaleDateString(
                  "pt-BR"
                )}
              </p>
            </div>

            {/* Usage Bar */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-foreground">
                  Auditorias Utilizadas
                </span>
                <span className="text-sm text-muted-foreground">
                  {currentSubscription.auditsUsed}/{currentSubscription.auditsLimit}
                </span>
              </div>
              <div className="w-full bg-secondary rounded-full h-2">
                <div
                  className="bg-primary h-2 rounded-full transition-all"
                  style={{ width: `${usagePercentage}%` }}
                ></div>
              </div>
            </div>

            {/* Features */}
            <div className="space-y-2 mb-6 pb-6 border-b border-border">
              {currentSubscription.features.map((feature, index) => (
                <div key={index} className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-safe flex-shrink-0" />
                  <span className="text-sm text-foreground">{feature}</span>
                </div>
              ))}
            </div>

            {/* Actions */}
            <div className="flex gap-2">
              <Button variant="outline" className="flex-1">
                Gerenciar Pagamento
              </Button>
              <Button className="flex-1 bg-primary hover:bg-primary/90">
                Fazer Upgrade
              </Button>
            </div>
          </div>

          {/* Other Plans */}
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-foreground mb-4">
              Outros Planos
            </h3>
            {availablePlans.map((plan) => (
              <div
                key={plan.name}
                className="bg-card border border-border rounded-lg p-4 flex items-center justify-between"
              >
                <div>
                  <p className="font-semibold text-foreground">{plan.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {plan.description}
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-bold text-primary">R${plan.price}</p>
                  <Button
                    variant="outline"
                    size="sm"
                    className="mt-2 border-primary text-primary hover:bg-primary/10"
                  >
                    Mudar
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Billing Info */}
      <div>
        <h3 className="text-xl font-bold text-foreground mb-4">
          Informações de Faturamento
        </h3>
        <div className="bg-card border border-border rounded-lg p-6">
          <div className="grid md:grid-cols-3 gap-6 mb-6">
            <div className="flex items-start gap-4">
              <CreditCard className="w-5 h-5 text-primary flex-shrink-0 mt-1" />
              <div>
                <p className="text-sm text-muted-foreground">
                  Método de Pagamento
                </p>
                <p className="font-semibold text-foreground">Cartão •••• 4242</p>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <Calendar className="w-5 h-5 text-primary flex-shrink-0 mt-1" />
              <div>
                <p className="text-sm text-muted-foreground">Próximo Pagamento</p>
                <p className="font-semibold text-foreground">
                  {new Date(currentSubscription.renewalDate).toLocaleDateString(
                    "pt-BR"
                  )}
                </p>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <AlertCircle className="w-5 h-5 text-primary flex-shrink-0 mt-1" />
              <div>
                <p className="text-sm text-muted-foreground">Status</p>
                <p className="font-semibold text-safe">Pagamento em Dia</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Invoices */}
      <div>
        <h3 className="text-xl font-bold text-foreground mb-4">
          Histórico de Faturas
        </h3>
        <div className="bg-card border border-border rounded-lg overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border bg-secondary/30">
                <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">
                  ID da Fatura
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">
                  Data
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">
                  Valor
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">
                  Status
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">
                  Ação
                </th>
              </tr>
            </thead>
            <tbody>
              {invoices.map((invoice) => (
                <tr
                  key={invoice.id}
                  className="border-b border-border hover:bg-secondary/20 transition-colors"
                >
                  <td className="px-6 py-4 text-sm font-semibold text-foreground">
                    {invoice.id}
                  </td>
                  <td className="px-6 py-4 text-sm text-foreground">
                    {new Date(invoice.date).toLocaleDateString("pt-BR")}
                  </td>
                  <td className="px-6 py-4 text-sm font-semibold text-foreground">
                    R${invoice.amount}
                  </td>
                  <td className="px-6 py-4">
                    <span className="px-3 py-1 rounded-full bg-safe/10 text-safe text-xs font-semibold">
                      {invoice.status === "pago" ? "Pago" : "Pendente"}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-primary hover:bg-primary/10"
                    >
                      Baixar
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
