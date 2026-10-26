"""Read back finite evidence and seal new phase410 review; never imports408."""
import hashlib
import json
import os
from pathlib import Path
import stat

ROOT = Path('/workspace/python-original-engine/repo')
PREP = 'data/phase410-setup-only408-preparation/'
FINAL = ROOT / 'data/phase410-independent408-source-review'
assert not FINAL.exists()


def checked(name, expected=None):
    path = ROOT / name
    assert path.resolve(strict=True) == path
    assert not any(p.is_symlink() for p in (path, *path.parents))
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and before.st_nlink == 1
    raw = path.read_bytes()
    after = path.lstat()
    assert identity(before) == identity(after) and before.st_size == len(raw)
    row = dict(path=name, size=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    if expected is not None:
        assert row == expected
    return raw, row


def identity(info):
    return [info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns]


prep_raw, prep_owner = checked(PREP + 'owned-files.json')
prep = json.loads(prep_raw)
for row in prep['files']:
    checked(row['path'], row)
references = json.loads(checked(PREP + 'references.json')[0])['files']
ref = {row['path']: row for row in references}
for row in references:
    checked(row['path'], row)
old = json.loads(checked('data/phase409-independent408-source-review/review.json')[0])
old_functional = json.loads(checked('data/phase409-independent408-component-first-001/result.json')[0])
assert old['status'] == 'INDEPENDENT409_STDLIB_INITIAL_AUDIT_SOURCE_BLOCKED'
assert old['source_static_status'] == 'PASS'
assert old['functional_component_status'] == 'FINITE_COMPONENTS_PASS'
assert old['dynamic']['top_level_API_calls'] == 20
assert old['dynamic']['successful_returns'] == 7 and old['dynamic']['expected_rejections'] == 13
assert old['original_read_scope_status'] == 'NOT_FULLY_SATISFIED'
assert old['dynamic']['additional_setup_completed_instances'] is None
result_raw, result_pin = checked('data/phase410-setup-only408-first-001/result.json')
result = json.loads(result_raw)
exit_raw, exit_pin = checked('data/phase410-setup-only408-launcher/exit.json')
exit_result = json.loads(exit_raw)
stdout_raw, stdout_pin = checked('data/phase410-setup-only408-launcher/stdout.txt')
stderr_raw, stderr_pin = checked('data/phase410-setup-only408-launcher/stderr.txt')
assert not stderr_raw
assert exit_result['child_exit_code'] == 0 and exit_result['invocations'] == 1
assert exit_result['timed_out'] is False and exit_result['timeout_seconds'] == 25
assert exit_result['elapsed_seconds'] < 25 and exit_result['automatic_retry'] is False
assert result['status'] == 'SETUP_ONLY_READ_SCOPE_PASS'
assert result['event_counts'] == {'open': 1, 'import': 0, 'compile': 1, 'exec': 1}
assert result['measurement_event_count'] == 3 and result['new_audit_module_instances'] == 1
assert result['observer_disabled_before_snapshot'] is True and result['used_profiler'] is False
assert [row['event'] for row in result['events']] == ['open', 'compile', 'exec']
assert result['events'][0]['path'] == str(ROOT / old['module']['path'])
assert result['events'][0]['flags'] & os.O_NOFOLLOW
assert result['events'][0]['flags'] & os.O_NONBLOCK
zero_keys = ('models', 'native', 'inputbuild', 'old_SUT_calls', 'schema_calls',
             'actual12_reads', 'top_level_API_calls', 'module_API_calls', 'main_run_audit_calls')
assert all(type(result[key]) is int and result[key] == 0 for key in zero_keys)
assert result['module'] == old['module'] == ref[old['module']['path']]
assert result['source_identity'] == identity((ROOT / old['module']['path']).lstat())
stages = [json.loads(line) for line in stdout_raw.splitlines()]
assert [row['stage'] for row in stages] == [
    'preloaded_and_source_metadata_checked', 'source_read_and_sha_verified',
    'complete_source_compiled', 'complete_module_executed',
    'observation_closed_snapshot_frozen', 'SETUP_ONLY_READ_SCOPE_PASS']
assert [row['observation_active'] for row in stages] == [False, True, True, True, False, False]
source_safety = json.loads(checked(PREP + 'source-top-level-safety.json')[0])
assert source_safety['status'] == 'PASS' and source_safety['source_API_calls_during_setup'] == 0
status = 'INDEPENDENT409_STDLIB_INITIAL_AUDIT_SOURCE_ACCEPTED_ROOT_PENDING'
FINAL.mkdir()


def save(name, value):
    raw = (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()
    with (FINAL / name).open('xb') as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    return checked(str((FINAL / name).relative_to(ROOT)))[1]


proof = dict(schema='independent410-setup-closure-proof/1', status='PASS',
    preparation_owner=prep_owner, preparation_readback_leaves=len(prep['files']),
    preparation_readback_bytes=sum(row['size'] for row in prep['files']),
    immutable_reference_descriptors=references, reference_readback_unchanged=True,
    result=result_pin, launcher_exit=exit_pin, stdout=stdout_pin, stderr=stderr_pin,
    full_source_read_scope=result['events'], source_identity=result['source_identity'],
    interval='active=True immediately before os.open through post-exec identity; active=False before tuple snapshot',
    complete_original_module_bytes_compiled_and_executed=True,
    measured_imports=0, measured_stdlib_pyc_opens=0, measured_project_pyc_opens=0,
    measured_actual_data_opens=0, source_API_calls=0,
    zero_API_proof='independent AST loading-boundary check + sealed runner makes no408 function call; no runtime profiler',
    progress_stages=stages, old409_scope_relabelled=False,
    timeout_diagnosis='SOURCE_ONLY_INFERENCE: old profiler frame.f_code audit feedback plus live-list generator traversal; old runtime events absent',
    no_old_setup_reexecution=True, new_setup_process_invocations=1,
    old_functional_completed_module_instances=1, old_timeout_completed_module_instances=None,
    new_setup_completed_module_instances=1, confirmed_completed_module_instances=2,
    total_setup_or_functional_process_attempts=3, automatic_retry=False)
proof_pin = save('final-proof.json', proof)
findings = '''# Phase410 independent408 SOURCE acceptance

Phase410 closes only the independent module setup read scope. Its sole new child exited0 within25s (external %.12fs). The complete original74685-byte408 module was opened once under canonical, regular, single-link, NOFOLLOW and stable-identity checks, matched its exact SHA, compiled and executed in an independent ModuleType with the original __file__. The measured events are exactly source open, compile, exec; imports and all stdlib/project pyc/data opens are zero. Observation stops before the immutable tuple snapshot and evidence writes. Stage stdout remains available. No profiler or object.__getattr__ observer is used.

The preparation owner was sealed before that child and all8 leaves were read back before launch and after completion. A narrow independent AST check establishes literal constants, eleven stdlib imports,29 undecorated functions with literal defaults/no evaluated annotations, an inert ValueError subclass and the skipped __main__ guard. Together with the sealed runner's absence of408 function calls, this proves setup makes zero API/main/run_audit calls without profile feedback. The SOURCE static83-leaf/29-API/inverse review and original20 functional calls were not rerun.

The immutable409 report remains BLOCKED. Its original functional evidence (7 returns,13 expected rejections) and SOURCE static PASS are retained as distinct evidence. Its original module-loader read scope remains NOT_FULLY_SATISFIED: seven unlisted stdlib pyc reads and one absent project pyc lookup. Phase410 does not rewrite that allowset or grant it a retrospective PASS. Its separate setup process timed out60s with no event/result files. The profiler frame.f_code/live-events feedback explanation remains SOURCE-only inference, not an observed runtime diagnosis.

Execution accounting is1 old functional completed module instance,1 old timeout attempt of unknown completion, and1 new completed setup instance:2 confirmed completions across3 process attempts. The new child made no408 public API calls. A preparation-only name matcher initially confused runner-local identity with the same408 function name before any preparation owner or setup child existed; the exact failed preparation source and a labelled error transcription are retained in phase410-preparation-diagnostics. The corrected local-binding check was sealed before the sole new setup launch.

This new phase410 report uses the exact408 consumer interface token INDEPENDENT409_STDLIB_INITIAL_AUDIT_SOURCE_ACCEPTED_ROOT_PENDING; its actual phase/schema and all supporting descriptors explicitly identify410. It binds the real408 source freeze/owner. It is a SOURCE acceptance pending Root review and a genuine narrow Root release, not an actual input audit permission. Actual12 semantic audit, schema/model/inputbuild/native/old SUT calls remain integer0; fullschema NOT_VALIDATED,88 source-chain targets MISSING/UNPROVEN and King/formal75 production admission remain unchanged. All original408/409 source, reports and output evidence remain retained.
''' % exit_result['elapsed_seconds']
findings_path = ROOT / 'docs/phase410_independent408_source_findings.md'
with findings_path.open('x') as handle:
    handle.write(findings)
findings_pin = checked(str(findings_path.relative_to(ROOT)))[1]
review = dict(schema='independent410-408-SOURCE-review/1', actual_phase=410,
    status=status, status_token_reason='exact interface token required by unchanged408 REVIEW_STATUS; actual review is phase410',
    module=old['module'], source_freeze=old['source_freeze'], source_owner=old['source_owner'],
    source_static_status='PASS_REUSED_IMMUTABLE409', functional_component_status='FINITE_COMPONENTS_PASS_REUSED_IMMUTABLE409',
    setup_regression_status='SETUP_ONLY_READ_SCOPE_PASS',
    original409_status=old['status'], original_read_scope_status='NOT_FULLY_SATISFIED',
    old409_report_unchanged=True, old409_allowset_unchanged=True,
    evidence=dict(original409_review=ref['data/phase409-independent408-source-review/review.json'],
        original409_owner=ref['data/phase409-independent408-source-review/owned-files.json'],
        original_static=ref['data/phase409-independent408-source-review/static-evidence.json'],
        original_functional=ref['data/phase409-independent408-component-first-001/result.json'],
        original_preload_discrepancy=ref['data/phase409-independent408-source-review/runner-preload-discrepancy.json'],
        original_timeout=ref['data/phase409-setup-only-launcher/timeout-result.json'],
        preparation_owner=prep_owner, new_setup_result=result_pin, new_setup_launcher_exit=exit_pin,
        final_proof=proof_pin, findings=findings_pin),
    source_identity=old['source_identity'], obligations=old['obligations'],
    obligation08_resolution='original functional guard evidence retained; separate410 setup scope PASS; original409 scope not retrospectively satisfied',
    dynamic=dict(original_top_level_API_calls=20, original_successful_returns=7,
        original_expected_rejections=13, new_top_level_API_calls=0, new_setup_process_invocations=1,
        old_functional_completed_module_instances=1, old_timeout_completed_module_instances=None,
        new_setup_completed_module_instances=1, confirmed_completed_module_instances=2,
        total_process_attempts=3, new_external_elapsed_seconds=exit_result['elapsed_seconds'], automatic_retry=False),
    models=0, native=0, inputbuild=0, old_SUT_calls=0, old_SUT_imports=0, schema_calls=0,
    actual12_reads=0, semantic12_audit_invocations=0, run_reads=0, capture_reads=0, expected_reads=0,
    main_run_audit_calls=0, fullschema='NOT_VALIDATED', genuine_input_accepted=False,
    King_admitted=False, formal75_production_admitted=False,
    required_targets=old['required_targets'], source_chain_status='88 MISSING/UNPROVEN; no SOURCE_DERIVED recipe',
    root_actual_audit_release_granted=False, remaining_requirement='Root all-owner readback then genuine narrowly scoped Root release before any actual audit',
    timeout_cause_provenance='SOURCE_ONLY_INFERENCE; old process no runtime events',
    unexecuted=old['unexecuted'], source_modified=False, no_more_writes_after_owner=True)
review_pin = save('review.json', review)
new_names = [row['path'] for row in prep['files']] + [prep_owner['path'],
    'tests/phase410_seal_independent408_review.py', findings_pin['path']]
for directory in ('data/phase410-preparation-diagnostics', 'data/phase410-setup-only408-first-001',
                  'data/phase410-setup-only408-launcher'):
    new_names.extend(str(path.relative_to(ROOT)) for path in sorted((ROOT / directory).iterdir()))
new_names += [proof_pin['path'], review_pin['path']]
assert len(new_names) == len(set(new_names))
rows = [checked(name)[1] for name in sorted(new_names)]
owner_pin = save('owned-files.json', dict(schema='independent410-final-evidence-owner/1',
    status=status, actual_phase=410, files=rows, ordinary_leaves=len(rows),
    ordinary_bytes=sum(row['size'] for row in rows), no_more_writes=True,
    retained_original409_status='INDEPENDENT409_STDLIB_INITIAL_AUDIT_SOURCE_BLOCKED'))
for row in rows:
    checked(row['path'], row)
print(json.dumps(dict(status=status, review=review_pin, owner=owner_pin,
    final_proof=proof_pin, ordinary_leaves=len(rows), ordinary_bytes=sum(row['size'] for row in rows),
    all_final_owned_leaves_readback=True, new_setup_invocations=1)))
