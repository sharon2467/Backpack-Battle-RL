"""Independent input/expected preparation only; no audit import/call."""
import hashlib
import json
import os
from pathlib import Path
import stat

R=Path('/workspace/python-original-engine/repo')
P=R/'data/phase409-independent408-component-preparation'
P.mkdir(exist_ok=False)
def save(name,value):
    p=P/name
    with p.open('x')as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
    return p
def desc(p):
    s=p.lstat();assert stat.S_ISREG(s.st_mode)and s.st_nlink==1
    b=p.read_bytes();return dict(path=str(p.relative_to(R)),size=len(b),sha256=hashlib.sha256(b).hexdigest())
def load(name):return json.loads((R/name).read_bytes())
static=load('data/phase409-independent408-source-review/static-evidence.json')
assert static['status']=='STATIC_PASS'
targets=load('data/phase409-independent408-source-review/independently-derived-targets.json')
base=[{k:r[k]for k in ('field_id','phase','side_or_role')}|dict(classification='MISSING',validation_result='UNPROVEN',proof_complete=False)for r in targets]
direct=next(i for i,r in enumerate(targets)if r['route']=='direct')
source=next(i for i,r in enumerate(targets)if r['route']=='source')
owner_paths=['data/phase402-independent-final/owned-files.json','data/phase405-independent-design-review/owned-files.json','data/phase408-initial-audit-source/source-owner.json']
owners=[load(p)for p in owner_paths]
first_name=next(iter(owners[1]['files']));first=owners[1]['files'][first_name]
bad_override={'files':{first_name:dict(first,path=first_name)}}
row=dict(path=first_name,**first)
bad_duplicate={'files':[row,row]}
variants=[dict(operation='identity'),dict(operation='remove_last'),dict(operation='duplicate_last'),
          dict(operation='patch',index=direct,patch={'proof_complete':0}),
          dict(operation='patch',index=direct,patch={'classification':'DIRECT_OBSERVATION','proof_complete':True}),
          dict(operation='patch',index=source,patch={'classification':'DIRECT_OBSERVATION','validation_result':'SUPPORTED','proof_complete':True}),
          dict(operation='patch',index=source,patch={'classification':'SOURCE_DERIVED','validation_result':'SUPPORTED','proof_complete':True}),
          dict(operation='patch',index=direct,patch={'validation_result':'SUPPORTED'})]
fs=P/'tinyfs';fs.mkdir()
ordinary=fs/'outside-ordinary.bin';ordinary.write_bytes(b'independent409-owned-component\n')
hard=fs/'hardlink-origin.bin';hard.write_bytes(b'hardlink-component\n');os.link(hard,fs/'hardlink-alias.bin')
os.symlink('outside-ordinary.bin',fs/'symlink-leaf')
os.mkfifo(fs/'special-fifo',0o600)
physical=[]
for name,data in [('symlink-leaf',b'independent409-owned-component\n'),('hardlink-alias.bin',b'hardlink-component\n'),('special-fifo',b'')]:
    p=fs/name
    physical.append(dict(path=str(p.relative_to(R)),descriptor=dict(path=name,size=len(data),sha256=hashlib.sha256(data).hexdigest())))
