"""Approved local MPS pair through the unchanged native foreground HTTP owner."""
import argparse,json,os,secrets,shlex,shutil,socket,subprocess,time,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/completion-leftovers-20261028'
PYTHON=OUT/'qwen-venv/bin/python'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--dtype',choices=['float16','float32'],default='float16');parser.add_argument('--codec-device',choices=['cpu']);args=parser.parse_args()
    binaries=OUT/'native-tools';binaries.mkdir(exist_ok=True)
    # Reuse the existing local FFmpeg build; only pipe bytes cross this bridge.
    # No model/server entrypoint, filesystem mount, network or user container edit.
    for name in ['ffmpeg','ffprobe']:
        path=binaries/name
        path.write_text('#!/bin/sh\nexec '+shlex.quote(shutil.which('docker'))+' run --pull=never --rm -i --network none --entrypoint '+name+' tangerine-local-speech:local "$@"\n');path.chmod(0o700)
    with socket.socket() as probe:probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
    env={**os.environ,'PATH':str(binaries)+os.pathsep+os.environ['PATH'],'TANGERINE_MODEL_DIR':str(OUT/'models'),'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','HF_DATASETS_OFFLINE':'1','TOKENIZERS_PARALLELISM':'false','PYTORCH_ENABLE_MPS_FALLBACK':'0','SPEECH_INTERNAL_TOKEN':secrets.token_hex(24)}
    candidate=OUT/(('qwen-mps' if args.dtype=='float16' else 'qwen-mps-float32')+('-cpu-codec' if args.codec_device else ''));candidate.mkdir(exist_ok=True)
    with (OUT/'qwen-native-server.log').open('a') as log:
        server=subprocess.Popen([str(PYTHON),'-B',str(ROOT/'audit/iteration-25-qwen-20261026/native_server.py'),'--port',str(port)],env=env,cwd=ROOT,stdout=log,stderr=log)
        (OUT/'qwen-server.json').write_text(json.dumps({'pid':server.pid,'port':port,'scope':'Owned local native MPS server; no user provider/configuration change.'},indent=2)+'\n')
        try:
            client=urllib.request.build_opener(urllib.request.ProxyHandler({}))
            for _ in range(100):
                try:
                    with client.open('http://127.0.0.1:'+str(port)+'/health/live',timeout=1) as response:
                        if response.status==200:break
                except OSError:time.sleep(.1)
            else:raise RuntimeError('Owned Qwen native server unavailable')
            step=0
            while not (candidate/'result.json').exists():
                step+=1
                command=[str(PYTHON),'-B',str(ROOT/'audit/iteration-25-qwen-20261026/compare.py'),'--out',str(candidate),'--endpoint','http://127.0.0.1:'+str(port),'--device','mps','--dtype',args.dtype,'--max-pieces','1']
                if args.codec_device:command+=['--codec-device',args.codec_device]
                stem='qwen-'+args.dtype+('-cpu-codec' if args.codec_device else '')+'-step-'+str(step)
                with (OUT/(stem+'.stdout')).open('w') as stdout,(OUT/(stem+'.stderr')).open('w') as stderr:
                    result=subprocess.run(command,env=env,cwd=ROOT,stdout=stdout,stderr=stderr,timeout=300)
                (OUT/(stem+'-exit-code')).write_text(str(result.returncode)+'\n')
                print(json.dumps({'step':step,'exit_code':result.returncode,'state':json.loads((candidate/'state.json').read_text()) if (candidate/'state.json').exists() else None}),flush=True)
                if result.returncode:return result.returncode
            return 0 if (candidate/'result.json').exists() else 1
        finally:
            server.terminate()
            try:server.wait(timeout=10)
            except subprocess.TimeoutExpired:server.kill();server.wait()

if __name__=='__main__':raise SystemExit(main())
