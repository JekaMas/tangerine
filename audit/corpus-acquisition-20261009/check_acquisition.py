"""Static evidence/specification checks; not application importer or LLM tests."""
from pathlib import Path
import copy
import hashlib
import json
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
AUDIT = Path(__file__).resolve().parent
BASELINE = '3a0a7b2'
YAML_MODULE = Path(shutil.which('openspec')).resolve().parent.parent / 'node_modules/yaml'
checks = []


def yaml_value(path=None, text=None):
    value = text if text is not None else (ROOT / path).read_text()
    command = ['node', '-e', 'const fs=require("fs"),y=require(process.argv[1]);process.stdout.write(JSON.stringify(y.parse(fs.readFileSync(0,"utf8"))));', str(YAML_MODULE)]
    result = subprocess.run(command, input=value, text=True, capture_output=True, check=True)
    return json.loads(result.stdout)


def pair(name, current, oracle, mutate):
    assert oracle(current), name + ': actual supported evidence rejected'
    changed = copy.deepcopy(current)
    mutate(changed)
    assert not oracle(changed), name + ': constructed contradictory metadata accepted'
    checks.extend([{'id': name + '.positive', 'status': 'pass', 'scope': 'static_actual_receipt_or_spec_consistency'},
                   {'id': name + '.negative', 'status': 'pass', 'scope': 'constructed_metadata_counterexample; not production behavior'}])


registry = yaml_value('specification/v2/domain/corpus-sources.v1.yaml')
ids = ['TET-GOLD-1', 'SPEECHOCEAN762', 'L2-ARCTIC', 'WILOCNESS-2.1', 'FCE-2.1', 'EFCAMDAT-R2', 'EFCAMDAT-SHATZ2020', 'EFCAMDAT-OKSUZ2025', 'DOUBAO-STUDY-RECORDS', 'MOODRICK-DATA', 'NIR-DATA']
pair('original_source_identities', registry, lambda d: [s['id'] for s in d['sources']] == ids,
     lambda d: d['sources'].pop())
pair('only_three_original_native_acquisitions', registry,
     lambda d: [s['id'] for s in d['sources'] if s['acquired']] == ['SPEECHOCEAN762', 'WILOCNESS-2.1', 'FCE-2.1'],
     lambda d: d['sources'][5].update(acquired=True))

research = json.loads((ROOT / 'specification/v2/domain/source-research.v1.json').read_text())
pair('complete_companion_is_not_cambridge_full_release', research,
     lambda d: all(m['record_bytes_acquired'] for m in d['efcamdat']['osf_metadata_members']) and not d['efcamdat']['full_cambridge_release_acquired'],
     lambda d: d['efcamdat'].update(full_cambridge_release_acquired=True))
pair('no_application_import_or_normalization_claim', research,
     lambda d: not d['application_import_observed'] and not d['normalized_complete_observed'],
     lambda d: d.update(normalized_complete_observed=True))

pair('actual_sent_and_csv_inspection_ledger', research,
     lambda d: d['efcamdat']['csv_record_rows_inspected'] and all(v['message_sent'] for v in d['vendors'].values()),
     lambda d: d['vendors']['NIR-DATA'].update(message_sent=False))

outreach = json.loads((AUDIT / 'outreach.json').read_text())
pair('ten_actual_sent_requests', outreach,
     lambda d: len(d) == 10 and all(m['status'] == 'sent_confirmed' and m['sender'] == 'jeka6655321@gmail.com' and m['confirmation'] for m in d),
     lambda d: d[0].update(status='prepared_not_sent'))

speech = json.loads((AUDIT / 'speechocean-native-conformance.json').read_text())
pair('speech_full_selected_join_and_five_raters', speech,
     lambda d: d['score_records'] == d['five_rater_records'] == d['unique_split_ids'] == 5000 and d['split_counts'] == {'train': 2500, 'test': 2500} and d['split_overlap'] == 0 and d['five_rater_lengths'] == {'5': 5000} and not any(d[k] for k in ['selected_without_wave', 'selected_without_aggregate', 'selected_without_detail', 'empty_wave_ids']),
     lambda d: d.update(selected_without_detail=['constructed_missing_id']))
pair('speech_unselected_is_not_additional_gold', speech,
     lambda d: d['archive_unique_wave_stems'] == 5245 and d['unselected_wave_stems'] == 245 and d['score_records'] == 5000,
     lambda d: d.update(score_records=5245))

icnale = json.loads((AUDIT / 'icnale-unlocked-inventory.json').read_text())
pair('all_nine_icnale_packages_crc_checked', icnale,
     lambda d: len(d) == 9 and all(x['files_read_crc_verified'] > 0 and not x['errors'] for x in d),
     lambda d: d[0]['errors'].append({'error': 'constructed CRC failure'}))

l2 = json.loads((AUDIT / 'l2-arctic-mirror-native-inventory.json').read_text())
pair('pinned_mirror_complete_native_members', l2,
     lambda d: len(d['archives']) == 25 and d['read_wave_count'] == 26867 and d['read_manual_annotation_count'] == 3599 and sum(len(x['members']) for x in d['archives']) == 84266 and all(not x['errors'] for x in d['archives']),
     lambda d: d['archives'].pop())
pair('mirror_not_false_official_conformance', research,
     lambda d: d['l2_arctic_acquisition']['full_scope_pinned_raw_mirror_acquired'] and not d['l2_arctic_acquisition']['official_byte_equivalence_claimed'] and d['l2_arctic_acquisition']['operation_count_convention_or_version_drift_unresolved'],
     lambda d: d['l2_arctic_acquisition'].update(official_byte_equivalence_claimed=True))
