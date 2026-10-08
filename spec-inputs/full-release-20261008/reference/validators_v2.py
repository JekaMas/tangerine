"""Reference checks for supplied real records.

This module does not create observations, approvals, teacher answers, or provider results.
Call full JSON Schema validation first. These checks add explicit semantic boundaries.
They do not prove linguistic correctness or the identity of a human reviewer.
"""
from __future__ import annotations
import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any
from .validators import check_span, validate_mapping_ids

AUDIO_TYPES = frozenset({'render','audio_qc','asr','alignment','phoneme_score','observed_phone','prosody','human_review'})


def frozen_answer_hash(text: str) -> str:
    """Hash the exact UTF-8 answer. Invalid Unicode is an error."""
    return hashlib.sha256(text.encode('utf-8', errors='strict')).hexdigest()


def validate_extraction_v2(text: str, output: Mapping[str, Any]) -> dict[str, str]:
    """Check real source ranges and return local-to-persistent claim identifiers."""
    digest = frozen_answer_hash(text)
    clauses = output['clauses']
    local: dict[str, Mapping[str, Any]] = {}
    identities: dict[str, str] = {}
    ordered = sorted(clauses, key=lambda c:(c['claim_span']['start_cp'],c['claim_span']['end_cp']))
    for c in ordered:
        if c['local_ref'] in local:
            raise ValueError('duplicate extraction-local claim')
        for key in ('claim_span','target_span','category_span','correction_span','rationale_span','explicit_retraction_of_span'):
            if c[key] is not None:
                check_span(text,c[key])
        span = c['claim_span']
        if span['end_cp'] <= span['start_cp']:
            raise ValueError('empty claim')
        material = [digest,span['start_cp'],span['end_cp'],span['exact_text']]
        raw = json.dumps(material,ensure_ascii=False,separators=(',',':')).encode('utf-8')
        identity = 'clm_'+hashlib.sha256(raw).hexdigest()[:32]
        if identity in identities.values():
            raise ValueError('duplicate or conflicting interpretation of one span')
        identities[c['local_ref']] = identity
        local[c['local_ref']] = c
    for span in output['unparsed_spans']:
        check_span(text,span)
    cursor=0
    for cell in output['coverage']:
        start,end=cell['span']['start'],cell['span']['end']
        if start!=cursor or not start<end<=len(text):
            raise ValueError('coverage is not an ordered disjoint partition')
        refs=set(cell['claim_refs'])
        if not refs<=local.keys():
            raise ValueError('unknown coverage claim')
        if cell['kind']=='whitespace':
            if refs or not text[start:end].isspace():
                raise ValueError('non-whitespace assigned to whitespace')
        elif cell['kind'] in ('claim','attachment'):
            if not refs: raise ValueError('source coverage has no claim')
            for ref in refs:
                c=local[ref]
                candidates=([c['claim_span']] if cell['kind']=='claim' else [c[k] for k in ('target_span','category_span','correction_span','rationale_span','explicit_retraction_of_span') if c[k] is not None])
                if not any(v['start_cp']<=start and end<=v['end_cp'] for v in candidates):
                    raise ValueError('coverage does not belong to its source span')
        elif cell['kind']=='unparsed':
            if not any(v['start_cp']<=start and end<=v['end_cp'] for v in output['unparsed_spans']):
                raise ValueError('unparsed coverage lacks its preserved span')
        elif cell['kind']=='non_assertive':
            if not cell['reason']:raise ValueError('unexplained non-assertive coverage')
        else:
            raise ValueError('unknown coverage kind')
        cursor=end
    if cursor!=len(text):raise ValueError('omitted source text')
    for rel in output['relations']:
        a,b=rel['from_claim_ref'],rel['to_claim_ref']
        if a not in local or b not in local or a==b:raise ValueError('invalid relation')
        if local[a]['claim_span']['start_cp']<=local[b]['claim_span']['start_cp']:
            raise ValueError('relation is not backwards')
        s,e=rel['evidence_span']['start'],rel['evidence_span']['end']
        if not 0<=s<e<=len(text):raise ValueError('invalid relation evidence')
        if rel['kind']=='retracts' and s<local[b]['claim_span']['end_cp']:
            raise ValueError('retraction precedes original assertion')
    return identities


