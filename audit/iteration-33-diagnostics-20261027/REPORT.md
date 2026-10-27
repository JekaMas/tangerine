# Iteration 33 — saved-audio diagnostics and ambiguous fixtures

Implementation and informational verification are complete. Committed-clean
acceptance is recorded separately in ACCEPTANCE.json after the selected gate.
Entry source: `0dadf31d0aac7fc7502a9d63de909cfbb04aafbe`. Scope: QUAL-04, not a
bulk judge campaign or universal acoustic qualification.

## Repairs, causes and related cases

| Finding | Single owner and repair | Independent observations and siblings |
| --- | --- | --- |
| Gemini ordinary diagnostics bypassed the owned context projection | `diagnostic_models.auditory_content` now serializes the same projection for Gemini and local audio judges. Key corrections/rationales, learner answers, prior scores and observed claims stay outside the listening task. | Actual native diagnostic entrypoint and HTTP request construction execute with a constructed external response. Literal expected targets/scopes/context, private canaries, actual serialized capture, target/reference order, blind labels and unmodified input are checked. Missing credentials, forbidden billing, proxy, redirect, provider failure, invalid output and omitted-target siblings pass. No live model call is inferred from these tests. |
| A nominal mutant always required an error, even with an ambiguous carrier | `category_validation.make_probe/compare_probe` accepts withheld explicit uncertain expectations. Uncertainty cannot become truth from favorable judge agreement and takes precedence over other failed rows. | Neutral/contrastive full forms, correct careful/connected delivery, declared accents, falling wh-questions and rising confirmation/repetition controls remain acceptable. False alarms and opposed judgments remain visible. The selected weak-form expectation is unresolved rather than a universal reduction rule. |
| A failed observation could confirm favorable attached findings | The same comparison owner keeps failed observations uncertain and preserves their supplied raw findings. | A concrete failed-provider packet with otherwise matching findings reproduced confirmation before repair and stays failed/uncertain afterward. Existing incomplete/invalid/503 and saved-failure/no-redispatch cases retain their independent expectations. |
| A measured change could falsely conflict with an explicitly valid contour | Physical/auditory conflict requires an authored defect-present expectation. A correct control is not a contradiction merely because the waveform changed. | A constructed valid rising-question control with actual supplied physical observations reproduced false uncertainty before repair. Correct-control confirmation and uncertain/error controls now keep their separate meanings. This is comparison logic, not new actual model hearing. |
| Future intonation context omitted a recorded word | `audit/iteration-26-acoustic-20261026/selection.json` now names “You have car insurance”, permits legitimate question/statement contours and states the actual public purpose. The existing preparation owner forwards explicit fixture expectations. | Original native recording text and all original model requests are inspected. The frozen old requests still omit “car”; their replies are not rewritten. Corrected inputs are explicitly not_run until a separately requested observation exists. |

The transport and comparison changes have literal retained red/green
counterexamples under `data/iteration-33-diagnostics-20261027/`. The first native
integration fixture omitted its required audio digest; that test-owned setup was
repaired without changing production admission. Its failed receipt is retained.
The first syntax command omitted Docker's stdin flag; the corrected command
passes. These tooling failures are not acoustic or application defects.

## What the original recordings actually support

Every set retains its original target and three controls, public questions,
exact WAV-to-request correspondence, bindings and actual model replies. The
zero-call reconciliation is
`data/iteration-33-diagnostics-20261027/reconciliation.json`; its owner is
`reconcile.py`. Original comparisons and frozen data are unchanged.

| Saved set | Supported observation | Remaining limit |
| --- | --- | --- |
| Linking | The retained four-control model check confirms this narrow joining contrast with no control false alarm. | George/British English and this public drill only. The model's reason is not an exact independent phone transcription; careful unlinked speech is permitted. |
| Voiced joining/assimilation | The retained model check confirms the selected voiced-joining drill and its careful control. | Heart/American English and this authored target only. Natural assimilation, accents and devoiced variants are not universally wrong. |
| Weak form | The model describes the full vowel in the candidate and accepts it; the contrastive full-form control is accepted. | This neutral carrier does not establish an error. Matching a narrow reduction drill is different from communicative correctness. The future candidate expectation remains uncertain. |
| Thought-group pause | The actual candidate contains **14400 additional zero samples at24kHz**, from sample9000 to23400: **600ms**. Prefix/suffix PCM matches outside the existing120-sample splice fades. | The saved decoder proposes the article/noun location. The model misses the pause. Physical silence is established; independent word alignment and perceived communicative disruption are not thereby established. No renderer defect is demonstrated. |
| Intonation function | Retained independent F0 windows fall **7.04→5.81→4.37 semitones** in the reference and rise **10.92→12.19→13.31** in the candidate. Original question and wh-question rise/fall controls remain inspectable. | The model describes a fall and falsely flags one valid confirmation-question control. Physical direction does not determine pragmatic correctness. Both replies/measurements stay visible; no contour is made universally obligatory. |

