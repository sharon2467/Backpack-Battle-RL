"""Four minimal checks of the already-read-back package; no battle execution."""
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
CLONE=Path('/workspace/backpack-github-source-clone-20261025')
PUBLIC=CLONE/'python_engine'
PACKAGE=PUBLIC/'experimental_source_king'
OUT=ROOT/'data/phase455-independent-remote-startup-first-001'
HEAD='dbe4a71f64fa0eba5ccd391490c5f1575444bc5b'
INNER='8855e67f4179c9bfca9c12034945eaa898c379176496390abe9f8b12d5f0db46'
OUTER='6160c40cf51419c6fd85d6614308fb679357ddcb4bca47023b690a8f257de6aa'
VERIFIER='591bc2101bc162e8f8269965cb258e354ee0f1ddad1db77b356301c16d36dc62'


def require(value,message):
    if not value:raise AssertionError(message)


def pin(path,expected=None):
    raw=path.read_bytes();record=dict(path=str(path),size=len(raw),sha256=hashlib.sha256(raw).hexdigest())
    if expected is not None:require(record['sha256']==expected,'SHA drift: '+str(path))
    return raw,record


def save(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def negative_probe():
    output=OUT/'forbidden-battle-result.json'
    require(not output.exists(),'negative output preexists')
    sys.dont_write_bytecode=True
    sys.pycache_prefix=str(OUT/'unused-bytecode-cache')
    sys.path.insert(0,str(PACKAGE))
    sys.argv=[str(PACKAGE/'headless.py'),'--layout',str(PACKAGE/'examples/layout-A.json'),'--seed','-1','--output',str(output)]
    targets={str(PACKAGE/'headless.py'):{'initialize':'initialize','CombatRandom.__init__':'CombatRandom.__init__','HeadlessBattle.run':'Battle.run'},str(PACKAGE/'godot_pcg_integer.py'):{'GodotPCGInteger.__init__':'GodotPCGInteger.__init__'},str(PACKAGE/'native_replay_v8/engine.py'):{'CombatEngine.__init__':'Engine.__init__','CombatEngine.prepare_only':'prepare','CombatEngine.activate_from_checkpoint':'activate','CombatEngine.run':'Engine.run','CombatEngine.step':'Engine.step'}}
    counts={name:0 for names in targets.values() for name in names.values()}
    def profile(frame,event,arg):
        if event=='call':
            table=targets.get(frame.f_code.co_filename)
            if table:
                name=table.get(frame.f_code.co_qualname)
                if name:counts[name]+=1
    error=None;sys.setprofile(profile)
    try:runpy.run_path(str(PACKAGE/'headless.py'),run_name='__main__')
    except ValueError as exc:error=str(exc)
    finally:sys.setprofile(None)
    require(error=='uint64 headless seed required','expected original invalidseed error')
    require(counts['initialize']==1 and all(value==0 for name,value in counts.items() if name!='initialize'),'invalidseed touched RNG/model')
    require(not output.exists(),'invalidseed wrote result')
    modules={}
    for name,module in list(sys.modules.items()):
        if name in ('original_rng','godot_pcg_integer') or name.startswith(('native_replay_v7','native_replay_v8')):
            path=Path(module.__file__).resolve();require(path.is_relative_to(PACKAGE),'wrong module source: '+name);modules[name]=str(path)
    report=dict(status='PASS_ORIGINAL_CLI_REJECTION_ZERO_RNG_MODEL',error=error,counts=counts,loaded_modules=modules,output_created=False,argv=sys.argv)
    save(OUT/'negative-probe.json',report)
    print(json.dumps(report))


def main():
    require(not OUT.exists(),'unique output already exists');OUT.mkdir()
    began=time.monotonic();report=dict(status='STARTED',checks=[],before=[],after=[],battle_calls=0,Expected_reads=0,new_native=0)
    failure=None
    def command(label,args,cwd):
        started=time.monotonic()
        with (OUT/(label+'.stdout')).open('wb') as stdout,(OUT/(label+'.stderr')).open('wb') as stderr:
            result=subprocess.run(args,cwd=cwd,stdout=stdout,stderr=stderr,timeout=15)
        row=dict(label=label,args=args,cwd=str(cwd),exit_code=result.returncode,seconds=time.monotonic()-started)
        report['checks'].append(row)
        require(result.returncode==0,'startup check failed: '+label)
        return (OUT/(label+'.stdout')).read_text()
    try:
        head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=CLONE,text=True).strip();require(head==HEAD,'wrong remotecommit');report['remote_head']=head
        for path,expected in [(PUBLIC/'tools/verify_manifest.py',VERIFIER),(PUBLIC/'MANIFEST.json',OUTER),(PACKAGE/'manifest.json',INNER)]:
            _,record=pin(path,expected);report['before'].append(record)
        manifest=json.loads((PUBLIC/'MANIFEST.json').read_text())['files']
        runtime=json.loads((PUBLIC/'evidence/runtime-sources.json').read_text())['files']
        require(len(manifest)==66 and len(runtime)==30 and all(manifest[k]==v for k,v in runtime.items()),'outer30legacy membership')
        require(manifest['experimental_source_king/manifest.json']['sha256']==INNER,'nestedmanifest not covered')
        text=command('outer-verifier',[sys.executable,'-B',str(PUBLIC/'tools/verify_manifest.py')],OUT)
        require('66 publication files; 30 exact historical runtime files' in text,'outer report')
        text=command('inner-verifier',[sys.executable,'-B',str(PACKAGE/'verify_manifest.py'),'--manifest-sha256',INNER],OUT)
        value=json.loads(text);require(value['files']==21 and value['source_files']==15 and value['manifest_sha256']==INNER and value['battle_calls']==0,'inner report')
        text=command('CLI-help',[sys.executable,'-B',str(PACKAGE/'headless.py'),'--help'],OUT)
        require(all(x in text for x in ('--layout','--seed','--batch','--keep-results')),'documented CLI options')
        text=command('CLI-invalid-seed',[sys.executable,'-I','-B',str(Path(__file__).resolve()),'--negative-probe'],OUT)
        report['negative_probe']=json.loads(text)
        _,record=pin(PUBLIC/'MANIFEST.json',OUTER);report['after'].append(record)
        for name,identity in manifest.items():
            _,record=pin(PUBLIC/name,identity['sha256']);require(record['size']==identity['size'],'poststartup size drift');report['after'].append(record)
        report['status']='PASS_REMOTE_DISTRIBUTION_STARTUP_NO_BATTLE'
    except BaseException as exc:
        failure=exc;report['status']='FAIL_FIRST_STOPPED_NO_RETRY';report['failure']=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
    finally:
        report['elapsed_seconds']=time.monotonic()-began
        save(OUT/'result.json',report)
        rows=[]
        for path in sorted(OUT.iterdir()):
            if path.is_file():_,record=pin(path);rows.append(record)
        save(OUT/'owned-files.json',dict(schema='phase455-independent-remote-startup-owner/1',payloads=rows))
    print(json.dumps(dict(status=report['status'],checks=len(report['checks']),elapsed_seconds=report['elapsed_seconds'],output=str(OUT))))
    if failure is not None:raise SystemExit(1)


if __name__=='__main__':
    if sys.argv[1:]==['--negative-probe']:negative_probe()
    else:main()
