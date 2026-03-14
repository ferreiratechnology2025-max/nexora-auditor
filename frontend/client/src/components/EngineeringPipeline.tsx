import { Cpu, Share2, MessageSquare, ShieldCheck } from "lucide-react";

/**
 * AuditX Engineering Pipeline
 * Design: Minimalismo Cirúrgico
 * - Explicação visual do pipeline de análise com IA
 */

const steps = [
    {
        title: "Decomposição (AST)",
        description: "Quebramos seu código em uma árvore lógica para entender o fluxo completo de dados e dependências profundas.",
        icon: <Share2 className="w-6 h-6" />,
    },
    {
        title: "Conselho de Inteligência",
        description: "Aplicamos análise profunda com múltiplas camadas de detecção.",
        icon: <Cpu className="w-6 h-6" />,
    },
    {
        title: "Validação Cruzada",
        description: "Validação cruzada elimina falsos positivos com regras contextuais.",
        icon: <MessageSquare className="w-6 h-6" />,
    },
    {
        title: "Engenharia de Refatoração",
        description: "Motor de correção gera o patch validado por análise de sintaxe.",
        icon: <ShieldCheck className="w-6 h-6" />,
    },
];

export default function EngineeringPipeline() {
    return (
        <section className="py-24 bg-secondary/20">
            <div className="container mx-auto px-4">
                <div className="text-center mb-16 animate-slideUp">
                    <h2 className="text-3xl md:text-5xl font-black text-foreground mb-4 tracking-tighter uppercase">
                        O Cérebro AuditX
                    </h2>
                    <p className="text-muted-foreground text-lg max-w-2xl mx-auto uppercase tracking-widest text-xs font-bold">
                        Como o pipeline de análise com IA funciona
                    </p>
                </div>

                <div className="grid md:grid-cols-4 gap-8 max-w-6xl mx-auto">
                    {steps.map((step, i) => (
                        <div key={i} className="relative group animate-slideUp" style={{ animationDelay: `${i * 0.1}s` }}>
                            {/* Connector line for desktop */}
                            {i < steps.length - 1 && (
                                <div className="hidden md:block absolute top-10 left-[60%] w-full h-[2px] bg-gradient-to-r from-primary/30 to-transparent z-0" />
                            )}

                            <div className="relative z-10 bg-card border border-border p-8 rounded-2xl group-hover:border-primary/50 transition-all group-hover:shadow-xl h-full">
                                <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center text-primary mb-6 group-hover:scale-110 transition-transform">
                                    {step.icon}
                                </div>
                                <h3 className="text-xl font-black text-foreground mb-3 uppercase tracking-tighter">
                                    {step.title}
                                </h3>
                                <p className="text-muted-foreground text-sm leading-relaxed italic">
                                    "{step.description}"
                                </p>

                                <div className="absolute top-4 right-4 text-4xl font-black text-foreground/5 pointer-events-none">
                                    0{i + 1}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
