"""Read-only pins and AST for the Root397 ownership supplement; no SUT import."""
import ast
import hashlib
import json
from pathlib import Path
import stat
R=Path(__file__).absolute().parents[1]
D=R/'data/phase397-independent-execution-closure-review'

def desc(p):
 s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and not any(q.is_symlink()for q in (p,*p.parents))
 return dict(path=str(p.relative_to(R)),size=s.st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def read(p):return json.loads(p.read_text())
def save(p,v):
 with p.open('x') as f:f.write(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+'\n')
def checked(row):
 assert desc(R/row['path'])==row
 return row

def main():
 #396 has been closed before this separate supplementary frame starts.
 r396=read(R/'data/phase396-independent-static-first-001/review.json')
 assert r396['status']=='BLOCKED396_SOURCE_PHYSICAL_GATE_ORDER_AND_READER_OWNER_BOOTSTRAP' and r396['no_more_writes'] is True
 assert not D.exists();D.mkdir()
 p=R/'data/phase397-root-native-execution-closure/execution-source-owner.json'
 owner=checked(dict(path=str(p.relative_to(R)),size=10755,sha256='e7d8b87673eb56ca432e3d8c3401c4c44b5f3c60f6b4a10de5c99b673fd1876a'))
 value=read(p);rows=[checked(r)for r in value['files']]
 assert len(rows)==len({r['path'] for r in rows})==52 and sum(r['size']for r in rows)==1306995
 original=checked(value['source_owner_origin']);old=read(R/original['path'])['files']
 expected={r['path']:r for r in old}
 expected[original['path']]=original
 for path,size,sha in [('tests/phase363_oracle_storage.py',15496,'ca098c2900a1e9d1c255c5e77009456c6b00cf285dba90a96def7ba5d39792fc'),('data/phase363-oracle-repair-source/source-owner.json',2546,'0806b38ffd797a16feee0a14d4ed7538d79997e32cc8b27dca2314eb0d400d51')]:
  expected[path]=checked(dict(path=path,size=size,sha256=sha))
 assert len(old)==49 and {r['path']:r for r in rows}==expected
 assert value['native_authorized'] is False and value['models_authorized'] is False
 graph=[];seen=set();todo=['tests/phase391_oracle_host.py']
 while todo:
  name=todo.pop()
  if name in seen:continue
  seen.add(name);assert name in expected;checked(expected[name])
  tree=ast.parse((R/name).read_text(),filename=name);mods=[]
  for node in ast.walk(tree):
   if isinstance(node,ast.Import):mods.extend(a.name for a in node.names)
   elif isinstance(node,ast.ImportFrom)and node.module:mods.append(node.module)
  local=sorted({'tests/'+m+'.py'for m in mods if(R/'tests'/(m+'.py')).is_file()})
  assert all(n in expected for n in local)
  graph.append(dict(path=name,local_imports=local));todo.extend(local)
 host='tests/phase391_oracle_host.py';raw=(R/host).read_text();tree=ast.parse(raw)
 functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
 names=['execute_driver_descriptors','_payload_rows','resolve_execute_payloads','verify_execute_payloads','plan','execute']
 callsites=[]
 for name in names:
  n=functions[name];text=ast.get_source_segment(raw,n)
  (D/(name+'.source.txt')).write_text(text+'\n')
  callsites.append(dict(function=name,line=n.lineno,end_line=n.end_lineno,AST_sha256=hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()))
 driver=ast.get_source_segment(raw,functions['execute_driver_descriptors'])
 assert "read(descriptor(root,config['source_owner']))['files']" in driver
 resolver=ast.get_source_segment(raw,functions['resolve_execute_payloads'])
 assert 'list(driver_descriptors)'in resolver and 'verify_execute_payloads(root,graph)'in resolver
 verifier=ast.get_source_segment(raw,functions['verify_execute_payloads'])
 assert 'for row in unique.values(): check_source_descriptor(root,row)'in verifier
 execute=functions['execute'];calls=[n for n in ast.walk(execute)if isinstance(n,ast.Call)]
 find=lambda name:sorted(n.lineno for n in calls if isinstance(n.func,ast.Name)and n.func.id==name)
 source_map_line=next(n.lineno for n in calls if isinstance(n.func,ast.Name)and n.func.id=='write_new' and isinstance(n.args[0],ast.BinOp) and isinstance(n.args[0].right,ast.Constant)and n.args[0].right.value=='driver/source-map.json')
 assert find('verify_execute_payloads')[0] < find('lease')[0] < source_map_line < min(find('execute_process'))
 save(D/'evidence.json',dict(schema='phase397-independent-source-supplement-evidence/1',execution_owner=owner,ordinary_nlink1_files=52,bytes=1306995,exact_union='39149 leaves + original391 owner + old363storage + old363 owner',all_actual_pins=rows,recursive_local_import_graph=graph,caller_AST=callsites,source_map_line=source_map_line,first_process_call_line=min(find('execute_process')),resolver_calls=0,driver_calls=0,SUT_imports=0,SUT_calls=0,native=0,models=0))
 report=dict(schema='phase397-independent-execution-closure-review/1',status='INDEPENDENT397_EXECUTION_SOURCE_SUPPLEMENT_STATIC_PASS_ROOT_PENDING',execution_source_owner=owner,source_freeze=checked(dict(path='data/phase391-terminal-source/combined-source-freeze.json',size=65361,sha256='e55a602c9d7087a71a2fe6b78a3a143663fc8f0f659c0fe3fb690019ba8173c9')),evidence=desc(D/'evidence.json'),ordinary_nlink1_leaves=52,bytes=1306995,actual_resolver_calls=0,actual_driver_calls=0,SUT_imports=0,SUT_calls=0,native=0,models=0,Godot=0,actual_pool=0,actual_source_driver_archive_created=False,conditional_conclusion='If future Root config selects this exact source_owner, actual391 execute_driver_descriptors consumes its files, resolver carries them into driver_sources, strict verification checks them before lease, and execute archives them before first Godot process.',limitations=['Static pins/AST only; no resolver, source gate, driver, process or model called','No actual future Root config or native archive asserted','Does not grant native release or clear BLOCKED396 recovery SOURCE','Root must prepin full execution sources before interpreter startup, then runtime rechecks; READY/fresh budget/fixed06 release remain required'],no_more_writes=True)
 save(D/'review.json',report)
 leaves=sorted(p for p in D.rglob('*')if p.is_file())+[Path(__file__).absolute(),R/'docs/phase396_independent_execution_binding_addendum.md']
 owned=[desc(p) for p in sorted(set(leaves))]
 save(D/'owned-files.json',dict(schema='phase397-independent-static-owner/1',files=owned,leaf_count=len(owned),byte_count=sum(r['size']for r in owned),no_more_writes=True))
 for row in owned:checked(row)
 print(json.dumps(dict(status=report['status'],review=desc(D/'review.json'),owner=desc(D/'owned-files.json'),files=len(owned),bytes=sum(r['size']for r in owned),SUT_calls=0)))
if __name__=='__main__':main()
