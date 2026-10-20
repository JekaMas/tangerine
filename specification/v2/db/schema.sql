-- Reference DDL for the local workspace. No application runtime was executed here.
BEGIN;
CREATE TABLE workspace (
 id text PRIMARY KEY CHECK (id = 'local'),
 permission_epoch bigint NOT NULL DEFAULT 0 CHECK (permission_epoch >= 0),
 maintenance_mode boolean NOT NULL DEFAULT false,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE TABLE schema_registry (
 kind text NOT NULL,
 version text NOT NULL,
 sha256 char(64) NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
 schema_json jsonb NOT NULL CHECK (jsonb_typeof(schema_json) = 'object'),
 PRIMARY KEY (kind, version, sha256)
);
CREATE TABLE document (
 id varchar(128) PRIMARY KEY,
 workspace_id text NOT NULL REFERENCES workspace(id) ON DELETE RESTRICT CHECK (workspace_id = 'local'),
 kind text NOT NULL,
 schema_version text NOT NULL,
 schema_sha256 char(64) NOT NULL,
 payload jsonb NOT NULL CHECK (jsonb_typeof(payload) = 'object'),
 payload_sha256 char(64) NOT NULL CHECK (payload_sha256 ~ '^[0-9a-f]{64}$'),
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 FOREIGN KEY (kind, schema_version, schema_sha256) REFERENCES schema_registry(kind, version, sha256) ON DELETE RESTRICT,
 UNIQUE(id, kind), UNIQUE(id, payload_sha256)
);
CREATE TABLE entity_head (
 id varchar(128) PRIMARY KEY,
 workspace_id text NOT NULL REFERENCES workspace(id) ON DELETE RESTRICT CHECK(workspace_id = 'local'),
 kind text NOT NULL,
 document_id varchar(128) NOT NULL,
 revision bigint NOT NULL CHECK(revision >= 0),
 state text NOT NULL,
 FOREIGN KEY(document_id, kind) REFERENCES document(id, kind) ON DELETE RESTRICT,
 UNIQUE(kind, id)
);
CREATE TABLE object_node (
 node_id varchar(128) NOT NULL,
 scope_id varchar(128) NOT NULL,
 kind text NOT NULL,
 document_id varchar(128) NOT NULL REFERENCES document(id) ON DELETE RESTRICT,
 json_pointer text NOT NULL,
 content_sha256 char(64) NOT NULL CHECK(content_sha256 ~ '^[0-9a-f]{64}$'),
 case_version_id varchar(128),
 PRIMARY KEY(node_id, scope_id),
 UNIQUE(node_id, scope_id, kind, content_sha256),
 UNIQUE(document_id, json_pointer),
 FOREIGN KEY(case_version_id) REFERENCES document(id) ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE object_reference (
 source_document_id varchar(128) NOT NULL REFERENCES document(id) ON DELETE RESTRICT,
 source_pointer text NOT NULL,
 ordinal integer NOT NULL DEFAULT 0 CHECK(ordinal >= 0),
 target_id varchar(128) NOT NULL,
 target_scope_id varchar(128) NOT NULL,
 target_kind text NOT NULL,
 expected_sha256 char(64) NOT NULL,
 relation text NOT NULL,
 PRIMARY KEY(source_document_id, source_pointer, ordinal),
 FOREIGN KEY(target_id, target_scope_id, target_kind, expected_sha256)
   REFERENCES object_node(node_id, scope_id, kind, content_sha256)
   ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE operation (
 id varchar(128) PRIMARY KEY,
 workspace_id text NOT NULL REFERENCES workspace(id) CHECK(workspace_id='local'),
 operation_name text NOT NULL,
 idempotency_key uuid NOT NULL,
 request_sha256 char(64) NOT NULL CHECK(request_sha256 ~ '^[0-9a-f]{64}$'),
 state text NOT NULL CHECK(state IN('reserved','running','complete','failed','cancelled','interrupted')),
 subject_id varchar(128),
 input_document_id varchar(128) REFERENCES document(id) ON DELETE RESTRICT,
 result_document_id varchar(128) REFERENCES document(id) ON DELETE RESTRICT,
 error_document_id varchar(128) REFERENCES document(id) ON DELETE RESTRICT,
 started_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 finished_at timestamptz,
 UNIQUE(workspace_id, operation_name, idempotency_key)
);
CREATE TABLE evaluation_lease (
 attempt_id varchar(128) PRIMARY KEY REFERENCES entity_head(id) ON DELETE RESTRICT,
 epoch bigint NOT NULL CHECK(epoch >= 0),
 token uuid NOT NULL,
 operation_id varchar(128) NOT NULL REFERENCES operation(id) ON DELETE RESTRICT,
 acquired_at timestamptz NOT NULL,
 deadline_at timestamptz NOT NULL,
 expires_at timestamptz NOT NULL,
 CHECK(deadline_at = acquired_at + interval '270 seconds'),
 CHECK(expires_at = acquired_at + interval '300 seconds')
);
CREATE TABLE asset_location (
 asset_id varchar(128) PRIMARY KEY REFERENCES entity_head(id) ON DELETE RESTRICT,
 storage_key varchar(128) NOT NULL UNIQUE,
 state text NOT NULL CHECK(state IN('reserved','uploading','bytes_verified','linked','orphaned','erasing','erased')),
 byte_count numeric(40,0) CHECK(byte_count >= 0),
 sha256 char(64) CHECK(sha256 ~ '^[0-9a-f]{64}$'),
 verified_at timestamptz,
 linked_at timestamptz,
 CHECK(state NOT IN('bytes_verified','linked') OR (byte_count IS NOT NULL AND sha256 IS NOT NULL AND verified_at IS NOT NULL)),
 CHECK(state <> 'linked' OR linked_at IS NOT NULL)
);
CREATE TABLE stage_cache_index (
 cache_key char(64) PRIMARY KEY CHECK(cache_key ~ '^[0-9a-f]{64}$'),
 document_id varchar(128) NOT NULL REFERENCES document(id) ON DELETE RESTRICT,
 attempt_id varchar(128) NOT NULL REFERENCES entity_head(id) ON DELETE RESTRICT,
 binding_sha256 char(64) NOT NULL,
 permission_epoch bigint CHECK(permission_epoch >= 0), -- legacy metadata, not an admission or cache gate
 complete boolean NOT NULL CHECK(complete)
);
CREATE TABLE playback_index (
 event_id varchar(128) PRIMARY KEY REFERENCES document(id) ON DELETE RESTRICT,
 attempt_id varchar(128) NOT NULL REFERENCES entity_head(id) ON DELETE RESTRICT,
 page_instance_id varchar(128) NOT NULL,
 event_sequence bigint NOT NULL CHECK(event_sequence >= 0),
 received_at timestamptz NOT NULL,
 UNIQUE(attempt_id, page_instance_id, event_sequence)
);
CREATE TABLE usage_ledger (
 receipt_id varchar(128) PRIMARY KEY REFERENCES document(id) ON DELETE RESTRICT,
 operation_id varchar(128) NOT NULL REFERENCES operation(id) ON DELETE RESTRICT,
 provider text NOT NULL,
 input_units numeric(40,0) CHECK(input_units >= 0),
 output_units numeric(40,0) CHECK(output_units >= 0),
 known_cost_usd numeric(30,12) CHECK(known_cost_usd >= 0),
 reserved_cost_usd numeric(30,12) CHECK(reserved_cost_usd >= 0),
 charge_state text NOT NULL CHECK(charge_state IN('known','estimated','unknown','not_billable')),
 price_profile_sha256 char(64),
 occurred_at timestamptz NOT NULL
);
CREATE TABLE audit_event (
 sequence bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 workspace_id text NOT NULL REFERENCES workspace(id) CHECK(workspace_id='local'),
 operation_id varchar(128) REFERENCES operation(id) ON DELETE SET NULL,
 action text NOT NULL,
 subject_document_id varchar(128) REFERENCES document(id) ON DELETE SET NULL,
 previous_event_sha256 char(64),
 event_sha256 char(64) UNIQUE CHECK(event_sha256 ~ '^[0-9a-f]{64}$'),
 details_document_id varchar(128) REFERENCES document(id) ON DELETE SET NULL,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE TABLE deletion_tombstone (
 id varchar(128) PRIMARY KEY,
 original_document_id varchar(128) NOT NULL,
 retained_digest char(64),
 deletion_request_id varchar(128) NOT NULL,
 permitted_retention_basis text NOT NULL,
 deleted_at timestamptz NOT NULL
);
CREATE TABLE migration_receipt (
 migration_id text PRIMARY KEY,
 source_sha256 char(64) NOT NULL CHECK(source_sha256 ~ '^[0-9a-f]{64}$'),
 applied_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 contract_vector_sha256 char(64) NOT NULL CHECK (contract_vector_sha256 ~ '^[0-9a-f]{64}$')
);
CREATE INDEX document_kind_created_idx ON document(kind, created_at, id);
CREATE INDEX entity_head_kind_state_idx ON entity_head(kind, state, id);
CREATE INDEX object_node_case_idx ON object_node(case_version_id, kind);
CREATE INDEX object_reference_target_idx ON object_reference(target_id, target_scope_id);
CREATE INDEX operation_state_idx ON operation(state, started_at);
CREATE INDEX usage_ledger_time_idx ON usage_ledger(occurred_at);
CREATE INDEX audit_event_subject_idx ON audit_event(subject_document_id, sequence);

CREATE FUNCTION reject_document_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF TG_OP = 'DELETE' AND current_setting('tangerine.maintenance_delete', true) = 'on' THEN RETURN OLD; END IF;
 RAISE EXCEPTION 'immutable record: append a version; explicit local maintenance can delete';
END $$;
CREATE TRIGGER document_immutable BEFORE UPDATE OR DELETE ON document FOR EACH ROW EXECUTE FUNCTION reject_document_mutation();
-- Local audit is diagnostic; deletion may remove or null records. No tamper-evident chain or unerasable payload is required.
COMMIT;
-- Immutable published listening versions; existing render/key records stay intact.
CREATE TABLE listening_case (
 case_version_id varchar(128) PRIMARY KEY REFERENCES document(id) ON DELETE RESTRICT,
 source_key_id varchar(128) NOT NULL UNIQUE REFERENCES document(id) ON DELETE RESTRICT,
 audio_asset_id varchar(128) NOT NULL REFERENCES asset_location(asset_id) ON DELETE RESTRICT,
 case_sha256 char(64) NOT NULL,
 audio_sha256 char(64) NOT NULL,
 sample_count bigint NOT NULL CHECK(sample_count>0),
 task_components jsonb NOT NULL CHECK(jsonb_typeof(task_components)='object')
);
CREATE TABLE attempt_context (
 attempt_id varchar(128) PRIMARY KEY REFERENCES entity_head(id) ON DELETE RESTRICT,
 case_version_id varchar(128) NOT NULL REFERENCES listening_case(case_version_id) ON DELETE RESTRICT,
 case_item jsonb NOT NULL CHECK(jsonb_typeof(case_item)='object'),
 configuration jsonb NOT NULL CHECK(jsonb_typeof(configuration)='object'),
 prompt_bundle jsonb NOT NULL CHECK(jsonb_typeof(prompt_bundle)='object'),
 evaluator_bindings jsonb NOT NULL CHECK(jsonb_typeof(evaluator_bindings)='array'),
 requested_language text NOT NULL CHECK(requested_language IN('en','ru')),
 result_id varchar(128) REFERENCES document(id) ON DELETE RESTRICT
);
CREATE INDEX attempt_history_idx ON entity_head(kind,id) WHERE kind='attempt';

ALTER TABLE playback_index ADD COLUMN attempt_revision bigint NOT NULL DEFAULT 0 CHECK(attempt_revision>=0);
