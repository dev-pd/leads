/**
 * Resume download proxy.
 *
 * The backend guards the resume route with `Authorization: Bearer`, but a plain
 * browser link can't send that header. So this same-origin route reads the
 * httpOnly cookie server-side, attaches the Bearer token, and streams the PDF
 * back. The dashboard links to `/dashboard/leads/{id}/resume`.
 */
import type { NextRequest } from "next/server";

import { apiBaseUrl } from "@/lib/api";
import { getToken } from "@/lib/session";

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  const token = await getToken();
  if (!token) return new Response("Unauthorized", { status: 401 });

  const { id } = await params;
  const upstream = await fetch(`${apiBaseUrl()}/leads/${id}/resume`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });

  if (!upstream.ok) {
    return new Response("Resume not found", { status: upstream.status });
  }

  return new Response(upstream.body, {
    status: 200,
    headers: {
      "Content-Type": upstream.headers.get("content-type") ?? "application/pdf",
      "Content-Disposition":
        upstream.headers.get("content-disposition") ?? "inline",
    },
  });
}
