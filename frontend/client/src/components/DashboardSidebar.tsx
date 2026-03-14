import { useState } from "react";
import { useLocation } from "wouter";
import { BarChart3, FileText, Settings, Bell, LogOut, Menu, X } from "lucide-react";
import { Button } from "@/components/ui/button";

/**
 * AUDITX Dashboard Sidebar
 * Design: Minimalismo Cirúrgico
 * - Navegação entre seções do dashboard
 * - Links para Auditorias, Assinatura, Perfil
 * - Logout
 * - Responsivo com menu mobile
 */

interface DashboardSidebarProps {
  activeTab: "auditorias" | "assinatura" | "perfil";
  onTabChange: (tab: "auditorias" | "assinatura" | "perfil") => void;
  onLogout: () => void;
}

export default function DashboardSidebar({
  activeTab,
  onTabChange,
  onLogout,
}: DashboardSidebarProps) {
  const [mobileOpen, setMobileOpen] = useState(false);

  const navItems = [
    {
      id: "auditorias",
      label: "Minhas Auditorias",
      icon: BarChart3,
    },
    {
      id: "assinatura",
      label: "Assinatura",
      icon: FileText,
    },
    {
      id: "perfil",
      label: "Perfil",
      icon: Settings,
    },
  ];

  const externalLinks = [
    {
      label: "Notificações",
      icon: Bell,
      href: "/notifications",
    },
  ];

  return (
    <>
      {/* Mobile Toggle */}
      <div className="md:hidden sticky top-0 z-40 bg-card border-b border-border p-4 flex items-center justify-between">
        <span className="font-semibold text-foreground">Menu</span>
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="text-foreground"
        >
          {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Sidebar */}
      <aside
        className={`fixed md:relative top-0 left-0 z-30 h-screen md:h-auto w-64 bg-card border-r border-border transition-transform ${
          mobileOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        }`}
      >
        <div className="p-6 space-y-8">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary rounded flex items-center justify-center">
              <span className="text-white font-bold text-sm">AX</span>
            </div>
            <span className="font-bold text-lg text-foreground">AUDITX</span>
          </div>

          {/* Navigation */}
          <nav className="space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    onTabChange(item.id as any);
                    setMobileOpen(false);
                  }}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                    isActive
                      ? "bg-primary/10 text-primary font-semibold"
                      : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Divider */}
          <div className="border-t border-border"></div>

          {/* External Links */}
          <nav className="space-y-2">
            {externalLinks.map((link) => {
              const Icon = link.icon;
              return (
                <a
                  key={link.href}
                  href={link.href}
                  className="w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all text-muted-foreground hover:text-foreground hover:bg-secondary/50"
                >
                  <Icon className="w-5 h-5" />
                  <span>{link.label}</span>
                </a>
              );
            })}
          </nav>

          {/* Divider */}
          <div className="border-t border-border"></div>

          {/* Logout */}
          <Button
            onClick={onLogout}
            variant="outline"
            className="w-full border-border text-muted-foreground hover:text-foreground justify-start gap-3"
          >
            <LogOut className="w-5 h-5" />
            Sair
          </Button>
        </div>
      </aside>

      {/* Mobile Overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-20 md:hidden"
          onClick={() => setMobileOpen(false)}
        ></div>
      )}
    </>
  );
}
