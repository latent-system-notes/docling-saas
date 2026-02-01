import type {
  AppConfig,
  DiskUsage,
  HealthStatus,
  ModelStatus,
  ProcessingOptions,
  ProcessingResult,
} from "./types";

const BASE = "/api";

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status}: ${body}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => fetchJSON<HealthStatus>(`${BASE}/health`),

  config: () => fetchJSON<AppConfig>(`${BASE}/config`),

  process: async (
    file: File,
    options: ProcessingOptions
  ): Promise<ProcessingResult> => {
    const form = new FormData();
    form.append("file", file);
    form.append("options", JSON.stringify(options));
    return fetchJSON<ProcessingResult>(`${BASE}/process`, {
      method: "POST",
      body: form,
    });
  },

  models: {
    list: () => fetchJSON<ModelStatus[]>(`${BASE}/models`),

    download: (modelId: string) =>
      fetchJSON<{ success: boolean; message: string | null }>(
        `${BASE}/models/${modelId}/download`,
        { method: "POST" }
      ),

    downloadRequired: () =>
      fetchJSON<Record<string, boolean>>(`${BASE}/models/download-required`, {
        method: "POST",
      }),

    downloadAll: () =>
      fetchJSON<Record<string, boolean>>(`${BASE}/models/download-all`, {
        method: "POST",
      }),

    downloadEasyOCR: (languages: string[] = ["en", "ar"]) =>
      fetchJSON<{ success: boolean; languages: string[]; messages: string[] }>(
        `${BASE}/models/download-easyocr`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(languages),
        }
      ),

    verifyRapidOCR: () =>
      fetchJSON<{ success: boolean; messages: string[] }>(
        `${BASE}/models/verify-rapidocr`,
        { method: "POST" }
      ),

    clearCache: () =>
      fetchJSON<{ success: boolean }>(`${BASE}/models/cache`, {
        method: "DELETE",
      }),

    diskUsage: () => fetchJSON<DiskUsage>(`${BASE}/models/disk-usage`),

    offlineStatus: () =>
      fetchJSON<{
        offline_mode: boolean;
        hf_hub_offline: string;
        transformers_offline: string;
        hf_home: string;
        easyocr_module_path: string;
        models_dir: string;
      }>(`${BASE}/models/offline-status`),
  },
};
