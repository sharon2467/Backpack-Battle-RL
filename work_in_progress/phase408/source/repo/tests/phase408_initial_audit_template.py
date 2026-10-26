# Appended after literal constants; no imports of schema/candidate/model.
import argparse
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat
import struct
import sys
import traceback


class SourceIntegrityError(ValueError):
    pass


def need(ok, message):
    if not ok:
        raise SourceIntegrityError(message)


def exact(value, keys, label):
    need(type(value) is dict and set(value) == set(keys), 'closed '+label)


def same(left, right):
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return set(left) == set(right) and all(same(left[k], right[k]) for k in left)
    if type(left) is list:
        return len(left) == len(right) and all(same(a, b) for a, b in zip(left, right))
    if type(left) is float:
        return struct.pack('>d', left) == struct.pack('>d', right)
    return left == right


def strict_json(raw):
    def pairs(values):
        result = {}
        for key, value in values:
            need(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    def bad(value):
        raise SourceIntegrityError('nonfinite JSON number '+value)
    def real(value):
        number = float(value)
        need(math.isfinite(number), 'finite JSON real')
        return number
    return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
                      parse_constant=bad, parse_float=real)


def descriptor(row):
    exact(row, ('path', 'size', 'sha256'), 'descriptor')
    need(type(row['path']) is str and type(row['size']) is int and 0 <= row['size'] <= TOTAL_BYTES,
         'descriptor primitive fields')
    need(type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}', row['sha256']) is not None,
         'descriptor SHA')
    return row


def canonical(root, name):
    need(type(name) is str and bool(name) and '\\' not in name and '\0' not in name,
         'relative path string')
    rel = PurePosixPath(name)
    need(not rel.is_absolute() and rel.as_posix() == name and
         all(x not in ('', '.', '..') for x in name.split('/')), 'canonical relative member')
    return root.joinpath(*rel.parts)


def unlinked(path):
    need(not any(p.is_symlink() for p in (path, *path.parents)), 'no symlink ancestry')


def identity(info):
    return [info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns]


def read_regular(path, row, cap, io):
    descriptor(row)
    need(row['size'] <= cap, 'file cap')
    unlinked(path)
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1, 'ordinary single-link before read')
    need(before.st_size == row['size'], 'physical size')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        opened = os.fstat(stream.fileno())
        need(identity(opened) == identity(before) and stat.S_ISREG(opened.st_mode) and opened.st_nlink == 1,
             'opened identity before read')
        raw = stream.read(row['size'] + 1)
        closed = os.fstat(stream.fileno())
    unlinked(path)
    need(identity(before) == identity(closed) == identity(path.lstat()), 'read identity stable')
    need(len(raw) == row['size'] and hashlib.sha256(raw).hexdigest() == row['sha256'], 'content identity')
    io.append(dict(path=str(path), size=len(raw), sha256=row['sha256'], identity=identity(before)))
    return raw


def source_path(root, name):
    if name in STATIC_PINS and Path(name).is_absolute():
        return Path(name)
    return canonical(root, name)


def metadata(root, row, io):
    path = canonical(root, descriptor(row)['path'])
    need(row['path'].startswith('data/') and row['size'] <= 8 * 1024 * 1024, 'bounded repo authority leaf')
    return strict_json(read_regular(path, row, 8 * 1024 * 1024, io))


def owned_index(value):
    need(type(value) is dict and type(value.get('files')) in (list, dict), 'owner list or path-map files')
    files = value['files']
    rows = []
    if type(files) is dict:
        for name, content in files.items():
            exact(content, ('size', 'sha256'), 'path-map owner value; no path override')
            rows.append(dict(path=name, size=content['size'], sha256=content['sha256']))
    else:
        rows = files
    result = {}
    for row in rows:
        descriptor(row)
        name = row['path']
        need(bool(name) and '\\' not in name and '\0' not in name, 'owner path string')
        if PurePosixPath(name).is_absolute():
            need(name in STATIC_PINS and name == PurePosixPath(name).as_posix() and
                 all(part not in ('', '.', '..') for part in name.split('/')[1:]), 'exact approved absolute SOURCE owner path')
            normalized = name
        else:
            normalized = canonical(Path('.'), name).as_posix()
            need(normalized == name, 'canonical relative owner path')
        need(normalized not in result, 'unique normalized owned source path')
        result[normalized] = dict(path=normalized, size=row['size'], sha256=row['sha256'])
    return result


