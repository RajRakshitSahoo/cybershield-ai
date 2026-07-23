# CyberShield AI

**AI-Powered Phishing Website Detection & Domain Intelligence Platform**

CyberShield AI lets anyone paste a URL and get back a full security
intelligence report: WHOIS/domain data, SSL/TLS posture, DNS records,
security header grading, technology fingerprinting, live reputation/blacklist
checks, and an explainable AI phishing verdict with a 0–100 risk score.

---

## 1. Architecture

```
cybershield-ai/
├── backend/          FastAPI REST API + ML pipeline
│   ├── app/
│   │   ├── auth/          JWT auth (register/login/session)
│   │   ├── ml/             feature extraction, training, inference
│   │   ├── models/         Pydantic schemas
│   │   ├── routers/        /auth /analyze /history /compare /report
│   │   │                   /dashboard /admin /domain /security /ml
│   │   ├── services/       whois/dns/ssl/headers/tech/reputation/pdf
│   │   ├── tests/          pytest unit tests
│   │   ├── config.py       env-driven settings
│   │   ├── database.py     Mongo (motor) with in-memory mongomock fallback
│   │   └── main.py         FastAPI app entrypoint
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/          React + TypeScript + Vite + Tailwind SPA
│   └── src/
│       ├── components/     Navbar, Panel, RiskGauge, ReportView, ...
│       ├── pages/          Home, Login, Register, History, Compare,
│       │                   Dashboard, Admin
│       └── lib/            api client, auth context
├── docker-compose.yml  Full stack: mongo + backend + frontend
└── README.md
```

**Request flow for a scan:** the frontend calls `POST /api/analyze`, which
runs a pipeline (`app/services/analysis_orchestrator.py`) that fans out to
WHOIS/DNS, SSL, HTTP header fetch, tech fingerprinting, reputation feeds, the
ML model, and screenshot capture — recording a step-by-step timeline — then
stores the resulting report in MongoDB (or the in-memory mock DB) and
returns it to the client.

---

## 2. Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript, Vite, Tailwind CSS, Framer Motion, Recharts, Axios |
| Backend | Python, FastAPI, JWT auth, Pydantic |
| Machine Learning | scikit-learn (RandomForest), pandas, NumPy, joblib |
| Database | MongoDB (via Motor), with a zero-config `mongomock` fallback |
| Deployment | Docker, Docker Compose, Nginx (frontend), Vercel/Render-ready |

---

## 3. Installation

### Option A — Docker Compose (recommended, full stack)

```bash
cp backend/.env.example backend/.env   # edit secrets/API keys as desired
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend API docs (Swagger): http://localhost:8000/docs
- MongoDB: localhost:27017

### Option B — Run locally without Docker

**Backend**
```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python -m app.ml.train_model      # trains + saves the phishing model
uvicorn app.main:app --reload
```
With `USE_MOCK_DB=true` (the default in `.env.example`) the API runs with
zero external dependencies — no MongoDB installation required. Set
`USE_MOCK_DB=false` and point `MONGO_URI` at a real MongoDB instance for
persistent storage.

**Frontend**
```bash
cd frontend
npm install
npm run dev
```
Visit http://localhost:5173 — Vite proxies `/api` to `http://localhost:8000`.

---

## 4. Features

- **URL Scanner** — paste any URL, get a full report in seconds.
- **Domain Intelligence** — WHOIS, IP/IPv6, registrar, domain age, hosting
  provider, ASN, geolocation, CDN detection.
- **SSL/TLS Analysis** — certificate validity, issuer, TLS version, days to
  expiry, HSTS.
- **DNS Analysis** — A, AAAA, MX, TXT, NS, CNAME, SOA, DNSSEC presence.
- **Security Header Grading** — CSP, X-Frame-Options, X-Content-Type-Options,
  Referrer-Policy, Permissions-Policy, HSTS, X-XSS-Protection, graded
  missing / weak / strong.
- **Technology Fingerprinting** — frontend/backend frameworks, CMS, server,
  CDN, and analytics detection via signature matching.
- **Reputation & Blacklist Checks** — VirusTotal, Google Safe Browsing,
  OpenPhish (free feed, no key needed), AbuseIPDB. Missing API keys degrade
  gracefully to "unavailable" rather than failing the scan.
- **Explainable AI Phishing Detection** — a RandomForest classifier trained
  on 19 URL/domain features returns a Safe / Suspicious / Phishing verdict,
  a 0–100 risk score, a confidence percentage, and plain-English reasons.
