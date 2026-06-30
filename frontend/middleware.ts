import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Cookie name is inlined: middleware runs on the edge runtime and must avoid
// importing Node-only modules (next/headers). Presence-only check — the backend
// is the source of truth and re-validates the JWT on every request.
const AUTH_COOKIE = "auth_token";

export function middleware(req: NextRequest) {
  const token = req.cookies.get(AUTH_COOKIE)?.value;
  if (!token) {
    const url = req.nextUrl.clone();
    url.pathname = "/login";
    url.searchParams.set("next", req.nextUrl.pathname);
    return NextResponse.redirect(url);
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*"],
};
