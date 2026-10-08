"""Calculate the reference policy fractions. This module uses no network or model.

Input requires the separate semantic and scope checks.
"""
from fractions import Fraction
from typing import Any

DOMAINS = ('grammar','lexis','pronunciation.segmental','pronunciation.suprasegmental',
           'fluency','discourse','pragmatics_register','acceptable_variant')
METRIC_IDS = (
 'detection.precision','detection.recall','detection.f1','detection.miss_rate','detection.false_discovery_rate',
 'classification.coverage','classification.family_accuracy','classification.exact_accuracy',
 'classification.hierarchical_accuracy','classification.hierarchical_recall',
 'correction.attempt_rate','correction.strict_accuracy','correction.graded_accuracy','correction.strict_recall',
 'correction.graded_recall','correction.assertion_precision','explanation.coverage',
 'explanation.strict_accuracy','explanation.graded_accuracy','explanation.graded_recall',
 'decoy.overcorrection_rate','decoy.unflagged_rate','decoy.explicit_acceptability_accuracy',
 'acceptability.explicit_accuracy','weighted.precision','weighted.recall','weighted.f1')

def reporting_domain(node: str | None) -> str | None:
    if node is None:
        return None
    for d in sorted(DOMAINS, key=len, reverse=True):
        if node == d or node.startswith(d+'.'):
            return d
    return None

def hierarchical(pred: str, gold: str) -> Fraction:
    a,b=pred.split('.'),gold.split('.')
    shared=0
    for x,y in zip(a,b):
        if x != y: break
        shared+=1
    return Fraction(2*shared,len(a)+len(b))

def metric(n: int | Fraction, d: int | Fraction, reason: str='no_opportunities') -> dict[str,Any]:
    if d == 0:
        return dict(value=None,numerator=None,denominator=None,status='not_applicable',reason=reason)
    q=Fraction(n)/Fraction(d)
    if max(len(str(q.numerator)),len(str(q.denominator)))>4096: raise ValueError('numeric capacity exceeded')
    if not 0<=q<=1:
        raise ValueError('metric out of range')
    return dict(value=float(q),numerator=str(q.numerator),denominator=str(q.denominator),status='available',reason=None)

def credit(v: dict[str,int], supplied: bool) -> Fraction:
    if type(v['numerator']) is not int or type(v['denominator']) is not int or v['denominator']>9007199254740991 or v['denominator']<=0 or not 0<=v['numerator']<=v['denominator']:
        raise ValueError('invalid rubric fraction')
    q=Fraction(v['numerator'],v['denominator'])
    if not supplied and q:
        raise ValueError('credit without a supplied answer')
    return q

