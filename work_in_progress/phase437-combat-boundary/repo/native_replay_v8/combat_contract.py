"""Fixed King-A minimum combat initial audit; full observation evidence stays intact.

This is a requirement projection, not an input builder or combat admission gate.
It never projects events, histories, RNG, callback ordering, or terminal controls.
"""
from collections import Counter
from copy import deepcopy
import argparse
import hashlib
import json
import math
from pathlib import Path
import stat

PROFILE = 'pure-combat-initial-fixed-king-A/437'
PHASES = ('pre_prepare', 'pre_activate')
UI_TIMERS = frozenset(('king_hide:P:12', 'king_drag:P:12'))
TIMER_ROLES = (('tick:P', 'tick:O') +
               tuple(f'buff:{side}:{kind}' for side in ('P', 'O') for kind in range(100, 111)) +
               ('fatigue:start', 'fatigue:tick') +
               tuple(f'aux:{side}:{name}' for side in ('P', 'O')
                     for name in ('battleRageTimer', 'autoRageTimer')) +
               ('invu:P', 'invu:O', 'king_buff:P:12', 'king_hide:P:12', 'king_drag:P:12'))
TIMER_FIELDS = ('process_mode', 'wait_time', 'time_left', 'one_shot', 'autostart',
                'paused', 'stopped', 'node.native_id', 'node.role', 'node.path',
                'node.name', 'node.class', 'node.positions', 'node.priority',
                'node.inside_tree', 'node.ordinary_physics', 'node.internal_physics',
                'node.ordinary_idle', 'node.internal_idle', 'private_left')
LINEAGE_FIELDS = ('lineage.timer_id', 'lineage.owner_id', 'lineage.kind',
                  'lineage.starts', 'lineage.stops', 'lineage.birth', 'private_provenance_label')
FIVE_TIMERS = ('invu:P', 'invu:O', 'king_buff:P:12', 'king_hide:P:12', 'king_drag:P:12')
PARTICLE_FIELDS = ('visible', 'emitting', 'one_shot', 'lifetime', 'explosiveness', 'speed_scale')
FIELD_REASONS = {
    'Character.invulBubbleVisible': 'BUBBLE_ANIMATION_ONLY',
    'King.crown': 'OBSERVER_LAST_DISPLAY_ARGUMENT_NOT_LOG_HISTORY',
    'King.light_visible': 'CIRCLE_LIGHT_RENDER_ONLY',
    'King.light_modulate': 'CIRCLE_LIGHT_RENDER_ONLY',
}
INDEX_SHA256 = '27f4a859ba9144314bb25764d6787e07c8c929e96b44c37a077c4437c47cd46b'
OVERLAY_SHA256 = '18460c39e42a3e8254aafd59d7980fc846bd3efcb9419eaf0d6383c4dd6a58aa'
SOURCE_REVIEW = {
    'path': 'data/phase437-independent-source-review-first-001/source-review.json',
    'size': 81336,
    'sha256': 'e2e50a4eca9359662e6f05790c5bac42d47181ca3e86c06a99b03a16b619be1e',
}


def full_initial_target_keys():
    keys = set()
    for phase in PHASES:
        for side in ('P', 'O'):
            for name in ('buffProtectStacks', 'invulnerable', 'invulnerabilityItem', 'invulBubbleVisible'):
                keys.add(('Character.' + name, phase, side))
        for name in ('invuCharges', 'activations', 'activationsToTrigger', 'protectedBuffs',
                     'manaCost', 'crown', 'light_visible', 'light_modulate'):
            keys.add(('King.' + name, phase, 'P:12'))
        for role in TIMER_ROLES:
            keys.update(('Timer.' + name, phase, role) for name in TIMER_FIELDS)
    for part in ('activation', 'drag'):
        keys.update(('Particle.' + part + '.' + name, 'pre_activate', 'P:12')
                    for name in PARTICLE_FIELDS)
    for role in FIVE_TIMERS:
        keys.update(('Timer.' + name, 'pre_activate', role) for name in LINEAGE_FIELDS)
    return frozenset(keys)


