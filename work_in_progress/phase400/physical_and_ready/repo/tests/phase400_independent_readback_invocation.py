"""One-shot independent launcher for the frozen398 actual physical reader."""
import hashlib,json,os,stat,subprocess,sys,time,traceback
from pathlib import Path
R=Path(__file__).absolute().parents[1]
D=R/'data/phase400-independent-readback-launch-first-001'
FIXED=R/'data/phase398-independent-actual-readback-first-001'

def identity(p):
 s=p.lstat();assert stat.S_ISREG(s.st_mode)and s.st_nlink==1 and not any(q.is_symlink()for q in(p,*p.parents))
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 t=p.lstat();assert(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==(t.st_dev,t.st_ino,t.st_size,t.st_mtime_ns,t.st_ctime_ns)
 return dict(size=s.st_size,sha256=h.hexdigest())
def desc(p):return dict(path=str(p.relative_to(R)),**identity(p))
def verified(row):
 assert type(row)is dict and set(row)=={'path','size','sha256'}
 p=Path(row['path']);assert not p.is_absolute()and p.as_posix()==row['path']and all(x not in('','.','..')for x in row['path'].split('/'))
 target=R/p;assert identity(target)=={k:row[k]for k in('size','sha256')};return target

def read(p):return json.loads(p.read_text())
def save(n,v):
 with(D/n).open('x')as f:f.write(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+'\n')
def raw(n,b):
 with(D/n).open('xb')as f:f.write(b)

def main():
 assert not D.exists();D.mkdir()
 calls=0;started=None;args=None
 try:
  release_row=dict(path='data/phase400-root-attempt05-complete-restore/independent-readback-execution-release.json',size=1532,sha256='82ae0ffa5fa60f0c4d74cc8c702b0465ceea4ff4904c14b22d90e79891ebdb79')
  release=read(verified(release_row))
  assert release['schema']=='root400-independent398-physical-reader-release/1'and release['status']=='ROOT_RELEASED_ONCE_AFTER_ACTUAL80_WRITE_RESTORE_STATE_FAILED'
  assert type(release['reader_main_calls_allowed'])is int and release['reader_main_calls_allowed']==1 and release['actual_pool_readonly']is True and release['automatic_retry']is False
  for key in('READY_allowed','restore_allowed','native','models'):assert type(release[key])is int and release[key]==0
  for key in('authorization','restore_receipt','reader','source_owner','source_review','restore_invocation'):verified(release[key])
  assert release['source_owner']==dict(path='data/phase398-independent-readback-source/source-owner.json',size=96725,sha256='7a5cf72b88b3ab374fe8e7d3cd5a91fdf0ccedca3d29d849c6f77cc01541652b')
  owner=read(R/release['source_owner']['path']);rows=owner['files'];assert len({row['path']for row in rows})==len(rows)
  for row in rows:verified(row)
  assert release['reader']in rows
  config=read(R/release['authorization']['path']);receipt=read(R/release['restore_receipt']['path']);review=read(R/release['source_review']['path'])
  assert config['schema']=='phase398-root-pool-recovery/1'and config['action']=='restore'and config['root_restore_authorized']is True
  assert receipt['status']=='RESTORED_EXACT_TARGET_STATE_REMAINS_FAILED_INDEPENDENT_READBACK_PENDING'and type(receipt['writes'])is int and receipt['writes']==80 and receipt['READY_committed']is False
  assert receipt['failed_state']==dict(size=250,sha256='419a93cecf2e7c8ebfff9fe09f94b3ac8d34825c937b123ff1c451a6e039a245')
  assert review['status']=='INDEPENDENT399_ATTEMPT05_COMPLETE_RECOVERY_SOURCE_ACCEPTED_ROOT_PENDING'and review['source_freeze']==config['source_freeze']==receipt['source_freeze']
  for key in('models','native'):assert type(review[key])is int and review[key]==0
  assert not FIXED.exists()and not FIXED.is_symlink()
  args=[sys.executable,str(R/release['reader']['path']),'--execute']
  for key,label in(('authorization','authorization'),('restore_receipt','restore-receipt')):
   row=release[key];args+=['--'+label,row['path'],'--'+label+'-size',str(row['size']),'--'+label+'-sha256',row['sha256']]
  args+=['--source-owner-size',str(release['source_owner']['size']),'--source-owner-sha256',release['source_owner']['sha256']]
  save('preflight.json',dict(status='SOURCE_AND_REAL_RELEASE_PINS_PASS_FIXED_OUTPUT_ABSENT',release=release_row,source_owner=release['source_owner'],source_files=len(rows),source_bytes=sum(r['size']for r in rows),reader=release['reader'],authorization=release['authorization'],restore_receipt=release['restore_receipt'],fixed_output=str(FIXED),fixed_output_absent=True,source_check_scope='all actual owner leaves ordinary/nlink1/SHA before reader interpreter',reader_calls=0))
  save('intent.json',dict(schema='phase400-independent-reader-once-intent/1',args=args,cwd=str(R),environment_overrides={'PYTHONDONTWRITEBYTECODE':'1'},outer_timeout_seconds=180,automatic_retry=False,root_release=release_row,reader_calls_allowed=1,restore=0,READY=0,native=0,models=0))
  env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');started=time.monotonic();calls=1
  try:
   result=subprocess.run(args,cwd=R,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=180)
   elapsed=time.monotonic()-started;raw('stdout.txt',result.stdout);raw('stderr.txt',result.stderr)
   save('invocation-result.json',dict(args=args,elapsed_seconds=elapsed,exit_code=result.returncode,timeout=False,reader_main_calls=1,stdout=desc(D/'stdout.txt'),stderr=desc(D/'stderr.txt'),automatic_retry=False))
   print(json.dumps(dict(exit_code=result.returncode,elapsed_seconds=elapsed,reader_main_calls=1,stdout=desc(D/'stdout.txt'),stderr=desc(D/'stderr.txt'))))
   return result.returncode
  except subprocess.TimeoutExpired as exc:
   raw('stdout.txt',exc.stdout or b'');raw('stderr.txt',exc.stderr or b'')
   save('invocation-result.json',dict(args=args,elapsed_seconds=time.monotonic()-started,exit_code=None,timeout=True,reader_main_calls=1,stdout=desc(D/'stdout.txt'),stderr=desc(D/'stderr.txt'),automatic_retry=False))
   raise
 except BaseException as exc:
  save('first-failure.json',dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc(),reader_main_calls=calls,args=args,automatic_retry=False));raise
if __name__=='__main__':raise SystemExit(main())
