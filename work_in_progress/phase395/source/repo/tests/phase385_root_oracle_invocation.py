from pathlib import Path
import subprocess,os,json,time,hashlib,sys
r=Path('/workspace/python-original-engine/repo');d=r/'data/phase385-root-oracle-attempt05';mode=sys.argv[1];assert mode in ('plan','execute');config=d/'oracle-acceptance.json';b=config.read_bytes();assert len(b)==4226 and hashlib.sha256(b).hexdigest()=='89fce82940bcb7191c0518758d51e41a57286ccd3c0e97695c08a0b171376de1'
args=['python','tests/phase380_oracle_host.py','--source-root',str(r),'--task-root','/workspace/godotsteam-startup-20261013','--baseline','/workspace/godotsteam-startup-20261013/baseline/Backpack Battles','--pool','/workspace/native-combat-20261013/pool','--runs-root','/workspace/native-combat-20261013/runs','--config',str(config.relative_to(r)),'--config-size',str(len(b)),'--config-sha256',hashlib.sha256(b).hexdigest(),'--'+mode]
env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';assert not (d/(mode+'-invocation.json')).exists();started=time.monotonic();p=subprocess.run(args,cwd=r,env=env,capture_output=True,timeout=120 if mode=='plan' else 650)
(d/(mode+'.stdout')).write_bytes(p.stdout);(d/(mode+'.stderr')).write_bytes(p.stderr);v=dict(mode=mode,returncode=p.returncode,elapsed_seconds=time.monotonic()-started,args=args,host_invocations=1,models=0,inputbuilds=0,expected_comparison=0)
(d/(mode+'-invocation.json')).write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v));print(p.stderr.decode()[-2500:])
if mode=='execute':print(p.stdout.decode()[-1500:])
raise SystemExit(p.returncode)