def verify_audit_release(root, release_descriptor, io):
    root = Path(root).absolute()
    unlinked(root)
    need(root.is_dir(), 'source root')
    release = metadata(root, release_descriptor, io)
    exact(release, ('schema','action','authorized','run','input_directory','output_directory',
                   'permissions','source_freeze','source_owner','source_review','source_review_owner',
                   'root402','design405_review','input_files'), 'Root audit release')
    need(release['schema'] == 'root408-lawful12-initial-audit/1' and
         release['action'] == 'initial_presence_source_chain_audit' and release['authorized'] is True,
         'explicit Root initial-audit authority')
    exact(release['permissions'], PERMISSION_KEYS, 'permissions')
    need(all(type(v) is int and v == 0 for v in release['permissions'].values()), 'strict zero non-audit permissions')
    need(release['run'] == FIXED_RUN and release['input_directory'] == FIXED_RUN+'/output/capture',
         'exact fixed06 capture root')
    out_name = release['output_directory']
    need(type(out_name) is str and re.fullmatch(r'data/phase408-initial-audit-[A-Za-z0-9_-]+', out_name) is not None,
         'new bounded audit output root')
    output = canonical(root, out_name)
    unlinked(output)
    need(output.parent.is_dir() and not output.exists(), 'exclusive new output directory')
    need(release['root402'] == STATIC_PINS[ROOT402] and release['design405_review'] == STATIC_PINS[REVIEW405],
         'actual402Root/405review descriptors')
    controls = {}
    for name, row in STATIC_PINS.items():
        controls[name] = read_regular(source_path(root, name), row, TOTAL_BYTES, io)
    accepted = strict_json(controls[ROOT402])
    need(accepted['status'] == 'ROOT_ACCEPTS_FIXED06_BOUNDED_TERMINAL_SOURCE_PROCESS_CONTROLS' and
         accepted['full12_business_or_input_admitted'] is False and accepted['King_admitted'] is False,
         'bounded actual402 receipt only')
    need(accepted['review'] == STATIC_PINS[REVIEW402] and accepted['owner'] == STATIC_PINS[OWNER402],
         'actual402 review owner relation')
    need(owned_index(strict_json(controls[OWNER402])).get(REVIEW402) == STATIC_PINS[REVIEW402], 'owned402 review')
    review405 = strict_json(controls[REVIEW405])
    need(review405['status'] == 'INDEPENDENT405_DESIGN_ACCEPTED_FOR_SMALL_STDLIB_AUDIT_SOURCE_IMPLEMENTATION_ROOT_PENDING' and
         review405['models'] == 0 and type(review405['models']) is int and review405['writer_closure_proven'] is False,
         'actual405 limited design review')
    need(owned_index(strict_json(controls[OWNER405])).get(REVIEW405) == STATIC_PINS[REVIEW405], 'owned405 review')
    need(release['source_freeze']['path'] == SOURCE+'/source-freeze.json' and
         release['source_owner']['path'] == SOURCE+'/source-owner.json', 'fixed408 authority paths')
    freeze = metadata(root, release['source_freeze'], io)
    owner = owned_index(metadata(root, release['source_owner'], io))
    exact(freeze, ('schema','module','files','static_pins','fullschema','derived_recipes','old_SUT_calls'), 'SOURCE freeze')
    need(freeze['schema'] == 'phase408-readonly-initial-audit-SOURCE/1' and
         freeze['static_pins'] == STATIC_PINS and freeze['derived_recipes'] == [] and
         freeze['fullschema'] == 'NOT_VALIDATED' and type(freeze['old_SUT_calls']) is int and freeze['old_SUT_calls'] == 0,
         'exact408 source scope')
    need(freeze['module']['path'] == MODULE and Path(__file__).absolute() == canonical(root, MODULE),
         'executing exact SOURCE path')
    declared = owned_index({'files': freeze['files']})
    need(set(declared) == set(SOURCE_ARTIFACTS) | set(STATIC_PINS), 'closed SOURCE payload set')
    need(set(owner) == set(declared) | {SOURCE+'/source-freeze.json', SOURCE+'/summary.json'}, 'closed408 source owner set')
    need(declared.get(MODULE) == freeze['module'] and owner.get(release['source_freeze']['path']) == release['source_freeze'],
         'owner covers freeze/module')
    for name, row in declared.items():
        need(owner.get(name) == row, 'owner covers every frozen leaf')
        if name in STATIC_PINS:
            need(row == STATIC_PINS[name], 'fixed source descriptor')
        else:
            read_regular(canonical(root, name), row, TOTAL_BYTES, io)
    review = metadata(root, release['source_review'], io)
    review_owner = owned_index(metadata(root, release['source_review_owner'], io))
    need(review_owner.get(release['source_review']['path']) == release['source_review'], 'actual owned409 review')
    need(review.get('status') == REVIEW_STATUS and review.get('source_freeze') == release['source_freeze'] and
         review.get('source_owner') == release['source_owner'], '409 binds actual408 freeze and owner')
    need(all(type(review.get(k)) is int and review[k] == 0 for k in ('models','native','inputbuild','old_SUT_calls','schema_calls')),
         'review does not grant engine or schema execution')
    exact(release['input_files'], INPUT_NAMES, 'exact lawful12 names')
    for name, row in release['input_files'].items():
        exact(row, ('size','sha256'), 'lawful identity')
        descriptor(dict(path=name, **row))
    need(sum(row['size'] for row in release['input_files'].values()) <= TOTAL_BYTES, 'lawful12 total cap')
    allowed = {row['path'] for row in io}
    allowed.update(str(Path(release['input_directory']) / name) for name in INPUT_NAMES)
    return dict(root=root, release=release, output=output, allowed=allowed,
                controls=controls, source_freeze=release['source_freeze'], source_owner=release['source_owner'])


