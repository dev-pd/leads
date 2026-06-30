"use server";

import { revalidatePath } from "next/cache";

import { ApiError, apiFetch, type LeadState } from "@/lib/api";
import { getToken } from "@/lib/session";

export interface UpdateResult {
  ok?: boolean;
  error?: string;
}

export async function updateLeadState(
  id: string,
  state: LeadState,
): Promise<UpdateResult> {
  const token = await getToken();
  if (!token) return { error: "Not authenticated" };
  try {
    await apiFetch(`/leads/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ state }),
      token,
    });
  } catch (err) {
    const message = err instanceof ApiError ? err.message : "Update failed";
    return { error: message };
  }
  revalidatePath("/dashboard");
  revalidatePath(`/dashboard/leads/${id}`);
  return { ok: true };
}
