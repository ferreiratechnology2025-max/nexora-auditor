import { AlertTriangle, Lock, Shield, Zap, Code2, TrendingDown } from "lucide-react";

/**
 * AUDITX Coverage Section
 * Design: Minimalismo Cirúrgico
 * - Cards com ícones representando tipos de vulnerabilidades
 * - Layout em grid responsivo
 * - Cores de severidade integradas
 */
export default function CoverageSection() {
  const vulnerabilities = [
    {
      icon: AlertTriangle,
      title: "SQL Injection",
      description: "Queries não parametrizadas que expõem seu banco de dados a ataques de extração.",
      color: "text-critical",
    },
    {
      icon: Lock,
      title: "Secrets Expostos",
      description: "API keys, tokens e senhas hardcoded em código-fonte ou arquivos de configuração.",
      color: "text-critical",
    },
    {
      icon: Code2,
      title: "XSS & Injeção HTML",
      description: "Inputs não sanitizados que permitem execução de scripts maliciosos.",
      color: "text-warning",
    },
    {
      icon: Shield,
      title: "Dependências Vulneráveis",
      description: "Pacotes desatualizados com CVEs conhecidos que colocam sua aplicação em risco.",
      color: "text-critical",
    },
    {
      icon: Zap,
      title: "Gargalos de Performance",
      description: "N+1 queries, loops ineficientes e operações bloqueantes que degradam a UX.",
      color: "text-warning",
    },
    {
      icon: TrendingDown,
      title: "Certificado de Qualidade",
      description: "Score 0–100 auditado, com QR Code verificável e timestamp para seus clientes.",
      color: "text-safe",
    },
  ];

  return (
    <section id="cobertura" className="py-20 md:py-32 bg-background">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            O que a autopsia revela
          </h2>
          <p className="text-lg text-muted-foreground">
            Análise estática profunda em Python, JavaScript, TypeScript, PHP, Java e mais.
            <span className="block mt-2 font-medium text-primary/80">
              Suporte nativo para React, Next.js, Node.js, Laravel, Django e Spring Boot.
            </span>
          </p>
        </div>

        {/* Grid de Vulnerabilidades */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {vulnerabilities.map((vuln, index) => {
            const Icon = vuln.icon;
            return (
              <div
                key={index}
                className="p-6 border border-border rounded-lg bg-card hover:shadow-lg transition-shadow animate-fadeIn"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <Icon className={`w-8 h-8 mb-4 ${vuln.color}`} />
                <h3 className="text-lg font-semibold text-foreground mb-2">
                  {vuln.title}
                </h3>
                <p className="text-sm text-muted-foreground">
                  {vuln.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
