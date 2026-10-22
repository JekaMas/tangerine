"""Current contract copies plus retained complete specification checks."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2]
code=(R/'audit/iteration-15-recovery-20261021/check_spec.py').read_text().rsplit("result={'status'",1)[0]
exec(compile(code,str(Path(__file__)),'exec'))
for name in ['audio-judge-input','audio-judge-output','audio-judge-profile','audio-measurement','audio-diagnostic-defaults','audio-diagnostic-run','audio-diagnostic-list','audio-diagnostic-packet','audio-diagnostic-view','generation-input','library-item','acoustic-production-plan','render-progress','preparation-state','preparation-summary']:
 ns['namespace']['ck']('i16.schema.copy.'+name,(R/'specification/v2/contracts'/(name+'.schema.json')).read_bytes()==(R/'services/api/internal/contracts/schemas'/(name+'.schema.json')).read_bytes())
measurement=load('audio-measurement');ns['namespace']['ck']('i16.actual.finding.typed',{'target_unit_id','auditory_finding'}<=set(measurement['properties']))
ns['namespace']['ck']('i16.native.legacy.rows.valid',not {'target_unit_id','auditory_finding'}&set(measurement['required']))
ns['namespace']['ck']('i16.library.safe.digest','audio_sha256' in load('library-item')['properties'] and not {'units','utterances','target_count'}&set(load('library-item')['properties']))
ns['namespace']['ck']('i16.audio.prompt.copy',(R/'specification/v2/prompts/audio-judge-v1.txt').read_bytes()==(R/'services/api/internal/app/generationdata/audio-judge-v1.txt').read_bytes())
result={'status':'passed','assertions':len(checks),'checks':checks,'proof_boundary':'Static current schema/reference/prompt/vector/copy checks only; not actual model or product behavior.'}
Path(sys.argv[1]).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
