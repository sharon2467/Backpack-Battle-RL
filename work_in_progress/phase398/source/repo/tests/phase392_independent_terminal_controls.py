"""Exact391 pure terminal and host-file component units; never a native capture."""
from pathlib import Path
import argparse
import ast
import collections
import copy
import dataclasses
import hashlib
import importlib.abc
import importlib.util
import json
import math
import os
import re
import stat
import struct
import sys
import sysconfig
import traceback
import types
# Trusted standard-library bootstrap before audit, including inherited helper imports.
import contextlib, fcntl, selectors, shutil, signal, subprocess, time, zipfile

R = Path(__file__).resolve().parents[1]
SD = R/'data/phase392-independent-execution-source'
D = R/'data/phase392-independent-terminal-first-001'
MIRROR = SD/'source-root'
TRACKED = {'decode_clock','validate_terminal_evidence','validate_terminal_receipt',
           'validate_terminal_diagnostics','read_terminal_expected_controls',
           'validate_active_source_tuple','load_terminal_schema'}
STATIC_IDS = {'C07','C20','C23','C26','C31','C32'}


def dump(path, value):
    with path.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n')


def identity(path):
    raw=path.read_bytes()
    return dict(size=len(raw),sha256=hashlib.sha256(raw).hexdigest())


class ExactSourceFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def __init__(self, modules): self.modules=modules
    def find_spec(self, fullname, path=None, target=None):
        if fullname in self.modules:
            return importlib.util.spec_from_loader(fullname,self,origin=str(self.modules[fullname]))
        return None
    def create_module(self,spec): return None
    def exec_module(self,module):
        path=self.modules[module.__name__]
        module.__file__=str(path)
        exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true',required=True)
    parser.parse_args()
    D.mkdir(exist_ok=False)
    closure=json.loads((SD/'read-closure.json').read_text())
    # The execution-source owner and its exact self hash are verified by the launcher.
    for row in closure['mirror_files']:
        path=MIRROR/row['path']; info=path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or identity(path)!={k:row[k] for k in ('size','sha256')}:
            raise ValueError('frozen mirror drift: '+row['path'])
    contract=json.loads((SD/'execution-contract.json').read_text())
    plan=json.loads((MIRROR/'data/phase392-independent-preparation/contract.json').read_text())
    freeze=json.loads((MIRROR/'data/phase391-terminal-source/combined-source-freeze.json').read_text())
    modules={name:MIRROR/rel for name,rel in contract['source_modules'].items()}
    stdlib=Path(sysconfig.get_paths()['stdlib']).resolve()
    exact_reads={str((MIRROR/x['path']).resolve()) for x in closure['mirror_files']}
    exact_reads.update(str((R/x['path']).resolve()) for x in closure['local_files'])
    audit=[];blocked=[];executions=[];profile=collections.Counter();top_calls=[];results=[]
    def under(path,root): return path==root or root in path.parents
    def hook(event,args):
        if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)):
            path=Path(os.fsdecode(args[0])).resolve()
            mode=args[1]; flags=args[2]
            writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC)))
            allowed=under(path,D) or (not writing and (str(path) in exact_reads or (under(path,stdlib) and 'site-packages' not in path.parts and 'dist-packages' not in path.parts)))
            audit.append(dict(event='open',path=str(path),write=writing,allowed=allowed))
            if not allowed:
                blocked.append(audit[-1]);raise PermissionError('exact SOURCE/owned-output read boundary: '+str(path))
        if event.startswith(('subprocess.','socket.')) or event in ('os.system','os.exec','os.posix_spawn','os.fork'):
            blocked.append(dict(event=event));raise PermissionError('no process/network')
        if event=='exec':
            filename=args[0].co_filename
            if filename.startswith(str(MIRROR)+'/'):
                executions.append(filename)
    def profiler(frame,event,arg):
        if event=='call' and frame.f_code.co_name in TRACKED and frame.f_code.co_filename.startswith(str(MIRROR)+'/'):
            profile[(str(Path(frame.f_code.co_filename).relative_to(MIRROR)),frame.f_code.co_name)]+=1
    sys.addaudithook(hook)
    sys.meta_path.insert(0,ExactSourceFinder(modules))
    sys.setprofile(profiler)
    failure=None
    try:
        import phase391_king_observer_schema as schema
        import phase391_oracle_host as host
        for name in ('validate_terminal_evidence','validate_terminal_receipt','validate_terminal_diagnostics'):
            if getattr(schema.schema,name) is not getattr(schema,name):raise AssertionError('real export identity')
        def invoke(case,name,fn,args,accept):
            entry=dict(case=case,api=name,expected='ACCEPT' if accept else 'REJECT')
            top_calls.append(entry)
            try:value=fn(*args)
            except ValueError as exc:
                entry.update(actual='REJECT',error=str(exc))
                if accept:raise AssertionError('unexpected rejection '+case+' '+name) from exc
                return None
            entry['actual']='ACCEPT'
            if not accept:raise AssertionError('unexpected acceptance '+case+' '+name)
            return value
        def carrier(base):
            h=base['checkpoint_counter_notation']
            bits=struct.pack('>d',schema.PHYSICS_DELTA).hex()
            return dict(schema=schema.SCHEMA,lineage='fresh_activate_idle_tail',environment=dict(physics_fps=60,scale_bits='3ff0000000000000',paused=False),checkpoint=dict(phase='activate_items_idle_tail',physics_frame=h['physics_frame'],idle_frame=h['idle_frame'],util_frame_counter=h['physics_frame'],util_time_bits='0000000000000000',util_clock_time_bits='0000000000000000'),passes=[dict(row,delta_bits=bits) for row in base['rows_notation']])
        def endpoint(base):
            last=base['rows_notation'][-1]
            return dict(schema=schema.TERMINAL_ENDPOINT_SCHEMA,terminal_policy=schema.TERMINAL_POLICY,phase='idle_pre_internal_flush',physics_frame=last['physics_frame'],idle_frame=last['idle_frame'],passes=len(base['rows_notation']),fx_exact_comparison='NOT_EVALUATED_REQUIRES_MODEL',**base['expected'])
        def evidence_objects(base):
            end=endpoint(base); p=end['physics_frame']; i=end['idle_frame']
            cut={key:end[key] for key in schema.TERMINAL_CUT_KEYS if key!='schema'};cut['schema']=schema.TERMINAL_CONTROL_SCHEMA
            receipt=dict(source_window_complete=True,failed=False,clock_closed=True,ui_closed=True,cleanup=base['cleanup_clock'],clock_passes=end['passes'],native_capture_accepted=False,collector_archive_pending=True,terminal_cut=copy.deepcopy(cut))
            ack=dict(receiver_id='1001',physics=p,idle=i,serial=1)
            control=dict(phase='FINALIZED',dispatching=False,emit_count=1,receiver_available=True,receiver_id='1001',physics=p,idle=i,ack=ack,script_emit_return=None,script_emit_return_observed=True,native_emit_error_available=False,native_emit_error=None,finish_return=True,failed=False,closed=True,complete=True,clock_closed=True,ui_closed=True,first_error=None,ready_connect=dict(physics=0,idle=0),diagnostic_error=None,terminal_cut=copy.deepcopy(cut))
            validation=dict(cut=dict(physics=p,idle=i,preinternal=True),full_snapshot_reads=1,terminal_cut=copy.deepcopy(cut),native_checks_pass=True,end_barrier=True)
            def connection(source,target,method):
                return dict(ordinal=0,source_has_key=True,source_variant_type=2,source_available=True,source_native_id=source,target_has_key=True,target_variant_type=2,target_available=True,target_native_id=target,method=method,flags=0,binds_count=0,binds=[])
            private=dict(complete_seen=True,row_count=1,rows=[connection('1002','1001','on_idle_source_cut')],reason=None)
            tree=dict(complete_seen=True,row_count=1,rows=[connection('1001','1002','clock_idle_signal')],reason=None)
            emitting=copy.deepcopy(control);emitting.update(phase='EMITTING',dispatching=True,ack=None,script_emit_return_observed=False,finish_return=None)
            returned=copy.deepcopy(control);returned.update(phase='RETURNED',finish_return=None)
            diagnostics=[]
            for n,(reason,value) in enumerate((('EMITTING',emitting),('RETURNED_ACK_CHECKED',returned),('FINALIZED',control))):
                payload=dict(control=copy.deepcopy(value))
                if n==0:payload.update(private_connections=private,tree_connections=tree)
                diagnostics.append(dict(schema='phase391-source-control/1',control_sequence=n,site='emit_source_idle_cut_once',reason=reason,physics=p,idle=i,in_physics=False,observer_sequence=50,ui_sequence=20,clock_passes=end['passes'],payload=payload))
            return end,receipt,control,validation,diagnostics
        def files_for(case,base,end,receipt,validation,diagnostics):
            cap=D/'unit-files'/case;cap.mkdir(parents=True,exist_ok=False)
            raw=carrier(base); header={key:value for key,value in raw.items() if key!='passes'}
            for name,value in (('king-capture-endpoint.json',end),('observer7-status.json',receipt),('validation.json',validation),('king-clock-checkpoint.json',header)):
                dump(cap/name,value)
            for name,rows in (('king-clock-passes.jsonl',raw['passes']),('source-window-diagnostic.jsonl',diagnostics)):
                with (cap/name).open('x',encoding='utf-8') as stream:
                    for row in rows:stream.write(json.dumps(row,sort_keys=True)+'\n')
            dump(cap/'UNIT-PROVENANCE.json',dict(synthetic_SOURCE_unit=True,actual_native=False,full12=False,model_bundle=False,synthetic_identity_notation=['1001','1002']))
            return cap
        for logical in plan['cases']:
            case=logical['id']
            if case in STATIC_IDS:
                results.append(dict(case=case,status='SOURCE_ONLY_STATIC_REVIEW_NO_LANGUAGE_EXECUTION'));continue
            base=copy.deepcopy(plan['baseline_notation_only'][logical['baseline']])
            if case=='C09':
                base['rows_notation'] += [dict(kind='physics',physics_frame=104,idle_frame=12),dict(kind='idle',physics_frame=104,idle_frame=12)]
                base['expected'].update(first_eligible_idle_pass=6,observed_future_physics_signals=3)
            elif case=='C10':
                base['rows_notation'].append(dict(kind='idle',physics_frame=103,idle_frame=12));base['expected']['first_eligible_idle_pass']=5
            elif case=='C12':
                base['rows_notation']=[dict(kind='physics',physics_frame=101,idle_frame=11),dict(kind='physics',physics_frame=102,idle_frame=11),dict(kind='idle',physics_frame=102,idle_frame=11)]
                base['expected'].update(first_eligible_idle_pass=3,observed_future_physics_signals=1)
            elif case=='C13':base['rows_notation']=base['rows_notation'][:-1]
            elif case=='C25':
                base['rows_notation']=base['rows_notation'][:2];base['expected'].update(first_eligible_idle_pass=2,observed_future_physics_signals=0)
            end,receipt,control,validation,diagnostics=evidence_objects(base)
            if case=='C08':receipt['cleanup']['is_in_physics_frame']=False
            elif case=='C11':base['rows_notation'].append(dict(kind='physics',physics_frame=104,idle_frame=12))
            elif case=='C14':base['rows_notation'][1]['physics_frame']=103
            elif case=='C15':end['cleanup_anchor_pass']=True
            elif case=='C16':end['observed_future_physics_signals']=2
            elif case=='C17':receipt['terminal_cut']['first_eligible_idle_pass']=5
            elif case=='C19':
                diagnostics.insert(1,copy.deepcopy(diagnostics[0]))
                for n,row in enumerate(diagnostics):row['control_sequence']=n
            elif case=='C21':diagnostics[0]['payload']['control']['phase']='IDLE'
            elif case=='C22':control.update(native_emit_error_available=True,native_emit_error=0)
            elif case=='C24':control['physics']=104
            elif case=='C27':receipt['cleanup']['idle_frame']=99
            elif case=='C28':end['cleanup_anchor_pass']=5
            elif case=='C29':diagnostics[0]['payload']['control']['script_emit_return_observed']=True
            elif case=='C30':control['finish_return']=1
            case_dir=D/'logical-inputs'/case;case_dir.mkdir(parents=True,exist_ok=False)
            dump(case_dir/'input.json',dict(provenance='SYNTHETIC_SOURCE_UNIT_NOT_NATIVE',clock=carrier(base),endpoint=end,receipt=receipt,control=control,validation=validation,diagnostics=diagnostics))
            if case=='C14':
                invoke(case,'decode_clock',schema.decode_clock,(carrier(base),),False)
            elif case=='C18':
                bad=copy.deepcopy(freeze);bad['profile']='observer7-355-native-single-king-A/1'
                invoke(case,'host.read_terminal_expected_controls',host.read_terminal_expected_controls,(MIRROR,bad,D/'unit-files/C03'),False)
            else:
                clock=invoke(case,'decode_clock',schema.decode_clock,(carrier(base),),True)
                if case in {'C19','C21','C29'}:
                    invoke(case,'validate_terminal_diagnostics',schema.schema.validate_terminal_diagnostics,(diagnostics,),False)
                elif case in {'C17','C22','C24','C30'}:
                    invoke(case,'validate_terminal_receipt',schema.schema.validate_terminal_receipt,(end,clock,receipt,control,validation),False)
                else:
                    proof=invoke(case,'validate_terminal_evidence',schema.schema.validate_terminal_evidence,(end,clock,receipt['cleanup']),case in {'C01','C02','C03','C04','C05','C06'})
                    if proof is not None:
                        for key,value in base['expected'].items():
                            if proof[key]!=value or type(proof[key]) is not type(value):raise AssertionError('predeclared typed proof '+case+' '+key)
                        if proof['no_model_stop_command'] is not True:raise AssertionError('expected-only proof')
                if case in {'C03','C17'}:
                    cap=files_for(case,base,end,receipt,validation,diagnostics)
                    hp=invoke(case,'host.read_terminal_expected_controls',host.read_terminal_expected_controls,(MIRROR,freeze,cap),case=='C03')
                    if hp is not None and (hp['expected_control_only'] is not True or hp['input_bundle_created'] is not False):raise AssertionError('host component dataflow')
            results.append(dict(case=case,status='OBSERVED_EXPECTED_API_OUTCOME'))
    except BaseException as exc:
        failure=dict(error=repr(exc),traceback=traceback.format_exc(),current_case=locals().get('case'))
    finally:
        sys.setprofile(None)
    report=dict(schema='phase392-first-component-results/1',status='FIRST_BATCH_PASS' if failure is None else 'FIRST_BATCH_FAILED_STOPPED',failure=failure,logical_results=results,top_level_API_calls=top_calls,
                observed_public_internal_call_counts=[dict(source=k[0],function=k[1],calls=v) for k,v in sorted(profile.items())],
                exact_source_execs=executions,unique_executed_source_files=sorted(set(executions)),
                counts=dict(logical_dynamic_completed=sum(r['status']=='OBSERVED_EXPECTED_API_OUTCOME' for r in results),logical_source_only=sum(r['status'].startswith('SOURCE_ONLY') for r in results),top_level_API_calls=len(top_calls),Godot=0,native=0,models=0,Engine=0,RNG=0,actual_inputbuilds=0,projection=0,actualpool=0),
                limits=dict(full12_positive=False,wholehost=False,model_or_King_admission=False,synthetic_SOURCE_controlfiles_only=True,producer_language_NOT_EXECUTED=True))
    dump(D/'report.json',report)
    dump(D/'audit.json',dict(schema='phase392-open-audit/1',events=audit,blocked=blocked,bootstrap='Trusted stdlib and mirror pin/read before audit; no SUT executes before hook',scope='File-open/process/network audit; metadata stat calls not claimed as audited reads'))
    files=[dict(path=str(p.relative_to(R)),**identity(p)) for p in sorted(D.rglob('*')) if p.is_file()]
    dump(D/'joint-seal.json',dict(schema='phase392-first-results-joint-seal/1',files=files,models=0,native=0))
    print(json.dumps(dict(status=report['status'],failure=failure,counts=report['counts'],blocked=len(blocked)),indent=2))
    if failure is not None:raise SystemExit(1)


if __name__=='__main__':main()
