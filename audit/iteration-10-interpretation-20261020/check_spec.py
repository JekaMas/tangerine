"""Current whole-artifact structural metadata only; no behavior/model claims."""
from pathlib import Path
import ast,json,sys
R=Path(__file__).resolve().parents[2]
# Reuse the existing exact schema/reference/YAML/field/prompt/request checks.
# Historical later sections assert a 2026-10-09 graph and are not current gates.
source=(R/'audit/flow-fullness-20261009/check.py').read_text().split('# Preserve all original categories')[0]
namespace={'__file__':str(R/'audit/iteration-10-interpretation-20261020/check_spec.py')}
exec(compile(source,'current-artifact-checks','exec'),namespace)
checks=namespace['checks']
# Development-time assembly evidence only. Ordinary reads trust admitted bundles.
bindings=json.loads((R/'services/api/internal/lab/builtin.json').read_text())
authored={(b['stage'],b.get('phase')):b for b in namespace['Y']['prompts/manifest.yaml']['bindings']}
def matches(rows):
 if len(rows)!=len(authored):return False
 for row in rows:
  source=authored.get((row['stage'],row.get('phase')))
  if source is None:return False
  if row['template']!=(R/'specification/v2'/source['path']).read_text():return False
  if any(row[key]!=source[key] for key in ['prompt_sha256','input_schema_sha256','output_schema_sha256']):return False
 return True
namespace['pair']('shipped_prompt_source',bindings,matches,lambda rows:rows[4].update(template='Superseded prompt'))
namespace['pair']('shipped_schema_binding',bindings,matches,lambda rows:rows[4].update(output_schema_sha256='0'*64))
result={'status':'passed','assertions':len(checks),'proof_boundary':'Static current schema/reference/field/vector/prompt/request ownership and shipped assembly checks only','checks':checks}
Path(sys.argv[1]).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
