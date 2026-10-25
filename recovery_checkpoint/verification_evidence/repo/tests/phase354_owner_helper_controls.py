"""Tiny independent public-artifact I/O controls, no archived code execution."""
from pathlib import Path,PurePosixPath
from copy import deepcopy
import ast
import hashlib
import importlib.util
import json
import os
import shutil
import stat
import sys
import sysconfig
import tempfile
import traceback

R=Path(__file__).resolve().parents[1]
SOURCE=R/'data/phase354-independent-owner-helper-source'
OUT=R/'data/phase354-independent-owner-helper-controls-first-001'
BODY=b'raise RuntimeError("ARCHIVE_BODY_MUST_NEVER_BE_EXECUTED")\n'
DEST='workspace/checkpoints/tiny-synthetic-owner.zip'

def pin(p):
 b=p.read_bytes();return dict(size=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,v):p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def load(p,name):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
 assert not OUT.exists();OUT.mkdir()
 owner=json.loads((SOURCE/'owned-files.json').read_text())
 for n,w in owner['files'].items():assert pin(R/n)==w,n
 tmp=Path(tempfile.mkdtemp(prefix='phase354-owner-helper-independent-',dir='/tmp'))
 W=load(SOURCE/'check_restored_work.py','phase354_frozen_work_reader')
 tree=ast.parse((SOURCE/'check_restored_work.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
 loop=next(n for n in ast.walk(fn) if isinstance(n,ast.For) and isinstance(n.target,ast.Tuple) and [getattr(x,'id',None) for x in n.target.elts]==['leaf','wanted'])
 # Original three statements, no removed/weakened guard.
 block=deepcopy(loop.body[:3]);assert isinstance(block[2],ast.If)
 resolver=ast.FunctionDef(name='resolve_owner_leaf',args=ast.arguments(posonlyargs=[],args=[ast.arg(arg=x) for x in ('leaf','aliases','repo')],kwonlyargs=[],kw_defaults=[],defaults=[]),body=block+[ast.Return(value=ast.Name(id='actual',ctx=ast.Load()))],decorator_list=[])
 module=ast.fix_missing_locations(ast.Module(body=[resolver],type_ignores=[]));env=dict(PurePosixPath=PurePosixPath,pin=W.pin);exec(compile(module,'exact-work-v2-leaf-resolver','exec'),env);resolve=env['resolve_owner_leaf']
 allowed={R/n for n in owner['files']}|{SOURCE/'owned-files.json'};reads=[];writes=[];blocked=[]
 stdlib={Path(sysconfig.get_path(k)).resolve() for k in ('stdlib','platstdlib')}
 def audit(event,values):
  if event=='open':
   name,mode,flags=values
   if type(name)is int:
    if name in (0,1,2):return
    raise PermissionError('unlisted fd')
   p=Path(name).absolute();writing=(type(mode)is str and any(c in mode for c in 'wax+'))or(type(flags)is int and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
   ok=p.is_relative_to(tmp)or p.parent==OUT if writing else p.is_relative_to(tmp)or p.parent==OUT or p in allowed or(any(p.is_relative_to(s)for s in stdlib)and not{'site-packages','dist-packages'}.intersection(p.parts))
   if not ok:blocked.append(dict(event=event,path=str(p)));raise PermissionError('outside tiny fixtures/frozen SOURCE/stdlib')
   (writes if writing else reads).append(str(p))
  elif event.startswith(('socket.','subprocess.','os.exec'))or event in ('os.system','os.fork','os.posix_spawn'):blocked.append(dict(event=event));raise PermissionError('no network/process')
 sys.addaudithook(audit)
 serial=0
 def fixture():
  nonlocal serial
  serial+=1;root=tmp/str(serial);pub=root/'pub';dest=root/'dest';pub.mkdir(parents=True);dest.mkdir();(pub/'parts').mkdir()
  shutil.copyfile(SOURCE/'materialize_owner_artifacts.py',pub/'materialize_owner_artifacts.py')
  part=pub/'parts/tiny.part001';part.write_bytes(BODY);identity=pin(part)
  manifest=dict(schema='github-workspace-checkpoint/1',historical_progress_archives=[dict(superseded_at='synthetic',archive=dict(format='zip',**identity,parts=[dict(path='parts/tiny.part001',**identity)]))])
  plan=dict(schema='public-owner-artifact-relocations/1',artifacts=[dict(historical_absolute='/'+DEST,destination=DEST,source='parts/tiny.part001',identity=identity)])
  write(pub/'MANIFEST.json',manifest);write(pub/'owner-relocations.json',plan)
  recovery=dict(status='ALL_ARCHIVES_AND_LOGICAL_FILES_VERIFIED',manifest=pin(pub/'MANIFEST.json'));write(dest/'RECOVERY-RECEIPT.json',recovery)
  M=load(pub/'materialize_owner_artifacts.py','tiny_materializer_'+str(serial))
  return dict(root=root,pub=pub,dest=dest,part=part,manifest=manifest,plan=plan,recovery=recovery,M=M)
 def update_manifest(f):write(f['pub']/'MANIFEST.json',f['manifest']);f['recovery']['manifest']=pin(f['pub']/'MANIFEST.json');write(f['dest']/'RECOVERY-RECEIPT.json',f['recovery'])
 def ready_work(f):
  target=f['dest']/DEST;target.parent.mkdir(parents=True);target.write_bytes(BODY)
  receipt=dict(schema='public-owner-artifact-materialization-receipt/1',status='HISTORICAL_OWNER_ARTIFACTS_MATERIALIZED',manifest=pin(f['pub']/'MANIFEST.json'),relocations=pin(f['pub']/'owner-relocations.json'),artifacts=f['plan']['artifacts'],destination=str(f['dest']),old_cloud_files_used=[],models=0,native=0,training=0)
  write(f['dest']/'OWNER-ARTIFACTS-RECEIPT.json',receipt);return receipt
 def sync_plan(f,receipt):write(f['pub']/'owner-relocations.json',f['plan']);receipt['artifacts']=f['plan']['artifacts'];receipt['relocations']=pin(f['pub']/'owner-relocations.json');write(f['dest']/'OWNER-ARTIFACTS-RECEIPT.json',receipt)
 def materialize(f):return f['M'].materialize(f['dest'])
 def aliases(f):return W.load_aliases(f['dest'],f['recovery'],f['pub'])
 cases=[];failure=None
 def run(label,mutate,operation,reason=None):
  f=fixture()
  try:
   mutate(f);value=operation(f)
   if reason is not None:raise AssertionError('EXPECTED_REJECTION_NOT_RAISED '+label)
   cases.append(dict(label=label,positive=True,passed=True));return
  except Exception as e:
   if reason is None or str(e).startswith('EXPECTED_REJECTION_NOT_RAISED')or reason not in str(e):raise
   cases.append(dict(label=label,positive=False,rejected=True,exception=type(e).__name__,reason=str(e)))
 def positive_materializer(f):
  result=materialize(f);target=f['dest']/DEST
  assert target.read_bytes()==BODY and pin(target)==f['plan']['artifacts'][0]['identity']and stat.S_IMODE(target.stat().st_mode)==0o644
  assert result['old_cloud_files_used']==[] and result['models']==result['native']==result['training']==0
  assert not (f['root']/'ARCHIVE_BODY_MUST_NEVER_BE_EXECUTED').exists()
 def positive_work(f):
  materialize(f);a=aliases(f);assert list(a)==['/'+DEST]and a['/'+DEST]==f['dest']/DEST
  assert resolve('/'+DEST,a,f['dest']/'workspace/python-original-engine/repo')==pin(f['dest']/DEST)
 def target_exists(f):p=f['dest']/DEST;p.parent.mkdir(parents=True);p.write_bytes(b'existing')
 def receipt_exists(f):write(f['dest']/'OWNER-ARTIFACTS-RECEIPT.json',{})
 def receipt_link(f):
  p=f['dest']/'RECOVERY-RECEIPT.json';other=f['root']/'external-recovery.json';p.rename(other);p.symlink_to(other)
 def source_link(f):
  other=f['root']/'external-source';f['part'].rename(other);f['part'].symlink_to(other)
 def multi_part(f):f['manifest']['historical_progress_archives'][0]['archive']['parts'].append(dict(path='parts/empty',size=0,sha256=hashlib.sha256(b'').hexdigest()));update_manifest(f)
 def whole_mismatch(f):f['manifest']['historical_progress_archives'][0]['archive']['size']+=1;update_manifest(f)
 def m_dest_escape(f):f['plan']['artifacts'][0]['destination']='workspace/checkpoints/../../escape';f['plan']['artifacts'][0]['historical_absolute']='/'+f['plan']['artifacts'][0]['destination'];write(f['pub']/'owner-relocations.json',f['plan'])
 def m_source_escape(f):f['plan']['artifacts'][0]['source']='parts/../escape';write(f['pub']/'owner-relocations.json',f['plan'])
 def recovery_mismatch(f):f['recovery']['manifest']['sha256']='0'*64;write(f['dest']/'RECOVERY-RECEIPT.json',f['recovery'])
 def recovery_status(f):f['recovery']['status']='PENDING';write(f['dest']/'RECOVERY-RECEIPT.json',f['recovery'])
 def target_parent_link(f):p=f['dest']/'workspace';p.symlink_to(f['pub'],target_is_directory=True)
 def source_unknown(f):f['plan']['artifacts'][0]['source']='parts/not-historical';write(f['pub']/'owner-relocations.json',f['plan'])
 def work_edit(field,value):
  def edit(f):r=ready_work(f);r[field]=value;write(f['dest']/'OWNER-ARTIFACTS-RECEIPT.json',r)
  return edit
 def work_receipt_link(f):
  ready_work(f);p=f['dest']/'OWNER-ARTIFACTS-RECEIPT.json';other=f['root']/'external-artifact-receipt';p.rename(other);p.symlink_to(other)
 def work_target_bad(f):ready_work(f);(f['dest']/DEST).write_bytes(b'bad')
 def work_source_bad(f):ready_work(f);f['part'].write_bytes(b'bad')
 def work_owner_link(f):
  r=ready_work(f);repo=f['dest']/'workspace/python-original-engine/repo';repo.mkdir(parents=True);other=f['root']/'external-leaf';other.write_bytes(BODY);(repo/'leaf').symlink_to(other)
 def owner_link_operation(f):return resolve('leaf',{},f['dest']/'workspace/python-original-engine/repo')
 def unknown_absolute(f):return resolve('/workspace/checkpoints/unknown-owner.zip',aliases(f),f['dest']/'workspace/python-original-engine/repo')
 def relative_escape(f):return resolve('../escape',{},f['dest']/'workspace/python-original-engine/repo')
 def work_plan_escape(f):r=ready_work(f);f['plan']['artifacts'][0]['destination']='workspace/checkpoints/../../escape';f['plan']['artifacts'][0]['historical_absolute']='/'+f['plan']['artifacts'][0]['destination'];sync_plan(f,r)
 try:
  run('materializer-positive',lambda f:None,positive_materializer)
  run('materializer-existing-target',target_exists,materialize,'artifact destination already exists')
  run('materializer-existing-receipt',receipt_exists,materialize,'artifact receipt already exists')
  run('materializer-recovery-receipt-symlink',receipt_link,materialize,'symlink ancestor')
  run('materializer-source-symlink',source_link,materialize,'symlink ancestor')
  run('materializer-source-hash',lambda f:f['part'].write_bytes(b'bad'),materialize,'source part identity')
  run('materializer-source-not-historical',source_unknown,materialize,'artifact not exact public whole archive')
  run('materializer-multipart',multi_part,materialize,'artifact not exact public whole archive')
  run('materializer-singlepart-whole-mismatch',whole_mismatch,materialize,'single part must equal whole archive')
  run('materializer-destination-escape',m_dest_escape,materialize,'unsafe path')
  run('materializer-source-escape',m_source_escape,materialize,'unsafe path')
  run('materializer-recovery-manifest',recovery_mismatch,materialize,'recovery and current manifest mismatch')
  run('materializer-unverified-receipt',recovery_status,materialize,'verified recovery required')
  run('materializer-target-parent-symlink',target_parent_link,materialize,'symlink ancestor')
  run('work-positive-whitelist-newdest',lambda f:None,positive_work)
  run('work-receipt-mapping-pin',work_edit('relocations',dict(size=0,sha256='0'*64)),aliases,'receipt mapping identity')
  run('work-receipt-artifact-declaration',work_edit('artifacts',[]),aliases,'receipt artifact declarations')
  run('work-receipt-manifest',work_edit('manifest',dict(size=0,sha256='0'*64)),aliases,'')
  run('work-receipt-destination',work_edit('destination','/old-workspace'),aliases,'receipt destination')
  run('work-receipt-oldcloud',work_edit('old_cloud_files_used',['/old-cloud']),aliases,'')
  run('work-receipt-BOOL-models',work_edit('models',False),aliases,'')
  run('work-receipt-symlink',work_receipt_link,aliases,'symlink ancestor')
  run('work-materialized-bytes',work_target_bad,aliases,'materialized artifact identity')
  run('work-public-source-bytes',work_source_bad,aliases,'public artifact identity')
  run('work-relative-owner-symlink',work_owner_link,owner_link_operation,'symlink ancestor')
  run('work-unknown-absolute-owner',ready_work,unknown_absolute,'')
  run('work-relative-owner-escape',lambda f:None,relative_escape,'')
  run('work-plan-path-escape',work_plan_escape,aliases,'')
 except Exception as e:failure=dict(type=type(e).__name__,message=str(e),traceback=traceback.format_exc())
 report=dict(status='INDEPENDENT354_OWNER_HELPER_TINY_CONTROLS_PASS'if failure is None else'FIRST_CONTROL_FAILURE_PRESERVED',cases=cases,positive_cases=sum(x['positive']for x in cases),negative_cases=sum(not x['positive']for x in cases),failure=failure,temporary_fixture_root=str(tmp),fixture_body_bytes=len(BODY),real20MB_copies=0,real_archive_payloads_executed=0,work_full_main_executed=False,work_exact_AST_leaf_block=True,read_count=len(reads),write_count=len(writes),blocked=blocked,models=0,native=0,training=0,no_more_writes=True)
 write(OUT/'report.json',report);write(OUT/'open-audit.json',dict(reads=reads,writes=writes,blocked=blocked,bootstrap='stdlib and exact SOURCE snapshots imported before hook; all subsequent file I/O only tiny fixtures/frozen SOURCE/own outputs/stdlib'))
 write(OUT/'owned-files.json',dict(files={str(p.relative_to(R)):pin(p)for p in OUT.iterdir()if p.is_file()},no_more_writes=True))
 print(json.dumps(dict(status=report['status'],report=pin(OUT/'report.json'),owner=pin(OUT/'owned-files.json'),positive=report['positive_cases'],negative=report['negative_cases'],failure=failure)))
 return int(failure is not None)

if __name__=='__main__':raise SystemExit(main())
