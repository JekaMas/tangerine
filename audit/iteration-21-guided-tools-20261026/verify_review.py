"""Review the actual current evidence relation; this is not a product gate."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PREFIX = 'data/iteration-21-verify-20261026/'


def review_errors(packet, facts, fixture):
    errors = []
    for name in ['ui_ux', 'typography', 'evidence']:
        part = packet.get(name, {})
        if not part.get('observations') or PREFIX + 'observations.json' not in part.get('references', []):
            errors.append(name + ' unsupported')
        for ref in part.get('references', []):
            if not (ROOT / ref).is_file():
                errors.append('missing ' + ref)
    for row in facts['layouts']:
        if row['overflow'] or row['bodySize'] != '17px' or row['bodyLine'] != '24.65px' or not row['loaded']:
            errors.append('readability')
        if any(float(size.removesuffix('px')) < 13 for size in row['help']):
            errors.append('helper readability')
    if len(facts['layouts']) != 6:
        errors.append('layout scope')
    if fixture['first_attempt'] == fixture['second_attempt'] or packet.get('deleted_attempt') != fixture['first_attempt']:
        errors.append('native identity')
    if facts['cases']['nativePreview']['inputs']['Deletion subjects']['value'] != fixture['first_attempt']:
        errors.append('preview identity')
    if packet.get('reference_origin') != 'independently authored literal expectations':
        errors.append('reference origin')
    if packet.get('unexecuted_cases') != []:
        errors.append('unexecuted')
    if packet.get('new_model_calls') != 0 or packet.get('new_synthesis_calls') != 0:
        errors.append('provider scope')
    if packet.get('performance_campaigns') != 'excluded':
        errors.append('performance scope')
    return errors
