"""Preserve and verify completed native run projects. No prune/delete command."""
from __future__ import annotations
import argparse
import contextlib
import ctypes
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import tempfile
import zipfile

RUNS = Path('/workspace/native-combat-20261013/runs')
BASE = Path('/workspace/godotsteam-startup-20261013/baseline/Backpack Battles')
DRIVERS = ('native_combat_capture.gd', 'native_capture_config.json', 'native_random_observer.gd', '.native-random-observer-disposable')
GENERATED = {'compaction', 'driver', '.native-compaction.lock'}
REQUIRED_BUNDLE = {'baseline-files.json', 'project-files.json', 'overlay-manifest.json', 'overlay.zip', 'retained-evidence.json', 'source-identities.json', 'eligibility.json', 'RESTORE-PROJECT.md'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, sort_keys=True, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def safe_path(name, root_ok=False):
    require(isinstance(name, str) and bool(name), 'invalid path')
    if root_ok and name == '.':
        return name
    p = PurePosixPath(name)
    require(not p.is_absolute() and not any(x in ('', '.', '..') for x in name.split('/'))
            and '\\' not in name and '\0' not in name and p.as_posix() == name,
            'unsafe relative path: ' + name)
    return name


def inventory(root, exclude=(), relaxed=False):
    """Full byte/mode/time manifest; relaxed retains untouched user special nodes."""
    root = Path(root)
    device = root.lstat().st_dev
    rows = []
    def visit(path):
        rel = path.relative_to(root).as_posix()
        if rel != '.' and rel.split('/')[0] in exclude:
            return
        s = path.lstat()
        mode = stat.S_IMODE(s.st_mode)
        require(s.st_dev == device, 'cross-device path: ' + str(path))
        row = dict(path=rel, mode=mode, mtime_ns=s.st_mtime_ns)
        if not relaxed:
            require(not mode & 0o7000, 'special permission bits: ' + str(path))
            require(not os.listxattr(path, follow_symlinks=False), 'xattrs/ACL unsupported: ' + str(path))
        if stat.S_ISDIR(s.st_mode):
            row['kind'] = 'directory'
            rows.append(row)
            for child in sorted(path.iterdir()):
                safe_path(child.relative_to(root).as_posix())
                visit(child)
        elif stat.S_ISREG(s.st_mode):
            require(relaxed or s.st_nlink == 1, 'hardlink unsupported: ' + str(path))
            flags = os.O_RDONLY | os.O_NOFOLLOW
            fd = os.open(path, flags)
            with os.fdopen(fd, 'rb') as f:
                before = os.fstat(f.fileno())
                h = hashlib.sha256()
                for block in iter(lambda: f.read(1024 * 1024), b''):
                    h.update(block)
                after = os.fstat(f.fileno())
            signature = lambda x: (x.st_dev, x.st_ino, x.st_mode, x.st_size, x.st_mtime_ns, x.st_ctime_ns)
            require(signature(s) == signature(before) == signature(after) == signature(path.lstat()), 'changed during read: ' + str(path))
            row.update(kind='file', size=s.st_size, sha256=h.hexdigest())
            rows.append(row)
        else:
            require(relaxed, 'unsupported node: ' + str(path))
            row.update(kind='symlink' if stat.S_ISLNK(s.st_mode) else 'special', type_bits=stat.S_IFMT(s.st_mode))
            if stat.S_ISLNK(s.st_mode):
                row['target'] = os.readlink(path)
            rows.append(row)
    visit(root)
    return {'schema': 'native-run-project-manifest/1', 'entries': rows}


def index(manifest):
    rows = manifest['entries']
    result = {}
    for row in rows:
        path = safe_path(row['path'], root_ok=True)
        require(path not in result, 'duplicate manifest path')
        require(row['kind'] in ('file', 'directory'), 'unsupported manifest kind')
        require(type(row['mode']) is int and 0 <= row['mode'] <= 0o777, 'invalid mode')
        require(type(row['mtime_ns']) is int, 'invalid mtime')
        if row['kind'] == 'file':
            require(type(row['size']) is int and row['size'] >= 0 and len(row['sha256']) == 64, 'invalid file manifest')
        result[path] = row
    require(result.get('.', {}).get('kind') == 'directory', 'missing root directory')
    for path, row in result.items():
        if path != '.':
            parent = PurePosixPath(path).parent.as_posix()
            require(result.get(parent, {}).get('kind') == 'directory', 'missing/conflicting parent')
    return result


def overlay_plan(base, project):
    b, p = index(base), index(project)
    for name in b.keys() & p.keys():
        require(b[name]['kind'] == p[name]['kind'], 'file/directory replacement unsupported: ' + name)
    content = [name for name, row in p.items() if row['kind'] == 'file' and (name not in b or row['sha256'] != b[name].get('sha256'))]
    return {'schema': 'native-run-overlay/1', 'content': sorted(content), 'removed': sorted(b.keys() - p.keys()),
            'added': sorted(p.keys() - b.keys()), 'changed': sorted(k for k in b.keys() & p.keys() if b[k] != p[k])}


def process_check(run):
    ignored = {os.getpid()}  # All ancestors are inspected; only this checking process is excluded.
    target = str(run)
    matches, gaps, inspected = [], [], []
    def relevant(value):
        return value == target or value.startswith(target + '/')
    for proc in Path('/proc').iterdir():
        if not proc.name.isdecimal() or int(proc.name) in ignored:
            continue
        try:
            tail = (proc / 'stat').read_text().rsplit(')', 1)[1].split()
            if tail[0] == 'Z':
                continue
            args = (proc / 'cmdline').read_bytes().split(b'\0')
            require(bool(args[0]), 'unknown live process command: ' + proc.name)
            pid = int(proc.name)
            inspected.append({'pid': pid, 'starttime': tail[19]})
            if any(relevant(a.decode(errors='replace')) for a in args):
                matches.append({'pid': pid, 'kind': 'command'})
            for what in ('cwd', 'fd', 'maps'):
                try:
                    if what == 'cwd':
                        values = [os.readlink(proc / what)]
                    elif what == 'fd':
                        values = []
                        for fd in (proc / what).iterdir():
                            try:
                                values.append(os.readlink(fd))
                            except FileNotFoundError:
                                pass
                    else:
                        values = [line.split(maxsplit=5)[5] for line in (proc / what).read_text().splitlines() if len(line.split(maxsplit=5)) == 6]
                    if any(relevant(v.removesuffix(' (deleted)')) for v in values):
                        matches.append({'pid': pid, 'kind': what})
                except PermissionError:
                    gaps.append({'pid': pid, 'unreadable': what})
                except FileNotFoundError:
                    pass
        except FileNotFoundError:
            continue
    require(not matches, 'active run references: ' + json.dumps(matches))
    return {'checked_utc': stamp(), 'active_matches': matches, 'inspected': inspected,
            'inspection_gaps': gaps, 'excluded_self_pid': os.getpid(), 'process_inspection_complete': not gaps, 'prune_eligible': False}


def scope(run, baseline):
    run, baseline = Path(run).absolute(), Path(baseline).absolute()
    require(run.parent == RUNS and run.name not in ('', '.', '..'), 'run outside fixed runs directory')
    for path in (run, run / 'project', run / 'output', run / 'data', run / 'user', baseline):
        require(path.resolve() == path and path.is_dir() and not path.is_symlink(), 'invalid scope: ' + str(path))
    require(baseline == BASE, 'baseline path must be immutable approved snapshot')
    return run, baseline


def retained(run):
    result = {}
    for name in ('output', 'data', 'user'):
        tree = inventory(run / name, GENERATED if name == 'output' else (), relaxed=True)
        if name == 'output':
            # Adding new children changes only this parent's mtime; all old descendants stay exact.
            tree['entries'][0].pop('mtime_ns')
        result[name] = tree
    return result


def eligibility(run):
    process = process_check(run)
    r, h, v = [read(run / 'output' / n) for n in ('process_result.json', 'host_manifest.json', 'host_validation.json')]
    require(r.get('capture_complete') is True and v.get('capture_complete') is True, 'capture not explicitly complete')
    require(r.get('source_changes_after_run') == [] and r.get('timed_out') is False and type(r.get('exit_code')) is int and r['exit_code'] == 0 and 'abort_reason' in r and r['abort_reason'] is None, 'failed/changed process result')
    require(v.get('errors') == [] and h.get('baseline_modifications') == [], 'validation/source errors')
    require(bool(v.get('file_sha256')), 'missing capture hash map')
    for name, sha in v['file_sha256'].items():
        safe_path(name)
        require(digest(run / 'output/capture' / name) == sha, 'capture hash mismatch: ' + name)
    n = read(run / 'output/capture/native_manifest.json')
    config = read(run / 'project/native_capture_config.json')
    for key in ('global_seed', 'util_seed'):
        require(config[key] == h[key] and config[key] == n['config'][key], 'config seed mismatch')
    require(config['timeouts'] == n['config']['timeouts'] and config['timeouts']['battle_seconds'] == h['limits_seconds']['battle'] and config['timeouts']['total_seconds'] + 5 == h['limits_seconds']['total'], 'config budget mismatch')
    require(n['entry'] == h['entry'] and bool(config.get('player_fixture_enabled', False)) == ('player_fixture_sha256' in h), 'entry mismatch')
    require(digest(run / 'project/native_combat_capture.gd') == h['collector_sha256'], 'historical collector mismatch')
    require(digest(run / 'data/custom_opponent.json') == h['fixture_sha256'], 'opponent input mismatch')
    if 'player_fixture_sha256' in h:
        require(digest(run / 'data/custom_player.json') == h['player_fixture_sha256'] == n['player_fixture_sha256'], 'player input mismatch')
    return {'status': 'PASS', 'process_check': process, 'process_clean_exit': r.get('process_clean_exit'),
            'historical_report_sha256': {x: digest(run / 'output' / x) for x in ('process_result.json', 'host_manifest.json', 'host_validation.json')}}


def sources(run, baseline, base_tree, project_tree):
    task = baseline.parent.parent
    h = read(run / 'output/host_manifest.json')
    migration = task / 'migration-manifest.json'
    require(digest(migration) == h['source_manifest_sha256'], 'migration identity mismatch')
    b, p = index(base_tree), index(project_tree)
    records = {x['path'].removeprefix('Backpack Battles/'): x for x in read(migration)['files'] if x['path'].startswith('Backpack Battles/')}
    require({k for k, v in b.items() if v['kind'] == 'file'} == records.keys(), 'baseline path set mismatch')
    expected = {}
    for name, row in records.items():
        require(b[name]['size'] == row['size'] and b[name]['sha256'] == row['sha256'], 'baseline corruption: ' + name)
        expected[name] = row['sha256']
    patch = h.get('audited_runtime_observation_patch')
    if patch:
        require(patch == read(run / 'output/observer-patch/native_random_observer_patch_manifest.json'), 'historical patch manifest mismatch')
        require(digest(run / 'output/observer-patch/native_random_observer.patch') == patch['diff_sha256'], 'historical patch diff mismatch')
        seen = set()
        for row in patch['patches']:
            name = safe_path(row['path'])
            require(name not in seen and b.get(name, {}).get('sha256') == row['before_sha256'], 'patch base mismatch')
            seen.add(name)
            require(p.get(name, {}).get('size') == row['after_size'], 'patch size mismatch')
            expected[name] = row['after_sha256']
    for name, sha in expected.items():
        require(p.get(name, {}).get('sha256') == sha, 'run source mismatch: ' + name)
    identity = {}
    for name in ('migration-manifest.json', 'receiving-index.json', 'imports-parts-manifest.json'):
        path = task / name
        require(path.is_file(), 'private source identity missing: ' + name)
        identity[name] = {'sha256': digest(path), 'contents': read(path)}
    require(identity['receiving-index.json']['contents'].get('library_uploads'), 'missing private baseline versions')
    return {'source_project_files': len(records), 'identities': identity}


def archive_overlay(project, tree, plan, dest):
    rows = index(tree)
    with zipfile.ZipFile(dest, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name in plan['content']:
            info = zipfile.ZipInfo(name)
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | rows[name]['mode']) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            with z.open(info, 'w') as out, (project / name).open('rb') as src:
                shutil.copyfileobj(src, out)
    validate_archive(dest, tree, plan)


def validate_archive(path, tree, plan):
    rows = index(tree)
    with zipfile.ZipFile(path) as z:
        infos = z.infolist()
        require(len(infos) == len({x.filename for x in infos}) and set(z.namelist()) == set(plan['content']), 'overlay member set mismatch')
        for info in infos:
            name = safe_path(info.filename)
            require(stat.S_IFMT(info.external_attr >> 16) == stat.S_IFREG and stat.S_IMODE(info.external_attr >> 16) == rows[name]['mode'], 'overlay member type/mode mismatch')
            require(info.file_size == rows[name]['size'], 'overlay size mismatch')
            with z.open(info) as f:
                h = hashlib.sha256()
                for block in iter(lambda: f.read(1048576), b''):
                    h.update(block)
            require(h.hexdigest() == rows[name]['sha256'], 'overlay member SHA mismatch')


def load_bundle(bundle):
    bundle = Path(bundle)
    m = read(bundle / 'bundle-manifest.json')
    require(REQUIRED_BUNDLE <= set(m['files']), 'required static bundle members missing from hash closure')
    for rel, sha in m['files'].items():
        safe_path(rel)
        require((bundle / rel).resolve() == bundle.absolute() / rel and (bundle / rel).is_file(), 'non-regular or linked bundle member')
        require(digest(bundle / rel) == sha, 'bundle hash mismatch: ' + rel)
    for name, sha in m['driver_sha256'].items():
        safe_path(name)
        require(digest(bundle.parent / 'driver' / name) == sha, 'retained driver mismatch: ' + name)
    base, project, plan = [read(bundle / x) for x in ('baseline-files.json', 'project-files.json', 'overlay-manifest.json')]
    require(overlay_plan(base, project) == plan, 'overlay plan mismatch')
    validate_archive(bundle / 'overlay.zip', project, plan)
    return base, project, plan


def _reconstruct(baseline, bundle, dest):
    base, project, plan = load_bundle(bundle)
    actual = inventory(baseline)
    # Restored private baseline timestamps/modes may differ; validate all bytes and paths.
    b, a = index(base), index(actual)
    require(b.keys() == a.keys(), 'restore baseline path set mismatch')
    for name in b:
        require(b[name]['kind'] == a[name]['kind'] and all(b[name].get(k) == a[name].get(k) for k in ('size', 'sha256')), 'restore baseline mismatch: ' + name)
    dest = Path(dest).absolute()
    check_destination(baseline, bundle, dest)
    p = index(project)
    need = sum(((r.get('size', 0) + 4095) // 4096) * 4096 for r in p.values()) + 1024**3
    require(shutil.disk_usage(dest.parent).free >= need, 'insufficient rebuild headroom')
    dest.mkdir(mode=0o700)
    # Build exactly the target set. Missing baseline files are not copied; originals untouched.
    for name, row in p.items():
        if row['kind'] == 'directory' and name != '.':
            (dest / name).mkdir(mode=0o700)
    content = set(plan['content'])
    with zipfile.ZipFile(Path(bundle) / 'overlay.zip') as z:
        for name, row in p.items():
            if row['kind'] != 'file':
                continue
            with (dest / name).open('xb') as out:
                with (z.open(name) if name in content else (Path(baseline) / name).open('rb')) as src:
                    shutil.copyfileobj(src, out)
            os.chmod(dest / name, row['mode'])
            os.utime(dest / name, ns=(row['mtime_ns'], row['mtime_ns']))
    for name, row in sorted(p.items(), key=lambda x: x[0].count('/'), reverse=True):
        if row['kind'] == 'directory':
            os.chmod(dest / name, row['mode'])
            os.utime(dest / name, ns=(row['mtime_ns'], row['mtime_ns']))
    require(inventory(dest) == project, 'full reconstructed tree mismatch')
    return project


def check_destination(baseline, bundle, dest):
    dest = Path(dest).absolute()
    for protected in (Path(baseline).resolve(), Path(bundle).resolve()):
        require(dest != protected and protected not in dest.parents and dest not in protected.parents, 'destination intersects baseline/bundle')
    require(dest != RUNS and dest not in RUNS.parents, 'destination is runs root/ancestor')
    if RUNS.is_dir():
        for run in RUNS.iterdir():
            if run.is_dir() and any((run / name).exists() for name in ('project', 'output', 'data', 'user')):
                require(dest != run and run not in dest.parents and dest not in run.parents, 'destination intersects existing run')
    require(not dest.exists() and not dest.is_symlink() and dest.parent.resolve() == dest.parent, 'restore destination must be new under resolved parent')


def sync_tree(root):
    for path in sorted(Path(root).rglob('*'), reverse=True) + [Path(root)]:
        with path.open('rb') if path.is_file() else contextlib.nullcontext(None) as stream:
            if stream is not None:
                os.fsync(stream.fileno())
        if path.is_dir():
            fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)


def publish_new_directory(source, dest):
    # Linux renameat2 NOREPLACE avoids overwriting even an empty destination in a race.
    libc = ctypes.CDLL(None, use_errno=True)
    rename = libc.renameat2
    rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    rename.restype = ctypes.c_int
    if rename(-100, os.fsencode(source), -100, os.fsencode(dest), 1) != 0:
        err = ctypes.get_errno()
        raise OSError(err, os.strerror(err), str(dest))
    fd = os.open(Path(dest).parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def reconstruct(baseline, bundle, dest):
    dest = Path(dest).absolute()
    check_destination(baseline, bundle, dest)
    with tempfile.TemporaryDirectory(prefix='.native-restore-', dir=dest.parent) as temp:
        staged = Path(temp) / 'project'
        result = _reconstruct(baseline, bundle, staged)
        sync_tree(staged)
        check_destination(baseline, bundle, dest)
        publish_new_directory(staged, dest)
    return result


@contextlib.contextmanager
def locked(run):
    with (run / 'output/.native-compaction.lock').open('a') as f:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def pack(run, baseline):
    run, baseline = scope(run, baseline)
    with locked(run):
        require(not (run / 'output/compaction').exists() and not (run / 'output/driver').exists(), 'bundle/driver already exists')
        gate = eligibility(run)
        print('COMPACTION inventory source/project/retained', flush=True)
        base_tree, project_tree, original = inventory(baseline), inventory(run / 'project'), retained(run)
        identity = sources(run, baseline, base_tree, project_tree)
        plan = overlay_plan(base_tree, project_tree)
        with tempfile.TemporaryDirectory(prefix='.native-pack-', dir=run.parent) as tmp:
            tmp = Path(tmp)
            bundle, driver = tmp / 'compaction', tmp / 'driver'
            bundle.mkdir(); driver.mkdir()
            for name in DRIVERS:
                if (run / 'project' / name).is_file():
                    shutil.copy2(run / 'project' / name, driver / name)
            inventory(run / 'data')  # Strict input types; copytree preserves empty directories too.
            shutil.copytree(run / 'data', bundle / 'inputs')
            require(inventory(bundle / 'inputs') == inventory(run / 'data'), 'input copy metadata/content mismatch')
            for name, value in [('baseline-files.json', base_tree), ('project-files.json', project_tree), ('overlay-manifest.json', plan), ('retained-evidence.json', original), ('source-identities.json', identity), ('eligibility.json', gate)]:
                write(bundle / name, value)
            archive_overlay(run / 'project', project_tree, plan, bundle / 'overlay.zip')
            (bundle / 'RESTORE-PROJECT.md').write_text('''# Private project reconstruction\n\nValidate the checkpoint and bundle hashes first. Restore the immutable private baseline using source-identities.json / receiving-index and the current Library materialization skill. Never extract into the baseline.\n\nUse tests/native_run_compaction.py restore --baseline /absolute/verified/baseline --bundle /absolute/output/compaction --dest /absolute/new-project. The destination must not exist. This only reconstructs files; it never starts Godot. Full path/content SHA256/mode/mtime equality is required. Original data/user/logs remain at the run; the checkpoint does not claim to contain all user saves. Historical runner refuses any existing run root. Use a new run ID and fresh user directory for any future execution.\n\nThis pack/verify stage retains the original project and has no prune command. Incomplete process-reference inspection is recorded and cannot authorize deletion.\n''')
            files = {p.relative_to(bundle).as_posix(): digest(p) for p in sorted(bundle.rglob('*')) if p.is_file()}
            drivers = {p.name: digest(p) for p in driver.iterdir()}
            write(bundle / 'bundle-manifest.json', {'schema': 'native-run-compaction/1', 'run_id': run.name, 'files': files, 'driver_sha256': drivers, 'created_utc': stamp(), 'tool_sha256': digest(__file__)})
            require(inventory(run / 'project') == project_tree and inventory(baseline) == base_tree and retained(run) == original, 'source/evidence changed during pack')
            eligibility(run)
            load_bundle(bundle)
            sync_tree(tmp)
            publish_new_directory(driver, run / 'output/driver')
            publish_new_directory(bundle, run / 'output/compaction')
        require(retained(run) == original, 'retained evidence changed on publish')
    return {'status': 'PACKED', 'run': str(run), 'overlay_bytes': (run / 'output/compaction/overlay.zip').stat().st_size, 'bundle_sha256': digest(run / 'output/compaction/bundle-manifest.json'), 'original_project_retained': True}


def verify(run, baseline, proof_name="roundtrip-verification.json"):
    run, baseline = scope(run, baseline)
    safe_path(proof_name)
    require('/' not in proof_name and proof_name.startswith('roundtrip-verification') and proof_name.endswith('.json'), 'invalid proof name')
    with locked(run):
        gate = eligibility(run)
        bundle = run / 'output/compaction'
        require(not (bundle / proof_name).exists(), 'proof already exists; choose a new proof name')
        base_tree, project_tree, _ = load_bundle(bundle)
        original = read(bundle / 'retained-evidence.json')
        require(retained(run) == original and inventory(run / 'project') == project_tree and inventory(baseline) == base_tree, 'pre-verify source/evidence mismatch')
        sources(run, baseline, base_tree, project_tree)
        print('COMPACTION reconstructing complete project from baseline + overlay', flush=True)
        with tempfile.TemporaryDirectory(prefix='.native-roundtrip-', dir=run.parent) as tmp:
            reconstruct(baseline, bundle, Path(tmp) / 'project')
        require(inventory(run / 'project') == project_tree and inventory(baseline) == base_tree and retained(run) == original, 'post-verify source/evidence mismatch')
        last_gate = eligibility(run)
        proof = {'status': 'PASS', 'schema': 'native-run-roundtrip/1', 'run_id': run.name, 'verified_utc': stamp(), 'tool_sha256': digest(__file__),
                 'bundle_sha256': digest(bundle / 'bundle-manifest.json'), 'baseline_manifest_sha256': digest(bundle / 'baseline-files.json'), 'project_manifest_sha256': digest(bundle / 'project-files.json'), 'overlay_sha256': digest(bundle / 'overlay.zip'),
                 'full_path_sha256_mode_mtime_equality': True, 'files': sum(r['kind'] == 'file' for r in project_tree['entries']), 'directories': sum(r['kind'] == 'directory' for r in project_tree['entries']),
                 'source_project_unchanged': True, 'baseline_unchanged': True, 'original_output_data_user_unchanged': True,
                 'original_project_retained': True, 'prune_implemented': False, 'prune_eligible': False,
                 'process_checks': [gate['process_check'], last_gate['process_check']]}
        write(bundle / proof_name, proof)
    return proof


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('plan', 'pack', 'verify', 'restore'))
    parser.add_argument('--run', type=Path)
    parser.add_argument('--baseline', type=Path, default=BASE)
    parser.add_argument('--bundle', type=Path)
    parser.add_argument('--dest', type=Path)
    parser.add_argument('--proof-name', default='roundtrip-verification.json')
    args = parser.parse_args()
    if args.action == 'restore':
        require(args.bundle is not None and args.dest is not None, 'restore needs --bundle and --dest')
        tree = reconstruct(args.baseline, args.bundle, args.dest)
        result = {'status': 'RESTORED', 'entries': len(tree['entries']), 'dest': str(args.dest)}
    else:
        require(args.run is not None, '--run required')
        run, base = scope(args.run, args.baseline)
        if args.action == 'plan':
            result = {'status': 'METADATA_CANDIDATE', 'run': str(run), 'eligibility': eligibility(run), 'no_files_written': True}
        elif args.action == 'pack':
            result = pack(run, base)
        else:
            result = verify(run, base, args.proof_name)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
