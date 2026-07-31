# AGENTS.md

## Project Overview

Web Scanner - An AI-powered website classification system that automatically scans and categorizes websites as gambling, scam, or safe. Uses LLM-based browser automation to navigate and analyze sites, with optional urlscan.io integration for additional threat intelligence.

## Tech Stack

- **Backend**: Python 3.14, FastAPI, uvicorn
- **Browser Automation**: browser-use (LLM-powered agents), Playwright
- **Database**: PostgreSQL (via psycopg)
- **Frontend**: React 19, TypeScript, Vite
- **Containerization**: Docker, Docker Compose
- **Package Manager**: uv
- **Linting**: ruff (format + check), pre-commit hooks
- **Testing**: pytest

## Project Structure

```
web_scanner/
├── main.py                  # FastAPI API server (port 8080)
├── scan_cli.py              # CLI for local development
├── scan_worker.py           # Subprocess worker for async scanning
├── migrate.py               # Database migration CLI
├── config/
│   └── settings.py          # Frozen dataclass config from env vars
├── db/
│   ├── connection.py        # psycopg connection singleton
│   ├── repository.py        # CRUD operations for all tables
│   └── migrations/
│       ├── runner.py        # Custom migration engine
│       └── *.sql            # Timestamped migration files
├── models/
│   ├── scan.py              # ScanResult, ClassificationLabel enum
│   └── urlscan.py           # UrlScanResult dataclasses
├── prompts/
│   └── classify.py          # LLM prompt template for classification
├── scanner/
│   ├── browser.py           # BrowserAgent wrapper for browser-use
│   ├── website.py           # WebsiteScanner orchestration
│   └── urlscan.py           # UrlScanClient (urlscan.io API)
├── utils/
│   └── url.py               # URL parsing, scrap ID generation
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # React Router setup
│   │   ├── api.ts           # API client functions
│   │   ├── pages/           # Home, ResultPage
│   │   └── components/      # ScanForm, ScanResults
│   └── dist/                # Built frontend (served by FastAPI)
├── tests/
│   ├── test_urlscan.py      # UrlScan extraction tests
│   └── fixtures/            # JSON test fixtures
├── Dockerfile               # Multi-stage: Node build + Python runtime
├── docker-compose.yml       # PostgreSQL + scanner services
├── pyproject.toml           # Python project config
└── .env.example             # Environment variable template
```

## Conventions

### Code Style
- Python: ruff formatter (line-length 88, double quotes, space indent)
- TypeScript: Vite default config
- Use frozen dataclasses for config/models
- Use Pydantic BaseModel for API request/response schemas

### Git
- Use conventional commits: `feat:`, `fix:`, `chore:`, `docs:`
- Commit messages should be concise

### Naming
- Files: snake_case for Python, PascalCase for React components
- Classes: PascalCase (BrowserAgent, WebsiteScanner, UrlScanClient)
- Functions: snake_case (build_classify_prompt, derive_site_name)
- Database tables: snake_case plural (scan_requests, scan_results, urlscan_results)

## Key Commands

### Development
```bash
cd web_scanner
uv sync                          # Install dependencies
source .venv/bin/activate        # Activate venv
uvicorn main:app --reload        # Run API server (port 8000)
```

### Frontend
```bash
cd web_scanner/frontend
npm install                      # Install deps
npm run dev                      # Dev server (port 5173, proxies /api to 8000)
npm run build                    # Build for production (outputs to dist/)
```

### Database
```bash
python migrate.py                # Apply pending migrations
python migrate.py --status       # Show migration status
```

### Testing
```bash
uv run pytest                    # Run all tests
uv run pytest tests/test_urlscan.py  # Run specific test file
```

### Linting
```bash
uv run ruff format .             # Format code
uv run ruff check .              # Lint
uv run ruff check --fix .        # Auto-fix lint issues
pre-commit run --all-files       # Run all pre-commit hooks
```

### Docker
```bash
docker compose up --build        # Build and run (API on port 8000)
```

## Domain Knowledge

### Classification Labels
| Label | Description |
|-------|-------------|
| `GAMBLING_WEBSITE` | Online gambling, betting, slots, togel, poker |
| `SCAM_WEBSITE` | Phishing, brand impersonation, fraud |
| `UNCLASSIFIED` | No gambling, scam, or malicious indicators detected |
| `ERR_CONNECTION_RESET` | Connection reset error |
| `BLOCKED_BY_NETWORK_FILTER` | Blocked by network filtering |
| `BLOCKED_BY_GOVERNMENT` | Indonesian government block message |
| `CLOUDFLARE_BLOCKED` | Stuck at Cloudflare verification |

### Scanning Pipeline
1. API receives URL via `POST /api/scan`
2. `scan_worker.py` spawned as subprocess
3. BrowserAgent uses LLM to navigate and classify the website
4. Optional: UrlScanClient submits to urlscan.io for parallel analysis
5. Results stored in PostgreSQL (scan_results + urlscan_results)
6. Screenshots captured and stored as BYTEA

### API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/scan` | Submit URL for scanning (fire-and-forget) |
| `GET` | `/api/result/{request_id}` | Poll scan status/results |
| `GET` | `/api/screenshot/{id_scrap}` | Get screenshot image |
| `GET` | `/api/urlscan/{request_id}` | Get urlscan.io results |
| `GET` | `/api/health` | Health check |

### Database Schema
- **scan_requests**: request_id (PK), status, error, timestamps
- **scan_results**: id_scrap (PK), request_id (FK), classification, screenshot (BYTEA)
- **urlscan_results**: uuid (PK), request_id (FK), threat intelligence fields, network data
- **schema_migrations**: version tracking for migrations

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AI_KEY` | Yes | LLM API key |
| `AI_GATEWAY` | Yes | LLM API gateway URL |
| `DATABASE_URL` | Yes | PostgreSQL connection URL |
| `URLSCAN_API_KEY` | No | urlscan.io API key |
| `HEADLESS` | No | Run browser headless (default: true) |

## Testing

- pytest with `pythonpath = ["."]` in pyproject.toml
- Test fixtures in `tests/fixtures/` (JSON files)
- Test urlscan extraction logic with mock API responses
- Run: `uv run pytest`

## Security

- Never commit `.env` files or expose API keys
- Use environment variables for all secrets
- Database connections use parameterized queries (psycopg)
- File uploads validated by type and size
