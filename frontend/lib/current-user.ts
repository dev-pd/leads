/** Server-side current-attorney lookup, used to render auth-aware navigation. */
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/session";

export interface CurrentUser {
  id: string;
  email: string;
  name: string;
}

export async function getCurrentUser(): Promise<CurrentUser | null> {
  const token = await getToken();
  if (!token) return null;
  try {
    return await apiFetch<CurrentUser>("/auth/me", { token });
  } catch {
    return null; // expired/invalid token -> treat as logged out
  }
}
