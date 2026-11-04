"""Directed synthetic ledger checks; no actual capture or whole projection."""
import argparse
import copy
import dataclasses
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import struct
import sys
import time
import traceback
import types

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/phase528-independent-controls-first-001'


def require(value, message):
    if not value:
        raise AssertionError(message)


def descriptor(path):
    raw = path.read_bytes()
    return {'path': str(path.relative_to(ROOT)), 'size': len(raw),
            'sha256': hashlib.sha256(raw).hexdigest()}


def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pins', required=True)
    parser.add_argument('--pins-sha256', required=True)
    args = parser.parse_args()
    pins_path = Path(args.pins).absolute()
    pins_raw = pins_path.read_bytes()
    require(hashlib.sha256(pins_raw).hexdigest() == args.pins_sha256, 'pins SHA')
    pins = json.loads(pins_raw)
    blobs = {}
    for row in pins['files']:
        path = ROOT / row['path']
        raw = path.read_bytes()
        require(len(raw) == row['size'] and hashlib.sha256(raw).hexdigest() == row['sha256'], 'pin ' + row['path'])
        blobs[row['path']] = raw
    require(not OUT.exists(), 'new output required')
    OUT.mkdir(mode=0o700)
    allowed_reads = {pins_path, *(ROOT / name for name in blobs)}
    opened = set()
    result = {'status': 'STARTED', 'cases': [], 'module_loads': {},
              'top_validate_ledger_calls': 0, 'module_entries': {},
              'actual_capture_reads': 0, 'Expected_reads': 0, 'models': 0,
              'Native': 0, 'whole_projection_calls': 0, 'build_calls': 0}
    started = time.monotonic()
    sys.dont_write_bytecode = True

    def audit(event, values):
        if event in ('subprocess.Popen', 'os.system', 'os.exec', 'os.posix_spawn', 'socket.connect', 'socket.bind'):
            raise AssertionError('forbidden operation ' + event)
        if event == 'open' and not isinstance(values[0], int):
            path = Path(os.fsdecode(values[0])).absolute()
            flags = values[2]
            write = flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)
            require(path.is_relative_to(OUT) if write else path in allowed_reads or path.is_relative_to(OUT),
                    'IO scope ' + str(path))
            if not write:
                opened.add(str(path))
        if event in ('os.remove', 'os.rmdir', 'os.mkdir', 'os.chmod', 'os.utime'):
            require(Path(os.fsdecode(values[0])).absolute().is_relative_to(OUT), 'mutation scope')
        if event in ('os.rename', 'os.link', 'os.symlink'):
            require(all(Path(os.fsdecode(p)).absolute().is_relative_to(OUT) for p in values[:2]), 'link scope')

    watched = {str(ROOT / pins[k]['path']): k for k in ('initial', 'schema_module')}

    def profile(frame, event, arg):
        if event != 'call' or frame.f_code.co_filename not in watched:
            return
        name = frame.f_code.co_name
        key = watched[frame.f_code.co_filename] + ':' + name
        result['module_entries'][key] = result['module_entries'].get(key, 0) + 1
        require(name not in {'build_initial_receipt', 'value_index', 'validate_timer',
                             'project_from_bytes', 'build_from_files'}, 'forbidden candidate entry ' + name)

    def load(key):
        row = pins[key]
        module = types.ModuleType('_phase528_independent_' + key)
        module.__file__ = str(ROOT / row['path'])
        sys.modules[module.__name__] = module
        result['module_loads'][key] = result['module_loads'].get(key, 0) + 1
        exec(compile(blobs[row['path']], module.__file__, 'exec'), module.__dict__)
        require(module.__file__ == str(ROOT / row['path']), 'loaded source path')
        return module

    def deadline(signum, frame):
        raise TimeoutError('15 second directed control deadline')

    code = 1
    sys.addaudithook(audit)
    signal.signal(signal.SIGALRM, deadline)
    signal.alarm(15)
    try:
        sys.setprofile(profile)
        schema = load('schema_module')
        initial = load('initial')
        vectors = json.loads(blobs[pins['vectors']['path']])
        require(len(vectors['cases']) == 3, 'exact3 cases')
        for case in vectors['cases']:
            value = copy.deepcopy(case['input'])
            before = copy.deepcopy(value)
            result['top_validate_ledger_calls'] += 1
            row = {'name': case['name'], 'expected': case['expected']}
            result['cases'].append(row)
            try:
                answer = initial.validate_ledger(value['facts'], value['role'], value['owner'], value['timer'], schema)
            except ValueError as error:
                require(case['expected']['kind'] == 'reject' and str(error) == case['expected']['message'],
                        'unexpected rejection ' + case['name'] + ': ' + str(error))
                row['actual_error'] = str(error)
            else:
                require(case['expected']['kind'] == 'accept', 'expected rejection ' + case['name'])
                require(answer == case['expected']['value'], 'exact preserved ledger output')
                require(answer['lineage'] is not value['facts']['timers'][value['role']]['lineage'], 'ledger deepcopy')
                row['actual'] = answer
            require(value == before, 'input mutated')
            row['status'] = 'PASS'
        require(result['top_validate_ledger_calls'] == 3, 'three top calls')
        require(result['module_entries'].get('schema_module:validate_state') == 4, 'four nested real Timer/Node validations')
        result['status'] = 'PASS_EXACT3_SYNTHETIC_LEDGER_ONLY'
        code = 0
    except BaseException as error:
        sys.setprofile(None)
        result['status'] = 'FIRST_ERROR_STOPPED'
        result['error'] = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
    finally:
        sys.setprofile(None)
        signal.alarm(0)
        try:
            result['source_after'] = [descriptor(ROOT / row['path']) for row in pins['files']]
            require(result['source_after'] == pins['files'], 'sealed sources changed')
        except BaseException as error:
            code = 1
            result['source_after_error'] = {'type': type(error).__name__, 'message': str(error)}
            result['status'] = 'SOURCE_AFTER_ERROR'
        result['elapsed_seconds'] = time.monotonic() - started
        result['opened_read_paths_after_audit'] = sorted(opened)
        result['pins'] = {'path': str(pins_path), 'sha256': args.pins_sha256}
        save(OUT / 'result.json', result)
        save(OUT / 'owned-files.json', {'schema': 'phase528-exact3-output-owner/1',
                                      'files': [descriptor(OUT / 'result.json')], 'no_more_writes': True})
    print(json.dumps({'status': result['status'], 'elapsed_seconds': result['elapsed_seconds']}))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
