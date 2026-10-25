"""Exactly one empty-project Godot language oracle, never an original Game attempt."""
import hashlib
import json
import os
from pathlib import Path
import sys
import types

R=Path(__file__).resolve().parents[1];D=R/'data/phase364-independent-startup-diagnosis'
def pin(p):
 b=p.read_bytes();return dict(size=len(b),sha256=hashlib.sha256(b).hexdigest())
def save(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def module(name,p):
 m=types.ModuleType(name);m.__file__=str(p);sys.modules[name]=m;exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m

def main():
 contract=json.loads((D/'execution-contract.json').read_text())
 for row in contract['files']:
  p=R/row['path'];assert pin(p)=={k:row[k] for k in ('size','sha256')}
 runtime=json.loads((D/'source-provenance.json').read_text())['runtime_pins']
 for row in runtime:assert pin(Path(row['path']))=={k:row[k] for k in ('size','sha256')}
 project=D/'empty-project';run=D/'language-run';assert not (project/'language-report.json').exists()
 assert not (run/'output').exists();(run/'output').mkdir()
 for name in ('data','config','cache','run','tmp'):(run/'user'/name).mkdir(parents=True,mode=0o700)
 task=Path('/workspace/godotsteam-startup-20261013')
 module('native_run_compaction',D/'SOURCE/compaction.py');module('phase363_oracle_storage',D/'SOURCE/storage.py');monitor=module('__language_probe_generic_monitor__',D/'SOURCE/process.py')
 # The monitor imports phase363_oracle_storage definitions only. No oracle wrapper.
 command=[sys.executable,str(R/'tests/godotsteam_offline_exec.py'),str(task/'debian/usr/bin/xvfb-run'),'-a','-s','-screen 0 640x480x24 -nolisten tcp','-e',str(run/'output/xvfb.log'),str(task/'engine/godotsteam.362.editor.x86_64'),'--path',str(project),'--audio-driver','Dummy','--time-scale','1.0','--script','res://probe.gd']
 before={p.name:pin(p) for p in project.iterdir() if p.is_file()};save(run/'before-launch.json',dict(command=command,project=before,language_probe=1,actual_Game=0,native_battle=0,models=0,autoload_contract='Noautoload/main_scene configured; actual report checks both.'))
 def scan():
  paths=list(run.rglob('*'))
  if any(p.is_symlink() for p in paths):raise ValueError('language probe linked user file')
  total=sum(p.stat().st_size for p in paths if p.is_file())
  if total>16*1024**2 or len(paths)>512:raise ValueError('tiny language probe output cap')
  return dict(bytes=total,entries=len(paths))
 result=monitor.monitor_command(command,run,monitor.environment(task,run),run/'output','language',18.,scan_callback=scan,poll_seconds=.05,term_grace_seconds=.2,kill_grace_seconds=.5,log_limit_bytes=2*1024**2)
 # Generic actual_oracle_processes=0 is its API category, not a total count of Godot tools.
 receipt=dict(schema='phase364-one-language-probe-receipt/1',Godot_language_probes=1,actual_Godot_engine_programs=1,actual_Game_processes=0,native_battles=0,Python_CombatEngine_instances=0,models=0,projection_calls=0,oracle_wrapper_calls=0,generic_monitor_calls=1,SOURCE_module_imports=3,explicit_probe_RNG_calls=0,Godot_internal_RNG_calls='NOT_INSTRUMENTED',monitor=result,first_exit=result['exit_code'],before=before,after_sources={name:pin(project/name) for name in before},report_exists=(project/'language-report.json').is_file(),automatic_retry=False)
 assert receipt['after_sources']==before
 save(run/'language-execution-receipt.json',receipt)
 payloads=[run/'before-launch.json',run/'language-execution-receipt.json',run/'output/language-monitor-result.json',run/'output/language-stdout.log',run/'output/language-stderr.log']
 if (project/'language-report.json').exists():payloads.append(project/'language-report.json')
 save(run/'language-joint-seal.json',dict(schema='phase364-language-output-jointseal/1',files=[dict(path=str(p.relative_to(R)),**pin(p)) for p in payloads],Godot_language_probes=1,actual_Game_processes=0,native_battles=0,models=0))
 print(json.dumps(dict(exit_code=result['exit_code'],clean=result['process_clean_exit'],report_exists=receipt['report_exists'],Godot_language_probes=1,actual_Game=0,native_battle=0)))
if __name__=='__main__':main()
