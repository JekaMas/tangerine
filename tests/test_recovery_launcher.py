"""Constructed Docker CLI only: actual launcher/Lab workspace selection."""
from pathlib import Path
import json, os, shutil, subprocess, tempfile, unittest
R=Path(__file__).resolve().parents[1]
class RecoveryLauncherTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name).resolve()
  shutil.copytree(R/'scripts',self.root/'scripts');(self.root/'data/config/restores/restored').mkdir(parents=True)
  (self.root/'.env').write_text('');(self.root/'data/config/runtime.env').write_text('');(self.root/'data/config/restores/restored/runtime.env').write_text('')
  self.trace=self.root/'trace';bin=self.root/'bin';bin.mkdir()
  (bin/'docker').write_text('#!/usr/bin/env python3\nimport json,os,sys\nwith open(os.environ["CLI_TRACE"],"a") as f:f.write(json.dumps(sys.argv[1:])+"\\n")\nif sys.argv[1:]==["compose","version","--short"]:print("2.40.0")\nelse:print("{}")\n');(bin/'docker').chmod(0o700)
  self.env={k:v for k,v in os.environ.items() if k not in ('COMPOSE_PROJECT_NAME','TANGERINE_RUNTIME_FILE')};self.env.update(PATH=str(bin)+':'+os.environ['PATH'],CLI_TRACE=str(self.trace))
 def run_lab(self,entry,project=None):
  if project:self.env['COMPOSE_PROJECT_NAME']=project
  p=subprocess.run(['sh','scripts/'+entry,*(['lab','active'] if entry=='tangerine' else ['active'])],cwd=self.root,env=self.env,capture_output=True,text=True)
  self.assertEqual(p.returncode,0,p.stderr)
  return [json.loads(line) for line in self.trace.read_text().splitlines() if 'runtime.env' in line]
 def test_selected_lab_positive(self):
  (self.root/'data/config/active-project').write_text('restored\n')
  for entry in ['tangerine','lab']:
   with self.subTest(entry=entry):
    commands=self.run_lab(entry)
    self.assertTrue(commands)
    self.assertTrue(all(str(self.root/'data/config/restores/restored/runtime.env') in c for c in commands),commands)
 def test_explicit_lab_override_positive(self):
  (self.root/'data/config/active-project').write_text('restored\n')
  commands=self.run_lab('lab','original')
  self.assertTrue(all(str(self.root/'data/config/runtime.env') in c for c in commands),commands)
 def test_selected_lab_missing_runtime_negative(self):
  (self.root/'data/config/active-project').write_text('restored\n');(self.root/'data/config/restores/restored/runtime.env').unlink()
  p=subprocess.run(['sh','scripts/lab','active'],cwd=self.root,env=self.env,capture_output=True,text=True)
  self.assertNotEqual(p.returncode,0)
  self.assertFalse(self.trace.exists(),'must not use original credentials for selected missing workspace')
if __name__=='__main__':unittest.main()
