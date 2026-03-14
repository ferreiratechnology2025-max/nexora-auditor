import { useState } from "react";
import { useLocation } from "wouter";
import DashboardSidebar from "@/components/DashboardSidebar";
import DashboardHeader from "@/components/DashboardHeader";
import AuditHistory from "@/components/AuditHistory";
import SubscriptionManagement from "@/components/SubscriptionManagement";
import UserProfile from "@/components/UserProfile";

/**
 * AUDITX Dashboard Page
 * Design: Minimalismo Cirúrgico
 * - Layout com sidebar + main content
 * - Navegação entre tabs (Auditorias, Assinatura, Perfil)
 * - Componentes específicos para cada seção
 */

type DashboardTab = "auditorias" | "assinatura" | "perfil";

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<DashboardTab>("auditorias");
  const [, setLocation] = useLocation();

  const handleLogout = () => {
    // Simular logout
    setLocation("/");
  };

  const getTabTitle = () => {
    switch (activeTab) {
      case "auditorias":
        return "Minhas Auditorias";
      case "assinatura":
        return "Minha Assinatura";
      case "perfil":
        return "Meu Perfil";
      default:
        return "Dashboard";
    }
  };

  const getTabSubtitle = () => {
    switch (activeTab) {
      case "auditorias":
        return "Visualize e baixe todos os seus laudos de auditoria";
      case "assinatura":
        return "Gerencie seu plano e informações de faturamento";
      case "perfil":
        return "Atualize suas informações pessoais e configurações de segurança";
      default:
        return "";
    }
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <DashboardSidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onLogout={handleLogout}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <DashboardHeader
          title={getTabTitle()}
          subtitle={getTabSubtitle()}
        />

        {/* Content */}
        <main className="flex-1 overflow-auto">
          <div className="p-6 md:p-8">
            {activeTab === "auditorias" && <AuditHistory />}
            {activeTab === "assinatura" && <SubscriptionManagement />}
            {activeTab === "perfil" && <UserProfile />}
          </div>
        </main>
      </div>
    </div>
  );
}
