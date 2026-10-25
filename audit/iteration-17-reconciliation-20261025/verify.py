"""Finite development-ledger checks. Never imported by the application."""
import json
from pathlib import Path

ALLOWED={'completed','superseded','still required','optional/external'}
# Independent open-scope anchors: source-owner bytes/real populations and named
# unqualified provider observations cannot be closed by this status-only task.
# See ORIGINAL-SCOPE, GEN.R4/CMP.R2/R3 and the unchanged production SP-01 gap.
EXTERNAL={10,14,15,16,20,21,32,36,63,64,65,78,80,99,100,101}
STILL_REQUIRED={11,52,58,92,93,94,96,98}

def read(root,path):return json.loads((root/path).read_text())

def ledger_errors(root,ledger,baseline):
 errors=[];rows=ledger.get('items',[])
 expected={f'H{i:03}':x for i,x in enumerate(baseline,1)}
 if len(rows)!=101 or len({x.get('id') for x in rows})!=101 or {x.get('id') for x in rows}!=set(expected):errors.append('Original 101 identities missing/duplicated')
 for row in rows:
  old=expected.get(row.get('id'))
  if not old:continue
  if (row.get('baseline_line'),row.get('original_section'),row.get('original_text'))!=(old['line'],old['section'],old['text']):errors.append(row['id']+': changed original')
  if row.get('disposition') not in ALLOWED:errors.append(row['id']+': invalid disposition')
  number=int(row['id'][1:])
  if number in EXTERNAL and row.get('disposition')!='optional/external':errors.append(row['id']+': unobserved external qualification')
  if number in STILL_REQUIRED and row.get('disposition')!='still required':errors.append(row['id']+': unimplemented completion claim')
  if not row.get('scope') or not row.get('references'):errors.append(row['id']+': no evidence/scope')
  for path in row.get('references',[]):
   if not (root/path).is_file():errors.append(row['id']+': absent reference '+path)
  if row.get('disposition')=='optional/external' and not row.get('activation'):errors.append(row['id']+': missing activation')
  if row.get('disposition')=='still required' and not row.get('successor_tasks'):errors.append(row['id']+': no residual owner')
  for task in row.get('successor_tasks',[]):
   if task+' ' not in (root/'openspec/changes/implement-teacher-error-trainer/tasks.md').read_text():errors.append(row['id']+': unknown successor '+task)
 return errors

def acceptance_errors(packet):
 errors=[];a=packet['i12'];b=packet['i16'];early=packet['earlier_i16']
 if a.get('status')!='passed' or a.get('git',{}).get('dirty') is not False or a.get('git',{}).get('head')!='691714a73e5d169bdf5da0fe848b8b0f092d7e68':errors.append('I12 lacks actual clean ancestor')
 if len(a.get('cases',[]))!=139 or any(x.get('status')!='passed' for x in a.get('cases',[])):errors.append('I12 case receipt not 139 passed')
 if a.get('semantic_status')!='passed' or len(a.get('semantic_cases',[]))!=6:errors.append('I12 semantic contrast missing')
 if b.get('status')!='passed' or b.get('require_clean') is not True or b.get('case_edges')!=373 or b.get('unresolved')!=0 or len(b.get('cases',{}))!=373 or any(x.get('status')!='passed' for x in b.get('cases',{}).values()):errors.append('I16 current selected acceptance missing')
 if early.get('status')!='incomplete' or early.get('unresolved')!=12 or early.get('acceptance')!='not_accepted':errors.append('Original I16 failure rewritten')
 return errors

def review_errors(packet):
 errors=[]
 for dim in ['ui_ux','typography']:
  if packet.get(dim,{}).get('disposition')!='not applicable' or not packet.get(dim,{}).get('reason'):errors.append(dim+': no justified scope disposition')
 if packet.get('evidence',{}).get('disposition')!='pass' or not packet.get('evidence',{}).get('references'):errors.append('evidence: missing inspected content')
 if packet.get('new_model_calls')!=0 or packet.get('new_synthesis_calls')!=0 or packet.get('performance_campaigns')!='excluded':errors.append('Unexpected inference/performance campaign')
 if packet.get('independence')!='self-review with independently specified source expectations':errors.append('Invented independent review')
 if packet.get('claims_new_product_acceptance') is not False:errors.append('Invented application/media acceptance')
 return errors

def overlap_errors(root,packet):
 errors=[];graph=read(root,'openspec/changes/implement-teacher-error-trainer/verification.json')
 cases={x['id']:x for x in graph['cases']};actual={x['case_id']:x for x in read(root,'audit/final-functional-ux-20261025/RECONCILIATION.json')['cases_observed']}
 expected={x['id'] for x in cases.values() if x['command_id'] in [f'completion-i{i}' for i in range(18,22)] and not x['property_id'].startswith('FIN-VERIFY')}
 rows=packet.get('ui_cases',[])
 if {x['continuation_case'] for x in rows}!=expected or len(rows)!=len(expected):errors.append('Missing continuation overlap case')
 for row in rows:
  if row['disposition'] not in ['reusable','partial']:errors.append('Unsupported overlap disposition')
  if row['disposition']=='partial' and not row.get('residual_observation'):errors.append('Partial proof hides residual')
  for old in row['candidate_existing_cases']:
   if old not in actual or old not in cases or actual[old]['test_id']!=cases[old]['test_id'] or actual[old]['status']!='passed':errors.append('Unobserved old case '+old)
 recurring=next(x for x in rows if x['continuation_case']=='FIN-UI-05.P1.recurring_positive')
 if recurring['disposition']!='partial' or 'five' not in recurring['residual_observation']:errors.append('Five intervals relabelled six')
 cv=read(root,packet['cv']['receipt'])
 if len(cv['cases'])!=518 or packet['cv']['registered_observations']!=518:errors.append('CV registration/observation mismatch')
 return errors
