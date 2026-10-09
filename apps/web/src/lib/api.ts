import type { Analytics, AskAnswer, BaiEvent, Calibration, Heatmap, Highlight, Session } from "./types";

let csrf: string | null = null;
export const setCsrf = (t: string | null) => {
  csrf = t;
};

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
  }
}

async function req<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  const method = (init.method ?? "GET").toUpperCase();
  if (csrf && !["GET", "HEAD", "OPTIONS"].includes(method)) headers.set("X-CSRF-Token", csrf);
  if (init.body && !(init.body instanceof FormData) && !headers.has("Content-Type"))
    headers.set("Content-Type", "application/json");
  const res = await fetch(path, { ...init, headers, credentials: "same-origin" });
  if (!res.ok) {
    let msg = res.statusText;
    try {
      const body = await res.json();
      msg = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail ?? body);
    } catch {
      /* not JSON */
    }
    throw new ApiError(res.status, msg);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  me: () => req<{ authenticated: boolean; auth_required: boolean; csrf: string | null }>("/api/auth/me"),
  login: (passphrase: string) =>
    req<{ authenticated: boolean; csrf: string | null }>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ passphrase }),
    }),
  logout: () => req("/api/auth/logout", { method: "POST" }),

  sessions: () => req<Session[]>("/api/sessions"),
  session: (id: string) => req<Session>(`/api/sessions/${id}`),
  patchSession: (id: string, body: { title?: string; player1?: string; player2?: string }) =>
    req<Session>(`/api/sessions/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
  deleteSession: (id: string) => req<void>(`/api/sessions/${id}`, { method: "DELETE" }),
  control: (id: string, action: "start" | "stop" | "reanalyse") =>
    req(`/api/sessions/${id}/${action}`, { method: "POST" }),
  youtube: (body: {
    url: string;
    title?: string;
    player1?: string;
    player2?: string;
    acknowledge_rights: boolean;
  }) => req<Session>("/api/sessions/youtube", { method: "POST", body: JSON.stringify(body) }),

  events: (id: string, q: Record<string, string | number> = {}) =>
    req<{ last_seq: number; events: BaiEvent[] }>(
      `/api/sessions/${id}/events?${new URLSearchParams(Object.entries(q).map(([k, v]) => [k, String(v)]))}`,
    ),
  analytics: (id: string) => req<Analytics>(`/api/sessions/${id}/analytics`),
  heatmap: (id: string, player: string, kind: string) =>
    req<Heatmap>(`/api/sessions/${id}/heatmap?player=${player}&kind=${kind}`),
  highlights: (id: string, k = 10, player?: string) =>
    req<{ highlights: Highlight[] }>(
      `/api/sessions/${id}/highlights?k=${k}${player ? `&player=${player}` : ""}`,
    ),
  calibrationProposal: (id: string, segment = 0) =>
    req<{
      frame: number;
      width: number;
      height: number;
      proposal: { points: Record<string, [number, number]>; score: number } | null;
      current: Calibration | null;
      reference_points: Record<string, [number, number]>;
    }>(`/api/sessions/${id}/calibration/proposal?segment=${segment}`),
  calibrate: (id: string, points: Record<string, [number, number]>) =>
    req<{ reprojection_error_px: number; n_points: number }>(`/api/sessions/${id}/calibration`, {
      method: "POST",
      body: JSON.stringify({ points }),
    }),
  correctWinner: (id: string, rally_event_id: string, winner: "P1" | "P2") =>
    req(`/api/sessions/${id}/corrections`, {
      method: "POST",
      body: JSON.stringify({ kind: "winner", rally_event_id, winner }),
    }),
  verifyEvent: (id: string, event_id: string, payload?: Record<string, unknown>) =>
    req(`/api/sessions/${id}/corrections`, {
      method: "POST",
      body: JSON.stringify({ kind: "verify", event_id, payload }),
    }),
  ask: (id: string, question: string, history: { role: string; content: string }[]) =>
    req<AskAnswer>(`/api/sessions/${id}/ask`, {
      method: "POST",
      body: JSON.stringify({ question, history }),
    }),
  askProvider: (id: string) =>
    req<{ available: boolean; provider: string | null; model: string | null }>(
      `/api/sessions/${id}/ask/provider`,
    ),
  system: () => req<Record<string, any>>("/api/system"),
  models: () => req<Record<string, any>[]>("/api/models"),
};

/** Upload with progress (fetch has no upload progress; XHR does). */
export function uploadVideo(
  form: FormData,
  onProgress: (fraction: number) => void,
): { promise: Promise<Session>; abort: () => void } {
  const xhr = new XMLHttpRequest();
  const promise = new Promise<Session>((resolve, reject) => {
    xhr.open("POST", "/api/sessions");
    xhr.withCredentials = true;
    if (csrf) xhr.setRequestHeader("X-CSRF-Token", csrf);
    xhr.upload.onprogress = (e) => e.lengthComputable && onProgress(e.loaded / e.total);
    xhr.onload = () => {
      try {
        const body = JSON.parse(xhr.responseText);
        if (xhr.status >= 200 && xhr.status < 300) resolve(body as Session);
        else
          reject(new ApiError(xhr.status, typeof body.detail === "string" ? body.detail : "Upload failed"));
      } catch {
        reject(new ApiError(xhr.status, "Upload failed"));
      }
    };
    xhr.onerror = () =>
      reject(new ApiError(0, "The upload was interrupted — check your connection and try again"));
    xhr.send(form);
  });
  return { promise, abort: () => xhr.abort() };
}

export const exportUrl = (id: string, kind: string) => `/api/sessions/${id}/exports/${kind}`;
export const hlsUrl = (id: string) => `/api/sessions/${id}/hls/index.m3u8`;
