"""Bounded static completion after preserving the first audit's wrong owner-only premise."""
import ast
import hashlib
import json
from pathlib import Path
import stat
R=Path(__file__).absolute().parents[1]
D=R/'data/phase397-independent-execution-closure-review'
def desc(p):
 s=p.lstat();assert stat.S_ISREG(s.st_mode)and s.st_nlink==1 and not any(q.is_symlink()for q in(p,*p.parents))
 return dict(path=str(p.relative_to(R)),size=s.st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def read(p):return json.loads(p.read_text())
def save(p,v):
 with p.open('x')as f:f.write(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+'\n')
def check(row):assert desc(R/row['path'])==row

def main():
 assert D.is_dir() and not any(D.iterdir())
 initial=R/'tests/phase397_independent_execution_closure_audit.py'
 save(D/'first-static-checker-failure.json',dict(schema='phase397-independent-first-checker-failure/1',kind='INDEPENDENT_CHECKER_COVERAGE_PREMISE_ERROR_NOT_SUT_FAILURE',script=desc(initial),tool_chunk='9eba67',returncode=1,traceback='Traceback (most recent call last):\n  File "/workspace/python-original-engine/repo/tests/phase397_independent_execution_closure_audit.py", line 74, in <module>\n    if __name__==\'__main__\':main()\n                            ^^^^^^\n  File "/workspace/python-original-engine/repo/tests/phase397_independent_execution_closure_audit.py", line 46, in main\n    assert all(n in expected for n in local)\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nAssertionError\n',completed_before_failure='52 owner leaves ordinary/nlink1/SHA, count/bytes/exact49+3 union; failure occurred when requiring imported363process in owner alone.',wrong_premise='All runtime imports must be in the52 owner alone.',correct_premise='Actual391 execute_driver_descriptors unions freeze.files and config.source_owner.files, then config/reviews/explicit bindings.',original_script_reruns=0,SUT_imports=0,SUT_calls=0))
 ownerpath='data/phase397-root-native-execution-closure/execution-source-owner.json'
 owner=desc(R/ownerpath);assert owner==dict(path=ownerpath,size=10755,sha256='e7d8b87673eb56ca432e3d8c3401c4c44b5f3c60f6b4a10de5c99b673fd1876a')
 op=read(R/ownerpath);owned={r['path']:r for r in op['files']}
 freeze_desc=dict(path='data/phase391-terminal-source/combined-source-freeze.json',size=65361,sha256='e55a602c9d7087a71a2fe6b78a3a143663fc8f0f659c0fe3fb690019ba8173c9')
 check(freeze_desc);freeze=read(R/freeze_desc['path']);frozen={r['path']:r for r in freeze['files']}
 assert len(frozen)==len(freeze['files'])==152 and len(owned)==len(op['files'])==52
 overlap=set(frozen)&set(owned);assert all(frozen[k]==owned[k]for k in overlap)
 union=dict(frozen);union.update(owned)
 for row in union.values():check(row)
 origin=op['source_owner_origin'];check(origin)
 original=read(R/origin['path'])['files'];expect={r['path']:r for r in original};expect[origin['path']]=origin
 for name in ('tests/phase363_oracle_storage.py','data/phase363-oracle-repair-source/source-owner.json'):expect[name]=owned[name]
 assert len(original)==49 and expect==owned
 assert owned['tests/phase363_oracle_storage.py']==dict(path='tests/phase363_oracle_storage.py',size=15496,sha256='ca098c2900a1e9d1c255c5e77009456c6b00cf285dba90a96def7ba5d39792fc')
 assert owned['data/phase363-oracle-repair-source/source-owner.json']==dict(path='data/phase363-oracle-repair-source/source-owner.json',size=2546,sha256='0806b38ffd797a16feee0a14d4ed7538d79997e32cc8b27dca2314eb0d400d51')
 assert op['native_authorized']is False and op['models_authorized']is False
 graph=[];seen=set();todo=['tests/phase391_oracle_host.py']
 while todo:
  name=todo.pop()
  if name in seen:continue
  seen.add(name);assert name in union
  tree=ast.parse((R/name).read_text(),filename=name);mods=[]
  for node in ast.walk(tree):
   if isinstance(node,ast.Import):mods.extend(a.name for a in node.names)
   elif isinstance(node,ast.ImportFrom)and node.module:mods.append(node.module)
  local=sorted({'tests/'+m+'.py'for m in mods if(R/'tests'/(m+'.py')).is_file()})
  assert all(n in union for n in local)
  graph.append(dict(path=name,local_imports=local,covered_by_freeze=name in frozen,covered_by_owner=name in owned));todo.extend(local)
 schema=freeze['schema_module'];assert union[schema['path']]==schema
 host='tests/phase391_oracle_host.py';raw=(R/host).read_text();tree=ast.parse(raw)
 fn={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
 names=['execute_driver_descriptors','_payload_rows','resolve_execute_payloads','verify_execute_payloads','plan','execute']
 callsites=[]
 for name in names:
  n=fn[name];text=ast.get_source_segment(raw,n)
  with(D/(name+'.source.txt')).open('x')as f:f.write(text+'\n')
  callsites.append(dict(function=name,line=n.lineno,end_line=n.end_lineno,AST_sha256=hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()))
 driver=ast.get_source_segment(raw,fn['execute_driver_descriptors'])
 assert "rows=list(freeze['files'])+read(descriptor(root,config['source_owner']))['files']"in driver
 assert "rows += [config_descriptor,config['source_owner'],config['source_freeze']]"in driver
 assert "rows += [review['receipt'],review['owner']]"in driver
 payload=ast.get_source_segment(raw,fn['_payload_rows'])
 assert "row['path'] in result and result[row['path']]!=row"in payload and 'same source path has conflicting identities'in payload
 resolver=ast.get_source_segment(raw,fn['resolve_execute_payloads'])
 assert 'list(driver_descriptors)'in resolver and 'list(bindings.values())'in resolver and 'verify_execute_payloads(root,graph)'in resolver
 verifier=ast.get_source_segment(raw,fn['verify_execute_payloads'])
 assert 'for row in unique.values(): check_source_descriptor(root,row)'in verifier
 calls=[n for n in ast.walk(fn['execute'])if isinstance(n,ast.Call)]
 find=lambda name:sorted(n.lineno for n in calls if isinstance(n.func,ast.Name)and n.func.id==name)
 source_map_line=next(n.lineno for n in calls if isinstance(n.func,ast.Name)and n.func.id=='write_new'and isinstance(n.args[0],ast.BinOp)and isinstance(n.args[0].right,ast.Constant)and n.args[0].right.value=='driver/source-map.json')
 assert find('verify_execute_payloads')[0]<find('lease')[0]<source_map_line<min(find('execute_process'))
 key_paths=['tests/phase363_oracle_process.py','tests/native_run_compaction.py','tests/phase391_oracle_host.py',schema['path'],'tests/phase363_oracle_storage.py','data/phase363-oracle-repair-source/source-owner.json']
 coverage=[dict(descriptor=union[k],in_freeze=k in frozen,in_owner=k in owned)for k in key_paths]
 save(D/'evidence.json',dict(schema='phase397-independent-static-union-evidence/1',execution_owner=owner,source_freeze=freeze_desc,owner_leaf_count=52,owner_bytes=sum(r['size']for r in owned.values()),freeze_leaf_count=152,overlap_count=len(overlap),union_leaf_count=len(union),union_bytes=sum(r['size']for r in union.values()),all_union_leaves_ordinary_nlink1_SHA_checked=True,union_descriptors=[union[k]for k in sorted(union)],key_dependency_coverage=coverage,recursive_local_import_graph=graph,caller_AST=callsites,source_map_write_line=source_map_line,first_process_call_line=min(find('execute_process')),SUT_imports=0,SUT_calls=0,native=0,models=0))
 report=dict(schema='phase397-independent-execution-closure-review/1',status='INDEPENDENT397_EXECUTION_SOURCE_SUPPLEMENT_STATIC_PASS_ROOT_PENDING',execution_source_owner=owner,source_freeze=freeze_desc,evidence=desc(D/'evidence.json'),first_checker_failure=desc(D/'first-static-checker-failure.json'),ordinary_nlink1_owner_leaves=52,owner_bytes=1306995,actual_resolver_calls=0,actual_driver_calls=0,SUT_imports=0,SUT_calls=0,native=0,models=0,Godot=0,actual_pool=0,original_checker_reruns=0,actual_source_driver_archive_created=False,conditional_conclusion='If future Root config selects this exact owner, actual391 caller consumes freeze.files union owner.files plus config/review descriptors and source bindings. Conflicting duplicate descriptors reject; all sources receive strict checks before lease, then execute copies driver_sources and writes source-map before first Godot call.',limitations=['Static pins/AST only; no resolver, source gate, driver, process or model called','Root39752 supplements the frozen391152; it does not replace freeze or confer native permission','Future actual config and archived source-driver do not yet exist in this review','396 remains BLOCKED and neither392 nor394 is rerun','Root pre-interpreter closure pins, real restore/readback/READY, fresh native budget and fixed06 release remain separate'],no_more_writes=True)
 save(D/'review.json',report)
 leaves=sorted(p for p in D.rglob('*')if p.is_file())+[Path(__file__).absolute(),initial,R/'docs/phase396_independent_execution_binding_addendum.md']
 rows=[desc(p)for p in sorted(set(leaves))]
 save(D/'owned-files.json',dict(schema='phase397-independent-static-owner/1',files=rows,leaf_count=len(rows),byte_count=sum(r['size']for r in rows),no_more_writes=True))
 for row in rows:check(row)
 print(json.dumps(dict(status=report['status'],union_files=len(union),union_bytes=sum(r['size']for r in union.values()),review=desc(D/'review.json'),owner=desc(D/'owned-files.json'),files=len(rows),bytes=sum(r['size']for r in rows),SUT_calls=0)))
if __name__=='__main__':main()
