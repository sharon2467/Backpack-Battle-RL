"""One pinned pure strict8 call on existing002 output. Never runs model or Original."""
import __future__,argparse,copy,hashlib,json,math,os,pathlib,re,signal,stat,struct,sys,time,types
R=pathlib.Path('/workspace/python-original-engine/repo');S=R/'data/phase657-independent-sealed002-strict8';OUT=R/'data/phase657-actual002-comparison-first-001'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--pins-sha256',required=True);args=ap.parse_args();assert not OUT.exists();OUT.mkdir(mode=0o700);started=time.monotonic();stage='preflight';access=[];counts={};opened=[];held={};before=[];after=[];owned=[]
 pinraw=(S/'pins.json').read_bytes();assert hashlib.sha256(pinraw).hexdigest()==args.pins_sha256;cfg=json.loads(pinraw);pins={p['path']:p for p in cfg['files']};ep=json.loads((S/'expected-pins.json').read_bytes());expected=ep['files'];allowed=set(pins)|{str(S/'pins.json')}|{p['path'] for p in expected.values()}
 report={'schema':'phase657-independent-actual-strict8/1','status':'RUNNING','model_calls':0,'candidate_imports':0,'Native':0,'original_INPUT12_reads':0,'native_capture_complete':True,'native_process_clean_exit':False}
 def alarm(a,b):raise TimeoutError('inner50secondcomparisondeadline')
 signal.signal(signal.SIGALRM,alarm);signal.alarm(50)
 def audit(event,a):
  if event.startswith(('subprocess.','socket.')) or event in ('os.system','os.exec','os.spawn','os.fork','os.posix_spawn'):raise RuntimeError('FORBIDDEN_EXTERNAL_OPERATION')
  if event!='open' or isinstance(a[0],int):return
  path=str(pathlib.Path(os.fsdecode(a[0])).absolute());flags=a[2] if isinstance(a[2],int) else 0;write=bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
  if write:assert pathlib.Path(path).parent==OUT,'WRITE_SCOPE'
  else:assert path in allowed,'READ_SCOPE:'+path
  access.append({'stage':stage,'path':path,'op':'write' if write else 'read'})
 sys.addaudithook(audit)
 def read(p):
  path=pathlib.Path(p['path']);a=path.lstat();assert stat.S_ISREG(a.st_mode) and not path.is_symlink();b=path.read_bytes();z=path.lstat();assert (a.st_ino,a.st_size,a.st_mtime_ns)==(z.st_ino,z.st_size,z.st_mtime_ns);assert len(b)==p['size'] and hashlib.sha256(b).hexdigest()==p['sha256'];return b
 def save(name,value):
  b=(json.dumps(value,ensure_ascii=False,allow_nan=False,indent=2)+'\n').encode();path=OUT/name;path.write_bytes(b);return {'path':str(path),'size':len(b),'sha256':hashlib.sha256(b).hexdigest()}
 adapterpath=str(R/'tests/phase621_mixed_business_output.py')
 def profile(f,e,a):
  if e=='call' and f.f_code.co_filename==adapterpath:counts[f.f_code.co_name]=counts.get(f.f_code.co_name,0)+1
 try:
  cache={}
  for path,p in pins.items():cache[path]=read(p);before.append(p)
  module=types.ModuleType('_phase657_exact621_adapter');module.__file__=adapterpath;sys.modules[module.__name__]=module;sys.setprofile(profile);exec(compile(cache[adapterpath],adapterpath,'exec'),module.__dict__)
  def load(p):return module.strict_json_loads(cache[p['path']])
  binding=module.strict_json_loads(cache[str(S/'comparison-binding.json')]);assert len(binding)==20 and binding['adapter_source']['sha256']=='cb48328cc0a8274516e33367640af7933676c47950fff11f1b1d54f37b435558'
  bundle=load(binding['input_bundle']);proof=load(binding['input_proof']);model=load(binding['model_output']);aux=load(binding['final_aux']);gate=load(binding['prepare_gate'])
  for value,key in [(bundle,'input_canonical_sha256'),(proof,'input_proof_canonical_sha256'),(model,'model_output_canonical_sha256'),(aux,'final_aux_canonical_sha256'),(gate,'prepare_gate_canonical_sha256')]:assert module.canonical_sha(value)==binding[key]
  pre=module.strict_json_loads(cache[str(S/'output-preflight-review.json')]);assert pre['status']=='ACCEPTED_SEALED_OUTPUT_B1_B2_READY_FOR_ONE_COMPARISON'
  assert set(expected)==module.EXPECTED_LEAVES and not any(n.startswith(('native_replay_v7','native_replay_v8')) for n in sys.modules)
  owned.append(save('before.json',{'pins':before,'binding':binding,'output_preflight':pre,'Expected_payload_reads':0}));stage='Expected9_read_decode';native={}
  for name,p in expected.items():
   f=open(p['path'],'rb');held[name]=(f,os.fstat(f.fileno()),p);opened.append(name);b=f.read();assert len(b)==p['size'] and hashlib.sha256(b).hexdigest()==p['sha256']
   if name.endswith('.jsonl'):
    assert b.endswith(b'\n');lines=b.splitlines();assert all(x.strip() for x in lines);native[name]=[module.strict_json_loads(x) for x in lines]
   else:native[name]=module.strict_json_loads(b)
  stage='one_compare_decoded';comparison=module.compare_decoded(native,model,bundle,proof,aux,binding);assert counts.get('compare_decoded')==1
  owned.append(save('comparison.json',comparison));report['status']='PASS_ALL_EIGHT_FIXED002_SECTIONS' if comparison['status']=='PASS' else 'FAIL_STRICT_BUSINESS_DIFFERENCE';report['first_differences']=comparison['first_differences'];report['model_events']=len(model['events']);report['native_events']=len(native['events.jsonl'])
 except BaseException as e:
  report['status']='FAIL_FIRST_CARRIER_OR_PROJECTION_NO_RETRY';frames=[];tb=e.__traceback__
  while tb:frames.append({'file':tb.tb_frame.f_code.co_filename,'line':tb.tb_lineno,'function':tb.tb_frame.f_code.co_name});tb=tb.tb_next
  report['first_error']={'stage':stage,'type':type(e).__name__,'message':str(e),'frames':frames};owned.append(save('first-error.json',report['first_error']))
 finally:
  sys.setprofile(None);stage='identity_readback';integrity_error=None;expected_after=[]
  try:
   for name,(f,a,p) in held.items():
    f.seek(0);b=f.read();z=os.fstat(f.fileno());live=os.stat(p['path']);assert (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns)==(live.st_dev,live.st_ino,live.st_size,live.st_mtime_ns);assert len(b)==p['size'] and hashlib.sha256(b).hexdigest()==p['sha256'];expected_after.append(p)
   for p in pins.values():read(p);after.append(p)
  except BaseException as e:integrity_error={'type':type(e).__name__,'message':str(e)};report['status']='FAIL_IDENTITY_READBACK'
  for f,a,p in held.values():f.close()
  signal.alarm(0);report.update({'elapsed_seconds':time.monotonic()-started,'calls':counts,'adapter_file':adapterpath,'Source_input_model_pins_before':before,'Source_input_model_pins_after':after,'Expected_opened_once':opened,'Expected_after':expected_after,'Expected_physical_passes_per_open_file':2,'Expected_decodes_per_open_file':1,'integrity_error':integrity_error,'audit_before_report':list(access),'audit_limit':'Snapshot before report writes; write scope remains enforced.','formal_support_unchanged':75,'retry':False})
  owned.append(save('result.json',report));save('owned-files.json',{'schema':'phase657-actual-comparison-owner/1','files':owned})
 return 0 if report['status']=='PASS_ALL_EIGHT_FIXED002_SECTIONS' else 1
if __name__=='__main__':raise SystemExit(main())
