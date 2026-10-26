"""Bound380 finite real-API controls. No actual host execution or pool access."""
import argparse
import contextlib
import copy
import ctypes
import datetime
import fcntl
import hashlib
import importlib.util
import json
import os
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
import traceback
import zipfile
from pathlib import Path

R=Path(__file__).resolve().parents[1]
SD=R/'data/phase380-independent-bound-source'
D=R/'data/phase380-independent-bound-first-001'
CALLS=[];RESULTS=[];AUDIT={'blocked':[]};MODULES=[]
KNOWN={'.native-random-observer-disposable','native_random_observer_sink_v7.gd'}

def pin(p):
    h=hashlib.sha256();size=0
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(65536),b''):h.update(block);size+=len(block)
    return dict(size=size,sha256=h.hexdigest())
def read(p):return json.loads(Path(p).read_text())
def save(name,x):
    p=D/name;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:json.dump(x,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
    return p
def require(x,m):
    if not x:raise AssertionError(m)
def load(name,file):
    p=SD/'SOURCE'/file;spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);MODULES.append(dict(name=name,path=str(p),**pin(p)));return m

def call(label,fn,args,accept=True,kwargs=None):
    try:result=fn(*args,**(kwargs or {}))
    except (ValueError,FileNotFoundError) as exc:
        CALLS.append(dict(label=label,API=fn.__module__+'.'+fn.__name__,outcome='reject',exception=type(exc).__name__,message=str(exc)))
        require(not accept,'unexpected rejection '+label+': '+str(exc));return None
    except BaseException as exc:
        CALLS.append(dict(label=label,API=fn.__module__+'.'+fn.__name__,outcome='unexpected_exception',exception=type(exc).__name__,message=str(exc)));raise
    else:
        CALLS.append(dict(label=label,API=fn.__module__+'.'+fn.__name__,outcome='accept',return_type=type(result).__name__))
        require(accept,'unexpected acceptance '+label);return result

def audit(event,args):
    if event in ('subprocess.Popen','os.system','os.fork','os.posix_spawn','socket.__new__','socket.connect','socket.bind'):
        AUDIT['blocked'].append(dict(event=event));raise PermissionError('no processes or network')
    if event=='open' and not isinstance(args[0],int):
        p=Path(os.fsdecode(args[0])).absolute();mode=args[1];flags=args[2]
        write=isinstance(mode,str) and any(c in mode for c in 'wax+') or isinstance(flags,int) and bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
        if write:allowed=p.is_relative_to(D)
        else:allowed=p.is_relative_to(D) or p.is_relative_to(SD) or p in READ_FILES or any(p.is_relative_to(root) for root in READ_ROOTS) or p.is_relative_to(Path(sys.base_prefix)/'lib') and not any(x in p.parts for x in ('site-packages','dist-packages'))
        if not allowed:AUDIT['blocked'].append(dict(event=event,path=str(p),write=write));raise PermissionError('outside frozen Source/unit/saved evidence boundary')
    if event in ('os.rename','os.remove','os.rmdir','os.mkdir','os.chmod','os.utime','os.link','os.symlink','os.truncate'):
        # Destination-aware check; source is also owned for all mutable harness cases.
        paths=[a for a in args[:2] if isinstance(a,(str,bytes,Path))]
        for item in paths:
            p=Path(os.fsdecode(item)).absolute()
            # symlink's relative link text is not a filesystem mutation target.
            if event=='os.symlink' and item==args[0]:continue
            if not p.is_relative_to(D):AUDIT['blocked'].append(dict(event=event,path=str(p)));raise PermissionError('no external mutation')

@contextlib.contextmanager
def changed_source(root,row,kind):
    p=root/row['path'];data=p.read_bytes();info=p.stat();other=p.with_name(p.name+'.unit-original')
    try:
        if kind=='missing':p.unlink()
        elif kind=='wronghash':p.write_bytes(bytes([data[0]^1])+data[1:])
        elif kind=='directory':p.unlink();p.mkdir()
        elif kind in ('symlink','hardlink'):
            p.rename(other)
            if kind=='symlink':p.symlink_to(other.name)
            else:os.link(other,p)
        else:raise AssertionError('unknown finite mutation')
        yield
    finally:
        if p.is_symlink() or p.is_file():p.unlink()
        elif p.is_dir():p.rmdir()
        if other.exists():other.rename(p)
        else:p.write_bytes(data)
        os.chmod(p,stat.S_IMODE(info.st_mode));os.utime(p,ns=(info.st_atime_ns,info.st_mtime_ns))

