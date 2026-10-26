"""Read-only historical recovery duplicate audit; writes only this new387 report directory."""
from pathlib import Path
import os,stat,json,hashlib,subprocess,collections,zipfile,time
R=Path('/workspace/python-original-engine/repo')
T=R/'data/compact-handover-validation/v2-full1801-first-001'
D=R/'data/phase387-readonly-duplicate-audit-v2'
Q=Path('/workspace/backpack-github-source-clone-20261025')
P=Path('/workspace/backpack-python-publish-20261025')
COMMIT='fdefd611a46eb67f03e88658bc740034043c1fc1'
ENV=dict(os.environ,GIT_NO_LAZY_FETCH='1',GIT_TERMINAL_PROMPT='0')
PATTERNS=[str(T).encode(),str(T.relative_to(R)).encode()]

def sha(data):return hashlib.sha256(data).hexdigest()
def pin(p):
    a=p.lstat();assert stat.S_ISREG(a.st_mode) and not p.is_symlink(),str(p)
    h=hashlib.sha256();hits=[False]*len(PATTERNS);tail=b''
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):
            h.update(block);b=tail+block
            for k,v in enumerate(PATTERNS):hits[k]|=v in b
            tail=b[-max(map(len,PATTERNS)):]
    b=p.lstat();assert (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_mode,a.st_nlink)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_mode,b.st_nlink),'unstable '+str(p)
    return dict(size=a.st_size,sha256=h.hexdigest()),dict(mode=stat.S_IMODE(a.st_mode),mtime_ns=a.st_mtime_ns,nlink=a.st_nlink,allocated_bytes=a.st_blocks*512,inode=a.st_ino,device=a.st_dev),hits

def desc(p):
    identity,_,_=pin(p);return dict(path=str(p.relative_to(R)) if p.is_relative_to(R) else str(p),**identity)
