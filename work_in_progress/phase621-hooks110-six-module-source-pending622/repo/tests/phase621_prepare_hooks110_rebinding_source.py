"""One Source-only six-module derivation. Never imports generated modules."""
from pathlib import Path
import ast
import copy
import difflib
import hashlib
import json
import traceback

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'data/phase621-hooks110-rebinding-source'
OBS = ROOT/'data/phase610-three-selected-hook-source-v2'
RUN = 'original030-mixed-modifiers-A-single-002'
VERSION = '7-mixed-modifiers-A-610-hooks110'
NPROFILE = 'observer7-mixed-modifiers-A-hooks110-native-tape/1'
MODULES = {key:ROOT/('tests/phase621_'+name+'.py') for key,name in {
 'host':'oracle_host','storage':'oracle_storage','A':'input_bridge','launcher':'mixed_tape_run',
 'adapter':'mixed_business_output','B2':'shared_callback_guard'}.items()}
OLD = {key:ROOT/('tests/'+name+'.py') for key,name in {
 'host':'phase590_oracle_host','storage':'phase590_oracle_storage','A':'phase578_input_bridge',
 'launcher':'phase583_mixed_tape_run','adapter':'phase583_mixed_business_output','B2':'phase583_shared_callback_guard'}.items()}


def pin(path):
    path=Path(path);raw=path.read_bytes()
    return dict(path=str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
                size=len(raw),sha256=hashlib.sha256(raw).hexdigest())


def read(path):return json.loads(Path(path).read_bytes())


def save(path,value):
    with Path(path).open('x') as stream:stream.write(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True)+'\n')


def assignment(text,name):
    nodes=[n for n in ast.parse(text).body if isinstance(n,ast.Assign) and len(n.targets)==1
           and isinstance(n.targets[0],ast.Name) and n.targets[0].id==name]
    assert len(nodes)==1,('exact assignment',name)
    return nodes[0]


def literal(text,name):return ast.literal_eval(assignment(text,name).value)


def functions(text):return {n.name:ast.get_source_segment(text,n) for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}


class Delta:
    def __init__(self,text):self.text=text;self.changes=[]
    def replace(self,before,after,label):
        assert before!=after and self.text.count(before)==1,('strict unique span',label)
        at=self.text.index(before);self.text=self.text[:at]+after+self.text[at+len(before):]
        self.changes.append(dict(offset=at,before=before,after=after,label=label))
    def assign(self,name,value,expression=False):
        n=assignment(self.text,name);assert n.col_offset==0
        lines=self.text.splitlines(keepends=True);start=sum(map(len,lines[:n.lineno-1]));end=sum(map(len,lines[:n.end_lineno]))
        assert start>0 and self.text[start-1]=='\n' and self.text[end-1]=='\n'
        assert n.end_col_offset==len(lines[n.end_lineno-1].removesuffix('\n').encode())
        before=self.text[start-1:end];after='\n'+name+' = '+(value if expression else repr(value))+'\n'
        self.replace(before,after,'AST full physical-line identity:'+name)
    def function(self,name,after):self.replace(functions(self.text)[name],after,'function:'+name)
    def inverse(self):
        text=self.text
        for row in reversed(self.changes):
            at=row['offset'];assert text[at:at+len(row['after'])]==row['after']
            text=text[:at]+row['before']+text[at+len(row['after']):]
        return text


