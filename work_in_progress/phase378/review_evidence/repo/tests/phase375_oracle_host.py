"""Explicit-path fixed original027 oracle host. No model/projection/admission code."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
from phase363_oracle_storage import (directory,member,pin,read,write_new,sync,budget,check_ready,lease,
                                     reset_previous,install,archive_streaming,c)
from phase363_oracle_process import execute_process,rename_capture,usage

SOURCE = 'data/phase375-food-hook-source'
DATA = 'data/phase362-oracle-capture-source'
CASE = 'NATIVE-027-KING-A'
RUN_NAME = 'original027-king-single-A-20261025-attempt04'
REVIEW_STATUS = 'INDEPENDENT375_FOOD_HOOK_SOURCE_REPAIR_ACCEPTED_ROOT_PENDING'
POLICY = 'bounded-writers-and-monitored-process/1'
NAMES = ('custom_player.json','custom_opponent.json','native_capture_config.json')
LAWFUL = ('fixture.json','player_fixture.json','observer7-input.jsonl','observer7-lineage.jsonl',
          'observer7-metadata.jsonl','observer7-primitives.jsonl','king-clock-checkpoint.json',
          'king-clock-passes.jsonl','king-input-facts.json','king-ui-authority.jsonl',
          'king-rng-checkpoint.json','king-slot-bindings.json')


def descriptor(source_root,row):
    if type(row) is not dict or set(row)!={'path','size','sha256'} or type(row['size']) is not int or row['size']<0 or not re.fullmatch('[0-9a-f]{64}',row['sha256']):
        raise ValueError('exact relative descriptor')
    path=member(source_root,row['path'])
    if not path.is_file() or pin(path)!={k:row[k] for k in ('size','sha256')}: raise ValueError('actual descriptor drift')
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


def source_gate(source_root,config_descriptor):
    root=directory(source_root); config_path=descriptor(root,config_descriptor); config=read(config_path)
    if config.get('schema')!='phase375-root-oracle-acceptance/1' or config.get('root_oracle_authorized') is not True:
        raise ValueError('actual root oracle-only authorization required')
    if any(type(config.get(k)) is not int or config[k]!=0 for k in ('models_allowed','input_builds_allowed','expected_comparison_allowed')):
        raise ValueError('strictINT0 model/inputbuild/expected permissions')
    if config.get('write_policy')!=POLICY: raise ValueError('exact root monitored-writes policy')
    freeze_path=descriptor(root,config['source_freeze'])
    if str(freeze_path.relative_to(root))!=SOURCE+'/combined-source-freeze.json': raise ValueError('exact362 SOURCE freeze')
    freeze=read(freeze_path)
    for row in freeze['files']: descriptor(root,row)
    leaves=verify_owner(root,config['source_owner'])
    if leaves.get(str(Path(__file__).relative_to(root)))!=pin(Path(__file__)) or leaves.get(config['source_freeze']['path'])!=pin(freeze_path):
        raise ValueError('owner must actually cover host and freeze')
    reviews=config.get('reviews')
    if type(reviews) is not list or not reviews: raise ValueError('real independent SOURCE reviews required')
    for review in reviews:
        receipt=descriptor(root,review['receipt']); owned=verify_owner(root,review['owner']); result=read(receipt)
        if owned.get(review['receipt']['path'])!=pin(receipt) or result.get('status')!=REVIEW_STATUS:
            raise ValueError('actual owned independent362 SOURCE status')
        if result.get('source_freeze')!=config['source_freeze'] or any(type(result.get(k)) is not int or result[k]!=0 for k in ('native','models')):
            raise ValueError('actual reviewed closure and zero execution')
    for row in freeze['accepted_source_controls']: descriptor(root,row)
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
    previous=check_ready(paths['pool'],paths['baseline'],config['relocations'])
    capacity=budget(paths['pool'],paths['runs_root'])
    run=paths['runs_root']/RUN_NAME
    if run.exists(): raise ValueError('fixed unique attempt path already exists')
    native_config=read(member(root,DATA+'/case-A/native_capture_config.json'))
    if native_config!=dict(schema='native-combat-capture/1',case_id=CASE,global_seed=35301,util_seed=35302,
                          player_fixture_enabled=True,timeouts=dict(battle_seconds=120,total_seconds=295)):
        raise ValueError('fixed SOURCE config/seeds/timeouts')
    return dict(schema='phase362-oracle-readonly-plan/1',paths={k:str(v) for k,v in paths.items()},source_root=str(root),
        run=str(run),case_id=CASE,attempt=4,previous_run=str(previous),budget=capacity,
        root_config=config_descriptor,freeze=config['source_freeze'],source_owner=config['source_owner'],
        reviews=config['reviews'],config=native_config,policy=POLICY,
        oracle_processes=0,models=0,projection_calls=0,Game_copies=0,
        source_profile=freeze['profile'],schema_case=freeze['schema_case'],native_scope='FIXED_A_SINGLE_KING_ORACLE_ONLY')


def execute(source_root,config_descriptor,task_root,baseline,pool,runs_root):
    launch=plan(source_root,config_descriptor,task_root,baseline,pool,runs_root)
    root,config,freeze=source_gate(source_root,config_descriptor)
    paths={key:Path(value) for key,value in launch['paths'].items()}
    with lease(paths['pool'],paths['baseline'],paths['runs_root'],RUN_NAME,config['relocations']) as (previous,run):
        run.mkdir(); (run/'output').mkdir(); (run/'output/driver').mkdir(); (run/'data').mkdir()
        for name in ('data','config','cache','run','tmp'): (run/'user'/name).mkdir(parents=True,mode=0o700)
        out=run/'output'; project=paths['pool']/'project'
        write_new(out/'readonly-plan.json',launch)
        reset=reset_previous(project,paths['baseline'],previous,out/'previous-source-preimages')
        write_new(out/'prior-observer-reset.json',reset)
        data=member(root,DATA+'/case-A')
        for name in NAMES:
            shutil.copy2(data/name,run/'data'/name)
        artifacts={'native_combat_capture.gd':member(root,SOURCE+'/collector.gd'),
                   'native_capture_config.json':data/NAMES[2],'.native-random-observer-disposable':member(root,DATA+'/disposable-marker.txt')}
        journal=install(root,project,freeze,artifacts,out/'source-preimages')
        for name in NAMES[:2]: shutil.copy2(run/'data'/name,paths['pool']/'data'/name)
        report=dict(schema='observer7-patch/1',patch_version='phase362-oracle-single-King',added_files=['native_random_observer_sink_v7.gd'],
                    patches=[dict(path=name,before_size=None if row['before'] is None else row['before']['size'],
                        before_sha256=None if row['before'] is None else row['before']['sha256'],
                        after_size=row['after']['size'],after_sha256=row['after']['sha256']) for name,row in freeze['paths'].items()])
        (out/'observer-patch').mkdir(); write_new(out/'observer-patch/native_random_observer_patch_manifest.json',report)
        write_new(out/'host_manifest.json',dict(schema='phase362-oracle-host/1',case_id=CASE,
            audited_runtime_observation_patch=report,source_freeze=config['source_freeze'],collector=pin(artifacts['native_combat_capture.gd']),models=0))
        # Archive the exact SOURCE actually used before any Godot command.
        source_owned=read(descriptor(root,config['source_owner']))['files']
        copies=[row for row in freeze['files']]+source_owned+[config_descriptor,config['source_owner'],config['source_freeze']]
        for review in config['reviews']: copies += [review['receipt'],review['owner']]
        copies=list({row['path']:row for row in copies}.values())
        saved=[]
        for index,row in enumerate(copies):
            source=descriptor(root,row); target=out/'driver'/str(index)
            shutil.copy2(source,target)
            if pin(target)!=pin(source): raise ValueError('driver SOURCE readback')
            saved.append(dict(file=target.name,source=row))
        write_new(out/'driver/source-map.json',dict(files=saved))
        write_new(out/'pool-provenance.json',dict(schema='phase362-explicit-pool-provenance/1',plan=launch,
            installed_preimages=journal,driver_sha256={p.name:c.digest(p) for p in (out/'driver').iterdir()},
            inputs={name:pin(run/'data'/name) for name in NAMES},full_game_copy=False))
        before=dict(baseline=c.inventory(paths['baseline']),project=c.inventory(project),staged=c.inventory(paths['pool']/'data'))
        write_new(out/'pool-before.json',before)
        parsed=execute_process(root,paths['task_root'],run,project,check_only=True)
        if not parsed['process_clean_exit'] or parsed['abort_reason']: raise RuntimeError('check-only failed; no native start')
        if c.inventory(project)!=before['project']: raise ValueError('parse-only changed project tree')
        if descriptor(root,config_descriptor)!=descriptor(root,launch['root_config']): raise ValueError('config drift')
        # Preserve the same config identity, no second dynamic plan after mutation.
        source_gate(root,config_descriptor); resource_gate(root,config,paths); usage(run)
        write_new(out/'one-shot-launch.json',dict(case_id=CASE,attempt=4,models=0,timeout=dict(battle=120,collector=295,runner=300)))
        result=execute_process(root,paths['task_root'],run,project,check_only=False)
        write_new(out/'process-returned.json',result)
        partition=collect_capture_metadata(run,result)
        project_changed=c.inventory(project)!=before['project']
        complete=partition['capture_complete'] and not project_changed
        write_new(out/'source-partition.json',partition)
        write_new(out/'process_result.json',dict(result,capture_complete=complete,
            primary_failure=partition['primary_failure'],secondary_errors=partition['secondary_errors'],
            source_changes_after_run=['PROJECT_TREE_CHANGED'] if project_changed else [],
            process_clean_exit=result['process_clean_exit'],model_acceptance=False,automatic_retry=False))
        if not complete: raise RuntimeError('first original027 failed/partial; preserve, no retry')
        proof=archive_streaming(paths['baseline'],paths['pool'],run,before)
        # No write after READY: retained run identity remains stable.
        return dict(status='ORACLE_CAPTURE_ARCHIVED_MODELS_AND_FULLPROJECTION_PENDING',run=str(run),proof=proof,
                    process_clean_exit=result['process_clean_exit'],models=0,inputbuilds=0,King_production_admitted=False)



def read_control(path,limit):
    if pin(path)['size']>limit: raise ValueError('bounded control JSON exceeded cap')
    value=read(path)
    if type(value) is not dict: raise ValueError('control JSON must be object')
    return value


def collect_capture_metadata(run,result):
    """Decode controls only; business/expected observations remain opaque hashes."""
    secondary=[]; primary=None; capture=None; present={}; expected={}; validation=None; partial={}; control_files={}
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
    complete=process_ok and primary is None and not missing and validation is not None and validation.get('native_checks_pass') is True and not secondary
    return dict(schema='phase365-partial-source-partition/1',capture_complete=complete,
        capture=None if capture is None else str(capture),lawful_inputs_present=present,lawful_inputs_missing=missing,
        expected_observations_opaque=expected,control_failures_opaque=control_files,partial_files_opaque=partial,primary_failure=primary,secondary_errors=secondary,
        expected_semantics_read=False,models=0,projection=0)


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
