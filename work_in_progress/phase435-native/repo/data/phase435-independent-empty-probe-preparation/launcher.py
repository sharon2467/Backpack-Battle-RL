"""Prepare-gated EMPTY probe launcher. Not executed during preparation."""
from pathlib import Path
import argparse,hashlib,json,os,selectors,signal,stat,subprocess,time,sys
B=Path(__file__).absolute().parent
REPO=B.parent.parent

def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
def checked(d):
 p=Path(d['path']);p=p if p.is_absolute() else REPO/p
 for a in (p,*p.parents):
  if stat.S_ISLNK(a.lstat().st_mode):raise ValueError('linked resource')
 s=p.lstat()
 if not stat.S_ISREG(s.st_mode) or s.st_nlink!=1 or s.st_size!=d['size'] or digest(p)!=d['sha256']:raise ValueError('pinned resource drift')
 return p
def write(name,value):
 with (B/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--release',required=True);parser.add_argument('--release-size',required=True,type=int);parser.add_argument('--release-sha256',required=True);args=parser.parse_args()
 rd={'path':args.release,'size':args.release_size,'sha256':args.release_sha256};root=json.loads(checked(rd).read_text())
 if root.get('schema')!='phase435-root-empty-probe-execution-release/1' or root.get('status')!='RELEASED_ONCE' or root.get('engine_processes')!=1 or type(root.get('engine_processes')) is not int or root.get('original_Game')!=0 or root.get('capture')!=0:raise ValueError('actual one EMPTY Root execution release required')
 ownerpath=checked(root['preparation_owner'])
 if ownerpath!=B/'owned-files.json':raise ValueError('exact preparation owner')
 owner=json.loads(ownerpath.read_text())
 for d in owner['files']:checked(d)
 prep=json.loads(checked(owner['preparation_release']).read_text())
 if root.get('runtime_pins')!=prep['runtime_pins']:raise ValueError('exact runtime closure')
 paths=[checked(d) for d in prep['runtime_pins']]
 expected=json.loads((B/'expected.json').read_text())
 workspace=B/'runtime'
 if workspace.exists():raise ValueError('fresh runtime required')
 for part in ('home','data','config','cache','run','tmp'):(workspace/part).mkdir(parents=True,mode=0o700)
 env=dict(prep['runtime_environment']);env.pop('HOME_XDG_TMP',None)
 env.update({'HOME':str(workspace/'home'),'XDG_DATA_HOME':str(workspace/'data'),'XDG_CONFIG_HOME':str(workspace/'config'),'XDG_CACHE_HOME':str(workspace/'cache'),'XDG_RUNTIME_DIR':str(workspace/'run'),'TMPDIR':str(workspace/'tmp')})
 command=[sys.executable,str(paths[3]),str(paths[2]),'-a','-s','-screen 0 320x240x24 -nolisten tcp','-e',str(workspace/'xvfb.log'),str(paths[0]),'--path',str(B/'empty-project'),'--audio-driver','Dummy','--time-scale','1.0']
 write('execute-started.json',{'Root_release':rd,'args':command,'environment':env,'engine_processes':1,'original_Game':0,'capture':0,'timeout_seconds':20,'automatic_retry':False})
 started=time.monotonic();reason=None;logs={'stdout':bytearray(),'stderr':bytearray()};total=0
 process=subprocess.Popen(command,cwd=B,env=env,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True,close_fds=True,bufsize=0)
 poller=selectors.DefaultSelector()
 for stream,kind in ((process.stdout,'stdout'),(process.stderr,'stderr')):
  os.set_blocking(stream.fileno(),False);poller.register(stream,selectors.EVENT_READ,kind)
 try:
  while process.poll() is None or poller.get_map():
   if time.monotonic()-started>18:reason='outer_deadline';break
   for key,mask in poller.select(0.05):
    chunk=os.read(key.fileobj.fileno(),65536)
    if not chunk:poller.unregister(key.fileobj);continue
    total+=len(chunk)
    if total>262144:reason='log_cap';break
    logs[key.data].extend(chunk)
   if reason:break
 finally:
  if process.poll() is None:
   os.killpg(process.pid,signal.SIGTERM)
   try:process.wait(timeout=0.3)
   except subprocess.TimeoutExpired:
    os.killpg(process.pid,signal.SIGKILL);process.wait(timeout=0.5)
  poller.close()
 for kind,raw in logs.items():
  with (B/(kind+'.txt')).open('xb') as f:f.write(raw)
 payloads=[]
 for line in logs['stdout'].decode('utf8','replace').splitlines():
  try:payloads.append(json.loads(line))
  except ValueError:pass
 finals=[x for x in payloads if isinstance(x,dict) and x.get('status')=='PASS']
 result=finals[-1] if finals else None
 good=reason is None and process.returncode==0 and result is not None and all(result.get(k)==v for k,v in expected['final'].items())
 if result is not None:good=good and [{'id':x['id'],'external_calls':x['external_calls'],'pass':x['pass']} for x in result['results']]==[{'id':x['id'],'external_calls':x['external_calls'],'pass':True} for x in expected['subcases']]
 text=(logs['stdout']+logs['stderr']).decode('utf8','replace')
 if 'SCRIPT ERROR:' in text or 'Parse Error:' in text or 'ERROR:' in text:good=False
 write('execute-result.json',{'status':'PASS' if good else 'BLOCKED_FIRST_FAILURE','exit':process.returncode,'abort_reason':reason,'elapsed_seconds':time.monotonic()-started,'payload':result,'expected':expected['final'],'engine_processes':1,'original_Game':0,'capture':0,'native_language_probe':1,'models':0,'automatic_retry':False,'interpretation':'Exact helper/getter/fixture language controls only; no original Game/bootstrap/filewriter/private-value/data admission.'})
 return 0 if good else 1
if __name__=='__main__':raise SystemExit(main())
