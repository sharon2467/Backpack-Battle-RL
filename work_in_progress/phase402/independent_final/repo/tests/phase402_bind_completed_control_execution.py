"""Independent stdlib binding only; never import SUT or decode business capture."""
import ast
import hashlib
import json
import os
from pathlib import Path
import stat

ROOT = Path('/workspace/python-original-engine/repo')
OUT = ROOT/'data/phase402-completed-control-execution-binding'
RELEASE = 'data/phase401-root-native-attempt06/independent402-completed-control-read-release.json'
PINS = {}

def raw(path):
    path = Path(path)
    for p in [path, *path.parents]:
        assert not p.is_symlink(), str(p)
    a = path.lstat()
    assert stat.S_ISREG(a.st_mode) and a.st_nlink == 1, str(path)
    b = path.read_bytes()
    assert a == path.lstat() and len(b) == a.st_size
    pin = dict(size=len(b), sha256=hashlib.sha256(b).hexdigest())
    if str(path) in PINS: assert PINS[str(path)] == pin
    PINS[str(path)] = pin
    return b

def checked(root, row, decode=True):
    p = root/row['path']; b = raw(p)
    assert PINS[str(p)] == {k:row[k] for k in ('size','sha256')}, str(p)
    return json.loads(b) if decode else b

def save(name, value):
    (OUT/name).open('x').write(json.dumps(value,sort_keys=True,indent=2)+'\n')

