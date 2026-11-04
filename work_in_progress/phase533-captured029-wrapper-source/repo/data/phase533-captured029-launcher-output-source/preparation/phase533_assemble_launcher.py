from pathlib import Path
import ast,json,hashlib
R=Path('/workspace/python-original-engine/repo');old=(R/'tests/phase476_joint_tape_run.py').read_text();api=json.loads((R/'data/phase526-launcher-output-design-v2/api-contract.json').read_bytes());fixed=api['fixed_bindings'];guardpath=R/'tests/phase533_shared_callback_guard.py';guardraw=guardpath.read_bytes();guardtree=ast.parse(guardraw)
def literal(name):return ast.literal_eval(next(n.value for n in guardtree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets)))
def fn(name):return ast.get_source_segment(old,next(n for n in ast.parse(old).body if isinstance(n,ast.FunctionDef) and n.name==name))
constants=dict(ROOT=None,CASE='NATIVE-029-WHELP-FAMILY-A',PROFILE='pure-combat-whelp-family-A-captured/1',SCHEMA='native-v8-pure-combat-runtime-input/whelp-family-1',FREEZE=fixed['candidate_freeze'],INPUT_SOURCE=fixed['input_source_owner'],INPUT_ABI=fixed['input_abi'],CONTRACT=fixed['comparison_contract'],INPUT_ACCEPTANCE_OWNER=fixed['input_acceptance_owner'],FIXED_INPUTS=dict(candidate_freeze=fixed['candidate_freeze'],input_source_owner=fixed['input_source_owner'],input_abi=fixed['input_abi'],input_bundle=fixed['input_artifacts']['input-bundle.json'],input_proof=fixed['input_artifacts']['input-proof.json'],initial_receipt=fixed['input_artifacts']['initial-receipt.json'],prepared_witness=fixed['input_artifacts']['prepared-witness.json'],input_seal=fixed['input_artifacts']['input-seal.json'],input_owner=fixed['input_artifacts']['owned-files.json'],input_acceptance=fixed['input_acceptance'],candidate_acceptance=fixed['candidate_acceptance'],comparison_contract=fixed['comparison_contract']),CLOSURE_EXTRACTOR=dict(path='tests/phase533_shared_callback_guard.py',size=len(guardraw),sha256=hashlib.sha256(guardraw).hexdigest()),CLOSURE_BASIS=literal('SOURCE_BASIS'),INPUT_UI_PIN=literal('INPUT_UI_PIN'))
out='''"""One fixed029 captured Tape model run. No Expected/oracle/retry/seed fallback."""\nimport argparse\nimport datetime\nimport hashlib\nimport importlib\nimport json\nimport math\nimport os\nfrom pathlib import Path\nimport stat\nimport struct\nimport sys\nimport time\nimport traceback\n\nROOT = Path(__file__).resolve().parents[1]\n'''
for k,v in constants.items():
 if k!='ROOT':out+=k+' = '+repr(v)+'\n'
