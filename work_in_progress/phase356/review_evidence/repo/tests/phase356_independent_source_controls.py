"""Presealed, stdlib-only SOURCE controls. Never import the staged candidate."""
import ast
import copy
import hashlib
import json
import math
from pathlib import Path
import re
import struct

R = Path(__file__).resolve().parents[1]
D = R / 'data/phase356-independent-source-review'


def identity(path):
    raw = path.read_bytes()
    return dict(size=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def main():
    contract = json.loads((D / 'source-contract.json').read_text())
    for row in contract['files']:
        assert identity(R / row['path']) == {k: row[k] for k in ('size', 'sha256')}
    helper_ns = {}
    exec(compile((R / 'tests/phase356_independent_source_helpers.py').read_text(), '<frozen-stdlib-source-supplement>', 'exec'), helper_ns)
    helper_ns['static_review'](R, D)
    s = (D / 'SOURCE/genuine.py').read_text()
    tree = ast.parse(s)
    ns = dict(hashlib=hashlib, json=json, math=math, re=re, struct=struct)
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                ns[node.targets[0].id] = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                if (isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name)
                        and node.value.func.id == 'frozenset' and len(node.value.args) == 1
                        and not node.value.keywords):
                    ns[node.targets[0].id] = frozenset(ast.literal_eval(node.value.args[0]))
    names = set(contract['exact_ast_functions'])
    selected = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert {n.name for n in selected} == names
    exec(compile(ast.Module(body=selected, type_ignores=[]), '<exact-selected-pure-SOURCE>', 'exec'), ns)
    interface = {}
    interface_source = (D / 'SOURCE/input_source_contract.py').read_text()
    interface_tree = ast.parse(interface_source)
    assert all(not isinstance(n, ast.Call) for n in interface_tree.body)
    exec(compile(interface_source, '<stdlib-proof-interface>', 'exec'), interface)
    fixture = json.loads((D / 'SOURCE/fixed-A-v8-fixture.json').read_text())
    results = []

    def check(label, expected, action):
        try:
            value = action()
        except (ValueError, TypeError, KeyError, UnicodeDecodeError, AttributeError) as exc:
            accepted = False
            detail = dict(type=type(exc).__name__, message=str(exc))
        else:
            accepted = True
            detail = dict(return_type=type(value).__name__)
        results.append(dict(label=label, expected=expected, accepted=accepted,
                            pass_=accepted == (expected == 'accept'), detail=detail))

    check('fixed-A-SOURCE-fixture', 'accept', lambda: ns['validate_single_king_fixture'](fixture))
    for label, mutation in (
        ('class-bool', lambda f: f['sides'][0].update(character_class=False)),
        ('class-two', lambda f: f['sides'][0].update(character_class=2)),
        ('wrong-geometry', lambda f: f['sides'][0]['items'][0].update(rotation=1)),
        ('missing-King', lambda f: f['sides'][0].update(items=[i for i in f['sides'][0]['items'] if i['item_index'] != 262])),
        ('wrong-HP', lambda f: f['sides'][0].update(hp=1.0)),
    ):
        modified = copy.deepcopy(fixture)
        mutation(modified)
        check(label, 'reject', lambda f=modified: ns['validate_single_king_fixture'](f))

    profile = dict(profile_id=ns['SINGLE_KING_GENUINE_PROFILE'], mode='genuine',
                   terminal_profile=ns['SINGLE_KING_TERMINAL'])
    result_profile = dict(profile=profile['profile_id'], mode='genuine',
                          terminal_profile=profile['terminal_profile'])
    check('new-profile-domain-only', 'reject', lambda: ns['validate_profile'](profile, fixture))
    check('new-result-domain-only', 'reject', lambda: ns['validate_result_profile'](result_profile, fixture))
    for name, obj, fun in (('input', profile, 'validate_profile'), ('result', result_profile, 'validate_result_profile')):
        for field, value in (('mode', 'synthetic'), ('terminal_profile', 'unknown')):
            bad = dict(obj, **{field: value})
            check(name + '-wrong-' + field, 'reject', lambda b=bad, fn=fun: ns[fn](b, fixture))

    binding = ns['SUPPORT68_PATCH']
    diff = (D / 'SOURCE/old307-native-source.patch').read_bytes()
    assert hashlib.sha256(diff).hexdigest() == binding['diff_sha256']
    report = dict(schema='observer7-patch/1', patch_version=binding['version'],
                  variant_generator_sha256=binding['profile_sha256'],
                  patches=[dict(path=name, **entry) for name, entry in binding['files'].items()])
    check('approved-old307-SOURCE-patch-alone', 'accept', lambda: ns['validate_patch'](report, diff))
    check('unknown-new-patch-rejected', 'reject', lambda: ns['validate_patch'](
        dict(schema='observer7-patch/1', patch_version='7-king-single-A-355'), b'unknown future SOURCE'))
    # This executes only the same pure admission predicates used separately by
    # engine/compare. It does not fabricate a capture, model or comparator PASS.
    def composed_old_patch():
        ns['validate_profile'](profile, fixture)
        ns['validate_result_profile'](result_profile, fixture)
        ns['validate_patch'](report, diff)
    check('NEW_PROFILE_MUST_NOT_ACCEPT_OLD307_PATCH', 'reject', composed_old_patch)

    def defaults(charges):
        fields = {key: dict(type='int', decimal=str(value)) for key, value in
                  [('descriptorIndex', 262), ('activations', 0), ('invuCharges', charges)]}
        fields.update({key: dict(type='float', binary64_be=struct.pack('>d', value).hex())
                       for key, value in [('activationsToTrigger', 6.0), ('protectedBuffs', 3.0), ('manaCost', 4.0)]})
        return dict(payload=dict(items=[dict(instance='P:12', fields=fields)]))
    pre, act = defaults(0), defaults(3)
    check('proof-defaults-local-scalar-only', 'accept', lambda: ns['validate_single_king_source_defaults'](pre, act))
    for key, value in [('descriptorIndex', dict(type='int', decimal='263')),
                       ('activations', dict(type='int', decimal=False)),
                       ('invuCharges', dict(type='int', decimal='3')),
                       ('manaCost', dict(type='int', decimal='4'))]:
        bad = copy.deepcopy(pre)
        bad['payload']['items'][0]['fields'][key] = value
        check('wrong-default-' + key, 'reject', lambda b=bad: ns['validate_single_king_source_defaults'](b, act))
    check('counter-BOOL', 'reject', lambda: ns['_single_king_counter'](False))
    check('counter-REAL', 'reject', lambda: ns['_single_king_counter'](0.0))
    check('REAL-NaN', 'reject', lambda: ns['_single_king_real']('7ff8000000000000'))

    def raw_fixture():
        data = {name: b'{}' for name in interface['INPUT_FILES']}
        for j, (name, channel) in enumerate(interface['CHANNEL_FILES'].items()):
            row = dict(schema='observer7-record/1', channel=channel, sequence=j,
                       payload=dict(kind='randf') if channel == 'primitive' else {})
            data[name] = json.dumps(row, separators=(',', ':')).encode() + b'\n'
        data['king-clock-passes.jsonl'] = b'{}\n'
        data['king-ui-authority.jsonl'] = b'{}\n'
        return data
    raw = raw_fixture()
    check('transport-only-eleven-framing-NOT-native-schema', 'accept', lambda: interface['decode_sources'](raw))
    changes = {
        'extra-expected-file': lambda d: d.update({'events.jsonl': b'{}\n'}),
        'missing-file': lambda d: d.pop('king-input-facts.json'),
        'nonbytes': lambda d: d.update({'fixture.json': '{}'}),
        'wrong-file-channel': lambda d: d.update({'observer7-input.jsonl': d['observer7-lineage.jsonl']}),
        'duplicate-cross-channel-sequence': lambda d: d.update({'observer7-input.jsonl': b'{"schema":"observer7-record/1","channel":"input","sequence":1}\n'}),
        'reverse-physical-sequence': lambda d: d.update({'observer7-input.jsonl': b'{"schema":"observer7-record/1","channel":"input","sequence":8}\n{"schema":"observer7-record/1","channel":"input","sequence":7}\n'}),
        'BOOL-sequence': lambda d: d.update({'observer7-input.jsonl': b'{"schema":"observer7-record/1","channel":"input","sequence":false}\n'}),
        'negative-sequence': lambda d: d.update({'observer7-input.jsonl': b'{"schema":"observer7-record/1","channel":"input","sequence":-1}\n'}),
        'oversize-sequence': lambda d: d.update({'observer7-input.jsonl': b'{"schema":"observer7-record/1","channel":"input","sequence":9223372036854775808}\n'}),
        'missing-EOF-newline': lambda d: d.update({'king-clock-passes.jsonl': b'{}'}),
        'blank-line': lambda d: d.update({'king-ui-authority.jsonl': b'\n'}),
        'duplicate-JSON-key': lambda d: d.update({'fixture.json': b'{"x":0,"x":1}'}),
        'invalid-UTF8': lambda d: d.update({'fixture.json': b'\xff'}),
        'nonfinite-JSON': lambda d: d.update({'fixture.json': b'{"x":NaN}'}),
        'overflow-REAL': lambda d: d.update({'fixture.json': b'{"x":1e999}'}),
        'global-primitive-forbidden': lambda d: d.update({'observer7-primitives.jsonl': b'{"schema":"observer7-record/1","channel":"primitive","sequence":3,"payload":{"kind":"global_u32"}}\n'}),
        'UI-record-cap': lambda d: d.update({'king-ui-authority.jsonl': b'{"x":"' + b'x' * 16384 + b'"}\n'}),
        'RNG-file-cap': lambda d: d.update({'king-rng-checkpoint.json': b' ' * 16385}),
    }
    for label, mutation in changes.items():
        bad = copy.deepcopy(raw)
        mutation(bad)
        check(label, 'reject', lambda b=bad: interface['decode_sources'](b))
    decoded = interface['decode_sources'](raw)
    # An actual old profile-shaped identity is sufficient for this early reject;
    # no fake full typed observer validator or fabricated native carrier is used.
    class OldSourceIdentity:
        VERSION = binding['version']
        PROFILE = 'observer7-298-headless-support68-layout/1'
    check('old-native-profile-delegation-rejected', 'reject', lambda: interface['validate_decoded_proofs'](decoded, fixture, OldSourceIdentity))
    for forbidden in interface['PROOF_ONLY']:
        runtime = {key: None for key in interface['RUNTIME_KEYS']}
        runtime.update(profile_id=interface['PROFILE'], mode='genuine')
        runtime[forbidden] = {}
        check('runtime-proof-leak-' + forbidden, 'reject', lambda v=runtime: interface['check_runtime_projection'](v))

    assert len(results) == 52
    supplement_facts = helper_ns['supplement'](ns, fixture, profile, result_profile, check, results, D)
    failures = [row for row in results if not row['pass_']]
    out = dict(schema='phase356-independent-pure-source-regression/1',
               status='SOURCE_COUNTEREXAMPLE_FOUND' if failures else 'SOURCE_CONTROLS_PASS',
               controls=results, executed=len(results), reused52=52, supplement=supplement_facts, expected_failclosed_violations=failures,
               positive_scope='transport/domain/local default predicates only, never complete native admission',
               source_caller='New result admission now raises pending before comparator Path/capture access; old comparator and patch validator unchanged',
               candidate_imports=0, RNG_constructions=0, Engine_constructions=0,
               models=0, native=0, input_builds=0, expected_reads=0)
    dest = D / 'controls-first-001'
    dest.mkdir(exist_ok=False)
    with (dest / 'report.json').open('x') as stream:
        json.dump(out, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps(dict(status=out['status'], executed=len(results), failures=[r['label'] for r in failures])))


if __name__ == '__main__':
    main()
