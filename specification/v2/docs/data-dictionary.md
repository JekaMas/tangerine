# Complete data dictionary

Every active schema field/constraint/reference is indexed in language/field-index.json and domain/persistence-map.json. Request projections preserve original full-response data fields and assign local envelopes/counts/receipts on the server. LLM origin/modality/receipt fields replace human prerequisites while retaining native person/qualification data. Read each field with its closed canonical schema and owning cross-field/source/math/runtime contract. Metadata coverage is not application or linguistic evidence.

| Record | Version | Storage | Fields |
|---|---|---|---:|
| accept-candidate-request | schema hash | derived DTO or actual operation input/output receipt | 3 |
| adjudicate-request | schema hash | Derived DTO or actual operation/stage input/output receipt | 5 |
| adjudication | schema hash | document.payload | 18 |
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
| backup-manifest | 2.0.0 | document.payload | 11 |
| backup-request | schema hash | derived DTO or actual operation input/output receipt | 1 |
| blind-annotation | 2.0.0 | document.payload | 27 |
| blind-review-view | schema hash | Derived view; durable source record remains private | 6 |
| blind-submit-request | 2.0.0 | Derived DTO or actual operation/stage input/output receipt | 3 |
| blueprint-write | schema hash | document.payload | 32 |
| blueprint | 2.0.0 | document.payload | 34 |
| cancel-request | schema hash | derived DTO or actual operation input/output receipt | 1 |
| candidate-envelope | schema hash | document.payload | 5 |
| capability-record | schema hash | document.payload | 13 |
| case-candidate | 1.0.0 | document.payload | 80 |
| case-head | schema hash | document.payload | 9 |
| claim-extraction | 2.0.0 | document.payload | 46 |
| common | schema hash | derived DTO or actual operation input/output receipt | 10 |
| configuration-view | schema hash | derived DTO or actual operation input/output receipt | 31 |
| configuration | 2.0.0 | document.payload | 54 |
| connector-configuration | 2.0.0 | document.payload | 12 |
| connector-request | 2.0.0 | Derived DTO or actual operation/stage input/output receipt | 30 |
| corpus-record | 1.0.0 | document.payload | 26 |
| create-dispute-request | 2.0.0 | Derived DTO or actual operation/stage input/output receipt | 8 |
| create-person-request | 2.0.0 | Derived DTO or actual operation/stage input/output receipt | 8 |
| delete-plan-request | 2.0.0 | Derived DTO or actual operation/stage input/output receipt | 2 |
| deletion-request | 2.0.0 | derived DTO or actual operation input/output receipt | 20 |
| difficulty-request | 2.0.0 | Derived DTO or actual operation/stage input/output receipt | 6 |
| difficulty-study | 2.0.0 | document.payload | 14 |
| disclosure-record | 2.0.0 | document.payload | 8 |
| dispute | 2.0.0 | document.payload | 24 |
| effective-binding | 2.0.0 | document.payload | 37 |
| error-opportunity | schema hash | document.payload | 11 |
| error-response | schema hash | derived DTO or actual operation input/output receipt | 8 |
| evaluation-key | 2.0.0 | document.payload | 115 |
| evaluator-output | 1.0.0 | derived DTO or actual operation input/output receipt | 38 |
| evidence | 2.0.0 | document.payload | 20 |
| exact-rational | schema hash | derived DTO or actual operation input/output receipt | 2 |
| extraction-input | 2.0.0 | derived DTO or actual operation input/output receipt | 13 |
| feedback-input | 2.0.0 | derived DTO or actual operation input/output receipt | 10 |
| feedback-output | 2.0.0 | derived DTO or actual operation input/output receipt | 11 |
| feedback | 2.0.0 | document.payload | 13 |
| format-binding-request | 2.0.0 | Derived DTO or actual operation/stage input/output receipt | 15 |
| generation-input | 2.0.0 | derived DTO or actual operation input/output receipt | 29 |
| generation-request | schema hash | derived DTO or actual operation input/output receipt | 5 |
| grant-request | 2.0.0 | Derived DTO or actual operation/stage input/output receipt | 15 |
| ground-truth | 2.0.0 | document.payload | 118 |
| health | schema hash | derived DTO or actual operation input/output receipt | 6 |
| holdout-report | 2.0.0 | document.payload | 18 |
| import-report | 2.0.0 | document.payload | 26 |
| import-request | schema hash | derived DTO or actual operation input/output receipt | 4 |
| judgment-issue | 2.0.0 | document.payload | 9 |
| key-disclosure | schema hash | derived DTO or actual operation input/output receipt | 3 |
| key-write | schema hash | document.payload | 3 |
| library-item | schema hash | derived DTO or actual operation input/output receipt | 8 |
| linguistic-audit-input | 2.0.0 | derived DTO or actual operation input/output receipt | 8 |
| linguistic-audit | 2.0.0 | document.payload | 16 |
| llm-profile | schema hash | Derived projection/configuration member; not an independent evidence document | 26 |
| llm-review-input | 2.0.0 | Derived DTO or actual operation/stage input/output receipt | 14 |
| llm-review-output | 2.0.0 | Derived DTO or actual operation/stage input/output receipt | 13 |
| maintenance-request | schema hash | derived DTO or actual operation input/output receipt | 3 |
| mapping-input | 2.0.0 | derived DTO or actual operation input/output receipt | 16 |
| measure-request | schema hash | derived DTO or actual operation input/output receipt | 3 |
| normalization | 2.0.0 | document.payload | 13 |
| operation-result | schema hash | derived DTO or actual operation input/output receipt | 9 |
| operation-status | schema hash | derived DTO or actual operation input/output receipt | 11 |
| permission-grant | 2.0.0 | document.payload | 17 |
| person | 2.0.0 | document.payload | 9 |
| play-event-request | 2.0.0 | Derived DTO or actual operation/stage input/output receipt | 8 |
| playback-event | 2.0.0 | document.payload | 10 |
| prepare-view | schema hash | derived DTO or actual operation input/output receipt | 7 |
| provider-receipt | 2.0.0 | document.payload | 25 |
| put-config-request | 2.0.0 | Derived DTO or actual operation/stage input/output receipt | 51 |
| qualification-report-request | 2.0.0 | Derived DTO or actual operation/stage input/output receipt | 5 |
| qualification-request | 2.0.0 | Derived DTO or actual operation/stage input/output receipt | 11 |
| qualification | 2.0.0 | document.payload | 12 |
| rationale-request | 2.0.0 | Derived DTO or actual operation/stage input/output receipt | 9 |
| rationale | 2.0.0 | document.payload | 11 |
| raw-record | 2.0.0 | document.payload | 13 |
| reconsider-request | schema hash | derived DTO or actual operation input/output receipt | 3 |
| render-constraint | schema hash | document.payload | 11 |
| render-plan | 2.0.0 | document.payload | 59 |
| render-request | schema hash | derived DTO or actual operation input/output receipt | 3 |
| resolve-dispute-request | 2.0.0 | Derived DTO or actual operation/stage input/output receipt | 8 |
| restore-request | schema hash | derived DTO or actual operation input/output receipt | 2 |
| result-envelope | 2.0.0 | document.payload | 12 |
| result-revision | 2.0.0 | document.payload | 11 |
| retry-request | schema hash | derived DTO or actual operation input/output receipt | 2 |
| review-context | 2.0.0 | document.payload | 19 |
| review-decide-request | 2.0.0 | Derived DTO or actual operation/stage input/output receipt | 5 |
| review-decision | 2.0.0 | document.payload | 26 |
| score-result | 2.0.0 | document.payload | 483 |
| scoring-input | schema hash | derived DTO or actual operation input/output receipt | 29 |
| source-format-binding | 2.0.0 | document.payload | 20 |
| source-release-request | 2.0.0 | Derived DTO or actual operation/stage input/output receipt | 26 |
| source-release | 2.0.0 | document.payload | 32 |
| source-status | schema hash | document.payload | 10 |
| speech-render-request | 2.0.0 | Derived DTO or actual operation/stage input/output receipt | 62 |
| speech-render-result | schema hash | document.payload | 15 |
| split-manifest | 2.0.0 | document.payload | 17 |
| split-request | 2.0.0 | Derived DTO or actual operation/stage input/output receipt | 15 |
| stage-cache | 2.0.0 | document.payload | 15 |
| start-review-request | 2.0.0 | Derived DTO or actual operation/stage input/output receipt | 3 |
| taxonomy-context | schema hash | derived DTO or actual operation input/output receipt | 13 |
| teacher-gold-request | 2.0.0 | Derived DTO or actual operation/stage input/output receipt | 18 |
| teacher-gold | 2.0.0 | document.payload | 24 |
| teacher-key | 2.0.0 | Derived view; durable source record remains private | 113 |
| teacher-rationale | schema hash | Derived projection/configuration member; not an independent evidence document | 6 |
| teacher-start-view | schema hash | derived DTO or actual operation input/output receipt | 11 |
| transformation | 2.0.0 | document.payload | 12 |
| transition-request | schema hash | derived DTO or actual operation input/output receipt | 3 |
| unit-correspondence | 2.0.0 | document.payload | 11 |
| unit-map-request | 2.0.0 | Derived DTO or actual operation/stage input/output receipt | 10 |
| verification-report | 1.0.0 | document.payload | 26 |

