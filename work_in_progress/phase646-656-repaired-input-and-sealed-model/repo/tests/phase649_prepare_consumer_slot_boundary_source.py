"""One minimal consumer Source derivation; no generated schema/helper imports."""
from pathlib import Path
import ast
import copy
import difflib
import hashlib
import json
import traceback

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/phase649-consumer-slot-boundary-source'
OLD_SCHEMA=ROOT/'data/phase610-three-selected-hook-source-v2/schema/phase610_mixed_observer_schema.py'
OLD_A=ROOT/'tests/phase621_input_bridge.py'
OLD_C=ROOT/'tests/phase621_mixed_tape_run.py'
NEW_A=ROOT/'tests/phase649_input_bridge.py'
NEW_C=ROOT/'tests/phase649_mixed_tape_run.py'


def pin(p):
    p=Path(p);b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),size=len(b),sha256=hashlib.sha256(b).hexdigest())


def read(p):return json.loads(Path(p).read_bytes())


def save(p,v):
    with Path(p).open('x') as f:f.write(json.dumps(v,ensure_ascii=False,indent=2)+'\n')


def functions(t):return {n.name:ast.get_source_segment(t,n) for n in ast.parse(t).body if isinstance(n,ast.FunctionDef)}


def assignment(t,name):
    a=[n for n in ast.parse(t).body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id==name]
    assert len(a)==1;return a[0]


class Delta:
    def __init__(self,t):self.text=t;self.changes=[]
    def replace(self,before,after,label):
        assert before!=after and self.text.count(before)==1,label
        at=self.text.index(before);self.text=self.text[:at]+after+self.text[at+len(before):]
        self.changes.append(dict(offset=at,before=before,after=after,label=label))
    def assign(self,name,v):
        n=assignment(self.text,name);assert n.col_offset==0
        lines=self.text.splitlines(keepends=True);start=sum(map(len,lines[:n.lineno-1]));end=sum(map(len,lines[:n.end_lineno]))
        assert start>0 and self.text[start-1]=='\n' and self.text[end-1]=='\n'
        assert n.end_col_offset==len(lines[n.end_lineno-1].removesuffix('\n').encode())
        self.replace(self.text[start-1:end],'\n'+name+' = '+repr(v)+'\n','exact AST full line:'+name)
    def inverse(self):
        t=self.text
        for row in reversed(self.changes):
            at=row['offset'];assert t[at:at+len(row['after'])]==row['after'];t=t[:at]+row['before']+t[at+len(row['after']):]
        return t


