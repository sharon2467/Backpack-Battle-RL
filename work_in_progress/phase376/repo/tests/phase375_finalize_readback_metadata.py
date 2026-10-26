"""Output-only status handoff; never reads pool, run, baseline or proc."""
import copy
import hashlib
import json
from pathlib import Path

R=Path(__file__).resolve().parents[1]
PRE=R/'data/phase375-independent-readback-metadata-source'
OLD=R/'data/phase375-independent-actual-readback-first-001'
D=R/'data/phase375-independent-readback-handoff'
def pin(p):
    b=p.read_bytes();return dict(size=len(b),sha256=hashlib.sha256(b).hexdigest())
def desc(p):return dict(path=p.relative_to(R).as_posix(),**pin(p))
def read(p):return json.loads(p.read_text())
def verify(row):
    p=R/row['path'];assert p.is_relative_to(R)
    assert pin(p)=={k:row[k] for k in ('size','sha256')};return p
def save(name,x):
    p=D/name
    with p.open('x') as f:json.dump(x,f,indent=2);f.write('\n')
    return p
def main():
    contract=read(PRE/'contract.json')
    for row in contract['files']:verify(row)
    owner=read(OLD/'owned-files.json')
    for row in owner['files']:verify(row)
    old=read(OLD/'review.json');config=read(verify(contract['authorization']));receipt=read(verify(contract['restore_receipt']))
    assert old['failure'] is None and old['status']=='INDEPENDENT370_RESTORED_POOL_EXACT_TARGET_READBACK_PASS'
    assert config['schema']=='phase375-root-pool-recovery/1'
    assert old['source_freeze']==config['source_freeze']==receipt['source_freeze']==contract['current_source_freeze']
    for name in ['restore_map','roots']:assert old[name]==config[name]==receipt[name]
    for name in ['project_target','staged_target','failed_state']:assert old[name]==receipt[name]
    assert old['roots']['failed_run'].endswith('original027-king-single-A-20261025-attempt03')
    assert old['failed_state']=={'size':250,'sha256':'2dea206ef316bea3c4e028ab1e7ca4ccf0c6d8e9ae97bbd38695af2d9b7fb2b6'}
    for name in ['project','staged','baseline']:assert old['observations'][name]['full_path_SHA_mode_mtime_equal'] is True
    assert old['observations']['failed_retained']['exact_capsule_owner_file_set_and_hash'] is True
    assert old['observations']['preserved_failed_overlay']['CRC_SHA_mode_valid'] is True
    assert old['observations']['process_inspection']['known_task_live']==0
    for name in ['native','models','Godot','processes_launched','actual_restore_calls','READY_commits','projection_calls']:assert type(old[name]) is int and old[name]==0
    new=copy.deepcopy(old);new['status']='INDEPENDENT375_RESTORED_POOL_EXACT_TARGET_READBACK_PASS'
    new['derived_metadata_only']=True
    new['metadata_handoff']=dict(original_review=desc(OLD/'review.json'),original_owner=desc(OLD/'owned-files.json'),original_status=old['status'],
        reason='Frozen checker lowercase phase wire replacement omitted uppercase370 status literal. Target observations unchanged. Genuine source/ROOT/map are375.',
        actual_fulltree_executions=1,metadata_only_finalizer_executions=1,new_pool_reads=0,new_inventory_calls=0,new_restore_calls=0,new_READY_calls=0)
    D.mkdir(exist_ok=False);save('review.json',new)
    paths={R/row['path'] for row in owner['files']}
    paths.update([OLD/'owned-files.json',D/'review.json',PRE/'contract.json',PRE/'source-owner.json',R/'tests/phase375_finalize_readback_metadata.py',R/'docs/phase375_readback_metadata_handoff_spec.md'])
    paths.update(verify(row) for row in contract['files'])
    ownerpath=save('owned-files.json',dict(files=[desc(p) for p in sorted(paths)],no_more_writes=True,scope='Readonly completed actual readback plus output-only metadata status handoff; all owner leaves in repo.'))
    for row in read(ownerpath)['files']:verify(row)
    print(json.dumps(dict(status=new['status'],review=desc(D/'review.json'),owner=desc(ownerpath),leaves=len(paths),bytes=sum(p.stat().st_size for p in paths))))
if __name__=='__main__':main()
