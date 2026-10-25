"""Literal regression cases for the actual request and response owners.

Constructed transport inputs test parsing/guidance, never a provider or storage.
"""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NODE = Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'

class PreparationRecovery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        script = r"""
        import {blueprintRequest} from './services/web/app/prepare/request.js';
        import {preparationResponse} from './services/web/app/prepare/response.js';
        import {requestError} from './services/web/app/requestError.js';
        const f={topic:'Picnic',speakers:2,words:150,level:'B1',families:[],categories:[],severities:[],amount:'exact',mutationCount:'',voices:['bf_emma','melo_en_au'],recurring:[],advanced:''};
        const advanced=(fields,overrides={})=>blueprintRequest({...f,...overrides,advanced:JSON.stringify({exercise_request:fields})}).exercise_request;
        const v={zero:advanced({mutation_count:0}),automatic:advanced({mutation_count:null}),one:advanced({speaker_count:1,mutation_count:1}),three:advanced({speaker_count:3,mutation_count:1}),density:advanced({text_length_words:400},{amount:'low'}),floor:advanced({category_ids:['a','b','c']},{amount:'low'}),recurring:advanced({speaker_count:1,mutation_count:1},{recurring:[{enabled:true},{enabled:true}]}),removed:advanced({recurring_errors:[]},{amount:'low',words:20,recurring:[{enabled:true},{enabled:true}]})};
        try{blueprintRequest(f)}catch(e){v.ordinaryInvalid=requestError(e)}
        try{blueprintRequest({...f,advanced:'{'})}catch(e){v.userJSON=requestError(e)}
        async function read(body,status=200){try{return {data:await preparationResponse(new Response(body,{status}))};}catch(e){return {message:requestError(e)};}}
        v.valid=await read('{"id":"saved-blueprint"}');
        v.html=await read('<html>SQL secret</html>',502);v.empty=await read('',503);v.badSuccess=await read('private broken body',200);
        v.secret=await read('{"code":"UNKNOWN","message":"SQL password=secret"}',500);
        v.setup=await read('{"code":"MODEL_SETUP_REQUIRED","message":"private"}',409);
        v.lease=await read('{"code":"LEASE_ACTIVE"}',409);
        v.nullFailure=await read('null',500);
        console.log(JSON.stringify(v));
        """
        result = subprocess.run([str(NODE),'--input-type=module','-e',script],cwd=ROOT,capture_output=True,text=True,timeout=20)
        if result.returncode:
            raise AssertionError(result.stderr)
        cls.v=json.loads(result.stdout)

    def test_advanced_count_positive(self):
        self.assertEqual(0,self.v['zero']['mutation_count'])
        self.assertIsNone(self.v['automatic']['mutation_count'])

    def test_effective_voice_count_positive(self):
        self.assertEqual(['bf_emma'],self.v['one']['speaker_voice_ids'])
        self.assertEqual(['bf_emma','melo_en_au',None],self.v['three']['speaker_voice_ids'])
        self.assertEqual([1],[r['speaker_number'] for r in self.v['recurring']['recurring_errors']])

    def test_effective_density_positive(self):
        self.assertEqual(4,self.v['density']['mutation_count'])
        self.assertEqual(3,self.v['floor']['mutation_count'])
        self.assertEqual(1,self.v['removed']['mutation_count'])

    def test_ordinary_invalid_negative(self):
        self.assertIn('Enter a whole number',self.v['ordinaryInvalid'])
        self.assertEqual('Advanced blueprint is not valid JSON. Your input is retained.',self.v['userJSON'])

    def test_success_response_positive(self):
        self.assertEqual({'data':{'id':'saved-blueprint'}},self.v['valid'])

    def test_unreadable_response_negative(self):
        expected='The local service returned an unreadable response. Your choices are retained. Refresh saved preparations before trying again.'
        for key in ['html','empty','badSuccess']:
            self.assertEqual(expected,self.v[key]['message'])
            self.assertNotIn('JSON',self.v[key]['message'])

    def test_backend_details_negative(self):
        for key in ['secret','nullFailure']:
            self.assertEqual('This step could not be completed. Your choices are retained. Refresh saved preparations before trying again.',self.v[key]['message'])

    def test_actionable_response_positive(self):
        self.assertIn('Set up the selected local speech model',self.v['setup']['message'])
        self.assertEqual('This preparation is still running. Refresh after it finishes or its foreground deadline expires.',self.v['lease']['message'])

if __name__ == '__main__':
    unittest.main(verbosity=2)
