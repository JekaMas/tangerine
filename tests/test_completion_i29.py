"""Independent literal oracles over actual I29 observations. Never dispatch models.

The complete-flow case deliberately fails if required recommendations are still
unavailable; a readable partial result must never be relabelled full acceptance.
"""
from pathlib import Path
from urllib.parse import urlparse,parse_qs
from fractions import Fraction
import copy,json,wave,hashlib,unittest

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/iteration-29-full-flow-20261026'
AUDIT=ROOT/'audit/iteration-29-full-flow-20261026'
ATTEMPT='8db4a113-d8b6-430c-9bb1-eaec2fc19ff5'
CASE='3029a559-14ca-4992-a984-b1c02cb067c4'
PREP='bc740ead-ff03-455f-805b-0fb4c7babcf1'
ROUTES={'/','/prepare','/attempts','/audio','/listen','/reviews','/reports','/sources','/settings','/recovery','/cleanup'}

def read(name):return json.loads((DATA/name).read_text())
def asset(id):return read('assets/'+id+'.json')
def events(name):return [json.loads(x) for x in (DATA/name).read_text().splitlines() if x.startswith('{')]
def passed(name):return {x.get('Test') for x in events(name) if x['Action']=='pass'}
def text(s):return ' '.join(s.split())

def flow_errors(packet, native):
    """Development evidence counterexamples only; no product readiness gate."""
    errors=[]
    for key in ['attempt_id','case_version_id','audio_asset_id','source_key_id']:
        if packet.get(key)!=native[key]:errors.append(key+' mismatch')
    if not native['complete_flow'] or packet.get('omitted_stages')!=[]:errors.append('required live stage incomplete')
    if packet.get('answer_origin')!='constructed partial developer answer':errors.append('answer origin')
    if packet.get('reference_origin')!='independent pre-score arithmetic and literal source expectations':errors.append('reference origin')
    if packet.get('performance_campaign')!='excluded':errors.append('performance campaign')
    if packet.get('unexecuted_claimed_passed'):errors.append('unexecuted claim')
    if not packet.get('edits_disclosed') or not packet.get('separate_saved_audio_disclosed'):errors.append('media editing disclosure')
    return errors

def review_errors(packet,facts,native):
    errors=flow_errors(packet,native)
    for part in ['ui_ux','typography','evidence']:
        if not packet.get(part,{}).get('observations') or not packet.get(part,{}).get('references'):errors.append(part+' unsupported')
    if {urlparse(r['url']).path for r in facts['routes']}!=ROUTES:errors.append('route scope')
    if not facts['faults'] or not any(r['name']=='mobile-menu-keyboard' for r in facts['routes']):errors.append('interaction proof')
    for r in facts['layouts']:
        if r['pageWidth']!=r['width'] or r['body']!='17px' or r['line']!='24.65px' or not r['fontLoaded']:errors.append('readability')
    if packet.get('actionable_caption_px',0)<13:errors.append('actionable caption readability')
    return errors

