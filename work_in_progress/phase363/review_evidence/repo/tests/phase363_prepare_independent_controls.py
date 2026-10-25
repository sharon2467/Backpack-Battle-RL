"""Pin/inverse SOURCE and preseal finite controls only; no helper imports/operations."""
import ast
import copy
import hashlib
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'data/phase363-independent-source-review';A=R/'data/phase363-oracle-repair-source'
def desc(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(R)),size=len(b),sha256=hashlib.sha256(b).hexdigest())
def save(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def main():
 D.mkdir(exist_ok=False);(D/'SOURCE').mkdir()
 owner=json.loads((A/'source-owner.json').read_text());assert desc(A/'source-owner.json')['sha256']=='0806b38ffd797a16feee0a14d4ed7538d79997e32cc8b27dca2314eb0d400d51'
 for row in owner['files']:assert desc(R/row['path'])==row
 oldf=json.loads((R/'data/phase362-oracle-capture-source/combined-source-freeze.json').read_text());newf=json.loads((A/'combined-source-freeze.json').read_text());assert oldf['paths']==newf['paths'] and oldf['collector']==newf['collector']
 assert desc(R/newf['collector']['path'])==newf['collector']
 cfg=[desc(p) for p in sorted((R/'data/phase362-oracle-capture-source/case-A').iterdir())]
 changed={'storage':{'install','lease','reset_previous','state_write'},'process':{'execute_process'},'host':{'source_gate','plan','execute'}};deltas={}
 for stem in changed:
  old=(R/f'tests/phase362_oracle_{stem}.py').read_text();new=(R/f'tests/phase363_oracle_{stem}.py').read_text();ot,nt=ast.parse(old),ast.parse(new);compile(nt,stem,'exec')
  of={n.name:n for n in ot.body if isinstance(n,ast.FunctionDef)};nf={n.name:n for n in nt.body if isinstance(n,ast.FunctionDef)}
  actual={k for k in of if ast.dump(of[k],include_attributes=False)!=ast.dump(nf[k],include_attributes=False)};assert actual==changed[stem]
  if stem=='host':
   s=new.replace('from phase363_oracle_storage import','from phase362_oracle_storage import').replace('from phase363_oracle_process import','from phase362_oracle_process import').replace("SOURCE = 'data/phase363-oracle-repair-source'\nDATA = 'data/phase362-oracle-capture-source'","SOURCE = 'data/phase362-oracle-capture-source'").replace("DATA+'/case-A","SOURCE+'/case-A").replace("DATA+'/collector.gd'","SOURCE+'/collector.gd'").replace("DATA+'/disposable-marker.txt'","SOURCE+'/disposable-marker.txt'").replace('INDEPENDENT363_INSTALLER_MONITOR_SOURCE_ACCEPTED_ROOT_PENDING','INDEPENDENT362_ORACLE_CAPTURE_SOURCE_ACCEPTED_ROOT_PENDING').replace('phase363-root-oracle-acceptance/1','phase362-root-oracle-acceptance/1');assert s==old
  else:
   inverse=copy.deepcopy(nt);inverse.body=[copy.deepcopy(of[n.name]) if isinstance(n,ast.FunctionDef) else n for n in inverse.body if not isinstance(n,ast.FunctionDef) or n.name in of]
   if stem=='process':
    inverse.body=[n for n in inverse.body if not isinstance(n,ast.Import) or [a.name for a in n.names]!=['math']]
    for n in inverse.body:
     if isinstance(n,ast.ImportFrom) and n.module=='phase363_oracle_storage':n.module='phase362_oracle_storage'
   assert ast.dump(inverse,include_attributes=False)==ast.dump(ot,include_attributes=False)
  (D/'SOURCE'/f'{stem}.py').write_bytes(new.encode());deltas[stem]=dict(changed=sorted(actual),new_functions=sorted(set(nf)-set(of)),inverse='PASS')
 (D/'SOURCE/compaction.py').write_bytes((R/'tests/native_run_compaction.py').read_bytes())
 monitor=next(n for n in ast.parse((D/'SOURCE/process.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='monitor_command')
 assert not [n for n in ast.walk(monitor) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ('wait','sleep')]
 old_static=R/'data/phase362-independent-source-review/static-first-001/report.json';assert not json.loads(old_static.read_text())['failures']
 save(D/'source-review.json',dict(schema='phase363-independent-delta-review/1',status='SOURCE_DELTA_REVIEWED_CONTROLS_PENDING',author_leaves=len(owner['files']),author_bytes=sum(r['size'] for r in owner['files']),deltas=deltas,inherited_collector=desc(R/newf['collector']['path']),inherited_paths75_exact=True,inherited_three_configs=cfg,reused_seven_static=desc(old_static),reused_not_rerun=True,single_selector_no_extra_wait=True,cleanup='TERM/grace/KILL uses own pgid/sid membership independent of leader; dynamic controls pending',kernel_quota=False,actual50ms='Configured selector timeout plus IO/scan/cleanup; no hard scan bound claim',helper_imports=0,operations=0))
 labels=[
 ('hardlink-version-regression','REJECT_UNCHANGED'),('all-target-hardlink-preflight','REJECT_UNCHANGED'),('regular-atomic-install-positive','PASS_EXACT_BYTES_METADATA'),('wrong-preimage','REJECT_UNCHANGED'),('symlink-leaf-and-ancestor','REJECT_UNCHANGED'),('unsafe-installer-path','REJECT_UNCHANGED'),('source-artifact-overlap','REJECT_UNCHANGED'),('existing-backup','REJECT_UNCHANGED'),('journal-exact-inverse','PASS_EXACT_BYTES_METADATA'),('added-file-before-null','PASS_NEW_AND_REJECT_EXISTING'),
 ('real-Python-monitor-positive','PASS_CLEAN_OUTPUT'),('combined-PIPE-cap','PASS_ABORT_PARTIAL'),('wall-timeout','PASS_TIMEOUT_NO_LIVE'),('leader-exit-descendant-ignores-TERM','PASS_GROUP_KILL_NO_LIVE'),('active-leader-and-descendant-ignore-TERM','PASS_GROUP_KILL_NO_LIVE'),('allowed-cache-accounting','PASS_ACTUAL_SCAN'),('unknown-user-root-abort','PASS_SCAN_ABORT'),('floor-attempt-exact-SOURCE-boundaries','PASS_PREDICATES'),('scan-IO-failure-partial','PASS_SCAN_ABORT_PARTIAL'),('single-poll-and-measured-gap','PASS_SOURCE_MEASUREMENTS_NO_MAX50_CLAIM'),('fixed-oracle-wrapper','PASS_SOURCE_ONLY'),
 ('tiny-logical-overlay-and-newREADY','PASS_FS_ONLY'),('bad-ZIP-bytes','REJECT'),('duplicate-foreign-overlay-members','REJECT'),('live-content-drift','REJECT'),('live-mode-mtime-drift','REJECT'),('unknown-and-missing-oldREADY-proof','REJECT'),('no-scratch-reconstruct','PASS_SOURCE_ONLY'),('capture-rename-neutral-interface-limit','SOURCE_ONLY_NOT_EXECUTED'),
 ('missing-ROOT-execute-refusal','REJECT_BEFORE_POPEN'),('wrong-schema-SOURCE-ROOT-refusal','REJECT_BEFORE_POPEN'),('roots-relocation-run-collision','REJECT_NO_OPERATION'),('real-budget-and-boundaries','PASS_IF_REAL_HEADROOM'),('writer-log-user-ledger','PASS_SOURCE_AND_PRIOR_UNIT'),('proof-before-unique-oracle','PASS_SOURCE_ONLY'),('unchanged-model-guards','PASS_SOURCE_IDENTITY')]
 assert len(labels)==36
 save(D/'cases.json',[dict(id=i+1,label=l,expected=e) for i,(l,e) in enumerate(labels)])
 print(json.dumps(dict(cases=36,source_delta='PASS',helper_imports=0)))
if __name__=='__main__':main()
