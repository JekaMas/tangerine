# Required AI development tooling and prompt/context control

Date2026-10-09. Baseline d18920f. The user explicitly invoked openspec-update-change and requested properties so Tangerine AI development always uses the selected MLflow tooling without unaccounted prompts/context. This increment explores and revises specifications/project guidance only. The unrelated GAPS.md edit is preserved.

## Result and important distinction

Twelve new DEV properties make actual AI development observation use the Lab. Existing LAB/CMP properties are retained: they already own runtime registry/context/trace/experiment behavior; DEV specifies the development evidence and coverage contract around those owners. Ordinary runtime stays independent of Lab. No quality-score threshold, peer review, full corpus requirement, hosted account or additional infrastructure is added. Activation remains explicit and available; development cannot falsely claim measured correctness/improvement/completion without its required observations.

The canonical definition is specification/v2/docs/ai-development.md. docs/development/AI_DEVELOPMENT.md routes future implementation/review through the existing tools. AGENTS.md and CLAUDE.md point to it outside the unchanged generated workflow blocks. A stale project review guide requiring corpus/empirical approvals and tenant/user authorization was reconciled with current user policy. The shared workflow revision, generated skills/config/install hashes and the referenced Smart Example worktree were not changed.

## Exploration findings

The former Lab scope had no mandatory project development evidence route. Its eight LLM roles/two generation phases did not alone cover the standalone diagnostic judge or speech/local model/ASR/assessment inputs. Stage templates were versioned but the development contract did not explicitly inventory schema descriptions, repair/fallback wrappers, adapter frames and other trusted additions. No development-level independent dispatch/native/MLflow reconciliation defined whether a logger/exporter missed a call.

Exact provider/prompt/HTTP searches covered services/api, services/speech, services/web, scripts and tests. The inspected Go client call in http.go is an internal speech readiness check; server.py is a health-only speech foundation; UI fetches are internal routes. These are not provider calls. Current inspected code has no implemented generation/evaluation/synthesis adapter to certify. The new14surface declaration remains planned. Search results are discovery evidence, not proof of runtime completeness or an exhaustive dynamic-call analysis.

## Properties, failure cases and independent evidence

| Property | Required development behavior | Counterexample / decisive oracle |
|---|---|---|
| DEV-01 | AI-affecting completion uses actual Lab-linked evidence; ordinary runtime remains independent. | Missing selected Lab observations cannot be replaced by an enabled flag or screenshot. Compare actual selected dependency/case/run receipts. |
| DEV-02 | Inventory all owned inference, helpers/wrappers/plugins and future adapters, including speech/local models. | A helper SDK/local-model path omitted from the registry must appear as an unmatched independent dispatch. |
| DEV-03 | Version every trusted instruction source, including schema/repair/fallback/judge/reference/adapter fragments. | Compare actual serialized bytes with owned fragment sources; hidden concatenation or recursive answer interpolation is exposed. |
| DEV-04 | Save exact final model-visible request parts/parameters/bytes and framing, also for SSML/audio/reference input. | Independent transport/local-argument capture detects a post-snapshot SDK/default mutation. Template hashes alone cannot pass. |
| DEV-05 | Separate all actual attempts/outcomes/cache views with real lineage and usage. | Refused/crashed/repaired calls remain observed even when no successful output exists; cache inspection never fabricates inference. |
| DEV-06 | Exercise actual disclosure, conditioning, source selection and budget fidelity. | Independent expected stage inputs detect key/prior-grade leaks, truncated answers and canonical-versus-surface assessment errors. |
| DEV-07 | Bind actual variants and cache identity to all relevant trusted/input/model/voice changes. | Stale alias/cache/profile substitution cannot change frozen execution or historical attempts. Compare actual dispatched binding. |
| DEV-08 | Measure affected semantics on frozen positive/negative references and dependent pipelines, preserving failed/unperformed rows and all122coverage reports. | Circular labels, leaked expectations, omitted failures and unselected leaves cannot establish independent improvement/full coverage. |
| DEV-09 | Observe/challenge judge/scorer prompts, references and correct/incorrect/unknown verdicts. | Withheld authored expectations and actual modality/native arithmetic expose self-validation, false support and invented heard phones. |
| DEV-10 | Inspect permitted context privately and through sanitized Lab copies with actual hashes/redaction/limits. | Controlled secret canaries must not export; a withheld/redacted body cannot be advertised as full capture. Grading bytes stay unchanged. |
| DEV-11 | Preserve native results across export failure; sync exports without new calls; cleanup failures remain pending. | Compare independent dispatch count before/after sync and actual exported artifact identities/cleanup receipts. |
| DEV-12 | Join independent dispatch observations, native input/receipt snapshots and actual Lab exports; invalidate only changed semantic proofs. | An orphan, duplicate link, zero-population integration claim or missing required path stays incomplete. Same-writer receipt counts are not an independent oracle. |

