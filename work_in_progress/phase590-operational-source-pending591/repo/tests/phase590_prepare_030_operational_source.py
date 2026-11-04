"""Phase590 isolated030 operational Source generation. No operational imports/calls."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import stat
import traceback
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/phase590-case030-host-restore-source'
OBS=ROOT/'data/phase572-mixed-observer-source-v2'
SPEC=ROOT/'docs/phase587_mixed030_host_restore_source_adaptation_spec.md'
NEW_HOST=ROOT/'tests/phase590_oracle_host.py'
NEW_STORAGE=ROOT/'tests/phase590_oracle_storage.py'
NEW_RESTORE=ROOT/'tests/phase590_restore_predecessor.py'
NEW_READER=ROOT/'tests/phase590_independent_predecessor_readback.py'
CASE='NATIVE-030-MIXED-MODIFIERS-A'
RUN='original030-mixed-modifiers-A-single-001'

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

OBSERVER_VALIDATOR='''def validate_observer_review(value,receipt,source_tuple):
    if (type(value) is not dict or receipt!=OBSERVER_REVIEW or source_tuple!=OBSERVER_TUPLE
            or value.get('schema')!='phase575-independent-final-acceptance/1'
            or value.get('status')!='ACCEPTED_SOURCE_AND_FINITE_SYNTHETIC_SCHEMA_ONLY'):
        raise ValueError('exact575 Source-only receipt and tuple binding required')
    source=value.get('Source');zero=value.get('zero_calls')
    if type(source) is not dict or type(zero) is not dict:
        raise ValueError('575 required actual Source/zero_calls fields')
    for key,expected in (('owner',OBSERVER_OWNER),('schema',OBSERVER_SCHEMA),('actual_install_targets',79),('actual_install_source_bytes',817389),('fixed_aliases',29),('descriptor_ids',12),('King_count',0)):
        if key not in source or type(source[key]) is not type(expected) or source[key]!=expected:
            raise ValueError('575 actual Source field: '+key)
    for key in ('Native','model','Expected','full_binding_join','actual_capture_inputs'):
        if key not in zero or type(zero[key]) is not int or zero[key]!=0:
            raise ValueError('575 Source-only exact integer zero: '+key)'''


def host_source(meta,tuple_value):
    e=Edit(ROOT/'tests/phase508_oracle_host.py')
    e.replace('from phase508_oracle_storage import','from phase590_oracle_storage import')
    for name,value in dict(SOURCE=str(OUT.relative_to(ROOT)),OBSERVER_SOURCE=str(OBS.relative_to(ROOT)),CASE=CASE,RUN_NAME=RUN,
        OBSERVER_FREEZE=meta['freeze'],OBSERVER_OWNER=meta['owner'],OBSERVER_REVIEW=meta['review'],OBSERVER_REVIEW_OWNER=meta['review_owner'],
        CASE_INPUTS=meta['cases'],SOURCE_AUTHORITY=meta['authority'],ABSOLUTE_SOURCE_PINS=meta['absolute'],
        OBSERVER_VERSION=tuple_value['observer_version'],OBSERVER_PROFILE=tuple_value['profile']).items():e.constant(name,value)
    # Future host review schema/status remain the exact587 design contract, never an actual approval.
    e.constant('HOST_REVIEW_SCHEMA','phase587-independent-host-restore-source-review/1')
    first=funcs(e.text)['descriptor'];e.replace(first,'OBSERVER_TUPLE = '+repr(meta['tuple'])+'\nOBSERVER_SCHEMA = '+repr(tuple_value['schema_module'])+'\n\n\n'+first)
    e.replace(funcs(e.text)['validate_observer_review'],OBSERVER_VALIDATOR)
    e.function('source_gate',[("'phase508-root-oracle-acceptance/1'","'phase590-root-oracle-acceptance/1'"),("'phase508-host-derived-source-freeze/1'","'phase590-host-derived-source-freeze/1'"),
        ("'WHELP-FAMILY-A-502'","'MIXED-MODIFIERS-A-572'"),("{'observer503','host_source'}","{'observer575','host_source'}"),("role=='observer503'","role=='observer575'")])
    e.function('plan',[("global_seed=50201,util_seed=50202","global_seed=57101,util_seed=57102"),("'phase508-oracle-readonly-plan/1'","'phase590-oracle-readonly-plan/1'"),("'FIXED_29_ITEM_ZERO_KING_WHELP_ORACLE_ONLY'","'FIXED_29_ITEM_ZERO_KING_MIXED_ORACLE_ONLY'")])
    e.function('execute',[("patch_version='phase508-oracle-zeroKing-whelp'","patch_version='phase590-oracle-zeroKing-mixed'"),("'phase508-oracle-host/1'","'phase590-oracle-host/1'"),("first original029 failed/partial","first original030 failed/partial")])
    old=funcs(e.text)['validate_active_source_tuple'];new=old
    for a,b in [("'phase508-host-derived-source-freeze/1'","'phase590-host-derived-source-freeze/1'"),("'phase502-zero-king-observer-source-tuple/1'","'phase572-zero-king-mixed-observer-source-tuple/1'"),("'phase502-native-patch-source/1'","'phase572-native-patch-source/1'"),("'WHELP-FAMILY-A-502'","'MIXED-MODIFIERS-A-572'"),("global_seed=50201,util_seed=50202","global_seed=57101,util_seed=57102"),("'phase502-source-authority/1'","'phase572-source-authority/1'")]:
        require(a in new,'tuple exact old literal '+a);new=new.replace(a,b)
    start=new.index("    keys={'schema'");end=new.index('    if (type(value)',start)
    new=new[:start]+'    keys=set('+repr(tuple(tuple_value.keys()))+')\n'+new[end:]
    a="            or value['case']!=CASE):"
    b="""            or value['case']!=CASE or value['operational_authority'] is not False
            or value['status']!='SOURCE_ONLY_NOT_OPERATIONAL'
            or value['actual_Native_UID_cut_cache_clock_setup']!='UNOBSERVED' or value['actual_Native_below_master'] is not None
            or type(value['global_seed']) is not int or value['global_seed']!=57101
            or type(value['util_seed']) is not int or value['util_seed']!=57102
            or value['proposed_run']!=RUN_NAME
            or type(value['project_install_count']) is not int or value['project_install_count']!=79
            or type(value['project_install_source_bytes']) is not int or value['project_install_source_bytes']!=817389
            or value['transparent_callsite_labels']!=['double_activation','least_buff']):"""
    require(new.count(a)==1,'tuple flag boundary');new=new.replace(a,b)
    a="'producer','sink','collector','schema_module','direct_primitive_wrapper'):";b="'producer','sink','collector','schema_module','direct_primitive_wrapper','default_p1_rule','source_case_draft'):"
    require(new.count(a)==1,'tuple required source leaves');new=new.replace(a,b)
    a="profile=OBSERVER_PROFILE,observer_version=OBSERVER_VERSION,terminal_policy=TERMINAL_POLICY):"
    b="profile=OBSERVER_PROFILE,observer_version=OBSERVER_VERSION,terminal_policy=TERMINAL_POLICY,status='SOURCE_ONLY_NOT_OPERATIONAL'):"
    require(new.count(a)==1,'patch closed sourceonly status');new=new.replace(a,b)
    start=new.index("    if (set(roles)");end=new.index("    if plan.get('config')",start)
    new=new[:start]+'''    if (set(roles)!={side+':'+str(n) for side,count in (('P',23),('O',6)) for n in range(count)}
            or set(roles.values())!={1,5,11,14,22,32,162,164,231,233,234,385}
            or roles.get('P:12')!=162 or roles.get('P:13')!=231 or roles.get('P:14')!=164
            or roles.get('P:15')!=32 or roles.get('P:19')!=385 or roles.get('O:4')!=231):
        raise ValueError('fixed29 aliases/twelve descriptors/zeroKing')
''' +new[end:]
    a="{authority['origin'][key]['path']:authority['origin'][key] for key in ('squirrel','sapphire')}!=ABSOLUTE_SOURCE_PINS"
    b="{row['path']:row for row in authority['origin'].values() if Path(row['path']).is_absolute()}!=ABSOLUTE_SOURCE_PINS"
    require(new.count(a)==1,'actual sourceauthority five absolute descriptors');new=new.replace(a,b)
    e.replace(old,new);return e


def restore_source(freeze_pin,storage_pin):
    e=Edit(ROOT/'tests/phase508_restore_predecessor.py')
    e.constant('RUN',"NATIVE / 'runs/"+RUN+"'",True);e.constant('CASE',CASE);e.constant('FREEZE',freeze_pin)
    sources=next(ast.literal_eval(n.value) for n in ast.parse(e.text).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SOURCES' for t in n.targets))
    sources['storage']=storage_pin;e.constant('SOURCES',sources)
    e.function('load_modules',[("'_phase508_restore_'","'_phase590_restore_'")])
    e.function('validate_request',[("'phase508-fixed-predecessor-restore-request/1'","'phase590-fixed-predecessor-restore-request/1'"),("closed case029 restore request","closed case030 restore request"),("exact508 host Source freeze","exact590 host Source freeze")])
    e.function('prepare',[("==814020","==817389")])
    e.function('main',[("'phase508-restore-'","'phase590-restore-'"),("'phase508-fixed-predecessor-restore-result/1'","'phase590-fixed-predecessor-restore-result/1'"),("'phase508-restore-output-owner/1'","'phase590-restore-output-owner/1'")])
    return e


def reader_source(freeze_pin):
    e=Edit(ROOT/'tests/phase508_independent_predecessor_readback.py')
    e.constant('CASE',CASE);e.constant('RUN',RUN);e.constant('FREEZE',freeze_pin)
    e.function('readback',[("'phase508-fixed-predecessor-readback-request/1'","'phase590-fixed-predecessor-readback-request/1'"),("fixed case029 roots","fixed case030 roots"),("== 814020","== 817389")])
    e.function('main',[("'phase508-readback-'","'phase590-readback-'"),("'phase508-independent-readback-result/1'","'phase590-independent-readback-result/1'"),("'_phase508_frozen_compaction'","'_phase590_frozen_compaction'"),("'phase508-readback-output-owner/1'","'phase590-readback-output-owner/1'")])
    return e

def main():
    require(not OUT.exists(),'unique new030 Source directory')
    for path in (NEW_HOST,NEW_STORAGE,NEW_RESTORE,NEW_READER):require(not path.exists(),'new isolated Source paths')
    OUT.mkdir()
    save(OUT/'generation-started.json',dict(schema='phase590-source-generation-started/1',producer=pin(Path(__file__)),spec=pin(SPEC),operational_imports=0,attempt=1))
    try:
        plan=json.loads((ROOT/'data/phase587-mixed030-host-restore-plan/source-preimages.json').read_bytes())
        for name in ('host','storage','restore','reader'):
            row=plan['files'][name];require(pin(ROOT/row['path'])==row,'exact508 preimage '+name)
        release=ROOT/'data/phase590-root-operational-Source-release/release.json'
        require(pin(release)['sha256']=='3e84eeb9bc57ac2bd8858daa64e55670f4f50491f7a680de8f7daec8bc2bcada','actual Root Source-only release')
        observer=json.loads((OBS/'combined-source-freeze.json').read_bytes());authority=json.loads((OBS/'source-authority.json').read_bytes());value=json.loads((OBS/'source-tuple.json').read_bytes())
        absolute={row['path']:row for row in authority['origin'].values() if Path(row['path']).is_absolute()}
        require(len(absolute)==5 and absolute==plan['absolute_source_authority_pins'],'exact five frozen absolute origins, metadata only')
        meta=dict(freeze=pin(OBS/'combined-source-freeze.json'),owner=pin(OBS/'source-owner.json'),tuple=pin(OBS/'source-tuple.json'),
            review=pin(ROOT/'data/phase575-independent-final-acceptance/review.json'),review_owner=pin(ROOT/'data/phase575-independent-final-acceptance/owned-files.json'),
            authority=pin(OBS/'source-authority.json'),absolute=absolute,
            cases={name:pin(OBS/'case-inputs'/name) for name in ('custom_player.json','custom_opponent.json','native_capture_config.json')})
        for key,h in [('tuple','7134099050c0847030bdf824f986cf95ab9258f222a866a898f57099610cf086'),('review','526d09b0de3948ff8932d7064dc6ef934c6674cfb89d8a6621f203c056edd3a7')]:require(meta[key]['sha256']==h,'pinned current sourceidentity '+key)
        storage=Edit(ROOT/'tests/phase508_oracle_storage.py');storage.constant('MAX_INSTALL_BYTES',817389)
        host=host_source(meta,value)
        # Each generated module is compiled once, only by finish; never import/call it.
        reports={};reports['storage']=storage.finish(NEW_STORAGE);reports['host']=host.finish(NEW_HOST)
        require(not reports['storage']['changed_functions'] and not reports['storage']['new_functions'],'all23 storage bodies exact')
        closure=[NEW_HOST,NEW_STORAGE,ROOT/'tests/phase363_oracle_process.py',ROOT/'tests/phase363_oracle_storage.py',ROOT/'tests/native_run_compaction.py',ROOT/'tests/godotsteam_offline_exec.py']
        for row in plan['inherited_driver_closure']:require(pin(ROOT/row['path'])==row,'unchanged inherited processclosure')
        common=[pin(p) for p in closure]+[pin(SPEC),pin(Path(__file__)),pin(release),meta['owner'],meta['freeze'],meta['review'],meta['review_owner'],meta['authority']]
        declared={row['path']:row for row in observer['files']}
        for row in common:
            require(row['path'] not in declared or declared[row['path']]==row,'graph descriptor conflict');declared[row['path']]=row
        for row in declared.values():
            if Path(row['path']).is_absolute():require(absolute.get(row['path'])==row,'only fixed absolute graph references; no author opens')
            else:require(pin(ROOT/row['path'])==row,'repo Source graph drift')
        paths=observer['paths'];artifacts=observer['artifacts']
        targets=list(paths)+list(artifacts)
        require(len(paths)==76 and len(artifacts)==3 and len(set(targets))==79 and sum(row['after']['size'] for row in paths.values())+sum(row['size'] for row in artifacts.values())==817389,'actual distinct79/817389 Source corpus')
        freeze={key:observer[key] for key in ('paths','artifacts','collector','schema_module','active_source_tuple','profile','observer_version','terminal_policy')}
        freeze.update(schema='phase590-host-derived-source-freeze/1',files=list(declared.values()),observer_source_freeze=meta['freeze'],observer_source_owner=meta['owner'],
            native_source_origin=meta['authority'],schema_case='MIXED-MODIFIERS-A-572',case_inputs=meta['cases'],host=pin(NEW_HOST),storage=pin(NEW_STORAGE),run_name=RUN,
            accepted_source_controls=[],historical_source_controls=[],project_install_count=79,project_install_source_bytes=817389,
            status='SOURCE_ONLY_PENDING_INDEPENDENT_REVIEW_ROOT_CONFIG_FRESH_READY_CAPACITY_NO_EXECUTE_RELEASE')
        save(OUT/'combined-source-freeze.json',freeze);freeze_pin=pin(OUT/'combined-source-freeze.json')
        host_owner=dict(declared);host_owner[freeze_pin['path']]=freeze_pin
        save(OUT/'source-owner.json',dict(schema='phase590-host-source-owner/1',files=list(host_owner.values()),no_more_writes=True,status='SOURCE_ONLY_NO_OPERATIONAL_AUTHORITY',absolute_origin_physical_checks_by_author=0))
        restore=restore_source(freeze_pin,pin(NEW_STORAGE));reader=reader_source(freeze_pin)
        reports['restore']=restore.finish(NEW_RESTORE);reports['reader']=reader.finish(NEW_READER)
        allowed={'host':{'validate_observer_review','source_gate','plan','execute','validate_active_source_tuple'},'storage':set(),
                 'restore':{'load_modules','validate_request','prepare','main'},'reader':{'readback','main'}}
        for name,report in reports.items():
            require(set(report['changed_functions'])==allowed[name] and report['new_functions']==[],'only intended Source function delta '+name+': '+repr(report['changed_functions']))
        for name in ('select_restore_images','action','apply','restore','no_process','finish_metadata','recheck_target'):
            require(name in reports['restore']['exact_functions'],'restore physical/selection kernel exact '+name)
        for name in ('descriptor','verify_owner','resource_gate','backup_predecessor_controls','collect_capture_metadata','read_control','_payload_rows','resolve_execute_payloads','verify_execute_payloads','execute_driver_descriptors','load_terminal_schema','read_terminal_expected_controls','main'):
            require(name in reports['host']['exact_functions'],'host nonbinding kernel exact '+name)
        save(OUT/'conservation.json',dict(schema='phase590-source-conservation/1',modules={k:dict(before=v['before'],after=v['after'],changed_functions=v['changed_functions'],new_functions=v['new_functions'],exact_functions=v['exact_functions']) for k,v in reports.items()},
            all23_storage_functions_exact=True,storage_constant_only=dict(MAX_INSTALL_PAYLOADS=79,MAX_INSTALL_BYTES=817389),
            inherited_driver_files_exact=[pin(p) for p in closure[2:]],complete_inverse=True,selector_O_union_N_and_fixture_restore_exact=True,
            no_previous_or_state_backfill=True,actual_previous=None,operational_calls=0))
        context_files=[SPEC,Path(__file__),release,ROOT/'data/phase587-mixed030-host-restore-plan/owned-files.json',ROOT/'data/phase589-independent-host-design-review/review.json']
        save(OUT/'source-context.json',dict(schema='phase590-source-context/1',files=[pin(p) for p in context_files],base_preimages={k:v['before'] for k,v in reports.items()},
            absolute_origin_pins_metadata_only=absolute,absolute_origin_physical_checks=0,current_pool_state=None,current_previous=None,current_resources=None,current_space=None,
            relocation='Explicit existing ABSOLUTE-REFERENCE-MAP only; never absolute fallback, missing-source bypass or None success',
            freeze_order='host/storage derivedfreeze then restore/readback, totalowner last; no selfhash cycle'))
        save(OUT/'api-contract.json',dict(schema='phase590-source-API/1',host=pin(NEW_HOST),storage=pin(NEW_STORAGE),restore=pin(NEW_RESTORE),reader=pin(NEW_READER),
            pure_interfaces=['validate_observer_review(value,receipt,source_tuple)','validate_active_source_tuple(root,freeze)','resolve_execute_payloads(source_root,freeze,driver_descriptors=())','verify_execute_payloads(source_root,graph)','select_restore_images(old,baseline,old_targets,old_images,journal,journal_images,expected_after)'],
            host_review_schema='phase587-independent-host-restore-source-review/1',host_review_status='ACCEPTED_SOURCE_ONLY_PENDING_ROOT_EXECUTE',
            host_review_fields=['schema/status exact','source_freeze actual','observer_source_owner exact','native/models strictINT0'],host_review_receipt=None,
            actual_config=None,Native_ready=False,operation_permissions=dict(models=0,inputbuild=0,Expected_comparison=0),
            controls_forbidden=['plan','execute','lease','prepare','restore','readback','actualpool/resource/space/baseline'],
            restore_request_schema='phase590-fixed-predecessor-restore-request/1',restore_evidence_count=12,restore_output_prefix='phase590-restore-',
            readback_request_schema='phase590-fixed-predecessor-readback-request/1',readback_evidence_count=8,readback_output_prefix='phase590-readback-',
            retained_control_decoding='Existing six terminal/control metadata leaves only; business Expected remains opaque; no zero-all-Expecteddecode claim'))
        save(OUT/'root-config-source-template.json',dict(schema='phase590-root-oracle-acceptance/1',host=pin(NEW_HOST),source_freeze=freeze_pin,source_owner=pin(OUT/'source-owner.json'),
            observer_source_freeze=meta['freeze'],observer_source_owner=meta['owner'],active_source_tuple=observer['active_source_tuple'],
            reviews=dict(observer575=dict(receipt=meta['review'],owner=meta['review_owner']),host_source=dict(receipt=None,owner=None)),resources=[],relocations={},
            write_policy='bounded-writers-and-monitored-process/1',restore_policy='restore-predecessor-after-independent-readback-root-commit/1',root_oracle_authorized=False,models_allowed=0,input_builds_allowed=0,expected_comparison_allowed=0))
        restore_evidence=('controls_manifest','patch_inventory','install_journal','pool_before','previous_bundle_manifest','previous_proof','previous_provenance','previous_project','previous_baseline','previous_staged','previous_host_manifest','pending_state')
        save(OUT/'restore-request-template.json',dict(schema='phase590-fixed-predecessor-restore-request/1',case_id=CASE,previous_run=None,writer=pin(NEW_RESTORE),source_freeze=freeze_pin,evidence={k:None for k in restore_evidence},root_restore_authorized=False))
        save(OUT/'readback-request-template.json',dict(schema='phase590-fixed-predecessor-readback-request/1',case_id=CASE,run=None,pool=None,baseline=None,previous_run=None,relocations={},host_source_freeze=freeze_pin,evidence={k:None for k in ('restore_receipt','restore_owner','controls_manifest','patch_inventory','install_journal','previous_proof','previous_bundle_manifest','pending_state')}))
        save(OUT/'compile-only.json',dict(schema='phase590-compile-only/1',unique_modules=4,discarded_compile_objects=4,operational_imports=0,helpers=0,plan=0,lease=0,restore=0,readback=0,Native=0,models=0,Expected=0,pool=0,baseline=0))
        save(OUT/'first-generation-result.json',dict(schema='phase590-first-generation/1',status='SOURCE_ONLY_COMPILED_PENDING_INDEPENDENT_ROOT_NO_NATIVE_AUTHORITY',source_generation_invocations=1,modules=4,
            project_targets=79,project_bytes=817389,case_inputs=3,actual_predecessor=None,actual_backups=None,operational_config_runnable=False,restore_request_runnable=False,readback_request_runnable=False,operational_calls=0))
        generated=[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()]+[pin(p) for p in (NEW_HOST,NEW_STORAGE,NEW_RESTORE,NEW_READER)]+[pin(p) for p in context_files]
        combined={row['path']:row for row in host_owner.values()}
        for row in generated:
            require(row['path'] not in combined or combined[row['path']]==row,'one complete Source owner descriptor');combined[row['path']]=row
        save(OUT/'owned-files.json',dict(schema='phase590-total-source-owner/1',files=list(combined.values()),no_more_writes=True,status='SOURCE_ONLY_PENDING_INDEPENDENT_REVIEW_NOT_EXECUTION_AUTHORITY'))
        print(json.dumps(dict(status='SOURCE_FROZEN_NO_OPERATIONAL_EXECUTION',owner=pin(OUT/'owned-files.json')),sort_keys=True));return 0
    except Exception as error:
        save(OUT/'first-generation-error.json',dict(schema='phase590-source-first-error/1',error_type=type(error).__name__,message=str(error),traceback=traceback.format_exc(),automatic_retry=False,operational_imports=0,helpers=0,Native=0,models=0,Expected=0,pool=0))
        partial=[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()]+[pin(p) for p in (NEW_HOST,NEW_STORAGE,NEW_RESTORE,NEW_READER) if p.exists()]+[pin(SPEC),pin(Path(__file__))]
        save(OUT/'partial-source-owner.json',dict(schema='phase590-partial-source-owner/1',files=partial,status='SOURCE_FIRST_ERROR_PRESERVED_NO_RETRY'))
        raise

if __name__=='__main__':raise SystemExit(main())
