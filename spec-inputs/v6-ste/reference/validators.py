"""Apply the reference boundary checks. These checks do not replace application security middleware."""
from typing import Any

def check_span(text: str, span: dict[str,Any]) -> None:
    start,end=span['start_cp'],span['end_cp']
    if type(start) is not int or type(end) is not int or not 0<=start<=end<=len(text):
        raise ValueError('invalid codepoint range')
    if text[start:end]!=span['exact_text']:
        raise ValueError('fabricated or shifted source quote')

def validate_extraction(text: str, output: dict[str,Any]) -> None:
    for c in output['clauses']:
        for key in ('claim_span','target_span','category_span','correction_span','rationale_span','explicit_retraction_of_span'):
            if c[key] is not None: check_span(text,c[key])
    for s in output['unparsed_spans']:check_span(text,s)

def validate_mapping_ids(output: dict[str,Any], claim_ids: set[str], units: dict[str,dict[str,Any]], evidence_ids: set[str], taxonomy_ids: set[str]) -> None:
    seen=set()
    for d in output['decisions']:
        if d['claim_id'] not in claim_ids or d['claim_id'] in seen: raise ValueError('unknown or repeated claim')
        if d['duplicate_of_claim_id'] is not None and d['duplicate_of_claim_id'] not in seen: raise ValueError('invalid duplicate link')
        seen.add(d['claim_id'])
        u=units.get(d['unit_id'])
        if d['unit_id'] is not None and u is None: raise ValueError('unknown unit')
        if d['category_id'] is not None and d['category_id'] not in taxonomy_ids:raise ValueError('unknown taxonomy')
        if not set(d['evidence_ids'])<=evidence_ids:raise ValueError('unknown evidence')
        for k in ('correction','explanation'):
            j=d[k]
            if not set(j['support_evidence_ids'])<=evidence_ids:raise ValueError('unknown judgment evidence')
            if u is None and (j['option_id'] or j['satisfied_proposition_ids'] or j['violated_proposition_ids']):raise ValueError('unscoped propositions')
            if u is None:continue
            if k=='correction':
                options={o['id']:o for o in u['corrections']}
                if j['option_id'] is not None and j['option_id'] not in options:raise ValueError('unknown correction')
                o=options.get(j['option_id'])
                req={p['id'] for p in o['required_propositions']} if o else set()
                bad={p['id'] for p in o['forbidden_propositions']} if o else set()
            else:
                if j['option_id'] is not None:raise ValueError('rationale is not a correction option')
                req={p['id'] for p in u['rationale_required_propositions']};bad={p['id'] for p in u['rationale_forbidden_propositions']}
            if not set(j['satisfied_proposition_ids'])<=req or not set(j['violated_proposition_ids'])<=bad:
                raise ValueError('invented rubric proposition')

    if seen != claim_ids: raise ValueError("missing claim decisions")
