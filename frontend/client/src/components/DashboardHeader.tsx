import { Bell, User } from "lucide-react";
import { Button } from "@/components/ui/button";

/**
 * AUDITX Dashboard Header
 * Design: Minimalismo Cirúrgico
 * - Notificações
 * - Perfil do utilizador
 * - Breadcrumbs
 */

interface DashboardHeaderProps {
  title: string;
  subtitle?: string;
  userName?: string;
}

export default function DashboardHeader({
  title,
  subtitle,
  userName = "João Silva",
}: DashboardHeaderProps) {
  return (
    <header className="bg-card border-b border-border sticky top-0 z-10">
      <div className="px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">{title}</h1>
          {subtitle && (
            <p className="text-sm text-muted-foreground mt-1">{subtitle}</p>
          )}
        </div>

        <div className="flex items-center gap-4">
          {/* Notifications */}
          <Button
            variant="ghost"
            size="icon"
            className="relative text-muted-foreground hover:text-foreground"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute top-2 right-2 w-2 h-2 bg-critical rounded-full"></span>
          </Button>

          {/* User Menu */}
          <div className="flex items-center gap-3 pl-4 border-l border-border">
            <div className="text-right hidden sm:block">
              <p className="text-sm font-semibold text-foreground">{userName}</p>
              <p className="text-xs text-muted-foreground">Plano Pro</p>
            </div>
            <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-primary" />
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
