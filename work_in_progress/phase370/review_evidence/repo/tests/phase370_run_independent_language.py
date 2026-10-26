"""One empty-project370 language gate; raw results jointsealed before interpretation."""
from pathlib import Path
import hashlib,json,sys,types

R=Path(__file__).resolve().parents[1];D=R/'data/phase370-independent-execution'
def pin(p):
 b=p.read_bytes();return dict(size=len(b),sha256=hashlib.sha256(b).hexdigest())
def desc(p):return dict(path=str(p.relative_to(R)),**pin(p))
def save(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def load(name,p):
 m=types.ModuleType(name);m.__file__=str(p);sys.modules[name]=m;exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m

def main():
 contract=json.loads((D/'execution-contract.json').read_text())
 for row in contract['files']:assert pin(R/row['path'])=={k:row[k] for k in ('size','sha256')}
 for row in contract['runtime_pins']:assert pin(Path(row['path']))=={k:row[k] for k in ('size','sha256')}
 run=D/'language-first-001';run.mkdir();(run/'output').mkdir()
 for name in ('data','config','cache','run','tmp'):(run/'user'/name).mkdir(parents=True,mode=0o700)
 project=D/'language-project';assert not (project/'language-report.json').exists()
 before={p.name:pin(p) for p in project.iterdir() if p.is_file()}
 load('native_run_compaction',D/'SOURCE/compaction.py');load('phase363_oracle_storage',D/'SOURCE/storage.py')
 monitor=load('__independent370_language_monitor__',D/'SOURCE/process.py')
 task=Path('/workspace/godotsteam-startup-20261013')
 command=[sys.executable,str(R/'tests/godotsteam_offline_exec.py'),str(task/'debian/usr/bin/xvfb-run'),'-a','-s','-screen 0 640x480x24 -nolisten tcp','-e',str(run/'output/xvfb.log'),str(task/'engine/godotsteam.362.editor.x86_64'),'--path',str(project),'--audio-driver','Dummy','--time-scale','1.0','--script','res://probe.gd']
 save(run/'before-launch.json',dict(command=command,project_sources=before,scope='ONE_EMPTY_PROJECT_LANGUAGE_GATE_NOT_GAME'))
 def scan():
  paths=list(run.rglob('*'));assert not any(p.is_symlink() for p in paths)
  size=sum(p.stat().st_size for p in paths if p.is_file());assert size<24*1024**2 and len(paths)<1024
  return dict(bytes=size,entries=len(paths))
 actual=monitor.monitor_command(command,run,monitor.environment(task,run),run/'output','language',18.,scan_callback=scan,poll_seconds=.05,term_grace_seconds=.2,kill_grace_seconds=.5,log_limit_bytes=2*1024**2)
 receipt=dict(schema='phase370-independent-one-language-execution/1',monitor=actual,actual_Godot_language_processes=1,
  actual_Game_processes=0,native_battles=0,Python_CombatEngine_instances=0,models=0,projection=0,actual_pool_operations=0,
  oracle_wrapper_calls=0,generic_monitor_calls=1,SOURCE_definition_imports=3,complete_production_script_instances=0,
  complete_production_lifecycle_calls=0,explicit_probe_RNG_calls=0,Godot_internal_RNG='NOT_INSTRUMENTED',
  first_exit=actual['exit_code'],automatic_retry=False,Python_command='-I -B -S',
  boundary='Explicit empty project + isolated XDG/user paths. No autoload/Game source or model. Not a kernel closed filesystem; trusted offline engine/Xvfb/bootstrap sources pinned.',
  source_unchanged={name:pin(project/name) for name in before}==before)
 save(run/'execution-receipt.json',receipt)
 report_path=project/'language-report.json'
 leaves=[p for p in run.rglob('*') if p.is_file()]
 if report_path.is_file():leaves.append(report_path)
 save(run/'raw-joint-seal.json',dict(schema='phase370-language-raw-joint-seal/1',files=[desc(p) for p in sorted(leaves)]))
 # All interpretation is after raw jointseal; a failed run is never retried here.
 report=json.loads(report_path.read_text()) if report_path.exists() else None
 passed=actual['exit_code']==0 and actual['abort_reason'] is None and not actual['timed_out'] and report is not None and report.get('completed') is True and report.get('failure') is None and receipt['source_unchanged']
 interpreted=dict(schema='phase370-independent-language-interpretation/1',status='PASS' if passed else 'FAIL_FIRST_LANGUAGE_GATE',
  execution=desc(run/'execution-receipt.json'),raw_jointseal=desc(run/'raw-joint-seal.json'),
  report=None if report is None else desc(report_path),actual_resource_attempts=0 if report is None else len(report['resource_loads']),
  actual_control_cases=0 if report is None else len(report['cases']),first_failure='REPORT_NOT_WRITTEN_OR_PROBE_PARSE' if report is None else report.get('failure'),
  future_host_tinyFS_savedmap='NOT_EXECUTED_IN_THIS_LANGUAGE_STAGE',full_actual12_positive=False,production_fullsnapshot_positive=False)
 save(run/'interpretation.json',interpreted)
 save(run/'owned-files.json',dict(schema='phase370-independent-language-output-owner/1',files=[desc(p) for p in sorted([p for p in run.rglob('*') if p.is_file()]+([report_path] if report_path.exists() else []))]))
 for row in json.loads((run/'owned-files.json').read_text())['files']:assert pin(R/row['path'])=={k:row[k] for k in ('size','sha256')}
 print(json.dumps(dict(status=interpreted['status'],exit=actual['exit_code'],interpretation=desc(run/'interpretation.json'),owner=desc(run/'owned-files.json'),resource_attempts=interpreted['actual_resource_attempts'],controls=interpreted['actual_control_cases'],failure=interpreted['first_failure'])))
 return 0 if passed else 1

if __name__=='__main__':raise SystemExit(main())
