"""First bounded independent probe of the actual standalone schema; no models."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

R = Path(__file__).resolve().parents[1]
D = R / 'data/phase357-independent-schema-review'


def desc(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(R)), size=len(b), sha256=hashlib.sha256(b).hexdigest())


def main():
    contract = json.loads((D / 'probe-contract.json').read_text())
    for row in contract['source_files']:
        assert desc(R / row['path']) == row
    fixtures = json.loads((D / 'synthetic-probe-fixtures.json').read_text())
    out = D / 'probe-first-001'
    out.mkdir(exist_ok=False)
    p = D / 'SOURCE/phase357_king_observer_schema.py'
    spec = importlib.util.spec_from_file_location('__independent357_real_pure_schema__', p)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    results = []
    with (out / 'journal.jsonl').open('x') as journal:
        for case in contract['controls']:
            label, expected = case['label'], case['expected']
            try:
                if case['operation'] == 'API':
                    assert module.VERSION == '7-king-single-A-355'
                    assert module.PROFILE == 'observer7-355-native-single-king-A/1'
                    assert module.schema.validate_state is module.validate_state
                    assert module.NATIVE_AUTHORIZED is False
                    value = True
                elif case['operation'] == 'state':
                    value = module.validate_state(fixtures[case['fixture']], case['kind'])
                else:
                    value = module.validate_typed(fixtures[case['fixture']])
            except (ValueError, TypeError, KeyError) as exc:
                accepted = False
                detail = dict(type=type(exc).__name__, message=str(exc))
            except Exception as exc:
                row = dict(label=label, expected=expected, accepted=None, pass_=False,
                           checker_error=dict(type=type(exc).__name__, message=str(exc)))
                results.append(row)
                journal.write(json.dumps(row, sort_keys=True) + '\n')
                journal.flush()
                raise
            else:
                accepted = True
                detail = dict(return_type=type(value).__name__)
            row = dict(label=label, expected=expected, accepted=accepted,
                       pass_=accepted == (expected == 'accept'), detail=detail)
            results.append(row)
            journal.write(json.dumps(row, sort_keys=True) + '\n')
            journal.flush()
    assert len(results) == 8 <= 80
    failures = [x for x in results if not x['pass_']]
    report = dict(schema='phase357-independent-first-pure-schema-probe/1',
                  status='BLOCKED_SOURCE_SEMANTIC_COUNTEREXAMPLE' if failures else 'PROBE_PASS_MORE_OBLIGATIONS_PENDING',
                  module=desc(p), controls=results, executed=len(results), failures=failures,
                  synthetic_only=True, actual_native_evidence=False, schema_module_imports=1,
                  candidate_imports=0, Engine_constructions=0, RNG_constructions=0,
                  RuntimeDTO_instances=0, input_builds=0, models=0, native=0,
                  capture_reads=0, expected_reads=0,
                  boundary='-I-B-S import of exact real standalone schema, no closed-file audit hook claim')
    with (out / 'report.json').open('x') as f:
        json.dump(report, f, indent=2, sort_keys=True)
        f.write('\n')
    print(json.dumps(dict(status=report['status'], executed=len(results), failures=[x['label'] for x in failures])))


if __name__ == '__main__':
    main()
