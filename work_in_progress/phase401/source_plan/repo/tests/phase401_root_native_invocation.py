"""One-shot Root plan/execute wrapper for the frozen391 fixed native attempt06."""
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
D = R / 'data/phase401-root-native-attempt06'


def verified(row):
    p = R / row['path']
    assert not Path(row['path']).is_absolute()
    assert all(x not in ('', '.', '..') for x in row['path'].split('/'))
    assert p.resolve() == p.absolute()
    info = p.lstat()
    assert stat.S_ISREG(info.st_mode) and info.st_nlink == 1
    raw = p.read_bytes()
    assert len(raw) == row['size'] and hashlib.sha256(raw).hexdigest() == row['sha256']
    return raw


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['plan', 'execute'])
    parser.add_argument('--config-size', type=int, required=True)
    parser.add_argument('--config-sha256', required=True)
    parser.add_argument('--release-size', type=int)
    parser.add_argument('--release-sha256')
    args = parser.parse_args()
    row = dict(path=str((D / 'oracle-acceptance.json').relative_to(R)),
               size=args.config_size, sha256=args.config_sha256)
    config = json.loads(verified(row))
    freeze = json.loads(verified(config['source_freeze']))
    owner = json.loads(verified(config['source_owner']))
    for leaf in freeze['files'] + owner['files']:
        verified(leaf)
    for review in config['reviews']:
        verified(review['receipt'])
        for leaf in json.loads(verified(review['owner']))['files']:
            verified(leaf)
    if args.mode == 'execute':
        release = json.loads(verified(dict(
            path=str((D / 'plan-reviewed-and-execute-release.json').relative_to(R)),
            size=args.release_size, sha256=args.release_sha256)))
        assert release['config'] == row and release['execute_calls_allowed'] == 1
        assert release['automatic_retry'] is False
        plan = json.loads((D / 'plan-invocation.json').read_text())
        assert plan['returncode'] == 0
    command = [sys.executable, str(R / 'tests/phase391_oracle_host.py'),
        '--source-root', str(R), '--task-root', '/workspace/godotsteam-startup-20261013',
        '--baseline', '/workspace/godotsteam-startup-20261013/baseline/Backpack Battles',
        '--pool', '/workspace/native-combat-20261013/pool',
        '--runs-root', '/workspace/native-combat-20261013/runs',
        '--config', row['path'], '--config-size', str(row['size']),
        '--config-sha256', row['sha256'], '--' + args.mode]
    invocation = D / (args.mode + '-invocation.json')
    assert not invocation.exists()
    save(D / (args.mode + '-started.json'), dict(args=command, config=row,
         mode=args.mode, automatic_retry=False, models=0, inputbuilds=0))
    env = os.environ.copy()
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    started = time.monotonic()
    try:
        result = subprocess.run(command, cwd=R, env=env, capture_output=True,
                                timeout=120 if args.mode == 'plan' else 650)
    except subprocess.TimeoutExpired as exc:
        (D / (args.mode + '.stdout')).write_bytes(exc.stdout or b'')
        (D / (args.mode + '.stderr')).write_bytes(exc.stderr or b'')
        save(invocation, dict(mode=args.mode, args=command, timeout=True,
             elapsed_seconds=time.monotonic() - started, error=repr(exc),
             automatic_retry=False, models=0, inputbuilds=0))
        raise
    (D / (args.mode + '.stdout')).write_bytes(result.stdout)
    (D / (args.mode + '.stderr')).write_bytes(result.stderr)
    record = dict(mode=args.mode, args=command, returncode=result.returncode,
        elapsed_seconds=time.monotonic() - started, host_invocations=1,
        timeout=False, models=0, inputbuilds=0, expected_comparison=0,
        automatic_retry=False)
    save(invocation, record)
    print(json.dumps(record, indent=2))
    if result.returncode:
        print(result.stderr.decode(errors='replace')[-4000:])
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
