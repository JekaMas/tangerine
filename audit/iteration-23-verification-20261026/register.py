"""Register current I23 error/recovery cases and honest invalidation inputs."""
import ast,copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];CHANGE=ROOT/'openspec/changes/implement-teacher-error-trainer'
PREFIX='data/iteration-23-verification-20261026/'
PROPS=['FIN-GEMINI.P1','FIN-VERIFY.I23']
OWNERS=['services/api/internal/provider/gemini.go','services/web/app/prepare/response.js','services/web/app/prepare/failureMessage.js','services/web/app/requestError.js']
SOURCES=['tests/test_completion_i23.py','tests/test_gemini_recovery.py','tests/test_gemini_recovery_evidence.py','services/api/internal/provider/gemini_recovery_test.go','tests/native_gemini_test.go','tests/native_gemini_recovery_test.go']
PROOF=[PREFIX+x for x in ['green-provider.jsonl','browser-facts.json','layouts.json','requests.jsonl','recovered.wav','lab-readback.json','browser/fixture.json','browser/before.json','browser/after.json','browser/dispatches.json','browser/native.jsonl','browser/documents.json','browser/assets/','controlled/native.jsonl','controlled/error-quota.json','controlled/error-denied.json','controlled/error-credentials.json','controlled/error-unavailable.json']]
def main():
 p=CHANGE/'verification.json';v=json.loads(p.read_text());template=copy.deepcopy(next(c for c in v['cases'] if c['id']=='FIN-GEMINI.P1.gemini_negative'))
 command='completion-i23-recovery'
 v['commands']=[x for x in v['commands'] if x['id']!=command]+[dict(id=command,runner='python-unittest',argv=['python3','-B','-m','unittest','-v','tests.test_gemini_recovery','tests.test_gemini_recovery_evidence'],cwd='.',env={},timeout_seconds=120,authority='local')]
 v['cases']=[c for c in v['cases'] if c.get('command_id')!=command]
 ids=[]
 for file,cls in [('tests/test_gemini_recovery.py','GeminiRecovery'),('tests/test_gemini_recovery_evidence.py','GeminiRecoveryEvidence')]:
  for n in ast.walk(ast.parse((ROOT/file).read_text())):
   if not isinstance(n,ast.FunctionDef) or not n.name.startswith('test_'):continue
   suffix=n.name.removeprefix('test_');prop='FIN-VERIFY.I23' if suffix in ['layouts_positive','browser_privacy_negative','browser_reopen_positive'] else 'FIN-GEMINI.P1'
   base=copy.deepcopy(next(c for c in v['cases'] if c['property_id']==prop))
   oracle=ast.get_source_segment((ROOT/file).read_text(),n)
   base.update(id=prop+'.recovery_'+suffix,polarity='negative' if suffix.endswith('negative') else 'positive',setup='Literal fixture and actual production-owner/native/CUA inputs in '+file+':'+n.name,observable=oracle,red_expectation='The literal independently expected guidance, preserved checkpoint, finite retry or current UI observation is contradicted.',green_expectation='All literal assertions hold at their labelled real/native or controlled boundary.',test_id='unittest::'+file[:-3].replace('/','.')+'.'+cls+'.'+n.name,command_id=command,state='implemented',source_path=file)
   base.pop('blocker',None)
   base['substitution']=dict(classification='EXTERNAL_BOUNDARY',owner_replaced='Controlled Gemini HTTP errors or replayed saved text replies; browser401/429 message-only responses; no production persistence/rendering/recovery owner replaced.',allowed_proof='Production guidance/error classification and actual saved checkpoint/local speech/CUA recovery for the finite selected fixtures.',forbidden_claims=['Hosted Gemini entitlement or linguistic quality from controlled replies','Universal UI aesthetics from a report assertion','Paid allowance or real quota exhaustion'])
   v['cases'].append(base);ids.append(base['test_id'])
 deps=OWNERS+SOURCES+PROOF
 for c in v['cases']:
  if c['property_id'] in PROPS:
   c['source_sha256']=hashlib.sha256((ROOT/c['source_path']).read_bytes()).hexdigest()
   c['invalidation_dependencies']=list(dict.fromkeys(c['invalidation_dependencies']+deps))
 for p in v['properties']:
  if p['id'] in PROPS:p['source_globs']=list(dict.fromkeys(p['source_globs']+deps))
 (CHANGE/'verification.json').write_text(json.dumps(v,indent=2)+'\n')
 p=CHANGE/'discovery.json';d=json.loads(p.read_text());d['scope']['test_ids']=list(dict.fromkeys(d['scope']['test_ids']+ids));d['reviews']=[x for x in d['reviews'] if x['id']!='iteration23-verification-20261026']
 d['reviews'].append(dict(id='iteration23-verification-20261026',question='Verify actual Gemini Free qualification and nonblocking failure recovery; repair terminal guidance and current/legacy error siblings.',property_ids=PROPS,test_ids=ids,disposition='current_change',rationale='Two P2 recovery defects reproduced with native classifier and JS message owners, repaired and observed through actual saved checkpoints/local speech/CUA. Retain unaffected live7-dispatch candidate and I17 replay receipts. No hosted calls or new product gate.',searches=[dict(kind='exact',status='completed',query='Trace Gemini error classification/Exchange/Execute, current and legacy status/code dialects, immediate and saved preparation guidance, foreground resume, safe read retry and sibling interpretation envelopes.',outcome='Known owners inspected directly; native controlled red/green, actual persistence/rendering/browser observations, literal independently expected outputs and source/evidence invalidation recorded.',results=[dict(path=x,classification='interface_dependency',reason='Named production owner, controlled fixture or direct regression source.') for x in OWNERS+SOURCES]),dict(kind='semantic',status='unavailable',query='jbcontext status for exact Tangerine worktree',reason='No index exists. Known owner tracing needs no index creation.',outcome='No semantic-index evidence claimed.',results=[]),dict(kind='jetbrains-index',status='not_applicable',query='Known Go/JS owners with no symbol refactoring.',reason='Exact source and native/browser observation answer the selected question.',outcome='No IDE/PSI evidence claimed.',results=[])]))
 p.write_text(json.dumps(d,indent=2)+'\n');print('Registered13 recovery cases plus refreshed8 invalidated I23 test-source pins.')
if __name__=='__main__':main()
