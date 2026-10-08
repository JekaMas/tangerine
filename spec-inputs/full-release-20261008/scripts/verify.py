#!/usr/bin/env python3
"""Inspect actual specification artifacts. This program creates no empirical fixtures.

This is not the official OpenSpec CLI, a PostgreSQL engine, an API test,
a dictionary-compliance certificate, or a live provider/corpus qualification.
"""
from __future__ import annotations
import argparse,ast,hashlib,importlib.metadata,json,pathlib,platform,re,sys,zipfile
from collections import Counter
from datetime import datetime,timezone
from urllib.parse import urlparse
import jsonschema
import sympy
import yaml

ROOT=pathlib.Path(__file__).resolve().parents[1]
CONTRACTS=ROOT/'contracts'
RESULTS=[]
def add(name,condition,details):
    RESULTS.append({'name':name,'status':'pass' if condition else 'fail','details':details})
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def walk(x,path=''):
    yield path,x
    if isinstance(x,dict):
        for k,v in x.items():yield from walk(v,path+'/'+str(k).replace('~','~0').replace('/','~1'))
    elif isinstance(x,list):
        for i,v in enumerate(x):yield from walk(v,path+'/'+str(i))
def pointer(d,fragment):
    for t in fragment.lstrip('/').split('/') if fragment else []:
        t=t.replace('~1','/').replace('~0','~')
        d=d[int(t)] if isinstance(d,list) else d[t]
    return d

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',type=pathlib.Path);args=ap.parse_args()
    docs={};parse_errors=[]
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file() or 'inputs' in p.relative_to(ROOT).parts:continue
        if p.suffix not in ('.json','.yaml','.yml'):continue
        try:docs[str(p.relative_to(ROOT))]=json.loads(p.read_text()) if p.suffix=='.json' else yaml.safe_load(p.read_text())
        except Exception as e:parse_errors.append({'path':str(p),'error':str(e)})
    add('structured_files_parse',not parse_errors,{'file_count':len(docs),'errors':parse_errors})
    schemas={p.name:json.loads(p.read_text()) for p in CONTRACTS.glob('*.schema.json')}
    errors=[]
    for n,d in schemas.items():
        try:jsonschema.Draft202012Validator.check_schema(d)
        except Exception as e:errors.append({'file':n,'error':str(e)})
    add('json_schema_meta_validation',not errors,{'schema_count':len(schemas),'errors':errors})
    refs=[];closure=[];objcount=0
    for name,d in schemas.items():
        for loc,x in walk(d):
            if not isinstance(x,dict):continue
            if x.get('type')=='object':
                objcount+=1
                if x.get('additionalProperties') is not False:closure.append(name+loc)
            if '$ref' in x:
                base,_,frag=x['$ref'].partition('#')
                try:
                    if base.startswith('http') and not base.startswith('https://tangerine.invalid/schemas/'):
                        raise ValueError('unbound remote namespace')
                    target=pathlib.Path(urlparse(base).path).name if base else name
                    pointer(schemas[target],frag)
                except Exception as e:refs.append({'file':name,'pointer':loc,'ref':x['$ref'],'error':str(e)})
    add('all_schema_objects_closed',not closure,{'object_count':objcount,'open_objects':closure})
    add('schema_references_resolve',not refs,{'errors':refs})
    gaps=docs['audit/gap-status.json']['entries'];expected={f'GAP-{i:03d}' for i in range(1,56) if i not in (5,6)}
    add('53_gap_inventory',len(gaps)==53 and {g['gap_id'] for g in gaps}==expected,{'count':len(gaps),'status_counts':dict(Counter(g['status'] for g in gaps))})
    missing=[{'gap':g['gap_id'],'path':a}for g in gaps for a in g['artifacts'] if not (ROOT/a).is_file()]
    add('gap_artifact_references_exist',not missing,{'missing':missing})
    specs=list((ROOT/'openspec/changes/complete-full-local-release/specs').glob('*/spec.md'))
    spec_errors=[];rc=sc=0
    for p in specs:
        text=p.read_text();rc+=len(re.findall(r'^### Requirement:',text,re.M));sc+=len(re.findall(r'^#### Scenario:',text,re.M))
        if not text.startswith('## ADDED Requirements') or 'MUST' not in text or text.count('#### Scenario:')<2:
            spec_errors.append(str(p.relative_to(ROOT)))
    add('openspec_structure_only',not spec_errors and rc==53,{'capabilities':len(specs),'requirements':rc,'scenarios':sc,'errors':spec_errors,'official_cli':False})
    zpath=ROOT/'inputs/teacher-error-trainer-openspec-v6-ste.zip'
    with zipfile.ZipFile(zpath) as z:
        def original(suffix):
            names=[n for n in z.namelist() if n.endswith('/'+suffix)]
            if len(names)!=1:raise ValueError('ambiguous baseline file '+suffix)
            return yaml.safe_load(z.read(names[0]))
        original_tax=original('domain/error-taxonomy.v1.yaml');original_metrics=original('domain/metrics.v1.yaml')
    tax=docs['domain/error-taxonomy.v1.yaml'];old={i['id']:i for i in original_tax['items']};new={i['id']:i for i in tax['items']}
    add('122_taxonomy_ids_preserved',len(new)==122 and set(new)==set(old),{'count':len(new)})
    changed=[i for i in old if old[i].get('example')!=new.get(i,{}).get('example')]
    add('protected_linguistic_examples_preserved',not changed,{'changed':changed,'examples_are_not_gold':True})
    m=docs['domain/metrics.v1.yaml']
    for key,count in [('metrics',27),('auxiliary_metrics',15)]:
        before={x['id']:x['formula'] for x in original_metrics[key]};after={x['id']:x['formula'] for x in m[key]}
        add(key+'_identities_and_formulas_preserved',before==after and len(after)==count,{'count':len(after)})
    # Compare actual calculation expressions, without constructed teacher records.
    tree=ast.parse((ROOT/'reference/scorer.py').read_text());vals=None;metric_ids=None;component_map=None
    for n in ast.walk(tree):
        if isinstance(n,ast.Assign):
            if any(isinstance(t,ast.Name) and t.id=='values' for t in n.targets):vals=n.value
            if any(isinstance(t,ast.Name) and t.id=='METRIC_IDS' for t in n.targets):metric_ids=ast.literal_eval(n.value)
            if any(isinstance(t,ast.Name) and t.id=='component_map' for t in n.targets):component_map=ast.literal_eval(n.value)
    assert isinstance(vals,ast.List)
    def symbolic(node):
        if isinstance(node,ast.Name):return sympy.Symbol(node.id)
        if isinstance(node,ast.Constant) and type(node.value) is int:return sympy.Integer(node.value)
        if isinstance(node,ast.BinOp):
            a,b=symbolic(node.left),symbolic(node.right)
            if isinstance(node.op,ast.Add):return a+b
            if isinstance(node.op,ast.Sub):return a-b
            if isinstance(node.op,ast.Mult):return a*b
            if isinstance(node.op,ast.Div):return a/b
        raise ValueError('unsupported symbolic expression')
    equalities=[]
    formulas={x['id']:x['formula'] for x in m['metrics']}
    for mid,expr in zip(metric_ids,vals.elts,strict=True):
        actual=symbolic(expr.elts[0])/symbolic(expr.elts[1])
        expected_expr=symbolic(ast.parse(formulas[mid],mode='eval').body).subs(sympy.Symbol('WFP'),sympy.Symbol('FP'))
        equalities.append({'metric_id':mid,'equal':sympy.simplify(actual-expected_expr)==0})
    add('27_symbolic_calculation_equalities',all(x['equal']for x in equalities),{'equalities':equalities,'boundary_and_semantic_inputs':'not_executed_with_empirical_records'})
    expected_composite={'detection':('detection.f1',45),'classification':('classification.hierarchical_recall',15),'correction':('correction.graded_recall',30),'explanation':('explanation.graded_recall',10)}
    add('composite_components_and_weights',component_map==expected_composite,{'actual':component_map})
    add('exact_composite_field_present','exact_value_0_100'in schemas['score-result.schema.json']['properties']['composite']['properties'],{'no_empirical_score_created':True})
    aux_text=json.dumps(schemas['auxiliary-results.schema.json'])
    absent=[x['id']for x in m['auxiliary_metrics']if x['id']not in aux_text]
    add('15_auxiliary_output_slots',not absent,{'missing':absent})
    pm=docs['prompts/manifest.yaml'];pe=[]
    for b in pm['bindings']:
        if b['prompt_sha256']!=sha(ROOT/b['path']):pe.append(b['stage']+':prompt')
        for k in ['input','output']:
            if b[k+'_schema_sha256']!=sha(CONTRACTS/b[k+'_schema']):pe.append(b['stage']+':'+k)
    add('six_prompt_schema_bindings_hash_exact',not pe and len(pm['bindings'])==6,{'count':len(pm['bindings']),'errors':pe})
    op=docs['domain/operations.yaml']['operations'];oa=docs['contracts/openapi.yaml'];oe=[]
    for o in op:
        schema=oa['paths'].get(o['path'],{}).get(o['method'].lower(),{})
        if schema.get('operationId')!=o['id']:oe.append(o['id'])
        for side in ['request','response']:
            name=o.get(side)
            if not name or name in ['binary','none'] or name.startswith('binary:'):continue
            name=name.removeprefix('list:')
            if name+'.schema.json'not in schemas:oe.append(o['id']+':'+name)
    add('internal_operation_inventory_and_bindings',not oe,{'operations':len(op),'errors':oe,'official_openapi_validator':False})
    profiles=docs['domain/providers.v1.yaml']['profiles'];pids={p['id']for p in profiles}
    configp=set(schemas['configuration.schema.json']['properties']['llm_profile']['enum'])
    add('configured_profile_ids_exist',configp<=pids,{'configured':sorted(configp),'available':sorted(pids)})
    add('no_mock_provider_profiles',not any('mock'in p['id'].lower()or p.get('provider')=='mock'for p in profiles),{'profile_count':len(profiles)})
    fe=schemas['extraction-input.schema.json']['properties']
    add('blind_extraction_shape_has_no_key',not set(fe)&{'key','ground_truth','transcript','rationales'}, {'allowed_fields':list(fe)})
    fb=schemas['feedback-output.schema.json']['properties'];add('model_feedback_has_no_server_receipt','receipt_id'not in fb and 'origin'not in fb,{'allowed_fields':list(fb)})
    am=docs['domain/target-capabilities.yaml']
    target_entries=am.get('targets',am.get('entries',am.get('items',[])))
    tids={x.get('taxonomy_id',x.get('id'))for x in target_entries}
    add('all_target_definitions_present',set(new)<=tids,{'count':len(target_entries),'missing':sorted(set(new)-tids)})
    vm=docs['domain/version-compatibility.yaml'];ve=[x['path']for x in vm['files']if not (ROOT/x['path']).is_file()or sha(ROOT/x['path'])!=x['sha256']]
    add('active_version_vector_hashes',not ve,{'members':len(vm['files']),'mismatches':ve})
    pyerrors=[]
    for p in (ROOT/'reference').glob('*.py'):
        try:compile(p.read_text(),str(p),'exec')
        except Exception as e:pyerrors.append({'file':str(p.relative_to(ROOT)),'error':str(e)})
    add('reference_python_compilation',not pyerrors,{'errors':pyerrors,'execution_of_real_answers':'not_run'})
    ce=docs['deploy/local/compose.reference.yaml'];ports=[(n,port)for n,s in ce['services'].items()for port in s.get('ports',[])]
    add('only_web_loopback_port_declared',bool(ports)and all(n=='web'and str(p).startswith('127.0.0.1:3000:')for n,p in ports),{'ports':ports,'docker_execution':'not_run'})
    zerrors=[]
    for p in (ROOT/'inputs').glob('*.zip'):
        with zipfile.ZipFile(p)as z:
            bad=z.testzip()
            if bad:zerrors.append({'zip':p.name,'member':bad})
    add('original_input_archive_integrity',not zerrors,{'errors':zerrors})
    dep={n:importlib.metadata.version(n)for n in ['jsonschema','PyYAML','sympy']}
    output={'inspection_date_utc':datetime.now(timezone.utc).isoformat(),'python':sys.version.split()[0],'platform':platform.platform(),'dependencies':dep,'checks':RESULTS,'summary':dict(Counter(x['status']for x in RESULTS)),
        'explicitly_not_proven':['All gaps semantically closed','Scoped policy approval','Current repository integration','Native private-source contract completeness','Actual source acquisition or rights','Genuine reviewer and gold observations','Live LLM/TTS/ASR qualification','Official OpenSpec CLI validation','Official OpenAPI validation','PostgreSQL migration execution','Docker amd64/arm64 end-to-end acceptance','Formal ASD-STE100 dictionary compliance']}
    if args.write:
        path=args.write if args.write.is_absolute()else ROOT/args.write;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(output,ensure_ascii=False,indent=2))
    return 1 if any(x['status']=='fail'for x in RESULTS)else 0
if __name__=='__main__':raise SystemExit(main())
