import { createContext, useState, useContext, useEffect, ReactNode } from "react";

/**
 * AUDITX Notification Context
 * Design: Minimalismo Cirúrgico
 * - Gerenciamento de notificações por e-mail
 * - Histórico de notificações
 * - Preferências de notificação
 */

export interface Notification {
  id: string;
  type: "audit_complete" | "audit_failed" | "security_alert" | "subscription_renewal";
  title: string;
  message: string;
  auditId?: string;
  auditScore?: number;
  vulnerabilityCount?: number;
  email: string;
  sentAt: string;
  read: boolean;
}

export interface NotificationPreferences {
  emailOnAuditComplete: boolean;
  emailOnAuditFailed: boolean;
  emailOnSecurityAlert: boolean;
  emailOnSubscriptionRenewal: boolean;
  digestFrequency: "immediate" | "daily" | "weekly";
  unsubscribeAll: boolean;
}

interface NotificationContextType {
  notifications: Notification[];
  preferences: NotificationPreferences;
  isLoading: boolean;
  sendAuditCompleteNotification: (
    email: string,
    auditId: string,
    score: number,
    vulnerabilityCount: number
  ) => Promise<void>;
  sendAuditFailedNotification: (email: string, auditId: string, error: string) => Promise<void>;
  markAsRead: (notificationId: string) => void;
  deleteNotification: (notificationId: string) => void;
  updatePreferences: (preferences: Partial<NotificationPreferences>) => Promise<void>;
  getNotifications: () => Notification[];
  getUnreadCount: () => number;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export function NotificationProvider({ children }: { children: ReactNode }) {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [preferences, setPreferences] = useState<NotificationPreferences>({
    emailOnAuditComplete: true,
    emailOnAuditFailed: true,
    emailOnSecurityAlert: true,
    emailOnSubscriptionRenewal: true,
    digestFrequency: "immediate",
    unsubscribeAll: false,
  });

  // Carregar preferências do localStorage
  useEffect(() => {
    const storedPreferences = localStorage.getItem("auditx_notification_preferences");
    if (storedPreferences) {
      try {
        setPreferences(JSON.parse(storedPreferences));
      } catch (error) {
        console.error("Erro ao carregar preferências:", error);
      }
    }

    const storedNotifications = localStorage.getItem("auditx_notifications");
    if (storedNotifications) {
      try {
        setNotifications(JSON.parse(storedNotifications));
      } catch (error) {
        console.error("Erro ao carregar notificações:", error);
      }
    }
  }, []);

  const sendAuditCompleteNotification = async (
    email: string,
    auditId: string,
    score: number,
    vulnerabilityCount: number
  ) => {
    setIsLoading(true);
    try {
      // Verificar preferências
      if (!preferences.emailOnAuditComplete || preferences.unsubscribeAll) {
        console.log("Notificações desativadas para este tipo de evento");
        return;
      }

      // Simular chamada à API
      await new Promise((resolve) => setTimeout(resolve, 1000));

      const notification: Notification = {
        id: "notif-" + Math.random().toString(36).substr(2, 9),
        type: "audit_complete",
        title: "Auditoria Concluída com Sucesso",
        message: `Sua auditoria foi concluída com score ${score}/100 e ${vulnerabilityCount} vulnerabilidades detectadas.`,
        auditId,
        auditScore: score,
        vulnerabilityCount,
        email,
        sentAt: new Date().toISOString(),
        read: false,
      };

      const updatedNotifications = [notification, ...notifications];
      setNotifications(updatedNotifications);
      localStorage.setItem("auditx_notifications", JSON.stringify(updatedNotifications));

      // Aqui você faria uma chamada à API para enviar e-mail
      console.log(`E-mail de conclusão de auditoria enviado para ${email}`);
      console.log("Notification:", notification);
    } finally {
      setIsLoading(false);
    }
  };

  const sendAuditFailedNotification = async (email: string, auditId: string, error: string) => {
    setIsLoading(true);
    try {
      // Verificar preferências
      if (!preferences.emailOnAuditFailed || preferences.unsubscribeAll) {
        console.log("Notificações desativadas para este tipo de evento");
        return;
      }

      // Simular chamada à API
      await new Promise((resolve) => setTimeout(resolve, 1000));

      const notification: Notification = {
        id: "notif-" + Math.random().toString(36).substr(2, 9),
        type: "audit_failed",
        title: "Erro na Auditoria",
        message: `A auditoria falhou: ${error}`,
        auditId,
        email,
        sentAt: new Date().toISOString(),
        read: false,
      };

      const updatedNotifications = [notification, ...notifications];
      setNotifications(updatedNotifications);
      localStorage.setItem("auditx_notifications", JSON.stringify(updatedNotifications));

      // Aqui você faria uma chamada à API para enviar e-mail
      console.log(`E-mail de erro de auditoria enviado para ${email}`);
      console.log("Notification:", notification);
    } finally {
      setIsLoading(false);
    }
  };

  const markAsRead = (notificationId: string) => {
    const updatedNotifications = notifications.map((notif) =>
      notif.id === notificationId ? { ...notif, read: true } : notif
    );
    setNotifications(updatedNotifications);
    localStorage.setItem("auditx_notifications", JSON.stringify(updatedNotifications));
  };

  const deleteNotification = (notificationId: string) => {
    const updatedNotifications = notifications.filter((notif) => notif.id !== notificationId);
    setNotifications(updatedNotifications);
    localStorage.setItem("auditx_notifications", JSON.stringify(updatedNotifications));
  };

  const updatePreferences = async (newPreferences: Partial<NotificationPreferences>) => {
    setIsLoading(true);
    try {
      // Simular chamada à API
      await new Promise((resolve) => setTimeout(resolve, 800));

      const updatedPreferences = { ...preferences, ...newPreferences };
      setPreferences(updatedPreferences);
      localStorage.setItem("auditx_notification_preferences", JSON.stringify(updatedPreferences));

      console.log("Preferências de notificação atualizadas:", updatedPreferences);
    } finally {
      setIsLoading(false);
    }
  };

  const getNotifications = () => notifications;

  const getUnreadCount = () => notifications.filter((notif) => !notif.read).length;

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        preferences,
        isLoading,
        sendAuditCompleteNotification,
        sendAuditFailedNotification,
        markAsRead,
        deleteNotification,
        updatePreferences,
        getNotifications,
        getUnreadCount,
      }}
    >
      {children}
    </NotificationContext.Provider>
  );
}

export function useNotification() {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error("useNotification deve ser usado dentro de um NotificationProvider");
  }
  return context;
}
