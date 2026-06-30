# Frontend — Next.js app

App Router + TypeScript + Tailwind. Talks to the FastAPI backend through the
typed client in `lib/api.ts`.

## Layout
```
app/
  layout.tsx           root layout (Inter font, globals)
  page.tsx             landing
  apply/               public lead form (Phase 3)        — no auth
  login/               attorney login (Phase 4)
  dashboard/           leads table + detail (Phase 4)    — auth-guarded
components/             reusable UI
lib/
  api.ts               typed fetch client + ApiError + base-URL resolution
middleware.ts          guards /dashboard (Phase 4)
```

## Conventions
- **API base** comes from `lib/api.ts#apiBaseUrl()`: browser → `/api`
  (same-origin via nginx), server → `BACKEND_INTERNAL_URL`. Never hardcode URLs.
- **Forms**: react-hook-form + zod resolver. Mirror backend validation
  (names required, valid email, PDF only, ≤10MB).
- **Errors**: catch `ApiError`, show `error.message`. Don't swallow.
- **Auth**: attorney JWT from `POST /api/auth/login`, stored in an httpOnly
  cookie set by a Next server action; `middleware.ts` redirects unauthenticated
  `/dashboard` visitors to `/login`. Server components forward the token to the
  API; the public form sends no token.
- Keep server/client component split explicit (`"use client"` only when needed).

## Commands
- Dev: `npm run dev`  · Build: `npm run build`  · Types: `npm run typecheck`
