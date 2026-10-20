"""Independent literal numerical oracles, real Praat; no model/network doubles."""
import base64, copy, hashlib, pathlib, sys, unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'services/speech'))
import numpy as np
from acoustic_plan import meaningful,scopes
from acoustic_alignment import phone_interval,resolve,project_native
from acoustic_controls import transform,encode,samples,features,resolve_parameters,vot_landmarks,Unmeasurable


def parameters(**kw):
    p=dict(duration_ratio=None,gain_db=None,pitch_points=[],pause_ms=None,vot_ms=None,reference_ipa=None,mutated_ipa=None,phone_start=None,phone_end=None,expected_feature='controlled contrast',accepted_reference='stated audible comparison')
    p.update(kw);return p

def edit(kind='pitch_duration',a=0,b=5,**kw):
    return dict(unit_id='e1',utterance_id='u1',scope=dict(start=a,end=b),controller=kind,parameters=parameters(**kw))

def step(kind='pitch_duration',a=2400,b=16800,**kw):
    return dict(id='step-1',unit_id='e1',source_piece_id='piece-1',source_interval=dict(start=a,end=b),controller=kind,parameters=parameters(**kw),reference_piece_id=None)

def tone(n=24000,hz=140):
    return .15*np.sin(2*np.pi*hz*np.arange(n)/24000)+.06*np.sin(4*np.pi*hz*np.arange(n)/24000)

