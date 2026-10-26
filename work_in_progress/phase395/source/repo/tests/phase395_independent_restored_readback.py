"""Read-only physical395 complete-install restored target validation. No recovery, READY or process execution."""
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
D=R/'data/phase395-independent-actual-readback-first-001'
SD=R/'data/phase395-independent-readback-source'
AUDIT=dict(write_attempts=0,blocked=[],subprocesses=0,network=0)
READBACK_STATUS = 'INDEPENDENT395_ATTEMPT05_RESTORED_POOL_EXACT_TARGET_READBACK_PASS'

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
    require(type(row) is dict and set(row) in ({'path','size','sha256'},{'root','path','size','sha256'}),'closed actual descriptor')
    require(type(row['size']) is int and row['size']>=0 and type(row['sha256']) is str and len(row['sha256'])==64,'strict descriptor fields')
    path=canonical(root,row['path']);info=path.lstat()
    require(stat.S_ISREG(info.st_mode) and info.st_nlink==1,'ordinary nlink1 descriptor source')
    require(pin(path)=={k:row[k] for k in ('size','sha256')},'descriptor drift: '+str(path));return path
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
    require(config.get('schema')=='phase395-root-pool-recovery/1' and config.get('action')=='restore' and config.get('root_restore_authorized') is True,'ROOT exact395 restore-only source')
    require(all(type(config.get(k)) is int and config[k]==0 for k in ('native_allowed','models_allowed','projection_allowed')),'restore did not grant native/model/projection')
    for key in ('source_freeze','restore_map','input_pins'):require(config[key]==source[key],'current exact source/map/pins '+key)
    require(source['readback_status']==READBACK_STATUS,'exact395 API readback status')
    require(config.get('source_owner')==source['recovery_source_owner'],'actual recovery SOURCE owner binding')
    require(config.get('terminal_component_context')==source['terminal_component_context'],'actual Root bounded component context')
    context=read(verify_descriptor(R,source['terminal_component_context']))
    require(context.get('status')=='ROOT_391_BOUNDED_COMPONENT_ACCEPTED_LANGUAGE_AND_NATIVE_PENDING' and context.get('restore_allowed')==0 and type(context.get('restore_allowed')) is int,'component context is not restore authority')
    reviews=config.get('reviews');require(type(reviews)is list and bool(reviews),'actual SOURCE review descriptors from ROOT required')
    for item in reviews:
        review=read(verify_descriptor(R,item['receipt']));owned=read(verify_descriptor(R,item['owner']))
        for row in owned['files']:verify_descriptor(R,row)
        require(any(row==item['receipt'] for row in owned['files']),'owned actual SOURCE review')
        require(review.get('status')==source['SOURCE_review_status'] and review.get('source_freeze')==config['source_freeze'],'actual395 recovery SOURCE accepted closure')
        require(all(type(review.get(key))is int and review[key]==0 for key in ('native','models')),'SOURCE review not native/model acceptance')
    mapping=read(verify_descriptor(R,config['restore_map']))
    require(mapping['schema']=='phase395-attempt05-complete-restore-source-map/1','actual395 complete05 map schema')
    for key in ('failed_run','previous_run','pool','source_root'):require(config['roots'][key]==mapping['roots'][key],'actual current roots binding '+key)
    require(Path(config['roots']['failed_run']).name.endswith('attempt05'),'failed source is completed attempt05')
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
    expected_writes=verify_complete_saved_contract(roots,contract,mapping)
    require(receipt.get('status')=='RESTORED_EXACT_TARGET_STATE_REMAINS_FAILED_INDEPENDENT_READBACK_PENDING','exact successful restore-only receipt status')
    require(receipt['READY_committed'] is False and receipt['writes']==expected_writes,'complete restore-only actual receipt')
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
        process_rows=[]
        groups,known,historical_process_controls=attempt05_process_controls(roots,contract)
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
        save(D/'task-process-scope.json',dict(schema='phase395-task-process-scope/1',attempt05_process_records=historical_process_controls,known_pid_group_proof_applicable=True,known_pgids=sorted(groups),known_pids=sorted(known),
            inspected=process_rows,known_task_live=0,visible_live_Godot_Xvfb=0,whole_system_proc_complete=False,
            restriction='Recorded historical PID/PGIDs are not starttime identities; live matching values conservatively block. Zombies are not claimed reaped; scoped visibility gaps remain explicit.'))

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
        result['failed_capsule']=verify_capsule385(contract,expected_owner)
        require(all(not name.startswith('run/') or name.startswith(('run/output/','run/data/')) for name in expected_owner['files']),'exact failed output/data member selection')
        prefix='run/'
        expected={name[len(prefix):]:row for name,row in expected_owner['files'].items() if name.startswith(prefix)}
        actual_failed={name:inventory(failed/name) for name in ('output','data')}
        actual_files={name+'/'+row['path']:{k:row[k] for k in ('size','sha256','mode','mtime_ns')} for name,tree in actual_failed.items() for row in tree['entries'] if row['kind']=='file'}
        require(actual_files==expected,'failed original source/log/UI/preservation file set/hash mismatch')
        save(D/'failed-retained-readback.json',actual_failed)
        result['failed_retained']=dict(files=len(actual_files),bytes=sum(x['size'] for x in actual_files.values()),
            exact_capsule_owner_file_set_and_hash=True,observation_semantics_read=False,
            historical_mode_mtime_comparison='All367 file mode/mtime equal actual385 capsule metadata; directory metadata recorded without historical equality claim.')
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
        result['process_inspection']=dict(active_matches=0,inspection_gaps=sum(len(v['inspection_gaps']) for v in inspections.values()),whole_system_proc_complete=False,known_task_live=0,known_native_pid_group_record=True,visible_live_Godot_Xvfb=0,exclusive_pool_lock_acquired_readonly=True,processes_launched=0,source_exact_functions=2)
    except BaseException as exc:
        failure=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc());save(D/'first-failure.json',failure)
    finally:
        if lock is not None:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
    save(D/'audit.json',dict(AUDIT,read_scope='Actual direct tree bytes/metadata; business observations opaque, no business expected decoding.',no_external_write_attempts=not AUDIT['blocked']))
    value=dict(schema='phase395-independent-physical-readback/1',status=READBACK_STATUS if failure is None else 'BLOCKED_INDEPENDENT395_RESTORED_POOL_READBACK',
        **{key:receipt[key] for key in ('roots','restore_map','source_freeze','project_target','staged_target','failed_state')},
        restore_receipt=contract['restore_receipt'],observations=result,failure=failure,
        native=0,models=0,Godot=0,processes_launched=0,actual_restore_calls=0,READY_commits=0,projection_calls=0,
        elapsed_seconds=time.monotonic()-started,no_more_writes=True,
        scope='Independent actual full-target read-only physical validation; ROOT READY commit and new native attempt remain separate. No Game tree copied.')
    if failure is None:
        value.update(project_readback=desc(D/'project-readback.json'),staged_readback=desc(D/'staged-readback.json'))
    save(D/'review.json',value)
    selected=[p for p in D.rglob('*') if p.is_file()]
    selected += [SD/'CAPSULE385.json',SD/'source-contract.json',SD/'source-owner.json',SD/'readonly-process-inspector.py']
    selected+=[R/'docs/phase395_complete_restore_source_implementation_addendum.md',R/'tests/phase395_independent_restored_readback.py']
    save(D/'owned-files.json',dict(schema='phase395-independent-readback-owner/1',files=[desc(p) for p in sorted(selected)],no_more_writes=True,external_paths_provenance_only=True))
    for row in read(D/'owned-files.json')['files']:verify_descriptor(R,row)
    print(json.dumps(dict(status=value['status'],review=desc(D/'review.json'),owner=desc(D/'owned-files.json'),observations=result,failure=failure)))
    return 0 if failure is None else 1

