"""Focused instruction/closure checks, not application or linguistic acceptance."""
import json
import subprocess
import sys
from pathlib import Path
root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / '.agents/workflow/scripts'))
from integration import render_config
checks = []
def check(name, ok):
    checks.append({'name': name, 'passed': bool(ok)})
    assert ok, name
report = (root / 'audit/decision-closure-20261009/REPORT.md').read_text()
tasks = (root / 'openspec/changes/implement-teacher-error-trainer/tasks.md').read_text()
guide = (root / 'docs/development/REVIEW_AND_VALIDATION.md').read_text()
config = (root / 'openspec/config.yaml').read_text()
profile = json.loads((root / '.agents/workflow-project.json').read_text())
check('Pinned renderer equals current config', config == render_config(profile))
check('Settled approval context is active', 'approved by the actual user' in config and 'separate unapproved decisions' not in config)
check('Definition portion complete', '- [x] 13.6 Reconcile' in tasks)
check('Native acquisition portion remains incomplete', '- [ ] 13.6a Obtain actual complete' in tasks)
check('Future implementation remains incomplete', '- [ ] 13.7 Future implementation only after separate authorization' in tasks)
check('Three stale instructions are recorded', 'three remaining planning contradictions' in report)
check('Seven dependency rows retained', all(x in report for x in ['| Cambridge EFCAMDAT','| Doubao |','| Moodrick and NIR |','| Official L2-ARCTIC','| Supplementary media/access |','| Empirical mappings/benchmark/populations |','| Provider/application observations |']))
check('No outstanding product decision reported', 'zero outstanding product decisions' in report)
def follows_local_authority(text):
    return ('no human peer review' in text and 'Clearly labelled constructed fixtures are permitted' in text
            and 'Ordinary generated-exercise use does not require full-corpus acquisition' in text
            and 'No tenant/user account authorization' in text
            and 'Release requires' not in text)
check('Positive local verification authority', follows_local_authority(guide))
check('Negative human review gate rejected', not follows_local_authority(guide.replace('no human peer review', 'mandatory human peer review')))
check('Negative artificial-fixture ban rejected', not follows_local_authority(guide.replace('Clearly labelled constructed fixtures are permitted', 'Constructed fixtures are forbidden')))
check('Negative corpus certification gate rejected', not follows_local_authority(guide + '\nRelease requires full corpus certification.'))
check('Protected active contracts and graphs unchanged', subprocess.run(['git','diff','--quiet','d18920f','--','specification/v2','openspec/changes/implement-teacher-error-trainer/verification.json','openspec/changes/implement-teacher-error-trainer/discovery.json'],cwd=root).returncode == 0)
check('Historical user edit remains unstaged', subprocess.run(['git','diff','--cached','--quiet','--','audit/spec-fullness-20261008/GAPS.md'],cwd=root).returncode == 0)
result = {'baseline': 'd18920f', 'status': 'passed', 'focused_checks': checks,
          'retained_evidence': 'audit/flow-fullness-20261009/validation-results.json: 366 static checks; unchanged contracts/graphs, no rerun',
          'proof_boundary': 'Document/instruction reconciliation, constructed negative instruction variants and unchanged protected scopes; no application/provider/empirical behavior',
          'rerun_reason': {'openspec': 'tasks and rendered config changed', 'routes': 'stale rendered approval context regenerated', 'focused_checks': 'new closure and revised local verification guidance'}}
(root / 'audit/decision-closure-20261009/validation-results.json').write_text(json.dumps(result, indent=2) + '\n')
print(f'{len(checks)} focused checks passed')
