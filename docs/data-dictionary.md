# Data dictionary

The JSON Schemas define field types and structural limits. This dictionary states the field meanings.
The exact field paths and local constraints appear in `language/field-index.json`.
Read `docs/contract-invariants.md` for relations between fields and records.

One name can occur in multiple parent types. The parent schema determines its shape and permitted enumeration.
Descriptions do not authorize an extra field or a new enum value. Unknown fields must fail the closed schema.

All original field names remain traceable. The current request removes active substitute-origin enum values.
Read `audit/schema-restrictions.json` for each such change. Original examples and formula strings are not reworded data.

| Field | Meaning |
| --- | --- |
| `CA` | Number of those TP units with a supplied correction. |
| `CK` | Number of supplied eligible corrections with credit exactly one. |
| `CQ` | Sum of correction credit for eligible TP units. |
| `D` | Number of designated permitted controls. |
| `DA` | Number of designated controls explicitly identified as permitted. |
| `DF` | Number of distinct designated controls wrongly flagged. |
| `EA` | Number of those TP units with a supplied explanation. |
| `EK` | Number of supplied eligible explanations with credit exactly one. |
| `EQ` | Sum of explanation credit for eligible TP units. |
| `FC` | Number of FP assertions with an unnecessary correction. |
| `FN` | `G-TP`. |
| `FP` | Number of resolved false error assertions after duplicate removal. |
| `G` | Number of all confirmed true-error units. |
| `GC` | Number of all correction-eligible true units. |
| `GE` | Number of all explanation-eligible true units. |
| `H` | Sum of hierarchical credit for the TP units. |
| `LC` | Number of TP units with an explicit valid category. |
| `LE` | Number of those categories in the permitted exact-leaf set. |
| `LF` | Number of those categories in the correct reporting domain. |
| `SA` | Number of those judgments that agree with the key. |
| `SN` | Number of explicit judgments mapped to true units or controls. |
| `TC` | Number of correction-eligible TP units. |
| `TE` | Number of explanation-eligible TP units. |
| `TP` | Number of distinct true units with a supported error assertion. |
| `WFN` | Sum of weights for missed true units. |
| `WFP` | `FP`, with the existing fixed false-assertion weight of one. |
| `WTP` | Sum of weights for detected true units. |
| `accent_evidence` | This field states the available evidence for the requested accent. |
| `acceptability.explicit_accuracy` | This ratio measures correct explicit judgments among mapped units. Unsupported off-key assertions remain false positives outside this denominator. |
| `accepted_taxonomy_ids` | These registered taxonomy IDs can receive exact-category credit for this unit. |
| `accepted_varieties` | These English varieties are permitted by the fixed case context. |
| `age_group` | This field retains the source age group without an inferred age. |
| `answer_text` | This field contains the exact original teacher answer. |
| `answer_utf8_sha256` | This hash identifies the original answer bytes in UTF-8. |
| `approved_rationale_ids` | These IDs refer to reviewed explanations that feedback can cite. |
| `approved_text_alternatives` | These reviewed text alternatives can receive correction credit. |
| `approved_unit_ids` | These unit IDs identify the targets that the reviewer approved. |
| `assessment_basis` | This field states the declared basis for judging the language target. |
| `asset_id` | This identifier refers to the exact stored asset. |
| `asset_sha256` | This hash identifies the actual stored asset bytes. |
| `attempt_id` | This identifier refers to the frozen teacher attempt. |
| `audio` | This object describes the exact delivered audio asset. |
| `audio_interval` | This object locates an event in the delivered audio. |
| `audio_intervals` | These intervals locate the unit in the delivered audio. |
| `audio_origin_policy` | The current runtime permits synthetic-only exercises. Other origins require separate owner approval. |
| `audio_sha256` | This hash identifies the exact audio bytes for the observation. |
| `authorized_asset_id` | This historical substitution field has no active authorized value in this revision. |
| `blueprint_id` | This identifier refers to the source blueprint version. |
| `canonical` | This field identifies the designated canonical correction option. |
| `canonical_ipa` | This field contains the reviewed reference pronunciation, not the observed sound. |
| `canonical_text` | This field contains the intended correct text before mutations. |
| `canonical_utterance_id` | This identifier locates the canonical utterance for the opportunity. |
| `case_insensitive` | This field permits case-insensitive comparison only for this reviewed option. |
| `case_sha256` | This hash identifies the immutable case payload used by the attempt. |
| `case_version_id` | This identifier refers to one immutable case version. |
| `category_id` | This field contains the mapped category that the teacher explicitly supplied. |
| `category_span` | This span quotes the category from the original teacher answer. |
| `channels` | This field gives the required channel count for the audio asset. |
| `claim_id` | This identifier refers to one extracted teacher claim. |
| `claim_span` | This span quotes the full claim from the original answer. |
| `classification` | This flag states whether the task requests a category for each detected error. |
| `classification.coverage` | This ratio measures detected units with a category that the teacher explicitly supplied. |
| `classification.exact_accuracy` | This ratio measures exact permitted taxonomy IDs among explicitly categorized detections. |
| `classification.family_accuracy` | This ratio measures correct primary domains among explicitly categorized detections. |
| `classification.hierarchical_accuracy` | This ratio measures tree-based category credit among explicitly categorized detections. |
| `classification.hierarchical_recall` | This ratio measures category credit across all true units. Missing detections and missing categories contribute zero. |
| `clauses` | These records preserve the extracted claims and their original answer spans. |
| `components` | These flags select the task components before answer entry. |
| `composite` | This object contains the policy-derived aggregate score and its applicability. |
| `content_provenance_ids` | These IDs link the content to its actual source and transformation records. |
| `context_evidence` | These records support the contextual judgment for the unit. |
| `correction` | This flag or object describes correction requirements or decisions in its parent contract. |
| `correction.assertion_precision` | This ratio measures fully correct repairs among repairs of true detections and unnecessary repairs. |
| `correction.attempt_rate` | This ratio measures proposed corrections among detected units that permit correction. |
| `correction.graded_accuracy` | This ratio measures proposition-based correction credit among proposed corrections. The model cannot choose an arbitrary partial score. |
| `correction.graded_recall` | This ratio measures correction credit across all true correction opportunities. Missed units contribute zero. |
| `correction.strict_accuracy` | This ratio measures fully correct corrections among proposed corrections of true detections. |
| `correction.strict_recall` | This ratio measures fully corrected units among all true units that permit correction. |
| `correction_credit` | This fraction gives proposition-derived correction credit. |
| `correction_eligible` | This flag states whether the true unit has a correction opportunity. |
| `correction_option_ids` | These IDs refer to the reviewed correction alternatives used in feedback. |
| `correction_span` | This span quotes the proposed correction from the original answer. |
| `correction_supplied` | This flag records whether the teacher actually supplied a correction. |
| `corrections` | These options define reviewed repairs and their proposition constraints. |
| `counts` | This object contains raw counts, not reduced metric fractions. |
| `created_at` | This field records the actual creation time with its timezone. |
| `decision` | This field states the supported mapping outcome for one claim. |
| `decision_id` | This identifier refers to one saved semantic decision. |
| `decision_set_sha256` | This hash identifies the immutable set of decisions used for the score. |
| `decisions` | These records contain one supported outcome for every extracted claim. |
| `decoy.explicit_acceptability_accuracy` | This ratio measures correct explicit judgments among explicitly judged negative controls. |
| `decoy.overcorrection_rate` | This ratio measures designated permitted units that the teacher wrongly marks as errors. |
| `decoy.unflagged_rate` | This ratio measures designated permitted units that the teacher does not mark as errors. Silence does not prove conscious recognition. |
| `decoy_false_positives` | This count gives designated permitted units wrongly marked as errors. |
| `delivery_audio_sha256` | This hash identifies the final audio file that reviewers assessed. |
| `denominator` | This field contains the exact denominator of the stored ratio. |
| `detection` | This flag states whether the task requests error detection. |
| `detection.f1` | This ratio combines detection precision and recall. If true opportunities exist and the teacher finds none, its value is zero. |
| `detection.false_discovery_rate` | This ratio measures unsupported error assertions among all distinct error assertions. |
| `detection.miss_rate` | This ratio measures true units that the teacher missed. |
| `detection.precision` | This ratio measures supported error assertions among all distinct error assertions. |
| `detection.recall` | This ratio measures the true detection units that the teacher found. |
| `difficulty` | This field contains the declared difficulty value only with its stated evidence status. |
| `difficulty_evidence_ref` | This reference supports the difficulty claim. Missing evidence must not become a measured difficulty. |
| `domain` | This field names the primary reporting domain for the observation. |
| `domain_results` | These results partition opportunities by their primary reporting domain. |
| `duplicate_claims` | This count identifies claims excluded from extra credit because they repeat a prior claim. |
| `duplicate_of` | This reference identifies the earlier claim with the same supported meaning. |
| `duplicate_of_claim_id` | This identifier refers to an earlier compatible nonduplicate claim. |
| `duration_ms` | This field gives duration in milliseconds. |
| `duration_ms_max` | This field gives the maximum permitted duration in milliseconds. |
| `duration_ms_min` | This field gives the minimum permitted duration in milliseconds. |
| `eligible_span` | This span locates the canonical material available for the planned mutation. |
| `enabled_components` | These component names identify the fixed inputs used by the composite. |
| `end_cp` | This offset is the excluded end of a Unicode codepoint span. |
| `end_ms` | This field gives the interval end in milliseconds from the asset start. |
| `epistemic_status` | This field separates requests, inference, measurement, and human observation. |
| `evaluation_policy_version` | This field identifies the fixed semantic evaluation policy. |
| `evidence_hash` | This hash identifies the exact evidence payload. |
| `evidence_ids` | These IDs identify actual supporting records within the permitted subject and version scope. |
| `exact_text` | This text must equal the original substring at the specified codepoint offsets. |
| `expected_judgment` | This field states whether the reviewed unit is a true error, permitted control, or excluded item. |
| `explanation` | This flag or object describes explanation requirements or judgments in its parent contract. |
| `explanation.coverage` | This ratio measures proposed explanations among detected units that permit explanation. |
| `explanation.graded_accuracy` | This ratio measures proposition-based explanation credit among proposed explanations. |
| `explanation.graded_recall` | This ratio measures explanation credit across all true explanation opportunities. Missed units contribute zero. |
| `explanation.strict_accuracy` | This ratio measures fully correct explanations among proposed explanations of true detections. |
| `explanation_credit` | This fraction gives credit from the reviewed explanation propositions. |
| `explanation_eligible` | This flag states whether the unit has an explanation opportunity. |
| `explanation_supplied` | This flag records whether the teacher actually supplied an explanation. |
| `explicit_retraction_of_span` | This span identifies the original assertion that the teacher explicitly retracts. |
| `f1` | This ratio contains the F1 value under the stated counting policy. |
| `failure_reason` | This field describes the actual reason that candidate generation cannot satisfy its constraints. |
| `feature` | This name identifies the measured or requested feature inside the typed parent object. |
| `fn` | This count gives missed true units. |
| `forbidden_propositions` | These propositions describe changes that invalidate the correction or explanation. |
| `format` | This field names the exercise or file format specified by its parent contract. |
| `fp` | This count gives resolved false error assertions after duplicate removal. |
| `gates` | These records contain the applicable publication checks and their evidence. |
| `group_ids` | These IDs keep related records together during data-split assignment. |
| `hard_render_constraints` | These strings are historical target constraints. DEC-004 blocks unregistered interpretation or silent approximation. |
| `id` | This value uniquely identifies the record within its declared entity and version scope. |
| `idempotency_key` | This key identifies one logical request with one request-body hash. |
| `intended_ipa` | This field contains the requested pronunciation, not an acoustic observation. |
| `ipa` | This field contains IPA for the operation or correction specified by its parent object. |
| `item_decision_ids` | These IDs identify the saved decisions that support the feedback item. |
| `items` | These records contain the typed feedback entries defined by this parent object. |
| `kind` | This field selects the exact operation or judgment type from the parent enumeration. |
| `l1` | This field records the declared first language. It does not imply a particular error. |
| `language` | This field selects the requested interface or processing language. |
| `learner_cefr` | This field states the requested learner proficiency level. |
| `lease_expires_at` | This time limits the authority of the current evaluation lease. |
| `lease_token` | This token identifies the current evaluation lease for revision-checked writes. |
| `licence` | This object preserves the actual source license and permitted uses. |
| `licence_evidence_hash` | This hash identifies the retained evidence for source permissions. |
| `locale` | This field identifies the English locale for the stated voice or operation. |
| `locator` | This field locates the cited evidence within the named source. |
| `lower` | This field contains the declared lower bound in the stated unit. |
| `max_count` | This field gives the maximum permitted number of target units. |
| `method_version` | This field identifies the exact method used for the evidence. |
| `metrics` | This object contains the registered metric results and applicability reasons. |
| `min_count` | This field gives the minimum required number of target units. |
| `mode` | This field selects the representation or review mode allowed by its parent contract. |
| `normalized_case_version_id` | This identifier links a source record to its separately reviewed case version. |
| `note` | This text records contextual information without authority to override a failed gate. |
| `numerator` | This field contains the exact numerator of the stored ratio. |
| `numeric_measure` | This field contains an actual measurement with its method and unit. |
| `observation` | This field contains the reviewer observation, not a requested target. |
| `observations` | These entries retain the actual reviewer observations for the case. |
| `observed` | This field records evidence produced by the named method. |
| `observed_accent_notes` | This field contains reviewer observations without an invented accent-strength score. |
| `observed_ipa` | This field records the pronunciation that a qualified reviewer actually observed. |
| `observed_pace_wpm` | This field gives measured pace in words per minute. |
| `observed_pause_ms` | This field gives measured pause duration in milliseconds. |
| `observed_value` | This field contains the measured feature value in its declared unit. |
| `ops` | These typed operations specify how the provider must construct one audio turn. |
| `option_id` | This identifier selects one existing reviewed correction option. |
| `origin` | This field records actual source origin. It must not promote a substitute to genuine evidence. |
| `outcome` | This field records the overall publication-check result. |
| `pace_target_wpm` | This field gives the requested pace in words per minute. |
| `pace_tolerance_fraction` | This field gives the allowed relative deviation from the requested pace. |
| `pace_wpm` | This field gives the speaker pace target in words per minute. |
| `parent_evidence_ids` | These IDs link the evidence to the actual earlier records that it depends on. |
| `parser_version` | This field identifies the exact source import parser. |
| `pause_ms` | This field gives the requested pause duration in milliseconds. |
| `phase` | This field identifies the reviewer phase relative to key disclosure. |
| `pitch_semitones` | This field gives the requested pitch change in semitones. |
| `planned_pause_ms` | This field gives the planned pause duration, not its observed duration. |
| `planned_units` | These records describe proposed targets before acoustic realization and review. |
| `policy_version` | This field identifies the fixed policy that governs the parent operation. |
| `precision` | This ratio contains detection precision under the stated counting policy. |
| `primary_taxonomy_id` | This field selects the narrowest supported primary category for the unit. |
| `profile_id` | This identifier selects the registered provider or method profile required by the parent record. |
| `prosody` | This object states the bounded prosodic target or reviewed correction. |
| `provider_profile_id` | This identifier selects one versioned provider configuration. |
| `public_constraints` | These conditions give the teacher the context necessary to judge the case fairly. |
| `public_context` | This field contains task context that the teacher can read before submission. |
| `qualification_evidence_id` | This identifier links the reviewer to actual qualification evidence. |
| `quality_status` | This field states source-record quality without inventing approval. |
| `rate_percent` | This field gives the requested rate control as a percentage. |
| `rationale` | This field contains the reviewed reason for the correction or judgment. |
| `rationale_forbidden_propositions` | These assertions make the explanation incorrect under its reviewed criteria. |
| `rationale_required_propositions` | These assertions are necessary for full explanation credit. |
| `rationale_span` | This span quotes the explanation from the original teacher answer. |
| `raw_annotations_asset_id` | This identifier refers to the unchanged source annotation asset. |
| `raw_asset_sha256` | This hash identifies the acquired raw source file. |
| `raw_private_asset_id` | This identifier locates restricted original evidence on the server. |
| `reason` | This field explains why a metric or decision is unavailable under the stated enumeration. |
| `reason_code` | This code states the supported cause for the mapping outcome. |
| `recall` | This ratio contains detection recall under the stated counting policy. |
| `register` | This field states the social or institutional register required by the task. |
| `rejected_unit_ids` | These IDs identify units that the reviewer rejected. |
| `release_id` | This field identifies the exact acquired dataset release. |
| `requested_accent` | This field states an accent request. It does not prove the resulting accent. |
| `required_capabilities` | These capability names must all exist in the selected active provider profile. |
| `required_propositions` | These assertions are necessary for full credit for this reviewed option. |
| `review_decisions` | These records preserve authenticated reviewer decisions for the final artifact. |
| `reviewer_id` | This identifier refers to the actual authenticated human reviewer. |
| `reviews` | These records preserve independent review decisions and their evidence. |
| `revision` | This number identifies the current revision for concurrency checks. |
| `rights_approval_id` | This reference identifies the actual approval for this source use. |
| `sample_rate_hz` | This field gives the audio sample rate in hertz. |
| `satisfied_proposition_ids` | These existing required propositions match the actual teacher answer. |
| `schema_version` | This field identifies the data contract version, not a claim of implementation readiness. |
| `scoring_policy_version` | This field identifies the exact formula and counting policy. |
| `secondary_taxonomy_ids` | These categories describe the same event without adding detection opportunities. |
| `semantic_judgments_present` | This flag states that the result depends on semantic judgments in addition to arithmetic. |
| `severity` | This field contains the reviewed severity class fixed before the attempt. |
| `sha256` | This field contains a SHA-256 digest of the exact referenced bytes. |
| `source` | This object links the record to its real source and permitted transformation. |
| `source_id` | This identifier refers to a source in the source registry. |
| `source_profile_id` | This identifier refers to a corpus source profile in the corpus registry. |
| `source_record_id` | This identifier locates the actual original record inside the named source release. |
| `source_refs` | These references locate actual supporting material in named sources. |
| `source_score_scale` | This field preserves the original score scale and its definition. |
| `source_unit_id` | This identifier links an operation to the planned or verified source unit. |
| `source_uri` | This field records the actual source location without claiming download or permission. |
| `span` | This object gives exact codepoint offsets and the corresponding original text. |
| `speaker_id` | This identifier links an utterance or record to its stated speaker. |
| `speakers` | These profiles specify the distinct speakers in the exercise. |
| `split` | This field records the fixed data partition for the source record. |
| `stance` | This field distinguishes an error assertion, permitted-form assertion, question, comment, or retraction. |
| `start_cp` | This offset is the included start of a Unicode codepoint span. |
| `start_ms` | This field gives the interval start in milliseconds from the asset start. |
| `state` | This field records the current attempt lifecycle state. |
| `status` | This field states the parent operation result from its declared enumeration. |
| `status_label` | This field distinguishes error status from category and preferred style. |
| `subject_ids` | These IDs identify the exact units or entities supported by this evidence. |
| `submitted_at` | This field records the actual submission time after the answer-freeze transaction. |
| `sufficient_statistics` | These counts and sums permit exact recomputation of the metric ratios. |
| `supplied` | This flag records whether the source teacher text actually contains the relevant component. |
| `support_evidence_ids` | These IDs identify existing evidence within the judgment scope. |
| `surface_text` | This field contains the text after intentional textual mutations. |
| `target_label` | This field names the declared phonetic or prosodic target without claiming observation. |
| `target_locale` | This field identifies the target English locale for the published variety policy. |
| `target_span` | This span quotes the target that the teacher identified in the original answer. |
| `targets` | These entries specify registered target categories and their count limits. |
| `task_components` | These flags freeze the requested answer components before the attempt. |
| `taxonomy_id` | This field references a registered category at the declared taxonomy version. |
| `taxonomy_version` | This field identifies the immutable category registry used by the case. |
| `tenant_id` | This identifier fixes the owning organization for access control. |
| `terminal_period_insensitive` | This flag permits terminal-period normalization for this reviewed option only. |
| `text` | This field contains literal text for the specific typed operation or feedback item. |
| `text_spans` | These entries locate target text in named utterances. |
| `threshold_id` | This identifier refers to an approved threshold, not a model-selected limit. |
| `tp` | This count gives distinct supported true detections. |
| `transform_ids` | These IDs identify the actual transformations from raw data to this record. |
| `true_errors` | This count gives all confirmed true-error units in the case. |
| `turns` | These entries preserve the ordered audio turns and their speakers. |
| `type` | This field selects the typed evidence or source-reference class. |
| `unit` | This field identifies the measurement unit declared by the parent object. |
| `unit_id` | This identifier refers to the exact reviewed detection unit. |
| `units` | These entries contain the reviewed detection opportunities and negative controls. |
| `unparsed_spans` | These spans preserve substantive answer text that the extractor cannot resolve. |
| `unresolved_claims` | This count gives score-relevant claims that still require review. |
| `unresolved_reason` | This code states why the correction or explanation cannot receive a resolved judgment. |
| `upper` | This field contains the declared upper bound in the stated unit. |
| `user_id` | This identifier refers to the authenticated owner of the attempt. |
| `uses` | These operations are the exact uses permitted by the retained license approval. |
| `utterance_id` | This identifier locates one utterance in the fixed case version. |
| `utterance_ids` | These identifiers locate all utterances needed to interpret the unit. |
| `utterances` | These records preserve speaker identity and canonical and surface text. |
| `value` | This field contains the numeric result or null under the parent applicability rule. |
| `value_0_100` | This field contains the policy composite on the 0 to 100 scale, or null. |
| `variety_constraints` | These statements restrict the correction to its approved English varieties. |
| `variety_policy` | This object fixes locale, permitted varieties, register, and judgment basis. |
| `verdict` | This field records the resolved semantic outcome for the teacher claim. |
| `verification` | This field states review status, not the fact that a model requested a target. |
| `verification_policy_version` | This field identifies the publication-check policy used for the case. |
| `violated_proposition_ids` | These existing forbidden propositions occur in the actual teacher response. |
| `voice_id` | This field identifies the exact provider voice used for the audio turn. |
| `voice_profile_id` | This identifier selects the registered voice profile for the speaker. |
| `weight` | This integer gives the fixed severity weight from the scoring policy. |
| `weighted.f1` | This ratio combines weighted precision and recall. It does not replace the unweighted metrics. |
| `weighted.precision` | This ratio applies fixed severity weights to true detections. Each false positive has penalty one. |
| `weighted.recall` | This ratio applies the case weights to detected and missed opportunities. The case fixes these weights before answer entry. |
| `description` | This text states one explicit proposition or field meaning in its parent contract. |
| `designated_decoys` | This count gives the reviewed permitted controls in the case. |
| `realization` | This object separates the intended target, actual audio, and observed evidence. |
| `realization_state` | This field records whether the planned opportunity actually produced its required target. |
| `realized_unit_id` | This identifier links the opportunity to the actual resulting detection unit. |

A field description does not prove semantic validity. Source and evidence checks remain necessary.
A missing typed method or contradictory constraint remains blocked in the open-decision register.
Do not fill that gap through an invented default.

## Owner approval fields

These fields document the approval control that the owner explicitly requested. They do not approve themselves.

| Field | Meaning |
| --- | --- |
| `schema_version` | This field identifies the approval record contract. |
| `change_id` | This identifier selects one exact proposed change. |
| `decision` | This field records the actual owner decision. |
| `owner_identity_ref` | This reference identifies the authenticated owner, not a model role. |
| `source_statement_ref` | This reference locates the actual explicit owner statement. |
| `source_statement_sha256` | This digest identifies the retained owner statement bytes. |
| `artifact_sha256` | This digest identifies the exact proposed artifact or change manifest. |
| `allowed_paths` | These exact paths bound the approved change. |
| `allowed_use` | This text states the exact approved use, not a general testing exemption. |
| `environment` | This field names the environment in the owner approval. |
| `decided_at` | This field records the actual owner decision time. |
| `expires_at` | This field records the stated expiry. Null requires explicit approval without expiry. |
