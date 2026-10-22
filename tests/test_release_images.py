"""Controlled Docker boundary; literal rollback expectations, no live-image claim."""
from pathlib import Path
import json,tempfile,types,unittest
from release_images import PlatformImage
class DockerBoundary:
 def __init__(self,failure=None):
  self.active={'Id':'sha256:original-arm','Architecture':'arm64'};self.backup=None;self.failure=failure;self.pulls=[]
 def __call__(self,args,check=True):
  if args[1:3]==['image','inspect']:return types.SimpleNamespace(returncode=0 if self.active else 1,stdout=json.dumps([self.active]).encode())
  if args[1:3]==['image','tag']:self.backup=dict(self.active)
  elif args[1:3]==['image','rm']:
   if args[-1]=='retained:original':self.backup=None
   elif self.failure=='remove':raise RuntimeError('reference in use')
   else:self.active=None
  elif args[1]=='pull':
   arch=args[3].split('/')[1];self.pulls.append(arch)
   if arch=='amd64' and self.failure=='pull':raise RuntimeError('registry unavailable')
   self.active={'Id':'sha256:original-arm' if arch=='arm64' else 'sha256:actual-amd','Architecture':arch}
  return types.SimpleNamespace(returncode=0,stdout=b'')
class ReleaseImageTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'restoration.json'
 def tearDown(self):self.tmp.cleanup()
 def image(self,driver):return PlatformImage(driver,'postgres@sha256:original-index','retained:original',self.path)
 def test_switch_restore_positive(self):
  d=DockerBoundary();image=self.image(d);image.select('amd64');self.assertEqual(d.active['Architecture'],'amd64');self.assertEqual(d.backup,{'Id':'sha256:original-arm','Architecture':'arm64'})
  image.restore();self.assertEqual(d.active,{'Id':'sha256:original-arm','Architecture':'arm64'});self.assertIsNone(d.backup);self.assertEqual(d.pulls,['amd64','arm64']);self.assertEqual(json.loads(self.path.read_text())['status'],'restored')
 def test_matching_cache_positive(self):
  d=DockerBoundary();image=self.image(d);image.select('arm64');image.restore();self.assertEqual(d.pulls,[]);self.assertIsNone(d.backup);self.assertEqual(json.loads(self.path.read_text())['status'],'unchanged')
 def test_failed_pull_negative(self):
  d=DockerBoundary('pull');image=self.image(d)
  with self.assertRaisesRegex(RuntimeError,'registry unavailable'):
   try:image.select('amd64')
   finally:image.restore()
  self.assertEqual(d.active,{'Id':'sha256:original-arm','Architecture':'arm64'});self.assertIsNone(d.backup);self.assertEqual(d.pulls,['amd64','arm64'])
 def test_remove_failure_negative(self):
  d=DockerBoundary('remove');image=self.image(d)
  with self.assertRaisesRegex(RuntimeError,'reference in use'):
   try:image.select('amd64')
   finally:image.restore()
  self.assertEqual(d.active,{'Id':'sha256:original-arm','Architecture':'arm64'});self.assertEqual(d.pulls,[]);self.assertIsNone(d.backup)
if __name__=='__main__':unittest.main()
