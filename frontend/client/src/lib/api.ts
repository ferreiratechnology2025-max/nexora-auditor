const API_BASE = "https://auditor.nexora360.cloud/api";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem("auditx_token");
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erro na requisição");
  }
  return res.json();
}

export const api = {
  auth: {
    register: (email: string, password: string, name: string) =>
      request<{ token: string; user: ApiUser }>("/auth/register", {
        method: "POST",
        body: JSON.stringify({ email, password, name }),
      }),
    login: (email: string, password: string) =>
      request<{ token: string; user: ApiUser }>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      }),
    me: () => request<ApiUser>("/auth/me"),
  },
  audit: {
    zip: async (file: File) => {
      const form = new FormData();
      form.append("file", file);
      const token = localStorage.getItem("auditx_token");
      const res = await fetch(`${API_BASE}/audit/zip`, {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: form,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Erro na auditoria");
      return data;
    },
    github: (repo_url: string) =>
      request("/audit/github", { method: "POST", body: JSON.stringify({ repo_url }) }),
    get: (id: string) => request(`/audit/${id}`),
    report: (id: string) => request(`/audit/${id}/report`),
  },
  plans: {
    list: () => request<Record<string, ApiPlan>>("/plans"),
  },
  payment: {
    create: (audit_id: string, plan: string, email: string) =>
      request<{ preference_id: string; init_point: string; sandbox_init_point?: string }>("/payment/create", {
        method: "POST",
        body: JSON.stringify({ audit_id, plan, email }),
      }),
  },
};

export interface ApiUser {
  id: number;
  email: string;
  name: string;
  plan: "free" | "pro" | "enterprise";
  scans_this_month: number;
  plan_info: ApiPlan;
}

export interface ApiPlan {
  name: string;
  scans_per_month: number;
  max_size_mb: number;
  features: string[];
  price_brl: number;
}
