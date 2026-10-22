# Iteration 16 verification and repair

**Status: GREEN for the complete selected iteration.** On committed-clean code `27b10be29bdc9679d46aa7350e401d85598adb5e`, all **373 case edges / 333 distinct physical tests** reconcile as passed over eight properties: 202 positive and 171 negative edges. There is no unresolved selected case. This is the complete union of actual retained and newly executed evidence under the user's explicit reuse rule, not a newly executed whole-suite command or a claim that every historical source/benchmark plan ran.

The canonical completion record is [release acceptance](../iteration-16-release-20261021/ACCEPTANCE.md). [RECONCILIATION.json](RECONCILIATION.json) records each physical identity, exact original observation, source, retained/fresh disposition and committed native receipt. Twenty edges executed on the final code revision; another 353 retain valid earlier observations. Fifty-five passing edges have committed-clean native receipts, including those twenty; these provenance groups are not additional tests. A documentation/delivery commit does not invalidate unchanged behavior.

## Repairs and responsibilities

| Finding | Final repair | Observed proof |
|---|---|---|
| V1: Settings showed a custom saved audio profile as disabled and advertised the wrong model setup | AudioDiagnostics.js renders the actual saved custom/overridden binding and derives setup from the saved model. Storage, inference and scoring owners are unchanged. | Actual Chrome/API/DB red; clean8a33dc0 four physical/five-edge green covers custom3B reload/setup, same-ID7B override, null disable preserving text profiles, zero inference and source startup. |
| AMD64 registry and classic-store cache blocked qualification | Authorized Docker Desktop restart restores registry access. Test-only PlatformImage retains the original variant, officially pulls the same pinned AMD64 reference, restores the ARM reference/image ID and publishes success only after cleanup. | Cleanf7a792a native16/16: twelve actual portable/cache observations plus four labelled controlled CLI-boundary regressions. Source completeness retains its original valid observations. |
| Local auditory model falsely reported a pause in clean speech | Explicitly select the user-authorized Gemini Free binding, preserving the original independent expected contrasts,512-token maximum and270-second action limit. | Both real HTTP200/completed responses pass on clean27b10be, with meaningful correct reasons, no conflicting findings and no invented timestamps. |
| V3: Gemini ignored configured HTTPS proxies | One production transport line uses standard proxy configuration; TLS verification and no redirects remain. The test-only encrypted tunnel permits only the approved Google443 destination in addition to its prior targets. | Two exact baseline counterexamples fail. Six affected request/response/proxy tests and two destination tests pass on clean27b10be. Actual verified-TLS Google requests then complete. |
| Setup guide still called implemented flows unimplemented | Correct current implementation wording, distinguish account entitlement from adapter code and add concrete optional Gemini setup/usage instructions. | Guide matches observed local main flow and actual unbilled-project admission. No new runtime gate or feature deferral. |

Go retains configuration, lineage, orchestration, private evidence, transactions and HTTP. Python retains audio transformations, actual inference/capture and foreground process lifetime. The frontend renders accepted state and explicit actions. Native grading remains separate from model judgments. The latest production change is one transport line; the cache/tunnel helpers are test infrastructure. No queue, application login, human qualification, silent fallback, repeated accepted-data audit or diagnostic publication gate was added.

## Same-binding actual auditory qualification

The user explicitly approved Gemini Free only, the Gemini onboarding terms/18+ declaration, separate Cloud terms and a restricted private key. The dedicated project `tangerine-free-audio-20261022` was created. Its authoritative Cloud linked-account page states **no billing account**. No trial, payment method, billing linkage, purchase, paid credits or overage was enabled. AI Studio created a new authorization key, Gemini-restricted by vendor default. It is stored only in ignored0600configuration; no key value appears in this report, source, ordinary backup or Lab packet. Admission evidence: data/iteration16/gemini-free-admission.json, gemini-no-billing.jpg and gemini-free-quota.txt.

The actual project quota admitted gemini-3.8-flash at5RPM/250KTPM/20RPD. This is a dated observation, not a product constant or another project's entitlement. Both requests use the same free-tier model, managed prompt bytes,512-token maximum, stateless/no-stream/no-background configuration and actual target/reference WAVs. Response model is gemini-3.8-flash in both cases.

| Independent fixture | Actual model result | Actual duration and usage |
|---|---|---|
| Actual Kokoro target with a native two-second inserted pause:4.1s/98,400samples; clean reference2.1s/50,400samples;24kHz | e1/pause_insert/supported; reason identifies a distinct roughly two-second pause before opens. No contradictory finding or invented location. | Provider23.233s;1,808total tokens. Complete native test51.70s including fixture preparation. |
| Actual clean2.1s/50,400sample target and separately constructed unfulfilled pause intent;24kHz | e1/speech_realization/contradicted; reason states the phrase is continuous without the intrusive pause. No contradictory finding or invented location. | Provider33.939s;1,627total tokens. Complete native test57.60s including fixture preparation. |

