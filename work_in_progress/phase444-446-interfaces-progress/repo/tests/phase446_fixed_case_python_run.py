"""One offline model run; no EXPECTED reader, oracle, seed fallback or retry."""
import argparse
import datetime
import hashlib
import importlib
import json
import os
from pathlib import Path
import stat
import sys
import time
import traceback

BUNDLE = 'data/phase441-fixed-A-input-first-001/input-bundle.json'
BUNDLE_SHA = 'c87525f35adf8fa3793cc5d1440dff420dc55f3a24c77e520766b01e8963ae2c'


def strict_json(raw):
    def pairs(items):
        obj = {}
        for key, value in items:
            if key in obj:
                raise ValueError('duplicate JSON key: ' + key)
            obj[key] = value
        return obj
    def invalid(value):
        raise ValueError('nonfinite JSON: ' + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)


def pin(path, expected=None):
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
        raise ValueError('ordinary single-link file required: ' + str(path))
    if any(p.is_symlink() for p in path.parents):
        raise ValueError('symlink ancestor: ' + str(path))
    raw = path.read_bytes()
    after = path.stat()
    if (before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_ino, after.st_size, after.st_mtime_ns):
        raise ValueError('file changed while read: ' + str(path))
    identity = dict(size=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    if expected is not None and identity != expected:
        raise ValueError('file pin mismatch: ' + str(path))
    return raw, identity


def write_json(path, value):
    raw = (json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':')) + '\n').encode()
    with path.open('xb') as stream:
        stream.write(raw)
    return dict(size=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate-freeze', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    launcher_path = Path(__file__).resolve()
    _, launcher_pin = pin(launcher_path)
    freeze = Path(args.candidate_freeze).absolute()
    freeze.relative_to(root)
    freeze_raw, freeze_pin = pin(freeze)
    source_rows = strict_json(freeze_raw)['files']
    if len(source_rows) != 15:
        raise ValueError('exact15 candidate Source files required')
    sources = {}
    staged = None
    for row in source_rows:
        rel = Path(row['path'])
        if rel.is_absolute() or '..' in rel.parts:
            raise ValueError('candidate path must be repo-relative')
        path = root / rel
        relative = Path(row['relative'])
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('candidate package-relative path')
        package_root = path
        for _ in relative.parts:
            package_root = package_root.parent
        if staged is None:
            staged = package_root
        if package_root != staged or staged / relative != path or str(path) in sources:
            raise ValueError('one exact candidate root required')
        _, value = pin(path, {key: row[key] for key in ('size', 'sha256')})
        sources[str(path)] = value
    if set(str(p) for p in staged.rglob('*.py')) != set(sources):
        raise ValueError('unexpected candidate Python Source file')
    bundle_raw, bundle_pin = pin(root / BUNDLE, dict(size=539534, sha256=BUNDLE_SHA))
    bundle = strict_json(bundle_raw)
    if set(bundle) != {'schema', 'fixture', 'runtime', 'draws', 'synthetic_seed'} or bundle['synthetic_seed'] is not None:
        raise ValueError('exact genuine bundle envelope; no synthetic seed')
    if len(bundle['draws']) != 365:
        raise ValueError('all365 original primitive records required')
    output = Path(args.output).absolute()
    if output.exists() or any(p.is_symlink() for p in output.parents):
        raise ValueError('new ordinary output directory required')
    output.mkdir(parents=True)
    before = dict(schema='phase446-fixed-case-before/1', launcher=dict(path=str(launcher_path), **launcher_pin),
                  source_freeze=dict(path=str(freeze), **freeze_pin),
                  sources=sources, input=dict(path=BUNDLE, **bundle_pin),
                  expected_reads=0, new_original_capture=0, utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    owned = {'before.json': write_json(output / 'before.json', before)}
    reads = []
    allowed_sources = set(sources) | {str(launcher_path)}
    python_roots = [Path(sys.base_prefix).resolve(), Path(sys.prefix).resolve()]
    stdlib = Path(os.__file__).resolve().parent
    python_roots.append(stdlib)
    def within(path, parent):
        try:
            path.relative_to(parent)
            return True
        except ValueError:
            return False
    def audit(event, values):
        if event.startswith(('subprocess.', 'socket.')) or event in ('os.system', 'os.exec', 'os.spawn', 'os.fork', 'os.posix_spawn'):
            raise RuntimeError('model subprocess/network denied: ' + event)
        if event == 'open' and isinstance(values[0], (str, bytes, os.PathLike)):
            path = Path(os.fsdecode(values[0])).absolute()
            flags = values[2] or 0
            writing = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
            if writing:
                if not within(path, output):
                    raise RuntimeError('model write outside output denied: ' + str(path))
            elif (within(path, staged) and '__pycache__' in path.parts and not path.exists()):
                # Importlib probes an absent cache even with bytecode writes off.
                # Existing unpinned bytecode is deliberately never accepted.
                reads.append(str(path))
            elif str(path) not in allowed_sources and not within(path, output) and not any(within(path, p) for p in python_roots):
                raise RuntimeError('model external read denied: ' + str(path))
            else:
                reads.append(str(path))
    sys.dont_write_bytecode = True
    # Use a never-populated cache namespace; no previous candidate bytecode may run.
    sys.pycache_prefix = str(output / 'unused-bytecode-cache')
    sys.addaudithook(audit)
    sys.path.insert(0, str(staged))
    start = time.monotonic()
    engine = tape = None
    calls = dict(construct_attempts=0, full_run_attempts=0)
    status = 'FAILED'
    try:
        module = importlib.import_module('native_replay_v8.engine')
        randomness = importlib.import_module('native_replay_v8.randomness')
        if Path(module.__file__).absolute() != staged / 'native_replay_v8/engine.py':
            raise ValueError('imported candidate identity mismatch')
        tape = randomness.TapeRandom(bundle['draws'])
        calls['construct_attempts'] += 1
        engine = module.CombatEngine(bundle['fixture'], tape, bundle['runtime'])
        calls['full_run_attempts'] += 1
        result = engine.run()
        tape.assert_consumed()
        for name, identity in sources.items():
            pin(Path(name), identity)
        owned['model-output.json'] = write_json(output / 'model-output.json', result)
        status = 'ACTUAL_OUTPUT_SEALED_NOT_COMPARED'
    except BaseException as exc:
        failure = dict(type=type(exc).__name__, message=str(exc), traceback=traceback.format_exc())
        if engine is not None:
            failure['partial'] = dict(events=engine.events, frame=engine.frame, elapsed=engine.elapsed,
                                      prepared=engine.prepared, activated=engine.activated, ended=engine.ended,
                                      runtime_trace=engine.runtime_trace, schedule_trace=engine.schedule_trace,
                                      pure_api_trace=engine.pure_api_trace, pure_snapshots=engine.pure_snapshots)
        if tape is not None:
            failure['tape'] = dict(position=tape.position, records=len(tape.records), audit=tape.audit)
        owned['failure.json'] = write_json(output / 'failure.json', failure)
    report = dict(schema='phase446-fixed-case-execution/1', status=status, calls=calls,
                  elapsed_wall_seconds=time.monotonic() - start, candidate_source=str(staged),
                  tape_position=None if tape is None else tape.position, tape_records=365,
                  candidate_execution_file_reads=reads, expected_reads=0, new_original_capture=0,
                  King_admitted=False, formal_support=75)
    owned['execution.json'] = write_json(output / 'execution.json', report)
    write_json(output / 'output-seal.json', dict(schema='phase446-output-seal/1', status=status, files=owned))
    print(json.dumps({key: report[key] for key in ('status', 'calls', 'elapsed_wall_seconds', 'tape_position')}))
    return 0 if status == 'ACTUAL_OUTPUT_SEALED_NOT_COMPARED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
