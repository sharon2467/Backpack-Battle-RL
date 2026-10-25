"""Output-only final metadata; never re-execute source controls or a candidate."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[1]
D = R / 'data/phase356-independent-source-review'
A = R / 'data/phase356-king-admission-source-repair'


def desc(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(R)), size=len(b), sha256=hashlib.sha256(b).hexdigest())


def write(name, obj):
    with (D / name).open('x') as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write('\n')


def main():
    report = json.loads((D / 'controls-first-001/report.json').read_text())
    static = json.loads((D / 'static-review.json').read_text())
    contract = json.loads((D / 'regression-contract.json').read_text())
    assert report['executed'] == 68 and report['reused52'] == 52
    assert all(x['pass_'] for x in report['controls']) and not report['expected_failclosed_violations']
    expected = {x['label']: x['expected'] for x in contract['base_controls']}
    actual = {x['label']: x['expected'] for x in report['controls'][:52]}
    assert len(expected) == len(actual) == len(contract['base_controls']) == 52 and actual == expected
    assert static['status'] == 'PASS' and not (D / 'controls-first.stderr.txt').read_bytes()
    counts = dict(original_controls=52, supplement_controls=16, total_controls=68,
                  positive=sum(x['accepted'] for x in report['controls']),
                  rejections=sum(not x['accepted'] for x in report['controls']), failures=0,
                  candidate_imports=0, RNG_constructions=0, Engine_constructions=0,
                  RuntimeDTO_instances=0, initializations=0, steps=0,
                  input_builds=0, models=0, native=0, expected_reads=0)
    assert counts['positive'] == 6 and counts['rejections'] == 62
    coverage = dict(schema='phase356-independent-source-coverage/1', rows=[
        dict(obligation='Author23 identities/15modules/13bytes/old complete modules', status='OBSERVED_STATIC_PASS', evidence='static-review.json:23 leaves622877B;compile15; only shared guard and3calls inverse to complete355 AST. Old profiles,patch,helpers and runtime kernels preserved.'),
        dict(obligation='Shared no-parameter,unconditional pending guard/3entry sites', status='EXACT_AST_PURE_AND_STATIC_PASS', evidence='genuine input77/result150/runtime959 invoke same host-code guard; no args/branch/opening flag. Supplemental exact pending reasons all matched.'),
        dict(obligation='Original52 SOURCE controls', status='52_OF_52_PASS', evidence='Same bodies/unique labels; only2domain expectations change accept->reject. Old307 patch alone passes;new-profile composition now rejects. First355false-accept remains frozen.'),
        dict(obligation='Minimum caller-flag/3entry/old-profile supplement', status='16_OF_16_PASS', evidence='Flags/oldpatch cannot open;malformed/no fixture cannot precede guard;existing headless input/result positives and unknown/wrong-mode rejects preserved.'),
        dict(obligation='Runtime exact AST import boundary', status='OBSERVED_PURE_INTERFACE_PASS', evidence='Complete validator AST and actual RuntimeDTO class defined without instantiation. Four relative genuine imports resolve to in-memory exact shared functions;no staged module import/fake observer schema.'),
        dict(obligation='Pre-RNG/direct Engine/observed/comparator entry', status='SOURCE_ORDER_PASS_NOT_RUNTIME_EXECUTION', evidence='All direct calls retained separately:validate1187 then defaultSeed1188 thenfallback1189;observed validation17 beforeSeed21/Tape24/Engine25. New result guard precedes comparator Path/file access.'),
        dict(obligation='Character/King field type erratum', status='SOURCE_CONFIRMED_NO_RUNTIME_CHANGE', evidence='Character.buffProtectStacks INT declaration;King.protectedBuffs REAL3 callsite;engine +=int(amount) remains unchanged. Both SOURCE/typed-erratum and original excerpt frozen;old355matrix untouched.'),
        dict(obligation='Future native source schema/patch/collector/11actual inputs/adapter/host', status='PENDING_CLOSED_NOT_ADMITTED', evidence='No complete native positive fabricated. Future opening requires jointly code-bound observer/schema/patch/generator/report source and independent controls;not a flag flip/removingraise.'),
    ], counts=counts, control_inventory_note='Only independently executed proof-key control inventory uses unique-label matching;actual report order and every business stream remain untouched.')
    write('coverage.json', coverage)
    execution = dict(schema='phase356-independent-execution-receipt/1',
        command='python3 -I -B -S tests/phase356_independent_source_controls.py', attempt=1, exit_code=0,
        stdout=desc(D / 'controls-first.stdout.txt'), stderr=desc(D / 'controls-first.stderr.txt'),
        report=desc(D / 'controls-first-001/report.json'), static_report=desc(D / 'static-review.json'),
        source_owner=desc(D / 'source-owner.json'), counts=counts,
        isolation='-I-B-S stdlib/exact-AST SOURCE execution; no closed-file audit hook claim',
        runtime_source_boundary=report['supplement'], old_science_batches_rerun=0,
        metadata_first_failure=desc(D / 'metadata-first-failure.json'))
    write('execution-receipt.json', execution)
    review = dict(schema='phase356-independent-pending-admission-review/1',
        status='INDEPENDENT356_SHARED_PENDING_ADMISSION_SOURCE_REPAIR_ACCEPTED_NATIVE_CLOSED',
        accepted_source_repair=True, new_genuine_profile_admitted=False, native_ready=False,
        King_production_admitted=False, formal_production_accepted_bounded=75, full_engine_RL='IN_PROGRESS',
        candidate_source_freeze=desc(A / 'candidate-source-freeze.json'),
        author_source_owner=desc(A / 'source-owner.json'), source_control_owner=desc(D / 'source-owner.json'),
        closed_finding=desc(R / 'data/phase355-independent-source-review/finding.json'),
        preserved355_failure_owner=desc(R / 'data/phase355-independent-source-review/owned-files.json'),
        evidence=dict(static=desc(D / 'static-review.json'), regression=desc(D / 'controls-first-001/report.json'),
                      coverage=desc(D / 'coverage.json'), execution=desc(D / 'execution-receipt.json')),
        conclusion='Shared unconditional pending gate repairs355 source admission gap. Approved old307 patch alone remains valid;new-profile composition and all3entry routes reject. Accepted only as a CLOSED first SOURCE component.',
        future_required='Freeze complete observer/schema/patch/generator/report joint profile binding at input/runtime/result/comparator before reopening;reject old307/oldKing substitution. No collector or runnable native profile accepted now.',
        typed_erratum='Character.buffProtectStacks INT;King.protectedBuffs REAL at original callsite;no runtime change.',
        counts=counts, first_source_regression_exit=0, metadata_first_exit=1,
        metadata_note='Finalizer first compared independent frozenset-generated proof-key case inventories by list position. Repaired only metadata comparison to unique labels with exact expected outcomes;68controls/report/actual order unchanged and not rerun.',
        scope_limits=['No staged import or RNG/Engine/RuntimeDTO instance construction',
                      'No input build/model/native/capture/expected/host execution',
                      'No350/351/354scientific batch or355original52result repeated',
                      'Only356 first SOURCE regression;future native schema/11carriers/bundle/host remain pending'],
        no_more_writes=True)
    write('review.json', review)
    files = [R / 'docs/phase356_independent_pending_admission_regression_spec.md',
             R / 'tests/phase356_independent_source_controls.py',
             R / 'tests/phase356_independent_source_helpers.py', Path(__file__).resolve(),
             *sorted(p for p in D.rglob('*') if p.is_file() and p.name != 'owned-files.json')]
    assert len(files) == len(set(files))
    rows = [desc(p) for p in files]
    write('owned-files.json', dict(schema='phase356-independent-final-owner/1', files=rows,
                                  scope='Immutable repo-only SOURCE copies/contracts/actual outputs/first metadata error;no external cloud owner leaf'))
    owner = json.loads((D / 'owned-files.json').read_text())
    for row in owner['files']:
        assert desc(R / row['path']) == row
    print(json.dumps(dict(review=desc(D / 'review.json'), owner=desc(D / 'owned-files.json'),
                          leaves=len(rows), bytes=sum(x['size'] for x in rows))))


if __name__ == '__main__':
    main()
