from pathlib import Path
import json,hashlib,zipfile,stat,shutil,subprocess
r=Path('/workspace/python-original-engine/repo');audit=r/'data/phase387-readonly-duplicate-audit-v2';d=r/'data/phase389-root-derived-workcopy-release';assert not d.exists();d.mkdir()
def sha(p):
 with Path(p).open('rb') as s:return hashlib.file_digest(s,'sha256').hexdigest()
def save(n,v):(d/n).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def check(p,a):
 assert p.is_file() and not p.is_symlink() and p.stat().st_nlink==1,str(p)
 assert p.stat().st_size==a['size'] and sha(p)==a['sha256'],str(p)
owner=json.loads((audit/'owned-files.json').read_text())
for a in owner['files']:check(r/a['path'],a)
summary=json.loads((audit/'summary.json').read_text());root=Path(summary['root']);copy=root/'restored-v5';rows=json.loads((audit/'proposed-release-files.json').read_text())['files'];keep=json.loads((audit/'retained-and-excluded.json').read_text());provenance=json.loads((audit/'recovery-provenance.json').read_text());archive=Path('/workspace/checkpoints/python-original-engine-phase343-progress-from243.zip')
assert len(rows)==1801 and sum(a['size'] for a in rows)==1001970711 and summary['dependency_hits']==0
assert root==r/'data/compact-handover-validation/v2-full1801-first-001' and not any(p.is_symlink() for p in (copy,*copy.parents))
assert {str(p.relative_to(root)) for p in copy.rglob('*') if p.is_file() or p.is_symlink()}=={a['path'] for a in rows}
for a in keep['always_preserved_archives']:check(Path(a['path']),a)
for a in keep['files']:check(root/a['path'],a)
active=[];freeze=json.loads((r/'data/phase380-payload-source/combined-source-freeze.json').read_text());active+=freeze['files']+[freeze[k] for k in ['collector','schema_module','active_source_tuple','native_source_origin']]
for n in ['data/phase382-independent-final/owned-files.json','data/phase384-independent-readback-source/source-owner.json','data/phase384-independent-actual-readback-first-001/owned-files.json']:active+=json.loads((r/n).read_text())['files']
for a in active:check(r/a['path'],a);assert not (r/a['path']).is_relative_to(copy)
assert sha(archive)=='1cc74608955df9ea7169f36b018565871d99ed9b5c88529eb416b5f08704f044'
with zipfile.ZipFile(archive) as z:
 for a in rows:
  rel=Path(a['path']);assert not rel.is_absolute() and '..' not in rel.parts and rel.parts[0]=='restored-v5';p=root/rel;assert not any(x.is_symlink() for x in (p,*p.parents));check(p,a);info=p.stat();m=a['metadata'];assert (info.st_dev,info.st_ino,stat.S_IMODE(info.st_mode),info.st_mtime_ns,info.st_nlink)==(m['device'],m['inode'],m['mode'],m['mtime_ns'],m['nlink'])
  rec=a['recovery'];assert rec['archive']=='overlay343' and rec['commit']=='fdefd611a46eb67f03e88658bc740034043c1fc1';zi=z.getinfo(rec['member']);assert zi.file_size==a['size']
  with z.open(zi) as s:assert hashlib.file_digest(s,'sha256').hexdigest()==a['sha256']
pre=dict(status='ROOT_FRESH_ALL1801_DISK_AND_EXACT_ZIP_MEMBER_SHA_CRC_PASS',candidates=1801,bytes=1001970711,protected_archives=5,adjacent_retained=len(keep['files']),active_descriptors=len(active),active_dependency_hits=0,plan_sha256=sha(audit/'proposed-release-files.json'),archive_sha256=sha(archive),before_free=shutil.disk_usage('/workspace').free);save('preflight.json',pre)
removed=[]
try:
 for a in rows:
  p=root/a['path'];s=p.lstat();m=a['metadata'];assert stat.S_ISREG(s.st_mode) and (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_nlink)==(m['device'],m['inode'],a['size'],m['mtime_ns'],1);p.unlink();removed.append(a['path'])
 for a in keep['files']:check(root/a['path'],a)
 for a in keep['always_preserved_archives']:check(Path(a['path']),a)
 assert all(not (root/a['path']).exists() for a in rows) and copy.is_dir()
 after=shutil.disk_usage('/workspace').free;save('release-receipt.json',dict(status='VERIFIED_DERIVED_WORKING_FILES_RELEASED_ORIGINAL_REPORTS_AND_ARCHIVES_RETAINED',removed_files=len(removed),logical_bytes=1001970711,measured_free_before=pre['before_free'],measured_free_after=after,measured_free_delta=after-pre['before_free'],removed_paths=removed,preserved_adjacent=len(keep['files']),preserved_archives=5,directories_removed=0,Game=0,models=0,pool_operations=0));print(json.dumps(dict(status='RELEASED',files=len(removed),free=after,delta=after-pre['before_free'])))
except BaseException as e:save('first-failure.json',dict(error=repr(e),removed=removed));raise
