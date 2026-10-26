# Iteration 26 verification and repair

Starting source `3049db8b042364fc9df32ecca93d1a6cb051e288`, release worktree.
Scope: FIN-ACOUSTIC.P1, FIN-VERIFY.I26 and CV-01.P1 through CV-06.P1. The current
machine-readable result is the original I26 `STATUS.json`; this document
supersedes the apply report for verification. No iteration acceptance is issued
while actual browser input remains unobserved.

## Findings, causes and siblings

| Finding | Cause and repair owner | Direct and sibling evidence |
| --- | --- | --- |
| Startup read failure cannot recover through Refresh | `listening.py` previously retained the fallback empty list forever. Its new `selection_reader` retries an uncompleted read on a later request and reuses admitted metadata in memory. | The actual CLI/HTTP counterexample restored gallery.json but still returned zero players before the repair; the repaired request returns20. Admitted metadata survives a later file error without being revalidated. Font and unrelated routes do not trigger selection loading. |
| Unreadable saved judgment is labelled “not performed” | The display used the no-execution caption for an unavailable read. The same page owner now shows an unavailable-observation caption and authored recovery guidance. | The pre-repair literal case failed. All20 audio controls, independent judgments and Refresh survive a malformed comparison. Exception/backend canaries never appear. Missing/pending and failed-provider records remain usable and explicit. |
| The apply result has no full iteration clean gate | It ran20 new cases and reconciled518 retained observations, with one interaction skip. | Register four missing real CLI/HTTP recovery cases. The stable committed boundary selects all eight properties and all542 cases once; original model/audio evidence is reused and no model population is repeated. |
| Actual pointer/keyboard activation is still unavailable | A fresh page in the selected IAB behaves like the original tab: disclosure and Refresh clicks do not activate, Enter only focuses Refresh and audio Space only focuses audio. | Native HTTP counts remain unchanged after the click. Actual browser reload/navigation recovers files, so those observations are not labelled successful click/keyboard activation. The existing installed-Chrome selection question is unanswered. No DOM event synthesis, scripted play, browser switch or native-app bypass is used. |

The repair is confined to the selected sheet's loading/presentation owner.
`read_saved` remains the single local read/retry/logging owner; it is reused,
not duplicated. Actual saved-media HTTP failure returns authored guidance, while
another clip and the rest of the page remain usable. No stored schema, byte audit,
provider qualification, human review or additional learner boundary is introduced.

The sibling trace includes the private auditory transport, ordinary speech error
mapping, preparation response/failure presentation and Listen/audio/review callers.
The normal frontend uses authored `userError`/`requestError` guidance rather than
backend messages. Safe reads and explicit state recovery retain user input; an
uncertain generation/grading/diagnostic POST is not replayed to hide an error.
CV confirmation is referenced only by development/diagnostic owners, with no
playback or primary-scoring gate. Those unchanged product owners retain their
existing receipts; they are not relabelled newly verified by this Python repair.

## Tests and retained acoustic scope

`recovery-red.log` preserves both original counterexamples. The focused pair
passed after repair; the four new cases plus four affected existing listening
cases then passed. The font-route sibling and one-admission memory behavior also
passed through the actual native CLI/HTTP owner. Constructed failures affect only
test-owned files/HTTP responses; saved recordings are actual retained Kokoro clips.
No provider key is supplied to the CLI regression processes.

The original518 CV identities/native owners remain unchanged. The initial full
query reports506 not_loaded,31 registered passes and one skip because the old
parent receipt selected only12 edges while physically observing518 tests. The
existing REUSE.json supplies that exact identity/source reconciliation; not_loaded
does not manufacture a missing new execution or a model-quality pass. The new
complete iteration gate closes the native execution selection once, rather than
repeating unaffected suites during every fix. Its new input is the full selected
committed revision/expanded542-case gate, absent from apply. Pure mechanism/read
tests reuse the saved model results and dispatch zero inference/synthesis.

The four actual I26 Gemini Free observations are retained unchanged: selected
assimilation confirms; weak form is unconfirmed; pause and intonation retain
physical/listener conflicts, including the valid-question false alarm. Retained
linking confirms its narrow joining contrast without exact universal phone proof.
The original122-row matrix stays44 confirmed/78 unconfirmed. No universal acoustic
claim or retry-until-favorable judge campaign is added. The separately unimplemented
masked-overlap variant and unselected Azure/Qwen outputs keep their original scopes.

## UI/UX, typography and evidence

**UI/UX: recovery passes; actual activation remains incomplete.** Through the
actual source-built sheet and a test-owned dependency fixture, the browser shows
an initial unavailable page with enabled Refresh. After file restoration, browser
reload presents all20 controls. The transient clip's actual HTTP sequence is503→200;
the persistent clip stops after503→503 and shows a plain recovery message. Other
clips remain loaded, Refresh remains enabled and the backend canary is absent.
Restoring the dependency and reloading yields20 readyState4 clips, no media error
and no retry text. Request counts explicitly distinguish reload from the failed
Refresh click. The pointer/keyboard/disclosure/single-player proof stays open.

**Typography: pass for inspected states; activation-dependent views incomplete.**
The typography skill and pinned UI/UX review procedure were used. Actual1280×720,
390×844 and320×740 views load17px Source Sans3 at24.65px line height with no page
overflow. Recovery text wraps, primary actions stay legible and the focused
Refresh outline is visible. The focus was set by the documented locator operation;
it does not establish successful keyboard traversal/activation. Expanded notes
remain unobserved. Screenshots are inspected content, not an aesthetic count gate.

**Evidence: actual recovery retained; full iteration verdict follows the exact
native receipt.** Browser facts, actual HTTP sequences, original failures, native
tests and source bindings are separate from hosted acoustic opinions. Current
verification/export dispatches zero inference or synthesis. Local Lab17 reuses
its original `source-0987483` model/audio/context artifacts and appends this scoped
verification without repeating them. Private environment/credential files are
excluded from the explicit artifact allowlist.

Exact final revision, gate counts, structural/language checks, Lab readback and
cleanup are added below after the committed-source run. No deployment,
postdeployment, PBT, financial execution, paid use, installation or publication.