Each property has two concrete scenarios and distinct positive/negative planned edges, totaling48. properties.json retains setup, observable expectations and oracle. Verification/discovery records are in the existing canonical change; no second task list is created.

## Complete finite surface scope

domain/ai-development.v1.json declares nine application LLM stage/phase surfaces, the dedicated diagnostic judge, Azure TTS, Kokoro local inference, Whisper ASR and Azure assessment:14total. Assessment phone/prosody/chunk calls and all retries/fallback/repair/reconsideration/cache paths are individually observed under their real surface. Future learned/audio-capable adapters require inventory entries. Deterministic FFmpeg/Praat transformations retain their own evidence rather than becoming fake model calls.

New ai-surface-inventory and ai-development-run schemas define exact revision/dependency/source ownership, selected case/property/population scope, model-visible snapshot assets, dispatch/native/export links, MLflow artifacts and unresolved discrepancies. Zero-call deterministic artifacts still have actual Lab linkage when observed; pure spec updates keep future runtime work not_run. Required runtime snapshots cannot be omitted merely because the role has no text prompt. Provider-hidden context/weights/training remain unknown; this policy controls owned inputs and execution, not vendor internals.

Future helper contracts are `lab eval <experiment-file> --development <development-run-file>` and `lab verify <development-run-file>`. They reuse native owners and local MLflow; verify makes no inference. Existing lab export/activate/sync remains. This increment implements none of these. Run-scoped tracing/capture never silently changes ordinary workspace privacy settings.

## Validation and evidence limits

95static checks pass: new contract positive/negative assertions; independent constructed joins covering missing/duplicate/orphan/empty/cache populations; trusted/control/disclosure commitments; every current schema field/hash/reference/index and JSON/YAML/vector; preservation of earlier graph records and original source/provider/prompt/metric bytes; managed instruction-block preservation. These are audit artifacts and independent small arithmetic/identity counterexamples, not actual product-verifier or provider tests.

The active namespace has213files,134schemas,3,001indexed field occurrences and88local schema references. Strict OpenSpec and graph/discovery pass:374requirements,389properties,1,556case edges. All48new runtime behavior edges are blocked/unexecuted. Previous requirements/properties/cases and their receipts are unchanged; no historic application/provider/benchmark observation was refreshed.

The initial static check failed because the new quality paragraph omitted an explicit failed/unperformed-row statement. The document was completed; check-initial-failure.log is retained. No prior fully green check was repeated without changed semantic input. The final report/plan additions do not invalidate the observed artifact/graph contracts.

Project source-publication validation is recorded separately after staging the new guidance/spec. Shared routes, skill packages, workflow block/pin and application/native inputs are unchanged, so their unrelated previously observed mechanics are not rerun. No runtime Lab/SDK/model/Docker/install, inference, application implementation, key/config mutation, migration, email or external publication occurred. There is no current claim that runtime blind spots have been eliminated. Future implementation must establish the specified finite coverage using actual observations.

No additional product decision is needed for this scope: the user has selected the tool and required the development route. Preserve ordinary local simplicity, original122taxonomy/recipes,42grade formulas,22Labdiagnostic definitions,11full-source scopes and all original provider/prompt bindings. Continue from the canonical tasks with actual implementation/inference authority when provided.

Final focused inspection adds actual local-model preprocessing/weight/version evidence; public pipeline arguments alone are insufficient. The two new commitments and changed-vector parse/hash checks pass, with91unchanged static observations and the earlier green structural graph retained. See focused-check.log and invalidation.md.

Project workflow source-publication validation passed after staging:196owned sources checked, no errors. Separate scope assertions confirm the new guidance/spec documents are tracked and no application, generated skills/config/install metadata, shared pin or unrelated GAPS.md is staged. workflow-publication.log retains its source/index proof limits.
