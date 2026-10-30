"""One fixed restoration writer. Never writes state.json or READY."""
from pathlib import Path
import argparse
import fcntl
import hashlib
import json
import os
import re
import signal
import stat
import sys
import time
import traceback
import types

ROOT = Path(__file__).resolve().parents[1]
NATIVE = Path('/workspace/native-combat-20261013')
POOL = NATIVE / 'pool'
RUN = NATIVE / 'runs/original029-whelp-family-A-single-001'
PREVIOUS = None
CASE = 'NATIVE-029-WHELP-FAMILY-A'
FREEZE = {'path': 'data/phase508-case029-host-restore-source/combined-source-freeze.json', 'size': 62542, 'sha256': '3e668a3714183a6d371eb14ef019d4a1fc7dbdf2897f80300989d760df285199'}
SOURCES = {'compaction': {'path': 'tests/native_run_compaction.py', 'size': 27304, 'sha256': '829475e4ba5ee4a3ce3e3ce7a1d600b53cfa6ab243020a8528b6758675e6c260'}, 'storage': {'path': 'tests/phase508_oracle_storage.py', 'size': 21560, 'sha256': '77719d1146c06205e2562756b220a07070b75c61313dc39632ab171233937019'}}
CONTROLS = RUN / 'output/predecessor-control-preimages'
PATCH = RUN / 'output/previous-source-preimages'
JOURNAL = RUN / 'output/source-preimages'
BUNDLE = None
EVIDENCE_PATHS = {}
MARKER = '.native-random-observer-disposable'


def require(value, message):
    if not value:
        raise ValueError(message)


def signature(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def stable(path):
    path = Path(path).absolute()
    require(not any(x.is_symlink() for x in (path, *path.parents)), 'linked image path')
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and not stat.S_IMODE(before.st_mode) & 0o7000,
            'ordinary single-link image')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as stream:
        opened = os.fstat(stream.fileno())
        raw = stream.read()
        after = os.fstat(stream.fileno())
    require(signature(before) == signature(opened) == signature(after) == signature(path.lstat()),
            'image changed during read: ' + str(path))
    return {'raw': raw, 'identity': {'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()},
            'mode': stat.S_IMODE(before.st_mode), 'mtime_ns': before.st_mtime_ns,
            'signature': signature(before)}


def path_of(value):
    require(type(value) is str and bool(value), 'explicit path string')
    path = Path(value)
    path = path if path.is_absolute() else ROOT / path
    require(path.absolute() == path and '..' not in path.parts, 'canonical path')
    return path


def descriptor(row):
    require(type(row) is dict and set(row) == {'path', 'size', 'sha256'}, 'closed descriptor')
    require(type(row['size']) is int and row['size'] >= 0 and type(row['sha256']) is str
            and re.fullmatch('[0-9a-f]{64}', row['sha256']), 'descriptor types')
    image = stable(path_of(row['path']))
    require(image['identity'] == {k: row[k] for k in ('size', 'sha256')}, 'descriptor drift: ' + row['path'])
    return image['raw']


def decoded(raw):
    def pairs(rows):
        result = {}
        for key, value in rows:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    def invalid(value):
        raise ValueError('nonfinite JSON: ' + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)


def equal(actual, expected, label):
    # These JSON/physical records use exact values and typed metadata, never tolerant numbers.
    require(type(actual) is type(expected) and actual == expected, label)


def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())


def load_modules():
    raw = {key: descriptor(row) for key, row in SOURCES.items()}
    modules = {}
    for key in ('compaction', 'storage'):
        module = types.ModuleType('_phase508_restore_' + key)
        module.__file__ = str(path_of(SOURCES[key]['path']))
        if key == 'storage':
            prior = sys.modules.get('native_run_compaction')
            sys.modules['native_run_compaction'] = modules['compaction']
        try:
            exec(compile(raw[key], module.__file__, 'exec'), module.__dict__)
        finally:
            if key == 'storage':
                if prior is None:
                    sys.modules.pop('native_run_compaction', None)
                else:
                    sys.modules['native_run_compaction'] = prior
        modules[key] = module
    return modules['compaction'], modules['storage']


