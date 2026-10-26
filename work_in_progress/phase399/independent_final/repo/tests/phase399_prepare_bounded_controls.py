"""Bind and seal the nine authorized controls; imports no SUT."""
import hashlib,json,os,stat
from pathlib import Path
R=Path(__file__).absolute().parents[1];D=R/'data/phase399-independent-execution-preparation';F=D/'fixtures'
def pin(p):
 b=p.read_bytes();return dict(size=len(b),sha256=hashlib.sha256(b).hexdigest())
def desc(p):
 s=p.lstat();assert stat.S_ISREG(s.st_mode)and s.st_nlink==1 and not any(q.is_symlink()for q in(p,*p.parents))
 return dict(path=str(p.relative_to(R)),**pin(p))
def check(root,row):
 p=root/row['path'];v=desc(p)if p.is_relative_to(R)else None
 if v is None:
  s=p.lstat();assert stat.S_ISREG(s.st_mode)and s.st_nlink==1 and not any(q.is_symlink()for q in(p,*p.parents));v=pin(p)
 assert{k:v[k]for k in('size','sha256')}=={k:row[k]for k in('size','sha256')}
 return p

def read(p):return json.loads(p.read_text())
def save(p,v):
 with p.open('x')as f:f.write(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+'\n')
def put(p,raw):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb')as f:f.write(raw)

def node(p):
 s=p.lstat();v=dict(path=str(p),kind='symlink'if stat.S_ISLNK(s.st_mode)else'file',nlink=s.st_nlink,mode=stat.S_IMODE(s.st_mode),mtime_ns=s.st_mtime_ns,inode=s.st_ino,device=s.st_dev)
 if stat.S_ISLNK(s.st_mode):v['link_target']=os.readlink(p)
 else:v.update(pin(p))
 return v

