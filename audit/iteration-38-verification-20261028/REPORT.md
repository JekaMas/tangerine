# Iteration 38 verification — source empirical reports

Fresh self-review of `4c46ba9` against all eight I38 properties. Four findings
were demonstrated and repaired. Direct native, JS, real-browser and build checks
pass. All **16/16** selected cases passed with **--require-clean** on
**f377c23e335d195dc9b2f62f9b367b9eb97812d0**. [ACCEPTANCE.json](ACCEPTANCE.json) records the
complete receipt and scope. No in-scope finding remains.

This operation covers descriptive source reports, their saved observations and
their usable UI. It does not qualify every linguistic category, perform a new
corpus acquisition/annotation, or claim whole-product/provider acceptance.

## Findings and generalized repairs

| Finding | Demonstration | Repair and sibling coverage |
|---|---|---|
| V1: Invalid definitions were reported as temporary service failures. | Actual private Go API returned503 for missing population, duplicate windows, unknown category, negative opportunities and duplicate attempts. `red.jsonl` retains all five failures. | The report application owner wraps its existing calculation/difficulty/legacy-selector validation as ErrInput. HTTP400 permits correction; no new validation is introduced. All five inputs and a bad legacy selector now return400; the corrected selector succeeds. Real database failure still returns503 and preserves/reopens the earlier report after recovery. |
| V2: An ambiguous save told users only to Refresh. | The original request owner gave the same generic read guidance for an unconfirmed POST. | The request owner tells users that saving could not be confirmed and to check saved reports before explicitly trying again. No automatic POST replay. Source, saved-input and advanced operations retain fields and the previous result. |
| V3: Zero denominators could misdescribe the missing data. | A zero eligible-event/opportunity denominator said that fully annotated examples were absent, which does not follow. Literal JS counterexample retained in `presentation-red.log`. | The metric presenter says no eligible observations were counted for that measurement. Known zero, missing values and rare positive percentages remain distinct. “Word count” replaces “word-count exposure” in the ordinary summary. Arithmetic and saved report bytes are unchanged. |
| V4: Advanced-form failures appeared beside an unrelated source form. | Fresh screenshot `browser-before-form-feedback/11-correctable-input.png` shows the advanced request’s feedback beside the source selector. | The page routes report feedback to the submitting source, saved-input or advanced form. ReportError alone reveals the relevant disclosure and focuses the authored message. Browser assertions cover all three siblings, retained fields/results and correct form/focus; no extra backend gate is added. |

Layers remain separate: empirical calculations/mapping are unchanged; the Go
application owner classifies errors, the request presenter supplies authored
guidance, the page owns form placement, and the shared component owns reveal/focus.
No source admission, repeated byte validation, new service, queue or model call
was added. There is no unresolved in-scope product decision.

## Full property review and evidence reuse

| Property | Reviewed actual owner / observation | Disposition |
|---|---|---|
| P1: source populations | Published+completed imports; version/view separation, constructed origin, latest identical-import selection; retained native catalogue and all52 actual choices. | Pass; source selection and imports unchanged. |
| P2: writing denominators | Per-member M2 sentences/tokens, selected annotator, noops, invalid/unresolved exclusions and withheld originals; independent original-M2 census. | Pass; exact source numerator/denominator calculations unchanged. Correctable-input HTTP behavior extended by V1. |
| P3: mappings | Nine written/five phone rules, article context, ambiguous/stress-only/approximate negatives, frozen rule version and all122 rows. | Pass; derived positives do not imply complete absence annotations. |
| P4: speech | Original native-label census vs manual phone windows; read/Suitcase separation, no automatic/word/comment/silence inflation, unknown word exposure. | Pass; labels are source annotations, not an independent auditory verdict. |
| P5: coverage | Original/reference/rating/segment/turn/task/fragment units across JFLEG, SpeechOcean and the four supplement families. | Pass; alternative corrections, accents, ASR and related releases are not invented errors or independent learners. Fresh JFLEG UI observes747 originals,2988 alternatives and unmeasured mistakes. |
| P6: relationships | Exact native and mapped populations, distinct-event pairs, both directions, complete-window denominator, support/conditional/lift; independent M2/L2 censuses and literal four-window oracle. | Pass; no pooling, absence or causal estimate is invented. Original engine/52-report observations retained. |
| P7: persistence/recovery | Immutable input/output/read/reuse, source-change counterexample, missing-input preservation, real storage outage and recovery, typed validation and three form paths. | Pass in direct observations; full selected receipt reconciles retained and new cases. |
| P8: ordinary usability | Actual Next→Go→PostgreSQL/MinIO→Chrome creation, frozen reuse, download/reload, source failure/empty/retry and all report-form feedback. | Pass in direct observations at1280/390/320; no page errors, raw backend payloads or unrequested execution. |

