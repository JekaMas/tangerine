"""Bind exact native observations once at the stable I37 checkpoint."""
import ast,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent;OUT=ROOT/'data/iteration-37-supplements-20261027'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def functions(path):
 text=path.read_text();return {m.group(1):m.group(0).strip()+"\n" for m in re.finditer(r'(?ms)^func (Test\w+)\(.*?(?=^func |\Z)',text)}
def main():
 files=[ROOT/'services/api/internal/source/supplements_test.go',ROOT/'services/api/internal/source/jfleg_test.go',ROOT/'services/api/internal/app/source_supplements_test.go',ROOT/'tests/native_supplement_test.go',ROOT/'tests/native_supplement_consumers_test.go',ROOT/'tests/native_source_test.go',ROOT/'tests/native_source_admitted_test.go',ROOT/'tests/native_source_mapping_cursor_test.go',ROOT/'tests/native_jfleg_consumers_test.go']
 owners={}
 for path in files:
  for name,body in functions(path).items():owners[name]=(path,body)
 selected={};runs=[]
 receipts=['targeted-tests.jsonl','clock-history-tests.jsonl','window-tests.jsonl','edacc.jsonl','elrd.jsonl','diplomat.jsonl','dralbase.jsonl','dral8.jsonl','siblings.jsonl','consumers.jsonl','meaning.jsonl','persistence.jsonl','windows.jsonl','missing.jsonl','stale.jsonl','partition-green.jsonl','partitions.jsonl','jfleg-registry/native.jsonl']
 for receipt in receipts:
  path=OUT/receipt;rows=[json.loads(line) for line in path.read_text().splitlines() if line.strip()];passing=[r['Test'] for r in rows if r.get('Action')=='pass' and r.get('Test')];failing=[r['Test'] for r in rows if r.get('Action')=='fail' and r.get('Test')]
  runs.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path),observed_passes=passing,observed_failures=failing))
  for name in passing:
   source,body=owners[name];selected[name]=dict(test_id='tangerine.local/api/internal/'+('source' if '/internal/source/' in str(source) else 'app')+'::'+name,source_path=str(source.relative_to(ROOT)),function_sha256=hashlib.sha256(body.encode()).hexdigest(),receipt=str(path.relative_to(ROOT)),receipt_sha256=digest(path))
 assert len(selected)==51,len(selected)
 superseded={'TestNativeSupplementReadbackPositive':'meaning.jsonl','TestNativeSupplementPersistencePositive':'persistence.jsonl','TestNativeSupplementMissingNegative':'missing.jsonl','TestNativeSupplementPersistenceNegative':'stale.jsonl'}
 for name,path in superseded.items():assert selected[name]['receipt'].endswith('/'+path)
 data=dict(entry_commit='05099ee6935065f611f9d938200203ad07ae8e0b',required_unique_go_cases=51,cases=selected,runs=runs,superseded_consumer_cases=superseded,scope='Actual imported data/storage/readback and labelled negative inputs. No models, synthesis, semantic/acoustic quality or every historical iteration claim.',reuse='Unchanged observed cases retain their receipts. Later targeted runs replace only the declared invalidated or failed oracle; a failed aggregate is never labelled passed.')
 (HERE/'NATIVE-EVIDENCE.json').write_text(json.dumps(data,indent=2)+'\n')
 protected=['corpus-sources.v1.yaml','error-taxonomy.v1.yaml','llm-quality-metrics.v1.json','metrics.v1.yaml','mutation-recipes.v1.json','providers.v1.yaml'];before=json.loads((ROOT/'data/iteration-36-verification-20261027/preservation.json').read_text())
 # Keep concrete canonical paths; no content/schema/corpus re-admission occurs.
 paths={name:next((ROOT/'specification/v2').rglob(name)) for name in protected};checks=[]
 for name,path in paths.items():
  original=subprocess.check_output(['git','show','05099ee:'+str(path.relative_to(ROOT))],cwd=ROOT);checks.append(dict(path=str(path.relative_to(ROOT)),entry_sha256=hashlib.sha256(original).hexdigest(),current_sha256=digest(path)));assert checks[-1]['entry_sha256']==checks[-1]['current_sha256']
 gaps=Path('/Users/jekamas/projects/0xatelerix/tangerine/audit/spec-fullness-20261008/GAPS.md');assert digest(gaps)=='78f8cfa15fdc0215d92f6045d2f0f6e53b391030e543050ee1b09ed65776db65'
 (OUT/'preservation.json').write_text(json.dumps(dict(catalogues=checks,canonical_gaps=dict(path=str(gaps),sha256=digest(gaps)),original_source_ids=11,total_source_cards=16),indent=2)+'\n');print('51 exact native Go cases and protected inputs reconciled')
if __name__=='__main__':main()