def validate_request(request):
    global PREVIOUS,BUNDLE,EVIDENCE_PATHS
    require(type(request) is dict and set(request)=={'schema','case_id','previous_run','writer','source_freeze','evidence','root_restore_authorized'},'closed case029 restore request')
    require(request['schema']=='phase508-fixed-predecessor-restore-request/1' and request['case_id']==CASE
            and request['root_restore_authorized'] is True,'explicit new Root restoration authorization')
    previous=path_of(request['previous_run'])
    require(previous.is_absolute() and previous.parent==RUN.parent and previous!=RUN,'fixed runs root and distinct actual predecessor')
    require(PREVIOUS is None or PREVIOUS==previous,'one fixed predecessor binding per invocation')
    PREVIOUS=previous;BUNDLE=PREVIOUS/'output/compaction'
    EVIDENCE_PATHS={'controls_manifest':CONTROLS/'manifest.json','patch_inventory':PATCH/'inventory.json',
        'install_journal':JOURNAL/'preimages.json','pool_before':RUN/'output/pool-before.json',
        'previous_bundle_manifest':BUNDLE/'bundle-manifest.json','previous_proof':BUNDLE/'pool-roundtrip.json',
        'previous_provenance':PREVIOUS/'output/pool-provenance.json','previous_project':BUNDLE/'project-files.json',
        'previous_baseline':BUNDLE/'baseline-files.json','previous_staged':BUNDLE/'staged-inputs.json',
        'previous_host_manifest':PREVIOUS/'output/host_manifest.json','pending_state':POOL/'state.json'}
    require(path_of(request['writer']['path'])==Path(__file__).absolute(),'exact new writer path')
    descriptor(request['writer']);equal(request['source_freeze'],FREEZE,'exact508 host Source freeze')
    freeze=decoded(descriptor(FREEZE))
    require(type(request['evidence']) is dict and set(request['evidence'])==set(EVIDENCE_PATHS),'fixed evidence keys')
    for key,path in EVIDENCE_PATHS.items():require(path_of(request['evidence'][key]['path'])==path,'fixed actual evidence path '+key)
    return freeze


def image_record(image):
    return {key: image[key] for key in ('identity', 'mode', 'mtime_ns')}


def row_record(row):
    return {'identity': {key: row[key] for key in ('size', 'sha256')},
            'mode': row['mode'], 'mtime_ns': row['mtime_ns']}


def check_image(image, row, label, metadata=True):
    equal(image['identity'], {key: row[key] for key in ('size', 'sha256')}, label + ' bytes')
    if metadata:
        equal([image['mode'], image['mtime_ns']], [row['mode'], row['mtime_ns']], label + ' metadata')


def no_process(c):
    result = c.process_check(POOL)
    require(result['active_matches'] == [], 'no readable active pool references')
    result['operational_scope'] = 'original-readable-reference-check-with-exclusive-pool-lock/1'
    result['global_process_completeness_claimed'] = False
    return result


def action(target, source, current_row, desired_row):
    current = stable(target) if current_row is not None else None
    if current is not None:
        check_image(current, current_row, 'current action target')
    else:
        require(not target.exists() and not target.is_symlink(), 'expected absent action target')
    if desired_row is None:
        require(source is None, 'absent desired source')
        operation = 'unlink' if current is not None else 'skip'
    else:
        require(source is not None and desired_row['kind'] == 'file', 'present desired regular image')
        check_image(source, desired_row, 'desired action source', metadata=False)
        operation = ('replace' if current is None or current['identity'] != source['identity'] else
                     'metadata' if image_record(current) != row_record(desired_row) else 'skip')
    return {'target': target, 'source': source, 'current': current, 'desired': desired_row, 'operation': operation}


def public_action(row):
    return {'target': str(row['target']), 'operation': row['operation'],
            'current': image_record(row['current']) if row['current'] else None,
            'desired': row['desired']}


