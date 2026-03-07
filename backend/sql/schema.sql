/*
 * Authentication Tables
 */

CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    user_role TEXT NOT NULL DEFAULT 'admin',
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    token_hash TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '24 hours'),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    token_hash TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '15 minutes'),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);


/*
 * Raw Layer Tables
 */


CREATE TABLE IF NOT EXISTS uploaded_files (
    uploaded_file_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    uploaded_by UUID NOT NULL,
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    original_file_name TEXT NOT NULL,
    original_file_size_in_bytes BIGINT NOT NULL,
    source TEXT NOT NULL,
    ingestion_status TEXT NOT NULL DEFAULT 'pending',
    processing_started_at TIMESTAMPTZ DEFAULT NULL,
    processing_finished_at TIMESTAMPTZ DEFAULT NULL,
    storage_path TEXT NOT NULL UNIQUE,
    checksum_sha256 TEXT NOT NULL UNIQUE,
    error_message TEXT DEFAULT NULL,
    transform_error_message TEXT DEFAULT NULL,
    transform_status TEXT NOT NULL DEFAULT 'pending',
    transform_started_at TIMESTAMPTZ DEFAULT NULL,
    transform_completed_at TIMESTAMPTZ DEFAULT NULL,


    CHECK (ingestion_status IN ('pending', 'processing', 'completed', 'failed')),
    CHECK (source IN ('libcal', 'myturn', 'niche')),
    CHECK (transform_status IN ('pending', 'processing', 'completed', 'failed'))
);

CREATE INDEX  IF NOT EXISTS idx_uploaded_files_transform_pending
ON uploaded_files (ingestion_status, transform_status);

CREATE TABLE IF NOT EXISTS raw_rows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    uploaded_file_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    raw_data JSONB NOT NULL,
    row_number INT NOT NULL,
    FOREIGN KEY (uploaded_file_id) REFERENCES uploaded_files(uploaded_file_id) ON DELETE CASCADE,
    UNIQUE (uploaded_file_id, row_number)
);

CREATE INDEX IF NOT EXISTS idx_raw_rows_uploaded_file_id
ON raw_rows(uploaded_file_id);


/*
 * Niche Canonical Tables
 */


CREATE TABLE IF NOT EXISTS tutorials (
    tutorial_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tutorial_name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tutorial_metrics (
    tutorial_id UUID NOT NULL,
    metric_date DATE NOT NULL,
    total_views INTEGER NOT NULL,
    uploaded_file_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (tutorial_id, metric_date),
    FOREIGN KEY (tutorial_id) REFERENCES tutorials(tutorial_id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_file_id) REFERENCES uploaded_files(uploaded_file_id) ON DELETE CASCADE
);