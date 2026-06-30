# Coding-agent usage

> Required writeup: tools used, what I delegated vs. wrote, and one place the
> agent produced wrong/subtly-bad code — how I caught it and fixed it.

## How I worked

I drove this project. I **planned it first** — turned the brief into a system
design, then **broke it into sub-plans / phases** (infra → backend core → APIs +
email + auth → public form → dashboard + auth → tests → docs), and worked them
in order, reviewing and verifying at each boundary. I made the architecture
calls myself: Postgres + Alembic over `create_all`, a `route → service →
repository → model` layering, a pluggable storage interface (local/MinIO), nginx
single-origin to avoid CORS, JWT behind one swappable dependency, and the async
"submit instantly, analyze in the background" pipeline.

**The AI resume-scoring feature was my idea, added after the base app was
working** — once the core CRUD + email + auth + dashboard were solid, I decided
the highest-value addition for an attorney was triage: parse the résumé, score
the prospect against a rubric, and surface the strongest leads. I specified the
parse-then-reason approach (pypdf for extraction, the LLM for judgment), the
explicit weighted rubric, the async pipeline with an "Analyzing…" state, and the
dashboard filter/score column. The agent implemented to that spec.

## Tools

- **Claude Code (Opus 4.8)** as the primary pair — I directed; it generated code,
  ran the stack, and helped debug.
- **Read-only sub-agents** for bounded fan-out (e.g. mining patterns, locating
  code) so the main thread stayed focused.

## What I delegated vs. wrote

- **Delegated** (under close review): boilerplate and well-specified modules —
  the storage backends, the email service, the Pydantic schemas, the Next.js
  form and table components, the test suite. I reviewed every file and ran it
  end-to-end rather than trusting it.
- **Wrote / hand-drove**: the architecture and all design decisions; the auth
  flow (httpOnly cookie + middleware + the cookie→Bearer résumé proxy); the
  state machine; the AI pipeline design (parse → rubric → async → defensive
  parsing); and the security hardening (removing hardcoded secrets so they're
  required from env). I was the main driver on anything load-bearing, and I
  edited agent output directly where it needed it.

## One place the agent produced subtly-bad code

The public form's résumé field validated with `z.instanceof(FileList)` at the
**module top level**. It compiled and type-checked fine — but `FileList` is a
browser-only global, and Next.js evaluates that module during **server-side
rendering**, where `FileList` is `undefined`. So the `/apply` page crashed with a
`ReferenceError` the moment it rendered on the server.

I caught it by **running it, not reading the diff** — `next build` and loading the
page surfaced the crash; reading the TypeScript would never have. I fixed it to
`z.custom<FileList>()` and moved the `instanceof FileList` check **inside the
refine callbacks**, which run only on the client at submit time. The takeaway,
which shaped how I worked: agent code that compiles and looks right still has to
be *run* — most of the real bugs only showed up when I booted the stack.

(A second class I caught by review: the agent left credential-shaped defaults in
the config — `attorney_password="changeme123"`, S3 keys defaulting to
`minioadmin`. I had those made **required from env** so no secrets live in
source.)

## Attribution

Per-file origin is tracked in [`../NOTES.md`](../NOTES.md). Representative,
cleaned-up prompts are in [`PROMPTS.md`](./PROMPTS.md). Agent-authored commits
carry a `Co-Authored-By: Claude` trailer; the planning, decisions, and reviews
were mine.
