# IssuePilot 🚀

AI-assisted GitHub issue triage for open-source teams.

IssuePilot connects to a GitHub repository, analyzes issues, detects likely duplicates, assigns priority/severity, and drafts a suggested maintainer reply. It includes a React dashboard, FastAPI API, PostgreSQL support, GitHub webhooks, optional OpenAI-powered analysis, deterministic fallback analysis, tests, Docker, and CI.

> Portfolio note: use this as a learning/open-source project. Only claim features you personally understand, test, and can demonstrate.

## Features
- GitHub REST API integration
- Issue classification: bug / feature / documentation / question / other
- Priority and severity scoring
- Duplicate detection with TF-IDF + cosine similarity
- Suggested maintainer replies
- Optional LLM enhancement via OpenAI
- HMAC-verified GitHub webhooks
- SQLAlchemy + PostgreSQL, with SQLite fallback
- React + Vite dashboard
- Docker Compose
- Pytest tests and GitHub Actions CI
- FastAPI OpenAPI/Swagger documentation

## Architecture

```text
React Dashboard
      |
      v
  FastAPI API <---- GitHub REST API
      |
      +---- Triage Engine ---- TF-IDF Duplicate Detector
      |              |
      |              +-------- Optional LLM Provider
      |
      +---- PostgreSQL / SQLite
      ^
      |
GitHub Webhook
```

## Quick start

1. Copy `.env.example` to `.env`.
2. Optionally add `GITHUB_TOKEN`.
3. Optionally add `OPENAI_API_KEY` and a supported `OPENAI_MODEL`.
4. Run:

```bash
docker compose up --build
```

Open:
- Frontend: http://localhost:5173
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs

### Local backend

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Local frontend

```bash
cd frontend
npm install
npm run dev
```

## Example API calls

```bash
curl -X POST http://localhost:8000/api/analyze ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"Login returns 500\",\"body\":\"Users get an internal server error after submitting credentials.\"}"
```

Fetch issues:

```bash
curl "http://localhost:8000/api/github/issues?owner=fastapi&repo=fastapi&state=open"
```

Analyze a GitHub issue:

```bash
curl -X POST http://localhost:8000/api/github/analyze ^
  -H "Content-Type: application/json" ^
  -d "{\"owner\":\"fastapi\",\"repo\":\"fastapi\",\"issue_number\":1}"
```

## GitHub webhook

Configure a repository webhook at:

`POST https://YOUR-DOMAIN/api/webhooks/github`

Set the same `GITHUB_WEBHOOK_SECRET` in GitHub and `.env`. IssuePilot validates `X-Hub-Signature-256` before processing issue events.

For local development, use a secure tunnel and never commit webhook secrets.

## OpenAI provider

The LLM provider is optional:

```env
OPENAI_API_KEY=your_key
OPENAI_MODEL=your_supported_model
```

If those values are absent, the deterministic analyzer remains fully usable.

## Production checklist
- HTTPS
- Secret manager
- Restricted CORS
- PostgreSQL
- Authentication/authorization
- Rate limiting
- Structured logging
- Pinned dependencies
- Regular secret rotation

## CV description

**IssuePilot — AI-Powered GitHub Issue Triage**
- Built a full-stack open-source platform that analyzes and triages GitHub issues by category, priority, and severity.
- Implemented TF-IDF/cosine-similarity duplicate detection and optional LLM-assisted issue analysis.
- Integrated GitHub REST APIs and HMAC-verified webhooks with a FastAPI backend.
- Developed a React dashboard and PostgreSQL-backed persistence layer, containerized with Docker.
