#!/usr/bin/env python3
"""Examine actual package files without artificial assessment inputs."""
from __future__ import annotations
import ast
import hashlib
import importlib.metadata
import json
import platform
import re
import shutil
import sys
from pathlib import Path
import jsonschema
import sympy as sp
import yaml
from language_review import run as language_run

ROOT=Path(__file__).resolve().parents[1]

def load(name):
    p=ROOT/name
    return yaml.safe_load(p.read_text()) if p.suffix in ['.yaml','.yml'] else json.loads(p.read_text())

def digest(data):return hashlib.sha256(data).hexdigest()

def ast_hash(text):
    tree=ast.parse(text)
    for n in ast.walk(tree):
        if isinstance(n,(ast.Module,ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) and n.body:
            first=n.body[0]
            if isinstance(first,ast.Expr) and isinstance(first.value,ast.Constant) and isinstance(first.value.value,str):n.body.pop(0)
    return digest(ast.dump(tree,include_attributes=False).encode())

def symbolic(n):
    if isinstance(n,ast.Expression):return symbolic(n.body)
    if isinstance(n,ast.Name):return sp.Symbol(n.id)
    if isinstance(n,ast.Constant) and type(n.value) is int:return sp.Integer(n.value)
    if isinstance(n,ast.BinOp):
        a,b=symbolic(n.left),symbolic(n.right)
        if isinstance(n.op,ast.Add):return a+b
        if isinstance(n.op,ast.Sub):return a-b
        if isinstance(n.op,ast.Mult):return a*b
        if isinstance(n.op,ast.Div):return a/b
    raise ValueError('Unsupported symbolic formula syntax')

def schema_objects(x):
    if isinstance(x,dict):
        if x.get('type')=='object' or 'properties' in x:yield x
        for v in x.values():yield from schema_objects(v)
    elif isinstance(x,list):
        for v in x:yield from schema_objects(v)

def main():
    checks=[]
    def add(name,ok,details):checks.append({'name':name,'status':'pass' if ok else 'fail','details':details})
    baseline=load('audit/baseline-lock.json')
    metrics=load('domain/metrics.v1.yaml');tax=load('domain/error-taxonomy.v1.yaml')
    add('taxonomy_id_preservation',[x['id'] for x in tax['items']]==baseline['taxonomy_ids'],{'count':len(tax['items'])})
    changed=[]
    for x in tax['items']:
        actual=digest(json.dumps(x['example'],ensure_ascii=False,sort_keys=True).encode())
        if actual!=baseline['example_payload_sha256'][x['id']]:changed.append(x['id'])
    add('literal_example_preservation',not changed,{'changed':changed,'human_review_claims':sum(bool(x['example']['expert_reviewed']) for x in tax['items'])})
    for kind,basekey in [('metrics','core_formulas'),('auxiliary_metrics','auxiliary_formulas')]:
        current={m['id']:m['formula'] for m in metrics[kind]}
        add(kind+'_formula_preservation',current==baseline[basekey],{'count':len(current)})
    schema_results=[];objects=0;missing_descriptions=[]
    for p in sorted((ROOT/'contracts').glob('*.schema.json')):
        d=json.loads(p.read_text());jsonschema.Draft202012Validator.check_schema(d)
        obs=list(schema_objects(d));objects+=len(obs)
        for o in obs:
            for k,v in o.get('properties',{}).items():
                if not v.get('description'):missing_descriptions.append(p.name+':'+k)
        schema_results.append({'file':p.name,'closed':all(o.get('additionalProperties') is False for o in obs)})
    add('schema_syntax_and_closed_objects',all(s['closed'] for s in schema_results),{'schemas':len(schema_results),'objects':objects,'files':schema_results})
    add('all_field_descriptions_present',not missing_descriptions,{'missing':missing_descriptions})
    for n,expected in baseline['reference_ast_sha256'].items():
        f=ROOT/'reference'/n
        add('reference_algorithm_preserved:'+n,ast_hash(f.read_text())==expected,{'source':'Actual AST without docstrings. No constructed teacher answers.'})
    tree=ast.parse((ROOT/'reference/scorer.py').read_text())
    values=next(n.value.elts for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='values' for t in n.targets))
    proofs=[]
    for m,pair in zip(metrics['metrics'],values):
        expected=symbolic(ast.parse(m['formula'],mode='eval')).subs(sp.Symbol('WFP'),sp.Symbol('FP'))
        actual=symbolic(pair.elts[0])/symbolic(pair.elts[1])
        proofs.append({'metric':m['id'],'symbolic_difference':str(sp.simplify(expected-actual))})
    add('core_symbolic_conformance',len(proofs)==27 and all(x['symbolic_difference']=='0' for x in proofs),
        {'assumption':'WFP=FP, as stated in the retained policy. Algebra does not prove semantic decisions or zero-denominator behavior.','proofs':proofs})
    paths=list((ROOT/'openspec/changes/bootstrap-teacher-error-trainer/specs').glob('*/spec.md'))
    ids=[];bad=[];scenarios=0
    for p in paths:
        text=p.read_text()
        for part in re.split(r'^### Requirement: ',text,flags=re.M)[1:]:
            rid=part.split()[0];ids.append(rid)
            n=len(re.findall(r'^#### Scenario:',part,re.M));scenarios+=n
            if n<2 or 'MUST' not in part.split('#### Scenario:')[0]:bad.append(rid)
    add('openspec_local_structure',not bad and len(ids)==len(set(ids)),{'capabilities':len(paths),'requirements':len(ids),'scenarios':scenarios,'invalid':bad,'official_cli':False})
    add('requirement_id_preservation',set(baseline['requirement_ids'])<=set(ids),{'new_ids':sorted(set(ids)-set(baseline['requirement_ids']))})
    profiles=load('domain/providers.v1.yaml')['profiles']
    bad_profiles=[p['id'] for p in profiles if p['provider'] in ['mock','first_party_recording']]
    add('no_active_mock_or_recording_profile',not bad_profiles,{'profiles':[p['id'] for p in profiles]})
    compose=load('deploy/local/compose.reference.yaml')
    bad_modes=[]
    for n,v in compose['services'].items():
        for k,s in v.get('environment',{}).items():
            if 'mock' in str(s).lower():bad_modes.append(n+'.'+k)
    add('compose_no_mock_or_fake_seed',not bad_modes and 'seed' not in compose['services'],{'services':list(compose['services']),'bad_modes':bad_modes,'docker_executed':False})
    decisions=load('approvals/decisions.json')['decisions']
    add('no_invented_owner_approval',decisions==[],{'exception_decisions':len(decisions)})
    add('no_inherited_artificial_tests_shipped',not (ROOT/'tests').exists(),{'inventory':'restricted/inherited-tests.json'})
    for p in (ROOT/'reference').glob('*.py'):compile(p.read_text(),str(p),'exec')
    add('reference_python_syntax',True,{'execution':'Compilation only. No artificial inputs.'})
    prompt_errors=[]
    for t in load('prompts/manifest.yaml')['templates']:
        if digest((ROOT/t['path']).read_bytes())!=t['sha256']:prompt_errors.append(t['id'])
    add('prompt_hashes',not prompt_errors,{'mismatches':prompt_errors})
    lang=language_run()
    (ROOT/'audit/language-results.json').write_text(json.dumps(lang,ensure_ascii=False,indent=2)+'\n')
    add('selected_mechanical_language_checks',not lang['findings'],{'files':lang['files_checked'],'prose_units':lang['prose_units_checked'],'findings':len(lang['findings']),'full_STE_compliance':False})
    outcome={
        'package':'teacher-error-trainer-openspec-v6-ste','review_date':'2026-10-03',
        'python':sys.version.split()[0],'platform':platform.machine(),
        'dependencies':{x:importlib.metadata.version(x) for x in ['jsonschema','PyYAML','sympy']},
        'checks':checks,'passed':sum(x['status']=='pass' for x in checks),'failed':sum(x['status']=='fail' for x in checks),
        'synthetic_assessment_inputs_created':0,'real_audio_assets_tested':0,'live_provider_requests':0,
        'not_run':['Official ASD-STE100 dictionary and sense review','Official OpenSpec CLI','Docker application E2E','Live provider calibration','Human audio gold evaluation'],
        'unresolved_properties':len(load('audit/open-decisions.json')),
        'release_status':'blocked','absolute_correctness_proven':False}
    (ROOT/'audit/validation-results.json').write_text(json.dumps(outcome,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in outcome.items() if k!='checks'},indent=2))
    for c in checks:
        if c['status']=='fail':print('FAILED',c['name'],c['details'])
    return 1 if outcome['failed'] else 0

if __name__=='__main__':raise SystemExit(main())
