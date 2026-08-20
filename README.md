# Recruitment Assist

Recruitment Assist is a full-stack talent intelligence platform for managing job descriptions, candidates, screening, assessments, interviews, vendors, fulfilment workflows, and recruitment analytics.

The application uses a React frontend, a Flask API, MongoDB Atlas, and optional OpenAI-powered extraction and recruitment workflows.

## Features

- Job description creation and document extraction
- Resume parsing, candidate profiles, and candidate search
- Candidate-to-job matching and ranking
- Assessment generation, delivery, submission, and evaluation
- Interview scheduling, rescheduling, follow-ups, and outcomes
- Client, vendor, bench, and fulfilment management
- Recruitment dashboards, reports, and audit history
- Recruiter assistant backed by agentic workflows
- Session-token authentication with role-restricted administration

## Architecture

```text
RecruitmentAssist/
├── backend/
│   ├── agents/          AI agent implementations
│   ├── app/             Document extraction and matching modules
│   ├── assessment/      Assessment models, validation, and evaluation
│   ├── orchestration/   LangGraph orchestration
│   ├── routes/          Flask HTTP blueprints
│   ├── services/        Business logic
│   ├── tests/           Backend tests
│   ├── tools/           Agent tool gateway
│   ├── workflows/       Recruitment workflows
│   ├── app.py           Flask application entrypoint
│   └── database.py      MongoDB data-access layer
├── frontend/
│   ├── public/          Static frontend assets
│   └── src/
│       ├── components/  Shared React components
│       ├── pages/       Route-level pages
│       ├── styles/      Application styles
│       ├── api.js       API client and authentication helpers
│       └── App.jsx      React router
├── scripts/             Local setup and documentation scripts
├── .editorconfig        Shared editor formatting rules
├── pyproject.toml       Python quality and test configuration
└── package.json         Local development commands
```

The intended dependency flow is:

```text
React pages -> API client -> Flask routes -> services -> database/external services
                                      \-> orchestration -> agents/tools
```

Routes should validate HTTP input and translate errors. Business logic belongs in services, while persistence belongs in `database.py` or a focused repository module.

## Requirements

- Node.js 18 or newer
- npm 9 or newer
- Python 3.11 or newer
- MongoDB Atlas or MongoDB 6+
- An OpenAI API key for LLM features
- SMTP credentials for email delivery

## Local setup

1. Clone the repository and enter the application directory.

```bash
git clone https://github.com/koushik-shimento/HR_AI.git
cd HR_AI
```

2. Install the root and frontend dependencies.

```bash
npm install
cd frontend
npm ci
cd ..
```

3. Create a Python virtual environment and install backend dependencies.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

4. Create the backend environment file.

```bash
cp backend/.env.example backend/.env
```

Configure at least:

```dotenv
MONGODB_URI=mongodb+srv://USER:PASSWORD@CLUSTER.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB=recruitment_assist
SECRET_KEY=replace-with-a-long-random-value
OPENAI_API_KEY=
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASS=
DEFAULT_FROM_EMAIL=
```

Never commit `.env`, credentials, API keys, session tokens, or database exports containing personal information.

5. Start both development servers.

```bash
npm run dev
```

The React application runs at `http://localhost:3001` and proxies API requests to Flask at `http://127.0.0.1:5000`.

## Database initialization

Application startup initializes MongoDB collections. Optional local seed data can be loaded with:

```bash
npm run seed:backend
```

Default users are created only when `SEED_DEFAULT_USERS=true` and the corresponding password variables are explicitly configured. Do not enable default-user seeding in production.

## Testing

Run backend tests from the repository root:

```bash
python -m pytest
```

Run the frontend test runner:

```bash
cd frontend
npm test
```

Create a production frontend build:

```bash
cd frontend
npm run build
```

Recommended Python quality checks:

```bash
python -m pip install black isort ruff
black --check backend
isort --check-only backend
ruff check backend
```

## API overview

Most API routes require either the Flask session cookie or an `X-Session-Token` header returned by `POST /api/login`.

| Area | Main endpoints |
| --- | --- |
| Authentication | `/api/login`, `/api/logout`, `/api/profile` |
| Dashboard | `/api/dashboard`, `/api/dashboard/team`, `/api/metrics/jd-performance` |
| Jobs | `/api/jds`, `/api/jds/create`, `/api/jds/:id` |
| Candidates | `/api/candidates`, `/api/candidates/:id`, `/api/compare` |
| Assessments | `/api/assessment/*` |
| Interviews | `/api/interviews/*` |
| Clients and vendors | `/api/clients/*`, `/api/vendors/*` |
| Reports | `/api/reports`, `/api/report/email` |
| Administration | `/api/admin/*` |
| Recruiter assistant | `/api/agentic/*` |

The candidate assessment token endpoints are intentionally public. Treat assessment URLs as secrets and avoid writing them to application logs.

## Clean-code conventions

- Keep route handlers small and delegate business logic to services.
- Use descriptive domain names rather than abbreviations.
- Prefer focused functions with one responsibility.
- Validate data at system boundaries.
- Return consistent HTTP status codes without exposing internal exceptions.
- Use structured logging instead of `print` in request-handling code.
- Load configuration from the environment in one place per integration.
- Add tests for bug fixes and important success and failure paths.
- Avoid duplicated business rules between React components and backend services.
- Keep secrets, generated files, uploads, and local environments out of Git.

Python formatting and lint rules are defined in `pyproject.toml`. General whitespace rules are defined in `.editorconfig`.

## Deployment notes

The frontend and Flask API must either be deployed on the same origin or connected through a reverse proxy that forwards `/api/*` and `/static/uploads/*` appropriately.

Before production deployment:

- Configure `MONGODB_URI`, `MONGODB_DB`, `SECRET_KEY`, `CORS_ORIGINS`, and `FRONTEND_URL`.
- Set `SESSION_COOKIE_SECURE=true` when using HTTPS.
- Use durable object storage for uploaded resumes and job descriptions. A serverless local filesystem is not persistent.
- Run document extraction and long LLM operations in a background worker when platform request limits are restrictive.
- Restrict MongoDB network access and use a least-privilege database user.
- Store SMTP and API credentials in the deployment platform's secret manager.
- Disable sample user seeding and rotate any development credentials.

## Troubleshooting

### API returns `503 Database not configured`

Confirm `MONGODB_URI` is available to the backend process and that the Atlas network policy permits the deployment environment.

### Email delivery returns `503`

Confirm `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, and `SMTP_PASS`. Gmail accounts normally require an app password.

### Frontend receives API `404` responses

Confirm the frontend proxy or production rewrite forwards `/api/*` to the Flask deployment.

### LLM extraction returns empty results

Confirm `OPENAI_API_KEY` is configured. Some extraction paths use regex fallback when an LLM is unavailable.

## Contributing

1. Create a focused branch.
2. Keep each change limited to one concern.
3. Add or update tests.
4. Run backend tests, lint checks, and the frontend production build.
5. Open a pull request describing behavior changes, validation performed, and deployment considerations.

## License

No license has been declared. Add a license file before distributing or accepting external contributions.
