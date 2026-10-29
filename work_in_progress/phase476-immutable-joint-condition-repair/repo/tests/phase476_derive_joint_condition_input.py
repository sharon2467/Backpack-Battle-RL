"""One fixed INPUT-only condition repair; never rebuilds12, runs a model or reads EXPECTED."""
from copy import deepcopy
from pathlib import Path
import argparse
import hashlib
import json
import math
import os
import stat

ROOT = Path(__file__).resolve().parents[1]
OLD_BUNDLE = {'path': 'data/phase470-joint-input-first-001/input-bundle.json', 'size': 500518,
              'sha256': 'bb731532d9852be73e374c0f296d5fc1d32923faeabbcef471d5aed75dee86ee'}
OLD_RECEIPT = {'path': 'data/phase470-joint-input-first-001/initial-receipt.json', 'size': 434877,
               'sha256': 'f09e7e18978582bb53b3739319609ffa62c4c0080d898f76d2a4c3f2d04fb635'}
EVIDENCE = {'path': 'data/phase475-cooldown-branch-input-evidence/receipt.json', 'size': 8279,
            'sha256': '9fa7642265d2bf4b75e42692866f9448dfb7899a6e677c14dda690df1ebfa156'}
PRIMITIVE = {'path': '/workspace/native-combat-20261013/runs/original028-king-basic-A-single-001/output/capture/observer7-primitives.jsonl',
             'size': 306106, 'sha256': 'ec5867d289ad3d6413a609e9a57a4e1af722843bdb74e6f23867ae0a84b4eba9'}
NEW_FIXTURE_SHA = '61895d66013fd6fa604ab0be8c3bc386ae20d680c78a6a888b2c7cf1c7825c59'


def require(value, message):
    if not value:
        raise ValueError(message)


def identity(raw):
    return {'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def strict_json(raw):
    def pairs(rows):
        value = {}
        for key, item in rows:
            require(key not in value, 'duplicate JSON key')
            value[key] = item
        return value
    def real(text):
        value = float(text); require(math.isfinite(value), 'nonfinite JSON real'); return value
    def invalid(value):
        raise ValueError('nonfinite JSON ' + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_float=real, parse_constant=invalid)


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def exact_raw(raw, expected):
    require(type(raw) is bytes and identity(raw) == {k: expected[k] for k in ('size', 'sha256')}, 'fixed input/evidence byte identity')


def read_pinned(row):
    path = ROOT / row['path']
    require(not any(p.is_symlink() for p in (path, *path.parents)), 'linked input/control path')
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1, 'ordinary single-link input/control')
    signature = lambda x: (x.st_dev, x.st_ino, x.st_mode, x.st_size, x.st_mtime_ns, x.st_ctime_ns)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as stream:
        opened = os.fstat(stream.fileno()); raw = stream.read(); after = os.fstat(stream.fileno())
    require(signature(before) == signature(opened) == signature(after) == signature(path.lstat()), 'input/control changed during read')
    exact_raw(raw, row)
    return raw


def derive_from_bytes(bundle_raw, evidence_raw):
    exact_raw(bundle_raw, OLD_BUNDLE); exact_raw(evidence_raw, EVIDENCE)
    evidence = strict_json(evidence_raw)
    require(evidence['schema'] == 'phase475-shared-cooldown-predicate-evidence/1'
            and evidence['status'] == 'ACCEPTED_FIXED_CASE_SOURCE_BOUND_BRANCH_WITNESS'
            and evidence['case'] == 'original028-king-basic-A-single-001', 'fixed independent Source/branch receipt')
    require(evidence['accepted_bundle'] == OLD_BUNDLE and evidence['actual_input_descriptor'] == PRIMITIVE,
            'same actual bundle/primitive provenance')
    require(evidence['derived_fixture_field'] == {'path': 'fixture.below_master', 'type': 'BOOL', 'value': True}
            and evidence['prepare_applicability']['accepted'] is True, 'fixed shared-predicate conclusion')
    facts = evidence['branch_evidence']
    require((facts['decoded_primitive_rows'], facts['cooldown_rows'], facts['selected_P_other'], facts['selected_O_belowMasterOpponent'])
            == (422, 165, 95, 70), 'fixed complete cooldown branch ledger')
    first = facts['startup'][6]
    require(first['physical_line'] == 7 and first['sequence'] == 1173 and first['item'] == 'O:11'
            and first['site'] == 'Items/Item.gd::adjustCooldown:belowMasterOpponent', 'first observed O branch')
    require(evidence['mode_evidence']['kind'] == 'SOURCE_PATH_NOT_DIRECT_MODE_SAMPLE'
            and evidence['mode_evidence']['value'] == 'Unranked'
            and evidence['mode_evidence']['specific_rank_or_rating'] is None, 'bounded Unranked Source path, no inferred rank')
    bundle = strict_json(bundle_raw)
    require(bundle['schema'] == 'native-v8-input-only/1' and bundle['synthetic_seed'] is None
            and bundle['runtime']['profile_id'] == 'pure-combat-king-basic-A-captured/1'
            and bundle['fixture']['below_master'] is False and len(bundle['draws']) == 422, 'fixed old INPUT-only proposal')
    before = b'"below_master": false'; after = b'"below_master": true'
    require(bundle_raw.count(before) == 1, 'unique raw fixture BOOL literal')
    offset = bundle_raw.index(before)
    repaired_raw = bundle_raw[:offset] + after + bundle_raw[offset + len(before):]
    expected = deepcopy(bundle); expected['fixture']['below_master'] = True
    repaired = strict_json(repaired_raw)
    require(canonical_sha(repaired) == canonical_sha(expected), 'only declared object field changed')
    require(canonical_sha(repaired['fixture']) == NEW_FIXTURE_SHA, 'new fixed fixture identity')
    require(repaired_raw[:offset] == bundle_raw[:offset]
            and repaired_raw[offset + len(after):] == bundle_raw[offset + len(before):], 'all other raw bytes retained')
    proof = {'schema': 'phase476-input-condition-derivation/1', 'status': 'INPUT_ONLY_REPAIRED_SHARED_CONDITION_NOT_RUNTIME_VALIDATED',
             'old_bundle': OLD_BUNDLE, 'old_initial_receipt_reused': OLD_RECEIPT, 'source_branch_evidence': EVIDENCE,
             'actual_primitive_identity_no_new_read': PRIMITIVE, 'new_raw_identity': identity(repaired_raw),
             'new_canonical_sha256': canonical_sha(repaired), 'new_fixture_canonical_sha256': NEW_FIXTURE_SHA,
             'only_semantic_change': {'pointer': '/fixture/below_master', 'before': False, 'after': True, 'type': 'BOOL'},
             'raw_change': {'offset': offset, 'before_ascii': before.decode(), 'after_ascii': after.decode(), 'all_other_bytes_exact': True},
             'scope': 'Fixed Unranked shared predicate controls Character accuracy/crit biases and Opponent cooldown together; no rank value or random-return inference.',
             'old_acceptance_qualification': 'Old transport/initial receipt retained; old false environment proposal was rejected at475; no old runtime validation is claimed.',
             'counts': {'derived_bundles': 1, 'twelve_input_rebuilds': 0, 'initial_receipt_regenerations': 0,
                        'raw_primitive_reads': 0, 'schema_imports': 0, 'models': 0, 'Expected_reads': 0, 'Oracle': 0, 'pool': 0},
             'model_release': False}
    return repaired_raw, proof


