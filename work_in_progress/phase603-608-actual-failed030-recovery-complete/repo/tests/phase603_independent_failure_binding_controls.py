"""Six frozen pure association controls; execute only on explicit Root release."""
import __future__
import argparse
import copy
import hashlib
import json
import os
import pathlib
import signal
import stat
import sys
import time
import traceback
import types

ROOT = pathlib.Path('/workspace/python-original-engine/repo')
OUT = ROOT / 'data/phase603-independent-controls-first-001'
TESTED = ROOT / 'tests/phase602_failed030_binding.py'
WATCHED = {str(TESTED), str(ROOT / 'tests/phase602_failed030_restore_predecessor.py'),
           str(ROOT / 'tests/phase602_failed030_independent_readback.py')}
FORBIDDEN = {'failure_association', 'main', 'prepare', 'restore', 'readback', 'apply',
             'action', 'select_restore_images', 'load_modules', 'stable', 'descriptor',
             'no_process', 'validate_request'}


def canonical(value):
    def encoded(item):
        if type(item) is bytes:
            return {'__bytes_hex__': item.hex()}
        raise TypeError(type(item).__name__)
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    allow_nan=False, default=encoded).encode()).hexdigest()


def pin(path):
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and before.st_nlink == 1, ('ordinary file', str(path))
    raw = path.read_bytes()
    after = path.lstat()
    fields = ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
    assert tuple(getattr(before, k) for k in fields) == tuple(getattr(after, k) for k in fields)
    return {'path': str(path.relative_to(ROOT)), 'size': len(raw),
            'sha256': hashlib.sha256(raw).hexdigest()}


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
    assert protocol['schema'] == 'phase603-exact-association-control-pins/1'
    assert not OUT.exists() and not OUT.is_symlink()
    OUT.mkdir(mode=0o700)
    started = time.monotonic()
    result = {'schema': 'phase603-independent-association-controls/1', 'status': 'RUNNING',
              'cases': [], 'top_entered': 0, 'top_completed': 0, 'positive': 0, 'rejected': 0,
              'module_eval_attempts': 0, 'module_imports_completed': 0, 'profile': {},
              'origins': {}, 'read_audit': [], 'writes': [], 'forbidden_calls': [],
              'production_writer_reader_imports': 0, 'production_wrapper_calls': 0,
              'host_calls': 0, 'restore_calls': 0, 'readback_calls': 0,
              'pool_reads': 0, 'pool_writes': 0, 'Native': 0, 'models': 0, 'Expected': 0}
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
                assert str(p) in allowed, ('READ_SCOPE', str(p), stage)
                result['read_audit'].append({'path': str(p), 'stage': stage})
        elif event in ('subprocess.Popen', 'os.system', 'os.exec', 'os.posix_spawn',
                       'os.remove', 'os.rename', 'os.rmdir', 'os.mkdir', 'os.chmod',
                       'os.utime', 'os.link', 'os.symlink', 'socket.connect', 'socket.bind'):
            raise RuntimeError('FORBIDDEN_EVENT ' + event)

    def profile(frame, event, arg):
        if event == 'call' and frame.f_code.co_filename in WATCHED:
            key = frame.f_code.co_filename + '::' + frame.f_code.co_name
            result['profile'][key] = result['profile'].get(key, 0) + 1
            if frame.f_code.co_name in FORBIDDEN or frame.f_code.co_filename != str(TESTED):
                result['forbidden_calls'].append(key)
                raise RuntimeError('FORBIDDEN_FUNCTION ' + key)

    def timeout(sig, frame):
        raise TimeoutError('phase603 15 second inner deadline')

    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(15)
    sys.dont_write_bytecode = True
    sys.addaudithook(audit)
    try:
        result['pins_before'] = [pin(ROOT / row['path']) for row in protocol['files']]
        assert result['pins_before'] == protocol['files']
        vectors = json.loads((ROOT / protocol['vectors']).read_text())
        assert len(vectors['cases']) == 6
        materials = {key: (ROOT / row['path']).read_bytes() for key, row in protocol['materials'].items()}
        stage = 'module_load'
        module = types.ModuleType('_phase603_actual_binding')
        module.__file__ = str(TESTED)
        assert module.__name__ not in sys.modules
        sys.modules[module.__name__] = module
        sys.setprofile(profile)
        result['module_eval_attempts'] += 1
        exec(compile(TESTED.read_bytes(), str(TESTED), 'exec'), module.__dict__)
        result['module_imports_completed'] += 1
        result['origins'][module.__name__] = module.__file__
        assert module.MATERIAL_PINS == protocol['materials']
        constants_before = canonical(module.MATERIAL_PINS)
        stage = 'controls'
        for case in vectors['cases']:
            row = {'id': case['id'], 'role': case['args']['role'], 'status': 'ENTERED',
                   'expected_rejection_depth': case.get('rejection_depth')}
            result['cases'].append(row)
            inputs = copy.deepcopy(case['args'])
            inputs['state_image']['raw'] = bytes.fromhex(inputs['state_image'].pop('raw_hex'))
            inputs['raw_materials'] = dict(materials)
            if case.get('material_mutation'):
                mutation = case['material_mutation']
                assert mutation == {'key': 'execute_owner', 'append_hex': '0a'}
                inputs['raw_materials'][mutation['key']] += bytes.fromhex(mutation['append_hex'])
            before = canonical(inputs)
            result['top_entered'] += 1
            try:
                value = module.validate_failure_association(**inputs)
            except ValueError as exc:
                row['first_reject'] = {'type': type(exc).__name__, 'message': str(exc)}
                assert case['expected'].get('exception') == 'ValueError' and str(exc) == case['expected']['message'], row
                result['rejected'] += 1
            else:
                assert 'returns' in case['expected'] and canonical(value) == canonical(case['expected']['returns']), row
                row['returned'] = value
                result['positive'] += 1
            row['input_before'] = before
            row['input_after'] = canonical(inputs)
            assert before == row['input_after'], row
            row['status'] = 'PASS'
            result['top_completed'] += 1
        assert result['top_completed'] == 6 and result['positive'] == 2 and result['rejected'] == 4
        assert result['module_imports_completed'] == 1 and not result['forbidden_calls']
        assert result['profile'][str(TESTED) + '::validate_failure_association'] == 6
        assert constants_before == canonical(module.MATERIAL_PINS)
        result['module_constants_unchanged'] = True
        result['status'] = 'PASS_PURE_FAILURE_ASSOCIATION_ONLY'
        code = 0
    except BaseException as exc:
        result['status'] = 'FIRST_ERROR_STOPPED'
        result['first_error'] = {'type': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()}
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
        result['remaining'] = 'Pure association only; production loading, locked live state/process/graph, restore and full physical readback are not executed.'
        result['write_audit_scope'] = 'writes is the serialization snapshot before result.json write; it is not the complete reporting write log. The write permission guard remains active.'
        stage = 'report'
        texts = {}
        if 'first_error' in result:
            texts['first-error.json'] = json.dumps(result['first_error'], indent=2) + '\n'
            (OUT / 'first-error.json').write_text(texts['first-error.json'])
        texts['result.json'] = json.dumps(result, indent=2) + '\n'
        (OUT / 'result.json').write_text(texts['result.json'])
        files = [{'path': str((OUT / name).relative_to(ROOT)), 'size': len(text.encode()),
                  'sha256': hashlib.sha256(text.encode()).hexdigest()} for name, text in texts.items()]
        (OUT / 'owned-files.json').write_text(json.dumps({'schema': 'phase603-control-output-owner/1', 'files': files}, indent=2) + '\n')
    return code


if __name__ == '__main__':
    raise SystemExit(main())
