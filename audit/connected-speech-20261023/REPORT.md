# Rhythm, blending, assimilation, intonation and connected speech

The requested families exist in Tangerine's taxonomy and native control routes. The previous comparison did not establish complete audible coverage. This follow-up adds concrete coalescent blending, acceptable connected-speech controls and opposed/contextual intonation examples, repairs the native intonation gap, and observes the current local speech service. The precise specification is `specification/v2/docs/connected-speech-and-intonation.md`; no taxonomy ID, original recipe, scoring formula, corpus scope, public API or human review requirement is added or removed.

## Coverage and actual observations

| Feature | Existing route | Added observation |
| --- | --- | --- |
| Rhythm | Scoped `pitch_duration` on `pronunciation.suprasegmental.rhythm` | “for the” in “I can pay for the car”: 1.5× selected duration, 1,800 added samples, surrounding samples preserved. |
| Blending / coalescence | Full-phrase `phone_pair` on the assimilation leaf | /d+j/ in “would you” and /t+j/ in “don't you”: careful reference, permitted blended variant and deliberately wrong affricate voicing. The paired model opinion reports the deliberate contrasts and the natural blends; it sometimes confuses two permitted forms. |
| Contextual assimilation | Same assimilation leaf | “ten bags”: permitted /n/ and bilabial /m/ controls versus inappropriate /ŋ/. The paired opinion distinguishes the target but sometimes hears the normal reference as the other permitted form. |
| Linking | Linking/resyllabification leaf | Three actual “turn it off” clips: smooth, carefully separated and intrusive glottal boundaries. The model opinion does not consistently confirm the intrusive boundary. Renderability is established; perceptual qualification remains mixed. |
| Weak forms | Weak-form leaf | Actual neutral /tə bi/ and strong /tuː bi/ requests. Paired opinions do not reliably distinguish this realization; it remains unconfirmed by this automated check. A strong form in a contrastive context is not intrinsically wrong. |
| Elision | Elision/reduction leaf | “documents, not one document”: permitted /t/ elision retaining plural /s/ versus removal of the plural-bearing ending. The paired model reports the deliberate loss of the ending. |
| Thought groups | Exact `pause_insert` | 600 ms = 14,400 zero samples between “The” and “policy”, rather than a legitimate clause boundary. |
| Statement versus confirmation question | Intonation-function leaf | Same words “You have car insurance.” and “You have car insurance?”: actual reference/contrast rise and fall measured in both directions. |
| WH-question | Intonation-contour leaf | “Why do I need insurance?”: actual falling reference and rising contrast; its question mark does not require a rising target. |
| Fall–rise / rise–fall | Same contour leaf | Self-contained audible uncertainty/certainty setups, with measured opposite reference/contrast shapes. |

There are **13 constructed practice contrasts and 31 actual local WAVs**. The loopback listening page is `http://localhost:8768/`, opened in the in-app browser. It exposes references, contrasts, permitted variants, measurements and the mixed auditory opinions. Both earlier comparison sets and the original user exercise/answer are preserved. These recordings do not establish universal native phonetic fidelity, independent linguistic gold, empirical frequencies or hosted-provider qualification.

## Repairs through the existing owners

The old source-relative resolver recognized only `(0,0)→(1,+5)`. Eight independent baseline cases failed for falling/fall–rise/rise–fall or missing periodic evidence; one intended fall even measured as a rise. The resolver now recognizes four named templates on the existing two intonation leaves and adds source-median F0 to their offsets once. Custom absolute curves and already-resolved data retain their semantics.

Real speech revealed a second problem: an end-of-word unvoiced tail could consume the end of a contour. Named template knots now map to actual source voiced-frame quantiles. No new field, model call, provider, saved-data audit or readiness gate is introduced. The existing measurement owner still reports missing periodic evidence. A final review also preserved nullable `pitch_points` on unrelated operations; its focused regression passes.

The original WH example's short “start” nucleus did not provide stable full-contour observation. That source, actual failed measurements and requests remain retained. A new self-contained WH item ending in “insurance” supplies a longer voiced nucleus; only that changed source and its controls were regenerated. The ten other passing physical observations were retained. The measurement procedure uses actual voiced frames and an independently declared 40–600 Hz analysis range, rather than assigning pitch to silence or excluding legitimate low male-voice F0. The source controller's measurements/limits remain separately captured.

Actual auditory replies used a `results` list or a unit-keyed object, sometimes expressing unit identity only in the map key. The diagnostic decoder now admits those unambiguous record forms, preserves all supplied observations/uncertainty and retains rejection of unrelated/malformed objects. This is normalization, not new acoustic evidence. All 13 actual retained HTTP200 replies were re-admitted through the repaired native decoder **without another model call**. Original native parse failures remain intact.

