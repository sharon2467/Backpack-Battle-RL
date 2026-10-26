"""Seal finite setup-only preparation without importing408."""
import ast
import hashlib
import json
from pathlib import Path
import stat

ROOT = Path('/workspace/python-original-engine/repo')
OUT = ROOT / 'data/phase410-setup-only408-preparation'
assert not OUT.exists()
PINS = {
    'tests/phase408_initial_source_audit.py': (74685, 'c572cdbb35f44a3e696b0fa5ab3df539e9e985c5d88770d73e1f3bb9afe6977d'),
    'data/phase408-initial-audit-source/source-owner.json': (16495, 'c188422bd9dfe6d6365465204410f27f7c8ed9d8798afe21b8220ca09236dc88'),
    'data/phase408-initial-audit-source/source-freeze.json': (29684, '38f29ec7829b64805cd5c8cbe09caf59a32d11f75032d29948990878e10eeab8'),
    'data/phase409-independent408-source-review/review.json': (7517, '577a36611885bf97183583ad8f85d0e40a4fdef848396c31c25326b329e51cad'),
    'data/phase409-independent408-source-review/owned-files.json': (6798, 'ce876a63ee0e6b1c31ad9a78899413588c6766d256156d3407e8202b14eb701f'),
}


def read(name):
    path = ROOT / name
    assert path.resolve(strict=True) == path
    assert not any(p.is_symlink() for p in (path, *path.parents))
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and before.st_nlink == 1
    raw = path.read_bytes()
    after = path.lstat()
    assert (before.st_dev, before.st_ino, before.st_mode, before.st_nlink, before.st_size,
            before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino,
            after.st_mode, after.st_nlink, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    row = dict(path=name, size=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    assert before.st_size == len(raw)
    if name in PINS:
        assert (row['size'], row['sha256']) == PINS[name]
    return raw, row


reference_names = list(PINS) + [
    'data/phase409-independent408-source-review/static-evidence.json',
    'data/phase409-independent408-component-first-001/result.json',
    'data/phase409-independent408-source-review/runner-preload-discrepancy.json',
    'data/phase409-independent408-component-preparation/execution-manifest.json',
    'tests/phase409_setup_only408.py',
    'data/phase409-setup-only-launcher/timeout-result.json',
    'data/phase409-setup-only-launcher/timeout-trace.txt',
]
references = {}
raws = {}
for name in reference_names:
    raws[name], references[name] = read(name)
old_owner = json.loads(raws['data/phase409-independent408-source-review/owned-files.json'])
old_index = {row['path']: row for row in old_owner['files']}
for name in reference_names:
    if name.startswith('data/phase409') or name == 'tests/phase409_setup_only408.py':
        if name != 'data/phase409-independent408-source-review/owned-files.json':
            assert references[name] == old_index[name]
source_name = 'tests/phase408_initial_source_audit.py'
tree = ast.parse(raws[source_name], filename=str(ROOT / source_name))
imports = []
definitions = []
statement_counts = {}
for node in tree.body:
    key = type(node).__name__
    statement_counts[key] = statement_counts.get(key, 0) + 1
    if isinstance(node, ast.Expr):
        assert isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)
    elif isinstance(node, ast.Assign):
        assert all(isinstance(target, ast.Name) for target in node.targets)
        ast.literal_eval(node.value)
    elif isinstance(node, ast.Import):
        imports.extend(alias.name for alias in node.names)
    elif isinstance(node, ast.ImportFrom):
        assert node.level == 0
        imports.append(node.module)
    elif isinstance(node, ast.FunctionDef):
        assert not node.decorator_list and node.returns is None and not node.type_params
        for arg in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs):
            assert arg.annotation is None
        assert node.args.vararg is None and node.args.kwarg is None
        for value in (*node.args.defaults, *node.args.kw_defaults):
            if value is not None:
                ast.literal_eval(value)
        definitions.append(node.name)
    elif isinstance(node, ast.ClassDef):
        assert node.name == 'SourceIntegrityError' and not node.decorator_list
        assert not node.keywords and not node.type_params and len(node.bases) == 1
        assert isinstance(node.bases[0], ast.Name) and node.bases[0].id == 'ValueError'
        assert len(node.body) == 1 and isinstance(node.body[0], ast.Pass)
    elif isinstance(node, ast.If):
        assert ast.unparse(node.test) == "__name__ == '__main__'"
        assert not node.orelse and len(node.body) == 1
        assert ast.unparse(node.body[0]) == 'sys.exit(main())'
    else:
        raise AssertionError(key)
