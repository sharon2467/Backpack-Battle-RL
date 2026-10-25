"""Read back recovered bounded75; optional CLI help, never run a battle."""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import subprocess
import sys


def pin(path):
    with path.open('rb') as stream:
        return {'size': path.stat().st_size, 'sha256': hashlib.file_digest(stream, 'sha256').hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', required=True, type=Path)
    parser.add_argument('--help-only', action='store_true')
    args = parser.parse_args()
    dest = args.destination.resolve(strict=True)
    recovered = json.loads((dest / 'RECOVERY-RECEIPT.json').read_text())
    assert recovered['status'] == 'ALL_ARCHIVES_AND_LOGICAL_FILES_VERIFIED'
    repo = dest / 'workspace/python-original-engine/repo'
    state = json.loads((repo / 'data/phase024-root/current-task-state.json').read_text())
    assert state['canonical']['headless_structural_default_items'] == 75
    assert state['accepted75_candidate_final']['promoted'] is True
    freeze_path = repo / state['canonical']['source_freeze']
    assert pin(freeze_path) == state['canonical']['source_freeze_identity']
    freeze = json.loads(freeze_path.read_text())['files']
    assert len(freeze) == 15
    for name, wanted in freeze.items():
        assert pin(repo / name) == {'size': wanted.get('size', wanted.get('bytes')), 'sha256': wanted['sha256']}, name
    tree = ast.parse((repo / 'headless.py').read_text())
    literal = next(node.value for node in tree.body if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name) and target.id == 'ITEMS' for target in node.targets))
    assert isinstance(literal, ast.Call) and literal.func.id == 'frozenset'
    admitted = ast.literal_eval(literal.args[0])
    assert len(admitted) == 75 and 262 not in admitted
    reviewed = {}
    for label, owner_path in (
        ('promotion', 'data/phase344-bounded75-promotion/owned-files.json'),
        ('independent_package', 'data/phase346-independent-portable75-first-001/owned-files.json'),
    ):
        owner_file = repo / owner_path
        rows = json.loads(owner_file.read_text())['files']
        for name, wanted in rows.items():
            assert pin(repo / name) == wanted, name
        reviewed[label] = {'owner': pin(owner_file), 'leaves': len(rows),
                           'bytes': sum(row['size'] for row in rows.values())}
    actual = json.loads((repo / 'data/phase346-independent-portable75-first-001/review.json').read_text())
    assert actual['status'] == 'INDEPENDENT344_PORTABLE75_ACTUAL_CLI34401_AND_SAMEINSTANCE_PASS'
    assert actual['root_seed'] == 34401 and actual['pure_models'] == 1 and actual['native'] == 0
    result = {'schema': 'restored-bounded75-readback/1', 'status': 'PASS',
              'formal_items': 75, 'formal_source_files': 15, 'candidate75_promoted': True,
              'King_production_admitted': False, 'full_engine_RL': 'IN_PROGRESS',
              'owners': reviewed, 'new_battle_runs': 0, 'new_native_runs': 0,
              'help_runs': 0, 'same_host_directory_test': True,
              'fresh_OS_verified': False, 'full_physical_restore': recovered['full_physical_restore']}
    out = dest / 'bounded75-entrypoint-validation'
    out.mkdir(exist_ok=False)
    if args.help_only:
        # -I excludes script-directory imports, so expose only the recovered source root.
        code = "import runpy,sys;sys.path.insert(0,sys.argv[1]);sys.argv=['headless.py','--help'];runpy.run_path(sys.path[0]+'/headless.py',run_name='__main__')"
        done = subprocess.run([sys.executable, '-I', '-B', '-S', '-c', code, str(repo)],
                              cwd=out, capture_output=True, timeout=30)
        (out / 'help.stdout').write_bytes(done.stdout)
        (out / 'help.stderr').write_bytes(done.stderr)
        assert done.returncode == 0 and b'--layout' in done.stdout and not done.stderr
        result['help_runs'] = 1
    (out / 'summary.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