"""Independent saved/process/capsule checks for the395 readonly physical reader."""


def verify_complete_saved_contract(roots, contract, mapping):
    # Each consumed saved leaf is checked before metadata decoding. No recovery imports.
    for row in read(verify_descriptor(R, contract['input_pins']))['files']:
        verify_descriptor(roots[row['root']], row)
    failed = roots['failed_run']; previous = roots['previous_run']
    load = lambda name: read(canonical(failed, name))
    journal = load('output/source-preimages/preimages.json')
    prior = load('output/previous-source-preimages/inventory.json')
    reset = load('output/prior-observer-reset.json')
    before = load('output/pool-before.json')
    target = read(canonical(previous, 'output/compaction/project-files.json'))
    target_data = read(canonical(previous, 'output/compaction/staged-inputs.json'))
    saved = load('output/failed-pool-preservation/failed-project-files.json')
    staged = load('output/failed-pool-preservation/failed-staged-files.json')
    base = load('output/failed-pool-preservation/baseline-files.json')
    require(before == dict(baseline=base,project=saved,staged=staged), 'saved05 equals complete before-native manifests')
    require(target == prior['project'] == reset['before'], 'old026 authoritative target/reset')
    index = lambda value: {row['path']:row for row in value['entries']}
    for value in (target,target_data,saved,staged,base,reset['after']):
        require(len(index(value)) == len(value['entries']), 'unique saved manifest paths')
    actual,wanted,start = index(saved),index(target),index(reset['after'])
    data,wanted_data = index(staged),index(target_data)
    require(actual.keys() == wanted.keys() and data.keys() == wanted_data.keys(), 'complete existing target path sets')
    require(all(actual[k]['kind'] == wanted[k]['kind'] for k in actual) and all(data[k]['kind'] == wanted_data[k]['kind'] for k in data), 'complete target kinds')
    file_diff = {k for k in actual if actual[k]!=wanted[k] and actual[k]['kind']=='file'}
    dir_diff = {k for k in actual if actual[k]!=wanted[k] and actual[k]['kind']=='directory'}
    require(len(mapping['file_differences']) == len(file_diff) and {row['path'] for row in mapping['file_differences']} == file_diff, 'independent complete project difference set')
    require(len(mapping['directory_differences']) == len(dir_diff) and {row['path'] for row in mapping['directory_differences']} == dir_diff, 'independent complete directory difference set')
    require({row['target']['path'] for row in mapping['staged_files']} == {k for k in wanted_data if wanted_data[k]['kind']=='file'}, 'all staged target file writes')
    driver = load('output/driver/source-map.json')['files']
    declared = {row['source']['path']:row for row in driver}
    require(len(declared) == len(driver), 'unique actual archived SOURCE')
    frozen = contract['installed_source_freeze']
    require(declared[frozen['path']]['source'] == frozen, 'actual380 installed SOURCE freeze')
    archived_freeze = verify_descriptor(failed, dict(path='output/driver/'+declared[frozen['path']]['file'], **{k:frozen[k] for k in ('size','sha256')}))
    source = read(archived_freeze)
    payloads = {name:row['after'] for name,row in source['paths'].items()}
    require(len(payloads)==75 and len(source['artifacts'])==3 and not(set(payloads)&set(source['artifacts'])), 'complete installed75+3 declaration')
    payloads.update({name:{k:row[k] for k in ('size','sha256')} for name,row in source['artifacts'].items()})
    jm = {row['path']:row for row in journal}
    require(len(jm)==len(journal)==len(payloads) and jm.keys()==payloads.keys(), 'complete unique actual install journal')
    checked=0
    for name,row in jm.items():
        require(row['after']==payloads[name]=={k:actual[name][k] for k in ('size','sha256')}, 'installed source/journal/failed bytes')
        if row['before'] is None:
            require(name not in start and row['backup'] is None, 'exact before-install absence only')
        else:
            require(row['before']==dict(identity={k:start[name][k] for k in ('size','sha256')},mode=start[name]['mode'],mtime_ns=start[name]['mtime_ns']), 'before-image/reset metadata')
            verify_descriptor(failed,dict(path='output/source-preimages/'+row['backup'],**row['before']['identity']));checked+=1
    for i,row in enumerate(prior['patch']['patches']):
        verify_descriptor(failed,dict(path='output/previous-source-preimages/'+str(i),size=row['after_size'],sha256=row['after_sha256']))
    verify_descriptor(failed,dict(path='output/previous-source-preimages/marker',**{k:wanted['.native-random-observer-disposable'][k] for k in ('size','sha256')}))
    for row in mapping['file_differences']:
        require(row['before_preserved']==actual[row['path']] and row['target']==wanted[row['path']], 'exact mapped targets')
        payload=verify_descriptor(roots[row['payload']['root']],row['payload'])
        require(pin(payload)=={k:row['target'][k] for k in ('size','sha256')}, 'old026 target payload bytes')
    for row in mapping['staged_files']:
        require(row['target']==wanted_data[row['target']['path']], 'exact staged target')
        payload=verify_descriptor(roots[row['payload']['root']],row['payload'])
        require(pin(payload)=={k:row['target'][k] for k in ('size','sha256')}, 'old026 staged payload bytes')
    expected_writes=len(file_diff)+len(mapping['staged_files'])
    expected=contract['complete_install']
    require((len(file_diff),len(dir_diff),len(mapping['staged_files']),sum(data[k]!=wanted_data[k] for k in wanted_data if wanted_data[k]['kind']=='file'),expected_writes,checked,len(prior['patch']['patches'])) ==
            (expected['project_file_differences'],expected['directory_differences'],expected['staged_files'],expected['staged_file_differences'],expected['expected_writer_files'],expected['checked_install_backups'],expected['checked_previous_patch_backups']), 'independently derived complete writer counts')
    return expected_writes


