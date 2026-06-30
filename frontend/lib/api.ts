/**
 * Typed API client for the FastAPI backend.
 *
 * Base URL resolution:
 *   - Browser  -> NEXT_PUBLIC_API_BASE_URL (default "/api", same-origin via nginx)
 *   - Server   -> BACKEND_INTERNAL_URL + "/api" (container-to-container)
 *
 * Errors are normalized to the backend's `{ error: { code, message } }` shape.
 */

export type LeadState = "PENDING" | "REACHED_OUT";

/** Mirrors the backend LeadState enum (OpenAPI schema is the source of truth). */
export const LEAD_STATES: LeadState[] = ["PENDING", "REACHED_OUT"];

export const LEAD_STATE_LABELS: Record<LeadState, string> = {
  PENDING: "Pending",
  REACHED_OUT: "Reached out",
};

export interface Lead {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  resume_filename: string;
  resume_content_type: string;
  state: LeadState;
  created_at: string;
  updated_at: string;
}

export interface LeadList {
  items: Lead[];
  total: number;
}

export class ApiError extends Error {
  code: string;
  status: number;
  constructor(code: string, message: string, status: number) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

export function apiBaseUrl(): string {
  if (typeof window === "undefined") {
    const internal = process.env.BACKEND_INTERNAL_URL ?? "http://localhost:8000";
    return `${internal}/api`;
  }
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api";
}

async function parseError(res: Response): Promise<ApiError> {
  let code = "HTTP_ERROR";
  let message = res.statusText;
  try {
    const body = await res.json();
    if (body?.error) {
      code = body.error.code ?? code;
      message = body.error.message ?? message;
    }
  } catch {
    /* non-JSON error body */
  }
  return new ApiError(code, message, res.status);
}

interface RequestOptions extends RequestInit {
  token?: string;
}

export async function apiFetch<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { token, headers, ...rest } = options;
  const res = await fetch(`${apiBaseUrl()}${path}`, {
    ...rest,
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    cache: "no-store",
  });
  if (!res.ok) throw await parseError(res);
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}
