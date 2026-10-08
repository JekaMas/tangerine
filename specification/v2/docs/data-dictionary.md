# Data dictionary

All active draft fields are indexed in language/field-index.json with exact pointers and hashes. domain/persistence-map.json declares storage classes. Each description must be read with its type/nullability/constraints and docs/cross-field-invariants.md. These are definitions, not source conformance or persisted application evidence. FRC-006/FRC-010/FRC-018 remain ownership, persistence and semantic projection gaps.

| Record | Version | Storage | Fields |
|---|---|---|---:|
| accept-candidate-request | schema hash | derived DTO or actual operation input/output receipt | 3 |
| adjudication | schema hash | document.payload | 11 |
| answer-write | schema hash | document.payload | 2 |
| approval-record | 1.0.0 | document.payload | 12 |
| asset-reservation-request | schema hash | derived DTO or actual operation input/output receipt | 8 |
| asset | 2.0.0 | document.payload | 16 |
| attempt-start-request | schema hash | derived DTO or actual operation input/output receipt | 3 |
| attempt-summary | schema hash | derived DTO or actual operation input/output receipt | 6 |
| attempt-view | schema hash | derived DTO or actual operation input/output receipt | 11 |
| attempt | 2.0.0 | document.payload | 25 |
| audio-measurement | schema hash | document.payload | 15 |
| auxiliary-results | 2.0.0 | document.payload | 139 |
| backup-manifest | 2.0.0 | document.payload | 25 |
| backup-request | schema hash | derived DTO or actual operation input/output receipt | 2 |
| blind-annotation | 2.0.0 | document.payload | 21 |
| blind-review-view | schema hash | Derived view; durable source record remains private | 6 |
| blueprint-write | schema hash | document.payload | 31 |
| blueprint | 2.0.0 | document.payload | 33 |
| cancel-request | schema hash | derived DTO or actual operation input/output receipt | 1 |
| candidate-envelope | schema hash | document.payload | 4 |
| capability-record | schema hash | document.payload | 13 |
| case-candidate | 1.0.0 | document.payload | 71 |
| case-head | schema hash | document.payload | 9 |
| claim-extraction | 2.0.0 | document.payload | 46 |
| common | schema hash | derived DTO or actual operation input/output receipt | 10 |
| configuration-view | schema hash | derived DTO or actual operation input/output receipt | 9 |
| configuration | 2.0.0 | document.payload | 28 |
| connector-configuration | 2.0.0 | document.payload | 12 |
| corpus-record | 1.0.0 | document.payload | 26 |
| deletion-request | 2.0.0 | derived DTO or actual operation input/output receipt | 14 |
| difficulty-study | 2.0.0 | document.payload | 14 |
| disclosure-record | 2.0.0 | document.payload | 8 |
| dispute | 2.0.0 | document.payload | 18 |
| effective-binding | 2.0.0 | document.payload | 22 |
| error-opportunity | schema hash | document.payload | 11 |
| error-response | schema hash | derived DTO or actual operation input/output receipt | 8 |
| evaluation-key | 2.0.0 | document.payload | 115 |
| evaluator-output | 1.0.0 | derived DTO or actual operation input/output receipt | 26 |
| evidence | 2.0.0 | document.payload | 20 |
| exact-rational | schema hash | derived DTO or actual operation input/output receipt | 2 |
| extraction-input | 2.0.0 | derived DTO or actual operation input/output receipt | 9 |
| feedback-input | 2.0.0 | derived DTO or actual operation input/output receipt | 10 |
| feedback-output | 2.0.0 | derived DTO or actual operation input/output receipt | 11 |
| feedback | 2.0.0 | document.payload | 13 |
| generation-input | 2.0.0 | derived DTO or actual operation input/output receipt | 16 |
| generation-request | schema hash | derived DTO or actual operation input/output receipt | 4 |
| ground-truth | 2.0.0 | document.payload | 118 |
| health | schema hash | derived DTO or actual operation input/output receipt | 6 |
| holdout-report | 2.0.0 | document.payload | 18 |
| import-report | 2.0.0 | document.payload | 23 |
| import-request | schema hash | derived DTO or actual operation input/output receipt | 4 |
| judgment-issue | 2.0.0 | document.payload | 8 |
| key-disclosure | schema hash | derived DTO or actual operation input/output receipt | 3 |
| key-write | schema hash | document.payload | 3 |
| library-item | schema hash | derived DTO or actual operation input/output receipt | 7 |
| linguistic-audit-input | 2.0.0 | derived DTO or actual operation input/output receipt | 8 |
| linguistic-audit | 2.0.0 | document.payload | 16 |
| llm-profile | schema hash | Derived projection/configuration member; not an independent evidence document | 14 |
| maintenance-request | schema hash | derived DTO or actual operation input/output receipt | 3 |
| mapping-input | 2.0.0 | derived DTO or actual operation input/output receipt | 12 |
| measure-request | schema hash | derived DTO or actual operation input/output receipt | 3 |
| normalization | 2.0.0 | document.payload | 13 |
| operation-result | schema hash | derived DTO or actual operation input/output receipt | 9 |
| operation-status | schema hash | derived DTO or actual operation input/output receipt | 10 |
| permission-grant | 2.0.0 | document.payload | 17 |
| person | 2.0.0 | document.payload | 9 |
| playback-event | 2.0.0 | document.payload | 10 |
| prepare-view | schema hash | derived DTO or actual operation input/output receipt | 6 |
| provider-receipt | 2.0.0 | document.payload | 22 |
| qualification | 2.0.0 | document.payload | 12 |
| rationale | 2.0.0 | document.payload | 11 |
| raw-record | 2.0.0 | document.payload | 13 |
| reconsider-request | schema hash | derived DTO or actual operation input/output receipt | 3 |
| render-constraint | schema hash | document.payload | 11 |
| render-plan | 2.0.0 | document.payload | 35 |
| render-request | schema hash | derived DTO or actual operation input/output receipt | 2 |
| restore-request | schema hash | derived DTO or actual operation input/output receipt | 3 |
| result-envelope | 2.0.0 | document.payload | 11 |
| result-revision | 2.0.0 | document.payload | 11 |
| retry-request | schema hash | derived DTO or actual operation input/output receipt | 2 |
| review-context | 2.0.0 | document.payload | 12 |
| review-decision | 2.0.0 | document.payload | 20 |
| score-result | 2.0.0 | document.payload | 406 |
| scoring-input | schema hash | derived DTO or actual operation input/output receipt | 28 |
| source-format-binding | 2.0.0 | document.payload | 16 |
| source-release | 2.0.0 | document.payload | 26 |
| source-status | schema hash | document.payload | 7 |
| speech-render-result | schema hash | document.payload | 10 |
| split-manifest | 2.0.0 | document.payload | 17 |
| stage-cache | 2.0.0 | document.payload | 15 |
| taxonomy-context | schema hash | derived DTO or actual operation input/output receipt | 13 |
| teacher-gold | 2.0.0 | document.payload | 17 |
| teacher-key | 2.0.0 | Derived view; durable source record remains private | 113 |
| teacher-rationale | schema hash | Derived projection/configuration member; not an independent evidence document | 6 |
| teacher-start-view | schema hash | derived DTO or actual operation input/output receipt | 11 |
| transformation | 2.0.0 | document.payload | 12 |
| transition-request | schema hash | derived DTO or actual operation input/output receipt | 3 |
| unit-correspondence | 2.0.0 | document.payload | 11 |
| verification-report | 1.0.0 | document.payload | 26 |