The last three rows remain unresolved perceptual/contextual observations. They
are not hidden passes, unresolved product choices, proof all transforms failed
or a reason to change a learner's key/score. This iteration repairs the proved
diagnostic/fixture defects and preserves these limits, as requested. No response
or context was fitted through repeated model attempts.

## Verification and exact evidence reuse

The stable actual native closure has **580 passing tests, zero failures/skips**:
512 category comparison cases, six original actual-evidence readers and62
diagnostic/context/fixture/recovery cases. Their original unittest transcripts
and source bindings are under `data/iteration-33-diagnostics-20261027/native/`.
The18 new diagnostic regressions also pass under the installed speech image's
**Python3.12** with network disabled; host-native observations use Python3.14.
No target runtime was installed. Stable syntax checks cover11 changed Python
files using that actual speech image.

The full I33 gate selects **I33.P1–I33.P4**, ten exact typed unittest assertions
(six positive/four negative). It observes the original native test identities,
unchanged semantic sources, real Lab bytes and preserved registries. It does
not redispatch580 green tests merely for a commit. `NATIVE-COVERAGE.json` maps
every native identity to existing case aliases and the exact I33 acceptance
reader. The existing CV command routes remain unchanged. Old active aliases
whose test source changed now point to the actual observed source; the I16
constructed fixture library records the valid planned_units carrier. Original
receipts retain their original fingerprints and are not relabelled.

The first informational full I33 gate passed10/10 on the dirty entry revision;
that is evidence only, not committed-clean acceptance. Structural OpenSpec1.13.1,
graph/discovery and390 current specification assertions pass. The stable language
scope is Python; unchanged Go/web build/behavior receipts remain valid within
their original boundaries. No Go, JavaScript, schema, prompt or scoring formula
changed. The specification compatibility metadata is updated once for the
changed/new canonical documents.

## AI/Lab evidence

Existing local MLflow experiment22, final run
`653686660f7547f59383cfc6056f2d3d`, retains57 artifacts. Nine actual artifacts
were downloaded and compared byte-for-byte, including original weak-form response,
intonation frozen input, actual pause/question WAVs, native test output, the
current model-input owner and managed prompt. The downloaded copies are retained
locally for executable inspection. See `MLFLOW.json` and
`data/iteration-33-diagnostics-20261027/lab-readback/`.

An earlier export/run `bc83400ced45452ca0f135b8e2b7b11b` is superseded only by
the later actual sibling repair/source. It remains historical. Both exports
perform **zero inference/synthesis**. Existing original I26 four calls and the
older linking call are referenced as original observations, never new calls or
current changed-context success. The new ordinary Gemini projection is verified
at a constructed transport boundary, not claimed as improved model accuracy.

## Review and preservation

Code self-review traced the actual native entrypoint, both auditory branches,
projection, tolerant decoder, measurement association, probe creation/comparison,
saved-response finalizer and original evidence. Production responsibilities stay
separate: projection/transport, pure fixture comparison and saved research each
retain one owner. No new stored-data check, model retry, service, public API,
learner gate or scoring/key mutation is introduced. Failed diagnostics and
uncertainty stay advisory; ordinary preparation/listening/grading remains usable.

**UI/UX: not applicable to changed product presentation.** No product route,
control, player, error rendering or style changed. The historical gallery uses
its frozen originals. Earlier I29/I32 actual route, keyboard, playback, recovery,
screenshot and video observations retain their original scope. This report makes
no new browser-activation or visual-flow claim.

**Typography: not applicable to changed product styles.** No formatted UI or
font/layout owner changed; no typography skill or new screenshot is claimed.
The changed public fixture wording is inspectable data for a future separately
requested observation, not a newly observed user screen.

**Evidence review: pass within the stated scope.** Actual saved contexts/replies,
twenty role-bound recordings, PCM insertion, retained F0 windows, native outputs
and real Lab downloads are inspected. No model opinion, requested IPA, punctuation,
file count or structural pass substitutes for hearing/physical function.
Semantic search is unavailable: the exact-worktree CLI reports no index for
`github.com/jekamas/tangerine`. Exact named-owner tracing supplies source evidence;
no semantic/IDE proof or independent reviewer is claimed.

`PRESERVATION.json` records unchanged original122 categories/recipes,42 formulas
and11 source scopes. User app3000, settings/data/media/tabs, other services and
the canonical unrelated GAPS.md edit are untouched. No paid credits, overage,
provider calls, new synthesis, installation, acquisition, deployment, publication,
PBT or financial execution occurred. No service restart is needed for this
development acceptance, and none was performed.
