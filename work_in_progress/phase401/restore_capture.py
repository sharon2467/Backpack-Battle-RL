"""Verify and extract one evidence-only capsule, using only adjacent Git files."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import zipfile


def sha(value):
    return hashlib.sha256(value).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', required=True)
    args = parser.parse_args()
    destination = Path(args.destination).absolute()
    if destination.exists() or destination.is_symlink():
        parser.error('destination must not exist')
    if any(p.is_symlink() for p in destination.parents):
        parser.error('symlink ancestor is forbidden')
    base = Path(__file__).resolve().parent
    summaries = {}
    for segment in ('host_capture',):
        directory = base / segment
        manifest = json.loads((directory / 'CAPSULE.json').read_text())
        archive = directory / manifest['archive']
        assert archive.stat().st_size == manifest['archive_size']
        assert sha(archive.read_bytes()) == manifest['archive_sha256']
        with zipfile.ZipFile(archive) as z:
            entries = z.infolist()
            assert len(entries) == len({i.filename for i in entries}) == manifest['file_count']
            assert {i.filename for i in entries} == set(manifest['files'])
            assert z.testzip() is None
            for info in entries:
                path = PurePosixPath(info.filename)
                assert not path.is_absolute() and str(path) == info.filename
                assert '..' not in path.parts and '\\' not in info.filename
                assert not info.is_dir() and not stat.S_ISLNK(info.external_attr >> 16)
                want = manifest['files'][info.filename]
                assert info.file_size == want['size']
                value = z.read(info)
                assert len(value) == want['size'] and sha(value) == want['sha256']
        summaries[segment] = manifest
    destination.mkdir(parents=True)
    for segment, manifest in summaries.items():
        with zipfile.ZipFile(base / segment / manifest['archive']) as z:
            for name, want in manifest['files'].items():
                target = destination / segment / name
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open('xb') as stream:
                    stream.write(z.read(name))
                assert target.stat().st_size == want['size'] and sha(target.read_bytes()) == want['sha256']
    receipt = {'status': 'ALL_CAPSULE_BYTES_VERIFIED', 'source': str(base),
               'file_count': sum(m['file_count'] for m in summaries.values()),
               'payload_bytes': sum(m['payload_bytes'] for m in summaries.values()),
               'archived_code_executed': False, 'pool_operations': 0, 'models': 0,
               'validation_level': 'same-host isolated evidence extraction; not freshOS or oracle acceptance',
               'archives': {s: {k: m[k] for k in ('archive_sha256', 'archive_size', 'file_count')}
                            for s, m in summaries.items()}}
    (destination / 'RESTORE-RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
