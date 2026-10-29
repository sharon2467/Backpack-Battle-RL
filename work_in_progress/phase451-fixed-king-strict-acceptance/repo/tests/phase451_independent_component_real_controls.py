"""Targeted component serializer controls; no component/model imports."""
from pathlib import Path
from copy import deepcopy
from collections import Counter
import functools
import hashlib
import json
import struct
import time
import traceback
import types

R=Path(__file__).resolve().parents[1]
SOURCE='tests/phase451_pure_business_output_v4.py'
SHA='ee905f14176415a09f58ee7d657e08b6008a70771bd74075fe0587bf9a966515'
OUT=R/'data/phase451-independent-output-controls-first-001'


def main():
    OUT.mkdir(exist_ok=False);began=time.monotonic();cases=[];reads=[];calls=Counter()
    result=dict(schema='phase451-independent-component-REAL-controls/1',status='RUNNING',cases=cases)
    def pin(path,digest):
        b=(R/path).read_bytes();actual=hashlib.sha256(b).hexdigest();assert actual==digest
        reads.append(dict(path=path,size=len(b),sha256=actual));return b
    def ok(name):cases.append(dict(name=name,status='PASS'))
    def reject(name,fn):
        try:fn()
        except ValueError as exc:cases.append(dict(name=name,status='PASS',rejection=str(exc)))
        else:raise AssertionError('accepted malformed '+name)
    try:
        raw=pin(SOURCE,SHA);A=types.ModuleType('adapter451');exec(compile(raw,str(R/SOURCE),'exec'),A.__dict__)
        for name in ('decode_native','project_model_api','project_native_api','bindings','first_difference'):
            original=getattr(A,name)
            def count(*a,_name=name,_fn=original,**kw):calls[_name]+=1;return _fn(*a,**kw)
            setattr(A,name,functools.wraps(original)(count))
        bundle=A.strict_json_loads(pin('data/phase441-fixed-A-input-first-001/input-bundle.json','c87525f35adf8fa3793cc5d1440dff420dc55f3a24c77e520766b01e8963ae2c'));B=A.bindings(bundle)
        def component(value):
            if type(value) is float:return dict(type='float',binary64_le=struct.pack('<d',value).hex(),display=str(value))
            if type(value) is bool:return dict(type='bool',value=value)
            if type(value) is int:return dict(type='int',decimal=str(value))
            if type(value) is str:return dict(type='string',value=value)
            if type(value) is list:return [component(x) for x in value]
            raise AssertionError('unexpected synthetic component field')
        real=component(-0.0)
        assert A.bits(A.decode_native(real,B))=='8000000000000000'
        assert A.bits(A.decode_native(dict(real,display='different nonauthoritative text'),B))=='8000000000000000'
        assert A.decode_native(dict(type='float',display='1.5',binary64_be=A.bits(1.5)),B)==1.5
        ok('LE_display_exact_shape_bits_and_BE_regression')
        rejects=[('display_type',dict(real,display=0)),('unknown_extra',dict(real,extra=0)),('missing_bits',dict(type='float',display='0')),
                 ('both_endian',dict(real,binary64_be=A.bits(-0.0))),('bad_hex',dict(real,binary64_le='bad')),
                 ('nonfinite',dict(real,binary64_le='000000000000f07f')),('wrong_type',dict(real,type='int'))]
        for name,value in rejects:reject(name,lambda value=value:A.decode_native(value,B))
        name='fatigue:start';node=B['nodes'][name];h=bundle['runtime']['frame_clock']['checkpoint'];p=h['physics_frame']+1;i=h['idle_frame']+1
        nr=[];mr=[]
        for edge in ('before','after'):
            n=deepcopy(node);n['internal_physics']=edge=='after'
            timer=dict(node=n,process_mode=0,wait_time=1.0 if edge=='before' else 14.0,time_left=0.0 if edge=='before' else 14.0,
                       one_shot=True,autostart=False,paused=False,stopped=edge=='before')
            public={k:component(v) for k,v in timer.items() if k!='node'}
            public.update({key:component(value) for key,value in dict(path=n['path'],index=n['positions'][-1],ancestor_positions=n['positions'],process_priority=n['priority'],**{k:n[k] for k in A.FLAGS}).items()})
            args=[dict(type='int',decimal='14')]
            nr.append(dict(sequence=1233+len(nr),edge='timer_'+edge,site='Interface/CombatTimer/CombatTimer.gd::start',
                subject=dict(type='native_ref',native_id=n['native_id'],role=name,**{'class':'Timer'}),stamp=dict(physics_frame=str(p),idle_frame=str(i)),
                payload=dict(role=name,operation='start',argc=1,args=deepcopy(args),public_before=timer if edge=='before' else None,public_after=timer if edge=='after' else None)))
            row=dict(role=name,edge=edge,operation='start',argc=1,args=args,physics_frame=p,idle_frame=i,state=dict(public=public))
            if edge=='after':row.update(helper_status=dict(ok=True,error=None),native_return_semantics=dict(typed={'type':'null'},basis='SOURCE_VOID_NOT_SAMPLED'))
            mr.append(row)
        model={'pure_combat_diagnostics':{'api':mr}}
        native=A.project_native_api(nr,bundle,B);projected=A.project_model_api(model,B)
        assert A.first_difference(native,projected) is None
        poisoned=deepcopy(model)
        for row in poisoned['pure_combat_diagnostics']['api']:
            for value in row['state']['public'].values():
                if isinstance(value,dict) and value.get('type')=='float':value['display']='ignored display'
        assert A.first_difference(native,A.project_model_api(poisoned,B)) is None
        poisoned['pure_combat_diagnostics']['api'][1]['state']['public']['time_left']=component(13.0)
        assert A.first_difference(native,A.project_model_api(poisoned,B))
        changed=deepcopy(model)
        for row in changed['pure_combat_diagnostics']['api']:row['args']=[dict(type='float',binary64_be=A.bits(14.0))]
        assert A.first_difference(native,A.project_model_api(changed,B))
        ok('actual_component_typed_public_API_shape_business_and_arg_type')
        pin(SOURCE,SHA);result['status']='PASS_SYNTHETIC_ADAPTER_INTERFACE_CONTROLS'
    except BaseException as exc:
        result['status']='FAIL_FIRST_ERROR_NO_RETRY';result['error']=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
    result.update(reads=reads,calls=dict(calls),elapsed_seconds=time.monotonic()-began,EXPECTED_reads=0,model_calls=0,component_imports=0,actual_comparisons=0)
    b=(json.dumps(result,indent=2)+'\n').encode();(OUT/'result.json').write_bytes(b)
    owner=dict(schema='phase451-targeted-control-owner/1',files=[dict(path=str((OUT/'result.json').relative_to(R)),size=len(b),sha256=hashlib.sha256(b).hexdigest())]);(OUT/'owned-files.json').write_text(json.dumps(owner,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],cases=len(cases),seconds=result['elapsed_seconds'])))
    return 0 if result['status'].startswith('PASS') else 1


if __name__=='__main__':raise SystemExit(main())