def main():
    assert not OUT.exists(); OUT.mkdir()
    release = checked(ROOT,dict(path=RELEASE,size=8623,sha256='b77b9892b172697650d36ea28336fa913f91083e38adca05797e68c73ea2f0d1'))
    assert release['status']=='ROOT_COMPLETED_FIXED06_CONTROL_ONLY_READ_RELEASE'
    assert release['terminal_helper_calls_allowed']==1 and release['expected_tail_constant'] is None
    assert all(type(release[k]) is int and release[k]==0 for k in ('READY_allowed','restore_allowed','native','models','inputbuild'))
    run=Path(release['run']); capture=Path(release['capture'])
    assert str(run)=='/workspace/native-combat-20261013/runs/original027-king-single-A-20261026-attempt06'
    assert capture==run/'output/capture'
    contract=checked(ROOT,release['preparation_contract']); checked(ROOT,release['preparation_owner'])
    evidence=checked(ROOT,contract['source_evidence'])
    config=checked(ROOT,release['config']); freeze=checked(ROOT,release['source_freeze']); owner=checked(ROOT,release['source_owner'])
    invocation=checked(ROOT,release['execute_invocation']); stdout=checked(ROOT,release['execute_stdout'])
    assert checked(ROOT,release['execute_stderr'],False)==b''
    assert invocation['host_invocations']==1 and invocation['returncode']==0 and invocation['timeout'] is False
    assert stdout['status']=='ORACLE_CAPTURE_ARCHIVED_MODELS_AND_FULLPROJECTION_PENDING' and stdout['run']==str(run)
    assert stdout['models']==stdout['inputbuilds']==0 and stdout['King_production_admitted'] is False
    assert config['source_freeze']==release['source_freeze'] and config['source_owner']==release['source_owner']
    metadata={d['path']:checked(run,d) for d in release['run_metadata']}
    assert len(metadata)==23
    for row in release['capture_controls']: checked(run,row,False)
    plan=metadata['output/readonly-plan.json']; provenance=metadata['output/pool-provenance.json']
    assert plan==provenance['plan'] and plan['run']==str(run) and plan['attempt']==6 and plan['case_id']=='NATIVE-027-KING-A'
    assert plan['freeze']==release['source_freeze'] and plan['source_owner']==release['source_owner'] and plan['root_config']==release['config']
    drivers=contract['source_driver_expected_descriptors']
    assert len(drivers)==196 and drivers==plan['execute_payloads']['driver_sources']
    sources={}
    for row in freeze['files']+owner['files']+drivers+[release['source_freeze'],release['source_owner']]:
        if row['path'] in sources: assert sources[row['path']]==row
        sources[row['path']]=row
        checked(ROOT,row,False)
    archived=metadata['output/driver/source-map.json']['files']
    assert archived==[dict(file=str(i),source=row) for i,row in enumerate(drivers)]
    assert {p.name for p in (run/'output/driver').iterdir()}=={str(i) for i in range(196)}|{'source-map.json'}
    for row in archived: checked(run,dict(path='output/driver/'+row['file'],size=row['source']['size'],sha256=row['source']['sha256']),False)
    archivehash={str(i):row['sha256'] for i,row in enumerate(drivers)}
    archivehash['source-map.json']=PINS[str(run/'output/driver/source-map.json')]['sha256']
    assert archivehash==provenance['driver_sha256']
    dr={e['path']:{k:e[k] for k in ('size','sha256')} for e in metadata['output/compaction/driver-files.json']['entries'] if e['kind']=='file'}
    assert dr=={k:PINS[str(run/'output/driver'/k)] for k in archivehash}
    assert 'tests/phase363_oracle_storage.py' in sources and 'data/phase363-oracle-repair-source/source-owner.json' in sources
    host=raw(ROOT/'tests/phase391_oracle_host.py').decode()
    tree=ast.parse(host); execute=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='execute')
    source_map_lines=[n.lineno for n in ast.walk(execute) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='write_new' and n.args and 'driver/source-map.json' in ast.unparse(n.args[0])]
    process_lines=[n.lineno for n in ast.walk(execute) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='execute_process']
    assert len(source_map_lines)==1 and len(process_lines)==2 and source_map_lines[0]<min(process_lines)
    part=metadata['output/source-partition.json']; proc=metadata['output/process_result.json']; relocated=metadata['output/capture-relocation.json']
    assert part['capture_complete'] is True and part['primary_failure'] is None and part['secondary_errors']==[]
    assert part['expected_semantics_read'] is False and part['models']==part['projection']==0
    assert proc['capture_complete'] is True and proc['primary_failure'] is None and proc['secondary_errors']==proc['source_changes_after_run']==[]
    assert proc['model_acceptance'] is False and proc['automatic_retry'] is False
    assert part['capture']==relocated['current']==str(capture) and relocated['physical_copy'] is False
    actualcapture={p.name:(raw(p),PINS[str(p)])[1] for p in sorted(capture.iterdir())}
    assert actualcapture==relocated['files']
    assert set(part['lawful_inputs_present'])==set(release['lawful_twelve_bytes_only']) and part['lawful_inputs_missing']==[]
    assert all(actualcapture[n]==v for n,v in part['lawful_inputs_present'].items())
    assert actualcapture==dict(part['lawful_inputs_present'],**part['expected_observations_opaque'])
    retained=metadata['output/compaction/retained-evidence.json']; logs={}
    for base, manifest in retained.items():
        for row in manifest['entries']:
            if row['kind']=='file' and (row['path'].endswith('.log') or 'stdout' in row['path'] or 'stderr' in row['path']):
                p=run/base/row['path']; checked(run,dict(path=str(p.relative_to(run)),size=row['size'],sha256=row['sha256']),False); logs[str(p.relative_to(run))]=PINS[str(p)]
    processes={}
    for kind in ('parse','native'):
        p=metadata[f'output/{kind}-process-result.json']; m=metadata[f'output/{kind}-monitor-result.json']
        assert p['exit_code']==0 and p['timed_out'] is False and p['abort_reason'] is None
        assert all(p[k]==v for k,v in m.items())
        assert p['actual_oracle_processes']==(1 if kind=='native' else 0)
        processes[kind]={k:p[k] for k in ('exit_code','abort_reason','timed_out','parse_only','actual_oracle_processes','process_clean_exit','active_duration_seconds','cleanup','scope','enforcement')}
        processes[kind]['polling_scalars']={k:v for k,v in p['polling'].items() if not isinstance(v,(list,dict))}
        processes[kind]['polling_collection_lengths']={k:len(v) for k,v in p['polling'].items() if isinstance(v,(list,dict))}
    native=metadata['output/native-process-result.json']
    assert metadata['output/process-returned.json']==native and all(proc[k]==v for k,v in native.items())
    assert stdout['process_clean_exit']==native['process_clean_exit']
    bundle=metadata['output/compaction/bundle-manifest.json']; proof=metadata['output/compaction/pool-roundtrip.json']
    assert bundle['driver_sha256']==archivehash and proof==stdout['proof']
    assert proof['status']=='PASS' and proof['run']==str(run) and proof['physical_reconstruction'] is False
    assert proof['verification_mode']=='logical-overlay-and-live-tree-equality/1' and proof['live_tree_byte_mode_mtime_equality'] is True
    assert proof['bundle_sha256']==PINS[str(run/'output/compaction/bundle-manifest.json')]['sha256']
    assert proof['provenance_sha256']==PINS[str(run/'output/pool-provenance.json')]['sha256']
    assert metadata['output/compaction/eligibility.json']['status']=='ORACLE_CAPTURE_ONLY_NOT_MODEL_ACCEPTANCE'
    for name,digest in bundle['files'].items():
        p=str(run/'output/compaction'/name)
        if p in PINS: assert PINS[p]['sha256']==digest
    identities=metadata['output/compaction/source-identities.json']
    assert identities==dict(baseline=metadata['output/compaction/baseline-files.json'],project=metadata['output/compaction/project-files.json'])
    closure=[row['path'] for row in evidence['actual_local_import_graph']]
    assert all(name in sources for name in closure)
    summary=dict(schema='independent402-completed-binding/1',status='BOUND_PRE_HELPER',release=dict(path=RELEASE,**PINS[str(ROOT/RELEASE)]),
        source_freeze=release['source_freeze'],source_owner=release['source_owner'],run=str(run),capture=str(capture),
        logical_obligations=8,source_count=len(sources),driver_count=196,driver_bytes=sum(r['size'] for r in drivers),
        source_map_write_line=source_map_lines[0],first_process_line=min(process_lines),
        ordering_scope='Pinned executed source sequential control flow plus actual completed plan/provenance and archive; no independent event timestamp claim.',
        metadata_count=23,capture_bytes_only=actualcapture,lawful12_bytes_only=part['lawful_inputs_present'],logs_bytes_only=logs,
        processes=processes,host_invocation=invocation,host_result=stdout,stored_compaction=proof,
        current_pool_verified=False,ready_basis='Successful recorded archive_streaming return occurs after state_write; no fresh pool-state read.',
        first_inspector_failure_preserved=True,corrected_inspector_exit_code=0,
        repeated_metadata_reads='The same released parse/native/partition and selected metadata were reread for shape inspection and binding. No SUT API had run.',
        local_import_closure=closure,terminal_helper_calls=0,native=0,models=0,inputbuild=0)
    save('pre-helper-evidence.json',summary)
    save('actual-source-owner.json',dict(schema='independent402-actual-source-owner/1',files=list(sources.values())))
    save('readallowset.json',dict(schema='independent402-readallowset/1',immutable_absolute_pins=PINS,
        source_root=str(ROOT),run=str(run),capture=str(capture),control_decode_paths=[str(run/r['path']) for r in release['capture_controls']],
        local_import_closure=closure,forbidden=['current pool','/proc','subprocess','network','noncontrol capture decode','model/inputbuild']))
    save('expected.json',dict(logical_cases=contract['cases'],real_API='phase391_oracle_host.read_terminal_expected_controls',maximum_calls=1,
        expected_schema='phase391-host-terminal-control-proof/1',tail_length_constant=None,
        source_freeze=release['source_freeze'],capture=str(capture),six_control_pins=release['capture_controls'],
        success_branch_bound=True,King_admission=False,native=0,models=0,inputbuild=0))
    print(json.dumps(dict(status=summary['status'],sources=len(sources),drivers=196,capture=len(actualcapture),logs=len(logs))))

if __name__=='__main__': main()
