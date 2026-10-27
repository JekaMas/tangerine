"""Read-only actual listening UI with isolated saved-file/media failures.

The original twenty role-bound WAVs and original model replies are used. All
changed comparison files and failure switches belong to this test directory.
"""
import argparse
import copy
from http.server import ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
import threading
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('i33_actual_listening',
    ROOT/'audit/iteration-26-acoustic-20261026/listening.py')
listening=importlib.util.module_from_spec(spec);spec.loader.exec_module(listening)
NOTES={
    'linking':'This saved model check supports this narrow joining contrast. Careful word boundaries and the declared British accent remain valid.',
    'assimilation':'This saved drill concerns voiced joining. Natural assimilation and careful variants are not universally wrong.',
    'weak-form':'The model hears a full vowel and accepts it. Strong forms can be correct in neutral careful speech as well as contrastive emphasis. This carrier does not establish a mistake; the revised candidate expectation is uncertain and has not been judged again.',
    'thought-group':'The saved PCM contains 600 ms of added silence. The model does not confirm the pause. Word alignment and communicative disruption remain unresolved; the waveform and model observations stay separate.',
    'intonation-function':'The actual recording says “You have car insurance.” The original model context below omitted “car”. Saved pitch windows rise in the candidate, but the model reports a fall and flags a valid confirmation-question control. Correct questions may rise or fall in their stated contexts. The corrected context has not been judged again.',
}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--port',type=int,default=0);args=parser.parse_args()
    output=args.out.resolve();output.mkdir(parents=True,exist_ok=True)
    rows=copy.deepcopy(json.loads((ROOT/'data/iteration-26-acoustic-20261026/gallery.json').read_text()))
    for row in rows:
        raw=Path(row['comparison']).read_text()
        target=output/(row['id']+'-comparison.json');target.write_text(raw)
        (output/(row['id']+'-original.json')).write_text(raw)
        row.update(comparison=str(target),research_note=NOTES[row['id']])
    (output/'linking-comparison.json').write_text(json.dumps(dict(audio_confirmation='PRIVATE_BACKEND_CANARY')))
    (output/'gallery.json').write_text(json.dumps(rows,indent=2)+'\n')
    parent=listening.handler(listening.selection_reader(output),output)
    events=[];lock=threading.Lock();counts={}
    class Observed(parent):
        def do_GET(self):
            path=urlsplit(self.path).path
            with lock:
                counts[path]=counts.get(path,0)+1;number=counts[path]
            transient=path=='/audio/linking/clean.wav' and number==1
            persistent=path=='/audio/linking/mutated.wav' and not (output/'media-available').exists()
            if transient or persistent:
                self.respond(503,b'PRIVATE_BACKEND_CANARY: test-owned unavailable saved clip','text/plain; charset=utf-8')
            else:super().do_GET()

        def respond(self,status,body,kind):
            super().respond(status,body,kind)
            with lock:
                events.append(dict(path=urlsplit(self.path).path,status=status,bytes=len(body)))
                target=output/'http-observations.json';temporary=output/'http-observations.partial'
                temporary.write_text(json.dumps(events,indent=2)+'\n');temporary.replace(target)
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Observed)
    (output/'server.json').write_text(json.dumps(dict(port=server.server_port,
        origin='Actual saved-listening source; original Kokoro WAVs/model replies; controlled read and media failures.',
        actual_new_model_calls=0,actual_new_synthesis_calls=0),indent=2)+'\n')
    print('I33 saved listening fixture on http://127.0.0.1:'+str(server.server_port)+'/',flush=True)
    server.serve_forever()


if __name__=='__main__':main()
