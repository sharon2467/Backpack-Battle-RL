"""Validate recovered entry points; optional one Python smoke and version probe."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import sys


def pin(path):
    with path.open('rb') as stream:
        return dict(size=path.stat().st_size, sha256=hashlib.file_digest(stream, 'sha256').hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--runtime-version', action='store_true')
    args = parser.parse_args()
    dest = args.destination.resolve(strict=True)
    receipt = json.loads((dest / 'RECOVERY-RECEIPT.json').read_text())
    if receipt['status'] != 'ALL_ARCHIVES_AND_LOGICAL_FILES_VERIFIED':
        raise ValueError('successful recovery receipt required')
    repo = dest / 'workspace/python-original-engine/repo'
    state = json.loads((repo / 'data/phase024-root/current-task-state.json').read_text())
    if state['status'] != 'PAUSED_USER_BALANCE_THRESHOLD' or state['canonical']['headless_structural_default_items'] != 68:
        raise ValueError('paused formal68 state required')
    if state['accepted75_candidate_final']['promoted'] is not False:
        raise ValueError('candidate75 must remain unpromoted')
    freeze = json.loads((repo / state['canonical']['source_freeze']).read_text())['files']
    if len(freeze) != 15:
        raise ValueError('formal15 source closure required')
    for name, expected in freeze.items():
        want = dict(size=expected.get('size', expected.get('bytes')), sha256=expected['sha256'])
        if pin(repo / name) != want:
            raise ValueError('restored formal source mismatch: ' + name)
    for name in ('data/phase340-independent026-final/summary.json',
                 'data/phase344-promotion-portable-PARTIAL-pause/handoff.json',
                 'data/phase346-independent-portable75-source/source-owner.json'):
        if not (repo / name).is_file():
            raise ValueError('current engineering record missing: ' + name)
    result = dict(schema='restored-entrypoint-check/1', formal_source_files=15,
                  formal_items=68, candidate75_promoted=False, implementation_paused=True,
                  fresh_OS_verified=False, full_physical_restore=receipt['full_physical_restore'],
                  pure_smoke_runs=0, original_battle_runs=0, training_runs=0,
                  runtime_version_probes=0)
    output = dest / 'entrypoint-validation'
    output.mkdir(exist_ok=False)
    if args.smoke:
        fixture = repo / 'data/phase320-independent-postcheck/runtime/example-layout.json'
        target = output / 'formal68-result.json'
        worker = r'''
from pathlib import Path
import hashlib,importlib.machinery,json,os,sys,sysconfig
repo=Path(sys.argv[1]).resolve();fixture=Path(sys.argv[2]).resolve();output=Path(sys.argv[3]).resolve()
freeze=json.loads((repo/'data/phase314-support68-final-export-source/candidate-source-freeze.json').read_text())['files']
allowed={repo/n for n in freeze}|{fixture}
stdlib={Path(sysconfig.get_path(k)).resolve() for k in ('stdlib','platstdlib')}
reads=[];blocked=[]
def audit(event,args):
 if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)):
  p=Path(os.fsdecode(args[0])).resolve();mode,flags=args[1:3]
  writing=(isinstance(mode,str) and any(x in mode for x in 'wax+')) or (isinstance(flags,int) and bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC)))
  standard=any(p.is_relative_to(q) for q in stdlib) and not {'site-packages','dist-packages'}&set(p.parts)
  if (writing and p!=output) or (not writing and p not in allowed and p!=output and not standard):
   blocked.append(str(p));raise PermissionError('outside recovered15/fixture/stdlib/own-output')
  if not writing:reads.append('runtime' if p in allowed else 'stdlib' if standard else 'own-output')
 if event.startswith(('socket.','subprocess.','os.exec')) or event in ('os.system','os.fork','os.posix_spawn'):
  blocked.append(event);raise PermissionError('network/process denied')
def source_only(loader,fullname):return loader.source_to_code(loader.get_data(loader.path),loader.path)
importlib.machinery.SourceFileLoader.get_code=source_only
sys.path.insert(0,str(repo));sys.addaudithook(audit)
import headless
sys.argv=['headless.py','--layout',str(fixture),'--seed','32001','--output',str(output)]
headless.main()
assert not blocked,blocked
print(json.dumps(dict(blocked=blocked,payload_read_scopes=sorted(set(reads)),old_workspace_payload_reads=0)))
'''
        done = subprocess.run([sys.executable, '-I', '-B', '-S', '-c', worker,
                               str(repo), str(fixture), str(target)], cwd=output,
                              capture_output=True, text=True, timeout=60)
        (output / 'python-smoke.stdout').write_text(done.stdout)
        (output / 'python-smoke.stderr').write_text(done.stderr)
        if done.returncode:
            raise RuntimeError('recovered Python smoke failed; first outputs preserved: ' + done.stderr)
        audit = json.loads(done.stdout)
        produced = json.loads(target.read_text())
        facts = dict(seed=32001,events=len(produced['events']),draws=len(produced['random_inputs']),
                     frames=produced['scheduling']['frames'],winner=produced['final']['winner'])
        if facts != dict(seed=32001, events=681, draws=842, frames=2340, winner='O'):
            raise ValueError('restored formal example differs from historical regression')
        # Read the retained historical receipt only after output creation.
        historical = json.loads((repo / 'data/phase320-independent-postcheck/review.json').read_text())
        same_bytes = pin(target) == {k: historical['result'][k] for k in ('size', 'sha256')}
        result.update(pure_smoke_runs=1, smoke=facts, smoke_output=pin(target),
                      historical_example_output_byte_identical=same_bytes,
                      smoke_payload_audit=audit)
        if not same_bytes:
            raise ValueError('full recovered CLI output differs from retained historical SHA')
    if args.runtime_version:
        runtime = dest / 'workspace/godotsteam-startup-20261013'
        engine = runtime / 'engine/godotsteam.362.editor.x86_64'
        env = dict(os.environ)
        env['LD_LIBRARY_PATH'] = str(runtime / 'engine') + ':' + str(runtime / 'debian/usr/lib/x86_64-linux-gnu')
        done = subprocess.run([str(engine), '--version'], cwd=output, env=env,
                              capture_output=True, text=True, timeout=30)
        (output / 'runtime-version.stdout').write_text(done.stdout)
        (output / 'runtime-version.stderr').write_text(done.stderr)
        if done.returncode or '3.6.2' not in done.stdout:
            raise RuntimeError('restored runtime version probe failed: ' + done.stderr)
        result.update(runtime_version_probes=1, runtime_version=done.stdout.strip())
    result['status'] = 'RESTORED_ENTRYPOINT_CHECK_PASS'
    with (output / 'summary.json').open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
