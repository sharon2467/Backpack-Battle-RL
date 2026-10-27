"""Bounded independent controls for the new phase437 policy only; no old SUT imports."""
from contextlib import redirect_stdout
from copy import deepcopy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/phase437-independent-implementation-review-first-001'
AUDIT = ROOT / 'data/phase437-combat-initial-first-001'
INPUTS = [ROOT / 'data/phase408-initial-audit-first-001/rawtyped-field-index.json',
          ROOT / 'data/phase426-king-buff-overlay-first-001/overlay-report.json']
REVIEW = ROOT / 'data/phase437-independent-source-review-first-001/source-review.json'
OWNER = ROOT / 'data/phase437-combat-contract-source/source-owner.json'
MODULE = ROOT / 'native_replay_v8/combat_contract.py'
checks = []
main_calls = 0
start = time.monotonic()


def read(path):
    return json.loads(path.read_bytes())


def pin(path):
    raw = path.read_bytes()
    s = path.stat()
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(raw).hexdigest(),
            'size': len(raw), 'metadata': [s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns]}


def check(name, assertion):
    if not assertion:
        raise AssertionError(name)
    checks.append({'name': name, 'status': 'PASS'})


def rejects(name, fn):
    try:
        fn()
    except ValueError as error:
        checks.append({'name': name, 'status': 'PASS', 'rejection': str(error)})
    else:
        raise AssertionError('unexpected acceptance: ' + name)


def key(row):
    return tuple(row[n] for n in ('field_id', 'phase', 'side_or_role'))