- **Visual Risk Meter** — animated circular gauge, color-coded by severity.
- **Threat Timeline** — step-by-step scan pipeline with per-step timing.
- **Website Screenshots** — desktop + mobile preview via microlink.io.
- **Compare Two Websites** — side-by-side scan of two URLs with a computed
  "overall safer" verdict.
- **Scan History** — search, filter by verdict, bookmark, delete, export.
- **PDF Reports** — professional report with charts, QR code, and
  recommendations, generated with ReportLab.
- **User Dashboard** — verdict distribution, scans over time, top TLDs/
  countries, average risk score.
- **Admin Console** — platform-wide stats, daily scan volume, top phishing
  domains, recent detections, user management, API integration health.
- **JWT Authentication** — visitor / registered user / admin roles (the
  first registered account automatically becomes admin).

---

## 5. Machine Learning

`backend/app/ml/train_model.py` trains a `RandomForestClassifier` on 19
engineered features per URL (length, entropy, hyphen/digit counts, brand
keywords, suspicious TLDs, IP-as-host, redirects, domain age, etc.) — see
`backend/app/ml/feature_extraction.py`.

**Data note:** the training set is generated programmatically (realistic
phishing-style vs. legitimate-style URL patterns with randomized noise)
rather than bundling a scraped third-party dataset, keeping the repo
self-contained and license-clean. Swap `build_dataset()` in `train_model.py`
for a real labeled corpus (PhishTank / UCI Phishing Websites / OpenPhish
exports) to retrain on real-world data — the training and evaluation code
does not need to change.

**Explainability:** each prediction returns the top contributing features
combined with rule-based, human-readable reasons ("domain registered very
recently", "uses a suspicious TLD", etc.) — see
`backend/app/ml/ml_service.py`. This gives SHAP-style, per-prediction
attribution without the heavier `shap` dependency; swapping in
`shap.TreeExplainer` is a documented one-function change if you install it.

**Evaluation metrics** (accuracy, precision, recall, F1, ROC-AUC, confusion
matrix) are saved to `backend/app/ml/metrics.json` after training and served
at `GET /api/ml/metrics`.

---

## 6. API Structure

| Prefix | Purpose |
|---|---|
| `/api/auth` | register, login, refresh, me |
| `/api/analyze` | run a full scan |
| `/api/history` | list/get/delete/bookmark past scans (registered users) |
| `/api/compare` | compare two URLs |
| `/api/report` | PDF export of a saved scan |
| `/api/dashboard` | per-user analytics |
| `/api/admin` | platform-wide stats + user management (admin only) |
| `/api/domain` | standalone WHOIS/DNS lookup |
| `/api/security` | standalone SSL/header checks |
| `/api/ml` | standalone prediction + model metrics |

Full interactive documentation is auto-generated by FastAPI at `/docs`
(Swagger UI) and `/redoc`.

---

## 7. Deployment

- **Frontend:** build with `npm run build` in `frontend/` and deploy the
  `dist/` folder to Vercel, Netlify, or any static host. Set the API base
  URL via a reverse proxy (see `frontend/nginx.conf`) or an environment
  variable if you adapt `src/lib/api.ts`.
- **Backend:** deploy the `backend/` Docker image to Render, Railway, AWS
  (ECS/Fargate/EC2), or any container platform. Provide a real `MONGO_URI`
  (e.g. MongoDB Atlas) and set `USE_MOCK_DB=false` in production.
- **Full stack:** `docker compose up --build` runs MongoDB, the backend, and
  an Nginx-served frontend together — see `docker-compose.yml`.

---

## 8. Future Scope

- Swap the synthetic training set for a real labeled phishing dataset.
- Add a local Playwright-based screenshot fallback for offline/self-hosted
  deployments (a commented starting point is already in
  `screenshot_service.py`).
- Wire up email alerts (SMTP settings are already in `.env.example`) for
  high-risk detections and weekly digest reports.
- Add WebSocket-based live progress updates during a scan instead of a
  single request/response round trip.
- Integrate a real `shap.TreeExplainer` for canonical SHAP values.

---

## 9. Testing

```bash
cd backend
pytest app/tests/ -v
```

Covers feature extraction correctness, phishing-pattern detection, ML
prediction sanity (including the domain-age-unknown edge case), and
security header grading logic.

---

## 10. Contributors

- Raj Rakshit — B.Tech CSE, C.V. Raman Global University, Bhubaneswar

## 11. License

MIT License — free to use, modify, and distribute for academic or
commercial purposes.
