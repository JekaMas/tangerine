-- Foreground owner/checkpoint pointer. Immutable stage records retain the data.
CREATE TABLE interpretation_checkpoint (
 attempt_id varchar(128) PRIMARY KEY REFERENCES entity_head(id) ON DELETE RESTRICT,
 document_id varchar(128) REFERENCES document(id) ON DELETE RESTRICT,
 operation_id varchar(128) NOT NULL REFERENCES operation(id) ON DELETE RESTRICT,
 epoch bigint NOT NULL,
 deadline_at timestamptz NOT NULL
);
