# Complete authored-flow and Lab contracts

## ADDED Requirements

### Requirement: CMP-01 Explicit simple preparation expansion

The system SHALL expand ordinary inputs according to generation-contract-details.md and the saved/default preparation configuration, preserving optional level, explicit family/count choices and advanced controls. It SHALL save the actual synthesis and generation bindings separately, cycle registered voices explicitly and freeze preparation/attempt settings. No approximate word/pace requirement SHALL become an undisclosed hard gate.

#### Scenario: CMP-01 Defaults and shared voices are visible

- **GIVEN** three speakers, local speech and no advanced options
- **WHEN** the ordinary blueprint expands
- **THEN** the registered locale voices cycle across three roles, unset level/L1/accent remain null and detection/correction task defaults are saved

#### Scenario: CMP-01 Conflicting explicit controls survive failure

- **GIVEN** explicit family/profile/count choices cannot coexist with the advanced controls
- **WHEN** preparation reports the conflict
- **THEN** it retains those choices and the saved baseline instead of deleting a family or silently substituting a voice/backend

### Requirement: CMP-02 Exact replayable mutation provenance

The system SHALL save mutation-manifest.schema.json with exact candidate identities, actual recipe records/hash, canonical-coordinate edits, surface-coordinate key scopes and typed acoustic intents. Replaying the edits SHALL reconstruct the actual surface text. Shared edits SHALL preserve independent event identity, without offset drift or double-counting alternatives.

#### Scenario: CMP-02 Insertions deletions and shared edits replay

- **GIVEN** a Unicode baseline with boundary insertions, a deletion and two independent obligations sharing one replacement
- **WHEN** the mutation manifest is saved
- **THEN** canonical-coordinate replay yields the exact surface strings and the key uses the resulting surface scopes with the original event identities

#### Scenario: CMP-02 An unattributed text change cannot become a complete key

- **GIVEN** a mutation output changes an unrelated slice or rewrites the ordered canonical baseline
- **WHEN** ordinary output repair cannot resolve the mismatch
- **THEN** the operation retains the clean checkpoint and reports failed mutation without manufacturing a replay proof or successful key

### Requirement: CMP-03 Complete authored key projection

The system SHALL fill every additional ground-truth field using the actual mutation/render provenance rules in generation-contract-details.md, keeping unknown acoustic observations null, ordinary difficulty unrated and optional review decisions empty. GENERATED-EXERCISE SHALL resolve as authored content separately from original acquired releases. Actual native/local recording imports SHALL retain their source origin and conversion provenance rather than be mislabeled synthetic. Difficulty SHALL use the persisted easy/medium/hard/expert/unrated labels with the existing Wilson thresholds.

#### Scenario: CMP-03 Candidate key uses actual turn intervals

- **GIVEN** actual assembled audio but no word timing or acoustic review
- **WHEN** planned units become the ordinary answer key
- **THEN** shared content is preserved, actual containing-turn intervals/provenance are assigned and observed IPA/accent/difficulty are not fabricated

#### Scenario: CMP-03 Empty keys and missing populations remain honest

- **GIVEN** an explicit zero-mutation exercise or inadequate teacher difficulty population
- **WHEN** the case and result are saved
- **THEN** playable use is allowed while absent scoring populations remain N/A and difficulty remains unrated

### Requirement: CMP-04 Typed frozen Lab datasets and semantic judges

The system SHALL use the dataset, pipeline-input, frozen configuration and judge policy/input/output contracts in llm-lab-contract-details.md. Every case/variant/repetition tuple SHALL remain accounted, with exact reference origin and actual judge receipts. The dedicated semantic judge SHALL return supported/unsupported/unknown propositions rather than grades; candidate-owned labels SHALL never become independent reference accuracy.

#### Scenario: CMP-04 Fixed inputs and a diagnostic judge survive settings changes

- **GIVEN** a saved answer-pipeline dataset, configuration snapshot and judge policy
- **WHEN** workspace settings change before the explicit comparison
- **THEN** execution uses the saved variant configuration and exact reference/key/answer, retaining every actual judge decision and receipt

#### Scenario: CMP-04 Failed rows and circular references remain visible

- **GIVEN** cancellation or a candidate-created reference key
- **WHEN** the comparison reports results
- **THEN** all planned tuples retain their actual status and candidate-derived labels are reported as self-consistency without independent-accuracy claims

### Requirement: CMP-05 Complete context and unbiased Lab arithmetic

The system SHALL retain actual candidate/extraction/scoring/rubric inputs and independent mapping-audit disclosure. Lab aggregates SHALL use unreduced sufficient statistics, known subtotals for unknown totals, explicit common paired populations and the per-metric aggregation rules in llm-lab-contract-details.md. All original42formulas SHALL remain unchanged.

#### Scenario: CMP-05 Pooled counts and actual inputs are inspectable

- **GIVEN** unequal per-case populations and a saved extraction/native score
- **WHEN** context and aggregate diagnostics are inspected
- **THEN** snapshots reference the actual inputs and pooled detection/category rates recompute from raw counts without averaging reduced per-case ratios

#### Scenario: CMP-05 Missing usage and audit leakage are handled correctly

- **GIVEN** a missing cost/token observation or a context policy including the first mapper's decisions in independent audit
- **WHEN** diagnostics or context are prepared
- **THEN** the unknown total retains its known subtotal and the audit context excludes the first mapper's decisions rather than claiming independence

### Requirement: CMP-06 Logical deadlines and optional quality reports

The system SHALL apply stage caps across all attempts/fallback/repair, preserve the existing persistence reserve and skip Lab export when no budget remains. Audio peak/loudness/unplanned-silence and unavailable acoustic diagnostics SHALL remain warnings under audio-methods.md; malformed or all-silent bytes SHALL not produce a playable case. Codec changes SHALL preserve new byte/version identity without a required separate review.

#### Scenario: CMP-06 Repairs and export share the original budget

- **GIVEN** a logical stage has spent most of its cap and the foreground deadline is near
- **WHEN** a repair or diagnostic export is considered
- **THEN** it uses only the remaining original budget and persistence reserve without resetting the cap or delaying the ordinary result for Lab

#### Scenario: CMP-06 Acoustic warnings do not become approval gates

- **GIVEN** playable non-silent audio with a loudness or unplanned-silence warning
- **WHEN** ordinary publication is selected
- **THEN** use remains available with that warning and no peer/case-review prerequisite, while malformed or all-silent output remains failed
