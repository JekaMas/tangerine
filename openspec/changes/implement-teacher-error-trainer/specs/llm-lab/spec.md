# Local prompt, context and quality management

## ADDED Requirements

### Requirement: LAB-01 Optional local MLflow workspace

The system SHALL provide the optional MLflow 3.17.0 LLM Lab specified in specification/v2/docs/llm-lab.md, using one local container, SQLite and local artifacts. Normal startup and learner workflows SHALL work without Lab. Local tooling SHALL need no account, cloud service, new host runtime or provider call at startup.

#### Scenario: LAB-01 Open the local workspace

- **WHEN** the operator invokes the optional lab helper
- **THEN** the versioned local UI and persistent registry/experiment store become available on loopback without inference

#### Scenario: LAB-01 Lab outage is isolated

- **GIVEN** Lab is stopped, unavailable or its port is occupied
- **WHEN** ordinary generation or answer checking uses a saved bundle
- **THEN** saved local bindings and native receipts remain usable and no learner operation depends on Lab readiness

### Requirement: LAB-02 Immutable prompt and context activation

The system SHALL support editing, comparing, exporting, activating and reverting complete prompt/context bundles with every original stage/phase binding. Activation SHALL freeze numeric registry/content/schema/profile identities for new operations, preserve old attempts, and invalidate semantic-cache reuse when their effective binding changes. Prompt editing SHALL not require a human approval or a quality gate.

#### Scenario: LAB-02 Activate a selected version

- **GIVEN** an exported complete bundle with a new mapping prompt and its context policy
- **WHEN** the operator activates it
- **THEN** new operations use that saved exact bundle while historical decisions remain linked to their earlier versions

#### Scenario: LAB-02 Alias drift and stale cache cannot change an operation

- **GIVEN** a registry alias moves or a prior cached decision belongs to another bundle
- **WHEN** a frozen operation proceeds
- **THEN** it keeps its selected numeric/local version and does not reuse the mismatched decision or silently fall back

### Requirement: LAB-03 Inspectable stage context

The system SHALL save exact per-attempt context snapshots with ordered component/version/hash/budget metadata and private rendered input assets. It SHALL preserve existing stage disclosure and provider-role rules, selected source provenance and input fidelity. Context editing SHALL never silently truncate required answer/key/evidence or leak the key into blind extraction.

#### Scenario: LAB-03 Inspect a mapping context

- **WHEN** the operator opens a recorded mapping attempt
- **THEN** the exact submitted answer, frozen key, selected context components, prompt/budget/schema versions and actual rendered request can be traced through private assets

#### Scenario: LAB-03 Required context exceeds its budget

- **GIVEN** the required context does not fit or a policy would reveal the key to blind extraction
- **WHEN** the stage prepares its actual request
- **THEN** it retains the input and reports the real component/conflict rather than truncating data or manufacturing a grade

### Requirement: LAB-04 Actual traces and nonblocking debugging

The system SHALL retain one operation trace and linked per-stage/attempt spans, including two generation phases, retries, repairs and cache hits. Go/Python SHALL export selected diagnostic copies through local OTLP/HTTP without a collector. Export failure SHALL preserve native receipts/results and permit explicit export-only sync.

#### Scenario: LAB-04 Debug a repaired reply

- **WHEN** a provider reply needs semantic repair
- **THEN** the trace links the original input/reply, normalization error, repair attempt, actual usage and resulting receipt without treating the two calls as one

#### Scenario: LAB-04 Failed export and cache inspection are honest

- **GIVEN** export fails or an existing stage result is inspected
- **WHEN** the diagnostic row is displayed or synced
- **THEN** it reports unexported/cache-hit status, makes no new inference for sync and does not record invented tokens/cost or fail grading

### Requirement: LAB-05 Controlled quality experiments

The system SHALL support explicit serial experiments comparing frozen prompt/context/model variants through the same native generation/evaluation/scoring owners. It SHALL preserve case/reference/split/scorer/repetition identity and actual expectation origin, report positive/negative coverage across all 122 leaves, and retain every failed/cancelled/not-run row. Semantic judges SHALL use explicit configurable profiles without human reviewers or default-provider fallback.

#### Scenario: LAB-05 Compare variants on saved cases

- **GIVEN** baseline/candidate bundles and fixed answer/key/audio cases
- **WHEN** the operator runs the declared answer-pipeline comparison
- **THEN** paired results use identical cases/references, actual native arithmetic and each variant's actual receipts with coverage and differences

#### Scenario: LAB-05 Partial or self-referential evaluation stays qualified

- **GIVEN** some rows fail/cancel or expectations come from the candidate's own mutation list
- **WHEN** the experiment is reported
- **THEN** all missing/error rows stay visible and self-consistency is not reported as independent benchmark accuracy or full-taxonomy coverage

### Requirement: LAB-06 Separate exact diagnostic metrics

The system SHALL calculate the 22 diagnostic metrics/populations in specification/v2/domain/llm-quality-metrics.v1.json separately from all 42 original grading equations. It SHALL report applicability, denominators, coverage and paired exclusions, preserve unknowns as N/A, and compare quality/latency/usage/cost without an invented blended score or mandatory activation threshold.

#### Scenario: LAB-06 Quality and latency differences are explainable

- **WHEN** two completed variants have applicable reference mappings and observed durations
- **THEN** diagnostics retain exact counts/ratios, nearest-rank latency samples and paired comparison populations while native learner grades remain unchanged

#### Scenario: LAB-06 Unknown usage and absent acoustic observations remain unavailable

- **GIVEN** token/cost components or actual acoustic confirmation are missing
- **WHEN** aggregate metrics are displayed
- **THEN** unknown totals/confirmation stay N/A with known subtotals/exclusions and text-only judgments do not become measured audio success

### Requirement: LAB-07 Local privacy and recovery

The system SHALL keep diagnostic export local with telemetry disabled, content capture opt-in and credential/source-private fields omitted. It SHALL include consistent optional Lab data and saved native bundles/experiments in backup and remove copied sensitive bodies on explicit deletion. Lab failure SHALL never justify claiming cleanup, export or restore completed when it did not.

#### Scenario: LAB-07 Restore a private local Lab backup

- **WHEN** a consistent backup is restored into new volumes
- **THEN** saved bundles, experiments and available diagnostic history are preserved without credentials, inference or losing the previous workspace

#### Scenario: LAB-07 Export and deletion preserve privacy accounting

- **GIVEN** a trace contains selected private content or Lab deletion is unavailable
- **WHEN** an export or deletion is requested
- **THEN** secrets/source-private fields are omitted from export and unsuccessful copied-body cleanup remains explicitly pending for local retry
