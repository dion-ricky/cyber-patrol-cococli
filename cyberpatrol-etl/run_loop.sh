#!/bin/sh
# Runs the ETL once, then sleeps, forever. Poor-man's cron for a single
# container: simpler than adding a cron daemon inside the image.
set -e

INTERVAL="${ETL_INTERVAL_SECONDS:-1800}"

while true; do
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) starting ETL run"
    python -m etl.main
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) run complete, sleeping ${INTERVAL}s"
    sleep "$INTERVAL"
done
