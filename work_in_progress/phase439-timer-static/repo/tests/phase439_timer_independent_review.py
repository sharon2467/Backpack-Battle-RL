"""Independent439-only controls/acceptance; no old helper or native execution."""
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import time

ROOT = Path('/workspace/python-original-engine/repo')
MODULE = ROOT / 'tests/phase439_timer_initial_overlay_v2.py'
OWNER = ROOT / 'data/phase439-timer-overlay-source-v2/source-owner.json'
CONTROL = ROOT / 'data/phase439-independent-controls-first-001'
REVIEW = ROOT / 'data/phase439-independent-acceptance-first-001'
OUTPUT = ROOT / 'data/phase439-timer-overlay-first-001'
SUPPLEMENT = ROOT / 'data/phase439-root-animation-source-supplement/receipt.json'
MSHA = '3a272044ebf127d3a228d0424f30849962f121c3e654a34607cf1f1b9ee4c4bf'
OSHA = 'b337ef4f345c062386636faa66d14d6bca1425e4305d31aba4291f09b9a9af0a'
SSHA = '8e7af43abef73f6e0bb296812d42318c963c876e33775bcbf5c66590fba71113'


def require(ok, why):
    if not ok:
        raise AssertionError(why)


def canon(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def pin(path):
    raw = path.read_bytes()
    return {'path': str(path), 'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def read(pin_value):
    p = Path(pin_value['path'])
    p = p if p.is_absolute() else ROOT / p
    raw = p.read_bytes()
    require(len(raw) == pin_value['size'] and hashlib.sha256(raw).hexdigest() == pin_value['sha256'], 'PIN:' + str(p))
    return raw


def save(path, value):
    with path.open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')
    return pin(path)


def setup():
    require(pin(MODULE)['sha256'] == MSHA and pin(OWNER)['sha256'] == OSHA, 'SOURCE_SEALS')
    for item in json.loads(OWNER.read_bytes())['files']:
        read(item)
    v1 = ROOT / 'data/phase439-timer-overlay-source/source-owner.json'
    require(pin(v1)['sha256'] == '5ec3260026771303feb5b3def12c8eacbc1c62272623228c2da88de72ff3c161', 'V1_SEAL')
    for item in json.loads(v1.read_bytes())['files']:
        read(item)
    spec = importlib.util.spec_from_file_location('independent439_sut', MODULE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    context = json.loads(read(m.CONTEXT))
    require(pin(SUPPLEMENT)['sha256'] == SSHA, 'SUPPLEMENT_SEAL')
    supplement = json.loads(SUPPLEMENT.read_bytes())
    historical = json.loads(read(supplement['historical_inventory']))
    historical = {entry['path']: entry for entry in historical['entries'] if entry['kind'] == 'file'}
    require(len(context['animation_leaves']) == len(supplement['leaves']) == 8, 'EXACT_EIGHT_LEAVES')
    for leaf, declared in zip(context['animation_leaves'], supplement['leaves']):
        rel = str(Path(leaf['path']).relative_to(m.BASE))
        require(rel == declared['path'], 'LEAF_ORDER')
        old = historical[rel]
        require(old['sha256'] == leaf['sha256'] == declared['sha256'] and old['size'] == leaf['size'] == declared['size'], 'HISTORICAL_LEAF_IDENTITY')
        text = read(leaf).decode()
        types = re.findall(r'^tracks/\d+/type = "([^"]+)"', text, re.M)
        paths = re.findall(r'^tracks/\d+/path = NodePath\("([^"]+)"\)', text, re.M)
        require(types == declared['track_types'] and paths == declared['track_paths'] and set(types) == {'value'}, 'VISUAL_TRACK_RECEIPT')
    raw = {name: read(item) for name, item in context['inputs'].items()}
    lines = raw['checkpoints'].splitlines()
    require(len(lines) == 6, 'SIX_RECORDS')
    return m, context, json.loads(raw['audit']), [json.loads(lines[i]) for i in (0, 3)], supplement


def pointer(obj, path):
    for part in path.lstrip('/').split('/'):
        obj = obj[int(part)] if isinstance(obj, list) else obj[part.replace('~1', '/').replace('~0', '~')]
    return obj


def verify(audit, report, proof, records, m):
    require(report['counts'] == {'DIRECT': 1289, 'SOURCE_DERIVED': 74, 'MISSING': 0}, 'AFTER_COUNTS')
    require(len(report['required_rows']) == 1363 and len(report['excluded_presentation']) == 116, 'ARRAY_COUNTS')
    require(canon(report['excluded_presentation']) == canon(audit['excluded_presentation']), 'EXCLUDED_PRESERVED')
    require(canon(report['full_reference_counts']) == canon(audit['full_reference_counts']), 'FULL_REFERENCE_PRESERVED')
    require(len(proof['changes']) == 64 and proof['candidate_count'] == 64, 'PROOF64')
    proof_by_key = {tuple(x['key']): (i, x) for i, x in enumerate(proof['changes'])}
    require(set(proof_by_key) == m.TARGETS, 'PROOF_KEYSET')
    changed, old_derived, buffs = [], 0, 0
    for ordinal, (before, after) in enumerate(zip(audit['required_rows'], report['required_rows'])):
        key = tuple(before[k] for k in ('field_id', 'phase', 'side_or_role'))
        require(key == tuple(after[k] for k in ('field_id', 'phase', 'side_or_role')), 'ROW_ORDER')
        if key not in m.TARGETS:
            require(canon(before) == canon(after), 'NONTARGET:' + str(ordinal))
            old_derived += before['classification'] == 'SOURCE_DERIVED'
            continue
        require(before['classification'] == 'MISSING' and after['classification'] == 'SOURCE_DERIVED' and after['proof_complete'] is True and after['validation_result'] == 'SUPPORTED', 'TARGET_STATUS')
        require(canon(after['actual_value']) == canon({'type': 'float', 'binary64_be': 'bff0000000000000'}), 'EXACT_MINUS1')
        index, witness = proof_by_key[key]
        require(witness['required_ordinal'] == ordinal and after['source_derivation']['proof_index'] == index and after['source_derivation']['proof_file'] == 'proof-evidence.json', 'PROOF_INDEX')
        require(canon(after['input_refs']) == canon(witness['input_refs']), 'PROOF_REFS')
        require(canon(witness['typed_witness']) == canon({'paused': False, 'mode': 0, 'inside_tree': True, 'internal_idle': False, 'internal_physics': False}), 'TYPED_WITNESS')
        require(canon(after['source_derivation']['typed_witness']) == canon(witness['typed_witness']), 'ROW_WITNESS')
        record = records[0 if key[1] == 'pre_prepare' else 1]
        native_timer = pointer(record, witness['input_refs'][0]['pointer'])
        require(len(witness['public_support_ordinals']) == 19, 'PUBLIC19')
        for name, support_index in zip(m.PUBLIC_FIELDS, witness['public_support_ordinals']):
            support = audit['required_rows'][support_index]
            require((support['field_id'], support['phase'], support['side_or_role']) == ('Timer.' + name, key[1], key[2]), 'SUPPORT_IDENTITY')
            require(support['classification'] == 'DIRECT_OBSERVATION', 'SUPPORT_DIRECT')
            val = native_timer
            for part in name.split('.'):
                val = val[part]
            require(canon(val) == canon(support['actual_value']), 'SUPPORT_ACTUAL')
            require(canon(pointer(record, support['input_refs'][0]['pointer'])) == canon(val), 'SUPPORT_POINTER')
        if key[2].startswith('buff:'):
            require(len(witness['input_refs']) == 2 and canon(pointer(record, witness['input_refs'][1]['pointer'])) == canon(native_timer), 'BUFF_DUAL_POINTER')
            buffs += 1
        else:
            require(len(witness['input_refs']) == 1, 'SCENE_TIMER_POINTER')
        changed.append({'ordinal': ordinal, 'key': list(key), 'actual_value': after['actual_value']})
    require(len(changed) == 64 and old_derived == 10 and buffs == 44, 'EXACT64_OLD10_BUFF44')
    changed_top = {k for k in set(audit) | set(report) if canon(audit.get(k)) != canon(report.get(k))}
    require(changed_top == {'schema', 'status', 'counts', 'required_rows', 'phase439_rule', 'source_attribution_limit'}, 'TOPLEVEL_PRESERVATION')
    require(report['King_admitted'] is False and report['fullschema'] == 'NOT_VALIDATED', 'ADMISSION_CLOSED')
    for name in ('input_builds', 'models', 'captures'):
        require(report[name] == audit[name] == 0, 'CLOSED:' + name)
    return {'changes': changed, 'actual_changed_rows': 64, 'non_target_rows_preserved': 1299, 'prior_derived_preserved': 10, 'excluded_preserved': 116, 'Buff_dual_bindings': 44, 'public_support_bindings': 1216, 'counts': report['counts']}


def model_traces():
    def fresh():
        return dict(mode=1, p=False, a=False, i=False, f=False, left=-1, one=False)
    def processing(s, value):
        if s['mode'] in (0, 1):
            s['f' if s['mode'] == 0 else 'i'] = value and not s['a']
        s['p'] = value
    def act(s, op, arg=None):
        if op == 'start':
            s['left'] = 1; processing(s, True)
        elif op == 'stop':
            s['left'] = -1; processing(s, False)
        elif op == 'pause' and s['a'] != arg:
            s['a'] = arg; processing(s, s['p'])
        elif op == 'mode' and s['mode'] != arg:
            if s['mode'] == 0 and s['f']:
                s['f'] = False; s['i'] = True
            elif s['mode'] == 1 and s['i']:
                s['i'] = False; s['f'] = True
            s['mode'] = arg
        elif op == 'tick' and s['p'] and s['mode'] in (0, 1) and s['f' if s['mode'] == 0 else 'i']:
            s['left'] -= arg
            if s['left'] < 0:
                if s['one']:
                    act(s, 'stop')
                else:
                    s['left'] += 1
    def trace(ops):
        s = fresh()
        for op, arg in ops:
            act(s, op, arg)
        return s
    zero = trace([('start', None), ('tick', 1)])
    over = trace([('start', None), ('tick', 4)])
    pause = trace([('start', None), ('pause', True)])
    bypass = deepcopy(zero); bypass['i'] = False; act(bypass, 'mode', 0)
    invalid = trace([('start', None), ('tick', 1), ('pause', True), ('mode', 2), ('pause', False), ('mode', 0)])
    # Guarded native receptor interrupts stop between flag update and P assignment.
    receptor = trace([('start', None)])
    receptor['left'] = -1; receptor['i'] = False
    act(receptor, 'start'); receptor['p'] = False
    act(receptor, 'pause', True); act(receptor, 'pause', False)
    require(zero['left'] == 0 and zero['p'] and zero['i'], 'MODEL_ZERO')
    require(over['left'] == -2 and over['p'], 'MODEL_OVERSHOOT')
    require(pause['left'] == 1 and pause['a'] and not pause['i'], 'MODEL_PAUSE')
    for s in (bypass, invalid):
        require(s['mode'] == 0 and not s['a'] and not s['i'] and not s['f'] and s['left'] == 0, 'MODEL_HIDDEN_HISTORY')
    require(not receptor['a'] and not receptor['i'] and not receptor['f'] and receptor['left'] == 1, 'MODEL_RECEPTOR')
    stopped = trace([('mode', 0)])
    observed = lambda s: (s['mode'], s['a'], s['i'], s['f'], max(s['left'], 0), s['left'] <= 0)
    require(observed(stopped) == observed(invalid) == observed(bypass), 'SAME_SNAPSHOT_HIDDEN_HISTORY')
    return {'label': 'ABSTRACT_SOURCE_MODEL_NOT_NATIVE_MEASUREMENT', 'witnesses': {'zero_active': zero, 'repeat_overshoot': over, 'paused_active': pause, 'inherited_flag_escape': bypass, 'invalid_history_escape': invalid, 'native_receptor_escape': receptor}, 'interpretation': 'First3 defeat weaker premise sets; last3 escape the accepted source domain. Current observed mode/flags/public0 cannot detect hidden invalid history; no claim adapter discovers it.'}


def controls(m, context, audit, records, supplement):
    source_io = []
    m.validate_source(context, source_io)
    report, proof = m.project(audit, records, context['receivers'])
    result = verify(audit, report, proof, records, m)
    rejects = []
    def reject(name, fn, exceptions=None):
        try:
            fn()
        except (exceptions or (m.Rejected,)) as error:
            rejects.append({'name': name, 'reason': str(error)})
        else:
            raise AssertionError('UNEXPECTED_ACCEPT:' + name)
    ordinals = m.validate_audit(audit)
    def cut_test(name, edit):
        x = deepcopy(records); edit(x)
        reject(name, lambda: m.validate_cuts(x, audit, context['receivers'], ordinals))
    def wrapper(x, role='tick:P', cut=0):
        return next(n for n in x[cut]['payload']['nodes'] if n['role'] == role)
    def node_change(x, field, value, role='tick:P', cut=0):
        w = wrapper(x, role, cut)
        w['node'][field] = value; w['timer']['node'][field] = value
    for field in ('internal_idle', 'internal_physics', 'inside_tree'):
        cut_test('bool_type:' + field, lambda x, f=field: node_change(x, f, 0))
    cut_test('flag_true', lambda x: node_change(x, 'internal_idle', True))
    for name, value in (('bool_mode', False), ('mode2', 2), ('float_mode', 0.0)):
        cut_test(name, lambda x, v=value: wrapper(x)['timer'].__setitem__('process_mode', v))
    cut_test('paused_true', lambda x: wrapper(x)['timer'].__setitem__('paused', True))
    cut_test('paused_int', lambda x: wrapper(x)['timer'].__setitem__('paused', 0))
    cut_test('missing_flag', lambda x: wrapper(x)['timer']['node'].pop('internal_idle'))
    cut_test('native_alias', lambda x: node_change(x, 'native_id', '84959'))
    cut_test('duplicate_role', lambda x: x[0]['payload']['nodes'].append(deepcopy(x[0]['payload']['nodes'][0])))
    cut_test('crosscut_id', lambda x: node_change(x, 'native_id', '9999999', cut=1))
    cut_test('renamed', lambda x: node_change(x, 'name', 'OtherTimer'))
    cut_test('script_marker', lambda x: node_change(x, 'script', 'foreign.gd'))
    cut_test('wrong_parent_path', lambda x: next(n for n in x[0]['payload']['nodes'] if n['role'] == 'character:P')['node'].__setitem__('path', '/foreign'))
    cut_test('wrong_positions', lambda x: node_change(x, 'positions', [0, 1]))
    cut_test('wrong_class', lambda x: node_change(x, 'class', 'Node'))
    cut_test('wrong_phase', lambda x: x[0]['stamp'].__setitem__('phase', 'after_activation'))
    def buff(x):
        return next(r for r in x[0]['payload']['source_resources'] if r['side'] == 'P')['buffs'][0]
    cut_test('buff_stack_type', lambda x: buff(x).__setitem__('stack', {'type': 'int', 'decimal': True}))
    cut_test('buff_character', lambda x: buff(x)['state']['character'].__setitem__('native_id', '84805'))
    cut_test('buff_state_type', lambda x: buff(x)['state'].__setitem__('type', {'type': 'int', 'decimal': '101'}))
    cut_test('buff_timer_dual', lambda x: buff(x)['state']['timer'].__setitem__('process_mode', 1))
    for what in ('actual', 'reference'):
        x = deepcopy(audit)
        row = x['required_rows'][ordinals[('Timer.node.priority', 'pre_prepare', 'tick:P')]]
        if what == 'actual':
            row['actual_value'] = 'foreign'
        else:
            row['input_refs'][0]['pointer'] += '/foreign'
        reject('public_' + what, lambda x=x: m.validate_cuts(records, x, context['receivers'], ordinals))
    for name in ('old_proof', 'excluded', 'order', 'missing_identity'):
        x = deepcopy(audit)
        if name == 'old_proof':
            next(r for r in x['required_rows'] if r['classification'] == 'SOURCE_DERIVED')['actual_value'] = {'type': 'bool', 'value': 0}
        elif name == 'excluded':
            x['excluded_presentation'][0]['reason'] += ':foreign'
        elif name == 'order':
            x['required_rows'][0], x['required_rows'][1] = x['required_rows'][1], x['required_rows'][0]
        else:
            next(r for r in x['required_rows'] if r['classification'] == 'MISSING')['side_or_role'] = 'foreign'
        reject('audit_' + name, lambda x=x: m.validate_audit(x))
    for name in ('receipt', 'missing_animation', 'premise'):
        x = deepcopy(context)
        if name == 'receipt':
            x['receipts']['root438']['sha256'] = '0' * 64
        elif name == 'missing_animation':
            x['animation_leaves'].pop()
        else:
            x['premises'][3] = 'unknown mode/flag writer history'
        reject('source_' + name, lambda x=x: m.validate_source(x, []))
    x = deepcopy(context['receivers']); x[0]['construction']['script'] = 'foreign.gd'
    reject('receiver_source_script', lambda: m.validate_cuts(records, audit, x, ordinals))
    for i, leaf in enumerate(context['animation_leaves']):
        path = CONTROL / ('animation-drift-' + str(i) + '.tres')
        raw = read(leaf)
        with path.open('xb') as f:
            f.write(bytes([raw[0] ^ 1]) + raw[1:])
        altered = dict(leaf, path=str(path))
        reject('animation_hash_drift:' + str(i), lambda p=altered: m.read_pinned(p, []))
    local = CONTROL / 'ordinary.dat'
    local.write_bytes(b'one')
    local_pin = pin(local)
    symbolic = CONTROL / 'symbolic.dat'; symbolic.symlink_to(local)
    reject('symlink', lambda: m.read_pinned(dict(local_pin, path=str(symbolic)), []))
    hard = CONTROL / 'hard.dat'; os.link(local, hard)
    reject('hardlink', lambda: m.read_pinned(dict(local_pin, path=str(hard)), []))
    reject('overwrite', lambda: m.save_new(local, {}), (FileExistsError,))
    result.update(status='PASS', pure_project_calls=1, actual_run_calls=0, negative_controls=rejects,
                  source_descriptors_verified=len(source_io), source_model=model_traces(),
                  native_runs=0, old_controls_run=0, supplemental_receipt=pin(SUPPLEMENT))
    return result


def actual(m, context, audit, records, supplement):
    result = json.loads((CONTROL / 'result.json').read_bytes())
    require(result['status'] == 'PASS' and result['module_sha256'] == MSHA, 'CONTROL_GATE')
    require(not OUTPUT.exists(), 'OUTPUT_FRESH')
    calls = []
    original = m.read_pinned
    def traced(p, io):
        data = original(p, io); calls.append(deepcopy(p)); return data
    m.read_pinned = traced
    receipt = m.run(str(OUTPUT))
    report = json.loads((OUTPUT / 'overlay-report.json').read_bytes())
    proof = json.loads((OUTPUT / 'proof-evidence.json').read_bytes())
    answer = verify(audit, report, proof, records, m)
    rb = json.loads((OUTPUT / 'input-readback.json').read_bytes())
    before, after = rb['before'], rb['after']
    expected = 1 + sum(len(context[k]) for k in ('project_scripts', 'scene_dependencies', 'animation_leaves', 'other_source', 'receipts', 'inputs'))
    require(len(before) == len(after) == expected and canon(before) == canon(after), 'READBACK_COUNTS')
    require(canon(calls[:expected]) == canon(before) and canon(calls[expected:2*expected]) == canon(after), 'ACTUAL_READBACK_TRACE')
    for leaf in context['animation_leaves']:
        require(sum(canon(x) == canon(leaf) for x in calls) == 2, 'ANIMATION_TWO_PASSES')
    require(rb['parsed_checkpoint_lines'] == [1, 4] and rb['postcleanup_records_parsed'] == 0 and rb['whole_file_bytes_include_unparsed_records'] is True, 'PARSE_ACCOUNTING')
    require(proof['source_context']['context_descriptor'] == m.CONTEXT, 'SHARED_CONTEXT')
    outputs = json.loads((OUTPUT / 'owned-files.json').read_bytes())['files']
    for p in outputs:
        read(p)
    answer.update(status='ACCEPTED_ACTUAL64_SOURCE_DERIVED', actual_run_calls=1, standalone_project_calls_in_actual_process=0,
                  actual_receipt=receipt, output_files=outputs, before_count=expected, after_count=expected,
                  observed_read_pinned_calls=len(calls), animation_hash_passes=2, checkpoint_records_parsed=[1, 4],
                  postcleanup_records_parsed=0, supplemental_receipt=pin(SUPPLEMENT), historical_inventory=supplement['historical_inventory'],
                  native_runs=0, old_controls_run=0, fullschema='NOT_VALIDATED', King_admitted=False,
                  input_builds=0, models=0, captures=0)
    return answer


def main():
    p = argparse.ArgumentParser(); p.add_argument('mode', choices=['controls', 'actual']); args = p.parse_args()
    destination = CONTROL if args.mode == 'controls' else REVIEW
    destination.mkdir(mode=0o700)
    start = time.monotonic()
    try:
        m, context, audit, records, supplement = setup()
        result = (controls if args.mode == 'controls' else actual)(m, context, audit, records, supplement)
        result.update(module_sha256=MSHA, source_owner_sha256=OSHA, elapsed_seconds=time.monotonic()-start,
                      scope_limit='Bounded G02 ordinary-native Source attribution; no native/private measurement; historical815 public redaction/migration limits and earlier RECONSTRUCTED analysis reports remain disclosed.')
        result_pin = save(destination / 'result.json', result)
        files = [result_pin, pin(Path(__file__)), pin(MODULE), pin(OWNER), pin(SUPPLEMENT)]
        if args.mode == 'actual':
            files += result['output_files'] + [pin(CONTROL / 'result.json'), pin(OUTPUT / 'owned-files.json')]
        save(destination / 'owned-files.json', {'schema': 'phase439-independent-owner/1', 'files': files, 'reviewer': 'timer_invariant_review_astra'})
        print(json.dumps({'status': result['status'], 'elapsed_seconds': result['elapsed_seconds'], 'result': result_pin}))
    except Exception as error:
        save(destination / 'first-error.json', {'type': type(error).__name__, 'reason': str(error), 'no_automatic_retry': True, 'elapsed_seconds': time.monotonic()-start})
        raise


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    main()
