"""Exactly one frozen eight-section comparison; no model invocation or retry."""
from pathlib import Path
from collections import Counter
import argparse
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
SOURCE='tests/phase476_joint_business_output.py'
SOURCE_SHA='23c5bec3eee0449bc0bccf9e6a216e288aec50895bfd3e4223506fc9971976b1'
BUNDLE='data/phase476-derived-joint-input-first-001/input-bundle.json'
MODEL_DIR=ROOT/'data/phase476-joint-actual-model-first-001'
CONTROL='data/phase477-independent-interfaces-first-001/result.json'
PINS=ROOT/'data/phase478-independent-comparison-source/pins.json'
OUT=ROOT/'data/phase478-joint-comparison-first-001'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--pins-sha256',required=True);args=parser.parse_args()
    OUT.mkdir(exist_ok=False)
    began=time.monotonic();reads=[];calls=Counter();pins=[];expected_opens=[]
    stage='preflight'; report=dict(prior_comparison_attempt=None, prior_EXPECTED_business_decodes=0, attempt_semantics='first fixed joint-case comparison after sealed one-model output; no model rerun', schema='phase478-joint-independent-comparison/1',status='RUNNING',King_admitted=False,formal_support=75)
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
        pins_raw=PINS.read_bytes();assert hashlib.sha256(pins_raw).hexdigest()==args.pins_sha256,'frozen comparator pins'
        config=json.loads(pins_raw); descriptors={p['path']:p for p in config['files']}
        assert descriptors[SOURCE]['sha256']==SOURCE_SHA
        raw=pinned(SOURCE,descriptors[SOURCE]);A=types.ModuleType('phase478_adapter')
        exec(compile(raw,str(ROOT/SOURCE),'exec'),A.__dict__)
        count_names=('compare_decoded','compare_projected','project_native','project_model','project_native_final','project_model_final',
                     'project_native_callbacks','project_model_callbacks','project_native_api','project_model_api','_snapshot_native','_snapshot_model','_terminal_native','_terminal_model','bindings','strict_json_loads')
        for name in count_names:
            original=getattr(A,name)
            def counted(*args,_name=name,_fn=original,**kwargs):
                calls[_name]+=1;return _fn(*args,**kwargs)
            setattr(A,name,functools.wraps(original)(counted))
        def load(path,want=None):return A.strict_json_loads(pinned(path,want))
        def fixed(path):return load(path,descriptors[str(path)])
        for path in ('tests/phase478_independent_actual_compare.py','data/phase477-independent-final-acceptance/review.json'):
            pinned(path,descriptors[path])
        controls=fixed(CONTROL)
        assert controls['status']=='ACCEPTED_REPAIRED_JOINT_INPUT_AND_INTERFACES_NOT_FULL_RUN' and len(controls['cases'])==16
        assert controls['Expected_business_decode']==0 and controls['complete_model_run'] is False
        contract=fixed('data/phase466-captured-joint-bridge-design/comparison-contract.json')
        assert set(contract['sections'])==set(A.SECTIONS)
        index=fixed('data/phase474-root-external-identities/expected-pins.json')
        assert set(index['files'])==set(A.EXPECTED_LEAVES)
        capsule=load(index['capsule_manifest']['path'],index['capsule_manifest'])
        assert capsule['native_capture_complete'] is True and capsule['native_process_clean_exit'] is False
        for name,row in index['files'].items():
            saved=capsule['files']['run/output/capture/'+name]
            assert all(saved[k]==row[k] for k in ('size','sha256')),'old capsule association'
        binding=fixed('data/phase478-root-actual-joint-model-release/comparison-binding.json')
        assert binding==controls['input_binding']
        model_seal=fixed('data/phase476-joint-actual-model-first-001/output-seal.json')
        assert model_seal['status']=='ACTUAL_OUTPUT_SEALED_NOT_COMPARED'
        before=load(MODEL_DIR/'before.json',model_seal['files']['before.json'])
        execution=load(MODEL_DIR/'execution.json',model_seal['files']['execution.json'])
        assert before['input']==binding['input_bundle'] and before['source_freeze']==binding['candidate_freeze']
        assert execution['calls']==dict(candidate_import_attempts=1,construct_attempts=1,full_run_attempts=1)
        assert execution['tape_position']==execution['tape_records']==422 and execution['full_clock_passes']==2367
        assert execution['expected_reads']==execution['new_original_capture']==execution['comparator_calls']==0
        assert before['sources']==execution['source_after'] and len(before['sources'])==15
        assert execution['input_after']=={k:binding['input_bundle'][k] for k in ('size','sha256')}
        freeze=load(binding['candidate_freeze']['path'],binding['candidate_freeze'])
        assert len(freeze['files'])==15
        for row in freeze['files']:
            assert before['sources'][str(ROOT/row['path'])]=={k:row[k] for k in ('size','sha256')}
            pinned(row['path'],row)
        bundle=load(BUNDLE,binding['input_bundle'])
        assert hashlib.sha256(json.dumps(bundle,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()==binding['input_canonical_sha256']
        assert bundle['fixture']['below_master'] is True and len(bundle['draws'])==422
        result=load(MODEL_DIR/'model-output.json',model_seal['files']['model-output.json'])
        assert model_seal['files']['model-output.json']==dict(size=27176123,sha256='d4e9705b2a1d6907d9464f1caf8ffa6d4cdbe99aa296b427addc3aa21da28aae')
        assert not any(n.startswith(('native_replay_v7','native_replay_v8')) for n in sys.modules)
        allowed={row['path'] for row in index['files'].values()} | {str(ROOT/SOURCE),str(Path(__file__).resolve())}
        def audit(event,args):
            if event.startswith(('subprocess.','socket.')) or event in ('os.system','os.exec','os.spawn','os.fork','os.posix_spawn'):
                raise RuntimeError('forbidden comparator external operation '+event)
            if event!='open' or not isinstance(args[0],(str,bytes,os.PathLike)):return
            path=Path(os.fsdecode(args[0])).resolve();flags=args[2] or 0
            writing=bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
            if writing:assert path.is_relative_to(OUT),'write outside comparison output'
            elif path.is_relative_to('/workspace'):assert str(path) in allowed,'unapproved workspace read '+str(path)
            reads.append(dict(path=str(path),operation='write' if writing else 'read'))
        output_refs.append(dump(OUT/'before.json',dict(schema='phase478-before-Expected/1',pins=pins.copy(),expected_index=index,
            model_already_sealed=True,model_output_payload_reads_this_attempt=1,EXPECTED_reads_so_far=0,prior_interface_controls=CONTROL,
            frozen_contract_sha256=A.CONTRACT_SHA256,provenance_limit='Existing467 bounded complete capture; native_process_clean_exit=false retained; no recapture/old schema rerun')))
        sys.addaudithook(audit)
        signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,50)
        stage='read_and_decode_nine_EXPECTED_leaves';native={}
        for name,want in index['files'].items():
            expected_opens.append(name)
            raw=pinned(want['path'],want)
            if name.endswith('.jsonl'):
                lines=raw.splitlines();assert all(line.strip() for line in lines),'blank JSONL row'
                native[name]=[A.strict_json_loads(line) for line in lines]
            else:native[name]=A.strict_json_loads(raw)
        stage='single_compare_decoded'
        comparison=A.compare_decoded(native,result,bundle,binding)
        assert calls['compare_decoded']==1
        output_refs.append(dump(OUT/'comparison.json',comparison))
        report['status']='PASS_EIGHT_BUSINESS_SECTIONS_ROOT_ACCEPTANCE_PENDING' if comparison['status']=='PASS' else 'FAIL_STRICT_BUSINESS_DIFFERENCES'
        report['first_differences']=comparison['first_differences']
        stage='source_readback';pinned(SOURCE,descriptors[SOURCE])
    except BaseException as exc:
        report['status']='FAIL_FIRST_CARRIER_OR_PROJECTION_ERROR_NO_RETRY'
        report['failure']=dict(stage=stage,type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
        report.update(elapsed_seconds=time.monotonic()-began,calls=dict(calls),pins=pins,
                      EXPECTED_payload_open_attempts=expected_opens,EXPECTED_payload_successful_pins=[p for p in pins if '/output/capture/' in p['path']],
                      accesses_after_Expected_gate=reads.copy(),model_invocations=0,original_INPUT12_reads=0,new_native_capture=0,
                      contract_sha256='71c681047140d3bc13d91b24be590dcb598cb3454edac394288c64e01cb3ecef',model_imports=0,native_capture_complete=True,native_process_clean_exit=False)
        output_refs.append(dump(OUT/'result.json',report))
        dump(OUT/'owned-files.json',dict(schema='phase478-actual-comparison-owner/1',status=report['status'],files=output_refs))
    print(json.dumps(dict(status=report['status'],elapsed_seconds=report['elapsed_seconds'],calls=report['calls'],output=str(OUT))))
    return 0 if report['status'].startswith('PASS') else 1


if __name__=='__main__':raise SystemExit(main())