output_value=dict(component_only=True,purpose='strict physical output readback',actual12=False)
inputs=save('inputs.json',dict(scope='INCOMPLETE_COMPONENT_ROWS_NOT_NATIVE_OR_ROOT_AUTHORITY',real_owner_paths=owner_paths,required_targets=targets,base_assessment_rows=base,assessment_variants=variants,bad_owner_path_override=bad_override,bad_owner_duplicate=bad_duplicate,physical_negatives=physical,outside_owned_leaf=str(ordinary.relative_to(R)),output_value=output_value))
calls=[]
def case(name,api,obligations,**expected):calls.append(dict(id=name,API=api,obligations=obligations,expected=expected))
for name,o in zip(('actual402-map','actual405-map','actual408-list'),owners):case(name,'owned_index',['407-01'],count=len(o['files']))
case('owner-path-override','owned_index',['407-01'],exception_type='SourceIntegrityError',message_contains='closed path-map owner value; no path override')
case('owner-duplicate','owned_index',['407-01'],exception_type='SourceIntegrityError',message_contains='unique normalized owned source path')
case('required-exact-set','required_initial_targets',['407-04','407-06','407-07'],count=1479)
case('conservative-complete-set','assess_initial_feasibility',['407-05','407-06'],status='BLOCKED_INITIAL_SOURCE_GAPS')
for name,msg,obs in [('missing-target','complete exact required field/phase/role set',['407-06']),('duplicate-target','known unique required assessment target',['407-06']),('BOOL-proof-is-INT','assessment strict strings/BOOL proof',['407-03']),('complete-but-unproven','complete proof requires supported validation',['407-05']),('source-target-direct','SOURCE-only target cannot be directly observed',['407-05']),('caller-derived-recipe','zero reviewed SOURCE derivation recipes',['407-05']),('missing-but-supported','missing target stays unproven/incomplete',['407-05'])]:case(name,'assess_initial_feasibility',obs,exception_type='SourceIntegrityError',message_contains=msg)
case('actual-guard-install','install_io_guard',['407-08'],returns=None)
case('strict-new-output','save_new',['407-02','407-08'],nested_read_regular_calls=1)
case('exclusive-existing-output','save_new',['407-08'],exception_type='FileExistsError')
for name,msg in [('symlink','no symlink ancestry'),('hardlink','ordinary single-link before read'),('special','ordinary single-link before read')]:case('physical-'+name,'read_regular',['407-02'],exception_type='SourceIntegrityError',message_contains=msg,content_opens=0)
assert len(calls)==20
outbytes=(json.dumps(output_value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()
expected=save('expected.json',dict(calls=calls,ordinary_output_descriptor=dict(path='ordinary-output.json',size=len(outbytes),sha256=hashlib.sha256(outbytes).hexdigest()),builtin_guard_read_attempts=1,actual_audit_positive=False))
ledger=[]
for p in sorted(fs.iterdir()):
    s=p.lstat();ledger.append(dict(path=str(p.relative_to(R)),kind='symlink'if stat.S_ISLNK(s.st_mode)else'fifo'if stat.S_ISFIFO(s.st_mode)else'file',mode=s.st_mode,nlink=s.st_nlink,size=s.st_size,dev=s.st_dev,ino=s.st_ino,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,link_target=os.readlink(p)if p.is_symlink()else None,sha256=hashlib.sha256(p.read_bytes()).hexdigest()if stat.S_ISREG(s.st_mode)else None))
save('tinyfs-physical-ledger.json',dict(scope='owned isolated negative fixtures; aliases/special leaves excluded from ordinary evidence owner and retained',leaves=ledger))
readfiles=[R/'tests/phase408_initial_source_audit.py',*[R/p for p in owner_paths],inputs,expected]
readpins=[desc(p)for p in readfiles]
api=load('data/phase408-initial-audit-source/api-contract.json')
save('execution-manifest.json',dict(schema='independent409-finite-component-binding/1',static_status='STATIC_PASS',static_evidence=desc(R/'data/phase409-independent408-source-review/static-evidence.json'),source_freeze=desc(R/'data/phase408-initial-audit-source/source-freeze.json'),source_owner=desc(R/'data/phase408-initial-audit-source/source-owner.json'),actual_APIs=[r for r in api['functions']if r['name']in {c['API']for c in calls}],logical_obligations=8,planned_top_level_API_calls=20,planned_module_imports=1,whole_gate_calls=0,main_run_audit_calls=0,inputs=str(inputs.relative_to(R)),expected=str(expected.relative_to(R)),read_pins=readpins,readallowset=dict(pre_guard=[str(R/r['path'])for r in readpins],module_loader='only pinned408 source; stdlib preloaded, no bytecode write',guarded_read=[],guarded_output=str(R/'data/phase409-independent408-component-first-001'),owned_early_physical_checks=[r['path']for r in physical],denied_owned_read=str(ordinary)),runner=desc(R/'tests/phase409_run408_finite_components.py'),first_failure='preserve_and_stop_no_retry',actual12_reads=0,old_SUT_calls=0,models=0,native=0,inputbuild=0))
owned=[p for p in P.rglob('*')if p.is_file()and not p.is_symlink()and p.lstat().st_nlink==1]
owned += [R/'tests/phase409_prepare_finite_components.py',R/'tests/phase409_run408_finite_components.py',R/'tests/phase409_verify408_static.py',R/'docs/phase409_independent408_source_acceptance_spec.md',R/'data/phase409-independent408-source-review/static-evidence.json',R/'data/phase409-independent408-source-review/independently-derived-targets.json']
rows=[desc(p)for p in sorted(owned)]
save('owned-files.json',dict(schema='independent409-preexecution-owner/1',files=rows,no_more_writes=True,new_audit_imports=0,new_audit_calls=0,excluded_nonordinary_tinyfs='tinyfs-physical-ledger.json'))
print(json.dumps(dict(status='SEALED_BEFORE_IMPORT',files=len(rows),bytes=sum(r['size']for r in rows),top_level_API_calls_planned=20)))
