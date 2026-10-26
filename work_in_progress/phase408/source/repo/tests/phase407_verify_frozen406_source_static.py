"""Independent static identities only; never import/call the audit under review."""
import ast
import hashlib
import json
from pathlib import Path
import stat

ROOT=Path('/workspace/python-original-engine/repo')
OUT=ROOT/'data/phase407-frozen406-static-review'
READS={}

def read(row):
    path=Path(row['path']);path=path if path.is_absolute() else ROOT/path
    assert path.is_relative_to(ROOT) or path.is_relative_to('/workspace/godotsteam-startup-20261013/baseline/Backpack Battles'),str(path)
    for p in [path,*path.parents]:assert not p.is_symlink(),str(p)
    a=path.lstat();assert stat.S_ISREG(a.st_mode) and a.st_nlink==1
    raw=path.read_bytes();b=path.lstat()
    for k in ('st_dev','st_ino','st_mode','st_nlink','st_size','st_mtime_ns','st_ctime_ns'):assert getattr(a,k)==getattr(b,k)
    pin=dict(size=len(raw),sha256=hashlib.sha256(raw).hexdigest());assert pin=={k:row[k] for k in ('size','sha256')},str(path)
    READS[str(path)]=pin;return raw

def main():
    assert not OUT.exists();OUT.mkdir()
    ownerrow=dict(path='data/phase406-initial-audit-source/source-owner.json',size=11685,sha256='62cd2736af3d832d89d8d4ae0d402541a347cac07f732e10f95a2335ea2f6b4c')
    freezerow=dict(path='data/phase406-initial-audit-source/source-freeze.json',size=24871,sha256='26bab64ed73ad9fd3bcf3deecc1dd1850ab82fc9882fa6b1511e35c7f18015e9')
    apirow=dict(path='data/phase406-initial-audit-source/api-contract.json',size=7822,sha256='915cb39fa9f3b5d8f433230fedd8dad5e3ba282dd122cbf9c596f76da84f2c23')
    owner=json.loads(read(ownerrow));assert len(owner['files'])==58 and len({x['path'] for x in owner['files']})==58
    contents={x['path']:read(x) for x in owner['files']};assert sum(map(len,contents.values()))==1720413
    freeze=json.loads(read(freezerow));api=json.loads(read(apirow));raw=read(api['module']);text=raw.decode();tree=ast.parse(text);lines=text.splitlines(keepends=True)
    assert api['module']==dict(path='tests/phase406_initial_source_audit.py',size=68511,sha256='87b65f6df2cadc01b2855a79c127f072c0574a39900210beee6eff3b207a2473')
    constants={}
    for node in tree.body:
        if isinstance(node,ast.Assign):
            for target in node.targets:
                if isinstance(target,ast.Name):constants[target.id]=ast.literal_eval(node.value)
    functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    checked=[]
    for row in api['functions']:
        n=functions[row['name']];assert n.lineno==row['line'] and '('+ast.unparse(n.args)+')'==row['signature']
        segment=''.join(lines[n.lineno-1:n.end_lineno]).encode()
        assert len(segment)==row['size'] and hashlib.sha256(segment).hexdigest()==row['sha256'],row['name']
        checked.append(dict(row,end_line=n.end_lineno))
    assert len(checked)==28 and set(functions)=={x['name'] for x in api['functions']}
    imports=[ast.unparse(n) for n in ast.walk(tree) if isinstance(n,(ast.Import,ast.ImportFrom))]
    assert imports==['import argparse','import hashlib','import json','import math','import os','from pathlib import Path, PurePosixPath','import re','import stat','import struct','import sys','import traceback']
    assert freeze['static_pins']==constants['STATIC_PINS'] and freeze['module']==api['module']
    declared={x['path']:x for x in freeze['files']};owned={x['path']:x for x in owner['files']}
    assert set(declared)==set(constants['STATIC_PINS'])|set(constants['SOURCE_ARTIFACTS'])
    assert set(owned)==set(declared)|{constants['SOURCE']+'/source-freeze.json',constants['SOURCE']+'/summary.json'}
    assert all(owned[n]==row for n,row in declared.items())
    assert api['authority_schema']=='root406-lawful12-initial-audit/1' and api['required_review_status']==constants['REVIEW_STATUS']=='INDEPENDENT407_STDLIB_INITIAL_AUDIT_SOURCE_ACCEPTED_ROOT_PENDING'
    owners={}
    for label in ('OWNER402','OWNER405'):
        path=constants[label];value=json.loads(contents[path]);owners[label]=dict(path=path,descriptor=constants['STATIC_PINS'][path],files_container_type=type(value['files']).__name__,file_count=len(value['files']))
    callsites={}
    for name in ('verify_audit_release','run_audit','save_new','seal_audit_once','assess_initial_feasibility'):
        callsites[name]=[dict(line=n.lineno,call=ast.unparse(n.func)) for n in ast.walk(functions[name]) if isinstance(n,ast.Call)]
    snippets={name:''.join(lines[functions[name].lineno-1:functions[name].end_lineno]) for name in ('owned_index','verify_audit_release','read_regular','assess_initial_feasibility','save_new','seal_audit_once','run_audit')}
    for path,row in list(READS.items()):read(dict(path=path,**row))
    result=dict(schema='independent407-frozen406-static-identity/1',status='IDENTITIES_PASS_SEMANTIC_REVIEW_SEPARATE',source_owner=ownerrow,source_freeze=freezerow,api=apirow,module=api['module'],
        owned_leaves=58,owned_bytes=1720413,API_functions=checked,imports=imports,static_control_count=len(constants['STATIC_PINS']),source_artifact_count=len(constants['SOURCE_ARTIFACTS']),
        real_prior_owner_shapes=owners,callsites=callsites,source_snippets=snippets,consumed_pins=[dict(path=p,**v) for p,v in sorted(READS.items())],
        new_audit_imports=0,new_audit_calls=0,old_SUT_imports=0,old_SUT_calls=0,schema_calls=0,run_reads=0,capture_reads=0,inputbuild=0,models=0,native=0,post_pins_unchanged=True)
    (OUT/'source-identity-and-static-evidence.json').open('x').write(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],leaves=58,bytes=1720413,APIs=len(checked),prior_owner_shapes=owners,new_audit_calls=0)))

if __name__=='__main__':main()
