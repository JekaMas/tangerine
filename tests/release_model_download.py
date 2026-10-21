"""Explicit pinned public-model acquisition; independent files in parallel.

Uses the production downloader/admission/manifest format, existing host Python
and an owned ignored cache. No inference, host installation or credentials.
"""
import concurrent.futures,json,os,pathlib,sys,threading
R=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'services/speech'))
import model_setup as models
profile='qwen25-omni-3b-audio-v1';models.ROOT=R/'data/iteration16/models';repo,revision=models.MODELS[profile];root=models.ROOT/profile
manifest_path=root/'manifest.json';manifest=json.loads(manifest_path.read_text());accepted={r['path']:r for r in manifest['files']}
metadata=models.fetch(f'https://huggingface.co/api/models/{repo}/revision/{revision}?blobs=true');lock=threading.Lock()
def acquire(row):
 name=row['rfilename']
 if name in accepted:return
 value=models.download(f'https://huggingface.co/{repo}/resolve/{revision}/{name}',root/name,row['lfs']['sha256']);value['path']=name
 with lock:
  accepted[name]=value;manifest['files']=list(accepted.values());temporary=root/'manifest-parallel.tmp';temporary.write_text(json.dumps(manifest,indent=2));os.replace(temporary,manifest_path)
 print(json.dumps({'accepted':name,'bytes':value['size'],'sha256':value['sha256']}),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(acquire,[r for r in metadata['siblings'] if r['rfilename'].endswith('.safetensors')]))
print(json.dumps(models.setup(profile)),flush=True)
