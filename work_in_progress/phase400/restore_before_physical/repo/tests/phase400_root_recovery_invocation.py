"""One-shot Root wrapper around the independently reviewed398 recovery CLI."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
import time

R = Path(__file__).resolve().parents[1]
D = R / 'data/phase400-root-attempt05-complete-restore'


def verified(row):
    rel = row['path']
    assert type(rel) is str and not Path(rel).is_absolute()
    assert all(x not in ('', '.', '..') for x in rel.split('/'))
    p = R / rel
    assert p.resolve() == p.absolute()
    info = p.lstat()
    assert stat.S_ISREG(info.st_mode) and info.st_nlink == 1
    raw = p.read_bytes()
    assert type(row['size']) is int and len(raw) == row['size']
    assert hashlib.sha256(raw).hexdigest() == row['sha256'], rel
    return raw


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['restore', 'commit_ready'])
    parser.add_argument('--config-size', required=True, type=int)
    parser.add_argument('--config-sha256', required=True)
    args = parser.parse_args()
    config_path = D / (args.action.replace('_', '-') + '-authorization.json')
    row = dict(path=str(config_path.relative_to(R)), size=args.config_size,
               sha256=args.config_sha256)
    invocation = D / (args.action.replace('_', '-') + '-invocation.json')
    marker = D / (args.action.replace('_', '-') + '-started.json')
    assert not invocation.exists() and not marker.exists(), 'one-shot action already started'
    config = json.loads(verified(row))
    assert config['schema'] == 'phase398-root-pool-recovery/1'
    assert config['action'] == args.action
    assert config['root_' + args.action + '_authorized'] is True
    for key in ['native_allowed', 'models_allowed', 'projection_allowed']:
        assert type(config[key]) is int and config[key] == 0
    freeze = json.loads(verified(config['source_freeze']))
    owner = json.loads(verified(config['source_owner']))
    for leaf in owner['files']:
        verified(leaf)
    for leaf in freeze['files']:
        verified(leaf)
    for leaf in freeze['import_closure']:
        verified(leaf)
    for review in config['reviews']:
        result = json.loads(verified(review['receipt']))
        actual_owner = json.loads(verified(review['owner']))
        for leaf in actual_owner['files']:
            verified(leaf)
        assert result['status'] == 'INDEPENDENT399_ATTEMPT05_COMPLETE_RECOVERY_SOURCE_ACCEPTED_ROOT_PENDING'
        assert result['source_freeze'] == config['source_freeze']
    cli = R / 'tests/phase398_pool_recovery.py'
    assert any(x['path'] == str(cli.relative_to(R)) for x in freeze['import_closure'])
    roots = config['roots']
    command = [sys.executable, str(cli), '--source-root', str(R)]
    for key in ['pool', 'baseline', 'failed_run', 'previous_run']:
        command += ['--' + key.replace('_', '-'), roots[key]]
    command += ['--config', row['path'], '--config-size', str(row['size']),
                '--config-sha256', row['sha256'], '--action', args.action]
    if args.action == 'restore':
        command += ['--output', str(D / 'actual-restore')]
    save(marker, dict(action=args.action, args=command, config=row,
                      native=0, models=0, automatic_retry=False))
    started = time.monotonic()
    env = os.environ.copy()
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    try:
        completed = subprocess.run(command, cwd=R, env=env, capture_output=True, timeout=180)
    except subprocess.TimeoutExpired as exc:
        (D / (args.action + '.stdout')).write_bytes(exc.stdout or b'')
        (D / (args.action + '.stderr')).write_bytes(exc.stderr or b'')
        save(invocation, dict(action=args.action, args=command,
             elapsed_seconds=time.monotonic() - started, timeout=True,
             error=repr(exc), native=0, models=0, automatic_retry=False))
        raise
    (D / (args.action + '.stdout')).write_bytes(completed.stdout)
    (D / (args.action + '.stderr')).write_bytes(completed.stderr)
    result = dict(action=args.action, args=command, returncode=completed.returncode,
                  elapsed_seconds=time.monotonic() - started, timeout=False,
                  recover_calls=1, native=0, models=0, automatic_retry=False)
    save(invocation, result)
    print(json.dumps(result, indent=2))
    if completed.returncode:
        print(completed.stderr.decode(errors='replace')[-4000:])
    raise SystemExit(completed.returncode)


if __name__ == '__main__':
    main()
