"""Scoped platform acquisition for the classic Docker single-variant store."""
import json
class PlatformImage:
 def __init__(self,call,image,retained_tag,evidence):
  self.call,self.image,self.retained_tag,self.evidence=call,image,retained_tag,evidence
  self.original=None;self.changed=False;self.retained=False
 def inspect(self):
  result=self.call(['docker','image','inspect',self.image],check=False)
  return json.loads(result.stdout)[0] if result.returncode==0 else None
 def select(self,architecture):
  self.original=self.inspect()
  if self.original and self.original['Architecture']==architecture:return
  if self.original:
   # Keep the original image/layers alive. This tag is only rollback storage;
   # the application continues to use the official pinned registry reference.
   self.call(['docker','image','tag',self.original['Id'],self.retained_tag]);self.retained=True
   self.call(['docker','image','rm',self.image]);self.changed=True
  self.call(['docker','pull','--platform','linux/'+architecture,self.image])
 def restore(self):
  if self.changed:
   if self.inspect():self.call(['docker','image','rm',self.image])
   self.call(['docker','pull','--platform','linux/'+self.original['Architecture'],self.image])
   restored=self.inspect()
   if not restored or (restored['Id'],restored['Architecture'])!=(self.original['Id'],self.original['Architecture']):
    raise RuntimeError('Original platform image was not restored; retained rollback image: '+self.retained_tag)
   self.changed=False
   result=dict(status='restored',original_id=self.original['Id'],restored_id=restored['Id'],architecture=restored['Architecture'])
  else:result=dict(status='unchanged',original_id=None if not self.original else self.original['Id'])
  if self.retained:self.call(['docker','image','rm',self.retained_tag]);self.retained=False
  self.evidence.write_text(json.dumps(result,indent=2)+'\n')
