# Iteration 25 apply — local Qwen dialogue pair

**Incomplete; no iteration acceptance.** The native completion/recovery tooling
is implemented and its controlled observations pass. The complete real Qwen pair
and actual browser activation/playback remain unavailable. Tasks I25.1–I25.3
remain unchecked. Constructed PCM and the historical 5.6-second preview do not
close them.

## Implementation and exact boundaries

The common material is the same saved four opening car-insurance turns from
preparation `9dbf8c95-51a3-4c0f-9395-b3a77a824d22`. Its file, four target locations,
reference/mutated IPA and phonetic respellings are unchanged. Speaker 1 uses Ryan,
speaker 2 Aiden. Qwen's selected 0.6B adapter accepts text; the mutation variant
changes only choices→shoy-siz, companies→kum-PAN-eez, another→uh-NUH-zer and
Collision→KAH-li-zhun. This is a pronunciation approximation, not exact IPA
control or a guarantee of four audible errors. The original canonical text/key
and the user's exercise remain untouched.

`backends.qwen` now uses an explicit local runtime configuration. CPU/float32
remains the default. MPS and float16 are optional explicit selections, never an
automatic fallback. The model cache separates actual device/dtype bindings; the
receipt retains requested compute and the loaded model/codec placement as
separate facts, Torch version, pinned model/voice and actual
tokenizer/generator inputs. The cached model's accepted manifest is trusted;
there is no repeated hash/schema-byte audit or new learner qualification gate.

`compare.py` calls the existing private native speech HTTP owner. It freezes the
source/profile/voices/runtime and native plan, saves each accepted response and
piece, resumes without regenerating completed work, assembles a variant only
after its pieces finish, and makes the completed reference available even if the
mutation variant fails. Only the final piece of each turn receives its 300 ms gap.
Every explicit invocation stays within 270 seconds. The unchanged native server
kills its foreground process group on deadline or disconnect. Cancellation
retains partial progress and produces an authored recovery message. There is no
queue, enlarged deadline, detached model work or silent provider switch.

The read-only listening page shows each available complete variant, incomplete
progress, target spellings and the original dialogue. Refresh and playback make
no synthesis call. A media read failure retries once, then gives plain recovery
guidance; Refresh remains enabled. Only the page/font/two selected WAV paths are
served. Private requests, environment and Lab artifacts are not exposed.

## Observed tests and preserved failures

The complete selected informational graph has **28 exact cases: 26 passed,
2 skipped, 0 failed**. The skips are `FIN-QWEN.P1.qwen_positive` and
`FIN-VERIFY.I25.review_positive`. Native command exit 0 does not turn those skips
into acceptance. The committed-clean observation on source `35ac5b5` is recorded in STATUS.json:
26 pass,2 skip, runner incomplete. This is not a green acceptance receipt.

The passing cases cover literal target/voice/split projection; complete sample
assembly with exact turn gaps; admitted-response and completed-piece reuse;
partial cancellation and resume; reference survival; 270-second clamping;
actual native child termination on timeout, client disconnect and client socket
timeout; safe CLI recovery; explicit compute/cache/context wiring; missing-device
failure without fallback; preview rejection; private route exclusion; rendered
layout and actual controlled media read recovery; and misleading/omitted evidence
counterexamples. Only the trained-model output, device-availability signal or
model-import timing is substituted in those native cases. No fixture proves GPU
execution, Qwen voice quality, acoustic realization or real user activation.

Self-review then reproduced a requested/consumed-runtime defect on source
`f975f00`: a frozen CPU request was labelled one way while the adapter consumed
the server's MPS environment. The native factory counterexample failed as
expected. Runtime selection now travels in each saved `qwen_runtime` piece and
is consumed by the existing configuration owner, preserving it across changed
server defaults. Requested and actually loaded placement remain separate facts.
The exact red/green model-factory and planner tests retain this repair without
any trained-model inference or new runtime validation gate. The original
committed-clean24-pass/2-skip record is retained as superseded partial evidence;
it does not cover this counterexample or the repaired source.