def install_io_guard(allowed_read, output, violations):
    def guard(event, args):
        if event == 'open':
            path, mode, flags = args
            if type(path) is int:
                return
            p = Path(os.fsdecode(path)).absolute()
            write = isinstance(mode, str) and any(c in mode for c in 'wax+') or type(flags) is int and bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
            permitted = p.parent == output if write else str(p) in allowed_read or p == output or p.parent == output
            if not permitted:
                violations.append(dict(event=event, path=str(p)))
                raise PermissionError('audit file outside exact permission set')
        if event in ('subprocess.Popen','os.system','os.posix_spawn','socket.connect','socket.bind','ctypes.dlopen'):
            violations.append(dict(event=event));raise PermissionError('no process/network/native loading')
        if event == 'import':
            violations.append(dict(event=event, module=str(args[0])));raise PermissionError('no imports during audit execution')
        if event in ('os.remove','os.rename','os.rmdir','os.link','os.symlink','os.chmod','os.utime','os.truncate'):
            violations.append(dict(event=event));raise PermissionError('no filesystem mutation except new output files')
        if event == 'os.mkdir' and Path(os.fsdecode(args[0])).absolute() != output:
            violations.append(dict(event=event));raise PermissionError('only assigned output mkdir')
    sys.addaudithook(guard)


def read_lawful12_once(authority, io):
    decoded = {}
    seen = set()
    for name in INPUT_NAMES:
        row = dict(path=name, **authority['release']['input_files'][name])
        cap = 64*1024*1024 if name == 'king-clock-passes.jsonl' else 8*1024*1024 if name == 'king-ui-authority.jsonl' else TOTAL_BYTES
        raw = read_regular(Path(authority['release']['input_directory'])/name, row, cap, io)
        if not name.endswith('.jsonl'):
            value = strict_json(raw)
            need(type(value) is dict, 'lawful JSON object '+name)
            decoded[name] = value
            continue
        lines = raw.splitlines()
        count_cap = 200000 if name == 'king-clock-passes.jsonl' else 65536 if name == 'king-ui-authority.jsonl' else 300000
        line_cap = 1024 if name == 'king-clock-passes.jsonl' else 16384 if name == 'king-ui-authority.jsonl' else 2097152
        need(len(lines) <= count_cap, 'row cap '+name)
        records = [];previous = -1
        for line_number, line in enumerate(lines, 1):
            need(bool(line.strip()) and len(line) <= line_cap, 'bounded nonblank JSONL row')
            value = strict_json(line)
            need(type(value) is dict, 'JSONL object')
            if name in CHANNELS:
                seq = value.get('sequence')
                need(value.get('schema') == 'observer7-record/1' and value.get('channel') == CHANNELS[name] and
                     type(seq) is int and previous < seq < 1<<63 and seq not in seen, 'physical unique ordered observer sequence')
                seen.add(seq);previous = seq
            records.append((line_number, value))
        decoded[name] = records
    return decoded


def rawref(name, line, row, pointer, owner=None):
    return dict(file=name, line=line, sequence=row.get('sequence'), pointer=pointer, native_owner=owner)


def unique_records(rows, site, edge):
    return [(line, row) for line, row in rows if row.get('site') == site and row.get('edge') == edge]