def main():
    assert not OUT.exists();OUT.mkdir();(OUT/'schema').mkdir();(OUT/'input').mkdir();(OUT/'output').mkdir();(OUT/'inverse').mkdir()
    made=[]
    try:
        assert not NEW_A.exists() and not NEW_C.exists()
        old_s=OLD_SCHEMA.read_text();old_a=OLD_A.read_text();old_c=OLD_C.read_text()
        assert pin(OLD_SCHEMA)['sha256']=='a33d2b90669388e9b3b1973a70234a5ec672f480167c27a26e07245fff84f45c'
        s,a,c=Delta(old_s),Delta(old_a),Delta(old_c)
        plan=ast.literal_eval(assignment(old_s,'BINDING_FIXED_PLAN').value)
        counts={side:sum(row['side']==side for row in plan) for side in ('P','O')};assert counts=={'P':23,'O':6}
        old_fn=functions(old_s)['_binding_validate_value']
        anchor='    _binding_same_source(fixed_plan, BINDING_FIXED_PLAN)\n'
        assert old_fn.count(anchor)==1
        declaration="    side_limits = {side: sum(spec['side'] == side for spec in BINDING_FIXED_PLAN) - 1 for side in ('P', 'O')}\n"
        fn=old_fn.replace(anchor,anchor+declaration)
        for before,after in [("integer(row['input_slot'], 0, 19)","integer(row['input_slot'], 0, side_limits[side])"),
                             ("integer(row['inventory_encounter_index'], 0, 19)","integer(row['inventory_encounter_index'], 0, side_limits[side])")]:
            assert fn.count(before)==1;fn=fn.replace(before,after)
        s.replace(old_fn,fn,'only fixedplan side limits + two upper args')
        schema_path=OUT/'schema/phase649_consumer_schema.py';schema_path.write_text(s.text);made.append(schema_path)
        schema_pin=pin(schema_path)
        a.assign('SCHEMA_PIN',schema_pin)
        fixed=ast.literal_eval(assignment(a.text,'FIXED_SOURCE_BINDINGS').value);fixed['schema_module']=schema_pin;a.assign('FIXED_SOURCE_BINDINGS',fixed)
        auth=functions(a.text)['authenticate_request'];assert auth.count('tests/phase621_input_bridge.py')==1
        a.replace(auth,auth.replace('tests/phase621_input_bridge.py','tests/phase649_input_bridge.py'),'closed bridge selfpath only')
        NEW_A.write_text(a.text);made.append(NEW_A)
        ctx=read(ROOT/'data/phase621-hooks110-rebinding-source/input/source-context.json');old_ctx=copy.deepcopy(ctx)
        ctx['schema_module']=schema_pin;ctx['fixed_source_bindings']['schema_module']=schema_pin
        pins=[]
        for row in ctx['source_pins']:
            if row['path']==pin(OLD_SCHEMA)['path']:pins.append(schema_pin)
            elif row['path']==pin(OLD_A)['path']:pins.append(pin(NEW_A))
            else:pins.append(row)
        ctx['source_pins']=pins;assert len(pins)==15 and len({r['path'] for r in pins})==15
        save(OUT/'input/source-context.json',ctx)
        save(OUT/'consumer-repair-provenance.json',dict(schema='phase649-consumer-slot-repair-provenance/1',
             role='CONSUMER_VALIDATION_ONLY_NOT_NATIVE_PRODUCER',before=pin(OLD_SCHEMA),after=schema_pin,
             producer_source_owner=pin(ROOT/'data/phase610-three-selected-hook-source-v2/source-owner.json'),
             producer_acceptance=pin(ROOT/'data/phase612-independent-final-acceptance/source-acceptance.json'),
             producer_acceptance_scope='Original110producer/old610schema only;not649consumer acceptance',
             independent_consumer_acceptance=None,independent_review_stage='650_PENDING',trusted_plan_counts=counts,
             side_limits={side:n-1 for side,n in counts.items()},raw002_changed=False,models_allowed=0,Expected_allowed=0))
        input_files=pins+[pin(OUT/'input/source-context.json'),pin(OUT/'consumer-repair-provenance.json')]
        save(OUT/'input/owned-files.json',dict(schema='phase649-input-source-owner/1',files=input_files,no_more_writes=True))
        req=read(ROOT/'data/phase621-hooks110-rebinding-source/input/request-template.json');req['source_context']=pin(OUT/'input/source-context.json')
        assert req['input_descriptors']=={} and req['models_allowed']==req['expected_allowed']==0
        save(OUT/'input/request-template.json',req)
        c.assign('INPUT_SOURCE',pin(OUT/'input/owned-files.json'))
        c.assign('CANDIDATE_CONTEXT',pin(OUT/'input/source-context.json'))
        fixed_inputs=ast.literal_eval(assignment(c.text,'FIXED_INPUTS').value);fixed_inputs['input_source_owner']=pin(OUT/'input/owned-files.json');c.assign('FIXED_INPUTS',fixed_inputs)
        NEW_C.write_text(c.text);made.append(NEW_C)
        model_req=read(ROOT/'data/phase621-hooks110-rebinding-source/output/model-request-template.json')
        model_req.update(input_source_owner=pin(OUT/'input/owned-files.json'),launcher=pin(NEW_C));assert model_req['root_model_authorized'] is False
        save(OUT/'output/model-request-template.json',model_req)
        # Source-only checks; no candidate function is called.
        rows=[];compiled=[]
        for key,old,delta,target,changed_expected in [('schema',old_s,s,schema_path,{'_binding_validate_value'}),('A',old_a,a,NEW_A,{'authenticate_request'}),('C-launcher',old_c,c,NEW_C,set())]:
            assert delta.inverse()==old
            old_f,new_f=functions(old),functions(delta.text);assert set(old_f)==set(new_f)
            changed={name for name in old_f if old_f[name]!=new_f[name]};assert changed==changed_expected,(key,changed)
            compile(target.read_bytes(),str(target),'exec');compiled.append(pin(target))
            save(OUT/'inverse'/(key+'.json'),dict(schema='phase649-full-source-inverse/1',before=pin({'schema':OLD_SCHEMA,'A':OLD_A,'C-launcher':OLD_C}[key]),after=pin(target),replacements=delta.changes,exact=True))
            (OUT/'inverse'/(key+'.patch')).write_text(''.join(difflib.unified_diff(old.splitlines(True),delta.text.splitlines(True),fromfile=key+'-old',tofile=str(target.relative_to(ROOT)))))
            rows.append(dict(file=pin(target),changed_functions=sorted(changed),exact_functions=sorted(set(old_f)-changed),full_inverse=True))
        retained={key:pin(ROOT/path) for key,path in dict(adapter='tests/phase621_mixed_business_output.py',B2='tests/phase621_shared_callback_guard.py',initial='tests/phase578_initial_receipt.py',candidate_freeze='data/phase580-captured-mixed-source/candidate-source-freeze.json',contract='data/phase621-hooks110-rebinding-source/output/comparison-contract.json').items()}
        save(OUT/'conservation.json',dict(schema='phase649-consumer-slot-conservation/1',modules=rows,retained=retained,
             schema_declaration_identity_unchanged=True,producer110_and_host_recovery_unchanged=True,other_schema_helpers_exact=True,
             source_rules_exact=ctx['source_rules']==old_ctx['source_rules'],context_only_schema_and_self_source_pins_changed=True,
             fixed_plan=pin(OLD_SCHEMA),trusted_side_counts=counts,strict_INT_identity_geometry_unsorted_encounter_unchanged=True,
             C_all_function_bodies_exact=True,compile_objects=3,actual_build_calls=0,model_calls=0))
        save(OUT/'compile-only.json',dict(schema='phase649-source-compile/1',objects=compiled,generation_attempts=1,imports=0,helpers=0,tests=0,INPUT_build=0,models=0,Native=0,Expected=0,pool=0))
        dependencies=[pin(p) for p in (OLD_SCHEMA,OLD_A,OLD_C,ROOT/'docs/phase648_consumer_slot_boundary_repair_spec.md',ROOT/'docs/phase649_consumer_slot_boundary_implementation_addendum.md',ROOT/'data/phase647-independent-input-first-error-review/review.json',Path(__file__))]+list(retained.values())
        files=[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()]+[pin(NEW_A),pin(NEW_C)]+dependencies+pins
        unique={}
        for row in files:
            assert row['path'] not in unique or unique[row['path']]==row;unique[row['path']]=row
        save(OUT/'source-freeze.json',dict(schema='phase649-consumer-source-freeze/1',status='SOURCE_ONLY_PENDING_INDEPENDENT_CONSUMER_ACCEPTANCE',
             files=list(unique.values()),consumer_schema=schema_pin,bridge=pin(NEW_A),launcher=pin(NEW_C),input_context=pin(OUT/'input/source-context.json'),input_owner=pin(OUT/'input/owned-files.json'),
             retained=retained,producer_profile_unchanged=True,newconsumer_acceptance=None,actual_Input=None,actual_B2=None,actual_model=None,Expected=None))
        save(OUT/'api.json',dict(schema='phase649-consumer-repair-API/1',carrier_function='_binding_validate_value(value,fixed_plan)',public_carrier_function='validate_binding_carrier(binding_bytes,fixed_plan)',
             schema_module=schema_pin,trusted_side_limits={side:n-1 for side,n in counts.items()},new_bridge=pin(NEW_A),new_launcher=pin(NEW_C),input_CLI=['--request','--request-size','--request-sha256','--output-new'],
             input_output_prefix='phase578-',model_CLI=['--config','--config-sha256','--output'],model_output_prefix='phase582-',
             model_request_keys=17,Root_input_request_keys=7,Root_actual_pins=None,Source_imports=0,helper_tests=0,INPUT_builds=0,models=0))
        owner_files=list(unique.values())+[pin(OUT/'source-freeze.json'),pin(OUT/'api.json')]
        save(OUT/'owned-files.json',dict(schema='phase649-source-owner/1',files=owner_files,no_more_writes=True))
        print(json.dumps(dict(status='SOURCE_GENERATED_COMPILED_NOT_IMPORTED',owner=pin(OUT/'owned-files.json'),freeze=pin(OUT/'source-freeze.json'),compile_objects=3)))
    except BaseException as exc:
        save(OUT/'first-error.json',dict(schema='phase649-source-first-error/1',type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc(),generation_attempts=1,imports=0,helpers=0,tests=0,INPUT_build=0,models=0,Native=0,Expected=0))
        save(OUT/'partial-owner.json',dict(schema='phase649-source-partial-owner/1',files=[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()]+[pin(p) for p in made]+[pin(Path(__file__)),pin(ROOT/'docs/phase649_consumer_slot_boundary_implementation_addendum.md')],no_more_writes=True))
        raise


if __name__=='__main__':main()