annotations = json.loads((AUDIT / 'l2-arctic-native-annotation-accounting.json').read_text())
pair('phone_tier_counts_and_basename_joins', annotations,
     lambda d: d['read_phone_operations'] == {'s':18577,'d':7843,'a':1092} and d['suitcase_phone_operations'] == {'s':2158,'d':650,'a':90} and all(x['basename_joins_verified'] for x in d['archives']),
     lambda d: d['read_phone_operations'].update(s=14098))
replies = json.loads((AUDIT / 'owner-replies.json').read_text())
pair('cambridge_reply_not_access_grant', replies,
     lambda d: len(d) == 1 and d[0]['status'] == 'human_owner_reply_received' and not d[0]['release_granted'],
     lambda d: d[0].update(release_granted=True))

failed = json.loads((AUDIT / 'l2-arctic-v5-full-receipt.json').read_text())
pair('quota_html_not_corpus_bytes', failed,
     lambda d: d['status'] == 'download_failed' and 'text/html' in d['content_type'] and 'quota' in d['observation'],
     lambda d: d.update(status='download_verified'))

receipts = [json.loads(p.read_text()) for p in sorted(AUDIT.glob('*-receipt.json'))]
verified = [d for d in receipts if d['status'] == 'download_verified']
# Reuse each download's original observed SHA256. Do not rehash already verified large archives.
for d in verified:
    p = ROOT / d['path']
    assert p.is_file() and p.stat().st_size == d['bytes'] and re.fullmatch('[0-9a-f]{64}', d['sha256']), d['id']
checks.append({'id': 'all_verified_receipt_files_present_with_exact_sizes', 'status': 'pass', 'files': len(verified), 'scope': 'receipt reuse plus current filesystem availability; no repeated full hash operation'})
pair('verified_receipt_metadata', verified,
     lambda d: all(x['bytes'] > 0 and re.fullmatch('[0-9a-f]{64}', x['sha256']) for x in d),
     lambda d: d[0].update(sha256='constructed_bad_hash'))

current = yaml_value('specification/v2/domain/error-taxonomy.v1.yaml')
baseline_bytes = subprocess.check_output(['git', 'show', BASELINE + ':specification/v2/domain/error-taxonomy.v1.yaml'], cwd=ROOT).decode()
baseline = yaml_value(text=baseline_bytes)
for before, after in zip(baseline['items'], current['items']):
    assert {k: v for k, v in before.items() if k != 'coverage_requirement'} == {k: v for k, v in after.items() if k != 'coverage_requirement'}, before['id']
pair('all_taxonomy_data_preserved_and_stale_approval_removed', current,
     lambda d: len(d['items']) == 122 and [i['id'] for i in d['items']] == [i['id'] for i in baseline['items']] and all('settled six-stimulus' in i['coverage_requirement'] and 'unresolved negative-control' not in i['coverage_requirement'] for i in d['items']),
     lambda d: d['items'].pop())
metrics = yaml_value('specification/v2/domain/metrics.v1.yaml')
pair('all_42_equations_preserved', metrics,
     lambda d: len(d['metrics']) == 27 and len(d['auxiliary_metrics']) == 15,
     lambda d: d['auxiliary_metrics'].pop())
for path in ['specification/v2/domain/metrics.v1.yaml', 'specification/v2/domain/providers.v1.yaml']:
    assert (ROOT / path).read_bytes() == subprocess.check_output(['git', 'show', BASELINE + ':' + path], cwd=ROOT), path
checks.append({'id': 'metric_and_provider_definitions_unchanged', 'status': 'pass'})

# Changed aggregate byte inventory invalidates the prior vector gate; unchanged behavior checks are retained.
entries = []
for p in sorted((ROOT / 'specification/v2').rglob('*')):
    if not p.is_file():
        continue
    b = p.read_bytes()
    if p.suffix == '.json':
        json.loads(b)
    elif p.suffix in ('.yaml', '.yml'):
        yaml_value(text=b.decode())
    entries.append({'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b), 'lines': len(b.splitlines())})
vector = {'files': entries, 'file_count': len(entries), 'line_count': sum(x['lines'] for x in entries),
          'scope': 'full active namespace mechanical byte/line traversal and JSON/YAML syntax; not per-line linguistic or implemented native-format proof'}
(AUDIT / 'line-accounting.json').write_text(json.dumps(vector, indent=2) + '\n')
pair('whole_active_vector_members', entries,
     lambda d: {x['path'] for x in d} == {str(p.relative_to(ROOT)) for p in (ROOT / 'specification/v2').rglob('*') if p.is_file()},
     lambda d: d.pop())
pair('current_vector_hashes', entries,
     lambda d: all(x['sha256'] == hashlib.sha256((ROOT / x['path']).read_bytes()).hexdigest() for x in d),
     lambda d: d[0].update(sha256='0' * 64))

result = {'scope': 'static native acquisition, outreach receipts and specification consistency; application tests not_run',
          'baseline': BASELINE, 'checks': checks, 'pass_count': len(checks),
          'unchanged_behavior_tests_rerun': False, 'source_scripts_or_macros_executed': False,
          'taxonomy_ids': 122, 'core_equations': 27, 'auxiliary_equations': 15, 'original_source_ids': 11}
(AUDIT / 'static-validation.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'static_checks': len(checks), 'namespace_files': vector['file_count'], 'namespace_lines': vector['line_count'], 'verified_download_receipts': len(verified)}))
