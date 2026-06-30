"use client";

import Link from "next/link";
import { useState } from "react";

import { LoginModal } from "@/components/login-modal";
import { logoutAction } from "@/lib/auth-actions";

interface NavbarProps {
  attorneyName: string | null;
  /** Open the login modal on mount (e.g. redirected here needing auth). */
  openLoginInitially?: boolean;
}

export function Navbar({ attorneyName, openLoginInitially = false }: NavbarProps) {
  const [loginOpen, setLoginOpen] = useState(openLoginInitially);

  return (
    <header className="border-b border-stone-200 bg-white">
      <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-4">
        <Link href="/" className="font-semibold text-stone-900">
          Leads
        </Link>

        <nav className="flex items-center gap-3">
          {attorneyName ? (
            <>
              <Link
                href="/dashboard"
                className="text-sm font-medium text-stone-600 hover:text-stone-900"
              >
                Dashboard
              </Link>
              <span className="hidden text-sm text-stone-400 sm:inline">
                {attorneyName}
              </span>
              <form action={logoutAction}>
                <button
                  type="submit"
                  className="rounded-md border border-stone-300 px-3 py-1.5 text-sm font-medium text-stone-700 transition hover:bg-stone-50"
                >
                  Sign out
                </button>
              </form>
            </>
          ) : (
            <button
              type="button"
              onClick={() => setLoginOpen(true)}
              className="rounded-md bg-stone-900 px-3 py-1.5 text-sm font-medium text-white transition hover:bg-stone-800"
            >
              Attorney sign in
            </button>
          )}
        </nav>
      </div>

      {!attorneyName && (
        <LoginModal open={loginOpen} onClose={() => setLoginOpen(false)} />
      )}
    </header>
  );
}
