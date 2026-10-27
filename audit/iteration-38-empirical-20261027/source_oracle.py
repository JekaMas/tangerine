"""Independent original M2 census for report arithmetic; no toolkit/model/hash audit."""
import collections,json,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/iteration-38-empirical-20261027'
CORPORA=Path('/Users/jekamas/projects/0xatelerix/tangerine/data/corpora')
def census(text):
    windows=[];current=None
    for line in text.splitlines():
        if line.startswith('S '):
            if current is not None:windows.append(current)
            current={'words':len(line[2:].split()),'edits':[]}
        elif line.startswith('A ') and current is not None:
            fields=line.split('|||');start,end=map(int,fields[0].split()[1:]);current['edits'].append((int(fields[5]),start,end,fields[1]))
    if current is not None:windows.append(current)
    count=collections.Counter();presence=collections.Counter();pairs=collections.Counter();exclusions=collections.Counter();annotated=words=0
    for w in windows:
        candidates=w['edits'];selected=min((e[0] for e in candidates),default=None);labels=[];usable=selected is not None
        for annotator,start,end,label in candidates:
            if annotator!=selected:continue
            reason='noop' if label=='noop' or start==end==-1 else 'invalid' if start<0 or end<start or end>w['words'] else 'unresolved_native_label' if label in ['UNK','Um'] else None
            if reason:
                exclusions[reason]+=1
                if reason!='noop':usable=False
            else:labels.append(label);count[label]+=1
        if not usable:continue
        annotated+=1;words+=w['words'];types=collections.Counter(labels);presence.update(types.keys())
        for a in sorted(types):
            for b in sorted(types):
                if a!=b or types[a]>=2:pairs[(a,b)]+=1
    return dict(windows=len(windows),annotated=annotated,words=words,events=sum(count.values()),counts=dict(count),presence=dict(presence),pairs=[dict(a=a,b=b,count=n) for (a,b),n in sorted(pairs.items())],excluded=dict(exclusions))
def main():
    views={}
    for name in ['fce_v2.1.bea19.tar.gz','wi+locness_v2.1.bea19.tar.gz']:
        with tarfile.open(CORPORA/'bea'/name,'r:gz') as archive:
            for member in archive:
                if member.isfile() and member.name.endswith('.m2'):
                    views[member.name]=census(archive.extractfile(member).read().decode('utf-8'))
    (OUT/'independent-m2-oracle.json').write_text(json.dumps(views,indent=2)+'\n')
    print(json.dumps({name:{k:v for k,v in row.items() if k in ['windows','annotated','words','events']} for name,row in views.items()},indent=2))
if __name__=='__main__':main()
