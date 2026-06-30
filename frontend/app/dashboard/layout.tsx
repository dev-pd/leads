import { Navbar } from "@/components/navbar";
import { getCurrentUser } from "@/lib/current-user";

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const user = await getCurrentUser();

  return (
    <div className="min-h-screen bg-stone-50">
      <Navbar attorneyName={user?.name ?? null} />
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6">{children}</main>
    </div>
  );
}
