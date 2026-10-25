"""One bounded real-schema run; no candidate/model/input-build/native access."""
import ast
from collections import Counter
import copy
import dataclasses
import difflib
import hashlib
import json
import math
import os
from pathlib import Path
import pprint
import re
import struct
import sys
import sysconfig
import types

R = Path(__file__).resolve().parents[1]
D = R / 'data/phase358-independent-schema-review'


def desc(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(R)), size=len(b), sha256=hashlib.sha256(b).hexdigest())


def main():
    # Trusted bootstrap: this script/stdlib and exact manifested SOURCE/JSON
    # metadata. No actual schema or generator is imported before the audit hook.
    contract = json.loads((D / 'source-contract.json').read_text())
    for row in contract['files']:
        assert desc(R / row['path']) == row
    source_owner_pin = desc(D / 'source-owner.json')
    cases = json.loads((D / 'cases.json').read_text())
    assert len(cases) == 80 and [x['id'] for x in cases] == list(range(1, 81))
    out = D / 'controls-first-001'
    out.mkdir(exist_ok=False)
    allowed = {str((R / row['path']).resolve()) for row in contract['files']}
    allowed.add(str((D / 'source-contract.json').resolve()))
    stdlib = Path(sysconfig.get_path('stdlib')).resolve()
    out_root = out.resolve()
    audit = dict(reads=[], writes=[], blocked=[])
    def below(p, root):
        return p == root or root in p.parents
    def hook(event, args):
        if event == 'open':
            path = args[0]
            if isinstance(path, int):
                return
            p = Path(os.fsdecode(path)).absolute().resolve()
            mode, flags = args[1], args[2]
            writing = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)) if isinstance(flags, int) else bool(mode and any(x in mode for x in 'wax+'))
            permitted = below(p, out_root) if writing else str(p) in allowed or below(p, out_root) or (below(p, stdlib) and not {'site-packages', 'dist-packages'} & set(p.parts))
            if not permitted:
                audit['blocked'].append(dict(event=event, path=str(p), writing=writing))
                raise PermissionError('phase358 closed file boundary')
            audit['writes' if writing else 'reads'].append(str(p))
        elif event.startswith('socket.') or event in ('subprocess.Popen', 'os.system', 'os.posix_spawn', 'os.posix_spawnp', 'os.exec', 'os.fork'):
            audit['blocked'].append(dict(event=event))
            raise PermissionError('phase358 network/process boundary')
    sys.addaudithook(hook)

    def source_module(name, p):
        module = types.ModuleType(name)
        module.__file__ = str(p)
        sys.modules[name] = module
        exec(compile(p.read_bytes(), str(p), 'exec'), module.__dict__)
        return module
    schema = source_module('__independent358_real_schema__', D / 'SOURCE/schema.py')
    mapper = source_module('__independent358_real_mapper__', D / 'SOURCE/mapper.py')
    calls = Counter()
    def invoke(name, *args, **kwargs):
        calls[name] += 1
        return getattr(schema, name)(*args, **kwargs)
    results = []
    with (out / 'journal.jsonl').open('x') as journal:
        for case in cases:
            operation, data = case['operation'], case['data']
            try:
                if operation == 'API':
                    assert schema.VERSION == '7-king-single-A-355' and schema.PROFILE == 'observer7-355-native-single-king-A/1'
                    assert schema.schema.validate_state is schema.validate_state and schema.NATIVE_AUTHORIZED is False
                    value = True
                elif operation == 'STATE':
                    value = invoke('validate_state', data, case['kind'])
                elif operation == 'TYPED':
                    value = invoke('validate_typed', data)
                elif operation == 'RECORD':
                    value = invoke('validate_record', data)
                elif operation == 'MAPPER':
                    calls['SOURCE_MAPPER.arguments'] += 1
                    value = mapper.arguments(data)
                    if 'returns' in case and dict(names=value[0], types=value[1]) != case['returns']:
                        raise ValueError('mapper return differs from presealed SOURCE typing')
                elif operation == 'CACHE':
                    value = invoke('validate_cache', data, True)
                elif operation == 'PRIMITIVE':
                    value = invoke('validate_primitive', data)
                elif operation == 'CLOCK':
                    value = invoke('decode_clock', data)
                elif operation == 'TERMINAL':
                    clock = invoke('decode_clock', data['clock'])
                    value = invoke('validate_terminal_evidence', data['endpoint'], clock, data['cleanup'])
                elif operation == 'OBSERVATIONS':
                    value = invoke('validate_observation_records', data['records'], data['identity'])
                elif operation == 'UI':
                    value = invoke('validate_single_king_ui_authority', data)
                elif operation == 'STREAM':
                    value = invoke('decode_sources', {k: v.encode('utf-8') for k, v in data.items()})
                elif operation == 'RESOURCES':
                    value = invoke('validate_resources', data['panels'], data['nodes'])
                else:
                    raise AssertionError('unrecognized presealed operation ' + operation)
            except (ValueError, TypeError, KeyError) as exc:
                accepted, detail = False, dict(type=type(exc).__name__, message=str(exc))
            except Exception as exc:
                row = dict(id=case['id'], label=case['label'], expected=case['expected'], accepted=None,
                           pass_=False, checker_error=dict(type=type(exc).__name__, message=str(exc)))
                results.append(row)
                journal.write(json.dumps(row, sort_keys=True) + '\n')
                journal.flush()
                raise
            else:
                accepted, detail = True, dict(return_type=type(value).__name__)
            row = dict(id=case['id'], label=case['label'], expected=case['expected'], accepted=accepted,
                       pass_=accepted == (case['expected'] == 'accept'), detail=detail)
            results.append(row)
            journal.write(json.dumps(row, sort_keys=True) + '\n')
            journal.flush()
    failures = [x for x in results if not x['pass_']]
    report = dict(schema='phase358-independent-real-schema-controls/1',
        status='BOUNDED_SCHEMA_CONTROLS_PASS' if not failures else 'BLOCKED_SOURCE_SEMANTIC_COUNTEREXAMPLE',
        executed=len(results), unique_cases=80, required_version_regression_cases=12, new_unique_cases=68,
        controls=results, failures=failures, top_level_calls=dict(calls), top_level_call_total=sum(calls.values()),
        recursive_internal_calls='NOT_COUNTED', schema_module_imports=1, pure_mapper_module_imports=1,
        actual_native_evidence=False, synthetic_only=True, candidate_imports=0,
        RNG_constructions=0, Engine_constructions=0, RuntimeDTO_instances=0,
        input_builds=0, models=0, native=0, capture_reads=0, expected_file_reads=0,
        expected_shape_data='Presealed synthetic Timer/terminal objects only;no external expected data',
        full_source_carriers_or_bundle_positive=False, scope=contract['trusted_bootstrap'])
    with (out / 'report.json').open('x') as f:
        json.dump(report, f, indent=2, sort_keys=True)
        f.write('\n')
    files = [desc(out / n) for n in ('journal.jsonl', 'report.json')]
    with (out / 'open-audit.json').open('x') as f:
        json.dump(dict(schema='phase358-independent-file-audit/1', **audit,
            trusted_bootstrap='Stdlib,script and manifested SOURCE/metadata pins read beforehook;actual two SOURCE modules loaded afterhook',
            allowed_file_count=len(allowed), stdlib=str(stdlib), third_party='Excluded bysite-packages/dist-packages path',
            recording_cut='After journal/report actual readback through opening thisaudit file. Later only itsreadback, jointseal/stdout;hook remains enforcing.',
            no_claim_of_explicit_third_party_or_network_attack_test=True), f, indent=2, sort_keys=True)
        f.write('\n')
    files.append(desc(out / 'open-audit.json'))
    with (out / 'joint-seal.json').open('x') as f:
        json.dump(dict(schema='phase358-independent-schema-output-jointseal/1', files=files,
                       source_owner=source_owner_pin), f, indent=2, sort_keys=True)
        f.write('\n')
    print(json.dumps(dict(status=report['status'], controls=len(results), failures=[x['label'] for x in failures], calls=sum(calls.values()), blocked=len(audit['blocked']))))


if __name__ == '__main__':
    main()
