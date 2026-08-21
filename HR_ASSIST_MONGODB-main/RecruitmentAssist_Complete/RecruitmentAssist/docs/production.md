# Production topology and routing contract

## Topology

Production is a **single-origin Vercel deployment**:

```text
Browser
  |
  | https://<production-host>/
  v
Vercel
  |
  +-- /api/* ----------------------> api/index.py
  |                                     |
  |                                     v
  |                                  backend/app.py
  |                                     |
  |                                     +--> Flask blueprints
  |                                     +--> MongoDB
  |
  +-- /, /login, /dashboard, /jobs/1 -> frontend/build/index.html
```

The React application and Flask API therefore share one public origin. The React API client deliberately uses relative paths (`/api/...`), so no production API URL is hard-coded in the browser bundle.

The frontend's CRA `proxy` setting points to `http://127.0.0.1:5000`; that setting is **development-only** and is not the production routing mechanism.

## Production contract

`vercel.json` is the source of truth for the Vercel edge routing contract:

1. `/api/:path*` is matched first and rewritten to the Python function at `/api/index.py`.
2. Every non-API path is rewritten to `/index.html`, allowing React Router paths such as `/jobs/1` to load the application.
3. API requests must never fall through to the SPA rewrite.

The Python function imports the Flask application from `backend/app.py`.

Flask registers `/api/dashboard` as an authenticated JSON endpoint. Its authentication decorator returns `{"error":"Unauthorized"}` with HTTP 401 when no valid session token is present.

## Build contract

From the repository root:

```bash
npm run build
```

The root build script runs the frontend production build. Vercel publishes `frontend/build` as the static output while `/api/*` is handled by the Python function.

Required production environment variables must be configured in Vercel for the Flask process, including the MongoDB connection string and application secret. Do not commit `.env` values.

## Smoke test

After every production deployment:

```bash
python scripts/production_smoke_test.py https://<production-host>
```

The test verifies:

- `/` returns the React HTML document with HTTP 200.
- `/jobs/1` returns the React HTML document with HTTP 200 rather than a 404.
- unauthenticated `GET /api/dashboard` returns HTTP 401 with `application/json`.
- when `SMOKE_SESSION_TOKEN` is supplied, or when `SMOKE_USERNAME` and `SMOKE_PASSWORD` are supplied, authenticated `GET /api/dashboard` returns HTTP 200 JSON containing the dashboard `metrics` payload.

Example with a temporary smoke-test account:

```bash
SMOKE_USERNAME=smoke SMOKE_PASSWORD='***' \
python scripts/production_smoke_test.py https://<production-host>
```

Do not print or commit real production credentials or session tokens.
