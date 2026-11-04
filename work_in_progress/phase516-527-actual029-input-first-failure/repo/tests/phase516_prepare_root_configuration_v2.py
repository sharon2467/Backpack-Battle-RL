"""Fixed phase516 config/document preparation. No operational Source imports/calls."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import shutil
import stat
import sys

ROOT = Path('/workspace/python-original-engine/repo')
OUT = ROOT/'data/phase516-fixed029-root-configuration-v2'
TASK = Path('/workspace/godotsteam-startup-20261013')
BASELINE = TASK/'baseline/Backpack Battles'
POOL = Path('/workspace/native-combat-20261013/pool')
RUNS = POOL.parent/'runs'
RUN = RUNS/'original029-whelp-family-A-single-001'


def signature(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def image(path):
    path = Path(path)
    for ancestor in (path, *path.parents):
        assert not ancestor.is_symlink(), str(ancestor)
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and before.st_nlink == 1
    assert not stat.S_IMODE(before.st_mode) & 0o7000
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as stream:
        opened = os.fstat(stream.fileno())
        raw = stream.read()
        after = os.fstat(stream.fileno())
    assert signature(before) == signature(opened) == signature(after) == signature(path.lstat())
    assert len(raw) == before.st_size
    return raw, before


def descriptor(path):
    path = Path(path)
    raw, _ = image(path)
    name = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
    return dict(path=name, size=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def decoded(path):
    return json.loads(image(path)[0])


def verify(row):
    path = Path(row['path'])
    actual = descriptor(path if path.is_absolute() else ROOT/path)
    assert actual == row, (row, actual)
    return actual


def save(name, value):
    with (OUT/name).open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())


def main():
    OUT.mkdir(mode=0o700)
    template = ROOT/'data/phase508-case029-host-restore-source/root-config-source-template.json'
    historical = ROOT/'data/phase467-root-native-king-basic-001/oracle-acceptance.json'
    config = decoded(template)
    config['root_oracle_authorized'] = True
    config['resources'] = decoded(historical)['resources']
    review_dir = ROOT/'data/phase509-independent-final-acceptance'
    config['reviews']['host_source'] = dict(receipt=descriptor(review_dir/'review.json'),
                                           owner=descriptor(review_dir/'owned-files.json'))
    review_pin = config['reviews']['host_source']['receipt']
    assert review_pin['sha256'] == '700126e97c824ecba94fc252b33ec4a66bd6edd649242de5108b08707bdcc51b'
    review = decoded(ROOT/review_pin['path'])
    assert review['schema'] == 'phase509-independent-host-restore-source-review/1'
    assert review['status'] == 'ACCEPTED_SOURCE_ONLY_PENDING_ROOT_EXECUTE'
    assert review['source_freeze'] == config['source_freeze']
    assert review['observer_source_owner'] == config['observer_source_owner']
    assert all(type(config[key]) is int and config[key] == 0 for key in (
        'models_allowed', 'input_builds_allowed', 'expected_comparison_allowed'))
    assert set(config) == set(decoded(template)) and len(config) == 16
    pins = [config[key] for key in ('host', 'source_freeze', 'source_owner',
                                  'observer_source_freeze', 'observer_source_owner', 'active_source_tuple')]
    for role in config['reviews'].values():
        pins.extend(role.values())
        assert role['receipt'] in decoded(ROOT/role['owner']['path'])['files']
    freeze = decoded(ROOT/config['source_freeze']['path'])
    pins.extend(freeze['case_inputs'].values())
    pins.extend(descriptor(ROOT/'tests'/name) for name in (
        'phase508_oracle_storage.py', 'phase508_restore_predecessor.py',
        'phase508_independent_predecessor_readback.py', 'phase363_oracle_process.py',
        'phase363_oracle_storage.py'))
    authority_pin = freeze['native_source_origin']
    pins.append(authority_pin)
    checked = {row['path']: verify(row) for row in pins}
    resources = []
    for row in config['resources']:
        path = dict(source=ROOT, task=TASK, baseline=BASELINE)[row['root']]/row['path']
        actual = descriptor(path)
        assert all(actual[key] == row[key] for key in ('size', 'sha256'))
        resources.append(dict(row, actual_path=str(path), matched=True))
    authority = decoded(ROOT/authority_pin['path'])
    origins = []
    # Sapphire is an unmodified explicit Source origin, not an installation target.
    for key in ('squirrel', 'sapphire'):
        row = authority['origin'][key]
        assert Path(row['path']).parent == BASELINE/'Items/Exclusive'
        origins.append(verify(row))
    assert origins[1]['sha256'] == '583fdfee8bffcdcf56c795aba2ef1f7bbd29f9c16e906d2ffd48dfde150afc17'
    state_raw, _ = image(POOL/'state.json')
    state = json.loads(state_raw)
    assert state['status'] == 'ready'
    assert hashlib.sha256(state_raw).hexdigest() == 'e92ce49332709fe5cf71665b8add0f2ee47acaff4a04c5318f9d06ff0a543431'
    previous = Path(state['run'])
    assert previous.parent == RUNS and previous != RUN and previous.is_dir() and not previous.is_symlink()
    assert not RUN.exists() and not RUN.is_symlink()
    controls = []
    for name in ('state.json', 'data/custom_player.json', 'data/custom_opponent.json'):
        path = POOL/name
        pin = descriptor(path)
        info = path.lstat()
        controls.append(dict(pin, mode=stat.S_IMODE(info.st_mode), mtime_ns=info.st_mtime_ns))
    old_metadata = [descriptor(previous/name) for name in (
        'output/compaction/bundle-manifest.json', 'output/compaction/pool-roundtrip.json',
        'output/pool-provenance.json', 'output/host_manifest.json')]
    squirrel = POOL/'project/Items/Exclusive/Squirrel.gd'
    squirrel_pin = descriptor(squirrel)
    info = squirrel.lstat()
    ancestors = []
    for path in (POOL, POOL/'project', POOL/'project/Items', POOL/'project/Items/Exclusive'):
        entry = path.lstat()
        assert stat.S_ISDIR(entry.st_mode) and not path.is_symlink()
        ancestors.append(dict(path=str(path), mode=stat.S_IMODE(entry.st_mode),
                              mtime_ns=entry.st_mtime_ns, device=entry.st_dev, inode=entry.st_ino))
    free = shutil.disk_usage(RUNS).free
    required = 5905580032
    snapshot = dict(schema='phase516-selected-readonly-snapshot/1',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        source_scope='selected pins only; no Source helper or full inventory gate called',
        selected_source_pins=list(checked.values()), resource_pins_actual=resources,
        baseline_fixed_origin_pins=origins,
        pool_state=dict(controls[0], status=state['status'], run=state['run'],
                        scope='state-file only, NOT fresh full physical READY proof'),
        predecessor_control_files=controls, previous_control_metadata=old_metadata,
        squirrel_target=dict(squirrel_pin, mode=stat.S_IMODE(info.st_mode), mtime_ns=info.st_mtime_ns,
            ancestors=ancestors, equals_declared_reset_before={key:squirrel_pin[key] for key in ('size','sha256')}
                == freeze['paths']['Items/Exclusive/Squirrel.gd']['before'],
            scope='unlocked readonly snapshot; authoritative install preimage remains future'),
        space=dict(free_bytes=free, required_bytes=required, margin_bytes=free-required,
            sufficient=free>=required, pool_device=POOL.stat().st_dev, runs_device=RUNS.stat().st_dev,
            same_filesystem=POOL.stat().st_dev==RUNS.stat().st_dev,
            scope='snapshot; Root plan and lease must recheck'),
        run_path=str(RUN), unique_run_absent=True,
        zero_activities=dict(operational_source_imports=0, host_plan=0, host_execute=0, lease=0,
            pool_writes=0, cleanup=0, Godot=0, models=0, input_builds=0, Expected_business_reads=0, old_tests=0))
    save('oracle-acceptance.json', config)
    save('readonly-snapshot.json', snapshot)
    config_pin = descriptor(OUT/'oracle-acceptance.json')
    argv = [sys.executable, '-B', str(ROOT/'tests/phase508_oracle_host.py'),
        '--source-root', str(ROOT), '--task-root', str(TASK), '--baseline', str(BASELINE),
        '--pool', str(POOL), '--runs-root', str(RUNS), '--config', config_pin['path'],
        '--config-size', str(config_pin['size']), '--config-sha256', config_pin['sha256']]
    save('commands-for-root.json', dict(schema='phase516-root-command-proposal/1',
        status='PREPARED_NOT_INVOKED', cwd=str(ROOT), root_config=config_pin,
        plan_argv=argv+['--plan'], execute_argv=argv+['--execute'], attempt=1,
        case_id='NATIVE-029-WHELP-FAMILY-A', run=str(RUN), observed_predecessor=str(previous),
        seeds=dict(global_seed=50201, util_seed=50202), limits=dict(parse_wall_seconds=30,
            native_wall_seconds=300, collector_total_seconds=295, internal_battle_seconds=120,
            monitor_poll_seconds=0.05, term_grace_seconds=5.0, kill_grace_seconds=0.5,
            attempt_bytes=1610612736, free_floor_bytes=4294967296),
        guards='Independent config review; Root fresh Source/resource/READY/process/space/preimage gates; no retry',
        process_count=dict(parse_max=1, native_battle_max=1, model_max=0, input_build_max=0, expected_compare_max=0)))
    restore_paths = dict(controls_manifest=RUN/'output/predecessor-control-preimages/manifest.json',
        patch_inventory=RUN/'output/previous-source-preimages/inventory.json',
        install_journal=RUN/'output/source-preimages/preimages.json', pool_before=RUN/'output/pool-before.json',
        previous_bundle_manifest=previous/'output/compaction/bundle-manifest.json',
        previous_proof=previous/'output/compaction/pool-roundtrip.json',
        previous_provenance=previous/'output/pool-provenance.json',
        previous_project=previous/'output/compaction/project-files.json',
        previous_baseline=previous/'output/compaction/baseline-files.json',
        previous_staged=previous/'output/compaction/staged-inputs.json',
        previous_host_manifest=previous/'output/host_manifest.json', pending_state=POOL/'state.json')
    restore = dict(schema='phase508-fixed-predecessor-restore-request/1', case_id='NATIVE-029-WHELP-FAMILY-A',
        previous_run=str(previous), writer=descriptor(ROOT/'tests/phase508_restore_predecessor.py'),
        source_freeze=config['source_freeze'], evidence={key:None for key in restore_paths}, root_restore_authorized=False)
    readback = dict(schema='phase508-fixed-predecessor-readback-request/1', case_id='NATIVE-029-WHELP-FAMILY-A',
        run=str(RUN), pool=str(POOL), baseline=str(BASELINE), previous_run=str(previous), relocations={},
        host_source_freeze=config['source_freeze'], evidence={key:None for key in (
            'restore_receipt', 'restore_owner', 'controls_manifest', 'patch_inventory',
            'install_journal', 'previous_proof', 'previous_bundle_manifest', 'pending_state')})
    save('postcapture-restore-readback-contract.json', dict(schema='phase516-future-binding-contract-not-runtime-request/1',
        status='NOT_EXECUTABLE_NEW_EVIDENCE_NOT_YET_CREATED', restore_template=restore,
        restore_expected_paths={key:str(path) for key,path in restore_paths.items()}, readback_template=readback,
        restore_output_new=str(ROOT/'data/phase508-restore-case029-first-001'),
        readback_output_new=str(ROOT/'data/phase508-readback-case029-first-001'),
        request_binding='Root binds actual complete descriptors after stopped writers and exact failed/PENDING association.',
        failed_partial_rule='Missing exact pending or complete journal/backups/pool-before blocks unchanged restore; preserve first error.',
        ready_commit='Root exact saved state bytes/mode/mtime only after independent physical PASS; writer/reader READY_writes=0'))
    save('preparation-result.json', dict(schema='phase516-configuration-preparation/1',
        status='CANDIDATE_FROZEN_ROOT_AND_INDEPENDENT_REVIEW_PENDING', config=config_pin,
        template=descriptor(template), resource_identity_source=descriptor(historical),
        changed_config_keys=['root_oracle_authorized', 'reviews.host_source', 'resources'],
        unchanged_operational_source=True, selected_source_refs=len(checked), resource_pins_matched=len(resources),
        fresh_space_margin=free-required, actual_blockers=[] if free>=required else ['INSUFFICIENT_FRESH_SPACE'],
        uncompleted_gates=['independent exact config review', 'Root actual full Source/resource/READY/process/space plan',
            'lease/install actual ancestor/preimage gates', 'native parse/capture', 'actual restoration/readback/Root state commit'],
        author_counts=dict(configuration_assembly_attempts=2, first_inline_failed_before_output=1,
            operational_imports=0, plan=0, execute=0, Native=0, models=0, pool_writes=0),
        authorization_basis='Root 2026-11-04 explicit fixed029 oracle-only authorization, not Source/helperPASS',
        quota='UNKNOWN_NO_GUESS; trusted<=30/userpause checkpoint and stop'))
    print(json.dumps(dict(output=str(OUT), config=config_pin, space=snapshot['space'], previous=str(previous))))


if __name__ == '__main__':
    main()
