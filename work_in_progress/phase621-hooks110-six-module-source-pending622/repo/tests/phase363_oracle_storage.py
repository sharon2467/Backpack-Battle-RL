"""Explicit-path oracle storage; never reconstructs a second project tree."""
from pathlib import Path, PurePosixPath
import contextlib
import fcntl
import hashlib
import json
import os
import shutil
import stat
import zipfile
import native_run_compaction as c

RESERVE = 4 * 1024**3
ATTEMPT = 1536 * 1024**2


def regular_target(path, absent=False):
    """Uniform mutable-file gate; never follow links or truncate an alias."""
    path=Path(path)
    if any(parent.is_symlink() for parent in path.parents): raise ValueError('linked mutable ancestor')
    try: value=path.lstat()
    except FileNotFoundError:
        if absent: return None
        raise ValueError('missing mutable regular target: '+str(path))
    if not stat.S_ISREG(value.st_mode) or value.st_nlink!=1 or stat.S_IMODE(value.st_mode)&0o7000:
        raise ValueError('mutable target must be regular+nlink1: '+str(path))
    return value


def atomic_image(path, raw, before):
    """Stage an exact image, then recheck preimage before the sole replace."""
    path=Path(path)
    current=regular_target(path,absent=before is None)
    if before is None:
        if current is not None: raise ValueError('new mutable target appeared')
    elif current is None or pin(path)!=before['identity'] or stat.S_IMODE(current.st_mode)!=before['mode'] or current.st_mtime_ns!=before['mtime_ns']:
        raise ValueError('mutable preimage changed before atomic image')
    temporary=path.with_name(path.name+'.phase363-next')
    if temporary.exists() or temporary.is_symlink(): raise ValueError('unfinished atomic image')
    with temporary.open('xb') as stream: stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    os.chmod(temporary,before['mode'] if before else 0o644)
    ns=before['mtime_ns'] if before else 0
    os.utime(temporary,ns=(ns,ns))
    current=regular_target(path,absent=before is None)
    if before is None:
        if current is not None: raise ValueError('new mutable target appeared before replace')
    elif pin(path)!=before['identity'] or stat.S_IMODE(current.st_mode)!=before['mode'] or current.st_mtime_ns!=before['mtime_ns']:
        raise ValueError('mutable preimage changed before replace')
    os.replace(temporary,path); sync(path.parent)
    regular_target(path)


def pin(path):
    p = Path(path)
    return dict(size=p.stat().st_size, sha256=c.digest(p))


def directory(path):
    path = Path(path).absolute()
    if not path.is_dir() or any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('existing unlinked directory required')
    return path


def member(root, name):
    root = directory(root)
    relative = PurePosixPath(name)
    if relative.is_absolute() or str(relative) != name or any(x in ('.', '..') for x in relative.parts):
        raise ValueError('safe canonical relative member')
    path = root.joinpath(*relative.parts)
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('symlink member/ancestor')
    return path


