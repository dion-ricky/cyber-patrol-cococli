-- UP
CREATE TABLE IF NOT EXISTS urlscan_results (
    id                  SERIAL PRIMARY KEY,
    request_id          TEXT REFERENCES scan_requests(request_id),
    uuid                TEXT NOT NULL UNIQUE,
    verdicts            JSONB DEFAULT '{}',
    page                JSONB DEFAULT '{}',
    lists               JSONB DEFAULT '{}',
    stats               JSONB DEFAULT '{}',
    visible             JSONB DEFAULT '{}',
    network_requests    JSONB DEFAULT '[]',
    security_details    JSONB DEFAULT '{}',
    response_headers    JSONB DEFAULT '{}',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- DOWN
DROP TABLE IF EXISTS urlscan_results;
