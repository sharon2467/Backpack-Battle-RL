"""Read saved attempt04/reset evidence and generate a partial map; never reads livepool."""
from pathlib import Path
import argparse
import hashlib
import json
import stat
import native_run_compaction as c

KNOWN_MISSING = {'.native-random-observer-disposable','native_random_observer_sink_v7.gd'}
PRIOR_FREEZE = dict(path='data/phase375-food-hook-source/combined-source-freeze.json',size=61295,sha256='7fe7f1cf013e06277a75c31ba846283d10221b49ce9c24828e920216e12e6f8d')


def require(value,message):
    if not value: raise ValueError(message)


def pin(path):
    path=Path(path);info=path.lstat()
    require(stat.S_ISREG(info.st_mode) and info.st_nlink==1 and not any(p.is_symlink() for p in (path,*path.parents)),'unlinked regular saved evidence')
    return dict(size=info.st_size,sha256=c.digest(path))


def read(path):
    pin(path);return json.loads(Path(path).read_text())


def rooted(root,name,label):
    c.safe_path(name);path=Path(root).joinpath(*Path(name).parts)
    return dict(root=label,path=name,**pin(path))


def analyze_saved_partial(source_root,failed_run,previous_run):
    source_root,failed_run,previous_run=[Path(p).absolute() for p in (source_root,failed_run,previous_run)]
    for p in (source_root,failed_run,previous_run):require(p.is_dir() and not any(x.is_symlink() for x in (p,*p.parents)),'explicit saved/source roots')
    pres=failed_run/'output/failed-pool-preservation';receipt=read(pres/'receipt.json')
    require(receipt.get('schema')=='attempt04-partial-install-failed-pool-preservation/1' and receipt.get('status')=='PRESERVED_NOT_RESTORED' and receipt.get('state')=='failed' and type(receipt.get('restore')) is int and receipt['restore']==0,'exact partial preservation stage')
    require(receipt.get('baseline_unchanged') is True and receipt.get('exact_reset_after') is True and receipt.get('install_atomic_writes_reached') is False and receipt.get('install_preimages_journal_present') is False and type(receipt.get('install_backup_files_present')) is int and receipt['install_backup_files_present']==75,'partial prefix facts required, never a complete journal')
    require(receipt.get('missing_target_paths')==sorted(KNOWN_MISSING) and receipt.get('extra_current_paths')==[],'only known2 missing')
    require(type(receipt.get('overlay_bytes')) is int and receipt['overlay_bytes']==12398 and receipt.get('overlay_sha256')=='2904e55692627234b349bc70251a2a1af1ea74cdd556c8d5f167694feda52bd7','exact saved partial overlay')
    current=read(pres/'failed-project-files.json');staged=read(pres/'failed-staged-files.json');base=read(pres/'baseline-files.json')
    state=read(pres/'failed-pool-state.json');require(state.get('status')=='failed' and Path(state['run']).name=='original027-king-single-A-20261025-attempt04','actual failed attempt04')
    prior=read(failed_run/'output/previous-source-preimages/inventory.json');reset=read(failed_run/'output/prior-observer-reset.json')
    bundle=previous_run/'output/compaction';oldbase,target,_=c.load_bundle(bundle);target_staged=read(bundle/'staged-inputs.json')
    require(base==oldbase and target==prior['project']==reset['before'] and current==reset['after'],'complete saved reset/current/oldtarget relation')
    plan=read(pres/'overlay-manifest.json');require(plan==c.overlay_plan(base,current),'partial overlay plan')
    c.validate_archive(pres/'failed-project-overlay.zip',current,plan)
    require(pin(pres/'failed-project-overlay.zip')==dict(size=receipt['overlay_bytes'],sha256=receipt['overlay_sha256']),'partial overlay bytes/CRC')
    a,b=c.index(current),c.index(target);s,t=c.index(staged),c.index(target_staged)
    require(set(b)-set(a)==KNOWN_MISSING and not set(a)-set(b),'no generalized added/missing paths')
    require(all(a[k]['kind']==b[k]['kind'] for k in a),'no file/dir replacement')
    oldpatch=prior['patch']['patches'];lookup={row['path']:(i,row) for i,row in enumerate(oldpatch)}
    require(len(oldpatch)==73 and len(lookup)==73,'exact prior patch set')
    for i,row in enumerate(oldpatch):
        require(pin(failed_run/'output/previous-source-preimages'/str(i))==dict(size=row['after_size'],sha256=row['after_sha256']),'old after backup bytes')
    require('native_random_observer_sink_v7.gd' in lookup and lookup['native_random_observer_sink_v7.gd'][1]['before_sha256'] is None,'sink reset-delete provenance')
    require('native_random_observer_sink_v7.gd' in reset['restored'],'sink reset operation')
    marker=failed_run/'output/previous-source-preimages/marker';require(pin(marker)=={k:b['.native-random-observer-disposable'][k] for k in ('size','sha256')},'old marker deletion payload')
    # The real failed source contract fixes install iteration order, but supplies no nonexistent journal.
    frozen=source_root/PRIOR_FREEZE['path'];require(pin(frozen)=={k:PRIOR_FREEZE[k] for k in ('size','sha256')},'actual attempt04 source freeze')
    freeze=read(frozen);launch=read(failed_run/'output/readonly-plan.json')
    require(launch['freeze']==PRIOR_FREEZE,'actual failed plan/source identity')
    rawdir=failed_run/'output/source-preimages';require(not (rawdir/'preimages.json').exists(),'no complete journal at this cut')
    expected_raw={};raw_rows=[]
    require(len(freeze['paths'])==75,'attempt04 exact patch preflight')
    for i,(name,row) in enumerate(freeze['paths'].items()):
        if row['before'] is None:
            require(name=='native_random_observer_sink_v7.gd' and name not in a,'only old removed sink absent patch preimage')
        else:
            require(name in a and {k:a[name][k] for k in ('size','sha256')}==row['before'],'raw prefix matches actual postreset source')
            expected_raw[str(i)]=dict(target=name,identity=row['before'])
    require(len(expected_raw)==74,'actual74 patch backups')
    expected_raw['75']=dict(target='native_combat_capture.gd',identity={k:a['native_combat_capture.gd'][k] for k in ('size','sha256')})
    require({p.name for p in rawdir.iterdir()}==set(expected_raw),'exact raw75 prefix names, no fabricated journal or extra')
    for name,row in expected_raw.items():
        p=rawdir/name;require(pin(p)==row['identity'],'raw backup byte identity')
        raw_rows.append(dict(index=name,target=row['target'],payload=rooted(failed_run,'output/source-preimages/'+name,'failed_run'),classification='PREFIX_PREIMAGE_NOT_JOURNAL_METADATA'))
    changes=[];directories=[]
    for name in sorted(b):
        old=a.get(name);want=b[name]
        if old==want:continue
        if want['kind']=='directory':
            require(old is not None,'no unknown directory creates');directories.append(dict(path=name,before=old,target=want));continue
        if name in lookup:
            index,_=lookup[name];payload=rooted(failed_run,'output/previous-source-preimages/'+str(index),'failed_run')
        elif name=='.native-random-observer-disposable':payload=rooted(failed_run,'output/previous-source-preimages/marker','failed_run')
        else:raise ValueError('no old after payload for exact target difference: '+name)
        require({k:payload[k] for k in ('size','sha256')}=={k:want[k] for k in ('size','sha256')},'mapped old target bytes')
        changes.append(dict(path=name,before_preserved=old,target=want,payload=payload,creation_proof='RESET_DELETED_OLD_TARGET' if old is None else None))
    require({row['path'] for row in changes if row['before_preserved'] is None}==KNOWN_MISSING,'only two explicit creates')
    require(s.keys()==t.keys(),'staged paths exact')
    data=[]
    for name,want in sorted(t.items()):
        if want['kind']!='file':continue
        payload=rooted(previous_run,'output/compaction/inputs/'+name,'previous_run')
        require({k:payload[k] for k in ('size','sha256')}=={k:want[k] for k in ('size','sha256')},'old target data payload')
        require(pin(pres/'staged-bytes'/name)=={k:s[name][k] for k in ('size','sha256')},'actual saved staged bytes')
        data.append(dict(target=want,payload=payload))
    core=dict(schema='phase380-attempt04-partial-reset-map/1',failed_preservation=rooted(failed_run,'output/failed-pool-preservation/receipt.json','failed_run'),
        failed_project_inventory=rooted(failed_run,'output/failed-pool-preservation/failed-project-files.json','failed_run'),
        project_target=rooted(previous_run,'output/compaction/project-files.json','previous_run'),staged_target=rooted(previous_run,'output/compaction/staged-inputs.json','previous_run'),
        file_differences=changes,directory_differences=directories,staged_files=data,known_absent_creates=sorted(KNOWN_MISSING),
        reset_evidence=rooted(failed_run,'output/prior-observer-reset.json','failed_run'),raw_prefix=raw_rows,
        journal_present=False,install_writes_reached=False,restore_stage='RESET_COMPLETE_INSTALL_JOURNAL_INCOMPLETE')
    files=[rooted(failed_run,'output/failed-pool-preservation/'+str(p.relative_to(pres)),'failed_run') for p in sorted(pres.rglob('*')) if p.is_file()]
    files += [rooted(failed_run,'output/'+name,'failed_run') for name in ('prior-observer-reset.json','previous-source-preimages/inventory.json','readonly-plan.json')]
    files += [rooted(previous_run,'output/compaction/'+name,'previous_run') for name in ('bundle-manifest.json','pool-roundtrip.json','baseline-files.json','project-files.json','staged-inputs.json')]
    return dict(core=core,input_pins=dict(schema='phase380-partial-saved-input-pins/1',files=files),failed=current,failed_data=staged,target=target,target_data=target_staged,base=base)


