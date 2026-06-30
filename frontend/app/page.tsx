import { LeadForm } from "@/components/lead-form";
import { Navbar } from "@/components/navbar";
import { getCurrentUser } from "@/lib/current-user";

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<{ auth?: string }>;
}) {
  const [user, sp] = await Promise.all([getCurrentUser(), searchParams]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-indigo-50/60 via-white to-white">
      <Navbar
        attorneyName={user?.name ?? null}
        openLoginInitially={sp.auth === "required"}
      />
      <main className="mx-auto grid max-w-6xl items-start gap-12 px-4 py-12 sm:px-6 md:grid-cols-2 md:py-20">
        <section className="flex flex-col justify-center">
          <span className="inline-flex w-fit items-center gap-2 rounded-full border border-indigo-200 bg-indigo-50 px-3 py-1 text-xs font-medium text-indigo-700">
            <span className="h-1.5 w-1.5 rounded-full bg-indigo-500" />
            Free case review
          </span>
          <h1 className="mt-5 text-4xl font-semibold tracking-tight text-stone-900 sm:text-5xl">
            Tell us about your case
          </h1>
          <p className="mt-4 max-w-md text-lg text-stone-600">
            Share a few details and attach your resume or CV. Our attorneys review
            every submission and reach out personally if it&apos;s a fit.
          </p>
          <ul className="mt-8 space-y-3 text-sm text-stone-600">
            {[
              "Reviewed by a licensed attorney",
              "Your information stays confidential",
              "A response within two business days",
            ].map((item) => (
              <li key={item} className="flex items-center gap-3">
                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-indigo-100 text-xs font-bold text-indigo-700">
                  ✓
                </span>
                {item}
              </li>
            ))}
          </ul>
        </section>

        <section className="flex flex-col justify-center">
          <LeadForm />
        </section>
      </main>
    </div>
  );
}
