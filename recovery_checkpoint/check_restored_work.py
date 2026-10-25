"""Read back cumulative352 King work and failures; execute no engine code."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath


OWNERS = (
    'data/phase349-independent-source-review/final/owned-files.json',
    'data/phase350-author-components-first-001/owned-files.json',
    'data/phase350-author-components-gzip-v3-first-001/owned-files.json',
    'data/phase350-independent-final/owned-files.json',
    'data/phase351-author-fixed-pure-first-001/owned-files.json',
    'data/phase353-king-native-source-plan/owned-files.json',
)


def pin(path):
    with path.open('rb') as stream:
        return {'size': path.stat().st_size,
                'sha256': hashlib.file_digest(stream, 'sha256').hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', required=True, type=Path)
    args = parser.parse_args()
    destination = args.destination.resolve(strict=True)
    receipt = json.loads((destination / 'RECOVERY-RECEIPT.json').read_text())
    assert receipt['status'] == 'ALL_ARCHIVES_AND_LOGICAL_FILES_VERIFIED'
    assert receipt['manifest']['sha256'] == '8b7768680cfeac688693700adba6002b710017228a626e0fce155b80653988ed'
    repo = destination / 'workspace/python-original-engine/repo'
    verified = {}
    owners = {}
    queue = list(OWNERS)
    while queue:
        name = queue.pop(0)
        if name in owners:
            continue
        owner = repo / name
        before = pin(owner)
        rows = json.loads(owner.read_text())['files']
        if isinstance(rows, list):
            rows = {row['path']: {'size': row['size'], 'sha256': row['sha256']}
                    for row in rows}
        assert isinstance(rows, dict)
        for leaf, wanted in rows.items():
            relative = PurePosixPath(leaf)
            assert not relative.is_absolute() and '..' not in relative.parts
            actual = pin(repo / leaf)
            assert actual == wanted, leaf
            if leaf in verified:
                assert verified[leaf] == actual
            verified[leaf] = actual
            if leaf.endswith(('/owned-files.json', '/source-owner.json')):
                queue.append(leaf)
        assert pin(owner) == before, name
        owners[name] = {'identity': before, 'leaves': len(rows)}
    component = json.loads((repo / 'data/phase350-independent-final/summary.json').read_text())
    assert component['status'] == 'INDEPENDENT350_SINGLE_KING_FINITE_COMPONENTS_ACCEPTED_FULL_PURE_PENDING'
    result = {
        'schema': 'restored-cumulative352-work-readback/1', 'status': 'PASS',
        'owners': owners, 'unique_leaf_files': len(verified),
        'unique_leaf_bytes': sum(row['size'] for row in verified.values()),
        'formal_items': 75, 'King_production_admitted': False,
        'finite_components350': 'independently_accepted',
        'full_pure351_at_cut': 'four_raw_produced_independent_comparison_pending',
        'native353_at_cut': 'SOURCE_PLAN_ONLY',
        'new_models': 0, 'new_native': 0, 'new_training': 0,
        'same_host_directory_test': True, 'fresh_OS_verified': False,
    }
    output = destination / 'cumulative352-work-validation.json'
    with output.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
