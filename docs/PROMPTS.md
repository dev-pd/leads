# Prompt log — representative excerpts

A curated, cleaned-up sample of the prompts I used to drive the build. They show
the arc: I planned and decomposed the work, delegated well-scoped pieces, made
the design calls, and added the AI feature myself after the core app worked.

---

## 1. Planning & decomposition (me → agent)

> "Build a leads app: FastAPI + Next.js. Public form (first name, last name,
> email, résumé PDF) → store it → email both the prospect and an internal
> attorney. Plus an auth-guarded internal dashboard listing every lead, each
> with a state that starts PENDING and the attorney moves to REACHED_OUT.
> Production-shaped repo.
>
> Before writing anything: produce a system design, then break it into phases I
> can review one at a time. Recommend the stack and call out the decisions
> (DB, storage, email, auth) — I'll approve before you build."

Decisions I made off that: Postgres + Alembic, a storage interface (local/MinIO),
Resend for email, JWT auth, nginx single-origin. The agent then worked the phases
I approved.

---

## 2. A delegated, well-specified module (me → agent)

> "Build the pluggable file storage. A `StorageBackend` interface
> (`put`/`get`/`delete`) with two implementations: `LocalDiskBackend` (default,
> zero-infra) and `S3Backend` (boto3, works against MinIO locally and AWS S3 in
> prod — same code). Pick the backend from one env var. Store only the storage
> key + content-type in the DB, never the bytes. App code must never import
> boto3 or touch the filesystem directly."

---

## 3. Backend layering I insisted on (me → agent)

> "Refactor so all DB queries live in a repository layer. `route → service →
> repository → model`: routes parse/validate only, services hold the domain
> rules, repositories own every query — services should never touch the session
> directly. Add `LeadRepository` and `UserRepository`, inject them as FastAPI
> dependencies."

---

## 4. The AI feature — my idea, after the app worked (me → agent)

> "The core app is solid. The most valuable thing I can add for an attorney is
> triage: when a résumé comes in, parse it and score the prospect so they see
> who's worth pursuing first.
>
> Design it like this: pypdf extracts the résumé text and we store it; pass that
> text to the Anthropic API, which returns a fit score, a rating
> (strong/moderate/weak), a short summary, and strengths/concerns. Score against
> an **explicit weighted rubric** — keep the prompt in its own versioned file.
> Run it **async** after submission so the prospect never waits, and show an
> 'Analyzing…' state that auto-updates. Use Sonnet (cheap), make the model
> configurable, and parse the response defensively so a prompt/model change can't
> crash the flow. On the dashboard, add a fit-score column and a filter by
> rating."

Follow-up I gave when I wanted the extraction explicit:

> "Have the parser (pypdf) extract and store the text, then pass that to the LLM
> for understanding + scoring — with a fallback to sending the PDF itself if it's
> a scanned image with no text layer."

---

## 5. Debugging — caught by running it (me ↔ agent)

> me: "The `/apply` page is crashing on load. Figure out why and fix it."

→ Root cause: `z.instanceof(FileList)` ran at module load, but `FileList` is
undefined during Next.js SSR. Fixed to `z.custom<FileList>()` with the
`instanceof` check moved inside the client-only refine callbacks. (Full writeup
in `AGENT_USAGE.md`.)

---

## 6. Hardening I drove on review (me → agent)

> "Config shouldn't ship credential-shaped defaults — `attorney_password =
> 'changeme123'`, S3 keys defaulting to `minioadmin`, an in-source JWT secret.
> Make the secrets and seed values **required from env**; no hardcoded values in
> source. Then audit the rest of the code for the same pattern."
