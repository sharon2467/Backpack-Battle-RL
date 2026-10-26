"""SOURCE extension merged into a new363-derived storage module, never run here."""
MAX_INSTALL_PAYLOADS = 78
MAX_INSTALL_BYTES = 807199


def _identity(value):
    if (type(value) is not dict or set(value)!={'size','sha256'} or type(value['size']) is not int or value['size']<0
            or type(value['sha256']) is not str or len(value['sha256'])!=64 or any(x not in '0123456789abcdef' for x in value['sha256'])):
        raise ValueError('strict payload sizeINT/SHA identity')
    return value


def _source_descriptor(row):
    if type(row) is not dict or set(row)!={'path','size','sha256'} or type(row['path']) is not str:
        raise ValueError('exact source-root payload descriptor')
    _identity({k:row[k] for k in ('size','sha256')})
    return row


def _source_signature(info):
    return (info.st_dev,info.st_ino,info.st_mode,info.st_nlink,info.st_size,info.st_mtime_ns,info.st_ctime_ns)


def _read_source(source_root,row,retain):
    _source_descriptor(row); root=directory(source_root); path=member(root,row['path']); before=regular_target(path)
    if before.st_size!=row['size']: raise ValueError('payload source size drift')
    if retain and row['size']>MAX_INSTALL_BYTES: raise ValueError('payload exceeds exact frozen install preload bound')
    digest=hashlib.sha256(); count=0; blocks=[]
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
    with os.fdopen(fd,'rb') as stream:
        opened=os.fstat(stream.fileno())
        while True:
            block=stream.read(65536)
            if not block: break
            count+=len(block)
            if count>row['size']: raise ValueError('payload grew during source read')
            digest.update(block)
            if retain: blocks.append(block)
        after=os.fstat(stream.fileno())
    if (_source_signature(before)!=_source_signature(opened) or _source_signature(before)!=_source_signature(after)
            or _source_signature(before)!=_source_signature(regular_target(path))):
        raise ValueError('payload source changed during read')
    if dict(size=count,sha256=digest.hexdigest())!={k:row[k] for k in ('size','sha256')}:
        raise ValueError('payload source hash drift')
    return path,b''.join(blocks) if retain else None


def check_source_descriptor(source_root,row):
    """Public streaming identity check; no mutation and no caller proof flag."""
    return _read_source(source_root,row,False)[0]


def read_source_payload(source_root,row):
    """Finite SOURCE preload only, not a new capture/runtime source reader."""
    return _read_source(source_root,row,True)[1]


def preflight_install_payloads(source_root,project,source_freeze,artifacts):
    source_root,project=directory(source_root),directory(project)
    if source_root==project or source_root.is_relative_to(project) or project.is_relative_to(source_root):
        raise ValueError('SOURCE and mutable project roots must be disjoint')
    if type(artifacts) is not dict or type(source_freeze.get('artifacts')) is not dict or artifacts!=source_freeze['artifacts']:
        raise ValueError('artifact descriptors must equal explicit frozen artifact set')
    paths=source_freeze.get('paths')
    if type(paths) is not dict or not paths: raise ValueError('nonempty exact frozen patch set')
    declared={}
    for row in source_freeze['files']:
        _source_descriptor(row)
        if row['path'] in declared and declared[row['path']]!=row: raise ValueError('conflicting declared source identity')
        declared[row['path']]=row
    todo=[]; names=set()
    for name,row in paths.items():
        target=member(project,name); expected=row['before']
        if expected is not None: _identity(expected)
        info=regular_target(target,absent=expected is None)
        if expected is None and info is not None: raise ValueError('new source preimage unexpectedly exists')
        if expected is not None and pin(target)!=expected: raise ValueError('strict original source preimage')
        payload=dict(path=row['after_path'],**_identity(row['after']))
        todo.append(dict(name=name,target=target,descriptor=payload,before=None if info is None else dict(identity=pin(target),mode=stat.S_IMODE(info.st_mode),mtime_ns=info.st_mtime_ns)))
        names.add(name)
    for name,payload in artifacts.items():
        if name in names: raise ValueError('overlapping source/artifact destination')
        names.add(name); target=member(project,name); info=regular_target(target,absent=True)
        todo.append(dict(name=name,target=target,descriptor=_source_descriptor(payload),before=None if info is None else dict(identity=pin(target),mode=stat.S_IMODE(info.st_mode),mtime_ns=info.st_mtime_ns)))
    if len(todo)>MAX_INSTALL_PAYLOADS or sum(row['descriptor']['size'] for row in todo)>MAX_INSTALL_BYTES:
        raise ValueError('exact frozen SOURCE install corpus preload bound')
    for row in todo:
        payload=row['descriptor']
        if declared.get(payload['path'])!=payload: raise ValueError('install source is not the frozen descriptor')
        row['raw']=read_source_payload(source_root,payload)
    return todo


def install(source_root, project, source_freeze, artifacts, backup):
    source_root, project = directory(source_root), directory(project)
    backup = Path(backup).absolute()
    if backup.exists() or backup.is_symlink(): raise ValueError('preimage backup must be new')
    directory(backup.parent)
    if backup.is_relative_to(project) or backup==project: raise ValueError('backup outside project')
    # No backup directory, backup byte or target mutation before ALL payload/target checks.
    todo=preflight_install_payloads(source_root,project,source_freeze,artifacts)
    backup.mkdir()
    journal = []
    for i, row in enumerate(todo):
        target=row['target']; old=row['before']; current=regular_target(target,absent=old is None)
        if old is None:
            if current is not None: raise ValueError('new target appeared before backup')
        elif pin(target)!=old['identity'] or stat.S_IMODE(current.st_mode)!=old['mode'] or current.st_mtime_ns!=old['mtime_ns']:
            raise ValueError('preflight target drift before backup')
        if old is not None:
            with (backup / str(i)).open('xb') as stream: stream.write(target.read_bytes()); stream.flush(); os.fsync(stream.fileno())
            if pin(backup / str(i)) != old['identity']: raise ValueError('preimage readback')
        journal.append(dict(path=row['name'],backup=str(i) if old else None,before=old,after={k:row['descriptor'][k] for k in ('size','sha256')}))
    write_new(backup / 'preimages.json', journal); sync(backup)
    for entry,row in zip(journal,todo):
        # Immutable bytes were already checked before backup; original atomic writer remains intact.
        atomic_image(row['target'],row['raw'],entry['before'])
        if pin(row['target'])!=entry['after']: raise ValueError('installed after bytes')
    sync(project)
    return journal
