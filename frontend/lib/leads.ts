/**
 * Server-side data access for the guarded dashboard. Every call forwards the
 * attorney JWT from the cookie; a 401 (expired/invalid) bounces to /login.
 */
import { redirect } from "next/navigation";

import {
  ApiError,
  apiFetch,
  type Lead,
  type LeadList,
  type ProfileRating,
} from "@/lib/api";
import { getToken } from "@/lib/session";

async function authed<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = await getToken();
  if (!token) redirect("/login");
  try {
    return await apiFetch<T>(path, { ...init, token });
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) redirect("/login");
    throw err;
  }
}

export function fetchLeads({
  limit = 24,
  offset = 0,
  rating,
  sort = "recent",
}: {
  limit?: number;
  offset?: number;
  rating?: ProfileRating;
  sort?: "recent" | "score";
} = {}): Promise<LeadList> {
  const params = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
    sort,
  });
  if (rating) params.set("rating", rating);
  return authed<LeadList>(`/leads?${params.toString()}`);
}

export interface LeadStats {
  total: number;
  pending: number;
  reached_out: number;
}

export function fetchLeadStats(): Promise<LeadStats> {
  return authed<LeadStats>("/leads/stats");
}

export function fetchLead(id: string): Promise<Lead> {
  return authed<Lead>(`/leads/${id}`);
}
