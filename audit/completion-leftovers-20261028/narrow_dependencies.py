"""Correct this follow-up's overbroad verification dependency declarations.

No observer body, stored result, old receipt, formula or application behavior is
changed. Status/acceptance notes are not semantic inputs to unrelated tests.
"""
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];CHANGE=ROOT/'openspec/changes/implement-teacher-error-trainer';HERE=Path(__file__).resolve().parent
QWEN=['services/speech/backends.py','services/speech/qwen_runtime.py','services/speech/server.py','services/speech/audio.py','services/speech/inference_capture.py','services/speech/model_setup.py','tests/test_completion_i25.py','tests/test_qwen_comparison.py','tests/test_qwen_native_runtime.py','tests/test_qwen_player_observations.py','tests/speech-python','audit/iteration-25-qwen-20261026/compare.py','audit/iteration-25-qwen-20261026/player.py','audit/iteration-25-qwen-20261026/native_server.py','audit/iteration-25-qwen-20261026/browser-observations.json','audit/iteration-25-qwen-20261026/media-http-observations.json','audit/iteration-24-azure-20261026/material.json','audit/completion-leftovers-20261028/run_qwen.py','audit/completion-leftovers-20261028/browser_qwen.py','audit/completion-leftovers-20261028/export_qwen.py','tests/completion_leftovers_qwen.cjs','data/iteration-25-verify-20261026/cpu-timeout-observation.json','data/completion-leftovers-20261028/qwen-mps-float32-cpu-codec','data/completion-leftovers-20261028/qwen-browser','data/completion-leftovers-20261028/qwen-lab-readback.json']
ACOUSTIC=['services/speech/category_validation.py','services/speech/audio.py','tests/test_completion_i26.py','tests/test_selected_acoustic.py','tests/test_selected_listening_recovery.py','audit/iteration-26-acoustic-20261026/observe.py','audit/iteration-26-acoustic-20261026/listening.py','audit/iteration-26-acoustic-20261026/selection.json','audit/iteration-25-qwen-20261026/player.py','audit/completion-leftovers-20261028/browser_i26.py','tests/completion_leftovers_i26.cjs','data/iteration-26-acoustic-20261026/selected','data/completion-leftovers-20261028/i26']
RELEASE=['tests/test_completion_i30.py','tests/test_release_forwarder.py','audit/iteration-30-release-20261027/native_release.py','audit/iteration-30-release-20261027/readiness_forwarder.py','audit/iteration-30-release-20261027/launcher_fixture.sh','audit/completion-leftovers-20261028/release.py','audit/completion-leftovers-20261028/RELEASE-REVIEW.json','tests/completion_leftovers_i30.cjs','services/web/app/settings/page.js','services/web/app/clientRequest.js','services/web/app/requestError.js','data/completion-leftovers-20261028/release']
def main():
 path=CHANGE/'verification.json';graph=json.loads(path.read_text());base=json.loads(subprocess.check_output(['git','show','2433abe:openspec/changes/implement-teacher-error-trainer/verification.json'],cwd=ROOT));original={c['id']:c for c in base['cases']};entered=json.loads(subprocess.check_output(['git','show','943e050:openspec/changes/implement-teacher-error-trainer/verification.json'],cwd=ROOT));previous={c['id']:c for c in entered['cases']};changes=[];props={}
 for c in graph['cases']:
  p=c['property_id'];prior=c.get('invalidation_dependencies',[])
  if p in ['FIN-QWEN.P1','FIN-VERIFY.I25']:deps=QWEN
  elif p in ['FIN-ACOUSTIC.P1','FIN-VERIFY.I26']:deps=ACOUSTIC
  elif p in ['FIN-SOURCES.P1','FIN-VERIFY.I27']:
   deps=original.get(c['id'],{}).get('invalidation_dependencies',[])+['audit/completion-leftovers-20261028/browser_i27.py','audit/iteration-30-release-20261027/readiness_forwarder.py','tests/completion_leftovers_i27.cjs','data/completion-leftovers-20261028/i27']
  elif p in ['FIN-DELIVERY.P1','FIN-VERIFY.I30']:
   deps=list(RELEASE)
   if c['test_id'].split('.')[-1] not in ['test_missing_remote_negative','test_failed_push_negative','test_dirty_unrelated_landing_positive','test_overlapping_dirty_landing_negative','test_case_insensitive_origin_positive','test_unrelated_origin_not_rewritten_negative']:
    deps+=['README.md','LICENSE','.env.example','.dockerignore','scripts','deploy','services','specification/v2/domain','specification/v2/docs/local-delivery.md']
  elif p=='FIN-ACOUSTIC.P2':deps=[d for d in prior if d!='specification/v2/docs/speech-service-selection.md']
  else:continue
  deps=list(dict.fromkeys(deps))
  if previous[c['id']].get('invalidation_dependencies')!=deps:changes.append(dict(case_id=c['id'],previous=previous[c['id']].get('invalidation_dependencies'),current=deps,reason='Replace unrelated follow-up audit/UI scope with actual owner, test and fixed artifact producer dependencies; original receipts/bodies are unchanged.'))
  c['invalidation_dependencies']=deps;props.setdefault(p,[]).extend(deps)
 for p in graph['properties']:
  if p['id'] in props:p['source_globs']=list(dict.fromkeys(props[p['id']]))
 path.write_text(json.dumps(graph,indent=2,ensure_ascii=False)+'\n');(HERE/'DEPENDENCY-SCOPE-REPAIR.json').write_text(json.dumps(dict(source_revision='943e05092c1c7c7789bebecf024b163eeaedeea1',changes=changes,original_observed_receipts_modified=False,model_calls=0,corpus_imports=0,important_boundary='The runner hashes tracked source files only. Ignored model caches were not hashed. The real false invalidation came from tracked whole-audit/unrelated-file scopes. No runtime data integrity check or shared workflow engine change is introduced.'),indent=2)+'\n');print('Narrowed',len(changes),'case dependency declarations; observer bodies and old receipts retained')
if __name__=='__main__':main()
