"""One read-only verifier and isolated public validation; no model construction."""
import argparse,dataclasses,hashlib,importlib,json,math,os,random,re,signal,stat,struct,sys,time,types,typing
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/'data/phase555-independent-package-source-v2'
PACKAGE=Path('/workspace/backpack-github-receipt-clone-20261030/python_engine/experimental_nonking')
OUT=ROOT/'data/phase555-independent-package-first-001'
TRUSTED='3ba9018b2e2c4b025d3d0ff8422c50e59d04e5fe7bc2b6b7f27e8a51ffdf1e13'
COUNTS={};STAGE='preflight'
FORBIDDEN={'initialize','initialize_squirrel','initialize_experimental_nonking','_initialize_fixture','run_batch','CombatEngine.__init__','HeadlessBattle.__init__','CombatRandom.__init__','GodotPCGInteger.__init__','OriginalRNG.__init__','CombatEngine.prepare_only','CombatEngine.activate_from_checkpoint','CombatEngine.run','CombatEngine.step','HeadlessBattle.run','HeadlessBattle.step'}
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT))if p.is_relative_to(ROOT)else str(p),size=len(b),sha256=sha(b))
def save(n,v):
 p=OUT/n;p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n');return pin(p)
def frames(tb):
 while tb is not None:yield dict(file=tb.tb_frame.f_code.co_filename,line=tb.tb_lineno,function=tb.tb_frame.f_code.co_name);tb=tb.tb_next

def main():
 global STAGE
 OUT.mkdir(exist_ok=False);t=time.monotonic();refs=[];status='FAILED';imports=[];forbidden=[]
 try:
  refs=json.loads((PLAN/'pins.json').read_bytes())['files']
  for row in refs:assert pin(ROOT/row['path'])==row,('beforepin',row['path'])
  save('before.json',refs)
  allowed={str((ROOT/x['path']).resolve())for x in refs}|{str((PLAN/'pins.json').resolve())}
  original_files=sorted(str(p.relative_to(PACKAGE))for p in PACKAGE.rglob('*')if p.is_file())
  assert len(original_files)==21
  sys.dont_write_bytecode=True;sys.pycache_prefix=str(OUT/'unused-bytecode-cache');sys.path.insert(0,str(PACKAGE))
  def audit(event,args):
   if event=='open':
    if isinstance(args[0],int):return
    p=str(Path(os.fsdecode(args[0])).resolve());mode=args[1];flags=args[2]
    if p.startswith(str(OUT)+os.sep):return
    if(isinstance(mode,str)and any(c in mode for c in'wa+'))or(isinstance(flags,int)and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)):raise PermissionError('outside-output write '+p)
    if p not in allowed:raise PermissionError('unlisted read '+p)
    if(STAGE=='headless_import'or STAGE.startswith('public_validate'))and not p.startswith(str(PACKAGE)+os.sep):raise PermissionError('candidate read outside remote package '+p)
   if event in('subprocess.Popen','os.system','socket.connect'):raise PermissionError('external execution denied')
  prefix=str(PACKAGE)+os.sep
  def profile(frame,event,arg):
   if event!='call' or not frame.f_code.co_filename.startswith(prefix):return
   name=frame.f_code.co_qualname;relative=frame.f_code.co_filename[len(prefix):]
   if name in FORBIDDEN or name in('verify','validate_experimental_nonking_layout','validate_fixture','model_source_hashes'):
    k=relative+':'+name;COUNTS[k]=COUNTS.get(k,0)+1
   if name in FORBIDDEN:forbidden.append(dict(file=relative,function=name));raise AssertionError('forbidden constructor/model/RNG entry '+name)
  sys.setprofile(profile)
  STAGE='verifier_import';v=importlib.import_module('verify_manifest');assert Path(v.__file__).resolve()==PACKAGE/'verify_manifest.py'
  assert not any(x=='headless'or x.startswith(('native_replay_v7','native_replay_v8'))for x in sys.modules)
  STAGE='verifier_call';verified=v.verify(PACKAGE,TRUSTED);save('verifier-result.json',verified)
  assert verified==dict(status='VERIFIED_LISTED_PACKAGE_BYTES',files=20,source_files=15,manifest_sha256=TRUSTED,battle_modules_imported=0,battle_calls=0)
  sys.addaudithook(audit)
  STAGE='headless_import';h=importlib.import_module('headless')
  for name,mod in list(sys.modules.items()):
   if name in('headless','original_rng','godot_pcg_integer','verify_manifest')or name.startswith(('native_replay_v7','native_replay_v8')):
    p=Path(mod.__file__).resolve();assert str(p)in allowed and p.is_relative_to(PACKAGE),(name,p)
    imports.append(dict(name=name,path=str(p),sha256=sha(p.read_bytes())))
  validated=[]
  for name,count,kinds in [('Wolpertinger',22,{1,11,164,199,201,231}),('Enchanted-Weapons',24,{1,11,14,22,32,231,233,234,385})]:
   layout=json.loads((PACKAGE/('examples/layout-'+name+'.json')).read_bytes())
   STAGE='public_validate_'+name;fixture=h.validate_experimental_nonking_layout(layout);save('returned-fixture-'+name+'.json',fixture)
   assert fixture['schema']==1 and fixture['rules']=='default' and fixture['mode']=='Unranked'
   assert fixture['sides']==layout['sides'] and fixture['below_master']is layout['below_master']
   assert sum(len(s['items'])for s in fixture['sides'])==count
   assert {x['item_index']for s in fixture['sides']for x in s['items']}==kinds
   validated.append(dict(example=name,items=count,returned_fixture=True))
  sys.setprofile(None);STAGE='postcheck';save('validated-examples.json',validated)
  assert COUNTS['verify_manifest.py:verify']==1 and COUNTS['headless.py:validate_experimental_nonking_layout']==2
  assert not forbidden
  assert sorted(str(p.relative_to(PACKAGE))for p in PACKAGE.rglob('*')if p.is_file())==original_files
  status='PASS_EXACT_PORTABLE_PACKAGE_IMPORT_PUBLIC_VALIDATE_NO_CTOR'
 except BaseException as exc:
  sys.setprofile(None);save('first-error.json',dict(stage=STAGE,type=type(exc).__name__,message=str(exc),traceback=list(frames(exc.__traceback__)),calls=COUNTS))
 finally:
  signal.alarm(0);sys.setprofile(None);finalize_from=STAGE;STAGE='finalize'
  after=[pin(ROOT/x['path'])for x in refs];save('after.json',after)
  if after!=refs:status='FAILED_SOURCE_DRIFT'
  save('imports.json',imports)
  result=dict(status=status,stage=finalize_from,wall_seconds=time.monotonic()-t,python_version=sys.version,calls=COUNTS,forbidden_entries=forbidden,Source_input_pins=len(refs),unchanged=after==refs,constructors=0 if not forbidden else'REJECTED_BEFORE_BODY',Native=0,Expected=0,battles=0,old_tests=0,auto_retry=False)
  save('result.json',result);save('owned-files.json',dict(files=[pin(p)for p in sorted(OUT.iterdir())if p.is_file()],sealed=True))
 print(json.dumps(result));return 0 if status.startswith('PASS')else 1
if __name__=='__main__':
 def timeout(signum,frame):raise TimeoutError('phase55520second wall deadline')
 signal.signal(signal.SIGALRM,timeout);signal.alarm(20);sys.exit(main())
