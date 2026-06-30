import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Inlined (not imported from lib/session) because the edge runtime can't load
// next/headers. Presence-only check; the backend re-validates the JWT.
const AUTH_COOKIE = "auth_token";

export function middleware(req: NextRequest) {
  const token = req.cookies.get(AUTH_COOKIE)?.value;
  if (!token) {
    // No login page — send them to the landing page and open the sign-in modal.
    const url = req.nextUrl.clone();
    url.pathname = "/";
    url.search = "auth=required";
    return NextResponse.redirect(url);
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*"],
};
