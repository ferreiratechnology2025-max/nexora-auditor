import { useState } from "react";
import Header from "@/components/Header";
import HeroSection from "@/components/HeroSection";
import DynamicPricingCalculator from "@/components/DynamicPricingCalculator";
import ComparisonTable from "@/components/ComparisonTable";
import EngineeringPipeline from "@/components/EngineeringPipeline";
import SocialProof from "@/components/SocialProof";
import CoverageSection from "@/components/CoverageSection";
import DeliverablePreview from "@/components/DeliverablePreview";
import TestimonialSection from "@/components/TestimonialSection";
import FAQSection from "@/components/FAQSection";
import PlansComparison from "@/components/PlansComparison";
import SecondaryCTA from "@/components/SecondaryCTA";
import ValidatingLoading from "@/components/ValidationLoading";
import ResultsDashboard from "@/components/ResultsDashboard";
import AuditHistory from "@/components/AuditHistory";
import Footer from "@/components/Footer";
import { History, Home as HomeIcon } from "lucide-react";
import { Button } from "@/components/ui/button";

/**
 * AUDITX Home Page
 * Design: Minimalismo Cirúrgico
 * - Landing page com fluxo de análise
 * - Transição para dashboard de resultados
 * - Simulação de análise com delay
 */
export default function Home() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showResults, setShowResults] = useState(() => {
    return new URLSearchParams(window.location.search).get("unlocked") === "true";
  });
  const [view, setView] = useState<"landing" | "history">("landing");

  const isUnlocked = new URLSearchParams(window.location.search).get("unlocked") === "true";

  const handleAnalyzeStart = (type: "upload" | "github", value: string) => {
    setIsAnalyzing(true);
    // Simular análise com delay de 5 segundos para exibir animação completa
    setTimeout(() => {
      setIsAnalyzing(false);
      setShowResults(true);
    }, 5000);
  };

  const handleBackToLanding = () => {
    setShowResults(false);
    // Limpar query params ao voltar
    window.history.replaceState({}, '', '/');
  };

  if (showResults) {
    return <ResultsDashboard onBack={handleBackToLanding} isUnlocked={isUnlocked} />;
  }

  return (
    <div className="min-h-screen flex flex-col bg-background relative">
      {isAnalyzing && <ValidatingLoading />}

      {/* Floating History Toggle */}
      <div className="fixed bottom-6 right-6 z-40">
        <Button
          onClick={() => setView(view === "landing" ? "history" : "landing")}
          className="rounded-full w-14 h-14 shadow-2xl bg-foreground hover:bg-foreground/90 text-background group"
        >
          {view === "landing" ? (
            <History className="w-6 h-6 group-hover:rotate-12 transition-transform" />
          ) : (
            <HomeIcon className="w-6 h-6" />
          )}
        </Button>
      </div>

      <Header />
      <main className="flex-1">
        {view === "landing" ? (
          <>
            <HeroSection onAnalyzeStart={handleAnalyzeStart} isAnalyzing={isAnalyzing} />
            <DynamicPricingCalculator />
            <ComparisonTable />
            <CoverageSection />
            <EngineeringPipeline />
            <DeliverablePreview />
            <TestimonialSection />
            <SocialProof />
            <FAQSection />
            <PlansComparison />
            <SecondaryCTA />
          </>
        ) : (
          <div className="container mx-auto px-4 py-12">
            <AuditHistory />
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}

