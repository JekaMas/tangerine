# Cross-field acceptance rules

Every schema in the semantic invariant registry receives the universal rules and its family rules.
A structural contradiction is a rejected payload. A genuine unresolved interpretation is a review outcome.
Do not repair contradictory fields or choose a favorable interpretation silently.

## Total correction tuple table

| supplied | option/propositions | status | unresolved_reason | Accepted meaning |
|---|---|---|---|---|
| false | null option, empty proposition sets | not_supplied | null | No teacher work, zero credit. |
| true | valid fixed option, all required satisfied, no forbidden assertion | accepted | null | Full correction credit. |
| true | valid option, strict nonempty subset satisfied, no forbidden assertion | partial | null | Exact proposition fraction. |
| true | valid option, no required satisfied or any forbidden assertion | rejected | null | Zero credit. |
| true | null option and no invented proposition IDs | unresolved | a permitted nonnull reason | Novel or unclear repair, no final aggregate. |

An explanation uses this table but always has option_id=null and uses unit-rationale propositions.
An unresolved explanation can preserve known proposition findings only if it does not falsely claim a final fraction.
A control or off-key FP can have supplied unnecessary correction text, but no true-unit option or proposition credit.
Its correction status is rejected and its credit is zero after the error assertion is itself resolved.
Ignore and retracted groups never supply scorer credit. Contradictory endorsed groups remain unresolved.
Any tuple outside these rules is invalid.

## Decision fields

matched_error requires an assert_error source stance and a true_error target.
confirmed_acceptable requires an assert_acceptable source stance and an acceptable target.
wrong_acceptance requires an assert_acceptable source stance and a true_error target.
false_positive requires an assert_error stance and an acceptable or resolved off-key target.
unresolved requires a score-relevant unresolved reason and cannot imply a final supported grade.
ignore requires a non-assertive or explicitly retracted source statement.
duplicate references only an earlier equivalent representative and changes no count twice.
The source stance is checked against extraction, not invented in a mapper note.

## Evidence types

mutation and render evidence can be requested or inferred. They cannot populate observed IPA.
Audio QC and numeric prosody require measured status, final audio subject, exact method version, finite value, and its registered unit.
Observed phone evidence requires actual human observation or an independently qualified phonetic method, not a reference accuracy score.
Human review requires a genuine person, qualification, independent phase records, and exact final-file hash.
Semantic mapping requires an actual provider or adjudication receipt and exact teacher-answer scope.
Score evidence requires a completed deterministic calculation against frozen accepted semantic inputs.
Every evidence parent must exist in the same case/version or be an explicit versioned source dependency.
The parent graph must be acyclic. A cycle cannot prove itself.

## Audio and render fields

Plain text has no phoneme, pause, or prosody payload.
Phoneme requires exact spelling, intended IPA, and the target opportunity ID.
Pause requires an integer duration in its allowed range and no text payload.
Prosody requires nonempty text and at least one nonnull control. Its contour positions are strictly increasing.
Voice and locale must match the frozen profile and speaker.
An accent_features constraint needs an observed feature set, not only a nationality label.
Speech_rate requires a wpm bound and a registered tokenization/interval method.
A requested acoustic property remains hard until explicitly changed in the blueprint before generation.
Final audio has one channel, 24,000 Hz, complete PCM16 WAV bytes, and its actual digest.
Every interval is nonnegative, ordered, within the actual sample count, and tied to the correct clock.
A human label has no invented numeric measurement. A non-observed numeric state has null numeric value.

## Review fields

A blind annotation references a real review context and final audio but no planned unit ID.
The disclosure time must follow the frozen blind submission time.
A final review decision references that disclosure, the original blind record, and matching key/audio digests.
An approval cannot precede the audio or content that it approves.
Duplicate-person aliases, author conflicts, prior-key exposure, and expired competence disqualify counted independence.
Adjudication does not replace the two final approvals.

## Attempt and result fields

started has submitted_at=null and no lease or final result.
saved has a frozen answer/digest and submitted_at, but no active lease.
evaluating has a current token, epoch, acquired deadline, and expiry.
completed requires a saved complete semantic result. Commentary can have its explicit fallback or unavailable status.
review_required has explicit issues and null final counts, ratios, and composite.
evaluation_failed has a technical failure receipt and no invented result.
A complete ratio has exact numerator/denominator and no missingness reason.
An unavailable ratio has null values and a declared reason. The composite follows the same rule.
All per-domain counts reconcile with global counts. Unattributed FP is not copied into every domain.

## Source and lifecycle fields

A completed source manifest has actual hashes, file counts, documented format, and real current grants.
Observed record count equals accepted plus quarantined plus rejected for the same named count unit.
A transfer requires external_api_transfer for the exact recipient in addition to any other source-use permission.
A raw source value can preserve an unknown field. It cannot create an approved normalized semantic meaning.
A private connector with credentials but no actual interface contract remains interface_missing.
A file or profile that merely describes future data remains not_acquired.
No report can convert those statuses to completed evidence by changing a label.

## Direct unit support

A case-wide QC report does not prove that one target phone exists.
Observed-phone, prosody, mutation, and unit-alignment references must name the exact unit they support.
A shared utterance ID does not transfer an observation from one word to another.
A resolved mapped unit requires direct unit evidence in addition to allowed background evidence.

## Source and asset digest distinction

`asset_sha256` identifies the evidence payload when that evidence references an asset.
`subject_audio_sha256` identifies the final delivery bytes about which acoustic evidence makes a claim.
The fields have different meanings. A raw ASR JSON digest cannot replace the audio digest.
An acoustic observation requires the subject_audio_sha256 field to match the case audio.
