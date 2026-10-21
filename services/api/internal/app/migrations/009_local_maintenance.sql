-- Explicit local plans contain identifiers and dispositions, never deleted bodies.
CREATE TABLE local_deletion (
 id uuid PRIMARY KEY,
 plan jsonb NOT NULL,
 state text NOT NULL DEFAULT 'preview',
 created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
