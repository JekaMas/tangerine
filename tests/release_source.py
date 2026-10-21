"""The actual download source fixture; no private runtime or workflow files."""
from pathlib import Path
import zipfile

def archive_source(root,destination):
 root=Path(root)
 with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED) as archive:
  for dirname in ['services','deploy','scripts','specification/v2']:
   for path in (root/dirname).rglob('*'):
    if path.is_file() and not any(part in ['node_modules','.next','__pycache__'] for part in path.parts):archive.write(path,str(path.relative_to(root)))
  for name in ['LICENSE','NOTICE','THIRD_PARTY_NOTICES.md','README.md','.env.example','.dockerignore']:
   path=root/name
   if path.is_file():archive.write(path,name)
 return Path(destination)
