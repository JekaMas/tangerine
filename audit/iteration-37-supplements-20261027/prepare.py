"""Prepare acquired inert source members once, without a repeated hash audit."""
import json,tarfile,shutil,concurrent.futures
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/iteration-37-supplements-20261027';CORPUS=Path('/Users/jekamas/projects/0xatelerix/tangerine/data/corpora')
JOBS=[('edacc','edacc/edacc_v1.0.tar.gz','edacc-v10-current-native-inventory.json'),('elrd','elrd/owner-7e4c8f377b8d5cedff7dd429eb2050084a6a1b08.tar.gz',None),('dral-base','dral/DRAL-16kHz.tgz','dral-16khz-native-inventory.json'),('dral-8','dral/DRAL-8.0-fixes-plus-testdata.tar.gz','dral-latest-increment-native-inventory.json')]
def prepare(job):
 name,archive,inventory=job;folder=OUT/'members'/name;folder.mkdir(parents=True,exist_ok=True);index=OUT/(name+'-prepared.json')
 if index.exists():return json.loads(index.read_text())
 admitted={m['path']:m for m in json.loads((ROOT/'audit/corpus-acquisition-20261009'/inventory).read_text())['members'] if m['kind']=='file'} if inventory else {}
 files=[]
 with tarfile.open(CORPUS/archive,mode='r|gz') as stream:
  for member in stream:
   if not member.isfile():continue
   path=Path(member.name)
   if path.is_absolute() or '..' in path.parts:raise ValueError('Unexpected native path')
   destination=folder/path;destination.parent.mkdir(parents=True,exist_ok=True)
   if not destination.exists():
    temporary=destination.with_name(destination.name+'.preparing')
    with stream.extractfile(member) as source,temporary.open('wb') as target:shutil.copyfileobj(source,target,1024*1024)
    temporary.replace(destination)
   files.append(dict(path=member.name,bytes=member.size,sha256=admitted.get(member.name,{}).get('sha256')))
 value=dict(name=name,archive=str(CORPUS/archive),inventory=inventory,files=files,prepared_root=str(folder),scope='Actual acquired files, scripts remain inert; reuse admitted identities, no hash audit.')
 index.write_text(json.dumps(value,indent=2)+'\n');print(name,len(files),'prepared',flush=True);return value
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(prepare,JOBS))
 (OUT/'prepared.json').write_text(json.dumps(results,indent=2)+'\n')