def index_initial_observations(decoded):
    phases = {};findings = []
    def issue(label):
        findings.append(dict(kind='DOMAIN_REJECTED', detail=label))
    for phase, site in PHASES:
        cps = unique_records(decoded['observer7-input.jsonl'], site, 'checkpoint')
        entries = unique_records(decoded['observer7-input.jsonl'], site, 'enter')
        need(len(cps) == len(entries) == 1, 'unique checkpoint and entry '+phase)
        line, cp = cps[0];_, entry = entries[0]
        need(cp['sequence']+1 == entry['sequence'] and same(cp['stamp'], entry['stamp']) and
             same(cp['subject'], entry['subject']), 'checkpoint/entry immediate identity/stamp')
        payload = cp.get('payload')
        exact(payload, ('environment','nodes','items','source_resources'), 'checkpoint payload')
        nodes = {};native_ids = set();paths = set()
        need(type(payload['nodes']) is list and len(payload['nodes']) <= 16384, 'bounded actual nodes')
        for number, row in enumerate(payload['nodes']):
            exact(row, ('role','node','timer'), 'node envelope')
            node = row['node'];need(type(node) is dict, 'node object')
            role = row['role'];native = node.get('native_id');path = node.get('path')
            need(type(role) is str and role not in nodes and type(native) is str and re.fullmatch('[1-9][0-9]*', native) is not None and native not in native_ids and type(path) is str and path not in paths, 'unique actual node roles/IDs/paths')
            nodes[role] = (number,row);native_ids.add(native);paths.add(path)
        items = {}
        need(type(payload['items']) is list, 'checkpoint item rows')
        for number, item in enumerate(payload['items']):
            need(type(item) is dict and type(item.get('instance')) is str and item['instance'] not in items, 'unique checkpoint item')
            items[item['instance']] = (number,item)
        need(type(payload['source_resources']) is list, 'resource rows')
        resources = {}
        for number, resource in enumerate(payload['source_resources']):
            need(type(resource) is dict and resource.get('side') in ('P','O') and resource['side'] not in resources, 'unique resource side')
            resources[resource['side']] = (number,resource)
        if set(items) != {x['instance_id'] for x in SLOT_PLAN}:
            issue(phase+': exact39 slot identities required; O:12 absent')
        actual_timer_roles = {role for role, (_, row) in nodes.items() if row['timer'] is not None}
        if actual_timer_roles != set(TIMER_ROLES):
            issue(phase+': Timer membership differs from35 exact roles')
        phases[phase] = dict(line=line, checkpoint=cp, nodes=nodes, items=items, resources=resources)
    pre, act = phases['pre_prepare'], phases['pre_activate']
    need(pre['checkpoint']['sequence'] < act['checkpoint']['sequence'], 'prepare before activate')
    for role in set(pre['nodes']) | set(act['nodes']):
        if role not in pre['nodes'] or role not in act['nodes'] or any(not same(pre['nodes'][role][1]['node'].get(k),act['nodes'][role][1]['node'].get(k)) for k in ('native_id','role','path','name','class','positions','priority')):
            issue('node continuity '+role)
    binding = decoded['king-slot-bindings.json']
    need(type(binding.get('actual_bindings')) is list, 'actual binding array')
    if not same(binding.get('source_slot_table'), SLOT_PLAN):
        issue('fixed source slot plan')
    byrole = {};binding_ids = set()
    for number,row in enumerate(binding['actual_bindings']):
        need(type(row) is dict and type(row.get('instance_id')) is str and row['instance_id'] not in byrole, 'unique binding role')
        byrole[row['instance_id']] = (number,row)
        if row.get('native_id') in binding_ids:issue('binding native identity reused')
        binding_ids.add(row.get('native_id'))
    if set(byrole) != {x['instance_id'] for x in SLOT_PLAN}:issue('binding exact39 identities')
    lineage = decoded['observer7-lineage.jsonl']
    for spec in SLOT_PLAN:
        role = spec['instance_id'];pair = byrole.get(role)
        if pair is None:continue
        _, bound = pair
        if not same(bound.get('item_index'), {'type':'int','decimal':str(spec['item_index'])}) or not same(bound.get('orientation'), {'type':'int','decimal':str(spec['f'])}) or not same(bound.get('input_slot'), spec['input_slot']):
            issue('binding item/orientation/slot '+role)
        for phase, index in phases.items():
            item = index['nodes'].get('item:'+role);character = index['nodes'].get('character:'+spec['side'])
            if item is None or character is None or bound.get('native_id') != item[1]['node']['native_id'] or bound.get('character_id') != character[1]['node']['native_id']:
                issue(phase+': binding actual node owner '+role)
        scenes = [(ln,r) for ln,r in lineage if r.get('edge') == 'scene_instance' and r.get('payload',{}).get('item_id') == bound.get('native_id')]
        ready = [(ln,r) for ln,r in lineage if r.get('site') == 'Items/Item.gd::_ready' and r.get('edge') == 'enter' and r.get('subject',{}).get('native_id') == bound.get('native_id')]
        if len(scenes) != 1 or len(ready) != 1:
            issue('actual fresh scene/ready presence '+role)
        elif not (scenes[0][1]['sequence'] < ready[0][1]['sequence'] < pre['checkpoint']['sequence'] and scenes[0][1].get('payload',{}).get('pooled') is False and scenes[0][1].get('subject',{}).get('role') is None and ready[0][1].get('subject',{}).get('role') is None):
            issue('fresh lineage/earlyNULL order '+role)
    for side,name in [('P','player_fixture.json'),('O','fixture.json')]:
        fixture = decoded[name];planned = FIXED_FIXTURE['sides'][0 if side=='P' else 1]
        expected_items = [{k:v for k,v in item.items() if k!='instance_id'} for item in planned['items']]
        if fixture.get('class') != 0 or type(fixture.get('class')) is not int or not same(fixture.get('items'), expected_items):
            issue('fixed '+side+' fixture class/items')
        for field,target in [('health','hp'),('stamina','stamina')]:
            v=fixture.get(field)
            if type(v) not in (int,float) or not math.isfinite(v) or v != planned[target]:issue('fixed '+side+' initial '+field)
    return dict(phases=phases, findings=findings, raw_binding_rows=byrole,
                identity_scope='AUDIT_SUBSET_NOT_FULL391_BINDING_VALIDATION')


