"""Architecture observer selection only; Docker output is an explicit boundary fixture."""
from pathlib import Path
import sys,unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from assert_runtime_architecture import inspect
class ReleaseArchitectureProbe(unittest.TestCase):
 def replies(self,args,**kwargs):
  if args[:3]==['docker','ps','-q']:return 'owned-container\n'
  return '"arm64"\n' if args[:3]==['docker','image','inspect'] else 'actual-image\n'
 def test_selected_project_positive(self):
  with patch('subprocess.check_output',side_effect=self.replies) as run:rows=inspect('tangerine-i16-disposable','arm64')
  self.assertEqual([r['service'] for r in rows],['postgres','minio','speech','api','web']);self.assertIn('label=com.docker.compose.project=tangerine-i16-disposable',run.call_args_list[0].args[0])
 def test_wrong_architecture_negative(self):
  with patch('subprocess.check_output',side_effect=self.replies),self.assertRaisesRegex(ValueError,'architecture mismatch'):inspect('tangerine-i16-disposable','amd64')
 def test_missing_service_negative(self):
  with patch('subprocess.check_output',return_value=''),self.assertRaisesRegex(ValueError,'one actual running'):inspect('tangerine-i16-disposable','arm64')
 def test_ambiguous_project_negative(self):
  with patch('subprocess.check_output',return_value='container-a\ncontainer-b\n'),self.assertRaisesRegex(ValueError,'one actual running'):inspect('tangerine-i16-disposable','arm64')
if __name__=='__main__':unittest.main()
