"""One release-bound empty-project language attempt; no original Game command."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import os
import stat
import sys
import traceback
import types

R = Path(__file__).resolve().parents[1]
SD = R/'data/phase394-independent-launcher-source'
PREP = R/'data/phase394-independent-language-preparation'
RUN = R/'data/phase394-independent-language-first-001'
TASK = Path('/workspace/godotsteam-startup-20261013')
RELEASE_KEYS = {'schema','status','source_owner','entry','execution_contract','preparation_owner',
                'runtime_pins','project_files','output_directory','limits','permissions'}


def require(condition, message):
    if not condition: raise ValueError(message)


def strict_json(path):
    def pairs(rows):
        value={}
        for key,item in rows:
            require(key not in value,'duplicate JSON key')
            value[key]=item
        return value
    def invalid(value): raise ValueError('nonfinite JSON '+value)
    return json.loads(path.read_text(),object_pairs_hook=pairs,parse_constant=invalid)


def equal_typed(left,right):
    if type(left) is not type(right): return False
    if type(left) is dict:
        return left.keys()==right.keys() and all(equal_typed(left[k],right[k]) for k in left)
    if type(left) is list:
        return len(left)==len(right) and all(equal_typed(a,b) for a,b in zip(left,right))
    return left==right


def member(name):
    require(type(name) is str and name and '\\' not in name and '\x00' not in name,'relative path string')
    pure=PurePosixPath(name)
    require(not pure.is_absolute() and pure.as_posix()==name and all(x not in ('','.','..') for x in name.split('/')),'canonical repo-relative path')
    return R/name


def identity(path):
    raw=path.read_bytes()
    return dict(size=len(raw),sha256=hashlib.sha256(raw).hexdigest())


def descriptor(path): return dict(path=str(path.relative_to(R)),**identity(path))


def verify(row,external=False):
    require(type(row) is dict and set(row)=={'path','size','sha256'},'closed descriptor')
    require(type(row['size']) is int and row['size']>=0,'descriptor size strictINT')
    digest=row['sha256']
    require(type(digest) is str and len(digest)==64 and all(c in '0123456789abcdef' for c in digest),'descriptor SHA')
    path=Path(row['path']) if external else member(row['path'])
    require(path.is_absolute(),'absolute resolved source root')
    require(not any(p.is_symlink() for p in (path,*path.parents)),'linked source/runtime path')
    info=path.lstat()
    require(stat.S_ISREG(info.st_mode) and info.st_nlink==1,'ordinary single-link source/runtime leaf')
    require(equal_typed(identity(path),{k:row[k] for k in ('size','sha256')}),'actual descriptor mismatch: '+str(path))
    return path


def write_new(path,value):
    with path.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')
        stream.flush();os.fsync(stream.fileno())


def source_gate(args):
    release_row=dict(path=args.release,size=args.release_size,sha256=args.release_sha256)
    release=strict_json(verify(release_row))
    require(type(release) is dict and set(release)==RELEASE_KEYS,'closed Root language release')
    require(release['schema']=='phase394-root-language-release/1' and release['status']=='ROOT394_ONE_EMPTY_PROJECT_LANGUAGE_RELEASED','actual Root language status')
    owner_row=dict(path=str((SD/'owned-files.json').relative_to(R)),size=args.source_owner_size,sha256=args.source_owner_sha256)
    require(equal_typed(release['source_owner'],owner_row),'Root/exact CLI source-owner pin')
    owner=strict_json(verify(owner_row))
    require(type(owner.get('files')) is list and owner['files'],'actual source-owner list')
    owned={}
    for row in owner['files']:
        verify(row);require(row['path'] not in owned,'duplicate source-owner leaf');owned[row['path']]=row
    contract_path=SD/'execution-contract.json'
    contract_row=descriptor(contract_path)
    require(owned.get(contract_row['path'])==contract_row,'actual contract owner coverage')
    contract=strict_json(contract_path)
    own_entry=descriptor(Path(__file__))
    require(equal_typed(release['entry'],own_entry) and owned.get(own_entry['path'])==own_entry,'actual launcher owner/Root binding')
    require(equal_typed(release['execution_contract'],contract_row),'Root execution contract pin')
    require(equal_typed(release['preparation_owner'],contract['preparation_owner']),'Root preparation owner pin')
    prep_owner_path=verify(contract['preparation_owner'])
    require(owned.get(str(prep_owner_path.relative_to(R)))==contract['preparation_owner'],'preparation owner owned')
    for row in strict_json(prep_owner_path)['files']:
        require(owned.get(row['path'])==row,'full preparation SOURCE ownership');verify(row)
    for key in ('runtime_pins','project_files','limits','permissions','output_directory'):
        require(equal_typed(release[key],contract[key]),'Root exact contracted '+key)
    require(contract['output_directory']==str(RUN.relative_to(R)),'fixed unique destination')
    require(len(contract['project_files'])==4 and {Path(r['path']).name for r in contract['project_files']}=={'project.godot','probe.gd','full-sink.gd','full-collector.gd'},'four exact project sources')
    for row in contract['project_files']:
        require(owned.get(row['path'])==row and member(row['path']).parent==PREP/'project','owned immutable project source');verify(row)
    for row in contract['runtime_pins']:verify(row,external=True)
    require(contract['runtime_pins'][0]['sha256']=='09d1de6c4f97289c018556666c13c1d81093a5df5c2255725d464a87f40a8ea1','exact GodotSteam3.6.2')
    for row in contract['monitor_sources'].values():
        require(owned.get(row['path'])==row,'exact inherited monitor dependency owned');verify(row)
    return release_row,contract,owner_row,owner


def load_source(name,row):
    path=verify(row)
    module=types.ModuleType(name);module.__file__=str(path);sys.modules[name]=module
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    return module


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute',action='store_true',required=True)
    parser.add_argument('--release',required=True)
    parser.add_argument('--release-size',type=int,required=True)
    parser.add_argument('--release-sha256',required=True)
    parser.add_argument('--source-owner-size',type=int,required=True)
    parser.add_argument('--source-owner-sha256',required=True)
    args=parser.parse_args()
    release_row,contract,owner_row,owner=source_gate(args)
    # Nothing is created and no SUT/monitor imported before all exact Root gates pass.
    require(not RUN.exists() and not RUN.is_symlink(),'unique attempt destination already used')
    RUN.mkdir(exist_ok=False)
    project=RUN/'project';project.mkdir();output=RUN/'output';output.mkdir()
    for name in ('home','data','config','cache','run','tmp'):
        (RUN/'user'/name).mkdir(parents=True,mode=0o700)
    monitor_result=None;failure=None;attempts=0;definition_imports=0;copied=[];scan_gaps=0
    parent_environment=dict(os.environ)
    try:
        for row in contract['project_files']:
            source=verify(row);dest=project/source.name
            with dest.open('xb') as stream:stream.write(source.read_bytes())
            require(identity(dest)=={k:row[k] for k in ('size','sha256')},'exclusive project-copy readback')
            copied.append(dict(source=row,copy=descriptor(dest)))
        load_source('native_run_compaction',contract['monitor_sources']['compaction']);definition_imports+=1
        load_source('phase363_oracle_storage',contract['monitor_sources']['storage']);definition_imports+=1
        monitor=load_source('_phase394_exact_generic_monitor',contract['monitor_sources']['process']);definition_imports+=1
        env=monitor.environment(TASK,RUN)
        env['HOME']=str(RUN/'user/home')
        require(equal_typed(dict(os.environ),parent_environment),'parent env unexpectedly modified')
        runtime={Path(row['path']).name:row for row in contract['runtime_pins']}
        command=[sys.executable,runtime['godotsteam_offline_exec.py']['path'],runtime['xvfb-run']['path'],'-a','-s','-screen 0 640x480x24 -nolisten tcp','-e',str(output/'xvfb.log'),runtime['godotsteam.362.editor.x86_64']['path'],'--path',str(project),'--audio-driver','Dummy','--time-scale','1.0','--script','res://probe.gd']
        write_new(RUN/'before-launch.json',dict(schema='phase394-before-language-launch/1',release=release_row,source_owner=owner_row,command=command,project_copies=copied,child_user_paths={key:env[key] for key in ('HOME','XDG_DATA_HOME','XDG_CONFIG_HOME','XDG_CACHE_HOME','XDG_RUNTIME_DIR','TMPDIR')},parent_environment_unchanged=True,scope='EMPTY_PROJECT_PRIMITIVE_TRACKER_LANGUAGE_UNIT_NOT_GAME'))
        def scan():
            nonlocal scan_gaps
            total=0;entries=0
            for path in RUN.rglob('*'):
                try:info=path.lstat()
                except FileNotFoundError:
                    scan_gaps+=1;continue
                entries+=1
                if stat.S_ISLNK(info.st_mode) or not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)):
                    raise ValueError('unsupported/linked owned runtime leaf')
                if path.name=='native-capture' and stat.S_ISDIR(info.st_mode):
                    raise ValueError('unexpected production native-capture directory')
                if stat.S_ISREG(info.st_mode):total+=info.st_size
            if total>contract['limits']['owned_bytes'] or entries>contract['limits']['owned_entries']:
                raise ValueError('owned language size/entry threshold')
            return dict(bytes=total,entries=entries,disappearing_temp_paths=scan_gaps)
        scan()
        attempts=1
        monitor_result=monitor.monitor_command(command,RUN,env,output,'language',contract['limits']['wall_seconds'],scan_callback=scan,poll_seconds=contract['limits']['poll_seconds'],term_grace_seconds=contract['limits']['term_grace_seconds'],kill_grace_seconds=contract['limits']['kill_grace_seconds'],log_limit_bytes=contract['limits']['log_bytes'],abort_markers=('SCRIPT ERROR:',))
        scan()
    except BaseException as exc:
        failure=dict(error=repr(exc),traceback=traceback.format_exc())
    drift=[]
    for row in owner['files']:
        try:verify(row)
        except Exception as exc:drift.append(dict(path=row['path'],error=repr(exc)))
    for row in copied:
        try:require(identity(member(row['copy']['path']))=={k:row['copy'][k] for k in ('size','sha256')},'copy drift')
        except Exception as exc:drift.append(dict(path=row['copy']['path'],error=repr(exc)))
    for row in contract['runtime_pins']:
        try:verify(row,external=True)
        except Exception as exc:drift.append(dict(path=row['path'],error=repr(exc)))
    env_unchanged=equal_typed(dict(os.environ),parent_environment)
    report_path=project/'language-report.json'
    report_present=report_path.is_file() and not report_path.is_symlink()
    receipt=dict(schema='phase394-actual-language-execution/1',release=release_row,source_owner=owner_row,monitor=monitor_result,launcher_failure=failure,source_drift=drift,parent_environment_unchanged=env_unchanged,
        generic_monitor_calls=attempts,Godot_language_launches_requested=attempts,Godot_language_processes_observed=1 if monitor_result is not None else (0 if attempts==0 else None),SOURCE_definition_imports=definition_imports,
        detached_sink_instances='READ_ONLY_AFTER_RAW_SEAL',actual_Game=0,native_battles=0,models=0,RNG_calls_requested=0,FrameDriver=0,actualpool=0,projection=0,restore=0,READY=0,
        report_present=report_present,first_exit=None if monitor_result is None else monitor_result['exit_code'],automatic_retry=False,scan_disappearing_temp_paths=scan_gaps,
        process_group_scope='Leader/process_clean_exit distinct from actual live_remaining/zombies_not_claimed_reaped; no reaping claim inferred',enforcement='POLLING_NOT_KERNEL_AGGREGATE_QUOTA; explicit owned roots, not kernel filesystem closure')
    write_new(RUN/'execution-receipt.json',receipt)
    raw=[];unsupported=[]
    for path in sorted(RUN.rglob('*')):
        info=path.lstat()
        if stat.S_ISREG(info.st_mode) and info.st_nlink==1:
            raw.append(descriptor(path))
        elif not stat.S_ISDIR(info.st_mode):
            unsupported.append(dict(path=str(path.relative_to(RUN)),mode=info.st_mode,nlink=info.st_nlink,link_target=os.readlink(path) if stat.S_ISLNK(info.st_mode) else None))
    write_new(RUN/'raw-joint-seal.json',dict(schema='phase394-language-first-raw-joint-seal/1',files=raw,unsupported_leaves=unsupported,report_present=report_present,semantics_interpreted=False))
    # Interpretation is exclusively after raw receipt/log/report jointseal.
    report=None;interpret_error=None
    try:
        if report_present:report=strict_json(report_path)
        require(report is not None,'missing report / script parse or early failure')
        require(monitor_result is not None and monitor_result['exit_code']==0 and monitor_result['abort_reason'] is None and monitor_result['timed_out'] is False,'actual monitor/leader failure')
        require(failure is None and not drift and not unsupported and env_unchanged,'launcher/source/env/ordinary-output failure')
        require(report.get('completed') is True and report.get('failure') is None,'first actual language case failure')
        loads=report['resource_loads'];require(type(loads) is list and len(loads)==2,'two complete resource loads')
        require([(r['file'],r['base']) for r in loads]==[('full-collector.gd','SceneTree'),('full-sink.gd','Node')],'actual script base identities')
        require(all(r['loaded'] is True and r['can_instance'] is True for r in loads),'actual parse/load')
        require([r['label'] for r in report['cases']]==contract['unit_ids'] and all(r.get('pass') is True for r in report['cases']),'six fixed actual units')
        for key,value in contract['expected_report_counters'].items():
            require(equal_typed(report.get(key),value),'actual report type/count '+key)
    except Exception as exc:interpret_error=repr(exc)
    passed=interpret_error is None
    interpretation=dict(schema='phase394-independent-language-interpretation/1',status='PASS_BOUNDED_LANGUAGE_COMPONENT' if passed else 'FIRST_LANGUAGE_FAILURE_STOPPED',execution_receipt=descriptor(RUN/'execution-receipt.json'),raw_jointseal=descriptor(RUN/'raw-joint-seal.json'),report=None if not report_present else descriptor(report_path),failure=interpret_error,
        actual_resource_loads=None if report is None else len(report.get('resource_loads',[])),actual_unit_cases=None if report is None else len(report.get('cases',[])),actual_SUT_direct_calls=None if report is None else report.get('SUT_direct_method_calls'),detached_sink_instances=None if report is None else report.get('detached_sink_instances'),
        actual_Game=0,native=0,models=0,actual12_positive=False,wholeproducer_or_collector_positive=False,actual_clock_signal_schedule=False,fullsnapshot=False,activationdeath=False,King_admission=False)
    write_new(RUN/'interpretation.json',interpretation)
    leaves=[descriptor(p) for p in sorted(RUN.rglob('*')) if stat.S_ISREG(p.lstat().st_mode) and p.lstat().st_nlink==1]
    write_new(RUN/'owned-files.json',dict(schema='phase394-language-output-owner/1',files=leaves,unsupported_leaves=unsupported,scope='Ordinary leaves of owned new execution copy and actual first-run outputs; any unsafe shape is explicitly recorded, not followed; preparation sources unmodified'))
    for row in leaves:verify(row)
    print(json.dumps(dict(status=interpretation['status'],failure=interpret_error,execution=descriptor(RUN/'execution-receipt.json'),owner=descriptor(RUN/'owned-files.json')),indent=2))
    return 0 if passed else 1


if __name__=='__main__':raise SystemExit(main())
