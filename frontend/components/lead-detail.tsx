import Link from "next/link";

import { type Lead } from "@/lib/api";
import { LeadStateBadge } from "@/components/lead-state-badge";
import { StatusControl } from "@/components/status-control";
import { formatDateTime, initials } from "@/lib/format";

export function LeadDetail({ lead }: { lead: Lead }) {
  return (
    <div className="flex flex-col gap-6">
      <Link
        href="/dashboard"
        className="inline-flex w-fit items-center gap-1 text-sm font-medium text-stone-500 transition hover:text-stone-900"
      >
        ← Back to leads
      </Link>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Prospect */}
        <div className="md:col-span-2 rounded-xl border border-stone-200 bg-white p-6 shadow-sm sm:p-8">
          <div className="flex items-start gap-4">
            <span className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-lg font-semibold text-indigo-700">
              {initials(lead.first_name, lead.last_name)}
            </span>
            <div className="flex flex-1 flex-col gap-1">
              <div className="flex items-center justify-between gap-3">
                <h1 className="text-2xl font-semibold text-stone-900">
                  {lead.first_name} {lead.last_name}
                </h1>
                <LeadStateBadge state={lead.state} />
              </div>
              <a
                href={`mailto:${lead.email}`}
                className="w-fit text-sm text-indigo-600 underline-offset-2 hover:underline"
              >
                {lead.email}
              </a>
            </div>
          </div>

          <dl className="mt-8 grid grid-cols-1 gap-x-8 gap-y-6 border-t border-stone-100 pt-6 sm:grid-cols-2">
            <div>
              <dt className="text-xs font-medium uppercase tracking-wide text-stone-400">
                Submitted
              </dt>
              <dd className="mt-1 text-sm text-stone-900">
                {formatDateTime(lead.created_at)}
              </dd>
            </div>
            <div>
              <dt className="text-xs font-medium uppercase tracking-wide text-stone-400">
                Resume
              </dt>
              <dd className="mt-1">
                <a
                  href={`/dashboard/leads/${lead.id}/resume`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 rounded-lg border border-stone-200 bg-stone-50 px-3 py-2 text-sm font-medium text-stone-700 transition hover:border-indigo-200 hover:bg-indigo-50 hover:text-indigo-700"
                >
                  <span aria-hidden>📄</span>
                  {lead.resume_filename}
                  <span aria-hidden className="text-stone-400">↗</span>
                </a>
              </dd>
            </div>
          </dl>
        </div>

        {/* Actions */}
        <div className="rounded-xl border border-stone-200 bg-white p-6 shadow-sm">
          <h2 className="text-sm font-semibold text-stone-900">Outreach</h2>
          <p className="mt-1 text-sm text-stone-500">
            Update the lead once you&apos;ve reached out.
          </p>
          <div className="mt-4">
            <StatusControl leadId={lead.id} state={lead.state} />
          </div>
        </div>
      </div>
    </div>
  );
}
