import Link from "next/link";

import { type Lead } from "@/lib/api";
import { LeadStateBadge } from "@/components/lead-state-badge";

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function LeadsTable({ leads }: { leads: Lead[] }) {
  return (
    <div className="overflow-x-auto rounded-lg border border-stone-200 bg-white shadow-sm">
      <table className="w-full border-collapse text-left text-sm">
        <thead>
          <tr className="border-b border-stone-200 text-xs font-medium uppercase tracking-wide text-stone-500">
            <th className="px-4 py-3">Name</th>
            <th className="px-4 py-3">Email</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Submitted</th>
            <th className="px-4 py-3 text-right">
              <span className="sr-only">Actions</span>
            </th>
          </tr>
        </thead>
        <tbody>
          {leads.map((lead) => (
            <tr
              key={lead.id}
              className="border-b border-stone-100 last:border-0 transition hover:bg-stone-50"
            >
              <td className="px-4 py-3 font-medium text-stone-900">
                <Link
                  href={`/dashboard/leads/${lead.id}`}
                  className="block focus:outline-none"
                >
                  {lead.first_name} {lead.last_name}
                </Link>
              </td>
              <td className="px-4 py-3 text-stone-600">{lead.email}</td>
              <td className="px-4 py-3">
                <LeadStateBadge state={lead.state} />
              </td>
              <td className="px-4 py-3 text-stone-600">
                {formatDate(lead.created_at)}
              </td>
              <td className="px-4 py-3 text-right">
                <Link
                  href={`/dashboard/leads/${lead.id}`}
                  className="text-sm font-medium text-stone-700 underline-offset-2 hover:underline"
                >
                  View
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
