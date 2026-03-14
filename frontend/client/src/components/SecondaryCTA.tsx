import { Button } from "@/components/ui/button";
import { ArrowRight, Shield } from "lucide-react";

export default function SecondaryCTA() {
    return (
        <section className="py-20 md:py-32 bg-primary relative overflow-hidden">
            {/* Visual elements */}
            <div className="absolute top-0 right-0 -translate-y-1/2 translate-x-1/2 w-96 h-96 bg-white/10 rounded-full blur-3xl"></div>
            <div className="absolute bottom-0 left-0 translate-y-1/2 -translate-x-1/2 w-96 h-96 bg-black/10 rounded-full blur-3xl"></div>

            <div className="container mx-auto px-4 relative z-10 text-center text-white">
                <div className="max-w-3xl mx-auto">
                    <Shield className="w-16 h-16 mx-auto mb-8 opacity-90" />
                    <h2 className="text-3xl md:text-5xl font-bold mb-6 leading-tight">
                        Pronto para levar seu código ao nível de produção?
                    </h2>
                    <p className="text-xl text-white/80 mb-10">
                        Junte-se a centenas de desenvolvedores que confiam na AUDITX para garantir segurança e performance sem fricção.
                    </p>

                    <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                        <Button
                            size="lg"
                            variant="secondary"
                            className="text-primary font-bold text-lg px-8 h-14 group"
                            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                        >
                            Iniciar Minha Autopsia Agora
                            <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                        </Button>
                        <p className="text-sm font-medium text-white/70">
                            Diagnóstico gratuito em 60s
                        </p>
                    </div>
                </div>
            </div>
        </section>
    );
}