def select_restore_images(old, baseline, old_targets, old_images, journal, journal_images, expected_after):
    """Production O union N selection from already-read backup images; no filesystem access."""
    O=set(old_targets)|{MARKER};N=set(expected_after)
    equal(set(old_images),O,'all actual old patch and marker images')
    names=[row['path'] for row in journal]
    require(len(names)==len(set(names)) and set(names)==N,'exact unique new journal target membership')
    present=set()
    for name,image in old_images.items():
        require(name in old and old[name]['kind']=='file','old desired transformed target is regular')
        check_image(image,old[name],'old desired installed source')
    for index,row in enumerate(journal):
        require(set(row)=={'path','backup','before','after'},'closed new journal row')
        name=row['path'];equal(row['after'],expected_after[name],'journal new after identity')
        intermediate=None if name==MARKER else baseline.get(name) if name in old_targets else old.get(name)
        if intermediate is None:
            require(row['before'] is None and row['backup'] is None,'actual absent reset-time preimage')
        else:
            require(intermediate['kind']=='file','unsupported reset-time directory target')
            equal(row['before'],row_record(intermediate),'actual reset-time authority')
            require(row['backup']==str(index) and name in journal_images,'exact journal image binding')
            check_image(journal_images[name],intermediate,'reset-time backup bytes',metadata=False)
            present.add(name)
    equal(set(journal_images),present,'no extra/omitted present journal images')
    selected={}
    for name in sorted(O|N):
        desired=old.get(name)
        if desired is not None:require(desired['kind']=='file','unsupported desired directory target')
        if name in O:
            selected[name]=old_images[name]
        elif desired is None:
            selected[name]=None
        else:
            require(name in journal_images,'present desired new-only image')
            check_image(journal_images[name],desired,'new-only desired predecessor image',metadata=False)
            selected[name]=journal_images[name]
    return selected


