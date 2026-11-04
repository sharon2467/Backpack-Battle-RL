"""One fixed offline joint Tape run; no EXPECTED, oracle, retry or seed fallback."""
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

ROOT = Path(__file__).resolve().parents[1]
CASE = 'NATIVE-028-KING-BASIC-A'
PROFILE = 'pure-combat-king-basic-A-captured/1'
SCHEMA = 'native-v8-pure-combat-runtime-input/king-basic-1'
FREEZE = {'path': 'data/phase476-joint-condition-repair/candidate-source-freeze.json', 'size': 5234, 'sha256': 'ebd99ad8fbe50247b520a005314d6b0714895d7014081c199cba03791f11bc09'}
INPUT_SOURCE = {'path': 'data/phase476-joint-condition-repair/input-source-owner.json', 'size': 2175, 'sha256': '04d81d52a2677a95a4718b87cea5d9935a8c8c4618128cac578ff151ef87dda5'}
INPUT_ABI = {'path': 'data/phase470-joint-input-source/abi.json', 'size': 738,
             'sha256': '15d5671b349230ddcc04e48fd7dd3c98d1d4de2212de05d7c5cf73c7dc7e9727'}
CONTRACT = {'path': 'data/phase466-captured-joint-bridge-design/comparison-contract.json', 'size': 4636,
            'sha256': '71c681047140d3bc13d91b24be590dcb598cb3454edac394288c64e01cb3ecef'}


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


def path_of(value):
    if type(value) is not str or not value or '..' in Path(value).parts:
        raise ValueError('explicit canonical descriptor path')
    path = Path(value)
    path = path if path.is_absolute() else ROOT / path
    if path.absolute() != path or not path.is_relative_to(ROOT):
        raise ValueError('fixed repository Source/INPUT descriptor path')
    return path


def read_descriptor(row):
    if type(row) is not dict or set(row) != {'path', 'size', 'sha256'}:
        raise ValueError('closed actual descriptor required')
    if type(row['size']) is not int or row['size'] <= 0 or type(row['sha256']) is not str or len(row['sha256']) != 64 or any(c not in '0123456789abcdef' for c in row['sha256']):
        raise ValueError('strict actual descriptor types')
    return pin(path_of(row['path']), {key: row[key] for key in ('size', 'sha256')})[0]


