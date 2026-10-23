"""Literal request expectations over the shipped JS request owner; no inference."""
from pathlib import Path
import json,subprocess,unittest
ROOT=Path(__file__).resolve().parents[1]
NODE=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'

class UXRequest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        script="""
        import {blueprintRequest,mistakeCount,categoryFloor} from './services/web/app/prepare/request.js';
        const f={topic:'Making decisions',speakers:2,words:200,level:'B2',families:[],categories:[],severities:[],amount:'auto',mutationCount:'',advanced:''};
        const request=(overrides)=>blueprintRequest({...f,...overrides});
        const values={
          exact:request({categories:['lexis.collocation','pragmatics_register.formality']}),
          cleared:request({categories:[]}),
          presets:['low','medium','high'].map(amount=>mistakeCount({...f,amount})),
          rounded:mistakeCount({...f,words:150,amount:'low'}),short:mistakeCount({...f,words:10,amount:'low'}),
          floor:mistakeCount({...f,words:20,amount:'low',categories:['a','b','c']}),
          overlap:categoryFloor({...f,families:['grammar','pronunciation','pronunciation.segmental','pronunciation.suprasegmental']}),
          exact3:request({amount:'exact',mutationCount:'3'}).exercise_request.mutation_count,
          zero:request({amount:'exact',mutationCount:'0',categories:['lexis.collocation']}).exercise_request.mutation_count,
          auto:request({amount:'auto'}).exercise_request.mutation_count,
          advanced:request({categories:['lexis.collocation'],severities:['minor'],amount:'high',advanced:JSON.stringify({exercise_request:{category_ids:['pragmatics_register.formality'],category_families:[],severity_levels:['major'],mutation_count:1}})}),
          severity:request({categories:['lexis.collocation'],amount:'medium',severities:['major']}),
          invalid:['-1','1.5',''].map(mutationCount=>{try{request({amount:'exact',mutationCount});return false;}catch{return true;}}),
          tooFew:(()=>{try{request({amount:'exact',mutationCount:'1',categories:['lexis.collocation','pragmatics_register.formality']});return false;}catch{return true;}})(),
        };console.log(JSON.stringify(values));
        """
        result=subprocess.run([str(NODE),'--input-type=module','-e',script],cwd=ROOT,capture_output=True,text=True,timeout=20)
        if result.returncode:raise AssertionError(result.stderr)
        cls.v=json.loads(result.stdout)

    def test_exact_categories_positive(self):
        self.assertEqual(self.v['exact']['exercise_request']['category_ids'],['lexis.collocation','pragmatics_register.formality'])
        self.assertEqual(self.v['exact']['exercise_request']['category_families'],[])
        self.assertNotIn('targets',self.v['exact'])
    def test_clear_categories_positive(self):
        self.assertNotIn('category_ids',self.v['cleared']['exercise_request'])
        self.assertEqual(self.v['cleared']['exercise_request']['category_families'],[])
        self.assertIsNone(self.v['cleared']['exercise_request']['mutation_count'])
    def test_presets_positive(self):self.assertEqual([self.v['presets'],self.v['rounded'],self.v['short']],[[2,4,8],2,1])
    def test_coverage_floor_positive(self):self.assertEqual([self.v['floor'],self.v['overlap']],[3,3])
    def test_exact_and_zero_positive(self):self.assertEqual([self.v['exact3'],self.v['zero'],self.v['auto']],[3,0,None])
    def test_advanced_override_positive(self):
        self.assertEqual(self.v['advanced']['exercise_request'],{'topic':'Making decisions','speaker_count':2,'text_length_words':200,'english_level':'B2','category_families':[],'mutation_count':1,'category_ids':['pragmatics_register.formality'],'severity_levels':['major']})
    def test_invalid_count_negative(self):self.assertEqual([self.v['invalid'],self.v['tooFew']],[[True,True,True],True])
    def test_severity_independent_negative(self):
        self.assertEqual(self.v['severity']['exercise_request']['mutation_count'],4)
        self.assertEqual(self.v['severity']['exercise_request']['category_ids'],['lexis.collocation'])
        self.assertEqual(self.v['severity']['exercise_request']['severity_levels'],['major'])

if __name__=='__main__':unittest.main()
