"""Presealed finite Source-only controls; no physical host/restore operation."""
import sys
sys.dont_write_bytecode = True
import argparse
import copy
import hashlib
import importlib
import json
import os
from pathlib import Path
import time
import traceback
from collections import Counter

ROOT = Path('/workspace/python-original-engine/repo')
SOURCE = ROOT / 'data/phase509-independent-control-source'


def pin(path):
    raw = path.read_bytes()
    return dict(path=str(path.relative_to(ROOT)), size=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n')


def same(a, b):
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return set(a) == set(b) and all(same(a[k], b[k]) for k in a)
    if type(a) in (tuple, list):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def decoded_images(images):
    result = {}
    for key, value in images.items():
        if value is None:
            result[key] = None
        else:
            image = copy.deepcopy(value)
            image['raw'] = bytes.fromhex(image.pop('raw_hex'))
            assert image['identity'] == dict(size=len(image['raw']), sha256=hashlib.sha256(image['raw']).hexdigest())
            result[key] = image
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output-new', required=True)
    args = ap.parse_args()
    out = Path(args.output_new).absolute()
    assert out == ROOT / 'data/phase509-independent-controls-first-001'
    out.mkdir(exist_ok=False)
    started = time.monotonic()
    result = dict(schema='phase509-finite-source-control-result/1', status='STARTED',
                  top_level_calls=0, cases=[], tested_module_imports=0,
                  host_plan_execute=0, source_gate_calls=0, physical_restore=0,
                  pool_baseline_resource_reads=0, Native_Godot=0, models=0, Expected_decode=0)
    pins = json.loads((SOURCE / 'pins.json').read_text())
    counts = Counter()
    reads = Counter()
    codes = {}
    forbidden = set()
    allowed = {str(ROOT / x['path']) for x in pins['files']}
    allowed.add(str(SOURCE / 'pins.json'))
    # A new bytecode namespace avoids loading cached repo modules. No bytecode writes.
    sys.pycache_prefix = str(out / 'unused-bytecode-cache')
    library_roots = tuple(Path(x).absolute() for x in sys.path if x and
                          not Path(x).absolute().is_relative_to(Path('/workspace')))

    def audit(event, args):
        if event in ('subprocess.Popen', 'os.system', 'os.posix_spawn', 'socket.connect',
                     'socket.bind', 'os.fork', 'os.forkpty'):
            raise RuntimeError('forbidden control side effect: ' + event)
        if event == 'open':
            name, mode, flags = args
            if isinstance(name, int):
                return
            path = Path(os.fsdecode(name)).absolute()
            writing = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
            in_out = path.is_relative_to(out)
            if writing and not in_out:
                raise RuntimeError('write outside report scope: ' + str(path))
            if not writing and not (str(path) in allowed or in_out or
                                    any(path.is_relative_to(p) for p in library_roots)):
                raise RuntimeError('read outside frozen Source scope: ' + str(path))
            if not writing:
                reads[str(path)] += 1

    def profile(frame, event, arg):
        if event == 'call':
            if frame.f_code in forbidden:
                raise RuntimeError('forbidden production call: ' + frame.f_code.co_name)
            name = codes.get(frame.f_code)
            if name:
                counts[name] += 1

    def invoke(case, function, expected=None):
        result['top_level_calls'] += 1
        row = dict(name=case['name'], status='STARTED')
        result['cases'].append(row)
        try:
            value = function()
        except ValueError as exc:
            if 'reject' not in case or case['reject'] not in str(exc):
                raise
            row.update(status='PASS', rejection=str(exc))
        else:
            if 'reject' in case:
                raise AssertionError('accepted negative: ' + case['name'])
            assert same(value, expected), case['name']
            row['status'] = 'PASS'
        save(out / 'progress.json', result)

    try:
        for row in pins['files']:
            assert pin(ROOT / row['path']) == row, row['path']
        save(out / 'before.json', pins)
        vectors = json.loads((SOURCE / 'vectors.json').read_text())
        freeze = json.loads((ROOT / pins['freeze']['path']).read_text())
        review = json.loads((ROOT / pins['observer_review']['path']).read_text())
        source_tuple = json.loads((ROOT / freeze['active_source_tuple']['path']).read_text())
        sys.addaudithook(audit)
        sys.path.insert(0, str(ROOT / 'tests'))
        H = importlib.import_module('phase508_oracle_host')
        R = importlib.import_module('phase508_restore_predecessor')
        result['tested_module_imports'] = 2
        module_names = pins['repo_modules']
        loaded = {}
        for name, rel in module_names.items():
            module = sys.modules[name]
            assert Path(module.__file__).absolute() == ROOT / rel, name
            loaded[name] = pin(Path(module.__file__).absolute())
            for attr, value in vars(module).items():
                if callable(value) and hasattr(value, '__code__') and value.__module__ == name:
                    codes[value.__code__] = name + '.' + attr
                    if attr in {'source_gate', 'plan', 'execute', 'resource_gate', 'verify_execute_payloads',
                                'resolve_execute_payloads', 'load_terminal_schema', 'lease', 'check_ready',
                                'budget', 'install', 'reset_previous', 'archive_streaming', 'prepare',
                                'restore', 'apply', 'action', 'readback', 'load_modules', 'inventory',
                                'process_check', 'retained', 'execute_process', 'main'}:
                        forbidden.add(value.__code__)
        result['loaded_repo_modules'] = loaded
        sys.setprofile(profile)
        for case in vectors['host_cases']:
            if case['api'] == 'validate_active_source_tuple':
                value = copy.deepcopy(freeze)
                if case['mutation'] == 'old_schema':
                    value['schema'] = 'phase464-host-derived-source-freeze/1'
                elif case['mutation'] == 'wrapper_declared_hash':
                    target = source_tuple['direct_primitive_wrapper']['path']
                    leaf = next(x for x in value['files'] if x['path'] == target)
                    leaf['sha256'] = '0' * 64
                elif case['mutation'] == 'derived_origin':
                    value['native_source_origin']['sha256'] = '0' * 64
                elif case['mutation'] is not None:
                    raise AssertionError('unknown tuple mutation')
                before = copy.deepcopy(value)
                invoke(case, lambda: H.validate_active_source_tuple(ROOT, value), source_tuple)
                assert same(before, value), 'tuple mutation by SUT'
            else:
                assert case['api'] == 'validate_observer_review'
                value = copy.deepcopy(review)
                if case['mutation'] == 'review_owner':
                    value['accepted_source_owner']['sha256'] = '0' * 64
                else:
                    assert case['mutation'] is None
                before = copy.deepcopy(value)
                invoke(case, lambda: H.validate_observer_review(value, pins['observer_review'], freeze['active_source_tuple']))
                assert same(before, value), 'review mutation by SUT'
        for case in vectors['selection_cases']:
            values = copy.deepcopy(case['args'])
            for key in ('old_images', 'journal_images'):
                values[key] = decoded_images(values[key])
            expected = decoded_images(case['expected']) if 'expected' in case else None
            before = copy.deepcopy(values)
            invoke(case, lambda: R.select_restore_images(**values), expected)
            assert same(values, before), 'selector mutated input'
        assert result['top_level_calls'] == vectors['total_top_level_calls'] == 11
        assert len(result['cases']) == 11 and all(x['status'] == 'PASS' for x in result['cases'])
        result['status'] = 'PASS_FINITE_SOURCE_BINDING_SELECTION_NOT_PHYSICAL_OR_NATIVE'
    except BaseException as exc:
        result['status'] = 'FIRST_ERROR_STOPPED'
        result['error'] = dict(type=type(exc).__name__, message=str(exc), traceback=traceback.format_exc())
    finally:
        sys.setprofile(None)
        result['function_entries'] = dict(sorted(counts.items()))
        result['read_open_counts'] = dict(sorted(reads.items()))
        result['wall_seconds'] = time.monotonic() - started
        after = [pin(ROOT / row['path']) for row in pins['files']]
        result['source_after_unchanged'] = after == pins['files']
        if not result['source_after_unchanged']:
            result['status'] = 'SOURCE_DRIFT_STOPPED'
        save(out / 'after.json', dict(files=after))
        save(out / 'result.json', result)
        save(out / 'owned-files.json', dict(schema='phase509-control-output-owner/1',
             files=[pin(p) for p in sorted(out.iterdir()) if p.is_file()]))
    print(json.dumps({k: result[k] for k in ('status', 'top_level_calls', 'wall_seconds')}))
    return 0 if result['status'].startswith('PASS_') else 1


if __name__ == '__main__':
    raise SystemExit(main())
