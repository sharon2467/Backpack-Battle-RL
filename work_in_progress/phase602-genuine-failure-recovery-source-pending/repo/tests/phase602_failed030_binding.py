"""Pure fixed failed030 association. No filesystem or process operation."""
import hashlib
import json

ROOT_PREFIX = '/workspace/python-original-engine/repo/'
MATERIAL_PINS = {'authority': {'path': 'data/phase601-root-failed030-authority/authority.json', 'size': 8428, 'sha256': 'acde0c7ae926c0f1b097e7cee662fbd93416a68352d51c6c556d7c021fd04495'}, 'authority_owner': {'path': 'data/phase601-root-failed030-authority/owned-files.json', 'size': 531, 'sha256': '033b4c6563c5d31d6a4688a1a82cafe3d8f355141aa62258177112ce69caf77a'}, 'saved_failed': {'path': 'data/phase601-root-failed030-authority/actual-failed-state.json', 'size': 246, 'sha256': '698998f49b9bbe4dba03693016c3b35aca6d7a7129278aa187a77ba5ad7bc6ed'}, 'execute_owner': {'path': 'data/phase600-root-fixed030-execute-first-001/owned-files.json', 'size': 1399, 'sha256': 'd31a4321a490e47a93cc38a5fe5d122ccfa2c0390e7f43a9068e9e0ea5c00f74'}, 'invocation': {'path': 'data/phase600-root-fixed030-execute-first-001/invocation.json', 'size': 901, 'sha256': 'e722ee4b3db7f6f531f09be656b0ada6e712d9778a53c02e5fafffe10cae66c1'}, 'execution': {'path': 'data/phase600-root-fixed030-execute-first-001/execution.json', 'size': 1130, 'sha256': 'b60cf3213d4e7ac9b034d58080ef49fe394be423afd53d99a592009aa91b7410'}, 'first_error': {'path': 'data/phase600-root-fixed030-execute-first-001/first-error.json', 'size': 1130, 'sha256': 'b60cf3213d4e7ac9b034d58080ef49fe394be423afd53d99a592009aa91b7410'}, 'release': {'path': 'data/phase600-root-fixed030-execute-first-001/release.json', 'size': 1054, 'sha256': '8b66346f7d25c240fafd5f9806f8ee2f438a58fc53de4dbb8272c5b6bf5b7b13'}, 'config': {'path': 'data/phase597-resume030-conditional-release/oracle-acceptance.json', 'size': 3597, 'sha256': 'e5ccc41095e84fc644175910e229240a9749562ea1d98bb9d8e5fae17f51b7fd'}, 'config_owner': {'path': 'data/phase597-resume030-conditional-release/owned-files.json', 'size': 659, 'sha256': 'd583e4d370100b16d9d33d57e4677c2d000b36ad4272b3935ca950c02c7451ad'}}
EXPECTED_ARGV = ['/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python', '-B', '/workspace/python-original-engine/repo/tests/phase590_oracle_host.py', '--source-root', '/workspace/python-original-engine/repo', '--task-root', '/workspace/godotsteam-startup-20261013', '--baseline', '/workspace/godotsteam-startup-20261013/baseline/Backpack Battles', '--pool', '/workspace/native-combat-20261013/pool', '--runs-root', '/workspace/native-combat-20261013/runs', '--config', 'data/phase597-resume030-conditional-release/oracle-acceptance.json', '--config-size', '3597', '--config-sha256', 'e5ccc41095e84fc644175910e229240a9749562ea1d98bb9d8e5fae17f51b7fd', '--execute']
EXPECTED_HOST_FREEZE = {'path': 'data/phase590-case030-host-restore-source/combined-source-freeze.json', 'size': 65460, 'sha256': '2655616e809ea39c7cf6f4d3d6eed24dd68cce2cf134b7d499c213cee292f6b6'}
FIXED_RUN = '/workspace/native-combat-20261013/runs/original030-mixed-modifiers-A-single-001'
FIXED_POOL = '/workspace/native-combat-20261013/pool'
FIXED_PREVIOUS = '/workspace/native-combat-20261013/runs/original027-king-single-A-20261026-attempt06'
FIXED_REASON = "RuntimeError('first original030 failed/partial; preserve, no retry')"


def _require(condition, label):
    if not condition:
        raise ValueError(label)