def write_raw(path, raw):
    with path.open('xb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    require(path.read_bytes() == raw, 'output readback')
    return {'path': str(path.relative_to(ROOT)), **identity(raw)}


def write_json(path, value):
    return write_raw(path, (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n').encode())


def build_from_files(output_new):
    out = Path(output_new); out = out if out.is_absolute() else ROOT / out
    require(out.parent == ROOT / 'data' and out.name.startswith('phase476-') and not out.exists()
            and not any(x.is_symlink() for x in (out, *out.parents)), 'new fixed local derivation output only')
    out.mkdir(mode=0o700); owned = []
    try:
        old_raw = read_pinned(OLD_BUNDLE); fact_raw = read_pinned(EVIDENCE); receipt_raw = read_pinned(OLD_RECEIPT)
        repaired_raw, proof = derive_from_bytes(old_raw, fact_raw)
        owned.append(write_raw(out / 'input-bundle.json', repaired_raw))
        owned.append(write_json(out / 'derivation-proof.json', proof))
        require(read_pinned(OLD_BUNDLE) == old_raw and read_pinned(EVIDENCE) == fact_raw
                and read_pinned(OLD_RECEIPT) == receipt_raw, 'actual inputs/control/receipt readback unchanged')
        owned.append(write_json(out / 'readback.json', {'source_inputs': [OLD_BUNDLE, EVIDENCE, OLD_RECEIPT], 'unchanged': True,
            'whole_file_hash_reads': {'old_bundle': 2, 'evidence': 2, 'old_receipt_hash_only_not_revalidated': 2},
            'raw_capture_INPUT_reads': 0, 'Expected_reads': 0, 'model': 0, 'initial_receipt_regenerations': 0}))
        owned.append(write_json(out / 'reused-initial-receipt.json', {'descriptor': OLD_RECEIPT,
            'scope': 'Exact original74 initial derivations/runtime typed values; no receipt regeneration or initial proof rerun.'}))
        owned.append(write_json(out / 'input-seal.json', {'schema': 'phase476-derived-input-seal/1',
            'status': proof['status'], 'files': deepcopy(owned), 'old_initial_receipt_reused': OLD_RECEIPT,
            'source_branch_evidence': EVIDENCE, 'model_release': False, 'independent_acceptance': 'PENDING'}))
        write_json(out / 'owned-files.json', {'schema': 'phase476-derived-input-owner/1', 'files': owned, 'no_more_writes': True})
    except BaseException as error:
        write_json(out / 'first-error.json', {'status': 'FIRST_ERROR_STOPPED', 'type': type(error).__name__,
            'reason': str(error), 'preserved_outputs': owned, 'automatic_retry': False, 'model': 0, 'Expected': 0})
        raise
    return {'output': str(out), 'status': proof['status'], 'input_bundle': owned[0], 'actual_derivations': 1, 'models': 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-new', required=True)
    args = parser.parse_args()
    print(json.dumps(build_from_files(args.output_new), sort_keys=True))


if __name__ == '__main__':
    main()
