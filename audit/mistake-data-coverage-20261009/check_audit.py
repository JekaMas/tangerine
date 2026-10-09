"""Static/native-data positive and negative checks; no application execution."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
AUDIT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('mistake_audit_builder', AUDIT / 'build_audit.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
checks = []


def pair(name, value, oracle, mutate):
    assert oracle(value), name + ': supported static/native input failed'
    bad = copy.deepcopy(value)
    mutate(bad)
    assert not oracle(bad), name + ': constructed false metadata/edit accepted'
    checks.extend([{'id': name + '.positive', 'status': 'pass', 'proof': 'actual_static_or_native_inspection'},
                   {'id': name + '.negative', 'status': 'pass', 'proof': 'constructed_counterexample_to_audit_oracle_not_production_behavior'}])


def valid_edit(row):
    before, after, edit = row['canonical_example'], row['surface_example'], row['codepoint_edit']
    if edit is None:
        return False
    a, b, c, d = (edit[k] for k in ['start_cp', 'end_cp', 'surface_start_cp', 'surface_end_cp'])
    return (0 <= a <= b <= len(before) and 0 <= c <= d <= len(after)
            and before[a:b] == edit['exact_text'] and after[c:d] == edit['replacement']
            and before[:a] + edit['replacement'] + before[b:] == after
            and after[:c] + edit['exact_text'] + after[d:] == before)


taxonomy = builder.yaml_read('specification/v2/domain/error-taxonomy.v1.yaml')
catalogue = json.loads((ROOT / 'specification/v2/domain/mutation-recipes.v1.json').read_text())
matrix = json.loads((AUDIT / 'all-122-leaf-coverage.json').read_text())
ids = [x['id'] for x in taxonomy['items']]
pair('exact_122_leaf_recipe_identity', catalogue,
     lambda x: [r['taxonomy_id'] for r in x['recipes']] == ids and len(ids) == len(set(ids)) == 122,
     lambda x: x['recipes'].pop())
pair('exact_122_leaf_data_matrix', matrix,
     lambda x: [r['taxonomy_id'] for r in x] == ids and all(r['native_source_examples_mapped_to_leaf'] is None and r['leaf_frequency'] is None and r['data_needed'] for r in x),
     lambda x: x[0].update(leaf_frequency=0))
for row in catalogue['recipes']:
    name = row['taxonomy_id']
    pair(name + '.data_status', row,
         lambda r: r['source_mapping_count'] is None and r['empirical_leaf_frequency'] is None
         and r['source_mapping_missing_reason'] and r['frequency_missing_reason']
         and r['candidate_source_claim'].startswith('potential_material_only')
         and r['recipe_status'] == 'specified_not_provider_verified'
         and r['example_origin'] == 'authored_design_illustration_not_external_corpus_or_observed_audio',
         lambda r: r.update(source_mapping_count=1))
    if row['codepoint_edit'] is not None:
        pair(name + '.codepoint_round_trip', row, valid_edit,
             lambda r: r['codepoint_edit'].update(end_cp=len(r['canonical_example'])+1))
    else:
        pair(name + '.acoustic_request_not_observation', row,
             lambda r: r['required_final_evidence'] and r['procedure'] and r['context'] and not r['actual_generated_audio_observed'],
             lambda r: r.update(actual_generated_audio_observed=True))

unicode_row = {'canonical_example': '🙂 She works here.', 'surface_example': '🙂 She work here.'}
unicode_row['codepoint_edit'] = builder.replacement(unicode_row['canonical_example'], unicode_row['surface_example'])
pair('unicode_codepoint_not_utf16_offset', unicode_row, valid_edit,
     lambda r: r['codepoint_edit'].update(start_cp=r['codepoint_edit']['start_cp']+1))
pair('relationships_are_structural_or_candidate_not_empirical', catalogue,
     lambda d: all(e['meaning']=='structural_parent_not_empirical_cause' for e in d['hierarchy_edges'])
     and all(e['a'] in ids and e['b'] in ids and e['empirical_frequency'] is None for e in d['candidate_analysis_relationships'])
     and d['empirical_leaf_cooccurrence'] is None and d['observed_mapper_confusion'] is None,
     lambda d: d['candidate_analysis_relationships'][0].update(empirical_frequency=0.5))

toy = ('S She work work .\n'
       'A 1 2|||R:VERB:SVA|||works|||REQUIRED|||-NONE-|||0\n'
       'A 2 3|||R:VERB:SVA|||works|||REQUIRED|||-NONE-|||0\n'
       'A -1 -1|||noop|||-NONE-|||REQUIRED|||-NONE-|||1\n\n'
       'S They arrived .\n'
       'A -1 -1|||noop|||-NONE-|||REQUIRED|||-NONE-|||0\n\n')
toy_observation = builder.m2_observation(toy)
pair('alternative_annotator_not_simultaneous_error_and_presence_once', toy_observation,
     lambda d: d['eligible_corrected_edit_count']==2 and d['windows']==2
     and d['selected_tag_counts']=={'R:VERB:SVA':2,'noop':1}
     and next(s for s in d['statistics'] if s['native_tag']=='R:VERB:SVA')['window_presence_count']==1
     and d['selected_noop_annotations']==1,
     lambda d: d.update(eligible_corrected_edit_count=3))
pair('unmeasured_opportunity_rate', toy_observation,
     lambda d: all(s['error_opportunity_rate'] is None and s['opportunity_rate_missing_reason']=='correct_opportunities_not_enumerated' for s in d['statistics']),
     lambda d: d['statistics'][0].update(error_opportunity_rate={'numerator':2,'denominator':2}))

native = json.loads((AUDIT / 'bea-native-frequencies-and-cooccurrence.json').read_text())
initial = json.loads((ROOT / 'audit/corpus-acquisition-20261009/native-archive-inventory-initial.json').read_text())
old_views = {name: v for a in initial if 'bea/' in a['file'] for name, v in a['native_text_inventory'].items() if name.endswith('.m2')}
pair('all_twelve_native_m2_views_preserved_without_retagging', native,
     lambda d: len(d['views'])==12 and all(v['all_annotator_tag_counts']==old_views[v['member']]['types']
     and v['windows']==old_views[v['member']]['sentences'] for v in d['views']),
     lambda d: d['views'][0]['all_annotator_tag_counts'].update(noop=-1))
pair('native_counts_not_project_leaf_frequency', native,
     lambda d: d['granularity']=='native_M2_tags_not_122_project_leaves' and d['project_leaf_frequency'] is None
     and not d['opportunity_rates_available'],
     lambda d: d.update(granularity='122_project_leaves'))
pair('withheld_wi_test_labels_not_zero', native,
     lambda d: d['withheld_label_views'][0]['windows']==4477 and d['withheld_label_views'][0]['error_frequency'] is None,
     lambda d: d['withheld_label_views'][0].update(error_frequency=0))
for v in native['views']:
    pair(v['member']+'.frequency_denominators', v,
         lambda d: sum(s['selected_annotation_count'] for s in d['statistics'])==sum(d['selected_tag_counts'].values())
         and sum(s['eligible_corrected_edit_count'] for s in d['statistics'])==d['eligible_corrected_edit_count']
         and all(s['window_prevalence'] is None or s['window_prevalence']['denominator']==d['windows'] for s in d['statistics'])
         and all(s['event_share'] is None or s['event_share']['denominator']==d['eligible_corrected_edit_count'] for s in d['statistics']),
         lambda d: d.update(eligible_corrected_edit_count=d['eligible_corrected_edit_count']+1))

metrics = builder.yaml_read('specification/v2/domain/metrics.v1.yaml')
sources = builder.yaml_read('specification/v2/domain/corpus-sources.v1.yaml')
pair('all_42_grade_equations_unchanged', metrics,
     lambda d: len(d['metrics'])==27 and len(d['auxiliary_metrics'])==15,
     lambda d: d['metrics'].pop())
pair('all_11_original_full_source_identities', sources,
     lambda d: len(d['sources'])==11 and all(s['required_components'] for s in d['sources']),
     lambda d: d['sources'].pop())
graph = json.loads((ROOT / 'openspec/changes/implement-teacher-error-trainer/verification.json').read_text())
old_graph = json.loads(subprocess.check_output(['git','show','461cff3:openspec/changes/implement-teacher-error-trainer/verification.json'],cwd=ROOT,text=True))
pair('all_original_requirements_properties_cases_preserved', graph,
     lambda d: d['requirements'][:len(old_graph['requirements'])]==old_graph['requirements']
     and d['properties'][:len(old_graph['properties'])]==old_graph['properties']
     and d['cases'][:len(old_graph['cases'])]==old_graph['cases'],
     lambda d: d['cases'][0].update(state='pass'))
pair('all_new_behavior_edges_are_unperformed_plans', graph,
     lambda d: len([c for c in d['cases'] if c['property_id'].startswith('MDC-')])==28
     and all(c['state']=='blocked' and c['source_sha256'] is None for c in d['cases'] if c['property_id'].startswith('MDC-')),
     lambda d: next(c for c in d['cases'] if c['property_id'].startswith('MDC-')).update(state='pass'))

protected = ['specification/v2/domain/error-taxonomy.v1.yaml','specification/v2/domain/metrics.v1.yaml','specification/v2/domain/corpus-sources.v1.yaml']
protected += [str(p.relative_to(ROOT)) for p in (ROOT/'specification/v2/contracts').glob('*.json')]
for name in protected:
    before = subprocess.check_output(['git','show','461cff3:'+name],cwd=ROOT)
    assert (ROOT/name).read_bytes()==before, name+' was unexpectedly altered'
checks.append({'id':'protected_taxonomy_examples_metrics_sources_schemas_byte_preservation','status':'pass','files':len(protected),'proof':'git baseline byte equality'})
write = builder.write
write(AUDIT / 'static-validation.json', {'scope':'audit/static native methods and constructed metadata counterexamples; not production or empirical linguistic validation', 'checks':checks, 'pass':all(c['status']=='pass' for c in checks)})
print(json.dumps({'static_checks':len(checks),'all_pass':True,'protected_files':len(protected),'behavior_tests':'not_run'},indent=2))
