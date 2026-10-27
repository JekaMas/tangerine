"""Independent census of accepted original phone labels, not report projections."""
import collections,json,subprocess,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/iteration-38-empirical-20261027'
store=ROOT/'data/iteration-35-official-l2-20261027'
name=json.loads((store/'stack.json').read_text())['name']
choices=json.loads((OUT/'native-35/catalogue.json').read_text());identity=str(uuid.UUID(next(c['source']['import_id'] for c in choices if c['data_origin']=='native')))
sql="""SELECT CASE WHEN strpos(lower(member),'suitcase')>0 THEN 'suitcase' ELSE 'read' END,
 count(*) FILTER(WHERE lower(trim(split_part(native_row->>'label',',',3)))='s'),
 count(*) FILTER(WHERE lower(trim(split_part(native_row->>'label',',',3)))='d'),
 count(*) FILTER(WHERE lower(trim(split_part(native_row->>'label',',',3)))='a'),count(*)
 FROM source_row WHERE import_id='"""+identity+"""' AND table_name='intervals'
 AND strpos(lower(member),'/annotation/')>0 AND lower(native_row->>'tier')='phones'
 GROUP BY member ORDER BY member;"""
r=subprocess.run(['docker','exec','-i',name+'-postgres','psql','-U','tangerine','-d','tangerine','-At','-F','\t'],input=sql,text=True,capture_output=True,check=True)
result={}
for line in r.stdout.splitlines():
 task,*numbers=line.split('\t');s,d,a,intervals=map(int,numbers)
 v=result.setdefault(task,dict(windows=0,intervals=0,events=0,counts=collections.Counter(),presence=collections.Counter(),pairs=collections.Counter()))
 v['windows']+=1;v['intervals']+=intervals;counts={'s':s,'d':d,'a':a};v['counts'].update(counts);v['events']+=s+d+a
 v['presence'].update(k for k,n in counts.items() if n)
 for first,n in counts.items():
  for second,m in counts.items():
   if n and m and (first!=second or n>=2):v['pairs'][first,second]+=1
for v in result.values():v['pairs']=[dict(a=a,b=b,count=n) for (a,b),n in sorted(v['pairs'].items())]
(OUT/'independent-l2-oracle.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:{a:b for a,b in v.items() if a not in ['pairs','presence']} for k,v in result.items()}))
