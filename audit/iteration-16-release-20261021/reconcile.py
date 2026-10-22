"""Committed release reconciliation of actual retained/new per-case observations.
This is evidence readback, not another inference or a fabricated fresh test run.
"""
from pathlib import Path
import argparse,collections,datetime,json,subprocess,runpy,sys
R=Path(__file__).resolve().parents[2];A=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--require-clean',action='store_true');p.add_argument('--out',type=Path,required=True);args=p.parse_args()
if args.out.exists():raise SystemExit('Refuse to overwrite an original receipt')
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();dirty=bool(subprocess.check_output(['git','status','--porcelain','--untracked-files=normal'],cwd=R,text=True))
x=runpy.run_path(str(A/'observations.py'))['return_value'];g=json.loads((R/'openspec/changes/implement-teacher-error-trainer/verification.json').read_text());selected=[c for c in g['cases'] if c['id'].startswith('I16-')]
fresh={}
for path in [R/'data/iteration16/current-source-0baea04.json',R/'data/iteration16/attempts-b6e8e70.json',R/'data/iteration16/portable-b6e8e70.json',*sorted((R/'data/iteration16').glob('portable-remaining-*.json')),*sorted((R/'data/iteration16').glob('current-startup-*.json')),*sorted((R/'data/iteration16').glob('diagnostic-lab-*.json'))]:
 if path.exists():
  receipt=json.loads(path.read_text())
  if receipt.get('git',{}).get('dirty') is False:
   for identity,row in receipt['cases'].items():
    if row['status']=='passed':fresh[identity]=dict(receipt=str(path.relative_to(R)),source_revision=receipt['git']['head'],original_command_status=receipt['status'],original_evidence_fingerprint=row['evidence_fingerprint'])
rows={}
for c in selected:
 observation=x['records'][c['test_id']]['latest']
 rows[c['id']]=dict(status='passed' if observation and observation['status']=='pass' else 'missing_or_failed',test_id=c['test_id'],property_id=c['property_id'],polarity=c['polarity'],original_observation=observation,observation_kind='retained_original_event',current_literal_source=c['source_path'],current_source_sha256=c['source_sha256'],retention_basis='Exact named original event, independently expected literal assertions and affected-owner review in INVALIDATION.md/SELF-REVIEW.md. Broader glob/hash changes alone are not semantic invalidation. An individual pass within a failed command does not make that command green.')
for identity,receipt in fresh.items():
 if identity in rows and rows[identity]['status']=='passed':rows[identity].update(observation_kind='fresh_committed_native_execution',committed_native_receipt=receipt)
passed={i for i,r in rows.items() if r['status']=='passed'}
clean_native=passed&set(fresh);same_revision={i for i in clean_native if fresh[i]['source_revision']==head}
status='passed' if not x['missing'] and not(args.require_clean and dirty) else 'incomplete'
result=dict(status=status,kind='full_selected_release_evidence_reconciliation_not_fresh_behavior_execution',reviewed_revision=head,git=dict(head=head,dirty=dirty),require_clean=args.require_clean,case_edges=len(rows),committed_clean_native_case_edges=len(clean_native),fresh_on_reviewed_revision_case_edges=len(same_revision),retained_passed_case_edges=len(passed-same_revision),unresolved_case_edges=len(set(rows)-passed),physical_tests=x['required'],observed_physical_tests=x['observed'],properties=sorted({c['property_id'] for c in selected}),polarities=dict(collections.Counter(c['polarity'] for c in selected)),missing=x['missing'],cases=rows,policy='Actual user: preserve valid green evidence; a new commit/stage/docs update does not authorize a full rerun. Original receipts remain immutable. Committed-clean native executions for newly unobserved cases are separate artifacts.',finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='cases'}));sys.exit(0 if status=='passed' else 1)
