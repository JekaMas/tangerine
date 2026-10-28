"""Selected real acoustic observations and independent review counterexamples.

These readers perform zero inference. They do not promote model disagreement
to sound confirmation, or rendered controls to observed user activation.
"""
import base64
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/iteration-26-acoustic-20261026'
REVIEW=ROOT/'data/completion-leftovers-20261028/i26'
sys.path.insert(0,str(ROOT/'services/speech'))
from category_validation import compare_probe


def review_gaps(facts):
    gaps=[]
    if not facts.get('interaction',{}).get('activation_observed'):
        gaps.append('native interaction unobserved')
    layouts=facts.get('layouts',[])
    if not layouts:
        gaps.append('typography omitted')
    for view in layouts:
        if view.get('width')!=view.get('pageWidth') or view.get('size')!='17px' or not view.get('fontLoaded'):
            gaps.append('unreadable or unobserved layout')
    if facts.get('source_scope')!='I26 selected saved clips':gaps.append('source mismatch')
    for clip in facts.get('audio',[]):
        if clip.get('src')!='/audio/'+clip.get('case','')+'/'+clip.get('role','')+'.wav':gaps.append('media mismatch')
    if facts.get('claimed_all_122_confirmed'):gaps.append('unsupported universal qualification')
    if facts.get('requested_benchmark_calls',0):gaps.append('excluded benchmark campaign')
    return gaps


class CompletionI26(unittest.TestCase):
    def test_acoustic_positive(self):
        retained=ROOT/'data/category-realization-20261025/observations-gemini31/pronunciation.suprasegmental.linking_resyllabification'
        probe=json.loads((retained/'withheld.json').read_text())
        response=retained/'readmitted-response.json'
        if not response.exists():response=retained/'response.json'
        self.assertEqual('confirmed',compare_probe(probe,json.loads(response.read_text()))['audio_confirmation'])
        expected={'clean':'contradicted','mutated':'supported','acceptable':'contradicted','misleading_metadata':'contradicted'}
        for case in ['assimilation','weak-form','thought-group','intonation-function']:
            directory=DATA/'selected'/case
            frozen=json.loads((directory/'frozen.json').read_text())
            actual=json.loads((directory/'response.json').read_text())
            dispatch=json.loads((directory/'dispatch.json').read_text())
            self.assertEqual(('complete',200),(dispatch['outcome'],dispatch['http_status']))
            self.assertEqual(frozen['packet'],dispatch['input'])
            self.assertEqual((200,'free_tier','gemini-3.1-flash-lite'),
                             (actual['wire']['http_status'],actual['wire']['profile']['billing_mode'],actual['receipt']['model']))
            self.assertEqual(1,actual['receipt']['inference_calls'])
            wire=actual['wire']['request']
            self.assertEqual(frozen['packet']['prompt'],wire['system_instruction'])
            self.assertEqual(frozen['packet']['input'],json.loads(wire['input'][0]['text']))
            clips=[r for r in wire['input'] if r['type']=='audio']
            self.assertEqual(4,len(clips))
            for received,source in zip(clips,frozen['probe']['withheld']):
                self.assertEqual((ROOT/source['audio_path']).read_bytes(),base64.b64decode(received['data']))
            if case=='assimilation':
                result=compare_probe(frozen['probe'],actual)
                self.assertEqual(('confirmed',0,True),(result['audio_confirmation'],result['false_alarms'],result['controls_passed']))
                self.assertEqual(expected,{c['role']:c['actual'] for c in result['cases']})

    def test_acoustic_negative(self):
        results={case:json.loads((DATA/'selected'/case/'comparison.json').read_text())
                 for case in ['weak-form','thought-group','intonation-function']}
        weak=results['weak-form']
        self.assertEqual(('not_realized',0),(weak['audio_confirmation'],weak['false_alarms']))
        self.assertTrue(all(c['actual']=='contradicted' for c in weak['cases']))
        for case in ['thought-group','intonation-function']:
            row=results[case]
            self.assertEqual('uncertain',row['audio_confirmation'])
            self.assertTrue(row['physical_auditory_conflict'])
            self.assertEqual('supported',row['physical']['status'])
        self.assertEqual(14400,results['thought-group']['physical']['observations'][0]['actual']['additional_samples'])
        self.assertEqual(1,results['intonation-function']['false_alarms'])
        measured=results['intonation-function']['physical']['observations']
        self.assertLess(measured[0]['actual_semitone_windows'][-1],measured[0]['actual_semitone_windows'][0])
        self.assertGreater(measured[1]['actual_semitone_windows'][-1],measured[1]['actual_semitone_windows'][0])

    def test_review_positive(self):
        path=REVIEW/'browser-observations.json'
        if not path.exists():self.skipTest('Selected listening UI observations not yet retained.')
        facts=json.loads(path.read_text())
        if not facts.get('interaction',{}).get('activation_observed'):
            self.skipTest('Actual playback, keyboard and Refresh observations are required; rendered controls alone are insufficient.')
        self.assertEqual([],review_gaps(facts))
        self.assertEqual([1280,390,320],[v['width'] for v in facts['layouts']])
        self.assertEqual(20,len(facts['audio']))
        self.assertTrue(all(c['readyState']==4 and c['error'] is None for c in facts['audio']))
        self.assertGreater(facts['interaction']['advanced_time'],0)
        self.assertTrue(facts['interaction']['other_player_paused'])
        self.assertTrue(facts['interaction']['keyboard_observed'])
        self.assertTrue(facts['interaction']['refresh_observed'])

    def test_ux_omission_negative(self):
        self.assertIn('native interaction unobserved',review_gaps(dict(build_passed=True,screenshot_count=20)))

    def test_typography_omission_negative(self):
        self.assertIn('typography omitted',review_gaps(dict(font_family='Source Sans 3')))
        self.assertIn('unreadable or unobserved layout',review_gaps(dict(layouts=[dict(width=320,pageWidth=640,size='10px',fontLoaded=True)])))

    def test_evidence_mismatch_negative(self):
        self.assertIn('source mismatch',review_gaps(dict(source_scope='another exercise')))
        self.assertIn('media mismatch',review_gaps(dict(audio=[dict(case='weak-form',role='acceptable',src='/audio/other/clean.wav')])) )
        self.assertIn('unsupported universal qualification',review_gaps(dict(claimed_all_122_confirmed=True)))
        self.assertIn('excluded benchmark campaign',review_gaps(dict(requested_benchmark_calls=50)))


if __name__=='__main__':unittest.main(verbosity=2)
