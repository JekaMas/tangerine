"""Real foreground IPC/lifetimes; constructed model replies do not prove audio."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'services/speech'))
from kokoro_worker import KokoroWorker

MODEL_BOUNDARY = '''
import json,os,sys,time
count=0
for raw in sys.stdin.buffer:
    p=json.loads(raw);count+=1
    if p.get('ready'):open(p['ready'],'w').close()
    if p.get('exit'):sys.exit(7)
    if p.get('wait'):
        while not os.path.exists(p['wait']):time.sleep(.01)
    if p.get('sleep'):time.sleep(p['sleep'])
    result={'error':'VOICE_UNAVAILABLE'} if p.get('bad_voice') else {'pid':os.getpid(),'ordinal':count,'text':p['text']}
    print(json.dumps(result),flush=True)
'''


class KokoroWorkerTests(unittest.TestCase):
    def setUp(self):
        self.worker = KokoroWorker([sys.executable, '-u', '-c', MODEL_BOUNDARY])

    def tearDown(self):
        self.worker.close()

    def call(self, packet, timeout=3, disconnected=lambda: False):
        return self.worker.execute(packet, timeout, disconnected)

    def test_reuse_and_context_positive(self):
        first = self.call({'text': 'First speaker: café.'})
        second = self.call({'text': 'Second speaker: two quotes.'})
        self.assertEqual(first, {'pid': first['pid'], 'ordinal': 1, 'text': 'First speaker: café.'})
        self.assertEqual(second, {'pid': first['pid'], 'ordinal': 2, 'text': 'Second speaker: two quotes.'})
        self.assertIsNone(self.worker.process.poll())

    def test_deadline_negative(self):
        with self.assertRaises(subprocess.TimeoutExpired):
            self.call({'text': 'Slow result must not arrive.', 'sleep': 5}, timeout=.2)
        self.assertIsNone(self.worker.process)
        self.assertEqual(self.call({'text': 'Recovered.'})['ordinal'], 1)

    def test_disconnect_and_recovery_negative(self):
        with tempfile.TemporaryDirectory() as folder:
            ready = Path(folder) / 'ready'
            observed = []
            def disconnected():
                if ready.exists():
                    observed.append(self.worker.process.pid)
                    return True
                return False
            with self.assertRaises(ConnectionAbortedError):
                self.call({'text': 'Cancelled.', 'ready': str(ready), 'sleep': 5}, disconnected=disconnected)
            with self.assertRaises(ProcessLookupError):
                os.kill(observed[0], 0)
            recovered = self.call({'text': 'Fresh context.'})
            self.assertEqual(recovered['ordinal'], 1)
            self.assertNotEqual(recovered['pid'], observed[0])

    def test_waiter_cannot_cancel_owner_negative(self):
        with tempfile.TemporaryDirectory() as folder:
            ready, release = Path(folder) / 'ready', Path(folder) / 'release'
            results = []
            owner = threading.Thread(target=lambda: results.append(self.call({'text': 'Owner.', 'ready': str(ready), 'wait': str(release)})))
            owner.start()
            try:
                deadline = time.monotonic() + 2
                while not ready.exists() and time.monotonic() < deadline:
                    time.sleep(.01)
                self.assertTrue(ready.exists())
                pid = self.worker.process.pid
                with self.assertRaises(subprocess.TimeoutExpired):
                    self.call({'text': 'Expired waiter.'}, timeout=.1)
                self.assertEqual(self.worker.process.pid, pid)
                self.assertIsNone(self.worker.process.poll())
            finally:
                release.touch()
                owner.join(timeout=4)
            self.assertFalse(owner.is_alive())
            self.assertEqual(results, [{'pid': pid, 'ordinal': 1, 'text': 'Owner.'}])
            self.assertEqual(self.call({'text': 'Next.'}), {'pid': pid, 'ordinal': 2, 'text': 'Next.'})

    def test_reset_connection_negative(self):
        with tempfile.TemporaryDirectory() as folder:
            ready = Path(folder) / 'ready'
            observed = []
            def reset():
                if ready.exists():
                    observed.append(self.worker.process.pid)
                    raise ConnectionResetError()
                return False
            with self.assertRaises(ConnectionResetError):
                self.call({'text': 'Reset.', 'ready': str(ready), 'sleep': 5}, disconnected=reset)
            self.assertIsNone(self.worker.process)
            with self.assertRaises(ProcessLookupError):
                os.kill(observed[0], 0)
            self.assertEqual(self.call({'text': 'Recovered.'})['ordinal'], 1)

    def test_exited_worker_negative(self):
        self.assertEqual(self.call({'text': 'Failed.', 'exit': True}), {'error': 'SYNTHESIS_FAILED'})
        self.assertIsNone(self.worker.process)
        self.assertEqual(self.call({'text': 'Recovered.'})['ordinal'], 1)

    def test_native_error_preserved_positive(self):
        self.assertEqual(self.call({'text': 'Invalid voice.', 'bad_voice': True}), {'error': 'VOICE_UNAVAILABLE'})
        pid = self.worker.process.pid
        self.assertEqual(self.call({'text': 'Valid next request.'}), {'pid': pid, 'ordinal': 2, 'text': 'Valid next request.'})

    def test_idle_exit_recovery_positive(self):
        first = self.call({'text': 'Finished before exit.'})
        self.worker.process.kill()
        self.worker.process.wait(timeout=3)
        recovered = self.call({'text': 'Fresh successful caller.'})
        self.assertNotEqual(recovered['pid'], first['pid'])
        self.assertEqual(recovered, {'pid': recovered['pid'], 'ordinal': 1, 'text': 'Fresh successful caller.'})


if __name__ == '__main__':
    unittest.main()
