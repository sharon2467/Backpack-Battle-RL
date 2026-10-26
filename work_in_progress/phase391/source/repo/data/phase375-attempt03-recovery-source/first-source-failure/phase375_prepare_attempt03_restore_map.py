"""Generate an attempt03-only map from saved evidence, never inventory or mutate live pool."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import stat
import native_run_compaction as c

RECEIPT = {'size': 335, 'sha256': '355d5615d3d0ef86a79cd0ea9f7460eb9dd24bb9d7b30c07bd872f36db360e03'}
OVERLAY = dict(size=202992,sha256='6ed9cf9be0afe81938e552c2623ff141fd978b8162ef61f2e5dd18b181fdd0b9')


def pin(path):
    path=Path(path); info=path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or any(p.is_symlink() for p in (path,*path.parents)):
        raise ValueError('regular+nlink1 saved evidence only')
    return dict(size=info.st_size,sha256=c.digest(path))


def read(path):
    pin(path)
    return json.loads(Path(path).read_text())


def saved(root,name):
    c.safe_path(name)
    return Path(root).joinpath(*Path(name).parts)


def rooted(root,name,label):
    path=saved(root,name)
    return dict(root=label,path=name,**pin(path))


def write(path,value):
    with path.open('x') as stream:
        stream.write(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n');stream.flush();os.fsync(stream.fileno())


def generate(source_root,failed_run,previous_run,output):
    roots={k:Path(v).absolute() for k,v in dict(source_root=source_root,failed_run=failed_run,previous_run=previous_run).items()}
    for path in roots.values():
        if not path.is_dir() or any(p.is_symlink() for p in (path,*path.parents)):raise ValueError('explicit unlinked saved roots')
    output=Path(output).absolute()
    if not output.parent.is_dir() or any(p.is_symlink() for p in (output,*output.parents)):raise ValueError('safe new output')
    if any(output.is_relative_to(roots[k]) for k in ('failed_run','previous_run')):raise ValueError('no write in saved run')
    output.mkdir(mode=0o700,exist_ok=False)
    try:
        failed,previous=roots['failed_run'],roots['previous_run'];pres=failed/'output/failed-pool-preservation'
        receipt_path=pres/'receipt.json';overlay=pres/'failed-project-overlay.zip'
        assert pin(receipt_path)==RECEIPT and pin(overlay)==OVERLAY,'exact attempt03 preserved bytes'
        receipt=read(receipt_path)
        assert receipt['schema']=='attempt03-failed-pool-preservation/1' and receipt['status']=='PRESERVED_NOT_RESTORED'
        assert receipt['state']=='failed' and receipt['restore']==0 and type(receipt['restore']) is int and receipt['baseline_unchanged'] is True
        assert receipt['overlay_sha256']==OVERLAY['sha256'] and receipt['overlay_bytes']==OVERLAY['size']
        current=read(pres/'failed-project-files.json');staged=read(pres/'failed-staged-files.json');base=read(pres/'baseline-files.json')
        state=read(pres/'failed-pool-state.json')
        assert state['status']=='failed' and Path(state['run']).name=='original027-king-single-A-20261025-attempt03','attempt03 state only'
        bundle=previous/'output/compaction';oldbase,target,_=c.load_bundle(bundle)
        target_staged=read(bundle/'staged-inputs.json')
        assert oldbase==base
        plan=read(pres/'overlay-manifest.json');assert c.overlay_plan(base,current)==plan
        c.validate_archive(overlay,current,plan) # full CRC/SHA stream; no extraction/materialization.
        pre=read(failed/'output/source-preimages/preimages.json')
        prior=read(failed/'output/previous-source-preimages/inventory.json')
        reset=read(failed/'output/prior-observer-reset.json')
        assert prior['project']==target==reset['before'],'target matches real previous-source provenance'
        journal={row['path']:row for row in pre};assert len(journal)==len(pre)
        oldpatch=prior['patch']['patches'];patch={row['path']:(i,row) for i,row in enumerate(oldpatch)};assert len(patch)==len(oldpatch)
        # All original journals/backups are read and checked, not only the chosen subset.
        checked_install=0
        for row in pre:
            if row['before'] is not None:
                assert pin(saved(failed,'output/source-preimages/'+row['backup']))==row['before']['identity'];checked_install+=1
        for index,row in enumerate(oldpatch):
            assert pin(saved(failed,'output/previous-source-preimages/'+str(index)))==dict(size=row['after_size'],sha256=row['after_sha256'])
        a,b=c.index(current),c.index(target);s,t=c.index(staged),c.index(target_staged)
        assert a.keys()==b.keys() and s.keys()==t.keys(),'unknown added/missing paths require separate preservation scope'
        assert all(a[k]['kind']==b[k]['kind'] for k in a) and all(s[k]['kind']==t[k]['kind'] for k in s)
        changes=[];directories=[]
        for name in sorted(a):
            if a[name]==b[name]:continue
            if a[name]['kind']=='directory':directories.append(dict(path=name,before=a[name],target=b[name]));continue
            if name in patch:
                index,row=patch[name];payload=rooted(failed,'output/previous-source-preimages/'+str(index),'failed_run')
            elif name=='.native-random-observer-disposable':
                payload=rooted(failed,'output/previous-source-preimages/marker','failed_run')
            elif name in journal and journal[name]['before'] is not None:
                payload=rooted(failed,'output/source-preimages/'+journal[name]['backup'],'failed_run')
            else:raise ValueError('no proven old target payload: '+name)
            assert {k:payload[k] for k in ('size','sha256')}=={k:b[name][k] for k in ('size','sha256')}
            changes.append(dict(path=name,before_preserved=a[name],target=b[name],payload=payload))
        data=[]
        for name,row in sorted(t.items()):
            if row['kind']!='file':continue
            payload=rooted(previous,'output/compaction/inputs/'+name,'previous_run')
            assert {k:payload[k] for k in ('size','sha256')}=={k:row[k] for k in ('size','sha256')}
            assert pin(saved(pres,'failed-staged-bytes/'+name))=={k:s[name][k] for k in ('size','sha256')}
            data.append(dict(target=row,payload=payload))
        names=['output/failed-pool-preservation/'+str(p.relative_to(pres)) for p in sorted(pres.rglob('*')) if p.is_file()]
        names += ['output/source-preimages/preimages.json','output/previous-source-preimages/inventory.json','output/prior-observer-reset.json']
        files=[rooted(failed,name,'failed_run') for name in names]
        files += [rooted(previous,'output/compaction/'+name,'previous_run') for name in ('bundle-manifest.json','baseline-files.json','project-files.json','staged-inputs.json','pool-roundtrip.json')]
        mapping=dict(schema='phase375-attempt03-exact-restore-source-map/1',stage='SAVED_EVIDENCE_ONLY_NO_RESTORE',
            roots=dict(roots, pool=Path('/workspace/native-combat-20261013/pool')),roots_are='historical aliases; executor must receive explicit approved actual roots',
            failed_preservation=rooted(failed,'output/failed-pool-preservation/receipt.json','failed_run'),
            failed_project_inventory=rooted(failed,'output/failed-pool-preservation/failed-project-files.json','failed_run'),
            failed_state=rooted(failed,'output/failed-pool-preservation/failed-pool-state.json','failed_run'),
            project_target=rooted(previous,'output/compaction/project-files.json','previous_run'),staged_target=rooted(previous,'output/compaction/staged-inputs.json','previous_run'),
            file_differences=changes,directory_differences=directories,staged_files=data,restore_all_directory_metadata='deepest first full target manifest',
            unknown_path_policy='PRESERVE_AND_BLOCK',ready_commit='separate actual independent readback and exact root commit gate',Game_copies=0,pool_writes=0)
        mapping['roots']={k:str(v) for k,v in mapping['roots'].items()}
        write(output/'restore-map.json',mapping)
        write(output/'source-input-pins.json',dict(schema='phase375-attempt03-saved-control-pins/1',files=files,live_pool_inventory=False))
        result=dict(schema='phase375-attempt03-map-derivation/1',status='SAVED_SOURCE_MAP_FROZEN_NOT_RESTORED',
            map=pin(output/'restore-map.json'),input_pins=pin(output/'source-input-pins.json'),
            file_differences=len(changes),directory_differences=len(directories),staged_files=len(data),
            checked_install_backups=checked_install,checked_previous_patch_backups=len(oldpatch),
            actual_preservation_receipt=RECEIPT,overlay=OVERLAY,CRC_stream_verified=True,live_pool_inventory=False,restore=0,Game_copies=0,native=0,models=0)
        write(output/'derivation.json',result)
        for path in output.iterdir():pin(path)
        return result
    except BaseException as exc:
        write(output/'map-first-failure.json',dict(status='MAP_GENERATION_FAILED_NO_RESTORE',error=repr(exc),pool_writes=0))
        raise


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('source-root','failed-run','previous-run','output'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();print(json.dumps(generate(args.source_root,args.failed_run,args.previous_run,args.output),indent=2))


if __name__=='__main__':main()