REVIEW_FUNCTION = '''def validate_observer_review(value,receipt,source_tuple):
    if (type(value) is not dict or receipt!=OBSERVER_REVIEW or source_tuple!=OBSERVER_TUPLE
            or value.get('schema')!='phase612-selected-three-hook-source-acceptance/1'
            or value.get('status')!='ACCEPTED_SOURCE_AND_FINITE_SYNTHETIC_SCHEMA_ONLY'):
        raise ValueError('exact612 Source-only receipt and tuple binding required')
    for key,expected in (('source_owner',OBSERVER_OWNER),('source_freeze',OBSERVER_FREEZE),
                         ('source_tuple',OBSERVER_TUPLE),('schema_module',OBSERVER_SCHEMA)):
        if key not in value or type(value[key]) is not dict or value[key]!=expected:
            raise ValueError('612 actual Source descriptor:'+key)
    if value.get('source_static_pass') is not True:
        raise ValueError('612 actual static acceptance required')
    controls=value.get('finite_schema_controls')
    expected={'top_calls':13,'positive':6,'expected_reject':7,'schema_imports':1}
    if type(controls) is not dict or set(controls)!=set(expected):
        raise ValueError('612 exact finite-control fields')
    for key,count in expected.items():
        if type(controls[key]) is not int or controls[key]!=count:
            raise ValueError('612 strict finite counter:'+key)
    for key in ('native','models','Godot','fulljoin','fullcapture'):
        if type(value.get(key)) is not int or value[key]!=0:
            raise ValueError('612 Source-only strictINT0:'+key)
    if (value.get('actual_Native_facts') is not False or value.get('operational_authority') is not False
            or 'new_run' not in value or value['new_run'] is not None):
        raise ValueError('612 receipt is not operational or actual Native authority')'''

ORIGIN_BLOCK = '''    authority=read(check_source_descriptor(root,SOURCE_AUTHORITY))
    if (authority.get('schema')!='phase610-source-authority/1'
            or authority.get('old_source_owner')!=LEGACY_OBSERVER_OWNER
            or authority.get('old_source_freeze')!=LEGACY_OBSERVER_FREEZE
            or authority.get('current_run_authority','MISSING') is not None
            or authority.get('scope')!='SOURCE_ONLY_NO_NEW_ATTEMPT_AUTHORITY'):
        raise ValueError('exact610 wrapper; no invented operational origin')
    for row in (LEGACY_OBSERVER_OWNER,LEGACY_OBSERVER_FREEZE,LEGACY_SOURCE_AUTHORITY,OBSERVER_CENSUS):
        if declared.get(row['path'])!=row:raise ValueError('fixed legacy/census leaf outside graph')
        check_source_descriptor(root,row)
    legacy_leaves=verify_owner(root,LEGACY_OBSERVER_OWNER)
    for row in (LEGACY_OBSERVER_FREEZE,LEGACY_SOURCE_AUTHORITY):
        if legacy_leaves.get(row['path'])!={k:row[k] for k in ('size','sha256')}:
            raise ValueError('owned fixed legacy origin hop')
    origin=read(check_source_descriptor(root,LEGACY_SOURCE_AUTHORITY))
    if (origin.get('schema')!='phase572-source-authority/1' or type(origin.get('origin')) is not dict
            or {row['path']:row for row in origin['origin'].values() if Path(row['path']).is_absolute()}!=ABSOLUTE_SOURCE_PINS):
        raise ValueError('same exact five legacy absolute origins; no fallback')
    census=read(check_source_descriptor(root,OBSERVER_CENSUS))
    for key,expected in (('old_sites',107),('new_sites',110)):
        if type(census.get(key)) is not int or census[key]!=expected:
            raise ValueError('exact owned110 method census')
    if census.get('old_sites_deep_equal') is not True or census.get('old_MATRIX_deep_equal') is not True:
        raise ValueError('old107 mappings must remain exact')
'''


