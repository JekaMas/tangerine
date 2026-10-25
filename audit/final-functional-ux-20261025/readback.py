"""One final native readback of the selected actual user/development records."""
from pathlib import Path
import json,urllib.request
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/final-functional-ux-20261025'
def get(name,path):
 value=json.load(urllib.request.urlopen('http://localhost:3000/api/v1/'+path,timeout=15));(OUT/(name+'.json')).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n');return value
for name,path in [('options-final','preparation-options'),('library-final','library'),('preparations-final','preparations?limit=100&view=public'),('attempts-final','attempts?limit=100'),('reports-final','reports/empirical'),('configuration-final','configuration'),('original-attempt-final','attempts/3f4535dd-6210-4303-9c33-209e19016b55'),('test-draft-final','attempts/0e7d0278-f199-4f79-b5aa-25295e23ce3c')]:get(name,path)
reports=json.loads((OUT/'reports-final.json').read_text());report=next(x for x in reports if x['title']=='Final functional review · constructed collocation report');get('constructed-report-final','reports/empirical/'+report['id'])
runs=get('experiments-final','lab/experiments');run=next(x for x in runs if x['id']==json.loads((OUT/'experiments-final.json').read_text())[0]['id']);full=get('starter-experiment-final','lab/experiments/'+run['id']); dataset=get('starter-dataset-final','lab/assets/'+full['dataset_asset_id']); get('starter-input-final','lab/assets/'+dataset['cases'][0]['input_asset_id']); get('starter-configuration-final','lab/assets/'+full['variants'][0]['configuration_asset_id'])
print('Selected native HTTP records saved; no inference, write, cleanup or provider changes.')
