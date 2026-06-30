# Running locally

The whole stack runs in Docker. You need **Docker** with Compose v2 — nothing
else (no local Python or Node).

## 1. Configure environment

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

Edit `backend/.env` and set the values below. The seed attorney and JWT secret
are **required** (the app fails fast if missing — there are no insecure
in-source defaults). The two API keys are optional; leaving them empty disables
that feature gracefully.

| Variable | Required? | What to set |
|----------|-----------|-------------|
| `JWT_SECRET` | **yes** | any long random string |
| `ATTORNEY_EMAIL` / `ATTORNEY_PASSWORD` / `ATTORNEY_NAME` | **yes** | the internal login, seeded on boot |
| `RESEND_API_KEY` | optional | Resend key. Empty → emails are logged, not sent. |
| `EMAIL_FROM` | if email on | a verified Resend sender, e.g. `Firm <you@yourdomain.com>` |
| `NOTIFY_ATTORNEY_EMAIL` | if email on | inbox that receives the attorney notification |
| `ANTHROPIC_API_KEY` | optional | Anthropic API key. Empty → resume scoring is skipped. |
| `CLAUDE_MODEL` | optional | defaults to `claude-sonnet-5` |

The database, MinIO, storage backend, and upload limits already work out of the
box.

## 2. Start everything

```bash
make up          # or: docker compose up --build -d
```

Starts Postgres, MinIO, the FastAPI backend (runs migrations + seeds the
attorney on boot), the Next.js frontend, and an nginx reverse proxy.

| URL | What |
|-----|------|
| http://localhost | The app (public form + dashboard) |
| http://localhost/docs | Backend OpenAPI / Swagger UI |
| http://localhost/health | Health check |
| http://localhost:9001 | MinIO console (`minioadmin` / `minioadmin`) |

## 3. Walk the flow

1. Open http://localhost → fill the public form, attach a **PDF résumé**, submit
   (you get a confirmation toast).
2. Check the prospect + attorney inboxes (or `make backend-logs` if no email key
   is set).
3. Click **Sign in** (navbar) → log in with your `ATTORNEY_EMAIL` /
   `ATTORNEY_PASSWORD`.
4. The lead appears as **Pending / Analyzing…**; with an Anthropic key set it
   updates to a **fit score** within seconds (the page auto-refreshes).
5. Open the lead → read the AI summary + fit assessment, open the résumé, and
   click **Mark reached out** (state flips `PENDING → REACHED_OUT`).
6. Use the **rating filter** (Strong / Moderate / Weak) and pagination on the
   dashboard.

## Common commands

```bash
make help          # list all targets
make logs          # tail all logs
make backend-logs  # tail backend logs (see email + AI activity)
make test          # run the backend test suite
make fresh         # wipe volumes + rebuild from scratch (clean DB + storage)
make down          # stop (keeps data)
```

## Switching the storage backend

Resumes default to **MinIO** (S3-compatible). For plain local disk, set
`STORAGE_BACKEND=local` in `backend/.env` and restart — no code change.

## Troubleshooting

- **502 from nginx** — the backend is still booting or crashed; `make backend-logs`.
- **Emails not arriving** — confirm `RESEND_API_KEY` + a verified `EMAIL_FROM`;
  otherwise emails are only logged.
- **Resume not scored** — confirm `ANTHROPIC_API_KEY` is set; without it the
  lead stays "Analyzing…".
- **Port in use** — free `80`, `5432`, `9000`, or `9001`.
