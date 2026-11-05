"""One Source generation only. Does not import or execute any generated module."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import traceback

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/phase602-failed030-recovery-source'
WRITER = ROOT / 'tests/phase602_failed030_restore_predecessor.py'
READER = ROOT / 'tests/phase602_failed030_independent_readback.py'
BINDING = ROOT / 'tests/phase602_failed030_binding.py'


def pin(path):
    path = Path(path)
    raw = path.read_bytes()
    return dict(path=str(path.relative_to(ROOT)), size=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def save(path, value):
    with Path(path).open('x') as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def source_functions(text):
    return {n.name: ast.get_source_segment(text, n) for n in ast.parse(text).body if isinstance(n, ast.FunctionDef)}


class Delta:
    def __init__(self, text):
        self.text, self.changes = text, []

    def replace(self, before, after, label):
        assert before != after and self.text.count(before) == 1, label
        offset = self.text.index(before)
        self.text = self.text[:offset] + after + self.text[offset + len(before):]
        self.changes.append(dict(offset=offset, before=before, after=after, label=label))

    def inverse(self):
        text = self.text
        for change in reversed(self.changes):
            at = change['offset']
            assert text[at:at + len(change['after'])] == change['after']
            text = text[:at] + change['before'] + text[at + len(change['after']):]
        return text


COMMON = r'''"""Pure fixed failed030 association. No filesystem or process operation."""
import hashlib
import json

ROOT_PREFIX = '/workspace/python-original-engine/repo/'
MATERIAL_PINS = __PINS__
EXPECTED_ARGV = __ARGV__
EXPECTED_HOST_FREEZE = __FREEZE__
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
'''

WRAPPER = '''\n\ndef failure_association(state_image, controls, saved_ready, evidence, previous, role):
    raw_source = descriptor(FAILURE_BINDING)
    raw_materials = {key: descriptor(row) for key, row in FAILURE_MATERIALS.items()}
    module = types.ModuleType('_phase602_fixed_failure_binding')
    module.__file__ = str(path_of(FAILURE_BINDING['path']))
    exec(compile(raw_source, module.__file__, 'exec'), module.__dict__)
    provenance = module.validate_failure_association(raw_materials, state_image, controls, saved_ready,
                                                    evidence, str(previous), role)
    equal(descriptor(FAILURE_BINDING), raw_source, 'fixed binding Source unchanged')
    for key, row in FAILURE_MATERIALS.items():
        equal(descriptor(row), raw_materials[key], 'fixed failure authority unchanged:' + key)
    return provenance
'''


def main():
    assert not OUT.exists()
    OUT.mkdir()
    outputs, deltas = [], []
    try:
        for p in (WRITER, READER, BINDING):
            assert not p.exists(), 'immutable new module namespace'
        paths = dict(authority='data/phase601-root-failed030-authority/authority.json',
                     authority_owner='data/phase601-root-failed030-authority/owned-files.json',
                     saved_failed='data/phase601-root-failed030-authority/actual-failed-state.json',
                     execute_owner='data/phase600-root-fixed030-execute-first-001/owned-files.json',
                     invocation='data/phase600-root-fixed030-execute-first-001/invocation.json',
                     execution='data/phase600-root-fixed030-execute-first-001/execution.json',
                     first_error='data/phase600-root-fixed030-execute-first-001/first-error.json',
                     release='data/phase600-root-fixed030-execute-first-001/release.json',
                     config='data/phase597-resume030-conditional-release/oracle-acceptance.json',
                     config_owner='data/phase597-resume030-conditional-release/owned-files.json')
        materials = {key: pin(ROOT / path) for key, path in paths.items()}
        assert materials['authority']['sha256'] == 'acde0c7ae926c0f1b097e7cee662fbd93416a68352d51c6c556d7c021fd04495'
        assert materials['authority_owner']['sha256'] == '033b4c6563c5d31d6a4688a1a82cafe3d8f355141aa62258177112ce69caf77a'
        oldw = (ROOT / 'tests/phase590_restore_predecessor.py').read_text()
        oldr = (ROOT / 'tests/phase590_independent_predecessor_readback.py').read_text()
        freeze = ast.literal_eval(next(n.value for n in ast.parse(oldw).body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'FREEZE' for t in n.targets)))
        argv = json.loads((ROOT / paths['invocation']).read_bytes())['argv']
        common = COMMON.replace('__PINS__', repr(materials)).replace('__ARGV__', repr(argv)).replace('__FREEZE__', repr(freeze))
        BINDING.write_text(common);outputs.append(BINDING)
        constants = '\nFAILURE_BINDING = ' + repr(pin(BINDING)) + '\nFAILURE_MATERIALS = ' + repr(materials) + '\n'
        w = Delta(oldw)
        w.replace('\n\ndef require(value, message):', constants + WRAPPER + '\n\ndef require(value, message):', 'fixed authority/predicate declarations')
        before = """    require(pending.get('status') == 'failed' and pending.get('reason') == 'PENDING_INDEPENDENT_PREDECESSOR_RESTORE'
            and pending.get('run') == str(RUN) and pending.get('previous_run') == str(PREVIOUS), 'fixed pending state')
    equal(pending['control_preimages'], {'path': str(CONTROLS), 'manifest':
          {key: request['evidence']['controls_manifest'][key] for key in ('size', 'sha256')}, 'restored': False},
          'pending controls association')
