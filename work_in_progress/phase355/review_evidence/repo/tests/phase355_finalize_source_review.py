"""Output-only completion after the preserved static-tool metadata failure."""
import ast
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
D = R / 'data/phase355-independent-source-review'
A = R / 'data/phase355-king-finite-source'


def desc(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(R)), size=len(b), sha256=hashlib.sha256(b).hexdigest())


def write(name, value):
    with (D / name).open('x') as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write('\n')


def main():
    errors = (D / 'static-first.stderr.txt').read_text()
    assert 'line 109, in main' in errors and 'AssertionError' in errors
    assert "positions['validate_runtime_inputs'] < positions['SeededRandom']" in errors
    # The original tool's straight-line control flow has already completed its
    # compilation, module inverse and fixed-fixture assertions before line109.
    # This completion does not rerun those successful validations.
    source = (D / 'SOURCE/engine.py').read_text()
    tree = ast.parse(source)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'CombatEngine')
    init = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == '__init__')
    calls = {key: sorted(n.lineno for n in ast.walk(init) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == key)
             for key in ('validate_runtime_inputs', 'SeededRandom')}
    assert calls == dict(validate_runtime_inputs=[1186, 1188], SeededRandom=[1187])
    early = next(n for n in init.body if isinstance(n, ast.Assign) and n.lineno == 1186)
    assert isinstance(early.value, ast.IfExp) and isinstance(early.value.test, ast.BoolOp)
    assert isinstance(early.value.test.op, ast.Or)
    assert [n.func.id for n in early.value.test.values] == ['_source_king_profile', '_single_king_genuine_profile']
    assert early.value.body.func.id == 'validate_runtime_inputs'
    late = next(n for n in init.body if isinstance(n, ast.Assign) and n.lineno == 1188)
    assert isinstance(late.value, ast.IfExp) and isinstance(late.value.test, ast.Compare)
    assert ast.dump(late.value.test, include_attributes=False) == ast.dump(ast.parse('source_runtime is not None', mode='eval').body, include_attributes=False)
    assert isinstance(late.value.body, ast.Name) and late.value.body.id == 'source_runtime'
    functions = {}
    for name in ('engine.py', 'genuine.py'):
        path = R / 'data/phase349-king-fresh-source/staged/native_replay_v8' / name
        functions[name] = sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in ast.walk(ast.parse(path.read_text())))
    static = dict(schema='phase355-independent-static-output-completion/1',
                  status='CONSERVATION_SUCCESS_REUSED_METADATA_ORDER_CORRECTED',
                  original_tool_exit=1, original_tool=desc(R / 'tests/phase355_independent_static_review_v2.py'),
                  original_stderr=desc(D / 'static-first.stderr.txt'),
                  success_before_first_error=dict(author_owner_leaves=27, author_owner_bytes=704335,
                      compiled_candidate_modules=15, byte_conserved=13,
                      whole_old_modules_inverse_AST=True, old_function_counts=functions,
                      total_old_functions=sum(functions.values()), exact_fixed_A_conversion=True),
                  success_evidence='Original frozen tool straight-line assertions at lines64-100 completed before preserved failure at109; no separate per-layer snapshot was produced and none is invented.',
                  metadata_defect='Dictionary overwrote the first same-named validate_runtime_inputs call with the fallback call at1188.',
                  corrected_source_order=dict(all_calls=calls, new_profile_branch='At1186 new-profile predicate validates before default RNG1187. Successful DTO reused at1188; invalid validation raises before RNG. No candidate execution used.'),
                  completed_now='Only AST calls/conditional order and output metadata; successful conservation/52 semantic controls not rerun.',
                  candidate_imports=0, RNG_constructions=0, Engine_constructions=0, models=0, native=0)
    write('static-completion.json', static)
    controls = json.loads((D / 'controls-first-001/report.json').read_text())
    assert controls['executed'] == 52 and len(controls['expected_failclosed_violations']) == 1
    coverage = dict(schema='phase355-independent-first-source-coverage/1', rows=[
        dict(obligation='Author27 identities/fifteen candidate sources/thirteen unchanged349 modules', status='OBSERVED_STATIC_PASS', evidence='static-completion.json; all original author leaf identities actually read'),
        dict(obligation='Whole old genuine/engine modules and231 functions, old profile/PCG/effects/Timer/FrameDriver', status='OBSERVED_STATIC_PASS_REUSED', evidence='Whole inverse assertions completed before metadata first failure;13byte-identical modules; no old runtime replay'),
        dict(obligation='Exact351 A, six IDs/class0/singleP King/no gem/default geometry', status='PURE_SOURCE_DOMAIN_CONTROLS_PASS', evidence='Fixed-A positive + five fixture mutations rejected; exact schema/default conversion preserved; no native/runtime-positive claimed'),
        dict(obligation='New profile/result/patch source admission', status='BLOCKED_FALSE_ACCEPT', evidence='finding.json: approved old307 patch passes alongside new355 profile/result. Unknown patch rejection alone insufficient.'),
        dict(obligation='New genuine validation before default RNG', status='SOURCE_ORDER_PASS_WITH_ADMISSION_BLOCK', evidence='static-completion.json:1186 ->1187 ->1188; this does not repair the missing source coupling'),
        dict(obligation='Eleven lawful files/order/channel/duplicate/type/EOF/caps; primitive Util ABI', status='TRANSPORT_CONTROLS_PASS_ONLY', evidence='controls-first-001/report.json; no full typed schema or native carrier proof invented'),
        dict(obligation='Typed King pre/act defaults and proof-only runtime whitelist', status='LOCAL_PURE_CONTROLS_PASS', evidence='Exact decimal/REAL tags, four default mutations, bool/REAL counter/NaN rejection, nine proof-leak rejects. Complete future adapter remains pending.'),
        dict(obligation='Five freshTimer/scene/generic-ready/particle/UI/native identity joins', status='SOURCE_REVIEWED_NOT_EXECUTED_WITH_NATIVE', evidence='genuine.py872-918/960-1035: five distinct timer IDs/birth/current/no-start/owner; READY_OWNER_ONLY_NOT_TIMER; UI source authority independent flags; copied111 helper reviewed by narrow diff'),
        dict(obligation='Actual clock/twofuturephysics/first-idle-preinternal/EOF/trailing', status='OLD_SOURCE_BYTE_AST_CONSERVED_NO_NEW_RUN', evidence='v7 frame_driver byteexact349 and old EngineFrameDriver/step/finish AST; actual clock355 values absent'),
        dict(obligation='RNGcheckpoint never seed and postprepare facts never runtime branch/end marker', status='SOURCE_FLOW_REVIEWED_PARTIAL', evidence='Checkpoint helper returns proof only, constructor absent; validate_decoded_proofs only proof/runtime_returnedFalse/draws_returnedFalse. Complete adapter/poison controls not implemented.'),
        dict(obligation='Native full typed schema/collector/patch/source producer/adapter/model tools/host', status='NOT_IMPLEMENTED_PENDING_NOT_POSITIVE', evidence='Author remaining-dependencies.json; no fabricated new observer or actual11 inputs'),
        dict(obligation='Original Character buffProtectStacks field type', status='SOURCE_DOCUMENTATION_CORRECTION', evidence='Original Character.gd:82 explicitly var buffProtectStacks:int=0; method1465 +=amount. Field-matrix suggestion that stored field may promote toREAL is unsupported; no runtime effect change needed.'),
    ], actual_counts=dict(source_controls=52, matched_expected=51, false_accept=1,
                          static_tool_executions=1, static_tool_exit=1,
                          candidate_imports=0, RNG_constructions=0, Engine_constructions=0,
                          initializations=0, steps=0, input_builds=0, models=0, native=0, expected_reads=0))
    write('coverage.json', coverage)
    review = dict(schema='phase355-independent-first-source-review/1',
                  status='INDEPENDENT355_FIRST_SOURCE_BLOCKED_PROFILE_PATCH_COUPLING', accepted=False,
                  candidate_source_freeze=desc(A / 'candidate-source-freeze.json'),
                  author_source_owner=desc(A / 'source-owner.json'),
                  source_control_owner=desc(D / 'source-owner.json'),
                  controls=desc(D / 'controls-first-001/report.json'), finding=desc(D / 'finding.json'),
                  static_completion=desc(D / 'static-completion.json'), coverage=desc(D / 'coverage.json'),
                  blockers=['New355 profile/result admission is not coupled to new observer/patch provenance; real old307 SOURCE patch still accepted by independent patch predicate. Shared pending failclosed gate required before new genuine admission.'],
                  minimum_repair='New frozen version: failclosed shared host-code gate for355 input/result/runtime before RNG while new observer/schema/patch closure absent. Keep legacy profiles and pure source/helper contracts; do not build collector now.',
                  pending_scope='First SOURCE block only; no complete finite-native profile/actual eleven inputs/bundle/model/host accepted.',
                  first_facts=dict(source_controls_exit=0, source_control_failures=1,
                      static_tool_exit=1, static_tool_error='checker metadata last-call-overwrite; successful prior layers reused by control-flow evidence',
                      unused_static_tool_v1_executions=0, unused_static_tool_v1_reason='SOURCE preflight corrected invented fixture schema to existing v8 default discriminants before any execution'),
                  documentation_note='Typed original buffProtectStacks remainsINT; revise future matrix wording rather than runtime.',
                  counts=coverage['actual_counts'], formal_production_accepted_bounded=75,
                  King_production_admitted=False, no_more_writes=True)
    write('review.json', review)
    source_files = [R / 'docs/phase355_independent_first_source_review_spec.md',
                    R / 'tests/phase355_independent_source_controls.py',
                    R / 'tests/phase355_independent_static_review.py',
                    R / 'tests/phase355_independent_static_review_v2.py', Path(__file__).resolve()]
    files = source_files + sorted(p for p in D.rglob('*') if p.is_file() and p.name != 'owned-files.json')
    assert len(files) == len(set(files))
    rows = [desc(p) for p in files]
    write('owned-files.json', dict(schema='phase355-independent-final-owner/1', files=rows,
                                  scope='Immutable repo SOURCE snapshots, controls, first failures and final metadata only; no external cloud leaves'))
    for row in rows:
        assert desc(R / row['path']) == row
    print(json.dumps(dict(review=desc(D / 'review.json'), owner=desc(D / 'owned-files.json'),
                          leaves=len(rows), bytes=sum(row['size'] for row in rows))))


if __name__ == '__main__':
    main()
