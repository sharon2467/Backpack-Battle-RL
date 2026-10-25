"""First King SOURCE block: lawful bytes/proof interface, never a bundle builder.

This module has no filesystem reader, CLI, capture/expected loader or model entry.
The future observer profile must implement the complete typed record schema before
validate_decoded_proofs can be used. Neither routine authenticates native output.
"""
import json
import math

PROFILE = 'observer7-355-native-single-king-A/1'
OBSERVER_VERSION = '7-king-single-A-355'
CASE = 'KING-K1-A-353'
INPUT_FILES = (
    'fixture.json', 'player_fixture.json', 'observer7-input.jsonl',
    'observer7-lineage.jsonl', 'observer7-metadata.jsonl', 'observer7-primitives.jsonl',
    'king-clock-checkpoint.json', 'king-clock-passes.jsonl', 'king-input-facts.json',
    'king-ui-authority.jsonl', 'king-rng-checkpoint.json',
)
CHANNEL_FILES = {
    'observer7-input.jsonl': 'input', 'observer7-lineage.jsonl': 'lineage',
    'observer7-metadata.jsonl': 'metadata', 'observer7-primitives.jsonl': 'primitive',
}
TOTAL_BYTES = 268435456
FILE_CAPS = dict.fromkeys(INPUT_FILES, TOTAL_BYTES)
FILE_CAPS.update({
    'king-clock-checkpoint.json': 2097152, 'king-clock-passes.jsonl': 67108864,
    'king-input-facts.json': 2097152, 'king-ui-authority.jsonl': 8388608,
    'king-rng-checkpoint.json': 16384,
})
LINE_CAPS = dict.fromkeys(CHANNEL_FILES, 2097152)
LINE_CAPS.update({'king-clock-passes.jsonl': 1024, 'king-ui-authority.jsonl': 16384})
ROW_CAPS = dict.fromkeys(CHANNEL_FILES, 1000000)
ROW_CAPS.update({'king-clock-passes.jsonl': 200000, 'king-ui-authority.jsonl': 65536})
RUNTIME_KEYS = frozenset((
    'schema', 'mode', 'profile_id', 'checkpoint', 'environment', 'nodes',
    'timer_lineage', 'initial_items', 'prepare_order', 'activate_order',
    'terminal_profile', 'frame_clock', 'king_particles', 'root_node',
    'processing_nodes', 'inactive_auxiliaries', 'ui_authority',
))
PROOF_ONLY = frozenset((
    'source_resources', 'source_defaults', 'initial_rng', 'rng_checkpoint',
    'fresh_facts', 'source_caches', 'source_proof', 'cleanup', 'terminal_endpoint',
))


def strict_json(raw):
    def pairs(rows):
        result = {}
        for key, value in rows:
            if key in result:
                raise ValueError('duplicate source JSON key ' + key)
            result[key] = value
        return result
    def real(text):
        value = float(text)
        if not math.isfinite(value):
            raise ValueError('nonfinite source JSON number')
        return value
    def invalid(text):
        raise ValueError('nonfinite source JSON constant ' + text)
    return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
                      parse_float=real, parse_constant=invalid)


def decode_sources(raw_by_name):
    """Validate framing/order before filtering, grouping or typed delegation.

    The returned lists retain their original physical order and primitive DTOs.
    They are transport-checked data, not admitted runtime or an input bundle.
    """
    if type(raw_by_name) is not dict or set(raw_by_name) != set(INPUT_FILES):
        raise ValueError('exact eleven lawful source names; no expected files')
    if any(type(raw_by_name[n]) is not bytes or not 0 < len(raw_by_name[n]) <= FILE_CAPS[n]
           for n in INPUT_FILES):
        raise ValueError('nonempty bounded raw source bytes required')
    if sum(len(value) for value in raw_by_name.values()) > TOTAL_BYTES:
        raise ValueError('eleven-source total byte cap')
    decoded = {}
    seen = set()
    for name in INPUT_FILES:
        raw = raw_by_name[name]
        if not name.endswith('.jsonl'):
            decoded[name] = strict_json(raw)
            continue
        if not raw.endswith(b'\n'):
            raise ValueError('source JSONL final newline ' + name)
        lines = raw.splitlines(keepends=True)
        if not 1 <= len(lines) <= ROW_CAPS[name]:
            raise ValueError('source JSONL row cap ' + name)
        rows = []
        previous = -1
        for line in lines:
            if not line.strip() or len(line) > LINE_CAPS[name]:
                raise ValueError('source JSONL record cap ' + name)
            row = strict_json(line)
            if type(row) is not dict:
                raise ValueError('source JSONL object required ' + name)
            if name in CHANNEL_FILES:
                seq = row.get('sequence')
                if (row.get('schema') != 'observer7-record/1'
                        or row.get('channel') != CHANNEL_FILES[name]
                        or type(seq) is not int or not previous < seq < (1 << 63)
                        or seq in seen):
                    raise ValueError('physical source channel/order/global sequence ' + name)
                previous = seq
                seen.add(seq)
            rows.append(row)
        decoded[name] = rows
    for row in decoded['observer7-primitives.jsonl']:
        payload = row.get('payload')
        if type(payload) is not dict or payload.get('kind') not in ('randf', 'randf_range', 'randi_range'):
            raise ValueError('K1 Util primitive ABI only; no Mirror/global_u32')
    return decoded


