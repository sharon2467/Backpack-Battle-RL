"""Prepare read-only checker SOURCE and saved pins; never execute/import that checker."""
from pathlib import Path
import ast
import copy
import difflib
import hashlib
import json

R=Path(__file__).resolve().parents[1]
SD=R/'data/phase381-independent-readback-source'


def pin(p):
    b=p.read_bytes();return dict(size=len(b),sha256=hashlib.sha256(b).hexdigest())


def desc(p):return dict(path=str(p.relative_to(R)),**pin(p))


def save(name,value):
    with (SD/name).open('x') as f:f.write(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')


def main():
    SD.mkdir(exist_ok=False)
    oldpath=R/'tests/phase375_independent_restored_readback.py';original=oldpath.read_text();text=original
    pairs=[('Read-only physical366 target validation.','Read-only physical380 partial-restored target validation.'),
        ("data/phase375-independent-actual-readback-first-001","data/phase381-independent-actual-readback-first-001"),
        ("data/phase375-independent-readback-source","data/phase381-independent-readback-source"),
        ('phase375-root-pool-recovery/1','phase380-root-pool-recovery/1'),
        ('phase375-attempt03-exact-restore-source-map/1','phase380-attempt04-partial-reset-map/1'),
        ("endswith('attempt03')","endswith('attempt04')"),
        ('failed source is attempt03, not prior attempt','failed source is attempt04 partial-install, not prior attempt'),
        ('new attempt03 map schema','new attempt04 partial-reset map schema'),
        ('ROOT exact370 restore-only source','ROOT exact380 restore-only source'),
        ('phase375-independent-physical-readback/1','phase381-independent-physical-readback/1'),
        ("status='INDEPENDENT370_RESTORED_POOL_EXACT_TARGET_READBACK_PASS' if failure is None else 'BLOCKED_INDEPENDENT370_RESTORED_POOL_READBACK'", "status=READBACK_STATUS if failure is None else 'BLOCKED_INDEPENDENT380_RESTORED_POOL_READBACK'"),
        ('phase375-independent-readback-owner/1','phase381-independent-readback-owner/1'),
        ('CAPSULE372.json','CAPSULE377.json'),
        ('docs/phase375_independent_actual_readback_source_spec.md','docs/phase381_independent_partial_restore_readback_source_spec.md'),
        ('tests/phase375_independent_restored_readback.py','tests/phase381_independent_restored_readback.py')]
    for a,b in pairs:assert a in text,a;text=text.replace(a,b)
    text=text.replace("AUDIT=dict(write_attempts=0,blocked=[],subprocesses=0,network=0)","AUDIT=dict(write_attempts=0,blocked=[],subprocesses=0,network=0)\nREADBACK_STATUS = 'INDEPENDENT380_RESTORED_POOL_EXACT_TARGET_READBACK_PASS'")
    edits=[]
    def edit(a,b):
        nonlocal text
        assert text.count(a)==1,a;text=text.replace(a,b,1);edits.append((a,b))
    a="    for key in ('source_freeze','restore_map','input_pins'):require(config[key]==source[key],'current exact source/map/pins '+key)"
    b=a+"\n    require(source['readback_status']==READBACK_STATUS,'exact380 API readback status')\n    reviews=config.get('reviews');require(type(reviews)is list and bool(reviews),'actual SOURCE review descriptors from ROOT required')\n    for item in reviews:\n        review=read(verify_descriptor(R,item['receipt']));owned=read(verify_descriptor(R,item['owner']))\n        for row in owned['files']:verify_descriptor(R,row)\n        require(any(row==item['receipt'] for row in owned['files']),'owned actual SOURCE review')\n        require(review.get('status')==source['SOURCE_review_status'] and review.get('source_freeze')==config['source_freeze'],'actual380 SOURCE accepted closure')\n        require(all(type(review.get(key))is int and review[key]==0 for key in ('native','models')),'SOURCE review not native/model acceptance')"
    edit(a,b)
    a="    require(receipt['READY_committed'] is False and receipt['writes']==len(mapping['file_differences'])+len(mapping['staged_files']),'restore only receipt')"
    b="""    saved_staged=read(roots['failed_run']/'output/failed-pool-preservation/failed-staged-files.json')
    staged_index={row['path']:row for row in saved_staged['entries']}
    staged_differences=sum(staged_index[row['target']['path']]!=row['target'] for row in mapping['staged_files'])
    expected_writes=len(mapping['file_differences'])+staged_differences
    require(len(mapping['file_differences'])==74 and staged_differences==0 and expected_writes==74,'actual partial74+staged0, not old76')
    require(mapping['known_absent_creates']==['.native-random-observer-disposable','native_random_observer_sink_v7.gd'],'exact partial2 creates')
    require(receipt['READY_committed'] is False and receipt['writes']==expected_writes,'partial restore-only actual receipt')"""
    edit(a,b)
    start=text.index("        for name in ('parse-process-result.json','native-process-result.json'):")
    end=text.index("        for proc in Path('/proc').iterdir():",start)
    old=text[start:end]
    new="""        # This attempt failed before parse/Game; no native cleanup record or PGID exists.
        for name in ('parse-process-result.json','native-process-result.json'):
            require(not (roots['failed_run']/'output'/name).exists(),'attempt04 must not invent parse/Game process records')
"""
    text=text[:start]+new+text[end:];edits.append((old,new))
    edit("schema='phase366-task-process-scope/1',known_pgids=sorted(groups),known_pids=sorted(known)",
         "schema='phase381-task-process-scope/1',attempt04_native_process_records='ABSENT_EXPECTED_PRE_PARSE_GAME',known_pid_group_proof_applicable=False,known_pgids=sorted(groups),known_pids=sorted(known)")
    edit("known_task_live=0,live_Godot_Xvfb=0,whole_system_proc_complete=False,", "known_task_live=None,visible_live_Godot_Xvfb=0,whole_system_proc_complete=False,")
    edit("restriction='Permission gaps remain explicitly in process-inspection.json; readable task PID/group/command identities and exclusive pool lock are the task gate.'",
         "restriction='No attempt04 native PID/PGID cleanup record exists; empty known sets are not evidence. Generic scoped matches/visible identities plus readonly flock only; permission gaps remain explicit and wholeproc is not claimed.'")
    edit("result['process_inspection']=dict(active_matches=0,inspection_gaps=sum(len(v['inspection_gaps']) for v in inspections.values()),whole_system_proc_complete=False,known_task_live=0,live_Godot_Xvfb=0,exclusive_pool_lock_acquired_readonly=True,processes_launched=0,source_exact_functions=2)",
         "result['process_inspection']=dict(active_matches=0,inspection_gaps=sum(len(v['inspection_gaps']) for v in inspections.values()),whole_system_proc_complete=False,known_task_live=None,known_native_pid_group_record=False,visible_live_Godot_Xvfb=0,exclusive_pool_lock_acquired_readonly=True,processes_launched=0,source_exact_functions=2)")
    a="        expected_owner=read(R/contract['failed_capsule_manifest']['path'])" # old code has failed= prefix on same line.
    a="        failed=roots['failed_run'];expected_owner=read(R/contract['failed_capsule_manifest']['path'])"
    edit(a,a+"\n        require(expected_owner['schema']=='standalone-attempt04-partial-install-failure-capsule/1' and expected_owner['file_count']==173 and len(expected_owner['files'])==173,'real377 capsule manifest')\n        require(all(not name.startswith('run/') or name.startswith(('run/output/','run/data/')) for name in expected_owner['files']),'exact failed output/data member selection')")
    # Independently stream the old026 bundle and ZIP too; no extraction or original code execution.
    anchor="        result['previous_retained']={key:counts(value) for key,value in retained.items()};result['previous_driver']=counts(driver)"
    addition="""
        bundle=previous/'output/compaction';bundle_manifest=read(verify_descriptor(previous,contract['previous_bundle_manifest']))
        for name,sha in bundle_manifest['files'].items():require(pin(canonical(bundle,name))['sha256']==sha,'old026 bundle member SHA')
        for name,sha in bundle_manifest['driver_sha256'].items():require(pin(canonical(previous/'output/driver',name))['sha256']==sha,'old026 bundle driver SHA')
        old_overlay=read(bundle/'overlay-manifest.json')
        result['previous_overlay']=verify_overlay_archive(bundle/'overlay.zip',old_overlay,targets['project'])
"""
    edit(anchor,anchor+addition)
    helper="""
def verify_overlay_archive(path,overlay,tree):
    index={row['path']:row for row in tree['entries']}
    with zipfile.ZipFile(path) as archive:
        require(len(archive.infolist())==len(set(archive.namelist())) and set(archive.namelist())==set(overlay['content']),'overlay exact unique member set')
        for info in archive.infolist():
            canonical(D,info.filename) # lexical safety; no member is extracted or created.
            row=index[info.filename]
            require(stat.S_IFMT(info.external_attr>>16)==stat.S_IFREG and stat.S_IMODE(info.external_attr>>16)==row['mode'],'overlay regular type/mode')
            h=hashlib.sha256();size=0
            with archive.open(info) as stream:
                for block in iter(lambda:stream.read(1024*1024),b''):h.update(block);size+=len(block)
            require(size==row['size'] and h.hexdigest()==row['sha256'],'overlay CRC/SHA')
    return dict(members=len(overlay['content']),CRC_SHA_mode_valid=True,extractions=0)

"""
    text=text.replace('\ndef prepare_contract():','\n'+helper+'\ndef prepare_contract():',1)
    checker=R/'tests/phase381_independent_restored_readback.py';checker.write_text(text);compile(text,str(checker),'exec')
    of={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(original).body if isinstance(n,ast.FunctionDef)}
    nf={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}
    changed={k for k in of if of[k]!=nf[k]};assert changed=={'prepare_contract','main'}
    assert set(nf)-set(of)=={'verify_overlay_archive'}
    assert "status=READBACK_STATUS" in text and "INDEPENDENT370_RESTORED_POOL_EXACT_TARGET_READBACK_PASS" not in text
    (SD/'checker-source.patch').write_text(''.join(difflib.unified_diff(original.splitlines(True),text.splitlines(True),fromfile='frozen375/readback.py',tofile='source381/readback.py')))
    oldcontract=json.loads((R/'data/phase375-independent-readback-source/source-contract.json').read_text())
    mapping=R/'data/phase380-attempt04-partial-recovery-source/restore-map.json';m=json.loads(mapping.read_text());inputs=R/'data/phase380-attempt04-partial-recovery-source/source-input-pins.json'
    api=R/'data/phase380-payload-source/api-contract.json';av=json.loads(api.read_text());require_status='INDEPENDENT380_RESTORED_POOL_EXACT_TARGET_READBACK_PASS';assert av['readback_status']==require_status
    cap=Path('/workspace/checkpoints/phase377-attempt04-partial-install-failure-capsule/CAPSULE.json');cv=json.loads(cap.read_text());assert cv['file_count']==173 and len(cv['files'])==173 and cv['payload_bytes']==22642135
    (SD/'CAPSULE377.json').write_bytes(cap.read_bytes())
    saved=Path(m['roots']['failed_run'])/'output/failed-pool-preservation';failedstate=pin(saved/'failed-pool-state.json')
    previous=Path(m['roots']['previous_run']);staged=json.loads((saved/'failed-staged-files.json').read_text());si={r['path']:r for r in staged['entries']}
    count=sum(si[row['target']['path']]!=row['target'] for row in m['staged_files']);assert count==0 and len(m['file_differences'])==74
    bundle_manifest=next(row for row in json.loads(inputs.read_text())['files'] if row['root']=='previous_run' and row['path']=='output/compaction/bundle-manifest.json')
    contract=dict(schema='phase381-independent-readback-SOURCE-contract/1',source_freeze=desc(R/'data/phase380-payload-source/combined-source-freeze.json'),
        restore_map=desc(mapping),input_pins=desc(inputs),readback_status=require_status,SOURCE_review_status=av['review_status'],source_API=desc(api),
        external_targets=oldcontract['external_targets'],failed_state=failedstate,process_inspector_source=oldcontract['process_inspector_source'],
        failed_capsule_manifest=desc(SD/'CAPSULE377.json'),previous_bundle_manifest=bundle_manifest,
        actual_restore_receipt='REQUIRED_RUNTIME_CLI_DESCRIPTOR_NOT_YET_KNOWN',actual_authorization='REQUIRED_RUNTIME_CLI_DESCRIPTOR_NOT_YET_KNOWN',
        expected_restore_file_writes=74,project_differences=74,staged_file_differences=0,directory_differences=7,
        failed_retained=dict(run_output_members=161,run_data_members=3,total_capsule_members=173,user='OBSERVE_ONLY_EXCLUDED_HISTORICAL'),
        attempt04_process_records='NONE_EXPECTED_BEFORE_PARSE_GAME',known_native_pid_group_proof=False,whole_system_proc_complete=False,
        conservative_remaining=['Future380realSOURCEacceptance/Rootrestoreconfig/receipt unavailable now','No actual tree/process/ZIP reads by checker yet','Process permissiongaps must remain disclosed','No independent physical PASS/READY/native from source compile'])
    for row in contract['external_targets'].values():assert pin(previous/row['path'])=={k:row[k] for k in ('size','sha256')}
    assert pin(R/contract['process_inspector_source']['path'])=={k:contract['process_inspector_source'][k] for k in ('size','sha256')}
    save('source-contract.json',contract)
    save('source-derivation.json',dict(schema='phase381-source-derivation/1',before=desc(oldpath),after=desc(checker),protocol_pairs=pairs,body_edits=edits,
        changed_functions=sorted(changed),unchanged_functions=sorted(set(of)-changed),added_functions=['verify_overlay_archive'],
        full_inventory_and_audit_and_descriptor_functions_AST_identical=True,compile_only=True,checker_imports=0,checker_calls=0,actual_pool_reads=0))
    save('summary.json',dict(schema='phase381-readback-source-handoff/1',status='SOURCE_FROZEN_INDEPENDENT_STATIC_GATE_AND_ROOT_RESTORE_PENDING',checker=desc(checker),
        readback_status=require_status,expected_writes=74,attempt04_no_parse_game_record=True,actual_current_pool_reads=0,checker_calls=0,restores=0,READY=0,Godot=0,Game=0,models=0,independent_FINAL=False,no_more_writes=True))
    compile(Path(__file__).read_text(),str(Path(__file__)),'exec')
    own=[checker,Path(__file__),R/'docs/phase381_independent_partial_restore_readback_source_spec.md']+sorted(p for p in SD.iterdir() if p.is_file())
    rows=[desc(p) for p in own];save('source-owner.json',dict(schema='phase381-readback-source-owner/1',files=rows,scope='SOURCE only, no actual independent readback acceptance'))
    for row in rows:assert pin(R/row['path'])=={k:row[k] for k in ('size','sha256')}
    print(json.dumps(dict(checker=desc(checker),owner=desc(SD/'source-owner.json'),leaves=len(rows),bytes=sum(row['size'] for row in rows))))


if __name__=='__main__':main()
