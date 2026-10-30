"""One trusted package verifier and one two-job mixed Source batch; no replay."""
import copy
import functools
import hashlib
import importlib
import json
from pathlib import Path
import resource
import signal
import struct
import subprocess
import sys
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'data/phase487-independent-remote-harness-source'
OUT=ROOT/'data/phase487-independent-remote-batch-first-001'
PACKAGE=Path('/workspace/backpack-github-source-clone-20261025/python_engine/experimental_source_king')
MANIFEST_SHA='aa9d88147e1cd5334406afb6d007786987d03895b99fbdf6759eb5817cc5e297'
COUNTS={};BATTLES=[];STAGE='preflight';METRICS={}

def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode())
def pin(p):
    b=p.read_bytes()
    try:path=str(p.relative_to(ROOT))
    except ValueError:path=str(p)
    return dict(path=path,size=len(b),sha256=sha(b))
def save(name,v):
    p=OUT/name;p.write_text(json.dumps(v,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n');return pin(p)
def strict(a,b,where='$'):
    assert type(a)is type(b),(where,type(a).__name__,type(b).__name__)
    if isinstance(a,float):assert struct.pack('>d',a)==struct.pack('>d',b),(where,a,b)
    elif isinstance(a,dict):
        assert {(type(k),k)for k in a}=={(type(k),k)for k in b},(where,'keys')
        for k in a:strict(a[k],b[k],where+'.'+str(k))
    elif isinstance(a,(list,tuple)):
        assert len(a)==len(b),(where,len(a),len(b))
        for i,(x,y)in enumerate(zip(a,b)):strict(x,y,where+'['+str(i)+']')
    else:assert a==b,(where,a,b)
def verify_owner(path):
    x=json.loads(path.read_bytes())
    for row in x['files']:strict(pin(ROOT/row['path']),row,'owner')
    return x

def package_pins():
    manifest=PACKAGE/'manifest.json';strict(sha(manifest.read_bytes()),MANIFEST_SHA,'trusted_manifest')
    m=json.loads(manifest.read_bytes());rows=[]
    strict(len(m['files']),24);strict(m['source_file_count'],15)
    for row in m['files']:
        p=PACKAGE/row['path'];assert p.is_file() and not p.is_symlink() and p.stat().st_nlink==1
        actual=pin(p);strict((actual['size'],actual['sha256']),(row['size'],row['sha256']),row['path']);rows.append(actual)
    actual={str(p.relative_to(PACKAGE))for p in PACKAGE.rglob('*')if p.is_file()}
    strict(actual,{r['path']for r in m['files']}|{'manifest.json'},'physical_files')
    rows.append(pin(manifest));return rows

def memory():
    usage=resource.getrusage(resource.RUSAGE_SELF)
    value=dict(ru_maxrss_KiB=usage.ru_maxrss,minor_page_faults=usage.ru_minflt,major_page_faults=usage.ru_majflt)
    try:
        lines=Path('/proc/self/status').read_text().splitlines()
        value['current_RSS_KiB']=int(next(x for x in lines if x.startswith('VmRSS:')).split()[1])
    except (OSError,StopIteration,ValueError)as e:value['current_RSS_unavailable']=type(e).__name__
    return value

def counted(obj,name,label,capture=False):
    original=getattr(obj,name)
    @functools.wraps(original)
    def call(*a,**kw):
        COUNTS[label]=COUNTS.get(label,0)+1
        answer=original(*a,**kw)
        if capture:BATTLES.append(answer)
        return answer
    setattr(obj,name,call)

def main():
    global STAGE,METRICS
    start=time.perf_counter();OUT.mkdir(exist_ok=False);status='FAILED';before=[]
    try:
        verify_owner(SOURCE/'owned-files.json')
        binding=json.loads((SOURCE/'remote-binding.json').read_bytes())
        strict(binding['remote_commit'],'549af3d3c53b6188f637885fee85889ba6b4e9e8')
        strict(pin(Path(binding['Root_remote_receipt']['path'])),binding['Root_remote_receipt'])
        expected=json.loads((ROOT/'data/phase487-independent-batch-plan/expected-job-identities.json').read_bytes())
        strict(pin(ROOT/'data/phase487-independent-batch-plan/expected-job-identities.json'),binding['expected_jobs'])
        before=package_pins();save('source-input-before.json',before)
        jobpath=PACKAGE/'examples/jobs-RL-smoke.json';jobs=json.loads(jobpath.read_bytes());preserved=copy.deepcopy(jobs)
        strict(canonical(jobs),expected['ordered_batch_canonical_sha256']);strict(len(jobs),2)
        for i,(job,x)in enumerate(zip(jobs,expected['jobs'])):
            strict(job['seed'],x['seed']);strict(canonical(job),x['job_canonical_sha256'])
        STAGE='trusted_readonly_verifier'
        cmd=[sys.executable,'-B',str(PACKAGE/'verify_manifest.py'),'--manifest-sha256',MANIFEST_SHA]
        save('verifier-invocation.json',dict(argv=cmd,cwd=str(PACKAGE),wall_timeout_seconds=15))
        t=time.perf_counter();q=subprocess.run(cmd,cwd=PACKAGE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=15,check=False)
        (OUT/'verifier-stdout.txt').write_bytes(q.stdout);(OUT/'verifier-stderr.txt').write_bytes(q.stderr)
        save('verifier-execution.json',dict(returncode=q.returncode,wall_seconds=time.perf_counter()-t))
        strict(q.returncode,0,'verifier_exit')
        STAGE='import_exact_remote_source'
        sys.dont_write_bytecode=True;sys.pycache_prefix=str(OUT/'unused-bytecode-cache');sys.path.insert(0,str(PACKAGE))
        h=importlib.import_module('headless');e=importlib.import_module('native_replay_v8.engine')
        freeze=json.loads((ROOT/'data/phase482-source-king-mirror-poison-v2/candidate-source-freeze.json').read_bytes())
        allowed={str((PACKAGE/x['relative']).resolve()):x['sha256']for x in freeze['files']}
        loaded=[]
        for name,module in list(sys.modules.items()):
            if name in ('headless','original_rng','godot_pcg_integer')or name.startswith(('native_replay_v7','native_replay_v8')):
                p=Path(module.__file__).resolve();assert str(p)in allowed,(name,str(p));strict(sha(p.read_bytes()),allowed[str(p)])
                loaded.append(dict(module=name,path=str(p),sha256=allowed[str(p)]))
        save('actual-imports.json',loaded)
        counted(h,'initialize','initialize',capture=True)
        for obj,name,label in [(h,'run_batch','run_batch'),(h,'derive_stream_seeds','derive_stream_seeds'),
            (h.CombatRandom,'__init__','CombatRandom.__init__'),(h.GodotPCGInteger,'__init__','GodotPCGInteger.__init__'),
            (h.HeadlessBattle,'run','Battle.run'),(e.CombatEngine,'__init__','Engine.__init__'),
            (e.CombatEngine,'prepare_only','Engine.prepare_only'),(e.CombatEngine,'activate_from_checkpoint','Engine.activate_from_checkpoint'),
            (e.CombatEngine,'run','Engine.run'),(e.CombatEngine,'result','Engine.result')]:counted(obj,name,label)
        STAGE='one_mixed_batch'
        m0=memory();cpu=time.process_time();wall=time.perf_counter();signal.alarm(20)
        try:batch=h.run_batch(jobs,max_seconds=120.0,keep_results=True)
        finally:
            signal.alarm(0);METRICS=dict(batch_wall_seconds=time.perf_counter()-wall,batch_cpu_seconds=time.process_time()-cpu,
                before_memory=m0,after_memory=memory(),wall_limit_seconds=20,simulation_ceiling_per_job_seconds=120)
        output=save('batch-output.json',batch)
        STAGE='readonly_same_instance_acceptance'
        strict(jobs,preserved,'input_object_unchanged');strict(len(batch['jobs']),2);strict(batch['formal_support'],75)
        strict(batch['seed_policy'],'headless-sha256-domains/1');strict(len(BATTLES),2)
        assert BATTLES[0]is not BATTLES[1]and BATTLES[0]._engine is not BATTLES[1]._engine
        assert BATTLES[0]._engine.random is not BATTLES[1]._engine.random
        assert BATTLES[0]._engine.items is not BATTLES[1]._engine.items
        summaries=[]
        for i,(record,battle,request,x)in enumerate(zip(batch['jobs'],BATTLES,jobs,expected['jobs'])):
            strict(record['index'],i);strict(record['seed'],x['seed']);strict(record['status'],'COMPLETED')
            assert 'result'in record
            value=record['result'];engine=battle._engine
            strict(battle.done,True);strict(engine.frame_driver.finalized,True);strict(engine.finalized,True)
            strict(value['initialization']['root_seed'],request['seed']);strict(value['initialization']['profile'],x['profile'])
            strict(engine.runtime_inputs.data['profile_id'],x['profile']);strict(type(engine.random),h.CombatRandom)
            strict(value['fixture'],engine.fixture);strict(value['events'],engine.events)
            strict(value['random_inputs'],engine.random.audit);strict(value['source_rng'],engine.random.snapshot())
            strict(value['source_rng']['seed_policy'],'headless-sha256-domains/1')
            strict(value['source_rng']['native_seed_parity'],'PENDING_CUSTOM_BINARY_NUMERIC_AND_SESSION_CONSUMPTION')
            strict(record['summary']['winner'],engine.winner);strict(value['final']['winner'],engine.winner)
            strict(record['summary']['terminal_time'],value['final']['timestamp']);assert set(value['source_terminal'])=={'post_cleanup','final','passes'}
            strict(len(engine.runtime_inputs.data['timer_initial']),33)
            summaries.append(dict(index=i,seed=request['seed'],profile=x['profile'],winner=engine.winner,
                events=len(engine.events),draws=len(engine.random.audit),simulated_terminal_time=value['final']['timestamp'],
                physics_frame=engine.frame_driver.physics_frame,idle_frame=engine.frame_driver.idle_frame,
                passes=len(value['source_terminal']['passes']),source_rng=value['source_rng'],terminal_complete=True,provider='actual headless.CombatRandom'))
        for label in ('initialize','CombatRandom.__init__','Battle.run','Engine.__init__','Engine.prepare_only','Engine.run','Engine.result'):strict(COUNTS[label],2,label)
        strict(COUNTS['run_batch'],1);strict(COUNTS['Engine.activate_from_checkpoint'],4)
        METRICS.update(completed_jobs=2,jobs_per_batch_wall_second=2/METRICS['batch_wall_seconds'],
            measurement_scope='Same interpreter, imports excluded from timed batch; counters and two retained instances/full results included. No tracing profiler.',
            RSS_scope='Linux RUSAGE_SELF high-water KiB includes interpreter/imports/current batch and retained results. Before/after peak difference is not per-job memory.',
            sample_limit='Two fixed mixed-profile jobs; no repeated benchmark, cross-process determinism, native calibration or complete RL environment claim.')
        save('accepted-job-summaries.json',summaries);save('metrics.json',METRICS)
        save('batch-identity.json',dict(output=output,input=pin(jobpath),input_canonical_sha256=canonical(jobs),same_instance_ownership=True))
        status='PASS_REMOTE_PACKAGE_AND_ONE_MIXED_TWO_JOB_SOURCE_BATCH_LIMITED_SMOKE'
    except BaseException as exc:
        save('first-error.json',dict(stage=STAGE,type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc(),calls=COUNTS))
        save('metrics.json',METRICS)
        for i,battle in enumerate(BATTLES):
            try:save('partial-instance-'+str(i)+'.json',dict(events=battle._engine.events,random_inputs=battle._engine.random.audit,
                source_rng=battle._engine.random.snapshot(),elapsed=battle._engine.elapsed,ended=battle._engine.ended,finalized=battle.done))
            except BaseException as diagnostic:save('partial-diagnostic-'+str(i)+'.json',dict(type=type(diagnostic).__name__,message=str(diagnostic)))
    finally:
        signal.alarm(0)
        after=package_pins();strict(after,before,'package_and_input_after')
        save('source-input-after.json',after)
        result=dict(status=status,stage=STAGE,wall_total_seconds=time.perf_counter()-start,calls=COUNTS,
            retained_actual_instances=len(BATTLES),package_files_unchanged=len(after),native=0,Expected_reads=0,old_tests=0,
            standalone_battle_runs=0,batch_invocations=COUNTS.get('run_batch',0),auto_retry=False)
        save('result.json',result);save('owned-files.json',dict(schema='phase487-actual-owner/1',files=[pin(p)for p in sorted(OUT.iterdir())if p.is_file()],no_more_writes=True))
    print(json.dumps(result));return 0 if status.startswith('PASS')else 1

if __name__=='__main__':
    def timeout(signum,frame):raise TimeoutError('phase487 mixed batch20-second wall deadline')
    signal.signal(signal.SIGALRM,timeout)
    sys.exit(main())