def excluded_reason(field_id, side_or_role):
    if field_id == 'Character.invulBubbleVisible' and side_or_role in ('P', 'O'):
        return FIELD_REASONS[field_id]
    if field_id in ('King.crown', 'King.light_visible', 'King.light_modulate') and side_or_role == 'P:12':
        return FIELD_REASONS[field_id]
    if side_or_role == 'P:12' and field_id in {
            'Particle.' + part + '.' + name for part in ('activation', 'drag') for name in PARTICLE_FIELDS}:
        return 'KING_AUTOHIDE_PARTICLE_GETTER_ONLY'
    if side_or_role in UI_TIMERS and field_id in {
            'Timer.' + name for name in TIMER_FIELDS + LINEAGE_FIELDS}:
        return 'KING_AUTOHIDE_TIMEOUT_ONLY_HIDES_PARTICLES'
    return None


def _key(row):
    if type(row) is not dict:
        raise ValueError('initial row must be a dictionary')
    key = tuple(row.get(name) for name in ('field_id', 'phase', 'side_or_role'))
    if any(type(value) is not str for value in key):
        raise ValueError('exact initial row identity required')
    return key


def _supported_class(row):
    kind = row.get('classification')
    if kind == 'MISSING':
        if row.get('proof_complete') is not False or row.get('validation_result') != 'UNPROVEN' or 'actual_value' in row:
            raise ValueError('invalid missing row')
        return 'MISSING'
    if kind not in ('DIRECT_OBSERVATION', 'SOURCE_DERIVED'):
        raise ValueError('unknown required proof classification')
    if row.get('proof_complete') is not True or row.get('validation_result') != 'SUPPORTED' or 'actual_value' not in row:
        raise ValueError('unsupported required proof shape')
    return 'DIRECT' if kind == 'DIRECT_OBSERVATION' else 'SOURCE_DERIVED'


def partition_initial_rows(rows):
    """Accept required rows plus optional historical presentation rows, unchanged.

    Excluded presentation values/proof metadata are deliberately not admission
    requirements. Unknown identities and missing required rows still reject.
    """
    if type(rows) is not list:
        raise ValueError('initial rows must be a list')
    full = full_initial_target_keys()
    required_keys = {key for key in full if excluded_reason(key[0], key[2]) is None}
    seen, required, excluded = set(), [], []
    for row in rows:
        key = _key(row)
        if key not in full or key in seen:
            raise ValueError('unknown or duplicate initial target')
        seen.add(key)
        reason = excluded_reason(key[0], key[2])
        if reason is None:
            _supported_class(row)
            required.append(deepcopy(row))
        else:
            excluded.append(dict(reason=reason, original_row=deepcopy(row)))
    if not required_keys <= seen:
        raise ValueError('missing required combat initial target')
    counts = Counter(_supported_class(row) for row in required)
    return dict(profile=PROFILE, required_rows=required, excluded_presentation=excluded,
                required_count=len(required), excluded_present_count=len(excluded),
                counts={name: counts[name] for name in ('DIRECT', 'SOURCE_DERIVED', 'MISSING')})


def project_initial_audit(index, overlay):
    """Project the pinned historical full audit and its accepted saved overlay.

    This reuses existing proof classifications, never establishes a new proof.
    """
    if type(index) is not list or {_key(row) for row in index} != full_initial_target_keys() or len(index) != 1479:
        raise ValueError('exact full historical initial contract required')
    if type(overlay) is not dict or type(overlay.get('targets')) is not list:
        raise ValueError('saved overlay targets required')
    ordinals = {_key(row): i for i, row in enumerate(index)}
    missing = {_key(row) for row in index if row.get('classification') == 'MISSING'}
    replacements = {}
    for row in overlay['targets']:
        key = _key(row)
        ordinal = row.get('original_index')
        if key not in missing or key in replacements or type(ordinal) is not int or ordinal != ordinals[key]:
            raise ValueError('overlay target identity/index mismatch')
        if _supported_class(row) not in ('SOURCE_DERIVED', 'MISSING'):
            raise ValueError('overlay may not invent a direct observation')
        replacements[key] = row
    if set(replacements) != missing:
        raise ValueError('incomplete historical source overlay')
    combined = [deepcopy(replacements.get(_key(row), row)) for row in index]
    before = Counter(_supported_class(row) for row in combined)
    result = partition_initial_rows(combined)
    result.update(schema='combat-initial-feasibility/437',
                  status='BLOCKED_COMBAT_INITIAL_GAPS' if result['counts']['MISSING'] else
                         'REPORTED_SUPPORTED_NOT_FULLSCHEMA_ADMISSION',
                  full_reference_count=len(combined), full_reference_counts=dict(before),
                  excluded_reference_counts=dict(Counter(_supported_class(x['original_row'])
                                                         for x in result['excluded_presentation'])),
                  fullschema='NOT_VALIDATED', King_admitted=False,
                  input_builds=0, models=0, captures=0,
                  events_histories_RNG_terminal_projection='UNCHANGED_NOT_FILTERED',
                  shared_render_backend_RNG_purity='UNPROVEN_NATIVE_CALLS_UNCHANGED_STRICT_RNG_GATE_RETAINED',
                  notes='Minimum initial requirement projection only; full original contracts/evidence and strict independent RNG/log/terminal gates retained.')
    return result


