import Link from "next/link";

interface PaginationProps {
  page: number;
  pageSize: number;
  total: number;
  /** Extra query params to preserve across page links (rating, sort). */
  query?: Record<string, string>;
}

export function Pagination({ page, pageSize, total, query = {} }: PaginationProps) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const from = total === 0 ? 0 : (page - 1) * pageSize + 1;
  const to = Math.min(page * pageSize, total);

  const href = (p: number) => {
    const params = new URLSearchParams(query);
    if (p > 1) params.set("page", String(p));
    const qs = params.toString();
    return qs ? `/dashboard?${qs}` : "/dashboard";
  };

  const linkClass =
    "rounded-lg border border-stone-300 px-3 py-1.5 text-sm font-medium text-stone-700 transition hover:bg-stone-50";
  const disabledClass =
    "rounded-lg border border-stone-200 px-3 py-1.5 text-sm font-medium text-stone-300";

  return (
    <div className="flex items-center justify-between">
      <p className="text-sm text-stone-500">
        Showing <span className="font-medium text-stone-700">{from}</span>–
        <span className="font-medium text-stone-700">{to}</span> of{" "}
        <span className="font-medium text-stone-700">{total}</span>
      </p>
      <div className="flex items-center gap-3">
        <span className="text-sm text-stone-500">
          Page <span className="font-medium text-stone-700">{page}</span> of{" "}
          <span className="font-medium text-stone-700">{totalPages}</span>
        </span>
        {page > 1 ? (
          <Link href={href(page - 1)} className={linkClass}>
            Previous
          </Link>
        ) : (
          <span className={disabledClass}>Previous</span>
        )}
        {page < totalPages ? (
          <Link href={href(page + 1)} className={linkClass}>
            Next
          </Link>
        ) : (
          <span className={disabledClass}>Next</span>
        )}
      </div>
    </div>
  );
}