"""
        w.replace(before, '', 'remove inapplicable PENDING and nonexistent fields only')
        anchor = "    require(saved_state['status'] == 'ready' and saved_state['run'] == str(PREVIOUS), 'actual predecessor saved state')\n"
        w.replace(anchor, anchor + "    result['failure_authority'] = failure_association(stable(POOL / 'state.json'), manifest, saved_state,\n                                                       request['evidence'], PREVIOUS, 'writer')\n", 'actual saved-ready failure association under existing lock')
        for before, after in [('phase590-fixed-predecessor-restore-request/1','phase602-fixed-failed030-restore-request/1'),
                              ("'phase590-restore-'", "'phase602-restore-'"),
                              ('phase590-fixed-predecessor-restore-result/1','phase602-fixed-failed030-restore-result/1'),
                              ('phase590-restore-output-owner/1','phase602-restore-output-owner/1')]:
            w.replace(before, after, 'declarative namespace:' + before)
        WRITER.write_text(w.text);outputs.append(WRITER);deltas.append((WRITER, oldw, w))
        r = Delta(oldr)
        r.replace('\n\ndef require(condition, message):', constants + WRAPPER + '\n\ndef require(condition, message):', 'same fixed authority/predicate declarations')
        before = """        require(pending.get('status') == 'failed' and pending.get('reason') == 'PENDING_INDEPENDENT_PREDECESSOR_RESTORE',
                'pool must remain failed/PENDING until separate Root commit')
        require(relocate(pending['run'], mapping) == run and relocate(pending['previous_run'], mapping) == previous,
                'pending-state run association')
        require(relocate(pending['control_preimages']['path'], mapping) == controls and
                pending['control_preimages']['manifest'] == {k: evidence['controls_manifest'][k] for k in ('size', 'sha256')}
                and pending['control_preimages']['restored'] is False, 'pending-state backup association')
"""
        r.replace(before, '', 'remove inapplicable reader PENDING association only')
        anchor = """        require(old_state.get('status') == 'ready' and relocate(old_state['run'], mapping) == previous,
                'actual pre-busy predecessor ready image')
