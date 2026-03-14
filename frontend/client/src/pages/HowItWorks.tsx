import { ArrowRight, Package, Microscope, Zap, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Link } from 'wouter';

export default function HowItWorks() {
  const steps = [
    {
      number: '01',
      icon: Package,
      title: 'Ingestão',
      description: 'Envie seu ZIP ou cole a URL do GitHub. O AUDITX clona e mapeia toda a estrutura em segundos.',
      details: [
        'Suporta ZIP, GitHub, GitLab e Bitbucket',
        'Análise de estrutura automática',
        'Mapeamento de dependências'
      ]
    },
    {
      number: '02',
      icon: Microscope,
      title: 'Análise Cirúrgica',
      description: 'Motor estático examina cada arquivo — SQL injection, XSS, secrets expostos, dependências vulneráveis e mais.',
      details: [
        'Análise estática profunda',
        '+40 tipos de vulnerabilidades',
        'Detecção de padrões inseguros'
      ]
    },
    {
      number: '03',
      icon: Zap,
      title: 'Auto-Fix + Laudo',
      description: 'Correções são aplicadas automaticamente. Você recebe o projeto corrigido + laudo PDF com score certificado.',
      details: [
        'Patches automáticos aplicados',
        'Laudo PDF certificado',
        'Score 0-100 auditado'
      ]
    },
    {
      number: '04',
      icon: CheckCircle,
      title: 'Compartilhamento',
      description: 'Compartilhe o laudo com clientes via link verificável, e-mail ou QR Code. Transparência total.',
      details: [
        'Links públicos verificáveis',
        'Compartilhamento por e-mail',
        'QR Code com timestamp'
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-slate-50 to-white border-b border-border">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-4xl sm:text-5xl font-bold font-mono text-foreground mb-4">
              Como Funciona
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Processo automatizado em 4 etapas. Do upload ao laudo assinado. Sem configuração, sem agente instalado.
            </p>
          </div>
        </div>
      </section>

      {/* Steps Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
            {steps.map((step, index) => {
              const Icon = step.icon;
              return (
                <div key={index} className="relative">
                  {/* Step Card */}
                  <div className="bg-white border border-border rounded-lg p-8 hover:shadow-lg transition-shadow duration-300">
                    {/* Step Number */}
                    <div className="absolute -top-6 -left-6 w-12 h-12 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-bold text-lg font-mono">
                      {step.number}
                    </div>

                    {/* Icon */}
                    <div className="mb-6 mt-4">
                      <Icon className="w-12 h-12 text-primary" />
                    </div>

                    {/* Title */}
                    <h3 className="text-2xl font-bold font-mono text-foreground mb-3">
                      {step.title}
                    </h3>

                    {/* Description */}
                    <p className="text-muted-foreground mb-6">
                      {step.description}
                    </p>

                    {/* Details */}
                    <ul className="space-y-2">
                      {step.details.map((detail, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-sm text-muted-foreground">
                          <CheckCircle className="w-4 h-4 text-safe mt-0.5 flex-shrink-0" />
                          <span>{detail}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Arrow Connector */}
                  {index < steps.length - 1 && (
                    <div className="hidden md:flex absolute -right-8 top-1/2 transform -translate-y-1/2">
                      <ArrowRight className="w-6 h-6 text-primary" />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Timeline Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-slate-50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold font-mono text-foreground mb-12 text-center">
            Tempo Médio de Processamento
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white border border-border rounded-lg p-8 text-center">
              <div className="text-4xl font-bold text-primary font-mono mb-2">&lt;60s</div>
              <p className="text-muted-foreground">Ingestão e Mapeamento</p>
            </div>
            <div className="bg-white border border-border rounded-lg p-8 text-center">
              <div className="text-4xl font-bold text-primary font-mono mb-2">2-5m</div>
              <p className="text-muted-foreground">Análise Cirúrgica</p>
            </div>
            <div className="bg-white border border-border rounded-lg p-8 text-center">
              <div className="text-4xl font-bold text-primary font-mono mb-2">&lt;2h</div>
              <p className="text-muted-foreground">Laudo Completo</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Comparison */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold font-mono text-foreground mb-12 text-center">
            O que Detectamos
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {[
              { title: 'Segurança', items: ['SQL Injection', 'XSS & Injeção HTML', 'Secrets Expostos', 'Autenticação Fraca'] },
              { title: 'Dependências', items: ['CVEs Conhecidos', 'Pacotes Desatualizados', 'Licenças Problemáticas', 'Conflitos de Versão'] },
              { title: 'Performance', items: ['N+1 Queries', 'Loops Ineficientes', 'Memory Leaks', 'Bundle Size'] },
              { title: 'Qualidade', items: ['Code Duplication', 'Complexidade Ciclomática', 'Dead Code', 'Padrões Anti-pattern'] }
            ].map((category, idx) => (
              <div key={idx} className="bg-white border border-border rounded-lg p-8">
                <h3 className="text-xl font-bold font-mono text-foreground mb-4">
                  {category.title}
                </h3>
                <ul className="space-y-3">
                  {category.items.map((item, itemIdx) => (
                    <li key={itemIdx} className="flex items-center gap-3 text-muted-foreground">
                      <div className="w-2 h-2 bg-primary rounded-full" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-primary/10 to-primary/5 border-t border-border">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold font-mono text-foreground mb-6">
            Pronto para Auditar?
          </h2>
          <p className="text-lg text-muted-foreground mb-8">
            Comece com um diagnóstico gratuito. Sem cadastro, sem cartão de crédito.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/">
              <Button size="lg" variant="default">
                Auditar Agora
              </Button>
            </Link>
            <Link href="/planos">
              <Button size="lg" variant="outline">
                Ver Planos
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
