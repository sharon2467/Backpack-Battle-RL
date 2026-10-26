"""Verify existing actual reader evidence and seal its launch; never invoke SUT."""
import hashlib,json,stat
from pathlib import Path
R=Path(__file__).absolute().parents[1];D=R/'data/phase400-independent-readback-launch-first-001';Q=R/'data/phase398-independent-actual-readback-first-001'
def identity(p):
 s=p.lstat();assert stat.S_ISREG(s.st_mode)and s.st_nlink==1 and not any(q.is_symlink()for q in(p,*p.parents))
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return dict(size=s.st_size,sha256=h.hexdigest())
def desc(p):return dict(path=str(p.relative_to(R)),**identity(p))
def read(p):return json.loads(p.read_text())
def check(root,row):
 name=row['path'];rel=Path(name);assert not rel.is_absolute()and rel.as_posix()==name and all(x not in('','.','..')for x in name.split('/'))
 p=root/rel;assert identity(p)=={k:row[k]for k in('size','sha256')};return p

def save(p,v):
 with p.open('x')as f:f.write(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+'\n')
def main():
 invocation=read(D/'invocation-result.json');assert invocation['exit_code']==0 and invocation['timeout']is False and invocation['reader_main_calls']==1
 release=read(R/'data/phase400-root-attempt05-complete-restore/independent-readback-execution-release.json')
 for key in('authorization','restore_receipt','reader','source_owner','source_review','restore_invocation'):check(R,release[key])
 config=read(R/release['authorization']['path']);receipt=read(R/release['restore_receipt']['path']);review=read(Q/'review.json');owner=read(Q/'owned-files.json');contract=read(Q/'execution-contract.json');source=read(R/'data/phase398-independent-readback-source/source-contract.json');stdout=read(D/'stdout.txt')
 assert review['status']==stdout['status']=='INDEPENDENT398_ATTEMPT05_RESTORED_POOL_EXACT_TARGET_READBACK_PASS'and review['failure']is None
 assert desc(Q/'review.json')==stdout['review']and desc(Q/'owned-files.json')==stdout['owner']
 assert contract['authorization']==release['authorization']and contract['restore_receipt']==release['restore_receipt']and review['restore_receipt']==release['restore_receipt']
 for key in('roots','restore_map','source_freeze'):assert review[key]==receipt[key]==config[key]
 for key in('project_target','staged_target','failed_state'):assert review[key]==receipt[key]
 assert receipt['writes']==80 and type(receipt['writes'])is int and receipt['READY_committed']is False
 for key in('native','models','Godot','actual_restore_calls','READY_commits','projection_calls','processes_launched'):assert type(review[key])is int and review[key]==0
 assert len(owner['files'])==len({x['path']for x in owner['files']})
 for row in owner['files']:check(R,row)
 assert desc(Q/'review.json')in owner['files']
 source_owner=read(R/release['source_owner']['path'])
 for row in source_owner['files']:check(R,row)
 targets={};trees={}
 for key,output in(('project','project-readback.json'),('staged','staged-readback.json'),('baseline','baseline-readback.json'),('retained','previous-retained-readback.json'),('driver','previous-driver-readback.json')):
  row=source['external_targets'][key];p=check(Path(config['roots'][row['root']]),row);expected=read(p);actual=read(Q/output);assert actual==expected
  targets[key]=dict(target=row,readback=desc(Q/output),exact_complete_JSON_equal=True)
  if key in('project','staged','baseline'):
   entries=actual['entries'];trees[key]=dict(files=sum(x['kind']=='file'for x in entries),directories=sum(x['kind']=='directory'for x in entries),bytes=sum(x.get('size',0)for x in entries))
 assert trees['project']==dict(files=15422,directories=247,bytes=616322482)
 assert trees['staged']==dict(files=2,directories=1,bytes=3355)
 assert trees['baseline']==dict(files=15418,directories=247,bytes=616167851)
 audit=read(Q/'audit.json');assert audit['blocked']==[]and audit['no_external_write_attempts']is True and audit['subprocesses']==audit['network']==0
 scope=read(Q/'task-process-scope.json');inspections=read(Q/'process-inspection.json')
 assert scope['whole_system_proc_complete']is False and scope['known_task_live']==0 and scope['visible_live_Godot_Xvfb']==0
 assert scope['known_pgids']==[21970,22029]and scope['known_pids']==[21980,22039]
 known=[x for x in scope['inspected']if x['known_task_pid']or x['pgid']in scope['known_pgids']]
 assert all(x['state']=='Z'for x in known)
 gaps={k:len(v['inspection_gaps'])for k,v in inspections.items()};assert sum(gaps.values())==review['observations']['process_inspection']['inspection_gaps']==96
 assert all(v['active_matches']==[]for v in inspections.values())
 state=Path(config['roots']['pool'])/'state.json';state_identity=identity(state);assert state_identity==review['failed_state']and read(state)['status']=='failed'
 result=dict(schema='phase400-independent-reader-evidence-verification/1',status='ACTUAL398_PHYSICAL_PASS_AND_ALL_OWNED_EVIDENCE_VERIFIED_ROOT_READY_PENDING',reader_review=desc(Q/'review.json'),reader_owner=desc(Q/'owned-files.json'),reader_owner_files=len(owner['files']),reader_owner_bytes=sum(r['size']for r in owner['files']),actual_invocation=desc(D/'invocation-result.json'),reader_main_calls=1,exit_code=0,external_elapsed_seconds=invocation['elapsed_seconds'],reader_elapsed_seconds=review['elapsed_seconds'],source_owner_postcheck=release['source_owner'],source_owner_postcheck_files=len(source_owner['files']),source_owner_postcheck_bytes=sum(x['size']for x in source_owner['files']),complete_target_comparisons=targets,tree_counts=trees,failed_state_after=state_identity,pool_status_after='failed',capsule=review['observations']['failed_capsule'],failed_retained=review['observations']['failed_retained'],failed_overlay=review['observations']['preserved_failed_overlay'],process_scope=dict(known_pgids=scope['known_pgids'],known_pids=scope['known_pids'],known_observed_rows=known,inspection_gaps_by_scope=gaps,inspection_gaps_total=96,whole_system_proc_complete=False,zombies_claimed_reaped=False,known_task_live=0,visible_live_Godot_Xvfb=0,restriction=scope['restriction']),audit=desc(Q/'audit.json'),no_external_write_attempts=True,verification_only_no_reader_rerun=True,READY_commits=0,restore_calls=0,native=0,models=0,Godot=0,remaining='Separate Root READY release and later native/model gates; no fresh-OS restoration claim.',no_more_writes=True)
 save(D/'verification.json',result)
 leaves=set(p for p in D.rglob('*')if p.is_file());leaves.add(Q/'owned-files.json');leaves.update(R/row['path']for row in owner['files']);leaves.update([R/'docs/phase400_independent_physical_readback_execution_addendum.md',R/'tests/phase400_independent_readback_invocation.py',Path(__file__).absolute()])
 rows=[desc(p)for p in sorted(leaves)]
 save(D/'owned-files.json',dict(schema='phase400-independent-reader-execution-owner/1',files=rows,leaf_count=len(rows),byte_count=sum(r['size']for r in rows),no_more_writes=True))
 for row in rows:check(R,row)
 print(json.dumps(dict(status=result['status'],verification=desc(D/'verification.json'),launch_owner=desc(D/'owned-files.json'),owned_leaves=len(rows),owned_bytes=sum(r['size']for r in rows),reader_review=result['reader_review'],reader_owner=result['reader_owner'],READY=0,native=0,models=0)))
if __name__=='__main__':main()
