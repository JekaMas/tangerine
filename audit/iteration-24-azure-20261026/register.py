"""Materialize I24 without relabelling missing actual Azure evidence green."""
import ast,copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];CHANGE=ROOT/'openspec/changes/implement-teacher-error-trainer'
PROPS=['FIN-AZURE.P1','FIN-VERIFY.I24']
DEPS=['services/speech/backends.py','audit/iteration-24-azure-20261026/compare.py','audit/iteration-24-azure-20261026/player.py','audit/iteration-24-azure-20261026/run_contracts.py','tests/test_azure_comparison.py','tests/test_azure_recovery.py','tests/test_azure_player_observations.py','audit/iteration-24-azure-20261026/browser-observations.json','audit/iteration-24-azure-20261026/media-http-observations.json','tests/test_completion_i24.py','audit/iteration-24-azure-20261026/material.json','data/iteration-24-azure-20261026/access-inventory.json','data/iteration-24-azure-20261026/browser-facts.json','data/iteration-24-azure-20261026/layouts.json','data/iteration-24-azure-20261026/controlled/']
def main():
 p=CHANGE/'verification.json';v=json.loads(p.read_text());templates={prop:copy.deepcopy(next(c for c in v['cases'] if c['property_id']==prop)) for prop in PROPS}
 v['cases']=[c for c in v['cases'] if not c['id'].startswith('FIN-AZURE.P1.contract_') and not c['id'].startswith('FIN-VERIFY.I24.contract_')]
 native='completion-i24-contracts'
 v['commands']=[c for c in v['commands'] if c['id']!=native]+[dict(id=native,runner='python-unittest',argv=['python3','-B','audit/iteration-24-azure-20261026/run_contracts.py','-m','unittest','-v','tests.test_azure_comparison','tests.test_azure_recovery','tests.test_azure_player_observations'],cwd='.',env={},timeout_seconds=120,authority='local')]
 for src,cls in {'tests/test_azure_comparison.py':'AzureComparison','tests/test_azure_recovery.py':'AzureRecovery','tests/test_azure_player_observations.py':'AzurePlayerObservations'}.items():
  text=(ROOT/src).read_text()
  for n in ast.walk(ast.parse(text)):
   if not isinstance(n,ast.FunctionDef) or not n.name.startswith('test_') or n.name=='test_non_f0_overage_negative':continue
   prop='FIN-VERIFY.I24' if n.name.startswith('test_player') else 'FIN-AZURE.P1';c=copy.deepcopy(templates[prop]);oracle=ast.get_source_segment(text,n)
   c.update(id=prop+'.contract_'+n.name.removeprefix('test_'),property_id=prop,polarity='negative' if n.name.endswith('negative') else 'positive',setup='Literal constructed native compiler/policy/audio-transport or HTTP-player fixture in '+src+':'+n.name,observable=oracle,red_expectation='The exact literal target/word order, no-dispatch policy, retained piece/context, recovery or private-route expectation fails.',green_expectation='The independently expected literal assertions hold through the named real owner with the documented controlled boundary.',test_id='unittest::tests.'+Path(src).stem+'.'+cls+'.'+n.name,command_id=native,source_path=src,state='implemented')
   c.pop('blocker',None);v['cases'].append(c)
 src='tests/test_azure_comparison.py'
 selected=[c for c in v['cases'] if c['property_id'] in PROPS]
 for c in selected:
  if c['id']=='FIN-AZURE.P1.azure_negative':
   c.update(test_id='unittest::tests.test_azure_comparison.AzureComparison.test_non_f0_overage_negative',command_id=native,source_path=src)
  elif '.contract_' not in c['id']:c['source_path']='tests/test_completion_i24.py'
  c['state']='implemented';c['source_sha256']=hashlib.sha256((ROOT/c['source_path']).read_bytes()).hexdigest();c['invalidation_dependencies']=list(dict.fromkeys(c['invalidation_dependencies']+DEPS));c.pop('blocker',None)
  if c['command_id']==native:c['substitution']=dict(classification='EXTERNAL_BOUNDARY',owner_replaced='Constructed Azure HTTP response/WAV only; native SSML/render/billing, comparison persistence and HTTP file allowlist are real.',allowed_proof='Finite compiler, policy, context, resume and player-route behavior. No hosted synthesis in these cases.',forbidden_claims=['Actual F0 entitlement','Azure voice naturalness or realized pronunciation','Complete live pair from tone fixtures'])
  elif c['id'] in ['FIN-AZURE.P1.azure_positive','FIN-VERIFY.I24.review_positive']:
   c['blocker']='Microsoft passkey/security-window confirmation and actual F0 resource/key/region are unavailable. Test explicitly skips; no real Azure pair/playback is claimed.'
 for prop in v['properties']:
  if prop['id'] in PROPS:prop['source_globs']=list(dict.fromkeys(prop['source_globs']+DEPS))
 p.write_text(json.dumps(v,indent=2)+'\n')
 p=CHANGE/'discovery.json';d=json.loads(p.read_text());ids=[c['test_id'] for c in selected]
 old='unittest::tests.test_completion_i24.CompletionI24.test_azure_negative'
 d['scope']['test_ids']=list(dict.fromkeys([x for x in d['scope']['test_ids'] if x!=old]+ids))
 for row in d['reviews']:
  if old in row.get('test_ids',[]):row['test_ids']=[x for x in row['test_ids'] if x!=old]+['unittest::tests.test_azure_comparison.AzureComparison.test_non_f0_overage_negative']
 d['reviews']=[r for r in d['reviews'] if r['id'] not in ['iteration24-azure-20261026','iteration24-verify-20261026']]
 d['reviews'].append(dict(id='iteration24-azure-20261026',question='Complete the original four-turn Azure F0 reference/mutated comparison, preserve target/speaker/SSML provenance, and exclude paid/trial/fallback.',property_ids=PROPS,test_ids=ids,disposition='current_change',rationale='Native text fragments incorrectly became sentences; red/green mixed-content repair through existing ssml. Verify additionally reproduced missing transient recovery, tracebacks, delayed complete-variant publication and misleading missing-audio guidance; repaired their existing comparison/transport/player owners with controlled negative cases. Actual Microsoft passkey and F0 resource/key/region remain external blockers; positive live/media cases skip rather than pass.',searches=[dict(kind='exact',status='completed',query='Trace original speech-comparison REPORT/shared-material/serve, backends ssml/hosted/render/billing, acoustic hosted contracts and account configuration metadata without secret values.',outcome='Original four turns and target IPA retained; native compiler, request capture, piece finalizer and existing F0 guards located. Microsoft sign-in handoff observed; no key/resource configured.',results=[dict(path=x,classification='interface_dependency',reason='Known owner, frozen source or literal evidence dependency.') for x in DEPS if not x.startswith('data/')]),dict(kind='semantic',status='unavailable',query='How do Azure speech synthesis errors propagate from native transport through retries, saved preparation and human readable recovery messages?',reason='jbcontext search reports no index for this exact checkout; retained native semantic-search.log. No index creation or semantic proof claimed.',outcome='Exact tracing located native transport, comparison retry/finalization, speechPublicFailure and authored frontend failureReason/preparationResponse. Native plain-form probe also failed to activate; product click/keyboard acceptance remains unobserved.',results=[]),dict(kind='jetbrains-index',status='not_applicable',query='Small known Python compiler/helper change with no symbol refactor.',reason='Direct native and source observations answer this increment; no PSI operation needed.',outcome='No IDE/index proof claimed.',results=[])]))
 p.write_text(json.dumps(d,indent=2)+'\n');print('Registered',len(selected),'I24 cases; actual Azure and full player verification retain explicit blockers.')
if __name__=='__main__':main()
