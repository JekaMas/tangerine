"""Project existing actual FX observations onto future literal contracts; execute nothing."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MAPPING='''
override_positive|test_prepare_override_positive,test_prepare_choices_positive|
simple_positive|test_prepare_choices_positive,test_prepare_native_request_positive|
invalid_advanced_negative|test_prepare_malformed_negative|
cleared_override_negative|test_prepare_override_positive|Observe clearing the override and the literal B1/two-error summary; C1/zero does not establish clearing.
simple_path_positive|test_prepare_quick_path_positive,test_prepare_native_request_positive|
expanded_options_positive|test_prepare_choices_positive,test_prepare_override_positive|Verify recurrence retention in this precise expanded-options case.
focus_negative|test_prepare_required_negative,test_keyboard_focus_positive|
zero_negative|test_prepare_override_positive|
type_positive|test_typography_baseline_positive,test_caption_shrinkage_negative|
wrap_positive|test_page_overflow_negative,test_prepare_choices_positive|
tiny_type_negative|test_caption_shrinkage_negative|
hierarchy_negative|test_page_overflow_negative,test_keyboard_focus_positive|
failure_positive|test_failure_reasons_positive,test_failure_empty_message_negative|
recovery_positive|test_history_recovery_positive,test_completed_stale_failure_negative|Transport recovery and stale-failure helper exist; observe an explicit failed-preparation resume without repeating accepted pieces.
empty_reason_negative|test_failure_empty_message_negative|
read_only_negative|test_completed_stale_failure_negative,test_original_user_data_unchanged_negative|
records_positive|test_history_metadata_positive,test_history_native_projection_positive,test_audio_history_positive,test_review_selection_positive|
legacy_positive|test_legacy_negative,TestFXHistoryLegacyNegative|Native/presentation legacy fallback is tested; materialize the long-title legacy browser fixture if absent from retained observations.
same_title_negative|test_history_metadata_positive|Full-ID links exist; create the literal equal-title/equal-short-prefix pair before asserting that whole case.
narrow_metadata_negative|test_mobile_routes_positive,test_history_failure_negative,test_history_recovery_positive|
list_projection_positive|TestFXHistorySummaryPositive,TestFXHistorySummaryUnicodePositive,TestFXPreparationDatePositive,test_history_native_projection_positive,test_native_creation_dates_positive|Confirm exact 160 A plus ellipsis transport fixture rather than assuming another Unicode fixture is identical.
legacy_projection_negative|TestFXHistoryLegacyNegative,test_legacy_negative|Legacy absence is proved; combine equal-title/equal-short-prefix browser fixture with schema/pagination expectations.
results_positive|test_result_hierarchy_positive,test_result_optional_explanation_positive,test_result_immutable_copyable_positive|
draft_positive|test_draft_save_reopen_positive,test_draft_no_automatic_submission_negative|Saved editable draft exists; observe the named checking-progress view.
uncertain_negative|test_result_optional_explanation_positive|Completed result is not an unavailable/uncertain result; observe supported independent components in a distinct fixture.
optional_reason_negative|test_result_optional_explanation_positive|Supplied explanation100 exists; observe absent optional-reason presentation without a primary penalty.
replay_positive|test_replay_literal_keyboard_positive,test_passage_end_positive|
recurring_positive|test_replay_literal_keyboard_positive|Actual recording has five saved occurrences, not six. Materialize the six-interval fixture; do not fabricate a sixth or relabel this bounded proof.
autoplay_negative|test_no_autoplay_negative|
audio_failure_negative|test_replay_failure_negative,test_replay_recovery_positive|
range_stop_positive|test_replay_actual_range_positive,test_replay_literal_keyboard_positive,test_passage_end_positive|
range_interrupt_negative|test_replay_old_range_cancelled_negative,test_manual_seek_negative,test_range_replaced_positive|Actual replacement/manual seek cancellation exists; bind absent-timing behavior to its literal fixture separately.
starter_positive|test_starter_report_positive,test_starter_native_report_arithmetic_positive,test_starter_experiment_no_calls_negative|
cleanup_positive|test_cleanup_named_record_positive,test_cleanup_preview_shared_media_negative|
invalid_starter_negative|test_starter_invalid_json_negative,test_starter_failure_negative,test_starter_recovery_positive|
cleanup_identity_negative|test_cleanup_selection_invalidates_negative,test_cleanup_failure_retains_identity_negative|Selection invalidation is observed; literal equal-title/equal-short-prefix multi-record fixture remains.
named_form_positive|test_starter_report_positive,test_starter_experiment_no_calls_negative,test_selected_generation_binding_positive|
empty_workspace_negative|test_starter_failure_negative,test_starter_recovery_positive,test_invalid_fields_negative|Missing-default transport/pure invalid fields are proved; observe an empty-options workspace and its example/guidance without fake IDs.
'''
def build():
 g=json.loads((ROOT/'openspec/changes/implement-teacher-error-trainer/verification.json').read_text())
 fx=[x for x in g['cases'] if x['id'].startswith('FX-')]
 observations=json.loads((ROOT/'audit/final-functional-ux-20261025/RECONCILIATION.json').read_text())['cases_observed'];observed={x['test_id']:x for x in observations}
 mapping={line.split('|')[0]:line.split('|')[1:] for line in MAPPING.strip().splitlines()}
 def resolve(name):
  hits=[x for x in fx if x['test_id'].endswith('.'+name) or x['test_id'].endswith('::'+name)]
  if len(hits)>1:hits=[x for x in hits if x['command_id']=='final-functional-browser']
  if len(hits)!=1:raise ValueError((name,len(hits)))
  row=hits[0]
  if observed[row['test_id']]['status']!='passed':raise ValueError('Unpassed original observation')
  return row['id']
 rows=[]
 for x in g['cases']:
  if x['command_id'] not in [f'completion-i{i}' for i in range(18,22)] or x['property_id'].startswith('FIN-VERIFY'):continue
  names,residual=mapping[x['id'].split('.')[-1]]
  rows.append(dict(continuation_case=x['id'],iteration=int(x['command_id'].split('i')[-1]),candidate_existing_cases=[resolve(n) for n in names.split(',')],disposition='partial' if residual else 'reusable',residual_observation=residual,receipt_index='audit/final-functional-ux-20261025/RECONCILIATION.json',boundary='Only these literal native/browser/software observations; no new model/audio/FIN acceptance.'))
 return dict(implementation_commit='8bbc1e22654e35ba9b9cb274964eb4b767a572e4',policy='Only I17 applied. Future FIN cases stay planned until their own complete selections are reconciled. No duplicate implementation/inference merely for IDs.',fx_cases=len(observations),ui_cases=rows,cv=dict(receipt='audit/category-realization-20261025/RECONCILIATION.json',properties=[f'CV-0{i}.P1' for i in range(1,7)],registered_observations=518,auditory_scope='Keep individual confirmed/unconfirmed/uncertain/HTTP503 states. Native green is not heard proof; simultaneous masking remains unavailable.',consumer='I26.1'))
if __name__=='__main__':
 d=build();Path(__file__).with_name('OVERLAP.json').write_text(json.dumps(d,indent=2)+'\n');print('Mapped',len(d['ui_cases']),'reusable',sum(x['disposition']=='reusable' for x in d['ui_cases']),'partial',sum(x['disposition']=='partial' for x in d['ui_cases']))
