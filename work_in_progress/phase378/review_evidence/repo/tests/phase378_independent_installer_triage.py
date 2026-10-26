"""Readonly SOURCE/control analysis only; imports no host/storage/game module."""
import ast
import hashlib
import json
from pathlib import Path

R=Path(__file__).resolve().parents[1]
ROOT=R/'data/phase377-root-oracle-attempt04'
RUN=Path('/workspace/native-combat-20261013/runs/original027-king-single-A-20261025-attempt04')
D=R/'data/phase378-independent-installer-triage'
SD=R/'data/phase378-independent-source'
def pin(p):
    h=hashlib.sha256();size=0
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block);size+=len(block)
    return dict(size=size,sha256=h.hexdigest())
def read(p):return json.loads(p.read_text())
def desc(p):return dict(path=p.relative_to(R).as_posix(),**pin(p))
def save(n,x):
    p=D/n;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:json.dump(x,f,indent=2,ensure_ascii=False);f.write('\n')
    return p
def mirror(p,n):
    q=D/n;q.parent.mkdir(parents=True,exist_ok=True)
    with q.open('xb') as f:f.write(p.read_bytes())
    assert pin(q)==pin(p);return q
def functions(path):
    text=path.read_text();tree=ast.parse(text)
    return text,{n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
def main():
    D.mkdir(exist_ok=False)
    for row in read(SD/'source-owner.json')['files']:assert pin(R/row['path'])=={k:row[k] for k in ('size','sha256')}
    controls={}
    for n in ['execute-first-invocation.json','execute-first.stderr.txt','execute-first.stdout.json','plan-first-invocation.json','plan-first.stdout.json','oracle-acceptance.json']:
        p=ROOT/n;q=mirror(p,'controls/'+n)
        if n.endswith('.json') and n!='execute-first.stdout.json':controls[n]=read(q)
    runplan=mirror(RUN/'output/readonly-plan.json','controls/run-readonly-plan.json')
    resetp=mirror(RUN/'output/prior-observer-reset.json','controls/prior-observer-reset.json')
    oldp=mirror(RUN/'output/previous-source-preimages/inventory.json','controls/previous-source-inventory.json')
    freeze_path=R/'data/phase375-food-hook-source/combined-source-freeze.json';freeze=read(freeze_path)
    host_path=R/'tests/phase375_oracle_host.py';storage_path=R/'tests/phase363_oracle_storage.py'
    host,hfn=functions(host_path);storage,sfn=functions(storage_path)
    assert "member(root,SOURCE+'/collector.gd')" in ast.get_source_segment(host,hfn['execute'])
    assert "reset_previous(" in ast.get_source_segment(host,hfn['execute'])
    source='data/phase375-food-hook-source';data='data/phase362-oracle-capture-source'
    constructed={'native_combat_capture.gd':R/source/'collector.gd','native_capture_config.json':R/data/'case-A/native_capture_config.json','.native-random-observer-disposable':R/data/'disposable-marker.txt'}
    declared={'native_combat_capture.gd':freeze['collector']}
    for name,path in list(constructed.items())[1:]:declared[name]=next(x for x in freeze['files'] if x['path']==path.relative_to(R).as_posix())
    artifacts={}
    for name,path in constructed.items():
        expected=declared[name];expected_path=R/expected['path'];assert pin(expected_path)=={k:expected[k] for k in ('size','sha256')}
        artifacts[name]=dict(constructed_relative=path.relative_to(R).as_posix(),constructed_exists=path.is_file(),frozen_descriptor=expected,actual_declared_identity=pin(expected_path),same_declared_path=path==expected_path)
    assert not artifacts['native_combat_capture.gd']['constructed_exists']
    assert all(artifacts[n]['constructed_exists'] and artifacts[n]['same_declared_path'] for n in ['native_capture_config.json','.native-random-observer-disposable'])
    for node in [hfn['source_gate'],hfn['plan']]:
        calls=[n for n in ast.walk(node) if isinstance(n,ast.Call)]
        assert not any(isinstance(n.func,ast.Name) and n.func.id=='install' for n in calls)
    assert 'artifacts' not in ast.get_source_segment(host,hfn['source_gate'])
    assert 'artifacts' not in ast.get_source_segment(host,hfn['plan'])
    install=ast.get_source_segment(storage,sfn['install'])
    assert install.index('for name, payload in artifacts.items():') < install.index('backup.mkdir()') < install.index('after=pin(payload)') < install.index("write_new(backup / 'preimages.json'") < install.index('atomic_image(target,raw')
    artifact_preflight=install[install.index('for name, payload in artifacts.items():'):install.index('backup.mkdir()')]
    assert 'pin(payload)' not in artifact_preflight and 'regular_target(payload)' not in artifact_preflight
    reset=read(resetp);previous=read(oldp);paths=freeze['paths'];names=list(paths)
    backup_ids={int(p.name):pin(p) for p in (RUN/'output/source-preimages').iterdir() if p.is_file() and p.name.isdecimal()}
    after_index={x['path']:x for x in reset['after']['entries']}
    backed=[]
    for idx,row in backup_ids.items():
        name=names[idx] if idx<len(names) else list(constructed)[idx-len(names)]
        target=after_index[name];assert row=={k:target[k] for k in ('size','sha256')}
        backed.append(dict(backup=str(idx),target=name,identity=row,phase='preimage_backup_not_installed_source'))
    patch_backups=sum(x['phase']=='preimage_backup_not_installed_source' and x['target'] in paths for x in backed)
    collector_backups=[x for x in backed if x['target']=='native_combat_capture.gd']
    assert patch_backups==74 and len(collector_backups)==1 and len(backed)==75
    assert not (RUN/'output/source-preimages/preimages.json').exists()
    assert reset['before']==previous['project'] and set(reset['restored'])=={x['path'] for x in previous['patch']['patches']}
    assert 'native_random_observer_sink_v7.gd' not in after_index and '.native-random-observer-disposable' not in after_index
    reset_restore_verified=[]
    for row in previous['patch']['patches']:
        if row['before_sha256'] is not None:
            actual=after_index[row['path']];assert actual['sha256']==row['before_sha256'] and actual['size']==row['before_size']
            reset_restore_verified.append(row['path'])
    datafiles={}
    for name in ['custom_player.json','custom_opponent.json','native_capture_config.json']:
        actual=pin(RUN/'data'/name);decl=next(x for x in freeze['files'] if x['path']==data+'/case-A/'+name)
        assert actual=={k:decl[k] for k in ('size','sha256')};datafiles[name]=actual
    absent=[n for n in ['parse-process-result.json','native-process-result.json','process_result.json','one-shot-launch.json','pool-before.json','host_manifest.json','pool-provenance.json','observer-patch'] if not (RUN/'output'/n).exists()]
    assert 'parse-process-result.json' in absent and 'native-process-result.json' in absent
    evidence={'artifact_resolution':artifacts,'backup_files':backed,'patch_preimage_backup_count':patch_backups,'collector_preimage_backup_count':1,'complete_install_journal_present':False,'reset_restored_paths':len(reset['restored']),'saved_reset_original_beforeimages_verified':len(reset_restore_verified),'saved_reset_removed_sink_and_marker':True,'run_data_copies':datafiles,'not_created_outputs':absent,'driver_files':len(list((RUN/'output/driver').iterdir())),'livepool_inventory':False}
    save('evidence.json',evidence)
    excerpts=[]
    for p,t,ns,selected in [(host_path,host,hfn,['source_gate','plan','execute']),(storage_path,storage,sfn,['lease','reset_previous','install'])]:
        for name in selected:
            n=ns[name];excerpts.append(dict(path=p.relative_to(R).as_posix(),function=name,line_start=n.lineno,line_end=n.end_lineno,text=ast.get_source_segment(t,n)))
    save('source-flow.json',dict(excerpts=excerpts,source_hashes=[desc(host_path),desc(storage_path),desc(freeze_path)]))
    finding={'status':'BLOCKED378_COLLECTOR_ARTIFACT_DESCRIPTOR_NOT_USED_AND_PREFLIGHT_AFTER_RESET',
     'direct':{'host_execute':controls['execute-first-invocation.json'],'first_error':'FileNotFoundError at storage.install journal after=pin(payload): '+str(constructed['native_combat_capture.gd']),'readonlyplan_exit':controls['plan-first-invocation.json']['exit_code'],'source_payload_presence':artifacts,'saved_run_data_copies_exact':datafiles,'partial_backups':len(backed),'complete_preimages_json':False,'driver_payloads':0},
     'source_derived_timeline':['lease writes busy state before yielding; failure handling writes failed state','reset_previous validates/backups old patch and restores its73 paths, deletes old sink and marker, returns full before/after inventory; actual saved reset confirms this completed','three input files copied to run/data before artifacts/install','install validates all75 frozen patch source payloads before backup; artifact payloads are merely Path-coerced and target-checked at this preflight','74 existing patch preimages and existing collector target are copied to numeric backup files','missing collector source throws while evaluating journal entry after-pin; in-memory journal is not persisted','preimages.json write, atomic installed-source loop, pool/data copy, patch/driver/provenance snapshots and parse/Game launch are all later and unreachable on this exception'],
     'not_claimed':['No newly installed375 source bytes are inferred from numeric backups. They contain old preimages.','No actual complete journal can be reconstructed or labeled original.','No fresh livepool/data equality asserted: SOURCE indicates pool/data copy was not reached; later actual failed-tree recovery/readback must verify bytes/metadata.','No fourth originalGame process, battle, complete12, projection or model acceptance.'],
     'same_class_finite_audit':{'execute_artifacts':3,'missing_constructed':1,'other_two_current_paths_exact_descriptor':True,'three_copied_case_inputs_exact_current_descriptors':True,'general_gap':'Both plan and source_gate validate freeze declarations, not the execute artifact binding list; directinstall independently lacks full source identity/regularity/root validation for artifact payloads before backup. Similar future alias/missing/changed payload errors can therefore occur after lease/reset or backups.'},
     'minimal_repair':['Resolve every artifact through exact frozen descriptors, including collector reuse, with one shared plan/execute binding function and expected fixed destinations.','Preflight every artifact/source/fixture identity, path safety and required metadata before lease/reset; rerun exact identity checks at the actual mutation boundary as necessary.','Direct installer must independently validate all artifact and patch payloads with expected identities before any backup or target mutation; no caller preflight Boolean shortcut.','Preserve current partial run/backs/reset/state and derive a new recovery map from actual failed tree, old026 target, reset and preimage evidence; never assume successful installed375 tree or synthesize missing preimages.json.'],
     'prior_review_limit':'375 independent gate proved exact host binding derivation but missed closure between reused collector descriptor and execute constructed path. The inherited path assumption was not proved by plan/sourcegate.',
     'actual_counts':{'readonly_analysis':1,'SUT_imports':0,'SUT_calls':0,'Godot':0,'parse_processes':0,'original_Game_processes':0,'native_battles':0,'models':0,'projection':0,'pool_writes':0,'restores':0,'READY':0,'expected_semantics_reads':0},'no_more_writes':True}
    save('finding.json',finding)
    paths=[p for p in D.rglob('*') if p.is_file()]+[host_path,storage_path,freeze_path,R/'data/phase375-food-hook-source/source-owner.json',SD/'source-owner.json',R/'tests/phase378_independent_installer_triage.py',R/'docs/phase378_attempt04_installer_triage_spec.md']
    paths+=[R/r['path'] for r in declared.values()]
    owner=save('owned-files.json',dict(files=[desc(p) for p in sorted(set(paths))],external_paths_provenance_only=True))
    for row in read(owner)['files']:assert pin(R/row['path'])=={k:row[k] for k in ('size','sha256')}
    print(json.dumps(dict(status=finding['status'],finding=desc(D/'finding.json'),owner=desc(owner),leaves=len(set(paths)),bytes=sum(p.stat().st_size for p in set(paths)))))
if __name__=='__main__':main()
