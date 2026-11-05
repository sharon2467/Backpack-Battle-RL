"""Frozen13 synthetic record controls. Execute only on explicit Root release."""
import __future__
import argparse
import copy
import dataclasses
import hashlib
import json
import math
import os
import pathlib
import re
import signal
import stat
import struct
import sys
import time
import traceback
import types

ROOT = pathlib.Path('/workspace/python-original-engine/repo')
OUT = ROOT / 'data/phase612-independent-controls-first-001'
TESTED = ROOT / 'data/phase610-three-selected-hook-source-v2/schema/phase610_mixed_observer_schema.py'
FORBIDDEN = {'decode_sources', 'validate_sources_with_binding', 'join_binding_provenance',
             'validate_observation_records', 'validate_source_carriers', '_transport_only_decode',
             'validate_binding_carrier', '_binding_validate_value', 'decode_clock',
             'validate_terminal_evidence', 'validate_terminal_receipt', 'validate_terminal_diagnostics',
             '_validate_mixed_prepared_facts', 'validate_single_king_input_provenance',
             'validate_single_king_ui_authority', 'validate_single_king_fresh_facts',
             '_validate_call_pairs'}


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def pin(path):
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and before.st_nlink == 1, ('ordinary file', str(path))
    raw = path.read_bytes()
    after = path.lstat()
    fields = ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
    assert tuple(getattr(before, k) for k in fields) == tuple(getattr(after, k) for k in fields)
    return {'path': str(path.relative_to(ROOT)), 'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pins', required=True)
    parser.add_argument('--pins-sha256', required=True)
    args = parser.parse_args()
    pins_path = pathlib.Path(args.pins)
    assert pins_path.is_absolute()
    raw_pins = pins_path.read_bytes()
    assert hashlib.sha256(raw_pins).hexdigest() == args.pins_sha256
    protocol = json.loads(raw_pins)
    assert protocol['schema'] == 'phase612-exact-schema-control-pins/1'
    assert not OUT.exists() and not OUT.is_symlink()
    OUT.mkdir(mode=0o700)
    started = time.monotonic()
    result = {'schema': 'phase612-independent-schema-controls/1', 'status': 'RUNNING',
              'cases': [], 'top_entered': 0, 'top_completed': 0, 'positive': 0, 'rejected': 0,
              'module_eval_attempts': 0, 'module_imports_completed': 0, 'profile': {},
              'origins': {}, 'read_audit': [], 'writes': [], 'forbidden_calls': [],
              'schema_SUT_stage_reads': 0, 'fulljoin': 0, 'fullcapture_decode': 0,
              'producer': 0, 'Godot': 0, 'Native': 0, 'models': 0, 'Expected': 0,
              'pool_reads': 0, 'pool_writes': 0, 'actual_Native_facts': False,
              'python': sys.version, 'synthetic_record_envelopes': True}
    allowed = {str(ROOT / row['path']) for row in protocol['files']} | {str(pins_path)}
    stage = 'before'
    code = 1

    def audit(event, arguments):
        if event == 'open':
            path, mode, flags = arguments
            if isinstance(path, int):
                raise RuntimeError('FD_OPEN_NOT_REQUIRED')
            p = pathlib.Path(os.fsdecode(path))
            assert p.is_absolute(), ('relative open forbidden', str(p))
            write = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
            if write:
                assert stage == 'report' and p.parent == OUT, ('WRITE_SCOPE', str(p), stage)
                result['writes'].append(str(p))
            else:
                result['read_audit'].append({'path': str(p), 'stage': stage})
                if stage == 'controls' or stage == 'schema_eval':
                    result['schema_SUT_stage_reads'] += 1
                    raise RuntimeError('SUT_FILE_READ_FORBIDDEN ' + str(p))
                assert str(p) in allowed, ('READ_SCOPE', str(p), stage)
        elif event in ('subprocess.Popen', 'os.system', 'os.exec', 'os.posix_spawn',
                       'os.remove', 'os.rename', 'os.rmdir', 'os.mkdir', 'os.chmod',
                       'os.utime', 'os.link', 'os.symlink', 'socket.connect', 'socket.bind'):
            raise RuntimeError('FORBIDDEN_EVENT ' + event)

    def profile(frame, event, arg):
        if event == 'call' and frame.f_code.co_filename == str(TESTED):
            key = str(TESTED) + ':' + str(frame.f_code.co_firstlineno) + '::' + frame.f_code.co_name
            result['profile'][key] = result['profile'].get(key, 0) + 1
            if frame.f_code.co_name in FORBIDDEN:
                result['forbidden_calls'].append(key)
                raise RuntimeError('FORBIDDEN_FUNCTION ' + key)

    def timeout(sig, frame):
        raise TimeoutError('phase612 15 second inner deadline')

    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(15)
    sys.dont_write_bytecode = True
    sys.addaudithook(audit)
    try:
        result['pins_before'] = [pin(ROOT / row['path']) for row in protocol['files']]
        assert result['pins_before'] == protocol['files']
        vectors = json.loads((ROOT / protocol['vectors']).read_text())
        assert len(vectors['cases']) == 13 and vectors['synthetic'] is True
        stage = 'module_load'
        source_bytes = TESTED.read_bytes()
        module = types.ModuleType('_phase612_actual_frozen_schema')
        module.__file__ = str(TESTED)
        assert module.__name__ not in sys.modules
        sys.modules[module.__name__] = module
        schema_code = compile(source_bytes, str(TESTED), 'exec')
        stage = 'schema_eval'
        sys.setprofile(profile)
        result['module_eval_attempts'] += 1
        exec(schema_code, module.__dict__)
        result['module_imports_completed'] += 1
        result['origins'][module.__name__] = module.__file__
        constants_before = canonical({'MATRIX': module.MATRIX, 'CONTRACT': module.CONTRACT})
        stage = 'controls'
        for case in vectors['cases']:
            entry = {'id': case['id'], 'status': 'ENTERED', 'expected_rejection_layer': case['layer']}
            result['cases'].append(entry)
            inputs = copy.deepcopy(case['row'])
            before = canonical(inputs)
            result['top_entered'] += 1
            try:
                value = module.validate_record(inputs)
            except ValueError as exc:
                entry['first_reject'] = {'type': type(exc).__name__, 'message': str(exc)}
                assert case['expected'].get('exception') == 'ValueError' and str(exc) == case['expected']['message'], entry
                result['rejected'] += 1
            else:
                assert case['expected'].get('returns_input') is True and canonical(value) == before, entry
                entry['returned_canonical'] = canonical(value)
                result['positive'] += 1
            entry['input_before'] = before
            entry['input_after'] = canonical(inputs)
            assert before == entry['input_after'], entry
            entry['status'] = 'PASS'
            result['top_completed'] += 1
        assert result['top_completed'] == 13 and result['positive'] == 6 and result['rejected'] == 7
        assert result['module_imports_completed'] == 1 and not result['forbidden_calls']
        assert result['schema_SUT_stage_reads'] == 0
        outer_key = str(TESTED) + ':' + str(module.validate_record.__code__.co_firstlineno) + '::validate_record'
        assert result['profile'][outer_key] == 13
        assert constants_before == canonical({'MATRIX': module.MATRIX, 'CONTRACT': module.CONTRACT})
        result['module_constants_unchanged'] = True
        result['status'] = 'PASS_FINITE_SYNTHETIC_SCHEMA_RECORDS_ONLY'
        code = 0
    except BaseException as exc:
        result['status'] = 'FIRST_ERROR_STOPPED'
        tb = exc.__traceback__
        frames = []
        while tb is not None:
            frames.append({'path': tb.tb_frame.f_code.co_filename, 'function': tb.tb_frame.f_code.co_name, 'line': tb.tb_lineno})
            tb = tb.tb_next
        result['first_error'] = {'type': type(exc).__name__, 'message': str(exc), 'traceback_frames': frames}
    finally:
        sys.setprofile(None)
        signal.alarm(0)
        stage = 'after'
        try:
            result['pins_after'] = [pin(ROOT / row['path']) for row in protocol['files']]
            assert result['pins_after'] == protocol['files']
            result['pins_unchanged'] = True
        except BaseException as exc:
            result['status'] = 'FIRST_ERROR_STOPPED'
            result['after_error'] = repr(exc)
            code = 1
        result['elapsed_seconds'] = time.monotonic() - started
        result['remaining'] = 'No actual Native hook execution, complete capture/fulljoin, Godot purity, actual UID/clock, host or runtime admission has been validated.'
        result['write_audit_scope'] = 'writes is the serialization snapshot before result.json write; not a complete reporting write log. The write permission guard remains active.'
        stage = 'report'
        texts = {}
        if 'first_error' in result:
            texts['first-error.json'] = json.dumps(result['first_error'], indent=2) + '\n'
            (OUT / 'first-error.json').write_text(texts['first-error.json'])
        texts['result.json'] = json.dumps(result, indent=2) + '\n'
        (OUT / 'result.json').write_text(texts['result.json'])
        files = [{'path': str((OUT / name).relative_to(ROOT)), 'size': len(text.encode()),
                  'sha256': hashlib.sha256(text.encode()).hexdigest()} for name, text in texts.items()]
        (OUT / 'owned-files.json').write_text(json.dumps({'schema': 'phase612-control-output-owner/1', 'files': files}, indent=2) + '\n')
    return code


if __name__ == '__main__':
    raise SystemExit(main())
