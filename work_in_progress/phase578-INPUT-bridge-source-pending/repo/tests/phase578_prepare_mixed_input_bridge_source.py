"""Finite Source assembly only. Never import generated bridge/initial/schema."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import stat
import traceback

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/phase578-mixed-input-bridge-source'
SPEC='docs/phase578_mixed_input_bridge_source_implementation_spec.md'
INITIAL=ROOT/'tests/phase578_initial_receipt.py'
BRIDGE=ROOT/'tests/phase578_input_bridge.py'
CASE='NATIVE-030-MIXED-MODIFIERS-A'
PROFILE='pure-combat-mixed-modifiers-A-captured/1'
RUNTIME_SCHEMA='native-v8-pure-combat-runtime-input/mixed-modifiers-1'
IDS=[1,5,11,14,22,32,162,164,231,233,234,385]

def require(ok,message):
    if not ok:raise ValueError(message)

def read(path):
    path=Path(path);require(path.is_relative_to(ROOT),'Source root')
    require(not any(p.is_symlink() for p in (path,*path.parents)),'Source symlink')
    s=path.lstat();require(stat.S_ISREG(s.st_mode) and s.st_nlink==1,'ordinary Source')
    return path.read_bytes()

def digest(b):return hashlib.sha256(b).hexdigest()

def pin(path):
    path=Path(path);b=read(path);return dict(path=str(path.relative_to(ROOT)),size=len(b),sha256=digest(b))

def write(path,b):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as f:f.write(b)

def save(path,v):write(path,(json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n').encode())

def funcs(text):return {n.name:ast.get_source_segment(text,n) for n in ast.parse(text).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}

def assign(text,name):
    ns=[n for n in ast.parse(text).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets)]
    require(len(ns)==1,'one assignment '+name);return ns[0]

class Delta:
    def __init__(self,path):self.path=path;self.before=read(path).decode();self.text=self.before;self.edits=[]
    def replace(self,a,b):
        require(a!=b and self.text.count(a)==1,'one exact delta: '+a[:100])
        position=self.text.index(a);self.text=self.text[:position]+b+self.text[position+len(a):]
        self.edits.append(dict(before=a,after=b,position=position))
    def constant(self,name,value):
        old=ast.get_source_segment(self.text,assign(self.text,name));self.replace('\n'+old+'\n','\n'+name+' = '+repr(value)+'\n')
    def function(self,name,new):self.replace(funcs(self.text)[name],new)
    def finish(self,path,changed):
        compile(self.text,str(path),'exec',dont_inherit=True)
        reverse=self.text
        for e in reversed(self.edits):
            p=e['position'];require(reverse[p:p+len(e['after'])]==e['after'],'inverse actual segment');reverse=reverse[:p]+e['before']+reverse[p+len(e['after']):]
        require(reverse==self.before,'complete byte inverse')
        a,b=funcs(self.before),funcs(self.text);require(set(a)==set(b),'same function inventory')
        actual=sorted(n for n in a if a[n]!=b[n]);require(set(actual)==set(changed),'unexpected functions '+repr(actual))
        write(path,self.text.encode())
        report=dict(before=pin(self.path),after=pin(path),changed_functions=actual,conserved_functions=sorted(set(a)-set(actual)),edits=self.edits,inverse='EXACT_COMPLETE_BYTES')
        save(OUT/(path.stem+'-inverse.json'),report)
        write(OUT/(path.stem+'.patch'),''.join(difflib.unified_diff(self.before.splitlines(True),self.text.splitlines(True),fromfile=str(self.path.relative_to(ROOT)),tofile=str(path.relative_to(ROOT)))).encode())
        return report


def derive_initial():
    d=Delta(ROOT/'tests/phase528_initial_receipt.py')
    premise=list(ast.literal_eval(assign(d.text,'SOURCE_PREMISES').value));premise[2]='572v2/575 fixed twelve-ID zeroKing Source domain; Source-only synthetic acceptance is not new actual object/application or Native seed law.'
    d.constant('SOURCE_PREMISES',tuple(premise))
    old=funcs(d.text)['validate_ledger'];d.function('validate_ledger',old.replace('phase502-zero-king-input-facts/1','phase572-zero-king-input-facts/1'))
    old=funcs(d.text)['build_initial_receipt'];new=old.replace('phase511-actual-object-initial-receipt/1','phase578-actual-object-initial-receipt/1').replace('pure-combat-whelp-family-A-captured/1',PROFILE)
    new=new.replace("'prepare_observations': {},", "'prepare_observations': {}, 'resource_observations': {},")
    new=new.replace("len(nodes) == len(set(current_ids.values())) == 67", "len(nodes) == len(set(current_ids.values())) == 1 + len(COMMON) + 5 + len(schema.FIXED_ROLES)")
    needle="        for si, resource in enumerate(resources):"
    require(new.count(needle)==1,'resource loop');new=new.replace(needle,"        result['resource_observations'][phase] = {}\n"+needle)
    needle="            for field, value in (('invulnerable', {'type': 'bool', 'value': False}), ('invulnerabilityItem', {'type': 'null'})):"
    replacement="""            observed_resources = {}
            for field in ('baseStaminaRegen','staminaRegen'):
                value = resource[field]
                schema.validate_typed(value); require(value['type'] == 'float','ACTUAL_CHARACTER_RESOURCE_REAL')
                schema.scalar_number(value)
                source_ref = ref(record, f'/payload/source_resources/{si}/{field}', owner['native_id'], line)
                put('Character.' + field, phase, side, value, [source_ref])
                observed_resources[field] = deepcopy(value)
                observed_resources[field + '_ref'] = source_ref
            observed_resources['native_id'] = owner['native_id']
            result['resource_observations'][phase][side] = observed_resources
