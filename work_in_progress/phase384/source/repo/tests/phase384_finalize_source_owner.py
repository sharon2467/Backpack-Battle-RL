"""Output-only SOURCE owner finalizer. Never imports the readback checker."""
from pathlib import Path
import hashlib,json,difflib,ast
R=Path(__file__).resolve().parents[1]
D=R/'data/phase384-independent-readback-source'
def desc(p):
    b=p.read_bytes();return dict(path=str(p.relative_to(R)),size=len(b),sha256=hashlib.sha256(b).hexdigest())
def save(p,v):
    with p.open('x') as f:f.write(json.dumps(v,indent=2,sort_keys=True)+'\n')
def main():
    owner=D/'source-owner.json';original=owner.read_bytes()
    (D/'initial-source-owner-before-failure-coverage.json').write_bytes(original)
    for row in json.loads(original)['files']:assert desc(R/row['path'])==row
    old=R/'tests/phase384_prepare_readback_source.py';new=R/'tests/phase384_prepare_readback_source_v2.py'
    (D/'source-preparation-repair.patch').write_text(''.join(difflib.unified_diff(old.read_text().splitlines(True),new.read_text().splitlines(True),fromfile=str(old.relative_to(R)),tofile=str(new.relative_to(R)))))
    save(D/'source-preparation-erratum.json',dict(status='SOURCE_PREPARATION_ONLY_CORRECTION',
        original_spec_statement='prepare_contract and main AST exceptions',correction='Only main AST changes; D/SD path constants are module-level. prepare_contract AST is unchanged.',
        first_failure_owner=desc(R/'data/phase384-source-preparation-first-001/owned-files.json'),
        checker_imports=0,checker_calls=0,actualpool_reads=0,proc_reads=0,independent_acceptance=False))
    files=[R/'tests/phase384_independent_restored_readback.py',old,new,Path(__file__),R/'docs/phase384_readback_consumer_pin_and_receipt_status_repair_spec.md']
    files+=sorted(p for p in D.iterdir() if p.is_file() and p!=owner)
    files+=sorted((R/'data/phase384-source-preparation-first-001').iterdir())
    rows=[desc(p) for p in files];assert len({r['path'] for r in rows})==len(rows)
    inspector=json.loads((D/'source-contract.json').read_text())['process_inspector_source'];assert inspector in rows
    for p in [R/'tests/phase384_independent_restored_readback.py',old,new,Path(__file__)]:compile(p.read_text(),str(p),'exec')
    a=ast.parse((R/'tests/phase381_independent_restored_readback.py').read_text());b=ast.parse((R/'tests/phase384_independent_restored_readback.py').read_text())
    f=lambda t:{n.name:ast.dump(n,include_attributes=False) for n in t.body if isinstance(n,ast.FunctionDef)}
    x,y=f(a),f(b);assert [k for k in x if x[k]!=y[k]]==['main']
    owner.write_text(json.dumps(dict(schema='phase384-readback-source-owner/1',files=rows,scope='Source only; preparation failure preserved; no actual independent physical acceptance'),indent=2,sort_keys=True)+'\n')
    for row in rows:assert desc(R/row['path'])==row
    print(json.dumps(dict(owner=desc(owner),leaves=len(rows),bytes=sum(r['size'] for r in rows),checker=desc(R/'tests/phase384_independent_restored_readback.py'),contract=desc(D/'source-contract.json'),unchanged_functions=len(x)-1)))
if __name__=='__main__':main()
