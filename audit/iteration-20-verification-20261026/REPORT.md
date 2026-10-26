# Iteration 20 verification and repair

Scope: UX-04/UX-05, results-first layout and finite stored-passage replay.
Baseline288da10 follows accepted source f2bb38f. The selected properties are
FIN-UI-04.P1, FIN-UI-05.P1 and FIN-VERIFY.I20.

Two confirmed P2 defects are repaired: old Refresh/progress/pre-submit snapshots
could overwrite a newer result or submitted answer; queued native seek/pause
events could cancel the next passage's end stop. FINDINGS.md lists causes,
repairs, all related sibling dispositions and proof limits. Session delivery is
owned by useListening; progress remains an adapter. Stored range lifecycle is
owned by passageReplay. Presentation and existing transient-read recovery keep
their existing responsibilities. No additional learner gate, stored-data scan,
approval or implicit provider/write retry was introduced.

**UI/UX: pass.** Actual source-built CUA verifies the exact stale-read races,
retained score/answer/input, bounded transient-read retry, explicit recovery,
draft Save/reopen, checking/uncertainty, media403 recovery, keyboard Replay,
replacement, manual playback and next-practice/return without autoplay. The
final progress probe holds later successful polls until after observing the
old response; they cannot conceal a regression.

**Typography: pass.** Applied the installed typography skill and project review
procedure. Current screenshots and computed styles cover completed1280/390/320,
draft320, checking320 and uncertain390. Loaded Source Sans3,17px/24.65px body,
16px controls at least44px high,15px labels and a3px visible focus remain readable
without horizontal overflow. The60.0/100 group fits at320px; explanation and
found/missed/false counts remain distinct. Results/CSS need no further change.
Inspected evidence includes completed-result-1280.jpg, completed-result-320.jpg,
keyboard-320.jpg, draft-320.jpg and uncertain-390.jpg. The original unchanged
presentation/maximum/unavailable receipts retain their stated narrower scope.

**Evidence: pass for the observed scope; final committed-clean reconciliation
is recorded in ACCEPTANCE.json after the source commit.** Existing native
attempt/results and25.875-second WAV are reused read-only. Current actual media
traces stop at16.220/16.237s after rapid replacement/queued pause. Ordinary UI
Replay9.590–14.839 pauses15.089s, with normal browser-event granularity; second
and replacement ranges pause16.519/24.764s. Native manual Home seeking cancels
the old stop and reaches the full25.875-second end. Current read-only submitted
answers never turn back into drafts after an obsolete response.

The original33-case receipt is immutable and does not cover the newly found
counterexamples. There are27 added cases: six queued/current media-owner,
six progress-owner and15 current CUA/review assertions. The complete selected
set contains60 unique physical test identities across five commands. Independent
expectations include exact result60, response ordering, draft text, range end
bounds, request counts and readability. INVALIDATION.md records why each changed
owner was reobserved and which native/presentation observations remain valid.
REVIEW.json names actual artifacts and self-review limits.

Focused owner and current-browser cases passed. Final source build, strict
OpenSpec, structural graph/discovery/compatibility, stable format and exact
committed-clean acceptance are reconciled in ACCEPTANCE.json. Source/runtime
and assertion identities are captured once in SOURCE.json; no raw-schema archive
or runtime consistency check is introduced.

Controlled HTTP provides old/current states and intercepted Save/Submit outcomes;
those writes do not prove new native persistence or LLM judgment. The diagnostic
page uses the real browser media element and production replay owner; ordinary
app wiring is tested separately. Six constructed intervals do not prove six
audible mistakes. The review is self-review with independently authored literal
expectations. No independent human reviewer, provider quality or full-release
qualification is claimed.

No provider inference/synthesis, paid credits/overage, PBT, financial execution,
deployment/postdeployment, installs or publication. User app3000, its settings/
database/media, pre-existing tabs and unrelated canonical GAPS.md are preserved.
API, speech, migration and catalogue inputs remain unchanged:122 categories and
recipes,42 formulas and11 original source scopes. No further product decision or
unresolved in-scope finding remains after the recorded repairs.

Evidence: `data/iteration-20-verification-20261026/` (ignored), with retained
native/presentation receipts in `data/iteration-20-results-replay-20261026/`.
Only the owned local test tab/gateway/container are cleaned up at completion.
