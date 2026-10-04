export function getApiBase(): string {
  if (process.env.NEXT_PUBLIC_API_URL !== undefined && process.env.NEXT_PUBLIC_API_URL !== "") {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  // Server-side (SSR / Server Functions): use Vercel service binding
  if (typeof window === "undefined") {
    return process.env.BACKEND_SERVICE_URL || process.env.BACKEND_URL || "http://127.0.0.1:8000";
  }
  // Client-side browser in local dev
  if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
    return "http://127.0.0.1:8000";
  }
  // Client-side browser in production on Vercel (public rewrites handle /api)
  return "";
}

export const API_BASE = getApiBase();

export class ApiError extends Error {
  status: number;
  errorCode?: string;
  data?: any;

  constructor(status: number, message: string, errorCode?: string, data?: any) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.errorCode = errorCode;
    this.data = data;
  }
}

export async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const base = getApiBase();
  const url = `${base}${endpoint}`;
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
    });

    if (!response.ok) {
      let errMessage = `API Error: ${response.status} ${response.statusText}`;
      let errorCode: string | undefined;
      let errData: any = null;
      try {
        errData = await response.json();
        if (errData.detail) {
          errMessage = typeof errData.detail === "string" ? errData.detail : (errData.detail.message || JSON.stringify(errData.detail));
          if (typeof errData.detail === "object" && errData.detail.error) {
            errorCode = errData.detail.error;
          }
        } else if (errData.message) {
          errMessage = errData.message;
        }
        if (errData.error) errorCode = errData.error;
      } catch (_) {}

      if (process.env.NODE_ENV === "development") {
        console.error("[JOB API DEBUG] request failed:", {
          endpoint,
          status: response.status,
          message: errMessage,
        });
      }

      throw new ApiError(response.status, errMessage, errorCode, errData);
    }

    return response.json();
  } catch (err: any) {
    if (err instanceof ApiError) {
      throw err;
    }
    if (process.env.NODE_ENV === "development") {
      console.error("[JOB API DEBUG] connection/network error:", {
        endpoint,
        error: err.message,
      });
    }
    throw new ApiError(0, err.message || "Network connection error", "NETWORK_ERROR");
  }
}

// 1-Click Demo
export async function seedDemoData() {
  return fetchApi<{ status: string; message: string; job_id: number; candidates_count: number }>("/api/demo/seed", {
    method: "POST",
  });
}

// Jobs
export async function getJobs() {
  return fetchApi<any[]>("/api/jobs");
}

export async function getJob(id: number | string) {
  if (!id || id === "undefined" || id === "null" || (typeof id === "number" && isNaN(id))) {
    throw new ApiError(400, "A valid job ID is required", "INVALID_JOB_ID");
  }
  return fetchApi<any>(`/api/jobs/${id}`);
}

export async function createJob(data: any) {
  return fetchApi<any>("/api/jobs", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateJob(id: number, data: any) {
  return fetchApi<any>(`/api/jobs/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function duplicateJob(id: number) {
  return fetchApi<any>(`/api/jobs/${id}/duplicate`, {
    method: "POST",
  });
}

export async function archiveJob(id: number) {
  return fetchApi<any>(`/api/jobs/${id}/archive`, {
    method: "PUT",
  });
}

export async function deleteJob(id: number) {
  return fetchApi<any>(`/api/jobs/${id}`, {
    method: "DELETE",
  });
}

export async function analyzeRawJD(title: string, raw_description: string) {
  return fetchApi<any>("/api/jobs/analyze-raw", {
    method: "POST",
    body: JSON.stringify({ title, raw_description }),
  });
}

export async function updateJobRequirements(jobId: number, requirements: any[]) {
  return fetchApi<any>(`/api/jobs/${jobId}/requirements`, {
    method: "PUT",
    body: JSON.stringify(requirements),
  });
}

// Matching & Rankings
export async function runMatching(jobId: number) {
  return fetchApi<any>("/api/matching/run", {
    method: "POST",
    body: JSON.stringify({ job_id: jobId }),
  });
}

export async function getJobMatches(jobId: number) {
  return fetchApi<any[]>(`/api/matching/${jobId}`);
}

export async function updateWeights(jobId: number, weights: any) {
  return fetchApi<any>(`/api/matching/${jobId}/weights`, {
    method: "PUT",
    body: JSON.stringify(weights),
  });
}

// Candidates
export async function getCandidates(params: Record<string, any> = {}) {
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== "") {
      q.append(k, String(v));
    }
  }
  return fetchApi<any[]>(`/api/candidates?${q.toString()}`);
}

export async function getCandidate(id: number, jobId?: number) {
  const q = jobId ? `?job_id=${jobId}` : "";
  return fetchApi<any>(`/api/candidates/${id}${q}`);
}

// Compare
export async function compareCandidates(jobId: number, candidateIds: number[]) {
  return fetchApi<any>("/api/candidates/compare", {
    method: "POST",
    body: JSON.stringify({ job_id: jobId, candidate_ids: candidateIds }),
  });
}

// Copilot & Natural Filtering
export async function askCopilot(query: string, jobId?: number, candidateId?: number) {
  return fetchApi<any>("/api/copilot/query", {
    method: "POST",
    body: JSON.stringify({ query, job_id: jobId, candidate_id: candidateId }),
  });
}

export async function filterWithNaturalLanguage(jobId: number, query: string) {
  return fetchApi<any>("/api/copilot/filter", {
    method: "POST",
    body: JSON.stringify({ job_id: jobId, query }),
  });
}

// File Upload
export async function uploadResumes(files: FileList | File[]) {
  const formData = new FormData();
  for (let i = 0; i < files.length; i++) {
    formData.append("files", files[i]);
  }
  const response = await fetch(`${getApiBase()}/api/resumes/batch`, {
    method: "POST",
    body: formData,
  });
  if (!response.ok) {
    throw new Error("Failed to upload resumes.");
  }
  return response.json();
}

// Analytics & Reports
export async function getAnalyticsReportData(params: Record<string, any> = {}) {
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== "" && v !== "ALL") {
      q.append(k, String(v));
    }
  }
  return fetchApi<any>(`/api/reports/analytics/data?${q.toString()}`);
}

export function getReportDownloadUrl(format: "csv" | "pdf" | "docx", params: Record<string, any> = {}): string {
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== "" && v !== "ALL") {
      q.append(k, String(v));
    }
  }
  return `${getApiBase()}/api/reports/analytics/${format}?${q.toString()}`;
}