def validate_evidence_scope(
    records: Sequence[Mapping[str,Any]], *, case_version_id: str,
    audio_sha256: str, known_subject_ids: set[str],
) -> dict[str,Mapping[str,Any]]:
    """Reject wrong-case, wrong-audio, unknown-subject, and cyclic evidence."""
    byid={e['id']:e for e in records}
    if len(byid)!=len(records):raise ValueError('duplicate evidence')
    for e in records:
        if e['case_version_id']!=case_version_id:raise ValueError('wrong-case evidence')
        if not set(e['subject_ids'])<=known_subject_ids:raise ValueError('unknown evidence subject')
        if e['type'] in AUDIO_TYPES and e['subject_audio_sha256']!=audio_sha256:
            raise ValueError('evidence is not bound to final delivery bytes')
        if e['type']=='observed_phone' and e['epistemic_status'] not in ('measured','human_observed'):
            raise ValueError('intended or inferred phone is not an observation')
        if not set(e['parent_evidence_ids'])<=byid.keys():raise ValueError('unknown evidence parent')
    active:set[str]=set();done:set[str]=set()
    def visit(i: str) -> None:
        if i in active:raise ValueError('evidence cycle')
        if i in done:return
        active.add(i)
        for parent in byid[i]['parent_evidence_ids']:visit(parent)
        active.remove(i);done.add(i)
    for i in byid:visit(i)
    return byid


def validate_mapping_v2(
    output: Mapping[str,Any], claims: Mapping[str,Mapping[str,Any]],
    key: Mapping[str,Any], evidence: Sequence[Mapping[str,Any]],
    taxonomy_ids: set[str], known_subject_ids: set[str],
) -> None:
    """Add exact scope and source-supplied component checks to inherited ID checks."""
    units={u['id']:u for u in key['units']}
    ev=validate_evidence_scope(evidence,case_version_id=key['case_version_id'],
        audio_sha256=key['audio']['sha256'],known_subject_ids=known_subject_ids)
    validate_mapping_ids(output,set(claims),units,set(ev),taxonomy_ids)
    for d in output['decisions']:
        c=claims[d['claim_id']];u=units.get(d['unit_id'])
        all_evidence=set(d['evidence_ids'])
        for part,span_key in [('correction','correction_span'),('explanation','rationale_span')]:
            j=d[part]
            if j['supplied'] != (c[span_key] is not None):
                raise ValueError('supplied component contradicts frozen source')
            if not j['supplied'] and (j['option_id'] is not None or j['satisfied_proposition_ids'] or j['violated_proposition_ids'] or j['status']!='not_supplied' or j['unresolved_reason'] is not None):
                raise ValueError('credit-bearing fields without source text')
            if (j['status']=='unresolved') != (j['unresolved_reason'] is not None):
                raise ValueError('inconsistent unresolved state')
            if j['status']=='unresolved' and d['decision']!='unresolved':
                raise ValueError('unresolved component in resolved decision')
            if len(set(j['satisfied_proposition_ids']))!=len(j['satisfied_proposition_ids']) or len(set(j['violated_proposition_ids']))!=len(j['violated_proposition_ids']):
                raise ValueError('duplicate proposition')
            if j['violated_proposition_ids'] and j['status'] not in ('rejected','unresolved'):
                raise ValueError('forbidden proposition without rejection')
            all_evidence.update(j['support_evidence_ids'])
        if d['category_id'] is not None and c['category_span'] is None:
            raise ValueError('model added a teacher category')
        if u:
            allowed_subjects={key['case_version_id'],u['id'],*u['utterance_ids']}
            for eid in all_evidence:
                subjects=set(ev[eid]['subject_ids'])
                if not subjects & allowed_subjects:
                    raise ValueError('evidence belongs to another unit')
                if ev[eid]['type'] in ('observed_phone','prosody','mutation','alignment') and u['id'] not in subjects:
                    raise ValueError('unit-level evidence lacks the exact unit subject')
            if d['decision'] in ('matched_error','confirmed_acceptable','wrong_acceptance') and not any(u['id'] in ev[eid]['subject_ids'] for eid in d['evidence_ids']):
                raise ValueError('no direct evidence for the target unit')
            if d['decision'] in ('matched_error','wrong_acceptance') and u['expected_judgment']!='true_error':
                raise ValueError('true error decision references a control')
            if d['decision']=='confirmed_acceptable' and u['expected_judgment']!='acceptable':
                raise ValueError('acceptance decision references an error')
            if d['decision']=='false_positive' and u['expected_judgment']!='acceptable':
                raise ValueError('false positive references an actual error')


def rubric_fraction(required: set[str], satisfied: set[str], forbidden: set[str], violated: set[str], *, supplied: bool) -> tuple[int,int]:
    """Derive exact credit from fixed propositions, not a model fraction."""
    from fractions import Fraction
    if not satisfied<=required or not violated<=forbidden:raise ValueError('out-of-scope proposition')
    if not supplied:
        if satisfied or violated:raise ValueError('findings without a supplied answer')
        return 0,1
    if not required:raise ValueError('missing rubric requirements')
    q=Fraction(0) if violated else Fraction(len(satisfied),len(required))
    return q.numerator,q.denominator
