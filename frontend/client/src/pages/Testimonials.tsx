import { useState } from 'react';
import { ChevronLeft, ChevronRight, Star } from 'lucide-react';
import { Button } from '@/components/ui/button';
import TestimonialCard from '@/components/TestimonialCard';
import { Link } from 'wouter';

export default function Testimonials() {
  const [currentIndex, setCurrentIndex] = useState(0);

  const testimonials = [
    {
      name: 'Carlos Silva',
      company: 'TechStart Solutions',
      role: 'CTO',
      avatar: 'CS',
      avatarImage: 'https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?auto=format&fit=crop&q=80&w=200&h=200',
      rating: 5,
      testimonial: 'O AUDITX identificou vulnerabilidades críticas que nosso time não havia detectado. O relatório foi tão detalhado que conseguimos corrigir tudo em poucas horas. Essencial para qualquer startup.',
      highlight: 'vulnerabilidades críticas'
    },
    {
      name: 'Marina Costa',
      company: 'FinTech Brasil',
      role: 'Head of Security',
      avatar: 'MC',
      avatarImage: 'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&q=80&w=200&h=200',
      rating: 5,
      testimonial: 'Para uma aplicação de pagamentos, segurança é tudo. O AUDITX nos deu a confiança de que nosso código está protegido contra as ameaças mais comuns. Recomendo para qualquer empresa que lida com dados sensíveis.',
      highlight: 'confiança de que nosso código está protegido'
    },
    {
      name: 'João Oliveira',
      company: 'E-commerce Plus',
      role: 'Developer Lead',
      avatar: 'JO',
      avatarImage: 'https://images.unsplash.com/photo-1544723795-3fb6469f5b39?auto=format&fit=crop&q=80&w=200&h=200',
      rating: 5,
      testimonial: 'Usamos o AUDITX antes de cada deploy em produção. O score certificado nos ajuda a comunicar qualidade aos stakeholders. O QR Code é perfeito para compartilhar com clientes.',
      highlight: 'score certificado'
    },
    {
      name: 'Ana Paula Gomes',
      company: 'Healthcare Digital',
      role: 'Engineering Manager',
      avatar: 'AG',
      avatarImage: 'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&q=80&w=200&h=200',
      rating: 5,
      testimonial: 'Cumprimento LGPD e HIPAA exige rigor. O AUDITX automatiza a detecção de problemas que poderiam resultar em multas pesadas. Investimento que se paga na primeira auditoria.',
      highlight: 'automatiza a detecção'
    },
    {
      name: 'Pedro Martins',
      company: 'SaaS Inovador',
      role: 'Founder',
      avatar: 'PM',
      avatarImage: 'https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?auto=format&fit=crop&q=80&w=200&h=200',
      rating: 5,
      testimonial: 'Como startup, não tínhamos orçamento para contratar especialistas em segurança. O AUDITX nos deu acesso a análise profissional por uma fração do custo. Mudou nosso jogo.',
      highlight: 'análise profissional'
    },
    {
      name: 'Fernanda Rocha',
      company: 'Enterprise Corp',
      role: 'VP Engineering',
      avatar: 'FR',
      avatarImage: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&q=80&w=200&h=200',
      rating: 5,
      testimonial: 'Escalabilidade é crítica para nós. O AUDITX detectou gargalos de performance que estavam impactando nossos usuários. O relatório foi usado para justificar refatoração urgente.',
      highlight: 'gargalos de performance'
    },
    {
      name: 'Lucas Ferreira',
      company: 'Mobile First Studio',
      role: 'Tech Lead',
      avatar: 'LF',
      avatarImage: 'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&q=80&w=200&h=200',
      rating: 5,
      testimonial: 'Trabalhar com múltiplas linguagens é desafiador. O AUDITX suporta tudo que usamos (Node, Python, Go) e fornece insights consistentes. Ferramenta indispensável.',
      highlight: 'suporta tudo que usamos'
    },
    {
      name: 'Beatriz Santos',
      company: 'Data Analytics Co',
      role: 'Security Officer',
      avatar: 'BS',
      avatarImage: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&q=80&w=200&h=200',
      rating: 5,
      testimonial: 'O certificado com QR Code é genial. Nossos clientes podem verificar a segurança do código de forma independente. Aumentou nossa credibilidade no mercado.',
      highlight: 'certificado com QR Code'
    }
  ];

  const itemsPerPage = 3;
  const totalPages = Math.ceil(testimonials.length / itemsPerPage);

  const currentTestimonials = testimonials.slice(
    currentIndex * itemsPerPage,
    (currentIndex + 1) * itemsPerPage
  );

  const handleNext = () => {
    setCurrentIndex((prev) => (prev + 1) % totalPages);
  };

  const handlePrev = () => {
    setCurrentIndex((prev) => (prev - 1 + totalPages) % totalPages);
  };

  const avgRating = (testimonials.reduce((sum, t) => sum + t.rating, 0) / testimonials.length).toFixed(1);

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-slate-50 to-white border-b border-border">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-4xl sm:text-5xl font-bold font-mono text-foreground mb-4">
              O que Nossos Clientes Dizem
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Empresas de todos os tamanhos confiam no AUDITX para proteger seu código.
            </p>
          </div>

          {/* Rating Summary */}
          <div className="flex justify-center items-center gap-4">
            <div className="flex gap-1">
              {Array.from({ length: 5 }).map((_, i) => (
                <Star
                  key={i}
                  className="w-5 h-5 fill-primary text-primary"
                />
              ))}
            </div>
            <span className="text-2xl font-bold text-foreground">{avgRating}</span>
            <span className="text-muted-foreground">baseado em {testimonials.length} avaliações</span>
          </div>
        </div>
      </section>

      {/* Testimonials Carousel */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          {/* Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
            {currentTestimonials.map((testimonial, idx) => (
              <TestimonialCard
                key={idx}
                {...testimonial}
              />
            ))}
          </div>

          {/* Carousel Controls */}
          <div className="flex justify-center items-center gap-4">
            <Button
              variant="outline"
              size="sm"
              onClick={handlePrev}
              className="border-border"
            >
              <ChevronLeft className="w-4 h-4" />
            </Button>

            <div className="flex gap-2">
              {Array.from({ length: totalPages }).map((_, i) => (
                <button
                  key={i}
                  onClick={() => setCurrentIndex(i)}
                  className={`w-2 h-2 rounded-full transition-colors ${
                    i === currentIndex ? 'bg-primary' : 'bg-border'
                  }`}
                />
              ))}
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={handleNext}
              className="border-border"
            >
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>

          {/* Page Indicator */}
          <div className="text-center mt-6 text-sm text-muted-foreground">
            Página {currentIndex + 1} de {totalPages}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-slate-50 border-y border-border">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="bg-white border border-border rounded-lg p-8 text-center">
              <div className="text-4xl font-bold text-primary font-mono mb-2">98%</div>
              <p className="text-muted-foreground">Taxa de Satisfação</p>
            </div>
            <div className="bg-white border border-border rounded-lg p-8 text-center">
              <div className="text-4xl font-bold text-primary font-mono mb-2">5.0</div>
              <p className="text-muted-foreground">Avaliação Média</p>
            </div>
            <div className="bg-white border border-border rounded-lg p-8 text-center">
              <div className="text-4xl font-bold text-primary font-mono mb-2">2.5k+</div>
              <p className="text-muted-foreground">Clientes Ativos</p>
            </div>
            <div className="bg-white border border-border rounded-lg p-8 text-center">
              <div className="text-4xl font-bold text-primary font-mono mb-2">47</div>
              <p className="text-muted-foreground">Países</p>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Case Studies */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold font-mono text-foreground mb-12 text-center">
            Histórias de Sucesso
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {[
              {
                title: 'Startup Reduz Tempo de Deploy em 60%',
                description: 'Uma startup de FinTech usou o AUDITX para automatizar verificações de segurança pré-deploy, reduzindo tempo de revisão de 4 horas para 1.5 horas.',
                metric: '60%',
                metricLabel: 'Redução de Tempo'
              },
              {
                title: 'Enterprise Evita Multa de Compliance',
                description: 'Uma empresa de healthcare detectou e corrigiu 23 vulnerabilidades críticas antes de uma auditoria de compliance, evitando multas potenciais de R$500k+.',
                metric: '23',
                metricLabel: 'Vulnerabilidades Fixadas'
              },
              {
                title: 'SaaS Aumenta Confiança de Clientes',
                description: 'Uma plataforma B2B começou a compartilhar certificados AUDITX com clientes, aumentando taxa de renovação de contrato em 35%.',
                metric: '35%',
                metricLabel: 'Aumento de Retenção'
              },
              {
                title: 'Agência Expande Serviços de Segurança',
                description: 'Uma agência de desenvolvimento usou AUDITX para oferecer auditorias de segurança como serviço, gerando R$150k em receita adicional no primeiro ano.',
                metric: 'R$150k',
                metricLabel: 'Receita Adicional'
              }
            ].map((caseStudy, idx) => (
              <div key={idx} className="bg-white border border-border rounded-lg p-8">
                <div className="mb-6">
                  <div className="text-3xl font-bold text-primary font-mono mb-2">
                    {caseStudy.metric}
                  </div>
                  <p className="text-sm text-muted-foreground font-medium">
                    {caseStudy.metricLabel}
                  </p>
                </div>
                <h3 className="text-xl font-bold text-foreground mb-3">
                  {caseStudy.title}
                </h3>
                <p className="text-muted-foreground">
                  {caseStudy.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-primary/10 to-primary/5 border-t border-border">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold font-mono text-foreground mb-6">
            Junte-se a Milhares de Empresas
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
