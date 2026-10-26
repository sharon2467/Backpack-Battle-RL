"""SOURCE-only independent381 review; no checked module imports/calls."""
import ast
import hashlib
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
SD=R/'data/phase381-independent-static-review-source'
D=R/'data/phase381-independent-static-review'
def pin(p):
    b=p.read_bytes();return dict(size=len(b),sha256=hashlib.sha256(b).hexdigest())
def desc(p):return dict(path=p.relative_to(R).as_posix(),**pin(p))
def read(p):return json.loads(p.read_text())
def require(x,m):
    if not x:raise ValueError(m)
def save(n,x):
    p=D/n
    with p.open('x') as f:json.dump(x,f,indent=2,ensure_ascii=False);f.write('\n')
def fns(t):return {n.name:n for n in t.body if isinstance(n,ast.FunctionDef)}
def main():
    D.mkdir(exist_ok=False)
    for row in read(SD/'source-owner.json')['files']:require(pin(R/row['path'])=={k:row[k] for k in ('size','sha256')},'independent source drift')
    author=read(R/'data/phase381-independent-readback-source/source-owner.json')
    for row in author['files']:require(pin(R/row['path'])=={k:row[k] for k in ('size','sha256')},'author source drift')
    p=R/'tests/phase381_independent_restored_readback.py';text=p.read_text();tree=ast.parse(text);compile(text,str(p),'exec');func=fns(tree)
    old=fns(ast.parse((R/'tests/phase375_independent_restored_readback.py').read_text()))
    conserved=['audit','canonical','counts','desc','inventory','pin','read','require','save','verify_descriptor']
    for name in conserved:require(ast.dump(old[name],include_attributes=False)==ast.dump(func[name],include_attributes=False),'conservation '+name)
    source=read(R/'data/phase381-independent-readback-source/source-contract.json');capsule=read(R/source['failed_capsule_manifest']['path'])
    require(pin(R/source['failed_capsule_manifest']['path'])=={k:source['failed_capsule_manifest'][k] for k in ('size','sha256')},'capsule descriptor')
    rows=capsule['files'];require(len(rows)==capsule['file_count']==173,'capsule173')
    out=sum(n.startswith('run/output/') for n in rows);data=sum(n.startswith('run/data/') for n in rows);require(out==161 and data==3,'run file identity sets')
    mapping=read(R/source['restore_map']['path']);require(len(mapping['file_differences'])==74 and len(mapping['staged_files'])==2,'map record count')
    status=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(k,ast.Name) and k.id=='READBACK_STATUS' for k in n.targets));require(status=='INDEPENDENT380_RESTORED_POOL_EXACT_TARGET_READBACK_PASS','direct exact380 status')
    main=ast.get_source_segment(text,func['main']);prep=ast.get_source_segment(text,func['prepare_contract']);overlay=ast.get_source_segment(text,func['verify_overlay_archive'])
    require('status=READBACK_STATUS if failure is None' in main,'no370 success status')
    require('known_task_live=None' in main and 'known_pid_group_proof_applicable=False' in main and "require(not (roots['failed_run']/'output'/name).exists()" in main,'no invented native proof')
    require("lock=(roots['pool']/'.lock').open('rb')" in main and 'fcntl.LOCK_EX|fcntl.LOCK_NB' in main,'read-only exclusive lock')
    require('expected_writes=len(mapping[\'file_differences\'])+staged_differences' in main and 'expected_writes==74' in main and 'staged_differences==0' in main,'74+0')
    for phrase in ['full path/kind/SHA/mode/mtime mismatch','retained==targets[\'retained\']','driver==targets[\'driver\']','old026 bundle member SHA','old026 bundle driver SHA','actual_files==expected','user=inventory','failed overlay CRC/hash','state changed during independent readback']:
        require(phrase in main,'conservative evidence '+phrase)
    require('overlay CRC/SHA' in overlay and 'stat.S_IFREG' in overlay and 'canonical(D,info.filename)' in overlay,'archive check')
    inspector=source['process_inspector_source'];actual=pin(R/inspector['path']);require(actual=={k:inspector[k] for k in ('size','sha256')},'current original inspector byte pin')
    owners={'381source':author,'380freeze':read(R/'data/phase380-payload-source/combined-source-freeze.json'),'382final':read(R/'data/phase382-independent-final/owned-files.json')}
    covered={name:any(r['path']==inspector['path'] for r in value['files']) for name,value in owners.items()}
    require(not any(covered.values()),'reassess possible complete owned inspector closure')
    exec_read="source=(R/contract['process_inspector_source']['path']).read_text()"
    require(exec_read in main,'actual inspector read consumer')
    require("verify_descriptor(R,contract['process_inspector_source'])" not in main and "verify_descriptor(R,source['process_inspector_source'])" not in prep,'reassess inspector verification')
    require("receipt['status']" not in main and "receipt.get('status')" not in main,'reassess receipt status consumer')
    def excerpt(name,needle):
        lines=text.splitlines();i=next(i for i,line in enumerate(lines) if needle in line)
        return dict(function=name,line=i+1,text='\n'.join(lines[max(0,i-2):min(len(lines),i+4)]))
    findings=[dict(id='F01',kind='UNVERIFIED_EXECUTABLE_SOURCE_CONSUMER',descriptor=inspector,current_actual_identity=actual,current_bytes_match=True,existing_owner_coverage=covered,evidence=excerpt('main',exec_read),
        explanation='Descriptor is recorded but omitted from owner.files/runtime verify loop; source is read/extracted/executed without actual SHA verification. Current matching bytes and public staging availability do not establish consumer failclosed.',minimum='Verify descriptor before reading/exec and include immutable true source or mirror in new SOURCE owner.'),
        dict(id='F02',kind='RESTORE_RECEIPT_STATUS_UNCHECKED',evidence=excerpt('main',"receipt['READY_committed'] is False"),explanation='Wires/failedstate/READY=false/writecount checked; successful restore-only status demanded by SPEC is not checked here. Future commit rejection is separate and cannot fulfill this checker clause.',minimum="Require exact status RESTORED_EXACT_TARGET_STATE_REMAINS_FAILED_INDEPENDENT_READBACK_PENDING before issuing readback PASS.")]
    save('review.json',dict(status='BLOCKED381_INSPECTOR_CONSUMER_PIN_AND_RECEIPT_STATUS',checker=desc(p),author_source_owner=desc(R/'data/phase381-independent-readback-source/source-owner.json'),findings=findings,
        static_pass=dict(author8pins=True,conserved_method_AST=conserved,compile_only=True,status_literal=status,write_logic='74 project +0 staged differences, not76',native_PID_PGID_proof='N/A explicitNone; no fake logs/groups',capsule173_run_output=out,capsule173_run_data=data,wholeproc_false_and_gaps_retained=True,full_target_baseline_oldretained_driver_bundle_overlay_state_checks_retained=True),
        scope='SOURCE only; no physical/PID/overlay execution or physical PASS. Component380/382 acceptance unchanged; Root real restoration/readback remain pending.',checker_imports=0,checker_calls=0,physical_inventory_calls=0,proc_reads=0,actualpool_reads=0,native=0,models=0,Godot=0,projection=0,no_more_writes=True))
    paths=[p for p in D.iterdir() if p.is_file()]+[SD/'source-owner.json',R/'tests/phase381_independent_readback_source_review.py',R/'docs/phase381_independent_readback_source_review_spec.md']+[R/r['path'] for r in author['files']]+[R/'data/phase381-independent-readback-source/source-owner.json',R/inspector['path']]
    save('owned-files.json',dict(files=[desc(p) for p in sorted(set(paths))],no_more_writes=True))
    for row in read(D/'owned-files.json')['files']:require(pin(R/row['path'])=={k:row[k] for k in ('size','sha256')},'actual owner readback')
    print(json.dumps(dict(status='BLOCKED381_INSPECTOR_CONSUMER_PIN_AND_RECEIPT_STATUS',review=desc(D/'review.json'),owner=desc(D/'owned-files.json'),leaves=len(set(paths)),bytes=sum(p.stat().st_size for p in set(paths)))))
if __name__=='__main__':main()
