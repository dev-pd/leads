import { type Lead } from "@/lib/api";

interface Stat {
  label: string;
  value: number;
  accent: string;
}

export function DashboardStats({ leads }: { leads: Lead[] }) {
  const pending = leads.filter((l) => l.state === "PENDING").length;
  const reachedOut = leads.filter((l) => l.state === "REACHED_OUT").length;

  const stats: Stat[] = [
    { label: "Total leads", value: leads.length, accent: "text-stone-900" },
    { label: "Pending", value: pending, accent: "text-amber-600" },
    { label: "Reached out", value: reachedOut, accent: "text-green-600" },
  ];

  return (
    <div className="grid grid-cols-3 gap-4">
      {stats.map((s) => (
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
