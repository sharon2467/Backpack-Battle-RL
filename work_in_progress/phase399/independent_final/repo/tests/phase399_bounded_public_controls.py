"""Nine sealed real public API controls. No recovery/native/process operations."""
import argparse,ast,contextlib,datetime,fcntl,hashlib,importlib.util,json,math,os,re,selectors,shutil,signal,stat,subprocess,sys,time,traceback,zipfile
from pathlib import Path
R=Path(__file__).absolute().parents[1]
P=R/'data/phase399-independent-execution-preparation'
D=R/'data/phase399-independent-dynamic-first-001'
sys.dont_write_bytecode=True
CURRENT=None;EVENTS=[];PROFILE={};SUT_PATHS=set()

def pin(p):
 b=p.read_bytes();return dict(size=len(b),sha256=hashlib.sha256(b).hexdigest())
def check(root,row):
 p=root/row['path'];s=p.lstat()
 assert stat.S_ISREG(s.st_mode)and s.st_nlink==1 and not any(q.is_symlink()for q in(p,*p.parents))
 assert pin(p)=={k:row[k]for k in('size','sha256')};return p

def save(name,value):
 with(D/name).open('x')as f:f.write(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')
def readable(value):
 if isinstance(value,Path):return str(value)
 if isinstance(value,set):return sorted(value)
 if isinstance(value,tuple):return[readable(x)for x in value]
 if isinstance(value,list):return[readable(x)for x in value]
 if isinstance(value,dict):return{k:readable(v)for k,v in value.items()}
 return value

def node(p):
 s=p.lstat();v=dict(path=str(p),kind='symlink'if stat.S_ISLNK(s.st_mode)else'file',nlink=s.st_nlink,mode=stat.S_IMODE(s.st_mode),mtime_ns=s.st_mtime_ns,inode=s.st_ino,device=s.st_dev)
 if stat.S_ISLNK(s.st_mode):v['link_target']=os.readlink(p)
 else:v.update(pin(p))
 return v

def audit(event,args):
 if CURRENT is None:return
 if event=='open':
  path,mode,flags=args
  if isinstance(path,int):
   EVENTS.append(dict(event=event,fd=path,mode=mode,flags=flags));raise PermissionError('harness: unexpected fd content open')
  path=str(Path(os.fsdecode(path)).absolute())
  write=(isinstance(mode,str)and any(x in mode for x in'wax+'))or(type(flags)is int and bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)))
  EVENTS.append(dict(event='open',path=path,write=bool(write),mode=mode,flags=flags))
  if write:raise PermissionError('harness: unexpected SUT write')
  if path not in CURRENT['read_allowset']:raise PermissionError('harness: read outside sealed allowset: '+path)
 if event in('subprocess.Popen','os.system','os.posix_spawn','socket.connect','socket.bind','os.kill','os.killpg'):
  EVENTS.append(dict(event=event,blocked=True));raise PermissionError('harness: prohibited process/network operation')
 if event in('os.listdir','os.scandir'):
  path=str(Path(os.fsdecode(args[0])).absolute());EVENTS.append(dict(event=event,path=path))
  if path not in CURRENT['directory_allowset']:raise PermissionError('harness: directory scan outside saved allowset')
 if event in('os.rename','os.remove','os.rmdir','os.mkdir','os.chmod','os.utime','os.link','os.symlink','os.truncate'):
  EVENTS.append(dict(event=event,blocked=True));raise PermissionError('harness: unexpected metadata mutation')

def profile(frame,event,arg):
 if event=='call'and frame.f_code.co_filename in SUT_PATHS:
  key=frame.f_code.co_filename+'::'+frame.f_code.co_name;PROFILE[key]=PROFILE.get(key,0)+1

