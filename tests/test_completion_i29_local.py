"""Literal observations of the actual saved-case/local-checker flow. No calls.

Generation/mutations/speech belong to the same original case. A new attempt
explicitly chooses local checking; the failed Gemini attempt is not switched.
"""
import datetime,json,unittest,wave
from fractions import Fraction
from pathlib import Path
from urllib.parse import urlparse,parse_qs

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/iteration-29-saved-case-flow-20261026'
FAILED=ROOT/'data/iteration-29-local-full-flow-20261026'
ATTEMPT='a5f608ea-6719-4682-9f86-d6330a4707b2'
PREP='bc740ead-ff03-455f-805b-0fb4c7babcf1'

def read(name):return json.loads((DATA/name).read_text())
def go_events(path):return [json.loads(x) for x in path.read_text().splitlines() if x.startswith('{')]
def strings(value):
    if isinstance(value,str):yield value
    elif isinstance(value,dict):
        for v in value.values():yield from strings(v)
    elif isinstance(value,list):
        for v in value:yield from strings(v)

class CompletionI29Local(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=read('attempts/'+ATTEMPT+'-result.json')
        cls.attempt=read('attempts/'+ATTEMPT+'.json')['Attempt']
        cls.prep=read('preparations/'+PREP+'.json')
        cls.ledger=read('call-reconciliation.json');cls.dispatch=read('dispatches.json')
        cls.ui={r['name']:r for r in read('ui-observations.json')}
    def test_actual_local_comments_positive(self):
        self.assertEqual('complete',self.result['feedback_status']);self.assertEqual('llm',self.result['feedback']['origin'])
        feedback=self.result['feedback']['items'];self.assertEqual({'detected','missed','recommendation'},{i['kind'] for i in feedback})
        self.assertIn('books',next(i['text'] for i in feedback if i['kind']=='detected'))
        missed=next(i for i in feedback if i['kind']=='missed');self.assertEqual(['u3_lexis_collocation'],missed['unit_ids'])
        for word in ['make','do','Rehearse']:self.assertIn(word,next(i['text'] for i in feedback if i['kind']=='recommendation'))
        receipt=next(r for r in self.ledger['calls'] if r['receipt_id']==self.result['feedback']['receipt_id'])
        self.assertEqual(('feedback','complete','gpt-oss:20b','local'),tuple(receipt[k] for k in ['stage','outcome','model','billing_mode']))
        raw=next(d['response'] for d in self.dispatch if d['index']==receipt['dispatch_index'])
        outputs=[c['text'] for o in raw['output'] if o['type']=='message' for c in o['content'] if c['type']=='output_text']
        body=json.loads(outputs[-1].removeprefix('```json').removesuffix('```').strip())
        actual=set(strings(body))
        self.assertTrue(all(i['text'] in actual for i in feedback),'UI comments must originate in the actual model response')
    def test_source_quote_projection_positive(self):
        body=next(d['response'] for d in self.dispatch if d['index']==40)
        raw=json.loads(next(c['text'] for o in body['output'] if o['type']=='message' for c in o['content'] if c['type']=='output_text'))
        self.assertEqual({'start_cp':138,'end_cp':178,'exact_text':'Many requires a plural countable noun.'},raw['clauses'][0]['rationale_span'])
        reason=self.result['interpretation']['decisions'][0]['explanation']
        self.assertEqual(['“Many” requires a plural countable noun.'],reason['source_texts'])
        self.assertEqual((138,178,'supported'),tuple(reason['additional_assertions'][0][k] for k in ['start_cp','end_cp','judgment']))
        rows=go_events(DATA/'quote-sibling-green.jsonl');self.assertFalse(any(r['Action']=='fail' for r in rows))
        self.assertIn('TestExtractionQuoteProjectionPositive',{r.get('Test') for r in rows if r['Action']=='pass'})
    def test_source_quote_bounds_negative(self):
        rows=go_events(DATA/'quote-qualified-red.jsonl')
        self.assertIn('TestExtractionQuoteProjectionPositive',{r.get('Test') for r in rows if r['Action']=='fail'})
        rows=go_events(DATA/'quote-sibling-green.jsonl')
        for case in ['TestExtractionQuoteProjectionNegative','TestExtractionRepairCoordinatesNegative','TestInterpretationForwardRetractionNegative','TestInterpretationUndeclaredOverlapNegative']:
            self.assertIn(case,{r.get('Test') for r in rows if r['Action']=='pass'})
    def test_local_alias_transport_positive(self):
        calls=[d for d in self.dispatch if d['kind']=='local_responses'];self.assertEqual(8,len(calls))
        self.assertTrue(all(d['url']=='http://ollama:11434/v1/responses' and d['http_host']=='localhost:11434' and not d['credential_header_present'] for d in calls))
        self.assertEqual(([],[],37),(self.ledger['unmatched_dispatches'],self.ledger['unmatched_receipts'],self.ledger['native_receipts']))
        observed=go_events(DATA/'provider-final-green.jsonl')
        self.assertFalse(any(r['Action']=='fail' for r in observed))
        self.assertIn('TestLocalAliasHostPositive',{r.get('Test') for r in observed if r['Action']=='pass'})
    def test_local_alias_scope_negative(self):
        observed=go_events(DATA/'provider-final-green.jsonl')
        self.assertIn('TestLocalLoopbackHostNegative',{r.get('Test') for r in observed if r['Action']=='pass'})
        probes=json.loads((FAILED/'host-api-read-probes.json').read_text())
        self.assertIn('403',str(probes));self.assertIn('200',str(probes))
        self.assertTrue(all(r['billing_mode']=='local' for r in self.ledger['calls'] if r['model']=='gpt-oss:20b'))
    def test_unchanged_case_new_attempt_negative(self):
        self.assertEqual(('3029a559-14ca-4992-a984-b1c02cb067c4','f3ceb3d6-be27-4cb3-a88f-86dc27a81a9f','f4683a72-c1b2-42dd-91ec-7207eb9e7a04'),tuple(self.ledger[k] for k in ['case_version_id','source_key_id','audio_asset_id']))
        old=read('attempts/8db4a113-d8b6-430c-9bb1-eaec2fc19ff5-result.json')
        self.assertEqual('unavailable',old['feedback_status']);self.assertEqual({'denominator':'1','numerator':'60'},old['score']['composite']['exact_value_0_100'])
        self.assertEqual((29,4),(sum(d['kind']=='gemini_free' for d in self.dispatch),self.ledger['local_synthesis_requests']))
        new=[r for r in self.ledger['calls'] if r['model']=='gpt-oss:20b']
        self.assertEqual({'blind_claim_extraction','claim_mapping','feedback'},{r['stage'] for r in new})
        req=[json.loads(x) for x in (DATA/'requests.jsonl').read_text().splitlines()]
        self.assertFalse(any(r['forbidden'] or r['controlled_response_fixture'] or r['controlled_display_fixture'] for r in req))
        self.assertFalse(any(r['method']=='POST' and r['path'].endswith(('candidates:generate',':render')) for r in req))
    def test_new_attempt_oracle_persistence_positive(self):
        expectation=read('answer-expectation.json');self.assertEqual(expectation['answer'],self.attempt['answer_text'])
        req=[json.loads(x) for x in (DATA/'requests.jsonl').read_text().splitlines()]
        submitted=next(r for r in req if r['path'].endswith(':submit'))
        at=datetime.datetime.fromisoformat(expectation['authored_at']).timestamp();self.assertLess(at,submitted['started_at_unix'])
        counts=self.result['score']['counts'];self.assertEqual((2,1,1,0),tuple(counts[k] for k in ['true_errors','tp','fn','fp']))
        expected=100*(45*Fraction(2,3)+30*Fraction(1,2))/75;self.assertEqual(Fraction(60),expected)
        self.assertEqual({'denominator':'1','numerator':'60'},self.result['score']['composite']['exact_value_0_100'])
        self.assertEqual(['detection','correction'],self.result['score']['composite']['enabled_components'])
        self.assertEqual(('1','1'),tuple(self.result['score']['metrics']['explanation.graded_accuracy'][k] for k in ['numerator','denominator']))
        for name in ['draft-saved','draft-reopened']:self.assertEqual(expectation['answer'],next(f['value'] for f in self.ui[name]['fields'] if f['label']=='Your answer'))
        for name in ['result-before-reopen','result-reopened-settled']:
            row=self.ui[name];self.assertEqual(ATTEMPT,parse_qs(urlparse(row['url']).query)['attempt'][0])
            for item in self.result['feedback']['items']:self.assertIn(' '.join(item['text'].split()),' '.join(row['main'].split()))
            self.assertTrue(row['audio'][0]['paused']);self.assertIsNone(row['audio'][0]['error'])
        self.assertEqual(read('reopen-before.json'),read('reopen-after.json'))
    def test_complete_playback_replay_layout_positive(self):
        a,b=self.ui['listening-playing']['audio'][0],self.ui['listening-ended']['audio'][0]
        self.assertFalse(a['paused']);self.assertTrue(b['paused']);self.assertEqual((29.65,29.65),(b['time'],b['duration']))
        a,b=self.ui['missed-passage-playing']['audio'][0],self.ui['missed-passage-ended']['audio'][0]
        self.assertFalse(a['paused']);self.assertTrue(b['paused']);self.assertTrue(15.65<=a['time']<22.55);self.assertTrue(22.55<=b['time']<22.95)
        for width in [1280,390,320]:
            row=self.ui['completed-result-'+str(width)];self.assertEqual((width,width,'17px','24.65px',True,[]),tuple(row[k] for k in ['width','pageWidth','body','line','fontLoaded','alerts']))
        focus=self.ui['completed-mobile-menu-keyboard']['active'];self.assertEqual(('BUTTON','3px','solid'),tuple(focus[k] for k in ['tag','outline','style']))
        self.assertIn('generation-local-i29',self.ui['explicit-local-settings-settled']['main']);self.assertIn('gpt-oss:20b',self.ui['explicit-local-settings-settled']['main'])
    def test_complete_media_and_lab_positive(self):
        m=read('media-receipt.json');self.assertEqual((ATTEMPT,self.ledger['case_version_id'],self.ledger['audio_asset_id']),tuple(m[k] for k in ['attempt_id','case_version_id','audio_asset_id']))
        self.assertTrue(m['edits_disclosed'] and m['separate_saved_audio_disclosed']);self.assertEqual([],m['omitted_stages'])
        self.assertEqual({'audio','video'},{x['codec_type'] for x in m['probe']['streams']})
        with wave.open(str(DATA/'share/exercise.wav'),'rb') as w:self.assertEqual((1,24000,711600),(w.getnchannels(),w.getframerate(),w.getnframes()))
        aligned=read('audio-video-match.json');self.assertGreater(aligned['aligned_correlation'],.98);self.assertLessEqual(abs(aligned['codec_alignment_lag_samples']),48)
        video=next(x for x in read('gallery-observation.json')['media'] if x['id']=='completed-video');self.assertGreater(video['time'],0);self.assertIsNone(video['error'])
        self.assertLess(abs(video['height']-video['width']*9/16),1)
        old=read('gallery-poster-before.json');self.assertGreater(old['height'],old['width'])
        lab=read('lab-readback.json');self.assertTrue(lab['readback']);self.assertEqual(('FINISHED',0),(lab['status'],lab['export_inference_calls']))
        for path in ['flow/call-reconciliation.json','flow/dispatches.json','flow/documents.json','flow/media-receipt.json']:self.assertIn(path,lab['checked_files'])
    def test_feedback_linebreaks_positive(self):
        expected=[i['text'] for i in self.result['feedback']['items']]
        self.assertIn('\n• ',expected[2])
        self.assertNotIn(expected[2],self.ui['comments-desktop']['main'])
        for width in [1280,390,320]:
            rows=self.ui['final-feedback-'+str(width)]['feedback']
            self.assertEqual(expected,[r['text'] for r in rows[:3]])
            self.assertTrue(all(r['whiteSpace']=='pre-wrap' and r['size']=='17px' for r in rows))
            self.assertEqual(expected,[r['rendered'] for r in rows[:3]])
    def test_feedback_layout_and_data_negative(self):
        for width in [1280,390,320]:
            row=self.ui['final-feedback-'+str(width)]
            self.assertEqual((width,width,'17px','24.65px',True,[]),tuple(row[k] for k in ['width','pageWidth','body','line','fontLoaded','alerts']))
            self.assertNotIn('Constructed UI fixture:',row['main'])
            self.assertNotIn('Comments and practice recommendations are unavailable.',row['main'])
        self.assertEqual(read('reopen-before.json'),read('reopen-after.json'))

if __name__=='__main__':unittest.main(verbosity=2)
