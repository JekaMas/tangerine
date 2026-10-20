"""Acoustic worker orchestration: compile/resolve/transform; no model implementation."""
import base64,copy,json,unicodedata
from model_setup import installed

def controlled_plan(profile,render_plan,text_plan):
 from acoustic_plan import scopes
 kokoro=profile['provider']=='local_kokoro' and profile.get('adapter_version')=='kokoro-controlled-v1'
 azure=profile['provider']=='azure_speech'
 if not kokoro and not azure:raise ValueError('CAPABILITY_UNAVAILABLE')
 partition=[(t,scopes(t)) for t in render_plan['turns']]
 manifest={};vocabulary=None
 if kokoro:
  root,manifest=installed('kokoro-local-en-v1');vocabulary=json.loads((root/'config.json').read_text())['vocab']
 pieces=[]
 for turn,segments in partition:
  source=copy.deepcopy(turn);source.pop('acoustic_edits',None)
  packet=text_plan(profile,{'turns':[source]})
  edits=[e for _,_,_,group in reversed(segments) for e in group]
  if not kokoro:
   # Without native word timing only a complete, explicitly selected phrase is
   # controllable. Never manufacture a word boundary by re-rendering fragments.
   length=sum(len(op['text']) for op in turn['operations'])
   if any(e['scope']!={'start':0,'end':length} or e['controller'] in ('vowel_duration','vot_edit') or e['parameters'].get('phone_start') is not None for e in edits):raise ValueError('CAPABILITY_UNAVAILABLE')
   if any(e['controller']=='phone_pair' for e in edits) and 'ipa' not in profile.get('capabilities',[]):raise ValueError('CAPABILITY_UNAVAILABLE')
  cursor=0;assigned=0
  for piece in packet['pieces']:
   surface=piece['operations'][0]['text'];a,b=cursor,cursor+len(surface);cursor=b
   piece['surface_scope']={'start':a,'end':b}
   selected=[e for e in edits if a<=e['scope']['start'] and e['scope']['end']<=b]
   assigned+=len(selected)
   if selected:
    piece['acoustic_edits']=selected
    if kokoro:
     from acoustic_alignment import compile_scopes
     compile_scopes(piece,selected,a,vocabulary)
   pieces.append(piece)
  if assigned!=len(edits):raise ValueError('INPUT_CAPACITY_EXCEEDED')
 return {'pieces':pieces,'model_context':manifest}


def resolve_acoustic(packet):
 from acoustic_alignment import resolve
 from acoustic_controls import resolve_parameters
 audio=base64.b64decode(packet['audio_base64']);turn=packet['turn'];native=packet['native']
 steps=resolve(turn,native,(len(audio)-44)//2,packet['piece_id'])
 words=[w for d in native.get('decoder',[]) for w in d.get('word_tokens',[])]
 resolved=[];observations=[]
 for step in steps:
  value,observation=resolve_parameters(step,audio,words,turn['gap_after_ms']*24,turn.get('target_wpm'))
  if step['controller']=='vot_edit':
   from acoustic_controls import vot_landmarks,samples,Unmeasurable
   from acoustic_alignment import phone_interval
   decoder=next((x for x in native.get('acoustic_scopes',[]) if x['unit_id']==step['unit_id']),native.get('decoder',[{}])[0]);phones=decoder.get('phonemes','');token=next((i for i,c in enumerate(phones) if c not in 'ˈˌ '),None)
   if token is None or phones[token]!='p':raise Unmeasurable('initial_p_alignment_unavailable')
   stop=phone_interval(decoder,token,token+1,(len(audio)-44)//2)
   a,b=value['source_interval']['start'],value['source_interval']['end']
   value['landmarks']=vot_landmarks(samples(audio)[a:b],(max(0,stop[0]-a),min(b-a,stop[1]-a)))
   value['landmarks']['source_offset_samples']=a
   value['landmarks']['clock']='source_interval_relative_24000'
  resolved.append(value);observations.append(observation)
 return {'steps':resolved,'source_observations':observations,'alignment_basis':'kokoro_decoder_duration_proposal'}


def transform_acoustic(packet):
 from acoustic_controls import transform
 from acoustic_alignment import project_native,retain_pauses,mapped_point
 native=packet.get('native',{});step=packet['step'];paired=None;replacement=None;crop=None
 if step['controller']=='phone_pair':
  pairs=native.get('paired_mutations',{})
  paired=pairs.get(step['unit_id'],native.get('paired_mutation'))
  if paired is None:raise ValueError('ALIGNMENT_UNAVAILABLE')
  replacement=base64.b64decode(packet.get('replacement_base64') or paired['audio_base64'])
  scope=next((x for x in paired['native'].get('acoustic_scopes',[]) if x['unit_id']==step['unit_id']),None)
  if scope:crop={'start':scope['start'],'end':scope['end']}
 result=transform(base64.b64decode(packet['audio_base64']),step,replacement,crop)
 result['native']=project_native(native,result['clock_mapping'],result['sample_count'])
 if step['controller']=='pause_insert':
  for scope in result['native'].get('acoustic_scopes',[]):
   if scope['unit_id']==step['unit_id']:scope['start']=min(scope['start'],step['source_interval']['start'])
 if paired and crop:
  source_scope=next(x for x in paired['native']['acoustic_scopes'] if x['unit_id']==step['unit_id'])
  original_scope=next(x for x in native['acoustic_scopes'] if x['unit_id']==step['unit_id'])
  offset=step['source_interval']['start']-crop['start']
  for target_scope in result['native']['acoustic_scopes']:
   original=next(x for x in native['acoustic_scopes'] if x['unit_id']==target_scope['unit_id'])
   if (original['start'],original['end'])!=(original_scope['start'],original_scope['end']):continue
   paired_scope=next(x for x in paired['native']['acoustic_scopes'] if x['unit_id']==target_scope['unit_id'])
   target_scope['phonemes']=paired_scope['phonemes']
   target_scope['phone_intervals']=[{'start':x['start']+offset,'end':x['end']+offset} for x in paired_scope['phone_intervals']]

 return retain_pauses(native,result,step['source_piece_id'])
