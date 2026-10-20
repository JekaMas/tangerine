# Iteration 9 verification and repair

Baseline:6396f71. This is the implementing agent's source/contract review and native counterexample verification, not an independent model/human review. Only Listening and answer persistence is accepted by this increment; later semantic evaluation and the three recorded I8 controller findings remain outside it. No product decision is needed.

## Findings and disposition

**R1 — P2, demonstrated defect: concurrent submission misrepresented the local draft as saved.** A second browser HTTP writer submitted a different answer at revision0. The first window tried to save, received412, then refreshed. The actual DOM displayed its unsent text in the disabled answer field beneath “Answer submitted and saved.” The baseline driver failed with actual `Unsubmitted local text 🟠`, expected `Submitted in another window. Ошибка.`. The original48case acceptance did not cover that state. Baseline failure and final DOM are retained under ignored data/iteration9/browser/run-e3c18eeb24f4, and the decisive trace is promoted to this change's evidence.

Repair: the submitted answer and language always come from the durable readback. A different dirty local response and its language appear in a separate, clearly unsubmitted, copyable recovery area. Repeated Refresh retains that area and cannot replace the frozen answer. The existing editable-draft conflict/retry path is preserved. Two concrete real-browser DAG cases cover actual submitted display/reopen and refusal to relabel/erase unsent Russian text. The ten-scenario browser repair run passed; committed-clean acceptance is recorded below after execution.

**R2 — code responsibility repair.** The HTTP audio adapter directly queried the catalogue; attempt persistence also contained effective configuration selection, while the page mixed rendering and the complete session controller. Move source-rights/asset loading into attempt_media.go, configuration snapshot selection into attempt_configuration.go, and browser request/retry/local-draft transitions into useListening.js. HTTP retains status/headers/range delivery; page.js retains presentation. No new service, queue, runtime abstraction, repeated stored-data validation or hash audit is introduced. Existing frozen settings, transport policy and normal draft behavior are preserved.

**R3 — missing explicit media-state evidence, now materialized.** The earlier native/browser cases did not directly demonstrate rights-restricted versus retired/quarantined access on an already-started attempt. Two native cases now independently expect exact previous audio for quarantine/retirement,403RIGHTS_BLOCKED with no private key for a rights restriction, and continued exact draft persistence. These focus on existing promised behavior, not a new product gate. Both and the three affected range/core/optional-configuration cases passed with real PostgreSQL/MinIO.

## Full property review

| Properties | Inspected owner and conclusion |
| --- | --- |
| I9-01 | New-content admission/codepoint limit and original decoded UTF-8 storage; English/Russian, combining marks, whitespace and full non-BMP capacity retain literal tests. |
| I9-02 | Closed attempt/start projections and saved envelope; no transcript/key/provider/lease disclosure or fabricated score. |
| I9-03 | Publication is atomic in the existing render finalizer, retains source key, uses actual immutable document identity and reuses published mapping. No change to this owner; retain five unchanged original finalization observations. |
| I9-04 | Entry freezes configuration/bundle/effective bindings; only core checking readiness is required. Selection moved without policy/dispatch changes; optional/core negative native cases passed. |
| I9-05 | Operation replay precedes mutable head checks; row/CAS lock, exact content/hash/language and stale/conflicting effects are tested through real storage. |
| I9-06 | Submission freezes before evaluation; empty and nonempty answers retain original versions. R1 corrects browser interpretation of remote submission without changing storage transitions. |
| I9-07 | Server receive time, exact attempt/audio/sample scope, stable page/sequence dedup and delayed unique arrivals. No new ordering gate or inferred hearing/ability. |
| I9-08 | Same-origin private proxy, body capacity, safe error/revision behavior and frozen range/ETag delivery. R2/R3 separate media ownership and add concrete source-state observations. |
| I9-09 | Stable creation-time/ID cursor, reopened pool and exact history/readback; no inference or hidden transcript in history. |
| I9-10 | Every directed draft/submit/stale sequence prefix has independent expected revisions/state; concurrent same-revision writers have exactly one winner; immutable predecessor survives. These are finite native traces, not an exhaustive scheduler proof. |
| I9-11 | Actual Chrome/Next/API/DB/media, played audio, exact bilingual draft reload, private-content exclusion and draft conflict recovery. No DOM/network owner substitution. |
| I9-12 | Actual save/submit/reopen and stopped/restarted DB/media; R1 adds separate frozen-answer/unsent-buffer observations and repeated refresh. |

## Evidence and invalidation

The source/test/contract changes invalidate current I9 acceptance. The iteration grows from48 to52implemented cases across the same12properties,26positive/26negative. Exact literal plans, fixtures, source owners and dependencies are wired through the existing verification.json/discovery.json/property-test-sets. No I9 placeholder supplies acceptance. Directly affected native5/browser10 observations ran first. A single complete52case committed-clean selection supplies final acceptance after the stable source commit.

Original render finalization, speech acknowledgement/publication/key, its five literal test bodies and selected command are unchanged; retain the original clean526ee75 receipt and explicit proof boundaries, without relabelling them current executions. The graph's conservative broad dependencies are reconciled by actual owner reachability. No original core category, recipe, formula, source registry, migration, provider dispatch or AI prompt changes. Go vet/gofmt, locked production web build, strict OpenSpec, DAG/discovery and static/preservation checks are current/unchanged-input observations, not whole-product readiness.

Only real test-owned PostgreSQL/MinIO and the existing installed Chrome/Playwright are used. Constructed admitted key/PCM/profile inputs and the original five dependency transport fixtures do not establish upstream LLM/synthesis quality or hosted entitlement. No live model/provider call, credit/overage/purchase, borrowed auth, installation, external publication or agent delegation occurred. Existing model/user data and canonical unrelated GAPS.md are preserved.

## Acceptance checkpoint

Pending the stable source commit and complete committed-clean iteration run; this line cannot be used as green acceptance. The canonical tasks.md owns completion state. Large private originals and full command outputs remain under ignored data/iteration9-verify-20261020 and data/iteration9/browser.
