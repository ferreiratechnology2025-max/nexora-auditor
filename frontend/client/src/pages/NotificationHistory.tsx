import { useState } from "react";
import { Mail, Trash2, Eye, EyeOff, Filter } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useNotification } from "@/contexts/NotificationContext";
import { toast } from "sonner";

/**
 * AUDITX Notification History Page
 * Design: Minimalismo Cirúrgico
 * - Histórico de notificações
 * - Filtro por tipo
 * - Marcar como lido/não lido
 * - Deletar notificações
 */

export default function NotificationHistory() {
  const { notifications, markAsRead, deleteNotification } = useNotification();
  const [filter, setFilter] = useState<string>("all");

  const filteredNotifications = notifications.filter((notif) => {
    if (filter === "all") return true;
    if (filter === "unread") return !notif.read;
    return notif.type === filter;
  });

  const handleMarkAsRead = (id: string) => {
    markAsRead(id);
    toast.success("Marcado como lido");
  };

  const handleDelete = (id: string) => {
    deleteNotification(id);
    toast.success("Notificação deletada");
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case "audit_complete":
        return "✓";
      case "audit_failed":
        return "✕";
      case "security_alert":
        return "⚠";
      case "subscription_renewal":
        return "🔄";
      default:
        return "•";
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case "audit_complete":
        return "bg-safe/10 border-safe/20 text-safe";
      case "audit_failed":
        return "bg-critical/10 border-critical/20 text-critical";
      case "security_alert":
        return "bg-warning/10 border-warning/20 text-warning";
      case "subscription_renewal":
        return "bg-primary/10 border-primary/20 text-primary";
      default:
        return "bg-muted/10 border-muted/20 text-muted-foreground";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Mail className="w-6 h-6 text-primary" />
          <h1 className="text-2xl font-bold text-foreground">Histórico de Notificações</h1>
        </div>
        <div className="text-sm text-muted-foreground">
          {notifications.length} notificações
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {[
          { value: "all", label: "Todas" },
          { value: "unread", label: "Não Lidas" },
          { value: "audit_complete", label: "Auditorias Concluídas" },
          { value: "audit_failed", label: "Erros" },
          { value: "security_alert", label: "Alertas" },
        ].map((f) => (
          <button
            key={f.value}
            onClick={() => setFilter(f.value)}
            className={`px-4 py-2 rounded-lg border transition-colors whitespace-nowrap text-sm font-medium ${
              filter === f.value
                ? "bg-primary text-white border-primary"
                : "bg-card border-border text-foreground hover:bg-secondary"
            }`}
          >
            <Filter className="w-3 h-3 inline mr-1" />
            {f.label}
          </button>
        ))}
      </div>

      {/* Notifications List */}
      <div className="space-y-3">
        {filteredNotifications.length === 0 ? (
          <div className="text-center py-12 bg-card border border-border rounded-lg">
            <Mail className="w-12 h-12 text-muted-foreground mx-auto mb-3 opacity-50" />
            <p className="text-muted-foreground">Nenhuma notificação encontrada</p>
          </div>
        ) : (
          filteredNotifications.map((notification) => (
            <div
              key={notification.id}
              className={`border rounded-lg p-4 transition-colors ${
                notification.read
                  ? "bg-card border-border"
                  : "bg-primary/5 border-primary/20"
              }`}
            >
              <div className="flex items-start gap-4">
                {/* Icon */}
                <div
                  className={`w-10 h-10 rounded-lg border flex items-center justify-center text-lg font-bold flex-shrink-0 ${getNotificationColor(
                    notification.type
                  )}`}
                >
                  {getNotificationIcon(notification.type)}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h3 className={`font-semibold ${
                        notification.read ? "text-foreground" : "text-foreground font-bold"
                      }`}>
                        {notification.title}
                      </h3>
                      <p className="text-sm text-muted-foreground mt-1">
                        {notification.message}
                      </p>

                      {/* Score and Vulnerabilities */}
                      {notification.auditScore !== undefined && (
                        <div className="flex gap-4 mt-2 text-xs">
                          <span className="text-foreground">
                            Score: <strong>{notification.auditScore}/100</strong>
                          </span>
                          {notification.vulnerabilityCount !== undefined && (
                            <span className="text-foreground">
                              Vulnerabilidades:{" "}
                              <strong>{notification.vulnerabilityCount}</strong>
                            </span>
                          )}
                        </div>
                      )}

                      {/* Timestamp */}
                      <p className="text-xs text-muted-foreground mt-2">
                        {new Date(notification.sentAt).toLocaleString("pt-BR")}
                      </p>
                    </div>

                    {/* Status Badge */}
                    {!notification.read && (
                      <div className="px-2 py-1 bg-primary text-white text-xs rounded font-semibold flex-shrink-0">
                        Novo
                      </div>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2 flex-shrink-0">
                  <button
                    onClick={() => handleMarkAsRead(notification.id)}
                    className="p-2 hover:bg-secondary rounded-lg transition-colors text-muted-foreground hover:text-foreground"
                    title={notification.read ? "Marcar como não lido" : "Marcar como lido"}
                  >
                    {notification.read ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                  <button
                    onClick={() => handleDelete(notification.id)}
                    className="p-2 hover:bg-critical/10 rounded-lg transition-colors text-muted-foreground hover:text-critical"
                    title="Deletar notificação"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Info Box */}
      {notifications.length > 0 && (
        <div className="bg-secondary/30 border border-border rounded-lg p-4 text-sm text-foreground">
          <p className="font-semibold mb-1">💡 Dica:</p>
          <p className="text-xs text-muted-foreground">
            Você tem {notifications.filter((n) => !n.read).length} notificação(ões) não lida(s).
            Clique no ícone de olho para marcar como lido/não lido.
          </p>
        </div>
      )}
    </div>
  );
}
