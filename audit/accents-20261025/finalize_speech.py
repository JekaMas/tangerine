"""Apply native transforms to retained actual pairs; no model calls."""
import base64,json,sys
from pathlib import Path
sys.path.insert(0,'/app')
from acoustic_runtime import transform_acoustic
p=Path('/evidence')
for voice in ['melo_en_au','melo_en_in']:
 d=p/voice;response=json.loads((d/'acoustic-response.json').read_text());piece=json.loads((d/'acoustic-input.json').read_text())['plan']['pieces'][0];resolved=json.loads((d/'resolved.json').read_text());native=response['receipt']['native']
 final=transform_acoustic({'piece_id':'accent-'+voice,'turn':piece,'native':native,'audio_base64':response['audio_base64'],'step':resolved['steps'][0]});(d/'mutated.wav').write_bytes(base64.b64decode(final.pop('audio_base64')));(d/'transformed.json').write_text(json.dumps(final,indent=2))
 assert final['receipt']['model_calls']==0
 print(voice,'transformed',final['sample_count'])
