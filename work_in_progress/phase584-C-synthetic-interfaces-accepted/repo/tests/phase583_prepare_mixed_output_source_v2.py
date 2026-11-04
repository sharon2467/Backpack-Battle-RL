"""Phase582 thin C Source assembly; compile/static only, no generated imports."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import stat
import traceback
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/phase582-mixed-launcher-output-source-v2'
SPEC='docs/phase583_mixed_C_helper_hash_repair_spec.md'
LAUNCHER=ROOT/'tests/phase583_mixed_tape_run.py'
ADAPTER=ROOT/'tests/phase583_mixed_business_output.py'
B2=ROOT/'tests/phase583_shared_callback_guard.py'
CASE='NATIVE-030-MIXED-MODIFIERS-A'
PROFILE='pure-combat-mixed-modifiers-A-captured/1'
SCHEMA='native-v8-pure-combat-runtime-input/mixed-modifiers-1'

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
        a,b=funcs(self.before),funcs(self.text);require(set(a)-set(b) <= {'validate_sapphire_gate_origin'},'only obsolete specific provenance function may be replaced')
        actual=sorted(n for n in a if n not in b or a[n]!=b[n]);require(set(actual)==set(changed),'unexpected functions '+repr(actual))
        write(path,self.text.encode())
        report=dict(before=pin(self.path),after=pin(path),changed_functions=actual,conserved_functions=sorted(set(a)-set(actual)),new_functions=sorted(set(b)-set(a)),removed_functions=sorted(set(a)-set(b)),edits=self.edits,inverse='EXACT_COMPLETE_BYTES')
        save(OUT/(path.stem+'-inverse.json'),report)
        write(OUT/(path.stem+'.patch'),''.join(difflib.unified_diff(self.before.splitlines(True),self.text.splitlines(True),fromfile=str(self.path.relative_to(ROOT)),tofile=str(path.relative_to(ROOT)))).encode())
        return report

PREPARED_VIEW='''def prepared_business_view(engine,bundle):
    check(engine.captured_clock_mode and not engine.king_mode and engine.king_states=={} and not engine.source_pure_mode and not engine.source_king_mode,'actual mixed captured instance')
    check(engine.prepared is True and engine.activated is False,'same instance prepared not activated')
    expected={i['instance_id']:i for side in bundle['fixture']['sides'] for i in side['items']}
    check(set(engine.items)==set(expected),'same-instance29 items')
    timers={}
    for role in bundle['runtime']['timer_initial']:
        node=engine.runtime_roles[role]
        timers[role]=dict(private_left_bits=real_bits(node.private_left),wait_time_bits=real_bits(node.wait_time),process_mode=node.process_mode,one_shot=node.one_shot,autostart=node.autostart,paused=node.paused,processing=node.processing,inside_tree=node.inside_tree,ordinary_physics=node.ordinary_physics,internal_physics=node.internal_physics,ordinary_idle=node.ordinary_idle,internal_idle=node.internal_idle)
    items={}
    for identity,item in engine.items.items():
        fields={name:{'type':'float','binary64_be':real_bits(value)} for name,value in (
            ('speedScale',item.speed_scale),('iterationCooldown',item.iteration_cooldown),('triggerTime',item.trigger_time),
            ('doubleActivationChance',item.double_activation_chance),('doubleAttackEffectChance',item.double_attack_effect_chance))}
        if item.item_index==162:fields['speedBonusGiven']={'type':'float','binary64_be':real_bits(item.bowl_speed_bonus_given)}
        elif item.item_index==231:
            count=item.definition['least_buffs'];check(type(count) is int,'actual Wolper definition INT')
            fields['numBuffs']={'type':'int','decimal':str(count)}
            fields['staminaRegenPerBuff']={'type':'float','binary64_be':real_bits(item.wolpertinger_stamina_regen_per_buff)}
            check(item.wolpertinger_buff_listener_registered is True,'actual completed Wolper registration')
        elif item.item_index==385:
            count=item.definition['least_buffs'];check(type(count) is int,'actual Enchanted definition INT')
            fields['buffs']={'type':'int','decimal':str(count)}
        items[identity]=dict(item_index=item.item_index,cache_prepared=item.cache_prepared,typed_fields=fields)
    return dict(profile=engine.runtime_inputs.data['profile_id'],prepared=engine.prepared,activated=engine.activated,king_mode=engine.king_mode,king_states=dict(engine.king_states),tape_position=engine.random.position,tape_audit_length=len(engine.random.audit),passes_consumed=engine.frame_driver.pass_index,
        snapshots=[{k:s[k] for k in ('stage','clock','off_clock')} for s in engine.pure_snapshots],items=items,
        caches={k:[i.instance_id for i in v] for k,v in engine.affected_items_cache.items()},listeners={k:list(v) for k,v in engine.activation_listeners.items()},timers=timers,
        characters={s:dict(invulnerable=c.invulnerable,invulnerabilityItem=engine.invu_origins[s],buffProtectStacks=c.buff_protect_stacks) for s,c in engine.characters.items()},
        character_resources={s:{'baseStaminaRegen':{'type':'float','binary64_be':real_bits(c.base_stamina_regen)},'staminaRegen':{'type':'float','binary64_be':real_bits(c.stamina_regen)}} for s,c in engine.characters.items()})'''

FINAL_VIEW='''def final_business_view(engine,result):
    check(engine.finalized is True and engine.frame_driver.finalized is True,'actual post-run finalized getter stage')
    check(result['final']['runtime']['profile']==PROFILE and result['final']['winner']==engine.winner,'same finalized result/profile')
    items={}
    for identity,index,properties in (('P:13',231,{'numBuffs':'least_buffs'}),('O:4',231,{'numBuffs':'least_buffs'}),('P:19',385,{'buffs':'least_buffs'}),('P:15',32,{'manaCost':'mana_cost','tempDamBonus':'temporary_damage','permDamBonus':'permanent_damage'})):
        item=engine.items[identity];final=result['final']['items'][identity]
        check(type(item.item_index) is int and item.item_index==index and final['item_index']==index and final['instance_id']==item.instance_id==identity,'actual final getter owner/index')
        values={}
        for name,key in properties.items():
            raw=item.definition[key]
            if index==32:
                check(type(raw) in (int,float) and math.isfinite(raw),'Staff actual numeric getter, notBOOL/nonfinite')
                projected=float(raw);kind='REAL'
            else:
                check(type(raw) is int and raw==(3 if index==231 else 1),'actual strictINT final count')
                projected=raw;kind='INT'
            values[name]=dict(getter="definition["+repr(key)+"]",raw_type=type(raw).__name__,raw_value=raw,projected_type=kind,projected_value=projected)
        items[identity]=dict(instance_id=identity,item_index=index,properties=values)
    check(engine.random.position==len(result['random_inputs']) and engine.frame_driver.pass_index==result['captured_terminal']['final']['passes_consumed'],'same final Tape/pass counters')
    return dict(schema='phase582-mixed-final-business-aux/1',case_id=CASE,profile=PROFILE,stage='POST_RUN_SAME_INSTANCE_FINAL_READ',
        finalized=engine.finalized,driver_finalized=engine.frame_driver.finalized,tape_position=engine.random.position,passes_consumed=engine.frame_driver.pass_index,
        projection_rule=PROJECTION_RULE,items=items)'''

VALIDATE_REQUEST='''def validate_request(request):
    expected={'schema','case_id','launcher','candidate_freeze','input_source_owner','input_abi','input_bundle','input_proof','initial_receipt','prepared_witness','input_seal','input_owner','input_acceptance','candidate_acceptance','business_closure','comparison_contract','root_model_authorized'}
    check(type(request) is dict and set(request)==expected and request['schema']=='phase582-root-captured-mixed-model-request/1' and request['case_id']==CASE and request['root_model_authorized'] is True,'closed17 Root model request')
    check(all(type(request[name]) is dict for name in expected-{'schema','case_id','root_model_authorized'}),'UNBOUND_ACTUAL_INPUT_OR_SOURCE_REQUEST')
    check(path_of(request['launcher']['path'])==Path(__file__).resolve(),'executing launcher identity')
    for name,row in FIXED_INPUTS.items():check(request[name]==row,'exact known Source '+name)
    names=expected-{'schema','case_id','root_model_authorized','business_closure'}
    provenance={name:read_descriptor(request[name]) for name in names}
    provenance['candidate_context']=read_descriptor(CANDIDATE_CONTEXT)
    provenance['projection_rule']=read_descriptor(PROJECTION_RULE)
    owner=strict_json(provenance['input_owner']);seal=strict_json(provenance['input_seal'])
    check(seal['status']=='INPUT_ONLY_NOT_RUNTIME_VALIDATED' and seal['runtime_validated'] is False and seal['model_release'] is False,'honest INPUT-only seal')
    for name in ('input_bundle','input_proof','initial_receipt','prepared_witness','input_seal'):owned_contains(owner,request[name])
    check(type(seal['request']) is dict,'actual Root INPUT request association')
    provenance['input_request']=read_descriptor(seal['request']);input_request=strict_json(provenance['input_request'])
    check(input_request['case_id']==CASE and input_request['source_context']==CANDIDATE_CONTEXT and all(type(input_request[k]) is int and input_request[k]==0 for k in ('models_allowed','expected_allowed')),'actual INPUT request/source identity')
    bundle=strict_json(provenance['input_bundle']);proof=strict_json(provenance['input_proof']);initial=strict_json(provenance['initial_receipt']);witness=strict_json(provenance['prepared_witness'])
    check(proof['source_context']==CANDIDATE_CONTEXT,'actual projection context pin')
    context=strict_json(provenance['candidate_context']);check(context['fixed_source_bindings']['candidate_freeze']==request['candidate_freeze'] and context['fixed_source_bindings']['candidate_interface_acceptance']==request['candidate_acceptance'],'same candidate Source in INPUT and model request')
    acceptance=strict_json(provenance['input_acceptance']);check(type(acceptance) is dict and type(acceptance['schema']) is str and type(acceptance['status']) is str and acceptance['status'].startswith('ACCEPTED'),'Root-selected actual independent INPUT acceptance')
    pair=request['business_closure'];check(set(pair)=={'receipt','owner'},'owned actual B2 pair')
    provenance['business_closure']=read_descriptor(pair['receipt']);provenance['business_closure_owner']=read_descriptor(pair['owner'])
    owned_contains(strict_json(provenance['business_closure_owner']),pair['receipt'])
    closure=strict_json(provenance['business_closure']);check(type(closure) is dict and set(closure)=={'schema','extraction_source','guard'} and closure['schema']=='phase582-owned-shared-callback-closure/1' and closure['extraction_source']==CLOSURE_EXTRACTOR,'actual code-bound extraction')
    provenance['closure_extractor']=read_descriptor(CLOSURE_EXTRACTOR)
    guard=closure['guard'];ui=proof['fixed_input_validation']['input_descriptors']['king-ui-authority.jsonl']
    check(guard['schema']=='phase582-actual030-B2-guard/1' and guard['status']=='ACTUAL_FIXED29_WINDOW_MATCHES_SOURCE_GUARD' and guard['raw_descriptor']==ui and guard['input_bundle']==request['input_bundle'] and guard['input_proof']==request['input_proof'] and same(guard['source_basis'],CLOSURE_BASIS),'current actual window/input/Source association')
    check(type(guard['model_noop_slots']) is int and guard['model_noop_slots']==31 and type(guard['native_roles_verified']) is int and guard['native_roles_verified']==29 and guard['full_FX_UI_gate_called'] is False,'conditional31 noops only')
    check(type(bundle) is dict and set(bundle)=={'schema','fixture','runtime','draws','synthetic_seed'} and bundle['schema']=='native-v8-input-only/1' and bundle['synthetic_seed'] is None,'actual INPUT-only envelope')
    data=bundle['runtime'];n=len(data['initial_items']);check(data['schema']==SCHEMA and data['profile_id']==PROFILE and data['mode']=='genuine' and n==29 and len(data['timer_initial'])==32 and len(data['nodes'])==32+5+n and len(data['processing_nodes'])==1+len(data['nodes']),'closed role formula satisfied by actual input')
    check(type(bundle['draws']) is list and type(data['frame_clock']['passes']) is list and bundle['draws'] and data['frame_clock']['passes'],'actual complete nonempty Tape/clock')
    check(initial['counts']['SOURCE_DERIVED']==72 and len(witness['items'])==29 and witness['stage']=='pre_activate','actual72/prepared witness')
    return bundle,strict_json(provenance['candidate_freeze']),proof,initial,witness,provenance'''
def launcher_delta(known,basis,extractor,contract,projection_rule,context_pin):
    d=Delta(ROOT/'tests/phase533_whelp_tape_run.py')
    for name,value in [('CASE',CASE),('PROFILE',PROFILE),('SCHEMA',SCHEMA),('FREEZE',known['candidate_freeze']),('INPUT_SOURCE',known['input_source_owner']),('INPUT_ABI',known['input_abi']),('CONTRACT',contract),('FIXED_INPUTS',dict(known,comparison_contract=contract)),('CLOSURE_EXTRACTOR',extractor),('CLOSURE_BASIS',basis),('INPUT_UI_PIN',None),('INPUT_ACCEPTANCE_OWNER',None)]:d.constant(name,value)
    # Append fixed Source metadata before the existing first helper, without selfhash cycles.
    first=funcs(d.text)['strict_json'];d.replace(first,'CANDIDATE_CONTEXT = '+repr(context_pin)+'\nPROJECTION_RULE = '+repr(projection_rule)+'\n\n\n'+first)
    d.function('validate_request',VALIDATE_REQUEST)
    d.function('prepared_business_view',PREPARED_VIEW)
    old=funcs(d.text)['validate_prepared_business_view'];new=old.replace("item['item_index'] in (22,23,164)","item['item_index'] in (5,22,162,164,231,385)").replace('exact six business cache consumers','exact seven business cache consumers')
    start=new.index("    basic=view['Basic']");end=new.index("    check(set(view['timers'])",start)
    new=new[:start]+'''    check(view['listeners']=={},'no Goobert activation listener in this closed mixed domain')
    for identity,observation in witness['items'].items():
        check(same(view['items'][identity]['typed_fields'],observation['typed_fields']),'actual prepared mixed typed field '+identity)
    for side in ('P','O'):
        actual=witness['characters'][side]
        check(actual['native_id']==nodes['character:'+side]['native_id'],'same-cut Character resource owner')
        check(all(same(view['character_resources'][side][field],actual[field]) for field in ('baseStaminaRegen','staminaRegen')),'actual prepared Character REAL resources')
''' +new[end:]
    ret=new.index("    return dict(schema=");new=new[:ret]+"    return dict(schema='phase582-same-instance-prepared-business-gate/1',status='PASS_PRE_ACTIVATION_SAME_INSTANCE',consumer_cache_roles=sorted(consumers),caches=view['caches'],listeners=view['listeners'],timer_count=32,Tape_position=view['tape_position'],passes_consumed=view['passes_consumed'],scope='Actual business cache and mixed typed fields; full colors/current remain provenance')"
    d.function('validate_prepared_business_view',new)
    old=funcs(d.text)['main'];new=old.replace('data/phase505-captured-nonking-source-v3/staged','data/phase580-captured-mixed-source/staged').replace("output.name.startswith('phase533-')","output.name.startswith('phase582-')").replace('new phase533 output','new phase582 output').replace('fixed505 staged root','fixed580 staged root').replace('phase533-captured029-before/1','phase582-captured030-before/1').replace('phase533-captured029-execution/1','phase582-captured030-execution/1').replace('phase533-output-seal/1','phase582-output-seal/1')
    needle="    watched={str(launcher):{k:request['launcher'][k] for k in ('size','sha256')},str(config_path):config_pin}"
    require(new.count(needle)==1,'watched metadata anchor');new=new.replace(needle,needle+"\n    for row in (CANDIDATE_CONTEXT,PROJECTION_RULE):watched[str(path_of(row['path']))]={k:row[k] for k in ('size','sha256')}\n    input_seal_value=strict_json(provenance['input_seal']);watched[str(path_of(input_seal_value['request']['path']))]={k:input_seal_value['request'][k] for k in ('size','sha256')}")
    new=new.replace("list(FIXED_INPUTS.values())+[INPUT_ACCEPTANCE_OWNER,CLOSURE_EXTRACTOR]", "[request[k] for k in ('candidate_freeze','input_source_owner','input_abi','input_bundle','input_proof','initial_receipt','prepared_witness','input_seal','input_owner','input_acceptance','candidate_acceptance','comparison_contract')]+[CLOSURE_EXTRACTOR]")
    needle="        owned['model-output.json']=write_json(output/'model-output.json',result)"
    require(new.count(needle)==1,'raw output stage');new=new.replace(needle,needle+"\n        aux=final_business_view(engine,result)\n        owned['final-business-aux.json']=write_json(output/'final-business-aux.json',aux)")
    terminal="    print(json.dumps({k:report[k] for k in ('status','calls','elapsed_wall_seconds','tape_position')}));return 0 if status=='ACTUAL_OUTPUT_SEALED_NOT_COMPARED' else 1"
    require(new.count(terminal)==1,'one launcher terminal metadata boundary')
    new=new.replace(terminal,"    _,seal_identity=pin(output/'output-seal.json')\n    write_json(output/'owned-files.json',dict(schema='phase582-model-output-owner/1',files=[dict(path=str(output/name),**identity) for name,identity in owned.items()]+[dict(path=str(output/'output-seal.json'),**seal_identity)],status=status))\n"+terminal)
    d.function('main',new)
    # Add observational final getter before main. Existing helper functions remain unchanged.
    main=funcs(d.text)['main'];d.replace(main,FINAL_VIEW+'\n\n\n'+main)
    return d

SUBTYPE='''def _basic_fields(item,bound):
    identity=item['instance'];index=bound['items'][identity]['item_index'];fields=item['fields']
    wanted = {'speedBonusGiven':float} if index==162 else {'numBuffs':int,'staminaRegenPerBuff':float} if index==231 else {'buffs':int} if index==385 else {'manaCost':float,'tempDamBonus':float,'permDamBonus':float} if index==32 else {}
    for name,kind in wanted.items():
        require(name in fields and type(fields[name]) is kind,'required actual mixed subtype '+identity+':'+name)
        if kind is float:bits(fields[name])
    if index==231:require(fields['numBuffs']==3,'Wolper actual INT3')
    if index==385:require(fields['buffs']==1,'Enchanted actual INT1')'''

BINDINGS='''def bindings(bundle,input_proof,root_binding):
    keys(root_binding,COMPARISON_KEYS,'closed20 external comparison binding')
    require(root_binding['schema']=='phase582-mixed-comparison-binding/1','external binding schema')
    for name in ('input_bundle','input_proof','input_seal','input_owner','candidate_freeze','contract','prepared_witness','prepare_gate','final_aux','model_output','output_seal','output_owner','adapter_source','projection_rule'):
        row=root_binding[name];keys(row,('path','size','sha256'),'actual descriptor shape')
        require(type(row['path']) is str and row['path'] and type(row['size']) is int and row['size']>0 and type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}',row['sha256']) is not None,'unbound/invalid actual descriptor')
    require(root_binding['candidate_freeze']==CANDIDATE_FREEZE and root_binding['contract']==CONTRACT_DESCRIPTOR and root_binding['projection_rule']==PROJECTION_RULE,'known B/contract/cast Source identity')
    require(canonical_sha(bundle)==root_binding['input_canonical_sha256'] and canonical_sha(input_proof)==root_binding['input_proof_canonical_sha256'],'actual Root input/proof canonical identity')
    require(type(bundle) is dict and set(bundle)=={'schema','fixture','runtime','draws','synthetic_seed'} and bundle['schema']=='native-v8-input-only/1' and bundle['synthetic_seed'] is None,'actual INPUT-only envelope')
    data=bundle['runtime'];require(data['schema']=='native-v8-pure-combat-runtime-input/mixed-modifiers-1' and data['profile_id']==PROFILE and data['mode']=='genuine','closed mixed runtime14')
    table={n['role']:deepcopy(n) for n in data['processing_nodes']};require(len(table)==len(data['processing_nodes']),'actual processing role uniqueness')
    native={n['native_id']:name for name,n in table.items()};require(len(native)==len(table),'native identity bijection')
    items={i['instance_id']:i for side in bundle['fixture']['sides'] for i in side['items']}
    require(len(items)==29 and len(data['timer_initial'])==32 and len(data['nodes'])==32+5+len(items) and len(table)==1+len(data['nodes']),'actual rows satisfy closed role formula, not old counts')
    require(all(type(i['item_index']) is int and i['item_index'] in {1,5,11,14,22,32,162,164,231,233,234,385} for i in items.values()),'fixed12 membership')
    for identity,index in {'P:12':162,'P:13':231,'P:14':164,'P:15':32,'P:19':385,'O:4':231}.items():require(items[identity]['item_index']==index,'mixed fixed identity/subtype')
    expected={'root_viewport','game','util','combat_timer','character:P','character:O'}|set(data['timer_initial'])|{'item:'+i for i in items}
    require(set(table)==expected,'complete actual role graph')
    origin=input_proof['field_origins']['runtime.checkpoint'];other=input_proof['field_origins']['runtime.activate_order']
    require(origin['file']==other['file']=='observer7-input.jsonl' and type(origin['sequence']) is int and origin['sequence']>0 and origin['sequence']==other['sequence'] and data['checkpoint']['source_phase']=='Core/Game.gd::activateItems:enter','actual activation cutoff')
    inactive=frozenset('invu:'+s for s in ('P','O'))|frozenset('aux:'+s+':'+n for s in ('P','O') for n in ('battleRageTimer','autoRageTimer'))
    require(len(inactive)==6 and inactive<=set(data['timer_initial']),'six actual inactive Timers retained')
    return dict(nodes=table,native=native,timers=frozenset(data['timer_initial']),items=items,inactive_timers=inactive,activation_after_sequence=origin['sequence'])'''

VALIDATE_AUX='''def validate_final_aux_origin(aux,result,bound,root_binding):
    require(canonical_sha(result)==root_binding['model_output_canonical_sha256'] and canonical_sha(aux)==root_binding['final_aux_canonical_sha256'],'same externally authenticated sealed model/aux canonical bytes')
    keys(aux,('schema','case_id','profile','stage','finalized','driver_finalized','tape_position','passes_consumed','projection_rule','items'),'closed final auxiliary')
    require(aux['schema']=='phase582-mixed-final-business-aux/1' and aux['case_id']=='NATIVE-030-MIXED-MODIFIERS-A' and aux['profile']==PROFILE and aux['stage']=='POST_RUN_SAME_INSTANCE_FINAL_READ' and aux['finalized'] is True and aux['driver_finalized'] is True and aux['projection_rule']==PROJECTION_RULE,'actual final getter stage/Source')
    require(type(aux['tape_position']) is int and type(aux['passes_consumed']) is int and aux['tape_position']==len(result['random_inputs']) and aux['passes_consumed']==result['captured_terminal']['final']['passes_consumed'],'same final counters')
    wanted={'P:13':(231,{'numBuffs':'least_buffs'}),'O:4':(231,{'numBuffs':'least_buffs'}),'P:19':(385,{'buffs':'least_buffs'}),'P:15':(32,{'manaCost':'mana_cost','tempDamBonus':'temporary_damage','permDamBonus':'permanent_damage'})}
    keys(aux['items'],wanted,'exact final getter owners');projected={}
    for identity,(index,properties) in wanted.items():
        item=aux['items'][identity];keys(item,('instance_id','item_index','properties'),'getter item')
        live=result['final']['items'][identity]
        require(item['instance_id']==live['instance_id']==identity and type(item['item_index']) is int and item['item_index']==live['item_index']==bound['items'][identity]['item_index']==index,'same final getter owner/subtype')
        keys(item['properties'],properties,'exact getter properties');values={}
        for name,key in properties.items():
            field=item['properties'][name];keys(field,('getter','raw_type','raw_value','projected_type','projected_value'),'raw getter/projection')
            raw=field['raw_value'];require(field['getter']=="definition["+repr(key)+"]" and field['raw_type']==type(raw).__name__,'raw getter exact origin/type')
            if index==32:
                require(type(raw) in (int,float) and math.isfinite(raw) and field['projected_type']=='REAL' and type(field['projected_value']) is float and bits(field['projected_value'])==bits(float(raw)),'Source float projection distinct from raw type')
            else:
                require(type(raw) is int and raw==(3 if index==231 else 1) and field['projected_type']=='INT' and type(field['projected_value']) is int and field['projected_value']==raw,'strictINT final getter')
            values[name]=field['projected_value']
        projected[identity]=values
    return projected'''

MODEL_FINAL='''def project_model_final(result,bound,sealed_final_aux,root_binding):
    aux=validate_final_aux_origin(sealed_final_aux,result,bound,root_binding)
    final=result['final'];rule=deepcopy(final['native_rule_state']);business=result['captured_terminal']['final']['business']
    require([c['instance'] for c in rule['characters']]==['P','O'] and business['king']=={},'zeroKing same final business state')
    keys(business['invu_origins'],('P','O'),'same-instance invu origins')
    rule['rules']['values']=restore_integer_table(rule['rules']['values']);seen=set()
    for char in rule['characters']:
        side=char['instance'];char['stats']=restore_integer_table(char['stats']);char['fields']['typedDamageFactors']=restore_integer_table(char['fields']['typedDamageFactors'])
        require('invulBubbleVisible' not in char['fields'] and 'invulnerabilityItem' not in char['fields'],'nonKing state projection shape')
        origin=business['invu_origins'][side];require(origin is None or type(origin) is str and origin in bound['items'],'same-instance final invu alias')
        char['fields']['invulnerabilityItem']=origin
        require(first_difference(char['fields']['invulnerable'],business['characters'][side]['invulnerable']) is None,'same final invulnerable')
        for item in char['items']:
            identity=item['instance'];require(identity in bound['items'] and identity not in seen,'model item identity');seen.add(identity)
            for name in ('buffPowers','buffAmplificationChances'):item['fields'][name]=restore_integer_table(item['fields'][name])
            live=final['items'][identity];index=bound['items'][identity]['item_index']
            require(type(live['item_index']) is int and live['item_index']==index and live['instance_id']==identity,'same final dataclass subtype')
            for field,attribute in (('doubleActivationChance','double_activation_chance'),('doubleAttackEffectChance','double_attack_effect_chance')):
                require(first_difference(item['fields'][field],live[attribute]) is None,'same final common chance')
            if index==162:
                require('speedBonusGiven' not in item['fields'],'disjoint Bowl mapping');item['fields']['speedBonusGiven']=live['bowl_speed_bonus_given']
            elif index==231:
                require('staminaRegenPerBuff' not in item['fields'] and 'numBuffs' not in item['fields'],'disjoint Wolper mapping')
                item['fields']['staminaRegenPerBuff']=live['wolpertinger_stamina_regen_per_buff'];item['fields'].update(aux[identity])
            elif index in (385,32):
                require(not set(item['fields'])&set(aux[identity]),'disjoint final getter fields');item['fields'].update(aux[identity])
            _basic_fields(item,bound)
    require(seen==set(bound['items']),'complete final items')
    return dict(native_rule_state=rule,game=deepcopy(final['game']),event_bus=deepcopy(final['event_bus']),timer=dict(combatTime=final['timestamp'],timeAdvance=final['time_advance'],fatigueCounter=final['fatigue_counter']),winner=final['winner'])'''
def adapter_delta(known,contract,projection,comparison_keys,model_hashes):
    d=Delta(ROOT/'tests/phase539_whelp_business_output.py')
    for name,value in [('PROFILE',PROFILE),('NATIVE_PROFILE','observer7-mixed-modifiers-A-native-tape/1'),('CONTRACT_SHA256',contract['sha256']),('CANDIDATE_FREEZE',known['candidate_freeze']),('CONTRACT_DESCRIPTOR',contract),('MODEL_SOURCE_HASHES',model_hashes)]:d.constant(name,value)
    for name in ('FIXTURE_CANONICAL_SHA256','INPUT_BUNDLE','INPUT_PROOF','INPUT_CANONICAL_SHA256','PROOF_CANONICAL_SHA256','PREPARE_GATE','PREPARE_GATE_CANONICAL_SHA256','PROVENANCE_ADDENDUM','PREPARED_WITNESS'):d.constant(name,None)
    first=funcs(d.text)['require'];d.replace(first,'COMPARISON_KEYS = '+repr(tuple(comparison_keys))+'\nPROJECTION_RULE = '+repr(projection)+'\n\n\n'+first)
    d.function('bindings',BINDINGS);d.function('_basic_fields',SUBTYPE);d.function('project_model_final',MODEL_FINAL)
    d.function('validate_sapphire_gate_origin',VALIDATE_AUX)
    old=funcs(d.text)['project_model'];new=old.replace('sealed_prepare_gate','sealed_final_aux').replace('observer7-502-zeroKing-whelp-candidate505','observer7-572-zeroKing-mixed-candidate580');d.function('project_model',new)
    old=funcs(d.text)['compare_decoded'];d.function('compare_decoded',old.replace('sealed_prepare_gate','sealed_final_aux'))
    old=funcs(d.text)['compare_projected'];new=old.replace('fixed029 raw32/29 zeroKing','fixed030 closedraw32/29 zeroKing');d.function('compare_projected',new)
    return d


def b2_delta(basis):
    d=Delta(ROOT/'tests/phase533_shared_callback_guard.py')
    d.constant('SOURCE_BASIS',basis)
    for name in ('INPUT_UI_PIN','INPUT_BUNDLE','INPUT_PROOF','INPUT_CANONICAL_SHA256'):d.constant(name,None)
    old=funcs(d.text)['extract_shared_callback_guard'];new=old.replace('def extract_shared_callback_guard(raw,bundle,pin_value):','def extract_shared_callback_guard(raw,bundle,pin_value,root_binding):')
    needle="    assert type(raw) is bytes and pin_value==INPUT_UI_PIN and len(raw)==pin_value['size'] and hashlib.sha256(raw).hexdigest()==pin_value['sha256']"
    replacement="""    assert type(root_binding) is dict and set(root_binding)=={'schema','input_bundle','input_proof','source_basis','input_bundle_canonical_sha256'} and root_binding['schema']=='phase582-B2-input-binding/1'
    equal(root_binding['source_basis'],SOURCE_BASIS)
    for name in ('input_bundle','input_proof'):
        p=root_binding[name];assert type(p) is dict and set(p)=={'path','size','sha256'} and type(p['path']) is str and type(p['size']) is int and p['size']>0 and type(p['sha256']) is str and len(p['sha256'])==64 and all(ch in '0123456789abcdef' for ch in p['sha256'])
    assert type(pin_value) is dict and set(pin_value)=={'path','size','sha256'} and type(pin_value['size']) is int and pin_value['size']>0 and type(pin_value['sha256']) is str and len(pin_value['sha256'])==64 and all(ch in '0123456789abcdef' for ch in pin_value['sha256']) and type(pin_value['path']) is str
    assert pin_value['path'].replace('\\\\','/').split('/')[-1]=='king-ui-authority.jsonl'
    assert type(raw) is bytes and len(raw)==pin_value['size'] and hashlib.sha256(raw).hexdigest()==pin_value['sha256']"""
    require(new.count(needle)==1,'B2 actual raw pin anchor');new=new.replace(needle,replacement).replace('==INPUT_CANONICAL_SHA256',"==root_binding['input_bundle_canonical_sha256']").replace("o['case']=='WHELP-FAMILY-A-502'","o['case']=='MIXED-MODIFIERS-A-572'").replace("'input_bundle':INPUT_BUNDLE,'input_proof':INPUT_PROOF", "'input_bundle':root_binding['input_bundle'],'input_proof':root_binding['input_proof']").replace('phase533-actual029-B2-guard/1','phase582-actual030-B2-guard/1').replace('Accepted444 shared3callback/readonly-callee rule plus independently reviewed fixed502 nineID dispatch and this actual complete window. Per-clock/write controls and positive-writer branch guards; initialfalse or unchanged code alone is not proof. Squirrel PetORFood and Whelp/Basic queries stay in the admitted read-only domain.','Accepted444 shared3callback/readonly-callee rule plus independently reviewed finite12 Source applicability and this actual complete window. Initialfalse or unchanged code alone is not proof. Squirrel tail RNG remains business; no GUI/global-generator equivalence.')
    d.function('extract_shared_callback_guard',new);return d


def metadata():
    source_context=ROOT/'data/phase582-root-candidate-context-binding/source-context-candidate-bound.json'
    require(pin(source_context)['sha256']=='ac15fe29b5609f504f389d5a642f5e47b8357a01dee10a4c25f204671e4d741b','actual Root newcontext')
    binding=json.loads(read(ROOT/'data/phase582-root-candidate-context-binding/binding.json'))
    # Use Root's exact descriptor path representation, not a guessed normalization.
    context_pin=binding['new_context'];context=json.loads(read(source_context));f=context['fixed_source_bindings']
    known=dict(candidate_freeze=f['candidate_freeze'],candidate_acceptance=f['candidate_interface_acceptance'],input_source_owner=pin(ROOT/'data/phase578-mixed-input-bridge-source/owned-files.json'),input_abi=pin(ROOT/'data/phase578-mixed-input-bridge-source/abi.json'))
    projection=dict(schema='phase582-final-getter-projection-rule/1',case_id=CASE,
        getter_source=pin(ROOT/'data/phase580-captured-mixed-source/staged/native_replay_v8/engine.py'),
        Original_rule=pin(ROOT/'data/phase576-mixed-captured-consumer-design/source-preimages.json'),
        mapping=dict(Wolf_numBuffs="liveitem.definition['least_buffs']; strictINT3",Skill_buffs="liveitem.definition['least_buffs']; strictINT1",Staff="liveitem.definition['mana_cost'/'temporary_damage'/'permanent_damage']; record rawINT/REAL unmodified then explicit float(raw) as Original REAL"),
        raw_type_is_not_projected_type=True,measure='same actual instance after run returns finalized',default_or_expected_fallback=False)
    save(OUT/'final-getter-projection-rule.json',projection)
    oldcontract=json.loads(read(ROOT/'data/phase526-launcher-output-design-v2/comparison-contract.json'))
    sections=oldcontract['sections'];sections['rng']='All actual new INPUT selected kinds/labels/typedargs/returnbits in physical order and exact completeTape; final Character and Item balanced states, no seed equivalence.'
    sections['final']='Full business fields/stats/Buffs/metrics/rules/Game/eventbus/time/winner; ledger/coefficient/chances from same rawfinal; Wolf/Skill counts and Staff REAL fields from same-instance finalaux; no subtype omission.'
    sections['cuts']='Both actual cleanup/final complete raw32 expected public Timers/root/invu-origin-protect/Util/frame clocks and full finite EOF; no invented subtype per-cut sample or later Native private countdown.'
    contract=dict(schema='phase582-fixed030-eight-section-contract/1',case_id=CASE,profile=PROFILE,native_profile='observer7-mixed-modifiers-A-native-tape/1',sections=sections,
        source_ABI=known['input_abi'],candidate_freeze=known['candidate_freeze'],projection_rule=pin(OUT/'final-getter-projection-rule.json'),
        actual_input=None,actual_model=None,actual_expected=None,status='FROZEN_BEFORE_ACTUAL_INPUT_MODEL_EXPECTED',presentation_policy=oldcontract['presentation_policy'],
        selected_callback_cut='actual matching INPUT checkpoint/activate_order origins only',native_private='Initial accepted64+8 actual premises required; later private only model diagnostic',
        source_only_no_general_admission=True)
    save(OUT/'comparison-contract.json',contract)
    basis=ast.literal_eval(assign(read(ROOT/'tests/phase533_shared_callback_guard.py').decode(),'SOURCE_BASIS').value)
    basis['candidate_freeze']=known['candidate_freeze'];basis['observer_tuple']=pin(ROOT/'data/phase572-mixed-observer-source-v2/source-tuple.json')
    for row in basis['callback_slices']:
        if row['wholefile']['path'].endswith('/Items/Item.gd'):row['wholefile']=pin(ROOT/'data/phase572-mixed-observer-source-v2/after-source/Items/Item.gd')
    basis['domain']='Closed12 IDs1/5/11/14/22/32/162/164/231/233/234/385; ordinary Item/Bag/Food/ForestFriend/Wolper/Enchanted/fourWeapon. Independent finite Source applicability review and actual window mandatory; not all84.'
    basis['finite_source_domain_argument']=pin(ROOT/'data/phase562-finite-mixed-source-design/source-pins.json')
    save(OUT/'shared-callback-source-basis.json',basis)
    return known,context_pin,pin(OUT/'comparison-contract.json'),pin(OUT/'final-getter-projection-rule.json'),basis
def main():
    require(not OUT.exists() and not any(p.exists() for p in (LAUNCHER,ADAPTER,B2)),'isolated new C Source outputs')
    OUT.mkdir()
    try:
        expected={'tests/phase533_whelp_tape_run.py':None,'tests/phase539_whelp_business_output.py':'b061e1fe4a0a82d110052a0c3a094d82d5e3286805bc6fd5aa6e4752ad3045de',
          'tests/phase533_shared_callback_guard.py':'3a78d45e720ca60438577e8c737f4845b6625a6b53659165cb0dce2c223ff91b',
          'data/phase580-captured-mixed-source/candidate-source-freeze.json':'e332b765f3bd48c6df63c1ffd047f82654fe0c0465e9886275d287b42160a51b',
          'data/phase581-independent-final-acceptance/review.json':'cc08dad18a8d6d0c263b828e8154a44010ba3cffca134bd0305e75f7016846d8',
          'data/phase582-root-C-Source-release/release.json':'8cb80d8ed9ac691bb13374c39cef03430f147ace356c7840ac30491ad1e31c24'}
        plan=json.loads(read(ROOT/'data/phase582-mixed-launcher-output-plan/source-boundaries-and-neutral-helpers.json'))
        expected['tests/phase533_whelp_tape_run.py']=plan['files']['old_launcher']['sha256']
        for path,h in expected.items():require(pin(ROOT/path)['sha256']==h,'pinned Source drift '+path)
        save(OUT/'source-before.json',dict(schema='phase582-before/1',files=[pin(ROOT/p) for p in expected],Source_generation_attempt=1,candidate_imports=0))
        known,context_pin,contract,projection,basis=metadata()
        interfaces=json.loads(read(ROOT/'data/phase582-mixed-launcher-output-plan/closed-interfaces-and-seals.json'))
        keys20=interfaces['comparison_root_binding']['exact_keys']
        bd=b2_delta(basis);b_report=bd.finish(B2,['extract_shared_callback_guard'])
        model_hashes={}
        freeze=json.loads(read(ROOT/'data/phase580-captured-mixed-source/candidate-source-freeze.json'))
        candidate_before=[]
        for row in freeze['files']:
            path=ROOT/row['path'];require(pin(path)=={k:row[k] for k in ('path','size','sha256')},'candidate15 before exact')
            candidate_before.append(pin(path));rel=Path(row['relative'])
            if rel.parts[0]=='native_replay_v8':model_hashes[rel.name]=row['sha256']
            elif rel.parts[0]=='native_replay_v7':model_hashes['component:'+rel.name]=row['sha256']
        ad=adapter_delta(known,contract,projection,keys20,model_hashes)
        a_report=ad.finish(ADAPTER,['bindings','_basic_fields','project_model_final','project_model','compare_decoded','compare_projected','validate_sapphire_gate_origin'])
        ld=launcher_delta(known,basis,pin(B2),contract,projection,context_pin)
        l_report=ld.finish(LAUNCHER,['validate_request','prepared_business_view','validate_prepared_business_view','main'])
        neutral=plan['adapter20_exact']
        neutral_census=[]
        for row in neutral:
            body=funcs(ad.text)[row['name']]
            require(body==funcs(ad.before)[row['name']],'20helper AST body exact '+row['name'])
            complete=(body+'\n').encode()
            require(len(complete)==row['size'] and digest(complete)==row['sha256'],'20helper complete-line size/SHA exact '+row['name'])
            neutral_census.append(dict(name=row['name'],AST_body_exact=True,complete_line_size=len(complete),complete_line_sha256=digest(complete),original_report=row))
        save(OUT/'neutral-helper-line-ending-census.json',dict(schema='phase583-helper-census/1',functions=neutral_census,AST_body_exact_count=20,original_size_SHA_exact_count=20,helper_executions=0))
        for name in plan['launcher5_exact']:require(funcs(ld.before)[name]==funcs(ld.text)[name],'launcher5 exact '+name)
        after=[pin(ROOT/r['path']) for r in freeze['files']];require(candidate_before==after,'candidate15 after exact')
        model_request={k:None for k in interfaces['model_request']['exact_keys']}
        model_request.update(schema='phase582-root-captured-mixed-model-request/1',case_id=CASE,launcher=pin(LAUNCHER),**known,comparison_contract=contract,root_model_authorized=False)
        save(OUT/'model-request-template.json',model_request)
        compare_template={k:None for k in keys20}
        compare_template.update(schema='phase582-mixed-comparison-binding/1',candidate_freeze=known['candidate_freeze'],contract=contract,adapter_source=pin(ADAPTER),projection_rule=projection)
        save(OUT/'comparison-binding-template.json',compare_template)
        save(OUT/'B2-binding-template.json',dict(schema='phase582-B2-input-binding/1',input_bundle=None,input_proof=None,source_basis=basis,input_bundle_canonical_sha256=None))
        save(OUT/'api-contract.json',dict(schema='phase582-C-api/1',modules=dict(launcher=pin(LAUNCHER),adapter=pin(ADAPTER),B2=pin(B2)),
            source_bound=dict(candidate_freeze=known['candidate_freeze'],candidate_acceptance=known['candidate_acceptance'],input_context=context_pin),
            model_request_keys=interfaces['model_request']['exact_keys'],comparison_binding_keys=keys20,
            B2_binding_keys=['schema','input_bundle','input_proof','source_basis','input_bundle_canonical_sha256'],
            B2='extract_shared_callback_guard(raw,bundle,pin_value,root_binding)',
            prepare='prepared_business_view(engine,bundle); validate_prepared_business_view(view,bundle,witness,initial)',
            final='final_business_view(engine,result)',
            pure_projection='project_model(result,bundle,input_proof,sealed_final_aux,root_binding)',
            pure_compare='compare_decoded(native_outputs,sealed_result,accepted_bundle,input_proof,sealed_final_aux,root_binding)',
            auxiliary_shape=interfaces['final_aux'],
            external_authentication='Independent I/O authenticates physical descriptors and outputseal ownership before pureprojection; pure code checks explicit canonical/data/source/type association, no bool shortcut',
            actual_input=None,actual_B2=None,actual_model=None,status='SOURCE_ONLY_UNBOUND_NOT_RUNTIME_RELEASE',author_calls=0))
        save(OUT/'conservation.json',dict(schema='phase582-C-conservation/1',adapter20helpers_exact=neutral,launcher5helpers_exact=plan['launcher5_exact'],
            changed_functions=dict(adapter=a_report['changed_functions'],launcher=l_report['changed_functions'],B2=b_report['changed_functions']),
            new_functions=dict(adapter=a_report['new_functions'],launcher=l_report['new_functions']),
            removed_functions=dict(adapter=a_report['removed_functions']),candidate15_before=candidate_before,candidate15_after=after,
            inverse='THREE_COMPLETE_PREIMAGE_BYTES',eight_sections=['events','event_references','histories','rng','final','callbacks','timer_api','cuts'],
            B2_canonical_key_addendum=pin(ROOT/'docs/phase582_B2_canonical_binding_implementation_addendum_spec.md'),
            candidate_imports=0,C_helper_calls=0,models=0,Expected=0,Native=0,pool=0))
        compile(read(Path(__file__)),str(Path(__file__)),'exec',dont_inherit=True)
        save(OUT/'compile-only.json',dict(schema='phase582-compile-only/1',discarded_compile_objects=4,new_C_modules=3,producer=1,C_imports=0,helper_SUT=0,model=0,Expected=0,Native=0,pool=0))
        save(OUT/'first-generation-result.json',dict(schema='phase582-first-generation/1',status='SOURCE_ONLY_COMPILED_PENDING_INDEPENDENT583',Source_generation_invocations=1,actual_Input_bound=False,actual_B2_bound=False,model_request_runnable=False,comparison_runnable=False,author_SUT_calls=0))
        external=[pin(ROOT/p) for p in expected]+[pin(ROOT/'data/phase582-root-candidate-context-binding/binding.json'),pin(ROOT/'data/phase582-root-candidate-context-binding/source-context-candidate-bound.json'),pin(ROOT/'data/phase582-mixed-launcher-output-plan/owned-files.json'),pin(ROOT/'docs/phase582_B2_canonical_binding_implementation_addendum_spec.md'),pin(ROOT/SPEC),pin(Path(__file__))]
        external += candidate_before+[pin(ROOT/'data/phase576-mixed-captured-consumer-design/source-preimages.json'),pin(ROOT/'data/phase562-finite-mixed-source-design/source-pins.json')]
        provenance_paths=[ROOT/'tests/phase582_prepare_mixed_output_source.py',ROOT/'tests/phase582_mixed_tape_run.py',ROOT/'tests/phase582_mixed_business_output.py',ROOT/'tests/phase582_shared_callback_guard.py',ROOT/'data/phase582-mixed-launcher-output-source/partial-source-owner.json',ROOT/'data/phase582-mixed-launcher-output-source/first-generation-error.json',ROOT/'docs/phase582_mixed_launcher_output_implementation_spec.md']
        external += [pin(p) for p in provenance_paths]
        write(OUT/'producer-v1-to-v2.patch',''.join(difflib.unified_diff(read(provenance_paths[0]).decode().splitlines(True),read(Path(__file__)).decode().splitlines(True),fromfile=str(provenance_paths[0].relative_to(ROOT)),tofile=str(Path(__file__).relative_to(ROOT)))).encode())
        owned=[pin(p) for p in sorted(OUT.iterdir()) if p.is_file()]+[pin(p) for p in (LAUNCHER,ADAPTER,B2)]+external
        unique={}
        for p in owned:require(p['path'] not in unique or unique[p['path']]==p,'unique Source descriptor');unique[p['path']]=p
        save(OUT/'source-freeze.json',dict(schema='phase582-C-source-freeze/1',files=list(unique.values()),candidate_freeze=known['candidate_freeze'],comparison_contract=contract,
            status='SOURCE_ONLY_UNBOUND_INPUT_B2_MODEL_EXPECTED_PENDING583',actual_INPUT=None,actual_model=None,Expected_reads=0))
        unique[pin(OUT/'source-freeze.json')['path']]=pin(OUT/'source-freeze.json')
        save(OUT/'owned-files.json',dict(schema='phase582-C-source-owner/1',files=list(unique.values()),no_more_writes=True,status='SOURCE_ONLY_PENDING_INDEPENDENT583'))
        print(json.dumps(dict(status='SOURCE_FROZEN_NO_SUT',owner=pin(OUT/'owned-files.json')),sort_keys=True));return 0
    except Exception as e:
        save(OUT/'first-generation-error.json',dict(schema='phase582-C-source-first-error/1',error_type=type(e).__name__,message=str(e),traceback=traceback.format_exc(),automatic_retry=False,C_imports=0,helper_SUT=0,models=0,Expected=0,Native=0,pool=0))
        partial=[pin(p) for p in sorted(OUT.iterdir()) if p.is_file()]+[pin(p) for p in (LAUNCHER,ADAPTER,B2) if p.exists()]+[pin(Path(__file__)),pin(ROOT/SPEC)]
        save(OUT/'partial-source-owner.json',dict(schema='phase582-C-partial-owner/1',files=partial,status='SOURCE_FIRST_ERROR_PRESERVED_NO_RETRY'))
        raise

if __name__=='__main__':raise SystemExit(main())
