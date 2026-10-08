# Data dictionary

The active dictionary consists of all closed schemas in `contracts/`.
`language/field-index.json` locates every field through its exact schema pointer.
`domain/persistence-map.json` binds each schema to durable storage or a derived transport object.
No earlier tenant or authenticated-user field reintroduces accounts into this local product.

A field description is not its complete validation rule. Read the referenced schema for types, nulls, enums, ranges, and conditional branches.
Cross-record constraints are in `docs/cross-field-invariants.md` and `docs/persistence.md`.

## Contract index

| Record | Version field | Persistence | Field definitions |
|---|---|---|---:|
| `accept-candidate-request` | `DTO identified by exact schema hash` | Derived DTO or operation receipt | 3 |
| `adjudication` | `DTO identified by exact schema hash` | Immutable document | 11 |
| `answer-write` | `DTO identified by exact schema hash` | Immutable document | 2 |
| `approval-record` | `1.0.0` | Immutable document | 12 |
| `asset-reservation-request` | `DTO identified by exact schema hash` | Derived DTO or operation receipt | 8 |
| `asset` | `2.0.0` | Immutable document | 16 |
| `attempt-start-request` | `DTO identified by exact schema hash` | Derived DTO or operation receipt | 3 |
| `attempt-summary` | `DTO identified by exact schema hash` | Derived DTO or operation receipt | 6 |
| `attempt-view` | `DTO identified by exact schema hash` | Derived DTO or operation receipt | 11 |
| `attempt` | `2.0.0` | Immutable document | 25 |
| `audio-measurement` | `DTO identified by exact schema hash` | Immutable document | 15 |
| `auxiliary-results` | `2.0.0` | Immutable document | 139 |
| `backup-manifest` | `2.0.0` | Immutable document | 25 |
| `backup-request` | `DTO identified by exact schema hash` | Derived DTO or operation receipt | 2 |
| `blind-annotation` | `2.0.0` | Immutable document | 21 |
| `blueprint-write` | `DTO identified by exact schema hash` | Immutable document | 31 |
| `blueprint` | `2.0.0` | Immutable document | 33 |
| `cancel-request` | `DTO identified by exact schema hash` | Derived DTO or operation receipt | 1 |
| `candidate-envelope` | `DTO identified by exact schema hash` | Immutable document | 4 |
| `capability-record` | `DTO identified by exact schema hash` | Immutable document | 13 |
| `case-candidate` | `1.0.0` | Immutable document | 71 |
| `case-head` | `DTO identified by exact schema hash` | Immutable document | 9 |
| `claim-extraction` | `2.0.0` | Immutable document | 46 |
| `common` | `DTO identified by exact schema hash` | Derived DTO or operation receipt | 10 |
| `configuration-view` | `DTO identified by exact schema hash` | Derived DTO or operation receipt | 9 |
| `configuration` | `2.0.0` | Immutable document | 20 |
| `connector-configuration` | `2.0.0` | Immutable document | 12 |
| `corpus-record` | `1.0.0` | Immutable document | 26 |
| `deletion-request` | `2.0.0` | Derived DTO or operation receipt | 14 |
| `difficulty-study` | `2.0.0` | Immutable document | 14 |
| `disclosure-record` | `2.0.0` | Immutable document | 8 |
| `dispute` | `2.0.0` | Immutable document | 18 |
| `effective-binding` | `2.0.0` | Immutable document | 22 |
| `error-opportunity` | `DTO identified by exact schema hash` | Immutable document | 11 |
| `error-response` | `DTO identified by exact schema hash` | Derived DTO or operation receipt | 8 |
| `evaluation-key` | `2.0.0` | Immutable document | 115 |
| `evaluator-output` | `1.0.0` | Derived DTO or operation receipt | 26 |
| `evidence` | `2.0.0` | Immutable document | 20 |
| `exact-rational` | `DTO identified by exact schema hash` | Derived DTO or operation receipt | 2 |
| `extraction-input` | `2.0.0` | Derived DTO or operation receipt | 9 |
| `feedback-input` | `2.0.0` | Derived DTO or operation receipt | 10 |
| `feedback-output` | `2.0.0` | Derived DTO or operation receipt | 11 |
| `feedback` | `2.0.0` | Immutable document | 13 |
| `generation-input` | `2.0.0` | Derived DTO or operation receipt | 16 |
| `generation-request` | `DTO identified by exact schema hash` | Derived DTO or operation receipt | 4 |
| `ground-truth` | `2.0.0` | Immutable document | 118 |
| `health` | `DTO identified by exact schema hash` | Derived DTO or operation receipt | 6 |
| `holdout-report` | `2.0.0` | Immutable document | 18 |
| `import-report` | `2.0.0` | Immutable document | 23 |
| `import-request` | `DTO identified by exact schema hash` | Derived DTO or operation receipt | 4 |
| `judgment-issue` | `2.0.0` | Immutable document | 8 |
| `key-disclosure` | `DTO identified by exact schema hash` | Derived DTO or operation receipt | 3 |
| `key-write` | `DTO identified by exact schema hash` | Immutable document | 3 |
| `library-item` | `DTO identified by exact schema hash` | Derived DTO or operation receipt | 7 |
| `linguistic-audit-input` | `2.0.0` | Derived DTO or operation receipt | 8 |
| `linguistic-audit` | `2.0.0` | Immutable document | 16 |
| `maintenance-request` | `DTO identified by exact schema hash` | Derived DTO or operation receipt | 3 |
| `mapping-input` | `2.0.0` | Derived DTO or operation receipt | 12 |
| `measure-request` | `DTO identified by exact schema hash` | Derived DTO or operation receipt | 3 |
| `normalization` | `2.0.0` | Immutable document | 13 |
| `operation-result` | `DTO identified by exact schema hash` | Derived DTO or operation receipt | 9 |
| `operation-status` | `DTO identified by exact schema hash` | Derived DTO or operation receipt | 10 |
| `permission-grant` | `2.0.0` | Immutable document | 17 |
| `person` | `2.0.0` | Immutable document | 9 |
| `playback-event` | `2.0.0` | Immutable document | 10 |
| `prepare-view` | `DTO identified by exact schema hash` | Derived DTO or operation receipt | 6 |
| `provider-receipt` | `2.0.0` | Immutable document | 22 |
| `qualification` | `2.0.0` | Immutable document | 12 |
| `rationale` | `2.0.0` | Immutable document | 11 |
| `raw-record` | `2.0.0` | Immutable document | 13 |
| `reconsider-request` | `DTO identified by exact schema hash` | Derived DTO or operation receipt | 3 |
| `release-manifest` | `2.0.0` | Immutable document | 20 |
| `render-constraint` | `DTO identified by exact schema hash` | Immutable document | 11 |
| `render-plan` | `2.0.0` | Immutable document | 35 |
| `render-request` | `DTO identified by exact schema hash` | Derived DTO or operation receipt | 2 |
| `restore-request` | `DTO identified by exact schema hash` | Derived DTO or operation receipt | 3 |
| `result-envelope` | `2.0.0` | Immutable document | 11 |
| `result-revision` | `2.0.0` | Immutable document | 11 |
| `retry-request` | `DTO identified by exact schema hash` | Derived DTO or operation receipt | 2 |
| `review-context` | `2.0.0` | Immutable document | 12 |
| `review-decision` | `2.0.0` | Immutable document | 20 |
| `score-result` | `2.0.0` | Immutable document | 406 |
| `scoring-input` | `DTO identified by exact schema hash` | Derived DTO or operation receipt | 28 |
| `source-format-binding` | `2.0.0` | Immutable document | 16 |
| `source-release` | `2.0.0` | Immutable document | 26 |
| `source-status` | `DTO identified by exact schema hash` | Immutable document | 7 |
| `speech-render-result` | `DTO identified by exact schema hash` | Immutable document | 10 |
| `split-manifest` | `2.0.0` | Immutable document | 17 |
| `stage-cache` | `2.0.0` | Immutable document | 15 |
| `taxonomy-context` | `DTO identified by exact schema hash` | Derived DTO or operation receipt | 13 |
| `teacher-gold` | `2.0.0` | Immutable document | 17 |
| `teacher-start-view` | `DTO identified by exact schema hash` | Derived DTO or operation receipt | 11 |
| `transformation` | `2.0.0` | Immutable document | 12 |
| `transition-request` | `DTO identified by exact schema hash` | Derived DTO or operation receipt | 3 |
| `unit-correspondence` | `2.0.0` | Immutable document | 11 |
| `verification-report` | `1.0.0` | Immutable document | 26 |
