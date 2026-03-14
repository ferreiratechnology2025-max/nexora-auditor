/**
 * AUDITX Social Proof Section
 * Design: Minimalismo Cirúrgico
 * - Estatísticas de impacto
 * - Layout horizontal com separadores
 * - Tipografia clara e hierárquica
 */
import { Github, Gitlab, HardDrive } from "lucide-react";

export default function SocialProof() {
  const stats = [
    {
      value: "94%+",
      label: "Dos projetos têm pelo menos uma falha",
      highlight: true,
    },
    {
      value: "94%",
      label: "Dos projetos analisados têm falhas críticas",
    },
    {
      value: "+40",
      label: "Tipos de falhas detectados",
    },
    {
      value: "< 3 min",
      label: "Tempo médio de auditoria",
    },
  ];

  return (
    <section className="py-16 md:py-24 bg-secondary/30 border-y border-border overflow-hidden">
      <div className="container mx-auto px-4">
        {/* Trusted By / Ecosystem Logos */}
        <div className="mb-16 text-center">
          <p className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-8">
            Compatível com os principais ecossistemas
          </p>
          <div className="flex flex-wrap justify-center items-center gap-12 opacity-50 grayscale hover:grayscale-0 transition-all duration-500">
            <div className="flex items-center gap-2">
              <Github className="w-8 h-8" />
              <span className="text-xl font-bold">GitHub</span>
            </div>
            <div className="flex items-center gap-2">
              <Gitlab className="w-8 h-8 text-[#FC6D26]" />
              <span className="text-xl font-bold">GitLab</span>
            </div>
            <div className="flex items-center gap-2 text-blue-600">
              <HardDrive className="w-8 h-8" />
              <span className="text-xl font-bold text-foreground">Bitbucket</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xl font-bold">Azure DevOps</span>
            </div>
          </div>
        </div>

        {/* Statistics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 md:gap-12">
          {stats.map((stat, index) => (
            <div key={index} className="text-center">
              <div className={`text-3xl md:text-4xl font-bold mb-2 ${stat.highlight ? 'text-primary animate-pulse' : 'text-foreground'}`}>
                {stat.value}
              </div>
              <p className="text-sm md:text-base text-muted-foreground">
                {stat.label}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