def typed_int(value):
    return type(value) is dict and set(value)=={'type','decimal'} and value['type']=='int' and type(value['decimal']) is str and re.fullmatch(r'0|-?[1-9][0-9]*',value['decimal']) is not None and -(1<<63)<=int(value['decimal'])<(1<<63)


def typed_real(value):
    return type(value) is dict and set(value)=={'type','binary64_be'} and value['type']=='float' and type(value['binary64_be']) is str and re.fullmatch('[0-9a-f]{16}',value['binary64_be']) is not None and math.isfinite(struct.unpack('>d',bytes.fromhex(value['binary64_be']))[0])


def direct_row(field, phase, role, actual, present, constraint, refs, supported):
    result = dict(field_id=field, phase=phase, side_or_role=role,
                  classification='DIRECT_OBSERVATION' if present else 'MISSING',
                  validation_result='SUPPORTED' if present and supported else 'REJECTED' if present else 'UNPROVEN',
                  proof_complete=bool(present and supported), constraint=constraint, input_refs=refs,
                  source_refs=[], unresolved=[] if present else ['actual lawful field absent'])
    if present:result['actual_value']=actual
    return result


def audit_direct_fields(index, decoded):
    rows = []
    for phase, item in index['phases'].items():
        cp=item['checkpoint'];line=item['line']
        def ref(pointer, owner=None):return rawref('observer7-input.jsonl',line,cp,pointer,owner)
        for side in ('P','O'):
            pair=item['resources'].get(side);node=item['nodes'].get('character:'+side)
            val=pair[1] if pair else {};owner=node[1]['node']['native_id'] if node else None
            present='buffProtectStacks' in val
            rows.append(direct_row('Character.buffProtectStacks',phase,side,val.get('buffProtectStacks'),present,{'type':'int','decimal':'0'},[ref('/payload/source_resources/'+str(pair[0])+'/buffProtectStacks',owner)] if pair else [],present and node is not None and val.get('native_id')==owner and same(val['buffProtectStacks'],{'type':'int','decimal':'0'})))
        king=item['items'].get('P:12');fields=king[1].get('fields',{}) if king else {};need(type(fields)is dict,'King fields object')
        for field,expected in [('invuCharges',{'type':'int','decimal':'0' if phase=='pre_prepare'else'3'}),('activations',{'type':'int','decimal':'0'}),('activationsToTrigger',{'type':'float','binary64_be':'4018000000000000'}),('protectedBuffs',{'type':'float','binary64_be':'4008000000000000'}),('manaCost',{'type':'float','binary64_be':'4010000000000000'})]:
            rows.append(direct_row('King.'+field,phase,'P:12',fields.get(field),field in fields,expected,[ref('/payload/items/'+str(king[0])+'/fields/'+field)]if king else [],field in fields and same(fields[field],expected)))
        for role in TIMER_ROLES:
            node=item['nodes'].get(role);timer=node[1]['timer'] if node else None
            if timer is not None:need(type(timer)is dict,'Timer object')
            timer=timer if timer is not None else {};n=timer.get('node',{})
            need(type(n)is dict,'Timer node')
            identity_ok=node is not None and same(n,node[1]['node']) and n.get('class')=='Timer'
            for field in ('process_mode','wait_time','time_left','one_shot','autostart','paused','stopped'):
                expected=1 if role.startswith(('king_hide:','king_drag:'))else 0
                valid = type(timer.get(field))is int and timer[field]==expected if field=='process_mode'else typed_real(timer.get(field)) if field=='wait_time'else same(timer.get(field),{'type':'float','binary64_be':'0000000000000000'})if field=='time_left'else timer.get(field) is (not role.startswith('tick:'))if field=='one_shot'else timer.get(field) is (field=='stopped')
                if field=='wait_time' and valid:valid=struct.unpack('>d',bytes.fromhex(timer[field]['binary64_be']))[0]>0
                rows.append(direct_row('Timer.'+field,phase,role,timer.get(field),field in timer,'fresh positive/configured public value; private unspecified',[ref('/payload/nodes/'+str(node[0])+'/timer/'+field,n.get('native_id'))]if node else [],identity_ok and valid))
            for field in ('native_id','role','path','name','class','positions','priority','inside_tree','ordinary_physics','internal_physics','ordinary_idle','internal_idle'):
                value=n.get(field);present=field in n
                valid = value is False if field in ('ordinary_physics','internal_physics','ordinary_idle','internal_idle')else value is True if field=='inside_tree'else type(value)is int if field=='priority'else type(value)is list and bool(value) and all(type(x)is int for x in value) if field=='positions'else (value is None or type(value)is str) if field=='role'else type(value)is str
                rows.append(direct_row('Timer.node.'+field,phase,role,value,present,'actual native node identity/configuration; fresh inactive flags',[ref('/payload/nodes/'+str(node[0])+'/timer/node/'+field,n.get('native_id'))]if node else [],identity_ok and valid))
    facts=decoded['king-input-facts.json'];kings=facts.get('kings');need(type(kings)is list,'facts kings array')
    king=kings[0]if len(kings)==1 and type(kings[0])is dict else {}
    actual_king=index['phases']['pre_activate']['nodes'].get('item:P:12')
    king_joined=actual_king is not None and same(king.get('node'),actual_king[1]['node'])
    ui_binds=[r.get('payload') for _,r in decoded['king-ui-authority.jsonl'] if r.get('kind')=='bind' and type(r.get('payload'))is dict and r['payload'].get('item_id')==king.get('node',{}).get('native_id')]
    if len(ui_binds)!=1: index['findings'].append(dict(kind='DOMAIN_REJECTED',detail='one actual King UI particle bind required'))
    for part in ('activation','drag'):
        values=king.get(part,{});need(type(values)is dict,'particle facts')
        particle_node=values.get('node',{});need(type(particle_node)is dict,'particle node')
        timer_role=('king_hide:'if part=='activation'else'king_drag:')+'P:12'
        timer_node=index['phases']['pre_activate']['nodes'].get(timer_role)
        particle_joined=king_joined and len(ui_binds)==1 and ui_binds[0].get(part+'_id')==particle_node.get('native_id') and timer_node is not None and same(values.get('timer'),timer_node[1]['timer']) and particle_node.get('class')=='Particles2D'
        for field,expected in [('visible',{'type':'bool','value':False}),('emitting',{'type':'bool','value':False}),('one_shot',{'type':'bool','value':False}),('lifetime',{'type':'float','binary64_be':'3fe6666660000000'}),('explosiveness',{'type':'float','binary64_be':'0000000000000000'}),('speed_scale',{'type':'float','binary64_be':'3ff0000000000000'})]:
            rows.append(direct_row('Particle.'+part+'.'+field,'pre_activate','P:12',values.get(field),field in values,expected,[dict(file='king-input-facts.json',pointer='/kings/0/'+part+'/'+field)],same(values.get(field),expected)and king.get('instance')=='P:12'and particle_joined))
    timers=facts.get('timers',{});need(type(timers)is dict,'five Timer fact map')
    if set(timers)!=set(FIVE_TIMER_ROLES):index['findings'].append(dict(kind='DOMAIN_REJECTED',detail='five Timer facts membership'))
    for role in FIVE_TIMER_ROLES:
        fact=timers.get(role,{});need(type(fact)is dict,'Timer fact')
        lineage=fact.get('lineage',{});need(type(lineage)is dict,'birth lineage object')
        node=index['phases']['pre_activate']['nodes'].get(role)
        current=fact.get('current');joined=node is not None and same(current,node[1]['timer'])
        owner_node=index['phases']['pre_activate']['nodes'].get('character:'+role[-1])if role.startswith('invu:')else actual_king if role.startswith('king_buff:')else None
        owner_id=owner_node[1]['node']['native_id']if owner_node else king.get('activation'if role.startswith('king_hide:')else'drag',{}).get('node',{}).get('native_id')
        expected_kind='Character.scene.ready'if role.startswith('invu:')else'King.scene.instance'if role.startswith('king_buff:')else'AutoHide.Timer.new'
        birth=lineage.get('birth',{})
        joined=joined and type(birth)is dict and type(birth.get('node'))is dict and lineage.get('timer_id')==node[1]['node']['native_id'] and lineage.get('owner_id')==owner_id and owner_id is not None and lineage.get('kind')==expected_kind and birth['node'].get('native_id')==node[1]['node']['native_id']
        if not joined:index['findings'].append(dict(kind='DOMAIN_REJECTED',detail='five Timer actual birth/current/owner join '+role))
        for field in ('timer_id','owner_id','kind','starts','stops','birth'):
            value=lineage.get(field);valid=type(value)is int and value==0 if field=='starts'else type(value)is int and value>=0 if field=='stops'else type(value)is dict if field=='birth'else type(value)is str
            rows.append(direct_row('Timer.lineage.'+field,'pre_activate',role,value,field in lineage,'observed birth/current ledger only; does not prove private constructor',[dict(file='king-input-facts.json',pointer='/timers/'+role+'/lineage/'+field)],valid and joined))
        rows.append(direct_row('Timer.private_provenance_label','pre_activate',role,fact.get('private_provenance'),'private_provenance'in fact,'source_constructor_minus_one_no_start_not_public_zero_inference',[dict(file='king-input-facts.json',pointer='/timers/'+role+'/private_provenance')],joined and fact.get('private_provenance')=='source_constructor_minus_one_no_start_not_public_zero_inference'))
    return rows


