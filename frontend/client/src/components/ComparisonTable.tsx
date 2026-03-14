import { Check, X, Zap } from "lucide-react";

/**
 * AuditX Comparison Table
 * Design: Minimalismo Cirúrgico
 * - Comparação direta entre Manual, Tradicional e AuditX
 * - Destaque visual para a coluna AuditX
 */

const features = [
    {
        name: "Velocidade",
        manual: "7 a 15 dias úteis",
        traditional: "5 a 10 minutos",
        auditx: "Resultado em minutos",
        highlight: true,
    },
    {
        name: "Custo Médio",
        manual: "R$ 15.000 - R$ 30.000",
        traditional: "R$ 1.200 (Anual)",
        auditx: "A partir de R$ 99",
        highlight: true,
    },
    {
        name: "Precisão",
        manual: "Alta (Sujeita a erro)",
        traditional: "Baixa (Falsos Positivos)",
        auditx: "Extrema (IA + AST)",
        highlight: true,
    },
    {
        name: "Correção",
        manual: "Apenas aponta o erro",
        traditional: "Apenas aponta o erro",
        auditx: "Auto-Fix (Código Pronto)",
        highlight: true,
    },
    {
        name: "Disponibilidade",
        manual: "Horário comercial",
        traditional: "24/7",
        auditx: "24/7 + Instantânea",
        highlight: true,
    },
];

export default function ComparisonTable() {
    return (
        <section className="py-24 bg-background">
            <div className="container mx-auto px-4">
                <div className="text-center mb-16 animate-slideUp">
                    <h2 className="text-3xl md:text-5xl font-black text-foreground mb-4 tracking-tighter uppercase">
                        O Custo da Inércia
                    </h2>
                    <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
                        Não contratar a AuditX não é apenas uma escolha técnica, é uma escolha financeira. Veja a diferença.
                    </p>
                </div>

                <div className="max-w-5xl mx-auto overflow-hidden rounded-2xl border border-border shadow-2xl animate-slideUp">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-secondary/30">
                                    <th className="p-6 text-sm font-black uppercase tracking-widest text-muted-foreground border-b border-border">
                                        Característica
                                    </th>
                                    <th className="p-6 text-sm font-black uppercase tracking-widest text-muted-foreground border-b border-border">
                                        Auditoria Manual
                                    </th>
                                    <th className="p-6 text-sm font-black uppercase tracking-widest text-muted-foreground border-b border-border">
                                        Ferramentas Tradicionais
                                    </th>
                                    <th className="p-6 text-sm font-black uppercase tracking-widest text-primary border-b border-border bg-primary/5">
                                        <div className="flex items-center gap-2">
                                            <Zap className="w-4 h-4 fill-primary" />
                                            AuditX (IA + AST)
                                        </div>
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                {features.map((feature, i) => (
                                    <tr key={i} className="group hover:bg-secondary/10 transition-colors">
                                        <td className="p-6 text-sm font-bold text-foreground border-b border-border">
                                            {feature.name}
                                        </td>
                                        <td className="p-6 text-sm text-muted-foreground border-b border-border">
                                            {feature.manual}
                                        </td>
                                        <td className="p-6 text-sm text-muted-foreground border-b border-border">
                                            {feature.traditional}
                                        </td>
                                        <td className="p-6 text-sm font-bold text-foreground border-b border-border bg-primary/5">
                                            <span className="text-primary">{feature.auditx}</span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    <div className="bg-primary p-6 text-center">
                        <p className="text-white font-bold text-lg">
                            AuditX é até 150x mais barato e 10.000x mais rápido que auditorias tradicionais.
                        </p>
                    </div>
                </div>
            </div>
        </section>
    );
}
