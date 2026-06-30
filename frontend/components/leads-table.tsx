import Link from "next/link";

import { type Lead } from "@/lib/api";
import { LeadStateBadge } from "@/components/lead-state-badge";
import { ProfileScoreBadge } from "@/components/profile-score-badge";
import { formatRelative, initials } from "@/lib/format";

export function LeadsTable({ leads }: { leads: Lead[] }) {
  return (
    <div className="overflow-hidden rounded-xl border border-stone-200 bg-white shadow-sm">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-stone-200 bg-stone-50/60 text-xs font-medium uppercase tracking-wide text-stone-500">
            <th className="px-5 py-3 font-medium">Prospect</th>
            <th className="px-5 py-3 font-medium">Fit score</th>
            <th className="px-5 py-3 font-medium">Status</th>
            <th className="px-5 py-3 font-medium">Submitted</th>
            <th className="px-5 py-3" />
          </tr>
        </thead>
        <tbody>
          {leads.map((lead) => (
            <tr
              key={lead.id}
              className="group border-b border-stone-100 transition last:border-0 hover:bg-indigo-50/40"
            >
              <td className="px-5 py-3">
                <Link
                  href={`/dashboard/leads/${lead.id}`}
                  className="flex items-center gap-3"
                >
                  <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-xs font-semibold text-indigo-700">
                    {initials(lead.first_name, lead.last_name)}
                  </span>
                  <span className="flex min-w-0 flex-col">
                    <span className="font-medium text-stone-900">
                      {lead.first_name} {lead.last_name}
                    </span>
                    <span className="truncate text-xs text-stone-500">
                      {lead.email}
                    </span>
                  </span>
                </Link>
              </td>
              <td className="px-5 py-3">
                <ProfileScoreBadge
                  score={lead.profile_score}
                  rating={lead.profile_rating}
                />
              </td>
              <td className="px-5 py-3">
                <LeadStateBadge state={lead.state} />
              </td>
              <td className="px-5 py-3 text-stone-500">
                {formatRelative(lead.created_at)}
              </td>
              <td className="px-5 py-3 text-right">
                <Link
                  href={`/dashboard/leads/${lead.id}`}
                  className="text-sm font-semibold text-indigo-600 opacity-0 transition group-hover:opacity-100"
                >
                  View →
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
