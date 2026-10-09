"""Follow-up native tier/identity accounting; no production importer execution."""
from pathlib import Path
import json,re,zipfile,collections
ROOT=Path(__file__).resolve().parents[2];A=Path(__file__).resolve().parent
inv=json.loads((A/'l2-arctic-mirror-native-inventory.json').read_text());out=[]
for r in inv['archives']:
 layers=collections.defaultdict(set)
 for m in r['members']:
  p=Path(m['path']);layers[p.parent.name].add(p.stem)
 assert layers['wav']==layers['transcript'],r['archive']
 if 'expected_read_waves' in r:assert layers['wav']==layers['textgrid'] and layers['annotation'] <= layers['wav']
 else:assert layers['wav']==layers['annotation'] and layers['wav']==(set(x['archive'].split('/')[-1][:-4].lower() for x in inv['archives'] if 'expected_read_waves' in x)-{'asi','ska'})
 ops=collections.Counter();tiers=collections.Counter();parsed=0
 with zipfile.ZipFile(ROOT/r['archive']) as z:
  for m in r['members']:
   if Path(m['path']).parent.name!='annotation':continue
   s=z.read(m['path']).decode('utf-8-sig');blocks=re.findall(r'^\s*item\s*\[\d+\]:\s*\n(.*?)(?=^\s*item\s*\[\d+\]:|\Z)',s,re.M|re.S);phone=[]
   for b in blocks:
    names=re.findall(r'name\s*=\s*"([^"]*)"',b);assert len(names)==1,m['path'];tiers.update(names)
    if names[0]=='phones':phone.append(b)
   assert len(phone)==1,m['path'];parsed+=1
   for label in re.findall(r'text\s*=\s*"((?:[^"]|"")*)"',phone[0]):
    op=label.replace('""','"').split(',')[-1].strip().lower()
    if op in ('s','d','a'):ops[op]+=1
 out.append({'archive':r['archive'],'manual_files':parsed,'manual_tier_counts':dict(tiers),'phones_tier_operation_counts':dict(ops),'basename_joins_verified':True})
result={'archives':out,'read_phone_operations':dict(sum((collections.Counter(x['phones_tier_operation_counts']) for x in out[:-1]),collections.Counter())),'suitcase_phone_operations':out[-1]['phones_tier_operation_counts'],'scope':'exact long-format item blocks, counts only phones-tier mutation labels; non-phone and unknown tiers preserved in original bytes; no production parser or semantic leaf normalization','earlier_inventory_label_count_scope':'all text labels across tiers; not phonetic-event count'}
(A/'l2-arctic-native-annotation-accounting.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='archives'}))