Exact root: data/iteration16/native/tangerine-diagnostic-49288ddc1064. Native clean two-case receipt: data/iteration16/auditory-native-gemini-corrected-27b10be.json. Full saved prompt/context, model bindings, audio, request/response, provider usage, native findings and operation receipts remain retained. Numeric native grades remain null for advisory model findings. This qualifies these independently authored contrasts, not universal phonetic/accent accuracy.

Earlier Qwen failures remain failures. The first Gemini direct attempt20b172f40a53 failed transport; its stopped-service downstream render failure is retained. The next proxy attempt1f5591da4e2d used a stale published test-agent port and also failed before a model result. Correcting that agent binding produced an unauthenticated non-model404 through verified TLS; only the two failed real auditory tests were then rerun. No good label alone, best-of response selection, hidden retry, deadline increase or score change supplied qualification.

## Local Lab and full selected coverage

All **19 diagnostic operation packets** passed actual local MLflow3.17.0 artifact/trace export and readback, including successful observations, failed local-model experiments and both failed Gemini transport attempts. The four physical/eight-edge Lab cases pass on clean27b10be. Export made **zero new model calls**, and the deliberately absent artifact was rejected. Root: data/iteration16/lab/run-ceb0a76cd0; receipt: data/iteration16/diagnostic-lab-gemini-27b10be.json. Full context and original outcomes are preserved; debug export does not relabel a failed experiment as accurate.

| Property | Passed edges | Unresolved |
|---|---:|---:|
| I16-01.P1 | 4 | 0 |
| I16-02.P1 | 16 | 0 |
| I16-03.P1 | 103 | 0 |
| I16-04.P1 | 125 | 0 |
| I16-05.P1 | 54 | 0 |
| I16-06.P1 | 22 | 0 |
| I16-07.P1 | 33 | 0 |
| I16-08.P1 | 16 | 0 |

The clean27b10be affected run proves eight protocol/tunnel tests and the current-source assertion; its two auditory failures remain recorded. The later same-code two-case run supplies their actual passes. The current source ZIP starts all five ARM services without Git/workflow metadata; startup-only selection retains the three unchanged Settings cases. Actual AMD64 synthesis, cross-architecture restore/collision, saved Library/result/audio and restart retain cleanf7a792a proof, including restored original ARM image ID. AMD64 execution here is emulated on this ARM Mac.

The actual installed-local LLM main browser flow, mutations/key, Kokoro speakers/audio, persisted answer, LLM interpretation/native100/comments/recommendations and optional review/dispute retain their earlier valid observations. All11main routes retain success/failure/recovery coverage. The [media index](../iteration-16-release-20261021/EVIDENCE.md) contains **153 pictures,25 silent browser videos and18 exact WAVs**. It retains custom Settings evidence when the current-source pointer advances and adds the two exact WAVs actually sent to Gemini. No audio was edited or fabricated for delivery.

## Checks and acceptance boundary

Stable447static assertions,5542structural property assertions and graph/discovery checks pass. Strict OpenSpec, unchanged Go vet/gofmt and native production builds retain their valid receipts; the fresh source run executes the locked production web build. The graph contains665requirements,680properties and3988historical edges, including1895original blocked and14planned entries. Those historical source/benchmark/scaffold entries are not invented runtime passes. The user's explicit retained-green rule supersedes a blind whole-suite rerun; every current selected case has its actual evidence in the reconciliation.

All122category/recipe identities,42formulas,11original full-source identities and migrations remain preserved. [ORIGINAL-SCOPE.md](../iteration-16-release-20261021/ORIGINAL-SCOPE.md) maps optional full-release bytes, empirical populations, provider entitlements and historical superseded plans to their actual consumers. Source mechanisms do not fabricate unavailable source bytes; these external data are not prerequisites for ordinary generated exercises. No universal linguistic, unavailable-provider or physical-x86/Windows claim is made.

This is the agent's source/responsibility review, not independent human or unavailable semantic/IDEindex evidence. Exact failure/source tracing identifies the changed owners. The sole task list remains openspec/changes/implement-teacher-error-trainer/tasks.md. Final delivery closes only the selected iteration and its mapped current release tasks; it does not archive or publish the whole OpenSpec change. Canonical unrelated GAPS.md, private records/models/media and original host containers remain protected.
