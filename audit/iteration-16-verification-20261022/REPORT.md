# Iteration 16 verification and repair

**Status: not green; full release acceptance remains blocked.** Reviewed starting sourcef2b5b47and repaired code on clean8a33dc0c53dfda0e954ef29d3d0e248df00f06b1. The user authorizes in-scope repair, separated layers/single responsibilities and commit. No paid-credit/hosted fallback, account setup, protected host restart, publication or archive is inferred.

## Confirmed defect and repair

**V1—Settings falsely represented saved audio-judge configuration.** A valid custom-IDprofile persisted through the actual API/DB, while the native selector displayed No audio judge selected. The captured page advertised7Bsetup although the saved model was3B. A model override under an existing preset ID also needed to display the actual saved model and matching weights, rather than the preset label/setup.

Real-browser red: `data/iteration16/verify-custom-profile-red.stderr`, root `data/iteration16/custom-audio-profile/run-c6ec2ec253`. Positive failed with saved_profile=custom-local-audio-judge, displayed_profile=''and the disabled-looking label. Its HTML contains the wrong7Bsetup command. Explicit null disable passed. These are real Chrome/Next/API/PostgreSQLobservations, not mocked DOM output.

Repair remains in `services/web/app/settings/AudioDiagnostics.js`: render the actual saved custom option; use saved model/billing values when its ID overlaps a preset; resolve setup through server-provided defaults matched to the actual saved model. Configuration selection still uses the existing save callback. No inference, persistence, provider, schema, score or acoustic owner was changed, and no new admission/audit gate was added.

Four physical tests/five DAG edges pass `--require-clean` on8a33dc0in55.427seconds:

- Custom ID, actual3Blabel, correct3Bsetup and reload persistence.
- Same-IDmodel override, actual7Blabel and correct7Bsetup.
- Explicit disable saves null, preserves text-LLM profiles and performs zero inference.
- Current source ZIP starts all five actual arm64services, with zero provider receipts.

The exact native receipt is `data/iteration16/verify-custom-final-source.json`. The new shared source fixture supplies the current-source requirement directly, replacing only the old exact-source startup test identity. It does not repeat the other unchanged source architecture/Settings assertions. The initial three-test intermediate green predates the strengthened setup expectations and is excluded from current qualification.

## Review scope and responsibility

Inspected the selected requirements, prior findings/raw observations and current changed owners: Go diagnostic configuration, input/reference selection, transport/evidence, durable transaction and HTTP; Python DSP/ASR/auditory/context/foreground lifetime; Settings/Reviews selection and readback; source/archive/architecture/recovery adapters; frontend/media/native/Lab correspondence. This is this agent's source review. No independent human review or unavailable semantic/IDEindex is claimed.

The suspected stale-case measurement identity is refuted because Reviews already keys Measurements by selected case version. Existing source-use checks inspect activity/catalog availability, not saved-byte consistency. Transport failures retain actual available bodies or explicit unavailable/null response; no unseen model body is invented. No additional demonstrated defect was found in these inspected paths. This does not certify unavailable external providers, every linguistic instance or all original empirical populations.

Go still owns configuration, lineage, orchestration, private evidence and transactional publication. Python owns sample transformations and actual model invocation/capture/lifetime. The frontend renders accepted state and requests explicit actions. Native grading remains separate from model judgments. The repair adds no background queue, hidden retry, human review, repeated stored-data check or score/publication gate.

## Full selected reconciliation

[RECONCILIATION.json](RECONCILIATION.json) records352/364passed edges and312/324distinct physical tests over eight properties,197positive/167negative edges. Twenty-nine passed edges have original committed-clean native receipts; five executed on the current reviewed code revision. The remaining347passed edges retain their original valid observations. These are overlapping provenance groups, not extra tests.

| Property | Passed | Unresolved |
|---|---:|---:|
| I16-01.P1 | 4 | 0 |
| I16-02.P1 | 16 | 0 |
| I16-03.P1 | 100 | 1 |
| I16-04.P1 | 125 | 0 |
| I16-05.P1 | 54 | 0 |
| I16-06.P1 | 20 | 0 |
| I16-07.P1 | 17 | 11 |
| I16-08.P1 | 16 | 0 |

Valid earlier main-flow, acoustic, ASR, textual LLM/review, source-import, arithmetic, native storage and media observations are retained. This operation made zero model calls. A new review stage, documentation commit or broader glob hash does not invalidate unchanged behavior. Fresh source startup is required because shipped web source changed; it is observed by the new real source fixture. No failed observation was relabelled green.