def prepare(request, freeze, c, s, result):
    raw = {key: descriptor(row) for key, row in request['evidence'].items()}
    evidence = {key: decoded(value) for key, value in raw.items()}
    pending = evidence['pending_state']
    require(pending.get('status') == 'failed' and pending.get('reason') == 'PENDING_INDEPENDENT_PREDECESSOR_RESTORE'
            and pending.get('run') == str(RUN) and pending.get('previous_run') == str(PREVIOUS), 'fixed pending state')
    equal(pending['control_preimages'], {'path': str(CONTROLS), 'manifest':
          {key: request['evidence']['controls_manifest'][key] for key in ('size', 'sha256')}, 'restored': False},
          'pending controls association')
    result['process_before'] = no_process(c)
    manifest = evidence['controls_manifest']
    require(manifest['schema'] == 'phase464-predecessor-control-preimages/1' and manifest['restored'] is False
            and manifest['previous_run'] == str(PREVIOUS), 'saved controls authority')
    equal([row['target'] for row in manifest['images']],
          ['state.json', 'data/custom_player.json', 'data/custom_opponent.json'], 'three fixed controls')
    controls = {}
    for index, row in enumerate(manifest['images']):
        if row['present'] is False:
            equal(row, {'target': row['target'], 'present': False, 'backup': None}, 'closed absent control')
            require(index != 0, 'saved state present')
            controls[row['target']] = None
        else:
            require(row['present'] is True and set(row) == {'target', 'present', 'backup', 'identity', 'mode', 'mtime_ns'}
                    and row['backup'] == str(index), 'closed present control')
            image = stable(CONTROLS / row['backup'])
            equal(image_record(image), {key: row[key] for key in ('identity', 'mode', 'mtime_ns')}, 'control backup exact')
            controls[row['target']] = image
    saved_state = decoded(controls['state.json']['raw'])
    require(saved_state['status'] == 'ready' and saved_state['run'] == str(PREVIOUS), 'actual predecessor saved state')
    bundle_index = c.index(saved_state['bundle_inventory'])
    for key, name in [('previous_bundle_manifest', 'bundle-manifest.json'), ('previous_proof', 'pool-roundtrip.json'),
                      ('previous_project', 'project-files.json'), ('previous_baseline', 'baseline-files.json'),
                      ('previous_staged', 'staged-inputs.json')]:
        check_image(stable(BUNDLE / name), bundle_index[name], 'saved bundle member')
    base, old_project, _ = c.load_bundle(BUNDLE)
    equal(base, evidence['previous_baseline'], 'bundle baseline authority')
    equal(old_project, evidence['previous_project'], 'bundle project authority')
    old_staged = evidence['previous_staged']
    proof = evidence['previous_proof']
    require(proof.get('status') == 'PASS' and proof.get('run') == str(PREVIOUS) and proof.get('pool') == str(POOL),
            'actual prior proof association')
    require((proof.get('verification_mode') is None and proof.get('full_path_sha256_mode_mtime_equality') is True)
            or (proof.get('verification_mode') == 'logical-overlay-and-live-tree-equality/1'
                and proof.get('physical_reconstruction') is False and proof.get('live_tree_byte_mode_mtime_equality') is True),
            'accepted prior proof form')
    equal(proof['bundle_sha256'], request['evidence']['previous_bundle_manifest']['sha256'], 'prior bundle proof SHA')
    equal(proof['provenance_sha256'], request['evidence']['previous_provenance']['sha256'], 'prior provenance proof SHA')
    bidx, old, staged = c.index(base), c.index(old_project), c.index(old_staged)
    prior = evidence['patch_inventory']
    equal(prior['project'], old_project, 'saved pre-reset project equals actual prior compaction')
    report = evidence['previous_host_manifest']['audited_runtime_observation_patch']
    equal(prior['patch'], report, 'saved patch report equals actual old host')
    old_images = {}
    old_targets = {}
    for index, row in enumerate(report['patches']):
        name = c.safe_path(row['path'])
        require(name not in old_images and old[name]['kind'] == 'file', 'unique old patch target')
        equal({'size': row['after_size'], 'sha256': row['after_sha256']},
              {key: old[name][key] for key in ('size', 'sha256')}, 'old patch after authority')
        image = stable(PATCH / str(index))
        check_image(image, old[name], 'old patch backup')
        if row['before_sha256'] is None:
            require(name not in bidx, 'old added target absent in baseline')
        else:
            equal({'size': row['before_size'], 'sha256': row['before_sha256']},
                  {key: bidx[name][key] for key in ('size', 'sha256')}, 'old patch baseline authority')
        old_images[name] = image
        old_targets[name] = row
    old_images[MARKER] = stable(PATCH / 'marker')
    check_image(old_images[MARKER], old[MARKER], 'old marker backup')
    expected_after={name:row['after'] for name,row in freeze['paths'].items()}
    expected_after.update({name:{key:row[key] for key in ('size','sha256')} for name,row in freeze['artifacts'].items()})
    require(len(expected_after)==79 and sum(row['size'] for row in expected_after.values())==814020,'exact new79 install corpus')
    journal=evidence['install_journal']
    equal([row['path'] for row in journal],list(freeze['paths'])+['native_combat_capture.gd','native_capture_config.json',MARKER],'exact actual79 journal order')
    journal_images={}
    for index,row in enumerate(journal):
        if row.get('before') is not None:
            require(row.get('backup')==str(index),'exact numeric before backup')
            journal_images[row['path']]=stable(JOURNAL/row['backup'])
    sources=select_restore_images(old,bidx,old_targets,old_images,journal,journal_images,expected_after)
    before=evidence['pool_before']
    current_project=c.inventory(POOL/'project');equal(current_project,before['project'],'current live project equals sealed post-install graph')
    current_staged=c.inventory(POOL/'data');equal(current_staged,before['staged'],'current live staged equals sealed post-install graph')
    current,current_data=c.index(current_project),c.index(current_staged)
    O=set(old_targets)|{MARKER};N=set(expected_after);U=set(sources)
    old_dirs={name for name,row in old.items() if row['kind']=='directory'}
    current_dirs={name for name,row in current.items() if row['kind']=='directory'}
    equal(current_dirs,old_dirs,'unsupported directory topology change')
    expected_paths=set(old)-O
    for name in O:
        reset=None if name==MARKER else bidx.get(name)
        if reset is not None:
            require(reset['kind']=='file','unsupported old target reset kind');expected_paths.add(name)
    expected_paths.update(N)
    equal(set(current),expected_paths,'exact reset/install path-set authority')
    for name,row in current.items():
        if name in old:equal(row['kind'],old[name]['kind'],'unchanged existing node kind')
        if row['kind']=='file' and name not in U:equal(row,old[name],'untouched project file')
    for name in U:
        if name in N:
            require(name in current and current[name]['kind']=='file','current installed target regular')
            equal({key:current[name][key] for key in ('size','sha256')},expected_after[name],'live installed new source')
        else:
            reset=None if name==MARKER else bidx.get(name)
            if reset is None:require(name not in current,'O-only reset target absent')
            else:equal(current.get(name),reset,'O-only live reset baseline authority')
    actions=[action(s.member(POOL/'project',name),sources[name],current.get(name),old.get(name)) for name in sorted(U)]
    fixtures={'custom_player.json','custom_opponent.json'}
    require(set(current_data)-{'.'}<=fixtures and set(staged)-{'.'}<=fixtures,'only fixed staged fixtures')
    for name in sorted(fixtures):
        image=controls['data/'+name];desired=staged.get(name)
        require((image is None)==(desired is None),'fixture presence equals old staged authority')
        if image is not None:check_image(image,desired,'old fixture control')
        actions.append(action(s.member(POOL/'data',name),image,current_data.get(name),desired))
    dirs=[(s.member(POOL/'project',name) if name!='.' else POOL/'project',row) for name,row in old.items() if row['kind']=='directory']
    dirs.append((POOL/'data',staged['.']))
    for path,row in dirs:
        s.directory(path);require(not os.listxattr(path,follow_symlinks=False),'unsupported directory xattrs')
    for row in actions:
        if row['operation']=='replace':
            temporary=row['target'].with_name(row['target'].name+'.phase363-next')
            require(not temporary.exists() and not temporary.is_symlink(),'unfinished atomic image before writes')
    for key,row in request['evidence'].items():equal(descriptor(row),raw[key],'critical descriptor unchanged before writes')
    result['validated_sources']={'old_patch':len(old_targets),'old_marker':1,'new_journal':len(journal),'controls':3,
        'project_union':len(U),'current_project_entries':len(current),'old_project_directories':len(old_dirs)}
    result['pending_state']=request['evidence']['pending_state']
    return actions,dirs,stable(POOL/'state.json')


