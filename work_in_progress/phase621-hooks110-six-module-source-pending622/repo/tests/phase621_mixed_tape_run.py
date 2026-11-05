"""One fixed029 captured Tape model run. No Expected/oracle/retry/seed fallback."""
import argparse
import datetime
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import stat
import struct
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
CASE = 'NATIVE-030-MIXED-MODIFIERS-A'
PROFILE = 'pure-combat-mixed-modifiers-A-captured/1'
SCHEMA = 'native-v8-pure-combat-runtime-input/mixed-modifiers-1'
FREEZE = {'path': '/workspace/python-original-engine/repo/data/phase580-captured-mixed-source/candidate-source-freeze.json', 'size': 4809, 'sha256': 'e332b765f3bd48c6df63c1ffd047f82654fe0c0465e9886275d287b42160a51b'}
INPUT_SOURCE = {'path': 'data/phase621-hooks110-rebinding-source/input/owned-files.json', 'size': 3444, 'sha256': '1d710151ab4a51a3d4d18e9103d6a232020c471f0d23f332b70e7042bd7333ae'}
INPUT_ABI = {'path': 'data/phase578-mixed-input-bridge-source/abi.json', 'size': 1362, 'sha256': '897a40ea9594be1c8adac869345646c1f6df8f9732e8663dfbd433cbff2c7eff'}
CONTRACT = {'path': 'data/phase621-hooks110-rebinding-source/output/comparison-contract.json', 'size': 3202, 'sha256': '9281c61529a841bd23fc7debdda4d7a5f5fc6d3e056b070fceb8e0971f810346'}
INPUT_ACCEPTANCE_OWNER = None
FIXED_INPUTS = {'candidate_freeze': {'path': '/workspace/python-original-engine/repo/data/phase580-captured-mixed-source/candidate-source-freeze.json', 'size': 4809, 'sha256': 'e332b765f3bd48c6df63c1ffd047f82654fe0c0465e9886275d287b42160a51b'}, 'candidate_acceptance': {'path': '/workspace/python-original-engine/repo/data/phase581-independent-final-acceptance/review.json', 'size': 9023, 'sha256': 'cc08dad18a8d6d0c263b828e8154a44010ba3cffca134bd0305e75f7016846d8'}, 'input_source_owner': {'path': 'data/phase621-hooks110-rebinding-source/input/owned-files.json', 'size': 3444, 'sha256': '1d710151ab4a51a3d4d18e9103d6a232020c471f0d23f332b70e7042bd7333ae'}, 'input_abi': {'path': 'data/phase578-mixed-input-bridge-source/abi.json', 'size': 1362, 'sha256': '897a40ea9594be1c8adac869345646c1f6df8f9732e8663dfbd433cbff2c7eff'}, 'comparison_contract': {'path': 'data/phase621-hooks110-rebinding-source/output/comparison-contract.json', 'size': 3202, 'sha256': '9281c61529a841bd23fc7debdda4d7a5f5fc6d3e056b070fceb8e0971f810346'}}
CLOSURE_EXTRACTOR = {'path': 'tests/phase621_shared_callback_guard.py', 'size': 10282, 'sha256': '6742fe2cf640c73c1fa99539de5c61f83b39e25062ef2aeb9cfa1a49d7f116a3'}
CLOSURE_BASIS = {'candidate_freeze': {'path': '/workspace/python-original-engine/repo/data/phase580-captured-mixed-source/candidate-source-freeze.json', 'size': 4809, 'sha256': 'e332b765f3bd48c6df63c1ffd047f82654fe0c0465e9886275d287b42160a51b'}, 'observer_tuple': {'path': 'data/phase610-three-selected-hook-source-v2/source-tuple.json', 'size': 2916, 'sha256': 'd6d33c940c4bcf49ac81b5572a3fee9439172fdc5c7cef096d37e4f60cae8b21'}, 'callback_slices': [{'function': '_physics_process', 'line_end': 4798, 'line_start': 4750, 'sha256': 'a53059d3b89b6d27cdef64858fe28775b2241c017799427878b78eb81bd5770c', 'size': 1079, 'wholefile': {'path': 'data/phase359-king-producer-source/after-source/Core/Game.gd', 'sha256': 'fafe9612858a25b95d8d6149531b50869dbd9709719bd5d2ab6b070b6b8283b1', 'size': 145943}}, {'function': '_process', 'line_end': 4737, 'line_start': 4736, 'sha256': 'e7200388f52f522c3de78cd1b934e14efcd0f7c427f527dc8cf6f9889ee04728', 'size': 59, 'wholefile': {'path': 'data/phase359-king-producer-source/after-source/Core/Game.gd', 'sha256': 'fafe9612858a25b95d8d6149531b50869dbd9709719bd5d2ab6b070b6b8283b1', 'size': 145943}}, {'function': '_process', 'line_end': 1937, 'line_start': 1791, 'sha256': '66e051694306fae459d6b58850797fa1e5772d10f49af5247165bc3a4c7caa0a', 'size': 5012, 'wholefile': {'path': 'data/phase572-mixed-observer-source-v2/after-source/Items/Item.gd', 'size': 178614, 'sha256': '11fb434eaa028eb965e10883d84ef7028ee96bdfbf2f53bdc71af64332ae0429'}}], 'rule_receipts': [{'path': 'data/phase444-independent-b2-review/review.json', 'sha256': '6fd0cee7140edd8771257d071a3cb92f24bf319ebd2abcc3175e758ebab73945', 'size': 5883}, {'path': 'data/phase444-root-b2-callee-supplement/source-argument.json', 'sha256': 'ad90cd5fd7e484947be5fb0ecdf5bde98d5634f5e8e85c504098da5d1a8fe2ec', 'size': 22238}], 'domain': 'Closed12 IDs1/5/11/14/22/32/162/164/231/233/234/385; ordinary Item/Bag/Food/ForestFriend/Wolper/Enchanted/fourWeapon. Independent finite Source applicability review and actual window mandatory; not all84.', 'finite_source_domain_argument': {'path': 'data/phase562-finite-mixed-source-design/source-pins.json', 'size': 8058, 'sha256': '36844a6cf790c3e6d1e37d3aefa9f8bc3ae85ed782a2d0266800829951e3770b'}}
INPUT_UI_PIN = None


