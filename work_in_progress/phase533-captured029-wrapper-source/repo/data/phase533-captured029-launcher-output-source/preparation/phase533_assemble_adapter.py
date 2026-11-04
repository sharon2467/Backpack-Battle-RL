from pathlib import Path
import ast,json,hashlib
R=Path('/workspace/python-original-engine/repo');old=R/'tests/phase476_joint_business_output.py';text=old.read_text();api=json.loads((R/'data/phase526-launcher-output-design-v2/api-contract.json').read_bytes());fixed=api['fixed_bindings'];known=api['known_input_identity'];freeze=json.loads((R/fixed['candidate_freeze']['path']).read_bytes())
def replace_fn(name,body):
 global text
 n=[x for x in ast.parse(text).body if isinstance(x,ast.FunctionDef) and x.name==name];assert len(n)==1
 lines=text.splitlines(keepends=True);a=n[0];text=''.join(lines[:a.lineno-1])+body.rstrip()+'\n'+''.join(lines[a.end_lineno:])
def constant(name,value):
 global text
 nodes=[x for x in ast.parse(text).body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in x.targets)];assert len(nodes)==1
 n=nodes[0];lines=text.splitlines(keepends=True);text=''.join(lines[:n.lineno-1])+name+' = '+repr(value)+'\n'+''.join(lines[n.end_lineno:])
constant('PROFILE','pure-combat-whelp-family-A-captured/1');constant('NATIVE_PROFILE','observer7-whelp-family-A-native-tape/1');constant('CONTRACT_SHA256',fixed['comparison_contract']['sha256']);constant('ACTIVATION_AFTER_SEQUENCE',None);constant('UI_TIMERS',frozenset())
# repr(frozenset()) is a normal Source expression, not a model invocation.
constant('CANDIDATE_FREEZE',fixed['candidate_freeze']);constant('CONTRACT_DESCRIPTOR',fixed['comparison_contract']);constant('FIXTURE_CANONICAL_SHA256',known['fixture_canonical_sha256'])
hashes={}
for row in freeze['files']:
 rel=Path(row['relative'])
 if rel.parent==Path('native_replay_v8'):hashes[rel.name]=row['sha256']
 elif rel.parent==Path('native_replay_v7'):hashes['component:'+rel.name]=row['sha256']
constant('MODEL_SOURCE_HASHES',hashes)
replace_fn('bindings','''def bindings(bundle,input_proof,root_binding):
    keys(root_binding,('schema','input_bundle','input_canonical_sha256','input_proof','input_proof_canonical_sha256','candidate_freeze','contract'),'closed fixed029 external comparison binding')
    require(root_binding['schema']=='phase533-fixed029-comparison-binding/1','external binding schema')
    for name in ('input_bundle','input_proof','candidate_freeze','contract'):
        row=root_binding[name];keys(row,('path','size','sha256'),'actual descriptor shape')
        require(type(row['path']) is str and row['path'] and type(row['size']) is int and row['size']>0 and type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}',row['sha256']) is not None,'actual descriptor types')
    require(root_binding['candidate_freeze']==CANDIDATE_FREEZE and root_binding['contract']==CONTRACT_DESCRIPTOR,'exact505 and pre-Expected contract')
    require(root_binding['input_bundle']==INPUT_BUNDLE and root_binding['input_proof']==INPUT_PROOF,'actual531 accepted INPUT/proof descriptors')
    require(canonical_sha(bundle)==root_binding['input_canonical_sha256']==INPUT_CANONICAL_SHA256,'actual bundle canonical bytes')
    require(canonical_sha(input_proof)==root_binding['input_proof_canonical_sha256']==PROOF_CANONICAL_SHA256,'actual proof canonical bytes')
    require(type(bundle) is dict and set(bundle)=={'schema','fixture','runtime','draws','synthetic_seed'} and bundle['schema']=='native-v8-input-only/1' and bundle['synthetic_seed'] is None and canonical_sha(bundle['fixture'])==FIXTURE_CANONICAL_SHA256,'actual fixed029 envelope/fixture')
    data=bundle['runtime'];require(data['schema']=='native-v8-pure-combat-runtime-input/whelp-family-1' and data['profile_id']==PROFILE and data['mode']=='genuine' and len(data['timer_initial'])==32 and len(data['nodes'])==66,'fixed029 raw32/66')
    table={n['role']:deepcopy(n) for n in data['processing_nodes']};require(len(table)==len(data['processing_nodes'])==67,'fixed67processing')
    native={n['native_id']:name for name,n in table.items()};require(len(native)==67,'native identity bijection')
    items={i['instance_id']:i for side in bundle['fixture']['sides'] for i in side['items']}
    require(len(items)==29 and all(type(i['item_index']) is int and i['item_index'] in {1,11,22,23,64,164,197,199,201} for i in items.values()),'fixed9ID zeroKing membership')
    for identity,index in {'P:9':23,'P:10':164,'P:12':201,'P:13':197,'P:14':199,'O:8':64}.items():require(items[identity]['item_index']==index,'fixed subtype identity')
    expected={'root_viewport','game','util','combat_timer','character:P','character:O'}|set(data['timer_initial'])|{'item:'+i for i in items}
    require(set(table)==expected,'complete67role graph')
    origin=input_proof['field_origins']['runtime.checkpoint'];other=input_proof['field_origins']['runtime.activate_order']
    require(origin['file']==other['file']=='observer7-input.jsonl' and type(origin['sequence']) is int and origin['sequence']>0 and origin['sequence']==other['sequence'] and data['checkpoint']['source_phase']=='Core/Game.gd::activateItems:enter','actual INPUT activation sequence witness')
    inactive=frozenset('invu:'+s for s in ('P','O'))|frozenset('aux:'+s+':'+n for s in ('P','O') for n in ('battleRageTimer','autoRageTimer'))
    require(len(inactive)==6 and inactive<=set(data['timer_initial']),'actual six inactive timers retained')
    return dict(nodes=table,native=native,timers=frozenset(data['timer_initial']),items=items,inactive_timers=inactive,activation_after_sequence=origin['sequence'])''')
