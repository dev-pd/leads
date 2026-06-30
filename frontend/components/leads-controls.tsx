import Link from "next/link";

import { type ProfileRating } from "@/lib/api";

type Rating = ProfileRating | "all";

const FILTERS: { key: Rating; label: string }[] = [
  { key: "all", label: "All" },
  { key: "strong", label: "Strong" },
  { key: "moderate", label: "Moderate" },
  { key: "weak", label: "Weak" },
];

function href(rating: Rating): string {
  return rating === "all" ? "/dashboard" : `/dashboard?rating=${rating}`;
}

export function LeadsControls({ rating }: { rating: Rating }) {
  return (
    <div className="flex items-center gap-1 rounded-lg border border-stone-200 bg-white p-1">
      {FILTERS.map((f) => {
        const active = f.key === rating;
        return (
          <Link
            key={f.key}
            href={href(f.key)}
            className={`rounded-md px-3 py-1.5 text-sm font-medium transition ${
              active
                ? "bg-indigo-600 text-white"
                : "text-stone-600 hover:bg-stone-100"
            }`}
          >
            {f.label}
          </Link>
        );
      })}
    </div>
  );
}
