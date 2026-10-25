"""Literal reconciliation cases for I17, not runtime/provider qualification."""
import copy,json,subprocess,unittest
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'audit/iteration-17-reconciliation-20261025'
spec=importlib.util.spec_from_file_location('iteration17_verify',HERE/'verify.py')
verify=importlib.util.module_from_spec(spec);spec.loader.exec_module(verify)
def read(name):
 path=ROOT/'audit/iteration-17-verification-20261025/REVIEW.json' if name=='REVIEW.json' else HERE/name
 return json.loads(path.read_text())

class CompletionI17(unittest.TestCase):
 def test_ledger_positive(self):
  baseline=json.loads((ROOT/'audit/completion-plan-20261025/UNCHECKED-BASELINE.json').read_text());ledger=read('LEDGER.json')
  self.assertEqual([],verify.ledger_errors(ROOT,ledger,baseline))
  self.assertEqual(53,sum('GAP-' in x['text'] for x in baseline))
  frozen=subprocess.check_output(['git','show',ledger['baseline_revision']+':openspec/changes/implement-teacher-error-trainer/tasks.md'],cwd=ROOT,text=True).splitlines()
  for row in ledger['items']:
   with self.subTest(row=row['id']):
    self.assertEqual('- [ ] '+row['original_text'],frozen[row['baseline_line']-1])
    self.assertIn('I17 '+row['id'],(ROOT/'openspec/changes/implement-teacher-error-trainer/tasks.md').read_text())
  self.assertEqual([],verify.acceptance_errors(read('ACCEPTANCE-SOURCES.json')))
  self.assertEqual([],verify.overlap_errors(ROOT,read('OVERLAP.json')))
  tools=read('REPOSITORY-TOOLS.json')
  self.assertEqual(('1.14.3','1.13.1','1.13.1'),(tools['global_cli_version'],tools['selected_cli_version'],tools['selected_cli_package_version']))
  self.assertEqual([],tools['remote_names']);self.assertEqual('0\t50',tools['main_head_difference'])
  self.assertIn('TANGERINE_OPENSPEC_CLI',(ROOT/'docs/development/OPENSPEC_WORKFLOW.md').read_text())
 def test_ledger_negative(self):
  baseline=json.loads((ROOT/'audit/completion-plan-20261025/UNCHECKED-BASELINE.json').read_text());ledger=read('LEDGER.json')
  for change in ['missing','duplicate','original','activation','successor','reference','fake_provider_pass','fake_full_release']:
   bad=copy.deepcopy(ledger)
   if change=='missing':bad['items'].pop()
   if change=='duplicate':bad['items'][-1]=bad['items'][0]
   if change=='original':bad['items'][0]['original_text']='101 absent features'
   if change=='activation':next(x for x in bad['items'] if x['disposition']=='optional/external')['activation']=None
   if change=='successor':next(x for x in bad['items'] if x['disposition']=='still required')['successor_tasks']=[]
   if change=='reference':bad['items'][0]['references']=['does-not-exist']
   if change=='fake_provider_pass':bad['items'][98]['disposition']='completed'
   if change=='fake_full_release':bad['items'][93]['disposition']='completed'
   with self.subTest(change=change):self.assertTrue(verify.ledger_errors(ROOT,bad,baseline))
  packet=read('ACCEPTANCE-SOURCES.json')
  for change in ['demo','missing_i12','old_failed_i16','rewrite_failure','duplicate_i12','unrelated_i16','dirty_i16','blank_semantics']:
   bad=copy.deepcopy(packet)
   if change=='demo':bad['i16']['cases']={};bad['i16']['case_edges']=1
   if change=='missing_i12':bad['i12']['cases']=[]
   if change=='old_failed_i16':bad['i16']['status']='incomplete';bad['i16']['unresolved']=12
   if change=='rewrite_failure':bad['earlier_i16']['status']='passed'
   if change=='duplicate_i12':bad['i12']['cases']=[bad['i12']['cases'][0]]*139
   if change=='unrelated_i16':bad['i16']['cases']={'fake'+str(i):v for i,v in enumerate(bad['i16']['cases'].values())}
   if change=='dirty_i16':bad['i16']['git']['dirty']=True
   if change=='blank_semantics':bad['i12']['semantic_cases']=[{}]*6
   with self.subTest(change=change):self.assertTrue(verify.acceptance_errors(bad))
  maintained=(ROOT/'openspec/changes/implement-teacher-error-trainer/tasks.md').read_text()
  bad=maintained.replace('I17 H099: optional/external','I17 H099: completed')
  self.assertTrue(verify.ledger_errors(ROOT,ledger,baseline,bad))
  old=next(line for line in maintained.splitlines() if 'I17 H099:' in line)
  self.assertTrue(verify.ledger_errors(ROOT,ledger,baseline,maintained.replace(old,old.replace('- [ ]','- [x]'))))
 def test_review_positive(self):
  self.assertEqual([],verify.review_errors(read('REVIEW.json')))
 def test_ux_omission_negative(self):
  p=read('REVIEW.json');p.pop('ui_ux');self.assertTrue(verify.review_errors(p))
  p=read('REVIEW.json');p['ui_ux']={'disposition':'pass','reason':'Web build and 48 pictures'};self.assertTrue(verify.review_errors(p))
 def test_typography_omission_negative(self):
  p=read('REVIEW.json');p.pop('typography');self.assertTrue(verify.review_errors(p))
  p=read('REVIEW.json');p['typography']={'disposition':'pass','font':'Source Sans 3','caption_px':10};self.assertTrue(verify.review_errors(p))
 def test_evidence_mismatch_negative(self):
  p=read('REVIEW.json');p['claims_new_product_acceptance']=True;self.assertTrue(verify.review_errors(p))
  p=read('REVIEW.json');p['new_model_calls']=50;p['performance_campaigns']='required';self.assertTrue(verify.review_errors(p))
  p=read('REVIEW.json');p['independence']='independent human approval';self.assertTrue(verify.review_errors(p))
  p=read('OVERLAP.json');r=next(x for x in p['ui_cases'] if x['continuation_case']=='FIN-UI-05.P1.recurring_positive');r['disposition']='reusable';r['residual_observation']='six recorded intervals';self.assertTrue(verify.overlap_errors(ROOT,p))

if __name__=='__main__':unittest.main()
