"""Independent single real408 CLI launch under the actual Root release."""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import time

ROOT = Path('/workspace/python-original-engine/repo')
OUT = ROOT / 'data/phase411-independent-initial-audit-launcher'
AUDIT_OUT = ROOT / 'data/phase408-initial-audit-first-001'
RELEASE = dict(path='data/phase411-root-initial-audit-release/input-audit-release.json',
               size=3529, sha256='8f5d6386019447576ae04a9457a489bfa0a6a6ae416c23d05eb99ad49097e193')
PINS = {
    'source_owner': dict(path='data/phase408-initial-audit-source/source-owner.json', size=16495,
                         sha256='c188422bd9dfe6d6365465204410f27f7c8ed9d8798afe21b8220ca09236dc88'),
    'source_freeze': dict(path='data/phase408-initial-audit-source/source-freeze.json', size=29684,
                          sha256='38f29ec7829b64805cd5c8cbe09caf59a32d11f75032d29948990878e10eeab8'),
    'source_review': dict(path='data/phase410-independent408-source-review/review.json', size=7423,
                          sha256='094215f7a342e18a378dd95fa82bb303544bafaed3c44a66500773ba3e8690a7'),
    'source_review_owner': dict(path='data/phase410-independent408-source-review/owned-files.json', size=4233,
                                sha256='e5d2a915c95253ebe726c3f5635443cf83824d9bd2af997aa143bf4e342198d6'),
}
assert not os.path.lexists(OUT)
OUT.mkdir()
reads = []
child_invocations = 0


def identity(info):
    return [info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns]


def metadata(path):
    assert path.is_absolute() and path.resolve(strict=True) == path
    assert not any(p.is_symlink() for p in (path, *path.parents))
    info = path.lstat()
    assert stat.S_ISREG(info.st_mode) and info.st_nlink == 1
    return identity(info)


def read(row):
    path = Path(row['path']) if Path(row['path']).is_absolute() else ROOT / row['path']
    before = metadata(path)
    assert before[4] == row['size']
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        assert identity(os.fstat(fd)) == before
        chunks = []
        remaining = row['size'] + 1
        while remaining:
            chunk = os.read(fd, remaining)
            if chunk == b'':
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        raw = b''.join(chunks)
        assert identity(os.fstat(fd)) == before
    finally:
        os.close(fd)
    assert metadata(path) == before and len(raw) == row['size']
    assert hashlib.sha256(raw).hexdigest() == row['sha256']
    reads.append(dict(**row, identity=before))
    return raw


