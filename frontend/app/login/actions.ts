"use server";

import { redirect } from "next/navigation";

import { apiBaseUrl } from "@/lib/api";
import { clearToken, setToken } from "@/lib/session";

export interface LoginState {
  error?: string;
}

const TOKEN_MAX_AGE = 60 * 60 * 24; // 24h, matches backend JWT expiry

/** Server action: exchange credentials for a JWT and store it httpOnly. */
export async function loginAction(
  _prev: LoginState,
  formData: FormData,
): Promise<LoginState> {
  const email = String(formData.get("email") ?? "").trim();
  const password = String(formData.get("password") ?? "");
  if (!email || !password) {
    return { error: "Email and password are required" };
  }

  let token: string;
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
    token = (await res.json()).access_token;
  } catch {
    return { error: "Could not reach the server. Is the backend running?" };
  }

  await setToken(token, TOKEN_MAX_AGE);
  redirect("/dashboard");
}

export async function logoutAction(): Promise<void> {
  await clearToken();
  redirect("/login");
}
