import { type ProfileRating } from "@/lib/api";
import { fetchLeads, fetchLeadStats } from "@/lib/leads";
import { DashboardStats } from "@/components/dashboard-stats";
import { LeadsControls } from "@/components/leads-controls";
import { LeadsTable } from "@/components/leads-table";
import { Pagination } from "@/components/pagination";

const PAGE_SIZE = 24;
const RATINGS: ProfileRating[] = ["strong", "moderate", "weak"];

export default async function DashboardPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string; rating?: string }>;
}) {
  const sp = await searchParams;
  const page = Math.max(1, Number(sp.page) || 1);
  const rating = RATINGS.includes(sp.rating as ProfileRating)
    ? (sp.rating as ProfileRating)
    : undefined;

  const [stats, { items, total }] = await Promise.all([
    fetchLeadStats(),
    fetchLeads({ limit: PAGE_SIZE, offset: (page - 1) * PAGE_SIZE, rating }),
  ]);

  const query: Record<string, string> = rating ? { rating } : {};

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-stone-900">
          Leads
        </h1>
        <p className="mt-1 text-sm text-stone-500">
          Prospect submissions, AI-scored so you see the strongest first.
        </p>
      </div>

      {/* Global KPIs — always shown, not page/filter scoped */}
      <DashboardStats stats={stats} />

      <LeadsControls rating={rating ?? "all"} />

      {items.length === 0 ? (
        <div className="rounded-xl border border-dashed border-stone-300 bg-white p-12 text-center">
          <p className="text-sm font-medium text-stone-900">
            {rating ? "No leads match this filter" : "No leads yet"}
          </p>
          <p className="mt-1 text-sm text-stone-500">
            {rating
              ? "Try a different rating."
              : "New prospect submissions will appear here."}
          </p>
        </div>
      ) : (
        <>
          <LeadsTable leads={items} />
          <Pagination
            page={page}
            pageSize={PAGE_SIZE}
            total={total}
            query={query}
          />
        </>
      )}
    </div>
  );
}
