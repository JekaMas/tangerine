"""Offline Melo English inference, explicit accent speakers and native timing.

The upstream VITS implementation and model are acquired at pinned revisions by
model-setup. This English-only frontend keeps BERT conditioning and the upstream
CMU phone/tone convention; espeak supplies OOV phones. No unrelated multilingual
models or packages are loaded. Native attention proposes timing, not heard truth.
"""
import base64,copy,hashlib,io,json,os,re,subprocess,sys,time,uuid
from accent_phones import arpa_phones,ipa_phones,route_voice
from model_setup import installed
from audio import normalize

CACHE={}

def assets():
 root,manifest=installed('melo-local-en-v1')
 if 'tokenizer' not in CACHE:
  from transformers import AutoTokenizer
  CACHE['tokenizer']=AutoTokenizer.from_pretrained(str(root/'bert'),local_files_only=True)
  dictionary={}
  for line in (root/'cmudict.rep').read_text().splitlines()[48:]:
   if '  ' not in line:continue
   word,phones=line.split('  ',1);dictionary[word]=arpa_phones(phones.replace(' - ',' ').split())
  CACHE['dictionary']=dictionary
 return root,manifest

def word_phones(text):
 from num2words import num2words
 word=text.upper().replace('’',"'")
 if word in CACHE['dictionary']:return CACHE['dictionary'][word]
 if re.fullmatch(r'\d+(?:\.\d+)?',text):
  expanded=num2words(float(text) if '.' in text else int(text))
  return [p for w in re.findall(r"[A-Za-z']+",expanded) for p in word_phones(w)]
 if text in '.!?,-':return [(text,0)]
 if text in ':;':return [(',',0)]
 raw=subprocess.run(['espeak-ng','-q','--ipa','-v','en-us',text],capture_output=True,text=True,check=True,timeout=10).stdout.strip()
 return ipa_phones(raw)

def frontend(text):
 assets();tokenizer=CACHE['tokenizer'];enc=tokenizer(text,return_offsets_mapping=True)
 ids=enc['input_ids'];offsets=enc['offset_mapping'];groups=[]
 for word in re.finditer(r"[A-Za-z]+(?:[’'][A-Za-z]+)*|\d+(?:\.\d+)?|[^\w\s]",text):
  a,b=word.span();indices=[i for i,(x,y) in enumerate(offsets) if y>a and x<b]
  if indices:groups.append([(i,a,b) for i in indices])
 rows=[{'phone':'_','tone':0,'bert_index':0,'start_cp':0,'end_cp':0}]
 for group in groups:
  a,b=group[0][1],group[-1][2];phones=word_phones(text[a:b]);counts=[0]*len(group)
  for _ in phones:counts[counts.index(min(counts))]+=1
  cursor=0
  for (i,_,_),count in zip(group,counts):
   for ph,tone in phones[cursor:cursor+count]:rows.append({'phone':ph,'tone':tone,'bert_index':i,'start_cp':a,'end_cp':b})
   cursor+=count
 rows.append({'phone':'_','tone':0,'bert_index':len(ids)-1,'start_cp':len(text),'end_cp':len(text)})
 return {'text':text,'input_ids':ids,'attention_mask':enc['attention_mask'],'rows':rows}

