"""Real Chrome video/PNG transport and native ffprobe, no application-quality claim."""
from pathlib import Path
import base64,json,os,subprocess,tempfile,time,unittest,uuid
from unittest.mock import patch
from browser_probe import Browser
R=Path(__file__).resolve().parents[1]
IMAGE='sha256:906700d3eda940912899001feb08a3b1b0df3fa3d6c8f8a3ae6e0c5bb96256e9'
def probe(path):
 p=subprocess.run(['docker','run','--rm','--network','none','--user','0','-v',str(path.parent)+':/evidence:ro','--entrypoint','ffprobe',IMAGE,'-v','error','-show_streams','-show_format','-of','json','/evidence/'+path.name],capture_output=True,text=True,timeout=30)
 if p.returncode:raise RuntimeError('MEDIA_EVIDENCE_MISSING_OR_UNREADABLE')
 return json.loads(p.stdout)
class ReleaseMediaTests(unittest.TestCase):
 def setUp(self):
  self.root=R/'data/iteration16/media-transport'/('run-'+uuid.uuid4().hex[:10]);self.root.mkdir(parents=True)
 def test_video_and_picture_positive(self):
  with patch.dict(os.environ,TANGERINE_TEST_VIDEO_DIR=str(self.root/'video')):
   browser=Browser(self.root/'chrome','data:text/html,<h1>Native recording probe</h1><button>Observed action</button>')
   try:
    browser.wait('Native recording probe');browser.call('UI.click',{'selector':'button'});time.sleep(.2)
    browser.evaluate("document.querySelector('h1').textContent='Native action observed';true");time.sleep(.2)
    png=base64.b64decode(browser.call('Page.captureScreenshot')['data']);self.assertTrue(png.startswith(b'\x89PNG\r\n\x1a\n'));(self.root/'observed.png').write_bytes(png)
   finally:browser.close()
  self.assertEqual(len(browser.videos),1)
  video=Path(browser.videos[0]);self.assertTrue(video.is_file());result=probe(video)
  self.assertTrue(any(s['codec_type']=='video' for s in result['streams']));self.assertGreater(float(result['format']['duration']),0)
  (self.root/'receipt.json').write_text(json.dumps({'origin':'Real browser transport probe; not app acceptance','video':str(video.relative_to(R)),'picture':str((self.root/'observed.png').relative_to(R)),'ffprobe':result},indent=2))
 def test_video_destination_negative(self):
  bad=self.root/'not-directory';bad.write_text('preserved')
  with patch.dict(os.environ,TANGERINE_TEST_VIDEO_DIR=str(bad)):
   with self.assertRaises(RuntimeError):Browser(self.root/'chrome','data:text/html,<h1>must not claim video</h1>')
  self.assertEqual(bad.read_text(),'preserved');self.assertFalse(list(self.root.glob('*.webm')))
 def test_unobserved_video_negative(self):
  with self.assertRaisesRegex(RuntimeError,'MEDIA_EVIDENCE_MISSING_OR_UNREADABLE'):probe(self.root/'absent.webm')
if __name__=='__main__':unittest.main()