def main():
 static=read(R/'data/phase399-independent-static/review.json');assert static['status']=='STATIC_PASS_CONDITIONAL_NINE_CALL_RELEASE'
 assert not D.exists();D.mkdir();F.mkdir()
 prep=read(R/'data/phase399-independent-repair-preparation/contract.json')
 api=read(R/'data/phase398-attempt05-recovery-source/api-contract.json')
 freeze=read(R/api['source_freeze']['path']);sourcecontract=read(R/api['reader_source_contract'])
 reader=R/'tests/phase398_independent_restored_readback.py';runtime=list(freeze['import_closure'])+[desc(reader)]
 for row in runtime:check(R,row)
 saved_roots={k:v for k,v in read(R/api['MAP'])['roots'].items()if k in('failed_run','previous_run')}
 savedpins=read(R/api['INPUT_PINS'])['files']
 for row in savedpins:check(Path(saved_roots[row['root']]),row)
 assert len(savedpins)==524
 historical_names=['data/phase383-root-attempt04-partial-restore/restore-authorization.json','data/phase383-root-attempt04-partial-restore/actual-restore/restore-receipt.json']
 historical=[desc(R/n)for n in historical_names]
 assert read(R/historical_names[0])['schema']=='phase380-root-pool-recovery/1'
 assert read(R/historical_names[1])['status']=='RESTORED_EXACT_TARGET_STATE_REMAINS_FAILED_INDEPENDENT_READBACK_PENDING'
 raw=b'phase399 owned source gate input\n';physical=[];cases=[];mirrors={}
 def case(cid,logical,dispatch,expect,root=None,descriptor=None,target=(),observed=(),reads='zero',prefix='',allow=(),dirs=(),forbidden=()):
  c=dict(id=cid,logical_case=logical,dispatch=dispatch,expect=expect,root=str(root)if root else None,descriptor=descriptor,target_read_paths=[str(x)for x in target],observe_nodes=[str(x)for x in observed],target_reads=reads,exception_prefix=prefix,read_allowset=[str(x)for x in allow],directory_allowset=[str(x)for x in dirs],must_not_read=[str(x)for x in forbidden])
  cases.append(c);return c
 for kind in('ordinary','symlink','hardlink'):
  base=F/'leaf'/kind;base.mkdir(parents=True)
  operand=base/'operand.bin';peer=base/'referent.bin'
  if kind=='ordinary':put(operand,raw);observed=[operand]
  else:
   put(peer,raw)
   if kind=='symlink':operand.symlink_to(peer.name)
   else:os.link(peer,operand)
   put(base/'ordinary-snapshot.bin',raw);observed=[operand,peer]
  physical+=observed
  row=dict(path=operand.name,size=len(raw),sha256=hashlib.sha256(raw).hexdigest())
  c=case('R10-F01-'+kind,'R10','leaf','accept'if kind=='ordinary'else'reject',base,row,observed,observed,'positive'if kind=='ordinary'else'zero',''if kind=='ordinary'else('symlink member/ancestor'if kind=='symlink'else'mutable target must be regular+nlink1'),observed)
  c['actual_API']='tests/phase398_pool_recovery.py::recovery_source_leaf(root,row)'
 owner_origin=R/api['reader_source_owner'];ownerbytes=owner_origin.read_bytes();ownerpin=pin(owner_origin)
 for kind in('symlink','hardlink'):
  root=F/('reader-'+kind);modulepath=root/'tests/phase398_independent_restored_readback.py';put(modulepath,reader.read_bytes())
  operand=root/'data/phase398-independent-readback-source/source-owner.json';peer=operand.with_name('owned-referent.json');put(peer,ownerbytes)
  if kind=='symlink':operand.symlink_to(peer.name)
  else:os.link(peer,operand)
  put(operand.with_name('ordinary-owner-snapshot.json'),ownerbytes)
  history=[]
  for row in historical:
   p=root/row['path'];put(p,(R/row['path']).read_bytes());history.append(p)
  argv=[str(modulepath),'--execute','--source-owner-size',str(ownerpin['size']),'--source-owner-sha256',ownerpin['sha256']]
  for key,row in zip(('authorization','restore-receipt'),historical):argv+=['--'+key,row['path'],'--'+key+'-size',str(row['size']),'--'+key+'-sha256',row['sha256']]
  mirrors[kind]=dict(module=str(modulepath),root=str(root),module_identity=pin(modulepath),owner_origin=desc(owner_origin),owner_expected_identity=ownerpin,owner_operand=str(operand),historical_argument_files=[dict(path=str(p),**pin(p))for p in history],scope='Complete unchanged reader module, natural __file__ roots. Early negative only; original383 arguments confer no398 authority.')
  observed=[operand,peer]+history;physical+=observed
  c=case('R20-F02-'+kind,'R20','bootstrap','reject',root,None,[operand,peer],observed,'zero','no linked paths'if kind=='symlink'else'ordinary nlink1 descriptor source',[operand,peer]+history,forbidden=history)
  c.update(actual_API='tests/phase398_independent_restored_readback.py::prepare_contract() complete module mirror',mirror=kind,argv=argv)
 normal=F/'descriptor/ordinary.json';put(normal,b'{"scope":"owned component metadata only"}\n');physical.append(normal)
 c=case('R13-owner-descriptor-ordinary','R13','descriptor','accept',normal.parent,dict(path=normal.name,**pin(normal)),[normal],[normal],'positive',allow=[normal]);c['actual_API']='tests/phase398_independent_restored_readback.py::verify_descriptor(root,row) helper only'
 allowed=[Path(saved_roots[row['root']])/row['path']for row in savedpins]
 pres=Path(saved_roots['failed_run'])/'output/failed-pool-preservation';dirs={pres}
 for p in allowed:
  if p.is_relative_to(pres):dirs.update(q for q in p.parents if q==pres or q.is_relative_to(pres))
 c=case('R01-saved-complete','R01','saved','accept',target=allowed,reads='positive',allow=allowed,dirs=sorted(dirs));c['actual_API']='tests/phase395_saved_complete_evidence.py::validate_complete_saved(roots) via actual398 imported binding'
 control=sourcecontract['process_controls'];realroot=Path(saved_roots['failed_run']);controlpaths=[realroot/row['path']for row in control.values()]
 observed_values={name:read(realroot/row['path'])for name,row in control.items()}
 expected_records={name:dict(identity=control[name],**{k:value[k]for k in('parse_only','actual_oracle_processes','exit_code','process_clean_exit','abort_reason','timed_out','cleanup')})for name,value in observed_values.items()}
 expected_process=[[21970,22029],[21980,22039],dict(records=expected_records,historical_zombies=[21980,22039],pid_reuse='Historical records have no starttime; live matching PID/PGID conservatively blocks, no identity/reaping claim')]
 c=case('R15-actual-controls','R15','process','accept',realroot,target=controlpaths,reads='positive',allow=controlpaths);c.update(actual_API='tests/phase398_independent_restored_readback.py::attempt05_process_controls(roots,contract)',component_contract=dict(process_controls=control),expected_result=expected_process)
 mutantroot=F/'process-bool-int';mutated={}
 for name,row in control.items():
  value=observed_values[name]
  if name=='parse-process-result.json':value=dict(value,parse_only=1)
  p=mutantroot/row['path'];put(p,(json.dumps(value,indent=2,sort_keys=True)+'\n').encode());physical.append(p)
  mutated[name]=dict(root='failed_run',path=row['path'],**pin(p))
  original=observed_values[name];assert {k:v for k,v in value.items()if k!='parse_only'}=={k:v for k,v in original.items()if k!='parse_only'}
 mutationpaths=[mutantroot/row['path']for row in mutated.values()]
 c=case('R16-parse-bool-int','R16','process','reject',mutantroot,target=mutationpaths,observed=mutationpaths,reads='positive',prefix='actual05 parse/native process control identity',allow=mutationpaths);c.update(actual_API='tests/phase398_independent_restored_readback.py::attempt05_process_controls(roots,contract)',component_contract=dict(process_controls=mutated),mutation='parse_only JSON true -> INT1 only; native record semantic content unchanged')
 assert len(cases)==9 and {c['id']for c in cases}=={c['id']for c in prep['dynamic_candidates']}
 runner=R/'tests/phase399_bounded_public_controls.py';compile(runner.read_text(),str(runner),'exec')
 fixture_nodes=[node(p)for p in sorted(set(physical))]
 save(D/'execution-contract.json',dict(schema='phase399-nine-real-public-controls/1',source_freeze=api['source_freeze'],source_API=desc(R/'data/phase398-attempt05-recovery-source/api-contract.json'),static_review=desc(R/'data/phase399-independent-static/review.json'),preparation=desc(R/'data/phase399-independent-repair-preparation/contract.json'),runtime_source_files=runtime,recovery_import_closure=freeze['import_closure'],reader_module_identity=pin(reader),reader_mirrors=mirrors,saved_roots=saved_roots,saved_read_allowset=savedpins,saved_expected=dict(summary=read(R/api['MAP'])['complete_install'],files=savedpins),historical_cli_arguments=historical,fixture_nodes=fixture_nodes,cases=cases,maximum_top_level_API_calls=9,maximum_logical_cases=20,io_observer='Records target content open attempts without blocking them; unrelated unexpected reads/writes/processes cause harness failure, never count as SUT rejection.',main_calls=0,actual_calls=0,actual_SUT_imports=0,native=0,models=0))
 save(D/'physical-fixture-ledger.json',dict(nodes=fixture_nodes,alias_nodes_are_not_regular_owned_leaves=True,all_alias_referents_owned=True,no_links_to_production=True))
 ordinary=[];aliases=[]
 for p in sorted(D.rglob('*')):
  s=p.lstat()
  if stat.S_ISREG(s.st_mode)and s.st_nlink==1:ordinary.append(p)
  elif stat.S_ISLNK(s.st_mode)or(stat.S_ISREG(s.st_mode)and s.st_nlink!=1):aliases.append(node(p))
 ordinary +=[runner,Path(__file__).absolute(),R/'docs/phase399_frozen398_execution_binding_spec.md']
 rows=[desc(p)for p in sorted(ordinary)]
 save(D/'owned-files.json',dict(schema='phase399-execution-code-input-owner/1',files=rows,leaf_count=len(rows),byte_count=sum(r['size']for r in rows),excluded_alias_nodes=aliases,no_more_writes=True))
 for row in rows:check(R,row)
 print(json.dumps(dict(status='NINE_INPUTS_CODE_EXPECTATIONS_SEALED_NOT_EXECUTED',owner=desc(D/'owned-files.json'),contract=desc(D/'execution-contract.json'),ordinary_files=len(rows),ordinary_bytes=sum(r['size']for r in rows),alias_nodes=len(aliases),SUT_calls=0,SUT_imports=0)))
if __name__=='__main__':main()
