"""Close the one static frame's exact inspector-origin metadata finding. No SUT."""
import hashlib,json,stat
from pathlib import Path
R=Path(__file__).absolute().parents[1];D=R/'data/phase399-independent-static'
def desc(p):
 s=p.lstat();assert stat.S_ISREG(s.st_mode)and s.st_nlink==1 and not any(q.is_symlink()for q in(p,*p.parents))
 return dict(path=str(p.relative_to(R)),size=s.st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def read(p):return json.loads(p.read_text())
def save(n,v):
 with(D/n).open('x')as f:f.write(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+'\n')
first=read(D/'first-failure.json');assert "process_inspector_origin"in first['traceback'] and 'line 83'in first['traceback']
a=read(R/'data/phase395-independent-readback-source/source-contract.json');b=read(R/'data/phase398-independent-readback-source/source-contract.json')
changed=sorted(k for k in set(a)|set(b)if a.get(k)!=b.get(k))
allowed={'schema','SOURCE_review_status','readback_status','source_freeze','recovery_source_owner','source_API','process_inspector_source','failed_capsule_manifest','process_inspector_origin'}
assert set(changed)==allowed
for field in('process_inspector_origin','process_inspector_source','failed_capsule_manifest'):
 for row in(a[field],b[field]):assert desc(R/row['path'])==row
 assert{k:a[field][k]for k in('size','sha256')}=={k:b[field][k]for k in('size','sha256')}
assert b['process_inspector_origin']['path']=='data/phase395-independent-readback-source/readonly-process-inspector.py'
ro=read(R/'data/phase398-independent-readback-source/source-owner.json')['files']
assert b['process_inspector_source']in ro and b['process_inspector_origin']in ro
assert 'data/phase398-independent-readback-source/source-owner.json'not in{r['path']for r in ro}
api=read(R/'data/phase398-attempt05-recovery-source/api-contract.json');freeze=read(R/api['source_freeze']['path'])
old=read(R/'data/phase396-independent-static-first-001/evidence.json')
summary=[]
for stem in('phase398_pool_recovery','phase398_independent_restored_readback','phase398_recovery_gate_source'):
 v=read(R/('data/phase398-attempt05-recovery-source/'+stem+'-inverse.json'))
 summary.append(dict(before=v['before'],after=v['after'],complete_inverse='PASS_IN_FIRST_INDEPENDENT_AUDIT_BEFORE_LINE83',semantic_changed_functions=v['semantic_changed_functions'],unchanged_functions=v['conserved_functions']))
resolution=dict(schema='phase399-static-checker-finding-resolution/1',kind='CHECKER_METADATA_ALLOWLIST_OMISSION_NOT_SUT_FAILURE',original_script=desc(R/'tests/phase399_static_frozen398_audit.py'),original_failure=desc(D/'first-failure.json'),first_invocation=dict(tool_chunk='ccb710',exit_code=1,last_assertion_line=83),earlier_completed_checks=['433 handoff ordinary/nlink1 SHA and7067200B','all freeze descriptors and exact six-module recursive local import closure','three exact byte inverse reconstructions and only two semantic changed functions','old396 eleven recovery and ten reader AST identities','actual/template F01 order and F02 before-read bootstrap','actual API statuses and unchanged395map/pins'],observed_delta=dict(old_origin=a['process_inspector_origin'],new_origin=b['process_inspector_origin'],actual_both_ordinary_singlelink_SHA_equal=True,source_reader_owner_covers_new_origin=True),resolution='395-to398 author truthfully records395 inspector mirror as immediate source; bytes remain equal to384. Add this exact provenance path change to reviewed metadata deltas; no code repair needed.',original_script_reruns=0,SUT_calls=0)
save('static-finding-resolution.json',resolution)
review=dict(schema='phase399-independent-frozen398-static-review/1',status='STATIC_PASS_CONDITIONAL_NINE_CALL_RELEASE',source_freeze=api['source_freeze'],handoff_owner=desc(R/'data/phase398-source-handoff/owned-files.json'),handoff_files=433,handoff_bytes=7067200,import_closure=freeze['import_closure'],independent_inverse_checks=summary,conserved375_functions=old['inverse_checks'][0]['conserved'],conserved384_functions=old['inverse_checks'][2]['conserved'],F01='actual metadata/member -> regular_target -> descriptor; template identical',F02='fixed own-owner descriptor -> strict verify_descriptor -> read returned path; no owner self-reference',reader_contract_changed_fields=changed,inspector_origin_resolution=desc(D/'static-finding-resolution.json'),api=desc(R/'data/phase398-attempt05-recovery-source/api-contract.json'),map=api['map'],input_pins=api['input_pins'],static_logical_cases=20,SUT_imports=0,SUT_calls=0,native=0,models=0,actual_pool=0,proc=0)
save('review.json',review)
leaves=[p for p in D.iterdir()if p.is_file()]+[Path(__file__).absolute(),R/'tests/phase399_static_frozen398_audit.py',R/'docs/phase399_frozen398_execution_binding_spec.md']
rows=[desc(p)for p in sorted(leaves)];save('owned-files.json',dict(schema='phase399-static-owner/1',files=rows,no_more_writes=True))
for row in rows:assert desc(R/row['path'])==row
print(json.dumps(dict(status=review['status'],review=desc(D/'review.json'),owner=desc(D/'owned-files.json'),files=len(rows),bytes=sum(r['size']for r in rows),SUT_calls=0)))
