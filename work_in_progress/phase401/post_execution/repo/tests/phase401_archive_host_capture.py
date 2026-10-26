"""Preserve host-complete fixed06 bytes; no capture semantics or engine execution."""
from pathlib import Path
import hashlib
import json
import stat
import zipfile

R = Path(__file__).resolve().parents[1]
RUN = Path('/workspace/native-combat-20261013/runs/original027-king-single-A-20261026-attempt06')
CONTROL = R / 'data/phase401-root-native-attempt06'
DEST = Path('/workspace/checkpoints/phase401-attempt06-host-complete-capsule')


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def snapshot(root, prefix):
    files, directories, sources = {}, {}, {}
    assert root.resolve() == root.absolute() and root.is_dir()
    for p in [root] + sorted(root.rglob('*')):
        s = p.lstat()
        name = prefix if p == root else prefix + '/' + p.relative_to(root).as_posix()
        meta = dict(mode=stat.S_IMODE(s.st_mode), mtime_ns=s.st_mtime_ns)
        if stat.S_ISDIR(s.st_mode):
            directories[name] = meta
        else:
            assert stat.S_ISREG(s.st_mode) and s.st_nlink == 1, str(p)
            files[name] = dict(meta, size=s.st_size, sha256=digest(p))
            sources[name] = p
    return files, directories, sources


def main():
    invocation = json.loads((CONTROL / 'execute-invocation.json').read_text())
    host = json.loads((CONTROL / 'execute.stdout').read_text())
    assert invocation['returncode'] == 0 and host['status'] == 'ORACLE_CAPTURE_ARCHIVED_MODELS_AND_FULLPROJECTION_PENDING'
    assert host['run'] == str(RUN) and not DEST.exists()
    files, directories, sources = {}, {}, {}
    for root, prefix in [(RUN, 'run'), (CONTROL, 'root-control')]:
        f, d, s = snapshot(root, prefix)
        files.update(f); directories.update(d); sources.update(s)
    for rel in ['docs/phase401_fixed_A_native_attempt06_execution_spec.md',
                'docs/phase401_successful_host_capture_capsule_spec.md',
                'tests/phase401_root_native_invocation.py',
                'tests/phase401_archive_host_capture.py']:
        p = R / rel; s = p.lstat()
        assert stat.S_ISREG(s.st_mode) and s.st_nlink == 1
        name = 'repo/' + rel
        files[name] = dict(mode=stat.S_IMODE(s.st_mode), mtime_ns=s.st_mtime_ns,
                           size=s.st_size, sha256=digest(p))
        sources[name] = p
    manifest = dict(schema='standalone-native401-host-complete-capsule/1',
        files=files, directories=directories, file_count=len(files),
        byte_count=sum(v['size'] for v in files.values()),
        source_run=str(RUN), source_root=str(R), baseline_in_main_checkpoint=True,
        independent402='PENDING', models=0, inputbuilds=0, King_admitted=False)
    DEST.mkdir()
    archive = DEST / 'host-complete-capsule.zip'
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        z.writestr('CAPSULE.json', json.dumps(manifest, indent=2, sort_keys=True) + '\n')
        for name, path in sorted(sources.items()):
            z.write(path, name)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert set(z.namelist()) == set(files) | {'CAPSULE.json'}
        for name, row in files.items():
            h = hashlib.sha256(); size = 0
            with z.open(name) as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b''):
                    h.update(block); size += len(block)
            assert size == row['size'] and h.hexdigest() == row['sha256'], name
            p = sources[name]; s = p.lstat()
            assert stat.S_ISREG(s.st_mode) and s.st_nlink == 1
            assert s.st_size == size and stat.S_IMODE(s.st_mode) == row['mode']
            assert s.st_mtime_ns == row['mtime_ns'] and digest(p) == row['sha256']
    receipt = dict(schema='native401-host-complete-capsule-receipt/1',
        archive=str(archive), size=archive.stat().st_size, sha256=digest(archive),
        files=len(files), bytes=manifest['byte_count'], CRC_SHA_all_members=True,
        retained_source_post_SHA=True, original_sources_retained=True,
        independent402='PENDING', models=0, inputbuilds=0, King_admitted=False)
    with (DEST / 'receipt.json').open('x') as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True); stream.write('\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
