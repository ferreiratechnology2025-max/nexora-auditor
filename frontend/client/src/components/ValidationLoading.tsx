import { useEffect, useState } from "react";
import { Shield, ShieldAlert, ShieldCheck, Database, Lock, Search, FileText } from "lucide-react";

interface ValidationLoadingProps {
    onComplete?: () => void;
}

export default function ValidationLoading({ onComplete }: ValidationLoadingProps) {
    const [step, setStep] = useState(0);
    const [progress, setProgress] = useState(0);

    const steps = [
        { label: "[DEBUG] Construindo Árvore de Sintaxe Abstrata (AST)...", icon: Lock, color: "text-blue-500" },
        { label: "[AI] Consultando Consenso de 9 IAs...", icon: Database, color: "text-indigo-500" },
        { label: "[SECURITY] Verificando vulnerabilidades OWASP Top 10...", icon: Search, color: "text-amber-500" },
        { label: "[TRACE] Procurando segredos hardcoded...", icon: ShieldAlert, color: "text-red-500" },
        { label: "[RASP] Avaliando rotas críticas em runtime...", icon: Shield, color: "text-primary" },
        { label: "[REPORT] Gerando laudo técnico e diffs...", icon: FileText, color: "text-emerald-500" },
        { label: "Certificado validado com sucesso!", icon: ShieldCheck, color: "text-safe" },
    ];

    useEffect(() => {
        const totalSteps = steps.length;
        const interval = setInterval(() => {
            setStep((prev) => {
                if (prev < totalSteps - 1) return prev + 1;
                clearInterval(interval);
                return prev;
            });
        }, 400);

        const progressInterval = setInterval(() => {
            setProgress((prev) => {
                if (prev < 100) return prev + 1.5;
                clearInterval(progressInterval);
                return 100;
            });
        }, 30);

        return () => {
            clearInterval(interval);
            clearInterval(progressInterval);
        };
    }, []);

    const CurrentIcon = steps[step].icon;

    return (
        <div className="fixed inset-0 z-50 bg-background/95 backdrop-blur-md flex flex-col items-center justify-center p-6 text-center">
            {/* Visual background elements */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-20">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-primary/20 rounded-full blur-[120px] animate-pulse"></div>
                <div className="absolute -top-24 -left-24 w-96 h-96 bg-blue-500/10 rounded-full blur-[100px]"></div>
                <div className="absolute -bottom-24 -right-24 w-96 h-96 bg-emerald-500/10 rounded-full blur-[100px]"></div>
            </div>

            <div className="max-w-xl w-full relative z-10">
                {/* Main Loading Visual */}
                <div className="relative w-32 h-32 mx-auto mb-12">
                    {/* Pulsing rings */}
                    <div className="absolute inset-0 border-4 border-primary/20 rounded-full animate-ping"></div>
                    <div className="absolute inset-2 border-2 border-primary/40 rounded-full animate-pulse"></div>

                    {/* Central Icon container */}
                    <div className="absolute inset-0 flex items-center justify-center bg-background rounded-full border border-border shadow-2xl">
                        <CurrentIcon className={`w-12 h-12 transition-all duration-300 ${steps[step].color} ${step < steps.length - 1 ? 'animate-bounce-subtle' : 'scale-110'}`} />
                    </div>

                    {/* Scanning Line overlay */}
                    {step < steps.length - 1 && (
                        <div className="absolute inset-0 overflow-hidden rounded-full opacity-50">
                            <div className="animate-scan border-primary/50"></div>
                        </div>
                    )}
                </div>

                {/* Labels & Progress */}
                <div className="space-y-6">
                    <div className="h-8">
                        <h2 className={`text-2xl font-bold transition-all duration-300 ${steps[step].color}`}>
                            {steps[step].label}
                        </h2>
                    </div>

                    <div className="w-full h-3 bg-secondary rounded-full overflow-hidden border border-border shadow-inner">
                        <div
                            className="h-full bg-primary transition-all duration-300 ease-out relative"
                            style={{ width: `${progress}%` }}
                        >
                            <div className="absolute inset-0 bg-white/20 animate-pulse"></div>
                        </div>
                    </div>

                    <div className="flex justify-between text-xs font-mono text-muted-foreground uppercase tracking-widest">
                        <span>Diagnóstico AuditX v2.4</span>
                        <span className="text-primary font-bold">{Math.round(progress)}%</span>
                    </div>
                </div>

                {/* Dynamic Log Entries (Simulation) */}
                <div className="mt-12 bg-black/80 rounded-lg border border-primary/20 p-6 text-left font-mono text-[10px] space-y-1.5 shadow-2xl relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-2 opacity-20 group-hover:opacity-40 transition-opacity">
                        <Database className="w-12 h-12 text-primary" />
                    </div>

                    <div className="flex items-center gap-2 text-primary/80 mb-2 border-b border-primary/10 pb-2">
                        <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
                        <span className="text-[9px] uppercase font-bold tracking-widest">Live Security Audit Console</span>
                    </div>

                    <div className="flex items-center gap-2">
                        <span className="text-safe">[OK]</span>
                        <span className="text-gray-400">Environment Decryption: SHA-256 layer active</span>
                    </div>
                    {step >= 1 && (
                        <div className="flex items-center gap-2">
                            <span className="text-safe">[OK]</span>
                            <span className="text-gray-400">Dependency Map: 142 nodes identified</span>
                        </div>
                    )}
                    {step >= 2 && (
                        <div className="flex items-center gap-2 animate-in slide-in-from-left duration-300">
                            <span className="text-warning">[WRN]</span>
                            <span className="text-gray-300 font-bold">Heuristic match: SQL String Concatenation at L42</span>
                        </div>
                    )}
                    {step >= 3 && (
                        <div className="flex items-center gap-2 animate-in slide-in-from-left duration-300">
                            <span className="text-critical">[CRIT]</span>
                            <span className="text-gray-300 font-bold">Hardcoded Secret: "AWS_SECRET_KEY" found</span>
                        </div>
                    )}
                    {step >= 4 && (
                        <div className="flex items-center gap-2">
                            <span className="text-safe">[OK]</span>
                            <span className="text-gray-400">Entropy check: PASS</span>
                        </div>
                    )}
                    {step >= 5 && (
                        <div className="flex items-center gap-2">
                            <span className="text-safe">[OK]</span>
                            <span className="text-gray-400">Correlacionando consenso das 9 IAs... concluído</span>
                        </div>
                    )}

                    <div className="flex items-center gap-2 animate-pulse mt-4">
                        <span className="text-primary font-bold">&gt;_</span>
                        <span className="text-primary/90 uppercase tracking-tighter font-bold">{steps[step].label}</span>
                    </div>

                    {/* Simulated data stream */}
                    <div className="pt-2 text-[8px] text-primary/30 truncate font-mono">
                        {[
                            "[DEBUG] Construindo Árvore de Sintaxe Abstrata (AST)...",
                            "[AI] Consultando Consenso de 9 IAs...",
                            "[SECURITY] Verificando vulnerabilidades OWASP Top 10...",
                            "[TRACE] Normalizando tokens...",
                        ].map((line, i) => (
                            <div key={i} className="whitespace-nowrap overflow-hidden">
                                {line}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
