import { type ProfileRating } from "@/lib/api";

const RATING_STYLES: Record<ProfileRating, string> = {
  strong: "border-green-200 bg-green-50 text-green-700",
  moderate: "border-amber-200 bg-amber-50 text-amber-700",
  weak: "border-stone-200 bg-stone-50 text-stone-600",
};

const RATING_LABELS: Record<ProfileRating, string> = {
  strong: "Strong",
  moderate: "Moderate",
  weak: "Weak",
};

export function ProfileScoreBadge({
  score,
  rating,
}: {
  score: number | null;
  rating: ProfileRating | null;
}) {
  if (score === null || rating === null) {
    return (
      <span className="inline-flex items-center rounded-full border border-dashed border-stone-300 px-2.5 py-0.5 text-xs font-medium text-stone-400">
        Analyzing…
      </span>
    );
  }
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-semibold ${RATING_STYLES[rating]}`}
    >
      {score} · {RATING_LABELS[rating]}
    </span>
  );
}
