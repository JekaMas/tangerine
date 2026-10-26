"""Production submission builders with independent constructed expectations."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NODE = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'


class GuidedStarters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        script = """
import fs from 'node:fs';
import {reportStarter,reportFromPopulation,experimentStarter} from './services/web/app/reports/starters.js';
const defaults=JSON.parse(fs.readFileSync('data/final-functional-ux-20261025/lab-defaults.json','utf8'));
const input=reportStarter('Original','lexis.collocation');
input.source={import_id:'native-import',member:'essays.m2',table:'sentences',annotator:'0',annotated_leaf_ids:[],leaf_by_event:{}};
input.input.population.label_origin='native';input.attempts=[{id:'retained-observation'}];
const before=JSON.stringify(input),report=reportFromPopulation(' New title ',input);
report.input.population.view='changed-copy';
const dataset={id:'saved-plan',scope:'generation_pipeline',dataset_asset_id:'accepted-dataset',dataset_sha256:'a'.repeat(64),judge_policy_asset_id:null};
const reused=await experimentStarter(defaults,{profile:'local-generation',dataset});
let errors=[];
for(const fn of [()=>reportFromPopulation('',input),()=>experimentStarter(defaults,{profile:'invented',dataset}),()=>experimentStarter(defaults,{profile:'local-generation',dataset:{...dataset,scope:'answer_pipeline'}}),()=>experimentStarter(defaults,{profile:'local-generation',dataset:{...dataset,judge_policy_asset_id:'judge'}})]){
 try{await fn();errors.push(null)}catch(e){errors.push(e.message)}
}
const unavailable=structuredClone(defaults);unavailable.configuration.llm_profiles.find(p=>p.id==='local-generation').model='unselected';let unavailableError=null;try{await experimentStarter(unavailable,{profile:'local-generation',dataset})}catch(e){unavailableError=e.message}
console.log(JSON.stringify({unavailableError,report,unchanged:JSON.stringify(input)===before,reused,errors,sva:reportStarter('SVA','grammar.verbs.subject_verb_agreement')}));
"""
        result = subprocess.run([str(NODE), '--input-type=module', '-e', script], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        if result.returncode:
            raise AssertionError(result.stderr)
        cls.v = json.loads(result.stdout)

    def test_named_population_positive(self):
        report = self.v['report']
        self.assertEqual('New title', report['title'])
        self.assertEqual({'import_id': 'native-import', 'member': 'essays.m2', 'table': 'sentences',
                          'annotator': '0', 'annotated_leaf_ids': [], 'leaf_by_event': {}}, report['source'])
        self.assertEqual('native', report['input']['population']['label_origin'])
        self.assertEqual([{'id': 'retained-observation'}], report['attempts'])

    def test_no_saved_population_mutation_negative(self):
        self.assertTrue(self.v['unchanged'])
        self.assertEqual('changed-copy', self.v['report']['input']['population']['view'])

    def test_named_dataset_positive(self):
        value = self.v['reused']
        self.assertEqual('accepted-dataset', value['experiment']['dataset_asset_id'])
        self.assertEqual('a' * 64, value['experiment']['dataset_sha256'])
        self.assertEqual({'bundle', 'config'}, set(value['assets']))
        self.assertEqual(1, value['experiment']['repetitions'])

    def test_selected_binding_positive(self):
        value = self.v['reused']
        self.assertEqual('local-generation', value['experiment']['variants'][0]['profile_id'])
        self.assertEqual('local-generation', value['assets']['config']['stage_profiles']['case_generation'])
        self.assertEqual('chatgpt-plan-responses-v1', value['assets']['config']['stage_profiles']['claim_mapping'])

    def test_unsupported_input_negative(self):
        errors = self.v['errors']
        self.assertIn('title', errors[0])
        self.assertIn('configured LLM profile', errors[1])
        self.assertEqual(['Use the advanced experiment definition for this dataset.'] * 2, errors[2:])

    def test_unavailable_selected_profile_negative(self):
        self.assertIsNotNone(self.v['unavailableError'])
        self.assertIn('configured LLM profile', self.v['unavailableError'])

    def test_constructed_scope_positive(self):
        value = self.v['sva']
        self.assertEqual('constructed', value['input']['population']['label_origin'])
        self.assertEqual(['The café open tomorrow.', 'The café opens tomorrow.'],
                         [window['id'] for window in value['input']['windows']])
        self.assertEqual([], value['attempts'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
