"""Generate/compile/freeze SOURCE only. Operational modules are never imported here."""
from pathlib import Path
import argparse
import ast
import copy
import difflib
import hashlib
import json

R=Path(__file__).resolve().parents[1]
D=R/'data/phase380-payload-source'
M=R/'data/phase380-attempt04-partial-recovery-source'


def pin(path):
    raw=path.read_bytes();return dict(size=len(raw),sha256=hashlib.sha256(raw).hexdigest())


def desc(path):
    assert path.is_relative_to(R) and not any(p.is_symlink() for p in (path,*path.parents))
    return dict(path=str(path.relative_to(R)),**pin(path))


def save(name,value):
    with (D/name).open('x') as stream:stream.write(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')


def function_span(text,name):
    tree=ast.parse(text);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
    return ''.join(text.splitlines(True)[node.lineno-1:node.end_lineno])


def funcs(text):
    return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}


def generate():
    D.mkdir(exist_ok=False)
    original=(R/'tests/phase363_oracle_storage.py').read_text();ext=(R/'tests/phase380_storage_preflight_source.py').read_text()
    old_install=function_span(original,'install');new_install=function_span(ext,'install')
    suffix='\n\n'+ext.replace(new_install,'',1)
    storage=original.replace(old_install,new_install,1)+suffix
    assert storage[:-len(suffix)].replace(new_install,old_install,1)==original
    sf=funcs(original);nf=funcs(storage);assert {k for k in sf if sf[k]!=nf[k]}=={'install'}
    (R/'tests/phase380_oracle_storage.py').write_text(storage);compile(storage,'phase380_oracle_storage.py','exec')
    save('storage-inverse.json',dict(before=desc(R/'tests/phase363_oracle_storage.py'),after=desc(R/'tests/phase380_oracle_storage.py'),
        old_install=old_install,new_install=new_install,removable_suffix=suffix,all_other_functions_identical=sorted(set(sf)-{'install'}),inverse='EXACT_COMPLETE_BYTES'))
    original=(R/'tests/phase375_oracle_host.py').read_text();host=original
    pairs=[('from phase363_oracle_storage import','from phase380_oracle_storage import'),
        ('reset_previous,install,archive_streaming,c)','reset_previous,install,archive_streaming,c,check_source_descriptor,MAX_INSTALL_PAYLOADS,MAX_INSTALL_BYTES)'),
        ("SOURCE = 'data/phase375-food-hook-source'","SOURCE = 'data/phase380-payload-source'"),
        ('INDEPENDENT375_FOOD_HOOK_SOURCE_REPAIR_ACCEPTED_ROOT_PENDING','INDEPENDENT380_PAYLOAD_PREFLIGHT_PARTIAL_SOURCE_ACCEPTED_ROOT_PENDING'),
        ('phase375-root-oracle-acceptance/1','phase380-root-oracle-acceptance/1'),
        ('original027-king-single-A-20261025-attempt04','original027-king-single-A-20261025-attempt05'),('attempt=4','attempt=5')]
    for a,b in pairs:assert a in host;host=host.replace(a,b)
    edits=[]
    def edit(a,b):
        nonlocal host
        assert host.count(a)==1,a;host=host.replace(a,b,1);edits.append((a,b))
    edit("    resource_gate(root,config,paths)\n    previous=check_ready", "    resource_gate(root,config,paths)\n    payloads=resolve_execute_payloads(root,freeze,execute_driver_descriptors(root,config_descriptor,config,freeze))\n    previous=check_ready")
    edit("native_config=read(member(root,DATA+'/case-A/native_capture_config.json'))", "native_config=read(check_source_descriptor(root,payloads['case_inputs']['native_capture_config.json']))")
    edit("reviews=config['reviews'],config=native_config,policy=POLICY,", "reviews=config['reviews'],config=native_config,policy=POLICY,execute_payloads=payloads,")
    edit("    paths={key:Path(value) for key,value in launch['paths'].items()}\n    with lease", "    paths={key:Path(value) for key,value in launch['paths'].items()}\n    payloads=resolve_execute_payloads(root,freeze,execute_driver_descriptors(root,config_descriptor,config,freeze))\n    if payloads!=launch['execute_payloads']: raise ValueError('plan/execute payload descriptor graph changed before lease')\n    verify_execute_payloads(root,payloads)\n    with lease")
    edit("        data=member(root,DATA+'/case-A')\n        for name in NAMES:\n            shutil.copy2(data/name,run/'data'/name)\n        artifacts={'native_combat_capture.gd':member(root,SOURCE+'/collector.gd'),\n                   'native_capture_config.json':data/NAMES[2],'.native-random-observer-disposable':member(root,DATA+'/disposable-marker.txt')}",
        "        for name in NAMES:\n            shutil.copy2(check_source_descriptor(root,payloads['case_inputs'][name]),run/'data'/name)\n            if pin(run/'data'/name)!={k:payloads['case_inputs'][name][k] for k in ('size','sha256')}: raise ValueError('case copy identity')\n        artifacts=payloads['artifacts']")
    edit("collector=pin(artifacts['native_combat_capture.gd'])", "collector=pin(project/'native_combat_capture.gd')")
    a="        source_owned=read(descriptor(root,config['source_owner']))['files']\n        copies=[row for row in freeze['files']]+source_owned+[config_descriptor,config['source_owner'],config['source_freeze']]\n        for review in config['reviews']: copies += [review['receipt'],review['owner']]\n        copies=list({row['path']:row for row in copies}.values())"
    edit(a,"        copies=payloads['driver_sources']")
    extension=(R/'tests/phase380_host_payload_source.py').read_text();anchor='\ndef main():\n';assert host.count(anchor)==1
    host=host.replace(anchor,'\n'+extension+anchor,1)
    inverse=host.replace('\n'+extension+anchor,anchor,1)
    for a,b in reversed(edits):assert b in inverse;inverse=inverse.replace(b,a,1)
    for a,b in reversed(pairs):inverse=inverse.replace(b,a)
    assert inverse==original
    hf,hnew=funcs(original),funcs(host);changed={k for k in hf if hf[k]!=hnew[k]};assert changed=={'source_gate','plan','execute'}
    (R/'tests/phase380_oracle_host.py').write_text(host);compile(host,'phase380_oracle_host.py','exec')
    save('host-inverse.json',dict(before=desc(R/'tests/phase375_oracle_host.py'),after=desc(R/'tests/phase380_oracle_host.py'),protocol_pairs=pairs,body_edits=edits,
        inserted_source=desc(R/'tests/phase380_host_payload_source.py'),changed_functions=sorted(changed),unchanged_functions=sorted(set(hf)-changed),inverse='EXACT_COMPLETE_BYTES'))
    original=(R/'tests/phase375_pool_recovery_v2.py').read_text();recovery=original
    pairs=[('from phase363_oracle_storage import','from phase380_oracle_storage import'),('from phase375_oracle_host import','from phase380_oracle_host import'),
        ('data/phase375-attempt03-recovery-source-v2','data/phase380-attempt04-partial-recovery-source'),
        ('INDEPENDENT375_RESTORED_POOL_EXACT_TARGET_READBACK_PASS','INDEPENDENT380_RESTORED_POOL_EXACT_TARGET_READBACK_PASS'),
        ('phase375-root-pool-recovery/1','phase380-root-pool-recovery/1')]
    for a,b in pairs:assert a in recovery;recovery=recovery.replace(a,b)
    before_verify=function_span(recovery,'verify_evidence');replacement=function_span((R/'tests/phase380_partial_recovery_source.py').read_text(),'verify_evidence')
    recovery=recovery.replace(before_verify,replacement,1)
    before_todo="        path=member(roots['pool']/tree,name); info=regular_target(path)\n        todo.append((path,payload,target,dict(identity=pin(path),mode=stat.S_IMODE(info.st_mode),mtime_ns=info.st_mtime_ns)))"
    after_todo="""        path=member(roots['pool']/tree,name)
        known=tree=='project' and name in KNOWN_MISSING
        info=regular_target(path,absent=known)
        if known:
            require(info is None,'only proven absent targets may be created')
        else:
            require(info is not None,'existing target required')
        todo.append((path,payload,target,None if info is None else dict(identity=pin(path),mode=stat.S_IMODE(info.st_mode),mtime_ns=info.st_mtime_ns)))"""
    assert recovery.count(before_todo)==1;recovery=recovery.replace(before_todo,after_todo)
    before_guard="    check_failed_state(roots,evidence['failed_state'])\n    require(c.inventory(roots['pool']/'project')==evidence['failed']"
    after_guard="    require(set(c.index(evidence['target']))-set(c.index(evidence['failed']))==KNOWN_MISSING and not set(c.index(evidence['failed']))-set(c.index(evidence['target'])) and evidence.get('known_absent_creates')==sorted(KNOWN_MISSING),'exact2 partial-map creations only')\n    check_failed_state(roots,evidence['failed_state'])\n    require(c.inventory(roots['pool']/'project')==evidence['failed']"
    assert recovery.count(before_guard)==1;recovery=recovery.replace(before_guard,after_guard)
    importline='from phase380_partial_map import analyze_saved_partial,KNOWN_MISSING\n'
    recovery=recovery.replace("MAP = ",importline+"\nMAP = ",1)
    inverse=recovery.replace(importline+'\n','',1).replace(after_guard,before_guard,1).replace(after_todo,before_todo,1).replace(replacement,before_verify,1)
    for a,b in reversed(pairs):inverse=inverse.replace(b,a)
    assert inverse==original
    rf,rnew=funcs(original),funcs(recovery);changed={k for k in rf if rf[k]!=rnew[k]};assert changed=={'source_gate','verify_evidence','restore_exact'}
    (R/'tests/phase380_pool_recovery.py').write_text(recovery);compile(recovery,'phase380_pool_recovery.py','exec')
    save('recovery-inverse.json',dict(before=desc(R/'tests/phase375_pool_recovery_v2.py'),after=desc(R/'tests/phase380_pool_recovery.py'),
        protocol_pairs=pairs,old_verify=before_verify,new_verify=replacement,old_todo=before_todo,new_todo=after_todo,old_guard=before_guard,new_guard=after_guard,
        import_line=importline,changed_functions=sorted(changed),unchanged_functions=sorted(set(rf)-changed),inverse='EXACT_COMPLETE_BYTES'))
    for stem,text in [('storage',storage),('host',host),('recovery',recovery)]:
        before=(R/('tests/phase363_oracle_storage.py' if stem=='storage' else 'tests/phase375_oracle_host.py' if stem=='host' else 'tests/phase375_pool_recovery_v2.py')).read_text()
        (D/(stem+'-source.patch')).write_text(''.join(difflib.unified_diff(before.splitlines(True),text.splitlines(True),fromfile='frozen/'+stem+'.py',tofile='source380/'+stem+'.py')))
    print('SOURCE generated/compiled only. No generated module imported.')


