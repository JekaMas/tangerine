"""Model-visible realization intent; the complete key stays in native storage."""
from diagnostic_audio import unit_features

def project_audio_intent(request):
 targets=[]
 for unit in request['planned_units']:
  realization={k:v for k,v in unit['realization'].items() if not k.startswith('observed_') and v is not None}
  if realization.get('mode')=='temporal_fluency' and realization.get('canonical_ipa')==realization.get('intended_ipa'):
   realization.pop('canonical_ipa',None);realization.pop('intended_ipa',None)
  if 'prosody' in realization:realization['prosody']=[{k:v for k,v in p.items() if k not in ['observation','evidence_ids'] and v is not None} for p in realization['prosody']]
  controllers=[]
  for edit in request.get('acoustic_edits',[]):
   if edit['unit_id']!=unit['id']:continue
   controllers.append(dict(controller=edit['controller'],text_scope_codepoints=edit['scope'],parameters={k:v for k,v in edit['parameters'].items() if k!='accepted_reference' and v is not None}))
  target=dict(unit_id=unit['id'],features=unit_features(unit,request),realization=realization,controllers=controllers)
  if target['features']==['speech_realization'] and realization.get('mode')=='temporal_fluency':
   target['judgment_question']='For speech_realization, assess the intended pause or speaking pace in realization. Word presence alone does not establish this timing target.'
  targets.append(target)
 return {**{k:request[k] for k in ['canonical_text','surface_text','task_target','source_interval','clip_duration_seconds'] if k in request},'targets':targets}
