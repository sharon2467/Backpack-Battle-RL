"""Four new object-argument schema controls; do not rerun the first8."""
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
    contract = json.loads((D / 'object-argument-contract.json').read_text())
    for row in contract['files']:
        assert desc(R / row['path']) == row
    fixtures = json.loads((D / 'object-argument-fixtures.json').read_text())
    out = D / 'object-argument-first-001'
    out.mkdir(exist_ok=False)
    spec = importlib.util.spec_from_file_location('__independent357_object_argument_source__', D / 'SOURCE/phase357_king_observer_schema.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    results = []
    with (out / 'journal.jsonl').open('x') as journal:
        for case in contract['controls']:
            try:
                value = module.validate_record(fixtures[case['fixture']])
            except (ValueError, TypeError, KeyError) as exc:
                accepted, detail = False, dict(type=type(exc).__name__, message=str(exc))
            else:
                accepted, detail = True, dict(return_type=type(value).__name__)
            row = dict(label=case['label'], expected=case['expected'], accepted=accepted,
                       pass_=accepted == (case['expected'] == 'accept'), detail=detail)
            results.append(row)
            journal.write(json.dumps(row, sort_keys=True) + '\n')
            journal.flush()
    failures = [x for x in results if not x['pass_']]
    report = dict(schema='phase357-independent-object-argument-probe/1',
        status='BLOCKED_SOURCE_TYPE_COUNTEREXAMPLE' if failures else 'OBJECT_ARGUMENT_CONTROLS_PASS',
        controls=results, executed=len(results), failures=failures, synthetic_only=True,
        actual_native_evidence=False, schema_module_imports=1, candidate_imports=0,
        RNG_constructions=0, Engine_constructions=0, RuntimeDTO_instances=0,
        models=0, input_builds=0, native=0, capture_reads=0, expected_reads=0)
    with (out / 'report.json').open('x') as f:
        json.dump(report, f, indent=2, sort_keys=True)
        f.write('\n')
    print(json.dumps(dict(status=report['status'], executed=len(results), failures=[x['label'] for x in failures])))


if __name__ == '__main__':
    main()
