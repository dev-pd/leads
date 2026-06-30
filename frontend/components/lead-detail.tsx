import Link from "next/link";

import { type Lead } from "@/lib/api";
import { LeadStateBadge } from "@/components/lead-state-badge";
import { StatusControl } from "@/components/status-control";

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export function LeadDetail({ lead }: { lead: Lead }) {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <Link
          href="/dashboard"
          className="text-sm font-medium text-stone-600 underline-offset-2 hover:underline"
        >
          ← Back to leads
        </Link>
      </div>

      <div className="rounded-xl border border-stone-200 bg-white p-6 shadow-sm sm:p-8">
        <div className="flex items-start justify-between gap-4">
          <div className="flex flex-col gap-1">
            <h2 className="text-2xl font-semibold text-stone-900">
              {lead.first_name} {lead.last_name}
            </h2>
            <a
              href={`mailto:${lead.email}`}
              className="text-sm text-stone-600 underline-offset-2 hover:underline"
            >
              {lead.email}
            </a>
          </div>
          <LeadStateBadge state={lead.state} />
        </div>

        <dl className="mt-6 grid grid-cols-1 gap-4 border-t border-stone-100 pt-6 sm:grid-cols-2">
          <div className="flex flex-col gap-1">
            <dt className="text-sm font-medium text-stone-500">Submitted</dt>
            <dd className="text-sm text-stone-900">
              {formatDate(lead.created_at)}
            </dd>
          </div>
          <div className="flex flex-col gap-1">
            <dt className="text-sm font-medium text-stone-500">Resume</dt>
            <dd className="text-sm">
              <a
                href={`/dashboard/leads/${lead.id}/resume`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 font-medium text-indigo-600 underline underline-offset-2 hover:text-indigo-700"
              >
                ↓ {lead.resume_filename}
              </a>
            </dd>
          </div>
        </dl>

        <div className="mt-6 border-t border-stone-100 pt-6">
          <StatusControl leadId={lead.id} state={lead.state} />
        </div>
      </div>
    </div>
  );
}
