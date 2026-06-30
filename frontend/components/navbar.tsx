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
    <>
    <header className="sticky top-0 z-40 border-b border-stone-200/80 bg-white/80 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        <Link href="/" className="flex items-center gap-2">
          <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-600 text-sm font-bold text-white">
            M
          </span>
          <span className="text-lg font-semibold tracking-tight text-stone-900">
            Meridian Law
          </span>
        </Link>

        <nav className="flex items-center gap-2">
          {attorneyName ? (
            <>
              <Link
                href="/dashboard"
                className="rounded-lg px-3 py-2 text-sm font-medium text-stone-600 transition hover:bg-stone-100 hover:text-stone-900"
              >
                Dashboard
              </Link>
              <form action={logoutAction}>
                <button
                  type="submit"
                  className="rounded-lg border border-stone-300 px-3 py-2 text-sm font-medium text-stone-700 transition hover:bg-stone-50"
                >
                  Sign out
                </button>
              </form>
            </>
          ) : (
            <button
              type="button"
              onClick={() => setLoginOpen(true)}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700"
            >
              Sign in
            </button>
          )}
        </nav>
      </div>
    </header>

    {!attorneyName && (
      <LoginModal open={loginOpen} onClose={() => setLoginOpen(false)} />
    )}
    </>
  );
}
