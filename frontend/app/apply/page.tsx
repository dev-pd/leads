import { LeadForm } from "@/components/lead-form";

export const metadata = {
  title: "Apply",
  description: "Submit your prospect application.",
};

export default function ApplyPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-xl flex-col justify-center gap-6 p-8">
      <header className="flex flex-col gap-2">
        <h1 className="text-3xl font-semibold text-stone-900">Prospect application</h1>
        <p className="text-stone-600">
          Tell us a little about yourself and attach your resume. Our team reviews
          every application and will reach out if it&apos;s a fit.
        </p>
      </header>
      <LeadForm />
    </main>
  );
}
