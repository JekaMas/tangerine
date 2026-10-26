"""Literal selected-probe tests; substituted judgments are not hearing evidence."""
import copy
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
path = ROOT/'audit/iteration-26-acoustic-20261026/observe.py'
spec = importlib.util.spec_from_file_location('selected_acoustic_observer', path)
observer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(observer)
path=ROOT/'audit/iteration-26-acoustic-20261026/listening.py'
spec=importlib.util.spec_from_file_location('selected_acoustic_listening',path)
listening=importlib.util.module_from_spec(spec);spec.loader.exec_module(listening)


def judged(frozen):
    # Independent role oracle; no candidate-generated answer or actual hearing.
    return dict(receipt=dict(inference_calls=1), output=dict(findings=[
        dict(unit_id=c['unit_id'], feature='category_probe',
             status='supported' if c['role']=='mutated' else 'contradicted',
             reason='Constructed native comparison expectation, not a listening observation.')
        for c in frozen['probe']['withheld']]))


class SelectedAcoustic(unittest.TestCase):
    def test_correct_control_projection_positive(self):
        for case in ['weak-form', 'intonation-function']:
            frozen = observer.prepare(case)
            by_role = {c['role']:c for c in frozen['probe']['withheld']}
            self.assertEqual(by_role['mutated']['audio_path'], by_role['acceptable']['audio_path'])
            self.assertEqual(by_role['clean']['audio_path'], by_role['misleading_metadata']['audio_path'])
            contexts = {c['unit_id']:c['public_context'] for c in frozen['packet']['input']['clips']}
            self.assertNotEqual(contexts[by_role['mutated']['unit_id']], contexts[by_role['acceptable']['unit_id']])
            self.assertEqual(('supported','contradicted'), (by_role['mutated']['expected'],by_role['acceptable']['expected']))

    def test_blind_public_context_negative(self):
        for case in ['assimilation','weak-form','thought-group','intonation-function']:
            frozen = observer.prepare(case)
            visible = json.dumps(frozen['packet']['input'],ensure_ascii=False)
            for private in ['expected','claimed_mutation','audio_path','taxonomy_id','/dʒ/','/tə/']:
                self.assertNotIn(private,visible)
            self.assertNotIn(frozen['probe']['category_id'],visible)
            self.assertEqual({'clip-1','clip-2','clip-3','clip-4'}, {c['unit_id'] for c in frozen['packet']['input']['clips']})

    def test_boundary_context_repair_positive(self):
        frozen = observer.prepare('thought-group')
        self.assertIn('between the and policy', frozen['packet']['input']['clips'][0]['public_context'])
        self.assertNotIn('word policy must remain uninterrupted',json.dumps(frozen['packet']['input']))
        self.assertEqual(14400, frozen['physical']['observations'][0]['actual']['additional_samples'])

    def test_selected_save_and_read_positive(self):
        frozen = observer.prepare('weak-form')
        calls=[]
        with tempfile.TemporaryDirectory() as tmp, patch.object(observer,'prepare',return_value=frozen):
            result=observer.observe_case('weak-form',Path(tmp),lambda p:calls.append(copy.deepcopy(p)) or judged(frozen))
            self.assertEqual('confirmed',result['audio_confirmation'])
            again=observer.observe_case('weak-form',Path(tmp),lambda p:self.fail('A read dispatched'))
            self.assertEqual(result,again)
            self.assertEqual([frozen['packet']],calls)

    def test_response_finalizer_recovery_positive(self):
        frozen=observer.prepare('thought-group')
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)/'thought-group'
            observer.save(directory/'frozen.json',frozen)
            observer.save(directory/'response.json',judged(frozen))
            result=observer.observe_case('thought-group',Path(tmp),lambda p:self.fail('Saved response dispatched'))
            self.assertEqual('confirmed',result['audio_confirmation'])
            self.assertEqual(frozen['physical'],result['physical'])

    def test_interrupted_request_negative(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)/'weak-form'
            observer.save(directory/'frozen.json',observer.prepare('weak-form'))
            result=observer.observe_case('weak-form',Path(tmp),lambda p:self.fail('Interrupted request redispatched'))
            self.assertEqual(('not_run','INTERRUPTED_OBSERVATION'),(result['audio_confirmation'],result['error']))
            self.assertFalse((directory/'comparison.json').exists())

    def test_free_failure_preserved_negative(self):
        frozen=observer.prepare('weak-form')
        failure=dict(error='DIAGNOSTIC_PROVIDER_FAILED',receipt=dict(inference_calls=1),wire=dict(http_status=503))
        calls=[]
        with tempfile.TemporaryDirectory() as tmp, patch.object(observer,'prepare',return_value=frozen):
            result=observer.observe_case('weak-form',Path(tmp),lambda p:calls.append(1) or failure)
            self.assertEqual(('uncertain','failed'),(result['audio_confirmation'],result['dispatch_status']))
            self.assertEqual(failure,json.loads((Path(tmp)/'weak-form/response.json').read_text()))
            observer.observe_case('weak-form',Path(tmp),lambda p:self.fail('Failure read retried'))
            self.assertEqual([1],calls)

    def test_correct_variant_false_alarm_negative(self):
        frozen=observer.prepare('weak-form');reply=judged(frozen)
        unit=next(c['unit_id'] for c in frozen['probe']['withheld'] if c['role']=='acceptable')
        next(c for c in reply['output']['findings'] if c['unit_id']==unit)['status']='supported'
        with tempfile.TemporaryDirectory() as tmp, patch.object(observer,'prepare',return_value=frozen):
            result=observer.observe_case('weak-form',Path(tmp),lambda p:reply)
            self.assertEqual(('uncertain',1,False),(result['audio_confirmation'],result['false_alarms'],result['controls_passed']))

    def test_native_http_failure_retention_negative(self):
        failure=dict(error='DIAGNOSTIC_PROVIDER_FAILED',wire=dict(http_status=503),receipt=dict(inference_calls=1))
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                self.rfile.read(int(self.headers['Content-Length']))
                body=json.dumps(failure).encode();self.send_response(422)
                self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
            def log_message(self,*args): pass
        http=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=http.serve_forever,daemon=True);thread.start()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                journal=Path(tmp)/'dispatch.json'
                native=observer.NativeDiagnostic('http://127.0.0.1:'+str(http.server_port),'private-canary',journal)
                self.assertEqual(failure,native(dict(timeout_seconds=260)))
                facts=json.loads(journal.read_text())
                self.assertEqual(('failed',422),(facts['outcome'],facts['http_status']))
                self.assertNotIn('private-canary',json.dumps(facts))
        finally:
            http.shutdown();http.server_close();thread.join()

    def test_remote_endpoint_rejected_negative(self):
        with self.assertRaisesRegex(ValueError,'LOCAL_ENDPOINT_REQUIRED'):
            observer.NativeDiagnostic('https://example.com','fixture',Path('unused'))