def _same(actual, expected, label):
    _require(type(actual) is type(expected), label + ':type')
    if type(actual) is dict:
        _require(set(actual) == set(expected), label + ':keys')
        for key in actual:
            _same(actual[key], expected[key], label + '/' + str(key))
    elif type(actual) is list:
        _require(len(actual) == len(expected), label + ':length')
        for index, (left, right) in enumerate(zip(actual, expected)):
            _same(left, right, label + '/' + str(index))
    else:
        _require(actual == expected, label + ':value')


def _path(value):
    _require(type(value) is str and bool(value) and '..' not in value.split('/'), 'fixed descriptor path')
    return value if value.startswith('/') else ROOT_PREFIX + value


def _descriptor(value):
    _require(type(value) is dict and set(value) == {'path', 'size', 'sha256'}, 'closed fixed descriptor')
    _require(type(value['size']) is int and value['size'] >= 0 and type(value['sha256']) is str
             and len(value['sha256']) == 64 and all(c in '0123456789abcdef' for c in value['sha256']),
             'typed descriptor identity')
    return dict(path=_path(value['path']), size=value['size'], sha256=value['sha256'])


def _owned(owner, target, label):
    _require(type(owner) is dict and type(owner['files']) is list, label + ':owner')
    selected = [row for row in owner['files'] if _path(row['path']) == _path(target['path'])]
    _require(len(selected) == 1, label + ':unique member')
    _same(_descriptor(selected[0]), _descriptor(target), label + ':owned descriptor')


def _decode(raw):
    def pairs(rows):
        value = {}
        for key, item in rows:
            _require(key not in value, 'duplicate metadata key')
            value[key] = item
        return value
    def invalid(value):
        raise ValueError('nonfinite metadata literal:' + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)


