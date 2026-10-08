# Teacher Error Trainer specification revision

## Why

The product trains teachers to find errors in prepared English audio. Its first interface is simple, but its linguistic domain remains broad.
The specification must distinguish requested behavior, actual evidence, and measured results. It must prevent unapproved substitutes and guessed properties.

## What Changes

This revision translates prose under the SimpleEnglish Strict rules. It preserves identifiers, formulas, command syntax, and original language examples.
It adds the owner approval controls that the current request explicitly requires. It removes active mock and human-recording substitute profiles.

The runtime remains local and containerized. The teacher still submits a free-form answer and waits for synchronous evaluation.
All 122 taxonomy IDs and all existing metric formulas remain present. No live classroom feature enters this scope.

## Capabilities

The package retains fourteen existing capabilities. It adds `change-approval` for the requested governance controls.
Each requirement has a permitted-use scenario and a boundary scenario. A scenario describes expected behavior, not a completed test.

| Capability | Purpose |
| --- | --- |
| `exercise-blueprints` | Define context, speakers, and targets. |
| `error-taxonomy` | Define the language categories and exclusions. |
| `case-generation` | Make candidates without invented evidence. |
| `speech-rendering` | Make audio through named service profiles. |
| `case-verification` | Require applicable checks and human reviews. |
| `content-lifecycle` | Preserve published versions and disputes. |
| `assessment-sessions` | Save answers and deliver the teacher loop. |
| `llm-evaluation` | Extract and map claims within explicit boundaries. |
| `teacher-metrics` | Calculate named metrics from resolved decisions. |
| `data-provenance` | Control source origin, rights, and transformations. |
| `validation-corpus` | Require real coverage and separate data splits. |
| `provider-contracts` | Name providers and restrict their authority. |
| `local-deployment` | Define local containers and private data access. |
| `platform-foundation` | Enforce authorization, costs, and truthful release records. |
| `change-approval` | Require exact owner approval for each restricted change. |

## Impact

This revision replaces the v5 specification package. It does not migrate a running application.
The source formulas and reference algorithm remain traceable through the preservation report. Historical artificial tests do not authorize new test doubles.

Application release remains blocked by the recorded evidence gaps. The official STE dictionary check is also incomplete.
The review report states actual checks separately from these outstanding obligations. It does not claim absolute semantic or linguistic proof.
