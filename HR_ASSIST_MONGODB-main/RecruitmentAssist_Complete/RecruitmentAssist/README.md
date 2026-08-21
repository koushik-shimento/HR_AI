# Recruitment Assist — React + Flask

## Production deployment (Vercel)

Production uses a **single public origin** for both React and Flask:

```text
Browser
   |
   v
Vercel
   |-- /api/* -----------------> api/index.py -> backend/app.py -> MongoDB
   |
   `-- /* ---------------------> frontend/build/index.html
```

The production routing contract is defined in `vercel.json`:

- `/api/:path*` is rewritten first to the Python function `api/index.py`.
- Every other path is rewritten to `/index.html` so React Router paths such as `/jobs/1` work on direct navigation or refresh.
- API requests therefore cannot fall through to the React SPA fallback.

The React API client intentionally uses same-origin relative paths such as `/api/dashboard`. The `frontend/package.json` `proxy` value is only for the local CRA development server and must not be relied on in production.

### Deploy

From `HR_ASSIST_MONGODB-main/RecruitmentAssist_Complete/RecruitmentAssist/`:

```bash
npm install
npm run build
```

Vercel runs the same root build command and publishes `frontend/build`. The Flask API is deployed as the Python function under `api/`.

Configure the production environment variables in Vercel, including the MongoDB connection string and `SECRET_KEY`. Never commit `.env` values.

### Production smoke test

Run this against the deployed URL after every deployment:

```bash
python scripts/production_smoke_test.py https://<production-host>
```

It verifies:

1. `GET /` returns React HTML with HTTP 200.
2. `GET /jobs/1` returns React HTML with HTTP 200.
3. Unauthenticated `GET /api/dashboard` returns HTTP 401 with `application/json` and an `Unauthorized` error.
4. If `SMOKE_SESSION_TOKEN` is supplied, authenticated `GET /api/dashboard` returns HTTP 200 JSON containing the dashboard `metrics` payload.
5. Alternatively, `SMOKE_USERNAME` and `SMOKE_PASSWORD` can be supplied so the smoke test obtains a session token through `/api/login` before calling `/api/dashboard`.

Example:

```bash
SMOKE_USERNAME=smoke SMOKE_PASSWORD='***' \
python scripts/production_smoke_test.py https://<production-host>
```

Use a temporary smoke-test account and never commit real credentials or session tokens.

See `docs/production.md` for the full routing and deployment contract.

## Local development

### Development (hot reload, two terminals)

```bash
# Terminal 1 — Flask API on :5000
cd backend && python app.py

# Terminal 2 — React dev server on :3000
cd frontend && npm start
```

The CRA development server proxies `/api/*` to Flask at `http://127.0.0.1:5000`.

### Production-style local Flask server (single port)

```bash
cd frontend
npm install
npm run build

cd ../backend
pip install -r requirements.txt
python app.py
```

The Flask application can serve the compiled React build directly from `backend/build/` for the single-process local deployment mode.

## Login Credentials

| Username | Password | Role |
|---|---|---|
| admin | admin123 | Admin |
| recruiter | recruiter | Recruiter |
| manager | manager | Hiring Manager |

## Project Structure

```text
RecruitmentAssist/
├── api/
│   └── index.py              ← Vercel Python entrypoint -> Flask app
├── backend/
│   ├── build/                ← React build for single-process Flask mode
│   ├── static/               ← Flask static assets and uploads
│   ├── templates/             ← Original Flask templates
│   ├── app.py                 ← Flask application and /api/* routes
│   ├── routes/                ← API blueprints
│   ├── services/              ← Auth and business logic
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── index.js
│   │   ├── App.jsx
│   │   ├── api.js             ← Central same-origin API client
│   │   ├── components/
│   │   ├── pages/
│   │   └── styles/
│   └── package.json            ← CRA development proxy only
├── docs/
│   └── production.md          ← Production topology and routing contract
├── scripts/
│   └── production_smoke_test.py
├── package.json
└── vercel.json                 ← Production rewrites
```
