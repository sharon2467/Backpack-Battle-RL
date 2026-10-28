"""Unexecuted until Root releases the phase441 helper-only control batch."""
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import time

ROOT = Path('/workspace/python-original-engine/repo')
MODULE = ROOT / 'tests/phase441_fixed_A_input_bridge.py'
OWNER = ROOT / 'data/phase441-fixed-A-input-source/source-owner.json'
MODULE_SHA = 'e6c3336c5d91e51988d9629eaa779c3a229af5c1cc08d423609062831032f4f9'
OWNER_SHA = '7184b737c00ca53ac497463c4f038164cdee39875efa5eea13707939b68882ea'


def pin(path):
    raw = path.read_bytes()
    return {'path': str(path), 'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def write_once(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def controls(output_new):
    output = Path(output_new).absolute()
    if not output.is_relative_to(ROOT / 'data') or output == ROOT / 'data':
        raise ValueError('review output must be new repo/data directory')
    output.mkdir(exist_ok=False)
    started = time.monotonic()
    calls, negatives, io = {}, [], []
    result = {'schema': 'phase441-independent-helper-controls/1', 'status': 'RUNNING',
              'call_counts': calls, 'negatives': negatives, 'read_pinned_successes': io,
              'raw12_reads': 0, 'accepted_audit_reads': 0,
              'full_bundle_projections': 0, 'actual_builds': 0, 'model_runs': 0,
              'old_controls': 0, 'EXPECTED_reads': 0, 'new_native': 0}
    try:
        assert pin(MODULE)['sha256'] == MODULE_SHA
        assert pin(OWNER)['sha256'] == OWNER_SHA
        owner = json.loads(OWNER.read_text())
        for saved in owner['files']:
            current = pin(ROOT / saved['path'])
            assert (current['size'], current['sha256']) == (saved['size'], saved['sha256'])
        context = json.loads((ROOT / 'data/phase441-fixed-A-input-source/context.json').read_text())
        schema_pin = context['schema_module']
        current = pin(ROOT / schema_pin['path'])
        assert (current['size'], current['sha256']) == (schema_pin['size'], schema_pin['sha256'])
        result['preimport_source_checks'] = {'author_owned': len(owner['files']), 'schema': schema_pin}
        sys.dont_write_bytecode = True
        spec = importlib.util.spec_from_file_location('phase441_bridge_independent_target', MODULE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert Path(module.native_schema.__file__).absolute() == ROOT / schema_pin['path']
        assert not any(name.startswith(('native_replay_v7', 'native_replay_v8')) for name in sys.modules)
        for name in ('decode_lawful12', 'load_accepted_initial', 'project_runtime',
                     'project_fixture', 'project_order', 'project_primitives',
                     'project_decoded', 'project_from_bytes', 'build_from_files'):
            original = getattr(module, name)
            def counted(*args, _name=name, _original=original, **kwargs):
                calls[_name] = calls.get(_name, 0) + 1
                return _original(*args, **kwargs)
            setattr(module, name, counted)

        def reject(label, reason, action):
            try:
                action()
            except ValueError as error:
                if reason not in str(error):
                    raise AssertionError(f'{label}: unexpected rejection {error}') from error
                negatives.append({'case': label, 'reason': str(error)})
            else:
                raise AssertionError(label + ': unexpected acceptance')

        reject('duplicate JSON keys', 'DUPLICATE_JSON_KEY', lambda: module.strict_json(b'{"x":1,"x":2}'))
        reject('nonfinite JSON', 'NONFINITE_JSON', lambda: module.strict_json(b'{"x":NaN}'))
        reject('BOOL is not INT', 'TYPED_int', lambda: module.typed_scalar({'type': 'bool', 'value': False}, 'int'))
        reject('BOOL payload is not integer0', 'TYPED_BOOL', lambda: module.typed_scalar({'type': 'bool', 'value': 0}, 'bool'))
        raw12 = {}
        for name, descriptor in module.INPUT_PINS.items():
            raw12[name] = module.read_pinned(descriptor, io)
            result['raw12_reads'] += 1
        audit = module.read_pinned(module.AUDIT_PIN, io)
        result['accepted_audit_reads'] += 1
        reject('missing carrier', 'EXACT_FIXED12_NAMES', lambda: module.verify_raw_inputs({k: v for k, v in raw12.items() if k != 'fixture.json'}))
        reject('extra carrier', 'EXACT_FIXED12_NAMES', lambda: module.verify_raw_inputs(dict(raw12, forbidden=b'{}')))
        for name, raw in raw12.items():
            changed = dict(raw12)
            changed[name] = raw[:-1] + bytes([raw[-1] ^ 1])
            reject('raw byte drift:' + name, 'FIXED_INPUT_IDENTITY_' + name, lambda x=changed: module.verify_raw_inputs(x))
        reject('accepted audit byte drift', 'ACCEPTED439_AUDIT_IDENTITY', lambda: module.load_accepted_initial(audit[:-1] + bytes([audit[-1] ^ 1])))
        decoded, aliases, _ = module.decode_lawful12(raw12)
        index = module.load_accepted_initial(audit)
        baseline, baseline_origins, _ = module.project_runtime(decoded, aliases, index)
        assert set(baseline) == set(module.RUNTIME_KEYS) and len(baseline['timer_initial']) == 33
        assert len(baseline['initial_items']) == 39 and 'O:12' not in baseline['initial_items']
        excluded = deepcopy(decoded)
        for row in excluded['observer7-input.jsonl']:
            if row['edge'] == 'checkpoint':
                for node in row['payload']['nodes']:
                    if node['role'] in module.EXCLUDED_TIMERS:
                        node['timer']['paused'] = not node['timer']['paused']
                        node['timer']['time_left'] = {'type': 'float', 'binary64_be': '3ff0000000000000'}
        # These decoded carriers are not read by the pure runtime projection.
        excluded['king-ui-authority.jsonl'] = [{'display_only_control_marker': True}]
        excluded['king-input-facts.json'] = {'display_only_control_marker': True}
        alternative, alternative_origins, _ = module.project_runtime(excluded, aliases, index)
        assert module.same(baseline, alternative) and module.same(baseline_origins, alternative_origins)
        result['decoded_display_control'] = 'Equal partial runtime and origins; no raw identity relaxation or full bundle projection.'

        def act(data):
            return next(r for r in data['observer7-input.jsonl'] if r['site'] == 'Core/Game.gd::activateItems' and r['edge'] == 'checkpoint')

        def changed_runtime(label, reason, mutation):
            changed = deepcopy(decoded)
            mutation(changed)
            reject(label, reason, lambda: module.project_runtime(changed, aliases, index))

        def mutate_mode(data):
            next(n for n in act(data)['payload']['nodes'] if n['role'] == 'invu:P')['timer']['process_mode'] = True
        changed_runtime('Timer mode BOOL', 'TIMER_ACTUAL_AUDIT_JOIN_', mutate_mode)

        def mutate_position(data):
            node = next(n for n in act(data)['payload']['nodes'] if n['role'] == 'invu:P')
            node['node']['positions'][-1] = 5
            node['timer']['node'] = deepcopy(node['node'])
        changed_runtime('P invu stale child5', 'ACTUAL_P7_O5_TOPOLOGY', mutate_position)

        def mutate_flag(data):
            next(n for n in act(data)['payload']['nodes'] if n['role'] == 'invu:P')['node']['ordinary_idle'] = 0
        changed_runtime('ordinary flag INT0', 'EMITTED_NODE_BOOL_', mutate_flag)

        def mutate_clock(data):
            for row in data['observer7-input.jsonl']:
                if row['site'] == 'Core/Game.gd::activateItems' and row['edge'] in ('checkpoint', 'enter'):
                    row['stamp']['combat_time'] = {'type': 'float', 'binary64_be': '8000000000000000'}
        changed_runtime('activation negativezero clock', 'ACTIVATION_PHASE_COMBAT_CLOCK', mutate_clock)
        bad_index = deepcopy(index)
        del bad_index[('Timer.private_left', 'pre_activate', 'invu:P')]
        reject('missing private source', 'EXACT_EMITTED_BUSINESS_NODE_ROLES', lambda: module.project_runtime(decoded, aliases, bad_index))
        wrong_private = deepcopy(index)
        wrong_private[('Timer.private_left', 'pre_activate', 'invu:P')][1]['actual_value'] = {'type': 'float', 'binary64_be': module.ZERO_BITS}
        reject('publiczero private inversion', 'SUPPORTED_PRIVATE_INITIAL_MINUS_ONE', lambda: module.project_runtime(decoded, aliases, wrong_private))
        entry = next(r for r in decoded['observer7-input.jsonl'] if r['site'] == 'Core/Game.gd::prepareItems' and r['edge'] == 'enter')
        bad_aliases = deepcopy(aliases)
        bad_aliases['role_to_native']['P:0'] = '1'
        reject('order native alias', 'GAME_ITEM_ALIAS', lambda: module.project_order(entry, bad_aliases))
        bad_fixture = deepcopy(decoded)
        bad_fixture['fixture.json']['items'].pop()
        reject('fixture slot loss', 'FIXED_FIXTURE_GEOMETRY_ORDER', lambda: module.project_fixture(bad_fixture))
        primitive = {'observer7-primitives.jsonl': [{'sequence': 2, 'site': 'Utility/Util.gd::roll', 'payload': {
            'kind': 'randf_range', 'label': 'synthetic_control_only',
            'args': [{'type': 'int', 'decimal': '1'}, {'type': 'float', 'binary64_be': '3ff0000000000000'}],
            'value': {'type': 'float', 'binary64_be': '3fe0000000000000'}}}]}
        reject('illegal primitive INT coercion', 'UNSUPPORTED_PRIMITIVE_ARGUMENT_COERCION', lambda: module.project_primitives(primitive, 1))

        with tempfile.TemporaryDirectory(prefix='phase441-independent-') as folder:
            directory = Path(folder)
            source = directory / 'source.json'
            source.write_bytes(b'{}')
            descriptor = pin(source)
            source.write_bytes(b'[]')
            reject('temporary same-size hash drift', 'PIN_HASH', lambda: module.read_pinned(descriptor, io))
            source.write_bytes(b'{}')
            link = directory / 'symlink.json'
            link.symlink_to(source)
            reject('symlink', 'PATH_SYMLINK', lambda: module.read_pinned(dict(descriptor, path=str(link)), io))
            link.unlink()
            os.link(source, link)
            reject('hardlink', 'NONORDINARY_FILE', lambda: module.read_pinned(descriptor, io))
            link.unlink()
            fifo = directory / 'fifo'
            os.mkfifo(fifo)
            reject('nonordinary FIFO', 'NONORDINARY_FILE', lambda: module.read_pinned(dict(descriptor, path=str(fifo)), io))
            try:
                module.save_new(source, {})
            except FileExistsError:
                negatives.append({'case': 'existing write-once output', 'reason': 'FileExistsError'})
            else:
                raise AssertionError('existing output unexpectedly overwritten')
        assert calls.get('decode_lawful12') == 1
        assert not any(calls.get(k, 0) for k in ('project_decoded', 'project_from_bytes', 'build_from_files'))
        result.update(status='PASS_HELPERS_ONLY_NO_FULL_BUNDLE', elapsed_seconds=time.monotonic() - started,
                      partial_runtime_positive_calls=2, source_module=pin(MODULE), author_owner=pin(OWNER))
        write_once(output / 'result.json', result)
        write_once(output / 'owned-files.json', {'schema': 'phase441-independent-controls-owned/1',
                   'files': [pin(output / 'result.json'), pin(Path(__file__).absolute()), pin(MODULE), pin(OWNER)]})
        return result
    except Exception as error:
        result.update(status='FIRST_ERROR_STOP_NO_RETRY', error_type=type(error).__name__,
                      error=str(error), elapsed_seconds=time.monotonic() - started)
        write_once(output / 'first-error.json', result)
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--released-controls-output-new', required=True)
    arguments = parser.parse_args()
    outcome = controls(arguments.released_controls_output_new)
    print(json.dumps({'status': outcome['status'], 'calls': outcome['call_counts'],
                      'raw12_reads': outcome['raw12_reads'], 'elapsed_seconds': outcome['elapsed_seconds']}))
