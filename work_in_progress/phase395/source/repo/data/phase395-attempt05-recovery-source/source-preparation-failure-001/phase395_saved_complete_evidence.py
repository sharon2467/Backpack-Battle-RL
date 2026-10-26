"""Saved05 completed-install consistency only. No current pool/process operations."""
from pathlib import Path
import hashlib
import json
import stat

FAILED_NAME = 'original027-king-single-A-20261025-attempt05'
PREVIOUS_NAME = 'native-v7-026-rainbow75-N-327'
RECEIPT = dict(size=492, sha256='6f2d5199b5e733973038e75b86c75edf691cd070c8828e2c6a17e523ee9e0e30')
INSTALLED_FREEZE = dict(path='data/phase380-payload-source/combined-source-freeze.json', size=63604,
                        sha256='0b849df817910a586e9d28548c2942e013cae1f15f7bf085aaf5e9b2a4337cfb')


def saved_pin(path):
    path = Path(path)
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('ordinary nlink1 saved source required')
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''): h.update(block)
    after = path.lstat()
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns):
        raise ValueError('saved source changed during read')
    return dict(size=after.st_size, sha256=h.hexdigest())


def saved_json(path):
    def pairs(rows):
        value = {}
        for key, item in rows:
            if key in value: raise ValueError('duplicate saved JSON key')
            value[key] = item
        return value
    saved_pin(path)
    return json.loads(Path(path).read_text(), object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('nonfinite saved JSON')))


