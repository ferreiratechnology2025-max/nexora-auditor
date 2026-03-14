import { CheckCircle2, ShieldCheck, Code, Zap } from "lucide-react";

export default function DeliverablePreview() {
    return (
        <section className="py-20 md:py-32 bg-background overflow-hidden">
            <div className="container mx-auto px-4">
                <div className="text-center mb-16">
                    <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
                        O que você recebe em minutos
                    </h2>
                    <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                        Não entregamos apenas uma lista de erros. Entregamos clareza, correções prontas e validação para o seu time.
                    </p>
                </div>

                <div className="grid lg:grid-cols-2 gap-12 items-center">
                    {/* Mockup Dashboard */}
                    <div className="relative group">
                        <div className="absolute -inset-1 bg-gradient-to-r from-primary to-blue-600 rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200"></div>
                        <div className="relative bg-card border border-border rounded-xl overflow-hidden shadow-2xl">
                            <div className="bg-muted px-4 py-2 border-b border-border flex items-center gap-2">
                                <div className="flex gap-1.5">
                                    <div className="w-3 h-3 rounded-full bg-red-500/50"></div>
                                    <div className="w-3 h-3 rounded-full bg-yellow-500/50"></div>
                                    <div className="w-3 h-3 rounded-full bg-green-500/50"></div>
                                </div>
                                <div className="text-[10px] text-muted-foreground font-mono">auditor.nexora360.cloud/report/v1042</div>
                            </div>
                            <img
                                src="/dashboard_mockup.png"
                                alt="AuditX dashboard com auditoria de código por IA e DevSecOps"
                                className="w-full h-auto"
                                width="640"
                                height="640"
                                loading="eager"
                            />
                        </div>

                        {/* Floating Features */}
                        <div className="absolute -bottom-6 -right-6 md:right-10 bg-background border border-border p-4 rounded-lg shadow-xl animate-bounce-subtle hidden md:block">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-safe/10 rounded-full">
                                    <ShieldCheck className="w-5 h-5 text-safe" />
                                </div>
                                <div>
                                    <p className="text-xs font-bold">Certificado Ativo</p>
                                    <p className="text-[10px] text-muted-foreground">ISO & OWASP Compliant</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Code Correction Preview */}
                    <div className="flex flex-col gap-8">
                        <div className="space-y-6">
                            <div className="flex items-start gap-4">
                                <div className="mt-1 p-2 bg-primary/10 rounded-lg">
                                    <Zap className="w-5 h-5 text-primary" />
                                </div>
                                <div>
                                    <h3 className="text-xl font-bold text-foreground">Score 0–100 Dinâmico</h3>
                                    <p className="text-muted-foreground">Entenda instantaneamente a saúde do seu projeto com nosso algoritmo de scoring proprietário.</p>
                                </div>
                            </div>

                            <div className="flex items-start gap-4">
                                <div className="mt-1 p-2 bg-primary/10 rounded-lg">
                                    <Code className="w-5 h-5 text-primary" />
                                </div>
                                <div>
                                    <h3 className="text-xl font-bold text-foreground">Exemplo de Correção (Autofix)</h3>
                                    <p className="text-muted-foreground">Veja como transformamos vulnerabilidades críticas em código seguro e otimizado.</p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-card border border-border rounded-xl overflow-hidden shadow-lg">
                            <div className="bg-muted/50 px-4 py-2 border-b border-border text-[10px] font-mono text-muted-foreground">
                                Before vs After Implementation
                            </div>
                            <img
                                src="/code_fix_preview.png"
                                alt="Comparativo antes e depois do autofix de vulnerabilidades no AuditX"
                                className="w-full h-auto"
                                width="640"
                                height="640"
                                loading="lazy"
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            {[
                                "Relatório em PDF",
                                "JSON para CI/CD",
                                "Certificado Digital",
                                "Auto-PR (Em breve)"
                            ].map((item, i) => (
                                <div key={i} className="flex items-center gap-2">
                                    <CheckCircle2 className="w-4 h-4 text-safe" />
                                    <span className="text-sm font-medium">{item}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
