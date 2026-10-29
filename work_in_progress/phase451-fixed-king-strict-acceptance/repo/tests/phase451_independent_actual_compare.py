"""Exactly one frozen eight-section comparison; no model invocation or retry."""
from pathlib import Path
from collections import Counter
import functools
import hashlib
import json
import os
import signal
import stat
import sys
import time
import traceback
import types

ROOT=Path(__file__).resolve().parents[1]
SOURCE='tests/phase451_pure_business_output_v4.py'
SOURCE_SHA='ee905f14176415a09f58ee7d657e08b6008a70771bd74075fe0587bf9a966515'
BUNDLE='data/phase441-fixed-A-input-first-001/input-bundle.json'
MODEL_DIR=ROOT/'data/phase446-fixed-A-model-first-001'
CONTROL='data/phase451-independent-output-controls-first-001/result.json'
OUT=ROOT/'data/phase451-fixed-A-comparison-first-001'


def main():
    OUT.mkdir(exist_ok=False)
    began=time.monotonic();reads=[];calls=Counter();pins=[];expected_opens=[]
    stage='preflight'; report=dict(prior_comparison_attempt='data/phase450-fixed-A-comparison-first-001', prior_EXPECTED_payload_reads=18, attempt_semantics='new immutable adapter continues unfinished strict comparison; no model rerun', schema='phase451-fixed-A-independent-comparison/1',status='RUNNING',King_admitted=False,formal_support=75)
    def dump(path,value):
        raw=(json.dumps(value,ensure_ascii=False,allow_nan=False,indent=2)+'\n').encode()
        with path.open('xb') as f:f.write(raw)
        return dict(path=str(path.relative_to(ROOT)),size=len(raw),sha256=hashlib.sha256(raw).hexdigest())
    def pinned(path,want=None):
        path=Path(path);path=path if path.is_absolute() else ROOT/path
        before=path.lstat()
        assert stat.S_ISREG(before.st_mode) and before.st_nlink==1 and not any(p.is_symlink() for p in path.parents),'ordinary single-link input'
        raw=path.read_bytes();after=path.stat()
        assert (before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_ino,after.st_size,after.st_mtime_ns),'concurrent input mutation'
        pin=dict(path=str(path),size=len(raw),sha256=hashlib.sha256(raw).hexdigest())
        if want is not None:assert all(pin[k]==want[k] for k in ('size','sha256')),'pin mismatch '+str(path)
        pins.append(pin);return raw
    def timeout(signum,frame):raise TimeoutError('50-second one-comparison budget')
    output_refs=[]
    try:
        raw=pinned(SOURCE,dict(size=41991,sha256=SOURCE_SHA));A=types.ModuleType('phase448_adapter')
        exec(compile(raw,str(ROOT/SOURCE),'exec'),A.__dict__)
        count_names=('compare_decoded','compare_projected','project_native','project_model','project_native_final','project_model_final',
                     'project_native_callbacks','project_model_callbacks','project_native_api','project_model_api','_snapshot_native','_snapshot_model','_terminal_native','_terminal_model','bindings','strict_json_loads')
        for name in count_names:
            original=getattr(A,name)
            def counted(*args,_name=name,_fn=original,**kwargs):
                calls[_name]+=1;return _fn(*args,**kwargs)
            setattr(A,name,functools.wraps(original)(counted))
        def load(path,want=None):return A.strict_json_loads(pinned(path,want))
        control_owner=load('data/phase451-independent-output-controls-first-001/owned-files.json')
        control_pin=control_owner['files'][0];controls=load(CONTROL,control_pin)
        assert controls['status']=='PASS_SYNTHETIC_ADAPTER_INTERFACE_CONTROLS' and controls['EXPECTED_reads']==0
        assert controls['reads'][0]['sha256']==SOURCE_SHA
        contract=load('data/phase445-business-output-contract/contract.json',dict(size=4664,sha256='d7c6b97de2c966fb207da8fc16ac0030bb0560f3fb1299356611c07ffb697f09'))
        assert set(contract['sections'])==set(A.SECTIONS)
        index=load('data/phase447-existing-expected-pins/pins.json')
        assert set(index['files'])==set(A.EXPECTED_LEAVES)
        capsule_path=Path('/workspace/backpack-python-publish-20261025')/index['source_manifest']['git_path']
        capsule=load(capsule_path,index['source_manifest'])
        for name,pin in index['files'].items():
            assert capsule['files'][index['capsule_member_prefix']+name]==pin,'old capsule association'
        model_seal=load(MODEL_DIR/'output-seal.json')
        assert model_seal['status']=='ACTUAL_OUTPUT_SEALED_NOT_COMPARED'
        before=load(MODEL_DIR/'before.json',model_seal['files']['before.json'])
        execution=load(MODEL_DIR/'execution.json',model_seal['files']['execution.json'])
        assert before['input']['sha256']=='c87525f35adf8fa3793cc5d1440dff420dc55f3a24c77e520766b01e8963ae2c'
        assert before['source_freeze']['sha256']=='b5a87cbaab96e859368fdc5a037889c5931908d429e3551a612c732af5e0d68a'
        assert execution['calls']==dict(construct_attempts=1,full_run_attempts=1) and execution['tape_position']==365
        assert execution['expected_reads']==0 and execution['new_original_capture']==0
        bundle=load(BUNDLE,dict(size=539534,sha256=before['input']['sha256']))
        result=load(MODEL_DIR/'model-output.json',model_seal['files']['model-output.json'])
        assert model_seal['files']['model-output.json']==dict(size=32056632,sha256='7867a3d4869c3e924557a6a865bf1efcb2eef2f32746b21ab55757b17e0d47ae')
        capture=Path(index['capture_root'])
        allowed={str(capture/name) for name in index['files']} | {str(ROOT/SOURCE),str(Path(__file__).resolve())}
        def audit(event,args):
            if event.startswith(('subprocess.','socket.')) or event in ('os.system','os.exec','os.spawn','os.fork','os.posix_spawn'):
                raise RuntimeError('forbidden comparator external operation '+event)
            if event!='open' or not isinstance(args[0],(str,bytes,os.PathLike)):return
            path=Path(os.fsdecode(args[0])).resolve();flags=args[2] or 0
            writing=bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
            if writing:assert path.is_relative_to(OUT),'write outside comparison output'
            elif path.is_relative_to('/workspace'):assert str(path) in allowed,'unapproved workspace read '+str(path)
            reads.append(dict(path=str(path),operation='write' if writing else 'read'))
        output_refs.append(dump(OUT/'before.json',dict(schema='phase451-before-Expected/1',pins=pins.copy(),expected_index=index,
            model_already_sealed=True,prior_model_output_hash_only_reads=1,EXPECTED_reads_so_far=0,prior_interface_controls=CONTROL,
            frozen_contract_sha256=A.CONTRACT_SHA256,provenance_limit='Existing401/402 bounded native acceptance; non-clean-exit disclosure retained; no recapture/old schema rerun')))
        sys.addaudithook(audit)
        signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,50)
        stage='read_and_decode_nine_EXPECTED_leaves';native={}
        for name,want in index['files'].items():
            expected_opens.append(name)
            raw=pinned(capture/name,want)
            if name.endswith('.jsonl'):
                lines=raw.splitlines();assert all(line.strip() for line in lines),'blank JSONL row'
                native[name]=[A.strict_json_loads(line) for line in lines]
            else:native[name]=A.strict_json_loads(raw)
        stage='single_compare_decoded'
        comparison=A.compare_decoded(native,result,bundle)
        assert calls['compare_decoded']==1
        output_refs.append(dump(OUT/'comparison.json',comparison))
        report['status']='PASS_EIGHT_BUSINESS_SECTIONS_ROOT_ACCEPTANCE_PENDING' if comparison['status']=='PASS' else 'FAIL_STRICT_BUSINESS_DIFFERENCES'
        report['first_differences']=comparison['first_differences']
        stage='source_readback';pinned(SOURCE,dict(size=41991,sha256=SOURCE_SHA))
    except BaseException as exc:
        report['status']='FAIL_FIRST_CARRIER_OR_PROJECTION_ERROR_NO_RETRY'
        report['failure']=dict(stage=stage,type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
        report.update(elapsed_seconds=time.monotonic()-began,calls=dict(calls),pins=pins,
                      EXPECTED_payload_open_attempts=expected_opens,EXPECTED_payload_successful_pins=[p for p in pins if '/output/capture/' in p['path']],
                      accesses_after_Expected_gate=reads.copy(),model_invocations=0,original_INPUT12_reads=0,new_native_capture=0,
                      contract_sha256='d7c6b97de2c966fb207da8fc16ac0030bb0560f3fb1299356611c07ffb697f09')
        output_refs.append(dump(OUT/'result.json',report))
        dump(OUT/'owned-files.json',dict(schema='phase451-actual-comparison-owner/1',status=report['status'],files=output_refs))
    print(json.dumps(dict(status=report['status'],elapsed_seconds=report['elapsed_seconds'],calls=report['calls'],output=str(OUT))))
    return 0 if report['status'].startswith('PASS') else 1


if __name__=='__main__':raise SystemExit(main())
