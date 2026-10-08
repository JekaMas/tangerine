CREATE TABLE accounts (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    email text NOT NULL UNIQUE CHECK (length(email) BETWEEN 3 AND 254),
    password_hash text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE sessions (
    token_hash char(64) PRIMARY KEY,
    account_id uuid NOT NULL REFERENCES accounts(id),
    expires_at timestamptz NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX sessions_account_id ON sessions(account_id);
CREATE INDEX sessions_expires_at ON sessions(expires_at);
-- A foundation catalog only. Insertion/publication is deliberately not exposed
-- until the original version/key/reviewer contracts are available.
CREATE TABLE exercise_catalog (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    title text NOT NULL CHECK (length(title) BETWEEN 1 AND 200),
    published_at timestamptz NOT NULL,
    source_revision text NOT NULL,
    audio_sha256 char(64) NOT NULL CHECK (audio_sha256 ~ '^[0-9a-f]{64}$')
);
