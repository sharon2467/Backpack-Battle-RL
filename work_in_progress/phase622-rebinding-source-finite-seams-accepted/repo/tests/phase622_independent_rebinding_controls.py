"""Frozen finite Source-only seams. Execute only after exact Root release."""
import __future__, argparse, contextlib, ctypes, datetime, fcntl, hashlib, json, os, pathlib
import shutil, stat, tempfile, zipfile, signal, selectors, subprocess, sys, time, math
import re, types, copy, struct, dataclasses

ROOT = pathlib.Path('/workspace/python-original-engine/repo')
OUT = ROOT/'data/phase622-independent-controls-first-001'
FORBIDDEN = {'source_gate','verify_owner','verify_execute_payloads','resolve_execute_payloads','plan','execute','lease','install','prepare','restore','readback','resource_gate','budget','check_ready','inventory','process_check','load_bundle','execute_process','archive_streaming','reset_previous','state_write','atomic_image','apply','action','read_terminal_expected_controls','load_terminal_schema','write_new','sync','rename_capture','usage'}

def canonical(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def pin(path):
    before=path.lstat();assert stat.S_ISREG(before.st_mode) and before.st_nlink==1
    raw=path.read_bytes();after=path.lstat()
    assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
    return {'path':str(path.relative_to(ROOT)),'size':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--pins',required=True);parser.add_argument('--pins-sha256',required=True);args=parser.parse_args()
    pins_path=pathlib.Path(args.pins);raw=pins_path.read_bytes();assert hashlib.sha256(raw).hexdigest()==args.pins_sha256
    protocol=json.loads(raw);assert protocol['schema']=='phase622-rebinding-control-pins/1'
    assert not OUT.exists() and not OUT.is_symlink();OUT.mkdir(mode=0o700)
    started=time.monotonic();result={'schema':'phase622-independent-seam-controls/1','status':'RUNNING','cases':[],'top_entered':0,'top_completed':0,'positive':0,'rejected':0,'module_eval_attempts':0,'module_imports_completed':0,'schema_eval_attempts':0,'schema_imports_completed':0,'profile':{},'origins':{},'read_audit':[],'writes':[],'forbidden_calls':[],'native':0,'models':0,'Expected':0,'actual_pool_baseline_resources':0}
    allowed={str(ROOT/x['path']) for x in protocol['files']}|{str(pins_path)}
    module_paths={str(ROOT/x['path']):x['name'] for x in protocol['modules']}
    schema_relative=protocol['schema_module']['path'];schema_absolute=str(ROOT/schema_relative)
    watched=set(module_paths)|{schema_relative,schema_absolute}
    stage='before';code=1
    def audit(event,arguments):
        if event=='open':
            path,mode,flags=arguments
            if isinstance(path,int):return
            p=pathlib.Path(os.fsdecode(path));assert p.is_absolute(),'relative open forbidden'
            write=bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
            if write:
                assert stage=='report' and p.parent==OUT,('WRITE_SCOPE',str(p),stage)
                result['writes'].append(str(p))
            else:
                assert str(p) in allowed,('READ_SCOPE',str(p),stage)
                result['read_audit'].append({'path':str(p),'stage':stage})
        elif event in ('subprocess.Popen','os.system','os.remove','os.rename','os.rmdir','socket.connect'):
            raise RuntimeError('FORBIDDEN_EVENT '+event)
    def profile(frame,event,arg):
        filename=frame.f_code.co_filename;name=frame.f_code.co_name
        if event=='call' and filename in watched:
            key=filename+'::'+name;result['profile'][key]=result['profile'].get(key,0)+1
            if filename in (schema_relative,schema_absolute):
                if name=='<module>':result['schema_eval_attempts']+=1
                permitted=name in ('<module>','<genexpr>','<listcomp>','<dictcomp>','<setcomp>','FramePass','ClockSchedule')
            elif module_paths[filename]=='phase578_initial_receipt':
                permitted=name in ('<module>','<genexpr>','<listcomp>','<dictcomp>','<setcomp>')
            elif module_paths[filename]=='phase621_input_bridge':
                permitted=name in ('<module>','<genexpr>','<listcomp>','<dictcomp>','<setcomp>','Rejected','load_schema','require')
            else:permitted=name not in FORBIDDEN
            if not permitted:
                result['forbidden_calls'].append(key);raise RuntimeError('FORBIDDEN_FUNCTION '+key)
    def timeout(sig,frame):raise TimeoutError('phase622 15 second inner deadline')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(15);sys.dont_write_bytecode=True
    sys.addaudithook(audit)
    try:
        result['pins_before']=[pin(ROOT/x['path']) for x in protocol['files']];assert result['pins_before']==protocol['files']
        vectors=json.loads((ROOT/protocol['vectors']).read_text());assert len(vectors['cases'])==11
        schema_raw=(ROOT/schema_relative).read_bytes()
        stage='module_load';sys.setprofile(profile)
        for item in protocol['modules']:
            name=item['name'];assert name not in sys.modules
            path=ROOT/item['path'];module=types.ModuleType(name);module.__file__=str(path);sys.modules[name]=module
            result['module_eval_attempts']+=1
            exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
            result['module_imports_completed']+=1;result['origins'][name]=module.__file__
        host=sys.modules['phase621_oracle_host'];bridge=sys.modules['phase621_input_bridge'];stage='controls'
        for case in vectors['cases']:
            row={'id':case['id'],'api':case['api'],'status':'ENTERED','schema_evals_before':result['schema_eval_attempts']};result['cases'].append(row);result['top_entered']+=1
            if case['api']=='load_schema':
                inputs=schema_raw if case['mode']=='exact_bytes' else schema_raw+b'\n';before=hashlib.sha256(inputs).hexdigest()
            elif case['api']=='validate_observer_review':
                inputs=copy.deepcopy([case['value'],case['receipt'],case['source_tuple']]);before=canonical(inputs)
            else:
                inputs=json.loads((ROOT/case['freeze_base']['path']).read_text());inputs[case['mutation']['key']]=copy.deepcopy(case['mutation']['value']);before=canonical(inputs)
            try:
                if case['api']=='load_schema':value=bridge.load_schema(inputs)
                elif case['api']=='validate_observer_review':value=host.validate_observer_review(*inputs)
                else:value=host.validate_active_source_tuple(ROOT,inputs)
            except ValueError as exc:
                row['first_reject']={'type':type(exc).__name__,'message':str(exc)}
                assert type(exc).__name__==case['expected'].get('exception') and str(exc)==case['expected']['message'],row
                result['rejected']+=1
            else:
                assert 'returns' in case['expected'],row
                if case['api']=='load_schema':
                    assert isinstance(value,types.ModuleType)
                    assert value.VERSION=='7-mixed-modifiers-A-610-hooks110' and value.PROFILE=='observer7-mixed-modifiers-A-hooks110-native-tape/1'
                    assert len(value.FIXED_ROLES)==29 and value.DESCRIPTOR_IDS==frozenset({1,5,11,14,22,32,162,164,231,233,234,385})
                    assert (ROOT/value.__file__).resolve()==ROOT/schema_relative
                    assert value.__name__ not in sys.modules
                    result['schema_imports_completed']+=1
                    row['returned']={'module':value.__name__,'file':value.__file__,'VERSION':value.VERSION,'PROFILE':value.PROFILE,'roles':29,'ids':sorted(value.DESCRIPTOR_IDS),'uncached':True}
                    result['origins']['nested_schema']=value.__file__
                else:assert value==case['expected']['returns'];row['returned']=value
                result['positive']+=1
            row['input_before']=before;row['input_after']=hashlib.sha256(inputs).hexdigest() if isinstance(inputs,bytes) else canonical(inputs);assert before==row['input_after']
            row['schema_evals_after']=result['schema_eval_attempts']
            assert row['schema_evals_after']-row['schema_evals_before']==(1 if case['id']=='01-load-new-schema' else 0)
            row['status']='PASS';result['top_completed']+=1
        assert result['top_completed']==11 and result['positive']==2 and result['rejected']==9
        assert result['module_imports_completed']==7 and result['schema_imports_completed']==result['schema_eval_attempts']==1 and not result['forbidden_calls']
        result['status']='PASS_SOURCE_SEAMS_ONLY';code=0
    except BaseException as exc:
        frames=[];tb=exc.__traceback__
        while tb is not None:
            frames.append({'file':tb.tb_frame.f_code.co_filename,'function':tb.tb_frame.f_code.co_name,'line':tb.tb_lineno});tb=tb.tb_next
        result['status']='FIRST_ERROR_STOPPED';result['first_error']={'type':type(exc).__name__,'message':str(exc),'frames':frames}
    finally:
        sys.setprofile(None);signal.alarm(0);stage='after'
        try:
            result['pins_after']=[pin(ROOT/x['path']) for x in protocol['files']];assert result['pins_after']==protocol['files'];result['pins_unchanged']=True
        except BaseException as exc:
            result['status']='FIRST_ERROR_STOPPED';result['after_error']=repr(exc);code=1
        result['elapsed_seconds']=time.monotonic()-started
        result['remaining']='Full positive tuple/deep legacy owner and five absolute origins/source_gate/host-review/resource/plan/lease/Native/restore are NOT executed. No actual INPUT/B2/B1/model/Native admission.'
        result['writes_scope']='Pre-result serialization snapshot; reporting write guard remains enabled, not claimed complete report-stage write audit.'
        stage='report';reports={}
        if 'first_error' in result:
            reports['first-error.json']=json.dumps(result['first_error'],indent=2)+'\n';(OUT/'first-error.json').write_text(reports['first-error.json'])
        reports['result.json']=json.dumps(result,indent=2)+'\n';(OUT/'result.json').write_text(reports['result.json'])
        files=[{'path':str((OUT/name).relative_to(ROOT)),'size':len(text.encode()),'sha256':hashlib.sha256(text.encode()).hexdigest()} for name,text in reports.items()]
        (OUT/'owned-files.json').write_text(json.dumps({'schema':'phase622-control-output-owner/1','files':files},indent=2)+'\n')
    return code

if __name__=='__main__':raise SystemExit(main())
