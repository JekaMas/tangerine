# Iteration 18 verification and repair

Scope: UX-01, UX-06 and UX-07; FIN-UI-01.P1, FIN-UI-06.P1,
FIN-UI-07.P1 and FIN-VERIFY.I18, plus 13 directly dependent existing request
and recurrence cases. Start: clean `886dee5` on `tangerine/iteration-16-release`.

The review confirmed four defect groups beyond the original 20-case acceptance.
They are repaired. The complete expanded selection contains **53 executable
cases**, with no selected placeholder. The committed-clean acceptance checkpoint
is recorded below after execution; structural checks alone do not accept it.

## Findings, causes and siblings

| Finding | Concrete trigger and effect | Repair and owner | Sibling coverage |
|---|---|---|---|
| F18-01 · P2 | Advanced `recurring_errors:[null]` crashes the preparation page because its JSX mapping ran outside the presentation catch. The editor becomes unavailable. | RequestPreview projects all recurring/category/severity values into safe display text inside its existing catch before rendering. Malformed entries retain editable input and local guidance. | Null speakers, object-valued speaker/frequency/instruction and category/family/severity values; no arbitrary object becomes a React child. The existing summaryVoices precedence remains unchanged. |
| F18-02 · P2 | An empty simple Exact field blocks advanced `mutation_count:0`, both in projection and native constraint validation. | The request owner applies advanced inputs before deriving count/voices/recurring speakers. Controls makes explicitly overridden native fields non-validating while retaining their values, with clear edit guidance. Clearing advanced restores normal editing/validation. | Null/automatic count; blank overridden Topic/speaker/word fields; advanced1/3 speakers; ordered/nullable voice vectors; active recurring speakers; advanced density/category floor and cleared recurring overrides. AmountControl consumes the same effective request instead of describing a second count. |
| F18-03 · P2 | A502 HTML service response is displayed as invalid advanced user JSON. A later saved-list failure can replace the primary actionable error. | A small preparationResponse owner handles transport parsing and authored messages; parseUserJSON remains the user-input owner. usePreparation preserves the primary action error when a secondary refresh fails. | Empty503, malformed200, unknown/null failure bodies, model-setup/active-lease guidance, configuration parsing, saved-list refresh and explicit recovery. Shared clientRequest/requestError remain unchanged. |
| F18-04 · P2 | With optional controls expanded at 390 px, Generate ends at 504 px while feedback begins at 3015 px, outside an 844 px viewport. The user cannot see that the action failed or completed. | page.js places loading/success/error feedback beside Generate, before optional controls. Small prepare.css spacing preserves the existing body/error typography and ARIA roles. | Actual error, busy, success and Stop outcomes, desktop and mobile; feedback never adds a confirmation, focus trap, provider dispatch or another validity gate. |

Baseline observations and screenshots remain under
`data/iteration-18-verification-20261026/baseline.json` and `screens/`.
The earlier apply result is preserved as a valid observation of its registered
cases; it did not cover these counterexamples. No earlier failure is rewritten.

## Nonblocking recovery and ownership

The existing shared request owner logs redacted method/path/status, retries safe
transient reads up to three times, respects cancellation and long Retry-After,
and never silently replays writes. Actual controlled503 reads recovered on
attempt 2; persistent reads stopped at 3 each. Explicit Retry/Refresh restored
options and retained Topic. Basic generation remains available while optional
catalogue choices are unavailable. Backend text, exception strings and response
HTML never become user-facing guidance.

Unknown write outcomes retain explicit saved-state refresh/resume ownership.
Blindly replaying generation could create a duplicate or consume another model
call; that is not a recovery strategy. Known input contradictions retain editable
fields and actionable local guidance. There is no new validation/approval stage,
repeated stored-data check, schema archive or retry/provider fallback loop.
No selected UI state requires a human peer review or benchmark to continue.

The code layers remain separate: request.js owns effective request projection;
RequestPreview/Controls/AmountControl own presentation; usePreparation owns
foreground state and action lifetime; response.js owns preparation transport
messages; clientRequest/requestError retain shared retry/redaction. API/storage,
provider admission, scoring and speech owners are unchanged.

## UI, UX, typography and evidence inspection

Used the installed typography SKILL.md, the project's
UI_UX_TYPOGRAPHY_VERIFICATION.md and pinned verification-design review/inspection
procedures. This is self-review using independent literal expectations, not an
independent agent, external approval or human product gate.

Inspected the original and repaired production-built frontend through CUA. The
summary override was reobserved at 1280, 960, 390 and 320 px, including C1, zero,
advanced AU/British order and retained basicB1. The exact90word/B1/two/minor
Number+Collocation request submits the independently specified body once.
Malformed/cleared overrides, disclosure retention, ordinary zero, advanced native
validation, read failure/retry, loading, controlled success, cancellation and
feedback visibility were exercised. The new model-independent amount display
shows4 for Low / 400words after a cleared recurring override.

