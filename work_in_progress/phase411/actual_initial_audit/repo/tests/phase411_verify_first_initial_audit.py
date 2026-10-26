"""Seal independent evidence verification; no408/schema/engine API imports."""
import collections
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import struct

ROOT = Path('/workspace/python-original-engine/repo')
OUT = ROOT / 'data/phase411-independent-initial-audit-launcher'
AUDIT = ROOT / 'data/phase408-initial-audit-first-001'
assert not (OUT / 'verification-report.json').exists()
checked_rows = []


def identity(info):
    return [info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns]


def checked(path, expected=None):
    assert path.resolve(strict=True) == path and path.is_absolute()
    assert not any(p.is_symlink() for p in (path, *path.parents))
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and before.st_nlink == 1
    if expected is not None:
        assert before.st_size == expected['size']
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        assert identity(os.fstat(fd)) == identity(before)
        chunks = []
        remaining = before.st_size + 1
        while remaining:
            chunk = os.read(fd, remaining)
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        raw = b''.join(chunks)
        assert identity(os.fstat(fd)) == identity(before)
    finally:
        os.close(fd)
    assert identity(path.lstat()) == identity(before) and len(raw) == before.st_size
    row = dict(path=str(path.relative_to(ROOT)), size=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    if expected is not None:
        assert row['size'] == expected['size'] and row['sha256'] == expected['sha256']
    checked_rows.append(row)
    return raw, row


def load(path, expected=None):
    raw, row = checked(path, expected)
    return json.loads(raw), row


def save(name, value):
    with (OUT / name).open('x') as handle:
        json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write('\n')
        handle.flush()
        os.fsync(handle.fileno())


def same(left, right):
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return left.keys() == right.keys() and all(same(left[key], right[key]) for key in left)
    if type(left) is list:
        return len(left) == len(right) and all(same(a, b) for a, b in zip(left, right))
    return left == right


def typed_real(value):
    if not (type(value) is dict and set(value) == {'type', 'binary64_be'} and
            value['type'] == 'float' and type(value['binary64_be']) is str and
            re.fullmatch('[0-9a-f]{16}', value['binary64_be'])):
        return False
    return math.isfinite(struct.unpack('>d', bytes.fromhex(value['binary64_be']))[0])


def domain(row):
    field, role = row['field_id'], row['side_or_role']
    value = row['actual_value']
    if type(row.get('constraint')) is dict:
        return same(value, row['constraint'])
    if field.startswith('Timer.node.'):
        name = field[len('Timer.node.'):]
        if name in ('ordinary_physics', 'internal_physics', 'ordinary_idle', 'internal_idle'):
            return value is False
        if name == 'inside_tree':
            return value is True
        if name == 'priority':
            return type(value) is int
        if name == 'positions':
            return type(value) is list and bool(value) and all(type(item) is int for item in value)
        if name == 'role':
            return value is None or type(value) is str
        if name == 'class':
            return value == 'Timer' and type(value) is str
        if name == 'native_id':
            return type(value) is str and re.fullmatch('[1-9][0-9]*', value) is not None
        return type(value) is str
    if field.startswith('Timer.lineage.'):
        name = field[len('Timer.lineage.'):]
        if name == 'starts':
            return type(value) is int and value == 0
        if name == 'stops':
            return type(value) is int and value >= 0
        if name == 'birth':
            return type(value) is dict
        return type(value) is str
    if field == 'Timer.private_provenance_label':
        return value == 'source_constructor_minus_one_no_start_not_public_zero_inference'
    if field.startswith('Timer.'):
        name = field[len('Timer.'):]
        if name == 'process_mode':
            return type(value) is int and value == (1 if role.startswith(('king_hide:', 'king_drag:')) else 0)
        if name == 'wait_time':
            return typed_real(value) and struct.unpack('>d', bytes.fromhex(value['binary64_be']))[0] > 0
        if name == 'time_left':
            return same(value, {'type': 'float', 'binary64_be': '0000000000000000'})
        if name == 'one_shot':
            return value is (not role.startswith('tick:'))
        return value is (name == 'stopped')
    raise AssertionError('Unclassified independent domain: ' + field)


review = dict(schema='independent411-first-real-initial-audit-verification/1', actual_phase=411,
    status='FIRST_ACTUAL_AUDIT_EVIDENCE_BLOCKED', actual_audit_invocations=None,
    automatic_retry=False, models=0, native=0, inputbuild=0, old_SUT_calls=0,
    old_SUT_imports=0, schema_calls=0, optional391_calls=0, expected_reads=0,
    input_content_reads_by_external_launcher_or_verifier=0,
    fullschema='NOT_VALIDATED', genuine_input_accepted=False, King_admitted=False,
    formal75_currently_accepted=True, continuation_authorized=False)
try:
    preparation, prep_pin = load(OUT / 'preparation-owner.json')
    for row in preparation['files']:
        checked(ROOT / row['path'], row)
    args, args_pin = load(OUT / 'args.json')
    release, release_pin = load(ROOT / args['genuine_release']['path'], args['genuine_release'])
    accepted, accepted_pin = load(ROOT / args['source_acceptance']['path'], args['source_acceptance'])
    preflight, preflight_pin = load(OUT / 'source-preflight.json')
    before_meta, before_pin = load(OUT / 'input-metadata-before.json')
    after_meta, after_pin = load(OUT / 'input-metadata-after.json')
    receipt, receipt_pin = load(OUT / 'exit.json')
    stdout, stdout_pin = checked(OUT / 'stdout.txt')
    stderr, stderr_pin = checked(OUT / 'stderr.txt')
    assert receipt['child_invocations'] == 1 and receipt['automatic_retry'] is False
    review.update(actual_audit_invocations=1, process=receipt,
        Root_release=release_pin, Root_source_acceptance=accepted_pin,
        preparation_owner=prep_pin, preflight=preflight_pin,
        launcher_receipts=dict(args=args_pin, exit=receipt_pin, stdout=stdout_pin, stderr=stderr_pin))
    assert receipt['child_exit_code'] == 0 and receipt['timed_out'] is False, 'first actual child failed; no retry'
    assert receipt['total_launcher_elapsed_seconds'] < 60
    assert not stderr
    assert before_meta['content_reads'] == after_meta['content_reads'] == 0
    assert after_meta['matches_before'] is True and before_meta['identities'] == after_meta['identities']
    for name, value in after_meta['identities'].items():
        assert identity(Path(name).lstat()) == value
    original_owner, original_owner_pin = load(AUDIT / 'owned-files.json')
    assert original_owner['schema'] == 'phase408-actual-initial-audit-owner/1' and original_owner['no_more_writes'] is True
    output = {}
    output_pins = {}
    for row in original_owner['files']:
        assert Path(row['path']).name == row['path']
        output[row['path']], output_pins[row['path']] = load(AUDIT / row['path'], row)
    assert set(output) == {'report.json', 'summary.json', 'rawtyped-field-index.json',
        'identity-domain-findings.json', 'io-observations.json', 'source-references.json'}
    report, summary = output['report.json'], output['summary.json']
    review.update(audit_report_status=report['status'], audit_output_owner=original_owner_pin,
        audit_output_pins=output_pins, original_summary=summary)
    assert summary['audit_invocations'] == summary['new_audit_module_execution'] == 1
    assert summary['first_error'] is None and report['status'] != 'FAILED_SOURCE_INTEGRITY'
    assert report['fullschema'] == 'NOT_VALIDATED' and report['genuine_input_accepted'] is False
    for container, keys in ((summary, ('old_SUT_calls', 'old_SUT_imports', 'schema_calls', 'models', 'inputbuild', 'bundle', 'projection', 'native', 'restore', 'READY')),
                            (report, ('old_SUT_calls', 'schema_calls', 'models', 'inputbuild', 'projection'))):
        assert all(type(container[key]) is int and container[key] == 0 for key in keys)
    refs = output['source-references.json']
    assert refs['source_freeze'] == release['source_freeze'] and refs['source_owner'] == release['source_owner']
    freeze, freeze_pin = load(ROOT / release['source_freeze']['path'], release['source_freeze'])
    assert refs['static_pins'] == freeze['static_pins'] and len(refs['static_pins']) == 49
    allowed = {}
    for row in [args['genuine_release'], release['source_freeze'], release['source_owner'],
                release['source_review'], release['source_review_owner']]:
        allowed[str(ROOT / row['path'])] = row
    for name, row in refs['static_pins'].items():
        path = Path(name) if Path(name).is_absolute() else ROOT / name
        allowed[str(path)] = row
    for row in freeze['files']:
        if row['path'] not in refs['static_pins']:
            allowed[str(ROOT / row['path'])] = row
    capture_paths = {}
    for name, row in release['input_files'].items():
        path = str(Path(release['input_directory']) / name)
        capture_paths[path] = dict(path=path, **row)
        allowed[path] = capture_paths[path]
    io = output['io-observations.json']
    assert io['violations'] == []
    phase_counts = {}
    for phase in ('before', 'readback'):
        rows = io[phase]
        assert len(rows) == len(allowed) and len({row['path'] for row in rows}) == len(allowed)
        assert {row['path'] for row in rows} == set(allowed)
        for row in rows:
            pin = allowed[row['path']]
            assert row['size'] == pin['size'] and row['sha256'] == pin['sha256']
            assert identity(Path(row['path']).lstat()) == row['identity']
            if row['path'] in capture_paths:
                assert row['identity'] == before_meta['identities'][row['path']]
        phase_counts[phase] = dict(all_successful_content_reads=len(rows),
            lawful_capture_content_reads=sum(row['path'] in capture_paths for row in rows))
    assert {row['path']: row for row in io['before']} == {row['path']: row for row in io['readback']}
    old_review, old_review_pin = load(ROOT / release['source_review']['path'], release['source_review'])
    old_owner_pin = old_review['evidence']['original409_owner']
    old_owner, unused = load(ROOT / old_owner_pin['path'], old_owner_pin)
    old_index = {row['path']: row for row in old_owner['files']}
    targets_name = 'data/phase409-independent408-source-review/independently-derived-targets.json'
    targets, targets_pin = load(ROOT / targets_name, old_index[targets_name])
    required = {(row['field_id'], row['phase'], row['side_or_role']): row['route'] for row in targets}
    rows = output['rawtyped-field-index.json']
    findings = output['identity-domain-findings.json']
    assert len(rows) == len(required) == 1479
    assert len({(row['field_id'], row['phase'], row['side_or_role']) for row in rows}) == len(rows)
    assert {(row['field_id'], row['phase'], row['side_or_role']) for row in rows} == set(required)
    classes = collections.Counter()
    validations = collections.Counter()
    domains = []
    for row in rows:
        key = (row['field_id'], row['phase'], row['side_or_role'])
        assert all(type(row[name]) is str for name in ('field_id', 'phase', 'side_or_role', 'classification', 'validation_result'))
        assert type(row['proof_complete']) is bool
        classification, validation = row['classification'], row['validation_result']
        assert classification in ('DIRECT_OBSERVATION', 'SOURCE_DERIVED', 'MISSING')
        assert validation in ('SUPPORTED', 'UNPROVEN', 'REJECTED')
        classes[classification] += 1
        validations[validation] += 1
        assert classification != 'SOURCE_DERIVED'
        if required[key] == 'source':
            assert classification == 'MISSING'
            assert row['missing_reason'] == 'AUDIT_RECIPE_NOT_ESTABLISHED_NOT_PROOF_ORIGINAL_DATA_ABSENT'
            assert row['source_refs'] and row['unresolved']
        if classification == 'MISSING':
            assert validation == 'UNPROVEN' and row['proof_complete'] is False and 'actual_value' not in row
        else:
            assert classification == 'DIRECT_OBSERVATION' and 'actual_value' in row and row['input_refs']
            valid = domain(row)
            if validation == 'SUPPORTED':
                assert valid and row['proof_complete'] is True, key
            else:
                assert validation == 'REJECTED' and row['proof_complete'] is False
            domains.append(dict(field_id=key[0], phase=key[1], side_or_role=key[2],
                scalar_domain_valid=valid, source_audit_validation=validation))
        for reference in row['input_refs']:
            assert reference['file'] in release['input_files']
            assert type(reference['pointer']) is str and reference['pointer'].startswith('/')
            if 'line' in reference:
                assert type(reference['line']) is int and reference['line'] > 0
            if reference.get('native_owner') is not None:
                assert type(reference['native_owner']) is str and re.fullmatch('[1-9][0-9]*', reference['native_owner'])
    counts = {name: classes[name] for name in ('DIRECT_OBSERVATION', 'SOURCE_DERIVED', 'MISSING')}
    assert counts == report['classifications'] and report['field_count'] == len(rows)
    assert validations['REJECTED'] == report['rejected_fields']
    assert all(set(row) == {'kind', 'detail'} and row['kind'] == 'DOMAIN_REJECTED' and type(row['detail']) is str for row in findings)
    inferred = 'REJECTED_INITIAL_DOMAIN' if validations['REJECTED'] or findings else 'BLOCKED_INITIAL_SOURCE_GAPS' if classes['MISSING'] or validations['UNPROVEN'] else 'FEASIBLE_PENDING_FULL_STRUCTURAL_VALIDATION'
    assert report['status'] == inferred == summary['status']
    parsed_stdout = json.loads(stdout)
    assert parsed_stdout['status'] == report['status'] and parsed_stdout['output'] == str(AUDIT)
    domain_rows = dict(schema='independent411-output-field-domain-checks/1', field_count=len(rows),
        classifications=counts, validation_states=dict(validations), direct_scalar_checks=domains,
        missing_recipe_interpretation='not established recipe does not prove original data absent; no recapture requirement inferred',
        independent_provenance_scope='file membership/pointer syntax plus original audit SOURCE proof; raw capture pointers not separately dereferenced',
        raw_capture_content_reads_by_verifier=0)
    save('field-domain-validation.json', domain_rows)
    review.update(status='FIRST_REAL_INITIAL_AUDIT_EVIDENCE_VERIFIED_ROOT_PENDING',
        field_classifications=counts, field_validation_states=dict(validations), rejected_fields=validations['REJECTED'],
        identity_domain_findings=findings, logical_targets=1479,
        input_read_accounting=dict(unique_lawful_capture_files=12, phases=phase_counts,
            successful_capture_content_reads=sum(value['lawful_capture_content_reads'] for value in phase_counts.values()),
            audit_invocations=1, original_seal_readback_is_second_read_not_retry=True),
        source_control_input_pin_set_exact=True, before_readback_and_external_identity_stable=True,
        guard_violations=[], source_freeze=release['source_freeze'], source_owner=release['source_owner'],
        source_review=release['source_review'], source_review_owner=release['source_review_owner'],
        new_audit_calls=dict(main=1, run_audit=1, read_lawful12_once=1, index_initial_observations=1,
            audit_direct_fields=1, audit_source_chain=1, assess_initial_feasibility=1, seal_audit_once=1),
        new_audit_call_count_basis='successful fixed original CLI control flow and original summary; no runtime function profiler; internal utility counts not observed',
        field_domain_verification='all output DIRECT scalar/configuration domains; exact independent409 field/phase/role coverage; raw capture pointers not separately dereferenced',
        missing_recipe_interpretation='AUDIT_RECIPE_NOT_ESTABLISHED_NOT_PROOF_ORIGINAL_DATA_ABSENT',
        feasibility_accepted=False, next_step='Root independent evidence review only; no structural/model/native continuation')
except BaseException as exc:
    review['first_verification_error'] = dict(type=type(exc).__name__, message=str(exc))
    review['preserve_first_actual_audit_and_stop'] = True
save('verification-report.json', review)
names = ['docs/phase411_independent_first_initial_audit_spec.md',
         'tests/phase411_launch_first_initial_audit.py', 'tests/phase411_verify_first_initial_audit.py']
names += [str(path.relative_to(ROOT)) for path in sorted(OUT.iterdir()) if path.is_file()]
if AUDIT.exists():
    names += [str(path.relative_to(ROOT)) for path in sorted(AUDIT.iterdir()) if path.is_file()]
owner_rows = [checked(ROOT / name)[1] for name in names]
save('owned-files.json', dict(schema='independent411-first-real-audit-evidence-owner/1',
    files=owner_rows, ordinary_leaves=len(owner_rows), ordinary_bytes=sum(row['size'] for row in owner_rows),
    no_more_writes=True, actual_audit_invocations=review['actual_audit_invocations'],
    automatic_retry=False, status=review['status']))
for row in owner_rows:
    checked(ROOT / row['path'], row)
raw, owner_pin = checked(OUT / 'owned-files.json')
report_pin = checked(OUT / 'verification-report.json')[1]
print(json.dumps(dict(status=review['status'], audit_status=review.get('audit_report_status'),
    report=report_pin, owner=owner_pin, ordinary_leaves=len(owner_rows),
    ordinary_bytes=sum(row['size'] for row in owner_rows), all_owner_leaves_readback=True)))
