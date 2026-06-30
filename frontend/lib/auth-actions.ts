"use server";

import { redirect } from "next/navigation";

import { apiBaseUrl } from "@/lib/api";
import { clearToken, setToken } from "@/lib/session";

export interface LoginState {
  ok?: boolean;
  error?: string;
}

const TOKEN_MAX_AGE = 60 * 60 * 24; // 24h, matches backend JWT expiry

// Returns a result instead of redirecting so the client can toast and navigate.
export async function loginAction(
  _prev: LoginState,
  formData: FormData,
): Promise<LoginState> {
  const email = String(formData.get("email") ?? "").trim();
  const password = String(formData.get("password") ?? "");
  if (!email || !password) {
    return { error: "Email and password are required" };
  }

  try {
    const res = await fetch(`${apiBaseUrl()}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
      cache: "no-store",
    });
    if (!res.ok) {
      const body = await res.json().catch(() => null);
      return { error: body?.error?.message ?? "Invalid email or password" };
    }
    const token = (await res.json()).access_token;
    await setToken(token, TOKEN_MAX_AGE);
  } catch {
    return { error: "Could not reach the server. Is the backend running?" };
  }
  return { ok: true };
}

export async function logoutAction(): Promise<void> {
  await clearToken();
  redirect("/");
}