def module(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def run():
 global CURRENT,EVENTS,PROFILE
 config=json.loads((P/'execution-contract.json').read_text())
 assert not D.exists();D.mkdir()
 save('invocation.json',dict(runner=str(Path(__file__).absolute()),runner_pin=pin(Path(__file__)),argv=sys.argv,pycache_prefix=sys.pycache_prefix,bytecode_writes=sys.dont_write_bytecode,maximum_top_calls=9,source_freeze=config['source_freeze']))
 results=[];imports=[];failure=None
 try:
  own=json.loads((P/'owned-files.json').read_text())
  for row in own['files']:check(R,row)
  for row in config['runtime_source_files']:check(R,row)
  for row in config['saved_read_allowset']:
   check(Path(config['saved_roots'][row['root']]),row)
  for row in config['fixture_nodes']:
   assert node(Path(row['path']))==row
  assert len(config['cases'])==9
  sys.path.insert(0,str(R/'tests'))
  rec=module('phase399_actual398_recovery',R/'tests/phase398_pool_recovery.py');imports.append(str(R/'tests/phase398_pool_recovery.py'))
  reader=module('phase399_actual398_reader',R/'tests/phase398_independent_restored_readback.py');imports.append(str(R/'tests/phase398_independent_restored_readback.py'))
  mirrors={}
  for key,row in config['reader_mirrors'].items():
   mirrors[key]=module('phase399_reader_'+key,Path(row['module']));imports.append(row['module'])
  runtime_paths={str(R/row['path'])for row in config['runtime_source_files']}
  runtime_paths.update(row['module']for row in config['reader_mirrors'].values())
  SUT_PATHS.update(runtime_paths)
  actual_modules={str(Path(getattr(m,'__file__','')).absolute())for m in list(sys.modules.values())if getattr(m,'__file__',None)}
  assert all(str(R/row['path'])in actual_modules for row in config['recovery_import_closure'])
  #Every source is pinned again before first actual API call, after imports.
  for row in config['runtime_source_files']:check(R,row)
  for row in config['reader_mirrors'].values():assert pin(Path(row['module']))==config['reader_module_identity']
  save('imports.json',dict(direct_module_loads=imports,actual_unique_SUT_module_files=sorted(runtime_paths),unique_SUT_module_count=len(runtime_paths),main_calls=0,source_files_post_import_pinned=True))
  sys.addaudithook(audit)
  for index,case in enumerate(config['cases'],1):
   before=[node(Path(p))for p in case['observe_nodes']]
   EVENTS=[];PROFILE={};caught=None;value=None;old_argv=sys.argv[:]
   if case['dispatch']=='bootstrap':sys.argv=case['argv']
   started=time.monotonic();CURRENT=case;sys.setprofile(profile)
   try:
    if case['dispatch']=='leaf':value=rec.recovery_source_leaf(Path(case['root']),case['descriptor'])
    elif case['dispatch']=='bootstrap':value=mirrors[case['mirror']].prepare_contract()
    elif case['dispatch']=='descriptor':value=reader.verify_descriptor(Path(case['root']),case['descriptor'])
    elif case['dispatch']=='saved':value=rec.validate_complete_saved({k:Path(v)for k,v in config['saved_roots'].items()})
    elif case['dispatch']=='process':value=reader.attempt05_process_controls({'failed_run':Path(case['root'])},case['component_contract'])
    else:raise AssertionError('unbound dispatch')
   except BaseException as exc:caught=exc
   finally:
    sys.setprofile(None);CURRENT=None;sys.argv=old_argv
   elapsed=time.monotonic()-started
   after=[node(Path(p))for p in case['observe_nodes']]
   event_rows=list(EVENTS);counts=dict(PROFILE)
   output=dict(id=case['id'],logical_case=case['logical_case'],top_level_call_index=index,actual_API=case['actual_API'],events=event_rows,selected_SUT_function_calls=counts,exception=None if caught is None else dict(type=type(caught).__name__,message=str(caught)),result=readable(value),before=before,after=after,elapsed_seconds=elapsed,assertions_passed=False)
   save('call-%02d-raw.json'%index,output)
   assert before==after,'fixture metadata or bytes changed'
   opens=[e for e in event_rows if e['event']=='open']
   assert not any(e.get('write')or e.get('blocked')for e in event_rows),'unexpected mutating/prohibited operation'
   if case['expect']=='reject':
    assert type(caught)is ValueError and str(caught).startswith(case['exception_prefix']),('wrong rejection',caught)
   else:
    assert caught is None,repr(caught)
   targetopens=[e for e in opens if e.get('path')in case['target_read_paths']]
   if case['target_reads']=='zero':assert not targetopens,'target content read before physical rejection'
   if case['target_reads']=='positive':assert targetopens,'missing genuine content read'
   assert not any(e.get('path')in case['must_not_read']for e in opens),'downstream authority bytes read'
   if case['dispatch']in('leaf','descriptor')and case['expect']=='accept':assert value==Path(case['root'])/case['descriptor']['path']
   if case['dispatch']=='saved':
    assert value==config['saved_expected'],'genuine saved association or full ledger drift'
   if case['dispatch']=='process'and case['expect']=='accept':
    assert readable(value)==case['expected_result'],'actual saved process facts differ'
   result=dict(id=case['id'],logical_case=case['logical_case'],status='PASS',expected_outcome=case['expect'],top_level_API_calls=1,target_content_open_attempts=len(targetopens),total_content_open_attempts=len(opens),selected_delegated_SUT_calls=counts,raw='call-%02d-raw.json'%index)
   results.append(result);save('call-%02d-result.json'%index,result)
  for row in config['runtime_source_files']:check(R,row)
  for row in config['fixture_nodes']:assert node(Path(row['path']))==row
 except BaseException as exc:
  failure=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc(),completed_calls=len(results),current_call=None if len(results)>=len(config['cases'])else config['cases'][len(results)]['id'],first_failure=True,retries=0)
  save('first-failure.json',failure)
 outcome=dict(schema='phase399-real-public-component-results/1',status='PASS_NINE_REAL_PUBLIC_COMPONENT_CALLS'if failure is None else'BLOCKED_FIRST_DYNAMIC_OR_HARNESS_FAILURE',results=results,failure=failure,top_level_API_calls=len(list(D.glob('call-*-raw.json'))),logical_dynamic_cases=len({x['logical_case']for x in results}),accept=sum(x['expected_outcome']=='accept'for x in results),reject=sum(x['expected_outcome']=='reject'for x in results),native=0,models=0,Godot=0,actual_pool=0,proc_inspection=0,restore=0,READY=0,whole_prepare_positive=False,whole_recover_positive=False,no_more_calls=True)
 save('result.json',outcome);print(json.dumps(dict(status=outcome['status'],top_level_API_calls=outcome['top_level_API_calls'],completed=len(results),failure=failure)))
 return 0 if failure is None else 1
if __name__=='__main__':raise SystemExit(run())
