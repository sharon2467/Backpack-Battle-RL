"""Presealed first365 SOURCE units; exactly one empty-project language process."""
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import traceback
import types

R=Path(__file__).resolve().parents[1]
D=R/'data/phase365-independent-source-review'
OUT=D/'first-001'
COUNTS=dict(SOURCE_module_imports=0,language_processes=0,new_config_calls=0,host_calls=0,recovery_calls=0,
            actual_Game=0,native=0,models=0,actual_pool_changes=0,actual_READY_commits=0)

def pin(path):
    b=Path(path).read_bytes();return dict(size=len(b),sha256=hashlib.sha256(b).hexdigest())
def save(path,value):
    with Path(path).open('x') as stream: json.dump(value,stream,indent=2,sort_keys=True,allow_nan=False);stream.write('\n')
def load(name,path):
    value=types.ModuleType(name);value.__file__=str(path);sys.modules[name]=value
    exec(compile(path.read_bytes(),str(path),'exec'),value.__dict__);COUNTS['SOURCE_module_imports']+=1;return value
def rejection(function):
    try: function()
    except (ValueError,KeyError,FileNotFoundError,RuntimeError) as exc:return dict(type=type(exc).__name__,message=str(exc))
    raise AssertionError('unexpected acceptance')
def call(function,*args,**kwargs):
    COUNTS['recovery_calls']+=1;return function(*args,**kwargs)
def restore_times(root,manifest):
    for row in sorted(manifest['entries'],key=lambda r:len(Path(r['path']).parts),reverse=True):
        p=root/row['path'];os.chmod(p,row['mode']);os.utime(p,ns=(row['mtime_ns'],row['mtime_ns']))

def run_language(monitor):
    run=OUT/'language';run.mkdir();(run/'output').mkdir()
    for name in ('data','config','cache','run','tmp'):(run/'user'/name).mkdir(parents=True,mode=0o700)
    project=D/'language-project';before={p.name:pin(p) for p in project.iterdir() if p.is_file()}
    assert 'regression-report.json' not in before
    task=Path('/workspace/godotsteam-startup-20261013')
    command=[sys.executable,str(R/'tests/godotsteam_offline_exec.py'),str(task/'debian/usr/bin/xvfb-run'),'-a','-s',
        '-screen 0 640x480x24 -nolisten tcp','-e',str(run/'output/xvfb.log'),str(task/'engine/godotsteam.362.editor.x86_64'),
        '--path',str(project),'--audio-driver','Dummy','--time-scale','1.0','--script','res://probe.gd']
    save(run/'before.json',dict(command=command,sources=before,scope='EMPTY_PROJECT_EXACT_SOURCE_UNIT_NO_GAME'))
    def scan():
        paths=list(run.rglob('*'));assert not any(p.is_symlink() for p in paths)
        size=sum(p.stat().st_size for p in paths if p.is_file());assert size<16*1024**2 and len(paths)<512
        return dict(bytes=size,entries=len(paths))
    COUNTS['language_processes']+=1
    result=monitor.monitor_command(command,run,monitor.environment(task,run),run/'output','language',18.,
        scan_callback=scan,poll_seconds=.05,term_grace_seconds=.2,kill_grace_seconds=.5,log_limit_bytes=2*1024**2)
    save(run/'execution.json',dict(monitor=result,Godot_language_processes=1,actual_Game=0,native_battles=0,
        models=0,callee_plain_Node_instances=1,automatic_retry=False,child_filesystem_kernel_sandbox=False))
    report_path=project/'regression-report.json'
    leaves=[p for p in run.rglob('*') if p.is_file()]
    if report_path.exists(): leaves.append(report_path)
    save(run/'joint-seal.json',dict(files=[dict(path=str(p.relative_to(R)),**pin(p)) for p in sorted(leaves)]))
    assert result['exit_code']==0 and not result['timed_out'] and result['abort_reason'] is None
    assert {name:pin(project/name) for name in before}==before
    report=json.loads(report_path.read_text())
    assert not report['failures'] and len(report['cases'])==14
    assert report['new_config_top_level_calls']==14 and report['old_original_BOOL_result'] is False
    assert report['old_original_full_config_result'] is False and report['autoloads']==[] and not report['Game_node_present']
    COUNTS['new_config_calls']=14
    return report