class AcousticControls(unittest.TestCase):
    def test_scope_positive(self):
        t=dict(operations=[dict(kind='text',text='A café opens.')],acoustic_edits=[edit('phone_pair',2,6,reference_ipa='kæfeɪ',mutated_ipa='kæfi')])
        rows=scopes(t);self.assertEqual([(s,a,b) for s,a,b,e in rows],[('A ',0,2),('café',2,6),(' opens.',6,13)])
    def test_scope_order_positive(self):
        a=edit('pause_insert',0,5,pause_ms=500);b=edit('pitch_duration',0,5,duration_ratio=1.2)
        rows=scopes(dict(operations=[dict(text='Hello there')],acoustic_edits=[a,b]));self.assertEqual([x['controller'] for x in rows[0][3]],['pitch_duration','pause_insert'])
    def test_overlap_negative(self):
        with self.assertRaisesRegex(ValueError,'CONSTRAINT_CONFLICT'):scopes(dict(operations=[dict(text='Hello there')],acoustic_edits=[edit(a=0,b=11,gain_db=2),edit(a=0,b=5,gain_db=3)]))
    def test_partial_word_negative(self):
        with self.assertRaisesRegex(ValueError,'ALIGNMENT_UNAVAILABLE'):scopes(dict(operations=[dict(text='Hello')],acoustic_edits=[edit(a=1,b=4,gain_db=2)]))
    def test_parameters_positive(self):
        for op in [edit('phone_pair',reference_ipa='pæn',mutated_ipa='bæn'),edit('vowel_duration',duration_ratio=.45,phone_start=1,phone_end=2),edit('pitch_duration',pitch_points=[dict(fraction=0,semitones=3),dict(fraction=1,semitones=8)]),edit('pause_insert',pause_ms=0),edit('vot_edit',vot_ms=10)]:meaningful(op)
    def test_gain_positive(self):
        raw=encode(tone());r=transform(raw,step(gain_db=6));y=samples(base64.b64decode(r['audio_base64']));x=samples(raw)
        self.assertTrue(np.array_equal(y[:2400],x[:2400]));self.assertTrue(np.array_equal(y[16800:],x[16800:]));self.assertAlmostEqual(np.sqrt(np.mean(y[3000:16000]**2))/np.sqrt(np.mean(x[3000:16000]**2)),10**(.3),places=3)
    def test_parameters_negative(self):
        for op in [edit(duration_ratio=0),edit('phone_pair',reference_ipa='p'),edit('pause_insert',pause_ms=-1),edit(pitch_points=[dict(fraction=.8,semitones=3),dict(fraction=.2,semitones=2)])]:
            with self.subTest(op=op),self.assertRaises(ValueError):meaningful(op)
    def test_unused_parameter_negative(self):
        with self.assertRaisesRegex(ValueError,'CONSTRAINT_CONFLICT'):meaningful(edit('pause_insert',pause_ms=1,gain_db=3))
    def test_decoder_positive(self):
        self.assertEqual(phone_interval(dict(pred_dur=[5,2,3,4,1]),1,3,10000),(2400,6600))
    def test_decoder_clamp_positive(self):
        self.assertEqual(phone_interval(dict(pred_dur=[[1,2,3,1]]),0,2,2500),(0,2500))
    def test_decoder_empty_negative(self):
        with self.assertRaisesRegex(ValueError,'ALIGNMENT_UNAVAILABLE'):phone_interval(dict(pred_dur=[0,0,2,1]),0,1,3000)
    def test_decoder_range_negative(self):
        with self.assertRaisesRegex(ValueError,'ALIGNMENT_UNAVAILABLE'):phone_interval(dict(pred_dur=[3,2,1]),0,2,3000)
    def test_pause_positive(self):
        raw=encode(tone());r=transform(raw,step('pause_insert',a=12000,b=16800,pause_ms=4000));pcm=np.frombuffer(base64.b64decode(r['audio_base64']),dtype='<i2',offset=44);old=np.frombuffer(raw,dtype='<i2',offset=44)
        noop=transform(raw,step("pause_insert",a=12000,b=16800,pause_ms=0));self.assertEqual(base64.b64decode(noop["audio_base64"]),raw)
        self.assertEqual(len(pcm),120000);self.assertTrue(np.all(pcm[12000:108000]==0));self.assertTrue(np.array_equal(pcm[:11880],old[:11880]));self.assertTrue(np.array_equal(pcm[108120:],old[12120:]))
    def test_pause_start_positive(self):
        r=transform(encode(tone()),step('pause_insert',a=0,b=100,pause_ms=1));self.assertEqual(r['sample_count'],24024);self.assertEqual(base64.b64decode(r['audio_base64'])[44:92],b'\0'*48)
    def test_pause_boundary_negative(self):
        with self.assertRaisesRegex(ValueError,'ALIGNMENT_UNAVAILABLE'):transform(encode(tone()),step('pause_insert',a=24000,b=24001,pause_ms=1))
    def test_no_silent_normalization_negative(self):
        r=transform(encode(tone()),step(gain_db=30));self.assertIn('clipping',r['observations']['warnings']);self.assertEqual(np.max(samples(base64.b64decode(r['audio_base64']))),32767/32768)
    def test_duration_positive(self):
        raw=encode(tone());r=transform(raw,step('vowel_duration',duration_ratio=.45));out=base64.b64decode(r['audio_base64']);self.assertLess(abs(r['sample_count']-(24000-14400+6480)),30);self.assertEqual(out[44:44+2*2400],raw[44:44+2*2400]);self.assertEqual(out[-2*(24000-16800):],raw[-2*(24000-16800):])
    def test_duration_pitch_positive(self):
        raw=encode(tone());r=transform(raw,step(duration_ratio=1.5));after=r['observations']['after'];self.assertAlmostEqual(after['median_f0_hz'],140,delta=3);self.assertGreater(r['sample_count'],30000)
    def test_duration_invalid_negative(self):
        with self.assertRaisesRegex(ValueError,'CONSTRAINT_CONFLICT'):meaningful(edit('vowel_duration',duration_ratio=-1,phone_start=0,phone_end=1))
    def test_duration_no_phone_negative(self):
        with self.assertRaisesRegex(ValueError,'CONSTRAINT_CONFLICT'):meaningful(edit('vowel_duration',duration_ratio=.5))
    def test_pitch_positive(self):
        r=transform(encode(tone()),step(pitch_points=[dict(fraction=0,semitones=12),dict(fraction=1,semitones=12)]));self.assertAlmostEqual(r['observations']['after']['median_f0_hz'],200,delta=5)
    def test_pitch_range_positive(self):
        varying=.1*np.sin(2*np.pi*np.cumsum(np.linspace(100,180,24000))/24000);raw=encode(varying)
        op=step();op['taxonomy_id']='pronunciation.suprasegmental.pitch_range';resolved,obs=resolve_parameters(op,raw);points=resolved['parameters']['pitch_points'];old=[x['semitones'] for x in obs['pitch_points']];new=[x['semitones'] for x in points];self.assertAlmostEqual(max(new)-min(new),2*(max(old)-min(old)),places=8)
    def test_pitch_unvoiced_negative(self):
        raw=encode(np.random.default_rng(12).normal(0,.02,24000))
        with self.assertRaises(Unmeasurable):transform(raw,step(pitch_points=[dict(fraction=0,semitones=4)]))
    def test_pitch_short_negative(self):
        with self.assertRaises(Unmeasurable):transform(encode(tone()),step(a=100,b=110,pitch_points=[dict(fraction=0,semitones=4)]))
    def test_phone_pair_positive(self):
        raw=encode(tone());changed=encode(tone(9600,200));r=transform(raw,step('phone_pair',a=0,b=24000,reference_ipa='pæn',mutated_ipa='bæn'),changed);self.assertEqual(r['sample_count'],9600);self.assertEqual({row['source_audio_sha256'] for row in r['sample_rows']},{hashlib.sha256(raw).hexdigest(),hashlib.sha256(changed).hexdigest()});self.assertAlmostEqual(r['observations']['after']['median_f0_hz'],200,delta=4)
        full=encode(tone(48000,200));r=transform(raw,step('phone_pair',a=2400,b=16800),full,dict(start=8000,end=20000));out=base64.b64decode(r['audio_base64']);self.assertEqual(r['sample_count'],21600);self.assertEqual(out[44:4844],raw[44:4844]);self.assertEqual(out[-14400:],raw[-14400:]);self.assertTrue(any(row['source_start']>=8000 and row['source_audio_sha256']==hashlib.sha256(full).hexdigest() for row in r['sample_rows']))
    def test_reference_private_positive(self):
        raw=encode(tone());other=encode(tone(12000,200));r=transform(raw,step('phone_pair',a=0,b=24000),other);self.assertNotEqual(r['audio_base64'],base64.b64encode(raw).decode());self.assertEqual(r['receipt']['model_calls'],0)
    def test_phone_pair_missing_negative(self):
        with self.assertRaisesRegex(ValueError,'CONSTRAINT_CONFLICT'):transform(encode(tone()),step('phone_pair'))
    def test_scope_alignment_missing_negative(self):
        turn=dict(acoustic_edits=[edit('vowel_duration',duration_ratio=.5,phone_start=0,phone_end=1)])
        with self.assertRaisesRegex(ValueError,'ALIGNMENT_UNAVAILABLE'):resolve(turn,{},1000,'piece')
    def vot_source(self):
        rng=np.random.default_rng(3);x=np.zeros(24000);x[480:600]=rng.normal(0,.4,120);x[600:2400]=rng.normal(0,.015,1800);x[2400:]=tone(21600);return encode(x)
    def test_vot_positive(self):
        raw=self.vot_source();land=vot_landmarks(samples(raw));self.assertTrue(480<=land['burst_sample']<600);self.assertLessEqual(abs(land['voicing_onset_sample']-2400),240);r=transform(raw,step('vot_edit',a=0,b=24000,vot_ms=0));expected=24000-(land['voicing_onset_sample']-land['burst_end_sample']);self.assertEqual(r['sample_count'],expected);self.assertGreater(r['observations']['landmarks']['measured_vot_ms'],0);self.assertEqual(base64.b64decode(r['audio_base64'])[44:44+2*land['burst_end_sample']],raw[44:44+2*land['burst_end_sample']])
    def test_vot_extend_positive(self):
        raw=self.vot_source();land=vot_landmarks(samples(raw));r=transform(raw,step('vot_edit',a=0,b=24000,vot_ms=150));self.assertEqual(r['sample_count'],24000-(land['voicing_onset_sample']-land['burst_end_sample'])+3600)
    def test_vot_unvoiced_negative(self):
        with self.assertRaises(Unmeasurable):vot_landmarks(np.zeros(24000))
    def test_vot_no_release_negative(self):
        with self.assertRaises(Unmeasurable):vot_landmarks(tone())
    def test_map_coverage_positive(self):
        r=transform(encode(tone()),step(duration_ratio=1.25));rows=r['sample_rows'];coverage=np.zeros(r['sample_count'],dtype=int)
        for row in rows:coverage[row['final_start']:row['final_end']]+=1
        self.assertTrue(np.all(coverage>=1));self.assertEqual(np.max(coverage),2);self.assertEqual(len({x['crossfade_group_id'] for x in rows if x['crossfade_group_id']}),2)
    def test_map_pause_positive(self):
        r=transform(encode(tone()),step('pause_insert',pause_ms=600));rows=r['sample_rows'];self.assertEqual(sum(x['final_end']-x['final_start'] for x in rows),r['sample_count']);pause=next(x for x in rows if x['kind']=='pause');self.assertEqual(pause['source_start'],pause['source_end']);self.assertEqual(pause['final_end']-pause['final_start'],14400)
    def test_map_empty_scope_negative(self):
        with self.assertRaises(ValueError):transform(encode(tone()),step(a=1,b=1,gain_db=3))
    def test_map_unknown_control_negative(self):
        with self.assertRaisesRegex(ValueError,'CAPABILITY_UNAVAILABLE'):transform(encode(tone()),step('unknown'))

    def test_features_positive(self):
        result=features(tone());self.assertEqual(result['prosody']['state'],'measured');self.assertLess(result['prosody']['f0_range_semitones'],.1);self.assertAlmostEqual(result['median_f0_hz'],140,delta=1)
    def test_relative_contour_positive(self):
        op=step(a=0,b=24000,pitch_points=[dict(fraction=0,semitones=0),dict(fraction=1,semitones=5)]);op['taxonomy_id']='pronunciation.suprasegmental.intonation_contour';resolved,obs=resolve_parameters(op,encode(tone()));points=resolved['parameters']['pitch_points'];self.assertAlmostEqual(100*2**(points[0]['semitones']/12),140,delta=1);self.assertAlmostEqual(points[1]['semitones']-points[0]['semitones'],5)
    def test_features_short_negative(self):
        result=features(tone(3000));self.assertEqual(result['prosody']['state'],'not_measurable');self.assertIsNone(result['prosody']['f0_range_semitones'])
    def test_relative_unvoiced_negative(self):
        op=step(a=0,b=24000,pitch_points=[dict(fraction=0,semitones=0),dict(fraction=1,semitones=5)]);op['taxonomy_id']='pronunciation.suprasegmental.intonation_contour'
        with self.assertRaises(Unmeasurable):resolve_parameters(op,encode(np.zeros(24000)))

    def test_composition_positive(self):
        ops=[edit('vowel_duration',0,5,duration_ratio=.5,phone_start=1,phone_end=2),edit('pitch_duration',0,5,pitch_points=[dict(fraction=0,semitones=3)],gain_db=4),edit('pause_insert',0,5,pause_ms=20)]
        rows=scopes(dict(operations=[dict(text='Hello')],acoustic_edits=ops));ordered=rows[0][3];self.assertEqual([x['controller'] for x in ordered],['vowel_duration','pitch_duration','pause_insert','pitch_duration']);self.assertIsNone(ordered[1]['parameters']['gain_db']);self.assertEqual(ordered[-1]['parameters']['gain_db'],4)
    def test_pause_composition_positive(self):
        from acoustic_runtime import transform_acoustic
        first=transform_acoustic(dict(audio_base64=base64.b64encode(encode(tone())).decode(),step=step('pause_insert',a=12000,b=16800,pause_ms=500),native={}))
        second=transform_acoustic(dict(audio_base64=first['audio_base64'],step=step(a=0,b=first['sample_count'],gain_db=3),native=first['native']))
        pauses=[r for r in second['sample_rows'] if r['kind']=='pause'];self.assertEqual([(r['final_start'],r['final_end']) for r in pauses],[(12000,24000)]);self.assertTrue(np.all(samples(base64.b64decode(second['audio_base64']))[12000:24000]==0))
    def test_duplicate_pause_negative(self):
        op=edit('pause_insert',pause_ms=20)
        with self.assertRaisesRegex(ValueError,'CONSTRAINT_CONFLICT'):scopes(dict(operations=[dict(text='Hello')],acoustic_edits=[op,op]))
    def test_conflicting_duration_negative(self):
        ops=[edit('vowel_duration',duration_ratio=.5,phone_start=1,phone_end=2),edit('pitch_duration',duration_ratio=2)]
        with self.assertRaisesRegex(ValueError,'CONSTRAINT_CONFLICT'):scopes(dict(operations=[dict(text='Hello')],acoustic_edits=ops))
    def test_mapped_decoder_positive(self):
        native=dict(decoder=[dict(pred_dur=[3,2,3,1],sample_count=3000,word_tokens=[dict(text='hello',start_sample=0,end_sample=3000)])]);mapped=project_native(native,[dict(source_start=0,source_end=3000,final_start=600,final_end=6600)],6600);self.assertEqual(phone_interval(mapped['decoder'][0],1,2,6600),(3000,6600));self.assertEqual(mapped['decoder'][0]['word_tokens'][0]['start_sample'],600)
    def test_zero_duration_symbol_positive(self):
        native=dict(decoder=[dict(pred_dur=[3,0,4,1],sample_count=2400,word_tokens=[])]);mapped=project_native(native,[dict(source_start=0,source_end=2400,final_start=0,final_end=2400)],2400);self.assertEqual(phone_interval(mapped['decoder'][0],0,2,2400),(0,2400))
    def test_mapped_empty_negative(self):
        with self.assertRaisesRegex(ValueError,'ALIGNMENT_UNAVAILABLE'):phone_interval(dict(phone_intervals=[dict(start=3,end=3)]),0,1,10)
    def test_projected_is_not_heard_negative(self):
        native=dict(decoder=[dict(pred_dur=[3,4,1],sample_count=2400,word_tokens=[])]);mapped=project_native(native,[dict(source_start=0,source_end=2400,final_start=0,final_end=4800)],4800);self.assertEqual(mapped['decoder'][0]['timing_basis'],'decoder_proposal_mapped_through_native_transform');self.assertNotIn('observed_ipa',mapped['decoder'][0])

    def test_rate_ratio_positive(self):
        from acoustic_controls import duration_ratio_for_rate
        words=[dict(start_sample=0,end_sample=4800),dict(start_sample=9600,end_sample=14400)];self.assertEqual(duration_ratio_for_rate(words,120),2)
        raw=encode(tone(48000));op=step(a=12000,b=36000);op['taxonomy_id']='fluency.speech_rate';words=[dict(text='one',phonemes='x',start_sample=a,end_sample=b) for a,b in [(0,6000),(12000,18000),(24000,36000),(42000,48000)]]
        resolved,_=resolve_parameters(op,raw,words,target_wpm=180);self.assertEqual(resolved['source_interval'],dict(start=12000,end=36000));self.assertAlmostEqual(resolved['parameters']['duration_ratio'],5/9)
        actual=base64.b64decode(transform(raw,resolved)['audio_base64']);self.assertEqual(actual[44:24044],raw[44:24044]);self.assertEqual(actual[-24000:],raw[-24000:])
    def test_rate_internal_gap_positive(self):
        from acoustic_controls import duration_ratio_for_rate
        words=[dict(start_sample=0,end_sample=4800),dict(start_sample=9600,end_sample=14400)];self.assertEqual(duration_ratio_for_rate(words,120,2400),1.75)
    def test_rate_silence_conflict_negative(self):
        from acoustic_controls import duration_ratio_for_rate
        with self.assertRaisesRegex(ValueError,'CONSTRAINT_CONFLICT'):duration_ratio_for_rate([dict(start_sample=0,end_sample=4800),dict(start_sample=9600,end_sample=14400)],600)
    def test_rate_missing_tokens_negative(self):
        from acoustic_controls import duration_ratio_for_rate
        with self.assertRaises(Unmeasurable):duration_ratio_for_rate([],120)

if __name__=='__main__':unittest.main()
