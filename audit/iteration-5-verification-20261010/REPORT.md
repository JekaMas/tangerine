# Iteration5 verification and repair

All identified native defects and artifact drift are repaired. The own iteration5 selection passed48/48 cases on committed-clean8b00d79b8ea14b330fb839acd8bdd4adace18a04. Current native reconciliation covers380/380 cases,190 positive and190 negative:184 newly observed cases and196 unchanged retained cases. Full hosted iteration5 acceptance remains blocked by the actual provider boundary below; native fixtures do not establish it.

## Findings and repairs

| Finding | Trigger and consequence | Repair and observation |
| --- | --- | --- |
| P2: action replay follows current head | First canonical attempt fails; explicit Resume succeeds and clears the current failure. Replaying the first key panics because the failed-action branch reads that now-empty failure. Completed actions also return later heads. | Both terminal outcomes read the action’s saved immutable result_document_id. Ordinary preparation readback still selects the current head. The baseline panic is retained in replay-red.stdout. I5-12 adds two positive/two negative cases for fail/resume/replay, completed action/head advancement, changed-key request conflict and a genuinely missing saved result. No new consistency checks. |
| P2: unsupported speaker cap | The request schema permits positive counts, but expansion rejects4001 roles with128000 context tokens because it divides the token budget by a supposed32 wire bytes per role. That estimate does not define actual serialized context consumption. | Removed the invented expansion cap. The existing context assembly/dispatch owner still handles real capacity. The shared-voice positive case asserts all4001 roles and their cycling. The old owner produces INPUT_CAPACITY_EXCEEDED in cap-red.stdout; the repaired own selection passes the same discriminator. |
| Artifact drift | Developer guidance still requires a definition archive; the active design still describes removed byte/backup/migration/catalogue audits. | Corrected guidance/design to accepted-data reuse, single admission, actual backup writes and availability readiness. All122 categories/recipes,42 formulas and11 full-source scopes remain preserved. |
| Missing own selection receipt | The original44 I5 case rows passed within a broader failed selection; that is not an overall successful own iteration receipt. | Expanded to12 properties/48 cases and obtained i5-own-clean.json with overall passed and known clean Git provenance. |

The preparation owner, request expansion, output admission, frozen settings/bindings, shared InvokeLLM dispatch, checkpoint/failure transactions, immutable action results, explicit Resume, completed-child recovery, CAS/deadlines and private HTTP/CLI readback were inspected against their contracts. This is self-review and actual native execution, not an independent reviewer or a fresh semantic/IDE index claim. Mutation, audio, answer/scoring and the combined Generate UI/action remain their agreed subsequent iterations; canonical text is never put in the playable Library.

## Evidence and invalidation

SELECTION.json records actual changed production/assertion/fixture inputs. The48 I5 cases and136 predecessor cases were invalidated;196 predecessor observations remain exact current-fingerprint greens. Original receipts were not rewritten.

- i5-own-clean.json:48/48 passed, own selection, --require-clean,8b00d79.
- predecessors-clean.json: overall failed. Its three successful commands observed32 foundation,52 storage and16 storage regression cases. Lab startup reached zero cases because the preview occupied its fixed5001 port. The failed receipt remains failed; no unavailable Lab result contributes acceptance.
- lab-clean.json:36/36 passed, --require-clean, same revision, after pausing the existing preview Lab. That exact stopped container was restored afterwards with its original configuration/data. The100 earlier successful cases were not rerun.
- NATIVE-VERIFICATION.json and reconcile.py: all380 current native cases match their literal cases, source/fixture/dependency fingerprints, successful command exit and native test identity. --check revalidates the finite reconciliation without inference or behavior reruns.

Strict OpenSpec, requirement DAG/discovery and3669 static property/fixture/preservation assertions passed. Go vet/gofmt passed through the pinned Go1.26.5 Docker route. Structural checks are not behavioral or hosted quality evidence. The final documentation-only alignment receives strict OpenSpec validation; unchanged language and behavior greens are retained.

controlled-native-context.tar.gz includes only the nine current native state/document roots and116 referenced files. It retains actual constructed-fixture prompt/context/settings/model outputs, wire bytes and native receipts; stale prior-run files are excluded. It contains no separate schema/adapter implementation archive. Controlled model endpoints and tooling diagnostics are explicitly labelled and do not establish actual LLM linguistic quality, hosted entitlement or hosted MLflow observations.

## Actual external blocker

LIVE-READBACK.json records health200 with provider_configuration=missing_credentials, no provider connections, the ChatGPT model unselected and included_only billing flags false for purchased credits/overage/fallback. A fresh credential-free OIDC GET returns200 from the host. From the actual API container it times out after6 seconds awaiting headers. An egress network is attached; no global VPN/network settings or borrowed credentials were used.

Required unperformed evidence: a successful Tangerine-owned grant and confirmed purchased-credit exclusion; an actually returned selected model; real positive/negative clean generation and its prompt/context/native/MLflow quality observations. Unblock the API outbound HTTPS route, complete the app’s own sign-in and credit exclusion, select its returned model, then execute those cases. Another product approval, fixture response or native green cannot supply them. No hosted inference, purchase or billed provider call was made.

The canonical hosted/full-acceptance tasks remain unchecked. The verify skill states that only external blockers stop the work; the project AI-development policy requires actual selected observations for an AI completion claim. Consequently this report accepts the native implementation and records full iteration5 as blocked, not fully passed or archived. No additional product decision was introduced.

## Landing and resume

LANDING.json records the final canonical fast-forward and live dependency/Library readback. The protected unrelated GAPS.md and runtime configuration keep their original hashes. Preview services/data are preserved. Resume from the hosted blocker above; no native case needs rerunning unless its recorded semantic input changes.
