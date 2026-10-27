"""Finite independent local ASR observation; no text reference supplied to model."""
import json
from pathlib import Path
from diagnostic_models import recognize
root=Path('/evidence')
for kind in ['obstructive','cooperative_backchannel']:
 for name in ['source-1.wav','mixed.wav']:
  target=root/kind/(name+'.asr.json')
  if target.exists():continue
  result=recognize((root/kind/name).read_bytes())
  target.write_text(json.dumps(result,ensure_ascii=False,indent=2))
  print(kind,name,result['hypothesis'],flush=True)
