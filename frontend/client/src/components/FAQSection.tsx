import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from "@/components/ui/accordion";

export default function FAQSection() {
    const faqs = [
        {
            question: "O que acontece com meu código após o diagnóstico?",
            answer: "A privacidade é nosso pilar fundamental. Todo código enviado é criptografado em repouso. Após o processamento da análise e geração do relatório, os arquivos originais são deletados permanentemente de nossos servidores de processamento dentro de 10 minutos."
        },
        {
            question: "Quais linguagens e frameworks são suportados?",
            answer: "Suportamos Python (Django, FastAPI), JavaScript/TypeScript (React, Node, Next.js), PHP (Laravel), Java (Spring Boot), Ruby (Rails) e Go. Estamos constantemente adicionando suporte a novas tecnologias do ecossistema moderno."
        },
        {
            question: "O diagnóstico é realmente gratuito?",
            answer: "Sim! O diagnóstico inicial e o score de qualidade são 100% gratuitos. Você recebe uma visão geral das vulnerabilidades sem custo. Recursos avançados como download de patches, exportação CI/CD e certificações completas fazem parte de nossos planos premium."
        },
        {
            question: "Posso integrar ao meu pipeline de CI/CD?",
            answer: "Com certeza. O AUDITX oferece APIs e webhooks robustos, permitindo que você bloqueie Pull Requests que não atinjam seu score de segurança mínimo configurado."
        }
    ];

    return (
        <section className="py-20 md:py-32 bg-secondary/20">
            <div className="container mx-auto px-4 max-w-3xl">
                <div className="text-center mb-16">
                    <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
                        Dúvidas Frequentes
                    </h2>
                    <p className="text-muted-foreground">
                        Tudo o que você precisa saber sobre a segurança e eficácia da nossa análise.
                    </p>
                </div>

                <Accordion type="single" collapsible className="w-full">
                    {faqs.map((faq, index) => (
                        <AccordionItem key={index} value={`item-${index}`} className="border-border">
                            <AccordionTrigger className="text-left font-semibold hover:text-primary transition-colors">
                                {faq.question}
                            </AccordionTrigger>
                            <AccordionContent className="text-muted-foreground leading-relaxed">
                                {faq.answer}
                            </AccordionContent>
                        </AccordionItem>
                    ))}
                </Accordion>
            </div>
        </section>
    );
}
