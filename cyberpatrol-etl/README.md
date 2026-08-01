# cyberpatrol-etl

Incremental extract/load pipeline: pulls new/changed rows from the
`cyberpatrol` Snowflake Postgres instance (`scan_requests`, `scan_results`,
`urlscan_results`) and merges them into native Snowflake tables under
`CYBERPATROL.RAW`, so Cortex Analyst can query the data.

Runs once per invocation (extract -> stage -> merge -> advance watermark)
and exits. Deployed as a standalone container, connecting to both Postgres
and Snowflake as a normal external client (a programmatic access token is
used for Snowflake auth, since it needs to run unattended).

## Local development

```bash
cp .env.example .env   # fill in DATABASE_URL and Snowflake PAT
uv sync
set -a && . .env && set +a && uv run python -m etl.main
```

## Deployment

```bash
cp .env.example .env   # fill in DATABASE_URL, SNOWFLAKE_* PAT credentials
docker compose up --build -d
```

This runs the container with `run_loop.sh` as the entrypoint, which executes
the ETL once, sleeps `ETL_INTERVAL_SECONDS` (default 1800s / 30 min), and
repeats indefinitely. Deploy this `docker-compose.yml` alongside the rest of
the app's infra (same host/orchestration as `web_scanner`).

### Snowflake-side setup (one-time)

Already created in the `cyberpatrol` Snowflake account:
- `CYBERPATROL.RAW` schema with `SCAN_REQUESTS`, `SCAN_RESULTS`,
  `URLSCAN_RESULTS`, `ETL_WATERMARKS` tables
- `CYBERPATROL_ETL_ROLE` with the privileges this app needs
- A network policy on the Postgres instance permitting inbound connections
  from wherever this container is deployed

The Snowflake PAT used in `.env` should be restricted to
`CYBERPATROL_ETL_ROLE`, and the Snowflake user must have a network policy
attached (`ALTER USER ... SET NETWORK_POLICY = ...`) to authenticate with a
PAT.
