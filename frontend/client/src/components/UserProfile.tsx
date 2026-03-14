import { User, Mail, Phone, MapPin, Save, Edit2, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";

/**
 * AUDITX User Profile
 * Design: Minimalismo Cirúrgico
 * - Informações pessoais
 * - Configurações de segurança
 * - Preferências
 */

interface UserData {
  name: string;
  email: string;
  phone: string;
  company: string;
  location: string;
  joinDate: string;
  twoFactorEnabled: boolean;
}

const mockUserData: UserData = {
  name: "João Silva",
  email: "joao@example.com",
  phone: "+55 11 98765-4321",
  company: "Tech Innovations LTDA",
  location: "São Paulo, SP",
  joinDate: "2025-12-11",
  twoFactorEnabled: true,
};

export default function UserProfile() {
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState(mockUserData);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSave = () => {
    setIsEditing(false);
    // Aqui você faria uma chamada à API para salvar os dados
  };

  return (
    <div className="space-y-8">
      {/* Profile Header */}
      <div>
        <div className="flex items-start justify-between mb-6">
          <h2 className="text-2xl font-bold text-foreground">Meu Perfil</h2>
          <Button
            onClick={() => setIsEditing(!isEditing)}
            variant={isEditing ? "default" : "outline"}
            className={isEditing ? "bg-primary hover:bg-primary/90" : ""}
          >
            {isEditing ? (
              <>
                <Save className="w-4 h-4 mr-2" />
                Salvar
              </>
            ) : (
              <>
                <Edit2 className="w-4 h-4 mr-2" />
                Editar
              </>
            )}
          </Button>
        </div>

        {/* Profile Card */}
        <div className="bg-card border border-border rounded-lg p-8">
          <div className="flex items-start gap-6 mb-8">
            {/* Avatar */}
            <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0">
              <User className="w-10 h-10 text-primary" />
            </div>

            {/* Basic Info */}
            <div className="flex-1">
              <h3 className="text-2xl font-bold text-foreground">
                {formData.name}
              </h3>
              <p className="text-muted-foreground">{formData.company}</p>
              <p className="text-sm text-muted-foreground mt-2">
                Membro desde{" "}
                {new Date(formData.joinDate).toLocaleDateString("pt-BR")}
              </p>
            </div>
          </div>

          {/* Form Fields */}
          <div className="grid md:grid-cols-2 gap-6">
            {/* Name */}
            <div>
              <label className="block text-sm font-semibold text-foreground mb-2">
                Nome Completo
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                disabled={!isEditing}
                className="w-full px-4 py-2 border border-border rounded-lg bg-background text-foreground disabled:opacity-50"
              />
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-semibold text-foreground mb-2">
                Email
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                disabled={!isEditing}
                className="w-full px-4 py-2 border border-border rounded-lg bg-background text-foreground disabled:opacity-50"
              />
            </div>

            {/* Phone */}
            <div>
              <label className="block text-sm font-semibold text-foreground mb-2">
                Telefone
              </label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                disabled={!isEditing}
                className="w-full px-4 py-2 border border-border rounded-lg bg-background text-foreground disabled:opacity-50"
              />
            </div>

            {/* Company */}
            <div>
              <label className="block text-sm font-semibold text-foreground mb-2">
                Empresa
              </label>
              <input
                type="text"
                name="company"
                value={formData.company}
                onChange={handleChange}
                disabled={!isEditing}
                className="w-full px-4 py-2 border border-border rounded-lg bg-background text-foreground disabled:opacity-50"
              />
            </div>

            {/* Location */}
            <div className="md:col-span-2">
              <label className="block text-sm font-semibold text-foreground mb-2">
                Localização
              </label>
              <input
                type="text"
                name="location"
                value={formData.location}
                onChange={handleChange}
                disabled={!isEditing}
                className="w-full px-4 py-2 border border-border rounded-lg bg-background text-foreground disabled:opacity-50"
              />
            </div>
          </div>

          {/* Save Button */}
          {isEditing && (
            <div className="flex gap-2 mt-6 pt-6 border-t border-border">
              <Button
                onClick={handleSave}
                className="bg-primary hover:bg-primary/90 text-white"
              >
                Salvar Alterações
              </Button>
              <Button
                onClick={() => {
                  setIsEditing(false);
                  setFormData(mockUserData);
                }}
                variant="outline"
              >
                Cancelar
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Security Settings */}
      <div>
        <h3 className="text-xl font-bold text-foreground mb-4">Segurança</h3>
        <div className="space-y-4">
          {/* Two Factor Auth */}
          <div className="bg-card border border-border rounded-lg p-6 flex items-center justify-between">
            <div className="flex items-start gap-4">
              <Shield className="w-5 h-5 text-primary flex-shrink-0 mt-1" />
              <div>
                <p className="font-semibold text-foreground">
                  Autenticação de Dois Fatores
                </p>
                <p className="text-sm text-muted-foreground mt-1">
                  Adicione uma camada extra de segurança à sua conta
                </p>
              </div>
            </div>
            <div>
              {formData.twoFactorEnabled ? (
                <span className="px-3 py-1 rounded-full bg-safe/10 text-safe text-xs font-semibold">
                  Ativado
                </span>
              ) : (
                <Button
                  variant="outline"
                  size="sm"
                  className="border-primary text-primary hover:bg-primary/10"
                >
                  Ativar
                </Button>
              )}
            </div>
          </div>

          {/* Change Password */}
          <div className="bg-card border border-border rounded-lg p-6 flex items-center justify-between">
            <div>
              <p className="font-semibold text-foreground">Alterar Senha</p>
              <p className="text-sm text-muted-foreground mt-1">
                Última alteração: 2026-01-15
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              className="border-primary text-primary hover:bg-primary/10"
            >
              Alterar
            </Button>
          </div>

          {/* API Keys */}
          <div className="bg-card border border-border rounded-lg p-6 flex items-center justify-between">
            <div>
              <p className="font-semibold text-foreground">Chaves de API</p>
              <p className="text-sm text-muted-foreground mt-1">
                Gerencie suas chaves para integração com CI/CD
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              className="border-primary text-primary hover:bg-primary/10"
            >
              Gerenciar
            </Button>
          </div>
        </div>
      </div>

      {/* Danger Zone */}
      <div>
        <h3 className="text-xl font-bold text-critical mb-4">Zona de Risco</h3>
        <div className="bg-critical/5 border border-critical/20 rounded-lg p-6">
          <p className="font-semibold text-foreground mb-4">Deletar Conta</p>
          <p className="text-sm text-muted-foreground mb-4">
            Uma vez que você delete sua conta, não há volta. Por favor, tenha
            certeza.
          </p>
          <Button
            variant="outline"
            className="border-critical text-critical hover:bg-critical/10"
          >
            Deletar Conta Permanentemente
          </Button>
        </div>
      </div>
    </div>
  );
}
