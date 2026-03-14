import { Quote, Star, ArrowRight } from "lucide-react";
import { Link } from "wouter";

export default function TestimonialSection() {
    const reviews = [
        {
            name: "Ricardo Mendes",
            role: "CTO @ TechStream",
            image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=200&h=200",
            quote: "O AUDITX reduziu nosso tempo de revisão de segurança de dias para segundos. O diagnóstico é assustadoramente preciso, e os patches sugeridos pela IA economizam horas de refatoração.",
            caseLink: "/depoimentos?case=techstream-auditx"
        },
        {
            name: "Ana Silveira",
            role: "Head of Security @ FintechOne",
            image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&q=80&w=200&h=200",
            quote: "Pela primeira vez temos uma ferramenta que não só aponta o erro, mas entrega a solução pronta para o deploy. É a peça que faltava no nosso pipeline DevSecOps.",
            caseLink: "/depoimentos?case=fintechone-devsecops"
        }
    ];

    return (
        <section className="py-20 md:py-32 bg-background border-t border-border">
            <div className="container mx-auto px-4">
                <h2 className="text-3xl font-black uppercase tracking-tighter text-center mb-16 italic">
                    Quem blinda o código com <span className="text-primary italic">AuditX</span>
                </h2>

                <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
                    {reviews.map((review, i) => (
                        <div key={i} className="bg-card border border-border rounded-3xl p-8 relative overflow-hidden shadow-xl group hover:border-primary/30 transition-all">
                            <div className="absolute top-4 right-4 text-primary/10">
                                <Quote className="w-12 h-12 rotate-180" />
                            </div>

                            <div className="flex gap-1 mb-6">
                                {[...Array(5)].map((_, i) => (
                                    <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                                ))}
                            </div>

                            <blockquote className="text-lg font-medium text-foreground mb-8 leading-relaxed italic">
                                "{review.quote}"
                            </blockquote>

                            <div className="flex items-center justify-between mt-auto border-t border-border pt-6">
                                <div className="flex items-center gap-4">
                                    <div className="w-12 h-12 rounded-xl overflow-hidden border-2 border-primary/20">
                                        <img
                                            src={review.image}
                                            alt={`${review.name} - ${review.role} validando a auditoria de código AuditX`}
                                            className="w-full h-full object-cover"
                                            width="200"
                                            height="200"
                                            loading="lazy"
                                        />
                                    </div>
                                    <div>
                                        <cite className="not-italic font-bold text-sm text-foreground block">{review.name}</cite>
                                        <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-widest">{review.role}</span>
                                    </div>
                                </div>
                                <Link href={review.caseLink} className="text-[10px] font-black uppercase tracking-widest text-primary flex items-center gap-1 hover:gap-2 transition-all">
                                    Ler Estudo de Caso <ArrowRight className="w-3 h-3" />
                                </Link>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