def write_json(path, value):
    raw = (json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':')) + '\n').encode()
    with path.open('xb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    return dict(size=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def validate_request(request):
    expected = {'schema', 'case_id', 'launcher', 'candidate_freeze', 'input_source_owner', 'input_abi',
                'input_bundle', 'input_acceptance', 'candidate_acceptance', 'business_closure',
                'comparison_contract', 'root_model_authorized'}
    if (type(request) is not dict or set(request) != expected or request['schema'] != 'phase474-root-joint-model-request/1'
            or request['case_id'] != CASE or request['root_model_authorized'] is not True):
        raise ValueError('closed fixed Root execution request/explicit authorization required')
    if (request['candidate_freeze'] != FREEZE or request['input_source_owner'] != INPUT_SOURCE
            or request['input_abi'] != INPUT_ABI or request['comparison_contract'] != CONTRACT
            or path_of(request['launcher']['path']) != Path(__file__).resolve()):
        raise ValueError('fixed launcher/candidate/INPUT Source/contract tuple')
    provenance = {name: read_descriptor(request[name]) for name in expected - {'schema', 'case_id', 'root_model_authorized'}}
    # Root accepts the real independent prerequisites before authorizing this request.
    # Their exact bytes are provenance, not a caller boolean gameplay certificate.
    bundle = strict_json(provenance['input_bundle'])
    if (type(bundle) is not dict or set(bundle) != {'schema', 'fixture', 'runtime', 'draws', 'synthetic_seed'}
            or bundle['schema'] != 'native-v8-input-only/1' or bundle['synthetic_seed'] is not None):
        raise ValueError('exact INPUT-only envelope; no synthetic seed')
    data = bundle['runtime']
    if (data.get('schema') != SCHEMA or data.get('profile_id') != PROFILE or data.get('mode') != 'genuine'
            or len(data['initial_items']) != 26 or len(data['timer_initial']) != 33
            or len(data['processing_nodes']) != 65 or len(data['nodes']) != 64
            or type(bundle['draws']) is not list or not bundle['draws']
            or type(data['frame_clock']['passes']) is not list or not data['frame_clock']['passes']):
        raise ValueError('fixed joint26/33/65/64/full actual Tape and clock')
    return bundle, strict_json(provenance['candidate_freeze']), provenance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    parser.add_argument('--config-sha256', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    launcher_path = Path(__file__).resolve()
    config_path = path_of(args.config)
    config_raw, config_pin = pin(config_path)
    if config_pin['sha256'] != args.config_sha256:
        raise ValueError('Root request SHA mismatch')
    request = strict_json(config_raw)
    bundle, freeze, provenance = validate_request(request)
    source_rows = freeze['files']
    if len(source_rows) != 15:
        raise ValueError('exact15 candidate Source files required')
    sources = {}; staged = ROOT / 'data/phase476-joint-condition-repair/staged'
    for row in source_rows:
        relative = Path(row['relative']); path = path_of(row['path'])
        if relative.is_absolute() or '..' in relative.parts or staged / relative != path or str(path) in sources:
            raise ValueError('one exact471 candidate root required')
        _, identity = pin(path, {key: row[key] for key in ('size', 'sha256')})
        sources[str(path)] = identity
    if set(str(p) for p in staged.rglob('*.py')) != set(sources):
        raise ValueError('unexpected candidate Python Source file')
    if any(name == prefix or name.startswith(prefix + '.') for name in sys.modules
           for prefix in ('native_replay_v8', 'native_replay_v7', 'original_rng', 'godot_pcg_integer')):
        raise ValueError('fresh single candidate import required')
    output = path_of(args.output)
    if (output.parent != ROOT / 'data' or not output.name.startswith('phase476-') or output.exists()
            or any(p.is_symlink() for p in output.parents)):
        raise ValueError('new ordinary phase474 output directory required')
    output.mkdir(mode=0o700)
    before = dict(schema='phase474-joint-before/1', case_id=CASE, launcher=request['launcher'],
        execution_request=dict(path=str(config_path), **config_pin), source_freeze=FREEZE,
        sources=sources, input=request['input_bundle'], input_abi=INPUT_ABI, comparison_contract=CONTRACT,
        prerequisite_descriptors={k: request[k] for k in ('input_acceptance','candidate_acceptance','business_closure')},
        prerequisite_role='External Root-reviewed provenance; launcher does not manufacture their business proof.',
        expected_reads=0, new_original_capture=0, utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    owned = {'before.json': write_json(output / 'before.json', before)}
    reads = []
    allowed_sources = set(sources) | {str(launcher_path), str(config_path), str(path_of(request['input_bundle']['path']))}
    python_roots = [Path(sys.base_prefix).resolve(), Path(sys.prefix).resolve(), Path(os.__file__).resolve().parent]
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
            path = Path(os.fsdecode(values[0])).absolute(); flags = values[2] or 0
            writing = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
            if writing:
                if not within(path, output):
                    raise RuntimeError('model write outside output denied: ' + str(path))
            elif within(path, staged) and '__pycache__' in path.parts and not path.exists():
                reads.append(str(path))
            elif str(path) not in allowed_sources and not within(path, output) and not any(within(path, p) for p in python_roots):
                raise RuntimeError('model external read denied: ' + str(path))
            else:
                reads.append(str(path))
    sys.dont_write_bytecode = True
    sys.pycache_prefix = str(output / 'unused-bytecode-cache')
    sys.addaudithook(audit)
    sys.path.insert(0, str(staged))
    start = time.monotonic(); engine = tape = None
    calls = dict(candidate_import_attempts=0, construct_attempts=0, full_run_attempts=0)
    status = 'FAILED'; source_after = {}; input_after = None
    try:
        calls['candidate_import_attempts'] += 1
        module = importlib.import_module('native_replay_v8.engine')
        randomness = sys.modules['native_replay_v8.randomness']
        if (Path(module.__file__).absolute() != staged / 'native_replay_v8/engine.py'
                or Path(randomness.__file__).absolute() != staged / 'native_replay_v8/randomness.py'):
            raise ValueError('imported candidate identity mismatch')
        tape = randomness.TapeRandom(bundle['draws'])
        calls['construct_attempts'] += 1
        engine = module.CombatEngine(bundle['fixture'], tape, bundle['runtime'])
        calls['full_run_attempts'] += 1
        result = engine.run()
        tape.assert_consumed()
        owned['model-output.json'] = write_json(output / 'model-output.json', result)
        for name, identity in sources.items():
            _, source_after[name] = pin(Path(name), identity)
        _, input_after = pin(path_of(request['input_bundle']['path']), {key: request['input_bundle'][key] for key in ('size', 'sha256')})
        pin(config_path, config_pin)
        pin(launcher_path, {key: request['launcher'][key] for key in ('size','sha256')})
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
    report = dict(schema='phase474-joint-execution/1', status=status, case_id=CASE, calls=calls,
        elapsed_wall_seconds=time.monotonic() - start, candidate_source=str(staged),
        tape_position=None if tape is None else tape.position, tape_records=len(bundle['draws']),
        full_clock_passes=len(bundle['runtime']['frame_clock']['passes']), source_after=source_after, input_after=input_after,
        candidate_execution_file_reads=reads, expected_reads=0, new_original_capture=0, comparator_calls=0,
        King_admitted=False, formal_support=75)
    owned['execution.json'] = write_json(output / 'execution.json', report)
    write_json(output / 'output-seal.json', dict(schema='phase474-output-seal/1', status=status, files=owned))
    print(json.dumps({key: report[key] for key in ('status', 'calls', 'elapsed_wall_seconds', 'tape_position')}))
    return 0 if status == 'ACTUAL_OUTPUT_SEALED_NOT_COMPARED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
