"""Frozen independent534 controls; execute only after exact Root release."""
import argparse
import collections
import copy
import datetime
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import re
import signal
import stat
import struct
import subprocess
import sys
import time
import traceback
import types

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/phase534-exact-control-source'
OUTPUT = ROOT / 'data/phase534-independent-controls-first-001'
LAUNCHER = ROOT / 'tests/phase533_whelp_tape_run.py'
ADAPTER = ROOT / 'tests/phase533_whelp_business_output.py'
GUARD = ROOT / 'tests/phase533_shared_callback_guard.py'
INPUT = ROOT / 'data/phase511-case029-actual-input-repaired-001'
STATIC_RECEIPT = ROOT / 'data/phase534-b2-source-applicability/source-receipt.json'
SOURCE_FILES = {str(LAUNCHER), str(ADAPTER), str(GUARD)}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def descriptor(path, raw=None):
    path = Path(path)
    if raw is None:
        raw = path.read_bytes()
    return dict(path=str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path), size=len(raw), sha256=sha(raw))


def absolute(row):
    p = Path(row['path'])
    return p if p.is_absolute() else ROOT / p


def read_exact(row):
    p = absolute(row)
    before = p.lstat()
    assert stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and not any(x.is_symlink() for x in p.parents)
    raw = p.read_bytes()
    after = p.stat()
    assert (before.st_ino, before.st_size, before.st_mtime_ns) == (after.st_ino, after.st_size, after.st_mtime_ns)
    assert len(raw) == row['size'] and sha(raw) == row['sha256'], str(p)
    return raw