"""
        r.replace(anchor, anchor + "        result['failure_authority'] = failure_association(stable(pool / 'state.json'), control_manifest, old_state,\n                                                           evidence, previous, 'reader')\n", 'reader same genuine failure association under original lock')
        anchor = "        explicit.update(path_of(row['path']) for row in request['evidence'].values())\n"
        r.replace(anchor, anchor + "        explicit.add(path_of(FAILURE_BINDING['path']))\n        explicit.update(path_of(row['path']) for row in FAILURE_MATERIALS.values())\n", 'explicit fixed metadata/source read closure only')
        for before, after in [('phase590-fixed-predecessor-readback-request/1','phase602-fixed-failed030-readback-request/1'),
                              ("'phase590-readback-'", "'phase602-readback-'"),
                              ('phase590-independent-readback-result/1','phase602-independent-failed030-readback-result/1'),
                              ('phase590-readback-output-owner/1','phase602-readback-output-owner/1')]:
            r.replace(before, after, 'declarative namespace:' + before)
        READER.write_text(r.text);outputs.append(READER);deltas.append((READER, oldr, r))
        compiled = []
        for p in (BINDING, WRITER, READER):
            compile(p.read_bytes(), str(p), 'exec');compiled.append(pin(p))
        census = []
        for p, old, delta in deltas:
            assert delta.inverse() == old, 'full byte inverse'
            a, b = source_functions(old), source_functions(delta.text)
            changed = [name for name in a if a[name] != b[name]]
            expected = {'validate_request','prepare','main'} if p == WRITER else {'readback','main'}
            assert set(changed) == expected, ('exact changed function set',p,changed)
            unchanged = [name for name in a if a[name] == b[name]]
            census.append(dict(file=str(p.relative_to(ROOT)), changed_functions=changed,
                               exact_functions=unchanged, added_functions=sorted(set(b)-set(a)),
                               full_inverse=True, preimage_size=len(old.encode()),
                               preimage_sha256=hashlib.sha256(old.encode()).hexdigest()))
            save(OUT / (p.stem + '-inverse.json'), dict(schema='phase602-exact-inverse/1', target=pin(p), changes=delta.changes))
            (OUT / (p.stem + '.patch')).write_text(''.join(difflib.unified_diff(old.splitlines(keepends=True), delta.text.splitlines(keepends=True), fromfile='old590', tofile=str(p.relative_to(ROOT)))))
        save(OUT/'conservation.json',dict(schema='phase602-conservation/1',files=census,shared_wrapper_exact=source_functions(w.text)['failure_association']==source_functions(r.text)['failure_association'],old590_unchanged=True))
        save(OUT/'compile-only.json',dict(schema='phase602-compile-only/1',objects=compiled,imports=0,helpers=0,operational=0,Native=0,Expected=0,model=0,pool_reads=0,pool_writes=0,generation_attempts=1))
        save(OUT/'api.json',dict(schema='phase602-recovery-source-api/1',status='SOURCE_ONLY_NOT_RESTORE_AUTHORIZATION',
             pure_binding='validate_failure_association(raw_materials,state_image,controls,saved_ready,evidence,previous,role)',
             pair_adapter='failure_association(state_image,controls,saved_ready,evidence,previous,role)',
             writer=dict(module=pin(WRITER),request_schema='phase602-fixed-failed030-restore-request/1',request_keys=7,evidence_count=12,output_prefix='phase602-restore-'),
             reader=dict(module=pin(READER),request_schema='phase602-fixed-failed030-readback-request/1',request_keys=9,evidence_count=8,output_prefix='phase602-readback-'),
             host_source_freeze=freeze,state_writes=0,actual_requests=None,restore_calls=0,readback_calls=0))
        sources=[pin(p) for p in (WRITER,READER,BINDING)]
        dependencies=list(materials.values())+[pin(ROOT/'tests/phase590_restore_predecessor.py'),pin(ROOT/'tests/phase590_independent_predecessor_readback.py'),pin(ROOT/'tests/phase590_oracle_storage.py'),pin(ROOT/'tests/native_run_compaction.py'),pin(ROOT/freeze['path']),pin(ROOT/'docs/phase602_failed030_recovery_source_spec.md'),pin(Path(__file__)),pin(ROOT/'data/phase602-root-failed030-recovery-source-release/release.json'),pin(ROOT/'data/phase601-independent-failure-and-recovery-review/review.json')]
        save(OUT/'source-freeze.json',dict(schema='phase602-fixed-failed030-source-freeze/1',status='SOURCE_ONLY_NOT_OPERATIONAL',modules=sources,dependencies=dependencies,original_host_freeze=freeze,storage_kernel_unchanged=True,no_self_hash=True))
        owner_files=[pin(p) for p in sorted(OUT.iterdir()) if p.is_file()]+sources+dependencies
        save(OUT/'owned-files.json',dict(schema='phase602-source-owner/1',files=owner_files,no_more_writes=True))
        print(json.dumps(dict(status='SOURCE_GENERATED_COMPILED_NOT_IMPORTED',owner=pin(OUT/'owned-files.json'),freeze=pin(OUT/'source-freeze.json'))))
    except BaseException as exc:
        save(OUT/'first-error.json',dict(schema='phase602-source-first-error/1',type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc(),generation_attempts=1,imports=0,helpers=0,pool_reads=0,pool_writes=0,Native=0,Expected=0))
        save(OUT/'partial-owner.json',dict(schema='phase602-source-partial-owner/1',files=[pin(p) for p in sorted(OUT.iterdir()) if p.is_file()]+[pin(p) for p in outputs],no_more_writes=True))
        raise


if __name__ == '__main__':
    main()