def resolver_cases(host,storage,freeze):
    require(not (R/'data/phase380-payload-source/collector.gd').exists(),'no guessed collector copy')
    graph=call('R01.actual-reused-collector',host.resolve_execute_payloads,[R,freeze])
    require(len(graph['patches'])==75 and len(graph['artifacts'])==3 and len(graph['case_inputs'])==3,'actual graph closure')
    save('actual-source-graph.json',graph)
    result=call('R02.actual-fullgraph',host.verify_execute_payloads,[R,graph])
    require(result['install_files']==78 and result['install_bytes']==807199,'actual corpus limits')
    RESULTS.extend([dict(id='R01',status='PASS',scope='real Source resolver only, not hostplan'),dict(id='R02',status='PASS',scope='actual graph source identity only')])
    mirror=D/'source-mirror';mirror.mkdir()
    for row in freeze['files']:
        target=mirror/row['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/row['path'],target)
        require(pin(target)=={k:row[k] for k in ('size','sha256')},'Source mirror drift')
    save('source-mirror-identity.json',dict(files=len(freeze['files']),bytes=sum(row['size'] for row in freeze['files']),Game_copy=False))
    patch=graph['patches'][0]['source'];arts=list(graph['artifacts'].values());inp=graph['case_inputs']['custom_player.json'];schema=graph['source_bindings']['schema_module']
    installed_paths={x['source']['path'] for x in graph['patches']}|{x['path'] for x in arts}|{x['path'] for x in graph['case_inputs'].values()}|{x['path'] for x in graph['source_bindings'].values()}
    driver=next(x for x in graph['driver_sources'] if x['path'] not in installed_paths and x['size']>0)
    for tag,row in [('patch',patch)]+[('artifact'+str(i),a) for i,a in enumerate(arts)]+[('input',inp),('schema',schema),('driver',driver)]:
        with changed_source(mirror,row,'missing'):call('R03.'+tag,host.verify_execute_payloads,[mirror,graph],False)
    RESULTS.append(dict(id='R03',status='PASS',variants=7))
    for tag,row in [('patch',patch),('artifact',arts[0]),('input',inp),('schema',schema),('driver',driver)]:
        with changed_source(mirror,row,'wronghash'):call('R04.'+tag,host.verify_execute_payloads,[mirror,graph],False)
    RESULTS.append(dict(id='R04',status='PASS',variants=5))
    for tag,key,value in [('boolsize','size',True),('negative','size',-1),('string','size','1'),('badhash','sha256','bad'),('extra','unexpected',True)]:
        row=copy.deepcopy(arts[0]);row[key]=value;call('R05.'+tag,storage.check_source_descriptor,[mirror,row],False)
    RESULTS.append(dict(id='R05',status='PASS',variants=5))
    with changed_source(mirror,arts[0],'directory'):call('R06',host.verify_execute_payloads,[mirror,graph],False)
    RESULTS.append(dict(id='R06',status='PASS'))
    for kind in ('symlink','hardlink'):
        with changed_source(mirror,arts[0],kind):call('R07.'+kind,host.verify_execute_payloads,[mirror,graph],False)
    RESULTS.append(dict(id='R07',status='PASS',variants=2))
    for name in ('../outside',str((D/'outside').absolute())):
        row=copy.deepcopy(arts[0]);row['path']=name;call('R08.'+name,storage.check_source_descriptor,[mirror,row],False)
    RESULTS.append(dict(id='R08',status='PASS',variants=2))
    bad=copy.deepcopy(graph);row=copy.deepcopy(bad['driver_sources'][0]);row['sha256']='0'*64;bad['driver_sources'].append(row);call('R09',host.verify_execute_payloads,[mirror,bad],False);RESULTS.append(dict(id='R09',status='PASS'))
    bad=copy.deepcopy(graph);bad['patches'][0]['target']='native_combat_capture.gd';call('R10',host.verify_execute_payloads,[mirror,bad],False);RESULTS.append(dict(id='R10',status='PASS'))
    for which in ('schema','collector'):
        bad=copy.deepcopy(graph)
        if which=='schema':del bad['source_bindings']['schema_module']
        else:del bad['artifacts']['native_combat_capture.gd']
        call('R11.'+which,host.verify_execute_payloads,[mirror,bad],False)
    RESULTS.append(dict(id='R11',status='PASS',variants=2))
    mirrored=call('R12.resolve-before-drift',host.resolve_execute_payloads,[mirror,freeze])
    with changed_source(mirror,arts[0],'wronghash'):call('R12.verify-after-drift',host.verify_execute_payloads,[mirror,mirrored],False)
    RESULTS.append(dict(id='R12',status='PASS',scope='real helper + static prelease caller proof; not hostplan execution'))

def adapt_install_fixture(helper,parent,name):
    f=helper.build_install_fixture(parent,name)
    f['freeze']['artifacts']=copy.deepcopy(f['artifacts'])
    rows=[dict(path=x['after_path'],**x['after']) for x in f['freeze']['paths'].values()]+list(f['artifacts'].values())+list(f['input_authorities'].values())
    f['freeze']['files']=list({r['path']:r for r in rows}.values());return f

def installer_cases(storage,helper):
    parent=D/'installer';parent.mkdir()
    f=adapt_install_fixture(helper,parent,'I01');before=helper.observed_targets(f);save('installer/I01-before.json',before)
    journal=call('I01.publicinstall',storage.install,[f['source'],f['project'],f['freeze'],f['artifacts'],f['backup']])
    observed=helper.verify_install_success(f,journal);save('installer/I01-actual.json',dict(observed,journal=journal,after=helper.observed_targets(f)));RESULTS.append(dict(id='I01',status='PASS',installed_targets=5))
    variants=[('I02','missing'),('I03.artifact','wronghash'),('I04','directory'),('I05.symlink','symlink'),('I05.hardlink','hardlink'),('I06.escape','unsafe')]
    done=set()
    for label,kind in variants:
        f=adapt_install_fixture(helper,parent,label)
        if kind=='wronghash':
            path=f['source']/f['artifacts']['native_combat_capture.gd']['path'];raw=path.read_bytes();path.write_bytes(bytes([raw[0]^1])+raw[1:])
        else:helper.mutate_artifact(f,'native_combat_capture.gd',kind)
        if kind=='unsafe':
            oldpath=f['freeze']['artifacts']['native_combat_capture.gd']['path']
            newrow=copy.deepcopy(f['artifacts']['native_combat_capture.gd']);f['freeze']['artifacts']=copy.deepcopy(f['artifacts'])
            f['freeze']['files']=[newrow if row['path']==oldpath else row for row in f['freeze']['files']]
        before=helper.observed_targets(f);call(label,storage.install,[f['source'],f['project'],f['freeze'],f['artifacts'],f['backup']],False)
        require(helper.observed_targets(f)==before and not f['backup'].exists(),'direct rejection changed target/backups '+label);save('installer/'+label+'-rejection.json',dict(before=before,after=helper.observed_targets(f)))
        done.add(label.split('.')[0])
    f=adapt_install_fixture(helper,parent,'I03.patch');payload=f['source']/f['freeze']['paths']['Core/A.gd']['after_path'];raw=payload.read_bytes();payload.write_bytes(bytes([raw[0]^1])+raw[1:]);before=helper.observed_targets(f);call('I03.patch',storage.install,[f['source'],f['project'],f['freeze'],f['artifacts'],f['backup']],False);require(helper.observed_targets(f)==before,'patch rejection mutation')
    f=adapt_install_fixture(helper,parent,'I06.overlap');f['artifacts']['Core/A.gd']=f['artifacts']['native_combat_capture.gd'];f['freeze']['artifacts']=copy.deepcopy(f['artifacts']);before=helper.observed_targets(f);call('I06.overlap',storage.install,[f['source'],f['project'],f['freeze'],f['artifacts'],f['backup']],False);require(helper.observed_targets(f)==before,'overlap changed targets')
    for kind in ('wrongbefore','hardlink'):
        f=adapt_install_fixture(helper,parent,'I07.'+kind);path=f['project']/'Core/A.gd'
        if kind=='wrongbefore':path.write_bytes(b'not the before bytes')
        else:os.link(path,path.with_name('hardlink-alias'))
        before=helper.observed_targets(f);call('I07.'+kind,storage.install,[f['source'],f['project'],f['freeze'],f['artifacts'],f['backup']],False);require(helper.observed_targets(f)==before and not f['backup'].exists(),'target rejection mutated')
    for id in ('I02','I03','I04','I05','I06','I07'):RESULTS.append(dict(id=id,status='PASS',scope='real direct public helper, no HOST preflight'))

def partial_fixture(c,parent,name):
    root=parent/name;root.mkdir();pool=root/'pool';pool.mkdir();project=pool/'project';data=pool/'data';project.mkdir();data.mkdir()
    roots=dict(pool=pool,baseline=root/'baseline',failed_run=root/'failed-run',previous_run=root/'previous-run',source_root=root/'source')
    for k,p in roots.items():
        if k!='pool':p.mkdir()
    payloads=root/'payloads';payloads.mkdir()
    (pool/'state.json').write_text('{"status":"failed","scope":"SYNTHETIC_MUTATION_COMPONENT_ONLY"}\n')
    (project/'neutral.txt').write_bytes(b'tiny retained file\n');(data/'custom_player.json').write_text('{"synthetic":true}\n')
    raw={'.native-random-observer-disposable':b'disposable-observation-copy\n','native_random_observer_sink_v7.gd':b'# tiny synthetic restored sink source\n'}
    for name,b in raw.items():(project/name).write_bytes(b);(payloads/name).write_bytes(b)
    for p in [project,*project.iterdir(),data,*data.iterdir()]:os.chmod(p,0o700 if p.is_dir() else 0o600);os.utime(p,ns=(1700000000000000000,1700000000000000000))
    target=c.inventory(project);target_data=c.inventory(data)
    for name in KNOWN:(project/name).unlink()
    failed=c.inventory(project);failed_data=c.inventory(data);index=c.index(target)
    evidence=dict(failed=failed,failed_data=failed_data,target=target,target_data=target_data,failed_state=pin(pool/'state.json'),payloads=[('project',name,payloads/name,index[name]) for name in sorted(KNOWN)],known_absent_creates=sorted(KNOWN),bundle=root/'unused-bundle',relocations={})
    return dict(root=root,roots=roots,evidence=evidence,output=root/'operations',label='SYNTHETIC_EVIDENCE_DTO_NOT_PRODUCTION_VERIFIED')

def partial_cases(partial,recovery,c,helper,freeze):
    # Real saved proof is readonly; it is not an actual restore or twelve-carrier positive.
    saved=call('P.SAVED.actual-analysis',partial.analyze_saved_partial,[R,Path(CONTRACT['saved_failed_run']),Path(CONTRACT['saved_previous_run'])])
    require(saved['core']=={k:v for k,v in CONTRACT['partial_map'].items() if k not in ('roots','roots_are')},'actual saved map proof differs')
    save('actual-saved-analysis-summary.json',dict(core_equal=True,changed_files=len(saved['core']['file_differences']),known2=saved['core']['known_absent_creates'],raw_prefix=len(saved['core']['raw_prefix']),source_proof_only=True,no_actualpool=True))
    parent=D/'partial';parent.mkdir()
    f=partial_fixture(c,parent,'P01');before=pin(f['roots']['pool']/'state.json')
    result=call('P01.restore_exact',recovery.restore_exact,[f['roots'],f['evidence'],f['output'],dict(scope=f['label'])])
    require(result['writes']==2 and result['READY_committed'] is False and c.inventory(f['roots']['pool']/'project')==f['evidence']['target'] and pin(f['roots']['pool']/'state.json')==before,'tiny known2 result')
    RESULTS.append(dict(id='P01',status='PASS',synthetic_creates=2,full_recover_positive=False))
    for id,mutation in [('P03','extra'),('P04','thirdmissing'),('P07','changedcurrent'),('P08','missingproof'),('P09.payload','badpayload'),('P09.staged','staged')]:
        f=partial_fixture(c,parent,id);project=f['roots']['pool']/'project'
        if mutation=='extra':(project/'unknown.extra').write_bytes(b'extra')
        elif mutation=='thirdmissing':(project/'neutral.txt').unlink();f['evidence']['failed']=c.inventory(project)
        elif mutation=='changedcurrent':(project/'neutral.txt').write_bytes(b'changed')
        elif mutation=='missingproof':f['evidence']['known_absent_creates']=[]
        elif mutation=='badpayload':f['evidence']['payloads'][0][2].write_bytes(b'bad old-after bytes')
        elif mutation=='staged':(f['roots']['pool']/'data/custom_player.json').write_bytes(b'wrong staged')
        before=dict(project=c.inventory(project),data=c.inventory(f['roots']['pool']/'data'),state=pin(f['roots']['pool']/'state.json'))
        call(id,recovery.restore_exact,[f['roots'],f['evidence'],f['output'],dict(scope=f['label'])],False)
        after=dict(project=c.inventory(project),data=c.inventory(f['roots']['pool']/'data'),state=pin(f['roots']['pool']/'state.json'))
        require(before==after,'negative mutation changed target/state '+id);save('partial/'+id+'-guard.json',dict(before=before,after=after))
    for id in ('P03','P04','P07','P08','P09'):RESULTS.append(dict(id=id,status='PASS',scope='isolated actual restore_exact mutation guards; reset/full-source verification not claimed'))
    f=partial_fixture(c,parent,'P11');cfg=f['roots']['source_root']/'deny.json';cfg.write_text(json.dumps(dict(schema='phase380-root-pool-recovery/1',action='commit_ready',root_commit_ready_authorized=False)))
    before=pin(f['roots']['pool']/'state.json');row=dict(path='deny.json',**pin(cfg))
    call('P11.public-recover-unauthorized',recovery.recover,[f['roots']['source_root'],row,f['roots']['pool'],f['roots']['baseline'],f['roots']['failed_run'],f['roots']['previous_run'],'commit_ready'],False)
    require(pin(f['roots']['pool']/'state.json')==before,'unauthorized READY changed tiny state');RESULTS.append(dict(id='P11',status='PASS',scope='real public recover Root negative; no accepted ROOT/recover positive'))
    for id,why in [('P02','completed-map entrypoint requires genuine Root/source acceptance, not synthesized'),('P05','fake-journal negative requires a valid full saved prefix; actual saved positive and explicit SOURCE predicate only'),('P06','reset/target tamper negative not accepted via synthetic mutation DTO; actual saved equality checked'),('P10','raw75 tamper negative not constructed by copying large preserved trees; actual saved75 proof and SOURCE predicates checked')]:
        RESULTS.append(dict(id=id,status='SOURCE_AND_ACTUAL_SAVED_POSITIVE_NEGATIVE_NOT_EXECUTED',reason=why))

def main():
    global CONTRACT,READ_FILES,READ_ROOTS
    D.mkdir(exist_ok=False)
    owner=read(SD/'source-owner.json')
    for row in owner['files']:require(pin(R/row['path'])=={k:row[k] for k in ('size','sha256')},'frozen independent source drift')
    CONTRACT=read(SD/'execution-contract.json');freeze=read(SD/'freeze380.json')
    READ_FILES={(R/row['path']).absolute() for row in freeze['files']}
    READ_FILES.add(R/'data/phase375-food-hook-source/combined-source-freeze.json')
    failed=Path(CONTRACT['saved_failed_run']);previous=Path(CONTRACT['saved_previous_run'])
    READ_ROOTS=[failed/'output/failed-pool-preservation',failed/'output/previous-source-preimages',failed/'output/source-preimages',previous/'output/compaction',previous/'output/driver']
    READ_FILES.update([failed/'output/readonly-plan.json',failed/'output/prior-observer-reset.json'])
    failure=None
    try:
        sys.addaudithook(audit)
        c=load('native_run_compaction','compaction.py');load('phase363_oracle_storage','old_storage.py');load('phase363_oracle_process','process.py');storage=load('phase380_oracle_storage','storage.py');host=load('phase380_oracle_host','host.py');partial=load('phase380_partial_map','partial.py');recovery=load('phase380_pool_recovery','recovery.py');helper=load('phase380_independent_control_draft','draft.py')
        resolver_cases(host,storage,freeze);installer_cases(storage,helper);partial_cases(partial,recovery,c,helper,freeze)
    except BaseException as exc:
        failure=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc());save('first-failure.json',failure)
    report=dict(status='PASS_BOUNDED_COMPONENT_SCOPE' if failure is None else 'FAIL_FIRST_STOP',results=RESULTS,calls=CALLS,imports=MODULES,failure=failure,audit=AUDIT,
        full_host_or_recover_positive=False,actual12positive=False,actualpool_reads=0,actualpool_writes=0,models=0,Godot=0,original_Game=0,projection=0,
        scope='real Source resolver/public installer + actual saved analysis + synthetic mutation DTO component; no forged Root/production evidence')
    save('report.json',report)
    files=[p for p in D.rglob('*') if p.is_file()]
    save('owned-files.json',dict(files=[dict(path=p.relative_to(R).as_posix(),**pin(p)) for p in sorted(files)],no_more_writes=True))
    for row in read(D/'owned-files.json')['files']:require(pin(R/row['path'])=={k:row[k] for k in ('size','sha256')},'output readback')
    print(json.dumps(dict(status=report['status'],definitions=len(RESULTS),calls=len(CALLS),imports=len(MODULES),failure=failure)))
    if failure:raise SystemExit(1)
if __name__=='__main__':main()