def save(path, value):
    raw = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False).encode() + b'\n'
    with Path(path).open('xb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    return descriptor(path, raw)


def timeout(signum, frame):
    raise TimeoutError('phase534 fixed wall deadline')


def load_module(path, raw, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def profile_for(counter):
    def profile(frame, event, arg):
        if event == 'call' and frame.f_code.co_filename in SOURCE_FILES and frame.f_code.co_name != '<module>':
            counter[frame.f_code.co_filename + '::' + frame.f_code.co_name] += 1
    return profile


def install_audit(allowed, reads, process_command=None):
    consumed = []
    def audit(event, values):
        if event == 'import' and values[0].split('.')[0] in ('native_replay_v8', 'native_replay_v7', 'headless', 'godot_pcg_integer', 'original_rng'):
            raise RuntimeError('candidate import forbidden')
        if event == 'subprocess.Popen':
            assert process_command is not None and not consumed and list(values[1]) == process_command, 'unapproved subprocess'
            consumed.append(True)
        elif event.startswith(('subprocess.', 'socket.')) or event in ('os.system', 'os.exec', 'os.spawn', 'os.fork', 'os.posix_spawn'):
            raise RuntimeError('forbidden process/network event ' + event)
        if event == 'open' and isinstance(values[0], (str, bytes, os.PathLike)):
            p = Path(os.path.abspath(os.fsdecode(values[0])))
            flags = values[2] or 0
            writing = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
            if writing:
                assert p.is_relative_to(OUTPUT), 'write outside new report'
            else:
                assert str(p) in allowed or p.is_relative_to(OUTPUT), 'read outside exact scope: ' + str(p)
                reads.append(str(p))
    sys.addaudithook(audit)


def child(pins):
    rows = {str(absolute(x)): x for x in pins['files']}
    raw = read_exact(rows[str(LAUNCHER)])
    req = SOURCE / 'invalid-request.json'
    request_raw = read_exact(rows[str(req)])
    counts = collections.Counter()
    reads = []
    install_audit(set(rows), reads)
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(8)
    sys.argv = [str(LAUNCHER), '--config', str(req), '--config-sha256', sha(request_raw), '--output', str(ROOT / 'data/phase533-invalid-534-must-not-exist')]
    sys.setprofile(profile_for(counts))
    error = None
    try:
        exec(compile(raw, str(LAUNCHER), 'exec'), {'__name__': '__main__', '__file__': str(LAUNCHER)})
    except BaseException as exc:
        error = dict(type=type(exc).__name__, message=str(exc))
    finally:
        sys.setprofile(None)
        signal.alarm(0)
    expected = dict(type='ValueError', message='closed17 fixed Root model request/authorization')
    ok = error == expected and counts[str(LAUNCHER)+'::main'] == 1 and counts[str(LAUNCHER)+'::validate_request'] == 1
    ok = ok and not (ROOT / 'data/phase533-invalid-534-must-not-exist').exists()
    forbidden = [n for n in sys.modules if n.split('.')[0] in ('native_replay_v8', 'native_replay_v7', 'headless')]
    ok = ok and not forbidden
    print(json.dumps(dict(status='EXPECTED_REJECTION' if ok else 'UNEXPECTED', error=error, calls=dict(counts), candidate_modules=forbidden, audited_reads=reads)))
    return 17 if ok else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cli-child', action='store_true')
    args = parser.parse_args()
    sys.dont_write_bytecode = True
    pins_raw = (SOURCE / 'pins.json').read_bytes()
    pins = json.loads(pins_raw)
    if args.cli_child:
        return child(pins)
    assert not OUTPUT.exists()
    assert not (ROOT / 'data/phase533-invalid-534-must-not-exist').exists()
    OUTPUT.mkdir(mode=0o700)
    start = time.monotonic()
    report = dict(schema='phase534-independent-exact-controls/1', status='RUNNING', completed=[], top_calls={}, imports={}, calls={}, reads=[], candidate_imports=0, model_calls=0, schema_imports=0, Expected_reads=0, Native_calls=0, actual_UI_reads=0)
    outputs = []
    cache = {}
    counts = collections.Counter()
    tops = collections.Counter()
    reads = []
    loaded = {}
    phase = 'preflight'
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(20)
    try:
        for row in pins['files']:
            cache[str(absolute(row))] = read_exact(row)
        assert str(Path(__file__).resolve()) in cache
        vector = json.loads(cache[str(SOURCE / 'vectors.json')])
        bundle = json.loads(cache[str(INPUT / 'input-bundle.json')])
        witness = json.loads(cache[str(INPUT / 'prepared-witness.json')])
        initial = json.loads(cache[str(INPUT / 'initial-receipt.json')])
        command = [sys.executable, '-I', '-B', str(Path(__file__).resolve()), '--cli-child']
        allowed = set(cache) | {str(SOURCE / 'pins.json'), str(absolute(pins['actual_UI']))}
        install_audit(allowed, reads, command)
        for name, path in [('launcher', LAUNCHER), ('adapter', ADAPTER), ('guard', GUARD)]:
            loaded[name] = load_module(path, cache[str(path)], 'phase534_tested_' + name)
            report['imports'][name] = dict(count=1, file=loaded[name].__file__)
        bound = dict(nodes={n['role']: n for n in bundle['runtime']['processing_nodes']}, items={i['instance_id']: i for s in bundle['fixture']['sides'] for i in s['items']}, inactive_timers={'invu:'+s for s in ('P','O')} | {'aux:'+s+':'+n for s in ('P','O') for n in ('battleRageTimer','autoRageTimer')})
        for case in vector['case_definitions']:
            phase = 'pure_case_' + case['id']
            function = case['function']
            if function == 'validate_prepared_business_view':
                v = copy.deepcopy(vector['synthetic_prepared_view'])
                w = copy.deepcopy(witness)
                mutation = case['mutation']
                if mutation == 'swap_squirrel':
                    v['caches']['P:10'][0:2] = reversed(v['caches']['P:10'][0:2])
                elif mutation == 'foreign_witness_uid':
                    w['items']['P:10']['ordered_cache_aliases'][0]['ordered_native_ids'][0] = vector['foreign_native_id']
                elif mutation == 'bool_basic':
                    v['Basic']['activations'] = False
                elif mutation == 'swap_sapphire':
                    v['Sapphire_types'][0:2] = reversed(v['Sapphire_types'][0:2])
                elif mutation == 'pass_one':
                    v['passes_consumed'] = 1
                arguments = (v, bundle, w, initial)
                target = loaded['launcher']
            else:
                target = loaded['adapter']
                if function == 'project_model_callbacks': arguments = (copy.deepcopy(case['argument']), bound)
                elif function == '_api_pairs': arguments = (copy.deepcopy(case['argument']),)
                elif function == 'first_difference': arguments = (copy.deepcopy(case['left']), copy.deepcopy(case['right']))
                elif function == '_terminal_model': arguments = (copy.deepcopy(case['result']), copy.deepcopy(case['bundle']))
                else: raise AssertionError('unplanned function')
            error = None
            value = None
            tops[function] += 1
            sys.setprofile(profile_for(counts))
            try:
                value = getattr(target, function)(*arguments)
            except BaseException as exc:
                error = dict(type=type(exc).__name__, message=str(exc))
            finally:
                sys.setprofile(None)
            observed = dict(id=case['id'], function=function, error=error, value=value)
            outputs.append(save(OUTPUT / ('case-'+case['id']+'.json'), observed))
            if case['expected'] == 'ValueError':
                assert error == dict(type='ValueError', message=case['message']), observed
            elif case['expected'] == 'DIFFERENCE':
                assert error is None and value['path'] == case['path'] and value['reason'] == case['reason'], observed
            else:
                assert error is None and value['status'] == 'PASS_PRE_ACTIVATION_SAME_INSTANCE', observed
            report['completed'].append(case['id'])
        phase = 'invalid_CLI'
        cli = subprocess.run(command, cwd='/tmp', capture_output=True, timeout=10)
        (OUTPUT / 'invalid-cli.stdout').write_bytes(cli.stdout)
        (OUTPUT / 'invalid-cli.stderr').write_bytes(cli.stderr)
        outputs.extend([descriptor(OUTPUT/'invalid-cli.stdout'), descriptor(OUTPUT/'invalid-cli.stderr')])
        report['invalid_CLI'] = dict(returncode=cli.returncode, command=command, stdout=json.loads(cli.stdout))
        assert cli.returncode == 17 and not cli.stderr and report['invalid_CLI']['stdout']['status'] == 'EXPECTED_REJECTION'
        phase = 'actual_B2'
        report['actual_UI_read_attempts'] = 1
        raw = read_exact(pins['actual_UI'])
        report['actual_UI_reads'] = 1
        tops['extract_shared_callback_guard'] += 1
        report['actual_UI_decode_attempts'] = 1
        sys.setprofile(profile_for(counts))
        try:
            guard = loaded['guard'].extract_shared_callback_guard(raw, bundle, pins['actual_UI'])
        finally:
            sys.setprofile(None)
        extraction = next(x for x in pins['files'] if absolute(x) == GUARD)
        receipt = dict(schema='phase533-owned-shared-callback-closure/1', extraction_source=extraction, guard=guard)
        receipt_pin = save(OUTPUT/'business-closure.json', receipt)
        outputs.append(receipt_pin)
        static = next(x for x in pins['files'] if absolute(x) == STATIC_RECEIPT)
        static_value = json.loads(cache[str(STATIC_RECEIPT)])
        assert static_value['status'] == 'SOURCE_APPLICABILITY_PASS_ACTUAL_WINDOW_PENDING'
        authorities = {r['path']: r for r in static_value['metadata_authorities']}
        assert authorities[guard['input_bundle']['path']] == guard['input_bundle']
        assert authorities[guard['source_basis']['observer_tuple']['path']] == guard['source_basis']['observer_tuple']
        joined = dict(schema='phase534-joined-static-and-actual-B2/1', status='ACCEPTED_FIXED029_CONDITIONAL_CALLBACK_DOMAIN', actual_receipt=receipt_pin, guard_canonical_sha256=sha(canonical(guard)), Source_applicability=static, candidate_freeze=guard['source_basis']['candidate_freeze'], observer_tuple=guard['source_basis']['observer_tuple'], input_bundle=guard['input_bundle'], input_proof=guard['input_proof'], callback_slices=guard['source_basis']['callback_slices'], model_release=False, actual_B1='PENDING_UNIQUE_MODEL_INSTANCE', full_FX_UI_gate_called=False)
        outputs.append(save(OUTPUT/'joined-bindings.json', joined))
        outputs.append(save(OUTPUT/'business-closure-owner.json', dict(schema='phase534-owned-B2-closure-and-Source/1', files=[receipt_pin, static, outputs[-1]])))
        report['B2'] = dict(receipt=receipt_pin, Source_applicability=static, guard_canonical_sha256=joined['guard_canonical_sha256'])
        report['status'] = 'PASS_WRAPPER_CONTROLS_AND_JOINED_B2_NOT_MODEL_VALIDATED'
    except BaseException as exc:
        sys.setprofile(None)
        report['status'] = 'FAILED_STOPPED_NO_RETRY'
        report['first_error'] = dict(phase=phase, type=type(exc).__name__, message=str(exc), traceback=traceback.format_exc())
    finally:
        sys.setprofile(None)
        signal.alarm(0)
    report['elapsed_wall_seconds'] = time.monotonic()-start
    report['top_calls'] = dict(tops)
    report['calls'] = dict(counts)
    report['audit_reads'] = reads
    report['source_and_input_after'] = []
    try:
        for row in pins['files']:
            read_exact(row)
            report['source_and_input_after'].append(row)
        assert (SOURCE/'pins.json').read_bytes() == pins_raw
    except BaseException as exc:
        report['status'] = 'FAILED_AFTER_CHECK'
        report['after_error'] = dict(type=type(exc).__name__, message=str(exc))
    outputs.append(save(OUTPUT/'result.json', report))
    save(OUTPUT/'owned-files.json', dict(schema='phase534-independent-actual-owned/1', files=outputs, pins=descriptor(SOURCE/'pins.json')))
    print(json.dumps({k:report[k] for k in ('status','completed','top_calls','actual_UI_reads','elapsed_wall_seconds')}))
    return 0 if report['status'].startswith('PASS_') else 1


if __name__ == '__main__':
    raise SystemExit(main())
