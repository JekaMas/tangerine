"""Inspect original saved observations once. No dispatch, synthesis or grading.

The old context is never replaced under an old model reply. Fixture repairs are
future inputs, explicitly unobserved. Acoustic measurements and conversational
correctness remain separate; this report cannot rewrite a learner's key/score.
"""
import array
import importlib.util
import json
from pathlib import Path
import sys
import wave

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'data/iteration-33-diagnostics-20261027'
SAVED = ROOT / 'data/iteration-26-acoustic-20261026/selected'
CONNECTED = ROOT / 'data/connected-speech-20261023/output'
sys.path.insert(0, str(ROOT / 'services/speech'))


def read(path):
    return json.loads(Path(path).read_text())


def load_observer():
    path = ROOT / 'audit/iteration-26-acoustic-20261026/observe.py'
    spec = importlib.util.spec_from_file_location('i33_selected_observer', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pcm(path):
    # This is a finite development measurement of selected original recordings,
    # not a qualification on playback or another accepted-value runtime gate.
    with wave.open(str(path)) as audio:
        values = array.array('h', audio.readframes(audio.getnframes()))
    if sys.byteorder != 'little':
        values.byteswap()
    return values


def pause_observation(reference, candidate, start, inserted):
    before, after = pcm(reference), pcm(candidate)
    return dict(additional_samples=len(after)-len(before), sample_rate_hz=24000,
                inserted_interval=dict(start=start, end=start+inserted),
                inserted_samples=inserted,
                all_inserted_samples_zero=all(x == 0 for x in after[start:start+inserted]),
                prefix_outside_120_sample_fade_unchanged=before[:start-120] == after[:start-120],
                suffix_outside_120_sample_fade_unchanged=before[start+120:] == after[start+inserted+120:],
                location_basis='Saved decoder proposed the word boundary; exact PCM establishes silence, not pragmatic correctness.')


def build():
    observer = load_observer()
    recordings = {r['id']:r for r in read(CONNECTED/'recordings.json')}
    physical = read(CONNECTED/'physical-reconciliation.json')
    linking = ROOT/'data/category-realization-20261025/observations-gemini31/pronunciation.suprasegmental.linking_resyllabification'
    plans = [
        ('linking', 'linking', linking, 'scoped_model_confirmation',
         'The selected joining contrast is supported by the saved model check. Careful unlinked speech remains permitted; exact phone identity is not independently established.'),
        ('assimilation', 'blend_dj', SAVED/'assimilation', 'scoped_model_confirmation',
         'The saved model supports this explicit voiced-joining drill, including its careful control. It does not establish a universal error rule for natural assimilation or accents.'),
        ('weak-form', 'weak_form', SAVED/'weak-form', 'unresolved_context',
         'The original model describes the full vowel and accepts it. A full form is not proof of an error in this neutral carrier; matching a narrow reduction drill and communicative correctness differ.'),
        ('thought-group', 'chunking', SAVED/'thought-group', 'physical_change_model_miss',
         'An actual 14400-sample / 600 ms silence was inserted. The model misses that boundary. Preserve the physical observation and the contrary reply; perceived disruption is unresolved.'),
        ('intonation-function', 'statement', SAVED/'intonation-function', 'measured_contour_model_disagreement',
         'Retained F0 windows fall in the reference and rise in the candidate. The model reports a fall and flags one valid confirmation-question control. Pitch direction alone does not establish conversational error.'),
    ]
    rows = []
    for name, source_id, directory, disposition, conclusion in plans:
        frozen = read(directory/'frozen.json') if name != 'linking' else None
        probe = frozen['probe'] if frozen else read(directory/'withheld.json')
        response_path = directory/'readmitted-response.json'
        if not response_path.exists():
            response_path = directory/'response.json'
        response = read(response_path)
        comparison = read(directory/'comparison.json')
        context = {c['unit_id']:c for c in probe['clips']}
        clips = []
        for clip in probe['withheld']:
            findings = [f for f in response.get('output',{}).get('findings',[])
                        if f.get('unit_id') == clip['unit_id'] and f.get('feature') == 'category_probe']
            clips.append({**clip, 'public_context':context[clip['unit_id']]['public_context'],
                          'question':context[clip['unit_id']]['question'],
                          'original_findings':findings})
        original_input = frozen['packet']['input'] if frozen else response['wire']['request']['input'][0]['text']
        if isinstance(original_input, str):
            original_input = json.loads(original_input)
        row = dict(id=name, disposition=disposition, conclusion=conclusion,
                   recording_text=recordings[source_id]['requested']['text'],
                   binding=probe['binding'], clips=clips,
                   original_input=original_input,
                   original_comparison=comparison,
                   original_response=str(response_path.relative_to(ROOT)),
                   historical_status_scope='Original model comparison on its original authored context; not a physical absence or perceptual-gold claim.')
        if frozen:
            fresh = observer.prepare(name)
            row['fixture_repair'] = dict(
                input=fresh['packet']['input'],
                withheld_expectations=[{k:c[k] for k in ['unit_id','role','expected']} for c in fresh['probe']['withheld']],
                note=fresh['probe'].get('expectation_note',fresh['repair']),
                observation='not_run' if fresh['packet']['input'] != original_input else 'unchanged_input_retained_observation',
                new_model_calls=0)
        if name == 'thought-group':
            step = recordings['chunking']['resolved_steps'][0]
            row['physical_observation'] = pause_observation(
                CONNECTED/'chunking-reference.wav', CONNECTED/'chunking-candidate.wav',
                step['source_interval']['start'], step['parameters']['pause_ms']*24)
        if name == 'intonation-function':
            row['physical_observation'] = dict(
                origin='Retained independent native F0 measurements, not new inference or a new measurement.',
                source='data/connected-speech-20261023/output/physical-reconciliation.json',
                contours=[c for c in physical['checks'] if c['case_id'] in ['statement','question','wh_question']],
                correctness='unresolved; neither a rise nor a fall is universally wrong for a question or statement')
        rows.append(row)
    return dict(scope='QUAL-04: five selected saved sets and their three correct controls each',
                original_sets=5, original_clips=20, actual_new_model_calls=0,
                actual_new_synthesis_calls=0, score_or_key_changes=0, sets=rows,
                unresolved=[dict(id=r['id'],reason=r['conclusion']) for r in rows
                            if r['disposition'] != 'scoped_model_confirmation'])


def main():
    OUT.mkdir(exist_ok=True)
    result = build()
    (OUT/'reconciliation.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'sets'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
