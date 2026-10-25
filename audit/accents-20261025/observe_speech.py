"""Explicit finite actual local voice/phone experiment; no hosted calls."""
import base64,copy,json,os,sys,time
from pathlib import Path
sys.path.insert(0,'/app')
from backends import plan,render
from acoustic_runtime import resolve_acoustic,transform_acoustic
O=Path(os.environ.get('ACCENT_EVIDENCE','/evidence'));O.mkdir(parents=True,exist_ok=True)
voices=[('af_heart','en-US'),('am_adam','en-US'),('bf_emma','en-GB'),('bm_george','en-GB'),('melo_en_au','en-AU'),('melo_en_in','en-IN')]
profile={'id':'local-english-accents-v1','provider':'local_english_accents','adapter_version':'local-english-accents-v1','model':'Kokoro-82M + MeloTTS-English','billing_mode':'local','voices':[{'id':v,'locale':l,'accent_description':l} for v,l in voices],'voice_settings':{'speed':1},'capabilities':['plain_text','ipa','prosody','multi_turn','voice_identity','locale','timed_pause']}
text='Hello. I can help you practise English. Shall we take the train to the city today?'
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2))
for voice,locale in voices:
 d=O/voice;d.mkdir(exist_ok=True)
 if (d/'preview.json').exists():continue
 turn={'id':'preview-'+voice,'speaker_id':'s1','voice_id':voice,'locale':locale,'operations':[{'kind':'text','text':text}],'gap_after_ms':0}
 packet=plan(profile,{'turns':[turn]});assert len(packet['pieces'])==1
 save(d/'preview-input.json',{'profile':profile,'plan':packet})
 value=render(profile,packet['pieces'][0]);(d/'preview.wav').write_bytes(base64.b64decode(value.pop('audio_base64')));save(d/'preview.json',value);print('Preview complete',voice,flush=True)
for voice,locale in voices[-2:]:
 d=O/voice
 if (d/'acoustic.json').exists():continue
 text='I think the train leaves at noon.';a=text.index('think');parameters={'reference_ipa':'θɪŋk','mutated_ipa':'sɪŋk','phone_start':None,'phone_end':None,'duration_ratio':None,'gain_db':None,'pitch_points':[],'pause_ms':None,'vot_ms':None}
 turn={'id':'acoustic-'+voice,'speaker_id':'s1','voice_id':voice,'locale':locale,'operations':[{'kind':'text','text':text}],'gap_after_ms':0,'acoustic_edits':[{'unit_id':'target','scope':{'start':a,'end':a+5},'controller':'phone_pair','taxonomy_id':'pronunciation.segmental.consonant_substitution','parameters':parameters}]}
 packet=plan(profile,{'turns':[turn]});piece=packet['pieces'][0];save(d/'acoustic-input.json',{'profile':profile,'plan':packet})
 response=render(profile,piece);audio=base64.b64decode(response['audio_base64']);(d/'reference.wav').write_bytes(audio)
 source={'piece_id':'accent-'+voice,'turn':piece,'native':response['receipt']['native'],'audio_base64':response['audio_base64']}
 resolved=resolve_acoustic(source);save(d/'resolved.json',resolved)
 save(d/'acoustic-response.json',response)
 final=transform_acoustic({**source,'step':resolved['steps'][0]});(d/'mutated.wav').write_bytes(base64.b64decode(final.pop('audio_base64')));save(d/'transformed.json',final)
 save(d/'acoustic.json',{'response':response,'resolved':resolved});print('Phone pair complete',voice,flush=True)