def recheck_target(row):
    path, current = row['target'], row['current']
    if current is None:
        require(not path.exists() and not path.is_symlink(), 'absent target appeared')
    else:
        equal(stable(path), current, 'target changed since validated plan: ' + str(path))


def finish_metadata(path, desired, s):
    info = s.regular_target(path)
    if stat.S_IMODE(info.st_mode) != desired['mode']:
        os.chmod(path, desired['mode'])
    if path.stat().st_mtime_ns != desired['mtime_ns']:
        os.utime(path, ns=(desired['mtime_ns'], desired['mtime_ns']))
    with path.open('rb') as stream:
        os.fsync(stream.fileno())
    s.sync(path.parent)
    check_image(stable(path), desired, 'restored file readback')


def apply(actions, dirs, s, out, result):
    for row in actions:
        recheck_target(row)
    progress = out / 'progress.jsonl'
    with progress.open('x', encoding='utf-8') as log:
        def record(value):
            log.write(json.dumps(value, sort_keys=True) + '\n'); log.flush(); os.fsync(log.fileno())
        for row in actions:
            recheck_target(row)
            path, desired, operation = row['target'], row['desired'], row['operation']
            if operation == 'replace':
                s.atomic_image(path, row['source']['raw'], image_record(row['current']) if row['current'] else None)
                finish_metadata(path, desired, s)
            elif operation == 'metadata':
                finish_metadata(path, desired, s)
            elif operation == 'unlink':
                s.regular_target(path); path.unlink(); s.sync(path.parent)
                require(not path.exists() and not path.is_symlink(), 'absent fixture readback')
            else:
                require(operation == 'skip', 'known restoration action')
            result['file_operations'][operation] += 1
            record({'target': str(path), 'operation': operation, 'completed': True})
        # Deepest project first, then staged root; neither operation changes pool state.
        for path, desired in sorted(dirs, key=lambda item: len(item[0].parts), reverse=True):
            s.directory(path)
            info = path.stat()
            changed = (stat.S_IMODE(info.st_mode), info.st_mtime_ns) != (desired['mode'], desired['mtime_ns'])
            if changed:
                os.chmod(path, desired['mode']); os.utime(path, ns=(desired['mtime_ns'], desired['mtime_ns']))
                s.sync(path)
            result['directory_operations']['metadata' if changed else 'skip'] += 1
            record({'directory': str(path), 'operation': 'metadata' if changed else 'skip', 'completed': True})
    for row in actions:
        if row['desired'] is None:
            require(not row['target'].exists() and not row['target'].is_symlink(), 'final absent target')
        else:
            check_image(stable(row['target']), row['desired'], 'final restored target')
    for path, desired in dirs:
        s.directory(path)
        equal([stat.S_IMODE(path.stat().st_mode), path.stat().st_mtime_ns],
              [desired['mode'], desired['mtime_ns']], 'final restored directory metadata')
    s.sync(POOL / 'project'); s.sync(POOL / 'data')
    s.sync(out)


