import { fetchLeads } from "@/lib/leads";
import { LeadsTable } from "@/components/leads-table";

export default async function DashboardPage() {
  const { items, total } = await fetchLeads();

  return (
    <div className="flex flex-col gap-6">
      <h2 className="text-xl font-semibold text-stone-900">
        Leads <span className="font-normal text-stone-500">({total})</span>
      </h2>

      {total === 0 ? (
        <div className="rounded-lg border border-stone-200 bg-white p-8 text-center text-stone-600 shadow-sm">
          No leads yet.
        </div>
      ) : (
        <LeadsTable leads={items} />
      )}
    </div>
  );
}
