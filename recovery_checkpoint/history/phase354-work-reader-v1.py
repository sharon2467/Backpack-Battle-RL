"""Read back cumulative354 King work and failures; execute no engine code."""
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
    'data/phase351-independent-checker-source/owned-files.json',
    'data/phase351-independent-final/owned-files.json',
    'data/phase352-independent-material-review/owned-files.json',
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
    assert receipt['manifest']['sha256'] == '832e363dc0a8a2bce97c5a6f2fa8c05da25695a2cf584e700c8e1d25d0995079'
    repo = destination / 'workspace/python-original-engine/repo'
    relocation = json.loads((Path(__file__).resolve().parent / 'owner-relocations.json').read_text())
    aliases = {row['historical_absolute']: destination / row['destination'] for row in relocation['artifacts']}
    alias_receipt = json.loads((destination / 'OWNER-ARTIFACTS-RECEIPT.json').read_text())
    assert alias_receipt['status'] == 'HISTORICAL_OWNER_ARTIFACTS_MATERIALIZED'
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
    component = json.loads((repo / 'data/phase350-independent-final/summary.json').read_text())
    assert component['status'] == 'INDEPENDENT350_SINGLE_KING_FINITE_COMPONENTS_ACCEPTED_FULL_PURE_PENDING'
    pure = json.loads((repo / 'data/phase351-independent-final/summary.json').read_text())
    assert pure['status'] == 'INDEPENDENT351_SINGLE_KING_FIXED_AB_INTERLEAVE_ACCEPTED_NATIVE_PENDING'
    state = json.loads((repo / 'data/phase024-root/current-task-state.json').read_text())
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
