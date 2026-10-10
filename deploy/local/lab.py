"""MLflow SDK edge: registry and diagnostic copies only, never model inference."""
import json,sys,hashlib,os,tempfile,time,subprocess,uuid,datetime,contextlib
from pathlib import Path
os.environ['MLFLOW_DISABLE_TELEMETRY']='true'
os.environ['DO_NOT_TRACK']='true'
os.environ['MLFLOW_HTTP_REQUEST_MAX_RETRIES']='0'
import mlflow
from mlflow import MlflowClient
URI=os.environ.get('MLFLOW_TRACKING_URI','http://llm-lab:5000')
mlflow.set_tracking_uri(URI)
client=MlflowClient(tracking_uri=URI)
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def digest(b):return hashlib.sha256(b).hexdigest()
def seed():
 rows=json.loads(Path('/tangerine/builtin.json').read_text());result=[]
 for b in rows:
  for name,text,kind in [('tangerine-'+b['prompt_id'],b['template'],'prompt'),('tangerine-context-'+b['prompt_id'],canonical(b['context_policy']),'context_policy')]:
   sha=digest(text.encode())
   try:existing=client.search_prompt_versions(name)
   except mlflow.exceptions.MlflowException as e:
    if e.error_code!='RESOURCE_DOES_NOT_EXIST':raise
    existing=[]
   same=next((v for v in existing if v.tags.get('tangerine.content_sha256')==sha and v.template==text),None)
   if same is None:same=mlflow.genai.register_prompt(name=name,template=text,tags={'kind':kind,'tangerine.content_sha256':sha})
   result.append({'name':name,'version':int(same.version),'sha256':sha})
 return result
def export(selection):
 rows=json.loads(Path('/tangerine/builtin.json').read_text());selected={(v['stage'],v['phase']):v for v in selection['bindings']}
 if len(selected)!=9 or len(selection['bindings'])!=9:raise ValueError('complete distinct nine-binding selection required')
 for b in rows:
  v=selected[b['stage'],b['phase']]
  if type(v['prompt_version']) is not int or v['prompt_version']<1 or type(v['context_version']) is not int or v['context_version']<1:raise ValueError('numeric frozen versions required')
  if v['prompt_name']!='tangerine-'+b['prompt_id'] or v['context_name']!='tangerine-context-'+b['prompt_id']:raise ValueError('manifest registry names required')
  p=mlflow.genai.load_prompt(f"prompts:/{v['prompt_name']}/{v['prompt_version']}");c=mlflow.genai.load_prompt(f"prompts:/{v['context_name']}/{v['context_version']}")
  b.update(template=p.template,prompt_sha256=digest(p.template.encode()),context_policy=json.loads(c.template),context_policy_sha256=digest(canonical(json.loads(c.template)).encode()),registry_name=v['prompt_name'],registry_version=v['prompt_version'],context_registry_name=v['context_name'],context_registry_version=v['context_version'])
 return rows

def sync(packet):
 """Explicit export with stable run identity and byte readback, no provider SDK."""
 if type(packet.get('capture',False)) is not bool:raise ValueError('capture requires an explicit JSON boolean')
 eid=client.get_experiment_by_name('tangerine-development')
 if eid is None:eid=client.get_experiment(client.create_experiment('tangerine-development'))
 operation=str(uuid.UUID(packet['operation']));runs=client.search_runs([eid.experiment_id],filter_string=f"tags.`tangerine.operation` = '{operation}'")
 if len(runs)>1:raise ValueError('duplicate diagnostic run linkage')
 run=packet.get('run') or (runs[0].info.run_id if runs else None)
 if run:
  existing=client.get_run(run)
  if existing.info.experiment_id!=eid.experiment_id or existing.data.tags.get('tangerine.operation')!=operation or (runs and runs[0].info.run_id!=run):raise ValueError('diagnostic run belongs to another operation')
 else:run=client.create_run(eid.experiment_id,tags={'tangerine.operation':operation,'tangerine.origin':packet.get('origin','native_diagnostic'),'tangerine.export_provider_calls':'0'}).info.run_id
 artifacts=[]
 with tempfile.TemporaryDirectory() as tmp:
  for a in packet['artifacts']:
   name=a['name']
   if Path(name).name!=name or name in ('','.', '..'):raise ValueError('local artifact filename required')
   body=a['body'].encode();sha=digest(body)
   if sha!=a['sha256']:raise ValueError('native artifact hash mismatch')
   redaction=native({'action':'sanitize','payload':json.loads(body),'capture':packet.get('capture',False),'secrets':packet.get('secrets',[])})
   body=canonical(redaction['bytes']).encode();sha=digest(body)
   p=Path(tmp)/name;p.write_bytes(body)
   existing=client.list_artifacts(run,'native')
   if any(a.path=='native/'+name for a in existing):
    before=Path(client.download_artifacts(run,'native/'+name,tmp+'/existing')).read_bytes()
    if before!=body:raise ValueError('immutable diagnostic export conflicts with saved bytes')
   else:client.log_artifact(run,str(p),'native')
   saved=Path(client.download_artifacts(run,'native/'+name,tmp+'/readback')).read_bytes()
   if saved!=body:raise ValueError('Lab byte readback mismatch')
   artifacts.append({'run':run,'artifact':'native/'+name,'sha256':sha,'original_sha256':redaction['original_sha256'],'redaction_reasons':redaction['reasons'],'verified':True})
 client.set_terminated(run)
 return {'run':run,'artifacts':artifacts,'provider_calls':0}