def audit_source_chain(index, direct, source_controls):
    rows=[]
    relevant=[row for name,row in STATIC_PINS.items() if name.endswith(('Core/Character.gd','Core/Game.gd','Items/Item.gd','Items/Exclusive/KingGoobert.gd','Utility/AutoHideParticles.gd','Core/Buff.gd','CombatTimer.gd','.tscn'))]
    for phase,_ in PHASES:
        groups=[('Character.'+field,side,['actual Character allocation branch (PLAYER reuse possible)','complete prepare and intervening-writer closure'])for side in ('P','O')for field in ('invulnerable','invulnerabilityItem','invulBubbleVisible')]
        groups += [('King.'+field,'P:12',['actual fresh constructor/scene configuration at this phase','complete setState/onStateChanged and no-intervening-writer proof'])for field in ('crown','light_visible','light_modulate')]
        groups += [('Timer.private_left',role,['complete native engine constructor/configuration provenance','actual no-start/all-writer coverage from allocation to this phase'])for role in TIMER_ROLES]
        for field,role,gaps in groups:
            refs=[r for row in direct if row['phase']==phase and row['side_or_role']==role for r in row['input_refs']]
            unique=[]
            for ref in refs:
                if ref not in unique:unique.append(ref)
            rows.append(dict(field_id=field,phase=phase,side_or_role=role,classification='MISSING',validation_result='UNPROVEN',proof_complete=False,
                             input_refs=unique,source_refs=relevant,unresolved=gaps,
                             missing_reason='AUDIT_RECIPE_NOT_ESTABLISHED_NOT_PROOF_ORIGINAL_DATA_ABSENT',explanation='SOURCE route candidates only. No complete reviewed derivation recipe in408. No actual initial value inferred; this does not imply recapture is necessary.'))
    return rows