def attempt05_process_controls(roots, contract):
    groups=set();pids=set();zombies=set();observed={}
    for name,row in contract['process_controls'].items():
        value=read(verify_descriptor(roots['failed_run'],row))
        parse=name=='parse-process-result.json'
        require(type(value['parse_only']) is bool and value['parse_only'] is parse and type(value['actual_oracle_processes']) is int and value['actual_oracle_processes']==(0 if parse else 1), 'actual05 parse/native process control identity')
        cleanup=value['cleanup'];group=cleanup['pgid']
        require(type(group) is int and group>0, 'actual positive recorded process group');groups.add(group)
        for key in ('before','after','live_remaining'):
            require(type(cleanup[key]) is list, 'recorded process member list')
            for item in cleanup[key]:
                require(type(item) is dict and type(item['pid']) is int and item['pid']>0 and type(item['live']) is bool and type(item['state']) is str, 'recorded process member primitives')
                pids.add(item['pid'])
        for pid in cleanup['zombies_not_claimed_reaped']:
            require(type(pid) is int and pid>0,'recorded zombie identity');pids.add(pid);zombies.add(pid)
        observed[name]=dict(identity=row,parse_only=value['parse_only'],actual_oracle_processes=value['actual_oracle_processes'],exit_code=value['exit_code'],
            process_clean_exit=value['process_clean_exit'],abort_reason=value['abort_reason'],timed_out=value['timed_out'],cleanup=cleanup)
    require(set(observed)=={'parse-process-result.json','native-process-result.json'},'both real05 process records required')
    return groups,pids,dict(records=observed,historical_zombies=sorted(zombies),pid_reuse='Historical records have no starttime; live matching PID/PGID conservatively blocks, no identity/reaping claim')


