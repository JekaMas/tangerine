"""I34 exact evidence readers and independent metric counterexamples.

The gate never repeats inference. Actual model cases originate in the opt-in Go
owner harness; failures and metric-only constructed packets remain labelled.
"""
from pathlib import Path
import copy
import importlib.util
import json
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'audit/iteration-34-local-generation-20261027'
OUT=ROOT/'data/iteration-34-local-generation-20261027'
spec=importlib.util.spec_from_file_location('local_generation_comparison',HERE/'compare.py')
compare=importlib.util.module_from_spec(spec);spec.loader.exec_module(compare)

def read(path):return json.loads(path.read_text())

class LocalGenerationAcceptance(unittest.TestCase):
    def selected(self):
        result=read(OUT/'comparison.json')
        self.assertIsNotNone(result['selected'],'No alternative satisfies the fixed functional contracts')
        return result,[r for r in result['rows'] if r['alternative']==result['selected']]

    def test_local_generation_positive(self):
        result,rows=self.selected();self.assertEqual(len(rows),2)
        row=next(r for r in rows if r['case']=='two-errors')
        self.assertTrue(row['admitted']);d=ROOT/row['directory'];prefix=row['id']+'-'
        clean=read(d/(prefix+'canonical_asset_id.json'));candidate=read(d/(prefix+'mutated_asset_id.json'))
        case=read(HERE/'PLAN.json')['cases'][0]
        assessed=compare.quality(case,clean,candidate)
        self.assertTrue(assessed['qualified'],assessed)
        self.assertEqual((assessed['TP'],assessed['FP'],assessed['FN'],assessed['TN']),(2,0,0,2))
        self.assertEqual({u['primary_taxonomy_id'] for u in candidate['planned_units']},{'grammar.nouns.number','lexis.collocation'})
        for u in candidate['planned_units']:
            self.assertEqual(u['weight'],1);self.assertTrue(u['explanation_eligible'])
            self.assertTrue(u['rationale_required_propositions']);self.assertTrue(u['rationale'])
        manifest=read(d/(prefix+'mutation_manifest_asset_id.json'))
        self.assertEqual(compare.replay(clean,manifest),{u['id']:u['surface_text'] for u in candidate['utterances']})
        prep=read(d/(prefix+'preparation.json'))
        self.assertEqual(prep['phase_states']['mutation'],'complete')
        self.assertIsNone(prep['audio_asset_id'],'This generation/key scope must not fabricate audio completion')
        native=[json.loads(l) for l in (OUT/'go-final.jsonl').read_text().splitlines() if l.strip()]
        observed={r.get('Test') for r in native if r.get('Action')=='pass'}
        self.assertTrue({'TestLocalMutationDerivedWeightPositive','TestLocalMutationSuppliedRationalePositive','TestLocalMutationExistingPropositionsPositive','TestLocalMutationExplicitSurfaceSpanPositive','TestLocalCorrectionScopeTrimPositive'}<=observed)

    def test_zero_error_negative(self):
        _,rows=self.selected();row=next(r for r in rows if r['case']=='zero-errors');d=ROOT/row['directory'];prefix=row['id']+'-'
        self.assertTrue(row['admitted']);c=read(d/(prefix+'mutated_asset_id.json'))
        self.assertEqual(c['planned_units'],[])
        self.assertEqual(read(d/(prefix+'mutation_manifest_asset_id.json'))['acoustic_edits'],[])
        self.assertTrue(all(u['canonical_text']==u['surface_text'] for u in c['utterances']))
        self.assertEqual((row['quality']['FP'],row['quality']['TN']),(0,4))
        self.assertIsNone(row['quality']['precision']);self.assertIsNone(row['quality']['recall'])
        native=[json.loads(l) for l in (OUT/'go-final.jsonl').read_text().splitlines() if l.strip()]
        observed={r.get('Test') for r in native if r.get('Action')=='pass'}
        self.assertTrue({'TestLocalMutationWeightExplicitNegative','TestLocalMutationRationaleUnknownNegative','TestLocalMutationMalformedRationaleNegative','TestLocalMutationSurfaceSpanAmbiguityNegative','TestLocalCorrectionScopePreserveNegative'}<=observed)

    def test_failure_retention_positive(self):
        for mode in ['runner','deadline','invalid-quote']:
            directory='controlled-deadline' if mode=='deadline' else 'controlled'
            native=[json.loads(l) for l in (OUT/directory/'native.jsonl').read_text().splitlines() if l.strip()]
            observed={r['Test'] for r in native if r.get('Action')=='pass' and r.get('Test')}
            self.assertIn('TestNativeLocalGenerationFailureModes/'+mode,observed)
            before=read(OUT/(directory+'/failure-'+mode+'-before.json'))
            after=read(OUT/(directory+'/failure-'+mode+'-after.json'))
            self.assertEqual(before['phase_states']['canonical_text'],'complete')
            self.assertEqual(before['phase_states']['mutation'],'failed')
            self.assertEqual(after['preparation']['phase_states']['mutation'],'complete')
            self.assertEqual(after['preparation']['settings_asset_id'],before['settings_asset_id'])
            self.assertEqual(after['preparation']['canonical_asset_id'],before['canonical_asset_id'])
            self.assertEqual(after['recovery_dispatches'],1)
            self.assertFalse(any(r.get('Action') in ['fail','skip'] and r.get('Test')=='TestNativeLocalGenerationFailureModes/'+mode for r in native))

    def test_failure_containment_negative(self):
        for mode,n in [('runner',2),('deadline',1),('invalid-quote',2)]:
            # A standalone same-profile500 is retried once by the existing
            # transport owner. Deadline never retries, semantic repair is one.
            directory='controlled-deadline' if mode=='deadline' else 'controlled'
            p=read(OUT/(directory+'/failure-'+mode+'-before.json'))
            for field in ['candidate_id','key_id','mutation_manifest_asset_id','audio_asset_id']:
                self.assertIsNone(p[field],(mode,field))
            self.assertIsNotNone(p['last_failure'])
            self.assertEqual(read(OUT/(directory+'/failure-'+mode+'-after.json'))['failed_dispatches'],n)
        retained=ROOT/'data/iteration-29-local-full-flow-20261026'
        for id in ['a2a1c235-1f9b-42c1-bbe4-82a614a7f47c','bace522e-56ab-427c-8410-abb25991f708','fb971a02-01c6-4010-981b-4e412691ff23']:
            p=read(retained/'preparations'/(id+'.json'))
            self.assertNotEqual(p['phase_states']['mutation'],'complete')
            self.assertIsNone(p['key_id'])

    def test_comparison_positive(self):
        result,rows=self.selected()
        self.assertEqual(len(result['rows']),16)
        self.assertEqual([a['requests'] for a in result['alternatives']],[2,2,2,2,2,2,2,2])
        self.assertEqual(result['api_charge_usd'],0);self.assertEqual(result['electricity'],'unmeasured')
        self.assertEqual(result['alternatives'][0]['quality'],compare.rates(1,1,1,6))
        self.assertEqual(result['alternatives'][1]['admitted'],0)
        self.assertIsNone(result['alternatives'][1]['quality']['precision'])
        self.assertTrue(all(r['total_seconds']<270 for r in rows))
        for r in result['rows']:
            d=ROOT/r['directory'];prefix=r['id']+'-'
            case=next(c for c in read(HERE/'PLAN.json')['cases'] if c['id']==r['case'])
            clean=read(d/(prefix+'canonical_asset_id.json')) if (d/(prefix+'canonical_asset_id.json')).exists() else None
            c=read(d/(prefix+'mutated_asset_id.json')) if (d/(prefix+'mutated_asset_id.json')).exists() else None
            self.assertEqual(r['quality'],compare.quality(case,clean,c))
        self.assertGreater(len((OUT/'resources.jsonl').read_text().splitlines()),1)
        self.assertIn('No arbitrary 122-category generation',result['proof_limit'])

    def test_quality_counterexamples_negative(self):
        # Metric-only packet. No claim of a provider or native-schema fixture.
        case=copy.deepcopy(read(HERE/'PLAN.json')['cases'][0])
        texts=['I have two books.','We make a decision.','We plan a book swap.','Please help with the event.']
        clean={'utterances':[dict(id='u'+str(i),canonical_text=t,surface_text=t) for i,t in enumerate(texts)]}
        c=copy.deepcopy(clean);c['planned_units']=[]
        for i,e in enumerate(case['expected']):
            t=texts[i].replace(e['canonical'],e['surface']);c['utterances'][i]['surface_text']=t;a=t.index(e['surface'])
            c['planned_units'].append(dict(id='e'+str(i),primary_taxonomy_id=e['category_id'],expected_judgment='true_error',text_spans=[dict(utterance_id='u'+str(i),span=dict(start_cp=a,end_cp=a+len(e['surface']),exact_text=e['surface']))],corrections=[dict(kind='replace',text=e['preferred_correction'],canonical=True)]))
        self.assertTrue(compare.quality(case,clean,c)['qualified'])
        c['planned_units'][0]['corrections'][0]['text']='books'
        q=compare.quality(case,clean,c);self.assertFalse(q['qualified']);self.assertEqual((q['TP'],q['FP'],q['FN']),(1,1,1));self.assertEqual(q['precision'],.5)
        duplicated=copy.deepcopy(c);unit=duplicated['planned_units'][1];unit['text_spans'][0]['span']['end_cp']-=len(' decision');unit['text_spans'][0]['span']['exact_text']='do a'
        q=compare.quality(case,clean,duplicated);self.assertEqual((q['TP'],q['FP'],q['FN']),(0,2,2));self.assertFalse(q['qualified'])
        c['planned_units'].append(dict(id='false-control',primary_taxonomy_id='lexis.collocation',expected_judgment='true_error',realization={'surface_text':'help with the event'},text_spans=[],corrections=[]))
        q=compare.quality(case,clean,c);self.assertFalse(q['qualified']);self.assertEqual(q['FP'],2);self.assertEqual(q['TN'],1)
        q=compare.quality(case,None,None);self.assertFalse(q['observed']);self.assertIsNone(q['accuracy'])
        self.assertEqual(compare.rates(0,0,0,0),dict(TP=0,FP=0,FN=0,TN=0,precision=None,recall=None,accuracy=None))
        zero=copy.deepcopy(read(HERE/'PLAN.json')['cases'][1]);z=copy.deepcopy(clean)
        z['utterances'][3]['canonical_text']+=' We can help with the event.'
        z['utterances'][3]['surface_text']=z['utterances'][3]['canonical_text']
        z['planned_units']=[]
        q=compare.quality(zero,z,z)
        self.assertTrue(q['qualified']);self.assertEqual(q['TN'],4)
        self.assertEqual(q['construction_deviations'],[dict(control='help with the event',requested_occurrences=1,actual_clean_occurrences=2)])

    def test_native_lab_positive(self):
        result,_=self.selected()
        expected=set()
        for path in (ROOT/'services/api/internal/app').glob('*_test.go'):
            expected.update(re.findall(r'^func (Test(?:LocalMutation|LocalCorrection|ReleaseMutation|Mutation|Preparation)[A-Za-z0-9_]*)\(',path.read_text(),re.M))
        native=[json.loads(l) for l in (OUT/'go-final.jsonl').read_text().splitlines() if l.strip()]
        observed=[r['Test'] for r in native if r.get('Action')=='pass' and r.get('Test')]
        self.assertEqual(set(observed),expected);self.assertEqual(len(observed),len(expected))
        self.assertFalse(any(r.get('Action') in ['fail','skip'] for r in native))
        self.assertEqual(len(result['native_calls']),result['dispatch_count'])
        self.assertEqual(len({r['receipt_id'] for r in result['native_calls']}),result['dispatch_count'])
        joined=[]
        for directory in ['', 'repair', 'final', 'repaired', 'deadline-profile', 'qwen-repaired']:
            joined+=compare.native_join(OUT/directory)
            events=[json.loads(l) for l in (OUT/directory/'native.jsonl').read_text().splitlines() if l.strip()]
            self.assertEqual((OUT/directory/'native-exit-code').read_text(),'0')
            self.assertFalse(any(e.get('Action') in ['fail','skip'] for e in events))
        self.assertEqual(result['native_calls'],joined)
        self.assertEqual(result['native_replays'],compare.native_join(OUT/'projection-replay'))
        self.assertEqual(len(result['native_replays']),4)
        self.assertEqual((OUT/'projection-replay/native-exit-code').read_text(),'0')
        replay=[json.loads(l) for l in (OUT/'projection-replay/native.jsonl').read_text().splitlines() if l.strip()]
        self.assertTrue(any(e.get('Action')=='pass' and e.get('Test')=='TestNativeLocalGenerationProjectionReplay' for e in replay))
        self.assertFalse(any(e.get('Action') in ['fail','skip'] for e in replay))
        lab=read(OUT/'lab-readback.json');self.assertTrue(lab['readback'])
        self.assertEqual(len(lab['runs']),8)
        for r in lab['runs']:self.assertEqual(r['status'],'FINISHED')
        self.assertEqual(read(OUT/'lab-readback/comparison.json'),result)
        self.assertEqual((OUT/'lab-readback/source/specification/v2/prompts/generate-v1.txt').read_text(),(ROOT/'specification/v2/prompts/generate-v1.txt').read_text())
        self.assertEqual((OUT/'lab-readback/source/services/api/internal/app/mutation_correction_projection.go').read_text(),(ROOT/'services/api/internal/app/mutation_correction_projection.go').read_text())

    def test_no_fallback_negative(self):
        for directory in ['', 'repair', 'final', 'repaired', 'deadline-profile', 'qwen-repaired']:
            d=OUT/directory
            for row in read(d/'dispatches.json'):
                self.assertEqual(row['url'],'http://ollama:11434/v1/responses')
                self.assertFalse(row['authorization_present'])
                self.assertIn(row['request']['model'],['tangerine-qwen35-9b-review-nospec-20261021','gpt-oss:20b','huihui_ai/Qwen3.8-abliterated:27b-q4_K_M'])
            self.assertEqual(read(d/'cleanup.json')['remaining'],'')
        for r in read(OUT/'comparison.json')['native_calls']:
            self.assertIn(r['budget_method'],['conservative_utf8_bytes','tokenizer'])

if __name__=='__main__':unittest.main()
