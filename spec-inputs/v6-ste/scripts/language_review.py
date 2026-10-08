#!/usr/bin/env python3
"""Inspect actual prose. This checker does not certify STE compliance."""
from __future__ import annotations
import json
import re
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
PROSE_KEYS = {
    'description','definition','inclusion_criteria','exclusion_criteria',
    'correction_contract','scoring_contract','reference_limit','coverage_requirement','annotation_priority',
    'scope','id_compatibility','units','zero_denominator','unresolved','inputs','zero_rule','aggregation',
    'authority','selection_rationale','request_format','local_audio','deployment_lock_required',
    'acquisition','rights','use','prohibited','release_rule','context','evidence_scope','finding',
    'required_action','runtime_rule','reason','limits','required_evidence','purpose','meaning','definition'
}
BANNED = re.compile(r'\b(?:should|would|may|might|could)\b', re.I)
CONTRACTIONS = re.compile(r"\b\w+(?:n't|'ll|'re|'ve|'d)\b|\bit's\b|\byou're\b", re.I)
PERFECT = re.compile(r'\b(?:has|have|had)\s+been\b|\b(?:has|have)\s+\w+ed\b', re.I)


def literals_removed(text: str) -> str:
    text = re.sub(r'`[^`\n]+`', ' LITERAL ', text)
    # Quote spans are literal language data or named text under the writing rules.
    text = re.sub(r'"[^"\n]*"', ' QUOTE ', text)
    text = re.sub(r'https?://\S+', ' URL ', text)
    text = re.sub(r'\([^()]*\)', ' PARENTHESIS ', text)
    return text


def inspect(text: str, path: str, location: str, limit: int) -> list[dict]:
    body = literals_removed(text.strip())
    if not body or not re.search(r'[A-Za-z]', body):
        return []
    issues=[]
    for rule,pattern in [('modal',BANNED),('contraction',CONTRACTIONS),('perfect_tense',PERFECT),
                         ('semicolon',re.compile(';')),('em_dash',re.compile('—'))]:
        for m in pattern.finditer(body):
            issues.append({'path':path,'location':location,'rule':rule,'text':text,'match':m.group(0)})
    for sent in re.split(r'(?<=[.!?:])\s+',body):
        words = re.findall(r"[A-Za-z0-9]+(?:[-_'.][A-Za-z0-9]+)*",sent)
        if len(words)>limit:
            issues.append({'path':path,'location':location,'rule':'sentence_length','words':len(words),'limit':limit,'text':text})
    return issues


def md_units(text: str):
    in_code=False
    for n,line in enumerate(text.splitlines(),1):
        if line.strip().startswith('```'):
            in_code=not in_code;continue
        if in_code or line.lstrip().startswith('#') or not line.strip():continue
        if re.match(r'^\s*\|[\s:|\-]+\|\s*$',line):continue
        if line.startswith('|'):
            for col,cell in enumerate(line.strip('|').split('|'),1):yield f'{n}:cell{col}',cell.strip()
        else:
            s=re.sub(r'^\s*(?:[-*]\s+|\d+\.\s+)(?:\[ \]\s+)?','',line)
            s=re.sub(r'^\*\*(GIVEN|WHEN|THEN|AND)\*\*\s*','',s)
            yield str(n),s


def structured_units(x,path=''):
    if isinstance(x,dict):
        for k,v in x.items():
            if k=='example':continue
            if k in PROSE_KEYS:
                if isinstance(v,str):yield path+'/'+k,v
                elif isinstance(v,list):
                    for i,s in enumerate(v):
                        if isinstance(s,str):yield f'{path}/{k}/{i}',s
            if not isinstance(v,str):yield from structured_units(v,path+'/'+k)
    elif isinstance(x,list):
        for i,v in enumerate(x):yield from structured_units(v,path+'/'+str(i))


def run() -> dict:
    issues=[];files=[];units=0
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(ROOT).as_posix()
        if rel.startswith(('audit/','restricted/')) or rel in ['manifest.json','language/field-index.json']:continue
        if p.suffix=='.md' or (p.suffix=='.txt' and rel.startswith('prompts/')):
            limit=20 if rel=='AGENTS.md' or rel.startswith('prompts/') else 25
            inp=md_units(p.read_text()) if p.suffix=='.md' else ((str(i),s) for i,s in enumerate(p.read_text().splitlines(),1))
        elif p.suffix in ['.json','.yaml','.yml']:
            try:
                x=json.loads(p.read_text()) if p.suffix=='.json' else yaml.safe_load(p.read_text())
            except (ValueError,yaml.YAMLError):continue
            limit=25;inp=structured_units(x)
        elif p.name=='.env.example':
            limit=20;inp=((str(i),s.lstrip('# ')) for i,s in enumerate(p.read_text().splitlines(),1) if s.startswith('#'))
        else:continue
        files.append(rel)
        for loc,text in inp:
            units+=1;issues.extend(inspect(text,rel,loc,limit))
    return {'scope':'Selected prose and all schema field descriptions. Protected code, formulas, and learner payloads are excluded.',
            'checker':'project mechanical checker based on read SimpleEnglish guidance',
            'official_dictionary_checked':False,'semantic_equivalence_proven':False,
            'files_checked':len(files),'prose_units_checked':units,'findings':issues,
            'status':'mechanical_issues_present' if issues else 'selected_mechanical_checks_pass',
            'limitations':['No full dictionary or part-of-speech analysis.','No complete passive-voice or first-use terminology analysis.',
                           'Sentence segmentation and literal recognition are heuristic.','Zero findings do not certify ASD-STE100 compliance.']}

if __name__=='__main__':
    result=run()
    (ROOT/'audit/language-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='findings'},indent=2))
    print('findings:',len(result['findings']))
