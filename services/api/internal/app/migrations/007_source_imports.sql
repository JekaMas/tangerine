-- Deterministic optional source imports. Existing migrations and user data remain.
CREATE TABLE source_file (
 id varchar(128) PRIMARY KEY,
 relative_path text NOT NULL,
 sha256 char(64) NOT NULL,
 byte_count bigint NOT NULL CHECK(byte_count>=0),
 asset_id varchar(128) NOT NULL REFERENCES asset_location(asset_id),
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 UNIQUE(relative_path,sha256,byte_count)
);
CREATE TABLE source_release (
 id varchar(128) PRIMARY KEY,
 source_id text NOT NULL,
 payload jsonb NOT NULL,
 scope_kind text NOT NULL,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE TRIGGER source_release_immutable BEFORE UPDATE OR DELETE ON source_release FOR EACH ROW EXECUTE FUNCTION reject_document_mutation();
CREATE TABLE source_member (
 release_id varchar(128) NOT NULL REFERENCES source_release(id),
 relative_path text NOT NULL,
 file_id varchar(128) NOT NULL REFERENCES source_file(id),
 component text NOT NULL,
 partition text,
 PRIMARY KEY(release_id,relative_path)
);
CREATE TABLE source_format (
 id varchar(128) PRIMARY KEY,
 source_id text NOT NULL,
 payload jsonb NOT NULL,
 program jsonb,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE TRIGGER source_format_immutable BEFORE UPDATE OR DELETE ON source_format FOR EACH ROW EXECUTE FUNCTION reject_document_mutation();
CREATE TABLE source_permission (
 id varchar(128) PRIMARY KEY,
 source_id text NOT NULL,
 payload jsonb NOT NULL,
 revoked_notice_asset_id varchar(128) REFERENCES asset_location(asset_id),
 revoked_at timestamptz
);
CREATE TABLE source_connector (
 id varchar(128) PRIMARY KEY,
 source_id text NOT NULL,
 payload jsonb NOT NULL,
 revision bigint NOT NULL DEFAULT 0
);
CREATE TABLE source_import (
 id varchar(128) PRIMARY KEY,
 release_id varchar(128) NOT NULL REFERENCES source_release(id),
 binding_id varchar(128) REFERENCES source_format(id),
 revision bigint NOT NULL DEFAULT 0,
 epoch bigint NOT NULL DEFAULT 0,
 operation_id varchar(128) REFERENCES operation(id),
 deadline_at timestamptz,
 phase text NOT NULL DEFAULT 'inventory',
 member_cursor text,
 row_cursor bigint NOT NULL DEFAULT -1,
 payload jsonb NOT NULL,
 frozen jsonb NOT NULL,
 UNIQUE(release_id,binding_id)
);
CREATE TABLE source_import_event (
 import_id varchar(128) NOT NULL REFERENCES source_import(id),
 revision bigint NOT NULL,
 payload jsonb NOT NULL,
 PRIMARY KEY(import_id,revision)
);
CREATE TRIGGER source_import_event_immutable BEFORE UPDATE OR DELETE ON source_import_event FOR EACH ROW EXECUTE FUNCTION reject_document_mutation();
CREATE TABLE source_row (
 import_id varchar(128) NOT NULL REFERENCES source_import(id),
 member text NOT NULL,
 table_name text NOT NULL,
 ordinal bigint NOT NULL,
 join_key text,
 native_row jsonb NOT NULL,
 raw_record jsonb,
 corpus_record jsonb,
 projection jsonb,
 state text NOT NULL DEFAULT 'staged',
 issues jsonb NOT NULL DEFAULT '[]',
 PRIMARY KEY(import_id,member,table_name,ordinal)
);
CREATE INDEX source_row_join_idx ON source_row(import_id,table_name,join_key,member,ordinal);
CREATE INDEX source_row_state_idx ON source_row(import_id,state,member,table_name,ordinal);
CREATE TABLE source_issue (
 import_id varchar(128) NOT NULL REFERENCES source_import(id),
 locator text NOT NULL,
 code text NOT NULL,
 detail text NOT NULL,
 PRIMARY KEY(import_id,locator,code)
);
CREATE INDEX source_release_source_idx ON source_release(source_id,created_at,id);
CREATE TABLE source_action (
 operation_id varchar(128) PRIMARY KEY REFERENCES operation(id),
 import_id varchar(128) NOT NULL REFERENCES source_import(id),
 result jsonb NOT NULL
);
ALTER TABLE source_import ADD COLUMN binding_selector text NOT NULL;
ALTER TABLE source_import ADD COLUMN created_at timestamptz NOT NULL DEFAULT clock_timestamp();
CREATE UNIQUE INDEX source_import_release_selector_idx ON source_import(release_id,binding_selector);
CREATE INDEX source_row_native_idx ON source_row USING gin(native_row jsonb_path_ops);
ALTER TABLE source_import ADD COLUMN published boolean NOT NULL DEFAULT false;
ALTER TABLE source_connector ADD COLUMN export_progress jsonb;
ALTER TABLE source_file ADD COLUMN media_metadata jsonb;
ALTER TABLE source_row ADD COLUMN transformation jsonb;

ALTER TABLE source_connector ADD COLUMN request_sha256 char(64);
