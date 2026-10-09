"""Inspect pinned mirror archives without extraction or dataset code execution."""
from pathlib import Path
import json,zipfile,hashlib,wave,io,time
ROOT=Path(__file__).resolve().parents[2]; AUDIT=Path(__file__).resolve().parent
jobs=json.loads((AUDIT/'l2-mirror-download-jobs.json').read_text());results=[]
expected={'ABA':1129,'ASI':1131,'BWC':1130,'EBVS':1007,'ERMS':1132,'HJK':1131,'HKK':1131,'HQTV':1132,'LXC':1131,'MBMPS':1132,'NCC':1131,'NJS':1131,'PNV':1132,'RRBI':1130,'SKA':974,'SVBI':1132,'THV':1132,'TLV':1132,'TNI':1131,'TXHC':1132,'YBAA':1130,'YDCK':1131,'YKWK':1131,'ZHAA':1132}
for job in jobs:
 if not job['file'].endswith('.zip'):continue
 rp=AUDIT/(job['id']+'-receipt.json')
 while not rp.exists():time.sleep(2)
 receipt=json.loads(rp.read_text())
 if receipt['status']!='download_verified':raise RuntimeError(receipt)
 path=ROOT/receipt['path'];members=[];layers={};errors=[];rates={};operations={};manual_tiers=set()
 with zipfile.ZipFile(path) as z:
  for i in z.infolist():
   if i.is_dir():continue
   b=z.read(i);parts=Path(i.filename).parts; layer=parts[-2] if len(parts)>1 else 'root';layers[layer]=layers.get(layer,0)+1
   members.append({'path':i.filename,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
   if i.filename.endswith('.wav'):
    with wave.open(io.BytesIO(b)) as w:key=str((w.getframerate(),w.getnchannels(),w.getsampwidth()))
    rates[key]=rates.get(key,0)+1
   if layer=='annotation' and i.filename.lower().endswith('.textgrid'):
    s=b.decode('utf-8-sig');import re
    manual_tiers.update(re.findall(r'name\s*=\s*"([^"]+)"',s))
    for label in re.findall(r'text\s*=\s*"((?:[^"]|"")*)"',s):
     op=label.replace('""','"').split(',')[-1].strip().lower()
     if op in ('s','d','a'):operations[op]=operations.get(op,0)+1
 r={'archive':str(path.relative_to(ROOT)),'files_crc_read':len(members),'native_layers':layers,'wave_formats':rates,'manual_operation_label_counts':operations,'manual_tier_names':sorted(manual_tiers),'members':members,'errors':errors}
 if path.stem in expected:
  r['expected_read_waves']=expected[path.stem];assert layers.get('wav')==expected[path.stem]
  assert layers.get('annotation')==(149 if path.stem=='YBAA' else 150)
 results.append(r);print(json.dumps({k:v for k,v in r.items() if k!='members'}),flush=True)
(AUDIT/'l2-arctic-mirror-native-inventory.json').write_text(json.dumps({'source_commit':jobs[0]['source_commit'],'provenance':'third-party pinned raw mirror; unavailable official ZIP byte equivalence not claimed','archives':results,'read_wave_count':sum(r['native_layers'].get('wav',0) for r in results if 'expected_read_waves' in r),'read_manual_annotation_count':sum(r['native_layers'].get('annotation',0) for r in results if 'expected_read_waves' in r),'scope':'all archive members decrypted/read and CRC checked; native WAV headers and manual label counts; not production TextGrid import','dataset_code_executed':False},indent=2)+'\n')
