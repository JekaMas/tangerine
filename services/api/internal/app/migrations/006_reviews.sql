-- Explicit optional foreground review; previous checkpoint events remain immutable.
CREATE TABLE review_checkpoint (
 id varchar(128) PRIMARY KEY,
 case_version_id varchar(128) NOT NULL REFERENCES document(id) ON DELETE RESTRICT,
 attempt_id varchar(128) REFERENCES entity_head(id) ON DELETE RESTRICT,
 operation_id varchar(128) REFERENCES operation(id) ON DELETE RESTRICT,
 epoch bigint NOT NULL DEFAULT 0,
 deadline_at timestamptz,
 revision bigint NOT NULL DEFAULT 0,
 payload jsonb NOT NULL
);
CREATE INDEX review_case_history ON review_checkpoint(case_version_id,id);
CREATE INDEX review_attempt_history ON review_checkpoint(attempt_id,id);
CREATE TABLE review_event (
 review_id varchar(128) NOT NULL REFERENCES review_checkpoint(id) ON DELETE RESTRICT,
 revision bigint NOT NULL,
 payload jsonb NOT NULL,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 PRIMARY KEY(review_id,revision)
);
CREATE TABLE reviewed_case_successor (
 old_case_version_id varchar(128) PRIMARY KEY REFERENCES document(id) ON DELETE RESTRICT,
 new_case_version_id varchar(128) NOT NULL UNIQUE REFERENCES document(id) ON DELETE RESTRICT,
 review_id varchar(128) NOT NULL REFERENCES review_checkpoint(id) ON DELETE RESTRICT,
 correspondence_id varchar(128) NOT NULL REFERENCES document(id) ON DELETE RESTRICT
);