def verify_capsule385(contract, manifest):
    archive_row=contract['capsule_archive']
    root=Path(contract['capsule_root']);require(root.is_dir() and not any(p.is_symlink() for p in (root,*root.parents)), 'explicit unlinked readonly capsule root')
    path=verify_descriptor(root,archive_row)
    require(manifest['schema']=='standalone-native385-failure-capsule/1' and manifest['file_count']==len(manifest['files'])==contract['capsule_members'], 'real complete385 capsule manifest')
    require(archive_row['size']==manifest['archive_size'] and archive_row['sha256']==manifest['archive_sha256'], 'capsule archive/manifest binding')
    source_members=contract['capsule_non_run_members']
    require(set(source_members)=={name for name in manifest['files'] if not name.startswith('run/')}, 'exact non-run capsule source ledger')
    with zipfile.ZipFile(path) as archive:
        infos=archive.infolist()
        require(len(infos)==len(set(archive.namelist())) and set(archive.namelist())==set(manifest['files']), 'exact unique380 capsule members')
        for info in infos:
            canonical(D,info.filename)
            require(stat.S_IFMT(info.external_attr>>16)==stat.S_IFREG, 'ordinary archived capsule member')
            expected=manifest['files'][info.filename]
            require(type(expected) is dict and set(expected)=={'size','sha256','mode','mtime_ns'}, 'closed385 capsule file metadata')
            require(stat.S_IMODE(info.external_attr>>16)==expected['mode'], 'capsule original archive file mode')
            h=hashlib.sha256();size=0
            with archive.open(info) as stream:
                for block in iter(lambda:stream.read(1048576),b''):h.update(block);size+=len(block)
            require(dict(size=size,sha256=h.hexdigest())=={k:expected[k] for k in ('size','sha256')}, 'capsule CRC/SHA/size')
            if info.filename in source_members:
                binding=source_members[info.filename]
                require(binding['identity']==expected, 'cross-root capsule member descriptor')
                require(binding['storage']=='source', 'all13 actual non-run source origins required')
                actual=verify_descriptor(Path(binding['root']),dict(path=binding['path'],**{k:expected[k] for k in ('size','sha256')}))
                require(pin(actual)=={k:expected[k] for k in ('size','sha256')}, 'actual non-run SOURCE member bytes')
                info_actual=actual.lstat()
                require(stat.S_IMODE(info_actual.st_mode)==expected['mode'] and info_actual.st_mtime_ns==expected['mtime_ns'], 'actual non-run original mode/mtime')
    return dict(members=len(manifest['files']),bytes=sum(row['size'] for row in manifest['files'].values()),non_run_members=len(source_members),CRC_SHA_valid=True,extractions=0,business_semantics_read=False)

if __name__=='__main__':raise SystemExit(main())
