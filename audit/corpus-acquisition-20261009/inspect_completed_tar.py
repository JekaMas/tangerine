"""Read-only native archive inventory. Does not extract or execute source content."""
from pathlib import Path
import collections
import hashlib
import json
import sys
import tarfile

source = Path(sys.argv[1])
output = Path(sys.argv[2])
assert source.is_file() and not source.name.endswith('.part')
entries = []
with tarfile.open(source, 'r|gz') as archive:
    for member in archive:
        item = {'path': member.name, 'bytes': member.size,
                'kind': 'file' if member.isfile() else 'directory' if member.isdir() else 'other'}
        if member.isfile():
            digest = hashlib.sha256()
            stream = archive.extractfile(member)
            count = 0
            while block := stream.read(1024 * 1024):
                digest.update(block)
                count += len(block)
            assert count == member.size, member.name
            item['sha256'] = digest.hexdigest()
        entries.append(item)
files = [entry for entry in entries if entry['kind'] == 'file']
result = {'archive': str(source), 'scope': 'complete native member byte traversal; no application import or semantic normalization',
          'members': entries, 'file_count': len(files),
          'extension_counts': dict(collections.Counter(Path(item['path']).suffix.lower() for item in files)),
          'native_file_bytes': sum(item['bytes'] for item in files),
          'other_member_count': sum(item['kind'] == 'other' for item in entries),
          'extracted_or_executed_source_content': False}
output.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'archive': source.name, 'file_count': result['file_count'], 'extensions': result['extension_counts']}), flush=True)
