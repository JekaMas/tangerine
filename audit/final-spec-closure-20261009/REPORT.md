# Final specification closure — 2026-10-09

The four remaining pre-implementation findings have written resolutions. No additional user decision is needed for them. The LLM already has the original text, injected mistakes and submitted answer; the first repair specifies how its judgment becomes a saved usable key/result, without adding another ordinary review stage.

## Key repair

The existing review/adjudication input now carries the saved mutation manifest alongside the complete ground truth and frozen answer. Its existing output has a nullable typed key_repair field. A substantive repair returns all proposed units, correction options, explanation propositions/rationale and total old/new correspondence, with the exact base key/audio identity. The server maps proposal-local references once, retains actual metadata/evidence origin, commits a revised key and computes exact native statistics. A complete decision payload can be reused; otherwise only the existing repaired-key mapper branch runs. Old answers/results/recordings and injection history remain intact. Explanation-only repair changes the optional component without cancelling valid correction credit.

The complete constructed two-error example is KEY-REPAIR-PACKET.json; it includes every planned-unit/correction field, valid surface codepoint spans, same/added correspondence and G=GC=TP=2,CQ=2,primary100. Incomplete proposals and changed-audio proposals retain the old result and actual diagnostics. The proposal contains no fabricated storage envelopes, measurements, empirical populations or grades.

## Persistence and generation

Three schemas define key-repair-proposal, preparation-settings and preparation-state. The preparation snapshot is saved before provider dispatch and contains the original request, expanded blueprint, selected immutable source IDs, full configuration/bundle/resolved generation bindings and saved speech/recipe definitions. Credentials remain references. Completed phases atomically link their verified private assets and actual receipts; settings/current profile changes do not change a checkpoint. Existing generate/render actions select preparation_id for explicit continuation. One read-only local preparation-list operation exposes failed/incomplete checkpoints. Existing preparation/status views carry the saved association. No new queue, scheduler, accounts, authentication or service is introduced.

Response-loss readback reuses committed output or finishes linking verified bytes without resynthesis. Resume of a complete exercise returns existing audio with zero inference. Late expired/superseded replies remain diagnostic and cannot overwrite selected checkpoints. A fresh exercise or explicitly changed render version is distinct from Resume. The remaining three-attempt render-request cap was removed; per-operation deadlines and bounded automatic requests remain.

Ordinary generated dialogues must make every decisive contextual fact audible or use already disclosed general task settings. Hidden preferences, private story facts and external required documents cannot determine an error. Context-sensitive categories remain supported through self-contained instances; unsuitable fixed scripts use the existing explicit new-text failure path. No extra briefing/review workflow is added.

## Concrete test design and preserved scope

The active fixture catalogue binds all390requirements/405properties/1,620case entries. It contains325reusable constructed packets and22specific named-scenario refinements, with literal positive/negative inputs, expected states/artifacts/counts/fractions and independent oracle instructions. Every case retains its exact source scenario contract. Generic definition/rejection/evidence scenarios now select explicit valid/invalid/no-observation packets rather than vague setup text.

All122category recipe/clean-control packets,42original arithmetic packets,22Lab diagnostic packets and11original full-source component packets are present. The original taxonomy, mutation recipe registry, equations, provider/source scopes and AI-development policy are byte-identical to starting commit9f5124a. Source records and recipe illustrations are constructed references, not acquired native data or verified sound. Expected values are fixed independently of candidate output; actual semantic/audio validity still requires observations when those tests are materialized.

Four older login/account case proof scopes conflict with the current local product. Their original source/test/command/hash receipts are retained in invalidated-historical-cases.json. The current revised cases are blocked. All other original case identities and bounded receipt scopes are preserved. The graph contains64implemented historical cases,16planned and1,540blocked; new fixture observations are allnot_run. This task runs no application/provider/voice behavior.

## Validation

The changed specification vector, prompt/schema bindings, field metadata, operation inventories, fixture identity coverage and independently constructed arithmetic were validated. The active vector covers223files,137schemas and3,063indexed field occurrences. The registry contains68internal operations; no complex public API or auth was added.

The final static check produced784passed artifact/constructed-arithmetic checks. Strict OpenSpec validation and property-graph/discovery validation passed. git diff --check passed. JSON Schema references and declared field shapes were inspected; no JSON Schema engine conformance or runtime acceptance is claimed. Previously valid behavior checks were not rerun. The changed graph and contracts invalidate their corresponding static validations; unrelated historical greens retain their original proof boundaries.

No application implementation, LLM inference, synthesis, Docker operation, source acquisition, message/email, install, secret/config change or publication occurred. The unrelated audit/spec-fullness-20261008/GAPS.md edit was preserved. REMAINING-GAPS.md distinguishes the closed specifications from future engineering observations and optional empirical/source data.
