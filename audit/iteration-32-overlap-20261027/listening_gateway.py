"""Read-only UI transport: real unchanged Next frontend + retained native media.

Attempt/results envelopes are explicitly constructed presentation fixtures. The
score arithmetic, key intervals and WAV bytes come from the native I32 cohort.
No model, synthesis, grading, user workspace or provider configuration can pass.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import hashlib, http.client, json, threading, time, os
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/iteration-32-overlap-20261027'
LOCK=threading.Lock(); STAMP=None; CONTROL={}
WEB_PORT=int(os.environ.get('TANGERINE_I32_WEB_PORT','53039'))
SCENES={'11111111-1111-4111-8111-111111111132':'obstructive',
        '22222222-2222-4222-8222-222222222232':'cooperative_backchannel'}
def read(p):return json.loads(p.read_text())
def envelope(id,kind):
    d=OUT/'selected'/kind; key=read(d/'key.json');score=read(d/'score.json')
    score['attempt_id']=id
    for item in score['items']:
        u=next(u for u in key['units'] if u['id']==item['unit_id'])
        item['reference']={'target_texts':[s['span']['exact_text'] for s in u['text_spans']],
                           'repairs':[],'rationale':u['rationale'], 'audio_intervals':u['audio_intervals']}
    name='Obstructive interruption' if kind=='obstructive' else 'Invited cooperative backchannel'
    answer='B interrupts the warning. B should wait until A finishes.' if kind=='obstructive' else 'The invited quiet acknowledgment is acceptable.'
    attempt={'id':id,'revision':1,'state':'complete','submitted_at':'2026-10-27T00:00:00Z',
        'answer_text':answer,'requested_language':'en','results_path':f'/api/v1/attempts/{id}/results',
        'audio_path':f'/api/v1/attempts/{id}/audio',
        'task_components':{'detection':True,'classification':False,'correction':False},
        'case':{'title':name+' · development fixture', 'duration_ms':key['audio']['duration_ms'],
                'public_context':'Controlled saved-attempt display using actual I32 local recordings and native key/score. No new model execution.'}}
    result={'attempt_id':id,'status':'complete','checking_stage':'complete','score':score,
        'feedback_status':'complete','feedback':{'items':[{'kind':'recommendation','status':'final',
        'text':'Constructed UI feedback: distinguish an obstructive interruption from an invited quiet backchannel.'}]},
        'auxiliary':{'measurements':{}},'interpretation':None,'issues':[]}
    return key,attempt,result
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):self.forward()
    def do_POST(self):self.forward()
    def do_PUT(self):self.forward()
    def forward(self):
        global CONTROL,STAMP
        path=self.path.split('?')[0];body=self.rfile.read(int(self.headers.get('Content-Length',0)))
        with LOCK:
            p=OUT/'listening-control.json'
            if p.exists() and p.stat().st_mtime_ns!=STAMP:STAMP=p.stat().st_mtime_ns;CONTROL=read(p)
            left=CONTROL.get('failures',{}).get(self.command+' '+path,0)
            if left>0:CONTROL['failures'][self.command+' '+path]=left-1
        status=200;headers={'Content-Type':'application/json'};raw=None
        bits=path.strip('/').split('/');id=bits[3] if len(bits)>3 and bits[:3]==['api','v1','attempts'] else None
        if left:status=503;raw=b'{"error":"PRIVATE_NATIVE_CANARY: synthetic transport unavailable"}'
        elif self.command=='POST' and id in SCENES and path.endswith('/playback'):
            status=201;raw=b'{"accepted":true,"origin":"constructed-ui-playback-ack"}'
        elif self.command!='GET':status=403;raw=b'{"error":"test_owned_write_dispatch_disabled"}'
        elif id in SCENES:
            key,attempt,result=envelope(id,SCENES[id]);headers.update({'ETag':'"1"','X-Tangerine-Audio-SHA256':key['audio']['sha256']})
            if len(bits)==4:raw=json.dumps(attempt).encode()
            elif bits[-1]=='results':raw=json.dumps(result).encode()
            elif bits[-1]=='audio':
                raw=(OUT/'selected'/SCENES[id]/'mixed.wav').read_bytes();headers['Content-Type']='audio/wav'
                wanted=self.headers.get('Range')
                if wanted and wanted.startswith('bytes='):
                    pair=wanted[6:].split('-',1);a=int(pair[0]);b=int(pair[1]) if pair[1] else len(raw)-1
                    if a>=len(raw):status=416;raw=b''
                    else:
                        b=min(b,len(raw)-1);headers['Content-Range']=f'bytes {a}-{b}/{len(raw)}';raw=raw[a:b+1];status=206
                headers['Accept-Ranges']='bytes'
            else:status=404;raw=b'{}'
        elif path=='/api/v1/preparations':
            base=read(OUT/'selected/obstructive/preparation.json');items=[]
            for i,(code,retryable,label) in enumerate([('PROVIDER_OUTPUT_INVALID',False,'Overlapping voices need different settings'),('CAPABILITY_UNQUALIFIED',False,'Word timing needs a compatible voice'),('INFRASTRUCTURE_UNAVAILABLE',True,'Temporary speech interruption')],1):
                row={k:base[k] for k in ['id','created_at','revision','canonical_word_count','surface_word_count','exercise_request','render_progress_summary']}
                row['id']=f'33333333-3333-4333-8333-{i:012d}';row['exercise_request']={**row['exercise_request'],'topic':label};row['phase_states']={'canonical_text':'complete','mutation':'complete','render':'failed'}
                row.update(audio_available=False,next_render_attempt=2,last_failure={'code':code,'retryable':retryable,'message':'PRIVATE_NATIVE_CANARY: never display this backend text'})
                items.append(row)
            raw=json.dumps({'items':items,'next_cursor':None}).encode()
        elif path=='/api/v1/preparation-options':
            upstream=http.client.HTTPConnection('127.0.0.1',53039,timeout=30);upstream.request('GET',self.path);response=upstream.getresponse();status=response.status;raw=response.read();headers=dict(response.getheaders());upstream.close()
        elif path.startswith('/api/'):status=404;raw=b'{"origin":"test-owned-read-only-fixture"}' 
        else:
            upstream=http.client.HTTPConnection('127.0.0.1',WEB_PORT,timeout=30)
            upstream.request('GET',self.path,headers={'Host':'localhost:3000','Accept-Encoding':'identity'})
            response=upstream.getresponse();status=response.status;raw=response.read();headers=dict(response.getheaders());upstream.close()
        self.send_response(status)
        for k,v in headers.items():
            if k.lower() not in ['connection','transfer-encoding','content-length','content-encoding']:self.send_header(k,v)
        self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(raw)));self.end_headers()
        try:self.wfile.write(raw)
        except BrokenPipeError:pass
        if path.startswith('/api/'):
            event={'at':time.time(),'method':self.command,'path':self.path,'status':status,
                   'origin':'constructed-presentation-actual-native-media','body':json.loads(body) if body else None}
            if id in SCENES and path.endswith('/audio'):event['served_sha256']=hashlib.sha256(raw).hexdigest()
            with LOCK:
                with (OUT/'listening-requests.jsonl').open('a') as f:f.write(json.dumps(event)+'\n')
if __name__=='__main__':
    server=ThreadingHTTPServer(('127.0.0.1',int(os.environ.get('TANGERINE_I32_GATEWAY_PORT','0'))),Handler)
    (OUT/'listening-gateway.json').write_text(json.dumps({'url':f'http://127.0.0.1:{server.server_port}',
        'upstream':f'http://127.0.0.1:{WEB_PORT}','proof_boundary':'Constructed UI envelopes, retained actual native WAV/key/score; no model or application write'})+'\n')
    server.serve_forever()