All52 reports from nine available source families remain available in the
[original report index](../iteration-38-empirical-20261027/REPORTS.md). No source
reimport or repeated source census was needed: these repairs do not change source
rows, arithmetic, mappings, populations or saved output. Source-specific native
rates remain separate from the smaller derived-category event proportions.
Opportunity rates/unsupported absence remain unmeasured. Manually selected L2
utterances are not a random population of all learners.

## Tests and structural checks

Fresh native race evidence is in
`data/iteration-38-verification-20261028/{green,selector}.jsonl`. Three top-level
HTTP tests cover six invalid-input contrasts, valid correction, actual storage
failure, continued readback and recovery with zero provider receipts. Original
engine/source/frozen-input native cases are retained individually, not inferred
from a package status or the apply report.

Six JS measurement/list/request cases passed; the final wording adjustment
reobserved its two affected guidance cases. The36 session/starter/list sibling
tests passed. The unchanged list suite was included in that shared invocation;
it is not claimed as new source/model evidence and was not repeated. An unsupported
Node flag failed before testing; that command error and the corrected genuine
red assertions are retained separately. No native failure is relabelled green.

Go1.26.5 vet/build and the final locked Next production build pass. No dependencies
were installed; cached build layers and existing runtimes were used. Pinned
OpenSpec1.13.1 strict validation, graph and discovery checks pass. These are
structural/build results, separate from the observed behavior. The exact final
I38 query selects eight properties, sixteen cases and one evidence command,
without substitution gaps. Broader planned/blocked requirements stay visible;
this iteration does not claim a full-project `--all` result.

## UI/UX, typography and evidence review

**UI/UX: pass.** Ordinary named source creation, native/mapped result separation,
all122 coverage rows, download identity, saved reload, frozen reuse and explicit
save recovery are observed. Transient source reads return503→200 automatically;
three503 responses produce authored guidance with saved work usable; keyboard
Retry recovers. Empty source choices do not remove saved reports or practice.
Two labelled save failures and one real invalid-definition response preserve
fields/results. All three forms own their feedback; advanced JSON is explicitly
entered input, not backend output. No experiment Run or provider operation occurs.

**Typography: pass.** Used the typography skill and the pinned/project UI review
procedure. Inspected actual desktop and320/390 images plus computed styles:
Source Sans3,17px body,24.65px body line height,14px measurement captions.
Headings/actions and count cards remain readable. Tables scroll in their own
containers; there is no page overflow at the three widths. Feedback is visible
and focused, with fields available for correction. Native file-picker text uses
the installed browser’s language; application-authored text remains English.

**Evidence: pass.** Reviewed final L2/JFLEG screenshots, native/request receipts,
saved download identity and frames from the actual continuous23.64-second Chrome
capture. The MP4 is a normal-speed transcode of its retained original WebM, with
no cuts or compressed waits. It is a silent report-workflow demo, not a new
text/audio-generation demonstration. Controlled503/empty states are explicitly
labelled in the gateway logs; underlying source computation/storage are real.
No recording, prompt or symbol is called independent linguistic/acoustic gold.

Key local evidence:

- [Report demo](../../data/iteration-38-verification-20261028/browser/source-reports-demo.mp4)
- [Report result, narrow](../../data/iteration-38-verification-20261028/browser/05-results-320.png)
- [Saved-input feedback](../../data/iteration-38-verification-20261028/browser/06c-saved-input-error.png)
- [Advanced-definition correction](../../data/iteration-38-verification-20261028/browser/11-correctable-input.png)
- [Coverage-only result](../../data/iteration-38-verification-20261028/coverage-visual/coverage-390.png)

## Preservation and limits

Original122 taxonomy/recipes,42 grading formulas, provider registry and11 full
source scopes are unchanged. Canonical unrelated GAPS.md is preserved. User
app3000, other services/data/settings/media/tabs and VPN were not changed. Only
recorded private test stacks and test-owned records were used. Restarted test
stores are stopped after the observations; their data and failure receipts remain.

No application LLM/speech/provider call, paid credit/overage, installation,
acquisition, deployment/postdeployment, PBT, financial execution, publication or
separate-agent review occurred. No semantic/IDE index evidence is claimed;
known exact owners were inspected. Optional missing source/empirical/provider
observations elsewhere are not represented as passing by this I38 verification.
