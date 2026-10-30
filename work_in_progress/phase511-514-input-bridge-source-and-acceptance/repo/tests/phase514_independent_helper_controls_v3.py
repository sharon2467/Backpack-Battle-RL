"""Frozen finite synthetic helpers only; Root release required before invocation."""
import argparse
import collections
from copy import deepcopy
import dataclasses
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import struct
import sys
import time
import traceback
import types

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / 'data/phase514-independent-control-source-v3'
OUTPUT = REPO / 'data/phase514-independent-controls-v3-001'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()


def descriptor(path):
    raw = path.read_bytes()
    return {'path': str(path.relative_to(REPO)), 'size': len(raw), 'sha256': digest(raw)}


def main():
    started = time.monotonic()
    sys.dont_write_bytecode = True
    sys.pycache_prefix = str(OUTPUT / 'unused-bytecode-cache')
    pins = json.loads((SOURCE / 'pins.json').read_bytes())
    before = []
    raws = {}
    for p in pins['files']:
        path = REPO / p['path']
        raw = path.read_bytes()
        assert len(raw) == p['size'] and digest(raw) == p['sha256'], p['path']
        before.append(dict(p)); raws[p['path']] = raw
    assert not OUTPUT.exists(), 'OUTPUT_ALREADY_EXISTS'
    OUTPUT.mkdir(mode=0o700)
    reads = []
    allowed_reads = {str((REPO / p['path']).resolve()) for p in pins['files']}
    allowed_reads.add(str((SOURCE / 'pins.json').resolve()))
    output_root = str(OUTPUT.resolve()) + os.sep

    def audit(event, args):
        if event == 'open':
            filename, mode, flags = args
            if isinstance(filename, int):
                return
            path = str(Path(os.fsdecode(filename)).absolute())
            writing = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
            if writing:
                if not path.startswith(output_root):
                    raise RuntimeError('WRITE_OUTSIDE_NEW_OUTPUT: ' + path)
            elif path not in allowed_reads and not path.startswith(output_root):
                raise RuntimeError('READ_OUTSIDE_FROZEN_SOURCE: ' + path)
            else:
                reads.append(path)
        if event in ('subprocess.Popen', 'os.system', 'os.posix_spawn', 'socket.connect', 'socket.bind'):
            raise RuntimeError('FORBIDDEN_EXTERNAL_OPERATION: ' + event)
    sys.addaudithook(audit)
    results = []
    top_calls = []
    modules = []
    call_entries = collections.Counter()
    watched = {str((REPO / x).resolve()) for x in (
        'tests/phase511_initial_receipt.py', 'tests/phase513_input_bridge.py',
        'data/phase502-whelp-observer-source-v4/schema/phase502_whelp_observer_schema.py')}
    watched.add('data/phase502-whelp-observer-source-v4/schema/phase502_whelp_observer_schema.py')

    def profile(frame, event, arg):
        if event == 'call' and frame.f_code.co_filename in watched and frame.f_code.co_name != '<module>':
            call_entries[frame.f_code.co_filename + ':' + frame.f_code.co_name] += 1

    def load(name, relative):
        assert name not in sys.modules, 'UNEXPECTED_PRELOADED_SOURCE'
        m = types.ModuleType(name); m.__file__ = str(REPO / relative)
        sys.modules[name] = m
        exec(compile(raws[relative], m.__file__, 'exec'), m.__dict__)
        assert Path(m.__file__).resolve() == (REPO / relative).resolve()
        modules.append({'name': name, 'file': m.__file__})
        return m

    def invoke(case, function, args, check=None):
        snapshot = encode(args)
        top_calls.append({'case': case['id'], 'api': case['api']})
        # The actual schema module object is passed separately by closure, not serialized.
        sys.setprofile(profile)
        try:
            value = function(*args)
        except ValueError as error:
            sys.setprofile(None)
            assert case['outcome'] == 'reject' and str(error) == case['reason'], (case['id'], type(error).__name__, str(error))
            assert encode(args) == snapshot, 'ARGUMENT_MUTATION'
            results.append({'case': case['id'], 'api': case['api'], 'status': 'PASS_EXPECTED_REJECTION', 'reason': str(error)})
            return None
        finally:
            sys.setprofile(None)
        assert case['outcome'] == 'accept', 'MISSING_REQUIRED_REJECTION: ' + case['id']
        assert encode(args) == snapshot, 'ARGUMENT_MUTATION'
        if check is not None:
            check(value)
        results.append({'case': case['id'], 'api': case['api'], 'status': 'PASS_ACCEPTED'})
        return value

    error = None
    try:
        initial = load('phase511_initial_receipt', 'tests/phase511_initial_receipt.py')
        bridge = load('phase514_reviewed_bridge', 'tests/phase513_input_bridge.py')
        v = json.loads(raws['data/phase514-independent-control-source/vectors.json'])
        cases = v['cases']; assert len(cases) == 12
        schema_path = 'data/phase502-whelp-observer-source-v4/schema/phase502_whelp_observer_schema.py'
        # Case01 needs bytes, not JSON arguments; profile and record the real loader once.
        top_calls.append({'case': '01', 'api': cases[0]['api']})
        sys.setprofile(profile)
        try:
            schema = bridge.load_schema(raws[schema_path])
        finally:
            sys.setprofile(None)
        schema_file = Path(schema.__file__)
        resolved_schema_file = (schema_file if schema_file.is_absolute() else bridge.REPO / schema_file).resolve()
        assert resolved_schema_file == (REPO / schema_path).resolve()
        modules.append({'name': schema.__name__, 'file': schema.__file__})
        assert schema.VERSION == '7-whelp-family-A-502'
        results.append({'case': '01', 'api': cases[0]['api'], 'status': 'PASS_ACCEPTED'})
        context_raw = raws['data/phase513-input-bridge-source/source-context.json']
        request = deepcopy(v['request_descriptor_only'])

        def authenticate(req, ctx):
            rr = encode(req); cr = bytes.fromhex(ctx)
            pin = {'path': 'data/phase514-synthetic-never-read/request.json', 'size': len(rr), 'sha256': digest(rr)}
            return bridge.authenticate_request(rr, pin, cr)

        invoke(cases[1], authenticate, [request, context_raw.hex()])
        bad = deepcopy(request); bad['models_allowed'] = False
        invoke(cases[2], authenticate, [bad, context_raw.hex()])
        ctx = json.loads(context_raw)
        p = next(p for p in ctx['source_pins'] if p['path'] == 'data/phase513-input-bridge-source/abi.json')
        p['path'] = 'data/phase514-synthetic-never-read/Expected.json'
        cr = encode(ctx); bad = deepcopy(request)
        bad['source_context'] = {'path': 'data/phase514-synthetic-never-read/context.json', 'size': len(cr), 'sha256': digest(cr)}
        invoke(cases[3], authenticate, [bad, cr.hex()])
        t = v['timer']
        timer_call = lambda wrapper, parent, role: initial.validate_timer(wrapper, parent, role, schema)
        invoke(cases[4], timer_call, [deepcopy(t['wrapper']), t['parent'], t['role']])
        bad = deepcopy(t['wrapper']); bad['timer']['process_mode'] = False
        invoke(cases[5], timer_call, [bad, t['parent'], t['role']])
        ledger_call = lambda facts, role, owner, timer: initial.validate_ledger(facts, role, owner, timer, schema)
        invoke(cases[6], ledger_call, [v['early_start_ledger'], t['role'], t['parent'], t['wrapper']['timer']])
        cache_call = lambda value, aliases: initial.validate_cache_alias(value, aliases, schema, current=False)
        invoke(cases[7], cache_call, [v['cache_foreign'], v['aliases']])
        decoded = {'observer7-primitives.jsonl': deepcopy(v['branch_rows'])}

        def branch_check(value):
            assert value['value'] is True and len(value['witnesses']) == 2
            assert [w['native_owner'] for w in value['witnesses']] == [v['aliases']['role_to_native'][x] for x in ('O:2', 'O:3')]
            assert [w['line'] for w in value['witnesses']] == [1, 2]
            assert 'not direct rank' in value['limits']

        invoke(cases[8], bridge.derive_branch_witness, [decoded, v['aliases']], branch_check)
        bad = deepcopy(decoded); bad['observer7-primitives.jsonl'][1]['site'] = 'Items/Item.gd::adjustCooldown:other'
        invoke(cases[9], bridge.derive_branch_witness, [bad, v['aliases']])
        bad = deepcopy(decoded); bad['observer7-primitives.jsonl'][0]['payload']['label'] = 'cooldown:O:999'
        invoke(cases[10], bridge.derive_branch_witness, [bad, v['aliases']])

        def prepared_check(value):
            assert value['status'] == 'OBSERVED_INPUT_NOT_MODEL_EQUIVALENCE'
            assert value['gate'] == 'EXTERNAL_SAME_INSTANCE_BUSINESS_PREPARE_GATE_REQUIRED_BEFORE_ACTIVATION'
            assert list(value['items']) == list(v['prepared_receipt']['prepare_observations']['pre_activate'])
            for role, item in value['items'].items():
                original = v['prepared_receipt']['prepare_observations']['pre_activate'][role]
                assert item['cachedAffectedItems'] == original['cachedAffectedItems']
                assert item['currentAffectedItems'] == original['currentAffectedItems']
                assert [x['color']['decimal'] for x in item['ordered_cache_aliases']] == ['7', '0', '4', '2']
                for x in item['ordered_cache_aliases']:
                    assert x['ordered_roles'] == ['O:2', 'P:1']
                    assert x['ordered_native_ids'] == [v['aliases']['role_to_native'][r] for r in ('O:2', 'P:1')]
                for x in item['ordered_current_aliases']:
                    assert [m['role'] for m in x['ordered_members']] == ['P:1', 'O:2']
            assert value['items']['P:9']['goobert_state'] == v['prepared_receipt']['prepare_observations']['pre_activate']['P:9']['goobert_state']
            assert [x['decimal'] for x in value['items']['P:14']['stackTypes']['values']] == ['101', '102', '103', '104', '106', '107']

        invoke(cases[11], bridge.project_prepared_witnesses, [{}, v['aliases'], v['prepared_receipt']], prepared_check)
        assert len(top_calls) == len(results) == 12
    except Exception as exc:
        sys.setprofile(None)
        frames = []
        tb = exc.__traceback__
        while tb is not None:
            frames.append({'file': tb.tb_frame.f_code.co_filename, 'line': tb.tb_lineno, 'function': tb.tb_frame.f_code.co_name})
            tb = tb.tb_next
        error = {'type': type(exc).__name__, 'reason': str(exc), 'frames': frames}
    after = [descriptor(REPO / p['path']) for p in pins['files']]
    if before != after and error is None:
        error = {'type': 'SourceDrift', 'reason': 'source/input pins differ after finite batch'}
    record = {'schema': 'phase514-independent-finite-controls/1', 'status': 'PASS_SYNTHETIC_HELPERS_ONLY' if error is None else 'FIRST_ERROR_STOPPED',
              'results': results, 'error': error, 'top_level_calls': top_calls, 'top_level_calls_entered': len(top_calls),
              'loaded_source_modules': modules, 'production_function_entry_counts': dict(call_entries),
              'nested_entries_include_schema_and_shared_predicates_not_extra_top_cases': True,
              'source_before': before, 'source_after': after, 'io_reads_after_audit': reads,
              'wall_seconds': time.monotonic() - started, 'synthetic_only': True,
              'counts': {'complete_projection': 0, 'actual_INPUT_reads': 0, 'raw12_constructed': 0, 'build': 0, 'model': 0, 'Native': 0, 'Expected': 0, 'pool': 0},
              'limits': 'No actual72 provenance or same-instance business prepare validation; no full decoded capture or input bundle.'}
    out = OUTPUT / 'result.json'; out.write_bytes(encode(record))
    owner = {'schema': 'phase514-control-output-owner/1', 'files': [descriptor(out)]}
    (OUTPUT / 'owned-files.json').write_bytes(encode(owner))
    print(json.dumps({'status': record['status'], 'top_calls': len(top_calls), 'passed': len(results), 'result': descriptor(out)}, sort_keys=True))
    return 0 if error is None else 1


if __name__ == '__main__':
    raise SystemExit(main())
