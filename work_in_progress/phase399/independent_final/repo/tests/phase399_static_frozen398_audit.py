"""Independent static audit of frozen398; no SUT imports or calls."""
import ast
import hashlib
import json
from pathlib import Path
import stat
import traceback
R=Path(__file__).absolute().parents[1];D=R/'data/phase399-independent-static'
def desc(p):
 s=p.lstat();assert stat.S_ISREG(s.st_mode)and s.st_nlink==1 and not any(q.is_symlink()for q in(p,*p.parents))
 b=p.read_bytes();t=p.lstat();assert(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==(t.st_dev,t.st_ino,t.st_size,t.st_mtime_ns,t.st_ctime_ns)
 return dict(path=str(p.relative_to(R)),size=len(b),sha256=hashlib.sha256(b).hexdigest())
def read(p):return json.loads(p.read_text())
def check(row):assert desc(R/row['path'])=={k:row[k]for k in('path','size','sha256')}
def save(name,v):
 with(D/name).open('x')as f:f.write(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+'\n')
def fns(text):return {n.name:ast.dump(n,include_attributes=False)for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}
def main():
 assert not D.exists();D.mkdir()
 pins=[('data/phase398-source-handoff/owned-files.json',97066,'50324ee7a58bae41a156ea742357385c5bb3b7abfd9cb545ff04c946cda77c71'),('data/phase398-attempt05-recovery-source/combined-source-freeze.json',96911,'5fb02ee64338e3cb87e84f238e42c7ecbb92e212cd52b7385b7757af7f752378'),('data/phase398-attempt05-recovery-source/source-owner.json',96144,'38098f36375ca8e982b7108dba31ea2d885e18c43d53b57db39c99a39686bd8f'),('data/phase398-independent-readback-source/source-owner.json',96725,'7a5cf72b88b3ab374fe8e7d3cd5a91fdf0ccedca3d29d849c6f77cc01541652b')]
 for name,size,sha in pins:check(dict(path=name,size=size,sha256=sha))
 handoff=read(R/pins[0][0]);rows=handoff['files']
 assert len(rows)==433 and len({r['path']for r in rows})==433 and sum(r['size']for r in rows)==7067200
 for row in rows:check(row)
 freeze=read(R/pins[1][0]);declared={r['path']:r for r in freeze['files']}
 for row in freeze['files']:check(row)
 owner={r['path']:r for r in read(R/pins[2][0])['files']}
 closure={};todo=['tests/phase398_pool_recovery.py'];graph=[]
 while todo:
  name=todo.pop()
  if name in closure:continue
  closure[name]=desc(R/name);tree=ast.parse((R/name).read_text());imports=[]
  for n in ast.walk(tree):
   if isinstance(n,ast.Import):imports.extend(a.name for a in n.names)
   elif isinstance(n,ast.ImportFrom)and n.module:imports.append(n.module)
  local=sorted({'tests/'+m+'.py'for m in imports if(R/'tests'/(m+'.py')).is_file()})
  graph.append(dict(path=name,local_imports=local));todo+=local
 assert closure=={r['path']:r for r in freeze['import_closure']}
 assert all(owner[k]==declared[k]==v for k,v in closure.items())
 inverses=[]
 for stem in('phase398_pool_recovery','phase398_independent_restored_readback','phase398_recovery_gate_source'):
  v=read(R/('data/phase398-attempt05-recovery-source/'+stem+'-inverse.json'));check(v['before']);check(v['after'])
  new=(R/v['after']['path']).read_text();old=(R/v['before']['path']).read_text();inverse=new;normalized=new
  assert[vv['kind']for vv in v['edits']].count('semantic')==1 and v['edits'][0]['kind']=='semantic'
  for edit in reversed(v['edits']):
   for pos in reversed(edit['positions']):
    assert inverse[pos:pos+len(edit['after'])]==edit['after']
    inverse=inverse[:pos]+edit['before']+inverse[pos+len(edit['after']):]
    if edit['kind']=='protocol':
     assert normalized[pos:pos+len(edit['after'])]==edit['after']
     normalized=normalized[:pos]+edit['before']+normalized[pos+len(edit['after']):]
  assert inverse==old
  a,b,n=fns(old),fns(new),fns(normalized)
  changes=sorted(k for k in a if a[k]!=b[k]);semantic=sorted(k for k in a if a[k]!=n[k])
  expected=['prepare_contract']if'readback'in stem else['recovery_source_leaf']
  assert semantic==expected and changes==v['changed_functions']
  inverses.append(dict(before=v['before'],after=v['after'],complete_inverse='INDEPENDENT_EXACT_BYTES',changed_functions=changes,semantic_changes=semantic,unchanged_functions=sorted(k for k in a if a[k]==b[k])))
 old_identity=read(R/'data/phase396-independent-static-first-001/evidence.json')
 conservation=[]
 for index,newpath in((0,'tests/phase398_pool_recovery.py'),(2,'tests/phase398_independent_restored_readback.py')):
  prior=old_identity['inverse_checks'][index];source=prior['source'];check(source)
  old=fns((R/source['path']).read_text());new=fns((R/newpath).read_text())
  for name in prior['conserved']:assert old[name]==new[name]
  conservation.append(dict(origin=source,successor=desc(R/newpath),conserved_names=prior['conserved']))
 rec=(R/'tests/phase398_pool_recovery.py').read_text();gate=(R/'tests/phase398_recovery_gate_source.py').read_text();reader=(R/'tests/phase398_independent_restored_readback.py').read_text()
 trees={k:ast.parse(v)for k,v in [('recovery',rec),('gate',gate),('reader',reader)]}
 funcs={k:{n.name:n for n in t.body if isinstance(n,ast.FunctionDef)}for k,t in trees.items()}
 for name in('recovery_source_leaf','source_gate'):assert ast.dump(funcs['recovery'][name],include_attributes=False)==ast.dump(funcs['gate'][name],include_attributes=False)
 leaf=funcs['recovery']['recovery_source_leaf'];calls=[n for n in ast.walk(leaf)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)]
 lines={name:min(n.lineno for n in calls if n.func.id==name)for name in('member','regular_target','descriptor')}
 assert lines['member']<lines['regular_target']<lines['descriptor'] and not any(n.func.id in('pin','read','open')for n in calls)
 boot=funcs['reader']['prepare_contract'];statements=[ast.unparse(n)for n in boot.body]
 verify_idx=next(i for i,x in enumerate(statements)if x=='owner_path = verify_descriptor(R, owner_descriptor)')
 read_idx=next(i for i,x in enumerate(statements)if x=='owner = read(owner_path)')
 assert verify_idx<read_idx and not any("pin(SD"in x or 'read(SD' in x for x in statements[:verify_idx])
 api=read(R/'data/phase398-attempt05-recovery-source/api-contract.json')
 assert api['source_freeze']==desc(R/pins[1][0]) and api['root_schema']=='phase398-root-pool-recovery/1'
 assert api['source_review_status']=='INDEPENDENT399_ATTEMPT05_COMPLETE_RECOVERY_SOURCE_ACCEPTED_ROOT_PENDING'and api['readback_status']=='INDEPENDENT398_ATTEMPT05_RESTORED_POOL_EXACT_TARGET_READBACK_PASS'
 for name in('map','input_pins'):check(api[name]);assert api[name]==read(R/'data/phase399-independent-repair-preparation/contract.json')['original396']['immutable395_'+('map'if name=='map'else'pins')]
 oldcontract=read(R/'data/phase395-independent-readback-source/source-contract.json');newcontract=read(R/'data/phase398-independent-readback-source/source-contract.json')
 changed=[k for k in set(oldcontract)|set(newcontract)if oldcontract.get(k)!=newcontract.get(k)]
 allowed={'schema','SOURCE_review_status','readback_status','source_freeze','recovery_source_owner','source_API','process_inspector_source','failed_capsule_manifest'}
 assert set(changed)<=allowed,changed
 for name in('process_inspector_source','failed_capsule_manifest'):
  assert{k:newcontract[name][k]for k in('size','sha256')}=={k:oldcontract[name][k]for k in('size','sha256')}
 ownread=read(R/pins[3][0])['files'];assert pins[3][0]not in{r['path']for r in ownread}
 assert newcontract['process_inspector_source']in ownread
 result=dict(schema='phase399-independent-frozen398-static-review/1',status='STATIC_PASS_CONDITIONAL_NINE_CALL_RELEASE',source_freeze=api['source_freeze'],handoff_owner=desc(R/pins[0][0]),handoff_files=433,handoff_bytes=7067200,import_closure=list(closure.values()),import_graph=graph,independent_inverse=inverses,old_accepted_kernel_conservation=conservation,F01=dict(member_line=lines['member'],physical_gate_line=lines['regular_target'],first_hash_descriptor_line=lines['descriptor'],template_actual_equal=True),F02=dict(owner_descriptor_then_strict_verifier_then_decode=True,bootstrap_start_line=boot.lineno,owner_self_reference=False),reader_contract_changed_fields=sorted(changed),api=desc(R/'data/phase398-attempt05-recovery-source/api-contract.json'),map=api['map'],input_pins=api['input_pins'],static_logical_cases=20,SUT_imports=0,SUT_calls=0,native=0,models=0,actual_pool=0,proc=0)
 save('review.json',result)
 leaves=[D/'review.json',Path(__file__).absolute(),R/'docs/phase399_frozen398_execution_binding_spec.md']
 own=[desc(p)for p in leaves];save('owned-files.json',dict(schema='phase399-static-owner/1',files=own,no_more_writes=True))
 print(json.dumps(dict(status=result['status'],review=desc(D/'review.json'),owner=desc(D/'owned-files.json'),files=len(own),bytes=sum(r['size']for r in own))))
if __name__=='__main__':
 try:main()
 except BaseException:
  if D.is_dir():save('first-failure.json',dict(traceback=traceback.format_exc(),SUT_calls=0))
  raise
