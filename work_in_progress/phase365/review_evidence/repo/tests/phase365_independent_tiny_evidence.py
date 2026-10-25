"""Neutral finite filesystem evidence, not a Game, native capture or ROOT authorization."""
from pathlib import Path
import copy
import json
import os
import shutil

T1=1600000000000000000
T2=T1+1000000000


def create(base,c,recovery,save,pin):
    base.mkdir()
    roots={key:base/key for key in ('source_root','pool','baseline','failed_run','previous_run')}
    for path in roots.values(): path.mkdir()
    pool=roots['pool']; previous=roots['previous_run']; failed_run=roots['failed_run']
    for name in ('project','data'): (pool/name).mkdir()
    (pool/'.lock').write_bytes(b'')
    save(pool/'state.json',dict(status='failed',run=str(failed_run),synthetic_filesystem_unit=True))
    for name in ('output','data','user','output/driver','output/compaction'):
        (previous/name).mkdir(parents=True,exist_ok=True)
    (previous/'output/driver/unit.txt').write_bytes(b'NEUTRAL_DRIVER_TEXT_NOT_EXECUTABLE')
    save(previous/'output/pool-provenance.json',dict(scope='SYNTHETIC_FS_UNIT_ONLY'))
    target=base/'neutral-target'; target.mkdir()
    def metadata(root,ns,mode):
        for path in sorted(root.rglob('*'),key=lambda p:len(p.parts),reverse=True):
            os.chmod(path,mode if path.is_file() else 0o750); os.utime(path,ns=(ns,ns))
        os.chmod(root,0o750); os.utime(root,ns=(ns,ns))
    for root,old in ((roots['baseline'],True),(target,True),(pool/'project',False)):
        for i in range(6): (root/('group%d'%i)).mkdir()
        for i in range(78):
            (root/('group%d/unit%02d.txt'%(i%6,i))).write_bytes(('TARGET_' if old else 'FAILED_').encode()+str(i).encode())
        metadata(root,T1 if old else T2,0o640 if old else 0o600)
    for root,old in ((previous/'data',True),(pool/'data',False)):
        for name in ('a.txt','b.txt'): (root/name).write_bytes(('OLD_' if old else 'NEW_').encode()+name.encode())
        metadata(root,T1 if old else T2,0o640 if old else 0o600)
    base_tree=c.inventory(roots['baseline']); target_tree=c.inventory(target)
    failed_tree=c.inventory(pool/'project'); failed_data=c.inventory(pool/'data'); target_data=c.inventory(previous/'data')
    bundle=previous/'output/compaction'; shutil.copytree(previous/'data',bundle/'inputs')
    plan=c.overlay_plan(base_tree,target_tree)
    for name,value in [('baseline-files.json',base_tree),('project-files.json',target_tree),('overlay-manifest.json',plan),
            ('retained-evidence.json',c.retained(previous)),('driver-files.json',c.inventory(previous/'output/driver')),
            ('staged-inputs.json',target_data),('source-identities.json',{'scope':'SYNTHETIC_FS_UNIT_ONLY'}),
            ('eligibility.json',{'scope':'SYNTHETIC_FS_UNIT_ONLY_NOT_NATIVE_ELIGIBILITY'})]: save(bundle/name,value)
    (bundle/'RESTORE-PROJECT.md').write_text('Neutral tiny filesystem unit only. No Game or native evidence.\n')
    c.archive_overlay(target,target_tree,plan,bundle/'overlay.zip')
    save(bundle/'bundle-manifest.json',dict(schema='native-run-compaction/1',
        files={p.relative_to(bundle).as_posix():c.digest(p) for p in sorted(bundle.rglob('*')) if p.is_file()},
        driver_sha256={'unit.txt':c.digest(previous/'output/driver/unit.txt')}))
    save(bundle/'pool-roundtrip.json',dict(status='PASS',scope='SYNTHETIC_FS_UNIT_ONLY',
        run=str(previous),pool=str(pool),bundle_sha256=c.digest(bundle/'bundle-manifest.json'),
        provenance_sha256=c.digest(previous/'output/pool-provenance.json')))
    saved=failed_run/'output/failed-pool-preservation'; saved.mkdir(parents=True)
    for name,value in [('baseline-files.json',base_tree),('failed-project-files.json',failed_tree),
            ('failed-staged-files.json',failed_data),('failed-pool-state.json',json.loads((pool/'state.json').read_text()))]: save(saved/name,value)
    failed_plan=c.overlay_plan(base_tree,failed_tree); save(saved/'overlay-manifest.json',failed_plan)
    c.archive_overlay(pool/'project',failed_tree,failed_plan,saved/'failed-project-overlay.zip')
    save(saved/'receipt.json',dict(status='PASS_PRESERVED_NOT_RESTORED',physical_restore_performed=False,
        scope='SYNTHETIC_FS_UNIT_ONLY',run=str(failed_run),pool=str(pool),baseline=str(roots['baseline']),
        zip_sha256=c.digest(saved/'failed-project-overlay.zip'),zip_bytes=(saved/'failed-project-overlay.zip').stat().st_size))
    def desc(key,path): return dict(root=key,path=path.relative_to(roots[key]).as_posix(),**pin(path))
    bi,ti=c.index(failed_tree),c.index(target_tree)
    files=[]; directories=[]
    payload_root=failed_run/'payloads'; payload_root.mkdir()
    for name,row in ti.items():
        if row['kind']=='file':
            payload=payload_root/name; payload.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(target/name,payload)
            files.append(dict(path=name,before_preserved=bi[name],target=row,payload=desc('failed_run',payload)))
        else: directories.append(dict(path=name,before=bi[name],target=row))
    mapping=dict(roots={k:str(v) for k,v in roots.items()},failed_preservation=desc('failed_run',saved/'receipt.json'),
        failed_project_inventory=desc('failed_run',saved/'failed-project-files.json'),
        project_target=desc('previous_run',bundle/'project-files.json'),staged_target=desc('previous_run',bundle/'staged-inputs.json'),
        file_differences=files,directory_differences=directories,staged_files=[dict(target=row,
            payload=desc('previous_run',bundle/'inputs'/name)) for name,row in c.index(target_data).items() if row['kind']=='file'])
    input_pins=dict(files=[mapping[k] for k in ('failed_preservation','failed_project_inventory','project_target','staged_target')])
    # Payload identities remain separately checked by exact evidence_path and target manifests.
    save(base/'mapping.json',mapping); save(base/'input-pins.json',input_pins)
    binding=dict(roots={k:str(v) for k,v in roots.items()},scope='SYNTHETIC_FS_UNIT_ONLY_NO_READY')
    return dict(base=base,roots=roots,mapping=mapping,pins=input_pins,binding=binding,
        baseline=copy.deepcopy(base_tree),previous=c.retained(previous))
