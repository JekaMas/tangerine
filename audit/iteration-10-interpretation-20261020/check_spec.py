"""Current whole-artifact structural metadata only; no behavior/model claims."""
from pathlib import Path
import ast,json,sys
R=Path(__file__).resolve().parents[2]
# Reuse the existing exact schema/reference/YAML/field/prompt/request checks.
# Historical later sections assert a 2026-10-09 graph and are not current gates.
source=(R/'audit/flow-fullness-20261009/check.py').read_text().split('# Preserve all original categories')[0]
namespace={'__file__':str(R/'audit/iteration-10-interpretation-20261020/check_spec.py')}
exec(compile(source,'current-artifact-checks','exec'),namespace)
checks=namespace['checks'];result={'status':'passed','assertions':len(checks),'proof_boundary':'Static current schema/reference/field/vector/prompt/request ownership checks only','checks':checks}
Path(sys.argv[1]).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
