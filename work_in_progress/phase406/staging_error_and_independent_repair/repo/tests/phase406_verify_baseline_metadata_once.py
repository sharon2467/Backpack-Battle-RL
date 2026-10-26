"""One authorized398 FS inventory; no recovery or business operations."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import time
import traceback

ROOT=Path('/workspace/python-original-engine/repo')
OUT=ROOT/'data/phase406-independent-baseline-metadata-repair-check'

def pin(path):
    for p in [path,*path.parents]:assert not p.is_symlink(),str(p)
    a=path.lstat();assert stat.S_ISREG(a.st_mode) and a.st_nlink==1
    raw=path.read_bytes();b=path.lstat()
    for k in ('st_dev','st_ino','st_mode','st_nlink','st_size','st_mtime_ns','st_ctime_ns'):assert getattr(a,k)==getattr(b,k)
    return dict(size=len(raw),sha256=hashlib.sha256(raw).hexdigest())

def save(name,value):(OUT/name).open('x').write(json.dumps(value,sort_keys=True,indent=2)+'\n')

def main():
    start=time.monotonic();bindings=json.loads((OUT/'bindings.json').read_bytes());prepared=json.loads((OUT/'preparation-owner.json').read_bytes())
    for row in prepared['files']:
        p=ROOT/row['path'];assert pin(p)=={k:row[k] for k in ('size','sha256')}
    for name,row in bindings['absolute_input_pins'].items():assert pin(Path(name))==row,name
    release=json.loads(Path(bindings['release']).read_bytes());baseline=Path(release['baseline']);modulepath=ROOT/release['reader_source']['path']
    expected=json.loads(Path(release['authoritative_manifest']).read_bytes());outer=json.loads(Path(release['verified_Git_outer_manifest']).read_bytes())
    before=json.loads((ROOT/release['before']['path']).read_bytes());repair=json.loads((ROOT/release['repair']['path']).read_bytes())
    assert outer['files']['run/output/compaction/baseline-files.json']==dict(size=release['manifest_size'],sha256=release['manifest_sha256'])
    assert len(before['affected_files'])==len(repair['files'])==13
    allowed=set(bindings['absolute_input_pins'])|{str(ROOT/r['path']) for r in prepared['files']}|{str(OUT/'preparation-owner.json')}
    reads=[];violations=[];calls={};top_calls=0;actual=None;status='FAIL';error=None
    sys.dont_write_bytecode=True;sys.pycache_prefix='/tmp/phase406-baseline-check-unused-cache'
    assert not Path(sys.pycache_prefix).exists()
    def audit(event,args):
        if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)):
            p=Path(os.path.abspath(os.fsdecode(args[0])));mode=args[1];flags=args[2]
            write=(isinstance(mode,str) and any(c in mode for c in 'wax+'))or(isinstance(flags,int)and bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)))
            permitted=p.parent==OUT if write else p.is_relative_to(baseline) or str(p) in allowed or p.parent==OUT or p.is_relative_to(sys.base_prefix) or str(p).startswith(sys.pycache_prefix+'/')
            if not permitted:violations.append(dict(event=event,path=str(p),write=write));raise PermissionError('outside exact readonly verification scope')
            if not write and (p.is_relative_to(baseline)or str(p) in allowed):reads.append(str(p))
        if event in ('subprocess.Popen','os.system','os.posix_spawn','socket.connect','socket.bind','os.remove','os.rename','os.rmdir','os.link','os.symlink','os.chmod','os.utime','os.truncate','os.mkdir'):
            violations.append(dict(event=event));raise PermissionError('readonly metadata check')
    def profile(frame,event,arg):
        if event=='call' and frame.f_code.co_filename==str(modulepath):
            name=frame.f_code.co_name;calls[name]=calls.get(name,0)+1
    sys.addaudithook(audit)
    try:
        assert pin(modulepath)=={k:release['reader_source'][k] for k in ('size','sha256')}
        spec=importlib.util.spec_from_file_location('_independent406_baseline398_fschecker',modulepath)
        module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
        assert module.inventory.__code__.co_firstlineno==bindings['inventory_definition']['line']
        sys.setprofile(profile);top_calls=1
        actual=module.inventory(baseline,exclude=(),relaxed=False)
        sys.setprofile(None)
        save('actual-baseline-inventory.json',actual)
        expected_rows={x['path']:x for x in expected['entries']};actual_rows={x['path']:x for x in actual['entries']}
        assert len(expected_rows)==len(expected['entries']) and len(actual_rows)==len(actual['entries'])
        differences=[]
        for name in sorted(set(expected_rows)|set(actual_rows)):
            if expected_rows.get(name)!=actual_rows.get(name):differences.append(dict(path=name,expected=expected_rows.get(name),actual=actual_rows.get(name)))
        save('manifest-comparison.json',dict(equal=actual==expected,difference_count=len(differences),differences= differences))
        assert actual==expected,'full baseline manifest differs'
        counts=dict(files=sum(x['kind']=='file' for x in actual['entries']),directories=sum(x['kind']=='directory' for x in actual['entries']),bytes=sum(x.get('size',0) for x in actual['entries']))
        assert counts==dict(files=15418,directories=247,bytes=616167851)
        repaired={x['path']:x for x in repair['files']};observations=[]
        for row in before['affected_files']:
            p=Path(row['path']);s=p.lstat();old=row['before_repair'];after=repaired[str(p)];target=row['target'];name=row['relative']
            assert p==baseline/name and expected_rows[name]==target and actual_rows[name]==target
            assert all(old[k]==target[k]for k in ('size','sha256','mode')) and old['mtime_ns']!=target['mtime_ns']
            assert all(after[k]==target[k]for k in ('size','sha256','mode','mtime_ns'))
            assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_dev==old['dev'] and s.st_ino==old['ino']
            assert stat.S_IMODE(s.st_mode)==target['mode'] and s.st_size==target['size'] and s.st_mtime_ns==target['mtime_ns']
            assert s.st_ctime_ns==after['ctime_ns'] and after['inode_unchanged'] is True and after['ctime_not_historical'] is True
            observations.append(dict(path=str(p),relative=name,size=s.st_size,sha256=target['sha256'],mode=stat.S_IMODE(s.st_mode),dev=s.st_dev,ino=s.st_ino,nlink=s.st_nlink,
                mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,atime_ns=s.st_atime_ns,inode_matches_before=True,mtime_matches_historical=True,ctime_matches_postrepair_record=True,historical_ctime_or_atime_claim=False))
        assert sum(x['relative'].endswith('.gd')for x in observations)==11 and sum(x['relative'].endswith('.tscn')for x in observations)==2
        save('thirteen-target-association.json',dict(targets=observations,files=13,GD=11,scenes=2,
            historical_fact='Root faulty staging rewrote the same bytes in13 absolute baseline leaves; this verification does not erase that event.',
            ctime_atime_limit='Only historical mtime is restored/verified. ctime is current/postrepair; atime may change on reads and is not historical.'))
        for name,row in bindings['absolute_input_pins'].items():assert pin(Path(name))==row,name
        assert calls.get('inventory')==1 and not any(calls.get(k,0)for k in ('main','prepare_contract','verify_complete_saved_contract','attempt05_process_controls','verify_capsule385','audit'))
        assert not violations
        status='PASS'
    except BaseException:
        sys.setprofile(None);error=traceback.format_exc();(OUT/'first-error-traceback.txt').open('x').write(error)
    finally:
        sys.setprofile(None)
        save('io-observation.json',dict(read_paths=reads,violations=violations))
        save('execution-result.json',dict(status=status,FSchecker_inventory_top_calls=top_calls,actual_reader_function_counts=calls,elapsed_seconds=time.monotonic()-start,error=error,
            FSchecker_module_imports=1 if '_independent406_baseline398_fschecker'in sys.modules else 0,
            full398_reader_runs=0,operational_restore_calls=0,schema_calls=0,Engine_calls=0,models=0,native=0,actual12_reads=0,pool_writes=0,restore=0,READY=0,automatic_retry=False))
    print(json.dumps(dict(status=status,inventory_calls=top_calls,elapsed_seconds=time.monotonic()-start)))
    return 0 if status=='PASS'else 1

if __name__=='__main__':raise SystemExit(main())