preloaded = ['argparse', 'hashlib', 'json', 'math', 'os', 'pathlib', 're', 'stat',
             'struct', 'sys', 'traceback']
assert imports == preloaded and len(definitions) == 29
for name in ('tests/phase410_setup_only408.py', 'tests/phase410_launch_setup_only408.py'):
    runner_tree = ast.parse(read(name)[0], filename=name)
    local_names = {node.name for node in runner_tree.body if isinstance(node, ast.FunctionDef)}
    for node in ast.walk(runner_tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in set(definitions) - local_names, node.func.id
OUT.mkdir()
created = []


def save(name, value):
    path = OUT / name
    raw = (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()
    with path.open('xb') as handle:
        handle.write(raw)
    created.append(str(path.relative_to(ROOT)))


save('source-top-level-safety.json', dict(schema='independent410-top-level-setup-safety/1',
    status='PASS', module=references[source_name], imports=imports, public_definitions=definitions,
    statement_counts=statement_counts, literal_assignments_only=True,
    function_defaults_literal_and_annotations_absent=True, inert_exception_class=True,
    main_guard_skipped_with_independent_module_name=True, runner_direct408_calls=0,
    source_API_calls_during_setup=0, check_scope='loading boundary only; no83-leaf/20API rerun'))
save('references.json', dict(schema='independent410-immutable-reference-bindings/1',
    files=list(references.values()), old409_unchanged=True,
    old_timeout_cause='SOURCE_ONLY_INFERENCE: profiler frame.f_code audit feedback with live-list generators; no runtime diagnosis'))
save('expected.json', dict(schema='independent410-setup-expected/1',
    status='SETUP_ONLY_READ_SCOPE_PASS', event_counts={'open': 1, 'import': 0, 'compile': 1, 'exec': 1},
    module_instances=1, top_level_API_calls=0, actual12_reads=0, automatic_retry=False))
save('execution-manifest.json', dict(schema='independent410-finite-setup-manifest/1',
    module=references[source_name], source_owner=references['data/phase408-initial-audit-source/source-owner.json'],
    source_freeze=references['data/phase408-initial-audit-source/source-freeze.json'],
    preloaded_modules=preloaded + ['types', 'time'],
    observed_events=['open', 'import', 'compile', 'exec'],
    measured_allowed_path_opens=[str(ROOT / source_name)], measured_allowed_imports=[],
    loader='compile complete original pinned bytes + exec independent ModuleType; original __file__',
    timeout_seconds=25, child_process_invocations=1, top_level_API_calls=0,
    models=0, native=0, inputbuild=0, old_SUT_calls=0, schema_calls=0, actual12_reads=0,
    first_failure='preserve_and_stop_no_retry',
    output_phase='result and launcher files after observation; progress stdout stage markers only',
    previous_completed_module_instances=1, previous_timeout_completion=None))
names = ['docs/phase410_setup_only408_scope_closure_spec.md',
         'tests/phase410_prepare_setup_only408.py', 'tests/phase410_setup_only408.py',
         'tests/phase410_launch_setup_only408.py'] + created
rows = [read(name)[1] for name in names]
save('owned-files.json', dict(schema='independent410-setup-preparation-owner/1', files=rows,
    ordinary_leaves=len(rows), ordinary_bytes=sum(row['size'] for row in rows),
    no_more_writes=True, sealed_before_single_child=True))
print(json.dumps(dict(status='PREPARATION_SEALED', leaves=len(rows), source_imports=0)))
