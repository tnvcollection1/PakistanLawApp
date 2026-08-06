# Pakistan Law App (pakistanlawapp.com)

A legal research platform with **369,810+ Pakistani case laws**, AI-powered search, citation analysis, cross-referencing, and case management tools.

## 🚀 Live Site
- **URL**: https://pakistanlawapp.com
- **Password**: `tnv2026`
- **Login**: `mtclaw` / `mtclawkhi786`

## 📊 Stats
- **Cases**: 369,810+ merged case laws
- **Courts**: 329+ courts covered
- **Judges**: 62,424+ judge records
- **Years**: 1950–2024 coverage

## 🏗 Architecture

### Backend
- **FastAPI** on port 8020 (via PM2)
- **Motor** (async MongoDB driver)
- **MongoDB** with `merged_caselaws` collection (369K docs)
- **OpenClaw** self-hosted AI gateway at `localhost:18789` (OpenAI-compatible API)
- **Moonshot/Kimi** models: `moonshot/kimi-k2.6`, `moonshot/kimi-k2.5`

### Frontend
- **React** (Create React App) with Tailwind CSS
- **Yarn** build system (static files served via Nginx)
- **Responsive** — mobile sidebar with hamburger menu

### Infrastructure
- **VPS**: 203.161.38.75
- **Nginx** reverse proxy (Docker container)
- **Docker** containers for frontend + backend
- **PM2** process manager for backend

## 🔑 Key Features

| Feature | Endpoint | Status |
|---------|----------|--------|
| Word-by-word search | `GET /api/search/caselaws?q=` | ✅ Fast (<1s) |
| Cases list | `GET /api/cases/list` | ✅ Fast |
| Case detail | `GET /api/case/{id}` | ✅ Full text |
| Search within case | `GET /api/case/{id}/search?q=` | ✅ NEW |
| Citation parser | `GET /api/case/{id}/references` | ✅ |
| Analytics | `GET /api/analytics/overview` | ✅ |
| Section search | `GET /api/section/search?section=` | ✅ |
| Export (PDF/Word) | `POST /api/export/{id}` | ✅ |
| Download (TXT/JSON) | `GET /api/download/{id}` | ✅ |
| AI chat/summary | `POST /api/ai/case-summary` | 🔄 Ready |
| Headnote generation | `POST /api/ai/generate-headnotes` | 🔄 Ready |
| Advanced search | `POST /api/advanced-search` | ✅ |
| Case comparison | `POST /api/compare-cases` | ✅ |

## 🗂 Project Structure

```
PakistanLawApp/
├── server.py                 # FastAPI main app
├── models.py                 # Pydantic models
├── database.py               # MongoDB connection
├── auth_utils.py             # JWT auth utilities
├── openclaw_client.py        # OpenClaw AI client
├── requirements.txt          # Python dependencies
├── Dockerfile               # Backend Docker image
├── docker-compose.yml       # Docker orchestration
├── ecosystem.config.js      # PM2 config
├── deploy.sh                # One-command deployment
├── .env.example             # Environment template
│
├── routes/                   # 50+ FastAPI route modules
│   ├── auth.py              # Auth (login/register/JWT)
│   ├── search.py            # Word-by-word search ($text + $regex)
│   ├── cases.py             # Case listing
│   ├── citation_parser.py   # Extract references from case text
│   ├── case_search.py       # Search within a single case
│   ├── analytics.py         # Dashboard analytics
│   ├── section_search.py    # Search by legal section
│   ├── advanced_search.py   # Advanced filter search
│   ├── export_case.py       # PDF/Word export
│   ├── download_case.py     # TXT/JSON/ZIP download
│   ├── ai_embedded.py       # AI helpers (embedded, NOT standalone)
│   └── ... 40+ more routes
│
├── frontend/                # React SPA
│   ├── src/
│   │   ├── App.jsx          # Main router
│   │   ├── index.js         # Entry point
│   │   ├── components/      # 50+ components (Sidebar, CaseSearchBox, etc.)
│   │   ├── pages/           # 60+ pages (Home, Cases, Analytics, etc.)
│   │   ├── hooks/           # Custom hooks (useAIContext, useOpenClaw, etc.)
│   │   ├── api/api.js       # API client
│   │   └── context/         # AuthContext, ThemeContext
│   ├── package.json
│   └── Dockerfile
│
├── middleware/rate_limit.py # Anti-scraping + rate limiting
├── utils/citation_utils.py  # Citation utilities
├── scripts/scrapers/        # 20+ case law scrapers
└── scrapers/                # Auto ingestion pipeline
```

## ⚙️ Environment Variables

```env
MONGODB_URI=mongodb://localhost:27017/pakistanlaw
DB_NAME=pakistanlaw
SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret
GLITCHTIP_DSN=your-glitchtip-dsn
OPENCLAW_URL=http://localhost:18789/v1
FRONTEND_URL=https://pakistanlawapp.com
ADMIN_KEY=your-admin-key
VPS_HOST=203.161.38.75
```

## 🚀 Deployment

```bash
# One-command deployment (from VPS)
./deploy.sh

# Or manual:
cd frontend && yarn build
cd .. && pm2 restart ecosystem.config.js
```

## 🔧 MongoDB Indexes

```javascript
db.merged_caselaws.createIndex({ "$**": "text" })
db.merged_caselaws.createIndex({ "citation": 1 })
db.merged_caselaws.createIndex({ "year": 1 })
db.merged_caselaws.createIndex({ "court": 1 })
db.merged_caselaws.createIndex({ "judges": 1 })
```

## 🤖 AI Integration (OpenClaw)

```bash
# Install OpenClaw gateway
./scripts/openclaw-install.sh

# Start with Moonshot API key
OPENCLAW_API_KEY=your-moonshot-key ./scripts/openclaw-install.sh
```

AI endpoints (embedded, NOT standalone):
- `POST /api/ai/generate-headnotes` — Generate headnotes for cases
- `POST /api/ai/case-summary` — Summarize case (Brief/Detailed/Bench)
- `POST /api/ai/enhance-search` — Smart query parsing
- `POST /api/ai/ask-about-case` — Inline Q&A
- `POST /api/ai/explain-section` — Explain PPC/Cr.P.C sections
- `POST /api/ai/find-related` — Find related cases
- `GET /api/ai/headnote-status` — Progress stats

## 📄 License

Private — All rights reserved by PakistanLawApp.
