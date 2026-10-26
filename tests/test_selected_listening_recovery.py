"""Actual saved-media CLI/HTTP recovery; no synthesis or auditory inference."""
import contextlib
import copy
import http.client
import importlib.util
import json
import os
from pathlib import Path
import selectors
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'audit/iteration-26-acoustic-20261026/listening.py'
spec=importlib.util.spec_from_file_location('selected_listening_recovery_owner',SOURCE)
listening=importlib.util.module_from_spec(spec);spec.loader.exec_module(listening)


def saved_rows():
    return json.loads((ROOT/'data/iteration-26-acoustic-20261026/gallery.json').read_text())


@contextlib.contextmanager
def application(gallery):
    with tempfile.TemporaryDirectory() as temporary:
        output=Path(temporary);(output/'gallery.json').write_text(gallery)
        with (output/'server.log').open('w') as errors:
            env={key:os.environ[key] for key in ['PATH','LANG','TMPDIR'] if key in os.environ}
            process=subprocess.Popen([sys.executable,'-B',str(SOURCE),'--out',str(output),'--port','0'],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=errors,text=True)
            connection=None
            try:
                with selectors.DefaultSelector() as ready:
                    ready.register(process.stdout,selectors.EVENT_READ)
                    if not ready.select(10):raise AssertionError('The test-owned reader did not start.')
                    line=process.stdout.readline().strip()
                if 'http://127.0.0.1:' not in line:raise AssertionError('The saved-media CLI did not report its loopback listener.')
                port=int(line.rsplit(':',1)[1].strip('/'))
                connection=http.client.HTTPConnection('127.0.0.1',port,timeout=5)
                yield connection,output
            finally:
                if connection:connection.close()
                process.terminate()
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:process.kill();process.wait(timeout=5)
                process.stdout.close()


def get(connection,path='/'):
    connection.request('GET',path);response=connection.getresponse()
    return response.status,response.read()


class SelectedListeningRecovery(unittest.TestCase):
    def test_initial_read_failure_recovers_on_refresh_positive(self):
        with application('{private_backend_canary') as (client,output):
            status,body=get(client);text=body.decode()
            self.assertEqual(200,status)
            self.assertEqual(0,text.count('<audio '))
            self.assertIn('id="refresh" type="button"',text)
            self.assertNotIn('disabled',text)
            self.assertNotIn('JSONDecodeError',text)
            self.assertNotIn('private_backend_canary',text)
            status,font=get(client,'/font.ttf')
            self.assertEqual(200,status)
            self.assertEqual((ROOT/'services/web/public/fonts/SourceSans3.ttf').read_bytes(),font)
            self.assertEqual(2,(output/'server.log').read_text().count('Saved comparison read failed:'))
            (output/'gallery.json').write_text(json.dumps(saved_rows()))
            status,body=get(client)
            self.assertEqual(200,status)
            self.assertEqual(20,body.decode().count('<audio '))
            self.assertEqual(2,(output/'server.log').read_text().count('Saved comparison read failed:'))
            status,body=get(client,'/audio/weak-form/acceptable.wav')
            self.assertEqual(200,status)
            row=next(r for r in saved_rows() if r['id']=='weak-form')
            audio=next(c['audio_path'] for c in row['probe']['withheld'] if c['role']=='acceptable')
            self.assertEqual((ROOT/audio).read_bytes(),body)

    def test_admitted_selection_reused_without_revalidation_positive(self):
        with application(json.dumps(saved_rows())) as (client,output):
            self.assertEqual(20,get(client)[1].decode().count('<audio '))
            (output/'gallery.json').write_text('{later_unreadable')
            self.assertEqual(20,get(client)[1].decode().count('<audio '))
            self.assertNotIn('Saved comparison read failed:',(output/'server.log').read_text())

    def test_unreadable_judgment_keeps_audio_and_guidance_negative(self):
        with tempfile.TemporaryDirectory() as temporary:
            rows=copy.deepcopy(saved_rows());path=Path(temporary)/'comparison.json'
            path.write_text('{private_backend_canary');rows[0]['comparison']=str(path)
            page=listening.page(rows)
            self.assertEqual(20,page.count('<audio '))
            self.assertIn('Saved listening observation unavailable',page)
            self.assertIn('Refresh saved observations to try again',page)
            self.assertIn('Confirmed in this model check',page)
            self.assertNotIn('private_backend_canary',page)
            self.assertNotIn('JSONDecodeError',page)
            self.assertNotIn('disabled',page)

    def test_media_failure_keeps_other_recordings_usable_negative(self):
        rows=copy.deepcopy(saved_rows())
        with tempfile.TemporaryDirectory() as temporary:
            next(c for c in rows[0]['probe']['withheld'] if c['role']=='clean')['audio_path']=str(Path(temporary)/'missing.wav')
            with application(json.dumps(rows)) as (client,output):
                status,body=get(client,'/audio/linking/clean.wav')
                self.assertEqual(503,status)
                self.assertIn(b'Refresh saved observations to try again',body)
                self.assertNotIn(b'FileNotFoundError',body)
                self.assertNotIn(temporary.encode(),body)
                status,body=get(client,'/audio/weak-form/acceptable.wav')
                self.assertEqual(200,status)
                self.assertTrue(body.startswith(b'RIFF'))
                status,body=get(client)
                self.assertEqual(200,status)
                self.assertEqual(20,body.decode().count('<audio '))
                self.assertEqual(2,(output/'server.log').read_text().count('Saved comparison read failed:'))


if __name__=='__main__':unittest.main(verbosity=2)
