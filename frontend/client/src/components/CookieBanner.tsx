import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Shield, X } from "lucide-react";

export default function CookieBanner() {
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        const consent = localStorage.getItem("auditx_cookie_consent");
        if (!consent) {
            setIsVisible(true);
        }
    }, []);

    const acceptCookies = () => {
        localStorage.setItem("auditx_cookie_consent", "true");
        setIsVisible(false);
    };

    if (!isVisible) return null;

    return (
        <div className="fixed bottom-6 left-6 right-6 z-[100] animate-in fade-in slide-in-from-bottom-10 duration-700">
            <div className="max-w-4xl mx-auto bg-background/80 backdrop-blur-xl border border-primary/20 p-6 rounded-2xl shadow-2xl flex flex-col md:flex-row items-center gap-6">
                <div className="bg-primary/10 p-3 rounded-xl flex-shrink-0">
                    <Shield className="w-6 h-6 text-primary" />
                </div>

                <div className="flex-1 text-center md:text-left">
                    <p className="text-sm text-foreground font-medium mb-1">Privacidade e Transparência (LGPD)</p>
                    <p className="text-xs text-muted-foreground leading-relaxed">
                        Utilizamos apenas cookies essenciais para o funcionamento da plataforma e garantia de segurança. Seus dados de código são processados em ambiente isolado e <strong>deletados permanentemente</strong> após a emissão do laudo. Leia nossa <a href="/privacy" className="underline text-primary font-semibold">Política de Privacidade</a>.
                    </p>
                </div>

                <div className="flex items-center gap-3 w-full md:w-auto">
                    <Button
                        variant="outline"
                        size="sm"
                        className="flex-1 md:flex-none text-[10px] font-bold uppercase tracking-widest border-border"
                        onClick={() => setIsVisible(false)}
                    >
                        Configurar
                    </Button>
                    <Button
                        size="sm"
                        className="flex-1 md:flex-none bg-primary text-white text-[10px] font-bold uppercase tracking-widest"
                        onClick={acceptCookies}
                    >
                        Aceitar e Continuar
                    </Button>
                </div>

                <button
                    onClick={() => setIsVisible(false)}
                    className="absolute top-4 right-4 text-muted-foreground hover:text-foreground transition-colors"
                >
                    <X className="w-4 h-4" />
                </button>
            </div>
        </div>
    );
}