def calculate(payload: dict[str,Any], *, _include_domains: bool = True) -> dict[str,Any]:
    units=payload['units']; ds=payload['decisions']; comps=payload['components']
    if len(units)>1000 or len(ds)>2000: raise ValueError('scoring capacity exceeded')
    if set(comps)!={'detection','classification','correction','explanation'} or any(type(v) is not bool for v in comps.values()): raise ValueError('invalid component flags')
    byid={u['id']:u for u in units}
    if len(byid)!=len(units): raise ValueError('duplicate unit ID')
    for u in units:
        if u['domain'] not in DOMAINS or reporting_domain(u['taxonomy_id']) != u['domain']:
            raise ValueError('unit domain mismatch')
        if u['kind'] not in ('true_error','acceptable') or not 1<=u['weight']<=4:
            raise ValueError('invalid unit')
        if u['kind']=='acceptable' and (u['correction_eligible'] or u['explanation_eligible']):
            raise ValueError('decoy cannot be a repair/rationale opportunity in this policy')
    seen={}; normalized=[]; duplicates=0
    for d in ds:
        if d['id'] in seen: raise ValueError('duplicate decision ID')
        if d['unit_id'] is not None and d['unit_id'] not in byid: raise ValueError('unknown unit ID')
        credit(d['correction_credit'],d['correction_supplied'])
        credit(d['explanation_credit'],d['explanation_supplied'])
        if d['duplicate_of']:
            original=seen.get(d['duplicate_of'])
            if original is None or original['duplicate_of']: raise ValueError('invalid duplicate chain')
            comparable=lambda x:{k:v for k,v in x.items() if k not in ('id','duplicate_of')}
            if comparable(original)!=comparable(d): raise ValueError('conflicting duplicate')
            duplicates+=1
        else:
            normalized.append(d)
        seen[d['id']]=d
    unresolved=[d for d in normalized if d['verdict']=='unresolved']
    assigned={}
    for d in normalized:
        verdict=d['verdict']; uid=d['unit_id']; u=byid.get(uid)
        if verdict in ('ignore','unresolved'): continue
        if verdict not in ('matched_error','false_positive','confirmed_acceptable','wrong_acceptance'):
            raise ValueError('unknown decision verdict')
        if verdict in ('matched_error','wrong_acceptance') and (not u or u['kind']!='true_error'):
            raise ValueError('true-error decision requires a true unit')
        if verdict=='confirmed_acceptable' and (not u or u['kind']!='acceptable'):
            raise ValueError('acceptable decision requires a negative unit')
        if verdict=='false_positive' and u and u['kind']!='acceptable':
            raise ValueError('FP cannot map to true unit')
        if verdict=='false_positive' and credit(d['correction_credit'],d['correction_supplied']):
            raise ValueError('FP correction cannot earn credit')
        if uid is not None:
            if uid in assigned: raise ValueError('unresolved duplicate or contradictory unit decisions')
            assigned[uid]=d
    if unresolved:
        return dict(status='review_required',counts=None,sufficient_statistics=None,
            metrics={i:dict(value=None,numerator=None,denominator=None,status='review_required',reason='unresolved') for i in METRIC_IDS},
            domain_results=[],composite=dict(value_0_100=None,exact_value_0_100=None,enabled_components=[k for k,v in comps.items() if v],reason='unresolved'))
    true=[u for u in units if u['kind']=='true_error']; negatives=[u for u in units if u['kind']=='acceptable']
    tps=[d for d in normalized if d['verdict']=='matched_error']
    fps=[d for d in normalized if d['verdict']=='false_positive']
    tpids={d['unit_id'] for d in tps}
    G=len(true); D=len(negatives); TP=len(tps); FP=len(fps); FN=G-TP
    labeled=[d for d in tps if d['category_id'] is not None]
    LC=len(labeled)
    LF=sum(reporting_domain(d['category_id'])==byid[d['unit_id']]['domain'] for d in labeled)
    LE=sum(d['category_id'] in byid[d['unit_id']]['accepted_taxonomy_ids'] for d in labeled)
    H=sum((max(hierarchical(d['category_id'],x) for x in byid[d['unit_id']]['accepted_taxonomy_ids']) for d in labeled),Fraction(0))
    def repair(kind: str):
        eligible=kind+'_eligible'; supplied=kind+'_supplied'; field=kind+'_credit'
        g=sum(u[eligible] for u in true)
        td=[d for d in tps if byid[d['unit_id']][eligible]]
        attempts=[d for d in td if d[supplied]]
        vals=[credit(d[field],True) for d in attempts]
        return g,len(td),len(attempts),sum(v==1 for v in vals),sum(vals,Fraction(0))
    GC,TC,CA,CK,CQ=repair('correction');GE,TE,EA,EK,EQ=repair('explanation')
    FC=sum(d['correction_supplied'] for d in fps)
    DF=sum(d['unit_id'] is not None for d in fps)
    DA=sum(d['verdict']=='confirmed_acceptable' for d in normalized)
    SN=sum(d['unit_id'] is not None and d['verdict'] in ('matched_error','false_positive','confirmed_acceptable','wrong_acceptance') for d in normalized)
    SA=TP+DA
    WTP=sum(u['weight'] for u in true if u['id'] in tpids)
    WFN=sum(u['weight'] for u in true if u['id'] not in tpids)
    values=[(TP,TP+FP,'no_assertions'),(TP,G),(2*TP,2*TP+FP+FN),(FN,G),(FP,TP+FP,'no_assertions'),
        (LC,TP),(LF,LC,'no_assertions'),(LE,LC,'no_assertions'),(H,LC,'no_assertions'),(H,G),
        (CA,TC),(CK,CA,'no_assertions'),(CQ,CA,'no_assertions'),(CK,GC),(CQ,GC),(CK,CA+FC,'no_assertions'),
        (EA,TE),(EK,EA,'no_assertions'),(EQ,EA,'no_assertions'),(EQ,GE),
        (DF,D),(D-DF,D),(DA,DA+DF,'no_assertions'),(SA,SN,'no_assertions'),
        (WTP,WTP+FP,'no_assertions'),(WTP,WTP+WFN),(2*WTP,2*WTP+FP+WFN)]
    metrics={i:metric(*v) for i,v in zip(METRIC_IDS,values,strict=True)}
    domain_results=[]
    for domain in ((*DOMAINS,'unattributed_fp') if _include_domains else ()):
        ug=[u for u in true if u['domain']==domain]
        dt=sum(u['id'] in tpids for u in ug)
        df=sum((byid[d['unit_id']]['domain'] if d['unit_id'] else reporting_domain(d['category_id']) or 'unattributed_fp')==domain for d in fps)
        dn=len(ug)-dt
        subunits=[u for u in units if u['domain']==domain]
        subids={u['id'] for u in subunits}
        subdecisions=[d for d in normalized if d['unit_id'] in subids or (d['unit_id'] is None and d['verdict']=='false_positive' and (reporting_domain(d['category_id']) or 'unattributed_fp')==domain)]
        sub=calculate(dict(units=subunits,decisions=subdecisions,components=comps),_include_domains=False)
        domain_results.append(dict(domain=domain,true_errors=len(ug),tp=dt,fn=dn,fp=df,
            precision=metric(dt,dt+df,'no_assertions'),recall=metric(dt,len(ug)),f1=metric(2*dt,2*dt+df+dn),metrics=sub['metrics']))
    component_map={'detection':('detection.f1',45),'classification':('classification.hierarchical_recall',15),
                   'correction':('correction.graded_recall',30),'explanation':('explanation.graded_recall',10)}
    weighted=Fraction(0);totalweight=0
    for name,(mid,w) in component_map.items():
        m=metrics[mid]
        if comps[name] and {'detection':G,'classification':G,'correction':GC,'explanation':GE}[name] > 0 and m['value'] is not None:
            weighted+=w*Fraction(int(m['numerator']),int(m['denominator']));totalweight+=w
    statistics={k:int(v) for k,v in dict(G=G,D=D,TP=TP,FP=FP,FN=FN,LC=LC,LF=LF,LE=LE,GC=GC,TC=TC,CA=CA,CK=CK,GE=GE,TE=TE,EA=EA,EK=EK,FC=FC,DF=DF,DA=DA,SN=SN,SA=SA,WTP=WTP,WFN=WFN,WFP=FP).items()}
    statistics.update({k:dict(numerator=str(v.numerator),denominator=str(v.denominator)) for k,v in dict(H=H,CQ=CQ,EQ=EQ).items()})
    result=dict(status='complete',sufficient_statistics=statistics,counts=dict(true_errors=G,tp=TP,fn=FN,fp=FP,designated_decoys=D,
        decoy_false_positives=DF,duplicate_claims=duplicates,unresolved_claims=0),metrics=metrics,domain_results=domain_results,
        composite=dict(value_0_100=float(100*weighted/totalweight) if totalweight else None,
                       exact_value_0_100=({'numerator':str((100*weighted/totalweight).numerator),'denominator':str((100*weighted/totalweight).denominator)} if totalweight else None),
                       enabled_components=[k for k,v in comps.items() if v],reason=None if totalweight else 'no_opportunities'))
    assert result['counts']['tp']+result['counts']['fn']==G
    for k in (('tp','fn','fp') if _include_domains else ()):
        assert sum(d[k] for d in domain_results)==result['counts'][k]
    return result


