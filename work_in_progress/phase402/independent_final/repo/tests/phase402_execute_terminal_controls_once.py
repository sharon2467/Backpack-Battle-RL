"""Sealed independent runner: exactly one real completed-capture terminal join."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import time
import traceback

ROOT=Path('/workspace/python-original-engine/repo')
BIND=ROOT/'data/phase402-completed-control-execution-binding-final'
OUT=ROOT/'data/phase402-terminal-controls-first-001'

def pin(path):
    for p in [path,*path.parents]:
        if p.is_symlink(): raise ValueError('symbolic path: '+str(p))
    a=path.lstat()
    if not stat.S_ISREG(a.st_mode) or a.st_nlink!=1: raise ValueError('ordinary single-link file required')
    h=hashlib.sha256(); size=0
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1048576),b''): h.update(block);size+=len(block)
    if a!=path.lstat() or size!=a.st_size: raise ValueError('file changed while reading')
    return dict(size=size,sha256=h.hexdigest())

def save(name,value):
    (OUT/name).open('x').write(json.dumps(value,indent=2,sort_keys=True)+'\n')

def main():
    started=time.monotonic()
    assert not OUT.exists(); OUT.mkdir()
    sealed=json.loads((BIND/'execution-preparation-owner.json').read_bytes())
    for path,row in sealed['files'].items(): assert pin(ROOT/path)==row,path
    allow=json.loads((BIND/'readallowset.json').read_bytes())
    expected=json.loads((BIND/'expected.json').read_bytes())
    for path,row in allow['immutable_absolute_pins'].items(): assert pin(Path(path))==row,path
    freeze=json.loads((ROOT/expected['source_freeze']['path']).read_bytes())
    allowed=set(allow['immutable_absolute_pins'])|{str(ROOT/p) for p in sealed['files']}
    allowed.add(str(BIND/'execution-preparation-owner.json'))
    controlpaths=set(allow['control_decode_paths'])
    reads=[]; violations=[]; calls={}; imported=[]; stage='import'; top_calls=0
    sys.dont_write_bytecode=True
    sys.pycache_prefix='/tmp/phase402-unused-bytecode-20261026-unique'
    assert not Path(sys.pycache_prefix).exists()
    sys.path.insert(0,str(ROOT/'tests'))
    modules_before=set(sys.modules)
    def audit(event,args):
        if event in ('subprocess.Popen','os.system','os.fork','os.posix_spawn','socket.connect','socket.bind'):
            violations.append(dict(event=event)); raise RuntimeError('forbidden operation')
        if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)):
            path=os.path.abspath(os.fsdecode(args[0])); mode=args[1]; flags=args[2]
            write=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC)))
            if write:
                if not path.startswith(str(OUT)+'/'):
                    violations.append(dict(event=event,path=path,write=True)); raise RuntimeError('unowned write')
                return
            if path.startswith('/proc/') or (path.startswith('/workspace/') and path not in allowed and not path.startswith(str(OUT)+'/')):
                violations.append(dict(event=event,path=path,write=False)); raise RuntimeError('read outside sealed allowset')
            if path.startswith(str(ROOT)+'/') or path.startswith(allow['run']+'/'):
                reads.append(dict(stage=stage,path=path))
        if event=='import': imported.append(str(args[0]))
    def profile(frame,event,arg):
        if event=='call':
            path=frame.f_code.co_filename
            if path.startswith(str(ROOT/'tests')+'/'):
                key=path+'::'+frame.f_code.co_name
                calls[key]=calls.get(key,0)+1
    sys.addaudithook(audit)
    outcome=dict(status='FAIL',top_level_helper_calls=0)
    try:
        spec=importlib.util.spec_from_file_location('_independent402_actual391_host',ROOT/'tests/phase391_oracle_host.py')
        host=importlib.util.module_from_spec(spec);sys.modules[spec.name]=host;spec.loader.exec_module(host)
        stage='helper';sys.setprofile(profile);top_calls=1
        result=host.read_terminal_expected_controls(ROOT,freeze,Path(expected['capture']))
        sys.setprofile(None);stage='postcheck'
        save('terminal-helper-return.json',result)
        assert result['schema']==expected['expected_schema'] and result['expected_control_only'] is True
        assert type(result['model_calls']) is int and result['model_calls']==0 and result['input_bundle_created'] is False
        assert result['source_schema']==freeze['schema_module'] and result['source_tuple']==freeze['active_source_tuple']
        actual_controls={Path(r['path']).name:{k:r[k] for k in ('size','sha256')} for r in expected['six_control_pins']}
        assert result['files']==actual_controls
        prior=json.loads((Path(allow['run'])/'output/source-partition.json').read_bytes())['terminal_expected_control']
        assert result==prior
        helper_capture_reads=[r['path'] for r in reads if r['stage']=='helper' and r['path'].startswith(allow['capture']+'/')]
        assert len(helper_capture_reads)==6 and set(helper_capture_reads)==controlpaths
        for path,row in allow['immutable_absolute_pins'].items(): assert pin(Path(path))==row,path
        for path,row in sealed['files'].items(): assert pin(ROOT/path)==row,path
        assert not violations
        outcome=dict(status='PASS',top_level_helper_calls=1,helper_capture_reads=helper_capture_reads,
            post_pin_count=len(allow['immutable_absolute_pins']),source_and_binding_unchanged=True)
    except BaseException as exc:
        sys.setprofile(None)
        outcome=dict(status='FAIL',top_level_helper_calls=top_calls,error_type=type(exc).__name__,error=str(exc))
        (OUT/'first-error-traceback.txt').open('x').write(traceback.format_exc())
    finally:
        sys.setprofile(None);stage='evidence'
        localmodules={name:str(getattr(module,'__file__','')) for name,module in sys.modules.items() if name not in modules_before and str(getattr(module,'__file__','')).startswith(str(ROOT/'tests')+'/')}
        save('io-read-observation.json',dict(reads=reads,violations=violations,import_events=imported))
        save('call-observation.json',dict(actual_function_call_counts=calls,local_module_instances=localmodules,
            schema_exec_note='Real host load_terminal_schema executes one pinned schema module and deletes its sys.modules entry on return.'))
        outcome.update(elapsed_seconds=time.monotonic()-started,native=0,models=0,inputbuild=0,restore=0,READY=0,
            current_pool_reads=0,new_proc_scans=0,automatic_retry=False)
        save('execution-result.json',outcome)
    print(json.dumps(outcome,sort_keys=True))
    return 0 if outcome['status']=='PASS' else 1

if __name__=='__main__': raise SystemExit(main())
