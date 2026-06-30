"use client";

import { useState, useTransition } from "react";
import { toast } from "sonner";

import {
  LEAD_STATES,
  LEAD_STATE_LABELS,
  type LeadState,
} from "@/lib/api";
import { updateLeadState } from "@/app/dashboard/actions";
import { Spinner } from "@/components/spinner";

interface StatusControlProps {
  leadId: string;
  state: LeadState;
}

export function StatusControl({ leadId, state }: StatusControlProps) {
  const [selected, setSelected] = useState<LeadState>(state);
  const [pending, startTransition] = useTransition();

  const terminal = state === "REACHED_OUT";

  function onUpdate() {
    startTransition(async () => {
      const result = await updateLeadState(leadId, selected);
      if (result.error) {
        toast.error(result.error);
      } else {
        toast.success(`Status updated to ${LEAD_STATE_LABELS[selected]}`);
      }
    });
  }

  if (terminal) {
    return (
      <div className="rounded-lg border border-green-200 bg-green-50 px-3 py-3 text-sm text-green-700">
        ✓ This lead has been reached out to — status is final.
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      <select
        id="lead-status"
        aria-label="Lead status"
        value={selected}
        disabled={pending}
        onChange={(e) => setSelected(e.target.value as LeadState)}
        className="w-full rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm text-stone-900 shadow-sm outline-none transition focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 disabled:opacity-60"
      >
        {LEAD_STATES.map((s) => (
          <option key={s} value={s}>
            {LEAD_STATE_LABELS[s]}
          </option>
        ))}
      </select>
      <button
        type="button"
        onClick={onUpdate}
        disabled={pending || selected === state}
        className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {pending && <Spinner />}
        {pending ? "Updating…" : "Update status"}
      </button>
    </div>
  );
}
