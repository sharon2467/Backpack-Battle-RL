"""Generate/compile/inverse/freeze395 SOURCE. Does not import recovery or reader."""
from pathlib import Path
import argparse
import ast
import copy
import difflib
import hashlib
import json
import re
import stat
import traceback

R=Path(__file__).resolve().parents[1]
D=R/'data/phase395-attempt05-recovery-source'
SD=R/'data/phase395-independent-readback-source'
HD=R/'data/phase395-source-handoff'
FAILED=Path('/workspace/native-combat-20261013/runs/original027-king-single-A-20261025-attempt05')
PREVIOUS=Path('/workspace/native-combat-20261013/runs/native-v7-026-rainbow75-N-327')
CAPSULE=Path('/workspace/checkpoints/phase385-attempt05-failure-capsule')
CONTEXT=R/'data/phase395-root-component-context/component-accepted.json'
REVIEW='INDEPENDENT396_ATTEMPT05_COMPLETE_RECOVERY_SOURCE_ACCEPTED_ROOT_PENDING'
READBACK='INDEPENDENT395_ATTEMPT05_RESTORED_POOL_EXACT_TARGET_READBACK_PASS'


def pin(p):
    i=p.lstat();assert stat.S_ISREG(i.st_mode) and i.st_nlink==1 and not any(x.is_symlink() for x in (p,*p.parents))
    h=hashlib.sha256()
    with p.open('rb') as stream:
        for block in iter(lambda:stream.read(1048576),b''):h.update(block)
    return dict(size=i.st_size,sha256=h.hexdigest())


def desc(p):return dict(path=str(p.relative_to(R)),**pin(p))

def read(p):return json.loads(p.read_text())

def save(p,v):
    with p.open('x') as stream:json.dump(v,stream,indent=2,sort_keys=True,allow_nan=False);stream.write('\n')

def write(p,t):
    with p.open('x') as stream:stream.write(t)

def functions(t):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(t).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}

def span(t,name):
    node=next(n for n in ast.parse(t).body if isinstance(n,ast.FunctionDef) and n.name==name)
    return ''.join(t.splitlines(True)[node.lineno-1:node.end_lineno])


class Delta:
    def __init__(self,p):self.path=p;self.before=p.read_text();self.text=self.before;self.edits=[]
    def edit(self,a,b,count=1):
        assert self.text.count(a)==count,(self.path,a[:100],self.text.count(a),count)
        pos=[m.start() for m in re.finditer(re.escape(a),self.text)]
        self.edits.append(dict(before=a,after=b,positions=[p+i*(len(b)-len(a)) for i,p in enumerate(pos)]))
        self.text=self.text.replace(a,b)
    def finish(self,p,expected):
        inverse=self.text
        for row in reversed(self.edits):
            for pos in reversed(row['positions']):
                assert inverse[pos:pos+len(row['after'])]==row['after']
                inverse=inverse[:pos]+row['before']+inverse[pos+len(row['after']):]
        assert inverse==self.before
        a,b=functions(self.before),functions(self.text);changed=sorted(k for k in a if a[k]!=b[k]);assert set(changed)==set(expected),(p,changed,expected)
        compile(self.text,str(p),'exec');write(p,self.text)
        save(D/(p.stem+'-inverse.json'),dict(before=desc(self.path),after=desc(p),edits=self.edits,inverse='EXACT_BYTES',changed_functions=changed,conserved_functions=sorted(set(a)-set(changed)),added_functions=sorted(set(b)-set(a))))
        write(D/(p.stem+'-source.patch'),''.join(difflib.unified_diff(self.before.splitlines(True),self.text.splitlines(True),fromfile=str(self.path.relative_to(R)),tofile=str(p.relative_to(R)))))