The first route test failed because its test-local variable shadowed the
`http` module. That harness error was repaired and its exact case passed.
The original failure remains in `contracts-first.log`. Initial discovery
validation also exposed references to the former planned negative test identity;
all scoped references now point to the implemented native cancellation case.
Strict OpenSpec 1.13.1, the complete structural DAG and discovery ledger pass.
Python syntax and rendered player JavaScript checks pass. Original 122 category
and recipe identities, 42 formulas, 11 source scopes and migrations are unchanged;
see PRESERVATION.json. Unaffected Go/web/provider/SSML behavior is retained from
its existing receipts, not rerun or relabelled by this increment.

## UI/UX, typography and evidence review

**UI/UX: incomplete for actual activation and Qwen playback.** Through CUA, the
real player rendered empty/partial/complete controlled views. A saved reference
remained visible while the other variant was unavailable. Each transient media
failure caused exactly two GETs and recovered; each persistent failure stopped
after two GETs with an authored message and an enabled Refresh button. Actual
audio metadata loaded without autoplay. These were constructed 6-second PCM
fixtures, visibly labelled as such. Their native HTTP observations are in
media-http-observations.json; browser facts are in browser-observations.json.

Clicks, the exposed Expand action, Playwright click, native audio Play and Tab
left the page unchanged, playback paused at 0 and focus at BODY. The documented
browser troubleshooting and scoped CDP mouse alternative did not restore
activation. No JavaScript dialog was present. The same input-delivery problem
was retained in I24; its cause remains unknown. No product interaction defect is
inferred, no page scripts/DOM mutations manufacture a pass, and the tool's prior
native-app inspection rejection is not bypassed. Actual keyboard, disclosure,
Refresh activation and playback remain unverified.

**Typography: pass for inspected rendered desktop/narrow states; expanded
details unverified.** The available typography skill and pinned verification
guidance were used. Inspected actual screenshots at 1280×720, 390×844 and 320×740
show clear heading/action/card hierarchy, 17 px Source Sans 3, 24.65 px line height,
readable wrapped labels and no page overflow. The reference and requested
mutation labels remain distinct. The loaded-font/computed-style observations
agree with the screenshots. Screenshot/metadata counts do not certify aesthetics
or unobserved interaction. Temporary viewport/display changes were reset and
the owned test tab/server were closed; user tabs and Microsoft handoff survive.

**Evidence: incomplete for the complete real Qwen pair.** Constructed/native
functional evidence and media read observations are retained separately from
actual synthesis. Model dispatches in this increment are 0; no hosted judge,
performance/bulk campaign, purchase, overage or fallback occurred. Local Lab
experiment16/run `22acb2b0fcc54e8780554724ebeb203c`, prefix `source-35ac5b5`,
retains48 artifacts and actual scoped readback of the source-bound run scope,
clean receipt, runtime inventory and browser observations. Export adds0 model
calls and cannot convert missing real synthesis into a pass. The earlier source
run `4afde08a6b9c487cb52660f32f37c4a2` remains separate. The earlier CPU timeout,
cancelled int8 attempt and short preview remain in the original comparison audit.

## Exact runtime blocker and next operation

The accepted pinned CustomVoice model is already in the local speech model
volume. The current Docker runtime is CPU-only and its prior full dialogue
attempt timed out. This Mac is an M1 Max with 64 GiB; existing Python 3.12/PyTorch 2.5.0
reports MPS built and available. Qwen/Transformers/tokenizer/audio dependencies
are absent from that host environment. The explicit request to install them in
an isolated project environment and copy the existing model cache is pending;
no installation has occurred. Repeating an unchanged failed CPU experiment is
not a new qualification or a practical runtime selection.

After that dependency is available, start the existing native HTTP owner on
loopback with the explicitly selected runtime/offline cache, execute the saved
comparison and inspect both complete recordings. Export actual dispatch/input/
output/model/context to the existing Lab, restore browser input delivery and
observe real playback/keyboard/Refresh. Rerun only invalidated cases, then obtain
the full committed-clean passed selection before checking I25 tasks. No new
product decision, corpus acquisition or human review is required.

The original task is I25 only. I24's protected Azure access and actual F0 pair
remain separate and blocked. The running app on port 3000, services, provider settings,
user DB/audio and canonical GAPS.md edit were preserved; no deployment occurred.

References inspected for runtime context: [Qwen's official model/API guide](https://github.com/QwenLM/Qwen3-TTS)
and [PyTorch's MPS documentation](https://docs.pytorch.org/docs/stable/notes/mps.html).
The actual host/cache observations, rather than those documents, establish this
installation's available hardware and missing dependencies.
