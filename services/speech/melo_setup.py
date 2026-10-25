"""Explicit one-time English accent assets; ordinary rendering is offline."""
import hashlib,json,os
from model_setup import ROOT,download

MODEL_REPO='myshell-ai/MeloTTS-English'
MODEL_REVISION='bb4fb7346d566d277ba8c8c7dbfdf6786139b8ef'
CODE_REVISION='209145371cff8fc3bd60d7be902ea69cbdb7965a'
BERT_REVISION='86b5e0934494bd15c9632b12f734a8a67f723594'

def setup():
 root=ROOT/'melo-local-en-v1';root.mkdir(parents=True,exist_ok=True);path=root/'manifest.json'
 old=json.loads(path.read_text()) if path.exists() else {'files':[]}
 if old.get('complete'):return old
 accepted={x['path']:x for x in old['files']}
 model=f'https://huggingface.co/{MODEL_REPO}/resolve/{MODEL_REVISION}/'
 bert=f'https://huggingface.co/google-bert/bert-base-uncased/resolve/{BERT_REVISION}/'
 code=f'https://raw.githubusercontent.com/myshell-ai/MeloTTS/{CODE_REVISION}/'
 files=[('config.json',model+'config.json',None),('checkpoint.pth',model+'checkpoint.pth','acd278040eaf9536908e2b965273df5a731c44d8f0da66cc5fed7972772ed23c'),('README.md',model+'README.md',None),('LICENSE',code+'LICENSE',None)]
 files += [('bert/'+n,bert+n,'68d45e234eb4a928074dfd868cead0219ab85354cc53d20e772753c6bb9169d3' if n=='model.safetensors' else None) for n in ['config.json','model.safetensors','tokenizer.json','tokenizer_config.json','vocab.txt','README.md']]
 files += [('code/melo/'+n,code+'melo/'+n,None) for n in ['models.py','modules.py','attentions.py','commons.py','transforms.py','monotonic_align/__init__.py','monotonic_align/core.py']]
 files += [('cmudict.rep',code+'melo/text/cmudict.rep',None)]
 for name,url,sha in files:
  dest=root/name
  if name not in accepted or not dest.exists():
   row=download(url,dest,sha);row['path']=name;accepted[name]=row
   print(json.dumps({'accepted':name,'size':row['size']}),flush=True)
  manifest={'profile':'melo-local-en-v1','repo':MODEL_REPO,'revision':MODEL_REVISION,'code_revision':CODE_REVISION,'bert_revision':BERT_REVISION,'complete':False,'files':list(accepted.values()),'upstream_terms':f'https://huggingface.co/{MODEL_REPO}/blob/{MODEL_REVISION}/README.md'}
  temp=root/'manifest.tmp';temp.write_text(json.dumps(manifest,indent=2));os.replace(temp,path)
 (root/'code/melo/__init__.py').write_text('')
 manifest['complete']=True;temp=root/'manifest.tmp';temp.write_text(json.dumps(manifest,indent=2));os.replace(temp,path)
 return manifest

if __name__=='__main__':print(json.dumps(setup()))
