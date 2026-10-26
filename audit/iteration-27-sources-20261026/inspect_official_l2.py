"""One intake inventory of the actual official archive; never execute source files."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, tempfile, time, zipfile

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/iteration-27-sources-20261026/research'
ARCHIVE=Path('/Users/jekamas/projects/0xatelerix/tangerine/data/corpora/l2-arctic/official-v5-20261026.zip')
SPEAKERS=set('ABA ASI BWC EBVS ERMS HKK NJS HQTV SKA YDCK TNI PNV HJK NCC MBMPS LXC TLV SVBI YBAA YKWK ZHAA RRBI THV TXHC'.split())


def canonical(name):
    parts=name.split('/')
    for i,part in enumerate(parts):
        if part in SPEAKERS or 'suitcase' in part.lower() and not part.lower().endswith('.zip'):
            return '/'.join(parts[i:])
    return name


def main():
    result=OUT/'l2-official-inventory.json'
    if result.exists():
        print('Retaining already inventoried official archive; no repeated byte audit.')
        return
    deadline=time.monotonic()+3600
    while not ARCHIVE.exists():
        if time.monotonic()>deadline:
            raise RuntimeError('Official transfer remains incomplete; do not inventory sparse partial bytes')
        time.sleep(1)
    receipt=json.loads((OUT/'l2-official-confirmed.json').read_text())
    assert receipt['status']=='downloaded'
    files=[];docs={}

    def inventory(z,prefix=''):
        for member in z.infolist():
            if member.is_dir():
                continue
            name=prefix+member.filename
            digest=hashlib.sha256();size=0;first=b''
            child=tempfile.TemporaryFile() if name.lower().endswith('.zip') else None
            with z.open(member) as reader:
                while True:
                    chunk=reader.read(1024*1024)
                    if not chunk:
                        break
                    if not first:
                        first=chunk[:65536]
                    digest.update(chunk);size+=len(chunk)
                    if child is not None:
                        child.write(chunk)
            assert size==member.file_size
            files.append(dict(path=name,canonical_path=canonical(name),bytes=size,sha256=digest.hexdigest(),crc32=member.CRC))
            basename=Path(member.filename).name.lower()
            if basename in ['license','readme.md','prompts']:
                docs[basename]=dict(path=name,sha256=digest.hexdigest(),excerpt=first.decode('utf8','replace')[:1000])
            if child is not None:
                child.seek(0)
                with zipfile.ZipFile(child) as nested:
                    inventory(nested,name+'/')
                child.close()

    with zipfile.ZipFile(ARCHIVE) as source:
        inventory(source)
    native=[row for row in files if not row['path'].lower().endswith('.zip')]
    read=[row for row in native if 'suitcase' not in row['path'].lower()]
    suit=[row for row in native if 'suitcase' in row['path'].lower()]
    read_wav=[row for row in read if '/wav/' in row['canonical_path'].lower() and row['path'].lower().endswith('.wav')]
    manual=[row for row in read if '/annotation/' in row['canonical_path'].lower() and row['path'].lower().endswith('.textgrid')]
    suit_wav=[row for row in suit if row['path'].lower().endswith('.wav')]
    actual={row['canonical_path']:row['sha256'] for row in native}
    reference=json.loads((ROOT/'audit/corpus-acquisition-20261009/l2-arctic-mirror-native-inventory.json').read_text())
    expected={row['path']:row['sha256'] for archive in reference['archives'] for row in archive['members']}
    missing=[name for name in expected if name not in actual]
    different=[name for name,sha in expected.items() if name in actual and actual[name]!=sha]
    match=sum(actual.get(name)==sha for name,sha in expected.items())
    summary=dict(source_id='L2-ARCTIC',source_version='official v5.0',observed_at=datetime.now(timezone.utc).isoformat(),
                 archive_path=str(ARCHIVE),archive_sha256=receipt['sha256'],archive_bytes=receipt['bytes'],
                 inventory_scope='Every actual archive member streamed once with native ZIP CRC checks and digest; source code is inert. No normalized database import or linguistic/acoustic claim.',
                 files=len(files),read_speakers=sorted({row['canonical_path'].split('/')[0] for row in read_wav}),
                 read_wav_count=len(read_wav),read_manual_annotation_count=len(manual),suitcase_wav_count=len(suit_wav),
                 license='CC BY-NC 4.0',license_basis='Actual source notice and retained author access email',documents=docs,
                 mirror_comparison=dict(scope='Canonical native members from the25accepted mirror component inventories; archive wrappers and outside documentation are not asserted byte-equivalent.',
                                        source_commit=reference['source_commit'],expected=len(expected),matched=match,missing=len(missing),different=len(different),all_saved_native_members_match=not missing and not different),
                 application_import_observed=False,normalized_complete_observed=False,dataset_code_executed=False)
    (OUT/'l2-official-members.json').write_text(json.dumps(dict(files=files,mirror_missing=missing,mirror_different=different),indent=2)+'\n')
    result.write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ['documents','read_speakers']},indent=2),flush=True)


if __name__=='__main__':
    main()
