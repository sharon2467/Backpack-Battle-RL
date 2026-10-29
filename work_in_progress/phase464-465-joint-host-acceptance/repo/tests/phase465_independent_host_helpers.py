"""First and only bounded phase465 helper batch; synthetic files, no pool/lease."""
from pathlib import Path
import copy
import hashlib
import json
import os
import signal
import stat
import sys
import time
import traceback
import types

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/phase465-independent-helper-source'
OUT = ROOT / 'data/phase465-independent-helpers-first-001'


def identity(raw):
    return {'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def pin(path):
    return dict(path=str(path.relative_to(ROOT)), **identity(path.read_bytes()))


def verify(row):
    path = ROOT / row['path']
    assert path.is_file() and not path.is_symlink() and path.stat().st_nlink == 1
    raw = path.read_bytes()
    assert dict(path=row['path'], **identity(raw)) == row, row['path']
    return raw


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def main():
    OUT.mkdir(exist_ok=False)
    started = time.monotonic()
    result = {'schema': 'phase465-independent-helper-result/1', 'status': 'RUNNING',
              'cases': [], 'top_level_calls': 0, 'module_loads': [], 'function_entries': {},
              'forbidden_calls': [], 'scope': 'TEST_ONLY_FIXTURES_AND_FROZEN_SOURCE',
              'actual_pool': 0, 'native': 0, 'models': 0, 'Expected': 0}
    exit_code = 1
    owner_rows = []
    contract = None
    watched = set()
    reads = set()
    writes = set()
    stdlib = Path(sys.base_prefix).resolve()
    # These are verified Source reads only; writes are confined to this new test directory.
    allowed_source = {str(Path(__file__).resolve())}

    def audit(event, args):
        if event in ('subprocess.Popen', 'os.system', 'os.exec', 'os.posix_spawn', 'socket.connect', 'socket.bind'):
            raise AssertionError('forbidden execution/network: ' + event)
        if event == 'open':
            path, mode, flags = args
            if isinstance(path, int):
                return
            p = Path(os.fsdecode(path)).absolute()
            writing = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
            if writing:
                assert p.is_relative_to(OUT), ('outside test writes', str(p))
                writes.add(str(p.relative_to(OUT)))
            else:
                assert (str(p) in allowed_source or p.is_relative_to(OUT)
                        or p.resolve().is_relative_to(stdlib)), ('outside frozen/test read', str(p))
                if not p.resolve().is_relative_to(stdlib):
                    reads.add(str(p))

    def profile(frame, event, arg):
        if event == 'c_call' and frame.f_code.co_filename in watched and arg is os.fsync:
            result['function_entries']['os.fsync'] = result['function_entries'].get('os.fsync', 0) + 1
            return
        if event != 'call' or frame.f_code.co_filename not in watched:
            return
        name = frame.f_code.co_name
        key = Path(frame.f_code.co_filename).name + ':' + name
        result['function_entries'][key] = result['function_entries'].get(key, 0) + 1
        if name in {'lease', 'plan', 'execute', 'budget', 'check_ready', 'resource_gate',
                    'reset_previous', 'install', 'archive_streaming', 'preflight_install_payloads',
                    'state_write', 'inventory', 'execute_process', 'rename_capture', 'usage',
                    'load_terminal_schema', 'read_terminal_expected_controls'}:
            result['forbidden_calls'].append(key)
            raise AssertionError('forbidden operational helper: ' + key)

    def invoke(case_id, fn, args, expected_message=None):
        row = {'id': case_id, 'helper': fn.__name__, 'status': 'ENTERED',
               'expected': 'PASS' if expected_message is None else 'REJECT_VALUE_ERROR'}
        result['cases'].append(row)
        result['top_level_calls'] += 1
        caught = None
        returned = None
        try:
            sys.setprofile(profile)
            returned = fn(*args)
        except ValueError as exc:
            caught = exc
        finally:
            sys.setprofile(None)
        if expected_message is None:
            if caught is not None:
                raise AssertionError(case_id + ' unexpectedly rejected: ' + str(caught)) from caught
        else:
            assert caught is not None and expected_message in str(caught), (case_id, repr(caught))
            row['rejection'] = {'type': type(caught).__name__, 'message': str(caught)}
        return returned, row

    try:
        def deadline(signum, frame):
            raise TimeoutError('phase465 one helper batch deadline15s')
        signal.signal(signal.SIGALRM, deadline)
        signal.alarm(15)
        owner = json.loads((SOURCE / 'owned-files.json').read_bytes())
        for row in owner['files']:
            verify(row)
            allowed_source.add(str(ROOT / row['path']))
        contract = json.loads((SOURCE / 'contract.json').read_bytes())
        for row in contract['pins'].values():
            verify(row)
            allowed_source.add(str(ROOT / row['path']))
        source_owner = json.loads(verify(contract['pins']['source_owner']))
        owner_rows = source_owner['files']
        for row in owner_rows:
            verify(row)
            allowed_source.add(str(ROOT / row['path']))
        inputs = json.loads(verify(contract['pins']['inputs']))
        freeze = json.loads(verify(contract['pins']['source_freeze']))
        observer_review = json.loads(verify(contract['pins']['observer_review']))
        result['source_before_verified'] = len(owner_rows)
        result['source_owner'] = contract['pins']['source_owner']
        result['source_freeze'] = contract['pins']['source_freeze']
        sys.dont_write_bytecode = True
        sys.addaudithook(audit)
        modules = {}
        for row in contract['load_order']:
            raw = verify(row['source'])
            name = row['module']
            assert name not in sys.modules
            module = types.ModuleType(name)
            module.__file__ = str(ROOT / row['source']['path'])
            sys.modules[name] = module
            exec(compile(raw, module.__file__, 'exec'), module.__dict__)
            modules[name] = module
            watched.add(module.__file__)
            result['module_loads'].append(dict(module=name, source=row['source']))
        h = modules['phase464_oracle_host_v2']
        assert h.__file__ == str(ROOT / contract['pins']['host']['path'])
        fixtures_before = {}
        raw = inputs['state_raw_utf8'].encode()
        state = dict(raw=raw, identity=identity(raw), mode=inputs['state_mode'], mtime_ns=inputs['mtime_ns'])

        def fixture_setup(case_id, present):
            base = OUT / case_id
            base.mkdir()
            pool = base / 'TEST_ONLY_FIXTURES'
            (pool / 'data').mkdir(parents=True)
            for name, content in present.items():
                path = pool / 'data' / name
                path.write_bytes(content.encode())
                os.chmod(path, inputs['fixture_mode'])
                os.utime(path, ns=(inputs['mtime_ns'], inputs['mtime_ns']))
                fixtures_before[str(path)] = dict(identity=identity(path.read_bytes()),
                    mode=stat.S_IMODE(path.stat().st_mode), mtime_ns=path.stat().st_mtime_ns)
            return base, pool

        for case_id, present in [('S1', inputs['fixtures_both_present']), ('S2', inputs['fixtures_one_absent'])]:
            base, pool = fixture_setup(case_id, present)
            returned, row = invoke(case_id, h.backup_predecessor_controls,
                                   (pool, base / 'backup', state, base / 'TEST_PREVIOUS_NOT_A_RUN'))
            manifest = json.loads((base / 'backup/manifest.json').read_bytes())
            assert returned['restored'] is False and manifest['restored'] is False
            assert returned['manifest'] == identity((base / 'backup/manifest.json').read_bytes())
            assert [x['target'] for x in manifest['images']] == ['state.json', 'data/custom_player.json', 'data/custom_opponent.json']
            for image in manifest['images']:
                target = image['target']
                expected = raw if target == 'state.json' else present.get(target.split('/')[1])
                if expected is None:
                    assert image == dict(target=target, present=False, backup=None)
                else:
                    expected = expected if isinstance(expected, bytes) else expected.encode()
                    path = base / 'backup' / image['backup']
                    mode = inputs['state_mode'] if target == 'state.json' else inputs['fixture_mode']
                    assert path.read_bytes() == expected and image['identity'] == identity(expected)
                    assert image['present'] is True and image['mode'] == mode and stat.S_IMODE(path.stat().st_mode) == mode
                    assert image['mtime_ns'] == inputs['mtime_ns'] == path.stat().st_mtime_ns
            row['status'] = 'PASS'
            row['manifest'] = pin(base / 'backup/manifest.json')
        base, pool = fixture_setup('S3', inputs['fixtures_both_present'])
        bad = copy.deepcopy(state)
        bad['identity']['sha256'] = '0' * 64
        _, row = invoke('S3', h.backup_predecessor_controls,
                        (pool, base / 'backup', bad, base / 'TEST_PREVIOUS_NOT_A_RUN'), 'locked predecessor state bytes')
        assert not (base / 'backup').exists()
        row['status'] = 'PASS'
        base, pool = fixture_setup('S4', {})
        target = base / 'TEST_ONLY_SYMLINK_TARGET'
        target.write_bytes(b'test only\n')
        (pool / 'data/custom_player.json').symlink_to(target)
        _, row = invoke('S4', h.backup_predecessor_controls,
                        (pool, base / 'backup', state, base / 'TEST_PREVIOUS_NOT_A_RUN'), 'symlink member/ancestor')
        assert (base / 'backup').is_dir() and not list((base / 'backup').iterdir())
        row['status'] = 'PASS'

        graph, row = invoke('D1', h.resolve_execute_payloads, (ROOT, freeze))
        install = [x['source'] for x in graph['patches']] + list(graph['artifacts'].values())
        assert len(install) == 78 and sum(x['size'] for x in install) == 812880
        assert contract['pins']['process_storage'] in graph['driver_sources']
        assert graph['case_inputs'] == freeze['case_inputs']
        write(OUT / 'resolved-graph.json', graph)
        row['status'] = 'PASS'
        row['install'] = {'files': len(install), 'bytes': sum(x['size'] for x in install)}
        bad = copy.deepcopy(graph)
        bad['install_limits']['bytes'] = inputs['wrong_install_bytes']
        _, row = invoke('D2', h.verify_execute_payloads, (ROOT, bad), 'exact frozen install limits')
        row['status'] = 'PASS'
        bad = copy.deepcopy(freeze)
        bad['case_inputs']['custom_player.json']['path'] = inputs['stale_case_input_path']
        _, row = invoke('D3', h.resolve_execute_payloads, (ROOT, bad), 'exact three462v3 case descriptors')
        row['status'] = 'PASS'
        returned, row = invoke('G1', h.validate_observer_review,
                               (observer_review, contract['pins']['observer_review'], freeze['active_source_tuple']))
        assert returned is None
        row['status'] = 'PASS'
        bad = copy.deepcopy(observer_review)
        bad['source_owner']['sha256'] = '0' * 64
        _, row = invoke('G2', h.validate_observer_review,
                        (bad, contract['pins']['observer_review'], freeze['active_source_tuple']), 'actual463 Source-only acceptance')
        row['status'] = 'PASS'
        base = OUT / 'G3'
        base.mkdir()
        write(base / 'TEST_ONLY_INVALID_CONFIG.json', inputs['invalid_bool_config'])
        data = (base / 'TEST_ONLY_INVALID_CONFIG.json').read_bytes()
        descriptor = dict(path='TEST_ONLY_INVALID_CONFIG.json', **identity(data))
        _, row = invoke('G3', h.source_gate, (base, descriptor), 'strictINT0 model/inputbuild/expected permissions')
        row['status'] = 'PASS'
        for name, expected in fixtures_before.items():
            path = Path(name)
            actual = dict(identity=identity(path.read_bytes()), mode=stat.S_IMODE(path.stat().st_mode), mtime_ns=path.stat().st_mtime_ns)
            assert actual == expected, name
        assert result['top_level_calls'] == 10 and all(x['status'] == 'PASS' for x in result['cases'])
        assert result['forbidden_calls'] == []
        result['fixtures_before_after_unchanged'] = fixtures_before
        result['status'] = 'PASS_10_SOURCE_HELPER_CONTROLS'
        exit_code = 0
    except BaseException as exc:
        sys.setprofile(None)
        result['status'] = 'FIRST_UNEXPECTED_ERROR_STOPPED'
        result['error'] = {'type': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()}
    finally:
        signal.alarm(0)
        sys.setprofile(None)
        try:
            after = [pin(ROOT / row['path']) for row in owner_rows]
            assert after == owner_rows
            if contract:
                for row in contract['pins'].values():
                    verify(row)
            write(OUT / 'source-after.json', {'files': after, 'unchanged': True})
        except BaseException as exc:
            result['status'] = 'SOURCE_AFTER_FAILURE'
            result['source_after_error'] = {'type': type(exc).__name__, 'message': str(exc)}
            exit_code = 1
        result['elapsed_seconds'] = time.monotonic() - started
        result['io_scope'] = {'audited_read_paths': sorted(reads), 'audited_write_paths': sorted(writes),
                              'preaudit': 'Read/hash only sealed contract/owner and declared Source leaves; no pool.'}
        write(OUT / 'result.json', result)
        files, links = [], []
        for path in sorted(OUT.rglob('*')):
            if path.is_symlink():
                links.append({'path': str(path.relative_to(ROOT)), 'target': os.readlink(path), 'classification': 'TEST_ONLY_NEGATIVE'})
            elif path.is_file():
                files.append(pin(path))
        write(OUT / 'owned-files.json', {'schema': 'phase465-helper-output-owner/1', 'files': files,
                                       'synthetic_links': links, 'no_more_writes': True})
        print(json.dumps({'status': result['status'], 'top_level_calls': result['top_level_calls'],
                          'module_loads': len(result['module_loads']), 'elapsed_seconds': result['elapsed_seconds']}))
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
