from pathlib import Path
import json,yaml
R=Path(__file__).resolve().parents[2];C=R/'specification/v2/contracts'
schemas={
'preparation-render-request':dict(type='object',properties={'preparation_id':dict(type='string',minLength=1),'render_attempt':dict(type='integer',minimum=1)},required=['preparation_id','render_attempt'],additionalProperties=True,description='Foreground generated-preparation action. Harmless additive interface fields are ignored; the two named fields own the effective action.'),
'preparation-summary':dict(type='object',properties={'id':dict(type='string'),'revision':dict(type='integer',minimum=0),'phase_states':{'$ref':'preparation-state.schema.json#/properties/phase_states'},'audio_available':dict(type='boolean'),'last_failure':{'$ref':'preparation-state.schema.json#/properties/last_failure'},'next_render_attempt':dict(type='integer',minimum=1)},required=['id','revision','phase_states','audio_available','last_failure'],additionalProperties=False),
'preparation-list':dict(type='object',properties={'items':dict(type='array',items={'oneOf':[{'$ref':'preparation-state.schema.json'},{'$ref':'preparation-summary.schema.json'}]}),'next_cursor':dict(type=['string','null'])},required=['items','next_cursor'],additionalProperties=False),
'preparation-render-error':dict(type='object',properties={'preparation':{'anyOf':[{'$ref':'preparation-summary.schema.json'},dict(type='null')]},'code':{'$ref':'error-response.schema.json#/properties/code'}},required=['preparation','code'],additionalProperties=False)
}
for name,d in schemas.items():
 d.update({'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'https://tangerine.invalid/schemas/'+name+'.schema.json','title':name});raw=json.dumps(d,indent=2)+'\n';(C/(name+'.schema.json')).write_text(raw);(R/'services/api/internal/contracts/schemas'/(name+'.schema.json')).write_text(raw)
ops=[dict(id='render_preparation',method='POST',path='/api/v1/preparations/{id}:render',request='preparation-render-request',response='preparation-summary',success=200,effect='Render the frozen generated candidate synchronously with saved pieces, key, sample map and final audio. Explicit retry reuses completed work.',activity='prepare',revision=False),dict(id='play_preparation_audio',method='GET',path='/api/v1/preparations/{id}/audio',request=None,response='binary:audio/wav',success=200,effect='Serve completed saved WAV bytes with byte ranges, without synthesis or key disclosure.',activity='teacher',revision=False)]
p=R/'specification/v2/domain/operations.yaml';text=p.read_text();start=text.index('  - id: list_preparations');end=text.index('  - id:',start+10);part=text[start:end].replace('response: list:preparation-state','response: preparation-list');text=text[:start]+part+text[end:]
if 'id: render_preparation' not in text:
 for op in ops:text+=''.join('  '+line+'\n' for line in yaml.safe_dump([op],sort_keys=False,allow_unicode=True).splitlines())
p.write_text(text)
p=C/'openapi.yaml';text=p.read_text();addition=''
for op in ops:
 if op['path']+':' in text:continue
 response={'description':op['effect'],'content':{('audio/wav' if op['request'] is None else 'application/json'):{'schema':({'type':'string','format':'binary'} if op['request'] is None else {'$ref':op['response']+'.schema.json'})}}}
 operation={'operationId':op['id'],'description':op['effect'],'tags':[op['activity']],'parameters':[dict(name='id',**{'in':'path'},required=True,schema=dict(type='string'))],'responses':{'200':response}}
 if op['request']:
  operation['requestBody']=dict(required=True,content={'application/json':dict(schema={'$ref':op['request']+'.schema.json'})});operation['responses']['422']={'description':'Retained failed checkpoint with a canonical application error','content':{'application/json':{'schema':{'$ref':'preparation-render-error.schema.json'}}}}
 else:operation['responses']['206']={'description':'Byte-range playback of the same stored asset','headers':{'Content-Range':{'schema':{'type':'string'}}},'content':{'audio/wav':{'schema':{'type':'string','format':'binary'}}}}
 fragment=yaml.safe_dump({op['path']:{op['method'].lower():operation}},sort_keys=False,allow_unicode=True);addition+=''.join('  '+line+'\n' for line in fragment.splitlines())
text=text.replace('components:\n',addition+'components:\n',1)
start=text.index('  /api/v1/preparations:\n');end=text.index('  /',start+10);part=text[start:end];a=part.index('        "200":');b=part.index('        "400":',a);part=part[:a]+'''        "200":
          description: Keyset page; view=public returns safe preparation summaries.
          content:
            application/json:
              schema:
                $ref: preparation-list.schema.json
'''+part[b:];text=text[:start]+part+text[end:];p.write_text(text)
print('Updated four typed contracts and the generated-preparation render/playback operations.')