def required_initial_targets():
    required = {}
    for phase, unused_site in PHASES:
        for side in ('P', 'O'):
            required[('Character.buffProtectStacks', phase, side)] = 'direct'
            for field in ('invulnerable', 'invulnerabilityItem', 'invulBubbleVisible'):
                required[('Character.'+field, phase, side)] = 'source'
        for field in ('invuCharges', 'activations', 'activationsToTrigger', 'protectedBuffs', 'manaCost'):
            required[('King.'+field, phase, 'P:12')] = 'direct'
        for field in ('crown', 'light_visible', 'light_modulate'):
            required[('King.'+field, phase, 'P:12')] = 'source'
        for role in TIMER_ROLES:
            for field in ('process_mode', 'wait_time', 'time_left', 'one_shot', 'autostart', 'paused', 'stopped'):
                required[('Timer.'+field, phase, role)] = 'direct'
            for field in ('native_id', 'role', 'path', 'name', 'class', 'positions', 'priority', 'inside_tree',
                          'ordinary_physics', 'internal_physics', 'ordinary_idle', 'internal_idle'):
                required[('Timer.node.'+field, phase, role)] = 'direct'
            required[('Timer.private_left', phase, role)] = 'source'
    for part in ('activation', 'drag'):
        for field in ('visible', 'emitting', 'one_shot', 'lifetime', 'explosiveness', 'speed_scale'):
            required[('Particle.'+part+'.'+field, 'pre_activate', 'P:12')] = 'direct'
    for role in FIVE_TIMER_ROLES:
        for field in ('timer_id', 'owner_id', 'kind', 'starts', 'stops', 'birth'):
            required[('Timer.lineage.'+field, 'pre_activate', role)] = 'direct'
        required[('Timer.private_provenance_label', 'pre_activate', role)] = 'direct'
    return required


def assess_initial_feasibility(rows, findings):
    need(type(rows) is list and type(findings) is list, 'assessment row/finding arrays')
    required = required_initial_targets()
    seen = set()
    for row in rows:
        need(type(row) is dict, 'assessment row object')
        fields = ('field_id', 'phase', 'side_or_role', 'classification', 'validation_result')
        need(all(type(row.get(field)) is str for field in fields) and
             type(row.get('proof_complete')) is bool, 'assessment strict strings/BOOL proof')
        key = (row['field_id'], row['phase'], row['side_or_role'])
        need(key in required and key not in seen, 'known unique required assessment target')
        seen.add(key)
        classification, validation, complete = row['classification'], row['validation_result'], row['proof_complete']
        need(classification in ('DIRECT_OBSERVATION', 'SOURCE_DERIVED', 'MISSING') and
             validation in ('SUPPORTED', 'REJECTED', 'UNPROVEN'), 'allowed assessment states')
        need(classification != 'SOURCE_DERIVED', 'zero reviewed SOURCE derivation recipes; caller flags cannot prove a chain')
        need(required[key] == 'direct' or classification == 'MISSING', 'SOURCE-only target cannot be directly observed, including private Timer')
        if classification == 'MISSING':
            need(validation == 'UNPROVEN' and complete is False, 'missing target stays unproven/incomplete')
        need(complete is False or validation == 'SUPPORTED', 'complete proof requires supported validation')
    need(seen == set(required), 'complete exact required field/phase/role set')
    for finding in findings:
        exact(finding, ('kind', 'detail'), 'assessment finding')
        need(finding['kind'] == 'DOMAIN_REJECTED' and type(finding['detail']) is str, 'known domain rejection finding')
    if any(row['validation_result']=='REJECTED'for row in rows)or any(x['kind']=='DOMAIN_REJECTED'for x in findings):
        status='REJECTED_INITIAL_DOMAIN'
    elif any(row['classification']=='MISSING'or row['validation_result']!='SUPPORTED'or row['proof_complete']is not True for row in rows):
        status='BLOCKED_INITIAL_SOURCE_GAPS'
    else:
        status='FEASIBLE_PENDING_FULL_STRUCTURAL_VALIDATION'
    return dict(schema='phase408-initial-source-feasibility/1',status=status,fullschema='NOT_VALIDATED',
                source_derived_recipes_implemented=0,field_count=len(rows),classifications={k:sum(r['classification']==k for r in rows)for k in ('DIRECT_OBSERVATION','SOURCE_DERIVED','MISSING')},
                rejected_fields=sum(r['validation_result']=='REJECTED'for r in rows),models=0,inputbuild=0,projection=0,old_SUT_calls=0,schema_calls=0,
                genuine_input_accepted=False,King_admitted=False,reader361='CLOSED',model356='CLOSED')


