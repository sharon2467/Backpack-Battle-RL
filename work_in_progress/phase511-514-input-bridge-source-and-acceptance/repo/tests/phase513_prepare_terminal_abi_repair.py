"""Minimal immutable SOURCE repair; no schema/projector execution."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import traceback

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/phase513-input-bridge-source'
OLD=ROOT/'tests/phase511_input_bridge.py'
NEW=ROOT/'tests/phase513_input_bridge.py'
BASE=ROOT/'data/phase511-input-bridge-source-v2'
SPEC=ROOT/'docs/phase513_runtime_terminal_abi_repair_spec.md'


def require(ok,message):
    if not ok:raise ValueError(message)


def pin(p):
    b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),size=len(b),sha256=hashlib.sha256(b).hexdigest())


def save(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:json.dump(v,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n')


def funcs(text):return {n.name:ast.get_source_segment(text,n) for n in ast.parse(text).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}


def main():
    require(not OUT.exists() and not NEW.exists(),'unique513 output')
    OUT.mkdir();save(OUT/'generation-started.json',{'producer':pin(Path(__file__)),'spec':pin(SPEC),'imports':0,'projection_calls':0})
    try:
        require(pin(OLD)['sha256']=='f34612453a0fb91fcb4dc74bf59e454c9f149fd582019c2b3e70afe210d1829a','exact oldbridge')
        original=OLD.read_text();text=original;edits=[]
        def replace(a,b):
            nonlocal text
            require(text.count(a)==1 and a!=b,'unique repair anchor')
            pos=text.index(a);text=text[:pos]+b+text[pos+len(a):];edits.append(dict(position=pos,before=a,after=b))
        consumer=ROOT/'data/phase505-captured-nonking-source-v3/staged/native_replay_v8/genuine.py'
        tree=ast.parse(consumer.read_text())
        value=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SINGLE_KING_TERMINAL' for t in n.targets))
        tuple_path=ROOT/'data/phase502-whelp-observer-source-v4/source-tuple.json';native_policy=json.loads(tuple_path.read_bytes())['terminal_policy']
        require(value=='source-two-physics-idle-pre-internal/1' and native_policy=='first-actual-idle-after-at-least-two-future-physics/1','actual original layered constants')
        f=funcs(text)['project_runtime'];newf=f.replace("terminal_profile='first-actual-idle-after-at-least-two-future-physics/1'","terminal_profile='source-two-physics-idle-pre-internal/1'").replace('data/phase511-input-bridge-source/abi.json','data/phase513-input-bridge-source/abi.json')
        require(f!=newf,'runtime emission repair');replace(f,newf)
        f=funcs(text)['authenticate_request'];newf=f.replace('tests/phase511_input_bridge.py','tests/phase513_input_bridge.py').replace('data/phase511-input-bridge-source/abi.json','data/phase513-input-bridge-source/abi.json')
        require(f!=newf,'mechanical closed Source paths');replace(f,newf)
        assignment=next(n for n in ast.parse(text).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SOURCE_RULES' for t in n.targets))
        rules=ast.literal_eval(assignment.value)
        rules['terminal_profiles']={'observer_collector_policy':native_policy,'runtime_terminal_profile':value,
            'observer_source':pin(tuple_path),'runtime_source':pin(consumer),
            'meaning':'Distinct existing identifiers at producer and consumer layers; unchanged FrameDriver behavior. Runtime emission must follow consumer ABI, not collector policy.'}
        replace(ast.get_source_segment(text,assignment),'SOURCE_RULES = '+repr(rules))
        compile(text,str(NEW),'exec',dont_inherit=True)
        before,after=funcs(original),funcs(text)
        require(set(before)==set(after),'function inventory exact')
        changed=sorted(n for n in before if before[n]!=after[n]);require(changed==['authenticate_request','project_runtime'],'only declared two function changes')
        inverse=text
        for row in reversed(edits):
            pos=row['position'];require(inverse[pos:pos+len(row['after'])]==row['after'],'inverse postimage')
            inverse=inverse[:pos]+row['before']+inverse[pos+len(row['after']):]
        require(inverse==original,'whole byte inverse')
        NEW.write_text(text)
        context=json.loads((BASE/'source-context.json').read_bytes())
        context['source_rules']=rules
        abi=json.loads((BASE/'abi.json').read_bytes())
        abi.update(observer_collector_policy=native_policy,runtime_terminal_profile=value,observer_policy_source=pin(tuple_path),runtime_terminal_source=pin(consumer))
        save(OUT/'abi.json',abi)
        source_pins=[]
        for p in context['source_pins']:
            if p['path']=='tests/phase511_input_bridge.py':source_pins.append(pin(NEW))
            elif p['path']=='data/phase511-input-bridge-source/abi.json':source_pins.append(pin(OUT/'abi.json'))
            else:source_pins.append(p)
        context['source_pins']=source_pins;save(OUT/'source-context.json',context)
        request=json.loads((BASE/'future-root-request-template.json').read_bytes());require(request['input_descriptors'] is None,'unknown actual inputs stay unknown')
        request['source_context']=pin(OUT/'source-context.json');save(OUT/'future-root-request-template.json',request)
        save(OUT/'inverse.json',{'before':pin(OLD),'after':pin(NEW),'edits':edits,'whole_byte_inverse':True})
        (OUT/'source.patch').write_text(''.join(difflib.unified_diff(original.splitlines(True),text.splitlines(True),fromfile=str(OLD.relative_to(ROOT)),tofile=str(NEW.relative_to(ROOT)))))
        save(OUT/'conservation.json',{'schema':'phase513-source-conservation/1','changed_functions':changed,'new_functions':0,'exact_function_count':len(before)-2,
            'exact_helpers':[n for n in before if before[n]==after[n]],'initial_receipt_reused':pin(ROOT/'tests/phase511_initial_receipt.py'),
            'schema_untouched':context['schema_module'],'candidate_untouched':context['fixed_source_bindings']['candidate_freeze'],
            'only_runtime_value_and_origin_plus_metadata_path_rebinding':True,'actual_input_pins':None,'schema_imports':0,'projection_calls':0})
        api=json.loads((BASE/'api-contract.json').read_bytes());api['source_repair']='Runtime terminal ABI corrected; observer policy preserved; unchanged function signatures/request top-level shape.'
        save(OUT/'api-contract.json',api)
        save(OUT/'compile-only.json',{'discarded_bridge_compile_objects':1,'schema_imports':0,'helper_calls':0,'projection_calls':0,'Native_records':0,'models':0,'pool':0,'Expected':0})
        save(OUT/'source-freeze.json',{'schema':'phase513-source-freeze/1','modules':[pin(ROOT/'tests/phase511_initial_receipt.py'),pin(NEW)],
            'source_context':pin(OUT/'source-context.json'),'ABI':pin(OUT/'abi.json'),'future_request_template':pin(OUT/'future-root-request-template.json'),
            'status':'FROZEN_COMPILE_ONLY_PENDING_ROOT_AND_INDEPENDENT_REVIEW_NO_ACTUAL_INPUT'})
        source_refs=[SPEC,Path(__file__),OLD,NEW,ROOT/'tests/phase511_initial_receipt.py',BASE/'owned-files.json',
            ROOT/'data/phase511-input-bridge-source/partial-source-owner.json',ROOT/'data/phase511-input-bridge-source/branch-source-rule.json',
            ROOT/'data/phase512-independent-source-first-finding/finding.json',ROOT/'data/phase512-independent-source-first-finding/owned-files.json',consumer,tuple_path]
        save(OUT/'source-context-refs.json',{'files':[pin(p) for p in source_refs],'old_firstassembly_not_reclassified':True,'actual_Native_fields_filled':False})
        save(OUT/'first-generation-result.json',{'source_generation_invocations':1,'status':'SOURCE_FROZEN_NOT_PROJECTED','projector_imports':0,'schema_imports':0,'projection_calls':0,'Native_records':0,'models':0,'pool':0,'Expected':0})
        files=[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()]+[pin(p) for p in source_refs]
        save(OUT/'owned-files.json',{'schema':'phase513-source-owner/1','files':list({p['path']:p for p in files}.values()),'no_more_writes':True,'status':'SOURCE_ONLY_ROOT_HANDOFF_NO_AUTOMATIC_REVIEW_OR_BUILD'})
        print(json.dumps({'status':'SOURCE_FROZEN_NOT_RUN','owner':pin(OUT/'owned-files.json')},sort_keys=True))
    except Exception as error:
        save(OUT/'first-generation-error.json',{'error':type(error).__name__,'message':str(error),'traceback':traceback.format_exc(),'automatic_retry':False,'imports':0,'projection_calls':0,'Native_records':0,'models':0,'pool':0,'Expected':0})
        raise


if __name__=='__main__':main()