def main():
    assert not OUT.exists();OUT.mkdir()
    for sub in ('host','input','output','inverse'):(OUT/sub).mkdir()
    generated=[];deltas={};sources={}
    try:
        for p in MODULES.values():assert not p.exists(),'immutable module namespace'
        selection=read(ROOT/'data/phase620-root-source-run-selection/selection.json')
        assert selection['selected_run']==RUN and selection['Native_authorized'] is False
        obs=read(OBS/'combined-source-freeze.json');obs_tuple=read(OBS/'source-tuple.json')
        assert obs['project_install_count']==79 and obs['project_install_source_bytes']==817696
        assert obs_tuple['proposed_run'] is None and obs_tuple['profile']==NPROFILE and obs_tuple['observer_version']==VERSION
        obs_receipt=ROOT/'data/phase612-independent-final-acceptance/source-acceptance.json'
        obs_review=pin(obs_receipt);obs_review_owner=pin(obs_receipt.parent/'owned-files.json')
        accepted=read(obs_receipt)
        assert accepted['source_owner']==pin(OBS/'source-owner.json') and accepted['schema_module']==obs['schema_module']
        for key,p in OLD.items():sources[key]=p.read_text();deltas[key]=Delta(sources[key])
        # Host/storage first: new graph is closed before A/C metadata exists.
        storage=deltas['storage'];storage.assign('MAX_INSTALL_BYTES',817696)
        MODULES['storage'].write_text(storage.text);generated.append(MODULES['storage'])
        host=deltas['host']
        host.replace('from phase590_oracle_storage import (','from phase621_oracle_storage import (','actual new isolated storage import')
        assignments=dict(SOURCE=str((OUT/'host').relative_to(ROOT)),OBSERVER_SOURCE=str(OBS.relative_to(ROOT)),RUN_NAME=RUN,
            HOST_REVIEW_SCHEMA='phase621-independent-host-source-review/1',
            OBSERVER_FREEZE=pin(OBS/'combined-source-freeze.json'),OBSERVER_OWNER=pin(OBS/'source-owner.json'),
            OBSERVER_REVIEW=obs_review,OBSERVER_REVIEW_OWNER=obs_review_owner,
            SOURCE_AUTHORITY=pin(OBS/'source-authority.json'),OBSERVER_TUPLE=pin(OBS/'source-tuple.json'),
            OBSERVER_SCHEMA=obs['schema_module'],OBSERVER_VERSION=VERSION,OBSERVER_PROFILE=NPROFILE)
        for name,value in assignments.items():host.assign(name,value)
        legacy_constants='\nLEGACY_OBSERVER_OWNER = '+repr(pin(ROOT/'data/phase572-mixed-observer-source-v2/source-owner.json'))
        legacy_constants+='\nLEGACY_OBSERVER_FREEZE = '+repr(pin(ROOT/'data/phase572-mixed-observer-source-v2/combined-source-freeze.json'))
        legacy_constants+='\nLEGACY_SOURCE_AUTHORITY = '+repr(pin(ROOT/'data/phase572-mixed-observer-source-v2/source-authority.json'))
        legacy_constants+='\nOBSERVER_CENSUS = '+repr(pin(OBS/'site-census.json'))+'\n'
        host.replace('\n\ndef descriptor(source_root,row):',legacy_constants+'\n\ndef descriptor(source_root,row):','one fixed legacy origin/census declarations')
        host.function('validate_observer_review',REVIEW_FUNCTION)
        gate=functions(host.text)['source_gate'];assert gate.count('observer575')==2
        host.function('source_gate',gate.replace('observer575','observer612'))
        active=functions(host.text)['validate_active_source_tuple']
        replacements=[("value['schema']!='phase572-zero-king-mixed-observer-source-tuple/1'","value['schema']!='phase610-selected-three-hook-source-tuple/1'"),
          ("value['actual_Native_UID_cut_cache_clock_setup']!='UNOBSERVED'","value['actual_Native_UID_cut_cache_clock_setup']!='UNOBSERVED_FOR_FUTURE_COMPLETE_RECORD;partial030_not_admitted'"),
          ("value['proposed_run']!=RUN_NAME","value['proposed_run'] is not None"),
          ("value['project_install_source_bytes']!=817389","value['project_install_source_bytes']!=817696"),
          ("schema='phase572-native-patch-source/1'","schema='phase610-selected-three-hook-native-patch-source/1'"),
          ("plan.get('profile')!=OBSERVER_PROFILE or plan.get('version')!=OBSERVER_VERSION",
           "plan.get('profile')!='observer7-mixed-modifiers-A-native-tape/1' or plan.get('version')!='7-mixed-modifiers-A-572'")]
        for before,after in replacements:
            assert active.count(before)==1,('fixed tuple identity span',before);active=active.replace(before,after)
        old_origin="""    authority=read(check_source_descriptor(root,SOURCE_AUTHORITY))
    if (authority.get('schema')!='phase572-source-authority/1' or type(authority.get('origin')) is not dict
            or {row['path']:row for row in authority['origin'].values() if Path(row['path']).is_absolute()}!=ABSOLUTE_SOURCE_PINS):
        raise ValueError('exact502 two absolute sourceorigin authorities')
"""
        assert active.count(old_origin)==1;active=active.replace(old_origin,ORIGIN_BLOCK)
        host.function('validate_active_source_tuple',active)
        MODULES['host'].write_text(host.text);generated.append(MODULES['host'])
        old_host_freeze=read(ROOT/'data/phase590-case030-host-restore-source/combined-source-freeze.json')
        graph=copy.deepcopy(old_host_freeze)
        for key in ('paths','artifacts','collector','schema_module','active_source_tuple','profile','observer_version','terminal_policy'):
            graph[key]=copy.deepcopy(obs[key])
        graph.update(host=pin(MODULES['host']),storage=pin(MODULES['storage']),run_name=RUN,
                     observer_source_freeze=pin(OBS/'combined-source-freeze.json'),observer_source_owner=pin(OBS/'source-owner.json'),
                     native_source_origin=pin(OBS/'source-authority.json'),project_install_count=79,project_install_source_bytes=817696)
        deps=list(old_host_freeze['files'])+list(obs['files'])+[pin(p) for p in (MODULES['host'],MODULES['storage'],OBS/'source-owner.json',OBS/'combined-source-freeze.json',OBS/'source-authority.json',obs_receipt,obs_receipt.parent/'owned-files.json',ROOT/'data/phase620-root-source-run-selection/selection.json',ROOT/'data/phase621-root-repaired110-rebinding-source-release/release.json',Path(__file__),ROOT/'docs/phase621_hooks110_rebinding_implementation_spec.md')]
        unique={}
        for row in deps:
            assert row['path'] not in unique or unique[row['path']]==row,'closed host Source identity'
            unique[row['path']]=row
        graph['files']=list(unique.values())
        save(OUT/'host/combined-source-freeze.json',graph)
        save(OUT/'host/source-owner.json',dict(schema='phase621-host-source-owner/1',files=list(unique.values())+[pin(OUT/'host/combined-source-freeze.json')],no_more_writes=True))
        config=read(ROOT/'data/phase595-root-source-bound-config-draft/oracle-configuration-source-bound-NOT-AUTHORIZED.json')
        config.update(host=pin(MODULES['host']),source_freeze=pin(OUT/'host/combined-source-freeze.json'),source_owner=pin(OUT/'host/source-owner.json'),
                      observer_source_freeze=pin(OBS/'combined-source-freeze.json'),observer_source_owner=pin(OBS/'source-owner.json'),active_source_tuple=pin(OBS/'source-tuple.json'),
                      reviews=dict(observer612=dict(receipt=obs_review,owner=obs_review_owner),host_source=dict(receipt=None,owner=None)),resources=[],root_oracle_authorized=False)
        save(OUT/'host/root-config-template.json',config)
        # A: reuse original initial/rules/ABI, new bridge and actual context pins.
        a=deltas['A'];a.assign('RUN',RUN);a.assign('SCHEMA_PIN',obs['schema_module'])
        bindings=literal(a.text,'FIXED_SOURCE_BINDINGS')
        bindings.update(schema_module=obs['schema_module'],observer_tuple=pin(OBS/'source-tuple.json'),
                        observer_owner=pin(OBS/'source-owner.json'),observer_acceptance=obs_review)
        a.assign('FIXED_SOURCE_BINDINGS',bindings)
        rules=literal(a.text,'SOURCE_RULES');rules['terminal_profiles']['observer_source']=pin(OBS/'source-tuple.json')
        a.assign('SOURCE_RULES',rules)
        fn=functions(a.text)['authenticate_request'];assert fn.count('tests/phase578_input_bridge.py')==1
        a.function('authenticate_request',fn.replace('tests/phase578_input_bridge.py',str(MODULES['A'].relative_to(ROOT))))
        fn=functions(a.text)['load_schema']
        for before,after in [("module.VERSION=='7-mixed-modifiers-A-572'","module.VERSION=="+repr(VERSION)),
                             ("module.PROFILE=='observer7-mixed-modifiers-A-native-tape/1'","module.PROFILE=="+repr(NPROFILE))]:
            assert fn.count(before)==1;fn=fn.replace(before,after)
        a.function('load_schema',fn)
        MODULES['A'].write_text(a.text);generated.append(MODULES['A'])
        context=read(ROOT/'data/phase582-root-candidate-context-binding/source-context-candidate-bound.json')
        context.update(schema_module=obs['schema_module'],source_rules=rules)
        context['fixed_source_bindings'].update(bindings)
        kept=[row for row in context['source_pins'] if row['path'] in ('data/phase578-mixed-input-bridge-source/branch-source-rule.json','data/phase578-mixed-input-bridge-source/abi.json','data/phase578-mixed-input-bridge-source/typed-witness-contract.json')]
        context['source_pins']=list(context['fixed_source_bindings'].values())+[pin(MODULES['A'])]+kept
        assert len(context['source_pins'])==len({r['path'] for r in context['source_pins']})==15
        save(OUT/'input/source-context.json',context)
        inputfiles=context['source_pins']+[pin(OUT/'input/source-context.json')]
        save(OUT/'input/source-freeze.json',dict(schema='phase621-input-source-freeze/1',profile=context['profile'],files=inputfiles,actual_INPUT=None,status='SOURCE_ONLY_NOT_INPUT_OR_MODEL_AUTHORITY'))
        save(OUT/'input/owned-files.json',dict(schema='phase621-input-source-owner/1',files=inputfiles+[pin(OUT/'input/source-freeze.json')],no_more_writes=True))
        input_template=dict(schema='phase578-root-bound-input-request/1',case_id='NATIVE-030-MIXED-MODIFIERS-A',run_name=RUN,source_context=pin(OUT/'input/source-context.json'),input_descriptors={},models_allowed=0,expected_allowed=0)
        save(OUT/'input/request-template.json',input_template)
        # C contract only changes native-profile identity; all semantic sections exactly retained.
        old_contract=read(ROOT/'data/phase582-mixed-launcher-output-source-v2/comparison-contract.json')
        contract=copy.deepcopy(old_contract);contract['native_profile']=NPROFILE
        assert {k:v for k,v in contract.items() if k!='native_profile'}=={k:v for k,v in old_contract.items() if k!='native_profile'}
        save(OUT/'output/comparison-contract.json',contract);contract_pin=pin(OUT/'output/comparison-contract.json')
        save(OUT/'output/contract-metadata-delta.json',dict(schema='phase621-contract-identity-delta/1',
             before=old_contract,after=contract,changed_fields=['native_profile'],all8sections_exact=True))
        b2=deltas['B2'];basis=literal(b2.text,'SOURCE_BASIS');basis['observer_tuple']=pin(OBS/'source-tuple.json');b2.assign('SOURCE_BASIS',basis)
        MODULES['B2'].write_text(b2.text);generated.append(MODULES['B2'])
        launch=deltas['launcher']
        launch.assign('INPUT_SOURCE',pin(OUT/'input/owned-files.json'));launch.assign('CONTRACT',contract_pin)
        fixed=literal(launch.text,'FIXED_INPUTS');fixed['input_source_owner']=pin(OUT/'input/owned-files.json');fixed['comparison_contract']=contract_pin
        launch.assign('FIXED_INPUTS',fixed);launch.assign('CLOSURE_EXTRACTOR',pin(MODULES['B2']));launch.assign('CLOSURE_BASIS',basis);launch.assign('CANDIDATE_CONTEXT',pin(OUT/'input/source-context.json'))
        MODULES['launcher'].write_text(launch.text);generated.append(MODULES['launcher'])
        adapter=deltas['adapter'];adapter.assign('NATIVE_PROFILE',NPROFILE)
        node=assignment(adapter.text,'NATIVE_SITES');assert isinstance(node.value,ast.Call)
        native_sites=set(ast.literal_eval(node.value.args[0]));assert len(native_sites)==107
        added=set(read(OBS/'site-census.json')['all_sites'])-native_sites;assert len(added)==3
        adapter.assign('NATIVE_SITES','frozenset('+repr(tuple(sorted(native_sites|added)))+')',expression=True)
        adapter.assign('CONTRACT_SHA256',contract_pin['sha256']);adapter.assign('CONTRACT_DESCRIPTOR',contract_pin)
        MODULES['adapter'].write_text(adapter.text);generated.append(MODULES['adapter'])
        # Existing unbound operational template shapes, no fake future descriptor.
        mreq=read(ROOT/'data/phase582-mixed-launcher-output-source-v2/model-request-template.json')
        mreq.update(launcher=pin(MODULES['launcher']),input_source_owner=pin(OUT/'input/owned-files.json'),comparison_contract=contract_pin,root_model_authorized=False)
        save(OUT/'output/model-request-template.json',mreq)
        breq=read(ROOT/'data/phase582-mixed-launcher-output-source-v2/B2-binding-template.json');breq['source_basis']=basis
        save(OUT/'output/B2-binding-template.json',breq)
        creq=read(ROOT/'data/phase582-mixed-launcher-output-source-v2/comparison-binding-template.json')
        if isinstance(creq.get('contract'),dict):creq['contract']=contract_pin
        save(OUT/'output/comparison-binding-template.json',creq)
        # Static inverse/function conservation. No generated code executed.
        census=[];compiled=[]
        expected={'host':{'validate_observer_review','source_gate','validate_active_source_tuple'},'storage':set(),
                  'A':{'authenticate_request','load_schema'},'launcher':set(),'adapter':set(),'B2':set()}
        for key in ('host','storage','A','launcher','adapter','B2'):
            delta=deltas[key];before=sources[key];assert delta.inverse()==before,('fullinverse',key)
            oldf,newf=functions(before),functions(delta.text);assert set(oldf)==set(newf)
            changed={name for name in oldf if oldf[name]!=newf[name]};assert changed==expected[key],('function surface',key,changed)
            compile(MODULES[key].read_bytes(),str(MODULES[key]),'exec');compiled.append(pin(MODULES[key]))
            save(OUT/'inverse'/(key+'.json'),dict(schema='phase621-source-fullinverse/1',before=pin(OLD[key]),after=pin(MODULES[key]),changes=delta.changes,exact=True))
            (OUT/'inverse'/(key+'.patch')).write_text(''.join(difflib.unified_diff(before.splitlines(True),delta.text.splitlines(True),fromfile=str(OLD[key].relative_to(ROOT)),tofile=str(MODULES[key].relative_to(ROOT)))))
            census.append(dict(module=key,source=pin(MODULES[key]),changed_functions=sorted(changed),exact_functions=sorted(set(oldf)-changed),full_inverse=True))
        bfreeze=read(ROOT/'data/phase580-captured-mixed-source/candidate-source-freeze.json')
        assert len(bfreeze['files'])==15
        bchecked=[]
        for row in bfreeze['files']:
            actual=pin(Path(row['path']))
            assert {k:actual[k] for k in ('size','sha256')}=={k:row[k] for k in ('size','sha256')},'exact B580 Source byte'
            bchecked.append(actual)
        assert pin(ROOT/'tests/phase578_initial_receipt.py')==bindings['receipt_source'],'exact initial Source byte'
        save(OUT/'conservation.json',dict(schema='phase621-source-conservation/1',modules=census,
             initial578=pin(ROOT/'tests/phase578_initial_receipt.py'),B580_freeze=pin(ROOT/'data/phase580-captured-mixed-source/candidate-source-freeze.json'),
             initial_unchanged=True,B580_all15_unchanged=True,B580_actual_Source_byte_checks=bchecked,C_all_function_bodies_exact=True,C20helper_reference=pin(ROOT/'data/phase582-mixed-launcher-output-source-v2/neutral-helper-line-ending-census.json'),
             contract_only_changed_field='native_profile',old_contract=pin(ROOT/'data/phase582-mixed-launcher-output-source-v2/comparison-contract.json'),new_contract=contract_pin,
             new_source_profile=NPROFILE,physical_process_lease_primitive_72_rules_unchanged=True,
             source_tuple_proposed_run_stays_null=True,selected_Source_run=RUN,Native_authority=False))
        save(OUT/'compile-only.json',dict(schema='phase621-source-compile/1',objects=compiled,generation_attempts=1,generated_imports=0,helper_calls=0,tests=0,host_plan=0,GD=0,Native=0,models=0,Expected=0,pool=0))
        allfiles=list(unique.values())+[pin(p) for p in generated]+[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()]
        closure={}
        for row in allfiles:
            assert row['path'] not in closure or closure[row['path']]==row,'final closed identity map'
            closure[row['path']]=row
        save(OUT/'source-freeze.json',dict(schema='phase621-six-module-source-freeze/1',status='SOURCE_ONLY_NOT_OPERATIONAL',files=list(closure.values()),modules={k:pin(v) for k,v in MODULES.items()},
             host_source_freeze=pin(OUT/'host/combined-source-freeze.json'),input_context=pin(OUT/'input/source-context.json'),input_owner=pin(OUT/'input/owned-files.json'),comparison_contract=contract_pin,
             observer_acceptance=obs_review,observer_acceptance_owner=obs_review_owner,selected_Source_run=RUN,actual_inputs=None,actual_B2=None,actual_model=None,actual_Expected=None,Root_oracle_authorized=False))
        save(OUT/'api.json',dict(schema='phase621-source-API/1',host=dict(module=pin(MODULES['host']),config_template=pin(OUT/'host/root-config-template.json'),CLI='existing --plan or --execute exactchoice;not invoked',review_schema='phase621-independent-host-source-review/1',review_status='ACCEPTED_SOURCE_ONLY_PENDING_ROOT_EXECUTE'),
             input=dict(module=pin(MODULES['A']),request_template=pin(OUT/'input/request-template.json'),request_keys=7,raw_leaves=12,context=pin(OUT/'input/source-context.json')),
             C=dict(launcher=pin(MODULES['launcher']),adapter=pin(MODULES['adapter']),B2=pin(MODULES['B2']),model_request_keys=17,comparison_keys=20,B2_keys=5,model_output_prefix='phase582-'),
             current_permissions=dict(oracle=False,models=0,input_build=0,Expected=0),recovery_pair_implemented=False))
        owner_files=list(closure.values())+[pin(OUT/'source-freeze.json'),pin(OUT/'api.json')]
        save(OUT/'owned-files.json',dict(schema='phase621-source-owner/1',files=owner_files,no_more_writes=True))
        print(json.dumps(dict(status='SOURCE_GENERATED_COMPILED_NOT_IMPORTED',owner=pin(OUT/'owned-files.json'),freeze=pin(OUT/'source-freeze.json'),modules=6)))
    except BaseException as exc:
        save(OUT/'first-error.json',dict(schema='phase621-source-first-error/1',type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc(),generation_attempts=1,imports=0,helpers=0,tests=0,pool=0,GD=0,Native=0,Expected=0))
        rows=[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()]+[pin(p) for p in generated]
        rows += [pin(Path(__file__)),pin(ROOT/'docs/phase621_hooks110_rebinding_implementation_spec.md')]
        save(OUT/'partial-owner.json',dict(schema='phase621-source-partial-owner/1',files=rows,no_more_writes=True))
        raise


if __name__=='__main__':main()
