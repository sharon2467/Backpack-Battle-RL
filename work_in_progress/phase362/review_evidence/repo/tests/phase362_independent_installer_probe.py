"""One real storage install control on tiny owned files; no Game/pool/process execution."""
import hashlib
import json
import os
from pathlib import Path
import sys
import types

R=Path(__file__).resolve().parents[1];D=R/'data/phase362-independent-source-review'
def desc(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(R)),size=len(b),sha256=hashlib.sha256(b).hexdigest())
def identity(p):return {k:desc(p)[k] for k in ('size','sha256')}
def main():
 contract=json.loads((D/'probe-contract.json').read_text())
 for row in contract['files']:assert desc(R/row['path'])==row
 out=D/'installer-first-001';out.mkdir(exist_ok=False)
 def module(name,p):
  m=types.ModuleType(name);m.__file__=str(p);sys.modules[name]=m;exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m
 module('native_run_compaction',D/'SOURCE/compaction.py');storage=module('phase362_oracle_storage',D/'SOURCE/storage.py')
 source=out/'tiny-source';target=out/'tiny-target';source.mkdir();target.mkdir()
 original=b'ORIGINAL_UNIT_BYTES\n';replacement=b'REPLACEMENT_UNIT_BYTES\n'
 (target/'example.txt').write_bytes(original);(source/'after.txt').write_bytes(replacement)
 alias=out/'alias.txt';os.link(target/'example.txt',alias)
 before=dict(target=identity(target/'example.txt'),alias=identity(alias),target_nlink=(target/'example.txt').stat().st_nlink)
 frozen=dict(paths={'example.txt':dict(before=identity(target/'example.txt'),after=identity(source/'after.txt'),after_path='after.txt')})
 try:value=storage.install(source,target,frozen,{},out/'backup')
 except Exception as exc:accepted=False;detail=dict(type=type(exc).__name__,message=str(exc))
 else:accepted=True;detail=dict(returned=value)
 after=dict(target=identity(target/'example.txt'),alias=identity(alias),target_nlink=(target/'example.txt').stat().st_nlink)
 passed=not accepted and before==after
 report=dict(schema='phase362-independent-installer-first/1',label='direct-install-rejects-hardlink-before-write',expected='reject without writes',accepted=accepted,pass_=passed,before=before,after=after,alias_modified=before['alias']!=after['alias'],detail=detail,top_level_install_calls=1,synthetic_FS_only=True,real_Game_or_pool_touched=False,host_upstream='c.inventory(project) in reset/check_ready rejects hardlinks; no claim that normal verified host bypassed that earlier guard.',module_imports=2,subprocesses=0,host_plan=0,Godot=0,native=0,models=0)
 with (out/'report.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps(dict(pass_=passed,accepted=accepted,alias_modified=report['alias_modified'])))
if __name__=='__main__':main()
