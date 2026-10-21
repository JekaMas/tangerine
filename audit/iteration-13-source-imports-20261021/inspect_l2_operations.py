"""Independent native grammar counter; no application parser, extraction or hash audit."""
from pathlib import Path
import collections,json,re,zipfile
R=Path(__file__).resolve().parents[2];A=Path(__file__).resolve().parent;root=Path('/Users/jekamas/projects/0xatelerix/tangerine/data/corpora/l2-arctic/mirror')
totals={'read':collections.Counter(),'suitcase':collections.Counter()};bare={'read':collections.Counter(),'suitcase':collections.Counter()};other=collections.Counter();files=0
for archive in sorted(root.glob('*.zip')):
 scope='suitcase' if archive.stem=='suitcase_corpus' else 'read'
 with zipfile.ZipFile(archive) as z:
  for member in z.namelist():
   if Path(member).parent.name!='annotation' or not member.lower().endswith('.textgrid'):continue
   files+=1;text=z.read(member).decode('utf-8-sig');blocks=re.findall(r'^\s*item\s*\[\d+\]:\s*\n(.*?)(?=^\s*item\s*\[\d+\]:|\Z)',text,re.M|re.S)
   for block in blocks:
    names=re.findall(r'name\s*=\s*"([^"]*)"',block)
    if names!=['phones']:continue
    for raw in re.findall(r'text\s*=\s*"((?:[^"]|"")*)"',block):
     label=raw.replace('""','"');parts=[x.strip() for x in label.split(',')]
     if len(parts)==3 and parts[2].lower() in ('s','d','a'):totals[scope][parts[2].lower()]+=1
     elif label.strip().lower() in ('s','d','a'):bare[scope][label.strip().lower()]+=1
     elif len(parts)>1:other[scope]+=1
result=dict(method='independent Python native item-block/quoted-label extraction; require three comma-separated fields and the documented operation with actual source case aliases; unchanged bareARPAbetS/D are not events',manual_files=files,operation_counts={k:dict(v) for k,v in totals.items()},historical_bare_symbol_false_positives={k:dict(v) for k,v in bare.items()},other_comma_labels=dict(other),historical_receipt='audit/corpus-acquisition-20261009/l2-arctic-native-annotation-accounting.json',source_bytes_changed=False,dataset_code_executed=False)
(A/'L2-OPERATION-CORRECTION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