def verify(packet):
 errors=[]
 with tempfile.TemporaryDirectory() as tmp:
  for a in packet['artifacts']:
   try:
    actual=Path(client.download_artifacts(a['run'],a['artifact'],tmp)).read_bytes()
    if digest(actual)!=a['sha256']:errors.append('artifact hash mismatch '+a['artifact'])
   except Exception:errors.append('missing Lab artifact '+a['artifact'])
 return {'status':'observed' if not errors else 'incomplete','discrepancies':errors,'provider_calls':0}

def native(packet):
 p=subprocess.run(['/tangerine/native','lab-json'],input=json.dumps(packet).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 if p.returncode:raise ValueError('native bundle/context validation failed')
 return json.loads(p.stdout)

def check_inventory(inv):
 """Read source bytes independently of the saved inventory declarations."""
 paths={d['path'] for d in inv['dependencies']}
 paths.update(f['path_or_asset'] for e in inv['entries'] for f in e['trusted_fragments'] if f['state']=='observed')
 actual={}
 expected=json.loads(Path('/tangerine/spec/domain/ai-development.v1.json').read_text())['planned_surfaces']
 entries={e['id']:e for e in inv['entries']}
 for surface in expected:
  row=entries.get(surface['id'])
  if row is None or any(row[k]!=surface[k] for k in ('stage','phase','kind')):raise ValueError('declared inference surface is missing or mismatched')
 for path in paths:
  if path=='services/api/internal/lab/builtin.json':physical=Path('/tangerine/builtin.json')
  elif path.startswith('specification/v2/'):
   root=Path('/tangerine/spec').resolve();physical=(root/path[len('specification/v2/'):]).resolve()
   if not physical.is_relative_to(root):raise ValueError('unresolved source dependency')
  else:raise ValueError('source dependency is not available in the tooling snapshot')
  actual[path]=digest(physical.read_bytes())
 native({'action':'inventory','payload':inv,'dependencies':actual})
def configuration():
 stages=['case_generation','linguistic_audit','blind_claim_extraction','claim_mapping','mapping_audit','feedback','case_review','adjudication']
 profile=dict(id='chatgpt-plan-responses-v1',provider='openai_chatgpt',model='unselected',endpoint='https://api.openai.com/v1/responses',reasoning_effort=None,temperature=None,max_output_tokens=None,context_budget_tokens=128000,adapter_version='chatgpt-plan-responses-v1',credential_ref='chatgpt_plan_oauth',store=False,stream=True,tools=[],roles=stages,auth_method='chatgpt_plan_oauth',billing_mode='included_subscription')
 return dict(schema_version='2.0.0',workspace_id='local',llm_profile=profile['id'],feedback_language='en',intended_uses=['local_analysis','derivative_exercises'],credential_refs=dict(deepseek=None,openai=None,azure=None),azure_region=None,connectors=[],limits=dict(daily_micro_usd=None,monthly_micro_usd=None,concurrent_paid_operations=1,archive_bytes='34359738368',expanded_bytes='137438953472',archive_members=250000,member_bytes='34359738368'),configuration_sha256='0'*64,llm_profiles=[profile],stage_profiles={s:None for s in stages},mapping_audit_enabled=False,llm_lab_trace_enabled=False,llm_lab_capture_content=False)
def export_command(args):
 import argparse
 p=argparse.ArgumentParser();choice=p.add_mutually_exclusive_group(required=True);choice.add_argument('--builtins',action='store_true');choice.add_argument('--selection');p.add_argument('--out',required=True);a=p.parse_args(args)
 if a.builtins:b=native({'action':'builtins'})
 else:
  b=native({'action':'builtins'});b.update(origin='registry_export',bindings=export(json.load(sys.stdin)));b=native({'action':'seal','bundle':b})
 # Output is stdout; shell owns the host destination, never a hidden container file.
 return b

def inventory(revision):
 policy=json.loads(Path('/tangerine/spec/domain/ai-development.v1.json').read_text());rows=json.loads(Path('/tangerine/builtin.json').read_text());dependencies=[]
 def dependency(path,physical,purpose):
  sha=digest(Path(physical).read_bytes());dependencies.append({'path':path,'sha256':sha,'purpose':purpose});return sha
 dependency('services/api/internal/lab/builtin.json','/tangerine/builtin.json','shipped prompt/context bytes')
 dep=dependency('specification/v2/domain/ai-development.v1.json','/tangerine/spec/domain/ai-development.v1.json','finite declared surface scope')
 entries=[]
 for surface in policy['planned_surfaces']:
  fragments=[]
  for b in rows:
   if b['stage']==surface['stage'] and b['phase']==surface['phase']:
    for kind,path in [('stage_prompt','prompts/'+b['prompt_id']+'.txt'),('wire_schema_projection','contracts/'+b['output_schema'])]:
     full='specification/v2/'+path;sha=dependency(full,'/tangerine/spec/'+path,'trusted '+kind)
     fragments.append({'kind':kind,'path_or_asset':full,'sha256':sha,'state':'observed'})
  entries.append(dict(id=surface['id'],stage=surface['stage'],phase=surface['phase'],kind=surface['kind'],implementation_state='planned',owner_paths=[surface['owner_root']],owner_symbols=[],adapter_paths=[],trusted_fragments=fragments,discovery_evidence_refs=['iteration3 source inspection: provider execution belongs to iteration4 onward'],coverage_reason='no implemented model-call owner in this tooling iteration'))
 result=dict(schema_version='2.0.0',id=str(uuid.uuid4()),source_revision=revision,dependencies=dependencies,entries=entries,non_ai_calls=[{'path':'deploy/local/lab.py','reason':'MLflow registry/diagnostics; no inference'}],unresolved_paths=[],inventory_sha256='0'*64)
 # Native contract uses RFC8785; JSON values here have no non-ASCII keys or floats.
 result['inventory_sha256']=digest(canonical({k:v for k,v in result.items() if k!='inventory_sha256'}).encode())
 native({'action':'inventory','payload':result,'dependencies':{d['path']:d['sha256'] for d in dependencies}})
 return result

def main():
 action=sys.argv[1]
 if action=='inventory':result=inventory(sys.argv[2])
 elif action=='seed':result=seed()
 elif action=='export':result=export(json.load(sys.stdin))
 elif action=='export-command':result=export_command(sys.argv[2:])
 elif action=='development-packet':result={'action':'development-prepare','payload':json.load(sys.stdin)}
 elif action=='development-verify':
  packet=json.load(sys.stdin);source_errors=[]
  try:check_inventory(packet['inventory'])
  except Exception:source_errors.append('inventory source/dependency verification failed')
  v=verify(packet);j=packet['join'];verified=v['status']=='observed'
  for e in (j.get('exports') or []):e['verified']=verified
  if j.get('deterministic_artifact') is not None:j['deterministic_artifact']['verified']=verified
  result=native({'action':'reconcile','join':j});result['discrepancies']+=packet['discrepancies']+v['discrepancies']+source_errors
  if result['discrepancies']:result['status']='incomplete'
  print(json.dumps(result,ensure_ascii=False));sys.exit(0 if result['status']=='observed' else 1)
 elif action=='diagnostic-packet':result={'action':'diagnostic-save','payload':json.load(sys.stdin)}
 elif action=='diagnostic-read-packet':result={'action':'diagnostic-read','id':json.load(sys.stdin)['id']}
 elif action=='activation-packet':result={'action':'activate','bundle':json.load(sys.stdin),'configuration':configuration()}
 elif action=='sync':
  with contextlib.redirect_stdout(sys.stderr):result=sync(json.load(sys.stdin))
 elif action=='verify':result=verify(json.load(sys.stdin))
 elif action=='snapshot':
  import sqlite3
  target=sys.argv[2]
  with sqlite3.connect('/lab/mlflow.db') as src,sqlite3.connect(target) as dst:src.backup(dst)
  result={'consistent_sqlite_snapshot':target,'provider_calls':0}
 else:raise ValueError('unknown Lab SDK action')
 print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':
 try:
  # SDK diagnostics belong on stderr; stdout is a machine-readable protocol.
  with contextlib.redirect_stdout(sys.stderr):
   import io
  main()
 except Exception as e:print('LAB_ACTION_FAILED: local registry/export is unavailable; native data retained.',file=sys.stderr);sys.exit(1)