def descriptor(name):
    path = ROOT / name
    before = metadata(path)
    # New launcher-owned files, outside capture; pin before owner sealing.
    raw = path.read_bytes()
    assert metadata(path) == before
    return dict(path=name, size=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def save(name, value):
    raw = (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()
    with (OUT / name).open('xb') as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())


started = time.monotonic()
try:
    assert sys.version_info[:2] == (3, 12)
    assert not os.path.lexists(AUDIT_OUT)
    release = json.loads(read(RELEASE))
    assert release['schema'] == 'root408-lawful12-initial-audit/1'
    assert release['action'] == 'initial_presence_source_chain_audit' and release['authorized'] is True
    assert all(type(value) is int and value == 0 for value in release['permissions'].values())
    assert release['output_directory'] == str(AUDIT_OUT.relative_to(ROOT))
    for key, pin in PINS.items():
        assert release[key] == pin
    owner = json.loads(read(PINS['source_owner']))
    assert len(owner['files']) == 83
    for row in owner['files']:
        read(row)
    source_ledger = list(reads)
    freeze = json.loads(read(PINS['source_freeze']))
    assert freeze['module'] == dict(path='tests/phase408_initial_source_audit.py', size=74685,
        sha256='c572cdbb35f44a3e696b0fa5ab3df539e9e985c5d88770d73e1f3bb9afe6977d')
    review = json.loads(read(PINS['source_review']))
    assert review['status'] == 'INDEPENDENT409_STDLIB_INITIAL_AUDIT_SOURCE_ACCEPTED_ROOT_PENDING'
    assert review['source_owner'] == PINS['source_owner'] and review['source_freeze'] == PINS['source_freeze']
    review_owner = json.loads(read(PINS['source_review_owner']))
    assert len(review_owner['files']) == 21
    for row in review_owner['files']:
        read(row)
    accepted_name = 'data/phase411-root-initial-audit-release/source-accepted.json'
    accepted_pin = descriptor(accepted_name)
    accepted = json.loads(read(accepted_pin))
    assert accepted['status'] == 'ROOT_408_SOURCE_ACCEPTED_FOR_ONE_INDEPENDENT_INITIAL_PRESENCE_AUDIT'
    assert accepted['review'] == PINS['source_review'] and accepted['review_owner'] == PINS['source_review_owner']
    assert accepted['formal75_currently_accepted'] is True and accepted['King_admitted'] is False
    assert len(release['input_files']) == 12
    before_inputs = {}
    for name, pin in release['input_files'].items():
        path = Path(release['input_directory']) / name
        before_inputs[str(path)] = metadata(path)
        assert before_inputs[str(path)][4] == pin['size']
    assert not os.path.lexists(AUDIT_OUT)
    args = [sys.executable, '-B', 'tests/phase408_initial_source_audit.py',
            '--source-root', str(ROOT), '--release', RELEASE['path'],
            '--release-size', str(RELEASE['size']), '--release-sha256', RELEASE['sha256']]
    save('args.json', dict(args=args, cwd=str(ROOT), environment_override={'PYTHONDONTWRITEBYTECODE': '1'},
        timeout_seconds=50, outer_timeout_seconds=60, invocations=1, automatic_retry=False,
        genuine_release=RELEASE, source_acceptance=accepted_pin,
        interpreter_version=sys.version, output_previously_absent=True,
        setup_boundary='trusted Python3.12 stdlib initialization allowed before original install_io_guard; no exhaustive startup event trace or preload claim',
        forbidden='nonlawful capture/event/history/final/postcleanup/logs; old engine/schema/Tape/361/optional391; model/inputbuild/native'))
    save('source-preflight.json', dict(status='PASS', source_owner=PINS['source_owner'],
        source_owner_leaf_count=83, source_owner_leaf_bytes=sum(row['size'] for row in owner['files']),
        phase410_owned_leaves=21, reads=reads, preflight_elapsed_seconds=time.monotonic()-started))
    save('input-metadata-before.json', dict(content_reads=0, identities=before_inputs))
    preparation_names = ['docs/phase411_independent_first_initial_audit_spec.md',
        'tests/phase411_launch_first_initial_audit.py', 'tests/phase411_verify_first_initial_audit.py']
    preparation_names += [str((OUT / name).relative_to(ROOT)) for name in
                          ('args.json', 'source-preflight.json', 'input-metadata-before.json')]
    rows = [descriptor(name) for name in preparation_names]
    save('preparation-owner.json', dict(schema='independent411-first-audit-preparation-owner/1',
        files=rows, no_more_writes=True, sealed_before_child=True))
    print(json.dumps(dict(stage='PREFLIGHT_SEALED_STARTING_ONLY_CHILD', source_leaves=83)), flush=True)
    child_started = time.monotonic()
    child_invocations = 1
    try:
        child = subprocess.run(args, cwd=ROOT, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'),
                               capture_output=True, timeout=50)
        stdout, stderr = child.stdout, child.stderr
        receipt = dict(status='CHILD_EXITED', child_exit_code=child.returncode, timed_out=False)
    except subprocess.TimeoutExpired as exc:
        stdout, stderr = exc.stdout or b'', exc.stderr or b''
        receipt = dict(status='FIRST_ACTUAL_AUDIT_TIMEOUT_STOP', child_exit_code=None, timed_out=True)
    for name, raw in (('stdout.txt', stdout), ('stderr.txt', stderr)):
        with (OUT / name).open('xb') as handle:
            handle.write(raw)
    receipt.update(child_elapsed_seconds=time.monotonic()-child_started,
        total_launcher_elapsed_seconds=time.monotonic()-started, child_invocations=1,
        automatic_retry=False, timeout_seconds=50,
        process_scope='one direct Python child waited; no proc inspection; source forbids subprocess/native spawn; no global process-absence claim')
    save('exit.json', receipt)
    after_inputs = {name: metadata(Path(name)) for name in before_inputs}
    save('input-metadata-after.json', dict(content_reads=0, identities=after_inputs,
        matches_before=after_inputs == before_inputs))
    print(json.dumps(receipt), flush=True)
except BaseException as exc:
    save('launcher-first-error.json', dict(type=type(exc).__name__, message=str(exc),
        child_invocations=child_invocations, automatic_retry=False, preserve_and_stop=True))
    raise
