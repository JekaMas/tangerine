# Iteration 11 verification and repair

Iteration 11, **Scoring, results and recommendations**, passes on committed-clean source `010a4d5b217059e5eb676f329b7e1726e2d3c39c`. All seven finding groups below are repaired. No in-scope finding remains. This report supersedes the earlier iteration-11 acceptance conclusion while retaining its original receipts and proof boundaries.

The selected DAG reconciles **322/322 cases: 161 positive and 161 negative**, with no failure, skip or missing observation. The complete iteration selection ran with `--require-clean`; unchanged dependency evidence retains its actual original revision.

| Selection | Passed | Evidence origin |
| --- | ---: | --- |
| All ten I11 properties | 138 | Fresh committed-clean source `010a4d5` |
| Affected interpretation dependencies | 112 | Fresh committed-clean source `010a4d5` |
| Invalidated provider cases | 4 | Fresh committed-clean source `010a4d5` |
| Unchanged provider cases | 68 | Original committed-clean `2b74329` passes; dependency fingerprints reconciled on `010a4d5` |

The 138 owned cases comprise 98 Go, 26 native PostgreSQL/MinIO, six browser and eight actual local feedback cases. Sixteen positive/negative regressions were added to the original 122-case iteration. The provider package also executed its 96 physical tests successfully; unselected or overlapping physical tests do not inflate the 322 logical-case total. [ACCEPTANCE.json](ACCEPTANCE.json) records each selected case, independent test identity, polarity, original source revision, dependency fingerprint and receipt.

## Findings and repairs

1. **Cohorts lost their frozen scoring policy.** Pooling replaced every policy with `answer-components-v2`, changing historical arithmetic and allowing unlike policies to blend. The pure pooling owner now preserves its input policy and rejects a mixed-policy cohort at admission. Empty pooling keeps the ordinary default. A legacy literal fixture independently expects `1114/21`, displayed as `53.0`; existing arithmetic expectations were not relaxed.
2. **Pooling lost domain-scoped uncertainty.** A grammar-only unresolved event could disappear or incorrectly make unrelated lexical results uncertain. Pooling now unions the actual domain masks, using the same global fallback as single-attempt scoring only when an input lacks a domain mask. The 42 formula identities and weights remain unchanged.
3. **Feedback skipped off-key false positives and overconstrained combined comments.** Off-key claims have no answer-key unit ID. Existing output admission now checks their actual source decision/claim IDs and accepts a factual combined comment covering a false positive and its supplied correction or explanation. A separate duplicate card is unnecessary. Native request/output cases observe both accepted and rejected behavior.
4. **Actual zero-TP feedback omitted practice recommendations.** The existing feedback prompt and hint now explicitly request practice even when every true mistake was missed. Actual local cases independently require useful nonempty practice alongside exact unchanged scores and grounded findings.
5. **Harmless repeated model metadata was rejected.** The existing opt-in model-stage JSON admission now normalizes identical duplicate fields once. Conflicting values remain ambiguous and are rejected. Standalone strict import projection remains unchanged; no saved-data revalidation was added. Native cases cover both outcomes and retained numerical results.
6. **Empty visible output lost stage-specific repair guidance.** Provider execution formerly skipped the stage diagnostic when no rejected candidate existed. It now forwards that existing guidance through the same bounded repair, including when the first visible response is empty. Native cases demonstrate recovery and persistent emptiness after exactly two requests; the saved score survives feedback failure. Deadlines and retry counts are unchanged, and hidden reasoning is never substituted for an answer.
7. **Actual feedback confused a proposed correction with the recording.** A prior response evaluated the grammaticality of the written command “Use coffee” rather than the proposed replacement of recorded “café.” The feedback input now explicitly pairs endorsed listener text with consolidated correction/explanation judgments and reasons. Withdrawn claims stay excluded. The prompt distinguishes the recording from listener proposals and asks for concise source-faithful explanations. Pure projection and native wire cases protect the input; independent literal references and developer source comparison cover actual feedback meaning. No extra model judge, human-review product step or numeric heuristic was introduced.

## Layer and responsibility review

`internal/scoring` owns exact counting, ratios, domain populations and pooling; it imports no application, provider, HTTP or storage layer. Application projection converts already admitted semantic judgments into numeric input. Persistence saves immutable numerical results before optional feedback and preserves existing checkpoint/lease ownership. Feedback preparation projects source roles; feedback admission checks the returned source references. The provider layer owns JSON admission, transport and the existing bounded repair. HTTP and browser presentation were unchanged by this verification.

The review traced formulas, absent/unknown component populations, category credit, false positives and controls, consolidation/duplicates, exact rounding, per-domain behavior, optional explanations, immutable historical results, score-before-feedback persistence, feedback-only retry, recovery, DB-only readback, native wire/context capture and user-visible browser results. No new service, auth, queue, repeated schema/hash check or review ceremony was added.

## Actual local AI evidence

Eight feedback cases used the existing local Ollama `gpt-oss:20b`: accepted correction, accepted optional reason, rejected correction, missed mistake, Russian feedback, false reason with a valid correction, off-key finding and off-key proposed correction. All retained their exact independent grade expectations. The saved comments support their independent source references, including the unnecessary meaning-changing coffee proposal and the rejected universal verb rule. [SEMANTIC-REVIEW.json](SEMANTIC-REVIEW.json) records the actual comments and source comparison; this is developer self-review, not external linguistic certification.

The final accepted run reconciles **10 actual local dispatches, 10 native receipts, 10 contexts and 10 MLflow spans across eight operations**, including bounded repairs. Prompt/context/model bindings, requests, visible outputs and failed variants remain under ignored `data/iteration11/`. Exports and MLflow span/identity readback agree with independently observed native dispatches. The compact acceptance ledger was also exported and read back with zero additional inference. [LOCAL-OBSERVATIONS.json](LOCAL-OBSERVATIONS.json) records the final links and counts.

Earlier failed candidates remain failed: `135ea38` passed 130/132, and `51f777c` passed 133/134. Their actual observations were retained/exported. Automated greens on `2b74329` did not close its demonstrated prose role defect; the source comparison and subsequent repair are recorded separately. `5326663` fixed the source role but was superseded by the final source-faithfulness wording refinement. No best-of output replaces a failed receipt.

Actual model inference in this verification is limited to feedback over constructed source-bound semantic judgments. Controlled responses exercise the real interpretation/controller/persistence owners; they do not establish general extraction-model accuracy. This acceptance makes no claim about hosted-account entitlement, universal linguistic quality, full empirical corpus acquisition or acoustic realization. **No paid credits, billed or hosted provider calls, installations, delegation, purchase or publication occurred.**

## Other checks and preservation

The stable source passed 372 artifact assertions, 4,647 property assertions, strict OpenSpec, graph and discovery validation. Those structural results do not replace behavior observations. The inventory accounts for 25 registered surfaces and 91 dependency paths with zero unresolved paths; planned surfaces remain labelled planned. Valid pinned Go vet/gofmt and the unchanged locked web build are retained rather than rerun after prompt-only or evidence changes.

All 122 taxonomy categories and recipes, 42 formula identities, 11 original source scopes and the recorded original migrations remain byte-identical. The canonical unrelated `GAPS.md` edit remains intact. [PRESERVATION.json](PRESERVATION.json) retains the exact source comparison. Known I8.R1–R3 remain outside this iteration and unchanged. The overall OpenSpec change stays active for its remaining iterations.

The final acceptance commit changes only this audit record and canonical task completion. It does not invalidate the committed-clean behavior receipts on `010a4d5`.