def save(n,value):
    with (D/n).open('x') as f:f.write(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')
def git_bytes(repo,path):
    return subprocess.check_output(['git','show',COMMIT+':'+path],cwd=repo,env=ENV)
def git_blob(repo,path):
    return subprocess.check_output(['git','rev-parse',COMMIT+':'+path],cwd=repo,env=ENV,text=True).strip()

def main():
    start=time.monotonic()
    for repo in (P,Q):assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,env=ENV,text=True).strip()==COMMIT
    metadata=[]
    values={}
    for name in ['MANIFEST.json','logical-files.jsonl','validation.json','VALIDATION.md','restore.py']:
        rel='recovery_checkpoint/'+name;b=git_bytes(Q,rel);values[name]=b
        local=Q/rel
        if local.exists():assert pin(local)[0]==dict(size=len(b),sha256=sha(b))
        metadata.append(dict(git_path=rel,git_blob=git_blob(Q,rel),size=len(b),sha256=sha(b),commit=COMMIT,working_checkout_present=local.exists()))
    manifest=json.loads(values['MANIFEST.json']);validation=json.loads(values['validation.json'])
    assert manifest['schema']=='github-workspace-checkpoint/1'
    assert dict(size=len(values['logical-files.jsonl']),sha256=sha(values['logical-files.jsonl']))=={k:manifest['logical_index'][k] for k in ('size','sha256')}
    assert validation['restore']['status']=='ALL_ARCHIVES_AND_LOGICAL_FILES_VERIFIED'
    assert validation['restore']['manifest']==dict(size=len(values['MANIFEST.json']),sha256=sha(values['MANIFEST.json']))
    assert validation['restore']['logical_index']==manifest['logical_index']
    assert validation['restore']['verified_logical_files']==48509 and validation['restore']['physical_readback_passes']==2
    assert validation['restore']['fresh_OS_verified'] is False and validation['restore']['full_physical_restore'] is False
    logical=[json.loads(b) for b in values['logical-files.jsonl'].splitlines()]
    assert len(logical)==len({r['path'] for r in logical})
    bypath={r['path']:r for r in logical}
    prefix='workspace/python-original-engine/repo/'+str(T.relative_to(R))+'/'
    subrows={r['path'][len(prefix):]:r for r in logical if r['path'].startswith(prefix)}
    # Protected closure: verify real current descriptor leaves and search literal dependency prefixes only.
    roots=['data/phase380-payload-source/combined-source-freeze.json','data/phase382-independent-final/owned-files.json','data/phase384-independent-readback-source/source-owner.json','data/phase384-independent-actual-readback-first-001/owned-files.json']
    protected=[];allpaths={};hits=[]
    for rel in roots:
        root=R/rel;x=json.loads(root.read_text());rows=x['files'];actual=desc(root)
        protected.append(dict(owner_or_freeze=actual,leaves=len(rows)))
        expected={'data/phase380-payload-source/combined-source-freeze.json':143,'data/phase382-independent-final/owned-files.json':394,'data/phase384-independent-readback-source/source-owner.json':19,'data/phase384-independent-actual-readback-first-001/owned-files.json':18}[rel]
        assert len(rows)==expected
        for row in rows:
            p=Path(row['path']);p=p if p.is_absolute() else R/p
            identity,metadata0,mentions=pin(p)
            assert identity=={k:row[k] for k in ('size','sha256')},'protected drift '+str(p)
            allpaths[str(p.absolute())]=dict(descriptor=row,owners=[])
            if any(mentions):hits.append(dict(consumer=str(p),owner=rel,kind='literal inspected subtree prefix; conservative dependency review'))
            if p.absolute().is_relative_to(T):hits.append(dict(consumer=str(p),owner=rel,kind='direct owned path below candidate tree'))
    freeze=json.loads((R/roots[0]).read_text());bindings=[]
    for name in ['tests/phase380_oracle_host.py','tests/phase380_oracle_storage.py','tests/phase363_oracle_process.py','tests/phase380_pool_recovery.py']:
        row=next(row for row in freeze['files'] if row['path']==name);assert desc(R/name)==row;bindings.append(row)
    save('protected-dependency-readback.json',dict(status='VERIFIED',closures=protected,four_bindings=bindings,unique_leaves=len(allpaths),literal_or_direct_dependency_hits=hits,
        method='Stream identity verification and exact full/relative subtree prefix search; no business expected interpretation',actualpool_reads=0))
    # Saved originals are hashed without extraction and remain retained.
    old={
      'base243':'python-original-engine-phase243-basic-goobert-progress-current.zip',
      'support243':'python-original-engine-phase243-local-verification-support.zip',
      'overlay343':'python-original-engine-phase343-progress-from243.zip',
      'control347':'python-original-engine-phase347-paused-control.zip',
      'progress_current':'python-original-engine-phase354-cumulative-current.zip'}
    archives=[]
    for key,name in old.items():
        p=Path('/workspace/checkpoints')/name;identity,meta,_=pin(p);expected=manifest['archives'][key]
        assert identity=={k:expected[k] for k in ('size','sha256')}
        assert validation['restore']['archives'][key]['identity']==identity
        with zipfile.ZipFile(p) as z:
            infos=z.infolist();assert len(infos)==len({i.filename for i in infos})
            detail=dict(members=len(infos),payload_member='PAYLOAD.tar.xz' if key=='base243' else None)
            if key=='base243':assert 'PAYLOAD.tar.xz' in z.namelist()
        archives.append(dict(id=key,local=desc(p),preserve=True,metadata=meta,zip_listing=detail,remote_logical_stream_verification=validation['restore']['archives'][key]))
    # Read exact Git parts directly from local committed object storage, no join/new archive or lazy network fetch.
    needed=sorted({r['archive'] for rel,r in subrows.items() if rel.startswith('restored-v5/')});git_archive=[]
    for key in needed:
        expected=manifest['archives'][key];whole=hashlib.sha256();whole_size=0;parts=[]
        for row in expected['parts']:
            path='recovery_checkpoint/'+row['path'];proc=subprocess.Popen(['git','show',COMMIT+':'+path],cwd=P,env=ENV,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            h=hashlib.sha256();size=0
            for b in iter(lambda:proc.stdout.read(1024*1024),b''):h.update(b);whole.update(b);size+=len(b)
            err=proc.stderr.read();assert proc.wait()==0,'Git part unavailable locally; retained/BLOCKED'
            assert not err,'Git part emitted stderr'
            assert dict(size=size,sha256=h.hexdigest())=={k:row[k] for k in ('size','sha256')}
            whole_size+=size;parts.append(dict(git_path=path,git_blob=git_blob(P,path),**row))
        assert dict(size=whole_size,sha256=whole.hexdigest())=={k:expected[k] for k in ('size','sha256')}
        git_archive.append(dict(id=key,commit=COMMIT,format=expected['format'],size=whole_size,sha256=whole.hexdigest(),parts=parts,
            local_objects_only=True,materialized_archive=False,remote_verification_scope='Existing validation.json full logical stream verification; active physical restore omitted inactive historical tree'))
    save('recovery-provenance.json',dict(commit=COMMIT,metadata=metadata,archives=archives,git_archives=git_archive,
        remote_verification_receipt=dict(git_path='recovery_checkpoint/validation.json',identity=dict(size=len(values['validation.json']),sha256=sha(values['validation.json'])),
         status=validation['restore']['status'],profile=validation['restore']['profile'],verified_logical_files=validation['restore']['verified_logical_files'],
         verified_logical_bytes=validation['restore']['verified_logical_bytes'],full_physical_restore=False,fresh_OS_verified=False),
        source_tree_logical_rows=len(subrows),old_cloud_files_used_by_historical_remote_restore=validation.get('old_cloud_files_required_for_supported_offline_continuation')))
    inventory=[];proposed=[];retained=[];dirs=[]
    for base,children,names in os.walk(T,followlinks=False):
        for name in children+names:
            p=Path(base)/name;rel=str(p.relative_to(T));s=p.lstat()
            if stat.S_ISDIR(s.st_mode):dirs.append(dict(path=rel,mode=stat.S_IMODE(s.st_mode),mtime_ns=s.st_mtime_ns,allocated_bytes=s.st_blocks*512));continue
            if not stat.S_ISREG(s.st_mode):
                row=dict(path=rel,kind='symlink' if stat.S_ISLNK(s.st_mode) else 'special',reason='nonordinary, retained');inventory.append(row);retained.append(row);continue
            identity,meta,_=pin(p);row=dict(path=rel,kind='file',**identity,metadata=meta);inventory.append(row)
            recovery=subrows.get(rel)
            reasons=[]
            if not rel.startswith('restored-v5/'):reasons.append('ORIGINAL_ADJACENT_REPORT_SOURCE_OR_EVIDENCE_ALWAYS_RETAINED')
            if s.st_nlink!=1:reasons.append('HARDLINK_OR_SHARED_STORAGE_RETAINED')
            if recovery is None:reasons.append('NO_EXACT_LOGICAL_PATH')
            elif identity!={k:recovery[k] for k in ('size','sha256')}:reasons.append('SAME_PATH_BYTE_MISMATCH_PRIVATE_OR_UNPROVEN_RETAINED')
            elif recovery['archive'] not in needed:reasons.append('RECOVERY_ARCHIVE_NOT_VERIFIED_BY_THIS_AUDIT')
            if str(p.absolute()) in allpaths:reasons.append('CURRENT_PROTECTED_OWNER_DIRECT_DEPENDENCY')
            if hits:reasons.append('UNRESOLVED_LITERAL_DEPENDENCY_RETAINED_CONSERVATIVELY')
            if reasons:retained.append(dict(**row,reasons=reasons,recovery_row=recovery))
            else:proposed.append(dict(**row,recovery=dict(commit=COMMIT,git_manifest_path='recovery_checkpoint/MANIFEST.json',git_index_path='recovery_checkpoint/logical-files.jsonl',
                archive=recovery['archive'],format=manifest['archives'][recovery['archive']]['format'],archive_size=manifest['archives'][recovery['archive']]['size'],archive_sha256=manifest['archives'][recovery['archive']]['sha256'],
                parts_ref='recovery-provenance.json/git_archives/'+recovery['archive'],container_member='PAYLOAD.tar.xz' if manifest['archives'][recovery['archive']]['format']=='compact_zip_tar_xz' else None,member=recovery['member'],logical_path=recovery['path'],active=recovery['active'],restored_mode=recovery['mode'])))
    # Prove this is only the derived tree from the old restore, not the surrounding independent first-failure evidence.
    stdout=json.loads((T/'restore-stdout.json').read_text());report=json.loads((T/'report.json').read_text())
    derived=[r for r in inventory if r['path'].startswith('restored-v5/')]
    assert len(derived)==stdout['source_files']==1801
    assert sum(r.get('size',0) for r in derived)==stdout['source_bytes']==1001970711
    assert stdout['status']=='RESTORED_ALL_PHYSICAL_SHA_PASS' and stdout['content_executed'] is False
    assert stdout['destination']==str(T/'restored-v5') and report['failed_own_tree_retained']==str(T/'restored-v5')
    # Original HANDOVER manifest gives an independent old generation identity for1800 leaves (manifest itself excluded).
    hmanifest=json.loads((T/'restored-v5/HANDOVER-MANIFEST.json').read_text());derived_by={r['path'][len('restored-v5/'):]:r for r in derived}
    assert len(hmanifest['files'])==1800
    for r in hmanifest['files']:assert {k:derived_by[r['path']][k] for k in ('size','sha256')}=={k:r[k] for k in ('size','sha256')}
    save('inventory.json',dict(root=str(T),files=inventory,directories=dirs,source_stat_stability_checked=True))
    save('proposed-release-files.json',dict(status='PROPOSED_ONLY_ROOT_APPROVAL_REQUIRED',files=proposed,deleted=0))
    save('retained-and-excluded.json',dict(files=retained,always_preserved_archives=[a['local'] for a in archives],
       directory_policy='All directories and adjacent reports remain; Root may later remove only explicitly listed ordinary files',
       note='Unmatched/private-redacted/SHA-different files are retained; no sanitized equality assumption.350unique outputs are outside scope and never candidates.'))
    before_free=os.statvfs(R);free=before_free.f_bavail*before_free.f_frsize
    summary=dict(schema='phase387-readonly-working-copy-audit/1',status='EXACT_DERIVED_DUPLICATES_PROPOSED_NO_CLEANUP' if proposed else 'NO_RELEASE_PROVED',
        root=str(T),git_commit=COMMIT,original_failure_report_status=report['status'],original_restore_status=stdout['status'],
        original_report_retained=True,derived_files=len(derived),derived_bytes=sum(r.get('size',0) for r in derived),
        proposed_files=len(proposed),proposed_logical_bytes=sum(r['size'] for r in proposed),proposed_allocated_bytes=sum(r['metadata']['allocated_bytes'] for r in proposed),
        retained_files=len(retained),retained_bytes=sum(r.get('size',0) for r in retained),dependency_hits=len(hits),
        source_scope='Only restored-v5 ordinary exact files; original first-failure reports and source snapshot retained',
        current_free_bytes=free,next_launch_required_bytes=5905580032,shortfall_before_any_cleanup=max(0,5905580032-free),
        note='Allocated bytes are measured st_blocks; future realized free bytes require Root cleanup and fresh df, not claimed here. Existing remote verification streamed all archive logical files; inactive historical tree was not physically materialized by that remote active profile.',
        deletes=0,moves=0,archive_extractions=0,new_restore_materializations=0,network_fetches=0,actualpool_reads=0,Game=0,Godot=0,models=0,
        elapsed_seconds=time.monotonic()-start,no_more_writes=True)
    save('summary.json',summary)
    # Read every original inspected file once more, proving no concurrent byte or metadata drift.
    for row in inventory:
        if row['kind']=='file':
            ident,meta,_=pin(T/row['path']);assert ident=={k:row[k] for k in ('size','sha256')} and meta==row['metadata']
    first=R/'data/phase387-readonly-duplicate-audit/owned-files.json'
    save('first-conservative-report-correction.json',dict(first_owner=desc(first),reason='Initial report verified candidate parts only for base243; exact final logical rows use overlay343. V2 follows each actual row archive and verifies its committed parts; no candidate bytes changed.',first_report_preserved=True))
    own=[R/'docs/phase387_historical_restore_duplicate_resource_audit_spec.md']+sorted(p for p in D.iterdir() if p.is_file())+[first]+[R/r['path'] for r in json.loads(first.read_text())['files']]
    own=sorted(set(own))
    rows=[desc(p) for p in own];save('owned-files.json',dict(schema='phase387-readonly-audit-owner/1',files=rows,scope='Audit proposal only; no deletion authorization or independent scientific acceptance'))
    for row in rows:assert desc(R/row['path'])==row
    print(json.dumps(dict(summary=summary,owner=desc(D/'owned-files.json'),owned_leaves=len(rows),owned_bytes=sum(r['size'] for r in rows))))
if __name__=='__main__':main()