def restore(request, freeze, c, s, out, result):
    require(set(path.name for path in s.directory(POOL).iterdir()) == {'.lock', 'state.json', 'project', 'data'}, 'fixed pool members')
    s.directory(RUN); s.directory(PREVIOUS)
    lock = POOL / '.lock'
    before_lock = s.regular_target(lock)
    fd = os.open(lock, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        equal(signature(os.fstat(fd)), signature(before_lock), 'same locked ordinary inode')
        actions, dirs, state = prepare(request, freeze, c, s, result)
        save(out / 'restore-plan.json', {'schema': 'phase469-fixed-restore-plan/1', 'case_id': CASE,
             'file_actions': [public_action(row) for row in actions],
             'directory_desired': [{'path': str(path), 'mode': row['mode'], 'mtime_ns': row['mtime_ns']} for path, row in dirs],
             'state_write': False, 'independent468_required': True})
        s.sync(out)
        equal(stable(POOL / 'state.json'), state, 'pending state before writes')
        result['write_phase_entered'] = True
        apply(actions, dirs, s, out, result)
        equal(stable(POOL / 'state.json'), state, 'pending state unchanged after restoration')
        result['process_after'] = no_process(c)
        result['state_unchanged'] = request['evidence']['pending_state']
        result['status'] = 'RESTORED_FILES_STATE_FAILED_INDEPENDENT468_PENDING'
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    parser.add_argument('--config-sha256', required=True)
    parser.add_argument('--output-new', required=True)
    args = parser.parse_args()
    out = path_of(args.output_new)
    require(out.parent == ROOT / 'data' and out.name.startswith('phase508-restore-'), 'unique local phase469 report only')
    require(not out.exists() and not out.is_symlink(), 'report must be new')
    out.mkdir(mode=0o700)
    started = time.monotonic()
    result = {'schema': 'phase508-fixed-predecessor-restore-result/1', 'case_id': CASE, 'run': str(RUN),
              'previous_run': None, 'pool': str(POOL), 'status': 'RUNNING', 'write_phase_entered': False,
              'file_operations': {'replace': 0, 'metadata': 0, 'unlink': 0, 'skip': 0},
              'directory_operations': {'metadata': 0, 'skip': 0}, 'READY_writes': 0, 'state_writes': 0,
              'native': 0, 'models': 0, 'Expected_semantic_decoding': 0}
    code = 1
    try:
        def deadline(signum, frame):
            raise TimeoutError('fixed restoration deadline300s')
        signal.signal(signal.SIGALRM, deadline); signal.alarm(300)
        config = stable(path_of(args.config))
        equal(config['identity']['sha256'], args.config_sha256, 'request SHA')
        request = decoded(config['raw'])
        freeze = validate_request(request)
        result['previous_run']=str(PREVIOUS)
        result['config'] = dict(path=str(path_of(args.config)), **config['identity'])
        result['source'] = request['writer']
        sys.dont_write_bytecode = True
        c, s = load_modules()
        restore(request, freeze, c, s, out, result)
        equal(stable(path_of(args.config)), config, 'request unchanged')
        descriptor(request['writer']); descriptor(FREEZE)
        for row in SOURCES.values():
            descriptor(row)
        code = 0
    except BaseException as exc:
        result['status'] = 'FIRST_ERROR_STOPPED_FAILED_STATE_READY_BLOCKED'
        result['error'] = {'type': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()}
    finally:
        signal.alarm(0)
        result['elapsed_seconds'] = time.monotonic() - started
        result['readback_role'] = 'Writer target/metadata checks only; independent468 full physical proof still required.'
        save(out / 'result.json', result)
        files = []
        for path in sorted(out.iterdir()):
            if path.is_file():
                files.append(dict(path=str(path.relative_to(ROOT)), **stable(path)['identity']))
        save(out / 'owned-files.json', {'schema': 'phase508-restore-output-owner/1', 'files': files, 'no_more_writes': True})
        print(json.dumps({'status': result['status'], 'elapsed_seconds': result['elapsed_seconds']}), flush=True)
    return code


if __name__ == '__main__':
    raise SystemExit(main())
