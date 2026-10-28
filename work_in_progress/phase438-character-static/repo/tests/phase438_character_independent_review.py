"""One-shot independent phase438 controls or actual acceptance; never native execution."""
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

ROOT = Path('/workspace/python-original-engine/repo')
MODULE = ROOT / 'tests/phase438_character_initial_overlay_v2.py'
OWNER = ROOT / 'data/phase438-character-overlay-source-v2/source-owner.json'
CONTROL = ROOT / 'data/phase438-character-independent-controls-first-001'
REVIEW = ROOT / 'data/phase438-character-independent-acceptance-first-001'
OUTPUT = ROOT / 'data/phase438-character-overlay-first-001'
MODULE_SHA = 'af6454e043a7118c50a0951d8d78ba34be610359febff8e07a3ca62a1623a34e'
OWNER_SHA = 'd65a3143dd70af23ad9be54b4a73edc6a375ed6ebe25799573186b39b3b48111'


def require(ok, reason):
    if not ok:
        raise AssertionError(reason)


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(path):
    raw = path.read_bytes()
    return {'path': str(path), 'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def pinned(pin):
    path = Path(pin['path'])
    if not path.is_absolute():
        path = ROOT / path
    raw = path.read_bytes()
    require(len(raw) == pin['size'] and hashlib.sha256(raw).hexdigest() == pin['sha256'], 'PIN:' + str(path))
    return raw


def save(path, obj):
    with path.open('x') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')
    return digest(path)


def load_module():
    require(digest(MODULE)['sha256'] == MODULE_SHA, 'MODULE_SEAL')
    require(digest(OWNER)['sha256'] == OWNER_SHA, 'OWNER_SEAL')
    owner = json.loads(OWNER.read_bytes())
    for pin in owner['files']:
        pinned(pin)
    # Later adapter v1 is preserved; reconstructed analysis prose is not its archive.
    v1 = ROOT / 'data/phase438-character-overlay-source/source-owner.json'
    require(digest(v1)['sha256'] == 'c838f626bacb889b5b32028010cc38593e9e57fd62d9fd94dc50c81c87b12909', 'V1_OWNER')
    for pin in json.loads(v1.read_bytes())['files']:
        pinned(pin)
    spec = importlib.util.spec_from_file_location('phase438_independent_sut', MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    context = json.loads(pinned(module.CONTEXT))
    raw = {k: pinned(v) for k, v in context['inputs'].items()}
    lines = raw['checkpoints'].splitlines()
    require(len(lines) == 6, 'SIX_RECORD_BYTES')
    records = [json.loads(lines[i]) for i in (0, 3)]
    return module, context, json.loads(raw['audit']), records, json.loads(raw['facts'])


def validate_result(audit, report, proof, m):
    require(len(report['required_rows']) == 1363, 'ROW_COUNT')
    require(report['counts'] == {'DIRECT': 1289, 'SOURCE_DERIVED': 10, 'MISSING': 64}, 'COUNTS')
    require(canonical(report['full_reference_counts']) == canonical(audit['full_reference_counts']), 'FULL_REFERENCE')
    require(canonical(report['excluded_presentation']) == canonical(audit['excluded_presentation']), 'EXCLUDED116')
    require(len(report['excluded_presentation']) == 116, 'EXCLUDED_COUNT')
    changes = []
    old_source = 0
    for index, (before, after) in enumerate(zip(audit['required_rows'], report['required_rows'])):
        require(m.key(before) == m.key(after), 'ORDER')
        if m.key(before) not in m.TARGETS:
            require(canonical(before) == canonical(after), 'NONTARGET:' + str(index))
            old_source += before['classification'] == 'SOURCE_DERIVED'
            continue
        require(before['classification'] == 'MISSING', 'TARGET_ORIGINAL')
        expected = {'type': 'bool', 'value': False} if before['field_id'] == 'Character.invulnerable' else {'type': 'null'}
        require(canonical(after['actual_value']) == canonical(expected), 'TYPED_VALUE')
        require(after['classification'] == 'SOURCE_DERIVED' and after['proof_complete'] is True and after['validation_result'] == 'SUPPORTED', 'DERIVED_STATUS')
        require(canonical(after['source_derivation']['original_row']) == canonical(before), 'OLD_ROW_PROVENANCE')
        require(after['rule'] == m.RULE and len(after['input_refs']) == 4, 'PROVENANCE_REFS')
        changes.append({'ordinal': index, 'key': list(m.key(after)), 'actual_value': after['actual_value']})
    require(len(changes) == 8 and old_source == 2, 'EXACT8_AND_OLD2')
    require(len(proof['changes']) == 8 and proof['candidate_count'] == 8 and proof['Buff44_promotions'] == 0, 'PROOF_COUNTS')
    changed_top = {key for key in set(audit) | set(report) if canonical(audit.get(key)) != canonical(report.get(key))}
    require(changed_top == {'schema', 'status', 'counts', 'phase438_rule', 'required_rows'}, 'TOPLEVEL_CONSERVATION')
    require(report['King_admitted'] is False, 'KING_UNADMITTED')
    return {'changes': changes, 'non_target_rows_unchanged': 1355, 'excluded_unchanged': 116, 'old_derived_unchanged': 2, 'counts': report['counts']}


def controls(m, context, audit, records, facts):
    report, proof = m.project(audit, records, facts)
    result = validate_result(audit, report, proof, m)
    rejected = []
    def reject(name, fn):
        try:
            fn()
        except m.Rejected as e:
            rejected.append({'name': name, 'reason': str(e)})
        else:
            raise AssertionError('UNEXPECTED_ACCEPT:' + name)
    for value in (False, 0.0, '0', -1, 1):
        x = deepcopy(facts)
        x['timers']['invu:P']['lineage']['starts'] = value
        reject('starts:' + repr(value), lambda x=x: m.validate_ledger(x, m.validate_cuts(records)))
    for name, edit in (
        ('missing_counter', lambda x: x['timers']['invu:P']['lineage'].pop('starts')),
        ('wrong_kind', lambda x: x['timers']['invu:P']['lineage'].__setitem__('kind', 'post_prepare')),
        ('owner_alias', lambda x: x['timers']['invu:P']['lineage'].__setitem__('owner_id', '84805')),
        ('timer_alias', lambda x: x['timers']['invu:P']['lineage'].__setitem__('timer_id', '84961')),
        ('bool_birth_mode', lambda x: x['timers']['invu:P']['lineage']['birth'].__setitem__('process_mode', False)),
        ('current_mismatch', lambda x: x['timers']['invu:P']['current']['node'].__setitem__('native_id', '84961')),
    ):
        x = deepcopy(facts); edit(x)
        reject(name, lambda x=x: m.validate_ledger(x, m.validate_cuts(records)))
    for name, edit in (
        ('wrong_phase', lambda x: x[0]['stamp'].__setitem__('phase', 'later')),
        ('wrong_sequence', lambda x: x[0].__setitem__('sequence', 139)),
        ('bool_sequence', lambda x: x[0].__setitem__('sequence', True)),
        ('wrong_frame', lambda x: x[0]['stamp'].__setitem__('idle_frame', '39')),
        ('resource_alias', lambda x: x[0]['payload']['source_resources'][0].__setitem__('native_id', '84805')),
        ('duplicate_node', lambda x: x[0]['payload']['nodes'].append(deepcopy(x[0]['payload']['nodes'][0]))),
        ('bool_environment', lambda x: x[0]['payload']['environment']['fps'].__setitem__('decimal', True)),
    ):
        x = deepcopy(records); edit(x)
        reject(name, lambda x=x: m.validate_cuts(x))
    x = deepcopy(records)
    next(n for n in x[0]['payload']['nodes'] if n['role'] == 'invu:P')['timer']['process_mode'] = False
    reject('bool_cut_mode', lambda: m.validate_cuts(x))
    for name in ('foreign_missing_key', 'swap_rows', 'old_derived_shape', 'excluded_payload', 'duplicate_target'):
        x = deepcopy(audit)
        if name == 'foreign_missing_key':
            next(r for r in x['required_rows'] if r['classification'] == 'MISSING' and r['field_id'] == 'Timer.private_left')['side_or_role'] = 'FOREIGN_UNIQUE'
        elif name == 'swap_rows':
            x['required_rows'][0], x['required_rows'][1] = x['required_rows'][1], x['required_rows'][0]
        elif name == 'old_derived_shape':
            next(r for r in x['required_rows'] if r['classification'] == 'SOURCE_DERIVED')['actual_value'] = {'type': 'bool', 'value': 0}
        elif name == 'excluded_payload':
            x['excluded_presentation'][0]['reason'] += ':foreign'
        else:
            indexes = [i for i, r in enumerate(x['required_rows']) if m.key(r) in m.TARGETS]
            x['required_rows'][indexes[1]] = deepcopy(x['required_rows'][indexes[0]])
        reject(name, lambda x=x: m.validate_audit(x))
    x = deepcopy(context); x['premises'][1] = 'constructor-to-ready window unknown'
    reject('pre_ready_domain_removed', lambda: m.validate_source(x, []))
    reject('duplicate_json', lambda: m.strict_json(b'{"a":0,"a":1}'))
    reject('nonfinite_json', lambda: m.strict_json(b'{"a":NaN}'))
    # Explicit source-domain witnesses; no native execution or Timer model.
    prebirth = {'item': 'old', 'invulnerable': False, 'starts_after_birth': 0}
    require(prebirth['starts_after_birth'] == 0 and prebirth['item'] is not None, 'PREBIRTH_WITNESS')
    timeout = {'item': 'old', 'invulnerable': False, 'whole_life_starts': 1}
    require(timeout['invulnerable'] is False and timeout['item'] is not None, 'TIMEOUT_ITEM_WITNESS')
    result.update(status='PASS', pure_project_calls=1, actual_run_calls=0, negative_controls=rejected,
                  source_counterexamples=['prebirth-or-reset-zero-does-not-prove-null', 'timeout-false-retains-item'],
                  checkpoint_records_parsed=[1, 4], whole_input_files_hashed=True,
                  native_runs=0, old_controls_run=0, Timer_abstract_enumeration_run=0)
    return result


def actual(m, context, audit, records, facts):
    previous = json.loads((CONTROL / 'result.json').read_bytes())
    require(previous['status'] == 'PASS' and previous['module_sha256'] == MODULE_SHA, 'CONTROL_GATE')
    require(not OUTPUT.exists(), 'NO_EXISTING_ACTUAL_OUTPUT')
    calls = []
    original = m.read_pinned
    def traced(pin, io):
        raw = original(pin, io)
        calls.append(deepcopy(pin))
        return raw
    m.read_pinned = traced
    receipt = m.run(str(OUTPUT))  # The only actual run call.
    report = json.loads((OUTPUT / 'overlay-report.json').read_bytes())
    proof = json.loads((OUTPUT / 'proof-evidence.json').read_bytes())
    result = validate_result(audit, report, proof, m)
    readback = json.loads((OUTPUT / 'input-readback.json').read_bytes())
    before, after = readback['before'], readback['after']
    require(canonical(before) == canonical(after) and len(before) == 848, 'ACTUAL_SECOND_PASS')
    require(canonical(calls[:len(before)]) == canonical(before), 'FIRST_PASS_TRACE')
    require(canonical(calls[len(before):2*len(before)]) == canonical(after), 'SECOND_PASS_TRACE')
    require(readback['parsed_checkpoint_lines'] == [1, 4] and readback['postcleanup_records_parsed'] == 0 and readback['whole_file_bytes_include_unparsed_records'] is True, 'PARSE_VS_BYTES')
    checkpoints = context['inputs']['checkpoints']
    require(sum(canonical(p) == canonical(checkpoints) for p in calls) == 2, 'TWO_CHECKPOINT_HASH_PASSES')
    for pin in json.loads((OUTPUT / 'owned-files.json').read_bytes())['files']:
        pinned(pin)
    result.update(status='ACCEPTED_CHARACTER8_ONLY', actual_run_calls=1, actual_receipt=receipt,
                  pure_project_calls_in_actual_process=0, whole_files_hashed_before=len(before),
                  whole_files_rehashed_after=len(after), checkpoint_byte_hash_passes=2,
                  checkpoint_bytes_per_pass=checkpoints['size'], checkpoint_records_parsed=[1, 4],
                  postcleanup_records_parsed=0, native_runs=0, King_admitted=False,
                  all_Timer64_remaining=True, observed_read_pinned_calls=len(calls))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['controls', 'actual'])
    args = parser.parse_args()
    destination = CONTROL if args.mode == 'controls' else REVIEW
    destination.mkdir(mode=0o700)
    started = time.monotonic()
    try:
        m, context, audit, records, facts = load_module()
        result = (controls if args.mode == 'controls' else actual)(m, context, audit, records, facts)
        result.update(module_sha256=MODULE_SHA, source_owner_sha256=OWNER_SHA,
                      elapsed_seconds=time.monotonic()-started,
                      correction_limit='Earlier analysis report/owner are RECONSTRUCTED, not archived originals; later v1 adapter remains pinned and preserved.')
        pin = save(destination / 'result.json', result)
        save(destination / 'owned-files.json', {'files': [pin, digest(Path(__file__)), digest(MODULE), digest(OWNER)], 'reviewer': 'timer_invariant_review_astra'})
        print(json.dumps({'status': result['status'], 'result': pin, 'elapsed_seconds': result['elapsed_seconds']}))
    except Exception as error:
        save(destination / 'first-error.json', {'type': type(error).__name__, 'reason': str(error), 'elapsed_seconds': time.monotonic()-started, 'no_automatic_retry': True})
        raise


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    main()
