# Iteration 22 — ElevenLabs dictionaries and ordinary-flow verification

The production adapter now creates scoped English PLS pronunciation dictionaries
and uses their admitted dictionary/version locators through the existing
preparation, frozen render plan, native speech, storage, listening and scoring
owners. This is an implemented adapter qualification, superseding the earlier
standalone comparison for the selected Flash v2 binding. Final acceptance and
its exact committed revision are recorded in `ACCEPTANCE.json`.

## Findings and repairs

| Finding | Single owner and repair | Evidence and sibling disposition |
| --- | --- | --- |
| ElevenLabs rejected phoneme operations | `elevenlabs_dictionary.py` owns PLS construction, fresh response admission, scoped planning and model-specific wire format; `backends.py` delegates transport/audio ownership | Actual Flash v2 requests/audio plus local HTTP v4 dialogue/TTS tests. No new service, SDK dependency, queue or learner gate. |
| A global word rule would also alter correct occurrences | Existing acoustic scopes are partitioned into target-safe pieces, retaining exact text/coordinates, speaker/voice and final-turn gap. Only the selected second “think” receives the dictionary | Speaker1 “I think we should think again.” has correct first think; speaker2 “I think so.” is an additional control. Actual target/reference locators and five TTS requests are retained. Long context chunk coordinates have a literal regression. |
| Resume must retain accepted bindings and work | Existing render-plan/progress and completed-piece owners save the two locators before synthesis and reuse them | An intentionally intercepted second-piece429 follows one saved piece. Explicit resume keeps its asset and original plan/model/voice despite changed current model settings. Completed speech has four pieces, with five actual TTS calls including the target pair. |
| Malformed dictionary metadata could fabricate a binding | Fresh dictionary response admission requires nonempty string id/version, returning native PROVIDER_FAILED before dependent synthesis | Missing/empty/null/list metadata, unsupported model, quota/400 and partial-word/numerical phone-timing limits are local HTTP counterexamples. Saved dictionaries are trusted; no stored-value revalidation is added. Native public failure mapping is preserved. |
| Valid full-word phone pairs were rejected when they also recorded the changed phone | The ElevenLabs planner retains phone indexes as intent metadata for whole-word IPA pairs, without requiring native decoder timing | Pre-repair retained-source rejection and local HTTP regression. Numerical phone timing remains unsupported; no hosted rerender. |
| Refresh showed stale success beside a later failure | `useListening.refresh` clears its own notice when a new refresh starts | Original browser counterexample and repaired repeat retained. Write/retryChecking already clear both states; preparation clears progress on failure. Input and ordinary actions remain usable. |
| Hosted timing falsely inherited a Kokoro label | Existing `resolve_acoustic` reports a generated-piece interval when there is no decoder and preserves an actual decoder’s timing basis | The actual stored resolve request was replayed without inference; whole-piece coordinates are unchanged. A decoder sibling regression also passes. Native numerical transforms and their actual capability limits remain intact. |

## Ordinary flow observed

The test enters the real canonical preparation and separate mutation owners with
labelled, independently authored text replies. Those replies are protocol
fixtures, not hosted text-model or linguistic-quality evidence. It then uses the
real private worker and ElevenLabs Free, stores and reloads the actual audio/key,
plays Listen, saves and reopens a draft, submits it through the ordinary UI,
executes the native interpretation/scorer with declared constructed semantic
replies, displays findings/recommendations and reopens the saved result.

Independent expected arithmetic for the single unit is TP1/FN0/FP0,
correction1/1 and primary100. The observed result is100.0/100; the absent optional
explanation is not a primary-score penalty. The speaker’s accent is not an error.
The stored recording is3.456167s, mono24kHz PCM16. Its target interval is
0.889–1.361s, calculated from actual saved piece samples. Passage replay paused
at1.623757s under ordinary timeupdate event granularity; this is finite playback,
not a sample-accurate cut or regenerated clip.

Five actual Flash v2 TTS calls and two dictionary creations produced the four
pieces and target reference/contrast. One blinded paired observation through
the existing Gemini Free diagnostic identified target /sɪŋk/ and reference
/θɪŋk/. That is a model listening opinion with retained actual audio/context;
it is not human review, linguistic gold or universal category/model accuracy.
No repeated judge, performance campaign or full taxonomy inference run occurred.
V3/v4 transport is covered by controlled protocol tests; new live acceptance is
limited to the selected Flash v2 model, Sarah US and George UK.

## UI, UX and typography — self-review

**UI/UX: pass for the affected scope.** Actual Prepare readback, Library,
Saved attempts and Listen/results were inspected. The browser observes audio
play/end, target replay, draft save/reload, submitted result/comments, history
and reopening. Two transient503 reads recover automatically; three persistent
failures produce one authored recovery message, retain text and leave actions
usable. A controlled submit failure is logged, keeps the draft and offers retry;
explicit recovery saves the same answer. Raw backend canaries never appear.
These failures are deliberately controlled; no allowance is exhausted to create
an error and no hidden provider/model/text-only or billed fallback occurs.

**Typography: pass.** The typography skill and pinned interaction/review
procedure were used. Source Sans3 is actually loaded at17px/24.65px;1280×720,
390×844 and320×740 layouts have no page overflow, readable labels and working
keyboard/mobile navigation. Screenshots were inspected, not merely counted.
Long mobile full-page captures can place the sticky header at their current
scroll position; the top-aligned view is retained separately. No style overhaul
or new design dependency was needed for this adapter change.

**Evidence: pass within the stated boundaries.** Actual native fixture, attempt,
source key, stored audio, result and browser links agree. `tests/test_completion_i22.py`
checks concrete contents and independently expected arithmetic. Its negative
review cases reject omitted UX/typography,10px actionable labels, mismatched
attempts, planned tests labelled passed, candidate-authored gold and a50-call
performance request. It is a development evidence review, never a product gate.

## Budget, provenance and retained evidence

ElevenLabs subscription readbacks report Free,8900→8922/10000 included units,
max_credit_limit_extension0, cannot extend and zero current overage. The existing
restricted private key was reused server-side. Restricted model-list read returned401
and public unauthenticated lookup404; those are not claimed model-list successes.
Current account voices were read and actual Flash v2 synthesis succeeded.
No purchased credits, top-up, paid plan, overage or provider fallback was enabled.
Free media terms remain attached to the speech-service specification; software
licensing remains Apache-2.0.

Local MLflow experiment12, run `d9122ab28728486babe5f62e4bc6ce21`, retains native
input/context/receipt/output files, constructed semantic wires, actual WAVs,
frozen dictionaries, key, score and UI facts. Readback succeeded. The initial
export succeeded but its stdout parser rejected ancillary output; the existing
finished run was recovered by readback, without repeating export or inference.
The later timing-label source/replay is appended to the same run. Export and
readback add zero inference. Private credentials/environment files are excluded.

Private artifacts are under `data/iteration-22-elevenlabs-20261026/` and in the
local Lab. They include the native race observations, actual provider requests,
WAV/reference/target, blinded opinion, requests/actions and before/after pictures.
They are ignored developer data, not bundled provider credentials or a public
media release. This is self-review with independent literal expectations, not
an independent reviewer’s approval.

The original122 categories/recipes,42 formulas and11 source scopes are preserved.
`PRESERVATION.json`, `SELECTION.json`, `SOURCE.json` and the canonical DAG provide
the final selected scope. Later completion iterations and their planned cases
remain open. No deployment/postdeployment, PBT, financial execution, installation,
publication or user-app restart occurred. The running app3000, user settings/data,
media, pre-existing tabs and canonical unrelated GAPS.md were preserved.
