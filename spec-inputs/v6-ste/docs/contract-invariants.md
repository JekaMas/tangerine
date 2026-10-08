# Cross-field rules

A valid schema is necessary but insufficient. The server must apply these rules after structural validation.
The server must reject a violated rule before publication or scoring.
Do not repair a violated rule through a guessed value.

## Identity and text

Each ID must be unique in its declared scope.
Each reference must exist in the exact tenant, case, and version.
Taxonomy IDs must exist in the frozen registry. Accepted category sets must include the primary category where the policy requires it.
Do not download schema references from the network during validation.

A text span uses the half-open interval `[start_cp,end_cp)`.
Offsets count Unicode codepoints, not bytes or UTF-16 units.
The source text slice must equal `exact_text`. Do not normalize teacher text before this comparison.
In browser code, count codepoints rather than JavaScript string units.

Each extraction clause must have a unique stable ID after server assignment.
A correction or rationale span must come from the frozen answer. It cannot come from the answer key.
Keep unparsed substantive spans unresolved. They must not disappear from scoring coverage.

## Audio and targets

Every audio interval must satisfy `0 <= start_ms < end_ms <= duration_ms`.
A textual insertion can have an empty span. Its audible context still requires a nonempty audio interval.
Every target must refer to its reviewed utterance and occurrence.
Secondary labels must not create extra detection units.

A correction-eligible true unit requires a correction option with required propositions.
An explanation-eligible true unit requires rationale propositions.
Permitted or excluded units must not add true-error denominators.
Keep the expected judgment separate from dialect and naturalness labels.

Canonical, intended, and observed IPA must remain separate.
An unknown observed phone remains null. Each observation must refer to actual final-audio evidence.
Requested accent metadata cannot satisfy acoustic verification.

Typed render operations must have the payload required by their operator.
A phoneme operation requires the target text and IPA.
A pause operation requires a duration. Arbitrary XML and remote audio references are forbidden.
Archival origin labels do not enable active fixture or human-recording providers.

## Approval and provenance

A published case requires the full publication procedure and two independent approvals.
Each approval must refer to the exact final audio hash and case version.
The server loads approvals from authenticated actions. Model output cannot create a human identity or permission.
A fixture origin can never approve publication.

Hashes identify stored immutable byte payloads. A changed serialization creates different bytes and a different hash.
Exclude a self-reference hash field from the separately stored payload that it identifies.
Do not assume cross-language canonical JSON without an explicit canonicalization contract.

## Mapping

Every extracted claim requires one decision. Repeated or unknown claim IDs fail validation.
Every unit, category, correction option, proposition, and evidence ID must belong to its permitted set.
An existing evidence ID is insufficient if it belongs to another unit or audio version.
The server must examine evidence subjects and provenance, not only global set membership.

A satisfied proposition cannot also be a violated proposition.
The correction verdict must agree with the proposition-derived credit.
A new plausible correction requires review. The model cannot edit the permitted alternatives.

A duplicate must refer to an earlier compatible nonduplicate claim. Cycles are forbidden.
Contradictory stance or repairs require review. Remaining collisions must not use last-write-wins behavior.
A missing supplied correction or explanation has credit zero. The model cannot supply a numeric grade.

`matched_error` and `wrong_acceptance` require a true unit.
`confirmed_acceptable` requires a designated permitted unit.
A mapped `false_positive` requires a designated permitted unit.
An off-key false assertion requires evidence review before scoring.

## Score and provider boundaries

Freeze the answer before a provider request. Freeze the case and component policy before answer entry.
A refusal, truncation, or schema failure must not produce a completed score.
The backend must preserve `TP+FN=G`. It must preserve domain totals and the formulas in the metric registry.
N/A requires null and a reason. No hidden substitution is permitted.

The provider adapter must use its supported strict-schema subset.
Do not silently erase unsupported constraints from the application contract.
If the wire projection fails conformance, block that profile and request an adapter decision.

The reference validators implement only the checks that their code contains.
Their current code does not replace application authorization or all rules in this document.
The open-decision register identifies the remaining reference and contract gaps.
