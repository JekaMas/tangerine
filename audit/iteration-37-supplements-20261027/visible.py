"""Independent visible strings from acquired native records, not app projections."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/iteration-37-supplements-20261027';CORPUS=Path('/Users/jekamas/projects/0xatelerix/tangerine/data/corpora')
a=OUT/'members/edacc/edacc_v1.0';segment=(a/'dev/segments').read_text().splitlines()[0].split();texts=dict(line.split(' ',1) for line in (a/'dev/text').read_text().splitlines());expected={'edacc':dict(id=segment[0],text=texts[segment[0]])}
p=sorted((OUT/'members/elrd').glob('*/diarized_transcripts/*.jsonl'))[0];v=json.loads(p.read_text().splitlines()[0]);expected['elrd']=dict(id='0',text=v['transcript'])
p=CORPUS/'diplomat';v=json.loads((p/'CQA_task_dataset/test.jsonl').read_text().splitlines()[0]);pir=json.loads((p/'PIR_second_subtask_dataset/test.jsonl').read_text().splitlines()[0]);expected['diplomat']=dict(id='0',text='\n'.join(v['text']),selected_choice=pir['choice'][pir['label']])
for name,file in [('dral-base','DRAL16kHz/metadata/conversation.csv'),('dral-8','DRAL-8.0/conversation.csv')]:
 with (OUT/'members'/name/file).open() as f:v=next(csv.DictReader(f))
 expected[name]=dict(id=v['id'],text=None)
(OUT/'expected-visible.json').write_text(json.dumps(expected,indent=2)+'\n');print('Five native visible baselines saved')