def validate_complete_saved(roots):
    """Return a fresh saved-only ledger; never inventory pool/baseline/current process."""
    failed, previous = Path(roots['failed_run']), Path(roots['previous_run'])
    if failed.name != FAILED_NAME or previous.name != PREVIOUS_NAME:
        raise ValueError('fixed failed05 and previous026 saved roots')
    ledger = {}
    def leaf(label, name):
        if type(name) is not str or '\\' in name or '\0' in name or Path(name).is_absolute() or any(x in ('', '.', '..') for x in name.split('/')):
            raise ValueError('canonical saved relative source')
        base = failed if label == 'failed_run' else previous if label == 'previous_run' else None
        if base is None: raise ValueError('saved roots only')
        path = base/name
        row = dict(root=label, path=name, **saved_pin(path))
        if (label, name) in ledger and ledger[label, name] != row: raise ValueError('saved source drift')
        ledger[label, name] = row
        return path
    def load(label, name): return saved_json(leaf(label, name))
    def index(value):
        if type(value) is not dict or value.get('schema') != 'native-run-project-manifest/1' or type(value.get('entries')) is not list:
            raise ValueError('actual saved manifest')
        result = {}
        for row in value['entries']:
            if row['path'] in result or row['kind'] not in ('file', 'directory'): raise ValueError('duplicate/special saved manifest entry')
            result[row['path']] = row
        return result
    def need(condition, message):
        if not condition: raise ValueError(message)
    pres = 'output/failed-pool-preservation/'
    receipt = load('failed_run', pres+'receipt.json')
    need(saved_pin(failed/pres/'receipt.json') == RECEIPT, 'actual05 preservation receipt')
    need(receipt['schema'] == 'attempt05-installed-failed-pool-preservation/1' and receipt['status'] == 'PRESERVED_NOT_RESTORED' and receipt['state'] == 'failed', 'completed05 failed preservation')
    for key in ('baseline_unchanged', 'project_exact_before_native', 'staged_exact_before_native', 'install_preimages_journal_present'):
        need(receipt[key] is True, 'complete preservation evidence')
    for key in ('restore', 'models', 'Gamecopies'): need(type(receipt[key]) is int and receipt[key] == 0, 'saved zero operation fields')
    state = load('failed_run', pres+'failed-pool-state.json')
    need(state['status'] == 'failed' and Path(state['run']).name == FAILED_NAME, 'original failed state')
    trees = {key:load('failed_run', pres+name) for key,name in [('baseline','baseline-files.json'),('project','failed-project-files.json'),('staged','failed-staged-files.json')]}
    before = load('failed_run','output/pool-before.json')
    need(trees == before, 'saved failed trees equal actual before-native manifests')
    journal = load('failed_run','output/source-preimages/preimages.json')
    prior = load('failed_run','output/previous-source-preimages/inventory.json')
    reset = load('failed_run','output/prior-observer-reset.json')
    target = load('previous_run','output/compaction/project-files.json')
    target_data = load('previous_run','output/compaction/staged-inputs.json')
    need(load('previous_run','output/compaction/baseline-files.json') == trees['baseline'], 'old026 baseline')
    need(target == prior['project'] == reset['before'], 'old026 target/reset provenance')
    current, wanted, start = index(trees['project']), index(target), index(reset['after'])
    staged, wanted_data = index(trees['staged']), index(target_data)
    need(current.keys() == wanted.keys() and staged.keys() == wanted_data.keys(), 'no current missing/unknown targets')
    need(all(current[k]['kind'] == wanted[k]['kind'] for k in current) and all(staged[k]['kind'] == wanted_data[k]['kind'] for k in staged), 'target kinds unchanged')
    source_map = load('failed_run','output/driver/source-map.json')
    archived = {}
    for row in source_map['files']:
        need(type(row) is dict and set(row) == {'file','source'}, 'closed archived source map row')
        path = leaf('failed_run','output/driver/'+row['file'])
        need(saved_pin(path) == {k:row['source'][k] for k in ('size','sha256')}, 'archived actual SOURCE byte identity')
        need(row['source']['path'] not in archived, 'unique archived source path')
        archived[row['source']['path']] = (row['source'], path)
    need(INSTALLED_FREEZE['path'] in archived and archived[INSTALLED_FREEZE['path']][0] == INSTALLED_FREEZE, 'actual installed380 freeze archived')
    freeze = saved_json(archived[INSTALLED_FREEZE['path']][1])
    declaration = {name:row['after'] for name,row in freeze['paths'].items()}
    need(len(declaration) == 75 and len(freeze['artifacts']) == 3, 'actual38075patch+3 artifacts')
    need(not (set(declaration) & set(freeze['artifacts'])), 'unique installation targets')
    declaration.update({name:{k:row[k] for k in ('size','sha256')} for name,row in freeze['artifacts'].items()})
    plan = load('failed_run','output/readonly-plan.json')
    provenance = load('failed_run','output/pool-provenance.json')
    need(plan['freeze'] == INSTALLED_FREEZE and provenance['plan'] == plan and provenance['installed_preimages'] == journal, 'real completed install provenance')
    need(type(journal) is list and len(journal) == len(declaration), 'complete actual install journal')
    jm = {row['path']:row for row in journal}
    need(len(jm) == len(journal) and jm.keys() == declaration.keys(), 'complete unique journal destinations')
    installs = 0
    for name,row in jm.items():
        need(row['after'] == declaration[name] == {k:current[name][k] for k in ('size','sha256')}, 'journal/declaration/installed failed hash')
        if row['before'] is None:
            need(name not in start and row['backup'] is None, 'exact preinstall absence, not current missing')
        else:
            need(name in start and row['before'] == dict(identity={k:start[name][k] for k in ('size','sha256')}, mode=start[name]['mode'], mtime_ns=start[name]['mtime_ns']), 'preinstall before image and metadata')
            need(saved_pin(leaf('failed_run','output/source-preimages/'+row['backup'])) == row['before']['identity'], 'all install backups')
            installs += 1
    oldpatch = prior['patch']['patches']
    pm = {row['path']:(i,row) for i,row in enumerate(oldpatch)}
    need(len(pm) == len(oldpatch), 'unique prior patch destinations')
    for i,row in enumerate(oldpatch):
        need(saved_pin(leaf('failed_run','output/previous-source-preimages/'+str(i))) == dict(size=row['after_size'],sha256=row['after_sha256']), 'all prior patch backups')
    marker = leaf('failed_run','output/previous-source-preimages/marker')
    need(saved_pin(marker) == {k:wanted['.native-random-observer-disposable'][k] for k in ('size','sha256')}, 'old026 marker bytes')
    routes = dict(previous_patch=0, previous_marker=0, install_preimage=0)
    files = dirs = 0
    for name in current:
        if current[name] == wanted[name]: continue
        if current[name]['kind'] == 'directory': dirs += 1; continue
        files += 1
        if name in pm: payload=leaf('failed_run','output/previous-source-preimages/'+str(pm[name][0]));routes['previous_patch']+=1
        elif name == '.native-random-observer-disposable': payload=marker;routes['previous_marker']+=1
        else:
            need(name in jm and jm[name]['before'] is not None, 'proven old026 source payload')
            payload=leaf('failed_run','output/source-preimages/'+jm[name]['backup']);routes['install_preimage']+=1
        need(saved_pin(payload) == {k:wanted[name][k] for k in ('size','sha256')}, 'each target payload byte identity')
    data_files = data_changes = 0
    for name,row in wanted_data.items():
        if row['kind'] != 'file': continue
        data_files += 1;data_changes += staged[name] != row
        need(saved_pin(leaf('previous_run','output/compaction/inputs/'+name)) == {k:row[k] for k in ('size','sha256')}, 'target staged source')
        need(saved_pin(leaf('failed_run',pres+'staged-bytes/'+name)) == {k:staged[name][k] for k in ('size','sha256')}, 'preserved staged source')
    leaf('previous_run','output/pool-provenance.json') # Direct runtime roundtrip-proof digest consumer.
    bundle = load('previous_run','output/compaction/bundle-manifest.json')
    for name,sha in bundle['files'].items(): need(saved_pin(leaf('previous_run','output/compaction/'+name))['sha256'] == sha, 'all consumed bundle members')
    for name,sha in bundle['driver_sha256'].items(): need(saved_pin(leaf('previous_run','output/driver/'+name))['sha256'] == sha, 'all consumed previous driver files')
    # The old generator also checks every preservation leaf; close those exact reads.
    for path in sorted((failed/pres).rglob('*')):
        if path.is_file(): leaf('failed_run',str(path.relative_to(failed)))
    for name in ('parse-process-result.json','native-process-result.json'):
        load('failed_run','output/'+name) # control record only, never capture output.
    summary = dict(journal_rows=len(journal), checked_install_backups=installs, checked_previous_patch_backups=len(oldpatch),
                   project_file_differences=files,directory_differences=dirs,staged_files=data_files,staged_file_differences=data_changes,
                   expected_writer_files=files+data_files,target_payload_routes=routes,installed_source_freeze=INSTALLED_FREEZE)
    return dict(summary=summary, files=[ledger[k] for k in sorted(ledger)])
