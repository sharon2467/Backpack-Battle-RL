"""Read back cumulative354 King work and failures; execute no engine code."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath


OWNERS = (
    'data/phase349-independent-source-review/final/owned-files.json',
    'data/phase350-author-components-first-001/owned-files.json',
    'data/phase350-author-components-gzip-v3-first-001/owned-files.json',
    'data/phase350-independent-final/owned-files.json',
    'data/phase351-author-fixed-pure-first-001/owned-files.json',
    'data/phase353-king-native-source-plan/owned-files.json',
    'data/phase351-independent-checker-source/owned-files.json',
    'data/phase351-independent-final/owned-files.json',
    'data/phase352-independent-material-review/owned-files.json',
)


def no_links(path):
    path = Path(os.path.abspath(path))
    assert not any(p.is_symlink() for p in (path, *path.parents)), 'symlink ancestor'
    return path


def read_json(path):
    return json.loads(no_links(path).read_text())


def pin(path):
    path = no_links(path)
    assert path.is_file(), 'regular file required'
    with path.open('rb') as stream:
        return {'size': path.stat().st_size,
                'sha256': hashlib.file_digest(stream, 'sha256').hexdigest()}


def load_aliases(destination, recovery, public_root):
    public_root = no_links(public_root)
    manifest_pin = pin(public_root / 'MANIFEST.json')
    assert recovery['manifest'] == manifest_pin, 'public/recovery manifest identity'
    plan_path = public_root / 'owner-relocations.json'
    plan = read_json(plan_path)
    receipt = read_json(destination / 'OWNER-ARTIFACTS-RECEIPT.json')
    assert receipt['schema'] == 'public-owner-artifact-materialization-receipt/1'
    assert receipt['status'] == 'HISTORICAL_OWNER_ARTIFACTS_MATERIALIZED'
    assert receipt['manifest'] == manifest_pin
    assert receipt['relocations'] == pin(plan_path), 'receipt mapping identity'
    assert receipt['artifacts'] == plan['artifacts'], 'receipt artifact declarations'
    assert receipt['destination'] == str(destination), 'receipt destination'
    assert receipt['old_cloud_files_used'] == []
    assert all(type(receipt[k]) is int and receipt[k] == 0 for k in ('models', 'native', 'training'))
    assert plan['schema'] == 'public-owner-artifact-relocations/1' and len(plan['artifacts']) == 1
    aliases = {}
    for row in plan['artifacts']:
        for field, prefix in (('destination', 'workspace/checkpoints/'), ('source', 'parts/')):
            name = row[field]
            path = PurePosixPath(name)
            assert type(name) is str and name.startswith(prefix) and not path.is_absolute()
            assert path.as_posix() == name and all(p not in ('', '.', '..') for p in name.split('/'))
            assert '\\' not in name and ':' not in name and not any(ord(c) < 32 or ord(c) == 127 for c in name)
        assert row['historical_absolute'] == '/' + row['destination']
        assert pin(public_root / row['source']) == row['identity'], 'public artifact identity'
        output = no_links(destination / row['destination'])
        assert output.is_relative_to(destination)
        assert pin(output) == row['identity'], 'materialized artifact identity'
        aliases[row['historical_absolute']] = output
    return aliases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', required=True, type=Path)
    args = parser.parse_args()
    destination = no_links(args.destination).resolve(strict=True)
    receipt = read_json(destination / 'RECOVERY-RECEIPT.json')
    assert receipt['status'] == 'ALL_ARCHIVES_AND_LOGICAL_FILES_VERIFIED'
    assert receipt['manifest']['sha256'] == '832e363dc0a8a2bce97c5a6f2fa8c05da25695a2cf584e700c8e1d25d0995079'
    repo = destination / 'workspace/python-original-engine/repo'
    aliases = load_aliases(destination, receipt, Path(__file__).resolve().parent)
    verified = {}
    owners = {}
    queue = list(OWNERS)
    while queue:
        name = queue.pop(0)
        if name in owners:
            continue
        owner = repo / name
        before = pin(owner)
        rows = read_json(owner)['files']
        if isinstance(rows, list):
            rows = {row['path']: {'size': row['size'], 'sha256': row['sha256']}
                    for row in rows}
        assert isinstance(rows, dict)
        for leaf, wanted in rows.items():
            relative = PurePosixPath(leaf)
            assert '..' not in relative.parts
            if relative.is_absolute():
                assert leaf in aliases, leaf
                actual = pin(aliases[leaf])
            else:
                actual = pin(repo / leaf)
            assert actual == wanted, leaf
            if leaf in verified:
                assert verified[leaf] == actual
            verified[leaf] = actual
            if leaf.endswith(('/owned-files.json', '/source-owner.json')):
                queue.append(leaf)
        assert pin(owner) == before, name
        owners[name] = {'identity': before, 'leaves': len(rows)}
    component = read_json(repo / 'data/phase350-independent-final/summary.json')
    assert component['status'] == 'INDEPENDENT350_SINGLE_KING_FINITE_COMPONENTS_ACCEPTED_FULL_PURE_PENDING'
    pure = read_json(repo / 'data/phase351-independent-final/summary.json')
    assert pure['status'] == 'INDEPENDENT351_SINGLE_KING_FIXED_AB_INTERLEAVE_ACCEPTED_NATIVE_PENDING'
    state = read_json(repo / 'data/phase024-root/current-task-state.json')
    assert state['pure351']['independent_equivalence_accepted'] is True
    result = {
        'schema': 'restored-cumulative354-work-readback/2', 'status': 'PASS',
        'owners': owners, 'unique_leaf_files': len(verified),
        'unique_leaf_bytes': sum(row['size'] for row in verified.values()),
        'formal_items': 75, 'King_production_admitted': False,
        'finite_components350': 'independently_accepted',
        'full_pure351_at_cut': 'INDEPENDENT_FIXED_AB_INTERLEAVE_ACCEPTED_NATIVE_PENDING',
        'native353_at_cut': 'SOURCE_PLAN_ONLY',
        'historical_absolute_owner_artifact_aliases': sorted(aliases),
        'old_cloud_files_used': [],
        'new_models': 0, 'new_native': 0, 'new_training': 0,
        'same_host_directory_test': True, 'fresh_OS_verified': False,
    }
    output = destination / 'cumulative354-work-validation.json'
    with output.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
