# ModelForge — combined app

This app is `model_forge_v2`'s backend paired with `new-design-master`'s
frontend. Nothing else was redesigned — the only changes made were the ones
needed to connect the two:

1. **`backend/app/core/config.py`** — added `http://localhost:3000` (the
   Next.js dev port) to `cors_origins`, alongside the existing
   `http://localhost:5173` default. Same one-line change mirrored in
   `backend/.env.example`.
2. **`frontend/next.config.ts`** — added a `rewrites()` rule so calls to
   `/api/:path*` are forwarded to the FastAPI backend
   (`MODELFORGE_BACKEND_URL`, default `http://localhost:8000`). This plays
   the same role the old frontend's `vite.config.ts` `server.proxy` did.
3. **`frontend/src/lib/modelforge-api.ts`** (new file) — a small client for
   the backend's `POST /api/v1/complete`, `GET /api/v1/models`, and
   `GET /api/v1/system/status`, in the same shape as
   `model_forge_v2/frontend/src/services/api.ts`.
4. **`frontend/src/hooks/use-modelforge.ts`** — `sendMessage`'s freeform
   chat path now calls the real backend (`modelforgeApi.complete`) instead
   of returning a canned string. Everything else in this hook (the four
   scripted "demo scenario" walkthroughs, GPU/heartbeat simulation, model
   card animation) is untouched.
5. **`frontend/src/components/gen-mode/index.tsx` and `workspace.tsx`** —
   Gen Mode's prompt bar previously had no `onClick`/state wiring at all
   (a static mockup with one hard-coded example exchange). It now uses the
   hook above, so typing a prompt and pressing "Generate" actually sends it
   to ModelForge and renders the real answer. Layout/styling classes are
   unchanged; only the data is now live.

Dev Mode (`src/components/dev-mode/*`) and the demo scenarios in the Gen
Mode sidebar are unchanged — they're self-contained UI showcases with no
backend equivalent to connect to.

## Running it locally

**Backend** (FastAPI, seeded with mock providers/models — no external API
keys needed):

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
python -m app.seed            # loads demo providers/models/policies
uvicorn app.main:app --reload # http://localhost:8000/docs
```

**Frontend** (Next.js):

```bash
cd frontend
npm install
npm run dev                   # http://localhost:3000
```

Open http://localhost:3000, switch to **Gen Mode** in the top nav, and send
a prompt — it's routed through the real ModelForge backend (task
classification → policy-filtered ranking → execution with fallback) and the
router status / model badge reflect whatever the backend actually picked.

If the backend runs somewhere other than `http://localhost:8000`, set
`MODELFORGE_BACKEND_URL` before starting the frontend.
