"""Explicit local model acquisition. Startup and inference never download assets."""
import hashlib, json, os, pathlib, sys, tempfile, urllib.request, zipfile

ROOT = pathlib.Path(os.environ.get('TANGERINE_MODEL_DIR', '/models'))
MODELS = {
 'kokoro-local-en-v1': ('hexgrad/Kokoro-82M', 'f3ff3571791e39611d31c381e3a41a3af07b4987'),
 'qwen-base-v1': ('Qwen/Qwen3-TTS-12Hz-0.6B-Base', '5d83992436eae1d760afd27aff78a71d676296fc'),
 'qwen-design-v1': ('Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign', '5ecdb67327fd37bb2e042aab12ff7391903235d3'),
 'qwen-custom-v1': ('Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice', '85e237c12c027371202489a0ec509ded67b5e4b5'),
 'faster-whisper-local-en-v1': ('Systran/faster-whisper-small', '536b0662742c02347bc0e980a01041f333bce120'),
 'qwen25-omni-audio-v1': ('Qwen/Qwen2.5-Omni-7B', 'ae9e1690543ffd5c0221dc27f79834d0294cba00'),
 'qwen25-omni-3b-audio-v1': ('Qwen/Qwen2.5-Omni-3B', 'f75b40e3da2003cdd6e1829b1f420ca70797c34e'),
}
VOICES = ('af_heart', 'am_adam', 'bf_emma', 'bm_george')

def fetch(url):
 with urllib.request.urlopen(url, timeout=60) as r:
  return json.load(r)

def download(url,dest,expected=None):
 dest.parent.mkdir(parents=True,exist_ok=True);partial=dest.with_name(dest.name+'.partial');offset=partial.stat().st_size if partial.exists() else 0
 request=urllib.request.Request(url,headers={'Range':f'bytes={offset}-'} if offset else {})
 with urllib.request.urlopen(request,timeout=300) as response:
  if offset and response.status!=206:offset=0
  if offset and not response.headers.get('Content-Range','').startswith(f'bytes {offset}-'):raise ValueError('MODEL_DOWNLOAD_INVALID')
  length=response.headers.get('Content-Length');expected_size=offset+int(length) if length else None
  sha=hashlib.sha256();size=offset
  # Partial network bytes have never been admitted. Hash their complete new
  # acquisition once; accepted model/manifest bytes are never re-audited.
  if offset:
   with partial.open('rb') as prior:
    while chunk:=prior.read(1024*1024):sha.update(chunk)
  with partial.open('ab' if offset else 'wb') as out:
   while chunk:=response.read(1024*1024):out.write(chunk);sha.update(chunk);size+=len(chunk)
 if expected_size is not None and size!=expected_size:raise ValueError('MODEL_DOWNLOAD_INCOMPLETE')
 if not size or (expected and sha.hexdigest()!=expected):partial.unlink(missing_ok=True);raise ValueError('MODEL_DOWNLOAD_INVALID')
 os.replace(partial,dest)
 return {'path':str(dest.name),'sha256':sha.hexdigest(),'size':size,'url':url}

def setup(profile):
 if profile == 'kokoro-controlled-v1': profile = 'kokoro-local-en-v1'
 repo, revision = MODELS[profile]; root = ROOT/profile; root.mkdir(parents=True, exist_ok=True)
 manifest_path = root/'manifest.json'
 previous = json.loads(manifest_path.read_text()) if manifest_path.exists() else {'files': []}
 if previous.get('complete') is True:return previous
 accepted = {r['path']:r for r in previous['files']}
 metadata = fetch(f'https://huggingface.co/api/models/{repo}/revision/{revision}?blobs=true')
 siblings = {r['rfilename']:r for r in metadata['siblings']}
 if profile.startswith('kokoro'):
  weights = [n for n in siblings if n.endswith('.pth') and '/' not in n]
  if len(weights) != 1: raise ValueError('MODEL_FORMAT_UNAVAILABLE')
  names = ['config.json', 'README.md', 'VOICES.md', *weights, *(f'voices/{v}.pt' for v in VOICES)]
 else:
  names = [n for n in siblings if (n.endswith(('.json','.txt','.safetensors','.md')) or n in ('LICENSE','LICENSE.txt') or profile=='faster-whisper-local-en-v1' and n=='model.bin') and not n.startswith('.')]
 files = []
 for name in names:
  dest = root/name
  if name in accepted and dest.is_file(): row = accepted[name]
  else:
   row = download(f'https://huggingface.co/{repo}/resolve/{revision}/{name}', dest, siblings[name].get('lfs',{}).get('sha256'))
   row['path'] = name
  files.append(row)
  # Each complete newly admitted file survives an interrupted setup.
  retained = dict(accepted);retained.update({r['path']:r for r in files})
  interim = {'profile':profile,'repo':repo,'revision':revision,'complete':False,'files':list(retained.values()),'upstream_terms':f'https://huggingface.co/{repo}/blob/{revision}/README.md'}
  temporary=root/'manifest.tmp'; temporary.write_text(json.dumps(interim,indent=2));os.replace(temporary,manifest_path)
 if profile.startswith('kokoro'):
  name='en_core_web_sm-3.8.0-py3-none-any.whl';dest=root/name
  row=accepted.get(name)
  if not row or not dest.exists():row=download('https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/'+name,dest)
  row['path']=name;files.append(row)
  with zipfile.ZipFile(dest) as archive:
   for member in archive.infolist():
    if member.filename.startswith('/') or '..' in pathlib.PurePosixPath(member.filename).parts:raise ValueError('MODEL_DOWNLOAD_INVALID')
   archive.extractall(root/'g2p')
 manifest={'profile':profile,'repo':repo,'revision':revision,'complete':True,'files':files,'upstream_terms':f'https://huggingface.co/{repo}/blob/{revision}/README.md'}
 temporary=root/'manifest.tmp';temporary.write_text(json.dumps(manifest,indent=2));os.replace(temporary,manifest_path)
 return manifest

def installed(profile):
 if profile == 'kokoro-controlled-v1':profile='kokoro-local-en-v1'
 p=ROOT/profile/'manifest.json'
 if not p.exists():raise ValueError('MODEL_SETUP_REQUIRED')
 d=json.loads(p.read_text())
 if not d.get('complete'):raise ValueError('MODEL_SETUP_REQUIRED')
 # Manifest and accepted bytes are trusted; no repeated consistency audit.
 return ROOT/profile,d

if __name__=='__main__':
 try:
  for profile in sys.argv[1:] or ['kokoro-local-en-v1']:print(json.dumps(setup(profile)))
 except Exception as e:
  print(json.dumps({'error':str(e) if isinstance(e,(ValueError,KeyError)) else 'MODEL_SETUP_FAILED'}));sys.exit(1)
