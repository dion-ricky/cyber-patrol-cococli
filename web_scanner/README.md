# Cyber Patrol - Website Classification Scraper

An automated system for classifying websites using AI-powered browser automation. The system opens target URLs and classifies them as gambling, scam, or safe websites, with support for detecting various connection error states.

## Features

- **Unified Website Classification**: Single classifier that detects gambling sites, scam/phishing sites, and safe sites
- **AI-Powered Navigation**: Uses LLM-based agents to browse and analyze websites
- **Error State Detection**: Handles connection resets, network filters, government blocks, and Cloudflare challenges
- **Screenshot Evidence**: Captures and stores screenshots of each classified website

## Classification Labels

| Label | Description |
|-------|-------------|
| `GAMBLING_WEBSITE` | Online gambling, betting, slots, togel, poker, etc. |
| `SCAM_WEBSITE` | Phishing, brand impersonation, or fraud site |
| `SAFE_WEBSITE` | Legitimate site with no gambling or scam indicators |
| `ERR_CONNECTION_RESET` | Connection reset error |
| `BLOCKED_BY_NETWORK_FILTER` | Blocked by network filtering |
| `BLOCKED_BY_GOVERNMENT` | Redirected with Indonesian government block message |
| `CLOUDFLARE_BLOCKED` | Stuck at Cloudflare verification page |

## Project Structure

```
web_scanner/
├── main.py                  # FastAPI API server
├── scan_cli.py              # One-shot CLI script for local dev
├── scan_worker.py           # Worker subprocess for scanning
├── migrate.py               # Database migration CLI
├── config/
│   └── settings.py          # Configuration dataclasses
├── db/
│   ├── connection.py        # Database connection
│   ├── repository.py        # CRUD operations
│   └── migrations/
│       ├── runner.py        # Migration engine
│       └── *.sql            # Migration files
├── models/
│   └── scan.py              # ScanResult, ScanRequest, ScanResponse
├── prompts/
│   └── classify.py          # Task prompt templates
├── scanner/
│   ├── browser.py           # Browser automation agent
│   └── website.py           # Website scanning orchestration
├── utils/
│   └── url.py               # URL/ID utilities
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
└── README.md
```

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Chrome/Chromium browser (not needed when using Docker)
- LLM API access (OpenAI-compatible endpoint)
- Docker (optional)

## Installation

### Using uv (Recommended)

```bash
cd web_scanner

# Install dependencies (creates .venv automatically)
uv sync

# Activate the virtual environment
source .venv/bin/activate
```

## Development

### Database Migrations

Migrations run automatically at startup. To manage manually:

```bash
# Check migration status
python migrate.py --status

# Apply pending migrations
python migrate.py
```

Creating a new migration:

```bash
# Create a new migration file with timestamp
touch db/migrations/$(date +%Y%m%d%H%M%S)_description.sql
```

Migration file format:

```sql
-- UP
CREATE TABLE new_table (...);

-- DOWN
DROP TABLE IF EXISTS new_table;
```

### Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) with [ruff](https://docs.astral.sh/ruff/) for code formatting and linting. The hooks run automatically on each commit.

#### Setup

```bash
# Install pre-commit hooks (run from repo root)
cd cyber-patrol-cococli
pre-commit install
```

#### Manual Usage

```bash
# Run ruff formatter manually
cd web_scanner
uv run ruff format .

# Run ruff linter manually
uv run ruff check .

# Auto-fix fixable lint issues
uv run ruff check --fix .

# Run pre-commit on all files
pre-commit run --all-files
```

## Docker

Build and run with Docker Compose:

```bash
# Copy and configure environment variables
cp .env.example .env
# Edit .env with your AI_KEY and AI_GATEWAY

# Build and run (API server on port 8000)
docker compose up --build
```

Or with plain Docker:

```bash
docker build -t web-scanner .
docker run -e AI_KEY=your_key -e AI_GATEWAY=your_gateway -p 8000:8000 -v ./result:/app/result web-scanner
```

## Environment Variables

```bash
export AI_KEY="your_api_key"
export AI_GATEWAY="your_api_gateway_url"
export RESULT_BASE_PATH="result"  # optional, defaults to "result"
```

## Usage

### API Server (Production)

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

#### Scan a website (fire-and-forget)

```bash
curl -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

Response:

```json
{"request_id": "a1b2c3d4e5f6", "status": "pending"}
```

#### Poll for results

```bash
curl http://localhost:8000/result/a1b2c3d4e5f6
```

Response (in progress):

```json
{"request_id": "a1b2c3d4e5f6", "status": "in_progress", "error": null, "results": []}
```

Response (done):

```json
{
  "request_id": "a1b2c3d4e5f6",
  "status": "done",
  "error": null,
  "results": [
    {
      "id_scrap": "example_20260724120000_abc123",
      "crawled_time": "2026-07-24T12:00:00",
      "website": "example",
      "task_id": "...",
      "classify_website": "SAFE_WEBSITE"
    }
  ]
}
```

Response (failed):

```json
{"request_id": "a1b2c3d4e5f6", "status": "failed", "error": "Connection timeout", "results": []}
```

#### Health check

```bash
curl http://localhost:8000/health
```

### CLI Script (Local Development)

For quick testing without running the server:

```bash
# Scan one website
python scan_cli.py https://example.com

# Scan multiple websites
python scan_cli.py https://site1.com https://site2.com https://site3.com

# Custom output file
python scan_cli.py -o results.csv https://example.com
```

### Output

Results are saved as CSV files:

```
classify_YYYYMMDD.csv
```

Each row contains:
- `id_scrap` — Unique scrap ID
- `crawled_time` — Timestamp of the crawl
- `website` — Domain name
- `task_id` — Task identifier
- `classify_website` — Classification result (one of the labels above)

Screenshots are saved to the `result/` directory.

## Modules

### config/settings.py
Configuration layer using frozen dataclasses. `get_settings()` returns a singleton `Settings` instance loaded from environment variables.

### models/scan.py
Domain models: `ClassificationLabel` enum and `ScanResult` dataclass with `to_dict()` serialization.

### prompts/classify.py
`build_classify_prompt(url)` generates the task prompt for the AI agent.

### scanner/browser.py
`BrowserAgent` wraps the `browser-use` library for LLM-powered browser automation.

### scanner/website.py
`WebsiteScanner` orchestrates the scanning pipeline: build prompt → run agent → extract result → save screenshots.

### utils/url.py
Utility functions: `derive_site_name()` extracts domain, `generate_scrap_id()` creates unique IDs.
