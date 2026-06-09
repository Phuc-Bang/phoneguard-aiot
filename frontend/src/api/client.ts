// API client tập trung cho FastAPI backend PhoneGuard AIoT.

export type HealthResponse = {
  status: string;
  service: string;
};

export type Telemetry = {
  device_id: string;
  timestamp: string;
  battery_level: number;
  charging: boolean;
  acc_x: number | null;
  acc_y: number | null;
  acc_z: number | null;
  light_lux: number | null;
  network_type: string | null;
  received_at?: string;
};

export type AnomalyEvent = {
  event_id: string;
  device_id: string;
  timestamp: string;
  event_type?: string;
  severity: string;
  decision?: string;
  explanation?: string;
  recommendation?: string;
  safety_note?: string;
  anomaly_score?: string | number;
  model_version?: string;
};

export type ForecastResult = {
  model_output: {
    target: string;
    predicted_battery_15min: number;
    predicted_battery_30min: number;
    model_version: string;
    confidence: number;
  };
  decision: {
    risk_level: "NORMAL" | "WARNING" | "HIGH" | "CRITICAL";
    recommendation: string;
    reason: string;
    safety_note: string;
  };
};

export type RiskResult = {
  device_id: string;
  overall_risk: "NORMAL" | "WARNING" | "HIGH" | "CRITICAL";
  risk_score: number;
  main_reason: string;
  recommendations: string[];
  control_allowed: boolean;
  safety_note: string;
  model_version: string;
};

export type DashboardData = {
  health: HealthResponse | null;
  latest: Telemetry | null;
  history: Telemetry[];
  events: AnomalyEvent[];
  forecast: ForecastResult | null;
  risk: RiskResult | null;
};

const DEFAULT_API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export function getDefaultApiBaseUrl(): string {
  return localStorage.getItem("phoneguard_api_base_url") || DEFAULT_API_BASE_URL;
}

export function saveApiBaseUrl(url: string): void {
  localStorage.setItem("phoneguard_api_base_url", url.replace(/\/$/, ""));
}

async function requestJson<T>(apiBaseUrl: string, path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl.replace(/\/$/, "")}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`${path} failed: HTTP ${response.status} ${body}`);
  }
  return response.json() as Promise<T>;
}

export async function getHealth(apiBaseUrl: string): Promise<HealthResponse> {
  return requestJson<HealthResponse>(apiBaseUrl, "/health");
}

export async function getLatest(apiBaseUrl: string): Promise<Telemetry | null> {
  try {
    return await requestJson<Telemetry>(apiBaseUrl, "/latest");
  } catch {
    return null;
  }
}

export async function getHistory(apiBaseUrl: string, limit = 120): Promise<Telemetry[]> {
  return requestJson<Telemetry[]>(apiBaseUrl, `/history?limit=${limit}`);
}

export async function getEvents(apiBaseUrl: string, limit = 50): Promise<AnomalyEvent[]> {
  return requestJson<AnomalyEvent[]>(apiBaseUrl, `/events?limit=${limit}`);
}

export async function postForecast(apiBaseUrl: string, telemetry: Telemetry | null): Promise<ForecastResult | null> {
  if (!telemetry) return null;
  return requestJson<ForecastResult>(apiBaseUrl, "/forecast", {
    method: "POST",
    body: JSON.stringify({ device_id: telemetry.device_id, telemetry }),
  });
}

export async function postRisk(apiBaseUrl: string, telemetry: Telemetry | null): Promise<RiskResult | null> {
  if (!telemetry) return null;
  return requestJson<RiskResult>(apiBaseUrl, "/predict-risk", {
    method: "POST",
    body: JSON.stringify(telemetry),
  });
}

export async function loadDashboardData(apiBaseUrl: string): Promise<DashboardData> {
  const [health, latest, history, events] = await Promise.all([
    getHealth(apiBaseUrl).catch(() => null),
    getLatest(apiBaseUrl),
    getHistory(apiBaseUrl).catch(() => []),
    getEvents(apiBaseUrl).catch(() => []),
  ]);
  const [forecast, risk] = await Promise.all([
    postForecast(apiBaseUrl, latest).catch(() => null),
    postRisk(apiBaseUrl, latest).catch(() => null),
  ]);
  return { health, latest, history, events, forecast, risk };
}
