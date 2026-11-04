"""Five fixed provenance controls; no candidate import, model run or comparison."""
from pathlib import Path
from collections import Counter
from copy import deepcopy
import argparse
import hashlib
import json
import math
import os
import re
import signal
import stat
import struct
import sys
import time
import traceback
import types

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / 'data/phase540-exact-control-source'
OUT = ROOT / 'data/phase540-independent-controls-first-001'
ADAPTER = 'tests/phase539_whelp_business_output.py'
MODEL_DIR = 'data/phase533-case029-actual-model-first-001/'
BINDING = 'data/phase539-sealed-sapphire-provenance-source/comparison-binding-template.json'
WATCH = ('bindings', 'project_model_final', 'validate_sapphire_gate_origin',
         'project_model', 'project_native', 'compare_decoded', 'compare_projected')


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pins-sha256', required=True)
    args = parser.parse_args()
    OUT.mkdir(exist_ok=False)
    started = time.monotonic()
    report = dict(schema='phase540-independent-provenance-controls/1', status='RUNNING',
                  completed=[], cases=[], direct_calls=[], entered={}, adapter_imports=0,
                  candidate_imports=0, model_runs=0, Expected_payload_reads=0,
                  Native_runs=0, comparisons=0)
    reads = []
    calls = Counter()
    files = {}
    cached = {}
    refs = []
    stage = 'pins'

    def dump(name, value):
        raw = (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2)+'\n').encode()
        path = OUT / name
        with path.open('xb') as f:
            f.write(raw)
            f.flush()
            os.fsync(f.fileno())
        row = dict(path=str(path.relative_to(ROOT)), size=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        refs.append(row)
        return row

    def read(row, phase):
        path = ROOT / row['path']
        before = path.lstat()
        assert stat.S_ISREG(before.st_mode) and before.st_nlink == 1
        assert not any(p.is_symlink() for p in (path, *path.parents))
        raw = path.read_bytes()
        after = path.stat()
        assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) == (
            after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        actual = dict(path=row['path'], size=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        assert actual == row, 'exact pin '+row['path']
        reads.append(dict(phase=phase, **actual))
        return raw

    def load(name):
        def pairs(values):
            result = {}
            for key, value in values:
                assert key not in result, 'duplicate JSON key'
                result[key] = value
            return result
        def invalid(value):
            raise ValueError('nonfinite JSON '+value)
        return json.loads(cached[name], object_pairs_hook=pairs, parse_constant=invalid)

    def timeout(signum, frame):
        raise TimeoutError('15-second provenance-control wall limit')

    def profile(frame, event, arg):
        if event == 'call' and frame.f_code.co_filename == str(ROOT/ADAPTER):
            name = frame.f_code.co_name
            if name in WATCH:
                calls[name] += 1

    def call(name, *values):
        report['direct_calls'].append(name)
        sys.setprofile(profile)
        try:
            return getattr(adapter, name)(*values)
        finally:
            sys.setprofile(None)

    def rejected(case, reason, name, *values):
        try:
            call(name, *values)
        except ValueError as exc:
            assert str(exc) == reason, 'unexpected first rejection: '+str(exc)
            report['cases'].append(dict(case=case, status='PASS_EXPECTED_REJECTION',
                                        first_rejection=str(exc)))
            report['completed'].append(case)
        else:
            raise AssertionError('negative accepted: '+case)

    signal.signal(signal.SIGALRM, timeout)
    signal.setitimer(signal.ITIMER_REAL, 15)
    try:
        pins_raw = (STAGE/'pins.json').read_bytes()
        assert hashlib.sha256(pins_raw).hexdigest() == args.pins_sha256
        pins = json.loads(pins_raw)
        files = {row['path']:row for row in pins['files']}
        assert len(files) == len(pins['files'])
        allowed = {str(ROOT/name) for name in files} | {str(STAGE/'pins.json')}
        def audit(event, values):
            if event == 'open' and not isinstance(values[0], int):
                path = os.path.abspath(os.fspath(values[0]))
                mode, flags = values[1:3]
                writing = (isinstance(mode, str) and any(c in mode for c in 'wax+')) or (
                    isinstance(flags, int) and bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC)))
                if writing:
                    assert path.startswith(str(OUT)+os.sep), 'write outside new report'
                else:
                    assert path in allowed or path.startswith(str(OUT)+os.sep), 'read outside exact pins: '+path
            elif event.startswith(('socket.', 'subprocess.')) or event in ('os.system', 'os.fork', 'os.posix_spawn'):
                raise RuntimeError('forbidden external operation '+event)
            elif event == 'import' and values[0].startswith(('native_replay', 'headless', 'original_rng', 'godot_pcg')):
                raise RuntimeError('candidate import forbidden')
        sys.addaudithook(audit)
        sys.dont_write_bytecode = True
        stage = 'authenticate_all_pins'
        for name, row in files.items():
            cached[name] = read(row, 'before')
        vectors = load('data/phase540-exact-control-source/vectors.json')
        assert vectors['case_ids'] == ['01','02','03','04','05']
        binding = load(BINDING)
        seal = load(MODEL_DIR+'output-seal.json')
        before = load(MODEL_DIR+'before.json')
        execution = load(MODEL_DIR+'execution.json')
        request = load('data/phase535-root-actual029-model-request/model-request.json')
        for name in ('model-output.json', 'prepare-gate.json', 'before.json', 'execution.json'):
            assert seal['files'][name] == {k:files[MODEL_DIR+name][k] for k in ('size','sha256')}
        assert seal['request'] == dict(files['data/phase535-root-actual029-model-request/model-request.json'],
                                     path=str(ROOT/'data/phase535-root-actual029-model-request/model-request.json'))
        assert seal['status'] == execution['status'] == 'ACTUAL_OUTPUT_SEALED_NOT_COMPARED'
        assert seal['comparison_contract'] == binding['contract']
        assert request['root_model_authorized'] is True
        assert execution['calls'] == dict(candidate_import_attempts=1,construct_attempts=1,
            prepare_attempts=1,prepared_gate_attempts=1,activate_attempts=1,full_run_attempts=1)
        assert execution['expected_reads'] == execution['new_original_capture'] == execution['comparator_calls'] == 0
        assert before['sources'] == execution['source_after'] and len(before['sources']) == 15
        for path, row in before['sources'].items():
            relative = str(Path(path).relative_to(ROOT))
            assert files[relative] == dict(row, path=relative)
        assert before['launcher'] == request['launcher']
        assert before['execution_request'] == seal['request']
        for name in ('input_bundle','input_proof','candidate_freeze'):
            assert before[name] == binding[name] == request[name]
        bundle = load(binding['input_bundle']['path'])
        proof = load(binding['input_proof']['path'])
        gate = load(binding['prepare_gate']['path'])
        assert request['prepared_witness'] == gate['input_witness']
        result = load(MODEL_DIR+'model-output.json')
        assert canonical(bundle) == binding['input_canonical_sha256']
        assert canonical(proof) == binding['input_proof_canonical_sha256']
        assert canonical(gate) == binding['prepare_gate_canonical_sha256']
        dump('before.json', dict(source_and_input_pins=list(files.values()), original_seal=seal,
                                 execution_calls=execution['calls'], five_cases=vectors))
        stage = 'adapter_import'
        adapter = types.ModuleType('phase540_adapter')
        adapter.__file__ = str(ROOT/ADAPTER)
        report['adapter_imports'] += 1
        exec(compile(cached[ADAPTER], str(ROOT/ADAPTER), 'exec'), adapter.__dict__)

        stage = '01_original_model_final_projection'
        bound = call('bindings', bundle, proof, binding)
        final = call('project_model_final', result, bound, gate, binding)
        char = next(c for c in final['native_rule_state']['characters'] if c['instance']=='P')
        item = next(i for i in char['items'] if i['instance']=='P:14')
        actual = item['fields']['stackTypes']
        measured = gate['view']['Sapphire_types']
        assert type(actual) is list and len(actual) == 6 and all(type(x) is int for x in actual)
        assert actual == measured and actual is not measured
        report['positive_projection'] = dump('model-final-projection.json', final)
        report['cases'].append(dict(case='01',status='PASS_MODEL_FINAL_ONLY',stackTypes=actual,
                                    value_origin='original sealed gate /view/Sapphire_types'))
        report['completed'].append('01')

        stage = '02_missing_gate_binding'
        bad_binding = deepcopy(binding)
        del bad_binding[vectors['missing_binding_key']]
        rejected('02', 'closed fixed029 external comparison binding', 'bindings', bundle, proof, bad_binding)
        stage = '03_gate_canonical_mutation'
        bad_gate = deepcopy(gate)
        bad_gate['view']['passes_consumed'] = vectors['mutated_passes_consumed']
        rejected('03', 'exact original sealed gate canonical identity', 'validate_sapphire_gate_origin', bad_gate, result, bound, binding)
        stage = '04_report_view_disagreement'
        bad_gate = deepcopy(gate)
        bad_gate['gate']['Sapphire_types'][0] += vectors['report_first_element_delta']
        rejected('04', 'exact original sealed gate canonical identity', 'validate_sapphire_gate_origin', bad_gate, result, bound, binding)
        stage = '05_final_identity_mismatch'
        bad_result = dict(result)
        bad_result['final'] = dict(result['final'])
        bad_result['final']['items'] = dict(result['final']['items'])
        bad_result['final']['items']['P:14'] = dict(result['final']['items']['P:14'])
        bad_result['final']['items']['P:14']['item_index'] = vectors['wrong_final_item_index']
        rejected('05', 'same instance final/bound Sapphire subtype', 'validate_sapphire_gate_origin', gate, bad_result, bound, binding)
        assert dict(calls) == dict(bindings=2, project_model_final=1, validate_sapphire_gate_origin=4)
        assert len(report['direct_calls']) == 6
        report['status'] = 'PASS_FIVE_PROVENANCE_CONTROLS_NOT_NATIVE_COMPARISON'
    except BaseException as exc:
        report['status'] = 'FAIL_FIRST_UNEXPECTED'
        report['failure'] = dict(stage=stage,type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
        dump('first-error.json', report['failure'])
    finally:
        sys.setprofile(None)
        signal.setitimer(signal.ITIMER_REAL, 0)
        try:
            for row in files.values():
                read(row, 'after')
            report['pins_after_unchanged'] = bool(files)
        except BaseException as exc:
            report['status'] = 'FAIL_FIRST_UNEXPECTED'
            report['after_failure'] = dict(type=type(exc).__name__,message=str(exc))
        report['entered'] = dict(calls)
        report['elapsed_wall_seconds'] = time.monotonic()-started
        report['physical_reads'] = reads
        report['limits'] = ['Cases03/04 reject canonical identity; no deep report/type branch execution claim.',
                            'Final projection JSON is diagnostic only; no business equality or support expansion.',
                            'Original sealed model read/hash before and after, decoded once; not rerun.']
        dump('result.json', report)
        dump('owned-files.json', dict(schema='phase540-actual-controls-owner/1',files=list(refs)))
    return 0 if report['status'].startswith('PASS_') else 1


if __name__ == '__main__':
    raise SystemExit(main())
