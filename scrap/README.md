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
scrap/
├── main.py                  # Main entry point and orchestration
├── ai_scrapper.py           # AI agent wrapper for browser automation
├── scrap_general.py         # Unified website classification scraper
├── task_creation.py         # Task prompt templates for AI agent
├── project.py               # Configuration and constants
├── requirements.txt         # Python dependencies
└── result/                  # Output screenshots (git-ignored)
```

## Prerequisites

- Python 3.9+
- Chrome/Chromium browser
- LLM API access (OpenAI-compatible endpoint)

## Installation

```bash
cd scrap
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment Variables

```bash
export AI_KEY="your_api_key"
export AI_GATEWAY="your_api_gateway_url"
export RESULT_BASE_PATH="result"  # optional, defaults to "result"
```

## Usage

### Run Classification

```bash
python main.py
```

Edit `main.py` to set the target URL:

```python
link = "https://example.com"
```

### Output

Results are saved as CSV files in the current directory:

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

### main.py
Entry point that orchestrates the scraping workflow. Derives site names from URLs, generates unique scrap IDs, and writes results to CSV.

### ai_scrapper.py
Wraps the `browser-use` library to run LLM-powered browser automation agents.

### scrap_general.py
Unified scraper class that calls the AI agent with classification tasks and collects results with screenshots.

### task_creation.py
Contains the `TaskCreation` class that generates classification prompts. The unified prompt instructs the AI to classify websites into gambling, scam, safe, or error categories.

### project.py
Reads environment variables and provides configuration objects for LLM parameters and browser profile settings.

## License

Internal use only - DANA Indonesia
