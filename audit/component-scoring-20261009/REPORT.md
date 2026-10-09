# Independent correction and optional explanation specification update

Starting revision: 98cefcc. Authority: the user's instruction to score correction and optional supplied explanation independently, apply that flow to suitable gaps, update the specification and list remaining gaps. Only written specification, OpenSpec planning and audit artifacts changed. No application implementation, inference, speech generation, Lab execution, installation, secret/config modification, download, email or publication occurred.

## Current product behavior

Correction correctness/credit and explanation correctness/credit are separate. Every supplied explanation is assessed in the existing mapper call even when the form did not invite one. Omission displays not provided and N/A with no primary penalty. A valid repair keeps its credit when its reason is wrong. The explanation records supported, unsupported and unknown assertions and receives contextual feedback. A verified false assertion gives zero only to its actual component under the retained forbidden-condition rule; a known forbidden condition already fixes zero even if another assertion is unknown. Unknown credit otherwise remains unavailable only for its affected component.

New ordinary attempts freeze answer-components-v2. The primary grade uses selected detection/classification/correction and original45/15/30 weights/formula inputs. Optional explanation uses100*EQ/EA over supplied eligible explanations; EA=0 is N/A. Explanation coverage/recall remain labelled descriptive populations. Unknown supplied reasons stay in their actual population and do not block a supported primary grade. Controls/off-key or otherwise ineligible reasons still receive assertion findings and feedback; formal rubric score is N/A with the actual reason rather than fabricated numerical credit. Historic four-component policies stay frozen for historical results/explicit legacy references, without automatic regrading.

The same separation now governs extraction/consolidation, optional mapper audit, feedback, issue blocking, explicit LLM reconsideration, saved result revisions and Lab reference packets. Typed additional_assertions carry actual answer spans/text, contextual judgment and reason rather than invented proposition IDs. The saved mapper asset supplies native arithmetic and feedback; stored feedback retains correction/explanation kinds and readback needs no provider call. All ten copied task-component flags now describe optional invitation rather than required work. No new mandatory LLM stage or human review was added.

## Applied earlier findings

| Finding | Written resolution |
|---|---|
| EXP-001 | Typed additional assertions now project into their actual correction/explanation forbidden condition; correction, explanation and primary detection retain separate credit/state. |
| EXP-005 | Mutation documentation now points to the same recipe-bearing generation input and typed manifest/hash/replay contract. |
| EXP-006 | Both operation registries and all three OpenAPI effect copies save actual source notices/status/provenance without permission epochs or grant closure. Independent authored content remains available. |
| EXP-007 | Explicit manual generation/render retries have no candidate-lifetime three-attempt cap. Existing automatic request/repair limits, foreground deadlines and attempt receipts remain. |
| EXP-008 | Linguistic-audit prompt permits the shared one same-profile output repair within the original stage cap and retains failed output. |
| EXP-009 | Local Kokoro is the LLM-key-only first-use default. Missing weights have an explicit setup/progress/retry action; external speech remains an explicit configured choice. No silent provider switch/startup download. |

[REMAINING-GAPS.md](REMAINING-GAPS.md) explains every remaining group, its concrete affected scenario, repair, owners and necessity. EXP-002 typed key/rubric repair, EXP-003 durable preparation resume, EXP-004 listener disclosure of decisive contextual facts and EXP-010 older generic property fixtures remain open. These are engineering specification repairs, not pending user product decisions. Missing implementation is excluded from this specification gap list.

## Scope preserved

The protected taxonomy, 122 mutation recipes, 27 core plus15 auxiliary formula definitions, 11 original full-source identities/scopes, provider catalogue, AI-development requirements and quality-metric definitions remain byte-identical to the starting revision. Existing optional imports, diagnostics, benchmarks, speech services and Lab remain available. The original metrics registry's global unresolved/composite metadata is retained as historical policy; the current explicit answer-component policy governs new attempts. Actual external data availability and earlier acquired bytes/statuses are unchanged and governed by product-data-relevance.

## Validation and limits

The affected initial audit passed395 static artifact/declared-shape/constructed-arithmetic checks. Six targeted final checks validated clarified known-zero precedence and affected prompt/vector inputs. A further23 targeted checks validated copied schema descriptions, stored feedback kind projection, source effects and their changed indexes/bindings/vector. Valid unrelated greens were retained; historical receipts were not rewritten. These are specification integrity and independently constructed arithmetic observations, not a JSON Schema engine qualification or actual model/application behavior.

Native OpenSpec strict validation passed. The pinned property-graph/discovery validation passed and its unchanged manifest identity was verified after final copy alignment. The graph now has386 requirements,401 properties and1,604 case edges. Existing case identities, states and source evidence hashes were preserved. This increment adds nine requirements,18 concrete scenario fixtures and36 blocked/unexecuted positive/negative behavior edges; it does not mark them as passing. Thirteen stipulated arithmetic packets distinguish omission, true/false/unknown reasons, wrong/partial repairs, pooling, selected classification, missed errors and known forbidden zero with retained uncertainty.

The final active inventory has216 files,134 schemas and3,015 indexed field occurrences; local schema references, prompt/schema bindings and the full active version vector resolve. No passing application, provider, audio, model semantic quality or Lab observation is claimed. The unrelated edit in audit/spec-fullness-20261008/GAPS.md remains outside this increment.
