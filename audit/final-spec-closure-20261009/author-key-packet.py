"""Construct complete declarative example; no model or application execution."""
import json,copy
from pathlib import Path
A=Path(__file__).resolve().parent;V=A.parents[1]/'specification/v2'
category='grammar.verbs.subject_verb_agreement'
def unit(uid,wrong,right,start,reason):
 prefix='new:' if uid.startswith('new:') else ''
 option=prefix+'o'+uid.split(':')[-1][-1];prop=prefix+'p'+uid.split(':')[-1][-1];rprop=prefix+'r'+uid.split(':')[-1][-1]
 return dict(id=uid,primary_taxonomy_id=category,accepted_taxonomy_ids=[category],secondary_taxonomy_ids=[],domain='grammar',expected_judgment='true_error',status_label='unequivocal_error',utterance_ids=['t1'],text_spans=[dict(utterance_id='t1',span=dict(start_cp=start,end_cp=start+len(wrong),exact_text=wrong))],realization=dict(mode='textual',canonical_text=right,surface_text=wrong,canonical_ipa=None,intended_ipa=None,observed_ipa=None,prosody=[],pace_target_wpm=None,observed_pace_wpm=None,planned_pause_ms=None,observed_pause_ms=None),severity='moderate',weight=2,difficulty='unrated',correction_eligible=True,corrections=[dict(id=option,kind='replace',text=right,ipa=None,approved_text_alternatives=[],case_insensitive=False,terminal_period_insensitive=True,variety_constraints=['standard contemporary English'],required_propositions=[dict(id=prop,description='Replace '+wrong+' with '+right+' while retaining the present meaning and subject.')],forbidden_propositions=[],canonical=True)],explanation_eligible=True,rationale_required_propositions=[dict(id=rprop,description=reason)],rationale_forbidden_propositions=[],rationale=reason)
surface='She work here. They is ready.'
proposal=dict(base_case_sha256='a'*64,audio_sha256='b'*64,affected_components=['key','detection','classification','correction','explanation'],proposed_units=[unit('u1','work','works',4,'The singular third-person subject she requires works in this present context.'),unit('new:u2','is','are',20,'The plural subject they requires are in this present context.')],correspondence_relations=[dict(old_unit_ids=['u1'],new_unit_ids=['u1'],kind='same',reason='Same first agreement event.'),dict(old_unit_ids=[],new_unit_ids=['new:u2'],kind='added',reason='Second agreement error was omitted from the old key.')],reason='Both independently repairable audible agreement errors must be represented; the recording is unchanged.')
for u in proposal['proposed_units']:
 span=u['text_spans'][0]['span'];assert surface[span['start_cp']:span['end_cp']]==span['exact_text']
packet=dict(origin='constructed_specification_fixture',canonical='She works here. They are ready.',surface=surface,answer='work -> works; is -> are',base_unit_ids=['u1'],proposal=proposal,expected=dict(G=2,GC=2,TP=2,CQ='2/1',primary='100/1',audio_sha256='b'*64,old_result_readable=True),negative=dict(changed_audio_sha256='c'*64,missing_repair_units=['u1']),negative_expected=dict(new_key_committed=False,old_result_readable=True))
(A/'KEY-REPAIR-PACKET.json').write_text(json.dumps(packet,indent=2)+'\n')
