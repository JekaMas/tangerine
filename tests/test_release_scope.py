"""Finite release scope and honest unavailable-data claims; structural proof only."""
from pathlib import Path
import copy,hashlib,json,subprocess,unittest
R=Path(__file__).resolve().parents[1]
PRESERVED={'error-taxonomy.v1.yaml':'12a8923cb5edaf9346ed3241927e871b52a734e61edeb54d8b3d1987090a7c0a','mutation-recipes.v1.json':'f8a366db4091eb8476c3c7269f01463ae531b4ae115f39cf98dfd1fa7ff90aad','metrics.v1.yaml':'a42acaf740295277cfd602a9a9b706028a2b67912ecbe582e48543c77241c730','corpus-sources.v1.yaml':'0b7f6278de5a9c86035c06383b5a99e19b7b80f65953bcebd157bf39f9ba81fc','providers.v1.yaml':'411840e16b4afd77959728d5a4ad79628b92caa169a9affb07f5cab63cd7f5ea'}
def scope(recipes):
 ids=[r['taxonomy_id'] for r in recipes['recipes']]
 if len(ids)!=122 or len(set(ids))!=122:raise ValueError('INCOMPLETE_FINITE_SCOPE')
 return ids

class ReleaseScopeTests(unittest.TestCase):
 def test_original_scope_positive(self):
  for name,digest in PRESERVED.items():self.assertEqual(hashlib.sha256((R/'specification/v2/domain'/name).read_bytes()).hexdigest(),digest)
  self.assertEqual(len(scope(json.loads((R/'specification/v2/domain/mutation-recipes.v1.json').read_text()))),122)
 def test_category_removed_negative(self):
  x=json.loads((R/'specification/v2/domain/mutation-recipes.v1.json').read_text());x['recipes'].pop()
  with self.assertRaisesRegex(ValueError,'INCOMPLETE_FINITE_SCOPE'):scope(x)
 def test_category_duplicated_negative(self):
  x=json.loads((R/'specification/v2/domain/mutation-recipes.v1.json').read_text());x['recipes'][-1]=copy.deepcopy(x['recipes'][0])
  with self.assertRaisesRegex(ValueError,'INCOMPLETE_FINITE_SCOPE'):scope(x)
 def test_release_source_manifest_positive(self):
  for p in ['LICENSE','NOTICE','README.md','.env.example','scripts/tangerine','services/api/go.sum','services/web/package-lock.json','services/speech/requirements.arm64.lock','services/speech/requirements.amd64.lock','services/speech/requirements.diagnostics.arm64.lock','services/speech/requirements.diagnostics.amd64.lock','deploy/local/compose.yaml']:
   self.assertGreater((R/p).stat().st_size,0,p)
if __name__=='__main__':unittest.main()
