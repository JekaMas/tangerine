"""Actual voice-summary owner, independently authored ordered expectations."""
import json
import subprocess
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NODE=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
class PreparationSummary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        script="""
        import {summaryVoices} from './services/web/app/prepare/summaryVoices.js';
        const voices=[{id:'bf_emma',accent_label:'British English',label:'Emma'},{id:'melo_en_au',accent_label:'Australian English',label:'Australian voice'}];
        const simple={exercise_request:{speaker_voice_ids:['bf_emma','melo_en_au']}};
        console.log(JSON.stringify({simple:summaryVoices(simple,voices),advanced:summaryVoices({...simple,speakers:[{voice_profile_id:'melo_en_au',requested_accent:'Australian English'},{voice_profile_id:'bf_emma'}]},voices),automatic:summaryVoices({exercise_request:{}},voices),partial:summaryVoices({exercise_request:{speaker_voice_ids:[null,'private-configured-profile']}},voices)}));
        """
        r=subprocess.run([str(NODE),'--input-type=module','-e',script],cwd=ROOT,capture_output=True,text=True,timeout=15)
        if r.returncode:raise AssertionError(r.stderr)
        cls.v=json.loads(r.stdout)
    def test_simple_order_positive(self):
        self.assertEqual(['Speaker 1: British English · Emma','Speaker 2: Australian English · Australian voice'],self.v['simple'])
    def test_advanced_precedence_positive(self):
        self.assertEqual(['Speaker 1: Australian English · Australian voice · Requested accent: Australian English','Speaker 2: British English · Emma'],self.v['advanced'])
    def test_no_invented_default_negative(self):
        self.assertEqual([],self.v['automatic'])
    def test_partial_and_custom_negative(self):
        self.assertEqual(['Speaker 1: Configured default','Speaker 2: private-configured-profile'],self.v['partial'])
if __name__=='__main__':unittest.main(verbosity=2)