class SelectedListening(unittest.TestCase):
    def test_gallery_contexts_and_playback_positive(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows=listening.materialize(Path(tmp))
            page=listening.page(rows)
            self.assertEqual(['linking','assimilation','weak-form','thought-group','intonation-function'],[r['id'] for r in rows])
            self.assertEqual(20,page.count('<audio '))
            self.assertNotIn('autoplay',page)
            self.assertIn('contrastively emphasizes',page)
            self.assertIn('between the and policy',page)
            self.assertIn('declarative word order',page.lower())
            self.assertNotIn('word policy must remain uninterrupted',page)

    def test_pending_error_and_read_failure_nonblocking_negative(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows=listening.materialize(Path(tmp))
            observer.save(Path(rows[1]['comparison']),dict(audio_confirmation='uncertain',error='PRIVATE_CANARY'))
            Path(rows[2]['comparison']).parent.mkdir(parents=True,exist_ok=True)
            Path(rows[2]['comparison']).write_text('{unfinished')
            page=listening.page(rows)
            self.assertEqual(20,page.count('<audio '))
            self.assertIn('Listening confirmation was unavailable',page)
            self.assertIn('Listening observation not performed',page)
            self.assertNotIn('PRIVATE_CANARY',page)
            self.assertNotIn('JSONDecodeError',page)
            self.assertIn('id="refresh" type="button"',page)
            self.assertNotIn('disabled',page)

    def test_read_and_refresh_do_not_infer_positive(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows=listening.materialize(Path(tmp))
            with patch.object(listening.observer,'observe_case',side_effect=AssertionError('Read inferred')):
                self.assertEqual(listening.page(rows),listening.page(rows))

    def test_media_relation_and_private_route_negative(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows=listening.materialize(Path(tmp))
            listener=ThreadingHTTPServer(('127.0.0.1',0),listening.handler(rows,Path(tmp)))
            thread=threading.Thread(target=listener.serve_forever,daemon=True);thread.start()
            connection=http.client.HTTPConnection('127.0.0.1',listener.server_port)
            try:
                connection.request('GET','/audio/weak-form/acceptable.wav')
                response=connection.getresponse();self.assertEqual(200,response.status)
                expected=next(c for c in rows[2]['probe']['withheld'] if c['role']=='mutated')['audio_path']
                self.assertEqual((ROOT/expected).read_bytes(),response.read())
                for path in ['/native-private.env','/selected/weak-form/frozen.json','/../native-private.env']:
                    connection.request('GET',path);response=connection.getresponse();self.assertEqual(404,response.status);response.read()
            finally:
                connection.close();listener.shutdown();listener.server_close();thread.join()


if __name__ == '__main__': unittest.main(verbosity=2)
