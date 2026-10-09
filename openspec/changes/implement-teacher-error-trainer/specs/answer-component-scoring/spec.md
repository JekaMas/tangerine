# Independent correction and optional explanation

## ADDED Requirements

### Requirement: ANS-01 Assess correction and explanation independently

The system SHALL assess each supplied correction and explanation independently in the existing mapper call. Explanation SHALL always be optional and SHALL be assessed when supplied regardless of task_components.explanation. A false or omitted rationale SHALL NOT erase supported correction or detection credit. Actual incompatible endorsed repairs SHALL NOT be resolved by selecting the highest-credit alternative. Owning contract: specification/v2/docs/answer-component-scoring.md.

#### Scenario: ANS-01 Correct repair with false reason

- **GIVEN** the only error is present-context She work here and the answer says Use works because third-person agreement applies and every English verb ends in s
- **WHEN** the mapper assesses the two components
- **THEN** correction credit is 1, detection TP is 1 and the default primary grade is 100; the explanation records the supported agreement fact and unsupported universal rule, earns explanation credit 0 and receives feedback on both

#### Scenario: ANS-01 Explanation omitted or flag false

- **GIVEN** a correct Use works answer without explanation, or with a correct agreement explanation while task_components.explanation=false
- **WHEN** grading runs
- **THEN** the omitted explanation has supplied=false and optional score N/A without a penalty; the supplied eligible correct explanation is assessed and scores 100; both primary grades remain 100

### Requirement: ANS-02 Project additional assertions into their actual component

Each additional substantive assertion SHALL retain exact original codepoint span/text, supported/unsupported/unknown judgment and contextual reason in its component's typed additional_assertions. Existing proposition references plus these assertions SHALL cover substantive component content without fabricated proposition IDs. An unsupported assertion SHALL activate the existing forbidden-condition zero-credit rule for that component alone; an unknown SHALL leave only its dependent credit unavailable. A distinct additional heard-error assertion SHALL remain its own detection claim.

#### Scenario: ANS-02 True extra explanation detail

- **GIVEN** Use works because she is singular and the intended tense is present with an eligible agreement rubric
- **WHEN** the mapper supports the actual additional present-tense assertion
- **THEN** its span equals the frozen substring, its contextual reason is retained, correction and explanation each retain credit 1 and no new rubric ID or detection FP is invented

#### Scenario: ANS-02 False repair versus false rationale

- **GIVEN** the fixed present-context error and either Use worked or Use works because every English verb ends in s
- **WHEN** the unsupported assertion is projected
- **THEN** the first answer has correction credit 0 and primary grade 60; the second keeps correction credit 1 and primary grade 100 with explanation credit 0; unsupported component labels or fabricated spans are repaired as output defects

### Requirement: ANS-03 Keep optional uncertainty nonblocking

Issues SHALL declare affected_components and the server SHALL derive blocks_final_score from actual primary dependencies. Unknown supplied eligible explanation SHALL retain actual GE/TE/EA, use null EK/EQ and unavailable dependent explanation metrics. The primary result SHALL remain complete when its only unresolved issue affects explanation; unknown explanation SHALL NOT be dropped from EA or converted into a primary unresolved claim.

#### Scenario: ANS-03 Unknown optional reason

- **GIVEN** G=GC=TP=1 and correction credit 1 with a supplied eligible explanation whose extra rule remains unknown
- **WHEN** scoring persists the result
- **THEN** primary grade is 100, result is complete, GE=TE=EA=1, EK/EQ are null and the explanation issue has affected_components=[explanation] and blocks_final_score=false

#### Scenario: ANS-03 Incompatible endorsed corrections

- **GIVEN** Use works and use worked are both endorsed without retraction for the same fixed present context
- **WHEN** genuine correction interpretation remains unresolved after LLM reconsideration
- **THEN** selected correction/primary composite remain provisional; an explanation-only issue is not used to conceal that primary uncertainty or select the favorable repair

### Requirement: ANS-04 Separate primary and optional explanation populations

New ordinary attempts SHALL freeze answer-components-v2 before answering. The primary composite SHALL use enabled detection/classification/correction with weights 45/15/30 and original metric inputs. Optional explanation score SHALL be 100*EQ/EA over supplied eligible explanations and N/A when EA=0. Original explanation coverage/recall SHALL remain descriptive metrics. Pooling SHALL use actual raw statistics within the same frozen policy and population, preserving unknowns and all 42 formula definitions.

#### Scenario: ANS-04 Missing optional explanation in pooled results

- **GIVEN** two one-error attempts each with correct detection/correction, one with correct eligible explanation and one without
- **WHEN** same-policy raw statistics are pooled
- **THEN** G=GC=TP=2, CQ=2, GE=TE=2, EA=EQ=1; primary grade is 100, optional explanation score is 100, coverage and graded recall are 1/2 and do not penalize primary grade

#### Scenario: ANS-04 Partial repair with true reason

- **GIVEN** G=GC=TP=1, a repair satisfies one of two required propositions without forbidden assertions, and a supplied explanation is fully correct
- **WHEN** the exact server scorer projects credit
- **THEN** CQ=1/2 and default primary grade is 80; explanation score is 100 and cannot increase correction credit; no LLM numeric grade or legacy explanation weight is adopted

### Requirement: ANS-05 Preserve component scope in feedback and reconsideration