class CompletionI29(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f=read('browser-observations.json');cls.by={r['name']:r for r in cls.f['routes']}
        cls.prep=read('preparations/'+PREP+'.json');cls.key=read('keys/'+PREP+'.json')
        cls.attempt=read('attempts/'+ATTEMPT+'.json')['Attempt'];cls.result=read('attempts/'+ATTEMPT+'-result.json')
        cls.requests=events('requests.jsonl');cls.dispatch=read('dispatches.json');cls.native=read('call-reconciliation.json')
        cls.selected_native=json.loads((ROOT/'data/iteration-29-saved-case-flow-20261026/call-reconciliation.json').read_text())
    def packet(self):return json.loads((AUDIT/'REVIEW.json').read_text())
    def test_request_positive(self):
        r=self.prep['exercise_request']
        self.assertEqual(('Organising a neighbourhood book swap',2,90,'B1',2),tuple(r[k] for k in ['topic','speaker_count','text_length_words','english_level','mutation_count']))
        self.assertEqual(['grammar.nouns.number','lexis.collocation'],r['category_ids']);self.assertEqual(['minor'],r['severity_levels'])
        self.assertEqual(['af_heart','bf_emma'],r['speaker_voice_ids']);self.assertEqual(94,self.prep['canonical_word_count'])
        self.assertTrue(all(v=='complete' for v in self.prep['phase_states'].values()))
    def test_mutation_replay_positive(self):
        manifest=asset(self.prep['mutation_manifest_asset_id']);self.assertEqual(2,len(manifest['edits']))
        self.assertEqual({'grammar.nouns.number','lexis.collocation'},{u['primary_taxonomy_id'] for u in self.key['units']})
        for turn in self.key['utterances']:
            original=turn['canonical_text'];out=original
            for edit in sorted([e for e in manifest['edits'] if e['utterance_id']==turn['id']],key=lambda e:(e['start_cp'],e['order']),reverse=True):
                self.assertEqual(edit['original_text'],original[edit['start_cp']:edit['end_cp']]);out=out[:edit['start_cp']]+edit['replacement_text']+out[edit['end_cp']:]
            self.assertEqual(turn['surface_text'],out)
        self.assertIn('many book to contribute',self.key['utterances'][0]['surface_text']);self.assertIn('to do it a fun event',self.key['utterances'][2]['surface_text'])
    def test_unclaimed_acoustic_negative(self):
        m=asset(self.prep['mutation_manifest_asset_id']);self.assertEqual(([],[]),(m['acoustic_edits'],m['acoustic_intents']))
        self.assertTrue(all(u['verification']=='candidate' for u in self.key['units']))
        self.assertTrue(all(s['accent_evidence']=='not_verified' for s in self.key['speakers']))
    def test_audio_positive(self):
        path=DATA/'assets'/(self.prep['audio_asset_id']+'.wav')
        with wave.open(str(path),'rb') as w:self.assertEqual((1,24000,711600),(w.getnchannels(),w.getframerate(),w.getnframes()))
        self.assertEqual(self.prep['audio_sha256'],hashlib.sha256(path.read_bytes()).hexdigest())
        pieces=[r['response']['receipt'] for r in self.dispatch if r['kind']=='speech_worker' and r['url'].endswith('/piece')]
        self.assertEqual(4,len(pieces));self.assertEqual({'af_heart','bf_emma'},{p['voice_id'] for p in pieces});self.assertTrue(all(p['billing_mode']=='local' for p in pieces))
    def test_answer_persistence_positive(self):
        expected=read('answer-expectation.json');self.assertEqual(expected['answer'],self.attempt['answer_text'])
        for name in ['draft-saved','draft-reopened']:
            self.assertEqual(expected['answer'],next(f['value'] for f in self.by[name]['fields'] if f['label']=='Your answer'))
        self.assertEqual({'detection':True,'classification':False,'correction':True,'explanation':False},self.attempt['task_components'])
    def test_exact_score_positive(self):
        counts=self.result['score']['counts'];self.assertEqual((2,1,1,0),tuple(counts[k] for k in ['true_errors','tp','fn','fp']))
        expected=100*(45*Fraction(2,3)+30*Fraction(1,2))/75
        self.assertEqual(Fraction(60),expected);self.assertEqual({'numerator':'60','denominator':'1'},self.result['score']['composite']['exact_value_0_100'])
        self.assertEqual(['detection','correction'],self.result['score']['composite']['enabled_components'])
    def test_optional_explanation_positive(self):
        m=self.result['score']['metrics']['explanation.graded_accuracy'];self.assertEqual(('1','1'),(m['numerator'],m['denominator']))
        self.assertIn('Optional explanation: 100.0%',self.by['scoring-result-observation']['main'])
        self.assertNotIn('explanation',self.result['score']['composite']['enabled_components'])
    def test_feedback_retry_preserves_score_negative(self):
        history=[json.loads(p.read_text()) for p in (DATA/'result-history').glob('*.json')]
        self.assertGreaterEqual(len(history),3)
        self.assertTrue(all(r['score']==self.result['score'] for r in history))
        rows=[r for r in self.requests if r['method']=='POST' and r['path'].endswith(':retry-feedback')];self.assertGreaterEqual(len(rows),1)
        self.assertTrue(all(ATTEMPT in r['path'] for r in rows))
        first=min(r['started_at_unix'] for r in rows)
        import datetime
        later=[r for r in self.native['calls'] if next(d for d in read('documents.json') if d['id']==r['receipt_id'])['started_at']>datetime.datetime.fromtimestamp(first,datetime.timezone.utc).isoformat().replace('+00:00','Z')]
        self.assertTrue(later);self.assertEqual({'feedback'},{r['stage'] for r in later})
    def test_provider_provenance_positive(self):
        self.assertEqual(([],[]),(self.native['unmatched_dispatches'],self.native['unmatched_receipts']))
        hosted=[d for d in self.dispatch if d['kind']=='gemini_free'];self.assertEqual(len(hosted),self.native['native_receipts'])
        self.assertTrue(all(r['model']=='gemini-3.1-flash-lite' and r['billing_mode']=='free_tier' for r in self.native['calls']))
        self.assertTrue(all(d['credential_header_present'] and urlparse(d['url']).hostname=='generativelanguage.googleapis.com' for d in hosted))
        self.assertEqual(CASE,self.native['relation']['case_version_id']);self.assertEqual(self.prep['key_id'],self.native['relation']['source_key_id'])
    def test_failures_retained_negative(self):
        self.assertTrue(any(d.get('http_status')==503 for d in self.dispatch));self.assertTrue(any('transport_error' in d for d in self.dispatch))
        self.assertTrue(any(r['outcome']=='schema_error' for r in self.native['calls']));self.assertTrue(any(r['outcome']=='deadline' for r in self.native['calls']))
    def test_interpretation_repair_positive(self):
        for name in ['TestExtractionRepairCoordinatesPositive','TestExtractionRelationCoordinateAliasesPositive','TestExtractionRedundantAttachmentPositive']:
            self.assertIn(name,passed('attachment-green.jsonl'))
        inputs=[json.loads(x['request']['input'])[-1].get('content','') for x in self.dispatch if x['kind']=='gemini_free']
        self.assertTrue(any('correction_span' in x and '[90,95)' in x and '[116,121)' in x for x in inputs))
        self.assertEqual(1,len(self.result['interpretation']['claims']))
    def test_interpretation_guess_negative(self):
        for name in ['TestExtractionRepairCoordinatesNegative','TestExtractionRelationCoordinateAliasesNegative','TestExtractionSelfRelationNegative','TestInterpretationForwardRetractionNegative','TestInterpretationUndeclaredOverlapNegative']:
            self.assertIn(name,passed('attachment-green.jsonl'))
    def test_eleven_routes_positive(self):
        self.assertEqual(ROUTES,{urlparse(r['url']).path for r in self.f['routes']})
        self.assertTrue(all(r['title'] for r in self.f['routes']))
        self.assertIn('No exercises yet',self.by['empty-library-1280']['main'])
        self.assertIn('Organising a neighbourhood book swap',self.by['populated-library-desktop']['main'])
    def test_read_recovery_positive(self):
        faults={(r['name'],r['phase']):r for r in self.f['faults']}
        for name in ['audio','attempts','prepare','reviews','reports','sources','settings','cleanup','recovery','listen','library-final']:
            self.assertTrue(faults[name,'error']['alerts'],name);self.assertEqual([],faults[name,'recovered']['alerts'],name)
            self.assertTrue(any(not b['disabled'] for b in faults[name,'error']['buttons']),name)
    def test_backend_leak_negative(self):
        for r in [*self.f['routes'],*self.f['faults']]:self.assertNotIn('private backend canary',r['main'])
        rows=[r for r in self.requests if r['scenario']=='library-final-persistent' and r['path']=='/api/v1/library'];self.assertEqual([503,503,503],[r['status'] for r in rows])
    def test_library_retention_positive(self):
        r=next(r for r in self.f['faults'] if r['name']=='library-final' and r['phase']=='error')
        self.assertEqual(1,len([a for a in r['links'] if a['text']=='Listen and answer']))
        self.assertTrue(any(CASE in a['href'] for a in r['links']))
    def test_library_append_negative(self):
        for r in self.f['faults']:
            if r['name']=='library-final':self.assertEqual(1,len([a for a in r['links'] if a['text']=='Listen and answer']),r['phase'])
    def test_audio_status_positive(self):
        for width in [1280,390,320]:
            s=self.by['layout-audio-final-'+str(width)]['main'];self.assertIn('4/4 audio pieces saved · Audio saved',s);self.assertNotIn('Ready to assemble',s)
    def test_audio_unassembled_negative(self):
        s=self.by['controlled-audio-unassembled']['main'];self.assertIn('Ready to assemble',s);self.assertIn('Resume audio',s);self.assertNotIn('· Audio saved',s)
        self.assertEqual('complete',self.prep['phase_states']['render'])
        rows=[r for r in self.requests if r['scenario']=='controlled-audio-unassembled']
        self.assertTrue(rows);self.assertTrue(all(r['method']=='GET' for r in rows))
    def test_actionable_caption_positive(self):
        for row in read('typography-controls.json'):
            self.assertEqual(row['width'],row['pageWidth'])
            self.assertTrue(all(x['size']=='14px' and x['width']>0 for x in [*row['amount'],*row['severity']]))
    def test_taxonomy_controls_negative(self):
        rows=read('preparation-options.json')['categories'];self.assertEqual((122,114,8),(len(rows),sum(not r['control'] for r in rows),sum(r['control'] for r in rows)))
        self.assertTrue(all(r['family']=='acceptable_variant' for r in rows if r['control']))
    def test_layout_positive(self):
        for route in ROUTES:
            views=[r for r in self.f['routes'] if urlparse(r['url']).path==route]
            for size in [(1280,720),(390,844),(320,740)]:self.assertTrue(any((r['width'],r['height'])==size for r in views),(route,size))
        for r in self.f['layouts']:
            self.assertEqual(r['width'],r['pageWidth']);self.assertEqual(('17px','24.65px',True),(r['body'],r['line'],r['fontLoaded']))
    def test_keyboard_positive(self):
        for name in ['mobile-menu-keyboard','keyboard-back-to-navigation','keyboard-forward-to-content']:
            self.assertEqual('3px',self.by[name]['active']['outline'])
        self.assertEqual('BUTTON',self.by['keyboard-forward-to-content']['active']['tag'])
        self.assertTrue(self.by['keyboard-skip-to-content']['url'].endswith('#main-content'))
    def test_finite_replay_positive(self):
        a,b=self.by['replay-missed-playing']['audio'][0],self.by['replay-missed-ended']['audio'][0]
        self.assertFalse(a['paused']);self.assertTrue(b['paused']);self.assertEqual(a['src'],b['src']);self.assertTrue(15.65<=a['time']<22.55);self.assertTrue(22.55<=b['time']<22.95)
        self.assertEqual((29.65,29.65),(a['duration'],b['duration']))
    def test_full_playback_positive(self):
        a,b=self.by['listening-playing']['audio'][0],self.by['listening-ended']['audio'][0]
        self.assertFalse(a['paused']);self.assertTrue(b['paused']);self.assertEqual(29.65,b['time']);self.assertEqual(a['src'],b['src']);self.assertIsNone(b['error'])
    def test_reports_positive(self):
        rows=read('saved-reports.json');self.assertEqual(1,len(rows))
        report=read('reports-'+rows[0]['id']+'.json');self.assertIn('constructed',json.dumps(report));self.assertIn('Constructed observations.',self.by['layout-reports-settled-320']['main'])
    def test_experiment_not_run_negative(self):
        rows=read('saved-experiments.json');self.assertEqual(1,len(rows))
        saved=read('experiments-'+rows[0]['id']+'.json');self.assertEqual('planned',saved['status'])
        self.assertFalse(any(r['method']=='POST' and r['path'].endswith(':run') for r in self.requests))
    def test_reads_no_inference_negative(self):
        self.assertEqual(read('reopen-before.json')['dispatches'],read('reopen-after.json')['dispatches'])
        self.assertFalse(any(r['forbidden'] for r in self.requests));self.assertEqual(0,self.native['export_inference_calls'])
    def test_reopen_positive(self):
        a,b=self.by['result-before-reopen'],self.by['result-reopened']
        self.assertEqual(a['main'],b['main']);self.assertEqual(a['audio'][0]['src'],b['audio'][0]['src']);self.assertEqual(ATTEMPT,parse_qs(urlparse(b['url']).query)['attempt'][0])
        self.assertTrue(b['audio'][0]['paused'])
    def test_media_positive(self):
        m=read('media-receipt.json');self.assertEqual((ATTEMPT,CASE,self.prep['audio_asset_id']),(m['attempt_id'],m['case_version_id'],m['audio_asset_id']))
        self.assertTrue(m['edits_disclosed'] and m['separate_saved_audio_disclosed']);self.assertGreater(float(m['probe']['format']['duration']),29.65)
        self.assertEqual({'audio','video'},{x['codec_type'] for x in m['probe']['streams']})
        aligned=read('audio-video-match.json');self.assertEqual((711600,711600),(aligned['source_samples'],aligned['video_decoded_samples']))
        self.assertGreater(aligned['aligned_correlation'],.98);self.assertLessEqual(abs(aligned['codec_alignment_lag_samples']),48)
        shown=read('gallery-observation.json')['media'];video=next(x for x in shown if x['tag']=='VIDEO')
        self.assertEqual(181.632,video['duration']);self.assertGreater(video['time'],0);self.assertIsNone(video['error'])
    def test_lab_positive(self):
        r=read('lab-readback.json');self.assertTrue(r['readback']);self.assertEqual(('FINISHED',0),(r['status'],r['export_inference_calls']))
        self.assertIn('flow/call-reconciliation.json',r['files']);self.assertIn('flow/media-receipt.json',r['files'])
    def test_flow_positive(self):self.assertEqual([],flow_errors(self.packet(),self.selected_native),'Actual required recommendations must complete; partial scores/builds cannot close I29.')
    def test_flow_negative(self):
        n=copy.deepcopy(self.selected_native);n['complete_flow']=False;self.assertIn('required live stage incomplete',flow_errors(self.packet(),n))
        p=self.packet();p['audio_asset_id']='old-recording';self.assertIn('audio_asset_id mismatch',flow_errors(p,self.selected_native))
    def test_review_positive(self):self.assertEqual([],review_errors(self.packet(),self.f,self.selected_native))
    def test_ux_omission_negative(self):
        p=self.packet();p.pop('ui_ux');self.assertIn('ui_ux unsupported',review_errors(p,self.f,self.selected_native))
    def test_typography_omission_negative(self):
        p=self.packet();p.pop('typography');self.assertIn('typography unsupported',review_errors(p,self.f,self.selected_native))
        p=self.packet();p['actionable_caption_px']=10;self.assertIn('actionable caption readability',review_errors(p,self.f,self.selected_native))
    def test_evidence_mismatch_negative(self):
        native=copy.deepcopy(self.selected_native);native['complete_flow']=True
        baseline=self.packet();baseline['omitted_stages']=[]
        self.assertEqual([],flow_errors(baseline,native))
        for key,value in [('attempt_id','other-attempt'),('case_version_id','other-key'),('reference_origin','candidate gold'),('unexecuted_claimed_passed',['planned']),('performance_campaign','50 p95 calls'),('edits_disclosed',False)]:
            p=copy.deepcopy(baseline);p[key]=value;self.assertTrue(flow_errors(p,native),key)

if __name__=='__main__':unittest.main(verbosity=2)