"""+needle
    require(new.count(needle)==1,'invu resource splice');new=new.replace(needle,replacement)
    start=new.index("            if role == 'P:9':");end=new.index("        result['prepare_observations'][phase]",start)
    new=new[:start]+'''            index = schema.ITEM_INDEX_BY_ROLE[role]
            required_fields = ['speedScale','iterationCooldown','triggerTime','doubleActivationChance','doubleAttackEffectChance']
            if index == 162:required_fields += ['speedBonusGiven']
            elif index == 231:required_fields += ['numBuffs','staminaRegenPerBuff']
            elif index == 385:required_fields += ['buffs']
            observed_fields, field_refs = {}, {}
            for field in required_fields:
                value = fields[field];schema.validate_typed(value)
                allowed = ('int',) if field in ('numBuffs','buffs') else (('null','float') if field == 'staminaRegenPerBuff' and phase == 'pre_prepare' else ('float',))
                require(value['type'] in allowed,'MIXED_DIRECT_TYPED_' + field)
                if value['type'] == 'float':schema.scalar_number(value)
                observed_fields[field] = deepcopy(value)
                field_refs[field] = ref(record, f'/payload/items/{ii}/fields/{field}', aliases['role_to_native'][role], line)
                put('Item.' + field, phase, role, value, [field_refs[field]])
            if index == 231:integer(fields['numBuffs'],3)
            if index == 385:integer(fields['buffs'],1)
            observations[role]['item_index'] = index
            observations[role]['typed_fields'] = observed_fields
            observations[role]['typed_field_refs'] = field_refs
''' +new[end:]
    d.function('build_initial_receipt',new)
    return d

AUTHENTICATE = '''def authenticate_request(request_raw,request_pin,context_raw):
    require(type(request_pin) is dict and set(request_pin)=={'path','size','sha256'},'EXPLICIT_ROOT_REQUEST_PIN')
    canonical(request_pin['path'])
    require(type(request_pin['size']) is int and type(request_pin['sha256']) is str and re.fullmatch('[0-9a-f]{64}',request_pin['sha256']) is not None,'ROOT_REQUEST_PIN_TYPES')
    require(type(request_raw) is bytes and len(request_raw)==request_pin['size'] and hashlib.sha256(request_raw).hexdigest()==request_pin['sha256'],'ROOT_SELECTED_REQUEST_BYTES')
    request=strict_json(request_raw)
    require(type(request) is dict and set(request)=={'schema','case_id','run_name','source_context','input_descriptors','models_allowed','expected_allowed'},'CLOSED_ROOT_REQUEST')
    require(request['schema']=='phase578-root-bound-input-request/1' and request['case_id']==CASE and request['run_name']==RUN,'FIXED_NEW_CASE_RUN')
    require(all(type(request[k]) is int and request[k]==0 for k in ('models_allowed','expected_allowed')),'REQUEST_STRICT_INT0')
    cp=request['source_context']
    require(type(cp) is dict and set(cp)=={'path','size','sha256'},'EXPLICIT_CONTEXT_PIN')
    canonical(cp['path'])
    require(type(cp['size']) is int and type(cp['sha256']) is str and type(context_raw) is bytes and len(context_raw)==cp['size'] and hashlib.sha256(context_raw).hexdigest()==cp['sha256'],'ROOT_BOUND_CONTEXT_BYTES')
    context=strict_json(context_raw)
    require(type(context) is dict and set(context)=={'schema','case_id','profile','runtime_schema','schema_module','fixed_source_bindings','source_pins','source_rules','prepared_gate'},'CLOSED_SOURCE_CONTEXT')
    require(context['schema']=='phase578-fixed-source-context/1' and context['case_id']==CASE and context['profile']==PROFILE and context['runtime_schema']==RUNTIME_SCHEMA and same(context['schema_module'],SCHEMA_PIN),'EXACT578_SOURCE_CONTEXT')
    bindings=context['fixed_source_bindings']
    require(type(bindings) is dict and set(bindings)==set(FIXED_SOURCE_BINDINGS)|{'candidate_freeze','candidate_interface_acceptance'},'CLOSED_FIXED_AND_FUTURE_SOURCE_BINDINGS')
    require(all(same(bindings[k],p) for k,p in FIXED_SOURCE_BINDINGS.items()) and same(context['source_rules'],SOURCE_RULES),'NO_CALLER_PROOF_FLAGS_OR_SOURCE_DRIFT')
    for name in ('candidate_freeze','candidate_interface_acceptance'):
        p=bindings[name]
        require(type(p) is dict and set(p)=={'path','size','sha256'},'CANDIDATE_SOURCE_UNBOUND')
        require(type(p['size']) is int and 0<p['size']<=4194304 and type(p['sha256']) is str and re.fullmatch('[0-9a-f]{64}',p['sha256']) is not None,'CANDIDATE_SOURCE_DESCRIPTOR')
        path=canonical(p['path']);relative=path.relative_to(REPO)
        require(len(relative.parts)==3 and relative.parts[0]=='data' and re.fullmatch(r'phase[0-9]+-[A-Za-z0-9_-]+',relative.parts[1]) is not None,'CANDIDATE_SOURCE_METADATA_DOMAIN')
        require(path.name==('candidate-source-freeze.json' if name=='candidate_freeze' else 'review.json'),'CANDIDATE_SOURCE_METADATA_LEAF')
    require(context['prepared_gate']=='EXTERNAL_SAME_INSTANCE_BUSINESS_PREPARE_GATE_REQUIRED_BEFORE_ACTIVATION','PREPARED_GATE_NOT_CERTIFIED_BY_BRIDGE')
    pins=request['input_descriptors']
    require(type(pins) is dict and set(pins)==set(LAWFUL),'EXACT12_ROOT_INPUT_PINS_REQUIRED')
    parents=set()
    for name,p in pins.items():
        require(type(p) is dict and set(p)=={'path','size','sha256'},'INPUT_PIN_SHAPE')
        require(type(p['size']) is int and 0<p['size']<=4194304 and type(p['sha256']) is str and re.fullmatch('[0-9a-f]{64}',p['sha256']) is not None,'INPUT_PIN_TYPES')
        path=canonical(p['path']);require(path.name==name,'LAWFUL_LEAF_NAME');parents.add(str(path.parent))
    require(len(parents)==1,'ONE_EXPLICIT_LAWFUL_INPUT_ROOT')
    require(type(context['source_pins']) is list and context['source_pins'],'EXPLICIT_SOURCE_PINS')
    allowed={p['path'] for p in bindings.values()} | {'tests/phase578_input_bridge.py','data/phase578-mixed-input-bridge-source/branch-source-rule.json','data/phase578-mixed-input-bridge-source/abi.json','data/phase578-mixed-input-bridge-source/typed-witness-contract.json'}
    require(len(context['source_pins'])==len(allowed) and {p['path'] for p in context['source_pins']}==allowed,'CLOSED_SOURCE_PIN_PATHS_NO_EXPECTED')
    actual={p['path']:p for p in context['source_pins']}
    for p in bindings.values():require(same(actual[p['path']],p),'ROOT_BOUND_SOURCE_PIN_IDENTITY')
    return request,context'''

VERIFY_CONTEXT = '''def verify_source_context(context,io):
    # Runs only after authenticate_request rejected unbound templates.
    seen=set();values={}
    for p in context['source_pins']:
        path=str(canonical(p['path']));require(path not in seen,'SOURCE_PIN_DUPLICATE');seen.add(path);values[p['path']]=read_pinned(p,io)
    bindings=context['fixed_source_bindings']
    required={str(canonical(p['path'])) for p in bindings.values()}
    require(required<=seen and str(Path(__file__).absolute()) in seen,'FIXED_SOURCE_AND_PROJECTOR_PINS_REQUIRED')
    freeze=strict_json(values[bindings['candidate_freeze']['path']])
    require(type(freeze) is dict and freeze.get('profile')==PROFILE and type(freeze.get('files')) is list and len(freeze['files'])==15,'ROOT_BOUND_CANDIDATE_PROFILE_AND15_SOURCE_METADATA')
    receipt=strict_json(values[bindings['candidate_interface_acceptance']['path']])
    require(type(receipt) is dict and type(receipt.get('schema')) is str,'ROOT_BOUND_INTERFACE_RECEIPT_METADATA')
    return {'status':STATUS,'fixed_source_bindings':deepcopy(bindings),'source_rules':deepcopy(SOURCE_RULES),'model_release':False,
            'candidate_binding_scope':'Explicit Root hash-bound Source metadata only; not semantic interface acceptance or model authorization'}'''

def derive_bridge(fixed,rules):
    d=Delta(ROOT/'tests/phase528_input_bridge.py')
    d.replace('from phase528_initial_receipt import build_initial_receipt,value_index','from phase578_initial_receipt import build_initial_receipt,value_index')
    for name,value in [('CASE',CASE),('RUN','original030-mixed-modifiers-A-single-001'),('PROFILE',PROFILE),('RUNTIME_SCHEMA',RUNTIME_SCHEMA),
                       ('SCHEMA_PIN',fixed['schema_module']),('FIXED_SOURCE_BINDINGS',fixed),('SOURCE_RULES',rules)]:d.constant(name,value)
    d.function('authenticate_request',AUTHENTICATE)
    old=funcs(d.text)['load_schema'];new=old.replace('EXACT_PINNED502_SCHEMA_BYTES','EXACT_PINNED572_SCHEMA_BYTES').replace('_phase511_exact502_schema','_phase578_exact572_schema').replace('7-whelp-family-A-502','7-mixed-modifiers-A-572').replace('observer7-whelp-family-A-native-tape/1','observer7-mixed-modifiers-A-native-tape/1').replace('frozenset({1,11,22,23,64,164,197,199,201})','frozenset({1,5,11,14,22,32,162,164,231,233,234,385})')
    d.function('load_schema',new)
    old=funcs(d.text)['project_runtime'];new=old.replace("len(timers) == 32 and len(processing) == 67 and len(nodes) == 66", "len(timers) == len(schema.TIMER_ROLES) == 32 and len(processing) == 1 + len(nodes) and len(nodes) == len(schema.TIMER_ROLES) + 5 + len(schema.FIXED_ROLES)").replace('data/phase513-input-bridge-source/abi.json','data/phase578-mixed-input-bridge-source/abi.json')
    d.function('project_runtime',new)
    old=funcs(d.text)['project_prepared_witnesses'];new=old.replace('phase511-lawful-prepared-witness/1','phase578-lawful-prepared-witness/1')
    start=new.index("    require(len(result['items'])==29");new=new[:start]+'''    require(set(result['items'])==schema_fixed_roles(receipt),'PREPARED29_ACTUAL_SPECIAL_IDENTITIES')
    for role,index in (('P:12',162),('P:13',231),('P:14',164),('P:19',385),('O:4',231)):
        require(role in result['items'] and result['items'][role]['item_index']==index,'PREPARED_MIXED_DESCRIPTOR_ROLE')
    result['characters'] = deepcopy(receipt['resource_observations']['pre_activate'])
    result['pre_prepare_characters'] = deepcopy(receipt['resource_observations']['pre_prepare'])
    require(set(result['characters'])=={'P','O'},'PREPARED_CHARACTER_RESOURCE_PAIR')
    result['source_default_p1'] = deepcopy(SOURCE_RULES['mixed_prepared'])
    return result'''
    # The role set is derived from actual receipt keys, checked earlier against the schema.
    new=new.replace("set(result['items'])==schema_fixed_roles(receipt)","len(result['items'])==29 and set(result['items'])==set(receipt['prepare_observations']['pre_prepare'])")
    d.function('project_prepared_witnesses',new)
    old=funcs(d.text)['validate_initial_consumer_coverage'];new=old.replace("len(data['timer_initial'])==32 and len(data['processing_nodes'])==67 and len(data['nodes'])==66 and len(data['initial_items'])==29", "len(data['timer_initial'])==32 and len(data['nodes'])==32+5+len(data['initial_items']) and len(data['processing_nodes'])==1+len(data['nodes']) and len(data['initial_items'])==29")
    needle="    for field in bundle:require('bundle.'+field in origins,'BUNDLE_ORIGIN_'+field)"
    require(new.count(needle)==1,'coverage witness stage');new=new.replace(needle,"    require(set(witness['characters'])=={'P','O'} and all('typed_fields' in x and 'typed_field_refs' in x for x in witness['items'].values()),'COMPLETE_MIXED_TYPED_PREPARED_WITNESSES')\n"+needle)
    d.function('validate_initial_consumer_coverage',new)
    old=funcs(d.text)['project_decoded'];new=old.replace("'source':'511 ABI'","'source':'578 ABI'").replace("'source':'511 runtime14 ABI'","'source':'578 runtime14 ABI'").replace('phase511-input-only-projection-proof/1','phase578-input-only-projection-proof/1');d.function('project_decoded',new)
    d.function('verify_source_context',VERIFY_CONTEXT)
    old=funcs(d.text)['build_from_files'];new=old.replace('phase511-root-bound-input-request/1','phase578-root-bound-input-request/1').replace("output.name.startswith('phase511-')","output.name.startswith('phase578-')").replace('phase511-input-only-seal/1','phase578-input-only-seal/1').replace('phase511-output-owner/1','phase578-output-owner/1');d.function('build_from_files',new)
    d.replace('Case029 lawful INPUT-only bridge. No schema load/default request at import.','Case030 lawful INPUT-only bridge. No schema load/default request at import.')
    return d


def main():
    require(not OUT.exists() and not INITIAL.exists() and not BRIDGE.exists(),'new Source outputs only')
    OUT.mkdir()
    try:
        # Verify the selected immutable preimages, not Native records or pool.
        expected={'tests/phase528_initial_receipt.py':'95173bc927049e101c7a3d696ebad050eabf744adb5ddec00ba3db9e3650963a',
          'tests/phase528_input_bridge.py':'a25c033845e560594fc11825ed1cf303a5cd00b4251423ce9515dbec256df245',
          'data/phase572-mixed-observer-source-v2/source-owner.json':'3f35f3a12a45d698b77362ed86143adbda9d85352b1c2a34ee1387a83ba728c6',
          'data/phase572-mixed-observer-source-v2/schema/phase572_mixed_observer_schema.py':'fd7da3dd9c95e44de14b09557130659a0ab6d20713f447695fc19a89e5ee9b43',
          'data/phase575-independent-final-acceptance/review.json':'526d09b0de3948ff8932d7064dc6ef934c6674cfb89d8a6621f203c056edd3a7',
          'data/phase577-independent-mixed-consumer-design-review/review.json':'4194690041ac33db11873596363384b03a9e5687f8f66a9a53d09e8c6fe8e75a'}
        for p,h in expected.items():require(pin(ROOT/p)['sha256']==h,'preimage drift '+p)
        save(OUT/'source-before.json',dict(schema='phase578-source-before/1',files=[pin(ROOT/p) for p in expected],source_generation_attempt=1,Native=0,models=0))
        initial=derive_initial();ir=initial.finish(INITIAL,['validate_ledger','build_initial_receipt'])
        old_bridge=read(ROOT/'tests/phase528_input_bridge.py').decode()
        old_bind=ast.literal_eval(assign(old_bridge,'FIXED_SOURCE_BINDINGS').value)
        fixed={k:v for k,v in old_bind.items() if k not in ('candidate_freeze','candidate_interface_acceptance','receipt_source','schema_module','observer_tuple','observer_owner','observer_acceptance')}
        for name,path in [('receipt_source',INITIAL),('schema_module',ROOT/'data/phase572-mixed-observer-source-v2/schema/phase572_mixed_observer_schema.py'),
                          ('observer_tuple',ROOT/'data/phase572-mixed-observer-source-v2/source-tuple.json'),('observer_owner',ROOT/'data/phase572-mixed-observer-source-v2/source-owner.json'),
                          ('observer_acceptance',ROOT/'data/phase575-independent-final-acceptance/review.json'),('default_p1_rule',ROOT/'data/phase572-mixed-observer-source-v2/source-default-p1-rule.json')]:fixed[name]=pin(path)
        # Preserve inherited branch Source reason, replace only case/domain/current Source tuple.
        branch=json.loads(read(ROOT/'data/phase511-input-bridge-source/branch-source-rule.json'))
        branch['schema']='phase578-fixed-source-cooldown-predicate-closure/1';branch['case_id']=CASE;branch['source_tuple']=fixed['observer_tuple']
        branch['local_closure']='Fixed current collector startFreshRun(Unranked) -> prepareItems -> Character.prepare -> original Item.preCombatStart adjustCooldown. Closed twelve-ID Bowl/Food/Wolper/Enchanted/ForestFriend/fourWeapon family changes no Game mode/league writer; inherited bounded ordinary Source premise retained. New complete O startup site stream required; no actual new witness asserted.'
        branch['new_family_Source_reviews']=[pin(ROOT/'data/phase575-independent-final-acceptance/review.json'),pin(ROOT/'data/phase577-independent-mixed-consumer-design-review/review.json')]
        save(OUT/'branch-source-rule.json',branch)
        old_rules=ast.literal_eval(assign(old_bridge,'SOURCE_RULES').value)
        rules=old_rules
        rules['cooldown_predicate']['descriptor']=pin(OUT/'branch-source-rule.json')
        rules['terminal_profiles']['observer_source']=fixed['observer_tuple']
        rules['terminal_profiles']['runtime_source']=None
        rules['terminal_profiles']['meaning']='Distinct producer policy and578 frozen consumer ABI; future candidate Source is an explicit unbound context slot, no fake pin.'
        rules['mixed_prepared']=dict(source_default_p1=fixed['default_p1_rule'],observed_p1=False,actual_coefficient='observed REAL0.7*same-cut actual base/100, validated by572 fulljoin',same_instance_gate='REQUIRED_EXTERNAL_NOT_EXECUTED')
        abi=dict(schema='phase578-input-ABI/1',runtime_schema=RUNTIME_SCHEMA,profile=PROFILE,
            runtime_keys=ast.literal_eval(assign(old_bridge,'RUNTIME_KEYS').value),status='INPUT_ONLY_NOT_RUNTIME_VALIDATED',
            observer_collector_policy='first-actual-idle-after-at-least-two-future-physics/1',runtime_terminal_profile='source-two-physics-idle-pre-internal/1',
            observer_policy_source=fixed['observer_tuple'],candidate_source=None,candidate_binding='UNBOUND_TEMPLATE_MUST_REJECT',
            role_policy=dict(raw_timers=32,business_timers=26,inactive_timers=6,ordinary_nonroot_base=5,items=29,total_configs_formula='32+5+actualitems',total_configs_if29=66,processing_formula='1+totalconfigs',processing_if29=67,actual_native_counts=None),
            derived_private_and_character=72,model_release=False)
        save(OUT/'abi.json',abi)
        witness_contract=dict(schema='phase578-typed-prepared-witness-contract/1',scope='LAWFUL_INPUT_ONLY_NOT_MODEL_EQUIVALENCE',
            common_REAL=['speedScale','iterationCooldown','triggerTime','doubleActivationChance','doubleAttackEffectChance'],
            subtype_fields={'162':{'speedBonusGiven':'REAL'},'231':{'numBuffs':'INT3','staminaRegenPerBuff':'NILorREALpre/REALpost'},'385':{'buffs':'INT1'}},
            character_REAL=['baseStaminaRegen','staminaRegen'],business_cache_consumers=['P:12','P:13','P:14','P:19','P:20','P:21','O:4'],
            all_color_current_provenance=True,same_instance_business_prepare_gate='REQUIRED_EXTERNAL_NOT_EXECUTED',
            old_Basic_Sapphire_special_cases=False,model_state_added=False)
        save(OUT/'typed-witness-contract.json',witness_contract)
        bridge=derive_bridge(fixed,rules);br=bridge.finish(BRIDGE,['authenticate_request','load_schema','project_runtime','project_prepared_witnesses','validate_initial_consumer_coverage','project_decoded','verify_source_context','build_from_files'])
        bindings=dict(fixed,candidate_freeze=None,candidate_interface_acceptance=None)
        source_pins={p['path']:p for p in fixed.values()}
        for path in [BRIDGE,OUT/'branch-source-rule.json',OUT/'abi.json',OUT/'typed-witness-contract.json']:source_pins[pin(path)['path']]=pin(path)
        context=dict(schema='phase578-fixed-source-context/1',case_id=CASE,profile=PROFILE,runtime_schema=RUNTIME_SCHEMA,
            schema_module=fixed['schema_module'],fixed_source_bindings=bindings,source_pins=list(source_pins.values()),source_rules=rules,
            prepared_gate='EXTERNAL_SAME_INSTANCE_BUSINESS_PREPARE_GATE_REQUIRED_BEFORE_ACTIVATION')
        save(OUT/'source-context-template.json',context)
        lawful=ast.literal_eval(assign(old_bridge,'LAWFUL').value)
        save(OUT/'request-template.json',dict(schema='phase578-root-bound-input-request/1',case_id=CASE,run_name='original030-mixed-modifiers-A-single-001',
            source_context=pin(OUT/'source-context-template.json'),input_descriptors={name:None for name in lawful},models_allowed=0,expected_allowed=0))
        save(OUT/'api-contract.json',dict(schema='phase578-source-api/1',modules=dict(initial=pin(INITIAL),reader=pin(BRIDGE)),
            interfaces=['build_initial_receipt(decoded,aliases,schema)','project_from_bytes(raw12,request_raw,request_pin,context_raw,schema_raw)','build_from_files(output_new,request_pin)'],
            template_status='UNBOUND_NON_EXECUTABLE_CANDIDATE_SOURCE_UNBOUND',default_request=None,
            future_context_policy='New immutable Root SHA-bound context supplies closed candidate_freeze/interface_receipt descriptors; old template never overwritten',
            external_interfaces_not_implemented=['captured candidate B','same-instance modelgate/finalaux/strict8 C'],author_SUT_calls=0))
        conserved=['strict_json','canonical','physical','read_pinned','save_new','typed_scalar','model_role','source_value','project_primitives','project_fixture','derive_branch_witness','decode_lawful12','project_from_bytes']
        for n in conserved:require(funcs(bridge.before)[n]==funcs(bridge.text)[n],'bridge kernel exact '+n)
        for n in ['validate_timer','parent_spec','validate_cache_alias','ref','value_index']:require(funcs(initial.before)[n]==funcs(initial.text)[n],'initial kernel exact '+n)
        save(OUT/'conservation.json',dict(schema='phase578-source-conservation/1',initial_changed=ir['changed_functions'],reader_changed=br['changed_functions'],
            bridge_conserved_helpers=conserved,initial_conserved_helpers=['validate_timer','parent_spec','validate_cache_alias','ref','value_index'],
            inverse='BOTH_COMPLETE_PREIMAGE_BYTES',candidate_files_changed=0,source_generation_attempts=1,
            schema_helper_or_reader_calls=0,models=0,Native=0,Expected=0,pool=0))
        compile(read(Path(__file__)),str(Path(__file__)),'exec',dont_inherit=True)
        save(OUT/'compile-only.json',dict(schema='phase578-compile-only/1',discarded_compile_objects=3,new_initial=True,new_reader=True,producer=True,
            candidate_imports=0,schema_imports=0,reader_helper_calls=0,INPUT_builds=0,model=0,Native=0,Expected=0,pool=0))
        external=[pin(ROOT/p) for p in expected]+[p for p in fixed.values()]+[pin(ROOT/'data/phase577-independent-mixed-consumer-design-review/review.json'),pin(ROOT/'data/phase576-mixed-captured-consumer-design/owned-files.json')]
        generated=[pin(p) for p in sorted(OUT.iterdir()) if p.is_file()]+[pin(INITIAL),pin(BRIDGE),pin(Path(__file__)),pin(ROOT/SPEC)]
        unique={}
        for p in generated+external:
            require(p['path'] not in unique or unique[p['path']]==p,'one physical Source descriptor');unique[p['path']]=p
        save(OUT/'source-freeze.json',dict(schema='phase578-source-freeze/1',files=list(unique.values()),status='SOURCE_ONLY_UNBOUND_TEMPLATE_NOT_RUNTIME',
            ABI=pin(OUT/'abi.json'),context_template=pin(OUT/'source-context-template.json'),candidate_source_bound=False,actual_Input_bound=False,
            imports=0,INPUT_build=0,model=0,Native=0))
        unique[pin(OUT/'source-freeze.json')['path']]=pin(OUT/'source-freeze.json')
        save(OUT/'owned-files.json',dict(schema='phase578-source-owner/1',files=list(unique.values()),status='FROZEN_SOURCE_ONLY_PENDING_INDEPENDENT579',no_more_writes=True))
        print(json.dumps(dict(status='SOURCE_FROZEN_UNBOUND_NO_SUT',owner=pin(OUT/'owned-files.json')),sort_keys=True));return 0
    except Exception as error:
        save(OUT/'first-generation-error.json',dict(schema='phase578-source-first-error/1',error_type=type(error).__name__,message=str(error),traceback=traceback.format_exc(),automatic_retry=False,schema_calls=0,reader_calls=0,models=0,Native=0,Expected=0,pool=0))
        partial=[pin(p) for p in sorted(OUT.iterdir()) if p.is_file()]
        for p in [INITIAL,BRIDGE]:
            if p.exists():partial.append(pin(p))
        save(OUT/'partial-source-owner.json',dict(schema='phase578-partial-source-owner/1',files=partial+[pin(Path(__file__)),pin(ROOT/SPEC)],status='SOURCE_FIRST_ERROR_PRESERVED_NO_RETRY'))
        raise

if __name__=='__main__':raise SystemExit(main())