| exercise-request | schema hash | derived DTO or actual operation input/output receipt | 8 |

| llm-context-snapshot | 2.0.0 | document.payload with linked private assets | 27 |

| llm-experiment | 2.0.0 | document.payload with linked private assets | 87 |

| llm-quality-case | 2.0.0 | document.payload with linked private assets | 30 |

| prompt-bundle | 2.0.0 | document.payload with linked private assets | 35 |

| llm-quality-dataset | 2.0.0 | document.payload with linked private assets | 14 |

| llm-quality-judge-input | 2.0.0 | document.payload with linked private assets | 17 |

| llm-quality-judge-output | 2.0.0 | document.payload with linked private assets | 9 |

| mutation-manifest | 2.0.0 | document.payload with linked private assets | 108 |

| ai-development-run | 2.0.0 | document.payload with linked private assets | 96 |

| ai-surface-inventory | 2.0.0 | document.payload with linked private assets | 28 |

| key-repair-proposal | 2.0.0 | LLM canonical payload stored with review/judgment and private raw receipt assets | 6 |
| preparation-settings | 2.0.0 | immutable private settings asset linked from preparation document | 16 |
| preparation-state | 2.0.0 | document.payload with entity_head revision and linked private assets | 31 |
| provider-access-policy | 2.0.0 | configuration or transient operation DTO; never model/callback secret evidence | 4 |

