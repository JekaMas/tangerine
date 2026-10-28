"""Register exact repaired assertions, preserving every unrelated DAG identity."""
import ast,copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];CHANGE=ROOT/'openspec/changes/implement-teacher-error-trainer';HERE=Path(__file__).resolve().parent
SOURCES={
 'tests/test_completion_i25.py':('CompletionI25','FIN-QWEN.P1','completion-i25'),
 'tests/test_qwen_comparison.py':('QwenComparison','FIN-QWEN.P1','completion-i25-contracts'),
 'tests/test_qwen_native_runtime.py':('QwenNativeRuntime','FIN-QWEN.P1','completion-i25-native-runtime'),
 'tests/test_completion_i26.py':('CompletionI26','FIN-ACOUSTIC.P1','completion-i26'),
 'tests/test_completion_i27.py':('CompletionI27','FIN-SOURCES.P1','completion-i27'),
 'tests/test_completion_i30.py':('CompletionI30','FIN-DELIVERY.P1','completion-i30'),
 'tests/test_release_forwarder.py':('ReleaseForwarder','FIN-DELIVERY.P1','completion-i30'),
}
PROPS=['FIN-QWEN.P1','FIN-VERIFY.I25','FIN-ACOUSTIC.P1','FIN-VERIFY.I26','FIN-SOURCES.P1','FIN-VERIFY.I27','FIN-DELIVERY.P1','FIN-VERIFY.I30']
DEPS=['services/speech/qwen_runtime.py','services/speech/backends.py','services/web/app/settings/page.js','specification/v2/docs/speech-runtime.md','audit/iteration-25-qwen-20261026/compare.py','audit/iteration-30-release-20261027/readiness_forwarder.py','audit/completion-leftovers-20261028','tests/completion_leftovers_i26.cjs','tests/completion_leftovers_i27.cjs','tests/completion_leftovers_i30.cjs','tests/completion_leftovers_qwen.cjs','data/completion-leftovers-20261028']
def main():
 path=CHANGE/'verification.json';g=json.loads(path.read_text());existing={c['test_id']:c for c in g['cases']};templates={p:next(c for c in g['cases'] if c['property_id']==p) for p in PROPS};updates=[];selected=[]
 for relative,(classname,default,command) in SOURCES.items():
  text=(ROOT/relative).read_text();sha=hashlib.sha256(text.encode()).hexdigest()
  methods=[(c.name,m) for c in ast.parse(text).body if isinstance(c,ast.ClassDef) for m in c.body]
  for classname,method in methods:
   if not isinstance(method,ast.FunctionDef) or not method.name.startswith('test_'):continue
   identity='unittest::tests.'+Path(relative).stem+'.'+classname+'.'+method.name
   row=existing.get(identity)
   if row is None:
    row=copy.deepcopy(templates[default]);row.update(id=default+'.'+method.name.removeprefix('test_'),property_id=default,test_id=identity,command_id=command,source_path=relative,state='implemented',polarity='negative' if method.name.endswith('negative') else 'positive')
    row['setup']='Literal independently authored inputs/assertions in '+relative+'::'+method.name+'. Native model/HTTP availability is explicitly constructed only at the named test boundary.'
    row['red_expectation']='The exact requested/loaded runtime, cache separation, frozen plan or HTTP origin/header relation differs from its literal independent expectation.'
    row['green_expectation']='Every exact literal assertion holds through the named production or shared test-isolation owner; constructed model outputs establish wiring only.'
    row['substitution']=dict(classification='EXTERNAL_BOUNDARY',owner_replaced='Only trained-model output or the local upstream HTTP response is constructed; actual Qwen selection/cache/planning and shared HTTP forwarder execute.',allowed_proof='Runtime placement, frozen selection, reuse and finite HTTP semantics only.',forbidden_claims=['Constructed waves prove actual Qwen or acoustic quality','A fixture reply proves actual GitHub publication','An upstream origin rewrite weakens production origin policy'])
    g['cases'].append(row)
   if row.get('source_sha256')!=sha:updates.append(dict(case_id=row['id'],test_id=identity,source=relative,previous_source_sha256=row.get('source_sha256'),current_source_sha256=sha,reason='Changed literal assertion source; only the selected changed owner/fixture scope is newly executed. Original receipts are retained.'))
   row.update(source_sha256=sha,observable=ast.get_source_segment(text,method),state='implemented')
   row['invalidation_dependencies']=list(dict.fromkeys(row.get('invalidation_dependencies',[])+DEPS))
   if method.name!='test_selected_owner_releases_positive':row.pop('blocker',None)
   selected.append(identity)
 for c in g['commands']:
  if c['id']=='completion-i30':c['argv']=['python3','-B','-m','unittest','-v','tests.test_completion_i30','tests.test_release_forwarder']
 for p in g['properties']:
  if p['id'] in PROPS:p['source_globs']=list(dict.fromkeys(p.get('source_globs',[])+DEPS))
 path.write_text(json.dumps(g,indent=2,ensure_ascii=False)+'\n')
 dpath=CHANGE/'discovery.json';d=json.loads(dpath.read_text());d['scope']['test_ids']=list(dict.fromkeys(d['scope']['test_ids']+selected));d['reviews']=[r for r in d['reviews'] if r['id']!='completion-leftovers-20261028']
 d['reviews'].append(dict(id='completion-leftovers-20261028',property_ids=PROPS,test_ids=selected,disposition='current_change',question='Close selected I25/I26/I27/I30 observation gaps and repair demonstrated local runtime/Settings defects while retaining original failures and unaffected evidence.',rationale='Actual Qwen failures discriminate float16 sampling and float32 codec-device limitations. Explicit CPU codec placement repairs only that model stage. Independent Settings reads preserve local configuration during connection failures. Existing Chrome authorization closes saved-audio/source controls; real publication/ZIP/startup evidence remains required separately. Missing private source-owner releases stay skipped.',searches=[dict(kind='exact',status='completed',query='Trace named I25 Qwen plan/native worker/cache/receipt, I26 saved player, I27 native lineage/status, I30 Settings/clientFetch/forwarder and original clean receipts.',outcome='Native CPU/MPS failures retained; codec/cache/frozen-plan/HTTP counterexamples materialized. Actual Chrome playback/Refresh and selected Sources lineage are observed separately from model quality and original source completeness.',results=[dict(path=p,classification='change_candidate',reason='Known directly affected owner or exact literal assertion inspected.') for p in [*SOURCES,*DEPS] if not p.startswith('data/')]),dict(kind='semantic',status='not_applicable',query='Existing properties, audit and receipt selectors identify the exact owners.',outcome='Direct named-file and native failure tracing; no semantic index evidence is claimed.',reason='No unfamiliar ownership discovery or index creation is needed.',results=[]),dict(kind='jetbrains-index',status='not_applicable',query='Known Python/JavaScript owners; no symbol refactor.',outcome='No PSI/IDE evidence claimed.',reason='Actual runtime and browser evidence answer the selected questions.',results=[])]))
 dpath.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n');(HERE/'BINDING-CHANGES.json').write_text(json.dumps(dict(reason='Once at the stable assertion/owner boundary; historical receipts are not rewritten',source_updates=updates,selected_test_ids=selected),indent=2)+'\n');print(json.dumps(dict(updated_or_registered=len(selected),source_binding_changes=len(updates))))
if __name__=='__main__':
 main()
 from narrow_dependencies import main as narrow
 narrow()
