# Frontend — Next.js app

App Router + TypeScript + Tailwind. Talks to the FastAPI backend through the
typed client in `lib/api.ts`.

## Layout
```
app/
  layout.tsx                       root layout (Inter font, globals)
  page.tsx                         landing + public lead form  — no auth
  dashboard/                       auth-guarded
    layout.tsx                     navbar shell
    page.tsx                       leads table + global KPIs + pagination
    actions.ts                     server actions (state update)
    leads/[id]/page.tsx            lead detail + AI O-1 assessment card
    leads/[id]/resume/route.ts     cookie→Bearer résumé proxy (streams the PDF)
components/                        reusable UI (lead-form, leads-table,
                                   lead-detail, login-modal, profile-score-badge,
                                   pending-refresher, …)
lib/
  api.ts                           typed fetch client + ApiError + base-URL resolution
middleware.ts                      guards /dashboard
```
Attorney login is a **modal** (`components/login-modal.tsx`) opened from the
navbar — there is no `/login` route.

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
- **AI scoring is async:** a new lead has a null score while the background job
  runs. The detail page shows an "Analyzing…" state and `pending-refresher.tsx`
  polls until the score lands. Treat `profile_score === null` as "still
  analyzing", and label model output clearly as AI-generated.

## Commands
- Dev: `npm run dev`  · Build: `npm run build`  · Types: `npm run typecheck`