Responsibilities remain separated: source-dependent contour resolution stays in `acoustic_controls.py`; response normalization stays in `diagnostic_models.py`; the existing compiler, model, transform, persistence and scoring owners retain their responsibilities. Only the speech image was rebuilt/recreated. Provider credentials/configuration were compared once before recreation and preserved; the speech container is healthy and the application readiness endpoint returned200. No existing data or playback asset was rewritten.

## Tests, reuse and proof limits

Four OpenSpec requirements/properties and **27 positive/negative executable cases** are linked in the current `verification.json` DAG:

- CS-01: source-relative templates, voiced endpoints, resolved/absolute/nullable compatibility and missing periodic evidence.
- CS-02: independent zero-crossing F0 direction on constructed signals and scoped duration/outside-sample preservation.
- CS-03: complete-phrase coalescent/unblended phone sequences and unchanged transcript compilation.
- CS-04: real diagnostic decoder normalization and malformed/unrelated controls.

The current27-case reconciliation uses20 unchanged cases from the24-case pass, six current wrapper cases from the repaired scoped command, and the final nullable regression. Appending wrapper methods changed the test-file fingerprint but not those20 test bodies/helpers or their production contour/compiler/rhythm semantics; their original observations are retained rather than rerun. The first wrapper command could not import the module inside the container; the corrected `discover -k AuditoryWrappers` command executes exactly that class. Both failed command and repaired receipt remain recorded. Two older source-relative and eight older judge-decoder regressions also pass on the final source. These **37 code observations** test native controls/normalization, not every product feature or all linguistic outcomes.

**12/12 actual speech physical observations pass**, using ten retained observations plus two changed-WH observations. The independent checks read actual PCM/F0/counts, not requested phonemes, target points or a transport status. The initial unvoiced-tail measurements and the original WH source failure are preserved rather than overwritten as green.

The free Gemini3.1Flash-Lite audio judge received actual audio and full captured context. Initial nine/eight-clip batches had ambiguous generic reference labels; explicit blinded two-clip observations then used the native transport's intended pairing. Eleven paired requests produced22 clip judgments, with **15/22 exact option agreements**. This is a model-opinion agreement count, not a validated accuracy estimate or universal synthesis pass. Most disagreements are between permitted forms; weak-form and intrusive-linking targets also remain uncertain/not confirmed. No new model-quality threshold, human review, automatic retry or publication gate was created. No case is declared perceived gold.

The real browser loaded all31players with `readyState=4`, no media error, and13case sections. Native UI playback of the statement and confirmation-question references succeeded; playing the latter paused the former. The page is retained for the user. This verifies playback, not what a listener hears.

Strict native OpenSpec validation passed. The workflow wrapper's final apply-guidance capture truncated stdout and returned `invalid_output` despite the passing spec and other guidance surfaces; the actual complete apply JSON was captured/parsed separately without rerunning the green spec check. Graph and discovery validation are recorded separately. No full-release or unrelated suite rerun is claimed.

## Evidence and Lab

Ignored `data/connected-speech-20261023/` retains actual plans, source/paired model inputs and outputs, decoder metadata, resolve/transform packets, WAVs, physical measurements, blinded prompts/bindings/replies, failures, source snapshots, deployment/runtime bindings, browser observations/screenshot, test/guidance logs and native export receipts. `stimuli.json` is the frozen authored test population; it is not an external corpus.

Local MLflow experiment4, run `0a6494d4086c49c7a46299cbe0d52c4b`, retains the native experiment,31WAVs and context/output artifacts. Physical readback observed12/12. Export dispatched zero inference calls. Final nullable source/test and delivery records are attached to that same run separately; earlier observed source snapshots remain intact.

Only existing local Kokoro and the existing unbilled Gemini Free auditory profile were used. **No purchased credits, purchase, trial, billing linkage, overage or paid fallback occurred.** No ElevenLabs allocation was consumed in this follow-up. Azure access and practical Qwen runtime qualification remain the earlier separate dependencies.

## Research basis

Natural coalescence and assimilation are permitted connected-speech phenomena; careful unblended variants are not automatically wrong. The actual task/meaning and declared allowed alternatives matter. See [British Council connected speech](https://www.teachingenglish.org.uk/professional-development/teachers/teaching-knowledge-database/c/connected-speech), [/d/ + /j/ assimilation](https://africa.teachingenglish.org.uk/classroom/pronunciation/assimilation-d-and-j), and [connected-speech examples](https://www.britishcouncil.org/voices-magazine/pop-songs-connected-speech-fluent-english). [Cambridge intonation](https://dictionary.cambridge.org/grammar/british-grammar/intonation) distinguishes common falling wh-questions, rising yes/no questions and fall–rise functions; those are contextual patterns, not a punctuation-to-pitch rule. These references explain the feature contracts, not the accuracy of these generated samples.
