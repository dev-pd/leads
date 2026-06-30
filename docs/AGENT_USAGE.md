# Coding-agent usage

> Writeup: tools used, what I delegated vs. wrote, and one place the agent
> produced subtly-bad code — how I caught and fixed it. (½ page.)

## How I worked

I drove the project. I planned it first, broke it into phases (infra → backend
core → APIs + email + auth → public form → dashboard + auth → tests → docs), and
worked them in order, reviewing and booting the stack at each boundary. The
architecture calls were mine: Postgres + Alembic (not `create_all`), a `route →
service → repository → model` layering, a pluggable storage interface
(local/MinIO), nginx single-origin to avoid CORS, JWT behind one swappable
dependency, and the "submit instantly, analyze in the background" pipeline. The
**AI résumé-scoring feature was my idea, added after the base app worked** — I
specified the parse-then-reason approach (pypdf extracts, the LLM judges), the
weighted O-1 rubric, the async pipeline with an "Analyzing…" state, and the
dashboard score column; the agent implemented to that spec.

## Tools

- **Claude Code (Opus 4.8)** as the primary pair — I directed; it generated
  code, ran the stack, and helped debug.
- Read-only sub-agents for bounded fan-out (locating code, mining patterns).

## Delegated vs. wrote

- **Delegated, under close review:** boilerplate and well-specified modules —
  storage backends, email service, Pydantic schemas, the Next.js form and table,
  the test suite. I reviewed every file and ran it end-to-end.
- **Hand-drove:** the architecture and all design decisions, the auth flow
  (httpOnly cookie + middleware + cookie→Bearer résumé proxy), the state machine,
  the AI pipeline design, and the security hardening (secrets required from env,
  no credential defaults in source).

## One place the agent produced subtly-bad code

For the résumé assessment the agent parsed the model's reply with a regex +
`json.loads`. It compiled, **passed the test suite, and worked for most
résumés** — but it broke whenever a string value (e.g. the summary) contained an
unescaped double-quote, raising `JSONDecodeError`. The lead then sat stuck
"Analyzing…" with a null score. Because it was input-dependent it was
intermittent — exactly the kind of bug a green test run hides.

I caught it in the **backend logs** (`resume_assessment_failed`,
`JSONDecodeError: Expecting ',' delimiter`) after a real submission stalled, not
from reading the diff. The fix was to stop hand-parsing model text: I switched to
a **forced `record_assessment` tool call**, so the API validates the output
against a schema and hands back guaranteed-valid JSON. (Earlier I caught a
similar class by review — `z.instanceof(FileList)` at a module top level crashed
Next SSR, and credential-shaped config defaults that I made required from env.)
The lesson that shaped my workflow: agent code that compiles and passes tests
still has to be *run on real input* — most real bugs only showed up live.

## Attribution

Per-file origin is in [`../NOTES.md`](../NOTES.md); representative prompts in
[`PROMPTS.md`](./PROMPTS.md). Agent-authored commits carry a `Co-Authored-By:
Claude` trailer; the planning, decisions, and reviews were mine.