Feedback, optional mapping audit, consolidation, case review, adjudication and explicit result revisions SHALL preserve correction/explanation separation. Every supplied explanation SHALL receive supported/unsupported/unknown findings and contextual feedback even if ineligible for a formal rubric score. Omission SHALL receive no reprimand. Feedback failure SHALL preserve stored scores. A reason-only revision SHALL preserve supported primary statistics and heard audio unless actual primary evidence changes. No human review or new mandatory LLM stage SHALL be added.

#### Scenario: ANS-05 Explanation revision

- **GIVEN** a saved primary grade 100 and wrong explanation with the original audio/key/answer identities
- **WHEN** explicit LLM reconsideration resolves only the explanation differently using supported evidence
- **THEN** a versioned explanation/feedback revision records the changed assessment and provenance while primary statistics and heard audio remain identical; a required actual rubric repair still uses key versioning

#### Scenario: ANS-05 Feedback unavailable

- **GIVEN** a saved primary grade 100, explanation score 0 and retained false-rule finding
- **WHEN** the feedback provider times out
- **THEN** both scores and semantic findings remain saved with commentary unavailable and explicit feedback retry; omission or provider failure does not become a scoring penalty or human queue

### Requirement: ANS-06 Freeze policy and Lab expectations

Attempt, scoring-input, score-result, cache and Lab identities SHALL retain the exact scoring policy. Existing historical results SHALL NOT be automatically regraded. Current Lab reference packets SHALL independently assert correction and explanation presence/credit/uncertainty, exact primary arithmetic and optional populations. Semantic assertion judgments SHALL remain model outputs; native arithmetic SHALL remain server-owned. Unexecuted plans SHALL NOT count as provider or application evidence.

#### Scenario: ANS-06 Frozen old result

- **GIVEN** an existing result bound to an explicitly frozen legacy four-component policy
- **WHEN** answer-components-v2 is activated for new attempts
- **THEN** the historical result retains its original grade/policy and a new ordinary attempt uses the new independent-component policy; comparisons label the distinct populations

#### Scenario: ANS-06 Explanation unknown in Lab

- **GIVEN** a current reference packet expects correct repair, primary 100 and unknown supplied explanation with EA=1
- **WHEN** a candidate drops the unknown explanation from EA or returns zero primary credit
- **THEN** the independent Lab oracle records the component/population mismatch; static schema receipts cannot report the candidate as a successful model observation

### Requirement: ANS-07 Use one mutation and source-effect contract

Active mutation documentation SHALL use generation-input.mutation_recipes and the typed mutation-manifest hash/replay projection. Source revoke effects SHALL save actual notice/status and selected-source provenance without a permission-epoch service. Independent authored exercises SHALL remain usable. Every original source scope and mutation recipe SHALL be retained.

#### Scenario: ANS-07 Typed manifest projection

- **GIVEN** saved clean She works here, mutated She work here and the selected agreement recipe
- **WHEN** mutation provenance is stored
- **THEN** the manifest references the actual candidate assets/JCS hashes, original and changed text and selected recipe; the old custom provenance DTO is not substituted

#### Scenario: ANS-07 Source notice and independent exercise

- **GIVEN** a source revoke notice and a generated exercise without that source dependency
- **WHEN** revoke saves the notice
- **THEN** selected-source status/provenance reflect the notice, no permission epoch is required and the independent generated exercise remains usable without interpreting the source as unrestricted

### Requirement: ANS-08 Allow explicit recovery with bounded automatic requests

Generation/rendering SHALL impose no candidate-lifetime three-attempt ceiling on manual retry. Each explicit retry SHALL preserve original saved content/bindings and previous receipts, retaining existing per-operation deadline, idempotency and bounded automatic requests. Linguistic audit SHALL permit the shared single same-profile output repair within its logical stage budget, with original malformed output retained and no fabricated observations.

#### Scenario: ANS-08 Fourth explicit render attempt

- **GIVEN** three manually requested failed renders during an outage and an unchanged saved candidate after service recovery
- **WHEN** the user explicitly retries a fourth time
- **THEN** a fourth recorded foreground render is allowed with frozen content/bindings and original per-operation bounds; no automatic indefinite loop occurs

#### Scenario: ANS-08 One linguistic output repair

- **GIVEN** truncated linguistic-audit JSON within the stage budget
- **WHEN** the adapter invokes one same-profile repair
- **THEN** one complete supported object can be accepted with the original failed output retained; a second repair loop or fabricated missing observation is not accepted

### Requirement: ANS-09 Support LLM-key-only local first use

Local speech SHALL be the default first-use route, with explicit model setup/progress/retry if weights are absent. External speech SHALL remain a supported explicit choice using its supplied key. Generate SHALL freeze the choice. Startup SHALL NOT silently download weights or switch paid/local bindings. Native synthesis failure SHALL NOT be represented as stored successful audio.

#### Scenario: ANS-09 Local first use

- **GIVEN** only a configured LLM key and missing Kokoro local assets
- **WHEN** the user selects the visible model-setup action and then Generate after successful setup
- **THEN** the local profile is frozen, speech requires no Azure key and ordinary exercise generation proceeds with actual stored audio

#### Scenario: ANS-09 Missing local assets or service key

- **GIVEN** local assets remain absent or external speech was explicitly selected without its key
- **WHEN** rendering is requested
- **THEN** the selected route exposes its actual setup/configuration failure and explicit continuation; it cannot silently change providers or report a successful audio asset
