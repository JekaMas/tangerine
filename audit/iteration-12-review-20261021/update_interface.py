"""Exact optional-review runtime overlay; original source/import DTOs stay preserved."""
from pathlib import Path
import json
def dump(v,**kw):return json.dumps(v,indent=2)+'\n'
R=Path(__file__).resolve().parents[2];V=R/'specification/v2';C=V/'contracts'
props={k:{'type':'string'} for k in ['id','purpose','case_version_id','attempt_id','base_result_id','statement','resolution','failure_code','new_result_id','new_case_version_id','unit_correspondence_id','created_at','input_modality']}
props.update(schema_version={'const':'2.0.0'},status={'enum':['ready','running','complete','failed']},revision={'type':'integer','minimum':0},origin={'const':'llm'},person_id={'type':'null'},qualification_ids={'type':'array','maxItems':0},findings={'anyOf':[{'$ref':'llm-review-output.schema.json'},{'type':'null'}]})
schemas={'review-view':dict(type='object',properties=props,required=list(props),additionalProperties=False),'review-list':dict(type='array',items={'$ref':'review-view.schema.json'}),'review-selection-result':dict(type='object',properties={'schema_version':{'const':'2.0.0'},'complete':{'type':'boolean'},'reviews':{'type':'array','items':{'$ref':'review-view.schema.json'}}},required=['schema_version','complete','reviews'],additionalProperties=False)}
for name,d in schemas.items():
 d.update({'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'https://tangerine.invalid/schemas/'+name+'.schema.json','title':name});raw=json.dumps(d,indent=2)+'\n';(C/(name+'.schema.json')).write_text(raw);(R/'services/api/internal/contracts/schemas'/(name+'.schema.json')).write_text(raw)
ops=[dict(id='create_optional_review',method='POST',path='/api/v1/reviews',request='review-request',response='review-view',success=201,effect='Freeze explicit case review, answer reconsideration or exact dispute; do not dispatch.',revision=False),dict(id='list_optional_reviews',method='GET',path='/api/v1/reviews',request=None,response='review-list',success=200,effect='Read up to50 saved summaries, filtered by case_version_id/attempt_id; X-Tangerine-Next-Cursor is the next saved ID.',revision=False),dict(id='read_optional_review',method='GET',path='/api/v1/reviews/{id}',request=None,response='review-view',success=200,effect='Read saved actual findings and immutable selected versions; never dispatch.',revision=False),dict(id='run_optional_review',method='POST',path='/api/v1/reviews/{id}:run',request=None,response='review-view',success=200,effect='Explicit synchronous Run/Resume; retain failed state with503, original result and admitted checkpoints.',revision=True),dict(id='reconsider_selected_answers',method='POST',path='/api/v1/reviews/{id}:reconsider',request='reconsider-request',response='review-selection-result',success=200,effect='Explicit same-audio selected attempts only; partial failed selection503 resumes unfinished children.',revision=False)]
(V/'domain/review-runtime-operations.yaml').write_text(dump({'description':'Normative current internal runtime projection for optional LLM review/disputes. review-runtime.md maps original logical operations and retained native source DTOs.','operations':ops},sort_keys=False))
paths={}
for op in ops:
 responses={str(op['success']):{'description':op['effect'],'content':{'application/json':{'schema':{'$ref':op['response']+'.schema.json'}}}}}
 if op['id'] in ['run_optional_review','reconsider_selected_answers']:responses['503']={'description':'Saved failed review or incomplete selected-answer action; explicit retry retains original authoritative data.','content':{'application/json':{'schema':{'$ref':op['response']+'.schema.json'}}}}
 parameters=[]
 if '{id}' in op['path']:parameters.append(dict(name='id',**{'in':'path'},required=True,schema={'type':'string'}))
 if op['method']=='POST':parameters.append(dict(name='Idempotency-Key',**{'in':'header'},required=True,schema={'type':'string'}))
 if op['revision']:parameters.append(dict(name='If-Match',**{'in':'header'},required=True,schema={'type':'string'}))
 if op['id']=='list_optional_reviews':
  parameters += [dict(name=k,**{'in':'query'},schema={'type':'string'}) for k in ['case_version_id','attempt_id','cursor']]
 operation=dict(operationId=op['id'],description=op['effect'],parameters=parameters,responses=responses)
 if op['request']:operation['requestBody']=dict(required=True,content={'application/json':{'schema':{'$ref':op['request']+'.schema.json'}}})
 paths.setdefault(op['path'],{})[op['method'].lower()]=operation
(C/'review-runtime.openapi.yaml').write_text(dump({'openapi':'3.1.0','info':{'title':'Tangerine optional review runtime','version':'2.0.0'},'servers':[{'url':'http://localhost:3000'}],'paths':paths},sort_keys=False))
