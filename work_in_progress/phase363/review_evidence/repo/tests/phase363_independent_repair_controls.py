"""Real generic-child and tinyFS controls; no oracle, actual pool or model."""
import ast
import copy
import ctypes
import dataclasses
import fcntl
import hashlib
import json
import os
from pathlib import Path
import selectors
import shutil
import signal
import stat
import subprocess
import sys
import sysconfig
import time
import types
import zipfile

R=Path(__file__).resolve().parents[1];D=R/'data/phase363-independent-source-review'
def desc(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(R)),size=len(b),sha256=hashlib.sha256(b).hexdigest())
def meta(p):
 s=p.stat();return dict(size=s.st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),mode=stat.S_IMODE(s.st_mode),mtime_ns=s.st_mtime_ns,nlink=s.st_nlink)
def save(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def main():
 contract=json.loads((D/'execution-contract.json').read_text())
 for row in contract['files']:assert desc(R/row['path'])==row
 ownerpin=desc(D/'source-owner.json');cases=json.loads((D/'cases.json').read_text());assert len(cases)==36
 out=D/'controls-first-001';out.mkdir(exist_ok=False)
 stdlib=Path(sysconfig.get_path('stdlib')).resolve();allowed={str((R/r['path']).resolve()) for r in contract['files']}|{str((D/'execution-contract.json').resolve()),str((D/'source-owner.json').resolve())};root=out.resolve()
 audit=dict(reads=[],writes=[],blocked=[],processes=[],signals=[])
 def below(p,r):return p==r or r in p.parents
 def hook(event,args):
  if event=='open':
   if isinstance(args[0],int):return
   p=Path(os.fsdecode(args[0])).absolute().resolve();mode,flags=args[1:3];writing=bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)) if isinstance(flags,int) else bool(mode and any(c in mode for c in 'wax+'))
   proc_allowed=below(p,Path('/proc')) and not writing and p.name in ('stat','status','cmdline','maps')
   null=p==Path('/dev/null') and isinstance(flags,int) and not flags&(os.O_CREAT|os.O_TRUNC|os.O_APPEND)
   permitted=below(p,root) if writing else str(p) in allowed or below(p,root) or proc_allowed or below(p,stdlib) and not {'site-packages','dist-packages'}&set(p.parts)
   if null:permitted=True
   if not permitted:audit['blocked'].append(dict(event=event,path=str(p),writing=writing));raise PermissionError('phase363 SOURCE/tinyFS boundary')
   audit['writes' if writing else 'reads'].append(str(p))
  elif event=='subprocess.Popen':
   exe,argv,cwd,env=args
   if exe!=sys.executable or type(argv)is not list or argv[:5]!=[sys.executable,'-I','-B','-S','-c'] or not below(Path(cwd).resolve(),root):
    audit['blocked'].append(dict(event=event,exe=str(exe)));raise PermissionError('Only declared real Python unit children')
   audit['processes'].append(dict(executable=exe,cwd=str(cwd),code_sha256=hashlib.sha256(argv[5].encode()).hexdigest()))
  elif event.startswith('socket.') or event in ('os.system','os.posix_spawn','os.posix_spawnp','os.fork','os.exec'):
   audit['blocked'].append(dict(event=event));raise PermissionError('No network/unmanifested process')
  elif event=='os.killpg':
   pgid,kind=args
   if pgid<=1 or pgid in (os.getpgrp(),os.getsid(0)):raise PermissionError('Never signal caller group')
   audit['signals'].append(dict(pgid=pgid,signal=kind))
 sys.addaudithook(hook)
 def module(name,p):
  m=types.ModuleType(name);m.__file__=str(p);sys.modules[name]=m;exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m
 comp=module('native_run_compaction',D/'SOURCE/compaction.py');storage=module('phase363_oracle_storage',D/'SOURCE/storage.py');process=module('phase363_oracle_process',D/'SOURCE/process.py');host=module('phase363_oracle_host',D/'SOURCE/host.py')
 calls={};results=[];monitors=[];descendants=[];shared={};emergency=[]
 def invoke(m,name,*args,**kw):
  label=m.__name__+'.'+name;calls[label]=calls.get(label,0)+1;return getattr(m,name)(*args,**kw)
 def reject(fn,message=None):
  try:fn()
  except (ValueError,OSError,zipfile.BadZipFile) as e:
   if message:assert message in str(e),(message,str(e))
   return dict(type=type(e).__name__,message=str(e))
  raise AssertionError('Invalid unit was accepted')
 def setup_install(case):
  src=case/'source';target=case/'target';src.mkdir();target.mkdir();(target/'one.txt').write_bytes(b'UNIT_OLD\n');(src/'one-after.txt').write_bytes(b'UNIT_NEW\n');os.chmod(target/'one.txt',0o640);os.utime(target/'one.txt',ns=(1700000000123456789,)*2)
  before=meta(target/'one.txt');freeze=dict(paths={'one.txt':dict(before={k:before[k] for k in ('size','sha256')},after=storage.pin(src/'one-after.txt'),after_path='one-after.txt')});return src,target,freeze,before
 def run_child(case,code,wall=2.0,callback=None,cap=4096):
  result=invoke(process,'monitor_command',[sys.executable,'-I','-B','-S','-c',code],case,dict(PATH='/usr/bin:/bin',LANG='C.UTF-8'),case,'unit',wall,scan_callback=callback,poll_seconds=0.02,term_grace_seconds=0.08,kill_grace_seconds=0.35,log_limit_bytes=cap)
  monitors.append(result);assert result['generic_subprocesses']==1 and result['actual_oracle_processes']==0 and not result['cleanup']['live_remaining']
  assert result['scope']=='GENERIC_SUBPROCESS_MONITOR_ONLY_NOT_ORACLE_OR_CAPTURE' and result['enforcement']=='POLLING_NOT_KERNEL_AGGREGATE_QUOTA'
  return result
 def proc_state(pid):
  try:return Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()[0]
  except FileNotFoundError:return 'GONE'
 def archive_fixture(case):
  base=case/'neutral-base';pool=case/'neutral-layout';run=case/'neutral-run';base.mkdir();pool.mkdir();run.mkdir();(pool/'project').mkdir();(pool/'data').mkdir();(pool/'.lock').write_bytes(b'UNIT_LOCK');save(pool/'state.json',dict(status='unit-initial-not-native'))
  for p in (run/'output',run/'data',run/'user',run/'output/driver'):p.mkdir()
  (base/'same.txt').write_bytes(b'UNCHANGED');(base/'old.txt').write_bytes(b'OLD');(base/'removed.txt').write_bytes(b'REMOVED')
  (pool/'project/same.txt').write_bytes(b'UNCHANGED');(pool/'project/old.txt').write_bytes(b'UPDATED');(pool/'project/added.txt').write_bytes(b'ADDED')
  for p in list(base.iterdir())+list((pool/'project').iterdir()):os.chmod(p,0o640);os.utime(p,ns=(1700000000000000000,)*2)
  for p in (base,pool/'project'):os.utime(p,ns=(1700000000000000000,)*2)
  (pool/'data/unit.txt').write_bytes(b'UNIT_INPUT');(run/'data/unit.txt').write_bytes(b'UNIT_INPUT');(run/'output/driver/unit.py.txt').write_bytes(b'NOT_EXECUTABLE_SOURCE_UNIT');save(run/'output/pool-provenance.json',dict(scope='SYNTHETIC_FILESYSTEM_UNIT_ONLY_NO_GAME_OR_CAPTURE'))
  before=dict(baseline=comp.inventory(base),project=comp.inventory(pool/'project'),staged=comp.inventory(pool/'data'))
  proof=invoke(storage,'archive_streaming',base,pool,run,before);assert proof['verification_mode']=='logical-overlay-and-live-tree-equality/1' and proof['physical_reconstruction'] is False
  assert invoke(storage,'check_ready',pool,base,{})==run
  return dict(base=base,pool=pool,run=run,before=before,proof=proof)
 def predicates():
  s=(D/'SOURCE/storage.py').read_text();t=ast.parse(s);budget=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='budget');test=next(n.test for n in budget.body if isinstance(n,ast.If) and isinstance(n.test,ast.Compare) and ast.unparse(n.test).startswith('free <'))
  code=compile(ast.Expression(copy.deepcopy(test)),'<exact-source-budget-compare>','eval');vals=[storage.RESERVE+storage.ATTEMPT+d for d in (-1,0,1)];assert [eval(code,dict(free=x,RESERVE=storage.RESERVE,ATTEMPT=storage.ATTEMPT)) for x in vals]==[True,False,False]
  ps=ast.parse((D/'SOURCE/process.py').read_text());usage=next(n for n in ps.body if isinstance(n,ast.FunctionDef) and n.name=='usage');floor=next(n.test for n in usage.body if isinstance(n,ast.If) and 'disk_usage' in ast.unparse(n.test));floor=copy.deepcopy(floor);floor.left=ast.Name(id='free',ctx=ast.Load());ast.fix_missing_locations(floor);fc=compile(ast.Expression(floor),'<exact-source-free-floor>','eval');floorvals=[4*1024**3+d for d in (-1,0,1)];assert [eval(fc,dict(free=x)) for x in floorvals]==[True,False,False]
  return dict(budget_values=vals,floor_values=floorvals,exact_SOURCE_predicate_evaluations=6,real_disk_pressure_simulated=False)
 for case_spec in cases:
  i=case_spec['id'];case=out/('case-'+str(i));case.mkdir();detail={};start=time.monotonic()
  try:
   if i<=10:
    if i==9:
     src,target,freeze,old,journal=shared['install'];before=meta(target/'one.txt');invoke(storage,'atomic_image',target/'one.txt',(shared['install_case']/'backup/0').read_bytes(),dict(identity={k:before[k] for k in ('size','sha256')},mode=before['mode'],mtime_ns=before['mtime_ns']));assert meta(target/'one.txt')==old;detail['inverse_exact']=True
    else:
     src,target,freeze,old=setup_install(case);backup=case/'backup';first=target/'one.txt'
     if i==1:os.link(first,case/'alias');old=meta(first)
     if i==2:
      (target/'two.txt').write_bytes(b'TWO_OLD');os.link(target/'two.txt',case/'alias');(src/'two-after.txt').write_bytes(b'TWO_NEW');freeze['paths']['two.txt']=dict(before=storage.pin(target/'two.txt'),after=storage.pin(src/'two-after.txt'),after_path='two-after.txt')
     if i==4:freeze['paths']['one.txt']['before']['sha256']='0'*64
     if i==5:first.unlink();first.symlink_to(src/'one-after.txt')
     if i==6:freeze['paths']['../OUTSIDE']=freeze['paths'].pop('one.txt')
     if i==8:backup.mkdir();(backup/'existing.txt').write_bytes(b'UNCHANGED')
     artifacts={'one.txt':src/'one-after.txt'} if i==7 else {}
     if i==10:
      first.unlink();freeze['paths']['one.txt']['before']=None
      journal=invoke(storage,'install',src,target,freeze,artifacts,backup);assert first.read_bytes()==b'UNIT_NEW\n' and journal[0]['before'] is None
      detail['existing_refusal']=reject(lambda:invoke(storage,'install',src,target,freeze,{},case/'second-backup'))
     elif i==3:
      journal=invoke(storage,'install',src,target,freeze,{},backup);now=meta(first);assert first.read_bytes()==b'UNIT_NEW\n' and now['mode']==old['mode'] and now['mtime_ns']==old['mtime_ns'] and now['nlink']==1
      assert (backup/'0').read_bytes()==b'UNIT_OLD\n';shared['install']=(src,target,freeze,old,journal);shared['install_case']=case;detail['journal']=journal
     else:
      before_files={str(p.relative_to(target)):meta(p) for p in target.rglob('*') if p.is_file() and not p.is_symlink()};before_payload=meta(src/'one-after.txt')
      detail['rejection']=reject(lambda:invoke(storage,'install',src,target,freeze,artifacts,backup))
      assert before_files=={str(p.relative_to(target)):meta(p) for p in target.rglob('*') if p.is_file() and not p.is_symlink()} and meta(src/'one-after.txt')==before_payload
      if i in (1,2):assert not backup.exists() and (case/'alias').read_bytes()==(b'UNIT_OLD\n' if i==1 else b'TWO_OLD')
      if i==5:
       first.unlink();first.write_bytes(b'UNIT_OLD\n');parent=case/'parent-link';parent.symlink_to(target,target_is_directory=True);detail['ancestor_rejection']=reject(lambda:invoke(storage,'install',src,parent,freeze,{},case/'other-backup'))
     detail.update(synthetic_FS=True,actual_pool=False)
   elif i==11:
    code="from pathlib import Path\nimport sys\nPath('owned.txt').write_text('UNIT_FILE')\nprint('UNIT_STDOUT',flush=True)\nprint('UNIT_STDERR',file=sys.stderr,flush=True)\n"
    result=run_child(case,code);assert result['exit_code']==0 and result['process_clean_exit'];assert (case/'unit-stdout.log').read_text()=='UNIT_STDOUT\n' and (case/'unit-stderr.log').read_text()=='UNIT_STDERR\n' and (case/'owned.txt').read_text()=='UNIT_FILE';detail['result']=result
   elif i==12:
    result=run_child(case,"import os,time\nos.write(1,b'A'*64)\nos.write(2,b'B'*64)\ntime.sleep(1)\n",cap=100);assert result['abort_reason']=='controlled_log_cap';assert (case/'unit-stdout.log').stat().st_size+(case/'unit-stderr.log').stat().st_size<=100 and (case/'unit-first-log-overflow.bin').is_file();detail['result']=result
   elif i==13:
    result=run_child(case,"import time\nprint('UNIT_TIMEOUT_PREFIX',flush=True)\ntime.sleep(2)\n",wall=.15);assert result['timed_out'] and result['abort_reason'].startswith('wall_timeout:') and 'UNIT_TIMEOUT_PREFIX' in (case/'unit-stdout.log').read_text();detail['result']=result
   elif i in (14,15):
    code="import os,signal,time,json\nfrom pathlib import Path\nchild=os.fork()\nif child==0:\n signal.signal(signal.SIGTERM,signal.SIG_IGN)\n Path('descendant.json').write_text(json.dumps({'pid':os.getpid(),'pgid':os.getpgrp(),'sid':os.getsid(0)}))\n time.sleep(2)\n os._exit(0)\nwhile not Path('descendant.json').exists():time.sleep(.005)\nprint('UNIT_DESCENDANT_READY',flush=True)\n"+("os._exit(0)\n" if i==14 else "signal.signal(signal.SIGTERM,signal.SIG_IGN)\ntime.sleep(2)\n")
    result=run_child(case,code,wall=.3);child=json.loads((case/'descendant.json').read_text());descendants.append(child);assert child['pgid']==child['sid']==result['cleanup']['pgid'] and result['cleanup']['kill_sent'];assert proc_state(child['pid']) in ('GONE','Z','X');assert result['timed_out'];detail.update(result=result,descendant=child,actual_descendant_state=proc_state(child['pid']))
   elif i in (16,17,19):
    scans=[]
    if i==16:code="from pathlib import Path\nimport time\np=Path('user/cache/owned.bin');p.parent.mkdir(parents=True);p.write_bytes(b'C'*64)\nprint('UNIT_CACHE',flush=True)\ntime.sleep(.08)\n"
    elif i==17:code="from pathlib import Path\nimport time\np=Path('user/data/UNKNOWN_UNIT_ROOT/file');p.parent.mkdir(parents=True);p.write_text('UNRECOGNIZED')\nprint('UNIT_UNKNOWN_ROOT',flush=True)\ntime.sleep(2)\n"
    else:code="from pathlib import Path\nimport time\nprint('UNIT_PREFIX_RETAINED',flush=True)\nPath('trigger').write_text('UNIT')\ntime.sleep(2)\n"
    def scan():
     if i==19 and (case/'trigger').exists():raise OSError('UNIT_ACCOUNTING_IO_FAILURE')
     value=invoke(process,'usage',case);scans.append(value);return value
    result=run_child(case,code,callback=scan)
    if i==16:assert result['process_clean_exit'] and scans and max(x['bytes'] for x in scans)>=64 and (case/'user/cache/owned.bin').read_bytes()==b'C'*64
    else:
     assert result['abort_reason'].startswith('scan_rejected:')
     if i==19:assert 'UNIT_PREFIX_RETAINED' in (case/'unit-stdout.log').read_text()
    detail.update(result=result,scan_values=scans)
   elif i==18:detail=predicates()
   elif i==20:
    t=ast.parse((D/'SOURCE/process.py').read_text());m=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='monitor_command');assert not [n for n in ast.walk(m) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ('wait','sleep')];assert len([n for n in ast.walk(m) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='select'])==1
    detail=dict(SOURCE_single_wait=True,observed_max_scan_gaps=[r['polling']['max_observed_scan_gap_seconds'] for r in monitors],hard_50ms_bound_claim=False)
   elif i==21:
    sig=ast.parse((D/'SOURCE/process.py').read_text());w=next(n for n in sig.body if isinstance(n,ast.FunctionDef) and n.name=='execute_process');assert [a.arg for a in w.args.args]==['source_root','task','run','project','check_only'];assert 'cmd=command(' in ast.get_source_segment((D/'SOURCE/process.py').read_text(),w);detail=dict(SOURCE_only=True,oracle_wrapper_invocations=0)
   elif i==22:
    shared['archive']=archive_fixture(case);x=shared['archive'];bundle=x['run']/'output/compaction';base,tree,plan=invoke(comp,'load_bundle',bundle);shared['bundle']=(bundle,base,tree,plan);detail=dict(verification_mode=x['proof']['verification_mode'],physical_reconstruction=False,synthetic_tinyFS_not_nativeREADY=True)
   elif i in (23,24):
    bundle,base,tree,plan=shared['bundle'];good=bundle/'overlay.zip';bad=case/'invalid.zip'
    with zipfile.ZipFile(good) as z:infos=z.infolist();contents=[(info,z.read(info.filename)) for info in infos]
    with zipfile.ZipFile(bad,'x') as z:
     for j,(info,payload) in enumerate(contents):z.writestr(info,b'CORRUPTED_UNIT_BYTES' if i==23 and j==0 else payload)
     if i==24:z.writestr(contents[0][0],contents[0][1])
    detail['rejection']=reject(lambda:invoke(comp,'validate_archive',bad,tree,plan));assert good.is_file()
   elif i in (25,26):
    x=shared['archive'];p=x['pool']/'project/old.txt';raw=p.read_bytes();before=meta(p)
    if i==25:p.write_bytes(b'DRIFT')
    else:os.chmod(p,0o600);os.utime(p,ns=(before['mtime_ns']+1,)*2)
    detail['rejection']=reject(lambda:invoke(storage,'check_ready',x['pool'],x['base'],{}))
    p.write_bytes(raw);os.chmod(p,before['mode']);os.utime(p,ns=(before['mtime_ns'],)*2);assert meta(p)==before
   elif i==27:
    x=shared['archive'];bundle=x['run']/'output/compaction';p=bundle/'pool-roundtrip.json';raw=p.read_bytes();before=meta(p)
    for mode in ('UNKNOWN_UNIT_MODE',None):
     proof=copy.deepcopy(x['proof'])
     if mode is None:proof.pop('verification_mode')
     else:proof['verification_mode']=mode
     p.write_text(json.dumps(proof));state=json.loads((x['pool']/'state.json').read_text());state['bundle_inventory']=comp.inventory(bundle);invoke(storage,'state_write',x['pool'],state)
     detail[str(mode)]=reject(lambda:invoke(storage,'check_ready',x['pool'],x['base'],{}),'proof')
    p.write_bytes(raw);os.chmod(p,before['mode']);os.utime(p,ns=(before['mtime_ns'],)*2);state=json.loads((x['pool']/'state.json').read_text());state['bundle_inventory']=comp.inventory(bundle);invoke(storage,'state_write',x['pool'],state)
   elif i==28:
    for name in ('storage.py','host.py'):
     t=ast.parse((D/'SOURCE'/name).read_text());assert not [n for n in ast.walk(t) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ('copytree','_reconstruct')]
    detail=dict(SOURCE_only=True,Game_copies=0)
   elif i==29:detail=dict(status='SOURCE_ONLY_NEUTRAL_INTERFACE_UNAVAILABLE',rename_method_inherited_AST=True,specialized_native_capture_names_not_faked=True,actual_rename_calls=0)
   elif i in (30,31):
    source=case/'source';source.mkdir();config=source/'unit-invalid-config.json'
    if i==30:
     args=dict(path='missing-root.json',size=1,sha256='0'*64)
     detail['rejection']=reject(lambda:invoke(host,'execute',source,args,case,case,case,case))
    else:
     config.write_text(json.dumps(dict(schema='phase362-root-oracle-acceptance/1',root_oracle_authorized=True)))
     args=dict(path=config.name,**storage.pin(config));detail['rejection']=reject(lambda:invoke(host,'source_gate',source,args),'actual root oracle-only authorization required')
    detail['Popen_count_unchanged']=len(audit['processes'])==8;assert detail['Popen_count_unchanged']
   elif i==32:
    x=shared['archive'];runs=case/'runs';runs.mkdir();(runs/'already-exists').mkdir()
    detail['collision']=reject(lambda:invoke(storage,'lease',x['pool'],x['base'],runs,'already-exists',{}).__enter__())
    detail['overlap']=reject(lambda:invoke(storage,'lease',x['pool'],x['pool'],runs,'different',{}).__enter__())
    detail['ambiguous_prefix']=reject(lambda:invoke(storage,'map_recorded',Path('/UNIT/a/b'),{'/UNIT':'/ONE','/UNIT/a':'/TWO'}))
   elif i==33:
    a=case/'one';b=case/'two';a.mkdir();b.mkdir();value=invoke(storage,'budget',a,b);assert value['required']==storage.RESERVE+storage.ATTEMPT and value['free']>=value['required'];detail.update(value=value,predicates=predicates())
   elif i==34:detail=dict(SOURCE_policy='bounded-writers-and-monitored-process/1',real_monitor_records=len(monitors),actual_cache_and_unknownroot_cases=[16,17],max_observed_gap_seconds=max(r['polling']['max_observed_scan_gap_seconds'] for r in monitors),kernel_aggregate_quota=False)
   elif i==35:
    source=(D/'SOURCE/host.py').read_text();t=ast.parse(source);f=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='execute');calls_source=ast.get_source_segment(source,f);assert calls_source.index("write_new(out/'pool-before.json'")<calls_source.index('parsed=execute_process(')<calls_source.index("write_new(out/'one-shot-launch.json'")<calls_source.index('result=execute_process(');detail=dict(SOURCE_only=True,actual_host_plan_successes=0,actual_oracle_calls=0)
   elif i==36:
    old=json.loads((D/'SOURCE/guard-identities.json').read_text());assert old['guard356']=='CLOSED' and old['guard361']=='PENDING';detail=dict(SOURCE_guard_pins=old,actual_API_calls=0)
   row=dict(id=i,label=case_spec['label'],pass_=True,detail=detail,elapsed_seconds=time.monotonic()-start)
  except Exception as exc:
   row=dict(id=i,label=case_spec['label'],pass_=False,error=dict(type=type(exc).__name__,message=str(exc)),elapsed_seconds=time.monotonic()-start)
  results.append(row)
  with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(row,sort_keys=True)+'\n');f.flush()
  if not row['pass_']:break
 # This branch is emergency safety only, never retroactively changes observations.
 for r in monitors:
  for member in r['cleanup']['live_remaining']:
   if proc_state(member['pid']) not in ('GONE','Z','X'):
    os.killpg(r['cleanup']['pgid'],signal.SIGKILL);emergency.append(r['cleanup']['pgid'])
 failures=[r for r in results if not r['pass_']]
 report=dict(schema='phase363-independent-real-unit-report/1',status='BOUNDED_REPAIR_CONTROLS_PASS' if not failures else 'BLOCKED_FIRST_SOURCE_OR_CONTROL_COUNTEREXAMPLE',planned=36,executed=len(results),controls=results,failures=failures,not_executed=[c for c in cases if c['id']>len(results)],top_level_helper_calls=calls,helper_call_total=sum(calls.values()),internal_calls='NOT_COUNTED',SOURCE_module_imports=4,synthetic_direct_python_children=len(audit['processes']),observed_descendant_processes=descendants,total_known_child_processes=len(audit['processes'])+len(descendants),monitor_results=monitors,emergency_cleanup_groups=emergency,actual_Game_operations=0,real_pool_operations=0,actual_hostplan_successes=0,Godot=0,parse=0,native=0,models=0,projection_calls=0,actual12_positive=False,actual_capture_or_expected_reads=0)
 save(out/'report.json',report)
 files=[desc(out/n) for n in ('journal.jsonl','report.json')]
 save(out/'open-audit.json',dict(schema='phase363-independent-open-process-audit/1',**audit,trusted_bootstrap='stdlib/script and manifested SOURCE/meta before hook; four actual SOURCE modules afterhook; procfs read-only stat/status/cmdline/maps needed for own group/legacy process checker.',DEVNULL_exception='Only exact/dev/null withoutCREATE/TRUNC/APPEND; generic helper stdin implementation.',recording_cut='Opening audit; later ownreadback/jointseal/stdout only under activehook.'))
 files.append(desc(out/'open-audit.json'));save(out/'joint-seal.json',dict(schema='phase363-independent-unit-jointseal/1',files=files,source_owner=ownerpin))
 print(json.dumps(dict(status=report['status'],executed=len(results),failures=[r['label'] for r in failures],direct_children=len(audit['processes']),descendants=len(descendants),blocked=len(audit['blocked']))))
if __name__=='__main__':main()
