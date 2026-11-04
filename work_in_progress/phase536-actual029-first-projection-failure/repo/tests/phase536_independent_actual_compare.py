"""One sealed029 strict8 comparison using exact533 adapter; never runs a model."""
from pathlib import Path
from collections import Counter
from copy import deepcopy
import argparse
import functools
import hashlib
import json
import math
import os
import re
import signal
import stat
import struct
import sys
import time
import traceback
import types

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'tests/phase533_whelp_business_output.py'
SOURCE_SHA = '8e5cf40ff790a7db616ebac54deb9a5bf3b6410c7e300e866542179089668e54'
MODEL = ROOT/'data/phase533-case029-actual-model-first-001'
STAGE = ROOT/'data/phase536-independent-comparison-source'
OUT = ROOT/'data/phase536-case029-comparison-first-001'
INDEX = 'data/phase532-root-opaque-expected-descriptors/expected-descriptors.json'
CONTROL = 'data/phase534-independent-controls-first-001/result.json'
FINAL = 'data/phase534-independent-final-acceptance/review.json'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--pins-sha256',required=True);args=parser.parse_args()
    OUT.mkdir(exist_ok=False)
    began=time.monotonic();reads=[];calls=Counter();pins=[];expected_opens=[];output_refs=[]
    stage='preflight'
    report=dict(schema='phase536-independent-actual-comparison/1',status='RUNNING',prior_comparison_attempt=None,prior_EXPECTED_business_decodes=0,formal_support=75)
    def dump(path,value):
        raw=(json.dumps(value,ensure_ascii=False,allow_nan=False,indent=2)+'\n').encode()
        with path.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
        return dict(path=str(path.relative_to(ROOT)),size=len(raw),sha256=hashlib.sha256(raw).hexdigest())
    def pinned(path,want=None):
        path=Path(path);path=path if path.is_absolute() else ROOT/path
        before=path.lstat()
        assert stat.S_ISREG(before.st_mode) and before.st_nlink==1 and not any(p.is_symlink() for p in path.parents),'ordinary single-link file'
        raw=path.read_bytes();after=path.stat()
        assert (before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_ino,after.st_size,after.st_mtime_ns),'concurrent mutation'
        row=dict(path=str(path),size=len(raw),sha256=hashlib.sha256(raw).hexdigest())
        if want is not None:assert all(row[k]==want[k] for k in ('size','sha256')),'pin mismatch '+str(path)
        pins.append(row);return raw
    def timeout(signum,frame):raise TimeoutError('50-second one-comparison wall budget')
    signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,50)
    try:
        pins_raw=(STAGE/'pins.json').read_bytes()
        assert hashlib.sha256(pins_raw).hexdigest()==args.pins_sha256,'exact comparison pins'
        config=json.loads(pins_raw);descriptors={p['path']:p for p in config['files']}
        assert descriptors[SOURCE]['sha256']==SOURCE_SHA
        sys.dont_write_bytecode=True
        raw=pinned(SOURCE,descriptors[SOURCE]);A=types.ModuleType('phase536_adapter');A.__file__=str(ROOT/SOURCE)
        exec(compile(raw,str(ROOT/SOURCE),'exec'),A.__dict__)
        count_names=('compare_decoded','compare_projected','project_native','project_model','project_native_final','project_model_final','project_native_callbacks','project_model_callbacks','project_native_api','project_model_api','_snapshot_native','_snapshot_model','_terminal_native','_terminal_model','bindings','strict_json_loads')
        for name in count_names:
            original=getattr(A,name)
            def counted(*args,_name=name,_fn=original,**kwargs):
                calls[_name]+=1;return _fn(*args,**kwargs)
            setattr(A,name,functools.wraps(original)(counted))
        def load(path,want=None):return A.strict_json_loads(pinned(path,want))
        def fixed(path):return load(path,descriptors[str(path)])
        pinned('tests/phase536_independent_actual_compare.py',descriptors['tests/phase536_independent_actual_compare.py'])
        final=fixed(FINAL);assert final['status']=='ACCEPTED_SOURCE_INTERFACES_AND_ACTUAL_B2_NOT_MODEL_VALIDATED'
        controls=fixed(CONTROL);assert controls['status']=='PASS_WRAPPER_CONTROLS_AND_JOINED_B2_NOT_MODEL_VALIDATED' and controls['completed']==[f'{i:02}' for i in range(1,13)]
        assert controls['model_calls']==controls['candidate_imports']==controls['Expected_reads']==controls['Native_calls']==0
        binding=fixed('data/phase536-independent-comparison-source/comparison-binding.json')
        assert set(binding)=={'schema','input_bundle','input_canonical_sha256','input_proof','input_proof_canonical_sha256','candidate_freeze','contract'}
        contract=load(binding['contract']['path'],binding['contract']);assert set(contract['sections'])==set(A.SECTIONS)
        index=fixed(INDEX);expected={Path(row['path']).name:row for row in index['descriptors']}
        assert len(expected)==9 and set(expected)==set(A.EXPECTED_LEAVES)
        capsule=load(index['source_manifest']['path'],index['source_manifest'])
        assert capsule['capture_complete'] is True and capsule['process_clean_exit'] is False
        capfiles={p['path']:p for p in capsule['files']}
        for name,row in expected.items():
            saved=capfiles['output/capture/'+name]
            assert all(saved[k]==row[k] for k in ('size','sha256')),'capsule Expected association'
            assert str(Path(capsule['run'])/'output/capture'/name)==row['path'],'exact029 Expected path'
        model_seal=fixed('data/phase533-case029-actual-model-first-001/output-seal.json')
        assert model_seal['status']=='ACTUAL_OUTPUT_SEALED_NOT_COMPARED' and model_seal['comparison_contract']==binding['contract']
        before=load(MODEL/'before.json',model_seal['files']['before.json'])
        execution=load(MODEL/'execution.json',model_seal['files']['execution.json'])
        gate=load(MODEL/'prepare-gate.json',model_seal['files']['prepare-gate.json'])
        assert execution['status']=='ACTUAL_OUTPUT_SEALED_NOT_COMPARED'
        assert execution['calls']==dict(candidate_import_attempts=1,construct_attempts=1,prepare_attempts=1,prepared_gate_attempts=1,activate_attempts=1,full_run_attempts=1)
        assert execution['tape_position']==execution['tape_records']==297 and execution['full_clock_passes']==1089
        assert execution['expected_reads']==execution['new_original_capture']==execution['comparator_calls']==0
        assert gate['actual_same_instance'] is True and gate['gate']['status']=='PASS_PRE_ACTIVATION_SAME_INSTANCE'
        assert gate['gate']['Tape_position']==gate['gate']['passes_consumed']==0 and gate['gate']['timer_count']==32
        assert before['input_bundle']==binding['input_bundle'] and before['input_proof']==binding['input_proof'] and before['candidate_freeze']==binding['candidate_freeze']
        assert before['sources']==execution['source_after'] and len(before['sources'])==15
        request=load(model_seal['request']['path'],model_seal['request'])
        assert request['root_model_authorized'] is True and request['business_closure']==before['business_closure']==final['business_closure']
        closure=load(request['business_closure']['receipt']['path'],request['business_closure']['receipt'])
        closure_owner=load(request['business_closure']['owner']['path'],request['business_closure']['owner'])
        assert set(closure)=={'schema','extraction_source','guard'}
        for row in closure_owner['files']:pinned(row['path'],row)
        joined=load(final['joined_Source_and_actual']['path'],final['joined_Source_and_actual'])
        assert joined['actual_receipt']==request['business_closure']['receipt'] and joined['Source_applicability']==final['static_Source_part']
        assert joined['guard_canonical_sha256']==hashlib.sha256(json.dumps(closure['guard'],sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
        assert joined['input_bundle']==binding['input_bundle'] and joined['input_proof']==binding['input_proof'] and joined['candidate_freeze']==binding['candidate_freeze']
        for path,row in execution['input_after'].items():
            assert len(execution['input_after'])==18
            pinned(path,row)
        expected_watched={}
        for key,row in request.items():
            if key in ('schema','case_id','root_model_authorized','business_closure'):continue
            path=Path(row['path']);path=path if path.is_absolute() else ROOT/path
            expected_watched[str(path)]={k:row[k] for k in ('size','sha256')}
        for row in [model_seal['request'],*request['business_closure'].values(),closure['extraction_source'],descriptors['data/phase531-independent-final-acceptance/owned-files.json']]:
            path=Path(row['path']);path=path if path.is_absolute() else ROOT/path
            expected_watched[str(path)]={k:row[k] for k in ('size','sha256')}
        assert execution['input_after']==expected_watched,'all18 actual watched identities'
        freeze=load(binding['candidate_freeze']['path'],binding['candidate_freeze']);assert len(freeze['files'])==15
        for row in freeze['files']:
            assert before['sources'][str(ROOT/row['path'])]=={k:row[k] for k in ('size','sha256')}
            pinned(row['path'],row)
        bundle=load(binding['input_bundle']['path'],binding['input_bundle'])
        proof=load(binding['input_proof']['path'],binding['input_proof'])
        for value,key in [(bundle,'input_canonical_sha256'),(proof,'input_proof_canonical_sha256')]:
            assert hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()==binding[key]
        assert len(bundle['draws'])==297
        result=load(MODEL/'model-output.json',model_seal['files']['model-output.json'])
        assert model_seal['files']['model-output.json']==config['model_output']
        assert not any(n.startswith(('native_replay_v7','native_replay_v8')) for n in sys.modules)
        allowed={row['path'] for row in expected.values()} | {str(ROOT/SOURCE),str(Path(__file__).resolve())}
        def audit(event,args):
            if event.startswith(('subprocess.','socket.')) or event in ('os.system','os.exec','os.spawn','os.fork','os.posix_spawn'):
                raise RuntimeError('forbidden comparator external operation '+event)
            if event!='open' or not isinstance(args[0],(str,bytes,os.PathLike)):return
            path=Path(os.path.abspath(os.fsdecode(args[0])));flags=args[2] or 0
            writing=bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
            if writing:assert path.is_relative_to(OUT),'write outside comparison output'
            else:assert str(path) in allowed or path.is_relative_to(OUT),'unapproved comparator read '+str(path)
            reads.append(dict(path=str(path),operation='write' if writing else 'read'))
        output_refs.append(dump(OUT/'before.json',dict(schema='phase536-before-Expected/1',pins=pins.copy(),expected_index=index,model_already_sealed=True,model_output_payload_reads_this_attempt=1,EXPECTED_reads_so_far=0,comparison_binding=binding,actual_B1=gate['gate'],business_closure=request['business_closure'],frozen_contract_sha256=A.CONTRACT_SHA256,provenance_limit='Existing029 complete capture; process_clean_exit=false preserved; no recapture or schema replay')))
        sys.addaudithook(audit)
        stage='read_and_decode_nine_EXPECTED_leaves';native={}
        for name,want in expected.items():
            expected_opens.append(name);raw=pinned(want['path'],want)
            if name.endswith('.jsonl'):
                lines=raw.splitlines();assert raw.endswith(b'\n') and all(line.strip() for line in lines),'complete nonblank JSONL'
                native[name]=[A.strict_json_loads(line) for line in lines]
            else:native[name]=A.strict_json_loads(raw)
        stage='single_compare_decoded'
        comparison=A.compare_decoded(native,result,bundle,proof,binding)
        assert calls['compare_decoded']==1
        output_refs.append(dump(OUT/'comparison.json',comparison))
        report['status']='PASS_EIGHT_BUSINESS_SECTIONS_ROOT_ACCEPTANCE_PENDING' if comparison['status']=='PASS' else 'FAIL_STRICT_BUSINESS_DIFFERENCES'
        report['first_differences']=comparison['first_differences']
        stage='source_readback';pinned(SOURCE,descriptors[SOURCE])
    except BaseException as exc:
        report['status']='FAIL_FIRST_CARRIER_OR_PROJECTION_ERROR_NO_RETRY'
        frames=[];tb=exc.__traceback__
        while tb is not None:
            frames.append(dict(file=tb.tb_frame.f_code.co_filename,line=tb.tb_lineno,function=tb.tb_frame.f_code.co_name));tb=tb.tb_next
        report['failure']=dict(stage=stage,type=type(exc).__name__,message=str(exc),traceback_frames=frames)
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
        report.update(elapsed_seconds=time.monotonic()-began,calls=dict(calls),pins=pins,EXPECTED_payload_open_attempts=expected_opens,EXPECTED_payload_successful_pins=[p for p in pins if '/output/capture/' in p['path']],accesses_after_Expected_gate=reads.copy(),model_invocations=0,original_INPUT12_reads=0,new_native_capture=0,contract_sha256='a261b2b262350653ee31d69bed5706f3feb54893b4e577f49f3337a270ef66a3',model_imports=0,native_capture_complete=True,native_process_clean_exit=False)
        output_refs.append(dump(OUT/'result.json',report));dump(OUT/'owned-files.json',dict(schema='phase536-actual-comparison-owner/1',status=report['status'],files=output_refs))
    print(json.dumps(dict(status=report['status'],elapsed_seconds=report['elapsed_seconds'],calls=report['calls'],output=str(OUT))))
    return 0 if report['status'].startswith('PASS') else 1


if __name__=='__main__':raise SystemExit(main())