def replace_scope(rows,start,end,phones):
 matching=[i for i,r in enumerate(rows) if r['end_cp']>start and r['start_cp']<end]
 if not matching:raise ValueError('ALIGNMENT_UNAVAILABLE')
 a,b=matching[0],matching[-1]+1
 if rows[a]['start_cp']!=start or rows[b-1]['end_cp']!=end:raise ValueError('ALIGNMENT_UNAVAILABLE')
 old=rows[a:b];new=[]
 for i,(ph,tone) in enumerate(phones):
  source=old[min(len(old)-1,i*len(old)//max(1,len(phones)))];new.append({**source,'phone':ph,'tone':tone,'start_cp':start,'end_cp':end})
 return rows[:a]+new+rows[b:]

def compile_turn(turn):
 text=turn['operations'][0]['text'];f=frontend(text);edits=turn.get('acoustic_edits',[])
 offset=turn.get('surface_scope',{}).get('start',0);f['offset_cp']=offset
 for row in f['rows']:row['start_cp']+=offset;row['end_cp']+=offset
 references={}
 for e in edits:
  if e['controller']=='phone_pair':
   k=(e['scope']['start'],e['scope']['end']);ref=e['parameters']['reference_ipa']
   if k in references and references[k]!=ref:raise ValueError('CONSTRAINT_CONFLICT')
   references[k]=ref
 for (a,b),ref in sorted(references.items(),reverse=True):f['rows']=replace_scope(f['rows'],a,b,ipa_phones(ref))
 turn['melo_frontend']=f
 variants={}
 for scope,reference in references.items():
  changes=[];group=[e for e in edits if e['controller']=='phone_pair' and (e['scope']['start'],e['scope']['end'])==scope]
  for e in group:
   changed=e['parameters']['mutated_ipa'];left=0
   while left<min(len(reference),len(changed)) and reference[left]==changed[left]:left+=1
   right=0
   while right<min(len(reference),len(changed))-left and reference[-1-right]==changed[-1-right]:right+=1
   changes.append((left,len(reference)-right,changed[left:len(changed)-right if right else None]))
  changes=sorted(set(changes))
  if any(b>c for (a,b,_),(c,d,_) in zip(changes,changes[1:])):raise ValueError('CONSTRAINT_CONFLICT')
  changed=reference
  for a,b,replacement in reversed(changes):changed=changed[:a]+replacement+changed[b:]
  rows=replace_scope(f['rows'],*scope,ipa_phones(changed))
  from acoustic_alignment import scope_key
  for e in group:
   if e['unit_id'] in turn.get('recurring_unit_ids',[]):
    previous=variants.get(e['unit_id'],f)
    variants[e['unit_id']]={**f,'rows':replace_scope(previous['rows'],*scope,ipa_phones(changed))}
    continue
   repeated=sum(x['unit_id']==e['unit_id'] and x['controller']=='phone_pair' for x in edits)>1
   key=scope_key(e['unit_id'],e['scope']) if repeated else e['unit_id']
   variants[key]={**f,'rows':rows}
 turn['melo_variants']=variants
 return turn

def load_model():
 root,manifest=assets()
 if 'model' not in CACHE:
  import torch
  torch.set_num_threads(min(4,os.cpu_count() or 1))
  from transformers import AutoModelForMaskedLM
  sys.path.insert(0,str(root/'code'))
  from melo.models import SynthesizerTrn
  config=json.loads((root/'config.json').read_text());model=SynthesizerTrn(len(config['symbols']),config['data']['filter_length']//2+1,config['train']['segment_size']//config['data']['hop_length'],n_speakers=config['data']['n_speakers'],num_tones=config['num_tones'],num_languages=config['num_languages'],**config['model']).cpu().eval()
  model.load_state_dict(torch.load(root/'checkpoint.pth',map_location='cpu',weights_only=True)['model'],strict=True)
  CACHE.update(model=model,config=config,bert=AutoModelForMaskedLM.from_pretrained(str(root/'bert'),local_files_only=True).cpu().eval())
 return manifest

def synthesize(profile,turn,variant=None):
 import numpy as np,torch,soundfile
 from inference_capture import observe_method
 manifest=load_model();config=CACHE['config'];_,_,speaker=route_voice(turn['voice_id']);f=variant or turn.get('melo_frontend') or frontend(turn['operations'][0]['text']);rows=f['rows'];symbols={p:i for i,p in enumerate(config['symbols'])}
 if any(r['phone'] not in symbols for r in rows):raise ValueError('CAPABILITY_UNAVAILABLE')
 phones=[0]+[n for r in rows for n in (symbols[r['phone']],0)];tones=[0]+[n for r in rows for n in (r['tone']+7,0)];languages=[0]+[n for _ in rows for n in (2,0)];indexes=[rows[0]['bert_index']]+[r['bert_index'] for r in rows for _ in range(2)]
 calls=[];start=time.time()
 with torch.inference_mode(),observe_method(CACHE['bert'],'forward',calls,False),observe_method(CACHE['model'],'infer',calls,False):
  bert=CACHE['bert'](input_ids=torch.tensor([f['input_ids']]),attention_mask=torch.tensor([f['attention_mask']]),output_hidden_states=True).hidden_states[-3][0]
  features=bert[torch.tensor(indexes)].T.unsqueeze(0)
  output=CACHE['model'].infer(torch.tensor([phones]),torch.tensor([len(phones)]),torch.tensor([speaker]),torch.tensor([tones]),torch.tensor([languages]),torch.zeros(1,1024,len(phones)),features,sdp_ratio=.2,noise_scale=.6,noise_scale_w=.8,length_scale=1/(profile.get('voice_settings',{}).get('speed') or 1))
 samples=output[0][0,0].cpu().numpy();durations=output[1][0,0].sum(dim=0).cpu().tolist();buffer=io.BytesIO();soundfile.write(buffer,samples,config['data']['sampling_rate'],format='WAV',subtype='PCM_16');audio=normalize(buffer.getvalue());count=(len(audio)-44)//2
 clock=[0]
 for v in durations:clock.append(clock[-1]+v*config['data']['hop_length']*24000/config['data']['sampling_rate'])
 intervals=[{'start':min(count,round(clock[2*i])),'end':min(count,round(clock[min(len(clock)-1,2*i+3)]))} for i in range(len(rows))]
 scopes=[]
 for edit in turn.get('acoustic_edits',[]):
  a,b=edit['scope']['start'],edit['scope']['end'];indices=[i for i,r in enumerate(rows) if r['end_cp']>a and r['start_cp']<b]
  if not indices:raise ValueError('ALIGNMENT_UNAVAILABLE')
  x,y=indices[0],indices[-1]+1;scopes.append({'unit_id':edit['unit_id'],'surface_scope':edit['scope'],'start':intervals[x]['start'],'end':intervals[y-1]['end'],'phonemes':[r['phone'] for r in rows[x:y]],'phone_intervals':intervals[x:y]})
 words=[]
 for a,b in sorted(set((r['start_cp'],r['end_cp']) for r in rows if r['end_cp']>r['start_cp'])):
  idx=[i for i,r in enumerate(rows) if (r['start_cp'],r['end_cp'])==(a,b)];offset=f.get('offset_cp',0);words.append({'text':f['text'][a-offset:b-offset],'start_sample':intervals[idx[0]]['start'],'end_sample':intervals[idx[-1]]['end'],'basis':'melo_native_attention'})
 native={'model_manifest':manifest,'speaker_id':speaker,'frontend':f,'decoder':[{'phone_intervals':intervals,'phonemes':[r['phone'] for r in rows],'word_tokens':words,'sample_count':count,'timing_basis':'melo_native_attention_512_at_44100_resampled_24000','attention_durations':durations}], 'acoustic_scopes':scopes,'model_visible_calls':calls,'execution':{'device':'cpu','torch_num_threads':torch.get_num_threads(),'sdp_ratio':.2,'noise_scale':.6,'noise_scale_w':.8},'inference_receipt':{'id':str(uuid.uuid4()),'provider':'local_melo','model':manifest['repo'],'voice_id':turn['voice_id'],'speaker_id':speaker,'locale':turn['locale'],'started_at_unix':start,'finished_at_unix':time.time(),'audio_sha256':hashlib.sha256(audio).hexdigest()}}
 return audio,native,None

def render(profile,turn):
 audio,native,raw=synthesize(profile,turn)
 for unit,variant in turn.get('melo_variants',{}).items():
  changed,changed_native,_=synthesize(profile,turn,variant);native.setdefault('paired_mutations',{})[unit]={'audio_base64':base64.b64encode(changed).decode(),'audio_sha256':hashlib.sha256(changed).hexdigest(),'native':changed_native}
 return audio,native,raw
