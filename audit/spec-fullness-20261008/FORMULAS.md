# Every formula and its remaining definitions

All27 core and15 auxiliary formula strings are present and preserved. The missing-attachments statement is obsolete. The table separates an equation from the protocol that supplies its inputs. Exact core zero reasons come from the inspected reference values table.

| Measurement | Formula | Zero / unavailable rule | Definition dependencies |
|---|---|---|---|
| `detection.precision` | `TP/(TP+FP)` | no_assertions | GAP-015, GAP-018, GAP-019, GAP-020, GAP-022, GAP-024, GAP-025 |
| `detection.recall` | `TP/G` | no_opportunities | GAP-015, GAP-018, GAP-019, GAP-020, GAP-022, GAP-024, GAP-025 |
| `detection.f1` | `2*TP/(2*TP+FP+FN)` | no_opportunities | GAP-015, GAP-018, GAP-019, GAP-020, GAP-022, GAP-024, GAP-025 |
| `detection.miss_rate` | `FN/G` | no_opportunities | GAP-015, GAP-018, GAP-019, GAP-020, GAP-022, GAP-024, GAP-025 |
| `detection.false_discovery_rate` | `FP/(TP+FP)` | no_assertions | GAP-015, GAP-018, GAP-019, GAP-020, GAP-022, GAP-024, GAP-025 |
| `classification.coverage` | `LC/TP` | no_opportunities | GAP-015, GAP-018, GAP-019, GAP-020, GAP-022, GAP-024, GAP-025 |
| `classification.family_accuracy` | `LF/LC` | no_assertions | GAP-015, GAP-018, GAP-019, GAP-020, GAP-022, GAP-024, GAP-025 |
| `classification.exact_accuracy` | `LE/LC` | no_assertions | GAP-015, GAP-018, GAP-019, GAP-020, GAP-022, GAP-024, GAP-025 |
| `classification.hierarchical_accuracy` | `H/LC` | no_assertions | GAP-015, GAP-018, GAP-019, GAP-020, GAP-022, GAP-024, GAP-025 |
| `classification.hierarchical_recall` | `H/G` | no_opportunities | GAP-015, GAP-018, GAP-019, GAP-020, GAP-022, GAP-024, GAP-025 |
| `correction.attempt_rate` | `CA/TC` | no_opportunities | GAP-015, GAP-018, GAP-019, GAP-020, GAP-022, GAP-024, GAP-025 |
| `correction.strict_accuracy` | `CK/CA` | no_assertions | GAP-015, GAP-018, GAP-019, GAP-020, GAP-022, GAP-024, GAP-025 |
| `correction.graded_accuracy` | `CQ/CA` | no_assertions | GAP-015, GAP-018, GAP-019, GAP-020, GAP-022, GAP-024, GAP-025 |
| `correction.strict_recall` | `CK/GC` | no_opportunities | GAP-015, GAP-018, GAP-019, GAP-020, GAP-022, GAP-024, GAP-025 |
| `correction.graded_recall` | `CQ/GC` | no_opportunities | GAP-015, GAP-018, GAP-019, GAP-020, GAP-022, GAP-024, GAP-025 |
| `correction.assertion_precision` | `CK/(CA+FC)` | no_assertions | GAP-015, GAP-018, GAP-019, GAP-020, GAP-022, GAP-024, GAP-025 |
| `explanation.coverage` | `EA/TE` | no_opportunities | GAP-015, GAP-018, GAP-019, GAP-020, GAP-022, GAP-024, GAP-025 |
| `explanation.strict_accuracy` | `EK/EA` | no_assertions | GAP-015, GAP-018, GAP-019, GAP-020, GAP-022, GAP-024, GAP-025 |
| `explanation.graded_accuracy` | `EQ/EA` | no_assertions | GAP-015, GAP-018, GAP-019, GAP-020, GAP-022, GAP-024, GAP-025 |
| `explanation.graded_recall` | `EQ/GE` | no_opportunities | GAP-015, GAP-018, GAP-019, GAP-020, GAP-022, GAP-024, GAP-025 |
| `decoy.overcorrection_rate` | `DF/D` | no_opportunities | GAP-015, GAP-018, GAP-019, GAP-020, GAP-022, GAP-024, GAP-025 |
| `decoy.unflagged_rate` | `(D-DF)/D` | no_opportunities | GAP-015, GAP-018, GAP-019, GAP-020, GAP-022, GAP-024, GAP-025 |
| `decoy.explicit_acceptability_accuracy` | `DA/(DA+DF)` | no_assertions | GAP-015, GAP-018, GAP-019, GAP-020, GAP-022, GAP-024, GAP-025 |
| `acceptability.explicit_accuracy` | `SA/SN` | no_assertions | GAP-015, GAP-018, GAP-019, GAP-020, GAP-022, GAP-024, GAP-025 |
| `weighted.precision` | `WTP/(WTP+WFP)` | no_assertions | GAP-015, GAP-018, GAP-019, GAP-020, GAP-022, GAP-024, GAP-025 |
| `weighted.recall` | `WTP/(WTP+WFN)` | no_opportunities | GAP-015, GAP-018, GAP-019, GAP-020, GAP-022, GAP-024, GAP-025 |
| `weighted.f1` | `2*WTP/(2*WTP+WFP+WFN)` | no_opportunities | GAP-015, GAP-018, GAP-019, GAP-020, GAP-022, GAP-024, GAP-025 |
| `annotation.agreement` | `agreements/N` | protocol-specific undefined/empty input rules required | GAP-012, GAP-048, GAP-025 |
| `annotation.cohen_kappa` | `(Po-Pe)/(1-Pe); Pe=sum_label(p_rater1(label)*p_rater2(label))` | protocol-specific undefined/empty input rules required | GAP-012, GAP-048, GAP-025 |
| `verification.wer` | `(substitutions+deletions+insertions)/reference_word_count` | protocol-specific undefined/empty input rules required | GAP-035, GAP-037, GAP-025 |
| `audio.speech_rate_wpm` | `60*spoken_token_count/elapsed_speech_span_seconds` | protocol-specific undefined/empty input rules required | GAP-035, GAP-025 |
| `audio.articulation_rate_wpm` | `60*spoken_token_count/active_speech_seconds` | protocol-specific undefined/empty input rules required | GAP-035, GAP-025 |
| `audio.pause_ratio` | `internal_silent_seconds/elapsed_speech_span_seconds` | protocol-specific undefined/empty input rules required | GAP-034, GAP-035, GAP-025 |
| `audio.disfluency_density` | `100*reviewed_disfluency_events/spoken_token_count` | protocol-specific undefined/empty input rules required | GAP-035, GAP-025 |
| `evaluation.coverage` | `resolved_decisions/eligible_decisions` | protocol-specific undefined/empty input rules required | GAP-048, GAP-050, GAP-025 |
| `evaluation.exact_mapping_agreement` | `identical_claim_to_unit_decisions/eligible_gold_decisions` | protocol-specific undefined/empty input rules required | GAP-048, GAP-050, GAP-025 |
| `telemetry.elapsed_seconds` | `submitted_at-started_at` | protocol-specific undefined/empty input rules required | GAP-049, GAP-025 |
| `telemetry.replay_count` | `count(validated_play_events)` | protocol-specific undefined/empty input rules required | GAP-049, GAP-025 |
| `teacher.talk_time` | `None` | not_observable_in_this_mode | GAP-025 |
| `teacher.pronunciation` | `None` | not_observable_in_this_mode | GAP-025 |
| `teacher.classroom_management` | `None` | not_observable_in_this_mode | GAP-025 |
| `teacher.engagement` | `None` | not_observable_in_this_mode | GAP-025 |

Hierarchy, proposition credit, composite weights/applicability and every existing QC threshold are recorded separately in formula-review.json. WER can exceed1; auxiliary rates/counts are not core0..1 ratios. Unobserved teacher measurements remain null. Neither equations nor inherited thresholds establish empirical teaching norms.
