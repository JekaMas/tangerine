from pathlib import Path
import json,shutil
R=Path(__file__).resolve().parents[2];V=R/'specification/v2';D=V/'contracts'
def load(n):return json.loads((D/(n+'.schema.json')).read_text())
def save(n,d):(D/(n+'.schema.json')).write_text(json.dumps(d,indent=2)+'\n')
scope=dict(type='string',enum=['full_named_release','partial_export','analysis_companion','mirror'],description='Actual selected export scope. An absent historic value means partial_export; raw completeness never proves original full-release acquisition.')
components=dict(type='array',items=dict(type='object',properties=dict(component=dict(type='string',minLength=1,maxLength=128),member_globs=dict(type='array',items=dict(type='string',minLength=1)),expected=dict(anyOf=[dict(type='string',pattern='^(0|[1-9][0-9]*)$'),dict(type='null')]),reconciliation_reason=dict(type='string')),required=['component','member_globs','expected','reconciliation_reason'],additionalProperties=False),description='Actual documented expected file populations and explanations; not invented private source counts.')
for n in ['source-release-request','source-release']:
 d=load(n);d['properties'].update(scope_kind=scope,component_expectations=components);save(n,d)
d=load('format-binding-request');d['properties']['mapping_program']={'$ref':'source-mapping-program.schema.json'};d['properties']['binding_program_asset_id']=load('source-format-binding')['properties']['binding_program_asset_id'];save('format-binding-request',d)
remote=dict(type='object',properties={k:dict(type='string') for k in ['endpoint','method','cursor_field','cursor_location','records_pointer','next_cursor_pointer','end_pointer','total_pointer','auth_header','auth_prefix','dataset_version','count_unit']},additionalProperties=False)
remote['properties'].update(headers=dict(type='object',additionalProperties=dict(type='string')),query=dict(type='object',additionalProperties=dict(type='string')),body=dict(type='object'),initial_cursor=dict(anyOf=[dict(type='string'),dict(type='null')]),end_value={},empty_page_is_end=dict(type='boolean'))
remote['required']=list(remote['properties']);remote['properties']['record_identity_pointer']=dict(type='string',minLength=1);d=load('connector-request');d['properties']['remote_spec']=remote;save('connector-request',d)
# Sync only the changed authored schemas for new-input admission. Global indexes,
# manifests and evidence fingerprints are reconciled once after the stable batch.
for n in ['source-release-request','source-release','format-binding-request','connector-request']:
 shutil.copyfile(D/(n+'.schema.json'),R/'services/api/internal/contracts/schemas'/(n+'.schema.json'))