replace_fn('_basic_fields','''def _basic_fields(item,bound):
    identity=item['instance'];index=bound['items'][identity]['item_index'];fields=item['fields']
    if index==23:
        require(identity=='P:9' and type(fields.get('activations')) is int,'Basic bound INT counter')
        for name in ('activationsToTrigger','iterationCooldown','triggerTime'):
            require(type(fields.get(name)) is float,'Basic REAL field '+name);bits(fields[name])
    if index==199:
        require(identity=='P:14' and type(fields.get('stackTypes')) is list,'Sapphire typed list')
        require(all(type(x) is int for x in fields['stackTypes']) and fields['stackTypes']==[101,102,103,104,106,107],'Sapphire ordered six INT')''')
replace_fn('project_model_final','''def project_model_final(result,bound):
    final=result['final'];rule=deepcopy(final['native_rule_state']);business=result['captured_terminal']['final']['business']
    require([c['instance'] for c in rule['characters']]==['P','O'] and business['king']=={},'zeroKing same final business state')
    keys(business['invu_origins'],('P','O'),'same-instance invu origins')
    rule['rules']['values']=restore_integer_table(rule['rules']['values']);seen=set()
    for char in rule['characters']:
        side=char['instance'];char['stats']=restore_integer_table(char['stats']);char['fields']['typedDamageFactors']=restore_integer_table(char['fields']['typedDamageFactors'])
        require('invulBubbleVisible' not in char['fields'] and 'invulnerabilityItem' not in char['fields'],'nonKing state projection shape')
        origin=business['invu_origins'][side];require(origin is None or type(origin) is str and origin in bound['items'],'same-instance origin alias')
        char['fields']['invulnerabilityItem']=origin
        require(first_difference(char['fields']['invulnerable'],business['characters'][side]['invulnerable']) is None,'same final invulnerable state')
        for item in char['items']:
            identity=item['instance'];require(identity in bound['items'] and identity not in seen,'model29 identity');seen.add(identity)
            for name in ('buffPowers','buffAmplificationChances'):item['fields'][name]=restore_integer_table(item['fields'][name])
            if bound['items'][identity]['item_index']==199:
                live=final['items'][identity];require(type(live['item_index']) is int and live['item_index']==199 and 'stackTypes' not in item['fields'],'same-instance Sapphire subtype')
                values=live['definition']['random_buff_types'];require(type(values) is list and all(type(x) is int for x in values),'sealed live definition typedstack')
                item['fields']['stackTypes']=deepcopy(values)
            _basic_fields(item,bound)
    require(seen==set(bound['items']),'complete model29')
    return dict(native_rule_state=rule,game=deepcopy(final['game']),event_bus=deepcopy(final['event_bus']),timer=dict(combatTime=final['timestamp'],timeAdvance=final['time_advance'],fatigueCounter=final['fatigue_counter']),winner=final['winner'])''')