CANDIDATE_CONTEXT = {'path': 'data/phase621-hooks110-rebinding-source/input/source-context.json', 'size': 8502, 'sha256': '00cfabe5a263ec9259f833477ba8f819307880b6223f41662453cdd609a21fe1'}
PROJECTION_RULE = {'path': 'data/phase582-mixed-launcher-output-source-v2/final-getter-projection-rule.json', 'size': 990, 'sha256': '644ca715e3b1ac427b0c32ed8747b3d5d982d2c7b402d58b3152e8cf13d0c11a'}


def strict_json(raw):
    def pairs(items):
        obj = {}
        for key, value in items:
            if key in obj:
                raise ValueError('duplicate JSON key: ' + key)
            obj[key] = value
        return obj
    def invalid(value):
        raise ValueError('nonfinite JSON: ' + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)


def pin(path, expected=None):
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
        raise ValueError('ordinary single-link file required: ' + str(path))
    if any(p.is_symlink() for p in path.parents):
        raise ValueError('symlink ancestor: ' + str(path))
    raw = path.read_bytes()
    after = path.stat()
    if (before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_ino, after.st_size, after.st_mtime_ns):
        raise ValueError('file changed while read: ' + str(path))
    identity = dict(size=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    if expected is not None and identity != expected:
        raise ValueError('file pin mismatch: ' + str(path))
    return raw, identity


def path_of(value):
    if type(value) is not str or not value or '..' in Path(value).parts:
        raise ValueError('explicit canonical descriptor path')
    path = Path(value)
    path = path if path.is_absolute() else ROOT / path
    if path.absolute() != path or not path.is_relative_to(ROOT):
        raise ValueError('fixed repository Source/INPUT descriptor path')
    return path


def read_descriptor(row):
    if type(row) is not dict or set(row) != {'path', 'size', 'sha256'}:
        raise ValueError('closed actual descriptor required')
    if type(row['size']) is not int or row['size'] <= 0 or type(row['sha256']) is not str or len(row['sha256']) != 64 or any(c not in '0123456789abcdef' for c in row['sha256']):
        raise ValueError('strict actual descriptor types')
    return pin(path_of(row['path']), {key: row[key] for key in ('size', 'sha256')})[0]


def write_json(path, value):
    raw = (json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':')) + '\n').encode()
    with path.open('xb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    return dict(size=len(raw), sha256=hashlib.sha256(raw).hexdigest())


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
    return bundle,strict_json(provenance['candidate_freeze']),proof,initial,witness,provenance


def prepared_business_view(engine,bundle):
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
        character_resources={s:{'baseStaminaRegen':{'type':'float','binary64_be':real_bits(c.base_stamina_regen)},'staminaRegen':{'type':'float','binary64_be':real_bits(c.stamina_regen)}} for s,c in engine.characters.items()})