def generate(source_root,failed_run,previous_run,output):
    output=Path(output).absolute();require(output.parent.is_dir() and not any(p.is_symlink() for p in (output,*output.parents)),'new safe output')
    for p in (Path(failed_run).absolute(),Path(previous_run).absolute()):require(not output.is_relative_to(p),'never write in saved run')
    output.mkdir(exist_ok=False)
    def save(name,value):
        with (output/name).open('x') as stream:stream.write(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')
    try:
        result=analyze_saved_partial(source_root,failed_run,previous_run);mapping=result['core']
        mapping.update(roots=dict(source_root=str(Path(source_root).absolute()),failed_run=str(Path(failed_run).absolute()),previous_run=str(Path(previous_run).absolute()),pool='/workspace/native-combat-20261013/pool'),roots_are='historical aliases; actual execution roots explicit')
        save('restore-map.json',mapping);save('source-input-pins.json',result['input_pins'])
        report=dict(status='SAVED_PARTIAL_MAP_GENERATED_NOT_RESTORED',map=pin(output/'restore-map.json'),input_pins=pin(output/'source-input-pins.json'),
            project_file_differences=len(mapping['file_differences']),known_creates=sorted(KNOWN_MISSING),directory_differences=len(mapping['directory_differences']),
            staged_files_verified=len(mapping['staged_files']),staged_file_differences=sum(c.index(result['failed_data'])[row['target']['path']]!=row['target'] for row in mapping['staged_files']),
            raw_prefix_files=75,complete_journal=False,new_source_install_writes=False,live_pool_inventory=False,restore=0,Game=0,models=0)
        save('derivation.json',report);return report
    except BaseException as exc:
        save('map-first-failure.json',dict(error=repr(exc),status='SAVED_MAP_FAILED_NO_RESTORE',pool_writes=0));raise


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for n in ('source-root','failed-run','previous-run','output'):parser.add_argument('--'+n,type=Path,required=True)
    a=parser.parse_args();print(json.dumps(generate(a.source_root,a.failed_run,a.previous_run,a.output),indent=2))


if __name__=='__main__':main()
