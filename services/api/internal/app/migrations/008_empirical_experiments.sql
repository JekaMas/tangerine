-- Explicit foreground experiments and immutable descriptive report snapshots.
CREATE TABLE quality_experiment (
 id text PRIMARY KEY,
 frozen_asset_id varchar(128) NOT NULL REFERENCES asset_location(asset_id),
 payload jsonb NOT NULL,
 revision bigint NOT NULL DEFAULT 0,
 active_operation_id varchar(128) REFERENCES operation(id),
 lease_until timestamptz,
 cancel_requested boolean NOT NULL DEFAULT false,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE TABLE empirical_report (
 id text PRIMARY KEY,
 asset_id varchar(128) NOT NULL REFERENCES asset_location(asset_id),
 input_asset_id varchar(128) NOT NULL REFERENCES asset_location(asset_id),
 title text NOT NULL,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE quality_experiment_event (
 experiment_id text NOT NULL REFERENCES quality_experiment(id),
 revision bigint NOT NULL,
 payload jsonb NOT NULL,
 PRIMARY KEY(experiment_id,revision)
);
CREATE TRIGGER quality_experiment_event_immutable BEFORE UPDATE OR DELETE ON quality_experiment_event FOR EACH ROW EXECUTE FUNCTION reject_document_mutation();
CREATE TABLE quality_call (
 row_operation_id varchar(128) NOT NULL REFERENCES operation(id),
 receipt_id varchar(128) PRIMARY KEY REFERENCES document(id),
 attempt_kind text NOT NULL,
 delivered boolean NOT NULL,
 projected boolean NOT NULL
);
CREATE TABLE quality_export (
 experiment_id text NOT NULL REFERENCES quality_experiment(id),
 asset_id varchar(128) PRIMARY KEY REFERENCES asset_location(asset_id),
 payload jsonb NOT NULL,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
