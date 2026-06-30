/**
 * Server-side session helpers. The attorney JWT lives in an httpOnly cookie set
 * by the login server action; client code can never read it. Server components,
 * server actions, and route handlers read it here.
 */
import { cookies } from "next/headers";

export const AUTH_COOKIE = "auth_token";

export async function getToken(): Promise<string | null> {
  const store = await cookies();
  return store.get(AUTH_COOKIE)?.value ?? null;
}

export async function setToken(token: string, maxAgeSeconds: number): Promise<void> {
  const store = await cookies();
  store.set(AUTH_COOKIE, token, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: maxAgeSeconds,
  });
}

export async function clearToken(): Promise<void> {
  const store = await cookies();
  store.delete(AUTH_COOKIE);
}
