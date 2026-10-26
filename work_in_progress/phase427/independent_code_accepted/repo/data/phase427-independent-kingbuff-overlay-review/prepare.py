from pathlib import Path
import ast,hashlib,json,os,stat
base=Path('data/phase427-independent-kingbuff-overlay-review')
def read(d):
 p=Path(d['path']);p=p if p.is_absolute() else Path.cwd()/p
 for a in (p,*p.parents):
  s=a.lstat();assert not stat.S_ISLNK(s.st_mode)
 s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
 try:
  chunks=[]
  while True:
   b=os.read(fd,65536)
   if not b:break
   chunks.append(b)
  z=os.fstat(fd)
 finally:os.close(fd)
 b=b''.join(chunks);assert len(b)==d['size'] and hashlib.sha256(b).hexdigest()==d['sha256'];assert (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns)
 return b
ownerdesc={'path':'data/phase426-king-buff-overlay-source/source-owner.json','size':6809,'sha256':'b7d192bde3caaae4a9be76e8e276b8a14b302b3ee854ce64f25a5a53ad5fe027'}
o=json.loads(read(ownerdesc));buf={d['path']:read(d) for d in o['files']};assert len(buf)==33 and sum(map(len,buf.values()))==727035
s=buf['tests/phase426_king_buff_overlay.py'].decode();old=buf['tests/phase420_initial_autohide_projection.py'].decode();a=ast.parse(s);b=ast.parse(old)
api=json.loads(buf['data/phase426-king-buff-overlay-source/api-contract.json']);reuse=[]
for d in api['source_text_reuse']:
 n=next(n for n in a.body if isinstance(n,ast.FunctionDef) and n.name==d['name']);p=next(n for n in b.body if isinstance(n,ast.FunctionDef) and n.name==d['name'])
 t=''.join(s.splitlines(keepends=True)[n.lineno-1:n.end_lineno]).encode();u=''.join(old.splitlines(keepends=True)[p.lineno-1:p.end_lineno]).encode();assert t==u and len(t)==d['size'] and hashlib.sha256(t).hexdigest()==d['sha256'];assert ast.dump(n,include_attributes=False)==ast.dump(p,include_attributes=False);reuse.append(d)
context=json.loads(buf['data/phase426-king-buff-overlay-source/context.json']);data={k:json.loads(read(d)) for k,d in context['data'].items()}
static={'schema':'independent427-static-evidence/1','owner':ownerdesc,'owned_files':o['files'],'owned_leaves':33,'owned_bytes':727035,'reuse':reuse,'reuse_count':11,'reuse_bytes_AST_equal':True,'old420_imports':0,'static_review':{'collector44':True,'pair_gaps_global':True,'A4_validate_exact88_keys':True,'nonpair86_same_rows':True,'pair_atomic0or2':True,'derive_internal_gate_before_data':True,'run_recomputes_evidence':True,'release_saveddata_exactset':True,'Root423_actualreview_outputowner_chain':True,'final427_owner_context_design_root_binding':True,'exclusive_output_after_verified_release':True},'static_limits':'No positive gate minted. Pair union/preservation after authorized gate reviewed statically; positive actual output deferred to fresh Root execution and independent result review. Reused helpers not dynamically retested except new integration boundaries.','saved_payload_pins':context['data'],'static_first_error_resolution':'API helper pins include terminal newline. Initial AST segment omitted it; all11 unchanged full-line byte/AST comparisons now pass. This is prep formatting, not426 semantic failure.','no_raw_or_project_execution':True}
for name,d in [('static-evidence.json',static),('fixture-saved-inputs.json',data)]:
 with (base/name).open('x') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
print('STATIC_PASS33leaves11helpers;fixture_saved_only')