def generate():
    D.mkdir(exist_ok=False);SD.mkdir(exist_ok=False)
    assert pin(CONTEXT)==dict(size=1918,sha256='eb8462f1f47fc4f287d486b69498af51647afcb0f4609041db4d706c04a39aae')
    old={}
    for name in ['data/phase393-complete-restore-source-design/owned-files.json','data/phase391-terminal-source/source-owner.json','data/phase384-independent-readback-source/source-owner.json']:
        p=R/name;old[name]=desc(p)
        for row in read(p)['files']:assert desc(R/row['path'])==row;old[row['path']]=row
    for name in ['tests/phase375_prepare_attempt03_restore_map_v2.py','tests/phase375_pool_recovery_v2.py','tests/phase375_oracle_host.py','tests/phase363_oracle_storage.py','tests/phase363_oracle_process.py','tests/native_run_compaction.py']:
        old[name]=desc(R/name)
    save(D/'old-source-before.json',dict(files=list(old.values())))
    m=Delta(R/'tests/phase375_prepare_attempt03_restore_map_v2.py')
    m.edit("RECEIPT = {'size': 335, 'sha256': '355d5615d3d0ef86a79cd0ea9f7460eb9dd24bb9d7b30c07bd872f36db360e03'}",'RECEIPT = '+repr(pin(FAILED/'output/failed-pool-preservation/receipt.json')))
    m.edit("OVERLAY = dict(size=202992,sha256='6ed9cf9be0afe81938e552c2623ff141fd978b8162ef61f2e5dd18b181fdd0b9')",'OVERLAY = '+repr(pin(FAILED/'output/failed-pool-preservation/failed-project-overlay.zip')))
    m.edit('attempt03','attempt05',count=m.text.count('attempt03'))
    m.edit('attempt05-failed-pool-preservation/1','attempt05-installed-failed-pool-preservation/1')
    m.edit('phase375-attempt05-exact-restore-source-map/1','phase395-attempt05-complete-restore-source-map/1')
    m.edit('phase375-attempt05-saved-control-pins/1','phase395-attempt05-saved-control-pins/1')
    m.edit('phase375-attempt05-map-derivation/1','phase395-attempt05-map-derivation/1')
    m.edit('import native_run_compaction as c','import sys\nsys.dont_write_bytecode=True\nimport native_run_compaction as c\nfrom phase395_saved_complete_evidence import validate_complete_saved')
    m.edit("        failed,previous=roots['failed_run'],roots['previous_run'];pres=failed/'output/failed-pool-preservation'", "        completed=validate_complete_saved(roots)\n        failed,previous=roots['failed_run'],roots['previous_run'];pres=failed/'output/failed-pool-preservation'")
    m.edit("        mapping=dict(schema=", "        files=completed['files'] # Every consumed saved leaf, including all backups and actual archived drivers.\n        mapping=dict(schema=")
    m.edit("        mapping['roots']={k:str(v) for k,v in mapping['roots'].items()}", "        mapping['roots']={k:str(v) for k,v in mapping['roots'].items()}\n        mapping['complete_install']=completed['summary']")
    m.edit('checked_install_backups=checked_install,checked_previous_patch_backups=len(oldpatch),','checked_install_backups=checked_install,checked_previous_patch_backups=len(oldpatch),complete_install=completed[\'summary\'],')
    m.finish(R/'tests/phase395_prepare_attempt05_restore_map.py',['generate'])

    rec=Delta(R/'tests/phase375_pool_recovery_v2.py')
    rec.edit('from phase375_oracle_host import descriptor, verify_owner, REVIEW_STATUS, SOURCE','from phase375_oracle_host import descriptor, verify_owner\nfrom phase395_saved_complete_evidence import validate_complete_saved\n\nSOURCE = \'data/phase395-attempt05-recovery-source\'\nREVIEW_STATUS = '+repr(REVIEW))
    rec.edit('data/phase375-attempt03-recovery-source-v2/restore-map.json','data/phase395-attempt05-recovery-source/map/restore-map.json')
    rec.edit('data/phase375-attempt03-recovery-source-v2/source-input-pins.json','data/phase395-attempt05-recovery-source/map/source-input-pins.json')
    rec.edit('INDEPENDENT375_RESTORED_POOL_EXACT_TARGET_READBACK_PASS',READBACK)
    ext=(R/'tests/phase395_recovery_gate_source.py').read_text();gate=span(ext,'source_gate')
    rec.edit(span(rec.text,'source_gate'),gate)
    rec.edit('\ndef main():\n','\n'+ext.replace(gate,'',1)+'\ndef main():\n')
    rec.edit('phase375-attempt03-exact-restore-source-map/1','phase395-attempt05-complete-restore-source-map/1')
    rec.edit('attempt03-failed-pool-preservation/1','attempt05-installed-failed-pool-preservation/1')
    rec.edit("    for row in input_pins['files']: evidence_path(roots,row)", "    for row in input_pins['files']: evidence_path(roots,row)\n    completed=validate_complete_saved(roots)\n    require(input_pins.get('schema')=='phase395-attempt05-saved-control-pins/1' and input_pins['files']==completed['files'] and mapping.get('complete_install')==completed['summary'],'complete saved evidence ledger/association/counts')")
    rec.edit('complete exact78/7 differences','complete manifest-derived file/directory differences')
    rec.finish(R/'tests/phase395_pool_recovery.py',['source_gate','verify_evidence'])

    rd=Delta(R/'tests/phase384_independent_restored_readback.py')
    for a,b in [('data/phase384-independent-actual-readback-first-001','data/phase395-independent-actual-readback-first-001'),('data/phase384-independent-readback-source','data/phase395-independent-readback-source'),('docs/phase384_readback_consumer_pin_and_receipt_status_repair_spec.md','docs/phase395_complete_restore_source_implementation_addendum.md'),('tests/phase384_independent_restored_readback.py','tests/phase395_independent_restored_readback.py'),('INDEPENDENT380_RESTORED_POOL_EXACT_TARGET_READBACK_PASS',READBACK),('BLOCKED_INDEPENDENT380_RESTORED_POOL_READBACK','BLOCKED_INDEPENDENT395_RESTORED_POOL_READBACK'),('phase380-root-pool-recovery/1','phase395-root-pool-recovery/1'),('phase380-attempt04-partial-reset-map/1','phase395-attempt05-complete-restore-source-map/1'),('CAPSULE377.json','CAPSULE385.json')]:
        rd.edit(a,b,count=rd.text.count(a))
    rd.edit('Read-only physical380 partial-restored target validation.', 'Read-only physical395 complete-install restored target validation.')
    rd.edit("    path=canonical(root,row['path']);require(pin(path)=={k:row[k] for k in ('size','sha256')},'descriptor drift: '+str(path));return path", "    require(type(row) is dict and set(row) in ({'path','size','sha256'},{'root','path','size','sha256'}),'closed actual descriptor')\n    require(type(row['size']) is int and row['size']>=0 and type(row['sha256']) is str and len(row['sha256'])==64,'strict descriptor fields')\n    path=canonical(root,row['path']);info=path.lstat()\n    require(stat.S_ISREG(info.st_mode) and info.st_nlink==1,'ordinary nlink1 descriptor source')\n    require(pin(path)=={k:row[k] for k in ('size','sha256')},'descriptor drift: '+str(path));return path")
    rd.edit("    require(source['readback_status']==READBACK_STATUS,'exact380 API readback status')", "    require(source['readback_status']==READBACK_STATUS,'exact395 API readback status')\n    require(config.get('source_owner')==source['recovery_source_owner'],'actual recovery SOURCE owner binding')\n    require(config.get('terminal_component_context')==source['terminal_component_context'],'actual Root bounded component context')\n    context=read(verify_descriptor(R,source['terminal_component_context']))\n    require(context.get('status')=='ROOT_391_BOUNDED_COMPONENT_ACCEPTED_LANGUAGE_AND_NATIVE_PENDING' and context.get('restore_allowed')==0 and type(context.get('restore_allowed')) is int,'component context is not restore authority')")
    rd.edit("endswith('attempt04')", "endswith('attempt05')")
    for a,b in [('ROOT exact380 restore-only source','ROOT exact395 restore-only source'),('actual380 SOURCE accepted closure','actual395 recovery SOURCE accepted closure'),('new attempt04 partial-reset map schema','actual395 complete05 map schema'),('failed source is attempt04 partial-install, not prior attempt','failed source is completed attempt05')]:rd.edit(a,b)
    begin=rd.text.index("    saved_staged=read(roots['failed_run']")
    end=rd.text.index("    require(receipt.get('status')",begin)
    rd.edit(rd.text[begin:end],"    expected_writes=verify_complete_saved_contract(roots,contract,mapping)\n")
    rd.edit('partial restore-only actual receipt','complete restore-only actual receipt')
    begin=rd.text.index('        process_rows=[];groups=set();known=set()')
    end=rd.text.index("        for proc in Path('/proc').iterdir():",begin)
    rd.edit(rd.text[begin:end],"        process_rows=[]\n        groups,known,historical_process_controls=attempt05_process_controls(roots,contract)\n")
    begin=rd.text.index("        save(D/'task-process-scope.json'")
    end=rd.text.index("\n\n        targets=",begin)
    rd.edit(rd.text[begin:end],"        save(D/'task-process-scope.json',dict(schema='phase395-task-process-scope/1',attempt05_process_records=historical_process_controls,known_pid_group_proof_applicable=True,known_pgids=sorted(groups),known_pids=sorted(known),\n            inspected=process_rows,known_task_live=0,visible_live_Godot_Xvfb=0,whole_system_proc_complete=False,\n            restriction='Recorded historical PID/PGIDs are not starttime identities; live matching values conservatively block. Zombies are not claimed reaped; scoped visibility gaps remain explicit.'))")
    rd.edit("        require(expected_owner['schema']=='standalone-attempt04-partial-install-failure-capsule/1' and expected_owner['file_count']==173 and len(expected_owner['files'])==173,'real377 capsule manifest')", "        result['failed_capsule']=verify_capsule385(contract,expected_owner)")
    rd.edit('known_task_live=None,known_native_pid_group_record=False','known_task_live=0,known_native_pid_group_record=True')
    rd.edit('phase381-independent-physical-readback/1','phase395-independent-physical-readback/1')
    rd.edit('phase381-independent-readback-owner/1','phase395-independent-readback-owner/1')
    rd.edit("if __name__=='__main__':raise SystemExit(main())",(R/'tests/phase395_reader_complete_source.py').read_text()+"\nif __name__=='__main__':raise SystemExit(main())")
    rd.finish(R/'tests/phase395_independent_restored_readback.py',['verify_descriptor','prepare_contract','main'])
    write(SD/'readonly-process-inspector.py',(R/'data/phase384-independent-readback-source/readonly-process-inspector.py').read_text())
    write(SD/'CAPSULE385.json',(CAPSULE/'CAPSULE.json').read_text())
    for name,row in old.items():assert desc(R/name)==row
    save(D/'source-generation.json',dict(status='SOURCE_GENERATED_COMPILED_NO_SUT_IMPORT',old_source_count=len(old),map_not_yet_generated=True,recovery_imports=0,reader_imports=0,live_pool_inventory=0,models=0))
    print('Generated/compiled395 SOURCE only; saved-map generation remains separate.')


