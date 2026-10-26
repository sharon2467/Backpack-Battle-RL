"""Read-only physical380 partial-restored target validation. No recovery, READY or process execution."""
import ast
import argparse
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import time
import traceback
import zipfile

R=Path(__file__).resolve().parents[1]
D=R/'data/phase384-independent-actual-readback-first-001'
SD=R/'data/phase384-independent-readback-source'
AUDIT=dict(write_attempts=0,blocked=[],subprocesses=0,network=0)
READBACK_STATUS = 'INDEPENDENT380_RESTORED_POOL_EXACT_TARGET_READBACK_PASS'

def pin(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return dict(size=path.stat().st_size,sha256=h.hexdigest())
def desc(path):return dict(path=str(path.relative_to(R)),**pin(path))
def read(path):return json.loads(path.read_text())
def save(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True,allow_nan=False);stream.write('\n')
def require(value,message):
    if not value:raise ValueError(message)
def canonical(root,name):
    require(type(name) is str and '\\' not in name and '\0' not in name,'canonical relative path')
    rel=Path(name);require(not rel.is_absolute() and rel.as_posix()==name and all(x not in ('','.','..') for x in name.split('/')),'safe relative member')
    path=root/rel;require(not any(p.is_symlink() for p in (path,*path.parents)),'no linked paths')
    return path
def verify_descriptor(root,row):
    path=canonical(root,row['path']);require(pin(path)=={k:row[k] for k in ('size','sha256')},'descriptor drift: '+str(path));return path
def inventory(root,exclude=(),relaxed=False):
    require(root.is_dir() and not any(p.is_symlink() for p in (root,*root.parents)),'unlinked inventory root')
    device=root.stat().st_dev;rows=[]
    def visit(path):
        name=path.relative_to(root).as_posix()
        if name!='.' and name.split('/')[0] in exclude:return
        before=path.lstat();mode=stat.S_IMODE(before.st_mode)
        require(before.st_dev==device,'cross device')
        if not relaxed:
            require(not mode&0o7000 and not os.listxattr(path,follow_symlinks=False),'unsupported permissions/xattrs')
        row=dict(path=name,mode=mode,mtime_ns=before.st_mtime_ns)
        if stat.S_ISDIR(before.st_mode):
            row['kind']='directory';rows.append(row)
            for child in sorted(path.iterdir()):visit(child)
        elif stat.S_ISREG(before.st_mode):
            require(relaxed or before.st_nlink==1,'hardlinked strict file')
            h=hashlib.sha256();fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
            with os.fdopen(fd,'rb') as stream:
                opened=os.fstat(stream.fileno())
                for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
                closed=os.fstat(stream.fileno())
            identity=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
            require(identity(before)==identity(opened)==identity(closed)==identity(path.lstat()),'file changed while reading')
            row.update(kind='file',size=before.st_size,sha256=h.hexdigest());rows.append(row)
        else:
            require(relaxed,'unsupported strict special node')
            row.update(kind='symlink' if stat.S_ISLNK(before.st_mode) else 'special',type_bits=stat.S_IFMT(before.st_mode))
            if stat.S_ISLNK(before.st_mode):row['target']=os.readlink(path)
            rows.append(row)
    visit(root);return dict(schema='native-run-project-manifest/1',entries=rows)
def counts(tree):
    return dict(entries=len(tree['entries']),files=sum(r['kind']=='file' for r in tree['entries']),
        directories=sum(r['kind']=='directory' for r in tree['entries']),bytes=sum(r.get('size',0) for r in tree['entries']))
def audit(event,args):
    if event=='open':
        path,mode,flags=args
        if isinstance(path,int):return
        write=(isinstance(mode,str) and any(x in mode for x in 'wax+')) or (type(flags)is int and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
        if write:
            AUDIT['write_attempts']+=1
            if not Path(os.fsdecode(path)).absolute().is_relative_to(D):AUDIT['blocked'].append(dict(event=event,path=os.fsdecode(path)));raise PermissionError('readback forbids external writes')
    if event in ('subprocess.Popen','os.system','os.posix_spawn','socket.connect','socket.bind'):
        AUDIT['blocked'].append(dict(event=event));raise PermissionError('no processes/network in readback')
    if event in ('os.rename','os.remove','os.rmdir','os.mkdir','os.chmod','os.utime','os.link','os.symlink','os.truncate'):
        path=args[0]
        if not isinstance(path,int) and not Path(os.fsdecode(path)).absolute().is_relative_to(D):
            AUDIT['blocked'].append(dict(event=event,path=os.fsdecode(path)));raise PermissionError('no original metadata mutation')


def verify_overlay_archive(path,overlay,tree):
    index={row['path']:row for row in tree['entries']}
    with zipfile.ZipFile(path) as archive:
        require(len(archive.infolist())==len(set(archive.namelist())) and set(archive.namelist())==set(overlay['content']),'overlay exact unique member set')
        for info in archive.infolist():
            canonical(D,info.filename) # lexical safety; no member is extracted or created.
            row=index[info.filename]
            require(stat.S_IFMT(info.external_attr>>16)==stat.S_IFREG and stat.S_IMODE(info.external_attr>>16)==row['mode'],'overlay regular type/mode')
            h=hashlib.sha256();size=0
            with archive.open(info) as stream:
                for block in iter(lambda:stream.read(1024*1024),b''):h.update(block);size+=len(block)
            require(size==row['size'] and h.hexdigest()==row['sha256'],'overlay CRC/SHA')
    return dict(members=len(overlay['content']),CRC_SHA_mode_valid=True,extractions=0)


def prepare_contract():
    parser=argparse.ArgumentParser(description='ROOT-released independent actual readback only; no restore/READY')
    parser.add_argument('--execute',action='store_true',required=True)
    for key in ('authorization','restore-receipt'):
        parser.add_argument('--'+key,required=True)
        parser.add_argument('--'+key+'-size',required=True,type=int)
        parser.add_argument('--'+key+'-sha256',required=True)
    parser.add_argument('--source-owner-size',required=True,type=int)
    parser.add_argument('--source-owner-sha256',required=True)
    args=parser.parse_args()
    require(pin(SD/'source-owner.json')==dict(size=args.source_owner_size,sha256=args.source_owner_sha256),'actual frozen readback Source owner pin')
    owner=read(SD/'source-owner.json')
    for row in owner['files']:verify_descriptor(R,row)
    require(any(row['path']==str(Path(__file__).relative_to(R)) and pin(Path(__file__))=={k:row[k] for k in ('size','sha256')} for row in owner['files']),'owned executing readback')
    authorization=dict(path=args.authorization,size=args.authorization_size,sha256=args.authorization_sha256)
    restore_receipt=dict(path=args.restore_receipt,size=args.restore_receipt_size,sha256=args.restore_receipt_sha256)
    config=read(verify_descriptor(R,authorization));verify_descriptor(R,restore_receipt)
    source=read(SD/'source-contract.json')
    require(config.get('schema')=='phase380-root-pool-recovery/1' and config.get('action')=='restore' and config.get('root_restore_authorized') is True,'ROOT exact380 restore-only source')
    require(all(type(config.get(k)) is int and config[k]==0 for k in ('native_allowed','models_allowed','projection_allowed')),'restore did not grant native/model/projection')
    for key in ('source_freeze','restore_map','input_pins'):require(config[key]==source[key],'current exact source/map/pins '+key)
    require(source['readback_status']==READBACK_STATUS,'exact380 API readback status')
    reviews=config.get('reviews');require(type(reviews)is list and bool(reviews),'actual SOURCE review descriptors from ROOT required')
    for item in reviews:
        review=read(verify_descriptor(R,item['receipt']));owned=read(verify_descriptor(R,item['owner']))
        for row in owned['files']:verify_descriptor(R,row)
        require(any(row==item['receipt'] for row in owned['files']),'owned actual SOURCE review')
        require(review.get('status')==source['SOURCE_review_status'] and review.get('source_freeze')==config['source_freeze'],'actual380 SOURCE accepted closure')
        require(all(type(review.get(key))is int and review[key]==0 for key in ('native','models')),'SOURCE review not native/model acceptance')
    mapping=read(verify_descriptor(R,config['restore_map']))
    require(mapping['schema']=='phase380-attempt04-partial-reset-map/1','new attempt04 partial-reset map schema')
    for key in ('failed_run','previous_run','pool','source_root'):require(config['roots'][key]==mapping['roots'][key],'actual current roots binding '+key)
    require(Path(config['roots']['failed_run']).name.endswith('attempt04'),'failed source is attempt04 partial-install, not prior attempt')
    require(source['external_targets']['project']==mapping['project_target'] and source['external_targets']['staged']==mapping['staged_target'],'old026 authoritative targets')
    require(not D.exists() and not D.is_symlink(),'new independent readback output only')
    D.mkdir()
    contract=dict(source,authorization=authorization,restore_receipt=restore_receipt,
        files=owner['files']+[authorization,restore_receipt],ROOT_actual_release_pins_checked=True)
    save(D/'execution-contract.json',contract)
    return contract

def main():
    contract=prepare_contract()
    for row in contract['files']:verify_descriptor(R,row)
    config=read(R/contract['authorization']['path']);roots={key:Path(value) for key,value in config['roots'].items()}
    for key,row in contract['external_targets'].items():verify_descriptor(roots[row['root']],row)
    receipt=read(R/contract['restore_receipt']['path']);mapping=read(R/config['restore_map']['path'])
    for key in ('roots','source_freeze','restore_map'):require(receipt[key]==config[key],'wire '+key)
    for key in ('project_target','staged_target'):require(receipt[key]==mapping[key],'wire target '+key)
    require(receipt['failed_state']==contract['failed_state'],'failed wire state')
    saved_staged=read(roots['failed_run']/'output/failed-pool-preservation/failed-staged-files.json')
    staged_index={row['path']:row for row in saved_staged['entries']}
    staged_differences=sum(staged_index[row['target']['path']]!=row['target'] for row in mapping['staged_files'])
    expected_writes=len(mapping['file_differences'])+staged_differences
    require(len(mapping['file_differences'])==74 and staged_differences==0 and expected_writes==74,'actual partial74+staged0, not old76')
    require(mapping['known_absent_creates']==['.native-random-observer-disposable','native_random_observer_sink_v7.gd'],'exact partial2 creates')
    require(receipt.get('status')=='RESTORED_EXACT_TARGET_STATE_REMAINS_FAILED_INDEPENDENT_READBACK_PENDING','exact successful restore-only receipt status')
    require(receipt['READY_committed'] is False and receipt['writes']==expected_writes,'partial restore-only actual receipt')
    sys.addaudithook(audit);started=time.monotonic();result={};failure=None;lock=None
    try:
        state=roots['pool']/'state.json';require(pin(state)==contract['failed_state'] and read(state)['status']=='failed','state must remain original failed')
        lock=(roots['pool']/'.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        # SOURCE-exact read-only process inspector; no staged candidate/module imports.
        source=verify_descriptor(R,contract['process_inspector_source']).read_text();tree=ast.parse(source)
        selected=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name in ('process_check','stamp')]
        require(len(selected)==2,'exact process inspector functions')
        ns=dict(Path=Path,os=os,json=json,datetime=datetime,require=require)
        exec(compile(ast.Module(body=selected,type_ignores=[]),'<exact-readonly-process-inspector>','exec'),ns)
        inspections={key:ns['process_check'](roots[key]) for key in ('pool','baseline','failed_run','previous_run')}
        save(D/'process-inspection.json',inspections)
        # Requirement interpretation: no active task Game/known PGID, not universal proc visibility.
        process_rows=[];groups=set();known=set()
        # This attempt failed before parse/Game; no native cleanup record or PGID exists.
        for name in ('parse-process-result.json','native-process-result.json'):
            require(not (roots['failed_run']/'output'/name).exists(),'attempt04 must not invent parse/Game process records')
        for proc in Path('/proc').iterdir():
            if not proc.name.isdecimal():continue
            try:
                tail=(proc/'stat').read_text().rsplit(')',1)[1].split();pid=int(proc.name)
                command=(proc/'cmdline').read_bytes().split(b'\0');comm=(proc/'comm').read_text().strip()
                uid=next(line.split()[1] for line in (proc/'status').read_text().splitlines() if line.startswith('Uid:'))
            except FileNotFoundError:continue
            except PermissionError as exc:raise ValueError('uninspectable task process identity: '+proc.name) from exc
            live=tail[0]!='Z';group=int(tail[2])
            if live and (pid in known or group in groups):raise ValueError('known task PID/PGID still live')
            if live:
                executable=command[0].decode(errors='replace') if command else ''
                require(not (comm.lower().startswith(('godot','xvfb')) or Path(executable).name.lower().startswith(('godot','xvfb'))),'live Godot/Xvfb process')
            process_rows.append(dict(pid=pid,uid=int(uid),state=tail[0],pgid=group,comm=comm,
                executable=command[0].decode(errors='replace') if command else '',known_task_pid=pid in known))
        save(D/'task-process-scope.json',dict(schema='phase381-task-process-scope/1',attempt04_native_process_records='ABSENT_EXPECTED_PRE_PARSE_GAME',known_pid_group_proof_applicable=False,known_pgids=sorted(groups),known_pids=sorted(known),
            inspected=process_rows,known_task_live=None,visible_live_Godot_Xvfb=0,whole_system_proc_complete=False,
            restriction='No attempt04 native PID/PGID cleanup record exists; empty known sets are not evidence. Generic scoped matches/visible identities plus readonly flock only; permission gaps remain explicit and wholeproc is not claimed.'))

        targets={key:read(roots[row['root']]/row['path']) for key,row in contract['external_targets'].items()}
        for name,path,target in [('project',roots['pool']/'project',targets['project']),('staged',roots['pool']/'data',targets['staged']),('baseline',roots['baseline'],targets['baseline'])]:
            actual=inventory(path);save(D/(name+'-readback.json'),actual)
            require(actual==target,'full path/kind/SHA/mode/mtime mismatch: '+name)
            result[name]=dict(**counts(actual),full_path_SHA_mode_mtime_equal=True)
        previous=roots['previous_run'];retained={}
        for name in ('output','data','user'):
            retained[name]=inventory(previous/name,('compaction','driver','.native-compaction.lock') if name=='output' else (),True)
            if name=='output':retained[name]['entries'][0].pop('mtime_ns')
        save(D/'previous-retained-readback.json',retained)
        require(retained==targets['retained'],'oldrun retained tree differs')
        driver=inventory(previous/'output/driver');save(D/'previous-driver-readback.json',driver)
        require(driver==targets['driver'],'oldrun driver differs')
        result['previous_retained']={key:counts(value) for key,value in retained.items()};result['previous_driver']=counts(driver)
        bundle=previous/'output/compaction';bundle_manifest=read(verify_descriptor(previous,contract['previous_bundle_manifest']))
        for name,sha in bundle_manifest['files'].items():require(pin(canonical(bundle,name))['sha256']==sha,'old026 bundle member SHA')
        for name,sha in bundle_manifest['driver_sha256'].items():require(pin(canonical(previous/'output/driver',name))['sha256']==sha,'old026 bundle driver SHA')
        old_overlay=read(bundle/'overlay-manifest.json')
        result['previous_overlay']=verify_overlay_archive(bundle/'overlay.zip',old_overlay,targets['project'])

        failed=roots['failed_run'];expected_owner=read(R/contract['failed_capsule_manifest']['path'])
        require(expected_owner['schema']=='standalone-attempt04-partial-install-failure-capsule/1' and expected_owner['file_count']==173 and len(expected_owner['files'])==173,'real377 capsule manifest')
        require(all(not name.startswith('run/') or name.startswith(('run/output/','run/data/')) for name in expected_owner['files']),'exact failed output/data member selection')
        prefix='run/'
        expected={name[len(prefix):]:row for name,row in expected_owner['files'].items() if name.startswith(prefix)}
        actual_failed={name:inventory(failed/name) for name in ('output','data')}
        actual_files={name+'/'+row['path']:{k:row[k] for k in ('size','sha256')} for name,tree in actual_failed.items() for row in tree['entries'] if row['kind']=='file'}
        require(actual_files==expected,'failed original source/log/UI/preservation file set/hash mismatch')
        save(D/'failed-retained-readback.json',actual_failed)
        result['failed_retained']=dict(files=len(actual_files),bytes=sum(x['size'] for x in actual_files.values()),
            exact_capsule_owner_file_set_and_hash=True,observation_semantics_read=False,
            historical_mode_mtime_comparison='No prior full failed output/data metadata target asserted; actual metadata recorded.')
        user=inventory(failed/'user',relaxed=True);save(D/'failed-user-observed.json',user)
        result['failed_user']=dict(**counts(user),historical_equality_claim=False,scope='Observed hash/metadata only; old frozen public capsule explicitly excludes user subtree.')
        saved=failed/'output/failed-pool-preservation'
        for row in read(R/contract['input_pins']['path'])['files']:verify_descriptor(roots[row['root']],row)
        overlay=read(saved/'overlay-manifest.json');failed_target=read(saved/'failed-project-files.json')
        index={row['path']:row for row in failed_target['entries']}
        with zipfile.ZipFile(saved/'failed-project-overlay.zip') as archive:
            require(len(archive.infolist())==len(set(archive.namelist())) and set(archive.namelist())==set(overlay['content']),'failed overlay exact member set')
            for info in archive.infolist():
                row=index[info.filename];require(stat.S_IFMT(info.external_attr>>16)==stat.S_IFREG and stat.S_IMODE(info.external_attr>>16)==row['mode'],'failed overlay mode/type')
                h=hashlib.sha256();size=0
                with archive.open(info) as stream:
                    for block in iter(lambda:stream.read(1024*1024),b''):h.update(block);size+=len(block)
                require(size==row['size'] and h.hexdigest()==row['sha256'],'failed overlay CRC/hash')
        result['preserved_failed_overlay']=dict(members=len(overlay['content']),CRC_SHA_mode_valid=True,extractions=0)
        require(pin(state)==contract['failed_state'] and read(state)['status']=='failed','state changed during independent readback')
        for row in contract['files']:verify_descriptor(R,row)
        for row in contract['external_targets'].values():verify_descriptor(roots[row['root']],row)
        result['process_inspection']=dict(active_matches=0,inspection_gaps=sum(len(v['inspection_gaps']) for v in inspections.values()),whole_system_proc_complete=False,known_task_live=None,known_native_pid_group_record=False,visible_live_Godot_Xvfb=0,exclusive_pool_lock_acquired_readonly=True,processes_launched=0,source_exact_functions=2)
    except BaseException as exc:
        failure=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc());save(D/'first-failure.json',failure)
    finally:
        if lock is not None:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
    save(D/'audit.json',dict(AUDIT,read_scope='Actual direct tree bytes/metadata; business observations opaque, no business expected decoding.',no_external_write_attempts=not AUDIT['blocked']))
    value=dict(schema='phase381-independent-physical-readback/1',status=READBACK_STATUS if failure is None else 'BLOCKED_INDEPENDENT380_RESTORED_POOL_READBACK',
        **{key:receipt[key] for key in ('roots','restore_map','source_freeze','project_target','staged_target','failed_state')},
        restore_receipt=contract['restore_receipt'],observations=result,failure=failure,
        native=0,models=0,Godot=0,processes_launched=0,actual_restore_calls=0,READY_commits=0,projection_calls=0,
        elapsed_seconds=time.monotonic()-started,no_more_writes=True,
        scope='Independent actual full-target read-only physical validation; ROOT READY commit and new native attempt remain separate. No Game tree copied.')
    if failure is None:
        value.update(project_readback=desc(D/'project-readback.json'),staged_readback=desc(D/'staged-readback.json'))
    save(D/'review.json',value)
    selected=[p for p in D.rglob('*') if p.is_file()]
    selected += [SD/'CAPSULE377.json',SD/'source-contract.json',SD/'source-owner.json',SD/'readonly-process-inspector.py']
    selected+=[R/'docs/phase384_readback_consumer_pin_and_receipt_status_repair_spec.md',R/'tests/phase384_independent_restored_readback.py']
    save(D/'owned-files.json',dict(schema='phase381-independent-readback-owner/1',files=[desc(p) for p in sorted(selected)],no_more_writes=True,external_paths_provenance_only=True))
    for row in read(D/'owned-files.json')['files']:verify_descriptor(R,row)
    print(json.dumps(dict(status=value['status'],review=desc(D/'review.json'),owner=desc(D/'owned-files.json'),observations=result,failure=failure)))
    return 0 if failure is None else 1

if __name__=='__main__':raise SystemExit(main())
