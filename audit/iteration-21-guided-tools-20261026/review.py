"""Evidence review only; no product admission or aesthetics gate."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PREFIX = 'data/iteration-21-guided-tools-20261026/'


def review_errors(packet, facts, native):
    errors = []
    for name in ['ui_ux', 'typography', 'evidence']:
        part = packet.get(name, {})
        if not part.get('observations') or PREFIX + 'observations.json' not in part.get('references', []):
            errors.append(name + ' unsupported')
        for ref in part.get('references', []):
            if not (ROOT / ref).is_file():
                errors.append('missing ' + ref)
    rows = facts['layouts']
    if {(x['route'], x['width']) for x in rows} != {(r, w) for r in ['reports', 'cleanup'] for w in [1280, 390, 320]}:
        errors.append('layout scope')
    for row in rows:
        if row['overflow'] or row['bodySize'] != '17px' or row['bodyLine'] != '24.65px' or not row['loaded'] or row['fonts'] != 'loaded':
            errors.append('readability')
        if any(float(x.removesuffix('px')) < 13 for x in row['fieldHelp']):
            errors.append('label readability')
    c = facts['cases']
    if c['cleanupFinalPreview']['inputs']['Deletion subjects']['value'] != native['first_attempt']:
        errors.append('attempt/preview identity')
    if native['first_attempt'] == native['second_attempt'] or packet.get('deleted_attempt') != native['first_attempt']:
        errors.append('distinct identity')
    if 'lexis.collocation\t1\t1/1\t1/2\t1/2\t125/1' not in c['constructedReport']['tables'][0]['rows']:
        errors.append('report arithmetic')
    if packet.get('reference_origin') != 'independently authored literal expectations':
        errors.append('reference origin')
    if packet.get('unexecuted_cases') != []:
        errors.append('unexecuted')
    if packet.get('new_model_calls') != 0 or packet.get('new_synthesis_calls') != 0:
        errors.append('provider scope')
    if packet.get('performance_campaigns') != 'excluded':
        errors.append('performance scope')
    return errors
