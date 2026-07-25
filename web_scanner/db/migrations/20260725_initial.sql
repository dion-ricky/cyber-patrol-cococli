-- UP
CREATE TABLE IF NOT EXISTS scan_requests (
    request_id  TEXT PRIMARY KEY,
    status      TEXT NOT NULL DEFAULT 'pending',
    error       TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS scan_results (
    id_scrap        TEXT PRIMARY KEY,
    request_id      TEXT REFERENCES scan_requests(request_id),
    crawled_time    TIMESTAMPTZ NOT NULL,
    website         TEXT NOT NULL,
    task_id         TEXT NOT NULL,
    classify_website TEXT NOT NULL,
    screenshot      BYTEA,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- DOWN
DROP TABLE IF EXISTS scan_results;
DROP TABLE IF EXISTS scan_requests;
