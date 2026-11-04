"""Fixed original028 King/basic oracle host Source. No model/projection/admission."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import stat
from phase508_oracle_storage import (directory,member,pin,read,write_new,sync,budget,check_ready,lease,
                                     reset_previous,install,archive_streaming,c,check_source_descriptor,MAX_INSTALL_PAYLOADS,MAX_INSTALL_BYTES,
                                     regular_target,state_write,_source_signature)
from phase363_oracle_process import execute_process,rename_capture,usage

SOURCE = 'data/phase508-case029-host-restore-source'
OBSERVER_SOURCE = 'data/phase502-whelp-observer-source-v4'
CASE = 'NATIVE-029-WHELP-FAMILY-A'
RUN_NAME = 'original029-whelp-family-A-single-001'
HOST_REVIEW_SCHEMA = 'phase509-independent-host-restore-source-review/1'
HOST_REVIEW_STATUS = 'ACCEPTED_SOURCE_ONLY_PENDING_ROOT_EXECUTE'
OBSERVER_FREEZE = {'path': 'data/phase502-whelp-observer-source-v4/combined-source-freeze.json', 'size': 58760, 'sha256': '04e152576b706f66da05d33fe493670604eca14110cbe98e73ee5f3703afb44a'}
OBSERVER_OWNER = {'path': 'data/phase502-whelp-observer-source-v4/source-owner.json', 'size': 27181, 'sha256': '48a578c6d8f9f2189e5241432d6e0b14fed8a5d4fda948ca73b0ab62dd6c8d8f'}
OBSERVER_REVIEW = {'path': 'data/phase503-independent-final-acceptance/review.json', 'size': 7550, 'sha256': '468ec5cb36e2d11f0a1a7e8160eca4d806b5fe10bb92ce90ccf2733ea1cd3db4'}
OBSERVER_REVIEW_OWNER = {'path': 'data/phase503-independent-final-acceptance/owned-files.json', 'size': 246, 'sha256': '3410cf0c5a236be98ee5344ba53b3fa3fc946be927d221964ad5985e90186d44'}
CASE_INPUTS = {'custom_player.json': {'path': 'data/phase502-whelp-observer-source-v4/case-inputs/custom_player.json', 'size': 1368, 'sha256': 'bfa9f397f496af588f13d2bca84720103b4ba859d6b5af76e884402119d87d4f'}, 'custom_opponent.json': {'path': 'data/phase502-whelp-observer-source-v4/case-inputs/custom_opponent.json', 'size': 1129, 'sha256': 'd8454598798be1401c75a6d7a97dd0c96b70857b2c8876028fd9693dd5935d5d'}, 'native_capture_config.json': {'path': 'data/phase502-whelp-observer-source-v4/case-inputs/native_capture_config.json', 'size': 237, 'sha256': 'fea1073bab56e162e3530ff445f2824de6d12fdddb1f3980ec24c9cae3b06ce4'}}
POLICY = 'bounded-writers-and-monitored-process/1'
RESTORE_POLICY = 'restore-predecessor-after-independent-readback-root-commit/1'
NAMES = ('custom_player.json','custom_opponent.json','native_capture_config.json')
SOURCE_AUTHORITY = {'path': 'data/phase502-whelp-observer-source-v4/source-authority.json', 'size': 3492, 'sha256': '2ffbd2330149605cabaac0742d9dd425ba34cad470b340ed68e62b235ad8ac64'}
BASELINE_SOURCE_REFERENCE = '/workspace/godotsteam-startup-20261013/baseline/Backpack Battles'
ABSOLUTE_SOURCE_PINS = {'/workspace/godotsteam-startup-20261013/baseline/Backpack Battles/Items/Exclusive/Squirrel.gd': {'path': '/workspace/godotsteam-startup-20261013/baseline/Backpack Battles/Items/Exclusive/Squirrel.gd', 'sha256': 'c23b8aec966449cc60761007879b99c3528c4cbe94309914789954cea34de949', 'size': 508}, '/workspace/godotsteam-startup-20261013/baseline/Backpack Battles/Items/Exclusive/SapphireWhelp.gd': {'path': '/workspace/godotsteam-startup-20261013/baseline/Backpack Battles/Items/Exclusive/SapphireWhelp.gd', 'sha256': '583fdfee8bffcdcf56c795aba2ef1f7bbd29f9c16e906d2ffd48dfde150afc17', 'size': 384}}
LAWFUL = ('fixture.json','player_fixture.json','observer7-input.jsonl','observer7-lineage.jsonl',
          'observer7-metadata.jsonl','observer7-primitives.jsonl','king-clock-checkpoint.json',
          'king-clock-passes.jsonl','king-input-facts.json','king-ui-authority.jsonl',
          'king-rng-checkpoint.json','king-slot-bindings.json')


def descriptor(source_root,row):
    if (type(row) is not dict or set(row)!={'path','size','sha256'} or type(row['path']) is not str
            or type(row['size']) is not int or row['size']<0 or type(row['sha256']) is not str or re.fullmatch('[0-9a-f]{64}',row['sha256']) is None):
        raise ValueError('exact Source descriptor')
    if Path(row['path']).is_absolute():
        if ABSOLUTE_SOURCE_PINS.get(row['path'])!=row:raise ValueError('unapproved absolute Source reference')
        origin=Path(BASELINE_SOURCE_REFERENCE)
        relative=str(Path(row['path']).relative_to(origin))
        return check_source_descriptor(origin,dict(path=relative,size=row['size'],sha256=row['sha256']))
    path=member(source_root,row['path'])
    if not path.is_file() or pin(path)!={k:row[k] for k in ('size','sha256')}:raise ValueError('actual descriptor drift')
    return path


def verify_owner(source_root,row):
    path=descriptor(source_root,row); value=read(path)
    rows=value['files']
    if type(rows) is not list or not rows: raise ValueError('nonempty actual source owner')
    leaves={}
    for leaf in rows:
        descriptor(source_root,leaf)
        if leaf['path'] in leaves: raise ValueError('duplicate owner leaf')
        leaves[leaf['path']]={k:leaf[k] for k in ('size','sha256')}
    return leaves


def validate_observer_review(value,receipt,source_tuple):
    if (receipt!=OBSERVER_REVIEW or value.get('schema')!='phase503-independent-final-producer-acceptance/1'
            or value.get('status')!='ACCEPTED_SOURCE_AND_12_SYNTHETIC_SCHEMA_CONTROLS_NOT_NATIVE_VALIDATION'
            or value.get('accepted_source_owner')!=OBSERVER_OWNER or value.get('accepted_source_tuple')!=source_tuple):
        raise ValueError('actual503 Source-only acceptance for exact502v4 required')


def source_gate(source_root,config_descriptor):
    root=directory(source_root); config_path=descriptor(root,config_descriptor); config=read(config_path)
    keys={'schema','host','source_freeze','source_owner','observer_source_freeze','observer_source_owner',
          'active_source_tuple','reviews','resources','relocations','write_policy','restore_policy',
          'root_oracle_authorized','models_allowed','input_builds_allowed','expected_comparison_allowed'}
    if type(config) is not dict or set(config)!=keys or config.get('schema')!='phase508-root-oracle-acceptance/1' or config.get('root_oracle_authorized') is not True:
        raise ValueError('actual root oracle-only authorization required')
    if any(type(config.get(k)) is not int or config[k]!=0 for k in ('models_allowed','input_builds_allowed','expected_comparison_allowed')):
        raise ValueError('strictINT0 model/inputbuild/expected permissions')
    if config.get('write_policy')!=POLICY or config.get('restore_policy')!=RESTORE_POLICY:
        raise ValueError('exact monitored-writes and predecessor-restore policies')
    if config['observer_source_freeze']!=OBSERVER_FREEZE or config['observer_source_owner']!=OBSERVER_OWNER:
        raise ValueError('exact actual462v3 observer source identities')
    descriptor(root,OBSERVER_FREEZE)
    observer_leaves=verify_owner(root,OBSERVER_OWNER)
    if observer_leaves.get(OBSERVER_FREEZE['path'])!={k:OBSERVER_FREEZE[k] for k in ('size','sha256')}:
        raise ValueError('observer owner must cover actual observer freeze')
    freeze_path=descriptor(root,config['source_freeze'])
    if str(freeze_path.relative_to(root))!=SOURCE+'/combined-source-freeze.json': raise ValueError('exact464 host-derived SOURCE freeze')
    freeze=read(freeze_path)
    if (freeze.get('schema')!='phase508-host-derived-source-freeze/1'
            or freeze.get('observer_source_freeze')!=OBSERVER_FREEZE or freeze.get('observer_source_owner')!=OBSERVER_OWNER):
        raise ValueError('host freeze must bind actual462 observer')
    observer_freeze=read(descriptor(root,OBSERVER_FREEZE))
    for key in ('paths','artifacts','collector','schema_module','active_source_tuple','profile','observer_version','terminal_policy'):
        if key not in observer_freeze or freeze.get(key)!=observer_freeze[key]: raise ValueError('missing/mixed observer binding: '+key)
    if freeze.get('native_source_origin')!=SOURCE_AUTHORITY or freeze.get('schema_case')!='WHELP-FAMILY-A-502':
        raise ValueError('derived actual sourceauthority and fixedplan case required')
    if freeze.get('case_inputs')!=CASE_INPUTS or config['source_owner'].get('path')!=SOURCE+'/source-owner.json':
        raise ValueError('exact464 Source owner and three462 case inputs')
    for row in freeze['files']: descriptor(root,row)
    leaves=verify_owner(root,config['source_owner'])
    if leaves.get(str(Path(__file__).relative_to(root)))!=pin(Path(__file__)) or leaves.get(config['source_freeze']['path'])!=pin(freeze_path):
        raise ValueError('owner must actually cover host and freeze')
    reviews=config['reviews']
    if type(reviews) is not dict or set(reviews)!={'observer503','host_source'}:
        raise ValueError('both actual observer463 and new host Source reviews required')
    for role,review in reviews.items():
        if type(review) is not dict or set(review)!={'receipt','owner'}: raise ValueError('closed review descriptors')
        receipt=descriptor(root,review['receipt']); owned=verify_owner(root,review['owner']); result=read(receipt)
        if owned.get(review['receipt']['path'])!=pin(receipt): raise ValueError('owned independent Source receipt')
        if role=='observer503':
            if review['owner']!=OBSERVER_REVIEW_OWNER:raise ValueError('actual463 review owner')
            validate_observer_review(result,review['receipt'],config['active_source_tuple'])
        elif (result.get('schema')!=HOST_REVIEW_SCHEMA or result.get('status')!=HOST_REVIEW_STATUS
              or result.get('source_freeze')!=config['source_freeze'] or result.get('observer_source_owner')!=OBSERVER_OWNER
              or any(type(result.get(k)) is not int or result[k]!=0 for k in ('native','models'))):
            raise ValueError('exact actual new host review and zero execution')
    if config.get('active_source_tuple') != freeze['active_source_tuple']:
        raise ValueError('Root must pin actual462v3 source tuple')
    validate_active_source_tuple(root,freeze)
    if freeze['accepted_source_controls'] != []:
        raise ValueError('historical controls cannot approve new SOURCE')
    for row in freeze['historical_source_controls']: check_source_descriptor(root,row)
    own=descriptor(root,config['host'])
    if own!=Path(__file__).absolute(): raise ValueError('exact executing host identity')
    return root,config,freeze


def resource_gate(root,config,paths):
    roots=dict(source=root,task=paths['task_root'],baseline=paths['baseline'])
    rows=config.get('resources')
    if type(rows) is not list or not rows: raise ValueError('actual runtime/resource pins required')
    seen=set()
    for row in rows:
        if row['root'] not in roots or (row['root'],row['path']) in seen: raise ValueError('duplicate/unknown resource root')
        seen.add((row['root'],row['path']))
        descriptor(roots[row['root']],{k:row[k] for k in ('path','size','sha256')})
    mandatory={('source','tests/godotsteam_offline_exec.py'),('task','engine/godotsteam.362.editor.x86_64'),
               ('task','engine/libsteam_api.so'),('task','debian/usr/bin/xvfb-run')}
    if not mandatory<=seen: raise ValueError('explicit offline runner/engine/Steam/Xvfb binding')
    engine=member(paths['task_root'],'engine/godotsteam.362.editor.x86_64')
    if pin(engine)['sha256']!='09d1de6c4f97289c018556666c13c1d81093a5df5c2255725d464a87f40a8ea1': raise ValueError('exact accepted engine')


def plan(source_root,config_descriptor,task_root,baseline,pool,runs_root):
    root,config,freeze=source_gate(source_root,config_descriptor)
    paths={name:directory(value) for name,value in dict(task_root=task_root,baseline=baseline,pool=pool,runs_root=runs_root).items()}
    if paths['baseline'] != paths['task_root']/'baseline/Backpack Battles': raise ValueError('explicit task/baseline relation')
    if paths['pool'].is_relative_to(root) or root.is_relative_to(paths['pool']): raise ValueError('SOURCE and pool disjoint')
    resource_gate(root,config,paths)
    payloads=resolve_execute_payloads(root,freeze,execute_driver_descriptors(root,config_descriptor,config,freeze))
    previous=check_ready(paths['pool'],paths['baseline'],config['relocations'])
    capacity=budget(paths['pool'],paths['runs_root'])
    run=paths['runs_root']/RUN_NAME
    if run.exists(): raise ValueError('fixed unique attempt path already exists')
    native_config=read(check_source_descriptor(root,payloads['case_inputs']['native_capture_config.json']))
    if native_config!=dict(schema='native-combat-capture/1',case_id=CASE,global_seed=50201,util_seed=50202,
                          player_fixture_enabled=True,timeouts=dict(battle_seconds=120,total_seconds=295)):
        raise ValueError('fixed SOURCE config/seeds/timeouts')
    return dict(schema='phase508-oracle-readonly-plan/1',paths={k:str(v) for k,v in paths.items()},source_root=str(root),
        run=str(run),case_id=CASE,attempt=1,previous_run=str(previous),budget=capacity,
        root_config=config_descriptor,freeze=config['source_freeze'],source_owner=config['source_owner'],
        reviews=config['reviews'],config=native_config,policy=POLICY,execute_payloads=payloads,
        oracle_processes=0,models=0,projection_calls=0,Game_copies=0,
        source_profile=freeze['profile'],schema_case=freeze['schema_case'],native_scope='FIXED_29_ITEM_ZERO_KING_WHELP_ORACLE_ONLY',
        restore_policy=RESTORE_POLICY,final_pool_state='FAILED_PENDING_INDEPENDENT_PREDECESSOR_RESTORE')


def backup_predecessor_controls(pool,backup,state_preimage,previous):
    """Fixed three images only; caller holds464 lease, state snapshot precedes busy."""
    backup=Path(backup)
    if backup.exists() or backup.is_symlink(): raise ValueError('unique predecessor control backup')
    if type(state_preimage) is not dict or set(state_preimage)!={'raw','identity','mode','mtime_ns'}:
        raise ValueError('fixed locked predecessor state image')
    if type(state_preimage['raw']) is not bytes or dict(size=len(state_preimage['raw']),sha256=hashlib.sha256(state_preimage['raw']).hexdigest())!=state_preimage['identity']:
        raise ValueError('locked predecessor state bytes')
    backup.mkdir()
    rows=[]
    images=[('state.json',state_preimage)]
    for name in NAMES[:2]:
        path=member(pool,'data/'+name);before=regular_target(path,absent=True)
        if before is None:
            images.append(('data/'+name,None));continue
        fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
        with os.fdopen(fd,'rb') as stream:
            opened=os.fstat(stream.fileno());raw=stream.read(before.st_size+1);after=os.fstat(stream.fileno())
        if (len(raw)!=before.st_size or _source_signature(before)!=_source_signature(opened)
                or _source_signature(before)!=_source_signature(after)
                or _source_signature(before)!=_source_signature(regular_target(path))):
            raise ValueError('locked predecessor fixture changed during backup')
        images.append(('data/'+name,dict(raw=raw,identity=dict(size=len(raw),sha256=hashlib.sha256(raw).hexdigest()),
                                       mode=stat.S_IMODE(before.st_mode),mtime_ns=before.st_mtime_ns)))
    for index,(target,image) in enumerate(images):
        if image is None:
            rows.append(dict(target=target,present=False,backup=None));continue
        path=backup/str(index)
        with path.open('xb') as stream: stream.write(image['raw']);stream.flush();os.fsync(stream.fileno())
        os.chmod(path,image['mode']);os.utime(path,ns=(image['mtime_ns'],image['mtime_ns']))
        info=regular_target(path)
        if pin(path)!=image['identity'] or stat.S_IMODE(info.st_mode)!=image['mode'] or info.st_mtime_ns!=image['mtime_ns']:
            raise ValueError('predecessor image readback')
        with path.open('rb') as stream:os.fsync(stream.fileno())
        rows.append(dict(target=target,present=True,backup=str(index),identity=image['identity'],
                         mode=image['mode'],mtime_ns=image['mtime_ns']))
    value=dict(schema='phase464-predecessor-control-preimages/1',previous_run=str(previous),images=rows,
               state_snapshot='inside_lease_lock_after_check_ready_before_busy',fixtures_snapshot='inside_same_lease_before_reset',
               restored=False,ready_commit='ROOT_ONLY_AFTER_INDEPENDENT_PHYSICAL_READBACK')
    write_new(backup/'manifest.json',value);sync(backup)
    return dict(path=str(backup),manifest=pin(backup/'manifest.json'),restored=False)


def execute(source_root,config_descriptor,task_root,baseline,pool,runs_root):
    launch=plan(source_root,config_descriptor,task_root,baseline,pool,runs_root)
    root,config,freeze=source_gate(source_root,config_descriptor)
    paths={key:Path(value) for key,value in launch['paths'].items()}
    payloads=resolve_execute_payloads(root,freeze,execute_driver_descriptors(root,config_descriptor,config,freeze))
    if payloads!=launch['execute_payloads']: raise ValueError('plan/execute payload descriptor graph changed before lease')
    verify_execute_payloads(root,payloads)
    with lease(paths['pool'],paths['baseline'],paths['runs_root'],RUN_NAME,config['relocations']) as (previous,run,state_preimage):
        run.mkdir(); (run/'output').mkdir(); (run/'output/driver').mkdir(); (run/'data').mkdir()
        for name in ('data','config','cache','run','tmp'): (run/'user'/name).mkdir(parents=True,mode=0o700)
        out=run/'output'; project=paths['pool']/'project'
        write_new(out/'readonly-plan.json',launch)
        controls_backup=backup_predecessor_controls(paths['pool'],out/'predecessor-control-preimages',state_preimage,previous)
        reset=reset_previous(project,paths['baseline'],previous,out/'previous-source-preimages')
        write_new(out/'prior-observer-reset.json',reset)
        for name in NAMES:
            shutil.copy2(check_source_descriptor(root,payloads['case_inputs'][name]),run/'data'/name)
            if pin(run/'data'/name)!={k:payloads['case_inputs'][name][k] for k in ('size','sha256')}: raise ValueError('case copy identity')
        artifacts=payloads['artifacts']
        journal=install(root,project,freeze,artifacts,out/'source-preimages')
        for name in NAMES[:2]: shutil.copy2(run/'data'/name,paths['pool']/'data'/name)
        report=dict(schema='observer7-patch/1',patch_version='phase508-oracle-zeroKing-whelp',added_files=['native_random_observer_sink_v7.gd'],
                    patches=[dict(path=name,before_size=None if row['before'] is None else row['before']['size'],
                        before_sha256=None if row['before'] is None else row['before']['sha256'],
                        after_size=row['after']['size'],after_sha256=row['after']['sha256']) for name,row in freeze['paths'].items()])
        (out/'observer-patch').mkdir(); write_new(out/'observer-patch/native_random_observer_patch_manifest.json',report)
        write_new(out/'host_manifest.json',dict(schema='phase508-oracle-host/1',case_id=CASE,
            audited_runtime_observation_patch=report,source_freeze=config['source_freeze'],collector=pin(project/'native_combat_capture.gd'),models=0))
        # Archive the exact SOURCE actually used before any Godot command.
        copies=payloads['driver_sources']
        saved=[]
        for index,row in enumerate(copies):
            source=descriptor(root,row); target=out/'driver'/str(index)
            shutil.copy2(source,target)
            if pin(target)!=pin(source): raise ValueError('driver SOURCE readback')
            saved.append(dict(file=target.name,source=row))
        write_new(out/'driver/source-map.json',dict(files=saved))
        write_new(out/'pool-provenance.json',dict(schema='phase362-explicit-pool-provenance/1',plan=launch,
            installed_preimages=journal,driver_sha256={p.name:c.digest(p) for p in (out/'driver').iterdir()},
            inputs={name:pin(run/'data'/name) for name in NAMES},full_game_copy=False,
            predecessor_control_preimages=controls_backup,previous_patch_and_marker_backup=str(out/'previous-source-preimages'),
            new_install_preimages=str(out/'source-preimages'),restore_policy=RESTORE_POLICY))
        before=dict(baseline=c.inventory(paths['baseline']),project=c.inventory(project),staged=c.inventory(paths['pool']/'data'))
        write_new(out/'pool-before.json',before)
        parsed=execute_process(root,paths['task_root'],run,project,check_only=True)
        if not parsed['process_clean_exit'] or parsed['abort_reason']: raise RuntimeError('check-only failed; no native start')
        if c.inventory(project)!=before['project']: raise ValueError('parse-only changed project tree')
        if descriptor(root,config_descriptor)!=descriptor(root,launch['root_config']): raise ValueError('config drift')
        # Preserve the same config identity, no second dynamic plan after mutation.
        source_gate(root,config_descriptor); resource_gate(root,config,paths); usage(run)
        write_new(out/'one-shot-launch.json',dict(case_id=CASE,attempt=1,models=0,timeout=dict(battle=120,collector=295,runner=300)))
        result=execute_process(root,paths['task_root'],run,project,check_only=False)
        write_new(out/'process-returned.json',result)
        partition=collect_capture_metadata(run,result,root,freeze)
        project_changed=c.inventory(project)!=before['project']
        complete=partition['capture_complete'] and not project_changed
        write_new(out/'source-partition.json',partition)
        write_new(out/'process_result.json',dict(result,capture_complete=complete,
            primary_failure=partition['primary_failure'],secondary_errors=partition['secondary_errors'],
            source_changes_after_run=['PROJECT_TREE_CHANGED'] if project_changed else [],
            process_clean_exit=result['process_clean_exit'],model_acceptance=False,automatic_retry=False))
        if not complete: raise RuntimeError('first original029 failed/partial; preserve, no retry')
        proof=archive_streaming(paths['baseline'],paths['pool'],run,before)
        # Existing archive briefly writes its normal READY while this same lease stays locked.
        # Do not expose a completed predecessor restoration or paste the old READY snapshot.
        state_write(paths['pool'],dict(status='failed',run=str(run),reason='PENDING_INDEPENDENT_PREDECESSOR_RESTORE',
                    previous_run=str(previous),control_preimages=controls_backup,utc=c.stamp()))
        return dict(status='ORACLE_CAPTURE_ARCHIVED_PENDING_INDEPENDENT_PREDECESSOR_RESTORE',run=str(run),proof=proof,
                    process_clean_exit=result['process_clean_exit'],models=0,inputbuilds=0,King_production_admitted=False)



def read_control(path,limit):
    if pin(path)['size']>limit: raise ValueError('bounded control JSON exceeded cap')
    value=read(path)
    if type(value) is not dict: raise ValueError('control JSON must be object')
    return value


def collect_capture_metadata(run,result,source_root,freeze):
    """Decode controls only; business/expected observations remain opaque hashes."""
    secondary=[]; primary=None; capture=None; present={}; expected={}; validation=None; partial={}; control_files={}; terminal=None
    try: capture=rename_capture(run)
    except Exception as exc:
        secondary.append(dict(code='capture_relocation_failed',error=repr(exc)))
        if (run/'output/capture').is_dir() and not (run/'output/capture').is_symlink(): capture=run/'output/capture'
        for root in (run/'user',) if capture is None else ():
            if root.is_dir() and not root.is_symlink():
                for path in sorted(root.rglob('*')):
                    if path.is_symlink(): secondary.append(dict(code='linked_partial_capture',path=str(path.relative_to(run))))
                    elif path.is_file(): partial[str(path.relative_to(run))]=pin(path)
    if capture is not None:
        for path in sorted(capture.iterdir()):
            if path.is_symlink() or not path.is_file():
                secondary.append(dict(code='unsupported_capture_leaf',file=path.name)); continue
            (present if path.name in LAWFUL else expected)[path.name]=pin(path)
        control_files={name:expected.pop(name) for name in ('collector-first-failure.json','observer7_failure.json') if name in expected}
        control=capture/'collector-first-failure.json'
        if control.name in control_files:
            try: primary=dict(kind='collector_control_failure',identity=pin(control),control=read_control(control,65536))
            except Exception as exc:
                primary=dict(kind='invalid_collector_control_failure',identity=pin(control))
                secondary.append(dict(code='bad_collector_control',error=repr(exc)))
        observer_failure=capture/'observer7_failure.json'
        if observer_failure.name in control_files:
            identity=control_files[observer_failure.name]
            try:
                observer_control=read_control(observer_failure,4096)
                if observer_control.get('schema')!='observer7-failure/1' or type(observer_control.get('code')) is not str:
                    raise ValueError('observer first failure control schema')
                observed=dict(kind='observer_control_failure',identity=identity,control=observer_control)
                if primary is None: primary=observed
                else: secondary.append(dict(code='additional_observer_control_failure',failure=observed,precedence='COLLECTOR_IF_PRESENT_NO_TIME_ORDER_INFERRED'))
            except Exception as exc:
                if primary is None: primary=dict(kind='invalid_observer_control_failure',identity=identity)
                secondary.append(dict(code='bad_observer_control',identity=identity,error=repr(exc)))
        path=capture/'validation.json'
        if path.name not in expected: secondary.append(dict(code='missing_required_file',file='validation.json'))
        else:
            try: validation=read_control(path,1024*1024)
            except Exception as exc: secondary.append(dict(code='bad_validation',identity=pin(path),error=repr(exc)))
    else: secondary.append(dict(code='missing_required_file',file='validation.json'))
    missing=[name for name in LAWFUL if name not in present]
    if missing: secondary.append(dict(code='missing_lawful_inputs',files=missing))
    process_ok=result['exit_code']==0 and not result['abort_reason'] and not result['timed_out']
    if primary is None and not process_ok:
        primary=dict(kind='native_process_failure',exit_code=result['exit_code'],abort_reason=result['abort_reason'],timed_out=result['timed_out'])
    if capture is not None:
        try: terminal=read_terminal_expected_controls(source_root,freeze,capture)
        except Exception as exc:
            secondary.append(dict(code='terminal_expected_control_failure',error=repr(exc)))
            if primary is None: primary=dict(kind='terminal_expected_control_failure',error=repr(exc))
    complete=process_ok and primary is None and not missing and validation is not None and validation.get('native_checks_pass') is True and terminal is not None and not secondary
    return dict(schema='phase365-partial-source-partition/1',capture_complete=complete,
        capture=None if capture is None else str(capture),lawful_inputs_present=present,lawful_inputs_missing=missing,
        expected_observations_opaque=expected,control_failures_opaque=control_files,partial_files_opaque=partial,primary_failure=primary,secondary_errors=secondary,
        expected_semantics_read=False,terminal_expected_control=terminal,models=0,projection=0)


"""Descriptor graph SOURCE merged into the new oracle host. No entrypoint."""


def _payload_rows(rows):
    if type(rows) not in (list,tuple): raise ValueError('descriptor row list required')
    result={}
    for row in rows:
        if type(row) is not dict or set(row)!={'path','size','sha256'}: raise ValueError('closed descriptor row')
        if row['path'] in result and result[row['path']]!=row: raise ValueError('same source path has conflicting identities')
        result[row['path']]=dict(row)
    return result


def resolve_execute_payloads(source_root,freeze,driver_descriptors=()):
    """Public real resolver, independent of pool/lease/ROOT execution permission."""
    root=directory(source_root); declared=_payload_rows(freeze['files'])
    validate_active_source_tuple(root,freeze)
    if type(freeze.get('paths')) is not dict or len(freeze['paths'])!=76: raise ValueError('exact76 SOURCE patches')
    patches=[]
    for name,row in freeze['paths'].items():
        c.safe_path(name)
        source=dict(path=row['after_path'],**row['after'])
        if declared.get(source['path'])!=source: raise ValueError('patch source not in frozen descriptor closure')
        patches.append(dict(target=name,source=source,before=row['before']))
    def frozen(name):
        if name not in declared: raise ValueError('required fixedDATA descriptor absent')
        return dict(declared[name])
    if freeze.get('case_inputs')!=CASE_INPUTS:raise ValueError('exact three462v3 case descriptors')
    cases={name:frozen(CASE_INPUTS[name]['path']) for name in NAMES}
    if cases!=CASE_INPUTS:raise ValueError('fixed actual462 input bytes')
    observer=read(check_source_descriptor(root,OBSERVER_FREEZE))
    artifacts={'native_combat_capture.gd':dict(freeze['collector']),
        'native_capture_config.json':dict(cases['native_capture_config.json']),
        '.native-random-observer-disposable':frozen(observer['artifacts']['.native-random-observer-disposable']['path'])}
    if artifacts!=freeze.get('artifacts') or artifacts!=observer['artifacts']:
        raise ValueError('actual462 artifact descriptors differ')
    for row in artifacts.values():
        if declared.get(row['path'])!=row: raise ValueError('artifact not in actual frozen descriptor closure')
    bindings={name:dict(freeze[name]) for name in ('collector','schema_module','active_source_tuple','native_source_origin')}
    drivers=_payload_rows(list(declared.values())+list(driver_descriptors)+list(bindings.values()))
    graph=dict(schema='phase380-execute-payloads/1',patches=patches,artifacts=artifacts,case_inputs=cases,
        source_bindings=bindings,driver_sources=[drivers[k] for k in sorted(drivers)],
        labels=dict(profile=freeze['profile'],schema_case=freeze['schema_case']),
        install_limits=dict(files=MAX_INSTALL_PAYLOADS,bytes=MAX_INSTALL_BYTES))
    verify_execute_payloads(root,graph)
    return graph


def verify_execute_payloads(source_root,graph):
    """Read every true execute SOURCE descriptor; no ready/preflight bool input."""
    root=directory(source_root)
    if type(graph) is not dict or set(graph)!={'schema','patches','artifacts','case_inputs','source_bindings','driver_sources','labels','install_limits'} or graph['schema']!='phase380-execute-payloads/1':
        raise ValueError('closed real execute payload graph')
    if graph['install_limits']!=dict(files=MAX_INSTALL_PAYLOADS,bytes=MAX_INSTALL_BYTES): raise ValueError('exact frozen install limits')
    if type(graph['patches']) is not list or len(graph['patches'])!=76: raise ValueError('exact76 execute patch descriptors')
    if set(graph['artifacts'])!={'native_combat_capture.gd','native_capture_config.json','.native-random-observer-disposable'} or set(graph['case_inputs'])!=set(NAMES):
        raise ValueError('complete fixed artifact and case-input destinations')
    targets=set(); install=[]
    for row in graph['patches']:
        if type(row) is not dict or set(row)!={'target','source','before'}: raise ValueError('closed patch payload row')
        c.safe_path(row['target'])
        if row['target'] in targets: raise ValueError('duplicate mutable patch destination')
        targets.add(row['target']); install.append(row['source'])
    for name,row in graph['artifacts'].items():
        c.safe_path(name)
        if name in targets: raise ValueError('overlapping mutable artifact destination')
        targets.add(name);install.append(row)
    if len(install)!=MAX_INSTALL_PAYLOADS or sum(row['size'] for row in install)!=MAX_INSTALL_BYTES:
        raise ValueError('actual complete frozen install corpus count/size differs')
    if graph['artifacts']['native_combat_capture.gd']!=graph['source_bindings'].get('collector') or graph['artifacts']['native_capture_config.json']!=graph['case_inputs']['native_capture_config.json']:
        raise ValueError('reused artifact authority mismatch')
    if set(graph['source_bindings'])!={'collector','schema_module','active_source_tuple','native_source_origin'}: raise ValueError('required explicit source origins')
    drivers=_payload_rows(graph['driver_sources'])
    all_rows=install+list(graph['case_inputs'].values())+list(graph['source_bindings'].values())+list(drivers.values())
    unique=_payload_rows(all_rows)
    if any(drivers.get(row['path'])!=row for row in all_rows): raise ValueError('driver archive missing execute source binding')
    for row in unique.values():
        if Path(row['path']).is_absolute():descriptor(root,row)
        else:check_source_descriptor(root,row)
    return dict(status='SOURCE_PAYLOAD_IDENTITIES_CHECKED_NOT_EXECUTED',sources=len(unique),install_files=len(install),install_bytes=sum(row['size'] for row in install))


def execute_driver_descriptors(root,config_descriptor,config,freeze):
    rows=list(freeze['files'])+read(descriptor(root,config['source_owner']))['files']
    rows += [config_descriptor,config['source_owner'],config['source_freeze']]
    for review in config['reviews'].values(): rows += [review['receipt'],review['owner']]
    return list(_payload_rows(rows).values())

"""Expected/control SOURCE helpers; loaded by the actual391 host after descriptor checks."""

TERMINAL_POLICY = 'first-actual-idle-after-at-least-two-future-physics/1'
OBSERVER_VERSION = '7-whelp-family-A-502'
OBSERVER_PROFILE = 'observer7-whelp-family-A-native-tape/1'


def validate_active_source_tuple(root, freeze):
    if (freeze.get('schema') != 'phase508-host-derived-source-freeze/1'
            or freeze.get('observer_source_freeze') != OBSERVER_FREEZE or freeze.get('observer_source_owner') != OBSERVER_OWNER):
        raise ValueError('closed508 binding to actual502 Source required')
    observer=read(check_source_descriptor(root,OBSERVER_FREEZE))
    if freeze['active_source_tuple'] != observer['active_source_tuple']:
        raise ValueError('exact502v4 tuple descriptor')
    value=read(check_source_descriptor(root,freeze['active_source_tuple']))
    keys={'schema','profile','observer_version','case','terminal_policy','fixed_fixture','fixed_plan','native_patch',
          'producer','sink','collector','schema_module','direct_primitive_wrapper','model_input_or_runtime_admitted','host_execution_ready'}
    if (type(value) is not dict or set(value)!=keys or value['schema']!='phase502-zero-king-observer-source-tuple/1'
            or value['model_input_or_runtime_admitted'] is not False or value['host_execution_ready'] is not False
            or value['case']!=CASE):
        raise ValueError('closed502 zeroKing tuple and historical false flags')
    if (value['profile'],value['observer_version'],value['terminal_policy']) != (OBSERVER_PROFILE,OBSERVER_VERSION,TERMINAL_POLICY):
        raise ValueError('exact502 profile/version/terminal')
    if (freeze['profile'],freeze['observer_version'],freeze['terminal_policy'],freeze['run_name']) != (OBSERVER_PROFILE,OBSERVER_VERSION,TERMINAL_POLICY,RUN_NAME):
        raise ValueError('host case/run/profile mismatch')
    declared=_payload_rows(freeze['files'])
    for key in ('fixed_fixture','fixed_plan','native_patch','producer','sink','collector','schema_module','direct_primitive_wrapper'):
        row=value[key]
        if declared.get(row['path'])!=row:raise ValueError('tuple leaf outside frozen graph')
        check_source_descriptor(root,row)
    for key in ('paths','artifacts','collector','schema_module','active_source_tuple','profile','observer_version','terminal_policy'):
        if key not in observer or freeze.get(key)!=observer[key]:raise ValueError('missing or mixed actual502 key '+key)
    if value['collector']!=freeze['collector'] or value['schema_module']!=freeze['schema_module']:
        raise ValueError('collector/schema tuple mismatch')
    for key,target in (('sink','native_random_observer_sink_v7.gd'),('direct_primitive_wrapper','Items/Exclusive/Squirrel.gd')):
        row=freeze['paths'][target]
        if value[key]!=dict(path=row['after_path'],**row['after']):raise ValueError('direct source-to-target mismatch')
    patch=read(check_source_descriptor(root,value['native_patch']))
    if patch != dict(schema='phase502-native-patch-source/1',paths=freeze['paths'],producer=value['producer'],sink=value['sink'],
                     profile=OBSERVER_PROFILE,observer_version=OBSERVER_VERSION,terminal_policy=TERMINAL_POLICY):
        raise ValueError('actual76 patch declaration mismatch')
    plan=read(check_source_descriptor(root,value['fixed_plan']))
    fixture=read(check_source_descriptor(root,value['fixed_fixture']))
    if (plan.get('fixture')!=fixture or plan.get('profile')!=OBSERVER_PROFILE or plan.get('version')!=OBSERVER_VERSION
            or plan.get('source_case')!='WHELP-FAMILY-A-502' or plan.get('native_case')!=CASE
            or len(plan.get('slots',[]))!=29 or fixture.get('below_master','MISSING') is not None):
        raise ValueError('exact proposed29 geometry; actual native branch not prefilled')
    roles={row['instance_id']:row['item_index'] for row in plan['slots']}
    if (set(roles)!={side+':'+str(n) for side,count in (('P',16),('O',13)) for n in range(count)}
            or set(roles.values())!={1,11,22,23,64,164,197,199,201} or 262 in roles.values()
            or roles.get('P:9')!=23 or roles.get('P:10')!=164 or roles.get('P:14')!=199):
        raise ValueError('fixed29 aliases/nine descriptors/zeroKing')
    if plan.get('config') != dict(schema='native-combat-capture/1',case_id=CASE,global_seed=50201,util_seed=50202,
                                 player_fixture_enabled=True,timeouts=dict(battle_seconds=120,total_seconds=295)):
        raise ValueError('Root preselected exact new seeds/config')
    if freeze.get('schema_case')!=plan['source_case'] or freeze.get('native_source_origin')!=SOURCE_AUTHORITY:
        raise ValueError('derived actual case/sourceauthority binding')
    if declared.get(SOURCE_AUTHORITY['path'])!=SOURCE_AUTHORITY:raise ValueError('sourceauthority outside graph')
    authority=read(check_source_descriptor(root,SOURCE_AUTHORITY))
    if (authority.get('schema')!='phase502-source-authority/1' or type(authority.get('origin')) is not dict
            or {authority['origin'][key]['path']:authority['origin'][key] for key in ('squirrel','sapphire')}!=ABSOLUTE_SOURCE_PINS):
        raise ValueError('exact502 two absolute sourceorigin authorities')
    return value


def load_terminal_schema(source_root, freeze):
    """Verify actual regular source bytes before executing this exact schema module."""
    import sys
    from types import ModuleType
    root = directory(source_root)
    validate_active_source_tuple(root, freeze)
    row = freeze['schema_module']
    path = check_source_descriptor(root, row)
    raw = path.read_bytes()
    if len(raw) != row['size'] or hashlib.sha256(raw).hexdigest() != row['sha256']:
        raise ValueError('schema changed between descriptor and read')
    name = '_phase508_terminal_schema_' + row['sha256']
    if name in sys.modules:
        raise ValueError('terminal schema already loaded; no cached foreign module')
    module = ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    try:
        exec(compile(raw, str(path), 'exec'), module.__dict__)
        if (module.VERSION, module.PROFILE, module.TERMINAL_POLICY) != (OBSERVER_VERSION, OBSERVER_PROFILE, TERMINAL_POLICY):
            raise ValueError('actual executed terminal module version')
        for api in ('validate_terminal_evidence', 'validate_terminal_receipt', 'validate_terminal_diagnostics'):
            if getattr(module.schema, api) is not getattr(module, api):
                raise ValueError('actual module export/delegate identity')
        return module
    finally:
        del sys.modules[name]


def read_terminal_expected_controls(source_root, freeze, capture):
    """Direct actual schema join; twelve lawful names remain unchanged, no model output."""
    module = load_terminal_schema(source_root, freeze)
    identities = {}
    def bounded(name, limit):
        path = member(capture, name)
        info = path.lstat()
        import stat
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > limit:
            raise ValueError('bounded ordinary expected/control leaf required: ' + name)
        raw = path.read_bytes()
        if len(raw) != info.st_size or len(raw) > limit:
            raise ValueError('control read size drift')
        identities[name] = dict(size=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        return raw.decode('utf-8')
    def obj(name, limit=1048576):
        value = module.strict_json_loads(bounded(name, limit))
        if type(value) is not dict:
            raise ValueError('actual expected/control object')
        return value
    def rows(name, limit, row_cap, row_bytes):
        text = bounded(name, limit)
        if not text.endswith('\n'):
            raise ValueError('complete physical JSONL newline required')
        lines = text.splitlines()
        if not 1 <= len(lines) <= row_cap or any(not line or len(line.encode('utf-8')) + 1 > row_bytes for line in lines):
            raise ValueError('bounded nonblank physical JSONL rows')
        return [module.strict_json_loads(line) for line in lines]
    endpoint = obj('king-capture-endpoint.json')
    receipt = obj('observer7-status.json')
    validation = obj('validation.json')
    header = obj('king-clock-checkpoint.json')
    module.exact(header, ('schema', 'lineage', 'environment', 'checkpoint'))
    passes = rows('king-clock-passes.jsonl', 67108864, module.MAX_PASSES, 1048576)
    clock = module.decode_clock(dict(header, passes=passes))
    diagnostics = rows('source-window-diagnostic.jsonl', 1048576, 64, 262144)
    control = module.schema.validate_terminal_diagnostics(diagnostics)
    proof = module.schema.validate_terminal_receipt(endpoint, clock, receipt, control, validation)
    if diagnostics[-1]['clock_passes'] != proof['passes']:
        raise ValueError('FINALIZED header/full actual clock mismatch')
    return dict(schema='phase391-host-terminal-control-proof/1', proof=proof, source_schema=freeze['schema_module'],
                source_tuple=freeze['active_source_tuple'], files=identities, expected_control_only=True,
                model_calls=0, input_bundle_created=False)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root',type=Path,required=True); parser.add_argument('--task-root',type=Path,required=True)
    parser.add_argument('--baseline',type=Path,required=True); parser.add_argument('--pool',type=Path,required=True)
    parser.add_argument('--runs-root',type=Path,required=True); parser.add_argument('--config',required=True)
    parser.add_argument('--config-size',type=int,required=True); parser.add_argument('--config-sha256',required=True)
    group=parser.add_mutually_exclusive_group(required=True);group.add_argument('--plan',action='store_true');group.add_argument('--execute',action='store_true')
    args=parser.parse_args(); value=dict(path=args.config,size=args.config_size,sha256=args.config_sha256)
    function=execute if args.execute else plan
    print(json.dumps(function(args.source_root,value,args.task_root,args.baseline,args.pool,args.runs_root),indent=2),flush=True)


if __name__=='__main__': main()
