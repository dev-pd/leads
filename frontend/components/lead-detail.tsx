import Link from "next/link";

import { type Lead } from "@/lib/api";
import { LeadStateBadge } from "@/components/lead-state-badge";
import { ProfileScoreBadge } from "@/components/profile-score-badge";
import { StatusControl } from "@/components/status-control";
import { PendingRefresher } from "@/components/pending-refresher";
import { Spinner } from "@/components/spinner";
import { formatDateTime, initials } from "@/lib/format";

function Card({
  title,
  children,
  className = "",
}: {
  title?: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={`rounded-xl border border-stone-200 bg-white p-6 shadow-sm ${className}`}
    >
      {title && (
        <h2 className="mb-4 text-sm font-semibold text-stone-900">{title}</h2>
      )}
      {children}
    </div>
  );
}

/** Sparkles mark — signals AI-generated content to the attorney. */
function AiSparkles({ className = "" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="currentColor"
      aria-hidden="true"
      className={className}
    >
      <path d="M12 2.5l1.6 4.3a4 4 0 002.4 2.4l4.3 1.6-4.3 1.6a4 4 0 00-2.4 2.4L12 19.1l-1.6-4.3a4 4 0 00-2.4-2.4L3.7 10.8l4.3-1.6a4 4 0 002.4-2.4L12 2.5z" />
      <path d="M19 14.5l.7 1.9a2 2 0 001.2 1.2l1.9.7-1.9.7a2 2 0 00-1.2 1.2l-.7 1.9-.7-1.9a2 2 0 00-1.2-1.2l-1.9-.7 1.9-.7a2 2 0 001.2-1.2l.7-1.9z" />
    </svg>
  );
}

function Bullets({ items, color }: { items: string[]; color: string }) {
  return (
    <ul className="space-y-1.5 text-sm text-stone-700">
      {items.map((it, i) => (
        <li key={i} className="flex gap-2">
          <span className={`mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full ${color}`} />
          {it}
        </li>
      ))}
    </ul>
  );
}

export function LeadDetail({ lead }: { lead: Lead }) {
  const reachedOut = lead.state === "REACHED_OUT";
  const analyzing = lead.profile_score === null;
  const a = lead.profile_assessment;

  return (
    <div className="flex flex-col gap-6">
      {analyzing && <PendingRefresher />}

      <Link
        href="/dashboard"
        className="inline-flex w-fit items-center gap-1 text-sm font-medium text-stone-500 transition hover:text-stone-900"
      >
        ← Back to leads
      </Link>

      {/* Header */}
      <Card>
        <div className="flex items-start gap-4">
          <span className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-lg font-semibold text-indigo-700">
            {initials(lead.first_name, lead.last_name)}
          </span>
          <div className="flex flex-1 flex-col gap-1">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h1 className="text-2xl font-semibold text-stone-900">
                {lead.first_name} {lead.last_name}
              </h1>
              <div className="flex items-center gap-2">
                <ProfileScoreBadge
                  score={lead.profile_score}
                  rating={lead.profile_rating}
                />
                <LeadStateBadge state={lead.state} />
              </div>
            </div>
            <a
              href={`mailto:${lead.email}`}
              className="w-fit text-sm text-indigo-600 underline-offset-2 hover:underline"
            >
              {lead.email}
            </a>
          </div>
        </div>
      </Card>

      {analyzing && (
        <div className="flex items-center gap-3 rounded-xl border border-indigo-200 bg-indigo-50 px-5 py-4 text-sm text-indigo-700">
          <Spinner className="text-indigo-600" />
          Generating the AI profile from the resume… this page updates
          automatically.
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="flex flex-col gap-6 lg:col-span-2">
          {/* AI fit assessment */}
          {lead.profile_score !== null && (
            <Card>
              <div className="mb-1 flex items-center gap-2">
                <span className="flex h-6 w-6 items-center justify-center rounded-md bg-indigo-100 text-indigo-600">
                  <AiSparkles className="h-3.5 w-3.5" />
                </span>
                <h2 className="text-sm font-semibold text-stone-900">
                  O-1 candidacy assessment
                </h2>
                <span className="inline-flex items-center gap-1 rounded-full bg-indigo-50 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-indigo-600">
                  <AiSparkles className="h-2.5 w-2.5" />
                  AI generated
                </span>
              </div>
              <p className="mb-4 text-xs text-stone-500">
                Scored against the O-1 extraordinary-ability criteria.
              </p>
              {lead.resume_summary && (
                <p className="mb-5 text-sm leading-relaxed text-stone-700">
                  {lead.resume_summary}
                </p>
              )}
              <div className="flex items-baseline gap-3">
                <span className="text-4xl font-semibold text-stone-900">
                  {lead.profile_score}
                </span>
                <span className="text-sm text-stone-500">/ 100</span>
                <ProfileScoreBadge
                  score={lead.profile_score}
                  rating={lead.profile_rating}
                />
              </div>
              {a?.rationale && (
                <p className="mt-3 text-sm text-stone-600">{a.rationale}</p>
              )}
              {(a?.strengths.length || a?.concerns.length) && (
                <div className="mt-5 grid gap-5 sm:grid-cols-2">
                  {a.strengths.length > 0 && (
                    <div>
                      <p className="mb-2 text-xs font-medium uppercase tracking-wide text-green-600">
                        Strengths
                      </p>
                      <Bullets items={a.strengths} color="bg-green-500" />
                    </div>
                  )}
                  {a.concerns.length > 0 && (
                    <div>
                      <p className="mb-2 text-xs font-medium uppercase tracking-wide text-amber-600">
                        Concerns
                      </p>
                      <Bullets items={a.concerns} color="bg-amber-500" />
                    </div>
                  )}
                </div>
              )}
            </Card>
          )}

        </div>

        {/* Activity + action */}
        <Card className="self-start">
          <a
            href={`/dashboard/leads/${lead.id}/resume`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700"
          >
            📄 Open résumé ↗
          </a>

          <h2 className="mb-4 mt-6 text-sm font-semibold text-stone-900">
            Activity
          </h2>
          <ol className="space-y-4">
            <li className="flex gap-3">
              <span className="mt-1 h-2.5 w-2.5 shrink-0 rounded-full bg-green-500" />
              <div>
                <p className="text-sm font-medium text-stone-900">
                  Application received
                </p>
                <p className="text-xs text-stone-500">
                  {formatDateTime(lead.created_at)}
                </p>
              </div>
            </li>
            <li className="flex gap-3">
              <span
                className={`mt-1 h-2.5 w-2.5 shrink-0 rounded-full ${
                  reachedOut ? "bg-green-500" : "border-2 border-stone-300 bg-white"
                }`}
              />
              <div>
                <p className="text-sm font-medium text-stone-900">
                  Marked reached out
                </p>
                <p className="text-xs text-stone-500">
                  {lead.reached_out_at
                    ? formatDateTime(lead.reached_out_at)
                    : "Not yet"}
                </p>
              </div>
            </li>
          </ol>

          {!reachedOut && (
            <div className="mt-6 border-t border-stone-100 pt-6">
              <p className="mb-3 text-xs font-medium uppercase tracking-wide text-stone-400">
                Update status
              </p>
              <StatusControl leadId={lead.id} state={lead.state} />
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
