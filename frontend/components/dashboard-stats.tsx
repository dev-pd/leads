import { type LeadStats } from "@/lib/leads";

interface Stat {
  label: string;
  value: number;
  accent: string;
}

export function DashboardStats({ stats }: { stats: LeadStats }) {
  const cards: Stat[] = [
    { label: "Total leads", value: stats.total, accent: "text-stone-900" },
    { label: "Pending", value: stats.pending, accent: "text-amber-600" },
    { label: "Reached out", value: stats.reached_out, accent: "text-green-600" },
  ];

  return (
    <div className="grid grid-cols-3 gap-4">
      {cards.map((s) => (
        <div
          key={s.label}
          className="rounded-xl border border-stone-200 bg-white px-5 py-4 shadow-sm"
        >
          <p className="text-sm text-stone-500">{s.label}</p>
          <p className={`mt-1 text-3xl font-semibold ${s.accent}`}>{s.value}</p>
        </div>
      ))}
    </div>
  );
}
