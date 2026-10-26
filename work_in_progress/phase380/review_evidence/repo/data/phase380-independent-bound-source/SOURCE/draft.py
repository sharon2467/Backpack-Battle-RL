"""Compile-only finite-control draft. No380 import or executable main binding."""
from pathlib import Path
import copy
import hashlib
import json
import os
import stat

PREPARATION_CONTRACT='data/phase380-independent-preparation/contract.json'
FIXED_METADATA_NS=1700000000000000000
ALLOWED_ABSENT_RECOVERY_PATHS=frozenset({'.native-random-observer-disposable','native_random_observer_sink_v7.gd'})

def identity(path):
    h=hashlib.sha256();size=0
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(65536),b''):h.update(block);size+=len(block)
    return dict(size=size,sha256=h.hexdigest())

def descriptor(root,path):
    return dict(path=Path(path).relative_to(root).as_posix(),**identity(path))

def save_exclusive(path,value):
    with Path(path).open('x') as stream:
        json.dump(value,stream,indent=2,sort_keys=True,allow_nan=False);stream.write('\n')
        stream.flush();os.fsync(stream.fileno())

def owned_child(root,name):
    relative=Path(name)
    if relative.is_absolute() or relative.as_posix()!=name or any(part in ('','.','..') for part in name.split('/')):
        raise ValueError('fixture mutation only canonical relative name')
    result=Path(root)/relative
    if result!=root and root not in result.parents:raise ValueError('outside owned fixture')
    return result

def write_fixture_leaf(root,name,data,mode=0o600):
    path=owned_child(root,name);path.parent.mkdir(parents=True,exist_ok=True)
    if any(p.is_symlink() for p in (path,*path.parents)):raise ValueError('linked fixture path')
    with path.open('xb') as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())
    os.chmod(path,mode);os.utime(path,ns=(FIXED_METADATA_NS,FIXED_METADATA_NS))
    return path

def inventory_tiny(root):
    """Observe links without following; reject nonfixture roots at call site."""
    root=Path(root)
    if not root.exists() and not root.is_symlink():return dict(exists=False,entries=[])
    rows=[]
    def visit(path):
        before=path.lstat();row=dict(path='.' if path==root else path.relative_to(root).as_posix(),mode=stat.S_IMODE(before.st_mode),mtime_ns=before.st_mtime_ns,nlink=before.st_nlink)
        if stat.S_ISDIR(before.st_mode):
            row['kind']='directory';rows.append(row)
            for child in sorted(path.iterdir()):visit(child)
        elif stat.S_ISREG(before.st_mode):
            row.update(kind='file',**identity(path));rows.append(row)
        elif stat.S_ISLNK(before.st_mode):
            row.update(kind='symlink',target=os.readlink(path));rows.append(row)
        else:
            row.update(kind='special',type_bits=stat.S_IFMT(before.st_mode));rows.append(row)
    visit(root);return dict(exists=True,entries=rows)

def build_install_fixture(parent,name):
    """Future owned tiny source/project only; text payloads are not a Game."""
    parent=Path(parent)
    if not parent.is_dir() or any(p.is_symlink() for p in (parent,*parent.parents)):
        raise ValueError('existing unlinked owned test parent')
    root=owned_child(parent,name);root.mkdir(exist_ok=False)
    source=root/'source';project=root/'project';source.mkdir();project.mkdir()
    before=b'# tiny independent source preimage; no native code executed\n'
    after=b'# tiny independent source replacement; no native code executed\n'
    original=write_fixture_leaf(project,'Core/A.gd',before)
    patch=write_fixture_leaf(source,'frozen/after/Core/A.gd',after)
    sink=write_fixture_leaf(source,'frozen/after/sink.gd',b'# tiny new sink text\n')
    collector=write_fixture_leaf(source,'reused/origin/collector.gd',b'# tiny reused collector text\n')
    config=write_fixture_leaf(source,'fixed/native_capture_config.json',b'{"synthetic_fixture":true}\n')
    marker=write_fixture_leaf(source,'fixed/disposable-marker.txt',b'disposable-observation-copy\n')
    player=write_fixture_leaf(source,'fixed/custom_player.json',b'{"synthetic_player":true}\n')
    opponent=write_fixture_leaf(source,'fixed/custom_opponent.json',b'{"synthetic_opponent":true}\n')
    write_fixture_leaf(project,'native_combat_capture.gd',b'# tiny previous collector\n')
    write_fixture_leaf(project,'native_capture_config.json',b'{"previous":true}\n')
    write_fixture_leaf(root,'state.json',b'{"status":"failed","scope":"owned-tinyFS-unit"}\n')
    (source/'new-source').mkdir()
    assert not (source/'new-source/collector.gd').exists()
    freeze=dict(paths={
        'Core/A.gd':dict(before=identity(original),after=identity(patch),after_path=patch.relative_to(source).as_posix()),
        'native_random_observer_sink_v7.gd':dict(before=None,after=identity(sink),after_path=sink.relative_to(source).as_posix())},
        collector=descriptor(source,collector))
    artifacts={'native_combat_capture.gd':descriptor(source,collector),
               'native_capture_config.json':descriptor(source,config),
               '.native-random-observer-disposable':descriptor(source,marker)}
    input_authorities={p.name:descriptor(source,p) for p in (player,opponent,config)}
    metadata={name:dict(mode=stat.S_IMODE(owned_child(project,name).stat().st_mode),mtime_ns=owned_child(project,name).stat().st_mtime_ns)
              for name in ('Core/A.gd','native_combat_capture.gd','native_capture_config.json')}
    metadata.update({name:dict(mode=0o644,mtime_ns=0) for name in ('native_random_observer_sink_v7.gd','.native-random-observer-disposable')})
    return dict(root=root,source=source,project=project,backup=root/'backups',state=root/'state.json',expected_metadata=metadata,
                freeze=freeze,artifacts=artifacts,input_authorities=input_authorities,
                expected_bytes={'Core/A.gd':after,'native_random_observer_sink_v7.gd':sink.read_bytes(),
                    'native_combat_capture.gd':collector.read_bytes(),'native_capture_config.json':config.read_bytes(),
                    '.native-random-observer-disposable':marker.read_bytes()},
                label='SYNTHETIC_FS_ONLY_NOT_GAME_NOT_NATIVE_CONFIG_NOT_ACCEPTED_SOURCE_ROOT')

