"""Fixed readonly predecessor verification. Never restore or write pool READY."""
from pathlib import Path
import argparse
import fcntl
import hashlib
import json
import os
import re
import signal
import stat
import sys
import time
import traceback
import types

ROOT = Path(__file__).resolve().parents[1]
CASE = 'NATIVE-028-KING-BASIC-A'
RUN = 'original028-king-basic-A-single-001'
HELPER = {'path': 'tests/native_run_compaction.py', 'size': 27304,
          'sha256': '829475e4ba5ee4a3ce3e3ce7a1d600b53cfa6ab243020a8528b6758675e6c260'}
FREEZE = {'path': 'data/phase464-joint-oracle-host-source-v2/combined-source-freeze.json', 'size': 58276,
          'sha256': 'b66879fe67a0afcf8cb84ce5a52f1ad7386ce7e58be5d1dcada0fcdb2e0b0965'}
EVIDENCE = {'restore_receipt', 'restore_owner', 'controls_manifest', 'patch_inventory',
            'install_journal', 'previous_proof', 'previous_bundle_manifest', 'pending_state'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def signature(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def stable(path):
    path = Path(path).absolute()
    require(not any(p.is_symlink() for p in (path, *path.parents)), 'linked control path: ' + str(path))
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1, 'ordinary single-link control required')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as stream:
        opened = os.fstat(stream.fileno())
        raw = stream.read()
        after = os.fstat(stream.fileno())
    require(signature(before) == signature(opened) == signature(after) == signature(path.lstat()), 'control changed during read')
    return {'raw': raw, 'identity': {'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()},
            'mode': stat.S_IMODE(before.st_mode), 'mtime_ns': before.st_mtime_ns}


def path_of(value):
    require(type(value) is str and bool(value), 'path string required')
    p = Path(value)
    p = p if p.is_absolute() else ROOT / p
    require(p.absolute() == p and '..' not in p.parts, 'canonical explicit path required')
    return p


def descriptor(row):
    require(type(row) is dict and set(row) == {'path', 'size', 'sha256'}, 'closed descriptor')
    require(type(row['size']) is int and row['size'] >= 0 and type(row['sha256']) is str
            and re.fullmatch('[0-9a-f]{64}', row['sha256']), 'descriptor identity types')
    image = stable(path_of(row['path']))
    require(image['identity'] == {k: row[k] for k in ('size', 'sha256')}, 'descriptor drift: ' + row['path'])
    return image['raw']


def decoded(raw):
    def invalid(value):
        raise ValueError('nonfinite JSON literal: ' + value)
    return json.loads(raw, parse_constant=invalid)


def relocate(value, mapping):
    p = path_of(value)
    matches = [(path_of(a), path_of(b)) for a, b in mapping.items()
               if p == path_of(a) or p.is_relative_to(path_of(a))]
    require(len(matches) <= 1, 'ambiguous recorded-path relocation')
    return matches[0][1] / p.relative_to(matches[0][0]) if matches else p


def difference(actual, expected, field='$'):
    if type(actual) is not type(expected):
        return {'field': field, 'actual_type': type(actual).__name__, 'expected_type': type(expected).__name__}
    if isinstance(actual, dict):
        if actual.keys() != expected.keys():
            return {'field': field, 'actual_keys': sorted(actual), 'expected_keys': sorted(expected)}
        for key in actual:
            found = difference(actual[key], expected[key], field + '/' + str(key))
            if found:
                return found
    elif isinstance(actual, list):
        if len(actual) != len(expected):
            return {'field': field, 'actual_length': len(actual), 'expected_length': len(expected)}
        for index, (a, b) in enumerate(zip(actual, expected)):
            found = difference(a, b, field + '/' + str(index))
            if found:
                return found
    elif actual != expected:
        if isinstance(actual, bytes):
            return {'field': field, 'actual_bytes': len(actual), 'expected_bytes': len(expected),
                    'actual_sha256': hashlib.sha256(actual).hexdigest(),
                    'expected_sha256': hashlib.sha256(expected).hexdigest()}
        return {'field': field, 'actual': actual, 'expected': expected}
    return None


def equal(actual, expected, label):
    mismatch = difference(actual, expected)
    require(mismatch is None, label + ': ' + json.dumps(mismatch, ensure_ascii=False))


def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def readback(request, c, out, result):
    require(type(request) is dict and set(request) == {'schema', 'case_id', 'run', 'pool', 'baseline',
            'previous_run', 'relocations', 'host_source_freeze', 'evidence'}, 'closed readback request')
    require(request['schema'] == 'phase468-fixed-predecessor-readback-request/1' and request['case_id'] == CASE,
            'fixed readback case')
    require(request['host_source_freeze'] == FREEZE, 'exact accepted464v2 Source freeze')
    freeze = decoded(descriptor(FREEZE))
    require(all(type(request[k]) is str and Path(request[k]).is_absolute()
                for k in ('run', 'pool', 'baseline', 'previous_run')), 'absolute runtime paths required')
    roots = {k: path_of(request[k]) for k in ('run', 'pool', 'baseline', 'previous_run')}
    run, pool, baseline, previous = (roots[k] for k in ('run', 'pool', 'baseline', 'previous_run'))
    require(run.name == RUN and run != previous, 'fixed current run and distinct predecessor')
    for p in roots.values():
        require(p.is_dir() and not any(x.is_symlink() for x in (p, *p.parents)), 'unlinked existing scope')
        require(not out.is_relative_to(p) and not p.is_relative_to(out), 'report/evidence scopes disjoint')
    require(len(set(roots.values())) == 4, 'distinct runtime roots')
    require(all(not a.is_relative_to(b) for a in roots.values() for b in roots.values() if a != b),
            'disjoint runtime roots')
    require(type(request['relocations']) is dict and all(type(k) is str and type(v) is str
            and Path(k).is_absolute() and Path(v).is_absolute() for k, v in request['relocations'].items()),
            'explicit absolute relocations only')
    mapping = request['relocations']
    evidence = request['evidence']
    require(type(evidence) is dict and set(evidence) == EVIDENCE, 'eight actual evidence descriptors')
    controls = run / 'output/predecessor-control-preimages'
    old_patch = run / 'output/previous-source-preimages'
    journal_dir = run / 'output/source-preimages'
    bundle = previous / 'output/compaction'
    expected_paths = {'controls_manifest': controls / 'manifest.json', 'patch_inventory': old_patch / 'inventory.json',
                      'install_journal': journal_dir / 'preimages.json', 'previous_proof': bundle / 'pool-roundtrip.json',
                      'previous_bundle_manifest': bundle / 'bundle-manifest.json', 'pending_state': pool / 'state.json'}
    for key, path in expected_paths.items():
        require(path_of(evidence[key]['path']) == path, 'fixed evidence path: ' + key)
    raw_evidence = {key: descriptor(row) for key, row in evidence.items()}
    owner = decoded(raw_evidence['restore_owner'])
    receipt = evidence['restore_receipt']
    covered = [row for row in owner['files'] if path_of(row['path']) == path_of(receipt['path'])]
    require(len(covered) == 1 and {k: covered[0][k] for k in ('size', 'sha256')} ==
            {k: receipt[k] for k in ('size', 'sha256')}, 'actual owned restoration receipt required')
    result['root_restore_receipt'] = receipt
    result['receipt_role'] = 'Pinned restoration provenance; success content is not used as physical proof.'
    result['physical_roots'] = {k: str(v) for k, v in roots.items()}
    require(set(p.name for p in pool.iterdir()) == {'.lock', 'state.json', 'project', 'data'}, 'exact pool membership')
    lock = pool / '.lock'
    stable(lock)
    fd = os.open(lock, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        result['readonly_lock_acquisitions'] += 1
        require(signature(os.fstat(fd)) == signature(lock.lstat()), 'same ordinary lock inode')
        # Recheck after acquiring the one lock; never trust a pre-lock state sample.
        for key, row in evidence.items():
            equal(descriptor(row), raw_evidence[key], 'locked evidence unchanged:' + key)
        pending = decoded(raw_evidence['pending_state'])
        require(pending.get('status') == 'failed' and pending.get('reason') == 'PENDING_INDEPENDENT_PREDECESSOR_RESTORE',
                'pool must remain failed/PENDING until separate Root commit')
        require(relocate(pending['run'], mapping) == run and relocate(pending['previous_run'], mapping) == previous,
                'pending-state run association')
        require(relocate(pending['control_preimages']['path'], mapping) == controls and
                pending['control_preimages']['manifest'] == {k: evidence['controls_manifest'][k] for k in ('size', 'sha256')}
                and pending['control_preimages']['restored'] is False, 'pending-state backup association')
        def no_process(label):
            value = c.process_check(pool)
            require(value['active_matches'] == [], 'no readable active pool references')
            value['operational_scope'] = 'original-readable-reference-check-with-exclusive-pool-lock/1'
            value['global_process_completeness_claimed'] = False
            result[label] = value
        no_process('process_before')
        control_manifest = decoded(raw_evidence['controls_manifest'])
        require(control_manifest['schema'] == 'phase464-predecessor-control-preimages/1'
                and control_manifest['restored'] is False
                and relocate(control_manifest['previous_run'], mapping) == previous, 'saved predecessor control identity')
        equal([x['target'] for x in control_manifest['images']],
              ['state.json', 'data/custom_player.json', 'data/custom_opponent.json'], 'three saved controls')
        saved_images = {}
        for index, row in enumerate(control_manifest['images']):
            if row['present'] is False:
                equal(row, {'target': row['target'], 'present': False, 'backup': None}, 'closed absent image')
                require(index != 0, 'saved predecessor state cannot be absent')
                saved_images[row['target']] = None
                continue
            require(row['present'] is True and set(row) == {'target', 'present', 'backup', 'identity', 'mode', 'mtime_ns'}
                    and row['backup'] == str(index), 'closed present image')
            image = stable(controls / row['backup'])
            equal({k: image[k] for k in ('identity', 'mode', 'mtime_ns')},
                  {k: row[k] for k in ('identity', 'mode', 'mtime_ns')}, 'saved controls bytes/metadata')
            saved_images[row['target']] = image
        old_state = decoded(saved_images['state.json']['raw'])
        require(old_state.get('status') == 'ready' and relocate(old_state['run'], mapping) == previous,
                'actual pre-busy predecessor ready image')

        def inventory_check(label, path, expected):
            actual = c.inventory(path)
            save(out / (label + '.json'), actual)
            equal(actual, expected, label)
            result.setdefault('inventory_checks', {})[label] = {
                'entries': len(actual['entries']), 'regular_files': sum(x['kind'] == 'file' for x in actual['entries']),
                'manifest_file_bytes_not_total_io': sum(x.get('size', 0) for x in actual['entries'])}
        inventory_check('previous-bundle-actual', bundle, old_state['bundle_inventory'])
        base, project, _ = c.load_bundle(bundle)
        proof = decoded(raw_evidence['previous_proof'])
        require(proof.get('status') == 'PASS', 'previous proof PASS')
        if proof.get('verification_mode') is None:
            require(proof.get('full_path_sha256_mode_mtime_equality') is True, 'old materialized proof form')
        else:
            require(proof['verification_mode'] == 'logical-overlay-and-live-tree-equality/1'
                    and proof.get('physical_reconstruction') is False
                    and proof.get('live_tree_byte_mode_mtime_equality') is True, 'old logical proof form')
        require(relocate(proof['run'], mapping) == previous and relocate(proof['pool'], mapping) == pool,
                'previous proof runtime association')
        require(proof['bundle_sha256'] == evidence['previous_bundle_manifest']['sha256']
                and proof['provenance_sha256'] == c.digest(previous / 'output/pool-provenance.json'),
                'previous bundle/provenance proof hashes')
        staged = c.read(bundle / 'staged-inputs.json')
        inventory_check('baseline-actual', baseline, base)
        inventory_check('project-actual', pool / 'project', project)
        inventory_check('staged-actual', pool / 'data', staged)
        inventory_check('previous-driver-actual', previous / 'output/driver', c.read(bundle / 'driver-files.json'))
        retained = c.retained(previous)
        save(out / 'previous-retained-actual.json', retained)
        equal(retained, c.read(bundle / 'retained-evidence.json'), 'previous retained evidence')
        result['retained_scope'] = 'Physical hash-only of old retained capture bytes; Expected semantic decoding0. Existing c.retained output-root-mtime/generated exclusions and relaxed user-special representation preserved.'
        bidx, pidx, sidx = c.index(base), c.index(project), c.index(staged)
        for name in ('data/custom_player.json', 'data/custom_opponent.json'):
            image = saved_images[name]
            expected = sidx.get(name.split('/')[1])
            if image is None:
                require(expected is None, 'saved absence agrees with predecessor staged tree')
            else:
                require(expected is not None and expected['kind'] == 'file', 'saved fixture exists in prior staged tree')
                equal(image['identity'], {k: expected[k] for k in ('size', 'sha256')}, 'saved fixture identity authority')
                equal([image['mode'], image['mtime_ns']], [expected['mode'], expected['mtime_ns']], 'saved fixture metadata authority')
        prior = decoded(raw_evidence['patch_inventory'])
        equal(prior['project'], project, 'pre-reset inventory equals predecessor project')
        report = c.read(previous / 'output/host_manifest.json')['audited_runtime_observation_patch']
        equal(prior['patch'], report, 'saved previous patch report')
        old_targets = {}
        for index, row in enumerate(report['patches']):
            name = c.safe_path(row['path'])
            require(name not in old_targets, 'unique old patch target')
            old_targets[name] = row
            original = pidx[name]
            equal({'size': row['after_size'], 'sha256': row['after_sha256']},
                  {k: original[k] for k in ('size', 'sha256')}, 'previous patch after identity')
            image = stable(old_patch / str(index))
            equal(image['identity'], {k: original[k] for k in ('size', 'sha256')}, 'saved old patch bytes')
            equal([image['mode'], image['mtime_ns']], [original['mode'], original['mtime_ns']], 'saved old patch metadata')
            if row['before_sha256'] is None:
                require(name not in bidx, 'previous added patch has no baseline source')
            else:
                equal({'size': row['before_size'], 'sha256': row['before_sha256']},
                      {k: bidx[name][k] for k in ('size', 'sha256')}, 'previous patch baseline identity')
        marker = '.native-random-observer-disposable'
        image = stable(old_patch / 'marker')
        equal(image['identity'], {k: pidx[marker][k] for k in ('size', 'sha256')}, 'old marker identity')
        equal([image['mode'], image['mtime_ns']], [pidx[marker]['mode'], pidx[marker]['mtime_ns']], 'old marker metadata')
        expected_after = {name: row['after'] for name, row in freeze['paths'].items()}
        expected_after.update({name: {k: row[k] for k in ('size', 'sha256')} for name, row in freeze['artifacts'].items()})
        require(len(expected_after) == 78 and sum(x['size'] for x in expected_after.values()) == 812880, 'fixed78 install corpus')
        journal = decoded(raw_evidence['install_journal'])
        expected_order = list(freeze['paths']) + ['native_combat_capture.gd', 'native_capture_config.json', marker]
        equal([x['path'] for x in journal], expected_order, 'new78 source journal order/targets')
        for index, row in enumerate(journal):
            require(set(row) == {'path', 'backup', 'before', 'after'}, 'closed new preimage row')
            name = row['path']
            equal(row['after'], expected_after[name], 'new journal source identity')
            intermediate = None if name == marker else bidx.get(name) if name in old_targets else pidx.get(name)
            if intermediate is None:
                require(row['before'] is None and row['backup'] is None, 'absent intermediate target')
            else:
                require(intermediate['kind'] == 'file', 'intermediate target regular')
                expected = {'identity': {k: intermediate[k] for k in ('size', 'sha256')},
                            'mode': intermediate['mode'], 'mtime_ns': intermediate['mtime_ns']}
                equal(row['before'], expected, 'journal intermediate before bytes/metadata')
                require(row['backup'] == str(index), 'journal backup identity')
                equal(stable(journal_dir / row['backup'])['identity'], expected['identity'], 'new journal saved bytes')
        result['preimages'] = {'controls': 3, 'old_patch_backups': len(old_targets), 'old_marker': 1, 'new_journal': 78}
        no_process('process_after')
        for key, row in evidence.items():
            equal(descriptor(row), raw_evidence[key], 'critical evidence unchanged after:' + key)
        result['pending_state_unchanged'] = evidence['pending_state']
        result['pool_ready_written'] = False
        result['status'] = 'PASS_PREDECESSOR_PHYSICAL_READBACK_ROOT_READY_PENDING'
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--config-sha256', required=True)
    parser.add_argument('--output-new', required=True)
    args = parser.parse_args()
    out = path_of(args.output_new)
    require(out.parent == ROOT / 'data' and out.name.startswith('phase468-'), 'new local phase468 report directory only')
    out.mkdir(exist_ok=False)
    started = time.monotonic()
    result = {'schema': 'phase468-independent-readback-result/1', 'status': 'RUNNING', 'native': 0, 'models': 0,
              'Expected_semantic_decoding': 0, 'restore_calls': 0, 'READY_writes': 0, 'helper_entries': {},
              'compaction_module_loads': 0, 'readonly_lock_acquisitions': 0}
    code = 1
    opened = set()
    script_image = None
    try:
        def deadline(signum, frame):
            raise TimeoutError('fixed independent readback deadline300s')
        signal.signal(signal.SIGALRM, deadline)
        signal.alarm(300)
        config_path = path_of(args.config)
        config_image = stable(config_path)
        require(config_image['identity']['sha256'] == args.config_sha256, 'Root request SHA mismatch')
        request = decoded(config_image['raw'])
        helper_raw = descriptor(HELPER)
        script_image = stable(Path(__file__))
        result['config'] = dict(path=str(config_path), **config_image['identity'])
        result['source'] = dict(path=str(Path(__file__)), **script_image['identity'])
        result['compaction_source'] = HELPER
        # Read roots are explicit. All writes remain outside physical/evidence trees.
        read_roots = [path_of(request[k]) for k in ('run', 'pool', 'baseline', 'previous_run')]
        explicit = {config_path, Path(__file__).absolute(), path_of(HELPER['path']), path_of(FREEZE['path'])}
        explicit.update(path_of(row['path']) for row in request['evidence'].values())
        def audit(event, values):
            if event in ('subprocess.Popen', 'os.system', 'os.exec', 'os.posix_spawn', 'socket.connect', 'socket.bind'):
                raise ValueError('readback cannot launch process/network')
            if event in ('os.remove', 'os.rmdir', 'os.mkdir', 'os.chmod', 'os.utime'):
                require(Path(os.fsdecode(values[0])).absolute().is_relative_to(out), 'mutation outside report directory')
            if event in ('os.rename', 'os.link', 'os.symlink'):
                require(all(Path(os.fsdecode(p)).absolute().is_relative_to(out) for p in values[:2]),
                        'link/rename outside report directory')
            if event == 'open':
                path, mode, flags = values
                if isinstance(path, int):
                    return
                p = Path(os.fsdecode(path)).absolute()
                write = flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)
                if write:
                    require(p.is_relative_to(out), 'write outside report directory')
                else:
                    require(p in explicit or p.is_relative_to(out) or p.is_relative_to(Path(sys.base_prefix))
                            or p.is_relative_to(Path('/proc')) or any(p.is_relative_to(root) for root in read_roots),
                            'read outside explicit Source/physical scope: ' + str(p))
                    opened.add(str(p))
        sys.addaudithook(audit)
        sys.dont_write_bytecode = True
        module = types.ModuleType('_phase468_frozen_compaction')
        module.__file__ = str(path_of(HELPER['path']))
        sys.modules[module.__name__] = module
        exec(compile(helper_raw, module.__file__, 'exec'), module.__dict__)
        result['compaction_module_loads'] = 1
        def profile(frame, event, arg):
            if event == 'call' and frame.f_code.co_filename == module.__file__:
                name = frame.f_code.co_name
                result['helper_entries'][name] = result['helper_entries'].get(name, 0) + 1
                require(name not in {'write', 'pack', 'verify', 'reconstruct', '_reconstruct', 'check_destination',
                                     'locked', 'publish_new_directory', 'sync_tree', 'archive_overlay', 'eligibility'},
                        'mutating/unneeded compaction helper forbidden: ' + name)
        sys.setprofile(profile)
        try:
            readback(request, module, out, result)
        finally:
            sys.setprofile(None)
        equal(stable(config_path), config_image, 'request unchanged')
        equal(stable(Path(__file__)), script_image, 'readback Source unchanged')
        descriptor(HELPER)
        descriptor(FREEZE)
        code = 0
    except BaseException as exc:
        sys.setprofile(None)
        result['status'] = 'FIRST_ERROR_STOPPED_ROOT_READY_BLOCKED'
        result['error'] = {'type': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()}
    finally:
        signal.alarm(0)
        sys.setprofile(None)
        try:
            descriptor(HELPER)
            descriptor(FREEZE)
            source_after = stable(Path(__file__))
            if script_image is not None:
                equal(source_after, script_image, 'final Source unchanged')
            result['source_after'] = {'script': source_after['identity'], 'compaction': HELPER,
                                      'host_source_freeze': FREEZE, 'unchanged': True}
        except BaseException as exc:
            result['status'] = 'SOURCE_AFTER_FAILURE_ROOT_READY_BLOCKED'
            result['source_after_error'] = {'type': type(exc).__name__, 'message': str(exc)}
            code = 1
        result['physically_opened_read_paths'] = sorted(opened)
        result['read_scope_note'] = 'Actual opened paths retained even on failure. Includes physical hash-only old capture reads if retained verification was reached; no combat Expected decoding, projection or model call.'
        result['elapsed_seconds'] = time.monotonic() - started
        save(out / 'result.json', result)
        files = []
        for p in sorted(out.iterdir()):
            if p.is_file():
                files.append(dict(path=str(p.relative_to(ROOT)), **stable(p)['identity']))
        save(out / 'owned-files.json', {'schema': 'phase468-readback-output-owner/1', 'files': files, 'no_more_writes': True})
        print(json.dumps({'status': result['status'], 'elapsed_seconds': result['elapsed_seconds']}), flush=True)
    return code


if __name__ == '__main__':
    raise SystemExit(main())
