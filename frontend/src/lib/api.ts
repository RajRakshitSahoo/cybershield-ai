import axios from "axios";

export const api = axios.create({ baseURL: "/api" });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("cs_access_token");
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface DomainInfo {
  domain: string;
  title?: string | null;
  favicon?: string | null;
  ip_address?: string | null;
  ipv6?: string | null;
  registrar?: string | null;
  creation_date?: string | null;
  expiry_date?: string | null;
  updated_date?: string | null;
  domain_age_days?: number | null;
  name_servers: string[];
  hosting_provider?: string | null;
  asn?: string | null;
  country?: string | null;
  city?: string | null;
  timezone?: string | null;
  cdn_provider?: string | null;
  organization?: string | null;
}

export interface SSLInfo {
  https: boolean;
  valid: boolean;
  issuer?: string | null;
  subject?: string | null;
  tls_version?: string | null;
  expiry_date?: string | null;
  days_remaining?: number | null;
  hsts: boolean;
  error?: string | null;
}

export interface DNSInfo {
  a: string[];
  aaaa: string[];
  mx: string[];
  txt: string[];
  ns: string[];
  cname: string[];
  soa: string[];
  dnssec: boolean;
}

export interface SecurityHeader {
  name: string;
  status: "present" | "missing" | "weak" | "strong";
  value?: string | null;
}

export interface TechStack {
  frontend: string[];
  backend: string[];
  cms: string[];
  server: string[];
  cdn: string[];
  analytics: string[];
  other: string[];
}

export interface ReputationResult {
  source: string;
  status: "clean" | "suspicious" | "blacklisted" | "unavailable";
  detail?: string | null;
}

export interface AIPrediction {
  verdict: "Safe" | "Suspicious" | "Phishing";
  confidence: number;
  risk_score: number;
  reasons: string[];
  feature_importances: Record<string, number>;
}

export interface TimelineStep {
  step: string;
  status: "done" | "skipped" | "failed";
  duration_ms: number;
}

export interface AnalysisReport {
  id?: string;
  url: string;
  scanned_at: string;
  domain_info: DomainInfo;
  ssl_info: SSLInfo;
  dns_info: DNSInfo;
  security_headers: SecurityHeader[];
  tech_stack: TechStack;
  reputation: ReputationResult[];
  ai_prediction: AIPrediction;
  timeline: TimelineStep[];
  screenshot_desktop?: string | null;
  screenshot_mobile?: string | null;
}

export const analyzeUrl = (url: string) =>
  api.post<AnalysisReport>("/analyze", { url }).then((r) => r.data);

export const compareUrls = (url_a: string, url_b: string) =>
  api.post("/compare", { url_a, url_b }).then((r) => r.data);

export const getHistory = (search = "", verdict = "") =>
  api
    .get("/history", { params: { search, verdict } })
    .then((r) => r.data as (AnalysisReport & { id: string })[]);

export const deleteHistoryItem = (id: string) => api.delete(`/history/${id}`);

export const bookmarkItem = (report_id: string, note?: string) =>
  api.post("/history/bookmark", { report_id, note });

export const getDashboardSummary = () =>
  api.get("/dashboard/summary").then((r) => r.data);

export const getAdminStats = () => api.get("/admin/stats").then((r) => r.data);

export const getAdminUsers = () => api.get("/admin/users").then((r) => r.data);
