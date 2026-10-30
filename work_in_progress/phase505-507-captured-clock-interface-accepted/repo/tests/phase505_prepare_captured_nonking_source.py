"""Prepare isolated phase505 Python SOURCE only; never import the candidate."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import traceback

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'data/phase497-source-three-whelps/staged'
OUT = ROOT/'data/phase505-captured-nonking-source'
SPEC = ROOT/'docs/phase505_captured_nonking_source_implementation_spec.md'
OLD_CAPTURED = ROOT/'data/phase476-joint-condition-repair/staged/native_replay_v8/engine.py'
PROFILE = 'pure-combat-whelp-family-A-captured/1'
SCHEMA = 'native-v8-pure-combat-runtime-input/whelp-family-1'


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
    def append(self,text):
        self.replace(self.text[-200:],self.text[-200:]+'\n\n'+text.rstrip()+'\n')
    def inverse(self):
        raw=self.text
        for row in reversed(self.edits):
            pos=row['position'];require(raw[pos:pos+len(row['after'])]==row['after'],'inverse postimage')
            raw=raw[:pos]+row['before']+raw[pos+len(row['after']):]
        require(raw==self.before,'complete inverse bytes')


def genuine_source(text,geometry_sha,tuple_pin):
    edit=Edit(text)
    edit.function('validate_profile',[("def validate_profile(data, fixture):", "def validate_profile(data, fixture):\n    if data.get('profile_id') == CAPTURED_WHELP_PROFILE:\n        validate_captured_whelp_profile(data, fixture)\n        return")])
    edit.function('validate_result_profile',[("def validate_result_profile(runtime,fixture):", "def validate_result_profile(runtime,fixture):\n    if runtime.get('profile') == CAPTURED_WHELP_PROFILE:\n        validate_captured_whelp_fixture(fixture)\n        if runtime.get('mode') != 'genuine' or runtime.get('terminal_profile') != SINGLE_KING_TERMINAL:\n            raise ValueError('captured Whelp result profile/terminal')\n        return")])
    edit.function('observer_label',[("def observer_label(data):", "def observer_label(data):\n    if data.get('profile_id') == CAPTURED_WHELP_PROFILE:return 'observer7-502-zeroKing-whelp-candidate505'")])
    contract=dict(native_profile='observer7-whelp-family-A-native-tape/1',native_observer_version='7-whelp-family-A-502',
        observer_source_tuple=tuple_pin,scope='Fixed29 zeroKing conditional actual Tape/fullclock; code interface only until independent actual INPUT and launcher gate.',
        timer_initial_domain='SOURCE_SUPPORTED_G02_INACTIVE_VALUES_NOT_ALL_NATIVE_FRESH_HISTORY',raw_timers=32,business_timers=26,inactive_timers=6,
        actual_input_bundle=None,actual_initial64_character8_receipts=None,actual_launcher_binding=None,
        input_binding_status='PENDING_EXTERNAL_ACTUAL_INPUT_ACCEPTANCE_AND_CODE_BOUND_LAUNCHER',comparison_status='NOT_EVALUATED')
    add="\n".join(["#505 finite captured nonKing interface. No Native input/admission is created here.",
        'CAPTURED_WHELP_PROFILE = '+repr(PROFILE),'CAPTURED_WHELP_SCHEMA = '+repr(SCHEMA),
        'CAPTURED_WHELP_GEOMETRY_SHA256 = '+repr(geometry_sha),'CAPTURED_WHELP_CONTRACT = '+repr(contract),
        'PROFILES = PROFILES | {CAPTURED_WHELP_PROFILE}', '''

def validate_captured_whelp_fixture(fixture):
    if type(fixture) is not dict or type(fixture.get('below_master')) is not bool:
        raise ValueError('captured Whelp requires explicit actual belowMaster BOOL')
    neutral = dict(fixture, below_master=None)
    if canonical_sha(neutral) != CAPTURED_WHELP_GEOMETRY_SHA256:
        raise ValueError('captured Whelp exact29 geometry/order/class0/default/noKing fixture')
    return True


def validate_captured_whelp_profile(data, fixture):
    validate_captured_whelp_fixture(fixture)
    if (data.get('schema') != CAPTURED_WHELP_SCHEMA or data.get('profile_id') != CAPTURED_WHELP_PROFILE
            or data.get('mode') != 'genuine' or data.get('terminal_profile') != SINGLE_KING_TERMINAL):
        raise ValueError('captured Whelp exact14 profile/terminal')
    return True
'''])
    edit.append(add);edit.inverse();return edit


STATE_METHOD = '''    def _validate_captured_whelp_state(self, prepared):
        if (type(prepared) is not bool or self.prepared is not prepared or not self.captured_clock_mode
                or self.king_mode or self.king_states or self.source_king_mode or self.source_pure_mode):
            raise ValueError('captured Whelp actual zeroKing preparation stage')
        self._validate_pure441_constructed()
        for item in self.items.values():
            if item.cache_prepared is not prepared:
                raise ValueError('captured Whelp actual cache preparation stage')
        item = self.items['P:9']
        expected = 5.0 if prepared else 0.0
        if (type(item.definition['activations_to_trigger']) is not int or item.definition['activations_to_trigger'] != 5
                or type(item.goobert_activations) is not int or item.goobert_activations != 0
                or type(item.iteration_cooldown) is not float or type(item.trigger_time) is not float
                or _float_bits(item.iteration_cooldown) != _float_bits(expected)
                or _float_bits(item.trigger_time) != _float_bits(expected)):
            raise ValueError('captured Whelp actual Basic threshold/counter/cooldown stage')
        stack_types = self.items['P:14'].definition['random_buff_types']
        if (type(stack_types) is not tuple or any(type(i) is not int for i in stack_types)
                or stack_types != (101,102,103,104,106,107)):
            raise ValueError('captured Whelp Source Sapphire ordered six INT nonMana types')

    def _run_captured_clock(self, max_seconds, delta):
        if not self.captured_clock_mode:
            raise ValueError('finite captured Whelp clock only')
        if (type(max_seconds) not in (int,float) or not math.isfinite(max_seconds)
                or not 0 < max_seconds <= 120.0 or type(delta) is not float or delta != NATIVE_PHYSICS_DELTA):
            raise ValueError('captured Whelp finite simulated budget and sealed clock delta')
        if not self.prepared:self.prepare_only()
        if not self.activated:self.activate_from_checkpoint()
        while not self.frame_driver.finalized:
            if not self.ended and self.elapsed >= max_seconds:
                raise TimeoutError('captured Whelp simulated combat budget exhausted')
            self.step(delta)
        return self.result()
'''


def engine_source(text):
    edit=Edit(text)
    edit.replace('from .genuine import PURE441_PROFILE, PURE441_SCHEMA, PURE441_CONTRACT, validate_pure441_profile',
        'from .genuine import PURE441_PROFILE, PURE441_SCHEMA, PURE441_CONTRACT, validate_pure441_profile\nfrom .genuine import CAPTURED_WHELP_PROFILE, CAPTURED_WHELP_SCHEMA, CAPTURED_WHELP_CONTRACT, validate_captured_whelp_profile')
    edit.function('_integration_domain',[("return _pure441_profile(data) or", "return _captured_whelp_profile(data) or _pure441_profile(data) or")])
    edit.function('validate_runtime_inputs',[("    if _source_pure_profile(data):", "    if _captured_whelp_profile(data):\n        return _validate_captured_whelp_runtime(data, fixture, runtime)\n    if _source_pure_profile(data):")])
    edit.function('build_runtime_scaffold',[("    if _source_pure_profile(dto):", "    if _captured_whelp_profile(dto):\n        return _build_pure441_scaffold(dto)\n    if _source_pure_profile(dto):")])
    edit.function('CombatEngine.__init__',[
        ("or _source_pure_profile(runtime) else None", "or _source_pure_profile(runtime) or _captured_whelp_profile(runtime) else None"),
        ("        self.random = random_source", "        if _captured_whelp_profile(runtime) and type(random_source) is not TapeRandom:\n            raise ValueError('captured Whelp requires exact TapeRandom; no fallback')\n        self.random = random_source"),
        ("self.pure_combat_mode = _pure441_profile(self.runtime_inputs)", "self.captured_clock_mode = _captured_whelp_profile(self.runtime_inputs)\n        self.pure_combat_mode = _pure441_profile(self.runtime_inputs) or self.captured_clock_mode"),
        ("            self.king_states['P:12'] = dict(invuCharges=0, protectedBuffs=3.0, manaCost=4.0)", "            if not self.captured_clock_mode:\n                self.king_states['P:12'] = dict(invuCharges=0, protectedBuffs=3.0, manaCost=4.0)"),
        ("        self._connect_runtime_callbacks()", "        if self.captured_clock_mode:\n            for role, node in self.runtime_roles.items():\n                if isinstance(node, TimerRecord):\n                    if role in CAPTURED_WHELP_INACTIVE:\n                        self.timer_runtime.connect_timeout(node, lambda timer, role=role: (_ for _ in ()).throw(ValueError('inactive captured Timer timeout: ' + role)))\n                    else:\n                        self.timer_runtime.connect_timeout(node, lambda timer, role=role: self._timer_timeout(role))\n        else:\n            self._connect_runtime_callbacks()"),
        ("if self.king_mode else None\n        if self.king_mode:", "if (self.king_mode or self.captured_clock_mode) else None\n        if self.king_mode or self.captured_clock_mode:"),
        ("            self._validate_pure441_constructed()", "            if self.captured_clock_mode:self._validate_captured_whelp_state(False)\n            else:self._validate_pure441_constructed()")])
    edit.function('CombatEngine._validate_pure441_prepared',[("def _validate_pure441_prepared(self):", "def _validate_pure441_prepared(self):\n        if self.captured_clock_mode:return self._validate_captured_whelp_state(True)")])
    edit.function('CombatEngine.activate_from_checkpoint',[("if self.king_mode and not self.frame_driver.activated:", "if (self.king_mode or self.captured_clock_mode) and not self.frame_driver.activated:")])
    edit.function('CombatEngine.death',[("if self.king_mode:self.frame_driver.request_end", "if self.king_mode or self.captured_clock_mode:self.frame_driver.request_end")])
    edit.function('CombatEngine.step',[("        if self.king_mode:", "        if self.king_mode or self.captured_clock_mode:")])
    edit.function('CombatEngine.run',[("def run(self, max_seconds=120.0, delta=NATIVE_PHYSICS_DELTA):", "def run(self, max_seconds=120.0, delta=NATIVE_PHYSICS_DELTA):\n        if self.captured_clock_mode:return self._run_captured_clock(max_seconds,delta)")])
    edit.function('CombatEngine.finish',[("if self.king_mode:self._stop_timer('invu:'+side)", "if self.king_mode or self.captured_clock_mode:self._stop_timer('invu:'+side)")])
    edit.function('CombatEngine._runtime_projection',[("        if self.king_mode:", "        if self.king_mode or self.captured_clock_mode:")])
    edit.function('CombatEngine._source_noninterfering_callback',[("def _source_noninterfering_callback(self,role,mode,delta):", "def _source_noninterfering_callback(self,role,mode,delta):\n        if self.captured_clock_mode:\n            if type(mode) is not int or type(role) is not str or (role,mode) not in self.captured_noop_slots:\n                raise ValueError('unknown captured no-op callback role/mode')")])
    # Exact admitted31-slot set is constructed before callback attachment; never a prefix allowlist.
    edit.function('CombatEngine.__init__',[("        self.processing_inputs={n['role']:n for n in self.runtime_inputs.data.get('processing_nodes',[])}", "        self.processing_inputs={n['role']:n for n in self.runtime_inputs.data.get('processing_nodes',[])}\n        self.captured_noop_slots = frozenset({('game',0),('game',1)} | {('item:'+identity,1) for identity in self.items}) if self.captured_clock_mode else frozenset()")])
    edit.function('CombatEngine.result',[
        ("        if self.king_mode:\n            if not self.frame_driver.finalized:", "        if self.king_mode or self.captured_clock_mode:\n            if not self.frame_driver.finalized:"),
        ("        if self.pure_combat_mode:\n            result['pure_combat_diagnostics']", "        if self.captured_clock_mode:\n            result['captured_terminal']=dict(post_cleanup=deepcopy(self.frame_driver.post_cleanup_snapshot),\n                                             final=deepcopy(self.frame_driver.final_snapshot),\n                                             passes=deepcopy(self.frame_driver.pass_trace))\n        if self.pure_combat_mode:\n            result['pure_combat_diagnostics']"),
        ("contract=deepcopy(PURE441_CONTRACT)", "contract=deepcopy(CAPTURED_WHELP_CONTRACT if self.captured_clock_mode else PURE441_CONTRACT)")])
    # Add only two new methods at an exact class method boundary.
    anchor='    def _validate_source_pure_state(self,prepared):'
    edit.replace(anchor,STATE_METHOD+'\n'+anchor)
    old=functions(OLD_CAPTURED.read_text())['_validate_joint_captured_runtime']
    new=old.replace('_validate_joint_captured_runtime','_validate_captured_whelp_runtime').replace('validate_captured_joint_profile','validate_captured_whelp_profile').replace('_joint_captured_roles','_captured_whelp_roles').replace('captured joint','captured Whelp')
    for before,after in [('len(order) != 26','len(order) != 29'),('exact26','exact29'),('len(rows) != 65','len(rows) != 67'),('processing65','processing67'),('len(configs)!=64','len(configs)!=66'),('config64','config66'),('len(timers)!=33','len(timers)!=32'),('exact33','exact32'),('pure33 timer values','raw32 timer values')]:
        require(before in new,'476 narrow validator literal: '+before);new=new.replace(before,after)
    original_owner_block = """    for side, child in (('P',7),('O',5)):
        timer,parent=table['invu:'+side],table['character:'+side]
        if timer['positions']!=parent['positions']+[child] or timer['path']!=parent['path']+'/InvulnerabilityTimer':raise ValueError('captured Whelp P7/O5 topology')
