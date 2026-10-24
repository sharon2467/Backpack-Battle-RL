"""Verify the explicit publication file set without importing either engine."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / 'MANIFEST.json').read_text())
    expected = manifest['files']
    actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*')
              if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'
              and p.name != 'MANIFEST.json'}
    if actual != set(expected):
        raise ValueError({'missing': sorted(set(expected) - actual),
                          'unexpected': sorted(actual - set(expected))})
    for name, identity in expected.items():
        path = ROOT / name
        if path.is_symlink() or '..' in Path(name).parts or Path(name).is_absolute():
            raise ValueError('unsafe publication path: ' + name)
        raw = path.read_bytes()
        if {'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()} != identity:
            raise ValueError('changed publication file: ' + name)
    runtime = json.loads((ROOT / 'evidence/runtime-sources.json').read_text())['files']
    if len(runtime) != 30 or any(expected.get(n) != w for n, w in runtime.items()):
        raise ValueError('two exact fifteen-file runtime snapshots required')
    print(f'PASS: {len(expected)} publication files; 30 exact runtime files')


if __name__ == '__main__':
    main()
