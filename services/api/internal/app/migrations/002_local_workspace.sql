-- Preserve historical local records while removing active application identity.
ALTER TABLE accounts RENAME TO legacy_accounts;
ALTER TABLE sessions RENAME TO legacy_sessions;
CREATE TABLE workspaces (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    singleton boolean NOT NULL DEFAULT true UNIQUE CHECK (singleton),
    created_at timestamptz NOT NULL DEFAULT now()
);
INSERT INTO workspaces(singleton) VALUES(true) ON CONFLICT(singleton) DO NOTHING;
ALTER TABLE exercise_catalog ADD COLUMN public_context text;
ALTER TABLE exercise_catalog ADD COLUMN duration_ms integer CHECK (duration_ms > 0);
ALTER TABLE exercise_catalog ADD COLUMN format text CHECK (format IN ('monologue','dialogue'));
ALTER TABLE exercise_catalog ADD COLUMN difficulty text CHECK (difficulty IN ('unrated','easy','medium','hard','expert'));
ALTER TABLE exercise_catalog ADD COLUMN availability text CHECK (availability IN ('published','retired','quarantined','rights_restricted'));
-- Unbound legacy rows remain stored, without inventing missing public/audio metadata.
