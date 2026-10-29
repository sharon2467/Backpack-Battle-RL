"""Synthetic new-adapter controls only; no EXPECTED or candidate execution."""
from pathlib import Path
from copy import deepcopy
from collections import Counter
import ast
import functools
import hashlib
import json
import signal
import time
import traceback
import types

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'tests/phase448_pure_business_output_v2.py'
SOURCE_SHA = '726652a8c6c3dabaefb060baccae49bbc5d06afb3ef91989d6fedda0987c376f'
BUNDLE = 'data/phase441-fixed-A-input-first-001/input-bundle.json'
OUT = ROOT / 'data/phase448-independent-output-controls-first-001'


def main():
    OUT.mkdir(exist_ok=False)
    start = time.monotonic(); calls = Counter(); cases = []; reads = []
    report = dict(schema='phase448-independent-output-controls/1', status='RUNNING', cases=cases)
    def pin(rel, digest):
        raw = (ROOT / rel).read_bytes(); actual = hashlib.sha256(raw).hexdigest()
        reads.append(dict(path=rel,size=len(raw),sha256=actual))
        assert actual == digest, 'pin drift '+rel
        return raw
    def ok(name):cases.append(dict(name=name,status='PASS'))
    def reject(name, fn):
        try:fn()
        except ValueError as exc:cases.append(dict(name=name,status='PASS',rejection=str(exc)))
        else:raise AssertionError('negative accepted: '+name)
    def timeout(signum, frame):raise TimeoutError('30s helper budget')
    try:
        signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,30)
        raw=pin(SOURCE,SOURCE_SHA); A=types.ModuleType('phase448_adapter')
        exec(compile(raw,str(ROOT/SOURCE),'exec'),A.__dict__)
        for name in [n.name for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)]:
            original=getattr(A,name)
            def counted(*args,_name=name,_fn=original,**kwargs):
                calls[_name]+=1
                return _fn(*args,**kwargs)
            setattr(A,name,functools.wraps(original)(counted))
        bundle=A.strict_json_loads(pin(BUNDLE,'c87525f35adf8fa3793cc5d1440dff420dc55f3a24c77e520766b01e8963ae2c'))
        B=A.bindings(bundle)
        assert len(B['timers'])==33 and len(B['nodes'])==78
        reject('input_identity_drift',lambda:A.bindings(dict(bundle,synthetic_seed=0)))
        assert A.first_difference(0.0,-0.0) and A.first_difference(False,0) and A.first_difference(1,1.0)
        assert A.first_difference({1:0},{'1':0}) and A.first_difference([1,2],[2,1])
        reject('duplicate_JSON',lambda:A.strict_json_loads('{"x":1,"x":2}'))
        reject('nonfinite_JSON',lambda:A.strict_json_loads('1e999'))
        reject('BOOL_typed_INT',lambda:A.decode_native(dict(type='int',decimal=True),B))
        reject('noncanonical_INT',lambda:A.decode_native(dict(type='int',decimal='01'),B))
        reject('duplicate_typed_dictionary',lambda:A.decode_native(dict(type='dictionary',entries=[dict(key=dict(type='int',decimal='1'),value=0)]*2),B))
        ok('strict_types_bits_keys_order')
        def ref(name):
            n=B['nodes'][name]
            return dict(type='native_ref',native_id=n['native_id'],role=name,**{'class':n['class']})
        assert A.decode_native(ref('item:P:12'),B)=='P:12'
        reject('foreign_native_ref',lambda:A.decode_native(dict(ref('item:P:12'),native_id='999999999'),B))
        ok('bound_reference_positive')

        chars=[]; live={}
        for side in ('P','O'):
            items=[]
            for ident,item in B['items'].items():
                if not ident.startswith(side+':'):continue
                items.append(dict(instance=ident,fields=dict(buffPowers={},buffAmplificationChances={},business=ident)))
                live[ident]=dict(item_index=item['item_index'],potion_full=False)
            chars.append(dict(instance=side,stats={},fields=dict(typedDamageFactors={},invulBubbleVisible=False,invulnerable=False),items=items))
        model=dict(final=dict(native_rule_state=dict(characters=chars,rules=dict(values={})),items=live,
                             game=dict(roundResults=[0]),event_bus={},timestamp=1.0,time_advance=0.0,fatigue_counter=0,winner='P'))
        native=dict(characters=deepcopy(chars),rules=dict(values={}),game=dict(roundResults=[0]),event_bus={},
                    timer=dict(combatTime=1.0,timeAdvance=0.0,fatigueCounter=0))
        for c in native['characters']:
            c['fields'].update(characterName='display',chibi=False)
            for i in c['items']:
                i['observer7_fields']={'isFull':False} if B['items'][i['instance']]['item_index']==19 else {}
                i['observer7_timers']={}
        nf=A.project_native_final(native,B);mf=A.project_model_final(model,B)
        assert A.first_difference(nf,mf) is None
        poison=deepcopy(native)
        poison['characters'][0]['fields'].update(characterName='POISON',chibi=True,invulBubbleVisible=True)
        assert A.first_difference(nf,A.project_native_final(poison,B)) is None
        poison['characters'][0]['fields']['invulnerable']=True
        assert A.first_difference(nf,A.project_native_final(poison,B))
        full=deepcopy(model);full['final']['items']['P:18']['potion_full']=True
        assert A.first_difference(mf,A.project_model_final(full,B))
        full['final']['items']['P:18']['potion_full']=1
        reject('Potion_BOOL_required',lambda:A.project_model_final(full,B))
        del full['final']['items']['P:18']['potion_full']
        try:A.project_model_final(full,B)
        except KeyError:ok('Potion_missing_rejected')
        else:raise AssertionError('Potion absent silently defaulted')
        ok('synthetic_final_display_business_and_live_Potion')

        h=bundle['runtime']['frame_clock']['checkpoint'];p=h['physics_frame']+1;i=h['idle_frame']+1
        def callback(name,mode):
            return dict(kind='source_callback',role=name,mode=mode,physics_frame=p,idle_frame=i,
                        delta_bits=A.bits(0.125),util_time_bits=A.bits(1.0),combat_time_bits=A.bits(0.5))
        callbacks=[callback('game',0),callback('game',1)]+[callback('item:'+ident,1) for ident in B['items']]
        callbacks += [callback('util',0),callback('util',1)]
        mcb={'pure_combat_diagnostics':{'callbacks':callbacks}}
        projected=A.project_model_callbacks(mcb,B);assert [x['mode'] for x in projected]==[0,1]
        reject('foreign_item_idle_not_swallowed',lambda:A.project_model_callbacks({'pure_combat_diagnostics':{'callbacks':[callback('item:FOREIGN',1)]}},B))
        native_cb=[]
        for j,site in enumerate(('Utility/Util.gd::_physics_process','Utility/Util.gd::_process')):
            native_cb.append(dict(schema='observer7-record/1',sequence=1233+j,channel='runtime',site=site,edge='enter',subject=ref('util'),
                stamp=dict(physics_frame=str(p),idle_frame=str(i),util_time=1.0,combat_time=0.5,phase='synthetic'),payload=dict(arguments=dict(delta=0.125))))
        A._runtime_rows(native_cb,B)
        assert A.first_difference(A.project_native_callbacks(native_cb,bundle,B),projected) is None
        assert A.first_difference(projected,A.project_model_callbacks({'pure_combat_diagnostics':{'callbacks':list(reversed(callbacks))}},B))
        trailing=deepcopy(native_cb);trailing.append(dict(deepcopy(trailing[-1]),sequence=1235))
        assert len(A.project_native_callbacks(trailing,bundle,B))==3
        ok('exact41_noop_order_and_trailing_callback_retention')

        def ntimer(name):
            return dict(node=deepcopy(B['nodes'][name]),process_mode=0,wait_time=1.0,time_left=0.0,
                        one_shot=not name.startswith('tick:'),autostart=False,paused=False,stopped=True)
        def mtimer(name):
            t=ntimer(name);n=t.pop('node')
            t.update(path=n['path'],index=n['positions'][-1],ancestor_positions=n['positions'],process_priority=n['priority'])
            t.update({k:n[k] for k in A.FLAGS});return t
        nrows=[];mrows=[]
        for name,args,site in [('tick:P',[],'Core/Character.gd::combatStart'),('fatigue:start',[dict(type='int',decimal='14')],'Interface/CombatTimer/CombatTimer.gd::start'),('invu:P',[dict(type='float',binary64_be=A.bits(1.5))],'Core/Character.gd::makeInvulnerable')]:
            for edge in ('before','after'):
                nrows.append(dict(sequence=1233+len(nrows),edge='timer_'+edge,site=site,subject=ref(name),
                    stamp=dict(physics_frame=str(p),idle_frame=str(i)),payload=dict(role=name,operation='start',argc=len(args),args=deepcopy(args),
                    public_before=ntimer(name) if edge=='before' else None,public_after=ntimer(name) if edge=='after' else None)))
                row=dict(role=name,edge=edge,operation='start',argc=len(args),args=deepcopy(args),physics_frame=p,idle_frame=i,state=dict(public=mtimer(name),private_left_bits='unobserved'))
                if edge=='after':row.update(helper_status=dict(ok=True,error=None),native_return_semantics=dict(typed={'type':'null'},basis='SOURCE_VOID_NOT_SAMPLED'))
                mrows.append(row)
        apim={'pure_combat_diagnostics':{'api':mrows}}
        np=A.project_native_api(nrows,bundle,B);mp=A.project_model_api(apim,B);assert A.first_difference(np,mp) is None
        for field,value in [('type','other'),('role','invu:O'),('class','Node'),('native_id',B['nodes']['invu:O']['native_id']),('extra',1)]:
            bad=deepcopy(nrows);bad[0]['subject'][field]=value
            reject('Timer_subject_'+field,lambda bad=bad:A.project_native_api(bad,bundle,B))
        bad=deepcopy(apim)
        for row in bad['pure_combat_diagnostics']['api'][2:4]:row['args']=[dict(type='float',binary64_be=A.bits(14.0))]
        assert A.first_difference(np,A.project_model_api(bad,B))
        reject('Timer_missing_pair',lambda:A.project_native_api(nrows[:-1],bundle,B))
        poison=deepcopy(apim)
        for row in poison['pure_combat_diagnostics']['api']:row['state']['private_left_bits']='different-unobserved'
        assert A.first_difference(mp,A.project_model_api(poison,B)) is None
        ok('Timer_arity_Variant_subject_pairs_private_partition')

        passes=bundle['runtime']['frame_clock']['passes'];anchor=len(passes)-3
        assert [r['kind'] for r in passes[-3:]]==['physics','physics','idle']
        at=passes[anchor-1];last=passes[-1]
        def nsnapshot(at,physics=False):
            return dict(timers={n:ntimer(n) for n in B['timers']},characters_invu={s:dict(invulnerable=False,invulnerabilityItem=None,buffProtectStacks=0) for s in ('P','O')},
                king_source_state={'P:12':{'fields':dict(activations=0,activationsToTrigger=6.0,invuCharges=3,protectedBuffs=3.0,manaCost=4.0)}},
                nodes=[dict(node=deepcopy(B['nodes']['root_viewport']))],physics_frame=at['physics_frame'],idle_frame=at['idle_frame'],
                util_time=1.0,util_clockTime=2.0,util_frameCounter=10,is_in_physics_frame=physics)
        clean_raw=nsnapshot(at,True);final_raw=nsnapshot(last)
        cleanup=A._snapshot_native(clean_raw,B);final=A._snapshot_native(final_raw,B)
        policy='first-actual-idle-after-at-least-two-future-physics/1'
        ep=dict(schema='phase390-first-eligible-idle-endpoint/1',phase='idle_pre_internal_flush',terminal_policy=policy,cleanup_anchor_pass=anchor,
            minimum_future_physics_signals=2,passes=len(passes),first_eligible_idle_pass=len(passes),observed_future_physics_signals=2,
            physics_frame=last['physics_frame'],idle_frame=last['idle_frame'])
        cut=dict(receipt=dict(terminal_cut=dict(terminal_policy=policy,cleanup_anchor_pass=anchor,first_eligible_idle_pass=len(passes),observed_future_physics_signals=2,minimum_future_physics_signals=2)),actual_final=final_raw)
        terminal_native={'king-capture-endpoint.json':ep,'king-collector-cut.json':cut}
        tn=A._terminal_native(terminal_native,bundle,cleanup,final)
        trace=[dict(index=j,kind=r['kind'],end_phase='idle_pre_internal_flush' if j==len(passes)-1 else r['kind']+'_tail',completed=j!=len(passes)-1) for j,r in enumerate(passes)]
        tm=dict(king_terminal=dict(post_cleanup=dict(passes_consumed=anchor,physics_frame=at['physics_frame']),
            final=dict(passes_consumed=len(passes),physics_frame=last['physics_frame'],idle_frame=last['idle_frame'],finalized=True,cleaned=True,physics_signals_remaining=0),passes=trace))
        assert A.first_difference(tn,A._terminal_model(tm,bundle)) is None
        bad=deepcopy(tm);bad['king_terminal']['passes'].pop()
        reject('terminal_missing_pass',lambda:A._terminal_model(bad,bundle))
        bad=deepcopy(terminal_native);bad['king-capture-endpoint.json']['first_eligible_idle_pass']-=1
        reject('terminal_wrong_first_idle',lambda:A._terminal_native(bad,bundle,cleanup,final))
        ok('full_clock_first_eligible_idle_no_frame_execution')
        sections={name:[0.0,dict(identity='retained')] for name in A.SECTIONS}
        assert A.compare_projected(sections,deepcopy(sections))['status']=='PASS'
        for name in A.SECTIONS:
            changed=deepcopy(sections);changed[name][0]=-0.0
            result=A.compare_projected(sections,changed)
            assert result['status']=='FAIL' and result['first_differences'][name]
        reject('missing_business_section',lambda:A.compare_projected(sections,{k:v for k,v in sections.items() if k!='histories'}))
        ok('all8_sections_strict_mutations')
        assert calls['compare_decoded']==calls['project_native']==calls['project_model']==0
        pin(SOURCE,SOURCE_SHA)
        report['status']='PASS_SYNTHETIC_ADAPTER_INTERFACE_CONTROLS'
    except BaseException as exc:
        report['status']='FAIL_FIRST_ERROR_NO_RETRY'
        report['error']=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
        report.update(calls=dict(calls),reads=reads,elapsed_seconds=time.monotonic()-start,
                      model_calls=0,EXPECTED_reads=0,actual_comparisons=0,fixture_kind='synthetic helper fixtures plus pinned INPUT identity/topology/clock')
        raw=(json.dumps(report,indent=2)+'\n').encode();(OUT/'result.json').write_bytes(raw)
        owner=dict(schema='phase448-control-output-owner/1',files=[dict(path=str((OUT/'result.json').relative_to(ROOT)),size=len(raw),sha256=hashlib.sha256(raw).hexdigest())])
        (OUT/'owned-files.json').write_text(json.dumps(owner,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],cases=len(cases),seconds=report['elapsed_seconds'])))
    return 0 if report['status'].startswith('PASS') else 1


if __name__=='__main__':raise SystemExit(main())