Important actual images inspected:

- `screens/error-beside-action-desktop.jpg`: error follows Generate before the
  expanded optional controls, in the viewport.
- `screens/error-beside-action-320.jpg`: wrapped16 px / 24 px human-readable error,
  retained voice/category/zero summary and accessible action.
- `screens/typography-320.jpg`: selected severity states and full descriptions
  wrap at 14 px without horizontal clipping.
- `screens/effective-density-help-390.jpg`: selected Low, readable quantitative
  captions and the actual4/400word effective amount help.

These paths are relative to `data/iteration-18-verification-20261026/`.
Computed current typography retains loaded Source Sans3,17 px body/24.65 px line
height and all nine 14 px amount/severity captions. The existing deliberate10px
negative, contrast/hierarchy, basic short-path geometry, focus/anchor and Tab
observations are retained because their relevant declarations, fixtures and
interaction inputs are unchanged. They are not relabelled as newly executed CUA
observations. `observations.json` lists each retained and reobserved group.

Actual source-built browser records, intercepted requests and final image/source
binding are in `repair-observations.json`, `requests.jsonl` and
`frontend-source.json`. Some unchanged core/feedback observations came from the
preceding repair image; the final image adds effective amount-help inspection.
Their unchanged semantic dependency is explicit. Final source is not inferred
from screenshot counts, a report label or a build alone.

All writes were intercepted by a test-owned gateway. Only GET/HEAD may reach the
existing local app. Constructed success responses prove frontend progress and
request ownership, never actual generated/saved exercises, provider accuracy,
scoring or audible pronunciation. There were zero new model/synthesis calls.
The helper assertions inspect actual facts and exact request relations; negative
review packets reject missing UX/typography and mismatched evidence.

## Checks and retained evidence

The exact53-case selection is `SELECTION.json`:20 original I18 cases, eight new
request/response cases,12 new browser regression cases and13 existing dependent
request/recurrence cases. The DAG and iteration routing now name them explicitly.
No unrelated model campaign, full product suite or already accepted corpus/audio
qualification was repeated. Existing unaffected shared recovery/other-route
receipts retain their original bounded claims; this is not a new all-route pass.

- Focused native projection/transport regressions:21passed initially; the later
  corrected recurrence-floor/density expectation passed its focused case.
- Focused actual-browser regression assertions:12passed.
- Pinned native OpenSpec1.13.1 strict validation:passed, zero issues.
- Graph/discovery validation:passed; this is structural coverage only.
- Locked production frontend Docker build:passed on the stable source.
- Preservation: original taxonomy/recipes,42 formulas,11 source scopes, schemas,
  API/speech/storage, prompts and provider configuration unchanged.
- Stable-batch whitespace/diff inspection passed. No Go/native/workflow source
  changed; their valid language/workflow receipts were retained.

Automation adaptations are distinguished from product findings: one strict
alert locator was ambiguous because saved rows also expose alerts; the observer
was scoped to the actual authored message. A read-only DOM shim does not expose
checkValidity, so submission/actual focus supplied that evidence. A transient
CDP fill timeout was inspected before retrying; an early overlapping persistent
read probe is retained but the final case awaits both terminal outcomes and
observes exactly 3 attempts each. A Docker --rm name-removal race used a fresh
fixture name. None is presented as a production defect or a successful model call.

No deployment, postdeployment, PBT, financial execution, installation, provider
call, purchased credit, overage or publication occurred. The running app,
settings, database, audio and unrelated canonical GAPS.md remain untouched.

Artifact drift was also repaired:16 implemented original cases still carried
obsolete planning-only blocker text. That text is removed; actual future planned
placeholders remain visible. The metadata correction invalidates structural
manifest acceptance only, not the unchanged behavioral observations.

The first committed-clean selection at `58916ca` passed52/53. Its remaining
case errored in the test journal lookup (`KeyError: scenario`) on an initial
unlabelled GET. The hypothesis was confirmed by replaying the same exact records
with optional label lookup and an added assertion rejecting unlabelled POSTs.
The focused case passed without changing expected bodies, counts or dispatch
checks. Original failed receipt: `data/iteration-18-verification-20261026/accepted-clean.json`.
This is a test-adapter repair; no application or browser observation changed.

## Acceptance checkpoint

Pending the full committed-clean53-case selection. Preserve valid receipts and
run that selection once at the stable revision; update this checkpoint with the
actual result. No product decision is required for these repairs.
