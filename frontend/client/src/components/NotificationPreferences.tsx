import { useState } from "react";
import { Bell, Loader2, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useNotification } from "@/contexts/NotificationContext";
import { toast } from "sonner";

/**
 * AUDITX Notification Preferences Component
 * Design: Minimalismo Cirúrgico
 * - Gestão de preferências de notificação
 * - Toggle de tipos de notificação
 * - Configuração de frequência
 */

export default function NotificationPreferences() {
  const { preferences, updatePreferences, isLoading } = useNotification();
  const [localPrefs, setLocalPrefs] = useState(preferences);
  const [saved, setSaved] = useState(false);

  const handleToggle = (key: keyof typeof preferences) => {
    setLocalPrefs((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
    setSaved(false);
  };

  const handleFrequencyChange = (frequency: "immediate" | "daily" | "weekly") => {
    setLocalPrefs((prev) => ({
      ...prev,
      digestFrequency: frequency,
    }));
    setSaved(false);
  };

  const handleSave = async () => {
    try {
      await updatePreferences(localPrefs);
      setSaved(true);
      toast.success("Preferências salvas com sucesso!");
      setTimeout(() => setSaved(false), 3000);
    } catch (error) {
      toast.error("Erro ao salvar preferências");
    }
  };

  return (
    <div className="bg-card border border-border rounded-lg p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3 pb-4 border-b border-border">
        <Bell className="w-5 h-5 text-primary" />
        <h3 className="text-lg font-semibold text-foreground">
          Preferências de Notificação
        </h3>
      </div>

      {/* Notification Types */}
      <div className="space-y-4">
        <h4 className="text-sm font-semibold text-foreground">
          Tipos de Notificação
        </h4>

        {/* Audit Complete */}
        <label className="flex items-center gap-3 p-3 border border-border rounded-lg hover:bg-secondary/30 cursor-pointer transition-colors">
          <input
            type="checkbox"
            checked={localPrefs.emailOnAuditComplete}
            onChange={() => handleToggle("emailOnAuditComplete")}
            className="w-4 h-4 rounded border-border"
          />
          <div className="flex-1">
            <p className="text-sm font-medium text-foreground">
              Auditoria Concluída
            </p>
            <p className="text-xs text-muted-foreground">
              Receba notificação quando uma auditoria for concluída
            </p>
          </div>
        </label>

        {/* Audit Failed */}
        <label className="flex items-center gap-3 p-3 border border-border rounded-lg hover:bg-secondary/30 cursor-pointer transition-colors">
          <input
            type="checkbox"
            checked={localPrefs.emailOnAuditFailed}
            onChange={() => handleToggle("emailOnAuditFailed")}
            className="w-4 h-4 rounded border-border"
          />
          <div className="flex-1">
            <p className="text-sm font-medium text-foreground">
              Erro na Auditoria
            </p>
            <p className="text-xs text-muted-foreground">
              Receba notificação se uma auditoria falhar
            </p>
          </div>
        </label>

        {/* Security Alert */}
        <label className="flex items-center gap-3 p-3 border border-border rounded-lg hover:bg-secondary/30 cursor-pointer transition-colors">
          <input
            type="checkbox"
            checked={localPrefs.emailOnSecurityAlert}
            onChange={() => handleToggle("emailOnSecurityAlert")}
            className="w-4 h-4 rounded border-border"
          />
          <div className="flex-1">
            <p className="text-sm font-medium text-foreground">
              Alertas de Segurança
            </p>
            <p className="text-xs text-muted-foreground">
              Receba notificação sobre vulnerabilidades críticas detectadas
            </p>
          </div>
        </label>

        {/* Subscription Renewal */}
        <label className="flex items-center gap-3 p-3 border border-border rounded-lg hover:bg-secondary/30 cursor-pointer transition-colors">
          <input
            type="checkbox"
            checked={localPrefs.emailOnSubscriptionRenewal}
            onChange={() => handleToggle("emailOnSubscriptionRenewal")}
            className="w-4 h-4 rounded border-border"
          />
          <div className="flex-1">
            <p className="text-sm font-medium text-foreground">
              Renovação de Assinatura
            </p>
            <p className="text-xs text-muted-foreground">
              Receba notificação sobre renovações de assinatura
            </p>
          </div>
        </label>
      </div>

      {/* Frequency */}
      <div className="space-y-3 pt-4 border-t border-border">
        <h4 className="text-sm font-semibold text-foreground">
          Frequência de Notificações
        </h4>

        <div className="space-y-2">
          {["immediate", "daily", "weekly"].map((freq) => (
            <label
              key={freq}
              className="flex items-center gap-3 p-3 border border-border rounded-lg hover:bg-secondary/30 cursor-pointer transition-colors"
            >
              <input
                type="radio"
                name="frequency"
                value={freq}
                checked={localPrefs.digestFrequency === freq}
                onChange={() =>
                  handleFrequencyChange(freq as "immediate" | "daily" | "weekly")
                }
                className="w-4 h-4 rounded-full border-border"
              />
              <div className="flex-1">
                <p className="text-sm font-medium text-foreground capitalize">
                  {freq === "immediate"
                    ? "Imediato"
                    : freq === "daily"
                      ? "Diário"
                      : "Semanal"}
                </p>
                <p className="text-xs text-muted-foreground">
                  {freq === "immediate"
                    ? "Receba notificações assim que ocorrem"
                    : freq === "daily"
                      ? "Receba um resumo diário"
                      : "Receba um resumo semanal"}
                </p>
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* Unsubscribe All */}
      <div className="space-y-3 pt-4 border-t border-border">
        <label className="flex items-center gap-3 p-3 border border-critical/20 bg-critical/5 rounded-lg hover:bg-critical/10 cursor-pointer transition-colors">
          <input
            type="checkbox"
            checked={localPrefs.unsubscribeAll}
            onChange={() => handleToggle("unsubscribeAll")}
            className="w-4 h-4 rounded border-critical"
          />
          <div className="flex-1">
            <p className="text-sm font-medium text-critical">
              Desinscrever de Todas as Notificações
            </p>
            <p className="text-xs text-critical/70">
              Desative todas as notificações por e-mail
            </p>
          </div>
        </label>
      </div>

      {/* Save Button */}
      <div className="flex gap-2 pt-4 border-t border-border">
        <Button
          onClick={handleSave}
          disabled={isLoading || saved}
          className="flex-1 bg-primary hover:bg-primary/90 text-white"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Salvando...
            </>
          ) : saved ? (
            <>
              <CheckCircle className="w-4 h-4 mr-2" />
              Salvo!
            </>
          ) : (
            "Salvar Preferências"
          )}
        </Button>
      </div>

      {/* Info Box */}
      <div className="bg-primary/5 border border-primary/20 rounded-lg p-4 text-sm text-foreground">
        <p className="font-semibold mb-1">💡 Dica:</p>
        <p className="text-xs text-muted-foreground">
          Você pode gerenciar suas preferências de notificação a qualquer momento.
          Desinscrever de todas as notificações desativará todos os alertas por e-mail.
        </p>
      </div>
    </div>
  );
}
