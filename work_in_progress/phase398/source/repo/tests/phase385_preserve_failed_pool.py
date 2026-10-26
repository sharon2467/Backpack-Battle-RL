from pathlib import Path
import sys,json,hashlib,shutil,fcntl
r=Path('/workspace/python-original-engine/repo');src=r/'tests/native_run_compaction.py';assert hashlib.sha256(src.read_bytes()).hexdigest()=='829475e4ba5ee4a3ce3e3ce7a1d600b53cfa6ab243020a8528b6758675e6c260'
sys.dont_write_bytecode=True;sys.path.insert(0,str(r/'tests'));import native_run_compaction as c
pool=Path('/workspace/native-combat-20261013/pool');base=Path('/workspace/godotsteam-startup-20261013/baseline/Backpack Battles');run=Path('/workspace/native-combat-20261013/runs/original027-king-single-A-20261025-attempt05');d=run/'output/failed-pool-preservation';assert not d.exists()
with (pool/'.lock').open('rb') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);checks={str(x):c.process_check(x) for x in (pool,run,base)};state=(pool/'state.json').read_bytes();assert json.loads(state)['status']=='failed'
 before=c.read(run/'output/pool-before.json');baseline=c.inventory(base);project=c.inventory(pool/'project');staged=c.inventory(pool/'data');assert baseline==before['baseline'] and project==before['project'] and staged==before['staged']
 d.mkdir();c.write(d/'baseline-files.json',baseline);c.write(d/'failed-project-files.json',project);c.write(d/'failed-staged-files.json',staged);(d/'failed-pool-state.json').write_bytes(state);c.write(d/'process-inspection.json',checks)
 plan=c.overlay_plan(baseline,project);c.write(d/'overlay-manifest.json',plan);c.archive_overlay(pool/'project',project,plan,d/'failed-project-overlay.zip')
 (d/'staged-bytes').mkdir()
 for name in c.index(staged):
  if c.index(staged)[name]['kind']=='file':shutil.copy2(pool/'data'/name,d/'staged-bytes'/name)
 assert c.inventory(base)==baseline and c.inventory(pool/'project')==project and c.inventory(pool/'data')==staged and (pool/'state.json').read_bytes()==state
 receipt=dict(schema='attempt05-installed-failed-pool-preservation/1',status='PRESERVED_NOT_RESTORED',state='failed',baseline_unchanged=True,project_exact_before_native=True,staged_exact_before_native=True,install_preimages_journal_present=(run/'output/source-preimages/preimages.json').is_file(),project_files=sum(x['kind']=='file' for x in project['entries']),overlay_members=len(plan['content']),overlay_bytes=(d/'failed-project-overlay.zip').stat().st_size,overlay_sha256=c.digest(d/'failed-project-overlay.zip'),restore=0,models=0,Gamecopies=0)
 c.write(d/'receipt.json',receipt);print(json.dumps(receipt))
