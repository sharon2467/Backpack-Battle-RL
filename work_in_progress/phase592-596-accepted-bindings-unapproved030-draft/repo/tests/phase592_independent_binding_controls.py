"""Frozen independent finite Source-binding controls; requires explicit Root execution release."""
import argparse, contextlib, ctypes, datetime, fcntl, hashlib, json, os, pathlib
import shutil, stat, tempfile, zipfile, signal, selectors, subprocess, sys, time, math
import re, types, copy, traceback
import __future__

ROOT = pathlib.Path('/workspace/python-original-engine/repo')
OUT = ROOT/'data/phase592-independent-controls-first-001'
MODULES = ('native_run_compaction','phase363_oracle_storage','phase363_oracle_process','phase590_oracle_storage','phase590_oracle_host')
FORBIDDEN = {'source_gate','verify_execute_payloads','resolve_execute_payloads','plan','execute','lease','install','prepare','restore','readback','resource_gate','budget','check_ready','inventory','process_check','load_bundle','execute_process','archive_streaming','reset_previous','state_write','atomic_image','apply','action','read_terminal_expected_controls','load_terminal_schema'}

def canonical(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def pin(path):
    before=path.stat();raw=path.read_bytes();after=path.stat()
    assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
    return {'path':str(path.relative_to(ROOT)),'size':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--pins',required=True);parser.add_argument('--pins-sha256',required=True);args=parser.parse_args()
    pins_path=pathlib.Path(args.pins);raw=pins_path.read_bytes();assert hashlib.sha256(raw).hexdigest()==args.pins_sha256
    protocol=json.loads(raw);assert protocol['schema']=='phase591-binding-control-pins/1'
    assert not OUT.exists() and not OUT.is_symlink();OUT.mkdir(mode=0o700)
    started=time.monotonic();result={'schema':'phase591-independent-binding-controls/1','status':'RUNNING','cases':[],'top_entered':0,'top_completed':0,'positive':0,'rejected':0,'module_eval_attempts':0,'module_imports_completed':0,'profile':{},'origins':{},'read_audit':[],'writes':[],'forbidden_calls':[],'native':0,'models':0,'Expected':0,'actual_pool_baseline_resources':0}
    allowed={str(ROOT/x['path']) for x in protocol['files']}|{str(pins_path)}
    watched={str(ROOT/'tests'/f'{name}.py') for name in MODULES}
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
        if event=='call' and frame.f_code.co_filename in watched:
            key=frame.f_code.co_filename+'::'+frame.f_code.co_name
            result['profile'][key]=result['profile'].get(key,0)+1
            if frame.f_code.co_name in FORBIDDEN:
                result['forbidden_calls'].append(key);raise RuntimeError('FORBIDDEN_FUNCTION '+key)
    def timeout(sig,frame):raise TimeoutError('phase591 15 second inner deadline')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(15);sys.dont_write_bytecode=True
    sys.addaudithook(audit)
    try:
        result['pins_before']=[pin(ROOT/x['path']) for x in protocol['files']];assert result['pins_before']==protocol['files']
        vectors=json.loads((ROOT/protocol['vectors']).read_text());assert len(vectors['cases'])==10
        stage='module_load';sys.setprofile(profile)
        for name in MODULES:
            assert name not in sys.modules
            path=ROOT/'tests'/f'{name}.py';module=types.ModuleType(name);module.__file__=str(path);sys.modules[name]=module
            result['module_eval_attempts']+=1
            exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
            result['module_imports_completed']+=1;result['origins'][name]=module.__file__
        host=sys.modules[MODULES[-1]];stage='controls'
        for case in vectors['cases']:
            row={'id':case['id'],'api':case['api'],'status':'ENTERED'};result['cases'].append(row);result['top_entered']+=1
            inputs=copy.deepcopy(case.get('args',case.get('freeze')));before=canonical(inputs)
            try:
                if case['api']=='validate_observer_review':value=host.validate_observer_review(*inputs)
                else:value=host.validate_active_source_tuple(ROOT,inputs)
            except ValueError as exc:
                row['first_reject']={'type':type(exc).__name__,'message':str(exc)}
                assert case['expected'].get('exception')=='ValueError' and str(exc)==case['expected']['message'],row
                result['rejected']+=1
            else:
                assert 'returns' in case['expected'] and value==case['expected']['returns'],row
                row['returned']=value;result['positive']+=1
            row['input_before']=before;row['input_after']=canonical(inputs);assert before==row['input_after']
            row['status']='PASS';result['top_completed']+=1
        assert result['top_completed']==10 and result['positive']==2 and result['rejected']==8
        assert result['module_imports_completed']==5 and not result['forbidden_calls']
        result['status']='PASS_SOURCE_BINDINGS_ONLY';code=0
    except BaseException as exc:
        result['status']='FIRST_ERROR_STOPPED';result['first_error']={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}
    finally:
        sys.setprofile(None);signal.alarm(0);stage='after'
        try:
            result['pins_after']=[pin(ROOT/x['path']) for x in protocol['files']];assert result['pins_after']==protocol['files'];result['pins_unchanged']=True
        except BaseException as exc:
            result['status']='FIRST_ERROR_STOPPED';result['after_error']=repr(exc);code=1
        result['elapsed_seconds']=time.monotonic()-started;result['remaining']='Actual Source_gate/hostreview, resources, Ready/lease, Native capture and restoration not exercised.'
        stage='report'
        if 'first_error' in result:(OUT/'first-error.json').write_text(json.dumps(result['first_error'],indent=2)+'\n')
        result_text=json.dumps(result,indent=2)+'\n'
        (OUT/'result.json').write_text(result_text)
        files=[]
        for name in ('result.json','first-error.json'):
            p=OUT/name
            if p.exists():
                # Report bytes already in memory: avoid broadening the read allowlist to output artifacts.
                data=result_text if name=='result.json' else json.dumps(result['first_error'],indent=2)+'\n'
                files.append({'path':str(p.relative_to(ROOT)),'size':len(data.encode()),'sha256':hashlib.sha256(data.encode()).hexdigest()})
        (OUT/'owned-files.json').write_text(json.dumps({'schema':'phase591-control-output-owner/1','files':files},indent=2)+'\n')
    return code

if __name__=='__main__':raise SystemExit(main())
