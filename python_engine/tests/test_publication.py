"""Small release checks; no original-game process, capture or training."""
from pathlib import Path
from unittest.mock import patch
import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'formal68'))
import headless


class PublicationTests(unittest.TestCase):
    def test_exact_runtime_snapshots(self):
        rows = json.loads((ROOT / 'evidence/runtime-sources.json').read_text())['files']
        self.assertEqual(len(rows), 30)
        for name, expected in rows.items():
            raw = (ROOT / name).read_bytes()
            self.assertEqual({'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}, expected, name)

    def test_seed_domains_against_recorded_reference(self):
        self.assertEqual(headless.derive_stream_seeds(32001),
                         (9706918252965337049, 10551809155756902645))
        self.assertEqual(len(headless.ITEMS), 68)
        self.assertNotIn(262, headless.ITEMS)

    def test_invalid_ingress_rejects_before_rng(self):
        layout = json.loads((ROOT / 'examples/formal68.json').read_text())
        bad = copy.deepcopy(layout)
        bad['sides'][0]['items'][0]['item_index'] = 74
        with patch.object(headless, 'GodotPCGInteger', side_effect=AssertionError('RNG constructed')) as rng:
            with self.assertRaises(ValueError):
                headless.initialize(bad, 32001)
            with self.assertRaises(ValueError):
                headless.initialize(layout, True)
            self.assertEqual(rng.call_count, 0)

    def test_single_isolated_formal_cli_regression(self):
        # Trusted stdlib/argument bootstrap precedes the payload-read hook.
        # Candidate imports and the one CLI run may read only exported runtime,
        # the example layout, stdlib and their own output, never a game/capture.
        worker = r'''
from pathlib import Path
import importlib.machinery,json,os,sys,sysconfig
runtime=Path(sys.argv[1]).resolve();layout=Path(sys.argv[2]).resolve();output=Path(sys.argv[3]).resolve()
stdlib={Path(sysconfig.get_path(k)).resolve() for k in ('stdlib','platstdlib')}
allowed={runtime.parent/n for n in json.loads((runtime.parent/'evidence/runtime-sources.json').read_text())['files'] if n.startswith('formal68/')}|{layout}
blocked=[]
def audit(event,args):
 if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)):
  p=Path(os.fsdecode(args[0])).resolve();mode,flags=args[1:3]
  write=(isinstance(mode,str) and any(x in mode for x in 'wax+')) or (isinstance(flags,int) and bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC)))
  standard=any(p.is_relative_to(q) for q in stdlib) and not {'site-packages','dist-packages'}&set(p.parts)
  if (write and p!=output) or (not write and p not in allowed and p!=output and not standard):
   blocked.append(str(p));raise PermissionError('outside exported runtime/layout/stdlib/output')
 if event.startswith(('socket.','subprocess.','os.exec')) or event in ('os.system','os.fork','os.posix_spawn'):
  blocked.append(event);raise PermissionError('network/process denied')
def source_only(loader,fullname):return loader.source_to_code(loader.get_data(loader.path),loader.path)
importlib.machinery.SourceFileLoader.get_code=source_only
sys.path.insert(0,str(runtime));sys.addaudithook(audit)
import headless
sys.argv=['headless.py','--layout',str(layout),'--seed','32001','--output',str(output)]
headless.main()
assert not blocked,blocked
print(json.dumps({'blocked_payload_or_network_attempts':blocked,'oracle_reads':0}))
'''
        with tempfile.TemporaryDirectory(prefix='python-engine-publication-') as folder:
            output = Path(folder) / 'result.json'
            done = subprocess.run([sys.executable, '-I', '-B', '-S', '-c', worker,
                                   str(ROOT / 'formal68'), str(ROOT / 'examples/formal68.json'), str(output)],
                                  cwd=folder, capture_output=True, text=True, timeout=30)
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertEqual(json.loads(done.stdout)['blocked_payload_or_network_attempts'], [])
            result = json.loads(output.read_text())
            self.assertEqual(result['schema'], 'headless-battle-result/1')
            self.assertEqual(len(result['events']), 681)
            self.assertEqual(len(result['random_inputs']), 842)
            self.assertEqual(result['scheduling']['frames'], 2340)
            self.assertEqual(result['final']['winner'], 'O')
            self.assertEqual(result['coverage']['items'], sorted(headless.ITEMS))


if __name__ == '__main__':
    unittest.main()