def validate_prepared_business_view(view,bundle,witness,initial):
    check(type(view) is dict and view['profile']==PROFILE and view['prepared'] is True and view['activated'] is False and view['king_mode'] is False and view['king_states']=={},'same-instance prepared zeroKing stage')
    check(all(type(view[k]) is int and view[k]==0 for k in ('tape_position','tape_audit_length','passes_consumed')),'no Tape/pass progress before activation')
    check(len(view['snapshots'])==2 and [s['stage'] for s in view['snapshots']]==['constructed_off_clock','prepare_off_clock'] and all(s['clock'] is None and s['off_clock'] is True for s in view['snapshots']),'constructor/prepare actual off-clock snapshots')
    items={i['instance_id']:i for side in bundle['fixture']['sides'] for i in side['items']};nodes={n['role']:n for n in bundle['runtime']['processing_nodes']}
    check(len(items)==29 and set(view['items'])==set(witness['items'])==set(items),'prepared29 identity')
    check(initial['counts']['SOURCE_DERIVED']==72,'accepted actual initial72 receipt')
    consumers={identity for identity,item in items.items() if item['item_index'] in (5,22,162,164,231,385)}
    check(set(view['caches'])==consumers,'exact seven business cache consumers')
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
    check(view['listeners']=={},'no Goobert activation listener in this closed mixed domain')
    for identity,observation in witness['items'].items():
        check(same(view['items'][identity]['typed_fields'],observation['typed_fields']),'actual prepared mixed typed field '+identity)
    for side in ('P','O'):
        actual=witness['characters'][side]
        check(actual['native_id']==nodes['character:'+side]['native_id'],'same-cut Character resource owner')
        check(all(same(view['character_resources'][side][field],actual[field]) for field in ('baseStaminaRegen','staminaRegen')),'actual prepared Character REAL resources')
    check(set(view['timers'])==set(bundle['runtime']['timer_initial']) and len(view['timers'])==32,'all32 real initial Timer records')
    for role,timer in view['timers'].items():
        expected=bundle['runtime']['timer_initial'][role]
        check(all(type(timer[k]) is type(v) and timer[k]==v for k,v in expected.items()),'source-supported initial Timer '+role)
        check(timer['inside_tree'] is True and all(type(timer[k]) is bool and timer[k] is False for k in ('processing','ordinary_physics','internal_physics','ordinary_idle','internal_idle')),'inactive initial actual Timer flags '+role)
    check(same(view['characters'],bundle['runtime']['initial_characters']),'actual Character initial/protection/origin fields')
    return dict(schema='phase582-same-instance-prepared-business-gate/1',status='PASS_PRE_ACTIVATION_SAME_INSTANCE',consumer_cache_roles=sorted(consumers),caches=view['caches'],listeners=view['listeners'],timer_count=32,Tape_position=view['tape_position'],passes_consumed=view['passes_consumed'],scope='Actual business cache and mixed typed fields; full colors/current remain provenance')


