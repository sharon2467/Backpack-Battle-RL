"""One frozen, synthetic-only phase463 helper batch; no observer or model run."""
import hashlib
import json
from pathlib import Path
import signal
import sys
import time
import traceback
import types

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/phase463-independent-helper-source'
OUTPUT = ROOT / 'data/phase463-independent-helpers-first-001'


def pin(path):
    data = path.read_bytes()
    return {'path': str(path.relative_to(ROOT)), 'size': len(data),
            'sha256': hashlib.sha256(data).hexdigest()}


def verify(row):
    path = ROOT / row['path']
    assert path.is_file() and not path.is_symlink() and path.stat().st_nlink == 1
    assert pin(path) == row, row['path']
    return path.read_bytes()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def same(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def main():
    OUTPUT.mkdir(exist_ok=False)
    started = time.monotonic()
    result = {'schema': 'phase463-independent-helper-result/1', 'status': 'RUNNING',
              'classification': 'SYNTHETIC_SOURCE_HELPERS_ONLY', 'cases': [],
              'counts': {'schema_imports': 0, 'top_level_helper_calls': 0,
                         'validate_state_top_level': 0, '_binding_validate_value_top_level': 0,
                         'model': 0, 'Godot_including_parse': 0, 'Expected': 0,
                         'pool_operations': 0, 'producer_regenerations': 0},
              'recursive_function_entries': {}}
    exit_code = 1
    source_rows = []
    contract = None
    try:
        def deadline(signum, frame):
            raise TimeoutError('phase463 helper batch 15s deadline')
        signal.signal(signal.SIGALRM, deadline)
        signal.alarm(15)
        owner = json.loads((SOURCE / 'owned-files.json').read_bytes())
        for row in owner['files']:
            verify(row)
        contract = json.loads((SOURCE / 'contract.json').read_bytes())
        for row in contract['pins'].values():
            verify(row)
        source_owner = json.loads(verify(contract['pins']['source_owner']))
        source_rows = source_owner['files']
        for row in source_rows:
            verify(row)
        result['source_before_verified_files'] = len(source_rows)
        result['source_owner'] = contract['pins']['source_owner']
        result['source_tuple'] = contract['pins']['source_tuple']
        cases = json.loads(verify(contract['pins']['synthetic_inputs']))['cases']
        assert [c['id'] for c in cases] == ['S' + str(i) for i in range(1, 12)] + ['B' + str(i) for i in range(1, 8)]
        assert len(cases) == 18
        module = types.ModuleType('phase463_frozen_observer_schema')
        module.__file__ = str(ROOT / contract['pins']['schema']['path'])
        sys.dont_write_bytecode = True
        sys.modules[module.__name__] = module
        result['counts']['schema_imports'] += 1
        exec(compile(verify(contract['pins']['schema']), module.__file__, 'exec'), module.__dict__)
        tracked = {module.validate_state.__code__: 'validate_state',
                   module._binding_validate_value.__code__: '_binding_validate_value'}
        entries = result['recursive_function_entries']
        def profile(frame, event, arg):
            if event == 'call' and frame.f_code in tracked:
                name = tracked[frame.f_code]
                entries[name] = entries.get(name, 0) + 1
        for case in cases:
            row = {'id': case['id'], 'helper': case['helper'], 'expected': case['expect'], 'status': 'ENTERED'}
            result['cases'].append(row)
            assert case['helper'] in ('validate_state', '_binding_validate_value')
            assert case['expect'] in ('PASS', 'REJECT_VALUE_ERROR')
            before = json.dumps(case['args'], sort_keys=True, separators=(',', ':'))
            result['counts']['top_level_helper_calls'] += 1
            result['counts'][case['helper'] + '_top_level'] += 1
            caught = None
            try:
                sys.setprofile(profile)
                returned = getattr(module, case['helper'])(*case['args'])
            except ValueError as exc:
                caught = exc
            finally:
                sys.setprofile(None)
            assert json.dumps(case['args'], sort_keys=True, separators=(',', ':')) == before, 'input mutated'
            if case['expect'] == 'PASS':
                if caught is not None:
                    raise AssertionError(f"{case['id']} unexpectedly rejected: {caught}") from caught
                assert same(returned, case['args'][0]), 'positive return differs in value/type'
                row['observation'] = 'accepted_exact_value_and_types'
            else:
                assert caught is not None, f"{case['id']} unexpectedly accepted"
                row['observation'] = {'exception': type(caught).__name__, 'message': str(caught)}
            row['status'] = 'PASS'
        result['status'] = 'PASS_18_SYNTHETIC_HELPER_CONTROLS'
        exit_code = 0
    except BaseException as exc:
        sys.setprofile(None)
        result['status'] = 'FIRST_UNEXPECTED_ERROR_STOPPED'
        result['error'] = {'type': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()}
    finally:
        signal.alarm(0)
        sys.setprofile(None)
        try:
            after = [pin(ROOT / row['path']) for row in source_rows]
            assert after == source_rows, 'frozen Source changed'
            if contract is not None:
                for row in contract['pins'].values():
                    verify(row)
            write(OUTPUT / 'source-after.json', {'files': after, 'unchanged': True})
            result['source_after'] = pin(OUTPUT / 'source-after.json')
        except BaseException as exc:
            result['status'] = 'SOURCE_AFTER_FAILURE'
            result['source_after_error'] = {'type': type(exc).__name__, 'message': str(exc)}
            exit_code = 1
        result['elapsed_seconds'] = time.monotonic() - started
        result['no_native_observation_or_capture_acceptance'] = True
        write(OUTPUT / 'result.json', result)
        outputs = [pin(path) for path in sorted(OUTPUT.iterdir()) if path.is_file()]
        write(OUTPUT / 'owned-files.json', {'schema': 'phase463-helper-output-owner/1', 'files': outputs, 'no_more_writes': True})
        print(json.dumps({'status': result['status'], 'counts': result['counts'], 'elapsed_seconds': result['elapsed_seconds']}))
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
