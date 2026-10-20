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
