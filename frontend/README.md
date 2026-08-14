# Recruitment Assist — React + Flask (Single Port Production)

## Quick Start

### Production (single port :5000)
```bash
# Step 1 — Build React
cd frontend
npm install
npm run build

# Step 2 — Copy build to backend
cp -r build ../backend/build

# Step 3 — Also copy logo into build for Flask to serve
cp public/ShimentoX-Light-Logo.webp ../backend/build/ShimentoX-Light-Logo.webp

# Step 4 — Run Flask
cd ../backend
pip install -r requirements.txt
python app.py
# ✅ Open http://localhost:5000
```

### Development (hot reload, two terminals)
```bash
# Terminal 1 — Flask API on :5000
cd backend && python app.py

# Terminal 2 — React dev server on :3000 (auto-proxies /api/* to :5000)
cd frontend && npm start
# ✅ Open http://localhost:3000
```

## Login Credentials
| Username  | Password  | Role           |
|-----------|-----------|----------------|
| admin     | admin123  | Admin          |
| recruiter | recruiter | Recruiter      |
| manager   | manager   | Hiring Manager |

## What Was Fixed (Full Width/Height)
- `html, body, #root` all set to `width:100%; min-height:100vh`
- Navbar spans full browser width (removed `max-width` cap)
- `main-container` uses full width with comfortable padding
- Metrics grid uses responsive column counts (5 → 4 → 3 → 2 → 1)
- Login page uses `position:fixed; inset:0` for true full-screen centering
- Background gradient on `body` uses `background-attachment: fixed`
- Card grids use `auto-fill` so they stretch to fill any screen size
- All page containers explicitly set to `width: 100%`

## Project Structure
```
RecruitmentAssist/
├── backend/
│   ├── app/            ← Core AI modules (LLM, matcher, extractor)
│   ├── build/          ← ⬅ Paste React build here (after npm run build)
│   ├── data/           ← JSON data store
│   ├── static/         ← Logo, uploads, CSS
│   ├── templates/      ← Original HTML (unused when build/ present)
│   ├── app.py          ← Flask: /api/* routes + serves React build
│   ├── requirements.txt
│   └── .env
└── frontend/
    ├── public/
    │   ├── index.html
    │   └── ShimentoX-Light-Logo.webp
    ├── src/
    │   ├── index.js        ← Entry (imports index.css)
    │   ├── index.css       ← Global html/body/#root full-width reset
    │   ├── App.jsx         ← Router
    │   ├── api.js          ← Central fetch utility (token auth)
    │   ├── components/
    │   │   ├── Navbar.jsx
    │   │   └── Layout.jsx  ← app-shell wrapper (flex column, full height)
    │   ├── pages/          ← 10 pages (.jsx), all wired to /api/*
    │   └── styles/         ← 7 CSS files (style.css fully rewritten)
    └── package.json        ← proxy → http://localhost:5000
```
