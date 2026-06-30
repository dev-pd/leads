import { LoginForm } from "@/components/login-form";

export const metadata = {
  title: "Sign in",
  description: "Attorney sign in for the leads dashboard.",
};

export default function LoginPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-sm flex-col justify-center gap-6 p-8">
      <header className="flex flex-col gap-2">
        <h1 className="text-3xl font-semibold text-stone-900">Sign in</h1>
        <p className="text-stone-600">
          Attorney access to the leads dashboard.
        </p>
      </header>
      <LoginForm />
    </main>
  );
}