def save_new(path, value):
    raw=(json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()
    need(len(raw)<=64*1024*1024,'bounded report artifact')
    unlinked(path)
    with path.open('xb') as stream:
        stream.write(raw);stream.flush();os.fsync(stream.fileno())
    expected=dict(path=path.name,size=len(raw),sha256=hashlib.sha256(raw).hexdigest())
    readback=read_regular(path,expected,64*1024*1024,[])
    need(readback==raw,'strict output physical/byte readback')
    return expected


def seal_audit_once(authority, report, rows, findings, io, error, violations):
    output=authority['output'];before=list(io);after=[]
    try:
        checked=set()
        for row in before:
            if row['path']in checked:continue
            checked.add(row['path']);p=Path(row['path'])
            read_regular(p,dict(path=row['path'],size=row['size'],sha256=row['sha256']),TOTAL_BYTES,after)
    except Exception:
        if error is None:error=traceback.format_exc()
        report=dict(schema='phase408-initial-source-feasibility/1',status='FAILED_SOURCE_INTEGRITY',fullschema='NOT_VALIDATED')
    owner=[]
    artifacts={'report.json':report,'rawtyped-field-index.json':rows,'identity-domain-findings.json':findings,
               'io-observations.json':dict(before=before,readback=after,violations=violations),
               'source-references.json':dict(source_freeze=authority['source_freeze'],source_owner=authority['source_owner'],static_pins=STATIC_PINS),
               'summary.json':dict(status=report['status'],audit_invocations=1,new_audit_module_execution=1,old_SUT_imports=0,old_SUT_calls=0,schema_calls=0,models=0,inputbuild=0,bundle=0,projection=0,native=0,restore=0,READY=0,fullschema='NOT_VALIDATED',first_error=error,automatic_retry=False,no_more_writes_after_owner=True)}
    for name,value in artifacts.items():owner.append(save_new(output/name,value))
    save_new(output/'owned-files.json',dict(schema='phase408-actual-initial-audit-owner/1',files=owner,no_more_writes=True))
    fd=os.open(output,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
    return report['status']


def run_audit(root, release_descriptor):
    io=[];violations=[]
    authority=verify_audit_release(root,release_descriptor,io)
    install_io_guard(authority['allowed'],authority['output'],violations)
    authority['output'].mkdir()
    rows=[];findings=[];error=None
    try:
        decoded=read_lawful12_once(authority,io)
        index=index_initial_observations(decoded)
        findings=index['findings']
        rows=audit_direct_fields(index,decoded)
        rows+=audit_source_chain(index,rows,authority['controls'])
        report=assess_initial_feasibility(rows,findings)
    except Exception:
        error=traceback.format_exc()
        report=dict(schema='phase408-initial-source-feasibility/1',status='FAILED_SOURCE_INTEGRITY',fullschema='NOT_VALIDATED')
    status=seal_audit_once(authority,report,rows,findings,io,error,violations)
    print(json.dumps(dict(status=status,output=str(authority['output']),models=0,inputbuild=0)))
    return 1 if status=='FAILED_SOURCE_INTEGRITY'else 0


def main():
    parser=argparse.ArgumentParser(description='SOURCE-bound readonly initial presence/route audit; no model or full schema')
    parser.add_argument('--source-root',type=Path,required=True)
    parser.add_argument('--release',required=True)
    parser.add_argument('--release-size',type=int,required=True)
    parser.add_argument('--release-sha256',required=True)
    args=parser.parse_args()
    return run_audit(args.source_root,dict(path=args.release,size=args.release_size,sha256=args.release_sha256))


if __name__=='__main__':
    sys.exit(main())