"""
    actual_owner_block = """    for side in ('P','O'):
        timer,parent=table['invu:'+side],table['character:'+side]
        if (len(timer['positions']) != len(parent['positions']) + 1 or timer['positions'][:-1] != parent['positions']
                or timer['path'] != parent['path'] + '/InvulnerabilityTimer'):
            raise ValueError('captured Whelp actual Character-owned invulnerability Timer')
"""
    require(new.count(original_owner_block) == 1, 'exact old owner topology block')
    new = new.replace(original_owner_block, actual_owner_block)
    start=new.index("    king_timer,king_parent=table['king_buff:P:6']")
    end=new.index('    if isinstance(original,RuntimeDTO)',start)
    new=new[:start]+new[end:]
    add='''#505 closed nonKing captured interface; no native facts or outcome filled here.
CAPTURED_WHELP_INACTIVE = frozenset(['invu:P','invu:O'] + ['aux:'+side+':'+name for side in ('P','O') for name in ('battleRageTimer','autoRageTimer')])


def _captured_whelp_profile(runtime):
    data = runtime.data if isinstance(runtime, RuntimeDTO) else runtime
    return type(data) is dict and data.get('profile_id') == CAPTURED_WHELP_PROFILE


def _captured_whelp_roles(fixture):
    roles = _required_roles(fixture)
    roles['game'] = 'ordinary'
    for side in ('P','O'):
        roles['invu:'+side] = 'timer'
        for name in ('battleRageTimer','autoRageTimer'):
            roles['aux:'+side+':'+name] = 'timer'
    if (len(roles) != 66 or len([role for role,kind in roles.items() if kind == 'timer']) != 32
            or _has_king(fixture) or _has_rage(fixture)):
        raise ValueError('captured Whelp raw32/26business+6inactive noKing roles')
    return roles


'''+new
    edit.append(add);edit.inverse();return edit


def main():
    require(not OUT.exists(),'unique505 output required')
    OUT.mkdir()
    save(OUT/'generation-started.json',dict(schema='phase505-source-generation-started/1',producer=pin(Path(__file__)),
        spec=pin(SPEC),native=0,models=0,generated_imports=0))
    try:
        frozen_path=ROOT/'data/phase497-source-three-whelps/candidate-source-freeze.json'
        frozen=json.loads(frozen_path.read_bytes())
        before=[];texts={}
        for row in frozen['files']:
            expected={k:row[k] for k in ('path','size','sha256')}
            require(pin(ROOT/row['path'])==expected,'exact497 Source drift')
            require((BASE/row['relative']).resolve()==(ROOT/row['path']).resolve(),'Source relative binding')
            before.append(expected);texts[row['relative']]=(ROOT/row['path']).read_text()
        require(len(texts)==15,'exact15 baseline')
        save(OUT/'source-before.json',dict(files=before,base_freeze=pin(frozen_path)))
        geometry_path=ROOT/'data/phase502-whelp-observer-source-v4/fixed-v8-fixture.json'
        geometry=json.loads(geometry_path.read_bytes())
        require(geometry['below_master'] is None,'native branch not prefilled')
        geometry_sha=sha(json.dumps(geometry,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
        tuple_path=ROOT/'data/phase502-whelp-observer-source-v4/source-tuple.json'
        engines=engine_source(texts['native_replay_v8/engine.py'])
        genuines=genuine_source(texts['native_replay_v8/genuine.py'],geometry_sha,pin(tuple_path))
        changed={'native_replay_v8/engine.py':engines,'native_replay_v8/genuine.py':genuines}
        payloads={name:(changed[name].text if name in changed else text) for name,text in texts.items()}
        # Complete buffer syntax check before any candidate payload is written/imported.
        for name,text in payloads.items():compile(text,str(OUT/'staged'/name),'exec',dont_inherit=True)
        changes={};conserved={};new_functions={}
        allowed_engine={'_integration_domain','validate_runtime_inputs','build_runtime_scaffold','CombatEngine.__init__',
            'CombatEngine._validate_pure441_prepared','CombatEngine.activate_from_checkpoint','CombatEngine.death',
            'CombatEngine.step','CombatEngine.run','CombatEngine.finish','CombatEngine._runtime_projection',
            'CombatEngine.result','CombatEngine._source_noninterfering_callback'}
        allowed_genuine={'validate_profile','validate_result_profile','observer_label'}
        for name,edit in changed.items():
            a,b=functions(edit.before),functions(edit.text)
            # Class container hashes are not separate method changes.
            methods=set(a)-{n.name for n in ast.parse(edit.before).body if isinstance(n,ast.ClassDef)}
            changed_names={n for n in methods if a[n]!=b[n]}
            require(changed_names==(allowed_engine if name.endswith('engine.py') else allowed_genuine),'exact changed method set '+repr(changed_names))
            changes[name]=sorted(changed_names);conserved[name]=sorted(n for n in methods if a[n]==b[n])
            new_functions[name]=sorted(set(b)-set(a))
            require('CombatEngine.prepare_only' not in changed_names,'prepare_only exact')
            save(OUT/'inverse'/(Path(name).stem+'.json'),dict(source_relative=name,edits=edit.edits,complete_inverse=True,
                before_sha256=sha(edit.before.encode()),after_sha256=sha(edit.text.encode())))
        for name,text in payloads.items():
            path=OUT/'staged'/name;path.parent.mkdir(parents=True,exist_ok=True)
            with path.open('x') as f:f.write(text)
        after=[dict(pin(OUT/'staged'/name),relative=name) for name in sorted(payloads)]
        conserved_files=[name for name in payloads if name not in changed]
        require(len(conserved_files)==13,'13 conserved modules')
        require(all((OUT/'staged'/name).read_bytes()==(BASE/name).read_bytes() for name in conserved_files),'13 module bytes exact')
        patch=''.join(''.join(difflib.unified_diff(texts[name].splitlines(True),payloads[name].splitlines(True),
            fromfile=str((BASE/name).relative_to(ROOT)),tofile=str((OUT/'staged'/name).relative_to(ROOT)))) for name in changed)
        with (OUT/'source.patch').open('x') as f:f.write(patch)
        save(OUT/'conservation.json',dict(schema='phase505-source-conservation/1',changed_functions=changes,
            new_functions=new_functions,conserved_functions=conserved,changed_files=sorted(changed),
            conserved_files=sorted(conserved_files),module_count=15,conserved_count=13,all_inverse_exact=True,
            explicit_wiring_only=True,prepare_only_exact=True,TimerRuntime_FrameDriver_exact=True,
            Source497_business_catalog_and_effects_exact=True,old_public_headless_exact=True))
        save(OUT/'api-contract.json',dict(schema='phase505-captured-interface-api/1',status='SOURCE_ONLY_PENDING506_AND_ACTUAL_INPUT',
            constructor='CombatEngine(fixture, exact TapeRandom, runtime14)',prepare='prepare_only()',activate='activate_from_checkpoint()',
            step='step() consumes one supplied physics/idle pass',run='run(max_seconds<=120) finite simulated combat budget; independent outer wall cap',
            result='result() requires computed barrier and exact finite exhaustion; captured_terminal+pure_combat_diagnostics',
            profile=PROFILE,runtime_schema=SCHEMA,raw_timers=32,business_timers=26,inactive_timers=6,processing_nodes=67,configs=66,
            king_mode=False,king_states={},native_UIDs=None,native_two_cuts=None,actual_initial64_character8_receipts=None,
            actual_input_bundle=None,actual_launcher_binding=None,Native_admission=False,
            external_gate='Typed explicit Source-supported initial values are not G02 certificates. Actual64+8/birth/lifetime/flags/cuts and whole lawfulINPUT/cache/branch/Tape/clock acceptance plus code-bound launcher required before actualNative model.',
            synthetic_policy='Test-owned synthetic DTOs only code interface; never labeled Original or actual capture.',
            author=dict(candidate_imports=0,controls=0,models=0,Godot=0,Expected=0,pool=0)))
        context_paths=[SPEC,Path(__file__),frozen_path,OLD_CAPTURED,
            ROOT/'data/phase504-captured-nonking-clock-design/owned-files.json',
            ROOT/'data/phase504-independent-design-review/review.json',geometry_path,tuple_path,
            ROOT/'data/phase502-whelp-observer-source-v4/source-owner.json',
            ROOT/'data/phase498-independent-final-acceptance/review.json']
        save(OUT/'source-context.json',dict(schema='phase505-source-context/1',files=[pin(p) for p in context_paths],
            source_inputs_only=True,no_actual_native_input=True,Native_execution_release=False,
            proof_boundary='All actual identity/cut and initial64+8 evidence pending; no property is inferred from Expected or Source498 outcome.'))
        save(OUT/'compile-only.json',dict(schema='phase505-compile-only/1',discarded_compile_objects=15,candidate_imports=0,
            models=0,tests=0,Godot=0,Expected=0,pool=0))
        save(OUT/'candidate-source-freeze.json',dict(schema='phase505-source-freeze/1',files=after,
            base_freeze=pin(frozen_path),conserved_files=sorted(conserved_files),profile=PROFILE,
            status='FROZEN_COMPILE_ONLY_PENDING506_NOT_NATIVE_ADMITTED'))
        save(OUT/'first-generation-result.json',dict(schema='phase505-first-source-generation/1',source_generation_invocations=1,
            status='SOURCE_GENERATED_COMPILED_PENDING_INDEPENDENT506',candidate_modules=15,changed_modules=2,conserved_modules=13,
            generated_module_imports=0,controls=0,models=0,Godot=0,Expected=0,pool=0,Native_facts_created=0))
        files=[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()]+[pin(p) for p in context_paths]+before
        bypath={}
        for row in files:
            require(row['path'] not in bypath or bypath[row['path']]==row,'conflicting owner Source identity')
            bypath[row['path']]=row
        save(OUT/'owned-files.json',dict(schema='phase505-source-owner/1',files=list(bypath.values()),no_more_writes=True,
            status='COMPILE_ONLY_SOURCE_PENDING506_AND_ACTUAL_NATIVE_INPUT'))
        print(json.dumps(dict(status='SOURCE_FROZEN_NOT_RUN',owner=pin(OUT/'owned-files.json')),sort_keys=True))
        return 0
    except Exception as error:
        save(OUT/'first-generation-error.json',dict(schema='phase505-first-source-error/1',error_type=type(error).__name__,message=str(error),
            traceback=traceback.format_exc(),automatic_retry=False,models=0,generated_module_imports=0,Godot=0,Expected=0,pool=0))
        raise


if __name__=='__main__':raise SystemExit(main())
