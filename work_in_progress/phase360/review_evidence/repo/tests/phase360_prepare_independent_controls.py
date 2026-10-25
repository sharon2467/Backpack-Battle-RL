"""Preseal SOURCE-only delta review and synthetic schema-unit cases; no schema import."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import struct

R = Path(__file__).resolve().parents[1]
D = R / 'data/phase360-independent-schema-review'
A = R / 'data/phase360-schema-auxiliary-binding-source'

def pin(p):
    b=p.read_bytes(); return dict(path=str(p.relative_to(R)),size=len(b),sha256=hashlib.sha256(b).hexdigest())
def save(p,x):
    with p.open('x') as f: json.dump(x,f,indent=2,sort_keys=True);f.write('\n')
def main():
    D.mkdir(exist_ok=False); (D/'SOURCE').mkdir()
    assert pin(A/'source-owner.json')['sha256']=='ed0ff1578733c306042e8195ae6a6f85fbab3033cb5ca9f4d37915207e372542'
    owner=json.loads((A/'source-owner.json').read_text())
    for row in owner['files']: assert pin(R/row['path'])==row
    old=(R/'tests/phase358_king_observer_schema.py').read_text(); new=(R/'tests/phase360_king_observer_schema.py').read_text()
    ot,nt=ast.parse(old),ast.parse(new)
    assignments=lambda t:{z.id:n for n in t.body if isinstance(n,ast.Assign) for z in n.targets if isinstance(z,ast.Name)}
    oa,na=assignments(ot),assignments(nt); om,nm=ast.literal_eval(oa['MATRIX'].value),ast.literal_eval(na['MATRIX'].value)
    funcs=lambda t:{n.name:ast.dump(n,include_attributes=False) for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
    of,nf=funcs(ot),funcs(nt); assert len(of)==58 and all(nf[k]==v for k,v in of.items())
    extras=set(nm['sites'])-set(om['sites']); assert extras=={'Items/Goobert.gd::'+x for x in ('prepare','onItemActivated','doCooldownEffect')}
    inverse=copy.deepcopy(nm)
    for k in extras: del inverse['sites'][k]
    assert inverse==om and len(om['sites'])==103
    prefix=nt.body[:len(ot.body)]; assert len(prefix)==len(ot.body)
    for x,y in zip(ot.body,prefix):
        if x is oa['MATRIX']: continue
        assert ast.dump(x,include_attributes=False)==ast.dump(y,include_attributes=False)
    allowed={'hashlib','json','math','re','struct','copy','dataclasses','types'}
    for n in nt.body:
        if isinstance(n,ast.Import): assert {a.name.split('.')[0] for a in n.names}<=allowed
        if isinstance(n,ast.ImportFrom): assert n.module.split('.')[0] in allowed
    combination=next(n for n in nt.body if isinstance(n,ast.FunctionDef) and n.name=='validate_sources_with_binding')
    calls=[n.func.id for n in ast.walk(combination) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)]
    assert calls.index('validate_source_carriers')<calls.index('join_binding_provenance')
    for n in ast.walk(nt):
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name): assert n.func.id not in {'open','eval','exec','__import__'}
    for src,dst in [('tests/phase360_king_observer_schema.py','schema.py'),('tests/phase360_binding_schema_extension.py','extension.py')]: (D/'SOURCE'/dst).write_bytes((R/src).read_bytes())
    for n in ['source-contract.json','fixed-slot-map.json','schema-source-freeze.json','goobert-three-site-source-map.json']:(D/'SOURCE'/n).write_bytes((A/n).read_bytes())
    c=ast.literal_eval(na['CONTRACT'].value); plan=json.loads((A/'fixed-slot-map.json').read_text()); source_contract=json.loads((A/'source-contract.json').read_text())
    I=lambda n:dict(type='int',decimal=str(n)); F=lambda n=0.:dict(type='float',binary64_be=struct.pack('>d',float(n)).hex()); B=lambda b=False:dict(type='bool',value=b); N=lambda:dict(type='null')
    S=lambda s:dict(type='string',value=s)
    ref=lambda n,role=None,cls='Node2D':dict(type='native_ref',native_id=n,role=role,**{'class':cls})
    td=lambda d:dict(type='dictionary',entries=[dict(key=S(k),value=v) for k,v in d.items()])
    cache=lambda:dict(type='dictionary',entries=[dict(key=I(k),value=dict(type='dictionary',entries=[])) for k in (0,2,4,7)])
    def node(n='9800',role='king_buff:P:12',cls='Timer'):
        return dict(native_id=n,role=role,**{'class':cls},name='SYNTHETIC',path='/SYNTHETIC_SCHEMA_UNIT/'+n,positions=[0],priority=0,inside_tree=True,ordinary_idle=False,ordinary_physics=False,internal_idle=False,internal_physics=False)
    def state(kind):
        out={}
        for k,t in c['state_schemas'][kind].items():
            if t=='auto_hide':v=state('auto_hide')
            elif t in ('node','timer','timer|null'):v=node() if t=='node' else state('timer')
            elif t=='id':v='9800'
            elif kind=='timer' and t in ('bool','int'):v=False if t=='bool' else 0
            elif t=='int':v=I(0)
            elif t=='float':v=F(1. if k in ('wait_time','speed_scale','speedScale') else 0.)
            elif t=='bool':v=B()
            elif t in ('array','temporary_array'):v=dict(type='array',values=[])
            elif t=='dictionary':v=cache() if k=='currentAffectedItems' else dict(type='dictionary',entries=[])
            elif '|null' in t:v=N()
            elif t=='string':v=S('SYNTHETIC_SCHEMA_UNIT')
            else:raise AssertionError((kind,k,t))
            out[k]=v
        if kind=='king':out.update(descriptorIndex=I(262),activationsToTrigger=F(6),protectedBuffs=F(3),manaCost=F(4))
        return out
    stamp=lambda:dict(physics_frame='1',idle_frame='1',util_time=F(),combat_time=N(),phase='SYNTHETIC_SCHEMA_UNIT')
    def record(site,edge,payload,seq,channel='runtime',subject=None):
        return dict(schema='observer7-record/1',sequence=seq,channel=channel,site=site,edge=edge,payload=payload,subject=ref('40012','P:12') if subject is None else subject,stamp=stamp())
    cases=[]
    def add(label,op,data,expect='accept',**kw):cases.append(dict(id=len(cases)+1,label=label,operation=op,data=data,expected=expect,**kw))
    kings=[]
    for method,args in [('prepare',{}),('onItemActivated',{'event':dict(type='event_ref',native_id='9900',event_id='1')}),('doCooldownEffect',{})]:
        site='Items/Goobert.gd::'+method; row=record(site,'enter',dict(arguments=td(args),state=state('king')),0); kings.append(row)
        add('new-site-'+method+'-entry','RECORD',row)
        bad=copy.deepcopy(row);bad['payload']['arguments']=td({'unexpected':I(0)});add('new-site-'+method+'-wrong-arguments','RECORD',bad,'reject')
        bad=copy.deepcopy(row);del bad['payload']['state']['invuCharges'];add('new-site-'+method+'-missing-King-field','RECORD',bad,'reject')
    paired=[]
    for row in kings:
        enter=copy.deepcopy(row);enter['sequence']=len(paired);paired.append(enter)
        leave=copy.deepcopy(enter);leave.update(edge='return_implicit',sequence=len(paired),payload=dict(return_value=N(),state=copy.deepcopy(enter['payload']['state'])));paired.append(leave)
    add('all-three-delegated-expected-pairing','OBSERVATIONS',paired)
    bad=copy.deepcopy(paired);bad[1]['subject']['native_id']='9999';add('new-site-pair-native-mismatch','OBSERVATIONS',bad,'reject')
    bad=copy.deepcopy(kings[0]);bad['payload']['state']=state('plain_item');bad['payload']['state']['descriptorIndex']=I(1);add('new-Goobert-rejects-plain-Item','RECORD',bad,'reject')
    bad=copy.deepcopy(paired[1]);bad['edge']='return_explicit';add('new-site-no-explicit-return','RECORD',bad,'reject')
    binding=dict(schema='phase359-source-slot-bindings/1',source_slot_table=copy.deepcopy(plan),actual_bindings=[],raw_early_rows_unchanged=True,model_input_admitted=False,remaining_interface='NOT_IN_358_ELEVEN_CARRIER_SCHEMA')
    for index,spec in enumerate(plan):
        side=spec['side'];binding['actual_bindings'].append(dict(instance_id=spec['instance_id'],input_slot=spec['input_slot'],native_id=str(40000+index),descriptor_id=str(10000+spec['item_index']),item_index=I(spec['item_index']),top_left=dict(x=F(spec['x']),y=F(spec['y'])),orientation=I(spec['f']),occupiedCells=copy.deepcopy(spec['cells']),inventory_id='30001' if side=='P' else '30002',character_id='20001' if side=='P' else '20002',inventory_encounter_index=spec['input_slot']))
    add('local39-SOURCE-shape-and-shared-descriptors','LOCAL',binding)
    reordered=copy.deepcopy(binding);reordered['actual_bindings'][0],reordered['actual_bindings'][1]=reordered['actual_bindings'][1],reordered['actual_bindings'][0]
    for i,row in enumerate(reordered['actual_bindings']):row['inventory_encounter_index']=i if i<20 else i-20
    add('local-actual-inventory-order-distinct-from-input-order','LOCAL',reordered)
    # Mutations are minimal and preserve every unmentioned baseline field.
    def local(label,fn):
        bad=copy.deepcopy(binding);fn(bad);add(label,'LOCAL',bad,'reject')
    def setrow(k,v,i=0):return lambda x:x['actual_bindings'][i].__setitem__(k,v)
    local('reject-O12-renumber',setrow('instance_id','O:12',32))
    local('reject-O13-inputslot13-instead-of12',setrow('input_slot',13,32))
    local('reject-BOOL-inputslot',setrow('input_slot',False))
    local('reject-BOOL-itemIndex',setrow('item_index',B(True)))
    local('reject-REAL-itemIndex',setrow('item_index',F(11)))
    local('reject-INT-topLeft',lambda x:x['actual_bindings'][0]['top_left'].__setitem__('x',I(plan[0]['x'])))
    local('reject-REAL-orientation',setrow('orientation',F(0)))
    local('reject-foreign-geometry',lambda x:x['actual_bindings'][0]['occupiedCells'][0].__setitem__(0,127))
    local('reject-duplicate-item-native',setrow('native_id',binding['actual_bindings'][1]['native_id']))
    local('reject-character-item-alias',setrow('native_id','20001'))
    local('reject-cross-side-inventory-alias',lambda x:[r.__setitem__('inventory_id','30001') for r in x['actual_bindings'] if r['instance_id'].startswith('O:')])
    local('reject-inconsistent-side-inventory',setrow('inventory_id','30003'))
    local('reject-descriptor-item-alias',lambda x:[r.__setitem__('descriptor_id','40000') for r in x['actual_bindings'] if r['item_index']==I(11)])
    local('reject-one-index-two-descriptors',setrow('descriptor_id','19999'))
    local('reject-one-descriptor-two-indices',setrow('descriptor_id','10011',12))
    local('reject-duplicate-inventory-ordinal',lambda x:x['actual_bindings'][1].__setitem__('inventory_encounter_index',0))
    local('reject-source-plan-BOOL-alias',lambda x:x['source_slot_table'][0].__setitem__('f',False))
    local('reject-caller-admission-flag',lambda x:x.__setitem__('model_input_admitted',True))
    add('reject-aux-unknown-key','LOCAL',dict(binding,unknown=True),'reject')
    add('reject-aux-missing-newline','RAW',json.dumps(binding,separators=(',',':')),'reject')
    add('reject-aux-duplicate-JSON-key','RAW',json.dumps(binding,separators=(',',':'))[:-1]+',"schema":"phase359-source-slot-bindings/1"}\n','reject')
    add('reject-aux-trailing-value','RAW',json.dumps(binding,separators=(',',':'))+'\n{}\n','reject')
    # This fixture tests relation-only join. Non-row clock/UI/facts placeholders intentionally fail full11 validation.
    names=ast.literal_eval(na['INPUT_FILES'].value)
    decoded={name:([{'SYNTHETIC_RELATION_UNIT_ONLY':True}] if name.endswith('.jsonl') else {}) for name in names}
    for name in ['observer7-input.jsonl','observer7-lineage.jsonl','observer7-metadata.jsonl','observer7-primitives.jsonl']:decoded[name]=[]
    byrole={r['instance_id']:r for r in binding['actual_bindings']}; descriptors={s['item_index']:'res://SYNTHETIC_SCHEMA_UNIT/'+str(s['item_index'])+'.tscn' for s in plan}
    for i,spec in enumerate(plan):
        r=byrole[spec['instance_id']];native=r['native_id']
        scene=record('Items/ItemDescriptor.gd::instantiate','scene_instance',dict(descriptor_id=r['descriptor_id'],item_id=native,item_index=I(spec['item_index']),scene_path=descriptors[spec['item_index']],pooled=False,particle=None),10+i*2,'lineage',ref(native))
        ready=record('Items/Item.gd::_ready','enter',dict(arguments=td({}),state={'native_id':native}),11+i*2,'lineage',ref(native))
        decoded['observer7-lineage.jsonl'] += [scene,ready]
    descrows=[]
    for ix,path in sorted(descriptors.items()):descrows.append(td(dict(itemIndex=I(ix),identifier=S('SYNTHETIC'),types=dict(type='array',values=[]),tags=I(0),gainedStacks=I(0),removedStacks=I(0),usedStacks=I(0),hasBattleRageEffect=B(),descriptionKey=S('SYNTHETIC'),scene_path=S(path))))
    decoded['observer7-metadata.jsonl']=[record('Sheets/ItemBook.gd::detectMentionedStacks','loaded_descriptors',dict(descriptors=dict(type='array',values=descrows),locale='SYNTHETIC'),1,'metadata',N())]
    timer_roles=['tick:P','tick:O','fatigue:start','fatigue:tick','invu:P','invu:O','king_buff:P:12','king_hide:P:12','king_drag:P:12']+['buff:'+s+':'+str(c) for s in ('P','O') for c in range(100,111)]+['aux:'+s+':'+k for s in ('P','O') for k in ('battleRageTimer','autoRageTimer')]
    roles=['root_viewport','game','util','combat_timer','character:P','character:O']+timer_roles+['item:'+s['instance_id'] for s in plan]
    nodes=[]
    for i,role in enumerate(roles):
        inner=role.split(':',1)[1] if role.startswith(('item:','character:')) else role
        native=byrole[inner]['native_id'] if role.startswith('item:') else '20001' if role=='character:P' else '20002' if role=='character:O' else str(60000+i)
        cls='Timer' if role in timer_roles else 'Node2D' if role.startswith('item:') else 'Node'
        nd=node(native,inner,cls);tm=state('timer') if role in timer_roles else None
        if tm:tm['node']=copy.deepcopy(nd)
        nodes.append(dict(role=role,node=nd,timer=tm))
    items=[]
    for spec in plan:
        fields=state('king' if spec['item_index']==262 else 'potion' if spec['item_index']==19 else 'plain_item');fields.update(descriptorIndex=I(spec['item_index']),faceDirection=I(spec['f']),placed=B(True),ownerType=I(1 if spec['side']=='P' else 3))
        items.append(dict(instance=spec['instance_id'],fields=fields,dragged=B(),moveback_running=B(),cachedAffectedItems=dict(type='dictionary',entries=[]),currentAffectedItems=cache()))
    resources=[]
    for side,native in [('P','20001'),('O','20002')]:
        buffs=[]
        for category in range(100,111):
            bs=state('buff');bs.update(type=I(category),character=ref(native,side,'Node'));buffs.append(dict(stack=I(category),state=bs))
        resources.append(dict(side=side,native_id=native,buffProtectStacks=I(0),debuffReflectStacks=I(0),buffs=buffs))
    payload=dict(environment=dict(fps=I(60),scale=F(1),paused=B()),nodes=nodes,items=items,source_resources=resources)
    decoded['observer7-input.jsonl']=[record('Core/Game.gd::'+m,'checkpoint',copy.deepcopy(payload),s,'input',N()) for m,s in [('prepareItems',100),('activateItems',110)]]
    primitive=dict(kind='randi_range',label='damage:P:13',args=[I(1),I(1)],value=I(1),context=dict.fromkeys(c['primitive_context_exact']))
    decoded['observer7-primitives.jsonl']=[record('Utility/BalancedRange.gd::randIntRange','return_native_primitive',primitive,120,'primitive',N())]
    add('synthetic-relation-join-positive-immutable','JOIN',decoded)
    def joinbad(label,fn):
        bad=copy.deepcopy(decoded);fn(bad);add(label,'JOIN',bad,'reject')
    inp='observer7-input.jsonl'; lin='observer7-lineage.jsonl';meta='observer7-metadata.jsonl';prim='observer7-primitives.jsonl'
    joinbad('reject-checkpoint-native-discontinuity',lambda x:x[inp][1]['payload']['nodes'][-1]['node'].__setitem__('native_id','99998'))
    joinbad('reject-checkpoint-item-descriptor',lambda x:x[inp][1]['payload']['items'][0]['fields'].__setitem__('descriptorIndex',I(1)))
    joinbad('reject-checkpoint-ownerType',lambda x:x[inp][0]['payload']['items'][0]['fields'].__setitem__('ownerType',I(3)))
    joinbad('reject-checkpoint-inner-role',lambda x:x[inp][0]['payload']['nodes'][-1]['node'].__setitem__('role','O:18'))
    joinbad('reject-scene-descriptor-id',lambda x:x[lin][0]['payload'].__setitem__('descriptor_id','19999'))
    joinbad('reject-scene-metadata-path',lambda x:x[lin][0]['payload'].__setitem__('scene_path','res://FOREIGN.tscn'))
    joinbad('reject-scene-index',lambda x:x[lin][0]['payload'].__setitem__('item_index',I(1)))
    joinbad('reject-ready-wrong-owner',lambda x:x[lin][1]['payload']['state'].__setitem__('native_id','99999'))
    joinbad('reject-early-role-restamp',lambda x:x[lin][1]['subject'].__setitem__('role','P:0'))
    joinbad('reject-ready-before-scene-order',lambda x:x[lin].__setitem__(slice(0,2),list(reversed(x[lin][:2]))))
    joinbad('reject-ready-after-pre',lambda x:x[inp][0].__setitem__('sequence',5))
    joinbad('reject-birth-frame-order',lambda x:x[lin][0]['stamp'].__setitem__('physics_frame','2'))
    joinbad('reject-metadata-foreign-index',lambda x:x[meta][0]['payload']['descriptors']['values'][0]['entries'][0].__setitem__('value',I(999)))
    joinbad('reject-physical-file-channel',lambda x:x[lin][0].__setitem__('channel','input'))
    joinbad('reject-cross-channel-sequence-duplicate',lambda x:x[prim][0].__setitem__('sequence',100))
    joinbad('reject-BOOL-physical-sequence',lambda x:x[prim][0].__setitem__('sequence',True))
    add('reject-different-SOURCE-contract','JOIN_CONTRACT',decoded,'reject')
    add('reject-incomplete-synthetic-full11-combination','FULL_REFUSAL',decoded,'reject')
    assert len(cases)<=64,len(cases)
    save(D/'cases.json',cases)
    save(D/'static-review.json',dict(schema='phase360-independent-static/1',status='PASS',author_leaves=len(owner['files']),author_bytes=sum(x['size'] for x in owner['files']),old_functions_classes_AST=58,old_sites_exact=103,new_sites=sorted(extras),whole_old_module_prefix_inverse_AST=True,combination_full11_before_join=True,no_filesystem_or_runtime_import=True,guard356='UNCHANGED_CLOSED',schema_imports=0,actual_full12_positive=False,preparation_metadata_note='One exploratory AST literal_eval on ROW_CAPS Call failed before controls were built/imported; not a schema call or semantic case. No successful semantic batch repeated.'))
    print(json.dumps({'cases':len(cases),'positive':sum(x['expected']=='accept' for x in cases),'negative':sum(x['expected']=='reject' for x in cases),'static':'PASS'}))
if __name__=='__main__':main()