def final_business_view(engine,result):
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
        projection_rule=PROJECTION_RULE,items=items)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--config',required=True);parser.add_argument('--config-sha256',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    launcher=Path(__file__).resolve();config_path=path_of(args.config);config_raw,config_pin=pin(config_path)
    check(config_pin['sha256']==args.config_sha256,'Root request SHA');request=strict_json(config_raw)
    bundle,freeze,proof,initial,witness,provenance=validate_request(request)
    staged=ROOT/'data/phase580-captured-mixed-source/staged';sources={}
    check(len(freeze['files'])==15,'exact15 candidate Source')
    for row in freeze['files']:
        relative=Path(row['relative']);path=path_of(row['path']);check(not relative.is_absolute() and '..' not in relative.parts and staged/relative==path and str(path) not in sources,'fixed580 staged root')
        _,sources[str(path)]=pin(path,{k:row[k] for k in ('size','sha256')})
    check({str(p) for p in staged.rglob('*.py')}==set(sources),'no unexpected candidate Python Source')
    check(not any(n==p or n.startswith(p+'.') for n in sys.modules for p in ('native_replay_v8','native_replay_v7','original_rng','godot_pcg_integer')),'fresh single import')
    output=path_of(args.output);check(output.parent==ROOT/'data' and output.name.startswith('phase582-') and not output.exists() and not output.is_symlink() and not any(p.is_symlink() for p in output.parents),'new phase582 output')
    output.mkdir(mode=0o700)
    before=dict(schema='phase582-captured030-before/1',case_id=CASE,launcher=request['launcher'],execution_request=dict(path=str(config_path),**config_pin),candidate_freeze=FREEZE,sources=sources,input_bundle=request['input_bundle'],input_proof=request['input_proof'],prepared_witness=request['prepared_witness'],initial_receipt=request['initial_receipt'],comparison_contract=CONTRACT,business_closure=request['business_closure'],expected_reads=0,new_original_capture=0,utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    owned={'before.json':write_json(output/'before.json',before)};reads=[]
    watched={str(launcher):{k:request['launcher'][k] for k in ('size','sha256')},str(config_path):config_pin}
    for row in (CANDIDATE_CONTEXT,PROJECTION_RULE):watched[str(path_of(row['path']))]={k:row[k] for k in ('size','sha256')}
    input_seal_value=strict_json(provenance['input_seal']);watched[str(path_of(input_seal_value['request']['path']))]={k:input_seal_value['request'][k] for k in ('size','sha256')}
    for row in [request[k] for k in ('candidate_freeze','input_source_owner','input_abi','input_bundle','input_proof','initial_receipt','prepared_witness','input_seal','input_owner','input_acceptance','candidate_acceptance','comparison_contract')]+[CLOSURE_EXTRACTOR]+list(request['business_closure'].values()):watched[str(path_of(row['path']))]={k:row[k] for k in ('size','sha256')}
    allowed=set(sources)|set(watched);python_roots=[Path(sys.base_prefix).resolve(),Path(sys.prefix).resolve(),Path(os.__file__).resolve().parent]
    def within(path,parent):
        try:path.relative_to(parent);return True
        except ValueError:return False
    def audit(event,values):
        if event.startswith(('subprocess.','socket.')) or event in ('os.system','os.exec','os.spawn','os.fork','os.posix_spawn'):raise RuntimeError('model subprocess/network denied: '+event)
        if event=='open' and isinstance(values[0],(str,bytes,os.PathLike)):
            path=Path(os.path.abspath(os.fsdecode(values[0])));flags=values[2] or 0;writing=bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
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
        aux=final_business_view(engine,result)
        owned['final-business-aux.json']=write_json(output/'final-business-aux.json',aux)
        status='ACTUAL_OUTPUT_SEALED_NOT_COMPARED'
    except BaseException as exc:
        failure=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
        if engine is not None:failure['partial']=dict(events=engine.events,frame=engine.frame,elapsed=engine.elapsed,prepared=engine.prepared,activated=engine.activated,ended=engine.ended,runtime_trace=engine.runtime_trace,pure_api_trace=engine.pure_api_trace,pure_snapshots=engine.pure_snapshots)
        if tape is not None:failure['tape']=dict(position=tape.position,records=len(tape.records),audit=tape.audit)
        owned['failure.json']=write_json(output/'failure.json',failure)
    try:
        for name,identity in sources.items():_,source_after[name]=pin(Path(name),identity)
        for name,identity in watched.items():_,input_after[name]=pin(Path(name),identity)
    except BaseException as exc:
        status='FAILED_SOURCE_OR_INPUT_AFTER_CHECK'
        owned['after-error.json']=write_json(output/'after-error.json',dict(type=type(exc).__name__,message=str(exc)))
    report=dict(schema='phase582-captured030-execution/1',status=status,case_id=CASE,calls=calls,elapsed_wall_seconds=time.monotonic()-start,candidate_source=str(staged),tape_position=None if tape is None else tape.position,tape_records=len(bundle['draws']),full_clock_passes=len(bundle['runtime']['frame_clock']['passes']),source_after=source_after,input_after=input_after,candidate_execution_file_reads=reads,expected_reads=0,new_original_capture=0,comparator_calls=0,King_admitted=False,formal_support=75)
    owned['execution.json']=write_json(output/'execution.json',report);write_json(output/'output-seal.json',dict(schema='phase582-output-seal/1',status=status,files=owned,request=dict(path=str(config_path),**config_pin),comparison_contract=CONTRACT))
    _,seal_identity=pin(output/'output-seal.json')
    write_json(output/'owned-files.json',dict(schema='phase582-model-output-owner/1',files=[dict(path=str(output/name),**identity) for name,identity in owned.items()]+[dict(path=str(output/'output-seal.json'),**seal_identity)],status=status))
    print(json.dumps({k:report[k] for k in ('status','calls','elapsed_wall_seconds','tape_position')}));return 0 if status=='ACTUAL_OUTPUT_SEALED_NOT_COMPARED' else 1


if __name__=='__main__':raise SystemExit(main())
