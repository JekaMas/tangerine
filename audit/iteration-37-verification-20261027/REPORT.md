# Iteration 37 verification and repair

Entry: `895cb51afdc1ec9c22c57c086eb0fcebce8d930f`. Scope: I37, all seven properties.
The expanded selection has16implemented positive/negative cases. Final acceptance
is recorded in ACCEPTANCE.json; this report cannot substitute for its clean receipt.

## Findings and sibling repairs

| Finding | Demonstrated trigger/result | Repair and proof |
|---|---|---|
| F1, P2: transient recording failure was immediately final | Actual Chrome on entry image; one controlled503 at original ELRD byte route. One read, paused at0, error4, no retry/diagnostic. | Single sourcePlayback owner logs safe codes and retries the same asset. Actual503→206, bounded three failures, explicit recovery, finite replay and player disposal pass. |
| F2, P3: proxy omitted original byte length | Actual44-byte WAVE range retained206/Content-Range/RIFF but lost Content-Length; full-length proxy case also failed. | Forward supplied length unchanged, leaving absent lengths absent. Three focused proxy tests and real range/Chrome readback pass. |

F2 is a transport-metadata omission. The separate red duration probe obtained the
complete recording and observed the correct597.25seconds. An early0:00 screenshot
does not establish a persistent wrong-duration defect; none is claimed.

All source recordings share the repaired owner: EdAcc, ELRD and both DRAL releases,
zero-clock fragments and nonzero recording windows. Siblings cover native controls,
manual seeks cancelling finite ranges, stale promises, permission rejection,
bounded failure, explicit retry, pending recovery and disposal. Selecting another
source stops old audio. DiPlomat has no fabricated recording/player.

Example/file/history JSON readers already use logged bounded read retry and
authored guidance; their unchanged receipts remain valid. Source writes retain
their idempotent action owner. No recurring hash check, re-import, synthesis,
source qualification or learner gate was introduced.

One visual oracle was corrected: existing alerts use16px/24px, while body text is
17px/24.65px. Requiring17px for the unchanged alert was an oracle mistake. Its
failure remains in keyboard-visual-oracle-red/. Actual keyboard/reflow/readability
passes without a stylesheet change.

## Native conformance and retained evidence

Format, projection, storage, summary, HTTP and consumer owners were traced against
native dictionaries and actual observations. Those native owners are unchanged;
all51Go race observations and the five complete imports remain valid. No corpus
download, identity audit or full import was repeated to change workflow stages.

| Selected release | Retained members, including containers/notices | Primary examples |
|---|---:|---:|
| EdAcc replacement DOI7914 |96|19,137|
| ELRD owner7e4c8f3 |36|589|
| DiPlomat owner8fc673f |19|35,255|
| DRAL16kHzbase |10,498|10,490|
| DRAL8.0fixes/test increment |3,086|13,596|

These count native views/member positions, not independent populations.

- EdAcc joins exact utterance keys inside their partition/root. Raw reference
  fillers, background locators, company ASR and scoring views retain distinct
  meanings. Accent varieties do not become errors.
- ELRD retains every turn/speaker/clock, ASR origin, meeting media and separate
  audio/transcript terms. No human-gold or voice-use right is invented.
- DiPlomat retains arrays/answers/ordered choices and option-index meanings,
  native train/validation/test and both NLI training views. Conservative exact
  contexts/supported paired views do not invent global dialogues or populations.
  All35,255native fields remain preserved.
- DRAL retains participants/languages/roles, fragment versus recording clocks,
  translations, base media and version-specific metadata. Thirty missing separate
  clips use actual parent-recording windows; no clip is manufactured. Repeated
  native views retain cross-version groups.
- Source corpus projections and empirical consumers were inspected. Metadata
  without error annotations does not become project error gold. Reports select a
  single declared member/view/population, not an automatic sum across versions.
- Stage/project/checkpoint/commit/resume preserve accepted rows and admitted
  identities. Readback trusts stored projections.

The original14-case apply clean receipt at798cc834 and all initial failures are
retained. It is superseded for changed media behavior by this expanded verify,
never relabelled as covering the new cases.

## UI/UX — pass in selected scope

Real installed Chrome exercised selection, interval/native playback, transient
failure, exhausted reads, explicit and keyboard retry, nonzero DRAL playback and
source replacement. Final media uses real Next/Go/PostgreSQL/private MinIO and
original admitted bytes. Only labelled media failures and saved-window selection
are controlled. Other examples, text, files, Refresh and navigation remain usable.
No raw backend text or model/write request appears.

Unchanged five-scope browsing, named-view, retained-file, empty/loading and reopen
observations retain their original receipts. Invalidated media/proxy cases were
reexecuted on the final image; native imports were not replayed.

## Typography — pass in selected scope

Used the typography skill and pinned project UI/UX procedure. Inspected actual
1280×720,390×844,320×740 screenshots, loaded Source Sans3,17px body,16px/24px
alerts,44.8px retry controls, keyboard focus, source terms, wrapping and absence of
horizontal overflow. Keyboard Enter recovers. No installed font/visual judge or
unperformed independent review is claimed.

## Evidence — pass within explicit limits

New observations: data/iteration-37-verification-20261027/. EVIDENCE.json binds
the tested player/proxy/browser sources and actual observations. The16-case cohort
reconciles51retained native Go cases, three retained source-session cases, eight
new playback cases and three new proxy cases.

Inspected recovery/source screenshots and five frames of the continuous28.32second
final browser video. It is silent; controlled failures and saved-window selection
are labelled. Viewport resizing is letterboxed. Original DRAL audio is separately
retained unchanged CC0 corpus bytes, not dubbed into the video. No acoustic
mutation, linguistic, LLM or source-wide error-frequency qualification follows.

Exact tracing completed. An actual jbcontext query reports no index for
github.com/jekamas/tangerine; no semantic/JetBrains proof is claimed. This is
self-review using independent contracts and literal expectations.

Native strict OpenSpec1.13.1, Go build/vet and source-session results retain their
apply receipts: their consumed inputs did not change. Current graph/discovery,
final web build, formatting and expanded selection are reconciled at the stable
boundary. Six protected catalogues and canonical GAPS.md remain unchanged.

No deployment/postdeployment, PBT, financial execution, model/provider/synthesis
call, acquisition/install, paid usage or publication occurred. User app3000,
data/settings/media/tabs are untouched; private source data persist.

No unresolved in-scope production finding or product decision remains. Acceptance
still requires the full16-case --require-clean receipt on the committed repair.
