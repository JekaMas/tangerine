"""Actual local repeated phone scopes and an unchanged correct exception."""
import base64,copy,json,os,re,sys
from pathlib import Path
sys.path.insert(0,'/app')
from backends import plan,render
from acoustic_runtime import resolve_acoustic,transform_acoustic
from acoustic_alignment import scope_key
voice=os.environ.get('RECURRING_VOICE','melo_en_au');locale='en-US' if voice=='af_heart' else 'en-AU'
O=Path('/evidence/speech-kokoro' if voice=='af_heart' else '/evidence/speech-grouped');O.mkdir(parents=True,exist_ok=True)
if (O/'observation.json').exists():print('Existing completed native observation retained.');raise SystemExit(0)
text='I think we should book now. I think the train is early. I think the platform is quiet. I think we can wait.'
matches=list(re.finditer(r'\bthink\b',text));changed=[0,1,3]
profile={'id':'local-english-accents-v1','provider':'local_english_accents','adapter_version':'local-english-accents-v1','model':'Kokoro-82M + MeloTTS-English','billing_mode':'local','voices':[{'id':voice,'locale':locale,'accent_description':locale}],'voice_settings':{'speed':1},'capabilities':['plain_text','ipa','prosody','multi_turn','voice_identity','locale','timed_pause']}
params={'reference_ipa':'θɪŋk','mutated_ipa':'sɪŋk','phone_start':None,'phone_end':None,'duration_ratio':None,'gain_db':None,'pitch_points':[],'pause_ms':None,'vot_ms':None}
edits=[{'unit_id':'habit','scope':{'start':matches[i].start(),'end':matches[i].end()},'controller':'phone_pair','taxonomy_id':'pronunciation.segmental.consonant_substitution','parameters':params} for i in changed]
turn={'id':'u1','speaker_id':'s1','voice_id':voice,'locale':locale,'operations':[{'kind':'text','text':text}],'gap_after_ms':0,'acoustic_edits':edits,'recurring_unit_ids':['habit']}
packet=plan(profile,{'turns':[turn]});assert len(packet['pieces'])==1;piece=packet['pieces'][0]
def save(name,value): (O/name).write_text(json.dumps(value,indent=2)+'\n')
save('input.json',{'profile':profile,'plan':packet,'expected_changed_indices':changed,'expected_correct_index':2})
if voice.startswith('melo_'):
 from melo_english import compile_turn
 offset=copy.deepcopy(piece);offset['surface_scope']={'start':100,'end':100+len(text)}
 for e in offset['acoustic_edits']:e['scope']={k:v+100 for k,v in e['scope'].items()}
 compile_turn(offset);assert all(r['start_cp']>=100 for r in offset['melo_frontend']['rows']);assert len(offset['melo_variants'])==1;save('offset-compile.json',offset)
response=render(profile,piece);save('response.json',response);(O/'reference.wav').write_bytes(base64.b64decode(response['audio_base64']))
native=response['receipt']['native'];expected=[scope_key('habit',edit['scope']) for edit in edits];assert set(native['paired_mutations'])=={'habit'}
for edit in edits:
 ref=next(r for r in native['acoustic_scopes'] if r['surface_scope']==edit['scope']);mut=next(r for r in native['paired_mutations']['habit']['native']['acoustic_scopes'] if r['surface_scope']==edit['scope']);expected_ref,expected_mut=(['th','ih','ng','k'],['s','ih','ng','k']) if voice.startswith('melo_') else ('θɪŋk','sɪŋk');assert ref['phonemes']==expected_ref and mut['phonemes']==expected_mut
current={'piece_id':'recurring-speech','turn':piece,'native':native,'audio_base64':response['audio_base64']};steps=[]
for index,edit in enumerate(sorted(edits,key=lambda e:e['scope']['start'],reverse=True)):
 resolved=resolve_acoustic(current);step=next(s for s in resolved['steps'] if s['surface_scope']==edit['scope']);result=transform_acoustic({**current,'step':step});save('transform-'+str(index)+'.json',result);steps.append({'scope':edit['scope'],'receipt':result['receipt']});current={**current,'native':result['native'],'audio_base64':result['audio_base64']}
(O/'mutated.wav').write_bytes(base64.b64decode(current['audio_base64']));save('final-native.json',current['native'])
word=lambda n:[w for d in n['decoder'] for w in d['word_tokens'] if w['text']=='think'][2]
before,after=word(native),word(current['native']);left=base64.b64decode(response['audio_base64'])[44+2*before['start_sample']:44+2*before['end_sample']];right=base64.b64decode(current['audio_base64'])[44+2*after['start_sample']:44+2*after['end_sample']];assert left==right and len(left)>100
save('observation.json',{'actual_local_synthesis':True,'scope_keys':expected,'shared_variant_keys':list(native['paired_mutations']),'mutated_opportunities':3,'eligible_opportunities':4,'correct_index':2,'correct_before':before,'correct_after':after,'correct_waveform_unchanged':left==right,'transform_receipts':steps,'scope':('One actual American Kokoro voice' if voice=='af_heart' else 'One actual Australian Melo voice')+', repeated theta→s in three of four think occurrences; one shared group variant; no universal auditory claim.'})
print(json.dumps({'actual_pairs':3,'correct_waveform_unchanged':True,'transform_model_calls':[s['receipt']['model_calls'] for s in steps]}))
