"""Finite SOURCE preparation only. No generated import/projection/schema or Native reads."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import traceback

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/phase511-input-bridge-source'
INITIAL=ROOT/'tests/phase511_initial_receipt.py'
BRIDGE=ROOT/'tests/phase511_input_bridge.py'
SPEC=ROOT/'docs/phase511_case029_input_bridge_source_spec.md'


def require(ok,message):
    if not ok:raise ValueError(message)


def pin(path):
    raw=path.read_bytes();return dict(path=str(path.relative_to(ROOT)),size=len(raw),sha256=hashlib.sha256(raw).hexdigest())


def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(value,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')


def functions(text):return {n.name:ast.get_source_segment(text,n) for n in ast.parse(text).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}


def replace(text,a,b):
    require(text.count(a)==1,'unique Source anchor '+a[:100]);return text.replace(a,b)


PARENT = '''def parent_spec(role):
    if role.startswith('fatigue:'):
        return 'combat_timer','FatigueStartTimer' if role.endswith('start') else 'FatigueTickTimer',None
    parts=role.split(':');side=parts[1]
    if parts[0]=='buff':return 'character:'+side,None,None
    if parts[0]=='tick':return 'character:'+side,'TickTimer',None
    if parts[0]=='invu':return 'character:'+side,'InvulnerabilityTimer',None
    return 'character:'+side,'BattleRageTimer' if parts[2]=='battleRageTimer' else 'AutoRageTimer',None'''

LEDGER = '''def validate_ledger(facts,role,owner,timer,schema):
    require(type(facts) is dict and facts.get('schema')=='phase502-zero-king-input-facts/1' and facts.get('kings')==[],'INITIAL_ZERO_KING_FACTS')
    fact=facts['timers'].get(role)
    require(type(fact) is dict and set(fact)=={'lineage','current','private_provenance'},'INITIAL_FACT_SHAPE')
    ledger=fact['lineage']
    require(type(ledger) is dict and set(ledger)=={'timer_id','owner_id','kind','starts','stops','birth'},'INITIAL_LEDGER_SHAPE')
    require(ledger['timer_id']==timer['node']['native_id'] and ledger['owner_id']==owner['native_id']
            and ledger['kind']=='Character.scene.ready','INITIAL_LEDGER_OWNER_KIND')
    require(type(ledger['starts']) is int and ledger['starts']==0 and type(ledger['stops']) is int and ledger['stops']>=0,'LIFETIME_NO_START_NONNEGATIVE_STOPS')
    birth=ledger['birth'];schema.validate_state(birth,'timer',constructor=True);bn=birth['node']
    require(bn['native_id']==timer['node']['native_id'] and bn['role'] is None and bn['class']=='Timer'
            and bn['name']==timer['node']['name'],'INITIAL_BIRTH_ID_CLASS_NAME')
    for field in ('process_mode','wait_time','one_shot','autostart','paused','stopped','time_left'):
        require(same(birth[field],timer[field]),'INITIAL_BIRTH_CONFIG_'+field)
    require(type(birth['process_mode']) is int and type(birth['paused']) is bool and type(birth['autostart']) is bool,'BIRTH_STRICT_TYPES')
    for field in ('ordinary_physics','internal_physics','ordinary_idle','internal_idle'):
        require(type(bn[field]) is bool and bn[field] is False,'BIRTH_INACTIVE_FLAGS')
    require(bn['inside_tree'] is True and bn['path']==timer['node']['path']
            and bn['path']==owner['path']+'/'+bn['name'] and bn['positions'][:-1]==owner['positions'],'CHARACTER_BIRTH_ACTUAL_PARENT')
    require(same(fact['current'],timer),'FACTS_CURRENT_CUT_JOIN')
    return {'file':'king-input-facts.json','pointer':'/timers/'+role+'/lineage',
            'native_owner':timer['node']['native_id'],'lineage':deepcopy(ledger)}'''


def initial_source():
    path=ROOT/'tests/phase470_joint_initial_receipt.py';old=path.read_text();text=old
    text=replace(text,"KING_TIMER = 'king_buff:P:6'\n",'')
    text=replace(text,functions(text)['parent_spec'],PARENT)
    timer=functions(text)['validate_timer']
    timer=timer.replace("('RigidBody2D' if role == KING_TIMER else 'Node2D')","'Node2D'")
    start=timer.index('    if child is not None:');end=timer.index('    require(parent[',start)
    timer=timer[:start]+timer[end:]
    text=replace(text,functions(text)['validate_timer'],timer)
    text=replace(text,functions(text)['validate_ledger'],LEDGER)
    node=next(n for n in ast.parse(text).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SOURCE_PREMISES' for t in n.targets))
    premises=('Accepted G02 ordinary legitimate native Timer processing invariant, closed modes/no escaped inherited flag writers/reentry; not publiczero proof.',
        'Accepted438 Character pre-ready caller/default domain plus actual two invu birth/owner/monotonic lifetime zero-start ledgers; no resets assumed.',
        '502v4/503 fixed nine-ID zeroKing producer domain and accepted shared native rule origins are Source premises; no old instance audit or Native seed law.',
        '32 actual new Timer identities at two uniquely located cuts: pausedfalse/internalflagsfalse supports private-1; no fresh-history assertion for every native object.')
    text=replace(text,ast.get_source_segment(text,node),'SOURCE_PREMISES = '+repr(premises))
    f=functions(text)['build_initial_receipt']
    f=replace(f,"    require([x['sequence'] for x in cuts] == [99, 1149], 'ACTUAL_FIXED_INITIAL_CUTS')", "    require(cuts[0]['sequence'] < cuts[1]['sequence'],'ACTUAL_INITIAL_CUT_ORDER')\n    schema.validate_single_king_fresh_facts(decoded['king-input-facts.json'])")
    f=f.replace('phase470-actual-object-initial-receipt/1','phase511-actual-object-initial-receipt/1').replace('pure-combat-king-basic-A-captured/1','pure-combat-whelp-family-A-captured/1')
    f=replace(f,"    for phase, record, line in zip(PHASES, cuts, (1, 4)):","    for phase, record in zip(PHASES,cuts):\n        line=next(i for i,row in enumerate(rows,1) if row is record)")
    f=replace(f,"timer_roles == set(COMMON) | {KING_TIMER, 'king_hide:P:6', 'king_drag:P:6'}, 'EXACT_35_RAW_TIMERS'", "timer_roles == set(COMMON), 'EXACT32_RAW_TIMERS'")
    f=replace(f,'for role in COMMON + (KING_TIMER,):','for role in COMMON:')
    f=replace(f,"'FRESH_KING_NATIVE_SCENE_NO_START' if role == KING_TIMER else 'INACTIVE_PROCESSING_INVARIANT'","'INACTIVE_PROCESSING_INVARIANT'")
    f=f.replace("len(payload['items']) == 26", "len(payload['items']) == 29").replace('INITIAL26_ITEMS','INITIAL29_ITEMS')
    a=f.index("            if role in ('P:6', 'P:7'):");b=f.index("        result['prepare_observations'][phase]",a)
    f=f[:a]+'''            if role == 'P:9':
                threshold='4014000000000000';integer(fields['activations'],0)
                require(same(fields['activationsToTrigger'],{'type':'float','binary64_be':threshold}),'BASIC_TYPED_THRESHOLD5')
                for field in ('iterationCooldown','triggerTime'):
                    require(same(fields[field],ZERO if phase=='pre_prepare' else {'type':'float','binary64_be':threshold}),'BASIC_PREPARE_STAGE_'+field)
                observations[role]['goobert_state']={k:deepcopy(fields[k]) for k in ('activations','activationsToTrigger','iterationCooldown','triggerTime')}
            if role == 'P:14':
                expected={'type':'array','values':[{'type':'int','decimal':str(i)} for i in (101,102,103,104,106,107)]}
                require(same(fields['stackTypes'],expected),'SAPPHIRE_ORDERED_SIX_INT')
                observations[role]['stackTypes']=deepcopy(fields['stackTypes'])
''' + f[b:]
    f=f.replace("('invu:P', 'invu:O', KING_TIMER)","('invu:P','invu:O')")
    a=f.index("    scenes = [r for r in decoded['observer7-lineage.jsonl']");b=f.index("    derived = ",a);f=f[:a]+f[b:]
    f=f.replace("len(derived) == 74, 'NEW74_DERIVED_INITIAL_FACTS'","len(derived) == 72, 'NEW64_TIMER_PLUS8_CHARACTER_FACTS'")
    text=replace(text,functions(text)['build_initial_receipt'],f)
    require('KING_TIMER' not in text and '[99, 1149]' not in text,'no old King/cut branch')
    return path,old,text

REQUEST = '''def authenticate_request(request_raw,request_pin,context_raw):
    require(type(request_pin) is dict and set(request_pin)=={'path','size','sha256'},'EXPLICIT_ROOT_REQUEST_PIN')
    canonical(request_pin['path'])
    require(type(request_pin['size']) is int and type(request_pin['sha256']) is str and re.fullmatch('[0-9a-f]{64}',request_pin['sha256']) is not None,'ROOT_REQUEST_PIN_TYPES')
    require(type(request_raw) is bytes and len(request_raw)==request_pin['size'] and hashlib.sha256(request_raw).hexdigest()==request_pin['sha256'],'ROOT_SELECTED_REQUEST_BYTES')
    request=strict_json(request_raw)
    require(type(request) is dict and set(request)=={'schema','case_id','run_name','source_context','input_descriptors','models_allowed','expected_allowed'},'CLOSED_ROOT_REQUEST')
    require(request['schema']=='phase511-root-bound-input-request/1' and request['case_id']==CASE and request['run_name']==RUN,'FIXED_NEW_CASE_RUN')
    require(all(type(request[k]) is int and request[k]==0 for k in ('models_allowed','expected_allowed')),'REQUEST_STRICT_INT0')
    cp=request['source_context']
    require(type(cp) is dict and set(cp)=={'path','size','sha256'},'EXPLICIT_CONTEXT_PIN')
    canonical(cp['path'])
    require(type(cp['size']) is int and type(cp['sha256']) is str and type(context_raw) is bytes and len(context_raw)==cp['size']
            and hashlib.sha256(context_raw).hexdigest()==cp['sha256'],'ROOT_BOUND_CONTEXT_BYTES')
    pins=request['input_descriptors']
    require(type(pins) is dict and set(pins)==set(LAWFUL),'EXACT12_ROOT_INPUT_PINS_REQUIRED')
    parents=set()
    for name,p in pins.items():
        require(type(p) is dict and set(p)=={'path','size','sha256'},'INPUT_PIN_SHAPE')
        require(type(p['size']) is int and 0<p['size']<=4194304 and type(p['sha256']) is str and re.fullmatch('[0-9a-f]{64}',p['sha256']) is not None,'INPUT_PIN_TYPES')
        path=canonical(p['path']);require(path.name==name,'LAWFUL_LEAF_NAME');parents.add(str(path.parent))
    require(len(parents)==1,'ONE_EXPLICIT_LAWFUL_INPUT_ROOT')
    context=strict_json(context_raw)
    require(type(context) is dict and set(context)=={'schema','case_id','profile','runtime_schema','schema_module','fixed_source_bindings','source_pins','source_rules','prepared_gate'},'CLOSED_SOURCE_CONTEXT')
    require(context['schema']=='phase511-fixed-source-context/1' and context['case_id']==CASE and context['profile']==PROFILE
            and context['runtime_schema']==RUNTIME_SCHEMA and same(context['schema_module'],SCHEMA_PIN),'EXACT511_SOURCE_CONTEXT')
    require(same(context['fixed_source_bindings'],FIXED_SOURCE_BINDINGS) and same(context['source_rules'],SOURCE_RULES),'NO_CALLER_PROOF_FLAGS_OR_SOURCE_DRIFT')
    require(context['prepared_gate']=='EXTERNAL_SAME_INSTANCE_BUSINESS_PREPARE_GATE_REQUIRED_BEFORE_ACTIVATION','PREPARED_GATE_NOT_CERTIFIED_BY_BRIDGE')
    require(type(context['source_pins']) is list and context['source_pins'],'EXPLICIT_SOURCE_PINS')
    allowed={p['path'] for p in FIXED_SOURCE_BINDINGS.values()} | {'tests/phase511_input_bridge.py','data/phase511-input-bridge-source/branch-source-rule.json','data/phase511-input-bridge-source/abi.json'}
    require(len(context['source_pins'])==len(allowed) and {p['path'] for p in context['source_pins']}==allowed,'CLOSED_SOURCE_PIN_PATHS_NO_EXPECTED')
    actual={p['path']:p for p in context['source_pins']}
    for p in FIXED_SOURCE_BINDINGS.values():require(same(actual[p['path']],p),'FIXED_SOURCE_PIN_IDENTITY')
    return request,context


def verify_raw_inputs(raw12,request):
    require(type(raw12) is dict and set(raw12)==set(LAWFUL),'EXACT12_LAWFUL_BYTES')
    for name,p in request['input_descriptors'].items():
        require(type(raw12[name]) is bytes and len(raw12[name])==p['size']
                and hashlib.sha256(raw12[name]).hexdigest()==p['sha256'],'ROOT_PINNED_INPUT_'+name)
    return deepcopy(request['input_descriptors'])


def load_schema(schema_raw):
    require(type(schema_raw) is bytes and len(schema_raw)==SCHEMA_PIN['size'] and hashlib.sha256(schema_raw).hexdigest()==SCHEMA_PIN['sha256'],'EXACT_PINNED502_SCHEMA_BYTES')
    name='_phase511_exact502_schema';module=types.ModuleType(name);module.__file__=SCHEMA_PIN['path']
    require(name not in sys.modules,'NO_CACHED_SCHEMA_SHORTCUT')
    sys.modules[name]=module
    try:
        exec(compile(schema_raw,module.__file__,'exec'),module.__dict__)
        require(module.VERSION=='7-whelp-family-A-502' and module.PROFILE=='observer7-whelp-family-A-native-tape/1'
                and len(module.FIXED_ROLES)==29 and module.DESCRIPTOR_IDS==frozenset({1,11,22,23,64,164,197,199,201}),'EXACT_ZERO_KING_SCHEMA_DOMAIN')
        return module
    finally:
        del sys.modules[name]


def decode_lawful12(raw12,request,schema):
    pins=verify_raw_inputs(raw12,request)
    decoded=schema._transport_only_decode({name:raw12[name] for name in schema.INPUT_FILES})
    for name in schema.CHANNEL_FILES:
        for row in decoded[name]:schema.validate_record(row)
    binding=schema.validate_binding_carrier(raw12['king-slot-bindings.json'],schema.BINDING_FIXED_PLAN)
    aliases=schema.join_binding_provenance(decoded,binding,schema.BINDING_SOURCE_CONTRACT)
    return decoded,aliases,{'input_descriptors':pins,'binding_join':aliases,'scope':'ROOT_PINNED_BYTES_TRANSPORT_TYPED_RELATION_ONLY','full_FX_UI_gate_called':False}


def derive_branch_witness(decoded,aliases):
    selected=[];opponent=[]
    for line,row in enumerate(decoded['observer7-primitives.jsonl'],1):
        if not row['site'].startswith('Items/Item.gd::adjustCooldown:'):continue
        label=row['payload']['label'];require(label.startswith('cooldown:'),'COOLDOWN_SOURCE_LABEL')
        role=label[len('cooldown:'):]
        require(role in aliases['role_to_native'] and re.fullmatch('[PO]:[0-9]+',role) is not None,'COOLDOWN_SELECTED_ALIAS')
        site=row['site']
        require(site in ('Items/Item.gd::adjustCooldown:belowMasterOpponent','Items/Item.gd::adjustCooldown:other'),'EXACT_TWO_SOURCE_BRANCHES')
        if role.startswith('P:'):require(site.endswith(':other'),'PLAYER_COOLDOWN_BRANCH')
        witness={'file':'observer7-primitives.jsonl','line':line,'sequence':row['sequence'],'role':role,
                 'native_owner':aliases['role_to_native'][role],'site':site,'startup':same(row['stamp']['combat_time'],{'type':'float','binary64_be':ZERO_BITS})}
        selected.append(witness)
        if role.startswith('O:'):opponent.append(witness)
    require(opponent and any(row['startup'] for row in opponent),'NEW_OPPONENT_STARTUP_BRANCH_REQUIRED')
    sites={row['site'] for row in opponent};require(len(sites)==1,'NEW_PREDICATE_BRANCH_NOT_STABLE')
    value=next(iter(sites)).endswith(':belowMasterOpponent')
    return {'schema':'phase511-new-input-predicate-witness/1','field':'fixture.below_master','type':'BOOL','value':value,
            'witnesses':selected,'source_rule':deepcopy(SOURCE_RULES['cooldown_predicate']),
            'limits':'Execution-site classifier plus unique frozen literal call mapping; not direct rank/UI/league serialization. No random return or bound comparison chooses the predicate.'}
'''

PREPARED = '''def validate_auxiliary_joins(decoded,aliases,schema):
    inputs=decoded['observer7-input.jsonl']
    act=one(inputs,'Core/Game.gd::activateItems','checkpoint')
    nodes={row['role']:row['node'] for row in act['payload']['nodes']}
    facts=decoded['king-input-facts.json'];rng=decoded['king-rng-checkpoint.json']
    schema._single_king_rng_checkpoint(rng,inputs)
    require(rng['game_id']==aliases['role_to_native']['game'] and rng['util']['native_id']==aliases['role_to_native']['util'],'RNG_ACTUAL_GAME_UTIL_ALIAS')
    require(same(facts['root_viewport'],nodes['root_viewport']) and facts['delayed_activation']['target_id']==rng['game_id'],'FACTS_ROOT_DELAYED_OWNER_JOIN')
    for item in facts['items']:
        require(same(item['node'],nodes['item:'+item['instance']]),'FACTS_ACTUAL_ITEM_NODE_JOIN')
        for socket in item['sockets']:
            require(socket['node']['native_id'] not in aliases['native_to_role'],'SOCKET_NOT_SELECTED_NODE_ALIAS')
    return {'initial_rng':'ACTUAL_SOURCE_CHECKPOINT_ONLY_NOT_SEED_REPLAY','facts_root_and_item_aliases':'JOINED_TO_ACTUAL_ACTIVATION_CUT'}


def project_prepared_witnesses(decoded,aliases,receipt):
    observations=receipt['prepare_observations']['pre_activate']
    result={'schema':'phase511-lawful-prepared-witness/1','stage':'pre_activate','status':'OBSERVED_INPUT_NOT_MODEL_EQUIVALENCE',
            'gate':'EXTERNAL_SAME_INSTANCE_BUSINESS_PREPARE_GATE_REQUIRED_BEFORE_ACTIVATION','items':{},
            'comparison_scope':'Only actual business-consumed target/cache order via B1 mapping; full color/current dictionaries are provenance, not Python UI state.'}
    for role,observation in observations.items():
        cached,current=observation['cachedAffectedItems'],observation['currentAffectedItems']
        arrays=[];relations=[]
        for color in cached['entries']:
            arrays.append({'color':deepcopy(color['key']),'ordered_roles':[r['role'] for r in color['value']['values']],
                           'ordered_native_ids':[r['native_id'] for r in color['value']['values']]})
        for color in current['entries']:
            relations.append({'color':deepcopy(color['key']),'ordered_members':[{'role':r['key']['role'],'native_id':r['key']['native_id'],'value':deepcopy(r['value'])} for r in color['value']['entries']]})
        value=deepcopy(observation);value['native_id']=aliases['role_to_native'][role]
        value['ordered_cache_aliases']=arrays;value['ordered_current_aliases']=relations
        result['items'][role]=value
    require(len(result['items'])==29 and all(r in result['items'] for r in ('P:9','P:10','P:14')),'PREPARED29_SPECIAL_IDENTITIES')
    require('goobert_state' in result['items']['P:9'] and 'stackTypes' in result['items']['P:14'],'PREPARED_BASIC_SAPPHIRE_TYPED_WITNESSES')
    return result


def validate_initial_consumer_coverage(bundle,origins,receipt,witness):
    require(set(bundle)=={'schema','fixture','runtime','draws','synthetic_seed'} and bundle['schema']=='native-v8-input-only/1' and bundle['synthetic_seed'] is None,'INPUT_ONLY_ENVELOPE')
    data=bundle['runtime'];require(set(data)==set(RUNTIME_KEYS) and data['schema']==RUNTIME_SCHEMA and data['profile_id']==PROFILE,'RUNTIME14_ABI')
    require(len(data['timer_initial'])==32 and len(data['processing_nodes'])==67 and len(data['nodes'])==66 and len(data['initial_items'])==29,'RAW32_67_66_29')
    require(receipt['counts']['SOURCE_DERIVED']==72 and len(witness['items'])==29,'ALL64_PLUS8_AND_PREPARED_WITNESS')
    for field in bundle:require('bundle.'+field in origins,'BUNDLE_ORIGIN_'+field)
    for field in data:require('runtime.'+field in origins,'RUNTIME_ORIGIN_'+field)
    for role,fields in data['timer_initial'].items():
        for field in fields:require('timer_initial.'+role+'.'+field in origins,'TIMER_FIELD_ORIGIN')
    for side,fields in data['initial_characters'].items():
        for field in fields:require('initial_characters.'+side+'.'+field in origins,'CHARACTER_FIELD_ORIGIN')
    return {'status':STATUS,'runtime_validated':False,'model_release':False,'future_model_blockers':list(DEFERRED)}


def project_decoded(decoded,aliases,receipt,branch,schema):
    fixture=project_fixture(decoded,branch,schema)
    runtime,origins,activation=project_runtime(decoded,aliases,value_index(receipt),schema)
    draws,sequences=project_primitives(decoded,activation)
    witness=project_prepared_witnesses(decoded,aliases,receipt)
    bundle={'schema':'native-v8-input-only/1','fixture':fixture,'runtime':runtime,'draws':draws,'synthetic_seed':None}
    origins.update({'bundle.schema':{'source':'511 ABI'},'bundle.fixture':{'files':['fixture.json','player_fixture.json','king-slot-bindings.json'],'predicate':'actual fixed geometry/resources plus new executed branch witness'},
        'bundle.runtime':{'source':'511 runtime14 ABI'},'bundle.draws':{'file':'observer7-primitives.jsonl','sequences':sequences,'predicate':'full actual selected physical stream including ended-tail'},
        'bundle.synthetic_seed':{'source':'511 ABI NULL; no seed manufacture'}})
    coverage=validate_initial_consumer_coverage(bundle,origins,receipt,witness)
    proof={'schema':'phase511-input-only-projection-proof/1','status':STATUS,'field_origins':origins,
           'primitive_original_sequences':sequences,'branch_witness':branch,'coverage':coverage,
           'timer_origin':'Actual new G02/Character premises; not publiczero or all fresh configured',
           'prepared_equivalence':'External same-instance prepare_only business gate required; not proven by bridge',
           'model_release':False}
    return bundle,proof,witness


def project_from_bytes(raw12,request_raw,request_pin,context_raw,schema_raw):
    """Explicit Root-bound pure bytes interface; no filesystem I/O or import-time schema load."""
    request,context=authenticate_request(request_raw,request_pin,context_raw)
    verify_raw_inputs(raw12,request)  # identity before any data/schema decode
    schema=load_schema(schema_raw)
    decoded,aliases,validation=decode_lawful12(raw12,request,schema)
    receipt=build_initial_receipt(decoded,aliases,schema)
    auxiliary=validate_auxiliary_joins(decoded,aliases,schema)
    branch=derive_branch_witness(decoded,aliases)
    bundle,proof,witness=project_decoded(decoded,aliases,receipt,branch,schema)
    proof['fixed_input_validation']=validation;proof['auxiliary_source_joins']=auxiliary;proof['source_context']=deepcopy(request['source_context'])
    proof['initial_receipt']={'file':'initial-receipt.json','counts':deepcopy(receipt['counts'])}
    return bundle,proof,receipt,witness


def verify_source_context(context,io):
    # Source files only. This is called by the explicit future filesystem build, not by import.
    seen=set()
    for p in context['source_pins']:
        path=str(canonical(p['path']));require(path not in seen,'SOURCE_PIN_DUPLICATE');seen.add(path);read_pinned(p,io)
    required={str(canonical(p['path'])) for p in FIXED_SOURCE_BINDINGS.values()}
    require(required<=seen and str(Path(__file__).absolute()) in seen,'FIXED_SOURCE_AND_PROJECTOR_PINS_REQUIRED')
    return {'status':STATUS,'fixed_source_bindings':deepcopy(FIXED_SOURCE_BINDINGS),'source_rules':deepcopy(SOURCE_RULES),'model_release':False}


def build_from_files(output_new,request_pin):
    require(request_pin is not None,'NO_DEFAULT_REQUEST_OR_NATIVE_PINS')
    source_io=[];input_io=[];owned=[]
    request_raw=read_pinned(request_pin,source_io);request_head=strict_json(request_raw)
    require(type(request_head) is dict and request_head.get('schema')=='phase511-root-bound-input-request/1','EXPLICIT_ROOT_REQUEST_SCHEMA')
    context_raw=read_pinned(request_head['source_context'],source_io)
    request,context=authenticate_request(request_raw,request_pin,context_raw)
    authority=verify_source_context(context,source_io)
    schema_raw=read_pinned(SCHEMA_PIN,source_io)
    output=canonical(output_new);require(output.parent==REPO/'data' and output.name.startswith('phase511-'),'OUTPUT_DOMAIN')
    physical(output.parent,False);require(not os.path.lexists(output),'OUTPUT_EXISTS');output.mkdir(mode=0o700)
    try:
        raw12={name:read_pinned(p,input_io) for name,p in request['input_descriptors'].items()}
        bundle,proof,receipt,witness=project_from_bytes(raw12,request_raw,request_pin,context_raw,schema_raw)
        proof['source_authority']=authority
        source_after=[];input_after=[]
        for p in source_io:read_pinned(p,source_after)
        for p in input_io:read_pinned(p,input_after)
        require(same(source_io,source_after) and same(input_io,input_after),'SOURCE_INPUT_READBACK')
        for name,value in (('input-bundle.json',bundle),('initial-receipt.json',receipt),('input-proof.json',proof),('prepared-witness.json',witness),
                           ('inputs-before-interpretation.json',{'source':source_io,'input':input_io,'request':request_pin}),
                           ('input-readback.json',{'source_before':source_io,'source_after':source_after,'input_before':input_io,'input_after':input_after,'whole_files_read_and_hashed':True,'lawful_syntax_decoded':12,'Expected_reads':0})):
            owned.append(save_new(output/name,value))
        owned.append(save_new(output/'input-seal.json',{'schema':'phase511-input-only-seal/1','status':STATUS,'files':deepcopy(owned),'runtime_validated':False,'model_release':False,'external_same_instance_prepare_gate':'REQUIRED_NOT_EXECUTED','request':request_pin}))
        save_new(output/'owned-files.json',{'schema':'phase511-output-owner/1','files':owned,'independent_input_acceptance':'PENDING','status':STATUS})
    except Exception as error:
        if not os.path.lexists(output/'first-error.json'):save_new(output/'first-error.json',{'error':type(error).__name__,'reason':str(error)[:2000],'source_reads':source_io,'input_reads':input_io,'preserved_outputs':owned,'automatic_retry':False,'model_release':False})
        raise
    return {'status':STATUS,'input_bundle_created':True,'runtime_validated':False,'model_runs':0,'output':str(output)}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request',required=True);parser.add_argument('--request-size',type=int,required=True);parser.add_argument('--request-sha256',required=True)
    parser.add_argument('--output-new',required=True);args=parser.parse_args(argv)
    print(json.dumps(build_from_files(args.output_new,{'path':args.request,'size':args.request_size,'sha256':args.request_sha256}),sort_keys=True))
'''


def bridge_source(fixed,rules):
    path=ROOT/'tests/phase470_joint_input_bridge.py';old=path.read_text();f=functions(old)
    exact=['Rejected','require','same','strict_json','canonical','physical','read_pinned','save_new','fingerprint','source_value','typed_scalar','one','model_role','project_primitives']
    header='''"""Case029 lawful INPUT-only bridge. No schema load/default request at import."""
import argparse
from copy import deepcopy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import struct
import sys
import types
from phase511_initial_receipt import build_initial_receipt,value_index

REPO=Path(__file__).resolve().parents[1]
STATUS='INPUT_ONLY_NOT_RUNTIME_VALIDATED'
CASE='NATIVE-029-WHELP-FAMILY-A'
RUN='original029-whelp-family-A-single-001'
PROFILE='pure-combat-whelp-family-A-captured/1'
RUNTIME_SCHEMA='native-v8-pure-combat-runtime-input/whelp-family-1'
RUNTIME_KEYS=('schema','mode','profile_id','checkpoint','environment','nodes','timer_initial','initial_items','initial_characters','prepare_order','activate_order','terminal_profile','frame_clock','processing_nodes')
STACK_NAMES={100:'Block',101:'Lucky',102:'Regeneration',103:'Vampirism',104:'Spikes',105:'Mana',106:'Empower',107:'Heat',108:'Poison',109:'Blind',110:'Cold'}
ZERO_BITS='0000000000000000'
DEFERRED=('actual same-instance business prepare equivalence','ordinary callbacks/transform/selected RNG noninterference','candidate interface and actual INPUT acceptance','one-model output/strict8 mapping')
LAWFUL=('fixture.json','player_fixture.json','observer7-input.jsonl','observer7-lineage.jsonl','observer7-metadata.jsonl','observer7-primitives.jsonl','king-clock-checkpoint.json','king-clock-passes.jsonl','king-input-facts.json','king-ui-authority.jsonl','king-rng-checkpoint.json','king-slot-bindings.json')
DEFAULT_REQUEST=None
'''
    header+='SCHEMA_PIN = '+repr(fixed['schema_module'])+'\nFIXED_SOURCE_BINDINGS = '+repr(fixed)+'\nSOURCE_RULES = '+repr(rules)+'\n\n'
    order=f['project_order'].replace('def project_order(entry, aliases):','def project_order(entry,aliases,schema):').replace('native_schema','schema').replace('== 26','== 29').replace('GAME_ORDER26','GAME_ORDER29')
    fixture=f['project_fixture'].replace('def project_fixture(decoded):','def project_fixture(decoded,branch,schema):').replace('native_schema','schema')
    fixture=replace(fixture,'    return fixture',"    require(type(branch.get('value')) is bool,'ACTUAL_BRANCH_BOOL')\n    fixture['below_master']=branch['value']\n    return fixture")
    runtime=f['project_runtime'].replace('def project_runtime(decoded, aliases, index):','def project_runtime(decoded,aliases,index,schema):').replace('native_schema','schema')
    runtime=runtime.replace('project_order(pe, aliases), project_order(ae, aliases)','project_order(pe,aliases,schema), project_order(ae,aliases,schema)')
    runtime=replace(runtime,'set(raw_nodes) - EXCLUDED_TIMERS','set(raw_nodes)')
    runtime=replace(runtime,"        if raw_role in EXCLUDED_TIMERS:\n            continue\n",'')
    runtime=runtime.replace('len(timers) == 33 and len(processing) == 65 and len(nodes) == 64','len(timers) == 32 and len(processing) == 67 and len(nodes) == 66')
    a=runtime.index("    for side, child in (('P', 7), ('O', 5)):");b=runtime.index('    characters = {}',a);runtime=runtime[:a]+runtime[b:]
    runtime=runtime.replace('INITIAL_ITEMS_COMPLETE26','INITIAL_ITEMS_COMPLETE29').replace('source-two-physics-idle-pre-internal/1','first-actual-idle-after-at-least-two-future-physics/1')
    runtime=replace(runtime,"        characters[side] = values","        require(type(values['buffProtectStacks']) is int and values['buffProtectStacks']==0,'SUPPORTED_OBSERVED_CHARACTER_PROTECTION_INITIAL')\n        characters[side] = values")
    runtime=runtime.replace('data/phase470-joint-input-source/abi.json','data/phase511-input-bridge-source/abi.json').replace('two UI Timer exclusions','all raw32 Timer records; no exclusions').replace('actual26 native/role relation','actual29 native/role relation')
    # This validator is data-only and rejects ambiguous ancestor aliases before emission.
    hook='    characters = {}'
    checks='''    prefixes={};path_positions={};positions=set();paths=set()
    for node in processing:
        names=node['path'].split('/')[1:];pos=node['positions']
        require(len(pos)==len(names) and pos and pos[0]==-1 and node['path'] not in paths and tuple(pos) not in positions,'PROCESSING_PATH_POSITION_UNIQUE')
        for end in range(1,len(names)+1):
            pp=tuple(pos[:end]);np=tuple(names[:end])
            require((pp not in prefixes or prefixes[pp]==np) and (np not in path_positions or path_positions[np]==pp),'PROCESSING_BIDIRECTIONAL_PREFIX')
            prefixes[pp]=np;path_positions[np]=pp
        paths.add(node['path']);positions.add(tuple(pos))
'''
    runtime=replace(runtime,hook,checks+hook)
    text=header+'\n\n'.join(f[name] for name in exact)+'\n\n'+REQUEST+'\n\n'+order+'\n\n'+fixture+'\n\n'+runtime+'\n\n'+PREPARED+"\n\nif __name__=='__main__':main()\n"
    return path,old,text,exact


def main():
    require(not OUT.exists() and not INITIAL.exists() and not BRIDGE.exists(),'unique511 Source outputs')
    OUT.mkdir();save(OUT/'generation-started.json',{'source_only':True,'producer':pin(Path(__file__)),'spec':pin(SPEC),'Native_records_read':0})
    try:
        ip,initial_old,initial=initial_source();compile(initial,str(INITIAL),'exec',dont_inherit=True)
        INITIAL.write_text(initial)
        source_refs={
            'schema_module':ROOT/'data/phase502-whelp-observer-source-v4/schema/phase502_whelp_observer_schema.py',
            'observer_tuple':ROOT/'data/phase502-whelp-observer-source-v4/source-tuple.json',
            'observer_owner':ROOT/'data/phase502-whelp-observer-source-v4/source-owner.json',
            'observer_acceptance':ROOT/'data/phase503-independent-final-acceptance/review.json',
            'candidate_freeze':ROOT/'data/phase505-captured-nonking-source-v3/candidate-source-freeze.json',
            'candidate_interface_acceptance':ROOT/'data/phase506-independent-final-acceptance/review.json',
            'native_timer_source_rule':ROOT/'data/phase438-native-timer-source-review/source-ledger.json',
            'character_source_rule':ROOT/'data/phase438-root-character8-acceptance/acceptance.json',
            'timer_rule_acceptance':ROOT/'data/phase439-root-timer64-acceptance/acceptance.json',
            'receipt_source':INITIAL}
        fixed={k:pin(p) for k,p in source_refs.items()}
        branch_rule={'schema':'phase511-fixed-source-cooldown-predicate-closure/1','case_id':'NATIVE-029-WHELP-FAMILY-A',
            'predicate':'Game.isBelowLeague(Game.Leagues.Master) or Game.curMode == Game.Mode.Lobbies',
            'source_tuple':fixed['observer_tuple'],'two_fixed_calls':'Original Item.adjustCooldown if(O && predicate) calls(0.975,1.05), else(0.95,1.05);502 inherits359 Item wrapper that forwards same args/return and names site by low literal.',
            'same_consumer':'Original Character.prepare applies O accuracy/crit bias -0.2/+0.2 under the same predicate.',
            'local_closure':'Fixed collector startFreshRun(Unranked) -> prepareItems -> Character.prepare -> all Item.preCombatStart adjustCooldown. Nine-item family effects/ForestFriend/Goobert/Weapon shared callbacks add no Game mode/league writer; selected source-domain controls exclude external state setters/reentry. New complete O cooldown site stream must agree and include startup witness.',
            'new_family_Source_reviews':[pin(ROOT/'data/phase488-independent-design-review/review.json'),pin(ROOT/'data/phase492-amethyst-whelp-design/owned-files.json'),pin(ROOT/'data/phase496-independent-design-review/review.json')],
            'source_predicate_reason_ref':pin(ROOT/'data/phase475-cooldown-branch-input-evidence/source-evidence.json'),
            'limits':'No old branch rows/value/rating or Source498 flag carried. Actual selected site witness is required; numeric return/bounds do not infer branch. This is bounded ordinary Source-domain applicability, not arbitrary runtime hooks.'}
        save(OUT/'branch-source-rule.json',branch_rule)
        rules={'cooldown_predicate':dict(descriptor=pin(OUT/'branch-source-rule.json'),predicate=branch_rule['predicate'],basis='NEW_SITE_WITNESS_PLUS_FIXED_SOURCE_CLOSURE'),
               'initial':{'domain':'accepted G02 and Character default/pre-ready-call closure applied to actual new32/2cut objects','native_rule':fixed['native_timer_source_rule'],'character_rule':fixed['character_source_rule'],'timer_acceptance':fixed['timer_rule_acceptance'],
                          'limits':'Historical domain/migration limits retained. No old row/native-ID/private value or all-fresh assumption. Actual birth/no-start ledger only for2invu, no fabricated ledger for30others.'}}
        bp,bridge_old,bridge,exact=bridge_source(fixed,rules);compile(bridge,str(BRIDGE),'exec',dont_inherit=True);BRIDGE.write_text(bridge)
        abi={'schema':'phase511-input-ABI/1','status':'INPUT_ONLY_NOT_RUNTIME_VALIDATED','profile':'pure-combat-whelp-family-A-captured/1','runtime_schema':'native-v8-pure-combat-runtime-input/whelp-family-1',
             'runtime_keys':['schema','mode','profile_id','checkpoint','environment','nodes','timer_initial','initial_items','initial_characters','prepare_order','activate_order','terminal_profile','frame_clock','processing_nodes'],
             'raw_timers':32,'business_timers':26,'inactive_timers':6,'processing_nodes':67,'configs':66,'items':29,'derived_private_and_character':72,
             'prepared_witness':'Source-only full actual cache provenance; external same-instance business prepare gate required before activation','model_release':False}
        save(OUT/'abi.json',abi)
        source_pins=list(fixed.values())+[pin(INITIAL),pin(BRIDGE),pin(OUT/'branch-source-rule.json'),pin(OUT/'abi.json')]
        source_pins=list({p['path']:p for p in source_pins}.values())
        context={'schema':'phase511-fixed-source-context/1','case_id':'NATIVE-029-WHELP-FAMILY-A','profile':abi['profile'],'runtime_schema':abi['runtime_schema'],
                 'schema_module':fixed['schema_module'],'fixed_source_bindings':fixed,'source_pins':source_pins,'source_rules':rules,
                 'prepared_gate':'EXTERNAL_SAME_INSTANCE_BUSINESS_PREPARE_GATE_REQUIRED_BEFORE_ACTIVATION'}
        save(OUT/'source-context.json',context)
        save(OUT/'future-root-request-template.json',{'schema':'phase511-root-bound-input-request/1','case_id':'NATIVE-029-WHELP-FAMILY-A','run_name':'original029-whelp-family-A-single-001',
            'source_context':pin(OUT/'source-context.json'),'input_descriptors':None,'models_allowed':0,'expected_allowed':0})
        oldif,newif=functions(initial_old),functions(initial);oldbf,newbf=functions(bridge_old),functions(bridge)
        require(all(oldbf[name]==newbf[name] for name in exact),'exact typed/IO/Tape helper bodies')
        initial_exact=sorted(name for name in oldif if name in newif and oldif[name]==newif[name])
        require(all(name in initial_exact for name in ('require','same','ref','integer','validate_cache_alias','value_index')),'shape-neutral receipt core exact')
        require('INPUT_PINS' not in bridge and 'native_schema = load_schema()' not in bridge,'no old pins/import-time schema')
        require('KING_TIMER' not in initial and 'EXCLUDED_TIMERS' not in bridge,'no King branch/presentation exclusion')
        for name,old,new in [('initial',initial_old,initial),('bridge',bridge_old,bridge)]:
            (OUT/(name+'-vs470.patch')).write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=str((ip if name=='initial' else bp).relative_to(ROOT)),tofile=str((INITIAL if name=='initial' else BRIDGE).relative_to(ROOT)))))
        save(OUT/'conservation.json',{'schema':'phase511-source-conservation/1','exact470_bridge_helpers':exact,'exact470_initial_helpers':initial_exact,'Tape_conversion_body_exact':True,'I_O_bodies_exact':True,
            'old_modules_untouched':[pin(ip),pin(bp)],'schema_candidate_untouched':[fixed['schema_module'],fixed['candidate_freeze']],
            'new_modules':[pin(INITIAL),pin(BRIDGE)],'actual_projection_calls':0,'schema_imports':0})
        save(OUT/'api-contract.json',{'schema':'phase511-Source-API/1','project_from_bytes':'(raw12,request_raw,request_pin,context_raw,schema_raw) -> bundle,proof,initial_receipt,prepared_witness',
            'build_from_files':'(output_new, explicit future Root-selected request_pin); DEFAULT_REQUEST=None; no implicit pins',
            'authentication_boundary':'Root selects exact request descriptor out of band; hashes/typed rules are not self-created Native provenance or a generic authorization boolean.',
            'projection_status':'INPUT_ONLY_NOT_RUNTIME_VALIDATED','actual_input_pins':None,'actual_cuts_UID_branch_cache':None,'external_same_instance_prepare_gate':'REQUIRED_NOT_EXECUTED',
            'schema_calls_on_import':0,'model_release':False,'Prepared_compare_scope':'business target/cache order via reviewedB1; raw colors/current relation provenance is not UI equivalence'})
        save(OUT/'compile-only.json',{'schema':'phase511-compile-only/1','discarded_new_module_compile_objects':2,'projector_imports':0,'schema_imports':0,'projection_calls':0,'models':0,'Native_capture_reads':0,'baseline_pool_Expected':0})
        refs=[SPEC,Path(__file__),ip,bp,INITIAL,BRIDGE,ROOT/'docs/phase510_case029_input_bridge_preparation_design_spec_v2.md',ROOT/'data/phase510-independent-v2-delta-review/review.json']
        save(OUT/'source-before-and-context.json',{'files':[pin(p) for p in refs]+list(fixed.values()),'Source_only':True,'actual_Native_record_reads':0,'note':'475 source-evidence Source predicate text/metadata only; no old capture opened or old branch result imported.'})
        save(OUT/'source-freeze.json',{'schema':'phase511-source-freeze/1','modules':[pin(INITIAL),pin(BRIDGE)],'source_context':pin(OUT/'source-context.json'),'ABI':pin(OUT/'abi.json'),
             'future_request_template':pin(OUT/'future-root-request-template.json'),'status':'FROZEN_COMPILE_ONLY_PENDING_ROOT_AND512_NO_ACTUAL_INPUT'})
        save(OUT/'first-generation-result.json',{'source_generation_invocations':1,'status':'SOURCE_FROZEN_NO_PROJECTOR_OR_SCHEMA_EXECUTION','new_modules':2,'schema_imports':0,'projection_calls':0,'Native_records_opened':0,'models':0,'pool':0,'Expected':0,'actual_bundle_created':False})
        files=[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()]+[pin(p) for p in refs]
        unique={p['path']:p for p in files}
        save(OUT/'owned-files.json',{'schema':'phase511-source-owner/1','files':list(unique.values()),'no_more_writes':True,'status':'SOURCE_ONLY_PENDING_ROOT_REVIEW_NO_AUTOMATIC512_OR_BUILD'})
        print(json.dumps({'status':'SOURCE_FROZEN_NOT_RUN','owner':pin(OUT/'owned-files.json')},sort_keys=True))
    except Exception as error:
        save(OUT/'first-generation-error.json',{'error_type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc(),'automatic_retry':False,'schema_imports':0,'projection_calls':0,'Native_records_opened':0,'models':0,'pool':0,'Expected':0})
        raise


if __name__=='__main__':main()
