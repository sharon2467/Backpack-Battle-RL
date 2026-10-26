"""Finite SOURCE-only design identity and AST verification. No SUT execution."""
import ast
import hashlib
import json
from pathlib import Path
import stat

ROOT=Path('/workspace/python-original-engine/repo')
OUT=ROOT/'data/phase403-independent-design-review'
READS={}

def checked(row):
    p=ROOT/row['path'];assert p.is_relative_to(ROOT)
    for x in [p,*p.parents]: assert not x.is_symlink(),str(x)
    s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1
    b=p.read_bytes();pin=dict(size=len(b),sha256=hashlib.sha256(b).hexdigest())
    assert pin=={k:row[k] for k in ('size','sha256')} and s==p.lstat(),str(p)
    READS[row['path']]=pin;return b

def functions(tree,prefix=''):
    result={}
    for node in tree.body:
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):result[prefix+node.name]=node
        elif isinstance(node,ast.ClassDef):result.update(functions(node,prefix+node.name+'.'))
    return result

def main():
    assert not OUT.exists();OUT.mkdir()
    ownerrow=dict(path='data/phase403-genuine-input-model-design/owned-files.json',size=1157,sha256='9c1a6efafb7204440f80b3868ba719f986b880cf95b7639f68fee93a21a409d4')
    owner=json.loads(checked(ownerrow));data={}
    for row in owner['files']:data[row['path']]=checked(row)
    prefix='data/phase403-genuine-input-model-design/'
    pins=json.loads(data[prefix+'source-pins.json']);sources={row['path']:checked(row) for row in pins['files']}
    assert len(sources)==pins['source_count']==68 and sum(len(b) for b in sources.values())==pins['bytes']==2346208
    inv=json.loads(data[prefix+'source-api-inventory.json']);verified=[]
    for m in inv['modules']:
        path=m['module']['path'];raw=checked(m['module']);text=raw.decode();tree=ast.parse(text);table=functions(tree);lines=text.splitlines(keepends=True)
        imports=[ast.unparse(n) for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom))]
        assert imports==m['top_level_imports'],path
        for row in m['functions']:
            n=table[row['name']];assert (n.lineno,n.end_lineno)==(row['line'],row['end_line'])
            assert '('+ast.unparse(n.args)+')'==row['signature'],(path,row['name'])
            candidates={'full_source_lines':''.join(lines[n.lineno-1:n.end_lineno]),'AST_source_segment_plus_newline':ast.get_source_segment(text,n)+'\n'}
            matches=[label for label,s in candidates.items() if len(s.encode())==row['size'] and hashlib.sha256(s.encode()).hexdigest()==row['sha256']]
            assert matches,(path,row['name'],'source fragment identity')
            verified.append(dict(module=path,**row,verified_source_representations=matches))
    assert len(verified)==inv['function_count']==90
    ledger=json.loads(data[prefix+'source-compatibility-ledger.json']);same351=same356=0
    for row in ledger['files']:
        a,b,c=(checked(row[k]) for k in ('source349','source351','source356'))
        assert (a==b)==row['same349_351'] and (a==c)==row['same349_356']
        same351+=a==b;same356+=a==c
    assert len(ledger['files'])==15 and same351==15 and same356==13
    result=dict(schema='independent403-static-identity/1',status='PASS_SOURCE_IDENTITIES_AND_AST',
        design_owner=ownerrow,owned_design_leaves=5,owned_design_bytes=sum(len(v) for v in data.values()),
        source_count=68,source_bytes=pins['bytes'],api_function_count=90,api_module_count=len(inv['modules']),
        source349_351_same=same351,source349_356_same=same356,verified_APIs=verified,
        consumed_source_pins=[dict(path=k,**v) for k,v in sorted(READS.items())],
        SUT_imports=0,SUT_calls=0,capture_reads=0,expected_reads=0,models=0,inputbuild=0,native=0)
    (OUT/'source-identity-verification.json').open('x').write(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('verified_APIs','consumed_source_pins')}))

if __name__=='__main__':main()