def validate_failure_association(raw_materials, state_image, controls, saved_ready, evidence, previous, role):
    """Called after actual controls image validation, inside the original pool lock."""
    _require(type(raw_materials) is dict and set(raw_materials) == set(MATERIAL_PINS), 'closed fixed authority materials')
    values = {}
    for key, row in MATERIAL_PINS.items():
        raw = raw_materials[key]
        _require(type(raw) is bytes, 'authority material bytes:' + key)
        _same(dict(size=len(raw), sha256=hashlib.sha256(raw).hexdigest()),
              {k: row[k] for k in ('size', 'sha256')}, 'fixed material SHA:' + key)
        values[key] = _decode(raw)
    authority, authority_owner = values['authority'], values['authority_owner']
    _same(authority['schema'], 'phase601-actual-failed030-restoration-authority/1', 'authority schema')
    _same(authority_owner['schema'], 'phase601-failure-authority-owner/1', 'authority owner schema')
    _owned(authority_owner, MATERIAL_PINS['authority'], 'owned actual authority')
    _owned(authority_owner, MATERIAL_PINS['saved_failed'], 'owned actual failed copy')
    _same(authority['case_id'], 'NATIVE-030-MIXED-MODIFIERS-A', 'actual case')
    _same(authority['run'], FIXED_RUN, 'actual run')
    _same(authority['pool'], FIXED_POOL, 'actual pool')
    _same(authority['previous_run'], FIXED_PREVIOUS, 'actual predecessor authority')
    _same(previous, FIXED_PREVIOUS, 'request actual predecessor')
    for authority_key, source_key in [('saved_failed_state', 'saved_failed'), ('root_execute_receipt', 'execution'),
                                      ('root_execute_owner', 'execute_owner'), ('root_execute_release', 'release'),
                                      ('root_config', 'config')]:
        _same(_descriptor(authority[authority_key]), _descriptor(MATERIAL_PINS[source_key]), 'authority Source:' + authority_key)
    owner = values['execute_owner']
    _same(owner['schema'], 'phase600-root-execute-owner/1', '600 owner schema')
    for key in ('execution', 'first_error', 'invocation', 'release'):
        _owned(owner, MATERIAL_PINS[key], '600 owned:' + key)
    _same(values['config_owner']['schema'], 'phase597-release-owner/1', 'actual config owner schema')
    _owned(values['config_owner'], MATERIAL_PINS['config'], '597 owned actual config')
    execution = values['execution']
    _same(values['first_error'], execution, 'original first failure retained')
    for key, expected in [('exit', 1), ('pid', 1188), ('reaped', True), ('outer_timeout', False), ('automatic_retry', False)]:
        _same(execution[key], expected, 'actual failed execution:' + key)
    _require(type(execution['first_error']) is str
             and 'RuntimeError: first original030 failed/partial; preserve, no retry' in execution['first_error'],
             'actual fixed failure traceback')
    invocation = values['invocation']
    _same(invocation['argv'], EXPECTED_ARGV, 'single actual execute argv/config')
    _same(invocation['cwd'], ROOT_PREFIX[:-1], 'fixed Source cwd')
    for key in ('execute_calls', 'max_parse', 'max_battle'):
        _same(invocation[key], 1, 'single actual attempt:' + key)
    release, config = values['release'], values['config']
    _same(release['schema'], 'phase600-root-single-fixed030-execute/1', 'actual600 release')
    _same(_descriptor(release['config']), _descriptor(MATERIAL_PINS['config']), '600 actual config association')
    _same(release['automatic_retry'], False, 'no retry release')
    for key in ('models', 'inputbuilds', 'Expected_comparison'):
        _same(release[key], 0, 'released non-model scope:' + key)
    _same(config['schema'], 'phase590-root-oracle-acceptance/1', 'executed config schema')
    _same(config['root_oracle_authorized'], True, 'executed explicit Root config')
    _same(config['source_freeze'], EXPECTED_HOST_FREEZE, 'executed original590 freeze')
    for key in ('models_allowed', 'input_builds_allowed', 'expected_comparison_allowed'):
        _same(config[key], 0, 'executed strictINT0:' + key)
    failed = authority['actual_failed_state']
    _same(_descriptor(failed['descriptor']), _descriptor(authority['evidence']['pending_state']), 'actual state evidence')
    _same(_path(failed['descriptor']['path']), FIXED_POOL + '/state.json', 'fixed failed state path')
    _same(state_image['identity'], {k: failed['descriptor'][k] for k in ('size', 'sha256')}, 'locked exact failed bytes identity')
    _same(state_image['raw'], raw_materials['saved_failed'], 'locked exact saved failed raw bytes')
    for key in ('mode', 'mtime_ns'):
        _same(state_image[key], failed[key], 'locked failed metadata:' + key)
    _same(_decode(state_image['raw']), failed['value'], 'locked failed value')
    _same(values['saved_failed'], failed['value'], 'saved failed copy value')
    _require(type(failed['value']) is dict and set(failed['value']) == {'status', 'run', 'reason', 'utc'}, 'actual failed closed four keys')
    _same(failed['value']['status'], 'failed', 'actual failed status')
    _same(failed['value']['run'], FIXED_RUN, 'actual failed run')
    _same(failed['value']['reason'], FIXED_REASON, 'actual failed reason')
    _require(type(failed['value']['utc']) is str and bool(failed['value']['utc']), 'actual failure UTC')
    _same(authority['capture_complete'], False, 'partial remains partial')
    _same(authority['owned_live_remaining'], 0, 'saved scoped monitor settlement')
    _same(authority['global_process_completeness_claimed'], False, 'no global process assertion')
    _same(controls['schema'], 'phase464-predecessor-control-preimages/1', 'saved controls schema')
    _same(controls['restored'], False, 'saved controls unmodified')
    _same(controls['previous_run'], previous, 'controls predecessor')
    _same([row['target'] for row in controls['images']], ['state.json', 'data/custom_player.json', 'data/custom_opponent.json'], 'three saved controls')
    _same(controls['images'][0]['present'], True, 'saved ready state present')
    _same(controls['images'][0]['backup'], '0', 'saved ready image0')
    _same(saved_ready['status'], 'ready', 'saved actual ready status')
    _same(saved_ready['run'], previous, 'saved ready predecessor')
    shared = {'controls_manifest', 'patch_inventory', 'install_journal', 'previous_proof', 'previous_bundle_manifest', 'pending_state'}
    _require(type(evidence) is dict, 'actual evidence mapping')
    if role == 'writer':
        _same(set(evidence), set(authority['evidence']), 'twelve actual writer evidence keys')
        keys = set(evidence)
    elif role == 'reader':
        _same(set(evidence), shared | {'restore_receipt', 'restore_owner'}, 'eight actual reader evidence keys')
        keys = shared
    else:
        raise ValueError('fixed recovery role only')
    for key in keys:
        _same(_descriptor(evidence[key]), _descriptor(authority['evidence'][key]), 'actual owned evidence:' + key)
    return dict(authority=MATERIAL_PINS['authority'], authority_owner=MATERIAL_PINS['authority_owner'],
                actual_failed_state=failed['descriptor'], root_execution=MATERIAL_PINS['execution'],
                previous_run=previous, state_writes=0, partial_capture_admitted=False)