def write_new(path, value):
    path = Path(path)
    with path.open('xb') as stream:
        stream.write((json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n').encode())
        stream.flush(); os.fsync(stream.fileno())


def sync(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try: os.fsync(fd)
    finally: os.close(fd)


def read(path):
    return json.loads(Path(path).read_text())


def budget(pool, run_parent):
    pool, run_parent = directory(pool), directory(run_parent)
    if pool.stat().st_dev != run_parent.stat().st_dev:
        raise ValueError('same FS required for capture rename')
    free = shutil.disk_usage(run_parent).free
    if free < RESERVE + ATTEMPT:
        raise ValueError('4GiB reserve plus1536MiB attempt not available')
    return dict(reserve=RESERVE, attempt=ATTEMPT, free=free, required=RESERVE + ATTEMPT)


def map_recorded(path, relocations):
    path = Path(path)
    matches = [(Path(a), Path(b)) for a, b in relocations.items() if path == Path(a) or path.is_relative_to(Path(a))]
    if len(matches) > 1:
        raise ValueError('ambiguous approved relocation prefixes')
    return matches[0][1] / path.relative_to(matches[0][0]) if matches else path


def check_ready(pool, baseline, relocations):
    pool, baseline = directory(pool), directory(baseline)
    if set(p.name for p in pool.iterdir()) != {'.lock', 'state.json', 'project', 'data'}:
        raise ValueError('exact existing pool layout')
    state = read(member(pool, 'state.json'))
    if state.get('status') != 'ready':
        raise ValueError('existing READY only; preserve failed pool')
    previous = directory(map_recorded(state['run'], relocations))
    bundle = previous / 'output/compaction'
    if c.inventory(bundle) != state['bundle_inventory']:
        raise ValueError('old bundle physical inventory drift')
    base, project, plan = c.load_bundle(bundle)
    proof = read(bundle / 'pool-roundtrip.json')
    mode = proof.get('verification_mode')
    if mode is None:
        if proof.get('status') != 'PASS' or proof.get('full_path_sha256_mode_mtime_equality') is not True:
            raise ValueError('actual old materialized proof required')
    elif mode != 'logical-overlay-and-live-tree-equality/1' or proof.get('status') != 'PASS' or proof.get('physical_reconstruction') is not False:
        raise ValueError('unknown/new READY proof schema')
    if (map_recorded(proof['run'], relocations) != previous or map_recorded(proof['pool'], relocations) != pool
            or proof['bundle_sha256'] != c.digest(bundle / 'bundle-manifest.json')
            or proof['provenance_sha256'] != c.digest(previous / 'output/pool-provenance.json')):
        raise ValueError('actual prior proof/run/pool identities')
    if c.inventory(baseline) != base or c.inventory(pool / 'project') != project:
        raise ValueError('baseline/project full tree drift; no implicit public-variant exception')
    if c.inventory(pool / 'data') != read(bundle / 'staged-inputs.json'):
        raise ValueError('old staged data drift')
    if c.retained(previous) != read(bundle / 'retained-evidence.json') or c.inventory(previous / 'output/driver') != read(bundle / 'driver-files.json'):
        raise ValueError('prior evidence or drivers drift')
    c.process_check(pool)
    return previous


def state_write(pool, value):
    regular_target(pool/'state.json')
    path = pool / 'state.next.json'
    if path.exists() or path.is_symlink(): raise ValueError('unfinished pool state transaction')
    write_new(path, value); os.replace(path, pool / 'state.json'); sync(pool)


@contextlib.contextmanager
def lease(pool, baseline, runs_root, run_name, relocations):
    pool, baseline, runs_root = map(directory, (pool, baseline, runs_root))
    if PurePosixPath(run_name).name != run_name or run_name in ('.', '..'):
        raise ValueError('single new run name')
    run = runs_root / run_name
    if run.exists() or run.is_symlink(): raise ValueError('unique attempt must not exist')
    for a, b in ((pool, baseline), (pool, runs_root), (runs_root, baseline)):
        if a == b or a.is_relative_to(b) or b.is_relative_to(a): raise ValueError('disjoint paths')
    budget(pool, runs_root)
    lock_path = member(pool, '.lock')
    regular_target(lock_path)
    with lock_path.open('r+b') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        previous = check_ready(pool, baseline, relocations)
        state_write(pool, dict(status='busy', run=str(run), started_utc=c.stamp()))
        try:
            yield previous, run
        except BaseException as exc:
            state_write(pool, dict(status='failed', run=str(run), reason=repr(exc), utc=c.stamp()))
            raise


def reset_previous(project, baseline, previous, backup):
    project, baseline = directory(project), directory(baseline)
    report = read(previous / 'output/host_manifest.json')['audited_runtime_observation_patch']
    rows = report['patches']
    if not rows or len({r['path'] for r in rows}) != len(rows): raise ValueError('prior exact patch list')
    before = c.inventory(project)
    marker = project / '.native-random-observer-disposable'
    regular_target(marker)
    if marker.is_symlink() or marker.read_bytes() != b'disposable-observation-copy\n': raise ValueError('prior marker')
    for row in rows:
        target = member(project, row['path'])
        regular_target(target)
        if pin(target) != dict(size=row['after_size'], sha256=row['after_sha256']): raise ValueError('prior after bytes')
        if row['before_sha256'] is not None:
            original = member(baseline, row['path'])
            if pin(original) != dict(size=row['before_size'], sha256=row['before_sha256']): raise ValueError('prior before bytes')
        elif row['path'] != 'native_random_observer_sink_v7.gd':
            raise ValueError('unknown previous added source')
    backup = Path(backup)
    if backup.exists(): raise ValueError('prior patch backup must be new')
    backup.mkdir()
    for index, row in enumerate(rows):
        shutil.copy2(member(project,row['path']),backup/str(index))
        if pin(backup/str(index)) != pin(member(project,row['path'])): raise ValueError('old patch backup readback')
    shutil.copy2(marker,backup/'marker')
    write_new(backup/'inventory.json',dict(project=before,patch=report))
    c.sync_tree(backup)
    for row in rows:
        target = member(project, row['path'])
        info=regular_target(target)
        if row['before_sha256'] is None: target.unlink()
        else:
            original=member(baseline,row['path']); meta=original.stat()
            prior=dict(identity=pin(target),mode=stat.S_IMODE(info.st_mode),mtime_ns=info.st_mtime_ns)
            atomic_image(target,original.read_bytes(),prior)
            os.chmod(target,stat.S_IMODE(meta.st_mode)); os.utime(target,ns=(meta.st_mtime_ns,meta.st_mtime_ns))
    marker.unlink()
    return dict(before=before, restored=[r['path'] for r in rows], after=c.inventory(project))


def install(source_root, project, source_freeze, artifacts, backup):
    source_root, project = directory(source_root), directory(project)
    backup = Path(backup)
    if backup.exists(): raise ValueError('preimage backup must be new')
    todo = []
    for name, row in source_freeze['paths'].items():
        target = member(project, name)
        current=regular_target(target,absent=row['before'] is None)
        if row['before'] is None:
            if current is not None: raise ValueError('new source preimage unexpectedly exists')
        elif pin(target) != row['before']: raise ValueError('strict original source preimage')
        payload = member(source_root, row['after_path'])
        if pin(payload) != row['after']: raise ValueError('frozen after source drift')
        todo.append((name, target, payload))
    for name, payload in artifacts.items():
        target, payload = member(project, name), Path(payload)
        regular_target(target,absent=True)
        todo.append((name, target, payload))
    if len({n for n, _, _ in todo}) != len(todo): raise ValueError('overlapping source/artifact writes')
    backup.mkdir()
    journal = []
    for i, (name, target, payload) in enumerate(todo):
        old = None
        if target.exists():
            s = regular_target(target); old = dict(identity=pin(target), mode=stat.S_IMODE(s.st_mode), mtime_ns=s.st_mtime_ns)
            with (backup / str(i)).open('xb') as stream: stream.write(target.read_bytes()); stream.flush(); os.fsync(stream.fileno())
            if pin(backup / str(i)) != old['identity']: raise ValueError('preimage readback')
        journal.append(dict(path=name, backup=str(i) if old else None, before=old, after=pin(payload)))
    write_new(backup / 'preimages.json', journal); sync(backup)
    for row, (_, target, payload) in zip(journal, todo):
        raw = payload.read_bytes()
        atomic_image(target,raw,row['before'])
        if pin(target) != row['after']: raise ValueError('installed after bytes')
    sync(project)
    return journal


def archive_streaming(baseline, pool, run, before):
    baseline, pool, run = map(directory, (baseline, pool, run))
    if c.inventory(baseline) != before['baseline'] or c.inventory(pool / 'project') != before['project'] or c.inventory(pool / 'data') != before['staged']:
        raise ValueError('source tree/staged changed during capture')
    c.process_check(pool)
    bundle = run / 'output/compaction'
    if bundle.exists(): raise ValueError('new archive only')
    bundle.mkdir(); (bundle / 'inputs').mkdir()
    for path in (run / 'data').iterdir():
        if not path.is_file() or path.is_symlink(): raise ValueError('regular input only')
        shutil.copy2(path, bundle / 'inputs' / path.name)
    base, project = before['baseline'], before['project']
    plan = c.overlay_plan(base, project)
    c.archive_overlay(pool / 'project', project, plan, bundle / 'overlay.zip')
    c.validate_archive(bundle / 'overlay.zip', project, plan) # streams every ZIP member/CRC
    target, origins = c.index(project), c.index(base)
    with zipfile.ZipFile(bundle / 'overlay.zip') as archive:
        for name, row in target.items():
            if row['kind'] != 'file': continue
            stream = archive.open(name) if name in plan['content'] else member(baseline, name).open('rb')
            with stream:
                h = hashlib.sha256(); size = 0
                for block in iter(lambda: stream.read(1024 * 1024), b''): h.update(block); size += len(block)
            if dict(size=size, sha256=h.hexdigest()) != {k: row[k] for k in ('size', 'sha256')}:
                raise ValueError('logical overlay reconstructable byte identity')
    retained = c.retained(run)
    rows = {'baseline-files.json':base, 'project-files.json':project, 'staged-inputs.json':before['staged'],
            'overlay-manifest.json':plan, 'retained-evidence.json':retained,
            'driver-files.json':c.inventory(run / 'output/driver'),
            'source-identities.json':dict(baseline=base,project=project),
            'eligibility.json':dict(status='ORACLE_CAPTURE_ONLY_NOT_MODEL_ACCEPTANCE')}
    for name, value in rows.items(): write_new(bundle / name, value)
    (bundle / 'RESTORE-PROJECT.md').write_text('Logical overlay + live-tree equality. No second project materialized by this verifier. Use the separately audited restore tool for an authorized restoration.\n')
    drivers = {p.name:c.digest(p) for p in (run / 'output/driver').iterdir() if p.is_file()}
    files = {str(p.relative_to(bundle)):c.digest(p) for p in bundle.rglob('*') if p.is_file()}
    write_new(bundle / 'bundle-manifest.json', dict(schema='native-run-compaction/1',files=files,driver_sha256=drivers))
    if c.inventory(baseline) != base or c.inventory(pool / 'project') != project or c.retained(run) != retained:
        raise ValueError('source/evidence changed while streaming archive')
    proof = dict(status='PASS', verification_mode='logical-overlay-and-live-tree-equality/1', physical_reconstruction=False,
                 run=str(run), pool=str(pool), bundle_sha256=c.digest(bundle / 'bundle-manifest.json'),
                 provenance_sha256=c.digest(run / 'output/pool-provenance.json'), live_tree_byte_mode_mtime_equality=True)
    write_new(bundle / 'pool-roundtrip.json', proof)
    c.sync_tree(bundle)
    state_write(pool, dict(status='ready', run=str(run), bundle_inventory=c.inventory(bundle)))
    return proof
