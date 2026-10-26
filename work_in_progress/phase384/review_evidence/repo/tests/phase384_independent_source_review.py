"""Static384 consumer repair proof, not reviewed checker execution."""
import ast
import hashlib
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
SD=R/'data/phase384-independent-review-source'
D=R/'data/phase384-independent-source-review'
def pin(p):
    b=p.read_bytes();return dict(size=len(b),sha256=hashlib.sha256(b).hexdigest())
def desc(p):return dict(path=p.relative_to(R).as_posix(),**pin(p))
def read(p):return json.loads(p.read_text())
def require(x,m):
    if not x:raise ValueError(m)
def main():
    D.mkdir(exist_ok=False)
    for row in read(SD/'source-owner.json')['files']:require(pin(R/row['path'])=={k:row[k] for k in ('size','sha256')},'independent source drift')
    author_path=R/'data/phase384-independent-readback-source/source-owner.json';author=read(author_path)
    for row in author['files']:require(pin(R/row['path'])=={k:row[k] for k in ('size','sha256')} and not (R/row['path']).is_symlink(),'actual frozen author leaf')
    oldpath=R/'tests/phase381_independent_restored_readback.py';newpath=R/'tests/phase384_independent_restored_readback.py';old=oldpath.read_text();new=newpath.read_text()
    edits=[('data/phase381-independent-actual-readback-first-001','data/phase384-independent-actual-readback-first-001'),('data/phase381-independent-readback-source','data/phase384-independent-readback-source'),('docs/phase381_independent_partial_restore_readback_source_spec.md','docs/phase384_readback_consumer_pin_and_receipt_status_repair_spec.md'),('tests/phase381_independent_restored_readback.py','tests/phase384_independent_restored_readback.py'),("source=(R/contract['process_inspector_source']['path']).read_text();tree=ast.parse(source)","source=verify_descriptor(R,contract['process_inspector_source']).read_text();tree=ast.parse(source)"),("require(receipt['READY_committed'] is False and receipt['writes']==expected_writes,'partial restore-only actual receipt')","require(receipt.get('status')=='RESTORED_EXACT_TARGET_STATE_REMAINS_FAILED_INDEPENDENT_READBACK_PENDING','exact successful restore-only receipt status')\n    require(receipt['READY_committed'] is False and receipt['writes']==expected_writes,'partial restore-only actual receipt')"),("selected += [SD/'CAPSULE377.json',SD/'source-contract.json',SD/'source-owner.json']","selected += [SD/'CAPSULE377.json',SD/'source-contract.json',SD/'source-owner.json',SD/'readonly-process-inspector.py']")]
    expected=old
    for a,b in edits:require(a in expected,'exact allowed old literal');expected=expected.replace(a,b)
    require(expected==new,'whole source exact allowlist')
    compile(new,str(newpath),'exec');ot=ast.parse(old);nt=ast.parse(new)
    of={n.name:n for n in ot.body if isinstance(n,ast.FunctionDef)};nf={n.name:n for n in nt.body if isinstance(n,ast.FunctionDef)}
    require(of.keys()==nf.keys(),'no new operational function')
    preserved=[]
    for name in of:
        if name=='main':continue
        require(ast.dump(of[name],include_attributes=False)==ast.dump(nf[name],include_attributes=False),'function conserved '+name);preserved.append(name)
    require(len(preserved)==12,'twelve conserved methods')
    contract_path=R/'data/phase384-independent-readback-source/source-contract.json';contract=read(contract_path);oldcontract=read(R/'data/phase381-independent-readback-source/source-contract.json')
    mirror=contract['process_inspector_source'];origin=contract['process_inspector_origin'];require(origin==oldcontract['process_inspector_source'],'real inspector origin')
    require(mirror['path']=='data/phase384-independent-readback-source/readonly-process-inspector.py' and pin(R/mirror['path'])=={k:mirror[k] for k in ('size','sha256')}==pin(R/origin['path']),'actual mirror exact bytes')
    require(mirror['size']==27304 and mirror['sha256']=='829475e4ba5ee4a3ce3e3ce7a1d600b53cfa6ab243020a8528b6758675e6c260' and mirror in author['files'],'owned actual descriptor mirror')
    main=ast.get_source_segment(new,nf['main']);consumer="source=verify_descriptor(R,contract['process_inspector_source']).read_text()"
    require(main.index(consumer)<main.index('exec(compile('),'verifier/read before AST exec')
    require("SD/'readonly-process-inspector.py'" in main,'actual runtime owner includes mirror')
    status_guard="require(receipt.get('status')=='RESTORED_EXACT_TARGET_STATE_REMAINS_FAILED_INDEPENDENT_READBACK_PENDING'"
    require(main.index(status_guard)<main.index("state=roots['pool']/'state.json'")<main.index("actual=inventory(path)"),'receipt status before physical source/target work')
    status=next(ast.literal_eval(n.value) for n in nt.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='READBACK_STATUS' for t in n.targets))
    require(status==contract['readback_status']=='INDEPENDENT380_RESTORED_POOL_EXACT_TARGET_READBACK_PASS','380 runtime status no alias typo')
    normalized=dict(contract);normalized['schema']=oldcontract['schema'];normalized['failed_capsule_manifest']=oldcontract['failed_capsule_manifest'];normalized['process_inspector_source']=oldcontract['process_inspector_source'];del normalized['process_inspector_origin'];del normalized['required_restore_receipt_status'];require(normalized==oldcontract,'only declared contract metadata changes')
    failure=read(R/'data/phase384-source-preparation-first-001/failure.json')
    review=dict(status='INDEPENDENT384_READBACK_SOURCE_REPAIR_ACCEPTED_ROOT_EXECUTION_PENDING',checker=desc(newpath),author_source_owner=desc(author_path),
        F01=dict(closed_SOURCE=True,actual_consumer='verify_descriptor(...).read_text -> ast.parse -> selected AST exec',mirror=mirror,owned_in_source=True,owned_in_future_runtime=True),
        F02=dict(closed_SOURCE=True,exact_success_status='RESTORED_EXACT_TARGET_STATE_REMAINS_FAILED_INDEPENDENT_READBACK_PENDING',before_physical_pool_reads=True),
        full_source_allowlist_exact=True,conserved_function_AST=preserved,old381_review_reused=desc(R/'data/phase381-independent-static-review/review.json'),
        author_preparer_first_failure=failure,preparer_failure_scope='Static SOURCE preparer expectation only; actual checker/physical operation was not run.',
        runtime_readback_status=status,source_freeze=contract['source_freeze'],checker_imports=0,checker_calls=0,physical_inventory_calls=0,proc_reads=0,actualpool_reads=0,native=0,models=0,Godot=0,projection=0,
        scope='Narrow SOURCE acceptance only. Physical readback/READY/actual restore require later Root gates; no existing successful batch repeated.',no_more_writes=True)
    (D/'review.json').write_text(json.dumps(review,indent=2)+'\n')
    paths=[D/'review.json',SD/'source-owner.json',R/'tests/phase384_independent_source_review.py',R/'docs/phase384_independent_consumer_repair_review_spec.md',author_path,oldpath,R/'data/phase381-independent-static-review/review.json']+[R/r['path'] for r in author['files']]
    owner=dict(files=[desc(p) for p in sorted(set(paths))],no_more_writes=True)
    (D/'owned-files.json').write_text(json.dumps(owner,indent=2)+'\n')
    for row in owner['files']:require(pin(R/row['path'])=={k:row[k] for k in ('size','sha256')},'actual new owner readback')
    print(json.dumps(dict(status=review['status'],review=desc(D/'review.json'),owner=desc(D/'owned-files.json'),leaves=len(owner['files']),bytes=sum(r['size'] for r in owner['files']))))
if __name__=='__main__':main()