def seal():
    assert not (D/'source-owner.json').exists() and (M/'derivation.json').is_file()
    old={}
    for name in ('data/phase375-food-hook-source/source-owner.json','data/phase379-payload-preflight-design/source-owner.json','data/phase378-independent-installer-triage/owned-files.json'):
        p=R/name;old[name]=desc(p)
        for row in json.loads(p.read_text())['files']:assert desc(R/row['path'])==row;old[row['path']]=row
    for row in json.loads((R/'data/phase375-food-hook-source/old-source-readback.json').read_text())['files']:assert desc(R/row['path'])==row;old[row['path']]=row
    origin=R/'data/phase375-food-hook-source/combined-source-freeze.json';freeze=copy.deepcopy(json.loads(origin.read_text()))
    replacements={'tests/phase363_oracle_storage.py':desc(R/'tests/phase380_oracle_storage.py'),
        'tests/phase375_oracle_host.py':desc(R/'tests/phase380_oracle_host.py'),'tests/phase375_pool_recovery_v2.py':desc(R/'tests/phase380_pool_recovery.py')}
    freeze['files']=[row for row in freeze['files'] if not row['path'].startswith('data/phase375-attempt03-recovery-source-v2/')]
    for row in freeze['files']:
        if row['path'] in replacements:value=replacements[row['path']];row.clear();row.update(value)
    files={row['path']:row for row in freeze['files']};data='data/phase362-oracle-capture-source'
    artifacts={'native_combat_capture.gd':freeze['collector'],'native_capture_config.json':files[data+'/case-A/native_capture_config.json'],'.native-random-observer-disposable':files[data+'/disposable-marker.txt']}
    total=sum(row['after']['size'] for row in freeze['paths'].values())+sum(row['size'] for row in artifacts.values());assert total==807199
    extras=[Path(__file__),R/'docs/phase380_payload_preflight_and_partial_restore_implementation_addendum.md']
    extras += [R/'tests'/n for n in ('phase380_storage_preflight_source.py','phase380_host_payload_source.py','phase380_partial_recovery_source.py','phase380_partial_map.py')]
    extras += [R/'data/phase378-independent-installer-triage/finding.json',R/'data/phase378-independent-installer-triage/owned-files.json']
    extras += sorted(p for p in M.iterdir() if p.is_file())
    freeze['files'] += [desc(p) for p in extras];assert len({row['path'] for row in freeze['files']})==len(freeze['files'])
    freeze.update(schema='phase380-payload-preflight-partial-recovery-SOURCE/1',repair_origin=desc(origin),
        repair_finding=desc(R/'data/phase378-independent-installer-triage/finding.json'),run_name='original027-king-single-A-20261025-attempt05',
        artifacts=artifacts,install_payload_limits=dict(files=78,bytes=total,source='actual frozen75patch+3artifact descriptor sums'),current_authorized_operations=0)
    assert freeze['paths']==json.loads(origin.read_text())['paths'] and freeze['collector']==json.loads(origin.read_text())['collector']
    for row in freeze['files']:assert desc(R/row['path'])==row
    for row in freeze['paths'].values():assert pin(R/row['after_path'])==row['after']
    save('combined-source-freeze.json',freeze)
    save('api-contract.json',dict(schema='phase380-api-contract/1',
        host_root_schema='phase380-root-oracle-acceptance/1',recovery_root_schema='phase380-root-pool-recovery/1',
        review_status='INDEPENDENT380_PAYLOAD_PREFLIGHT_PARTIAL_SOURCE_ACCEPTED_ROOT_PENDING',readback_status='INDEPENDENT380_RESTORED_POOL_EXACT_TARGET_READBACK_PASS',
        resolver='resolve_execute_payloads(source_root,freeze,driver_descriptors=()) -> closed graph; actual SOURCE reads, no pool',
        verifier='verify_execute_payloads(source_root,graph) -> fresh actual identities, never boolproof',
        installer='install(source_root,project,freeze,artifacts:dict[target,exact source descriptor],backup): full own preflight before backup',
        artifact_declaration='freeze.artifacts mandatory; exact equal argument; all descriptors must be in freeze.files',
        preload=dict(files=78,bytes=807199),partial_map=desc(M/'restore-map.json'),known_creates=['.native-random-observer-disposable','native_random_observer_sink_v7.gd'],
        actual_SUT_calls=0,actual_live_pool_inventory=0,actual_restore=0,actual_native=0,models=0,
        model356='CLOSED',reader361='CLOSED',Root_acceptance=None,Root_attempt05_release=None))
    for name,row in old.items():assert desc(R/name)==row
    save('old-source-readback.json',dict(status='ALL_REFERENCED_OLD_LEAVES_IDENTICAL',files=list(old.values())))
    tools=[Path(__file__)]+[R/'tests'/n for n in ('phase380_storage_preflight_source.py','phase380_host_payload_source.py','phase380_partial_recovery_source.py','phase380_partial_map.py','phase380_oracle_storage.py','phase380_oracle_host.py','phase380_pool_recovery.py')]
    for p in tools:compile(p.read_text(),str(p),'exec')
    save('summary.json',dict(schema='phase380-source-handoff/1',status='SOURCE_FROZEN_INDEPENDENT_TESTING_PENDING',freeze=desc(D/'combined-source-freeze.json'),
        schema375_and_all75patches_and_collector_identical=True,source_map_generation_from_saved_only=True,
        resolver_calls=0,installer_calls=0,recovery_calls=0,live_pool_inventory=0,Godot=0,Game=0,models=0,projection=0,independent_FINAL=False,no_more_writes=True))
    own=tools+[R/'docs/phase380_payload_preflight_and_partial_restore_implementation_addendum.md']+sorted(p for p in D.rglob('*') if p.is_file())+sorted(p for p in M.iterdir() if p.is_file())
    rows=[desc(p) for p in own];assert len({r['path'] for r in rows})==len(rows)
    save('source-owner.json',dict(schema='phase380-source-owner/1',files=rows,scope='SOURCE and saved-only map, not operational/independent acceptance'))
    for row in rows:assert desc(R/row['path'])==row
    print(json.dumps(dict(freeze=desc(D/'combined-source-freeze.json'),owner=desc(D/'source-owner.json'),leaves=len(rows),bytes=sum(r['size'] for r in rows))))


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=('generate','seal'));a=p.parse_args();(generate if a.action=='generate' else seal)()


if __name__=='__main__':main()