# Only domain/message/dispatch edits in other functions.
text=text.replace("'all26 terminal items'","'all29 terminal items'").replace("'joint seven-ID empty particle wrapper'","'fixed9ID empty particle wrapper'")
text=text.replace("if row['sequence']<=ACTIVATION_AFTER_SEQUENCE:continue","if row['sequence']<=bound['activation_after_sequence']:continue")
text=text.replace("require(_subject(row,bound)=='item:P:6','King timeout owner');return 'king_buff:P:6',0,False","require(False,'King timeout outside zeroKing domain')")
text=text.replace("name,mode,ordinary=selected;delta=None","name,mode,ordinary=selected;require(name not in bound['inactive_timers'],'inactive timer callback');delta=None")
text=text.replace("name=row['role'];mode=row['mode']","name=row['role'];mode=row['mode']")
text=text.replace("if (name,mode) in noop_slots:","require(name not in bound['inactive_timers'],'inactive timer model callback')\n        if (name,mode) in noop_slots:")
text=text.replace('Exact28-slot','Exact31-slot').replace("'model Timer33 role'","'model raw32Timer role'")
text=text.replace("kings=value['king_source_state'];keys(kings,('P:6',),'one King snapshot')\n    king={k:decode_native(kings['P:6']['fields'][k],bound) for k in KING_KEYS}","keys(value['king_source_state'],(),'zeroKing Native snapshot');king={}")
oldking="    king_rows=[item for c in driver['model']['native_rule_state']['characters'] for item in c['items'] if item['instance']=='P:6']\n    require(len(king_rows)==1,'same-cut King state')\n    king={k:deepcopy(king_rows[0]['fields'][k]) for k in KING_KEYS}"
assert text.count(oldking)==1;text=text.replace(oldking,"    require(value['king']=={},'same-cut emptyKing state');king={}")
text=text.replace("driver=result['king_terminal']","driver=result['captured_terminal']").replace("result['king_terminal']","result['captured_terminal']")
text=text.replace('def project_native(native,bundle,root_binding):','def project_native(native,bundle,input_proof,root_binding):').replace('def project_model(result,bundle,root_binding):','def project_model(result,bundle,input_proof,root_binding):')
text=text.replace('bound=bindings(bundle,root_binding)','bound=bindings(bundle,input_proof,root_binding)')
text=text.replace("'observer7-king-basic-A-captured-candidate471'","'observer7-502-zeroKing-whelp-candidate505'")
text=text.replace('def compare_decoded(native_outputs,sealed_result,accepted_bundle,root_binding):','def compare_decoded(native_outputs,sealed_result,accepted_bundle,input_proof,root_binding):')
text=text.replace('project_native(native_outputs,accepted_bundle,root_binding),project_model(sealed_result,accepted_bundle,root_binding)','project_native(native_outputs,accepted_bundle,input_proof,root_binding),project_model(sealed_result,accepted_bundle,input_proof,root_binding)')
text=text.replace("'fixed joint26 conditional Tape business events/parents/histories/RNG/final/Timer/callback/clock'","'fixed029 raw32/29 zeroKing conditional Tape business events/parents/histories/RNG/final/Timer/callback/clock'")
text=text.replace("'28 modeled, inherited finite444 rule requires new-case applicability; no native ordinary entry rows'","'31 modeled under owned actual B2 Sourceclosure; no fabricated Native noop samples'")
text=text.replace('"""Fixed028 joint output-only business projection;', '"""Fixed029 zeroKing output-only business projection;')
text=text.replace('# Actual lawful joint INPUT checkpoint1149 immediately precedes activation enter1150.\n# This is a pinned INPUT-origin cut, not an EXPECTED-dependent callback selector.', '# Actual activation sequence is authenticated through the accepted INPUT proof.\n# No Native Expected-dependent callback selector or old fixed1150.')
text+='\nINPUT_BUNDLE = '+repr(fixed['input_artifacts']['input-bundle.json'])+'\nINPUT_PROOF = '+repr(fixed['input_artifacts']['input-proof.json'])+'\nINPUT_CANONICAL_SHA256 = '+repr(known['bundle_canonical_sha256'])+'\nPROOF_CANONICAL_SHA256 = '+repr(known['proof_canonical_sha256'])+'\n'
compile(text,str(R/'tests/phase533_whelp_business_output.py'),'exec')
(R/'tests/phase533_whelp_business_output.py').write_text(text)
# Static conservation only; no imported functions called.
newtree=ast.parse(text);newfn={n.name:ast.get_source_segment(text,n) for n in newtree.body if isinstance(n,ast.FunctionDef)}
oldtext=old.read_text();oldfn={n.name:ast.get_source_segment(oldtext,n) for n in ast.parse(oldtext).body if isinstance(n,ast.FunctionDef)}
reuse=json.loads((R/'data/phase526-launcher-output-design-v2/source-and-helper-pins.json').read_bytes())['reusable_output_functions']
for row in reuse:assert oldfn[row['name']]==newfn[row['name']],row['name']
print('adapter written/compile-only;20helpers exact; no imports')
