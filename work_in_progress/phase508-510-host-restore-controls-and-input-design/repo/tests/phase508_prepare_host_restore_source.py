"""Isolated case029 SOURCE assembly. Never imports or runs generated operational code."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import stat
import traceback

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/phase508-case029-host-restore-source'
SPEC=ROOT/'docs/phase508_case029_host_restore_source_implementation_spec.md'
OBS=ROOT/'data/phase502-whelp-observer-source-v4'
NEW_HOST=ROOT/'tests/phase508_oracle_host.py'
NEW_STORAGE=ROOT/'tests/phase508_oracle_storage.py'
NEW_RESTORE=ROOT/'tests/phase508_restore_predecessor.py'
NEW_READER=ROOT/'tests/phase508_independent_predecessor_readback.py'
CASE='NATIVE-029-WHELP-FAMILY-A'
RUN='original029-whelp-family-A-single-001'


def require(ok,message):
    if not ok:raise ValueError(message)


def pin(path):
    path=Path(path);require(path.is_relative_to(ROOT),'author may hash repo Source only')
    info=path.lstat();require(stat.S_ISREG(info.st_mode) and info.st_nlink==1 and not path.is_symlink(),'ordinary Source')
    raw=path.read_bytes();return dict(path=str(path.relative_to(ROOT)),size=len(raw),sha256=hashlib.sha256(raw).hexdigest())


def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as stream:json.dump(value,stream,sort_keys=True,indent=2,allow_nan=False);stream.write('\n')


def funcs(text):return {n.name:ast.get_source_segment(text,n) for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}


class Edit:
    def __init__(self,path):self.path=path;self.before=self.text=path.read_text();self.edits=[]
    def replace(self,a,b):
        require(a!=b and self.text.count(a)==1,'unique Source anchor '+a[:100])
        pos=self.text.index(a);self.text=self.text[:pos]+b+self.text[pos+len(a):]
        self.edits.append(dict(before=a,after=b,position=pos))
    def constant(self,name,value,expression=False):
        ns=[n for n in ast.parse(self.text).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets)]
        require(len(ns)==1,'one Source constant '+name)
        self.replace('\n'+ast.get_source_segment(self.text,ns[0])+'\n','\n'+name+' = '+(value if expression else repr(value))+'\n')
    def function(self,name,edits):
        a=funcs(self.text)[name];b=a
        for old,new in edits:
            require(b.count(old)==1,'one function anchor '+name+': '+old[:100]);b=b.replace(old,new)
        self.replace(a,b)
    def new_function_before(self,anchor,new):
        a=funcs(self.text)[anchor];self.replace(a,new.rstrip()+'\n\n\n'+a)
    def finish(self,path):
        compile(self.text,str(path),'exec',dont_inherit=True)
        inverse=self.text
        for row in reversed(self.edits):
            pos=row['position'];require(inverse[pos:pos+len(row['after'])]==row['after'],'inverse postimage')
            inverse=inverse[:pos]+row['before']+inverse[pos+len(row['after']):]
        require(inverse==self.before,'whole Source inverse')
        a,b=funcs(self.before),funcs(self.text)
        require(set(a)<=set(b),'no deleted operational functions')
        with path.open('x') as stream:stream.write(self.text)
        report=dict(before=pin(self.path),after=pin(path),edits=self.edits,inverse_complete=True,
                    changed_functions=sorted(n for n in a if a[n]!=b[n]),new_functions=sorted(set(b)-set(a)),
                    exact_functions=sorted(n for n in a if a[n]==b[n]))
        save(OUT/'inverse'/(path.stem+'.json'),report)
        (OUT/'inverse'/(path.stem+'.patch')).write_text(''.join(difflib.unified_diff(self.before.splitlines(True),self.text.splitlines(True),fromfile=str(self.path.relative_to(ROOT)),tofile=str(path.relative_to(ROOT)))))
        return report


TUPLE_VALIDATOR = '''def validate_active_source_tuple(root, freeze):
    if (freeze.get('schema') != 'phase508-host-derived-source-freeze/1'
            or freeze.get('observer_source_freeze') != OBSERVER_FREEZE or freeze.get('observer_source_owner') != OBSERVER_OWNER):
        raise ValueError('closed508 binding to actual502 Source required')
    observer=read(check_source_descriptor(root,OBSERVER_FREEZE))
    if freeze['active_source_tuple'] != observer['active_source_tuple']:
        raise ValueError('exact502v4 tuple descriptor')
    value=read(check_source_descriptor(root,freeze['active_source_tuple']))
    keys={'schema','profile','observer_version','case','terminal_policy','fixed_fixture','fixed_plan','native_patch',
          'producer','sink','collector','schema_module','direct_primitive_wrapper','model_input_or_runtime_admitted','host_execution_ready'}
    if (type(value) is not dict or set(value)!=keys or value['schema']!='phase502-zero-king-observer-source-tuple/1'
            or value['model_input_or_runtime_admitted'] is not False or value['host_execution_ready'] is not False
            or value['case']!=CASE):
        raise ValueError('closed502 zeroKing tuple and historical false flags')
    if (value['profile'],value['observer_version'],value['terminal_policy']) != (OBSERVER_PROFILE,OBSERVER_VERSION,TERMINAL_POLICY):
        raise ValueError('exact502 profile/version/terminal')
    if (freeze['profile'],freeze['observer_version'],freeze['terminal_policy'],freeze['run_name']) != (OBSERVER_PROFILE,OBSERVER_VERSION,TERMINAL_POLICY,RUN_NAME):
        raise ValueError('host case/run/profile mismatch')
    declared=_payload_rows(freeze['files'])
    for key in ('fixed_fixture','fixed_plan','native_patch','producer','sink','collector','schema_module','direct_primitive_wrapper'):
        row=value[key]
        if declared.get(row['path'])!=row:raise ValueError('tuple leaf outside frozen graph')
        check_source_descriptor(root,row)
    for key in ('paths','artifacts','collector','schema_module','active_source_tuple','profile','observer_version','terminal_policy'):
        if key not in observer or freeze.get(key)!=observer[key]:raise ValueError('missing or mixed actual502 key '+key)
    if value['collector']!=freeze['collector'] or value['schema_module']!=freeze['schema_module']:
        raise ValueError('collector/schema tuple mismatch')
    for key,target in (('sink','native_random_observer_sink_v7.gd'),('direct_primitive_wrapper','Items/Exclusive/Squirrel.gd')):
        row=freeze['paths'][target]
        if value[key]!=dict(path=row['after_path'],**row['after']):raise ValueError('direct source-to-target mismatch')
    patch=read(check_source_descriptor(root,value['native_patch']))
    if patch != dict(schema='phase502-native-patch-source/1',paths=freeze['paths'],producer=value['producer'],sink=value['sink'],
                     profile=OBSERVER_PROFILE,observer_version=OBSERVER_VERSION,terminal_policy=TERMINAL_POLICY):
        raise ValueError('actual76 patch declaration mismatch')
    plan=read(check_source_descriptor(root,value['fixed_plan']))
    fixture=read(check_source_descriptor(root,value['fixed_fixture']))
    if (plan.get('fixture')!=fixture or plan.get('profile')!=OBSERVER_PROFILE or plan.get('version')!=OBSERVER_VERSION
            or plan.get('source_case')!='WHELP-FAMILY-A-502' or plan.get('native_case')!=CASE
            or len(plan.get('slots',[]))!=29 or fixture.get('below_master','MISSING') is not None):
        raise ValueError('exact proposed29 geometry; actual native branch not prefilled')
    roles={row['instance_id']:row['item_index'] for row in plan['slots']}
    if (set(roles)!={side+':'+str(n) for side,count in (('P',16),('O',13)) for n in range(count)}
            or set(roles.values())!={1,11,22,23,64,164,197,199,201} or 262 in roles.values()
            or roles.get('P:9')!=23 or roles.get('P:10')!=164 or roles.get('P:14')!=199):
        raise ValueError('fixed29 aliases/nine descriptors/zeroKing')
    if plan.get('config') != dict(schema='native-combat-capture/1',case_id=CASE,global_seed=50201,util_seed=50202,
                                 player_fixture_enabled=True,timeouts=dict(battle_seconds=120,total_seconds=295)):
        raise ValueError('Root preselected exact new seeds/config')
    if freeze.get('schema_case')!=plan['source_case'] or freeze.get('native_source_origin')!=SOURCE_AUTHORITY:
        raise ValueError('derived actual case/sourceauthority binding')
    if declared.get(SOURCE_AUTHORITY['path'])!=SOURCE_AUTHORITY:raise ValueError('sourceauthority outside graph')
    authority=read(check_source_descriptor(root,SOURCE_AUTHORITY))
    if (authority.get('schema')!='phase502-source-authority/1' or type(authority.get('origin')) is not dict
            or {authority['origin'][key]['path']:authority['origin'][key] for key in ('squirrel','sapphire')}!=ABSOLUTE_SOURCE_PINS):
        raise ValueError('exact502 two absolute sourceorigin authorities')
    return value'''


SELECT_IMAGES = '''def select_restore_images(old, baseline, old_targets, old_images, journal, journal_images, expected_after):
    """Production O union N selection from already-read backup images; no filesystem access."""
    O=set(old_targets)|{MARKER};N=set(expected_after)
    equal(set(old_images),O,'all actual old patch and marker images')
    names=[row['path'] for row in journal]
    require(len(names)==len(set(names)) and set(names)==N,'exact unique new journal target membership')
    present=set()
    for name,image in old_images.items():
        require(name in old and old[name]['kind']=='file','old desired transformed target is regular')
        check_image(image,old[name],'old desired installed source')
    for index,row in enumerate(journal):
        require(set(row)=={'path','backup','before','after'},'closed new journal row')
        name=row['path'];equal(row['after'],expected_after[name],'journal new after identity')
        intermediate=None if name==MARKER else baseline.get(name) if name in old_targets else old.get(name)
        if intermediate is None:
            require(row['before'] is None and row['backup'] is None,'actual absent reset-time preimage')
        else:
            require(intermediate['kind']=='file','unsupported reset-time directory target')
            equal(row['before'],row_record(intermediate),'actual reset-time authority')
            require(row['backup']==str(index) and name in journal_images,'exact journal image binding')
            check_image(journal_images[name],intermediate,'reset-time backup bytes',metadata=False)
            present.add(name)
    equal(set(journal_images),present,'no extra/omitted present journal images')
    selected={}
    for name in sorted(O|N):
        desired=old.get(name)
        if desired is not None:require(desired['kind']=='file','unsupported desired directory target')
        if name in O:
            selected[name]=old_images[name]
        elif desired is None:
            selected[name]=None
        else:
            require(name in journal_images,'present desired new-only image')
            check_image(journal_images[name],desired,'new-only desired predecessor image',metadata=False)
            selected[name]=journal_images[name]
    return selected'''


def host_source(meta):
    e=Edit(ROOT/'tests/phase464_oracle_host_v2.py')
    e.replace('from phase464_oracle_storage import','from phase508_oracle_storage import')
    for name,value in dict(SOURCE=str(OUT.relative_to(ROOT)),OBSERVER_SOURCE=str(OBS.relative_to(ROOT)),CASE=CASE,RUN_NAME=RUN,
            HOST_REVIEW_SCHEMA='phase509-independent-host-restore-source-review/1',HOST_REVIEW_STATUS='ACCEPTED_SOURCE_ONLY_PENDING_ROOT_EXECUTE',
            OBSERVER_FREEZE=meta['freeze'],OBSERVER_OWNER=meta['owner'],OBSERVER_REVIEW=meta['review'],OBSERVER_REVIEW_OWNER=meta['review_owner'],
            CASE_INPUTS=meta['cases'],OBSERVER_VERSION='7-whelp-family-A-502',OBSERVER_PROFILE='observer7-whelp-family-A-native-tape/1').items():e.constant(name,value)
    anchor=funcs(e.text)['descriptor']
    e.replace(anchor,'''def descriptor(source_root,row):
    if (type(row) is not dict or set(row)!={'path','size','sha256'} or type(row['path']) is not str
            or type(row['size']) is not int or row['size']<0 or type(row['sha256']) is not str or re.fullmatch('[0-9a-f]{64}',row['sha256']) is None):
        raise ValueError('exact Source descriptor')
    if Path(row['path']).is_absolute():
        if ABSOLUTE_SOURCE_PINS.get(row['path'])!=row:raise ValueError('unapproved absolute Source reference')
        origin=Path(BASELINE_SOURCE_REFERENCE)
        relative=str(Path(row['path']).relative_to(origin))
        return check_source_descriptor(origin,dict(path=relative,size=row['size'],sha256=row['sha256']))
    path=member(source_root,row['path'])
    if not path.is_file() or pin(path)!={k:row[k] for k in ('size','sha256')}:raise ValueError('actual descriptor drift')
    return path''')
    e.replace(funcs(e.text)['validate_observer_review'],'''def validate_observer_review(value,receipt,source_tuple):
    if (receipt!=OBSERVER_REVIEW or value.get('schema')!='phase503-independent-final-producer-acceptance/1'
            or value.get('status')!='ACCEPTED_SOURCE_AND_12_SYNTHETIC_SCHEMA_CONTROLS_NOT_NATIVE_VALIDATION'
            or value.get('accepted_source_owner')!=OBSERVER_OWNER or value.get('accepted_source_tuple')!=source_tuple):
        raise ValueError('actual503 Source-only acceptance for exact502v4 required')''')
    e.function('source_gate',[
        ("'phase464-root-oracle-acceptance/1'","'phase508-root-oracle-acceptance/1'"),
        ("'phase464-host-derived-source-freeze/1'","'phase508-host-derived-source-freeze/1'"),
        ("for key in ('paths','artifacts','collector','schema_module','active_source_tuple','native_source_origin',\n                'profile','observer_version','terminal_policy','schema_case'):\n        if freeze.get(key)!=observer_freeze.get(key): raise ValueError('observer/host freeze binding differs: '+key)",
         "for key in ('paths','artifacts','collector','schema_module','active_source_tuple','profile','observer_version','terminal_policy'):\n        if key not in observer_freeze or freeze.get(key)!=observer_freeze[key]: raise ValueError('missing/mixed observer binding: '+key)\n    if freeze.get('native_source_origin')!=SOURCE_AUTHORITY or freeze.get('schema_case')!='WHELP-FAMILY-A-502':\n        raise ValueError('derived actual sourceauthority and fixedplan case required')"),
        ("set(reviews)!={'observer463','host_source'}","set(reviews)!={'observer503','host_source'}"),
        ("if role=='observer463':","if role=='observer503':")])
    e.function('plan',[("global_seed=45701,util_seed=45702","global_seed=50201,util_seed=50202"),("'phase464-oracle-readonly-plan/1'","'phase508-oracle-readonly-plan/1'"),("'FIXED_26_ITEM_KING_BASIC_ORACLE_ONLY'","'FIXED_29_ITEM_ZERO_KING_WHELP_ORACLE_ONLY'")])
    e.function('resolve_execute_payloads',[("len(freeze['paths'])!=75","len(freeze['paths'])!=76"),("exact75 SOURCE patches","exact76 SOURCE patches")])
    e.function('verify_execute_payloads',[("len(graph['patches'])!=75","len(graph['patches'])!=76"),("exact75 execute patch descriptors","exact76 execute patch descriptors"),("for row in unique.values(): check_source_descriptor(root,row)","for row in unique.values():\n        if Path(row['path']).is_absolute():descriptor(root,row)\n        else:check_source_descriptor(root,row)")])
    e.replace(funcs(e.text)['validate_active_source_tuple'],TUPLE_VALIDATOR)
    e.function('load_terminal_schema',[("'_phase464_terminal_schema_'","'_phase508_terminal_schema_'")])
    e.function('execute',[("patch_version='phase464-oracle-King-basic'","patch_version='phase508-oracle-zeroKing-whelp'"),("'phase464-oracle-host/1'","'phase508-oracle-host/1'"),("first original028 failed/partial","first original029 failed/partial")])
    # New declarations are metadata-only and do not alter inherited algorithm bodies.
    e.replace("LAWFUL = (",'SOURCE_AUTHORITY = '+repr(meta['authority'])+'\nBASELINE_SOURCE_REFERENCE = '+repr(meta['origin_root'])+'\nABSOLUTE_SOURCE_PINS = '+repr(meta['absolute'])+'\nLAWFUL = (')
    return e


def restore_source(freeze_pin,storage_pin):
    e=Edit(ROOT/'tests/phase469_restore_fixed_predecessor_v2.py')
    e.constant('RUN',"NATIVE / 'runs/"+RUN+"'",True);e.constant('CASE',CASE)
    e.constant('PREVIOUS',None);e.constant('BUNDLE',None);e.constant('EVIDENCE_PATHS',{})
    e.constant('FREEZE',freeze_pin)
    old_sources=next(ast.literal_eval(n.value) for n in ast.parse(e.text).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SOURCES' for t in n.targets))
    old_sources['storage']=storage_pin;e.constant('SOURCES',old_sources)
    e.function('load_modules',[("'_phase469_'","'_phase508_restore_'")])
    e.replace(funcs(e.text)['validate_request'],'''def validate_request(request):
    global PREVIOUS,BUNDLE,EVIDENCE_PATHS
    require(type(request) is dict and set(request)=={'schema','case_id','previous_run','writer','source_freeze','evidence','root_restore_authorized'},'closed case029 restore request')
    require(request['schema']=='phase508-fixed-predecessor-restore-request/1' and request['case_id']==CASE
            and request['root_restore_authorized'] is True,'explicit new Root restoration authorization')
    previous=path_of(request['previous_run'])
    require(previous.is_absolute() and previous.parent==RUN.parent and previous!=RUN,'fixed runs root and distinct actual predecessor')
    require(PREVIOUS is None or PREVIOUS==previous,'one fixed predecessor binding per invocation')
    PREVIOUS=previous;BUNDLE=PREVIOUS/'output/compaction'
    EVIDENCE_PATHS={'controls_manifest':CONTROLS/'manifest.json','patch_inventory':PATCH/'inventory.json',
        'install_journal':JOURNAL/'preimages.json','pool_before':RUN/'output/pool-before.json',
        'previous_bundle_manifest':BUNDLE/'bundle-manifest.json','previous_proof':BUNDLE/'pool-roundtrip.json',
        'previous_provenance':PREVIOUS/'output/pool-provenance.json','previous_project':BUNDLE/'project-files.json',
        'previous_baseline':BUNDLE/'baseline-files.json','previous_staged':BUNDLE/'staged-inputs.json',
        'previous_host_manifest':PREVIOUS/'output/host_manifest.json','pending_state':POOL/'state.json'}
    require(path_of(request['writer']['path'])==Path(__file__).absolute(),'exact new writer path')
    descriptor(request['writer']);equal(request['source_freeze'],FREEZE,'exact508 host Source freeze')
    freeze=decoded(descriptor(FREEZE))
    require(type(request['evidence']) is dict and set(request['evidence'])==set(EVIDENCE_PATHS),'fixed evidence keys')
    for key,path in EVIDENCE_PATHS.items():require(path_of(request['evidence'][key]['path'])==path,'fixed actual evidence path '+key)
    return freeze''')
    original=funcs(e.text)['prepare'];prefix=original[:original.index("    require(len(report['patches']) == 75")]
    prefix=prefix.replace('    sources = {}','    old_images = {}').replace('        sources[name] = image','        old_images[name] = image').replace("    sources[MARKER] = stable(PATCH / 'marker')","    old_images[MARKER] = stable(PATCH / 'marker')").replace("    check_image(sources[MARKER]", "    check_image(old_images[MARKER]")
    # Preserve old backup verification loop without its stale fixed count.
    middle=original[original.index('    sources = {}'):original.index('    expected_after = ')]
    middle=middle.replace('sources','old_images')
    # prefix ended immediately before the stale count, so it has not yet included this loop.
    new=prefix+middle+'''    expected_after={name:row['after'] for name,row in freeze['paths'].items()}
    expected_after.update({name:{key:row[key] for key in ('size','sha256')} for name,row in freeze['artifacts'].items()})
    require(len(expected_after)==79 and sum(row['size'] for row in expected_after.values())==814020,'exact new79 install corpus')
    journal=evidence['install_journal']
    equal([row['path'] for row in journal],list(freeze['paths'])+['native_combat_capture.gd','native_capture_config.json',MARKER],'exact actual79 journal order')
    journal_images={}
    for index,row in enumerate(journal):
        if row.get('before') is not None:
            require(row.get('backup')==str(index),'exact numeric before backup')
            journal_images[row['path']]=stable(JOURNAL/row['backup'])
    sources=select_restore_images(old,bidx,old_targets,old_images,journal,journal_images,expected_after)
    before=evidence['pool_before']
    current_project=c.inventory(POOL/'project');equal(current_project,before['project'],'current live project equals sealed post-install graph')
    current_staged=c.inventory(POOL/'data');equal(current_staged,before['staged'],'current live staged equals sealed post-install graph')
    current,current_data=c.index(current_project),c.index(current_staged)
    O=set(old_targets)|{MARKER};N=set(expected_after);U=set(sources)
    old_dirs={name for name,row in old.items() if row['kind']=='directory'}
    current_dirs={name for name,row in current.items() if row['kind']=='directory'}
    equal(current_dirs,old_dirs,'unsupported directory topology change')
    expected_paths=set(old)-O
    for name in O:
        reset=None if name==MARKER else bidx.get(name)
        if reset is not None:
            require(reset['kind']=='file','unsupported old target reset kind');expected_paths.add(name)
    expected_paths.update(N)
    equal(set(current),expected_paths,'exact reset/install path-set authority')
    for name,row in current.items():
        if name in old:equal(row['kind'],old[name]['kind'],'unchanged existing node kind')
        if row['kind']=='file' and name not in U:equal(row,old[name],'untouched project file')
    for name in U:
        if name in N:
            require(name in current and current[name]['kind']=='file','current installed target regular')
            equal({key:current[name][key] for key in ('size','sha256')},expected_after[name],'live installed new source')
        else:
            reset=None if name==MARKER else bidx.get(name)
            if reset is None:require(name not in current,'O-only reset target absent')
            else:equal(current.get(name),reset,'O-only live reset baseline authority')
    actions=[action(s.member(POOL/'project',name),sources[name],current.get(name),old.get(name)) for name in sorted(U)]
    fixtures={'custom_player.json','custom_opponent.json'}
    require(set(current_data)-{'.'}<=fixtures and set(staged)-{'.'}<=fixtures,'only fixed staged fixtures')
    for name in sorted(fixtures):
        image=controls['data/'+name];desired=staged.get(name)
        require((image is None)==(desired is None),'fixture presence equals old staged authority')
        if image is not None:check_image(image,desired,'old fixture control')
        actions.append(action(s.member(POOL/'data',name),image,current_data.get(name),desired))
    dirs=[(s.member(POOL/'project',name) if name!='.' else POOL/'project',row) for name,row in old.items() if row['kind']=='directory']
    dirs.append((POOL/'data',staged['.']))
    for path,row in dirs:
        s.directory(path);require(not os.listxattr(path,follow_symlinks=False),'unsupported directory xattrs')
    for row in actions:
        if row['operation']=='replace':
            temporary=row['target'].with_name(row['target'].name+'.phase363-next')
            require(not temporary.exists() and not temporary.is_symlink(),'unfinished atomic image before writes')
    for key,row in request['evidence'].items():equal(descriptor(row),raw[key],'critical descriptor unchanged before writes')
    result['validated_sources']={'old_patch':len(old_targets),'old_marker':1,'new_journal':len(journal),'controls':3,
        'project_union':len(U),'current_project_entries':len(current),'old_project_directories':len(old_dirs)}
    result['pending_state']=request['evidence']['pending_state']
    return actions,dirs,stable(POOL/'state.json')'''
    e.replace(original,new)
    e.new_function_before('prepare',SELECT_IMAGES)
    e.function('main',[("out.name.startswith('phase469-')","out.name.startswith('phase508-restore-')"),
        ("'phase469-fixed-predecessor-restore-result/1'","'phase508-fixed-predecessor-restore-result/1'"),
        ("'previous_run': str(PREVIOUS)","'previous_run': None"),
        ("        freeze = validate_request(request)","        freeze = validate_request(request)\n        result['previous_run']=str(PREVIOUS)"),
        ("'phase469-restore-output-owner/1'","'phase508-restore-output-owner/1'")])
    return e


def reader_source(freeze_pin):
    e=Edit(ROOT/'tests/phase468_independent_predecessor_readback_v2.py')
    e.constant('CASE',CASE);e.constant('RUN',RUN);e.constant('FREEZE',freeze_pin)
    e.function('readback',[("'phase468-fixed-predecessor-readback-request/1'","'phase508-fixed-predecessor-readback-request/1'"),
        ("require(run.name == RUN and run != previous, 'fixed current run and distinct predecessor')",
         "require(run == Path('/workspace/native-combat-20261013/runs')/RUN and pool == Path('/workspace/native-combat-20261013/pool')\n            and previous.parent == run.parent and run != previous, 'fixed case029 roots and actual distinct predecessor')"),
        ("len(expected_after) == 78","len(expected_after) == 79"),("== 812880","== 814020"),
        ("'fixed78 install corpus'","'fixed79 install corpus'"),("'new78 source journal order/targets'","'new79 source journal order/targets'"),
        ("'new_journal': 78","'new_journal': len(journal)")])
    e.function('main',[("out.name.startswith('phase468-')","out.name.startswith('phase508-readback-')"),
        ("'phase468-independent-readback-result/1'","'phase508-independent-readback-result/1'"),
        ("'_phase468_frozen_compaction'","'_phase508_frozen_compaction'"),
        ("'phase468-readback-output-owner/1'","'phase508-readback-output-owner/1'")])
    return e


def main():
    require(not OUT.exists(),'unique508 Source directory required')
    for path in (NEW_HOST,NEW_STORAGE,NEW_RESTORE,NEW_READER):require(not path.exists(),'new isolated Source paths')
    OUT.mkdir()
    save(OUT/'generation-started.json',dict(schema='phase508-source-generation-started/1',producer=pin(Path(__file__)),spec=pin(SPEC),operational_imports=0))
    try:
        observer=json.loads((OBS/'combined-source-freeze.json').read_bytes())
        authority=json.loads((OBS/'source-authority.json').read_bytes())
        absolute={authority['origin'][k]['path']:authority['origin'][k] for k in ('squirrel','sapphire')}
        require(len(absolute)==2 and all(Path(p).is_absolute() for p in absolute),'exact two frozen origin references')
        origin_roots={str(Path(p).parents[2]) for p in absolute}
        require(len(origin_roots)==1,'same exact sourceorigin root')
        review=ROOT/'data/phase503-independent-final-acceptance/review.json'
        meta=dict(freeze=pin(OBS/'combined-source-freeze.json'),owner=pin(OBS/'source-owner.json'),review=pin(review),
            review_owner=pin(ROOT/'data/phase503-independent-final-acceptance/owned-files.json'),
            authority=pin(OBS/'source-authority.json'),absolute=absolute,origin_root=next(iter(origin_roots)),
            cases={name:pin(OBS/'case-inputs'/name) for name in ('custom_player.json','custom_opponent.json','native_capture_config.json')})
        require(pin(OBS/'source-tuple.json')['sha256']=='026877626166fe632c08bd3cba28aec191561373b2167f3c6d15d1f1fac86658','exact accepted tuple')
        require(meta['review']['sha256']=='468ec5cb36e2d11f0a1a7e8160eca4d806b5fe10bb92ce90ccf2733ea1cd3db4','exact actual503')
        storage=Edit(ROOT/'tests/phase464_oracle_storage.py')
        storage.constant('MAX_INSTALL_PAYLOADS',79);storage.constant('MAX_INSTALL_BYTES',814020)
        host=host_source(meta)
        # Check all complete Source workbuffers before writing any operational module.
        compile(storage.text,str(NEW_STORAGE),'exec',dont_inherit=True);compile(host.text,str(NEW_HOST),'exec',dont_inherit=True)
        reports={}
        reports['storage']=storage.finish(NEW_STORAGE);reports['host']=host.finish(NEW_HOST)
        require(not reports['storage']['changed_functions'] and not reports['storage']['new_functions'],'storage all function bodies exact')
        closure=[NEW_HOST,NEW_STORAGE,ROOT/'tests/phase363_oracle_process.py',ROOT/'tests/phase363_oracle_storage.py',
                 ROOT/'tests/native_run_compaction.py',ROOT/'tests/godotsteam_offline_exec.py']
        common=[pin(p) for p in closure]+[pin(SPEC),pin(Path(__file__)),meta['owner'],meta['freeze'],meta['review'],meta['review_owner'],meta['authority']]
        # Source graph metadata copied exactly; absolute origin leaves deliberately NOT opened by author.
        declared={row['path']:row for row in observer['files']}
        for row in common:
            require(row['path'] not in declared or declared[row['path']]==row,'graph descriptor conflict')
            declared[row['path']]=row
        for row in declared.values():
            if Path(row['path']).is_absolute():require(absolute.get(row['path'])==row,'no arbitrary absolute Source graph leaf')
            else:require(pin(ROOT/row['path'])==row,'repo Source graph drift')
        paths=observer['paths'];artifacts=observer['artifacts']
        require(len(paths)==76 and len(artifacts)==3 and sum(row['after']['size'] for row in paths.values())+sum(row['size'] for row in artifacts.values())==814020,'actual79/814020 Source corpus')
        freeze={key:observer[key] for key in ('paths','artifacts','collector','schema_module','active_source_tuple','profile','observer_version','terminal_policy')}
        freeze.update(schema='phase508-host-derived-source-freeze/1',files=list(declared.values()),observer_source_freeze=meta['freeze'],
            observer_source_owner=meta['owner'],native_source_origin=meta['authority'],schema_case='WHELP-FAMILY-A-502',
            case_inputs=meta['cases'],host=pin(NEW_HOST),storage=pin(NEW_STORAGE),run_name=RUN,
            accepted_source_controls=[],historical_source_controls=[],project_install_count=79,project_install_source_bytes=814020,
            status='SOURCE_ONLY_PENDING509_ROOT_CONFIG_ACTUAL_CAPACITY_READY_NO_EXECUTE_RELEASE')
        save(OUT/'combined-source-freeze.json',freeze);freeze_pin=pin(OUT/'combined-source-freeze.json')
        host_owner_rows=dict(declared);host_owner_rows[freeze_pin['path']]=freeze_pin
        save(OUT/'source-owner.json',dict(schema='phase508-host-source-owner/1',files=list(host_owner_rows.values()),no_more_writes=True,
            status='SOURCE_ONLY_NO_EXECUTE_AUTHORIZATION',absolute_origin_physical_checks_by_author=0))
        restore=restore_source(freeze_pin,pin(NEW_STORAGE));reader=reader_source(freeze_pin)
        compile(restore.text,str(NEW_RESTORE),'exec',dont_inherit=True);compile(reader.text,str(NEW_READER),'exec',dont_inherit=True)
        reports['restore']=restore.finish(NEW_RESTORE);reports['reader']=reader.finish(NEW_READER)
        for name in ('no_process','action','public_action','recheck_target','finish_metadata','apply','restore'):
            require(name in reports['restore']['exact_functions'],'restore kernel drift '+name)
        for name in ('resource_gate','backup_predecessor_controls','collect_capture_metadata','read_control','_payload_rows','execute_driver_descriptors','read_terminal_expected_controls'):
            require(name in reports['host']['exact_functions'],'host shared kernel drift '+name)
        save(OUT/'conservation.json',dict(schema='phase508-source-conservation/1',modules={k:dict(before=v['before'],after=v['after'],changed_functions=v['changed_functions'],new_functions=v['new_functions'],exact_functions=v['exact_functions']) for k,v in reports.items()},
            storage_function_bodies_all_exact=True,storage_constant_only=dict(files=79,bytes=814020),
            process_compaction_offline_363storage_exact=[pin(p) for p in closure[2:]],complete_inverse=True,
            unknown_directory_topology_rejected=True,old_install_restore_hardcounts_not_authority=True))
        source_context=[SPEC,Path(__file__),ROOT/'data/phase507-host-restore-design/owned-files.json',ROOT/'data/phase507-independent-design-review/review.json',
            ROOT/'data/phase506-independent-final-acceptance/review.json',ROOT/'tests/phase464_oracle_host_v2.py',ROOT/'tests/phase464_oracle_storage.py',
            ROOT/'tests/phase469_restore_fixed_predecessor_v2.py',ROOT/'tests/phase468_independent_predecessor_readback_v2.py']
        save(OUT/'source-context.json',dict(schema='phase508-source-context/1',files=[pin(p) for p in source_context],
            actual_previous_run=None,actual_pool_state=None,actual_space=None,actual_source_before=None,
            absolute_origin_pins_metadata_only=absolute,absolute_origin_physical_checks=0,
            relocation_policy='Explicit ABSOLUTE-REFERENCE-MAP required on remote restoration; never missing-path fallback or None success.'))
        save(OUT/'api-contract.json',dict(schema='phase508-source-API/1',host_source=pin(NEW_HOST),storage_source=pin(NEW_STORAGE),restore_source=pin(NEW_RESTORE),reader_source=pin(NEW_READER),
            pure_source_bindings=['validate_observer_review(value,receipt,source_tuple)','validate_active_source_tuple(root,freeze) [repo Source descriptors only, no lease/pool]','verify_execute_payloads(source_root,graph) [exact allowed Source references, no lease/pool]'],
            pure_restore_selection='select_restore_images(old,baseline,old_targets,old_images,journal,journal_images,expected_after) -> O union N desired source images/None; production prepare calls this helper',
            control_limit='Independent509 presealed <=12 only after Root gate; author zero calls',
            forbidden_during_Source_controls=['plan','execute','lease','prepare','restore','readback','realpool/resource/space probes'],
            host_review_schema='phase509-independent-host-restore-source-review/1',host_review_status='ACCEPTED_SOURCE_ONLY_PENDING_ROOT_EXECUTE',
            host_review_required_fields=['schema','status','source_freeze','observer_source_owner','native INT0','models INT0'],
            Root_review_binding='Future actual independent review receipt and owner descriptors in a separate authorized Root config; no prefilled review SHA or selfhash cycle.',
            restore_previous='strict request previous_run under fixed runs root, then actual pending/controls/savedstate proof equality',
            actual_root_config=None,actual_host_review=None,Native_ready=False,actual_INPUT_model_comparison_permissions=dict(inputbuild=0,models=0,Expected=0)))
        save(OUT/'root-config-source-template.json',dict(schema='phase508-root-oracle-acceptance/1',host=pin(NEW_HOST),source_freeze=freeze_pin,
            source_owner=pin(OUT/'source-owner.json'),observer_source_freeze=meta['freeze'],observer_source_owner=meta['owner'],active_source_tuple=observer['active_source_tuple'],
            reviews=dict(observer503=dict(receipt=meta['review'],owner=meta['review_owner']),host_source=dict(receipt=None,owner=None)),
            resources=[],relocations={},write_policy='bounded-writers-and-monitored-process/1',restore_policy='restore-predecessor-after-independent-readback-root-commit/1',
            root_oracle_authorized=False,models_allowed=0,input_builds_allowed=0,expected_comparison_allowed=0))
        save(OUT/'compile-only.json',dict(schema='phase508-compile-only/1',unique_operational_modules=4,discarded_operational_compile_objects=8,
            complete_producer_buffer_compiled_separately=True,operational_imports=0,helpers=0,plan=0,models=0,Native=0,Godot=0,Expected=0,pool=0,baseline=0,cleanup=0))
        save(OUT/'first-generation-result.json',dict(schema='phase508-first-source-generation/1',status='SOURCE_GENERATED_COMPILED_PENDING_ROOT_AND509',source_generation_invocations=1,
            modules=4,install_targets=79,install_bytes=814020,current_pool_or_resources_observed=False,
            actual_predecessor=None,actual_restore_union=None,actual_root_authorization=False,operational_imports=0,helpers=0,plan=0,models=0,Native=0,Expected=0,pool=0))
        files=[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()]+[pin(p) for p in (NEW_HOST,NEW_STORAGE,NEW_RESTORE,NEW_READER)]+[pin(p) for p in source_context]
        bypath={row['path']:row for row in files}
        save(OUT/'owned-files.json',dict(schema='phase508-all-source-owner/1',files=list(bypath.values()),no_more_writes=True,
            status='SOURCE_ONLY_PENDING_ROOT_REVIEW_NO_AUTOMATIC509_OR_EXECUTE'))
        print(json.dumps(dict(status='SOURCE_FROZEN_NO_OPERATIONAL_EXECUTION',owner=pin(OUT/'owned-files.json')),sort_keys=True))
    except Exception as error:
        save(OUT/'first-generation-error.json',dict(error_type=type(error).__name__,message=str(error),traceback=traceback.format_exc(),automatic_retry=False,
            operational_imports=0,helpers=0,plan=0,models=0,Native=0,Expected=0,pool=0,baseline=0))
        raise


if __name__=='__main__':main()
