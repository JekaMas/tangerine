from pathlib import Path
import sys,unittest,json,copy
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tests'))
from test_iteration3 import Iteration3Tests,ROOT
class Counterexamples(Iteration3Tests):
 @classmethod
 def setup(cls):
  super().setup();cls.receipts=ROOT/'data/iteration3-verify/red-native';cls.receipts.mkdir(exist_ok=True)
 def test_foreign_run_binding(self):
  first=self.packet();export=self.good(self.sdk('sync',first));second=self.packet();second['run']=export['run'];p=self.sdk('sync',second,ok=False)
  (self.receipts/'foreign-run.json').write_text(json.dumps({'first_operation':first['operation'],'second_operation':second['operation'],'native_exit':p.returncode,'actual':p.stdout}))
  self.assertNotEqual(p.returncode,0,'different operation was accepted into the first operation run')
 def test_unobserved_selected_case(self):
  run=self.development();run['selected_case_ids']=['I3-20.P1.S999.POSITIVE'];p=self.development_verify(run,ok=False);(self.receipts/'unobserved-case.json').write_text(json.dumps({'selected_case_ids':run['selected_case_ids'],'native_exit':p.returncode,'actual':p.stdout}));self.assertNotEqual(p.returncode,0,'unobserved selected case accepted')
 def test_changed_run_dependency(self):
  run=self.development();run['dependencies'][0]['sha256']='0'*64;p=self.development_verify(run,ok=False);(self.receipts/'changed-dependency.json').write_text(json.dumps({'dependency':run['dependencies'][0],'native_exit':p.returncode,'actual':p.stdout}));self.assertNotEqual(p.returncode,0,'incorrect claimed dependency accepted')
 def test_redaction_reason_leak(self):
  p=self.compose('exec','-T','llm-lab','/tangerine/native','lab-json',input=json.dumps({'action':'sanitize','payload':{'api_key_CANARY':'private value'},'capture':True,'secrets':['CANARY']}));out=self.good(p);(self.receipts/'reason-canary.json').write_text(json.dumps(out));self.assertNotIn('CANARY',json.dumps(out),'known credential escaped through a redaction reason')
suite=unittest.TestSuite(Counterexamples(n) for n in ['test_foreign_run_binding','test_unobserved_selected_case','test_changed_run_dependency','test_redaction_reason_leak'])
result=unittest.TextTestRunner(verbosity=2).run(suite);sys.exit(not result.wasSuccessful())
