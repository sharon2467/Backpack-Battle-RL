"""Phase580 isolated captured mixed Source generation; no candidate imports or calls."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import traceback

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/phase564-source-finite-mixed'
REFERENCE=ROOT/'data/phase505-captured-nonking-source-v3/staged'
OUT=ROOT/'data/phase580-captured-mixed-source'
SPEC=ROOT/'docs/phase580_mixed_captured_candidate_implementation_spec.md'
PROFILE='pure-combat-mixed-modifiers-A-captured/1'
SCHEMA='native-v8-pure-combat-runtime-input/mixed-modifiers-1'
ABI=ROOT/'data/phase578-mixed-input-bridge-source/abi.json'

def require(ok,message):
    if not ok:raise ValueError(message)


def sha(raw):return hashlib.sha256(raw).hexdigest()


def pin(path):
    path=Path(path);info=path.lstat()
    require(path.is_file() and not path.is_symlink() and info.st_nlink==1,'ordinary single-link Source')
    raw=path.read_bytes()
    return dict(path=str(path.relative_to(ROOT)),size=len(raw),sha256=sha(raw))


def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(value,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n')


def functions(text):
    result={}
    for n in ast.parse(text).body:
        if isinstance(n,(ast.FunctionDef,ast.ClassDef)):
            result[n.name]=ast.get_source_segment(text,n)
            if isinstance(n,ast.ClassDef):
                result.update({n.name+'.'+m.name:ast.get_source_segment(text,m) for m in n.body if isinstance(m,ast.FunctionDef)})
    return result


class Edit:
    def __init__(self,text):self.before=self.text=text;self.edits=[]
    def replace(self,before,after):
        require(before!=after and self.text.count(before)==1,'unique Source anchor: '+before[:120])
        pos=self.text.index(before);self.text=self.text[:pos]+after+self.text[pos+len(before):]
        self.edits.append(dict(before=before,after=after,position=pos))
    def function(self,name,edits):
        before=functions(self.text)[name];after=before
        for old,new in edits:
            require(after.count(old)==1,'unique function anchor '+name+': '+old[:100]);after=after.replace(old,new)
        self.replace(before,after)
    def append(self,text,expected_name):
        last=ast.parse(self.text).body[-1]
        require(isinstance(last,ast.FunctionDef) and last.name==expected_name,'exact final top-level function name')
        require(not ''.join(self.text.splitlines(True)[last.end_lineno:]).strip(),'only whitespace after final function')
        anchor=ast.get_source_segment(self.text,last)
        require(self.text.count(anchor)==1,'unique complete final function body')
        self.replace(anchor,anchor+'\n\n'+text.rstrip()+'\n')
    def inverse(self):
        raw=self.text
        for row in reversed(self.edits):
            pos=row['position'];require(raw[pos:pos+len(row['after'])]==row['after'],'inverse postimage')
            raw=raw[:pos]+row['before']+raw[pos+len(row['after']):]
        require(raw==self.before,'complete inverse bytes')

def genuine_source(text,geometry_sha,tuple_pin):
    edit=Edit(text)
    edit.function('validate_profile',[("def validate_profile(data, fixture):", "def validate_profile(data, fixture):\n    if data.get('profile_id') == CAPTURED_MIXED_PROFILE:\n        validate_captured_mixed_profile(data, fixture)\n        return")])
    edit.function('validate_result_profile',[("def validate_result_profile(runtime,fixture):", "def validate_result_profile(runtime,fixture):\n    if runtime.get('profile') == CAPTURED_MIXED_PROFILE:\n        validate_captured_mixed_fixture(fixture)\n        if runtime.get('mode') != 'genuine' or runtime.get('terminal_profile') != SINGLE_KING_TERMINAL:\n            raise ValueError('captured mixed result profile/terminal')\n        return")])
    edit.function('observer_label',[("def observer_label(data):", "def observer_label(data):\n    if data.get('profile_id') == CAPTURED_MIXED_PROFILE:return 'observer7-572-zeroKing-mixed-candidate580'")])
    contract=dict(native_profile='observer7-mixed-modifiers-A-native-tape/1',native_observer_version='7-mixed-modifiers-A-572',observer_source_tuple=tuple_pin,input_ABI=pin(ABI),
        scope='Closed mixed29 conditional actual Tape/fullclock interface only; actual030 input applicability and launcher gate pending',
        timer_initial_domain='SOURCE_SUPPORTED_G02_INACTIVE_VALUES_NOT_ALL_NATIVE_FRESH_HISTORY',
        role_policy=dict(raw_timers=32,business_timers=26,inactive_timers=6,total_configs='32+5+actualitems',processing='1+totalconfigs',actual_native_counts=None),
        actual_input_bundle=None,actual_initial64_character8_receipts=None,actual_launcher_binding=None,
        input_binding_status='PENDING_EXTERNAL_ACTUAL_INPUT_ACCEPTANCE_AND_CODE_BOUND_LAUNCHER',comparison_status='NOT_EVALUATED')
    add='\n'.join(['#580 closed captured mixed interface. No native data/admission is created.',
        'CAPTURED_MIXED_PROFILE = '+repr(PROFILE),'CAPTURED_MIXED_SCHEMA = '+repr(SCHEMA),
        'CAPTURED_MIXED_GEOMETRY_SHA256 = '+repr(geometry_sha),'CAPTURED_MIXED_CONTRACT = '+repr(contract),
        'PROFILES = PROFILES | {CAPTURED_MIXED_PROFILE}', '''

def validate_captured_mixed_fixture(fixture):
    if type(fixture) is not dict or type(fixture.get('below_master')) is not bool:
        raise ValueError('captured mixed requires explicit actual belowMaster BOOL')
    neutral = dict(fixture, below_master=None)
    if canonical_sha(neutral) != CAPTURED_MIXED_GEOMETRY_SHA256:
        raise ValueError('captured mixed exact29 geometry/order/class0/default/noKing fixture')
    return True


def validate_captured_mixed_profile(data, fixture):
    validate_captured_mixed_fixture(fixture)
    if (data.get('schema') != CAPTURED_MIXED_SCHEMA or data.get('profile_id') != CAPTURED_MIXED_PROFILE
            or data.get('mode') != 'genuine' or data.get('terminal_profile') != SINGLE_KING_TERMINAL):
        raise ValueError('captured mixed exact14 profile/terminal')
    return True
'''])
    edit.append(add,'validate_pure441_profile');edit.inverse();return edit


STATE_METHOD='''    def _validate_captured_mixed_state(self, prepared):
        if (type(prepared) is not bool or self.prepared is not prepared or not self.captured_clock_mode
                or self.king_mode or self.king_states or self.source_king_mode or self.source_pure_mode):
            raise ValueError('captured mixed actual zeroKing preparation stage')
        self._validate_pure441_constructed()
        expected = {row['instance_id']:row['item_index'] for side in self.fixture['sides'] for row in side['items']}
        if set(self.items) != set(expected):
            raise ValueError('captured mixed actual fixed identity set')
        for identity,item in self.items.items():
            if (type(item.item_index) is not int or item.item_index != expected[identity]
                    or item.instance_id != identity or item.cache_prepared is not prepared):
                raise ValueError('captured mixed actual item/descriptor/cache stage')
            self._validate_attack_effect_chance(item)
            self._validate_bowl_double_activation_chance(item)
            if not prepared and (item.double_activation_chance != 0.0 or item.double_attack_effect_chance != 0.0):
                raise ValueError('captured mixed constructor chance0 domain')
            if item.item_index == 162:
                if type(item.bowl_speed_bonus_given) is not float or _float_bits(item.bowl_speed_bonus_given) != _float_bits(0.0):
                    raise ValueError('captured mixed Bowl actual initial/prepare REAL0 ledger')
            elif item.item_index == 231:
                if type(item.definition['least_buffs']) is not int or item.definition['least_buffs'] != 3:
                    raise ValueError('captured mixed Wolper Source count INT3')
                if item.wolpertinger_buff_listener_registered is not prepared:
                    raise ValueError('captured mixed Wolper actual listener stage')
                coefficient = item.wolpertinger_stamina_regen_per_buff
                if not prepared:
                    if coefficient is not None:
                        raise ValueError('captured mixed Python constructor coefficient; not Native pre-value')
                else:
                    percent = item.definition['stamina_regen_percent']
                    base = self.characters[item.side].base_stamina_regen
                    if (type(percent) is not float or percent != 0.7 or type(base) is not float or not math.isfinite(base)
                            or type(coefficient) is not float or not math.isfinite(coefficient)
                            or _float_bits(coefficient) != _float_bits((percent * base) / 100.0)):
                        raise ValueError('captured mixed actual prepared Wolper coefficient')
            elif item.item_index == 385:
                if type(item.definition['least_buffs']) is not int or item.definition['least_buffs'] != 1:
                    raise ValueError('captured mixed Enchanted Source count INT1')
        if self.frame_driver.pass_index != 0:
            raise ValueError('captured mixed constructor/prepare may not advance actual clock')

'''


def engine_source(text):
    edit=Edit(text)
    edit.replace('from .genuine import PURE441_PROFILE, PURE441_SCHEMA, PURE441_CONTRACT, validate_pure441_profile',
        'from .genuine import PURE441_PROFILE, PURE441_SCHEMA, PURE441_CONTRACT, validate_pure441_profile\nfrom .genuine import CAPTURED_MIXED_PROFILE, CAPTURED_MIXED_SCHEMA, CAPTURED_MIXED_CONTRACT, validate_captured_mixed_profile')
    edit.function('_integration_domain',[("return _pure441_profile(data) or", "return _captured_mixed_profile(data) or _pure441_profile(data) or")])
    edit.function('validate_runtime_inputs',[("    if _source_pure_profile(data):", "    if _captured_mixed_profile(data):\n        return _validate_captured_mixed_runtime(data, fixture, runtime)\n    if _source_pure_profile(data):")])
    edit.function('build_runtime_scaffold',[("    if _source_pure_profile(dto):", "    if _captured_mixed_profile(dto):\n        return _build_pure441_scaffold(dto)\n    if _source_pure_profile(dto):")])
    edit.function('CombatEngine.__init__',[
        ("or _source_pure_profile(runtime) else None", "or _source_pure_profile(runtime) or _captured_mixed_profile(runtime) else None"),
        ("        self.random = random_source", "        if _captured_mixed_profile(runtime) and type(random_source) is not TapeRandom:\n            raise ValueError('captured mixed requires exact TapeRandom; no fallback')\n        self.random = random_source"),
        ("self.pure_combat_mode = _pure441_profile(self.runtime_inputs)", "self.captured_clock_mode = _captured_mixed_profile(self.runtime_inputs)\n        self.pure_combat_mode = _pure441_profile(self.runtime_inputs) or self.captured_clock_mode"),
        ("            self.king_states['P:12'] = dict(invuCharges=0, protectedBuffs=3.0, manaCost=4.0)", "            if not self.captured_clock_mode:\n                self.king_states['P:12'] = dict(invuCharges=0, protectedBuffs=3.0, manaCost=4.0)"),
        ("        self._connect_runtime_callbacks()", "        if self.captured_clock_mode:\n            for role, node in self.runtime_roles.items():\n                if isinstance(node, TimerRecord):\n                    if role in CAPTURED_MIXED_INACTIVE:\n                        self.timer_runtime.connect_timeout(node, lambda timer, role=role: (_ for _ in ()).throw(ValueError('inactive captured Timer timeout: ' + role)))\n                    else:\n                        self.timer_runtime.connect_timeout(node, lambda timer, role=role: self._timer_timeout(role))\n        else:\n            self._connect_runtime_callbacks()"),
        ("if self.king_mode else None\n        if self.king_mode:", "if (self.king_mode or self.captured_clock_mode) else None\n        if self.king_mode or self.captured_clock_mode:"),
        ("            self._validate_pure441_constructed()", "            if self.captured_clock_mode:self._validate_captured_mixed_state(False)\n            else:self._validate_pure441_constructed()")])
    edit.function('CombatEngine._validate_pure441_prepared',[("def _validate_pure441_prepared(self):", "def _validate_pure441_prepared(self):\n        if self.captured_clock_mode:return self._validate_captured_mixed_state(True)")])
    edit.function('CombatEngine.activate_from_checkpoint',[("if self.king_mode and not self.frame_driver.activated:", "if (self.king_mode or self.captured_clock_mode) and not self.frame_driver.activated:")])
    edit.function('CombatEngine.death',[("if self.king_mode:self.frame_driver.request_end", "if self.king_mode or self.captured_clock_mode:self.frame_driver.request_end")])
    edit.function('CombatEngine.step',[("        if self.king_mode:", "        if self.king_mode or self.captured_clock_mode:")])
    edit.function('CombatEngine.run',[("def run(self, max_seconds=120.0, delta=NATIVE_PHYSICS_DELTA):", "def run(self, max_seconds=120.0, delta=NATIVE_PHYSICS_DELTA):\n        if self.captured_clock_mode:return self._run_captured_clock(max_seconds,delta)")])
    edit.function('CombatEngine.finish',[("if self.king_mode:self._stop_timer('invu:'+side)", "if self.king_mode or self.captured_clock_mode:self._stop_timer('invu:'+side)")])
    edit.function('CombatEngine._runtime_projection',[("        if self.king_mode:", "        if self.king_mode or self.captured_clock_mode:")])
    edit.function('CombatEngine._source_noninterfering_callback',[("def _source_noninterfering_callback(self,role,mode,delta):", "def _source_noninterfering_callback(self,role,mode,delta):\n        if self.captured_clock_mode:\n            if type(mode) is not int or type(role) is not str or (role,mode) not in self.captured_noop_slots:\n                raise ValueError('unknown captured no-op callback role/mode')")])
    edit.function('CombatEngine.__init__',[("        self.processing_inputs={n['role']:n for n in self.runtime_inputs.data.get('processing_nodes',[])}", "        self.processing_inputs={n['role']:n for n in self.runtime_inputs.data.get('processing_nodes',[])}\n        self.captured_noop_slots = frozenset({('game',0),('game',1)} | {('item:'+identity,1) for identity in self.items}) if self.captured_clock_mode else frozenset()")])
    edit.function('CombatEngine.result',[
        ("        if self.king_mode:\n            if not self.frame_driver.finalized:", "        if self.king_mode or self.captured_clock_mode:\n            if not self.frame_driver.finalized:"),
        ("        if self.pure_combat_mode:\n            result['pure_combat_diagnostics']", "        if self.captured_clock_mode:\n            result['captured_terminal']=dict(post_cleanup=deepcopy(self.frame_driver.post_cleanup_snapshot),\n                                             final=deepcopy(self.frame_driver.final_snapshot),\n                                             passes=deepcopy(self.frame_driver.pass_trace))\n        if self.pure_combat_mode:\n            result['pure_combat_diagnostics']"),
        ("contract=deepcopy(PURE441_CONTRACT)", "contract=deepcopy(CAPTURED_MIXED_CONTRACT if self.captured_clock_mode else PURE441_CONTRACT)")])
    run_method=functions((REFERENCE/'native_replay_v8/engine.py').read_text())['CombatEngine._run_captured_clock'].replace('Whelp','mixed')
    # AST method segment omits its first-line class indentation only.
    run_method='    '+run_method
    anchor='    def _validate_source_pure_state(self,prepared):'
    edit.replace(anchor,STATE_METHOD+run_method+'\n\n'+anchor)
    source=(REFERENCE/'native_replay_v8/engine.py').read_text();reference=functions(source)
    role=reference['_captured_whelp_roles'].replace('whelp','mixed').replace('Whelp','mixed')
    before="len(roles) != 66 or len([role for role,kind in roles.items() if kind == 'timer']) != 32"
    require(role.count(before)==1,'exact old role-count clause')
    role=role.replace(before,"len(roles) != 32 + 5 + sum(len(side['items']) for side in fixture['sides']) or len([role for role,kind in roles.items() if kind == 'timer']) != 32")
    validator=reference['_validate_captured_whelp_runtime'].replace('whelp','mixed').replace('Whelp','mixed')
    for a,b in [('len(order) != 29','len(order) != len(ids)'),('len(rows) != 67','len(rows) != 1 + len(required)'),('len(configs)!=66','len(configs)!=len(required)')]:
        require(validator.count(a)==1,'one runtime count formula '+a);validator=validator.replace(a,b)
    predicate=reference['_captured_whelp_profile'].replace('whelp','mixed').replace('WHELP','MIXED')
    validator=validator.replace('CAPTURED_WHELP','CAPTURED_MIXED')
    add="CAPTURED_MIXED_INACTIVE = frozenset(['invu:P','invu:O'] + ['aux:'+side+':'+name for side in ('P','O') for name in ('battleRageTimer','autoRageTimer')])\n\n\n"+predicate+'\n\n\n'+role+'\n\n\n'+validator
    edit.append(add,'_build_source_pure_scaffold');edit.inverse();return edit

def method_map(text):
    classes={n.name for n in ast.parse(text).body if isinstance(n,ast.ClassDef)}
    return {name:body for name,body in functions(text).items() if name not in classes}


def main():
    require(not OUT.exists(),'unique captured Source output')
    OUT.mkdir()
    save(OUT/'generation-started.json',dict(schema='phase580-generation-started/1',attempt=1,producer=pin(Path(__file__)),spec=pin(SPEC),candidate_imports=0))
    try:
        context_paths=[BASE/'candidate-source-freeze.json',BASE/'owned-files.json',ABI,ROOT/'data/phase578-mixed-input-bridge-source/owned-files.json',
            ROOT/'data/phase572-mixed-observer-source-v2/source-tuple.json',ROOT/'data/phase575-independent-final-acceptance/review.json',
            ROOT/'data/phase577-independent-mixed-consumer-design-review/review.json',ROOT/'data/phase580-mixed-captured-candidate-plan/owned-files.json',
            REFERENCE/'native_replay_v8/engine.py',REFERENCE/'native_replay_v8/genuine.py']
        expected={str(BASE/'candidate-source-freeze.json'):'1cf6f925d5bf91ae4b587e17001d80e052932317b8bfa3671aa17e7ff2f073d5',str(ABI):'897a40ea9594be1c8adac869345646c1f6df8f9732e8663dfbd433cbff2c7eff',
            str(REFERENCE/'native_replay_v8/engine.py'):'c3a433ff3ea0336ccee5741f09306f7db6c77831242bbd4d2c92dedd0671720f',
            str(REFERENCE/'native_replay_v8/genuine.py'):'1c56c2bcf93d4099f0cefb883381cdc093ccc77cec8998b1a763e5994b1e0978'}
        for p,h in expected.items():require(pin(Path(p))['sha256']==h,'pinned preimage '+p)
        abi=json.loads(ABI.read_bytes());require(abi['runtime_schema']==SCHEMA and abi['profile']==PROFILE and abi['candidate_source'] is None,'578 frozen unbound ABI')
        manifest=json.loads((BASE/'candidate-source-freeze.json').read_bytes())['files']
        require(len(manifest)==15,'actual564 exact15 manifest')
        before={}
        for row in manifest:
            p=ROOT/row['path'];require(pin(p)=={k:row[k] for k in ('path','size','sha256')},'base564 Source drift')
            require(p==BASE/'staged'/row['relative'] and row['relative'] not in before,'actual564 unique Source root')
            before[row['relative']]=p.read_bytes()
        require(sha(before['native_replay_v8/engine.py'])=='2a29367a60d55937bfd139ad16cc4b228c3616acf28f6d37f826c15284f9feff','exact564 engine')
        fixture_path=ROOT/'data/phase572-mixed-observer-source-v2/fixed-v8-fixture.json'
        fixture=json.loads(fixture_path.read_bytes());require(fixture['below_master'] is None,'no Source BOOL inherited')
        geometry_sha=sha(json.dumps(fixture,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
        edits={'native_replay_v8/genuine.py':genuine_source(before['native_replay_v8/genuine.py'].decode(),geometry_sha,pin(ROOT/'data/phase572-mixed-observer-source-v2/source-tuple.json')),
               'native_replay_v8/engine.py':engine_source(before['native_replay_v8/engine.py'].decode())}
        payload=dict(before)
        for rel,edit in edits.items():payload[rel]=edit.text.encode()
        for rel,raw in payload.items():compile(raw,str(OUT/'staged'/rel),'exec',dont_inherit=True)
        compile(Path(__file__).read_bytes(),str(Path(__file__)),'exec',dont_inherit=True)
        allowed_engine={'validate_runtime_inputs','build_runtime_scaffold','_integration_domain','CombatEngine.__init__','CombatEngine._validate_pure441_prepared',
            'CombatEngine.activate_from_checkpoint','CombatEngine._source_noninterfering_callback','CombatEngine.step','CombatEngine.run','CombatEngine.death',
            'CombatEngine.finish','CombatEngine._runtime_projection','CombatEngine.result'}
        allowed_genuine={'validate_profile','validate_result_profile','observer_label'}
        added_engine={'_captured_mixed_profile','_captured_mixed_roles','_validate_captured_mixed_runtime','CombatEngine._validate_captured_mixed_state','CombatEngine._run_captured_clock'}
        census={}
        for rel,edit in edits.items():
            old,new=method_map(edit.before),method_map(edit.text)
            changed={n for n in old if n in new and old[n]!=new[n]};added=set(new)-set(old)
            require(not set(old)-set(new),'no removed function')
            require(changed==(allowed_engine if rel.endswith('engine.py') else allowed_genuine),'exact allowed function delta '+repr(changed))
            require(added==(added_engine if rel.endswith('engine.py') else {'validate_captured_mixed_fixture','validate_captured_mixed_profile'}),'exact new functions')
            census[rel]=dict(changed=sorted(changed),added=sorted(added),conserved=sorted(set(old)-changed))
            if rel.endswith('engine.py'):
                require(old['CombatEngine.prepare_only']==new['CombatEngine.prepare_only'],'entire prepare_only byte exact')
                for name in ('TimerRuntime','EngineFrameDriver','HeadlessKingFrameDriver'):
                    if name in functions(edit.before):require(functions(edit.before)[name]==functions(edit.text)[name],'whole driver class exact '+name)
        conserved=[rel for rel in payload if rel not in edits];require(len(conserved)==13,'13 source files unchanged')
        for rel,raw in payload.items():
            p=OUT/'staged'/rel;p.parent.mkdir(parents=True,exist_ok=True)
            with p.open('xb') as f:f.write(raw)
        after=[dict(pin(OUT/'staged'/rel),relative=rel) for rel in sorted(payload)]
        for rel in conserved:require((OUT/'staged'/rel).read_bytes()==before[rel],'13 exactfile '+rel)
        for rel,edit in edits.items():
            stem=Path(rel).stem
            save(OUT/(stem+'-inverse.json'),dict(schema='phase580-complete-source-inverse/1',before=pin(BASE/'staged'/rel),after=pin(OUT/'staged'/rel),edits=edit.edits,inverse='COMPLETE_MODULE_BYTES_EXACT'))
            with (OUT/(stem+'.patch')).open('x') as stream:stream.write(''.join(difflib.unified_diff(edit.before.splitlines(True),edit.text.splitlines(True),fromfile=str((BASE/'staged'/rel).relative_to(ROOT)),tofile=str((OUT/'staged'/rel).relative_to(ROOT)))))
        save(OUT/'source-context.json',dict(schema='phase580-source-context/1',files=[pin(p) for p in context_paths]+[pin(fixture_path),pin(SPEC),pin(Path(__file__))],input_ABI=pin(ABI),
            scope='SOURCE_ONLY_NO_ACTUAL030_INPUT_OR_NATIVE_ADMISSION',actual_input=None,actual_Native_counts=None,actual_below_master=None,
            base15=manifest,reference='505 captured wiring only;564 business remains baseline'))
        save(OUT/'conservation.json',dict(schema='phase580-source-conservation/1',changed_files=sorted(edits),conserved_files=sorted(conserved),functions=census,
            entire_prepare_only_exact=True,FrameDriver_TimerRuntime_RNG_history_modules_exact=True,other_business_functions_exact=True,
            source_generation_invocations=1,models=0,candidate_imports=0,helper_SUT_calls=0,Expected=0,Godot=0,Native=0,pool=0))
        save(OUT/'api-contract.json',dict(schema='phase580-captured-mixed-api/1',profile=PROFILE,runtime_schema=SCHEMA,input_ABI=pin(ABI),
            constructor='CombatEngine(fixture, exact TapeRandom, runtime14)',prepare='prepare_only()',activate='activate_from_checkpoint()',
            run='run(max_seconds=120.0,delta=NATIVE_PHYSICS_DELTA)',step='step(delta=NATIVE_PHYSICS_DELTA)',result='result()',
            stage_checker='_validate_captured_mixed_state(prepared)',runtime_validator='_validate_captured_mixed_runtime(data,fixture,original)',
            public_headless_changed=False,actual_input=None,context='A remains immutable/unbound; Root later supplies new Source-bound context',
            role_policy=abi['role_policy'],sixinactive='actual TimerRecords; reject timeout, preserve cleanup order',
            B1='External actual same-instance consumed cache/fields gate beforeactivate required; no prepared witness supplied here',
            status='SOURCE_ONLY_NOT_INTERFACE_TESTED_OR_NATIVE_ACCEPTED'))
        save(OUT/'compile-only.json',dict(schema='phase580-compile-only/1',discarded_compile_objects=16,source_modules=15,producer=1,candidate_imports=0,
            constructors=0,prepare=0,steps=0,helper_SUT=0,model=0,Expected=0,Native=0,Godot=0,pool=0))
        save(OUT/'candidate-source-freeze.json',dict(schema='phase580-source-freeze/1',files=after,base_freeze=pin(BASE/'candidate-source-freeze.json'),
            conserved_files=sorted(conserved),profile=PROFILE,input_ABI=pin(ABI),status='FROZEN_COMPILE_ONLY_PENDING_INDEPENDENT581_AND_ACTUAL_INPUT'))
        save(OUT/'first-generation-result.json',dict(schema='phase580-source-generation/1',status='SOURCE_FROZEN_NO_RUNTIME_EXECUTION',generation_invocations=1,
            modules=15,changed=2,conserved=13,entire_prepare_only_exact=True,candidate_imports=0,helper_SUT=0,model=0,Expected=0,Native=0,pool=0))
        owned=[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()]+[pin(p) for p in context_paths]+[pin(fixture_path),pin(SPEC),pin(Path(__file__))]
        unique={}
        for p in owned:require(p['path'] not in unique or unique[p['path']]==p,'one Source path descriptor');unique[p['path']]=p
        save(OUT/'owned-files.json',dict(schema='phase580-source-owner/1',files=list(unique.values()),status='SOURCE_ONLY_PENDING_INDEPENDENT581_NOT_ACTUAL_INPUT',no_more_writes=True))
        print(json.dumps(dict(status='SOURCE_FROZEN_NOT_RUN',owner=pin(OUT/'owned-files.json')),sort_keys=True));return 0
    except Exception as error:
        save(OUT/'first-generation-error.json',dict(schema='phase580-source-first-error/1',error_type=type(error).__name__,message=str(error),traceback=traceback.format_exc(),automatic_retry=False,candidate_imports=0,helper_SUT=0,model=0,Expected=0,Native=0,pool=0))
        save(OUT/'partial-source-owner.json',dict(schema='phase580-partial-source-owner/1',files=[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()]+[pin(SPEC),pin(Path(__file__))],status='FIRST_SOURCE_ERROR_PRESERVED_NO_RETRY'))
        raise

if __name__=='__main__':raise SystemExit(main())