def main():
    contract=json.loads((D/'execution-contract.json').read_text())
    for row in contract['files']:assert pin(R/row['path'])=={k:row[k] for k in ('size','sha256')}
    for row in contract['runtime_pins']:assert pin(Path(row['path']))=={k:row[k] for k in ('size','sha256')}
    OUT.mkdir();rows=[];error=None
    def record(number,evidence):
        row=dict(id=number,label=contract['cases'][number-1]['label'],status='PASS',evidence=evidence)
        save(OUT/('case-%02d.json'%number),row);rows.append(row)
    try:
        c=load('native_run_compaction',D/'SOURCE/compaction.py')
        storage=load('phase363_oracle_storage',D/'SOURCE/storage.py')
        monitor=load('phase363_oracle_process',D/'SOURCE/process.py')
        host=load('phase365_oracle_host',D/'SOURCE/host.py')
        rec=load('__independent365_recovery__',D/'SOURCE/recovery.py')
        fixture=load('__independent365_tiny_evidence__',R/'tests/phase365_independent_tiny_evidence.py')
        language=run_language(monitor)
        for row in language['cases']:
            assert row['pass'] and row['actual'] is row['expected'] and row['unchanged'];record(row['id'],row)
        # Tiny control DTO directories only. No actual observation rows or completion markers.
        for number in range(15,22):
            run=OUT/('host-%02d'%number);cap=run/'output/capture';cap.mkdir(parents=True)
            result=dict(exit_code=2,abort_reason=None,timed_out=False,process_clean_exit=False)
            if number in (15,16):save(cap/'collector-first-failure.json',dict(code='fixed config differs',stage='startup',capture_complete=False))
            if number in (16,17):(cap/'validation.json').write_bytes(b'INVALID_CONTROL_JSON')
            if number==18:save(cap/'validation.json',dict(native_checks_pass=True,synthetic_negative_only=True));result['exit_code']=0
            if number==19:(cap/'collector-first-failure.json').write_bytes(b'INVALID_CONTROL_JSON')
            if number==20:result.update(exit_code=0,abort_reason='UNIT_ABORT',timed_out=True)
            if number==21:
                cap.rmdir();(run/'user').mkdir();(run/'user/partial-unit.bin').write_bytes(b'\xff\x00OPAQUE_PARTIAL')
            else:(cap/'opaque-unit.bin').write_bytes(b'\xff\x00BUSINESS_BYTES_MUST_NOT_BE_JSON_DECODED')
            COUNTS['host_calls']+=1;value=host.collect_capture_metadata(run,result)
            assert value['capture_complete'] is False and value['expected_semantics_read'] is False
            assert len(value['lawful_inputs_missing'])==12
            if number in (15,16): assert value['primary_failure']['kind']=='collector_control_failure'
            if number in (17,18,20): assert (value['primary_failure'] is None)==(number==18)
            if number==19:assert value['primary_failure']['kind']=='invalid_collector_control_failure'
            if number==21:assert 'user/partial-unit.bin' in value['partial_files_opaque']
            if number==20:assert value['primary_failure']==dict(kind='native_process_failure',exit_code=0,abort_reason='UNIT_ABORT',timed_out=True)
            record(number,dict(scope='SYNTHETIC_CONTROL_METADATA_ONLY',partition=value,source_changes_gate='SOURCE execute uses partition.capture_complete and not project_changed; clean is separately retained'))
        f=fixture.create(OUT/'neutral-fixture',c,rec,save,pin);roots=f['roots'];mapping=f['mapping'];pins=f['pins']
        evidence=call(rec.verify_evidence,roots,mapping,pins)
        failed_before=c.inventory(roots['pool']/'project');data_before=c.inventory(roots['pool']/'data');state_before=pin(roots['pool']/'state.json')
        def unchanged():
            assert c.inventory(roots['pool']/'project')==failed_before and c.inventory(roots['pool']/'data')==data_before
            assert pin(roots['pool']/'state.json')==state_before
        def preflight(m=None,p=None):return call(rec.verify_evidence,roots,m or mapping,p or pins)
        target=roots['pool']/'project'/mapping['file_differences'][0]['path']
        original=target.read_bytes();target.write_bytes(b'WRONG_BEFORE')
        record(22,rejection(lambda:call(rec.restore_exact,roots,evidence,OUT/'must-not-exist22',f['binding'])))
        target.write_bytes(original);restore_times(roots['pool']/'project',failed_before);unchanged();assert not(OUT/'must-not-exist22').exists()
        for number,index in ((23,0),(24,1)):
            m=copy.deepcopy(mapping);m['file_differences'][index]['payload']['path']='payloads/MISSING_NEUTRAL_UNIT'
            record(number,dict(scope='Neutral payload counterpart; actual old sink/marker identity covered by frozen SOURCE map',rejection=rejection(lambda:preflight(m))));unchanged()
        m=copy.deepcopy(mapping);m['staged_files'][1]['payload']['path']='output/compaction/inputs/MISSING'
        record(25,rejection(lambda:preflight(m)));unchanged()
        m=copy.deepcopy(mapping);m['file_differences'][0]['payload']['sha256']='0'*64
        record(26,rejection(lambda:preflight(m)));unchanged()
        m=copy.deepcopy(mapping);m['file_differences'][0]['payload']['path']='../escape'
        path_reject=rejection(lambda:preflight(m))
        bad=copy.deepcopy(evidence['target']);bad['entries'].append(copy.deepcopy(bad['entries'][1]))
        record(27,dict(path=path_reject,duplicate=rejection(lambda:c.index(bad))));unchanged()
        payload=roots['failed_run']/mapping['file_differences'][0]['payload']['path'];alias=payload.with_name('unit-hardlink')
        os.link(payload,alias);rj=rejection(preflight);alias.unlink()
        alias.symlink_to(payload);symlink=rejection(lambda:call(rec.evidence_path,roots,dict(root='failed_run',path=alias.relative_to(roots['failed_run']).as_posix(),**pin(payload))))
        alias.unlink();record(28,dict(hardlink=rj,symlink=symlink));unchanged()
        before_stat=target.stat();os.chmod(target,0o644)
        rj=rejection(lambda:call(rec.restore_exact,roots,evidence,OUT/'must-not-exist29',f['binding']))
        os.chmod(target,stat.S_IMODE(before_stat.st_mode));os.utime(target,ns=(before_stat.st_atime_ns,before_stat.st_mtime_ns))
        record(29,rj);unchanged()
        extra=roots['pool']/'project/unknown-unit.txt';extra.write_bytes(b'UNKNOWN')
        rj=rejection(lambda:call(rec.restore_exact,roots,evidence,OUT/'must-not-exist30',f['binding']));extra.unlink()
        restore_times(roots['pool']/'project',failed_before);record(30,rj);unchanged()
        bp=roots['baseline']/mapping['file_differences'][0]['path'];raw=bp.read_bytes();bp.write_bytes(b'DRIFT')
        rj=rejection(preflight);bp.write_bytes(raw);restore_times(roots['baseline'],f['baseline'])
        record(31,rj);unchanged()
        restored=call(rec.restore_exact,roots,evidence,OUT/'tiny-restore',f['binding'])
        assert restored['writes']==80 and restored['READY_committed'] is False
        assert json.loads((roots['pool']/'state.json').read_text())['status']=='failed'
        actual=call(rec.actual_targets,roots,evidence)
        assert c.inventory(roots['baseline'])==f['baseline'] and c.retained(roots['previous_run'])==f['previous']
        record(32,dict(scope='SYNTHETIC_FS_78_FILES_7_DIRS_2_DATA',receipt=restored,actual=actual,state_identity_unchanged=pin(roots['pool']/'state.json')==state_before))
        ff=fixture.create(OUT/'neutral-fault-fixture',c,rec,save,pin)
        ev=call(rec.verify_evidence,ff['roots'],ff['mapping'],ff['pins']);faultpayload=ev['payloads'][1][2]
        faultpayload.write_bytes(b'CHANGED_AFTER_VALID_PREFLIGHT')
        rj=rejection(lambda:call(rec.restore_exact,ff['roots'],ev,OUT/'tiny-partial',ff['binding']))
        partial=json.loads((OUT/'tiny-partial/restore-first-failure.json').read_text())
        assert len(partial['completed_writes'])==1 and json.loads((ff['roots']['pool']/'state.json').read_text())['status']=='failed'
        record(33,dict(fault='Payload deliberately changed AFTER genuine successful preflight',rejection=rj,partial=partial))
        receipt=OUT/'tiny-restore/restore-receipt.json'
        cfg=dict(restore_receipt=dict(path=str(receipt.relative_to(R)),**pin(receipt)),root_commit_ready_authorized=True)
        record(34,rejection(lambda:call(rec.commit_ready,R,cfg,roots,evidence,f['binding'])))
        assert pin(roots['pool']/'state.json')==state_before
        target.write_bytes(b'AFTER_TREE_WRONG')
        record(35,rejection(lambda:call(rec.actual_targets,roots,evidence)))
        # No retry or second restore: intentionally corrupt final tiny tree remains evidence.
        text=(D/'SOURCE/recovery.py').read_text();tree=ast.parse(text)
        functions={node.name:node for node in tree.body if isinstance(node,ast.FunctionDef)}
        assert 'copytree(' not in text and '_reconstruct(' not in text
        record(36,dict(engineering_writes=80,project_files=78,directory_differences=7,staged_files=2,Game_copies=0,actual_restore_calls=0))
        source=json.loads((D/'source-review.json').read_text());assert source['collector_inverse_fullbytes']
        record(37,source)
        assert source['host_inverse_AST'] and source['storage_process_reused']
        record(38,dict(host_inverse_AST=True,prior363_successes_reused=True,host_unit_calls=7,successful_full12_positive=False))
        calls=[node.func.id for node in ast.walk(functions['recover']) if isinstance(node,ast.Call) and isinstance(node.func,ast.Name)]
        for required in ('source_gate','check_roots','verify_evidence','restore_exact','commit_ready'):assert required in calls
        ready=ast.get_source_segment(text,functions['commit_ready'])
        assert ready.index("owned real independent readback")<ready.index('state_write(')
        assert "except BaseException" in ready and "failed-pool-state.json" in ready
        badroot=OUT/'missing-root-config';badroot.mkdir()
        missing=dict(path='MISSING.json',size=0,sha256='0'*64)
        root_reject=rejection(lambda:call(rec.source_gate,badroot,missing,'restore'))
        record(39,dict(source_order=True,missing_ROOT_rejected=root_reject,ready_not_committed=True))
        record(40,dict(actual_failedpool_readback=False,actual_pool_mutations=0,actual_READY_commits=0,
            next_gate='ROOT actual restore, independent full physical readback, ROOT commit; no attempt02 authorization'))
    except BaseException as exc:
        error=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
        save(OUT/'first-failure.json',error)
    finally:
        report=dict(schema='phase365-independent-unit-first/1',status='PASS' if error is None else 'FAIL',
            actual_controls=len(rows),planned_controls=40,cases=rows,counts=COUNTS,failure=error,
            remaining_NOT_EXECUTED=[row['id'] for row in contract['cases'] if row['id'] not in {r['id'] for r in rows}],
            scope='SOURCE + one true empty-project language regression + synthetic control metadata/tinyFS, NOT native/King acceptance')
        save(OUT/'report.json',report)
        leaves=[p for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()]
        save(OUT/'output-seal.json',dict(files=[dict(path=str(p.relative_to(R)),**pin(p)) for p in sorted(leaves)]))
        print(json.dumps(dict(status=report['status'],actual_controls=len(rows),counts=COUNTS,failure=error)))
    return 0 if error is None else 1

if __name__=='__main__':raise SystemExit(main())