All11main routes retain their original actual browser success/failure/recovery evidence. This verification adds the three Settings scenarios and a fresh source gate. Current media comprises144pictures,22silent browser videos and15exact WAVs. [Complete media index](../iteration-16-release-20261021/EVIDENCE.md) and [native metadata](../iteration-16-release-20261021/MEDIA.json) preserve exact original paths and constructed/actual boundaries. No new audio is necessary for a UI-only repair; previous generated/playback WAVs remain unchanged. The new actual custom-profile page was visually inspected.

Stable447static and5533structural property assertions, graph/discovery and strict OpenSpec pass. The structural graph has665requirements,680properties and3979edges, including1895original blocked and14planned entries; those are not runtime passes. Go source/toolchain did not change, so the valid pinned Go vet/gofmt evidence is retained. The real source build executes the production locked web build. The initial registration errors—missing shared-test scenario reason, obsolete discovery identity and omitted unavailable-index dispositions—were repaired as metadata errors; the original failures remain retained.

## Unresolved external/model observations

1. **Eleven actual amd64checks remain blocked.** The pinned PostgreSQLimage cannot be acquired through Docker Desktop's unreachable registry proxy. The actual failed portable receipt remains `data/iteration16/portable-b6e8e70.json`; pending tests cover startup/architecture/rejection/synthesis, cross-architecture restore/collision, saved Library/result/WAV, restart and zero new inference. Docker's supported load route was investigated as an alternative transport ([official load documentation](https://docs.docker.com/reference/cli/docker/image/load/)); no reconstructed digest, image alias or different database image was used to fabricate qualification. The host can reach Docker Hub metadata, which does not establish daemon pull success. Permission to repair/restart Docker remains unanswered because restart may interrupt three unrelated kind containers. No global Docker/proxy/VPNchange occurred.
2. **The actual no-pause auditory negative remains failed.** Local Qwen3Bfloat32/SDPAwrongly reports a2000ms pause in the clean2.1second recording. Original raw context/audio/response/native/Lab evidence remains in `data/iteration16/native/tangerine-diagnostic-abf0cb427beb`; the successful pause-present positive remains separate. The model is not contrast-qualified. The alternate larger-local-model/download or unbilled GeminiFreesetup question remains unanswered. No new model download, account, hosted call, purchase, credit or overage occurred. The required negative was not removed or weakened.

The two questions concern protected host action/resource authority, not a new product-policy approval. They were presented during this verification while independent repair continued. Their answers are required for those dependent operations. Full iteration execution/acceptance is not claimed from the four newly passed tests or the aggregate retained evidence. Canonical I16.06–.08/R4/R5/R12/R20/V2remain open; V1is repaired. No ACCEPTANCE artifact or archive is issued.

Original122categories/recipes,42formulas,11full-source identities and migrations are retained. The existing original-source/empirical/provider-eligibility boundaries in [ORIGINAL-SCOPE.md](../iteration-16-release-20261021/ORIGINAL-SCOPE.md) remain; source mechanisms are not complete unavailable-source bytes. Independently generated ordinary exercises retain their earlier successful actual local-model cycle and remain independent of optional corpus/diagnostic completion.

Only owned disposable test stacks were removed. The temporary network bridge and its verified host agent were stopped after observations; original kind-cloud-provider, kind-registry-mirror and desktop-control-plane remain running. Native receipts, media, private volumes, models and canonical user work remain preserved. Cleanup is recorded in `data/iteration16/verify-transport-cleanup.json`.

The sole task list remains `openspec/changes/implement-teacher-error-trainer/tasks.md`. Continue the protected/resource-dependent work when its explicit answer arrives, preserve valid greens, rerun the changed/failed cases and invalidated gates, then reconcile the entire selected iteration. Only an actually green complete result can close full release acceptance.

New screenshot: [Saved custom audio profile](/Users/jekamas/projects/0xatelerix/_worktrees/tangerine_iteration16_20261021/data/iteration16/custom-audio-profile/run-f0551a07c5/test_custom_profile_positive.png).

New silent Settings video: [Open recording](/Users/jekamas/projects/0xatelerix/_worktrees/tangerine_iteration16_20261021/data/iteration16/custom-audio-profile/run-f0551a07c5/videos/page@5864b61ddea9a3967149ccd66440f82a.webm).
