import Link from "next/link";

// Placeholder home. Replaced by the public lead form in Phase 3.
export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-xl flex-col justify-center gap-6 p-8">
      <h1 className="text-3xl font-semibold">Leads</h1>
      <p className="text-stone-600">
        Public prospect intake and internal lead management.
      </p>
      <div className="flex gap-4">
        <Link href="/apply" className="underline">
          Apply (public form)
        </Link>
        <Link href="/dashboard" className="underline">
          Attorney dashboard
        </Link>
      </div>
    </main>
  );
}
