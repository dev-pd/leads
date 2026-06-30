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
    <>
      <Navbar
        attorneyName={user?.name ?? null}
        openLoginInitially={sp.auth === "required"}
      />
      <main className="mx-auto grid max-w-5xl gap-10 px-4 py-12 md:grid-cols-2 md:py-20">
        <section className="flex flex-col justify-center">
          <h1 className="text-4xl font-semibold tracking-tight text-stone-900">
            Tell us about your case
          </h1>
          <p className="mt-4 text-lg text-stone-600">
            Share a few details and attach your resume or CV. Our attorneys review
            every submission and reach out personally if it&apos;s a fit.
          </p>
        </section>
        <section className="flex flex-col justify-center">
          <LeadForm />
        </section>
      </main>
    </>
  );
}