for name in ('strict_json','pin','path_of','read_descriptor','write_json'):out+='\n\n'+fn(name)+'\n'
out+='''

def check(condition,reason):
    if not condition:raise ValueError(reason)


def same(left,right):
    return json.dumps(left,sort_keys=True,separators=(',',':'),allow_nan=False)==json.dumps(right,sort_keys=True,separators=(',',':'),allow_nan=False)


def real_bits(value):
    check(type(value) is float and math.isfinite(value),'strict finite REAL')
    return struct.pack('>d',value).hex()


def owned_contains(owner,row):
    check(type(owner) is dict and type(owner.get('files')) is list,'actual owner file list')
    covered=[p for p in owner['files'] if path_of(p['path'])==path_of(row['path'])]
    check(len(covered)==1 and all(covered[0][k]==row[k] for k in ('size','sha256')),'actual owned receipt/file identity')


def validate_request(request):
    expected={'schema','case_id','launcher','candidate_freeze','input_source_owner','input_abi','input_bundle','input_proof','initial_receipt','prepared_witness','input_seal','input_owner','input_acceptance','candidate_acceptance','business_closure','comparison_contract','root_model_authorized'}
    check(type(request) is dict and set(request)==expected and request['schema']=='phase533-root-captured-whelp-model-request/1' and request['case_id']==CASE and request['root_model_authorized'] is True,'closed17 fixed Root model request/authorization')
    check(path_of(request['launcher']['path'])==Path(__file__).resolve(),'exact executing launcher')
    for name,row in FIXED_INPUTS.items():check(request[name]==row,'exact accepted Source/INPUT identity '+name)
    provenance={name:read_descriptor(request[name]) for name in FIXED_INPUTS}
    provenance['launcher']=read_descriptor(request['launcher'])
    provenance['input_acceptance_owner']=read_descriptor(INPUT_ACCEPTANCE_OWNER)
    owned_contains(strict_json(provenance['input_acceptance_owner']),request['input_acceptance'])
    owner=strict_json(provenance['input_owner']);seal=strict_json(provenance['input_seal'])
    check(seal['status']=='INPUT_ONLY_NOT_RUNTIME_VALIDATED' and seal['runtime_validated'] is False and seal['model_release'] is False,'honest INPUT-only seal')
    for name in ('input_bundle','input_proof','initial_receipt','prepared_witness','input_seal'):owned_contains(owner,request[name])
    pair=request['business_closure'];check(type(pair) is dict and set(pair)=={'receipt','owner'},'owned actual B2 receipt pair, no boolean certificate')
    provenance['business_closure']=read_descriptor(pair['receipt']);provenance['business_closure_owner']=read_descriptor(pair['owner'])
    owned_contains(strict_json(provenance['business_closure_owner']),pair['receipt'])
    closure=strict_json(provenance['business_closure']);check(type(closure) is dict and set(closure)=={'schema','extraction_source','guard'} and closure['schema']=='phase533-owned-shared-callback-closure/1','actual owned closure schema')
    check(closure['extraction_source']==CLOSURE_EXTRACTOR,'code-bound B2 extraction Source');provenance['closure_extractor']=read_descriptor(CLOSURE_EXTRACTOR)
    guard=closure['guard'];check(type(guard) is dict and guard['schema']=='phase533-actual029-B2-guard/1' and guard['status']=='ACTUAL_FIXED29_WINDOW_MATCHES_SOURCE_GUARD','actual typed window extraction')
    check(guard['raw_descriptor']==INPUT_UI_PIN and guard['input_bundle']==request['input_bundle'] and guard['input_proof']==request['input_proof'] and same(guard['source_basis'],CLOSURE_BASIS),'actual window/source/input association')
    check(type(guard['model_noop_slots']) is int and guard['model_noop_slots']==31 and type(guard['native_roles_verified']) is int and guard['native_roles_verified']==29 and guard['full_FX_UI_gate_called'] is False,'exact31 conditional callback scope')
    bundle=strict_json(provenance['input_bundle']);proof=strict_json(provenance['input_proof']);initial=strict_json(provenance['initial_receipt']);witness=strict_json(provenance['prepared_witness'])
    check(type(bundle) is dict and set(bundle)=={'schema','fixture','runtime','draws','synthetic_seed'} and bundle['schema']=='native-v8-input-only/1' and bundle['synthetic_seed'] is None,'actual INPUT-only envelope')
    data=bundle['runtime'];check(data['schema']==SCHEMA and data['profile_id']==PROFILE and data['mode']=='genuine' and len(data['initial_items'])==29 and len(data['timer_initial'])==32 and len(data['processing_nodes'])==67 and len(data['nodes'])==66,'closed29/raw32/67/66')
    check(type(bundle['draws']) is list and len(bundle['draws'])==297 and len(data['frame_clock']['passes'])==1089,'complete actual INPUT Tape/clock, not inferred model result')
    check(initial['counts']['SOURCE_DERIVED']==72 and len(witness['items'])==29 and witness['stage']=='pre_activate','actual72/witness prerequisites')
    return bundle,strict_json(provenance['candidate_freeze']),proof,initial,witness,provenance


def prepared_business_view(engine,bundle):
    check(engine.captured_clock_mode and not engine.king_mode and engine.king_states=={},'actual zeroKing captured instance')
    check(engine.prepared is True and engine.activated is False,'same instance prepared not activated')
    expected={i['instance_id']:i for side in bundle['fixture']['sides'] for i in side['items']}
    check(set(engine.items)==set(expected),'same-instance29 items')
    types=engine.items['P:14'].definition['random_buff_types'];check(type(types) is tuple,'live Sapphire definition tuple')
    basic=engine.items['P:9'];timers={}
    for role in bundle['runtime']['timer_initial']:
        node=engine.runtime_roles[role]
        timers[role]=dict(private_left_bits=real_bits(node.private_left),wait_time_bits=real_bits(node.wait_time),process_mode=node.process_mode,one_shot=node.one_shot,autostart=node.autostart,paused=node.paused,processing=node.processing,inside_tree=node.inside_tree,ordinary_physics=node.ordinary_physics,internal_physics=node.internal_physics,ordinary_idle=node.ordinary_idle,internal_idle=node.internal_idle)
    return dict(profile=engine.runtime_inputs.data['profile_id'],prepared=engine.prepared,activated=engine.activated,king_mode=engine.king_mode,king_states=dict(engine.king_states),tape_position=engine.random.position,tape_audit_length=len(engine.random.audit),passes_consumed=engine.frame_driver.pass_index,
        snapshots=[{k:s[k] for k in ('stage','clock','off_clock')} for s in engine.pure_snapshots],
        items={k:dict(item_index=i.item_index,cache_prepared=i.cache_prepared) for k,i in engine.items.items()},
        caches={k:[i.instance_id for i in v] for k,v in engine.affected_items_cache.items()},listeners={k:list(v) for k,v in engine.activation_listeners.items()},
        Basic=dict(activations=basic.goobert_activations,threshold=basic.definition['activations_to_trigger'],iterationCooldown_bits=real_bits(basic.iteration_cooldown),triggerTime_bits=real_bits(basic.trigger_time)),Sapphire_types=list(types),timers=timers,
        characters={s:dict(invulnerable=c.invulnerable,invulnerabilityItem=engine.invu_origins[s],buffProtectStacks=c.buff_protect_stacks) for s,c in engine.characters.items()})


def validate_prepared_business_view(view,bundle,witness,initial):
    check(type(view) is dict and view['profile']==PROFILE and view['prepared'] is True and view['activated'] is False and view['king_mode'] is False and view['king_states']=={},'same-instance prepared zeroKing stage')
    check(all(type(view[k]) is int and view[k]==0 for k in ('tape_position','tape_audit_length','passes_consumed')),'no Tape/pass progress before activation')
    check(len(view['snapshots'])==2 and [s['stage'] for s in view['snapshots']]==['constructed_off_clock','prepare_off_clock'] and all(s['clock'] is None and s['off_clock'] is True for s in view['snapshots']),'constructor/prepare actual off-clock snapshots')
    items={i['instance_id']:i for side in bundle['fixture']['sides'] for i in side['items']};nodes={n['role']:n for n in bundle['runtime']['processing_nodes']}
    check(len(items)==29 and set(view['items'])==set(witness['items'])==set(items),'prepared29 identity')
    check(initial['counts']['SOURCE_DERIVED']==72,'accepted actual initial72 receipt')
    consumers={identity for identity,item in items.items() if item['item_index'] in (22,23,164)}
    check(set(view['caches'])==consumers,'exact six business cache consumers')
    for identity,observation in witness['items'].items():
        check(view['items'][identity]['item_index']==items[identity]['item_index'] and type(view['items'][identity]['item_index']) is int and view['items'][identity]['cache_prepared'] is True,'prepared item type/cache stage')
        check(observation['native_id']==nodes['item:'+identity]['native_id'],'actual witness native owner')
        for key in ('ordered_cache_aliases','ordered_current_aliases'):
            check(type(observation[key]) is list,'ordered alias list')
            colors=[x['color'] for x in observation[key]];check(colors==[{'type':'int','decimal':str(k)} for k in (0,2,4,7)],'declared typed color ordering')
        cache=observation['ordered_cache_aliases'][0];current=observation['ordered_current_aliases'][0]
        check(len(cache['ordered_roles'])==len(cache['ordered_native_ids']) and len(set(cache['ordered_roles']))==len(cache['ordered_roles']),'cache ordered unique membership')
        for role,native in zip(cache['ordered_roles'],cache['ordered_native_ids']):check(role in items and native==nodes['item:'+role]['native_id'],'cache target UID/role association')
        current_roles=[]
        for member in current['ordered_members']:
            role=member['role'];check(role in items and member['native_id']==nodes['item:'+role]['native_id'] and member['value']=={'type':'bool','value':True},'current target typed membership/UID');current_roles.append(role)
        check(current_roles==cache['ordered_roles'],'current/cached consumed target order')
        if identity in consumers:check(view['caches'][identity]==cache['ordered_roles'],'actual model consumed target order '+identity)
    basic=view['Basic'];fields=witness['items']['P:9']['goobert_state']
    check(type(basic['activations']) is int and fields['activations']=={'type':'int','decimal':str(basic['activations'])},'Basic strictINT counter')
    check(type(basic['threshold']) is int and fields['activationsToTrigger']=={'type':'float','binary64_be':real_bits(float(basic['threshold']))},'Basic threshold REAL source conversion')
    for name in ('iterationCooldown','triggerTime'):check(fields[name]=={'type':'float','binary64_be':basic[name+'_bits']},'Basic actual cooldown/trigger bits')
    types=view['Sapphire_types'];check(type(types) is list and all(type(x) is int for x in types),'Sapphire ordered strictINT')
    check(witness['items']['P:14']['stackTypes']=={'type':'array','values':[{'type':'int','decimal':str(x)} for x in types]},'Sapphire observed ordered types')
    # Native fresh Basic connection order is a singleton Source consequence, not UI current-cache identity.
    check(view['listeners']=={'P:10':['P:9']} and view['caches']['P:9']==['P:10'],'actual Basic registered listener mapping')
    check(set(view['timers'])==set(bundle['runtime']['timer_initial']) and len(view['timers'])==32,'all32 real initial Timer records')
    for role,timer in view['timers'].items():
        expected=bundle['runtime']['timer_initial'][role]
        check(all(type(timer[k]) is type(v) and timer[k]==v for k,v in expected.items()),'source-supported initial Timer '+role)
        check(timer['inside_tree'] is True and all(type(timer[k]) is bool and timer[k] is False for k in ('processing','ordinary_physics','internal_physics','ordinary_idle','internal_idle')),'inactive initial actual Timer flags '+role)
    check(same(view['characters'],bundle['runtime']['initial_characters']),'actual Character initial/protection/origin fields')
    return dict(schema='phase533-same-instance-prepared-business-gate/1',status='PASS_PRE_ACTIVATION_SAME_INSTANCE',consumer_cache_roles=sorted(consumers),caches=view['caches'],listeners=view['listeners'],Basic=basic,Sapphire_types=types,timer_count=32,Tape_position=view['tape_position'],passes_consumed=view['passes_consumed'],scope='Actual business consumed cache order/Basic/Sapphire; no UI model replication or Native listener sample assertion')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--config',required=True);parser.add_argument('--config-sha256',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    launcher=Path(__file__).resolve();config_path=path_of(args.config);config_raw,config_pin=pin(config_path)
    check(config_pin['sha256']==args.config_sha256,'Root request SHA');request=strict_json(config_raw)
    bundle,freeze,proof,initial,witness,provenance=validate_request(request)
    staged=ROOT/'data/phase505-captured-nonking-source-v3/staged';sources={}
    check(len(freeze['files'])==15,'exact15 candidate Source')
    for row in freeze['files']:
        relative=Path(row['relative']);path=path_of(row['path']);check(not relative.is_absolute() and '..' not in relative.parts and staged/relative==path and str(path) not in sources,'fixed505 staged root')
        _,sources[str(path)]=pin(path,{k:row[k] for k in ('size','sha256')})
    check({str(p) for p in staged.rglob('*.py')}==set(sources),'no unexpected candidate Python Source')
    check(not any(n==p or n.startswith(p+'.') for n in sys.modules for p in ('native_replay_v8','native_replay_v7','original_rng','godot_pcg_integer')),'fresh single import')
    output=path_of(args.output);check(output.parent==ROOT/'data' and output.name.startswith('phase533-') and not output.exists() and not output.is_symlink() and not any(p.is_symlink() for p in output.parents),'new phase533 output')
    output.mkdir(mode=0o700)
    before=dict(schema='phase533-captured029-before/1',case_id=CASE,launcher=request['launcher'],execution_request=dict(path=str(config_path),**config_pin),candidate_freeze=FREEZE,sources=sources,input_bundle=request['input_bundle'],input_proof=request['input_proof'],prepared_witness=request['prepared_witness'],initial_receipt=request['initial_receipt'],comparison_contract=CONTRACT,business_closure=request['business_closure'],expected_reads=0,new_original_capture=0,utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    owned={'before.json':write_json(output/'before.json',before)};reads=[]
    watched={str(launcher):{k:request['launcher'][k] for k in ('size','sha256')},str(config_path):config_pin}
    for row in list(FIXED_INPUTS.values())+[INPUT_ACCEPTANCE_OWNER,CLOSURE_EXTRACTOR]+list(request['business_closure'].values()):watched[str(path_of(row['path']))]={k:row[k] for k in ('size','sha256')}
    allowed=set(sources)|set(watched);python_roots=[Path(sys.base_prefix).resolve(),Path(sys.prefix).resolve(),Path(os.__file__).resolve().parent]
    def within(path,parent):
        try:path.relative_to(parent);return True
        except ValueError:return False
    def audit(event,values):
        if event.startswith(('subprocess.','socket.')) or event in ('os.system','os.exec','os.spawn','os.fork','os.posix_spawn'):raise RuntimeError('model subprocess/network denied: '+event)
        if event=='open' and isinstance(values[0],(str,bytes,os.PathLike)):
            path=Path(os.fsdecode(values[0])).absolute();flags=values[2] or 0;writing=bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
            if writing:check(within(path,output),'model write outside output denied: '+str(path))
            elif within(path,staged) and '__pycache__' in path.parts and not path.exists():reads.append(str(path))
            elif str(path) not in allowed and not within(path,output) and not any(within(path,p) for p in python_roots):raise RuntimeError('model external read denied: '+str(path))
            else:reads.append(str(path))
    sys.dont_write_bytecode=True;sys.pycache_prefix=str(output/'unused-bytecode-cache');sys.addaudithook(audit);sys.path.insert(0,str(staged))
    calls=dict(candidate_import_attempts=0,construct_attempts=0,prepare_attempts=0,prepared_gate_attempts=0,activate_attempts=0,full_run_attempts=0);start=time.monotonic();engine=tape=None;status='FAILED';source_after={};input_after={}
    try:
        calls['candidate_import_attempts']+=1;module=importlib.import_module('native_replay_v8.engine');randomness=sys.modules['native_replay_v8.randomness']
        check(Path(module.__file__).absolute()==staged/'native_replay_v8/engine.py' and Path(randomness.__file__).absolute()==staged/'native_replay_v8/randomness.py','imported candidate identity')
        tape=randomness.TapeRandom(bundle['draws']);calls['construct_attempts']+=1;engine=module.CombatEngine(bundle['fixture'],tape,bundle['runtime'])
        calls['prepare_attempts']+=1;engine.prepare_only();calls['prepared_gate_attempts']+=1;view=prepared_business_view(engine,bundle);gate=validate_prepared_business_view(view,bundle,witness,initial)
        owned['prepare-gate.json']=write_json(output/'prepare-gate.json',dict(gate=gate,view=view,input_witness=request['prepared_witness'],actual_same_instance=True))
        calls['activate_attempts']+=1;engine.activate_from_checkpoint();calls['full_run_attempts']+=1;result=engine.run();tape.assert_consumed()
        owned['model-output.json']=write_json(output/'model-output.json',result)
        for name,identity in sources.items():_,source_after[name]=pin(Path(name),identity)
        for name,identity in watched.items():_,input_after[name]=pin(Path(name),identity)
        status='ACTUAL_OUTPUT_SEALED_NOT_COMPARED'
    except BaseException as exc:
        failure=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
        if engine is not None:failure['partial']=dict(events=engine.events,frame=engine.frame,elapsed=engine.elapsed,prepared=engine.prepared,activated=engine.activated,ended=engine.ended,runtime_trace=engine.runtime_trace,pure_api_trace=engine.pure_api_trace,pure_snapshots=engine.pure_snapshots)
        if tape is not None:failure['tape']=dict(position=tape.position,records=len(tape.records),audit=tape.audit)
        owned['failure.json']=write_json(output/'failure.json',failure)
    report=dict(schema='phase533-captured029-execution/1',status=status,case_id=CASE,calls=calls,elapsed_wall_seconds=time.monotonic()-start,candidate_source=str(staged),tape_position=None if tape is None else tape.position,tape_records=len(bundle['draws']),full_clock_passes=len(bundle['runtime']['frame_clock']['passes']),source_after=source_after,input_after=input_after,candidate_execution_file_reads=reads,expected_reads=0,new_original_capture=0,comparator_calls=0,King_admitted=False,formal_support=75)
    owned['execution.json']=write_json(output/'execution.json',report);write_json(output/'output-seal.json',dict(schema='phase533-output-seal/1',status=status,files=owned,request=dict(path=str(config_path),**config_pin),comparison_contract=CONTRACT))
    print(json.dumps({k:report[k] for k in ('status','calls','elapsed_wall_seconds','tape_position')}));return 0 if status=='ACTUAL_OUTPUT_SEALED_NOT_COMPARED' else 1


if __name__=='__main__':raise SystemExit(main())
'''
p=R/'tests/phase533_whelp_tape_run.py';compile(out,str(p),'exec');p.write_text(out)
print('launcher written/compile-only,0imports/model/helper calls')
