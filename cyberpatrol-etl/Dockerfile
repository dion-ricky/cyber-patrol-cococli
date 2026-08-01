FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock* ./
ENV UV_PROJECT_ENVIRONMENT=/usr/local
RUN uv sync --no-dev

COPY etl ./etl
COPY run_loop.sh ./run_loop.sh

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["./run_loop.sh"]
