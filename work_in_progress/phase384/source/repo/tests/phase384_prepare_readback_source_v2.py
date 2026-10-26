"""New readback SOURCE only: inspector consumer pin and restore-receipt status."""
from pathlib import Path
import ast
import hashlib
import json
import difflib

R=Path(__file__).resolve().parents[1]
D=R/'data/phase384-independent-readback-source'


def pin(p):
    b=p.read_bytes();return dict(size=len(b),sha256=hashlib.sha256(b).hexdigest())


def desc(p):return dict(path=str(p.relative_to(R)),**pin(p))


def save(name,value):
    with (D/name).open('x') as stream:stream.write(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')


def main():
    review=R/'data/phase381-independent-static-review/review.json';assert pin(review)==dict(size=4409,sha256='fdec12c4774172daa223bc4b23caadce08ccfbe9a2fd0b910eb2486ddfb7b765')
    reviewed=json.loads(review.read_text());assert [r['id'] for r in reviewed['findings']]==['F01','F02']
    D.mkdir(exist_ok=True);assert not any(D.iterdir()),'new SOURCE output must be empty'
    old={}
    for name in ('data/phase381-independent-readback-source/source-owner.json','data/phase381-independent-static-review/owned-files.json'):
        path=R/name;old[name]=desc(path)
        for row in json.loads(path.read_text())['files']:assert desc(R/row['path'])==row;old[row['path']]=row
    before_path=R/'tests/phase381_independent_restored_readback.py';before=before_path.read_text()
    pairs=[('data/phase381-independent-actual-readback-first-001','data/phase384-independent-actual-readback-first-001'),
        ('data/phase381-independent-readback-source','data/phase384-independent-readback-source'),
        ('docs/phase381_independent_partial_restore_readback_source_spec.md','docs/phase384_readback_consumer_pin_and_receipt_status_repair_spec.md'),
        ('tests/phase381_independent_restored_readback.py','tests/phase384_independent_restored_readback.py'),
        ("source=(R/contract['process_inspector_source']['path']).read_text();tree=ast.parse(source)",
         "source=verify_descriptor(R,contract['process_inspector_source']).read_text();tree=ast.parse(source)"),
        ("require(receipt['READY_committed'] is False and receipt['writes']==expected_writes,'partial restore-only actual receipt')",
         "require(receipt.get('status')=='RESTORED_EXACT_TARGET_STATE_REMAINS_FAILED_INDEPENDENT_READBACK_PENDING','exact successful restore-only receipt status')\n    require(receipt['READY_committed'] is False and receipt['writes']==expected_writes,'partial restore-only actual receipt')"),
        ("selected += [SD/'CAPSULE377.json',SD/'source-contract.json',SD/'source-owner.json']",
         "selected += [SD/'CAPSULE377.json',SD/'source-contract.json',SD/'source-owner.json',SD/'readonly-process-inspector.py']")]
    after=before
    for a,b in pairs:assert a in after,a;after=after.replace(a,b)
    inverse=after
    for a,b in reversed(pairs):inverse=inverse.replace(b,a)
    assert inverse==before,'complete checker inverse'
    checker=R/'tests/phase384_independent_restored_readback.py';assert checker.read_text()==after,'exact existing derived checker';compile(after,str(checker),'exec')
    oldf={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(before).body if isinstance(n,ast.FunctionDef)}
    newf={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(after).body if isinstance(n,ast.FunctionDef)}
    assert oldf.keys()==newf.keys();changed={k for k in oldf if oldf[k]!=newf[k]};assert changed=={'main'}
    # Consumer verification must be in the same expression before read/AST execution.
    assert "source=verify_descriptor(R,contract['process_inspector_source']).read_text();tree=ast.parse(source)" in after
    assert "READBACK_STATUS = 'INDEPENDENT380_RESTORED_POOL_EXACT_TARGET_READBACK_PASS'" in after
    contract=json.loads((R/'data/phase381-independent-readback-source/source-contract.json').read_text())
    origin=contract['process_inspector_source'];inspector=R/origin['path'];assert pin(inspector)==dict(size=27304,sha256='829475e4ba5ee4a3ce3e3ce7a1d600b53cfa6ab243020a8528b6758675e6c260')
    mirror=D/'readonly-process-inspector.py';mirror.write_bytes(inspector.read_bytes());assert pin(mirror)==pin(inspector)
    contract['schema']='phase384-independent-readback-source-contract/1'
    contract['process_inspector_source']=desc(mirror);contract['process_inspector_origin']=origin
    capsule=D/'CAPSULE377.json';capsule.write_bytes((R/'data/phase381-independent-readback-source/CAPSULE377.json').read_bytes())
    contract['failed_capsule_manifest']=desc(capsule)
    contract['required_restore_receipt_status']='RESTORED_EXACT_TARGET_STATE_REMAINS_FAILED_INDEPENDENT_READBACK_PENDING'
    save('source-contract.json',contract)
    (D/'checker-source.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='frozen381/readback.py',tofile='source384/readback.py')))
    save('source-derivation.json',dict(schema='phase384-source-narrow-repair/1',before=desc(before_path),after=desc(checker),literal_pairs=pairs,
        inverse='EXACT_COMPLETE_BYTES',changed_functions=['main'],unchanged_functions=sorted(oldf.keys()-changed),
        module_constants='D/SD path literals only',exceptions=dict(main='new paths; actual inspector verify-before-read/exec; exact successful receipt status; mirror included in runtimeowner'),
        inspector_origin=origin,inspector_mirror=desc(mirror),mirror_bytes_identical=True,independent_finding=desc(review),source_preparation_failure=desc(R/'data/phase384-source-preparation-first-001/owned-files.json'),
        compile_only=True,checker_imports=0,checker_calls=0,actualpool_reads=0,proc_reads=0))
    for name,row in old.items():assert desc(R/name)==row
    save('old-source-readback.json',dict(status='ALL_REFERENCED_381_AND_REVIEW_LEAVES_IDENTICAL',files=list(old.values())))
    compile(Path(__file__).read_text(),str(Path(__file__)),'exec')
    save('summary.json',dict(schema='phase384-readback-source-handoff/1',status='SOURCE_FROZEN_INDEPENDENT_STATIC_REVIEW_PENDING',checker=desc(checker),
        inspector_consumer_verified=True,inspector_owner_covered=True,receipt_success_status_checked=True,
        READBACK_STATUS='INDEPENDENT380_RESTORED_POOL_EXACT_TARGET_READBACK_PASS',
        checker_imports=0,checker_calls=0,actualpool_reads=0,proc_reads=0,restore=0,READY=0,Godot=0,Game=0,models=0,independent_FINAL=False,no_more_writes=True))
    own=[checker,Path(__file__),R/'docs/phase384_readback_consumer_pin_and_receipt_status_repair_spec.md']+sorted(p for p in D.iterdir() if p.is_file())
    rows=[desc(p) for p in own];save('source-owner.json',dict(schema='phase384-readback-source-owner/1',files=rows,scope='Source only, no actual independent physical acceptance'))
    assert any(row==desc(mirror) for row in rows)
    for row in rows:assert desc(R/row['path'])==row
    print(json.dumps(dict(checker=desc(checker),owner=desc(D/'source-owner.json'),leaves=len(rows),bytes=sum(r['size'] for r in rows))))


if __name__=='__main__':main()
