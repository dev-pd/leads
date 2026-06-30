/**
 * Server-side data access for the guarded dashboard. Every call forwards the
 * attorney JWT from the cookie; a 401 (expired/invalid) bounces to /login.
 */
import { redirect } from "next/navigation";

import { ApiError, apiFetch, type Lead, type LeadList } from "@/lib/api";
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

export function fetchLeads(): Promise<LeadList> {
  return authed<LeadList>("/leads");
}

export function fetchLead(id: string): Promise<Lead> {
  return authed<Lead>(`/leads/${id}`);
}