| provider-callback-query | 2.0.0 | configuration or transient operation DTO; never model/callback secret evidence | 6 |

| provider-connect-request | 2.0.0 | configuration or transient operation DTO; never model/callback secret evidence | 3 |

| provider-connect-result | 2.0.0 | configuration or transient operation DTO; never model/callback secret evidence | 2 |

| provider-connection | 2.0.0 | safe persistent document metadata; secret files and transient authorization fields excluded | 14 |

| speech-profile | schema hash | derived DTO or actual operation input/output receipt | 27 |

| acoustic-edit | schema hash | derived DTO or actual operation input/output receipt | 20 |

| acoustic-production-plan | schema hash | derived DTO or actual operation input/output receipt | 30 |

| audio-judge-input | schema hash | derived DTO or actual operation input/output receipt | 17 |

| audio-judge-output | schema hash | derived DTO or actual operation input/output receipt | 12 |

| audio-judge-profile | schema hash | derived DTO or actual operation input/output receipt | 12 |

| render-progress | schema hash | derived DTO or actual operation input/output receipt | 37 |

| source-mapping-program | schema hash | derived DTO or actual operation input/output receipt | 47 |

| audio-sample-map | schema hash | derived DTO or actual operation input/output receipt | 17 |

| interpretation-checkpoint | 2.0.0 | private immutable document and linked stage assets | 17 |

| interpretation-view | 2.0.0 | closed HTTP projection; no separate durable copy | 26 |

| preparation-list | schema hash | derived DTO or actual operation input/output receipt | 2 |

| preparation-render-error | schema hash | derived DTO or actual operation input/output receipt | 2 |

| preparation-render-request | schema hash | derived DTO or actual operation input/output receipt | 2 |

| preparation-summary | schema hash | derived DTO or actual operation input/output receipt | 12 |

| feedback-score | schema hash | derived DTO or actual operation input/output receipt | 40 |

| review-request | schema hash | derived DTO or actual operation input/output receipt | 16 |

| review-list | schema hash | derived DTO or actual operation input/output receipt | 0 |

| review-selection-result | schema hash | derived DTO or actual operation input/output receipt | 3 |

| review-view | schema hash | derived DTO or actual operation input/output receipt | 20 |

| llm-quality-answer-input | schema hash | derived DTO or actual operation input/output receipt | 0 |

| llm-quality-expectations | schema hash | derived DTO or actual operation input/output receipt | 0 |

| llm-quality-judge-policy | schema hash | derived DTO or actual operation input/output receipt | 0 |

| delete-apply-request | schema hash | derived DTO or actual operation input/output receipt | 1 |
