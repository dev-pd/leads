import { LEAD_STATE_LABELS, type LeadState } from "@/lib/api";

const STATE_STYLES: Record<LeadState, string> = {
  PENDING: "border-amber-200 bg-amber-50 text-amber-700",
  REACHED_OUT: "border-green-200 bg-green-50 text-green-700",
};

export function LeadStateBadge({ state }: { state: LeadState }) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${STATE_STYLES[state]}`}
    >
      {LEAD_STATE_LABELS[state]}
    </span>
  );
}