def run():
    global main_calls
    owner = read(OWNER)
    sealed_paths = [ROOT / f['path'] for f in owner['files']]
    core = read(ROOT / 'data/phase437-combat-contract-source/preserved-core-files-before.json')['files']
    paths = list(dict.fromkeys(INPUTS + [REVIEW, OWNER, MODULE] + sealed_paths + [ROOT / f['path'] for f in core]))
    before = [pin(p) for p in paths]
    check('source_owner_matches_before', all(pin(ROOT / f['path'])['sha256'] == f['sha256'] and (ROOT / f['path']).stat().st_size == f['size'] for f in owner['files']))
    check('eight_preserved_core_match_before', len(core) == 8 and all(pin(ROOT / f['path'])['sha256'] == f['sha256'] for f in core))
    spec = importlib.util.spec_from_file_location('phase437_new_policy_only', MODULE)
    policy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(policy)
    index, overlay, review = read(INPUTS[0]), read(INPUTS[1]), read(REVIEW)
    originals = deepcopy((index, overlay))
    reviewed = {key(r) for r in review['excluded_rows']}
    expected = {key(r) for r in index if policy.excluded_reason(r['field_id'], r['side_or_role'])}
    check('exact_independent_116_exclusion_set', expected == reviewed and len(expected) == 116)
    check('exact_full1479_known_key_set', policy.full_initial_target_keys() == {key(r) for r in index} and len(index) == 1479)
    result = policy.project_initial_audit(deepcopy(index), deepcopy(overlay))
    check('exact1363_required116_excluded_counts', result['required_count'] == 1363 and result['excluded_present_count'] == 116)
    check('exact_required1289_direct2_derived72_missing', result['counts'] == {'DIRECT': 1289, 'SOURCE_DERIVED': 2, 'MISSING': 72})
    check('full_historical_counts_preserved', result['full_reference_count'] == 1479 and result['full_reference_counts'] == {'DIRECT': 1391, 'SOURCE_DERIVED': 6, 'MISSING': 82})
    check('excluded102_direct4_derived10_missing', result['excluded_reference_counts'] == {'DIRECT': 102, 'SOURCE_DERIVED': 4, 'MISSING': 10})
    check('still_blocked_and_king_unadmitted', result['status'] == 'BLOCKED_COMBAT_INITIAL_GAPS' and result['fullschema'] == 'NOT_VALIDATED' and result['King_admitted'] is False)
    by_key = {key(r): r for r in overlay['targets']}
    combined = [deepcopy(by_key.get(key(r), r)) for r in index]
    required = [r for r in combined if key(r) not in reviewed]
    excluded = [r for r in combined if key(r) in reviewed]
    check('all_retained_rows_values_statuses_order_unchanged', result['required_rows'] == required)
    check('all_excluded_rows_archived_unchanged', [r['original_row'] for r in result['excluded_presentation']] == excluded)
    minimal = policy.partition_initial_rows(deepcopy(required))
    check('required1363_alone_partition_succeeds', minimal['required_count'] == 1363 and minimal['excluded_present_count'] == 0 and minimal['counts'] == result['counts'])
    changed = deepcopy(combined)
    for r in changed:
        if key(r) in reviewed:
            r.update(actual_value={'arbitrary': 'presentation-only'}, classification='MUTATED_PRESENTATION',
                     validation_result='MUTATED_PRESENTATION', proof_complete='MUTATED_PRESENTATION',
                     unresolved=['display unavailable'], constraint={'mutated': True})
    changed_result = policy.partition_initial_rows(changed)
    check('all116_presentation_values_proof_statuses_do_not_block_partition', changed_result['required_rows'] == required and changed_result['counts'] == result['counts'] and changed_result['excluded_present_count'] == 116)
    check('partition_returns_deepcopies', changed_result['required_rows'][0] is not changed[0] and changed_result['excluded_presentation'][0]['original_row'] is not changed[combined.index(excluded[0])])
    for f, role in [('Character.invulnerable', 'P'), ('Character.invulnerabilityItem', 'O'),
                    ('King.invuCharges', 'P:12'), ('King.protectedBuffs', 'P:12'), ('King.manaCost', 'P:12'),
                    ('King.activations', 'P:12'), ('King.activationsToTrigger', 'P:12'),
                    ('Timer.private_left', 'invu:P'), ('Timer.private_left', 'invu:O'), ('Timer.private_left', 'king_buff:P:12')]:
        check('required_scope_' + f + '_' + role, policy.excluded_reason(f, role) is None and any(r['field_id'] == f and r['side_or_role'] == role for r in required))
    for f, role in [('King.crown', 'O:12'), ('Particle.activation.visible', 'P:13'), ('Timer.time_left', 'king_hide:P:13'), ('Timer.unreviewed', 'king_hide:P:12')]:
        check('no_field_or_role_name_heuristic_' + f + '_' + role, policy.excluded_reason(f, role) is None)
    missing_required = [r for r in required if key(r) != ('Character.invulnerable', 'pre_prepare', 'P')]
    rejects('delete_required_invulnerable_rejected', lambda: policy.partition_initial_rows(deepcopy(missing_required)))
    missing_buff = [r for r in required if key(r) != ('Timer.private_left', 'pre_prepare', 'king_buff:P:12')]
    rejects('delete_required_kingbuff_private_rejected', lambda: policy.partition_initial_rows(deepcopy(missing_buff)))
    bad = deepcopy(required); bad[0]['field_id'] = 'Unknown.invulBubbleVisible'
    rejects('unknown_identity_rejected', lambda: policy.partition_initial_rows(bad))
    rejects('duplicate_required_rejected', lambda: policy.partition_initial_rows(deepcopy(required + [required[0]])))
    bad = deepcopy(required); bad[0]['proof_complete'] = False
    rejects('retained_unsupported_proof_rejected', lambda: policy.partition_initial_rows(bad))
    bad = deepcopy(required); next(r for r in bad if r['classification'] == 'MISSING')['actual_value'] = 0
    rejects('retained_missing_with_invented_value_rejected', lambda: policy.partition_initial_rows(bad))
    rejects('nonlist_rows_rejected', lambda: policy.partition_initial_rows({}))
    bad_index = deepcopy(index); bad_index[0]['side_or_role'] = 'P:unknown'
    rejects('full_index_altered_identity_rejected', lambda: policy.project_initial_audit(bad_index, deepcopy(overlay)))
    bad_overlay = deepcopy(overlay); bad_overlay['targets'][0]['original_index'] = True
    rejects('overlay_bool_ordinal_rejected', lambda: policy.project_initial_audit(deepcopy(index), bad_overlay))
    bad_overlay = deepcopy(overlay); bad_overlay['targets'][0]['original_index'] += 1
    rejects('overlay_wrong_ordinal_rejected', lambda: policy.project_initial_audit(deepcopy(index), bad_overlay))
    bad_overlay = deepcopy(overlay); bad_overlay['targets'][0]['field_id'] = 'King.not_reviewed'
    rejects('overlay_unknown_target_rejected', lambda: policy.project_initial_audit(deepcopy(index), bad_overlay))
    bad_overlay = deepcopy(overlay); bad_overlay['targets'].append(deepcopy(bad_overlay['targets'][0]))
    rejects('overlay_duplicate_rejected', lambda: policy.project_initial_audit(deepcopy(index), bad_overlay))
    bad_overlay = deepcopy(overlay); bad_overlay['targets'].pop()
    rejects('overlay_incomplete_rejected', lambda: policy.project_initial_audit(deepcopy(index), bad_overlay))
    bad_overlay = deepcopy(overlay); r = next(r for r in bad_overlay['targets'] if r['classification'] == 'SOURCE_DERIVED'); r['classification'] = 'DIRECT_OBSERVATION'
    rejects('overlay_invented_direct_proof_rejected', lambda: policy.project_initial_audit(deepcopy(index), bad_overlay))
    rejects('overlay_nonlist_targets_rejected', lambda: policy.project_initial_audit(deepcopy(index), {'targets': {}}))
    check('original_inmemory_saved_fixtures_unchanged', (index, overlay) == originals)
    stdout = io.StringIO()
    main_calls += 1
    with redirect_stdout(stdout):
        code = policy.main(['--full-index', str(INPUTS[0].relative_to(ROOT)),
                            '--accepted-overlay', str(INPUTS[1].relative_to(ROOT)),
                            '--output-new', str(AUDIT.relative_to(ROOT))])
    check('single_actual_saved_audit_main_returned_zero', code == 0 and main_calls == 1)
    saved = read(AUDIT / 'combat-initial-audit.json')
    check('saved_audit_equals_inmemory_projection', saved == result)
    contract = read(AUDIT / 'contract.json')
    check('saved_exact_minimum_contract', len(contract['required_keys']) == 1363 and {tuple(r) for r in contract['required_keys']} == {key(r) for r in required} and {tuple(r['key']) for r in contract['excluded_keys']} == reviewed)
    check('saved_readback_input_identity_unchanged', read(AUDIT / 'input-readback.json')['unchanged'] is True)
    output_owner = read(AUDIT / 'owned-files.json')
    check('all_saved_audit_output_hashes_match', len(output_owner['files']) == 4 and all((AUDIT / f['path']).stat().st_size == f['size'] and hashlib.sha256((AUDIT / f['path']).read_bytes()).hexdigest() == f['sha256'] for f in output_owner['files']))
    after = [pin(p) for p in paths]
    check('frozen_saved_inputs_source_review_owner_metadata_bytes_unchanged', before == after)
    check('eight_preserved_core_hashes_unchanged', all(pin(ROOT / f['path'])['sha256'] == f['sha256'] for f in core))
    report = dict(schema='phase437-independent-implementation-review/1', status='PASS_BOUNDED_INITIAL_CONTRACT_PROJECTION',
                  reviewer='presentation_scope_review_sol', checks=checks, checks_passed=len(checks),
                  production_module_main_calls=main_calls, old_SUT_or_model_calls=0,
                  Godot_capture_pool_calls=0, subprocesses_spawned_by_control=0,
                  saved_audit=str(AUDIT.relative_to(ROOT)), saved_audit_summary=json.loads(stdout.getvalue()),
                  input_and_core_pins_before=before, input_and_core_pins_after=after,
                  formal_bounded_items=75, formal_bounded_items_status='EXISTING_ACCEPTED_UNCHANGED',
                  King_admitted=False, fullschema='NOT_VALIDATED',
                  source_report_status_wording_correction='The sealed Source review formal75=UNCHANGED_UNADMITTED and Chinese combined 75/King wording were erroneous/ambiguous. The existing formal bounded 75 remain accepted; King remains unadmitted. No sealed Source bytes were changed.',
                  scope='Exact minimum initial requirement projection only; no output/event/history/RNG/terminal projection. 72 required initial gaps still block.',
                  RNG_limit='No global GPU/backend/shared RNG purity proof; all original native calls/order and independent strict RNG gates remain unchanged.',
                  remaining_blockers=['72 required MISSING/UNPROVEN rows', 'King not admitted', 'fullschema not validated'],
                  elapsed_seconds=time.monotonic() - start)
    OUT.mkdir(exist_ok=False)
    (OUT / 'review.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    files = [OUT / 'review.json', Path(__file__).resolve()]
    manifest = dict(schema='phase437-independent-review-owner/1', self_excluded=True,
                    files=[dict(path=str(p.relative_to(ROOT)), size=p.stat().st_size,
                                sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files])
    (OUT / 'owned-files.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(status=report['status'], checks_passed=len(checks), main_calls=main_calls,
                          saved_audit=report['saved_audit'], elapsed_seconds=report['elapsed_seconds'])))


if __name__ == '__main__':
    try:
        run()
    except Exception as error:
        failure = {'status': 'STOPPED_ON_FIRST_UNEXPECTED_RESULT', 'checks': checks,
                   'main_calls': main_calls, 'error': type(error).__name__ + ': ' + str(error)}
        OUT.mkdir(exist_ok=False)
        (OUT / 'failure.json').write_text(json.dumps(failure, ensure_ascii=False, indent=2) + '\n')
        raise
