"""Diagnostic token, clip and clock arithmetic; no inferred sound from intent."""
from decimal import Decimal,localcontext
from fractions import Fraction
import unicodedata,uuid

def lexical(text):
 out=[]
 for source in text.split():
  token=unicodedata.normalize('NFC',source).lower()
  while token and unicodedata.category(token[0]).startswith('P'):token=token[1:]
  while token and unicodedata.category(token[-1]).startswith('P'):token=token[:-1]
  if token:out.append(token)
 return out

def wer(reference,hypothesis):
 a,b=lexical(reference),lexical(hypothesis)
 # Keep literal S/D/I counters, with stable substitution/deletion/insertion ties.
 prior=[(j,0,0,j) for j in range(len(b)+1)]
 for i,x in enumerate(a,1):
  current=[(i,0,i,0)]
  for j,y in enumerate(b,1):
   cost,s,d,ins=prior[j-1];diagonal=(cost+(x!=y),s+(x!=y),d,ins)
   cost,s,d,ins=prior[j];deletion=(cost+1,s,d+1,ins)
   cost,s,d,ins=current[j-1];insertion=(cost+1,s,d,ins+1)
   current.append(min([diagonal,deletion,insertion],key=lambda row:row[0]))
  prior=current
 errors,s,d,ins=prior[-1];ratio=Fraction(errors,len(a)) if a else None
 with localcontext() as ctx:
  ctx.prec=38;decimal=format(Decimal(ratio.numerator)/Decimal(ratio.denominator),'f') if ratio is not None else None
 return dict(reference_tokens=a,hypothesis_tokens=b,substitutions=s,deletions=d,insertions=ins,reference_count=len(a),exact_ratio=None if ratio is None else dict(numerator=str(ratio.numerator),denominator=str(ratio.denominator)),decimal=decimal,decimal_precision=38,reason=None if a else 'no_reference_tokens')

def clip_windows(intervals,samples,maximum=240000):
 windows=[]
 for a,b in sorted(intervals):
  if not 0<=a<b<=samples:raise ValueError('INVALID_AUDIO_INTERVAL')
  start,end=max(0,a-24000),min(samples,b+24000)
  while start<end:
   stop=min(start+maximum,end)
   if windows and start<=windows[-1][1] and stop-windows[-1][0]<=maximum:windows[-1]=(windows[-1][0],max(stop,windows[-1][1]))
   else:windows.append((start,stop))
   start=stop
 return windows

def transcribe_complete(model,path):
 segments,info=model.transcribe(path,language='en',task='transcribe',beam_size=5,temperature=0,word_timestamps=True,initial_prompt=None,condition_on_previous_text=False,vad_filter=False)
 rows=[]
 for segment in segments:
  rows.append(dict(id=segment.id,start=segment.start,end=segment.end,text=segment.text,avg_logprob=segment.avg_logprob,words=[dict(start=w.start,end=w.end,word=w.word,probability=w.probability) for w in segment.words or []]))
 return dict(hypothesis=''.join(s['text'] for s in rows),segments=rows,language=info.language,language_probability=info.language_probability,duration=info.duration,timing_unit='seconds',final_sample_rate_hz=24000,parameters=dict(language='en',task='transcribe',beam_size=5,temperature=0,word_timestamps=True,initial_prompt=None,condition_on_previous_text=False,vad_filter=False))

def judge_measurements(output,sha,method,version,interval,evidence):
 rows=[];length=interval['end']-interval['start']
 for finding in output['findings']:
  span=finding.get('clip_interval') or dict(start=0,end=length)
  if not 0<=span['start']<span['end']<=length:raise ValueError('INVALID_AUDIO_INTERVAL')
  status=finding['status']
  if status not in ['supported','contradicted','uncertain','not_applicable']:raise ValueError('DIAGNOSTIC_OUTPUT_INVALID')
  rows.append(dict(id=str(uuid.uuid4()),audio_sha256=sha,method_id=method,method_version=version,feature=finding['feature'],interval=dict(start=interval['start']+span['start'],end=interval['start']+span['end'],sample_rate_hz=24000),status='observed' if status in ['supported','contradicted'] else 'not_measurable' if status=='uncertain' else 'not_applicable',numeric_value=None,categorical_value='model_'+status if status in ['supported','contradicted'] else None,unit='category',evidence_asset_ids=list(evidence),reason=None if status in ['supported','contradicted'] else finding['reason'],target_unit_id=finding['unit_id'],auditory_finding=finding))
 return rows

def complete_judge_measurements(output,request,method):
 rows=judge_measurements(output,request['audio_sha256'],method,'auditory-v1',request['source_interval'],[])
 reported={(f['unit_id'],f['feature']) for f in output['findings']}
 for unit in request['planned_units']:
  features=[p['feature'] for p in unit['realization']['prosody']] or ['speech_realization']
  for feature in dict.fromkeys(features):
   if (unit['id'],feature) in reported:continue
   missing=dict(unit_id=unit['id'],feature=feature,status='uncertain',clip_interval=None,proposed_ipa=None,description='The model supplied no finding for this target.',reason='model_omitted_target')
   row=judge_measurements({'findings':[missing]},request['audio_sha256'],method,'auditory-v1',request['source_interval'],[])[0]
   # A native unknown is not a statement made by the model. Its original
   # visible response remains intact, and no extra inference is performed.
   row.pop('auditory_finding');rows.append(row)
 return rows