def _read_pinned(path, expected):
    path = Path(path)
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or path.is_symlink() or before.st_nlink != 1:
        raise ValueError('ordinary single-link saved input required')
    raw = path.read_bytes()
    after = path.lstat()
    identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    if identity(before) != identity(after) or hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError('saved input identity/hash mismatch')
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise ValueError('duplicate JSON key')
            value[key] = item
        return value
    def finite(value):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError('nonfinite JSON')
        return number
    def invalid(value):
        raise ValueError('nonfinite JSON ' + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_float=finite, parse_constant=invalid), dict(
        path=str(path), size=len(raw), sha256=expected, stable_identity=list(identity(after)))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--full-index', required=True, type=Path)
    parser.add_argument('--accepted-overlay', required=True, type=Path)
    parser.add_argument('--output-new', required=True, type=Path)
    args = parser.parse_args(argv)
    index, index_pin = _read_pinned(args.full_index, INDEX_SHA256)
    overlay, overlay_pin = _read_pinned(args.accepted_overlay, OVERLAY_SHA256)
    review_path = Path(__file__).resolve().parents[1] / SOURCE_REVIEW['path']
    review, review_pin = _read_pinned(review_path, SOURCE_REVIEW['sha256'])
    reviewed_keys = {_key(row) for row in review['excluded_rows']}
    excluded_keys = {key for key in full_initial_target_keys() if excluded_reason(key[0], key[2]) is not None}
    if reviewed_keys != excluded_keys or len(review['excluded_rows']) != len(excluded_keys):
        raise ValueError('independent source-reviewed exclusion set mismatch')
    result = project_initial_audit(index, overlay)
    contract = dict(schema='minimum-combat-initial-contract/437', profile=PROFILE,
                    required_keys=[list(key) for key in sorted(full_initial_target_keys())
                                   if excluded_reason(key[0], key[2]) is None],
                    excluded_keys=[dict(key=list(key), reason=excluded_reason(key[0], key[2]))
                                   for key in sorted(full_initial_target_keys())
                                   if excluded_reason(key[0], key[2]) is not None],
                    full_reference_count=1479, source_review=deepcopy(SOURCE_REVIEW),
                    preserves_events_histories_RNG_terminal=True,
                    genuine_input_admission=False)
    args.output_new.mkdir(parents=True, exist_ok=False)
    summary = {key: value for key, value in result.items()
               if key not in ('required_rows', 'excluded_presentation')}
    values = {'contract.json': contract, 'combat-initial-audit.json': result, 'summary.json': summary}
    # Recheck frozen inputs before declaring a saved result. No original file is written.
    _, index_after = _read_pinned(args.full_index, INDEX_SHA256)
    _, overlay_after = _read_pinned(args.accepted_overlay, OVERLAY_SHA256)
    _, review_after = _read_pinned(review_path, SOURCE_REVIEW['sha256'])
    if index_pin != index_after or overlay_pin != overlay_after or review_pin != review_after:
        raise ValueError('saved inputs changed during projection')
    values['input-readback.json'] = dict(before=[index_pin, overlay_pin, review_pin],
                                       after=[index_after, overlay_after, review_after],
                                       unchanged=True, raw_capture_EXPECTED_reads=0)
    files = []
    for name, value in values.items():
        raw = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()
        path = args.output_new / name
        with path.open('xb') as stream:
            stream.write(raw)
        files.append(dict(path=name, size=len(raw), sha256=hashlib.sha256(raw).hexdigest()))
    with (args.output_new / 'owned-files.json').open('x') as stream:
        json.dump(dict(schema='combat-initial-audit-output-owner/437', files=files,
                       paths_relative_to_output=True, self_excluded=True), stream, indent=2)
        stream.write('\n')
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