def validate_decoded_proofs(decoded, fixture, native_profile):
    """Future pure SOURCE validator. No initial state, draws or bundle returned.

    The native schema module is trusted frozen host code, never a JSON readiness
    assertion. That module/collector is an explicitly pending later SOURCE block.
    """
    if type(decoded) is not dict or set(decoded) != set(INPUT_FILES):
        raise ValueError('complete decoded eleven-source interface')
    if native_profile.VERSION != OBSERVER_VERSION or native_profile.PROFILE != PROFILE:
        raise ValueError('new frozen King typed observer SOURCE schema required')
    for name in CHANNEL_FILES:
        for row in decoded[name]:
            native_profile.schema.validate_record(row)
    from native_replay_v8.genuine import (
        validate_single_king_fixture, validate_single_king_input_provenance,
    )
    from native_replay_v7.frame_driver import decode_clock
    validate_single_king_fixture(fixture)
    for side, name in (('P', 'player_fixture.json'), ('O', 'fixture.json')):
        raw = decoded[name]
        if type(raw) is not dict or set(raw) != {'schema_version', 'game_version', 'class', 'health', 'stamina', 'items'}:
            raise ValueError('closed native source fixture ' + side)
        if type(raw['schema_version']) is not int or raw['schema_version'] != 1 or raw['game_version'] != '1.1.8':
            raise ValueError('native source fixture schema/version ' + side)
        index = 0 if side == 'P' else 1
        expected = fixture['sides'][index]
        if (type(raw['class']) is not int or raw['class'] != 0
                or type(raw['health']) not in (int, float) or type(raw['stamina']) not in (int, float)
                or raw['health'] != expected['hp'] or raw['stamina'] != expected['stamina']):
            raise ValueError('fixed A native source class/resources ' + side)
        items = [{key: value for key, value in item.items() if key != 'instance_id'}
                 for item in expected['items']]
        if json.dumps(raw['items'], sort_keys=True, allow_nan=False) != json.dumps(items, sort_keys=True, allow_nan=False):
            raise ValueError('exact A native source inventory/typed geometry ' + side)
    header = decoded['king-clock-checkpoint.json']
    if type(header) is not dict or set(header) != {'schema', 'lineage', 'environment', 'checkpoint'}:
        raise ValueError('closed external clock header')
    clock = decode_clock(dict(header, passes=decoded['king-clock-passes.jsonl']))
    proof = validate_single_king_input_provenance(
        decoded['king-ui-authority.jsonl'], decoded['king-rng-checkpoint.json'],
        decoded['observer7-input.jsonl'], decoded['observer7-lineage.jsonl'],
        decoded['king-input-facts.json'], clock,
    )
    return dict(schema='phase355-eleven-source-proof-interface/1', proof=proof,
                bundle_build='NOT_IMPLEMENTED_FIRST_SOURCE_BLOCK',
                runtime_returned=False, draws_returned=False, model_calls=0)


def check_runtime_projection(runtime):
    """Structural boundary for the future adapter; not an adapter or admission."""
    if type(runtime) is not dict or set(runtime) != RUNTIME_KEYS or set(runtime) & PROOF_ONLY:
        raise ValueError('proof/outcome observations leaked into runtime projection')
    if runtime['profile_id'] != PROFILE or runtime['mode'] != 'genuine':
        raise ValueError('new King finite runtime projection only')
    return True