def mutable_payload(fixture,descriptor_row):
    """Never accepts real repo or live pool roots for a negative mutation."""
    source=fixture['root']/'source'
    if source!=fixture['source']:raise ValueError('owned fixture source mismatch')
    return owned_child(source,descriptor_row['path'])

def mutate_artifact(fixture,name,variant):
    """One fresh fixture per variant. Used only after future exact binding."""
    row=fixture['artifacts'][name];path=mutable_payload(fixture,row)
    if variant=='missing':path.unlink()
    elif variant=='wronghash':
        path.write_bytes(path.read_bytes()+b'changed\n')
    elif variant=='wrongsize':row['size']+=1
    elif variant=='boolsize':row['size']=True
    elif variant=='directory':path.unlink();path.mkdir()
    elif variant in ('symlink','hardlink'):
        original=path.with_name(path.name+'.original');path.rename(original)
        if variant=='symlink':path.symlink_to(original.name)
        else:os.link(original,path)
    elif variant=='unsafe':row['path']='../outside-source'
    else:raise ValueError('unknown finite mutation')

def observed_targets(fixture):
    return dict(project=inventory_tiny(fixture['project']),backup=inventory_tiny(fixture['backup']),state=identity(fixture['state']))

def record_one_case(output,case_id,fixture,operation,expect_accept,expected_exceptions):
    """Generic one-call journal; operation must be a frozen real API binding.

    No callback supplied during this preparation. A later concrete checker must
    pin the module and direct function, not provide a fake validation function.
    """
    output=Path(output);output.mkdir(exist_ok=False)
    before=observed_targets(fixture);save_exclusive(output/'before.json',before)
    try:
        returned=operation()
    except expected_exceptions as exc:
        outcome=dict(accepted=False,exception=type(exc).__name__,message=str(exc))
        if expect_accept:outcome['unexpected']=True
    except BaseException as exc:
        outcome=dict(accepted=False,unexpected=True,exception=type(exc).__name__,message=str(exc))
    else:
        outcome=dict(accepted=True,return_type=type(returned).__name__)
        if not expect_accept:outcome['unexpected']=True
    after=observed_targets(fixture);save_exclusive(output/'after.json',after)
    if not expect_accept and before!=after:outcome['unexpected_target_mutation']=True
    if not expect_accept and fixture['backup'].exists():outcome['unexpected_backup_created']=True
    outcome.update(case_id=case_id,public_api_calls=1,original_Game=0,actual_pool_writes=0,models=0)
    save_exclusive(output/'result.json',outcome)
    return outcome

def call_public_install(real_storage_module,fixture):
    """379 expected signature only; bind against real freeze before use."""
    return real_storage_module.install(fixture['source'],fixture['project'],fixture['freeze'],
                                       fixture['artifacts'],fixture['backup'])

def verify_install_success(fixture,journal):
    """Outcome oracle is presealed expected fixture bytes, not SUT assertion."""
    if not (fixture['backup']/'preimages.json').is_file():raise AssertionError('missing complete journal')
    observed=json.loads((fixture['backup']/'preimages.json').read_text())
    if observed!=journal:raise AssertionError('public return/journal mismatch')
    if {row['path'] for row in journal}!=set(fixture['expected_bytes']):raise AssertionError('journal destination closure')
    for name,expected in fixture['expected_bytes'].items():
        path=owned_child(fixture['project'],name)
        if path.read_bytes()!=expected:raise AssertionError('installed unexpected bytes')
        meta=fixture['expected_metadata'][name];observed=path.stat()
        if stat.S_IMODE(observed.st_mode)!=meta['mode'] or observed.st_mtime_ns!=meta['mtime_ns']:
            raise AssertionError('installed metadata differs from conserved writer fixture contract')
    if json.loads(fixture['state'].read_text())['status']!='failed':raise AssertionError('tiny state changed')
    return dict(complete_journal=True,expected_bytes_exact=True,tiny_failed_state_kept=True,
                native_capture_accepted=False,original_Game=0)

PARTIAL_EVIDENCE_DEFINITION={
    'schema_binding':'PENDING_ACTUAL380_FREEZE',
    'required_equalities':['current=preserved=reset.after','target=reset.before=previous.project=old026',
                           'exact75rawbackup prefix; completepreimages.json absent'],
    'allowed_before_null':sorted(ALLOWED_ABSENT_RECOVERY_PATHS),
    'target_metadata_source':'complete oldtarget manifest, never guessed numeric backup metadata',
    'payload_source':'verified old patched-after/bundle/previous-source backup image, never raw original-before substitution',
    'success_requires':'real tiny two-file creations + complete target bytes/mode/mtime readback + unchanged failed state',
    'early_READY':'requires separate owned independent report/Root gate; no fabricated accepted receipt',
    'NOT_IMPLEMENTED_HERE':'No fake partial evidence builder, recovery routine or Root validator.'}

def main():
    raise SystemExit('PREPARATION_ONLY: no frozen380 modules/API bindings or execution release; do not run this draft')

if __name__=='__main__':main()