def exact_display(numerator: str, denominator: str, *, percentage: bool) -> str:
    """Return one decimal place with half-up rounding. Do not calculate from a float."""
    if len(numerator.lstrip('-'))>4096 or len(denominator)>4096:
        raise ValueError('numeric capacity exceeded')
    n, d = int(numerator), int(denominator)
    if d <= 0: raise ValueError('nonpositive denominator')
    scale = 1000 if percentage else 10
    q, r = divmod(abs(n)*scale, d)
    q += int(2*r >= d)
    sign = '-' if n < 0 and q else ''
    return f"{sign}{q//10}.{q%10}"


def build_score_result(payload: dict[str,Any], *, attempt_id: str, case_version_id: str,
                       decision_set_sha256: str, scoring_policy_version: str) -> dict[str,Any]:
    """Add real caller-supplied identities to the reference numeric result.

    The caller must validate actual semantic evidence and schema first.
    This function does not issue a review approval or provider receipt.
    """
    import re
    if not re.fullmatch(r'[a-f0-9]{64}',decision_set_sha256):
        raise ValueError('invalid decision set digest')
    result=calculate(payload)
    result.update(schema_version='2.0.0',attempt_id=attempt_id,case_version_id=case_version_id,
                  decision_set_sha256=decision_set_sha256,scoring_policy_version=scoring_policy_version,
                  item_decision_ids=[d['id'] for d in payload['decisions']],semantic_judgments_present=True)
    return result
