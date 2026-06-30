import { fetchLeads } from "@/lib/leads";
import { DashboardStats } from "@/components/dashboard-stats";
import { LeadsTable } from "@/components/leads-table";

export default async function DashboardPage() {
  const { items, total } = await fetchLeads();

  return (
    <div className="flex flex-col gap-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-stone-900">
          Leads
        </h1>
        <p className="mt-1 text-sm text-stone-500">
          Prospect submissions and their outreach status.
        </p>
      </div>

      {total === 0 ? (
        <div className="rounded-xl border border-dashed border-stone-300 bg-white p-12 text-center">
          <p className="text-sm font-medium text-stone-900">No leads yet</p>
          <p className="mt-1 text-sm text-stone-500">
            New prospect submissions will appear here.
          </p>
        </div>
      ) : (
        <>
          <DashboardStats leads={items} />
          <LeadsTable leads={items} />
        </>
      )}
    </div>
  );
}
