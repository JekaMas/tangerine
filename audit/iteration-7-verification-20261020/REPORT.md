# Iteration 7 verification and repair — 2026-10-20

Baseline: 5804886bc26d1ee103530b644636d228a9bd68fa, clean isolated tangerine/iteration-7-speech. Canonical unrelated GAPS.md is protected. Scope: complete iteration 7 review, repair, graph and committed-clean verification; no paid calls or later iteration implementation.

## Findings and decisive observations

1. Final quality transport failure aborts usable audio assembly (I7-20/I7-25, speech.go). All pieces may already be persisted, but a 503 or malformed measurement reply is returned as a render failure. Required repair: save an explicit advisory unknown rather than withhold complete audio. A cancelled foreground operation must still stop.
2. Requested pace and its observation status are absent from the saved assembly diagnostic. The general contract promises actual rate/deviation, but I7 has no independently timed lexical tokens. Required repair: preserve requested target/tolerance and explicit unknown actual WPM/deviation; do not infer spoken tokens/onsets from the written text. Actual lexical/acoustic measurement remains iteration 8.

## Evidence selection

Before repair add native positive/negative transport regressions and pure diagnostic cases. Existing prior receipts remain untouched. Changes to speech orchestration/diagnostics invalidate I7 and broad app-dependent closures; unchanged independent contracts/runtime evidence is retained. The final stable boundary must execute the complete I7 selection on a clean commit, then reconcile exact matching dependency results. No new schema/content audit is introduced.

## Responsibility review

Review orchestration, frozen pure plan, storage/CAS, accepted asset reuse, sample transformations, HTTP projection/transport, synthesis/worker lifecycle and evidence export separately. Findings are repaired through their existing owners. No SQL belongs in orchestration or pure diagnostics.

## Current checkpoint

Repair and direct regressions passed: four native advisory cases plus 24 pure speech cases, including four new pace cases. Existing observations remain separate from committed-clean acceptance. Full I7/dependency acceptance and Lab reconciliation pending.

Decisive baseline: native PostgreSQL/MinIO tests in data/iteration7-verify-quality-red.jsonl, command exit1: the measured/warning positives passed; 503 and malformed-reply negatives failed because render became failed with no final audio. The immutable API image was built from baseline production source plus the new transport tests before repair; source edits after the build do not change that binary. These failed-command rows are excluded from acceptance.

Static fixture accounting initially rejected the added properties because its expected I7 count was frozen at26. It now expects28 I7 /569 total properties, preserving all previous identities and the new8 cases. This was a harness inventory failure, not a product failure. Current jbcontext status for repository916ef04e reports no indices; no semantic-index result is claimed. Exact anchored source review is current, while the existing IDE lane is not applicable to this non-PSI repair.

## Review coverage and proof boundaries

- Orchestration: RenderPreparation owns frozen preparation/attempt/lease and terminal checkpoint. renderSpeech owns ordered pending pieces and accepted-child reuse. No SQL was introduced.
- Persistence: speech_storage.go owns DB queries, operation state and final case link; preparation checkpoint owns CAS/atomic case association. Audio/piece assets remain private and durable.
- Assembly: speech_assembly.go owns exact sample concatenation, pauses, diagnostic persistence and existing key linkage. It calls the transport's advisory quality policy and pure pace projection.
- Pure domain projections: speech_plan.go freezes voice/locale/order; speech_audio.go contains PCM serialization and explicitly unavailable pace observations; speech_key.go preserves accepted units and actual containing-turn intervals.
- HTTP/UI: speech_http.go and the existing private Next proxy expose safe status/stored audio, range reads and Refresh recovery; no private answer/receipt leaks or new provider calls on playback.
- Speech adapters/setup/worker: backends.py, model_setup.py, voice_setup.py, inference_capture.py, audio.py and server.py were inspected for selected binding, single admission, saved reuse, complete text, cancellation, offline runtime and no fallback. Their production code/parameters remain byte-identical in this repair. Hosted protocols and learned voice-setup output retain their explicitly substituted fixture boundaries; previous actual Custom/Base/Kokoro/eSpeak proof is scoped, not universal perceptual qualification.
- Evidence: native piece context/receipt/export remains the existing route. Five fresh local synthesis observations will accompany the required full I7 run; text/mutation upstream inputs remain constructed, not paid text inference. No new content/consistency revalidation, human approval or release gate was added.

No additional in-scope defect or unresolved product decision was found in the traced contracts. Verification remains pending until the selected committed-clean runs and exact reconciliation complete.

## Dependency harness finding and repair

The first complete UI dependency trial passed52 iteration2 cases but failed iteration1.test_config_durable_positive. Its preceding damaged-file negative passed; the next startup read CONFIG_DAMAGED despite the Python cleanup having restored the file in place. The later startup and four isolated configure/corrupt/restore probes passed. Exact first-failure container bytes were not retained, so a VirtioFS visibility cause remains a hypothesis, not an established product defect. The initial isolated empty operator-file probe also returned an unreadable .env; the directory-mounted nonempty equivalent passed.

Repair is limited to test-owned fault cleanup: atomically replace restored files, consistent with production configuration's atomic publication. Existing failure/success/bytes/permissions expectations remain intact. Five existing source/configuration fault cleanup sites share this helper; no launcher/configuration production code or new retry/check was added. The full launcher command will be rerun after this test-source/fixture change. All passing rows in the original exit1 launcher command remain excluded; the separate exit0 iteration2 command retains its52 observed passes.

Full I7 acceptance already passed112/112 on committed-clean4d65a5c. The subsequent Python-only foundation fixture change does not affect its112 source/scenario/command/dependency fingerprints; they must be retained exactly.