def seal():
    assert not (D/'source-owner.json').exists() and (D/'map/derivation.json').is_file()
    old=read(D/'old-source-before.json')['files']
    for row in old:assert desc(R/row['path'])==row
    mapping=read(D/'map/restore-map.json');derivation=read(D/'map/derivation.json');proof=mapping['complete_install']
    assert (proof['project_file_differences'],proof['directory_differences'],proof['staged_file_differences'],proof['expected_writer_files'],proof['checked_install_backups'],proof['checked_previous_patch_backups'])==(78,7,2,80,76,73)
    assert proof['target_payload_routes']==dict(previous_patch=73,previous_marker=1,install_preimage=4)
    for row in read(D/'map/source-input-pins.json')['files']:
        root={'failed_run':FAILED,'previous_run':PREVIOUS}[row['root']];assert pin(root/row['path'])=={k:row[k]for k in ('size','sha256')}
    imports=[R/'tests'/n for n in ['phase395_pool_recovery.py','phase395_saved_complete_evidence.py','phase375_oracle_host.py','phase363_oracle_storage.py','phase363_oracle_process.py','native_run_compaction.py']]
    own_sources=[Path(__file__),R/'docs/phase395_complete_restore_source_implementation_addendum.md']+[R/'tests'/n for n in ['phase395_prepare_attempt05_restore_map.py','phase395_recovery_gate_source.py','phase395_reader_complete_source.py','phase395_independent_restored_readback.py']]+imports
    own_sources += [SD/'readonly-process-inspector.py',SD/'CAPSULE385.json']
    files={str(p.relative_to(R)):desc(p) for p in own_sources}
    design_owner=R/'data/phase393-complete-restore-source-design/owned-files.json'
    files[str(design_owner.relative_to(R))]=desc(design_owner)
    for row in read(design_owner)['files']:
        assert desc(R/row['path'])==row;files[row['path']]=row
    for p in sorted((D/'map').iterdir()):
        if p.is_file():files[str(p.relative_to(R))]=desc(p)
    context=read(CONTEXT);files[str(CONTEXT.relative_to(R))]=desc(CONTEXT)
    for field in ['source_freeze','source_tuple','source_owner','independent_review','independent_owner']:
        row=context[field];assert desc(R/row['path'])==row;files[row['path']]=row
    for field in ['source_owner','independent_owner']:
        for row in read(R/context[field]['path'])['files']:
            assert desc(R/row['path'])==row;files[row['path']]=row
    for p in [R/'data/phase363-oracle-repair-source/source-owner.json',R/'data/phase363-independent-source-review/review.json']:
        files[str(p.relative_to(R))]=desc(p)
    capsule=read(SD/'CAPSULE385.json');cross={}
    for name,identity in capsule['files'].items():
        if name.startswith('run/'):continue
        relative=name[len('repo/'):] if name.startswith('repo/') else 'data/phase385-root-oracle-attempt05/'+name[len('root-control/'):]
        assert pin(R/relative)==identity
        cross[name]=dict(storage='source',root=str(R),path=relative,identity=identity)
        files[relative]=desc(R/relative)
    assert len(cross)==13
    dep_inventory=[]
    for p in own_sources:
        if p.suffix!='.py':continue
        tree=ast.parse(p.read_text());compile(p.read_text(),str(p),'exec')
        rows=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):rows.extend(x.name for x in node.names)
            elif isinstance(node,ast.ImportFrom) and node.module:rows.append(node.module)
        locals_=sorted({x for x in rows if (R/'tests'/(x+'.py')).is_file()})
        for x in locals_:assert 'tests/'+x+'.py' in files,('missing local import',p,x)
        dep_inventory.append(dict(path=str(p.relative_to(R)),local_imports=locals_,all_imports=sorted(set(rows))))
    save(D/'import-closure.json',dict(imports=dep_inventory,pre_import_requirement='Root must verify ordinary source descriptors before starting interpreter; runtime gate rechecks; imported operational modules not executed by author',files=[desc(p)for p in imports]))
    files[str((D/'import-closure.json').relative_to(R))]=desc(D/'import-closure.json')
    freeze=dict(schema='phase395-complete-install-recovery-SOURCE/1',files=list(files.values()),import_closure=[desc(p)for p in imports],
        recovery_module=desc(R/'tests/phase395_pool_recovery.py'),map_generator=desc(R/'tests/phase395_prepare_attempt05_restore_map.py'),
        restore_map=desc(D/'map/restore-map.json'),input_pins=desc(D/'map/source-input-pins.json'),terminal_component_context=desc(CONTEXT),
        source_design=desc(R/'docs/phase393_attempt05_complete_restore_source_design_spec.md'),complete_install=proof,actual_operations_allowed=0)
    save(D/'combined-source-freeze.json',freeze)
    api=dict(schema='phase395-recovery-api-contract/1',root_schema='phase395-root-pool-recovery/1',source_review_status=REVIEW,readback_status=READBACK,
        map_schema='phase395-attempt05-complete-restore-source-map/1',SOURCE=str(D.relative_to(R)),MAP=str((D/'map/restore-map.json').relative_to(R)),INPUT_PINS=str((D/'map/source-input-pins.json').relative_to(R)),
        functions=dict(validate_complete_saved='(roots: {failed_run,previous_run,...}) -> summary + full saved descriptor ledger; no live tree/proc reads',
            generate='(source_root,failed_run,previous_run,output) -> frozen saved-only map; new output only',
            source_gate='(source_root,config_descriptor,action) -> root,config; own396 review and true context required',
            recover='(source_root,config_descriptor,pool,baseline,failed_run,previous_run,action,output=None); actions restore or commit_ready separated',
            reader='CLI --execute --authorization/size/sha256 --restore-receipt/size/sha256 --source-owner-size/sha256; actual future receipt required'),
        source_freeze=desc(D/'combined-source-freeze.json'),terminal_context=desc(CONTEXT),source_review=None,actual_restore_authorization=None,restore_receipt=None,independent_physical_report=None,READY_authorization=None,
        reader_source_contract=str((SD/'source-contract.json').relative_to(R)),reader_source_owner=str((SD/'source-owner.json').relative_to(R)),
        operational_calls=dict(saved_map_generation=2,saved_helper_execution=2,compaction_saved_read_import=2,recovery_imports=0,recovery_calls=0,reader_imports=0,reader_calls=0,schema_calls=0,live_pool_inventory=0,proc_inspection=0,restore=0,READY=0,Godot=0,Game=0,models=0,inputbuild=0,projection=0))
    save(D/'api-contract.json',api)
    save(D/'old-source-readback.json',dict(status='PINNED_OLD_SOURCE_IDENTICAL',files=old))
    save(D/'summary.json',dict(status='SOURCE_FROZEN_INDEPENDENT396_PENDING',freeze=desc(D/'combined-source-freeze.json'),api=desc(D/'api-contract.json'),complete_install=proof,operations=api['operational_calls'],native_or_reader_acceptance=False))
    own={row['path']:row for row in files.values()}
    for p in sorted(D.rglob('*')):
        if p.is_file():own[str(p.relative_to(R))]=desc(p)
    save(D/'source-owner.json',dict(schema='phase395-recovery-source-owner/1',files=list(own.values()),scope='SOURCE and saved-only map; actual recovery/reader/READY not executed'))
    previous_contract=read(R/'data/phase384-independent-readback-source/source-contract.json')
    source_contract={k:previous_contract[k] for k in ['external_targets','previous_bundle_manifest']}
    source_contract.update(schema='phase395-independent-readback-source-contract/1',SOURCE_review_status=REVIEW,readback_status=READBACK,
        source_freeze=desc(D/'combined-source-freeze.json'),recovery_source_owner=desc(D/'source-owner.json'),restore_map=desc(D/'map/restore-map.json'),input_pins=desc(D/'map/source-input-pins.json'),source_API=desc(D/'api-contract.json'),
        terminal_component_context=desc(CONTEXT),failed_state=pin(FAILED/'output/failed-pool-preservation/failed-pool-state.json'),complete_install=proof,
        installed_source_freeze=proof['installed_source_freeze'],process_controls={name:dict(root='failed_run',path='output/'+name,**pin(FAILED/'output'/name))for name in ('parse-process-result.json','native-process-result.json')},
        process_inspector_source=desc(SD/'readonly-process-inspector.py'),process_inspector_origin=desc(R/'data/phase384-independent-readback-source/readonly-process-inspector.py'),
        failed_capsule_manifest=desc(SD/'CAPSULE385.json'),capsule_root=str(CAPSULE),capsule_archive=dict(path='failure-capsule.zip',**pin(CAPSULE/'failure-capsule.zip')),capsule_members=len(capsule['files']),capsule_non_run_members=cross,
        required_restore_receipt_status='RESTORED_EXACT_TARGET_STATE_REMAINS_FAILED_INDEPENDENT_READBACK_PENDING',
        actual_authorization='REQUIRED_FUTURE_CLI_REAL_DESCRIPTOR',actual_restore_receipt='REQUIRED_FUTURE_CLI_REAL_DESCRIPTOR',whole_system_proc_complete=False)
    save(SD/'source-contract.json',source_contract)
    save(SD/'summary.json',dict(status='READONLY_READER_SOURCE_COMPILED_NOT_IMPORTED_OR_EXECUTED',module=desc(R/'tests/phase395_independent_restored_readback.py'),contract=desc(SD/'source-contract.json'),reader_calls=0,proc_inspection=0,live_pool_inventory=0,restore=0,READY=0))
    reader_own=dict(own)
    reader_own[str((D/'source-owner.json').relative_to(R))]=desc(D/'source-owner.json')
    for p in sorted(SD.iterdir()):
        if p.is_file():reader_own[str(p.relative_to(R))]=desc(p)
    save(SD/'source-owner.json',dict(schema='phase395-readback-source-owner/1',files=list(reader_own.values()),scope='READONLY reader SOURCE only; independent396 and actual physical gate pending'))
    HD.mkdir(exist_ok=False)
    save(HD/'summary.json',dict(status='395_SOURCE_HANDOFF_INDEPENDENT396_PENDING',recovery_owner=desc(D/'source-owner.json'),reader_owner=desc(SD/'source-owner.json'),freeze=desc(D/'combined-source-freeze.json'),map=desc(D/'map/restore-map.json'),api=desc(D/'api-contract.json'),operations=api['operational_calls'],no_more_writes=True))
    complete=dict(reader_own);complete[str((SD/'source-owner.json').relative_to(R))]=desc(SD/'source-owner.json');complete[str((HD/'summary.json').relative_to(R))]=desc(HD/'summary.json')
    save(HD/'owned-files.json',dict(schema='phase395-handoff-owner/1',files=list(complete.values()),scope='Full ordinary SOURCE closure and saved-only map; no operational acceptance'))
    for row in complete.values():assert desc(R/row['path'])==row
    for row in old:assert desc(R/row['path'])==row
    print(json.dumps(dict(handoff_owner=desc(HD/'owned-files.json'),recovery_owner=desc(D/'source-owner.json'),reader_owner=desc(SD/'source-owner.json'),freeze=desc(D/'combined-source-freeze.json'),leaves=len(complete),bytes=sum(row['size']for row in complete.values()))))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('generate','seal'));args=parser.parse_args()
    try:(generate if args.action=='generate' else seal)()
    except BaseException:
        failure=next(D/('source-preparation-failure-%03d'%n)for n in range(1,100)if not(D/('source-preparation-failure-%03d'%n)).exists());failure.mkdir(parents=True)
        for p in R.glob('tests/phase395_*.py'):write(failure/p.name,p.read_text())
        write(failure/'traceback.txt',traceback.format_exc());raise


if __name__=='__main__':main()
