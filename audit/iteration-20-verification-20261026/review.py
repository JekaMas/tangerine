"""Check review relations; this does not perform visual or independent review."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PREFIX = 'data/iteration-20-verification-20261026/'


def review_errors(packet, facts):
    errors = []
    for dimension in ['ui_ux', 'typography', 'evidence']:
        part = packet.get(dimension, {})
        if not part.get('observations') or PREFIX + 'observations.json' not in part.get('references', []):
            errors.append(dimension + ' unsupported')
        for reference in part.get('references', []):
            if not (ROOT / reference).is_file():
                errors.append('missing ' + reference)
    for row in facts['cases']['layouts']:
        if row['overflow'] or row['bodySize'] != '17px' or row['bodyLine'] != '24.65px' or not row['sourceSans'] or row['fonts'] != 'loaded':
            errors.append('readability')
    if facts['cases']['manualAfterOld']['score'] != 'Primary score: 60.0 / 100':
        errors.append('result ownership')
    if packet.get('reference_origin') != 'independently authored literal expectations':
        errors.append('reference origin')
    if packet.get('unexecuted_cases') != []:
        errors.append('unexecuted selected cases')
    if packet.get('new_model_calls') != 0 or packet.get('new_synthesis_calls') != 0:
        errors.append('provider scope')
    if packet.get('performance_campaigns') != 'excluded':
        errors.append('performance scope')
    return errors
