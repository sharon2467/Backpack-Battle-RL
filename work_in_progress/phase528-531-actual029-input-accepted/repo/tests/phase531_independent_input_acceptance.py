"""Read-only direct comparisons of sealed actual INPUT outputs; no Source imports."""
from pathlib import Path
import collections
import copy
import hashlib
import json
import struct
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/phase531-independent-actual-input-acceptance-first-001'
BUILD = ROOT / 'data/phase511-case029-actual-input-repaired-001'
REQUEST = ROOT / 'data/phase529-actual029-repaired-input-request/input-request.json'
ZERO = {'type': 'float', 'binary64_be': '0000000000000000'}
MINUS = {'type': 'float', 'binary64_be': 'bff0000000000000'}
BUFFS = ('Block', 'Lucky', 'Regeneration', 'Vampirism', 'Spikes', 'Mana', 'Empower', 'Heat', 'Poison', 'Blind', 'Cold')


def same(a, b):
    return json.dumps(a, sort_keys=True, separators=(',', ':'), allow_nan=False) == json.dumps(b, sort_keys=True, separators=(',', ':'), allow_nan=False)


def need(value, label):
    if not value:
        raise AssertionError(label)


def pin(path):
    raw = path.read_bytes()
    return {'path': str(path), 'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def checked(row):
    path = Path(row['path'])
    if not path.is_absolute():
        path = ROOT / path
    raw = path.read_bytes()
    need(len(raw) == row['size'] and hashlib.sha256(raw).hexdigest() == row['sha256'], 'descriptor ' + str(path))
    return raw


def pointer(value, path):
    for part in path.split('/')[1:]:
        part = part.replace('~1', '/').replace('~0', '~')
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def role_name(raw):
    if raw.startswith('buff:'):
        parts = raw.split(':')
        return ':'.join(parts[:2] + [BUFFS[int(parts[2]) - 100]])
    return raw


def main():
    need(not OUT.exists(), 'new report directory')
    OUT.mkdir()
    report = {'status': 'STARTED', 'checks': {}, 'raw_input_files_read': 0,
              'raw_input_bytes_read': 0, 'raw_input_JSON_decodes': 0,
              'Source_imports': 0, 'schema_calls': 0, 'bridge_calls': 0,
              'builds': 0, 'model': 0, 'Native': 0, 'Expected_payload_reads': 0,
              'pool_operations': 0}
    started = time.monotonic()
    stage = 'output seals'
    code = 1
    try:
        owner = json.loads((BUILD / 'owned-files.json').read_bytes())
        values = {}
        for row in owner['files']:
            raw = checked(row)
            values[Path(row['path']).name] = json.loads(raw)
        seal = values['input-seal.json']
        for row in seal['files']:
            checked(row)
        need(seal['runtime_validated'] is False and seal['model_release'] is False, 'input-only seal')
        request = json.loads(REQUEST.read_bytes())
        need(pin(REQUEST)['sha256'] == '6ba42c7346d23fdd559ba57ce51c38697a141f96fbfa045d3b3643aea45649a7', 'Root request pin')
        rb = values['input-readback.json']
        need(same(rb['source_before'], rb['source_after']) and same(rb['input_before'], rb['input_after']), 'full before/after identity')
        need(same(rb['input_before'], list(request['input_descriptors'].values())), 'exact request12 order/descriptors')
        for row in rb['source_after']:
            checked(row)
        before = values['inputs-before-interpretation.json']
        need(same(before['source'], rb['source_before']) and same(before['input'], rb['input_before']), 'before interpretation seal join')
        report['checks']['seals'] = {'owner_payloads': len(owner['files']), 'seal_payloads': len(seal['files']), 'source_records': len(rb['source_after']), 'input_records': len(rb['input_before'])}
        stage = 'lawful INPUT identity and JSON reads'
        raw_inputs = {}
        for name, row in request['input_descriptors'].items():
            raw = checked(row)
            report['raw_input_files_read'] += 1
            report['raw_input_bytes_read'] += len(raw)
            raw_inputs[name] = [json.loads(line) for line in raw.splitlines()] if name.endswith('.jsonl') else json.loads(raw)
            report['raw_input_JSON_decodes'] += 1
        receipt, proof, bundle, witness = (values[n] for n in ('initial-receipt.json', 'input-proof.json', 'input-bundle.json', 'prepared-witness.json'))
        all_docs = dict(raw_inputs, **{'initial-receipt.json': receipt})
        records = raw_inputs['observer7-input.jsonl']

        def ref_value(ref):
            obj = all_docs[ref['file']]
            if 'line' in ref:
                obj = obj[ref['line'] - 1]
                if 'sequence' in ref:
                    need(obj['sequence'] == ref['sequence'], 'reference physical line/sequence')
            elif 'sequence' in ref and isinstance(obj, list):
                matching = [x for x in obj if x['sequence'] == ref['sequence']]
                need(len(matching) == 1, 'unique reference sequence')
                obj = matching[0]
            return pointer(obj, ref['pointer']) if 'pointer' in ref else obj

        cut_rows = {}
        for phase, site in [('pre_prepare', 'prepareItems'), ('pre_activate', 'activateItems')]:
            found = [(i, x) for i, x in enumerate(records, 1) if x.get('site') == 'Core/Game.gd::' + site and x.get('edge') == 'checkpoint']
            need(len(found) == 1, 'unique actual ' + phase)
            cut_rows[phase] = found[0]
        report['actual_cuts'] = {k: {'line': v[0], 'sequence': v[1]['sequence']} for k, v in cut_rows.items()}
        stage = '460 receipt values and64Timer witnesses'
        index = {}
        derived = collections.Counter()
        direct = 0
        for row in receipt['values']:
            key = tuple(row['key'])
            need(key not in index, 'duplicate receipt key')
            index[key] = row
            linked = [ref_value(ref) for ref in row['input_refs']]
            need(linked, 'missing field origins')
            if row['classification'] == 'DIRECT_OBSERVATION':
                need(all(same(x, row['actual_value']) for x in linked), 'direct origin mismatch ' + str(key))
                direct += 1
            else:
                need(row['classification'] == 'SOURCE_DERIVED', 'unknown value classification')
                derived[key[0]] += 1
                expected = MINUS if key[0] == 'Timer.private_left' else ({'type': 'bool', 'value': False} if key[0] == 'Character.invulnerable' else {'type': 'null'})
                need(same(row['actual_value'], expected), 'derived typed value ' + str(key))
        need(derived == {'Timer.private_left': 64, 'Character.invulnerable': 4, 'Character.invulnerabilityItem': 4} and direct == 388, '64+8 and direct388')
        ids_by_phase = {}
        for tw in receipt['timer_witnesses']:
            phase, role = tw['phase'], tw['role']
            timer = ref_value(tw['timer_refs'][0]); parent = ref_value(tw['owner_ref']); node = timer['node']
            for ref in tw['timer_refs']:
                need(same(ref_value(ref), timer), 'dual Timer references')
            need(same(node, tw['native_node']) and node['native_id'] == tw['native_id'] and parent['native_id'] == tw['parent_id'], 'Timer/parent native identities')
            need(node['class'] == 'Timer' and parent['class'] == 'Node2D' and node['inside_tree'] is True and parent['inside_tree'] is True, 'native Timer tree/class')
            need(node['path'] == parent['path'] + '/' + node['name'] and node['positions'][:-1] == parent['positions'], 'current-cut parent path/position')
            need(all(type(node[k]) is bool and node[k] is False for k in ['ordinary_physics','internal_physics','ordinary_idle','internal_idle']), 'inactive flags')
            need(type(timer['process_mode']) is int and timer['process_mode'] == 0 and timer['paused'] is False and timer['autostart'] is False, 'G02 actual mode/paused premises')
            need(timer['stopped'] is True and same(timer['time_left'], ZERO), 'public consistency only')
            need(same(tw['typed_witness'], {k: timer[k] for k in tw['typed_witness']}), 'typed witness original fields')
            ids_by_phase.setdefault(phase, {})[role] = node['native_id']
            need(index[('Timer.private_left', phase, role)]['rule'] == 'INACTIVE_PROCESSING_INVARIANT', 'private rule source')
        need(len(receipt['timer_witnesses']) == 64 and all(len(x) == 32 for x in ids_by_phase.values()) and ids_by_phase['pre_prepare'] == ids_by_phase['pre_activate'], '32 actual identities at2cuts')
        stage = 'actual two birth ledgers and Character8'
        facts = raw_inputs['king-input-facts.json']
        need(facts['kings'] == [] and facts['schema'] == 'phase502-zero-king-input-facts/1', 'zeroKing facts')
        for role, entry in receipt['lifetime_witnesses'].items():
            ledger = ref_value(entry); fact = facts['timers'][role]
            need(same(ledger, entry['lineage']) and same(ledger, fact['lineage']), 'unmodified recorded birth ledger')
            need(type(ledger['starts']) is int and ledger['starts'] == 0 and type(ledger['stops']) is int and ledger['stops'] >= 0, 'lifetime no-start')
            side = role.split(':')[1]
            for phase, (_, cut) in cut_rows.items():
                nodes = {n['role']: n for n in cut['payload']['nodes']}
                timer = nodes[role]['timer']; parent = nodes['character:' + side]['node']; born = ledger['birth']; bn = born['node']
                need(ledger['timer_id'] == timer['node']['native_id'] == bn['native_id'] and ledger['owner_id'] == parent['native_id'], 'birth/current UID owner join')
                need(ledger['kind'] == 'Character.scene.ready' and bn['role'] is None and bn['class'] == 'Timer' and bn['inside_tree'] is True, 'birth kind class role')
                need(bn['path'] == timer['node']['path'] == parent['path'] + '/' + bn['name'], 'birth/current owner path')
                need(all(type(bn[k]) is bool and bn[k] is False for k in ['ordinary_physics','internal_physics','ordinary_idle','internal_idle']), 'birth inactive flags')
                for name in ['process_mode','wait_time','one_shot','autostart','paused','stopped','time_left']:
                    need(same(born[name], timer[name]), 'birth config ' + name)
                need(same(fact['current'], timer), 'current fact/cut equality')
                for name in ['Character.invulnerable', 'Character.invulnerabilityItem']:
                    val = index[(name, phase, side)]
                    need(val['rule'] == 'CHARACTER_DEFAULT_CALLER_CLOSURE_LIFETIME_ZERO_START' and len(val['input_refs']) == 2, 'Character rule and actual ledger origins')
        report['checks']['initial_receipt'] = {'derived': dict(derived), 'direct': direct, 'Timer_witnesses': 64, 'birth_ledgers': 2, 'P_birth_positions_preserved': facts['timers']['invu:P']['lineage']['birth']['node']['positions'], 'current_P_positions': facts['timers']['invu:P']['current']['node']['positions']}
        stage = 'runtime graph, Timer fields and origins'
        runtime = bundle['runtime']; pre = cut_rows['pre_prepare'][1]; act = cut_rows['pre_activate'][1]
        need(len(runtime['processing_nodes']) == 67 and len(runtime['nodes']) == 66 and len(runtime['timer_initial']) == 32, 'raw32/67/66')
        raw_nodes = act['payload']['nodes']
        role_uid = {}
        for raw, node in zip(raw_nodes, runtime['processing_nodes'], strict=True):
            expected = copy.deepcopy(raw['node']); expected['role'] = role_name(raw['role'])
            need(same(expected, node), 'processing original fields/order ' + raw['role'])
            role_uid[raw['node']['role']] = raw['node']['native_id']
        configs = [n for n in runtime['processing_nodes'] if n['role'] != 'root_viewport']
        for raw, config in zip(configs, runtime['nodes'], strict=True):
            need(all(same(raw[k], config[k]) for k in ['role','path','positions','priority']), 'config fields')
            need(config['kind'] == ('timer' if raw['class'] == 'Timer' else 'ordinary'), 'config class kind')
        for raw_role in ids_by_phase['pre_activate']:
            output = runtime['timer_initial'][role_name(raw_role)]
            for field, target in [('wait_time','wait_time_bits'),('one_shot','one_shot'),('process_mode','process_mode'),('autostart','autostart'),('paused','paused'),('private_left','private_left_bits')]:
                actual = index[('Timer.' + field, 'pre_activate', raw_role)]['actual_value']
                need(same(output[target], actual['binary64_be'] if target.endswith('_bits') else actual), 'runtime Timer field')
        for side in ('P','O'):
            for name in ['invulnerable','invulnerabilityItem','buffProtectStacks']:
                actual = index[('Character.'+name,'pre_activate',side)]['actual_value']
                expected = None if actual['type']=='null' else int(actual['decimal']) if actual['type']=='int' else actual['value']
                need(same(runtime['initial_characters'][side][name],expected),'runtime Character field')
        for phase, order_key, site in [('pre_prepare','prepare_order','prepareItems'),('pre_activate','activate_order','activateItems')]:
            entries = [x for x in records if x.get('site')=='Core/Game.gd::'+site and x.get('edge')=='enter']
            need(len(entries)==1, 'unique actual entry')
            entry=entries[0]; cut=cut_rows[phase][1]
            need(entry['sequence']==cut['sequence']+1, 'checkpoint entry adjacency')
            need(all(same(entry['stamp'][k],cut['stamp'][k]) for k in ['physics_frame','idle_frame','util_time','combat_time']), 'checkpoint entry same clock')
            args={x['key']['value']:x['value'] for x in entry['payload']['arguments']['entries']}
            refs=args['items']['values']
            need([x['role'] for x in refs]==runtime[order_key] and len(refs)==29, 'actual item order')
            need(all(role_uid[x['role']]==x['native_id'] and x['class']=='RigidBody2D' for x in refs), 'ordered item UID')
            if phase=='pre_activate':
                need(runtime['checkpoint']=={'util_time_bits':entry['stamp']['util_time']['binary64_be'],'combat_time_bits':entry['stamp']['combat_time']['binary64_be'],'source_phase':entry['stamp']['phase']}, 'runtime checkpoint direct')
        env=act['payload']['environment']
        need(type(runtime['environment']['fps']) is int and runtime['environment']['fps']==int(env['fps']['decimal']), 'environment FPS')
        need(struct.pack('>d',runtime['environment']['scale']).hex()==env['scale']['binary64_be'] and runtime['environment']['paused'] is env['paused']['value'], 'environment scale/paused')
        need(len(runtime['initial_items'])==29, '29 initial items')
        for raw in pre['payload']['items']:
            initial=runtime['initial_items'][raw['instance']]
            for field in ['lastActivationTime','lastTriggerTime']:
                need(initial[field+'_bits']==raw['fields'][field]['binary64_be'], 'initial limiter REAL bits')
            for field in ['activationsThisFrame','triggersThisFrame']:
                need(type(initial[field]) is int and initial[field]==int(raw['fields'][field]['decimal']), 'initial limiter INT')
            for field in ['dragged','moveback_running']:
                need(type(initial[field]) is bool and initial[field] is raw[field]['value'], 'initial item BOOL')
            need(initial['cache_fresh'] is True and same(raw['cachedAffectedItems'],{'type':'dictionary','entries':[]}), 'observed empty precache predicate')
        for key, origin in proof['field_origins'].items():
            if origin.get('file') == 'initial-receipt.json' and 'pointer' in origin:
                actual = ref_value(origin)
                ordinal = int(origin['pointer'].split('/')[2]); row = receipt['values'][ordinal]
                need(same(origin['key'],row['key']) and same(origin['input_refs'],row['input_refs']) and origin['rule']==row['rule'] and origin['classification']==row['classification'], 'receipt-origin metadata '+key)
            elif 'file' in origin and origin['file'] in all_docs:
                obj = ref_value(origin)
                if 'raw_role' in origin:
                    need(any(n['role']==origin['raw_role'] for n in obj['payload']['nodes']), 'processing origin role')
                if 'instance' in origin:
                    need(any(n['instance']==origin['instance'] for n in obj['payload']['items']), 'initial item origin')
            for ref in origin.get('input_refs',[]):
                ref_value(ref)
        need(len(proof['field_origins']) == 345, 'field-origin count')
        report['checks']['runtime_origins'] = {'processing':67,'configs':66,'timers':32,'field_origins':345}
        stage = 'complete primitive and clock mapping'
        primitives = raw_inputs['observer7-primitives.jsonl']
        seq = [x['sequence'] for x in primitives]
        need(seq == sorted(set(seq)) and same(seq,proof['primitive_original_sequences']) and same(seq,proof['field_origins']['bundle.draws']['sequences']), 'all physical primitive sequences')
        for row, draw in zip(primitives,bundle['draws'],strict=True):
            payload=row['payload'];need(row['sequence']>act['sequence'] and draw['kind']==payload['kind'] and draw['label']==payload['label'],'primitive identity/order')
            if payload['kind']=='randi_range':
                need(all(a['type']=='int' for a in payload['args']) and payload['value']['type']=='int','integer primitive rawtypes')
                need(draw['args']==[int(a['decimal']) for a in payload['args']] and type(draw['value']) is int and draw['value']==int(payload['value']['decimal']),'integer primitive exact values')
            else:
                need(payload['kind'] in ('randf','randf_range') and payload['value']['type']=='float','REAL primitive type')
                for arg,bits in zip(payload['args'],draw['args'],strict=True):
                    if arg['type']=='float':need(bits==arg['binary64_be'],'REAL arg bits')
                    else:need(row['site']=='Utility/Util.gd::roll' and same(arg,{'type':'int','decimal':'0'}) and bits=='0000000000000000','only Source roll INT0 coercion')
                need(draw['value_bits']==payload['value']['binary64_be'],'REAL return bits')
        header=raw_inputs['king-clock-checkpoint.json'];clock=runtime['frame_clock']
        need(same({k:v for k,v in clock.items() if k!='passes'},header) and same(clock['passes'],raw_inputs['king-clock-passes.jsonl']),'all clock header and passes exact')
        need(bundle['synthetic_seed'] is None,'no synthetic seed')
        report['checks']['stream']={'primitive_rows':len(primitives),'clock_passes':len(clock['passes']),'primitive_first_sequence':seq[0],'primitive_last_sequence':seq[-1],'all_typed_args_values_order_checked':True}
        stage = 'branch witness and prepared ordered cache'
        branch=proof['branch_witness'];selected=[(i,x) for i,x in enumerate(primitives,1) if x['site'].startswith('Items/Item.gd::adjustCooldown:')]
        for (line,row),w in zip(selected,branch['witnesses'],strict=True):
            role=row['payload']['label'].removeprefix('cooldown:')
            need(w['line']==line and w['sequence']==row['sequence'] and w['role']==role and w['native_owner']==role_uid[role] and w['site']==row['site'],'branch original site/owner')
            need(w['startup']==same(row['stamp']['combat_time'],ZERO),'branch startup marker')
            need(row['site'].endswith(':other') if role.startswith('P:') else row['site'].endswith(':belowMasterOpponent'),'fixed actual branch')
        need(branch['value'] is True and bundle['fixture']['below_master'] is True and any(w['role'].startswith('O:') and w['startup'] for w in branch['witnesses']),'opponent startup predicate witness')
        for phase,observations in receipt['prepare_observations'].items():
            need(len(observations)==29,'29prepared observations')
            for role,obs in observations.items():
                raw=ref_value(obs['input_ref']);need(raw['instance']==role,'item original role')
                for name in ['cachedAffectedItems','currentAffectedItems']:
                    need(same(obs[name],raw[name]) and same(raw[name],raw['fields'][name]),'cache dual/direct '+role)
                if 'goobert_state' in obs:need(all(same(v,raw['fields'][k]) for k,v in obs['goobert_state'].items()),'Basic exact fields')
                if 'stackTypes' in obs:need(same(obs['stackTypes'],raw['fields']['stackTypes']),'Sapphire exact fields')
                if phase!='pre_activate':continue
                w=witness['items'][role];need(all(same(v,w[k]) for k,v in obs.items()) and w['native_id']==role_uid[role],'prepared witness copy')
                for col,out in zip(raw['cachedAffectedItems']['entries'],w['ordered_cache_aliases'],strict=True):
                    refs=col['value']['values'];need(same(col['key'],out['color']) and [x['role'] for x in refs]==out['ordered_roles'] and [x['native_id'] for x in refs]==out['ordered_native_ids'],'ordered cache identity')
                    for x in refs:need(role_uid[x['role']]==x['native_id'] and x['class']=='RigidBody2D','cache reference binding')
                for col,out in zip(raw['currentAffectedItems']['entries'],w['ordered_current_aliases'],strict=True):
                    need(same(col['key'],out['color']),'current color')
                    for x,m in zip(col['value']['entries'],out['ordered_members'],strict=True):
                        need(m['role']==x['key']['role'] and m['native_id']==x['key']['native_id']==role_uid[m['role']] and same(m['value'],x['value']),'ordered current binding')
        expected6={'type':'array','values':[{'type':'int','decimal':str(i)} for i in (101,102,103,104,106,107)]}
        need(same(witness['items']['P:14']['stackTypes'],expected6),'Sapphire six ordered types')
        need(same(witness['items']['P:9']['goobert_state']['activationsToTrigger'],{'type':'float','binary64_be':'4014000000000000'}),'Basic REAL threshold5')
        need(witness['status']=='OBSERVED_INPUT_NOT_MODEL_EQUIVALENCE' and witness['gate']=='EXTERNAL_SAME_INSTANCE_BUSINESS_PREPARE_GATE_REQUIRED_BEFORE_ACTIVATION','B1 not claimed')
        report['checks']['prepared']={'items':29,'two_cut_observations':58,'Basic_role':'P:9','Sapphire_role':'P:14','all_ordered_cache_members_preserved':True,'branch_rows':len(selected),'below_master':True,'business_B1_executed':False}
        stage = 'fixture direct geometry and final boundary'
        for side,name in [('P','player_fixture.json'),('O','fixture.json')]:
            raw=raw_inputs[name];output=next(x for x in bundle['fixture']['sides'] if x['side']==side)
            need(raw['class']==output['character_class'] and raw['health']==output['hp'] and raw['stamina']==output['stamina'],'fixture resources')
            need(same(raw['items'],[{k:v for k,v in item.items() if k!='instance_id'} for item in output['items']]),'fixture geometry order')
        report['status']='PASS_ACTUAL_INPUT_ONLY_NOT_RUNTIME_VALIDATED'
        report['build_artifacts']={name:pin(BUILD/name) for name in ['input-bundle.json','input-proof.json','initial-receipt.json','prepared-witness.json','input-seal.json','owned-files.json']}
        report['remaining']=['Actual runtime validator/constructor interface acceptance','Same-instance consumed prepare/cache B1 equivalence before activation','Ordinary callback/noninterference applicability and launcher/output mapping','Separately authorized one candidate model run and strict8 comparison']
        report['limits']=['Accepted prior G02/Character Source domains remain conditional; no publiczero/private direct observation claim.','No native same-seed law, complete engine or formal75 upgrade.','Native capture nonclean-exit diagnostic retained; no new native execution.']
        code=0
    except BaseException as error:
        report['status']='FIRST_DIFFERENCE_STOPPED'
        report['failure']={'stage':stage,'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    report['elapsed_seconds']=time.monotonic()-started
    (OUT/'result.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    (OUT/'owned-files.json').write_text(json.dumps({'schema':'phase531-independent-readonly-output-owner/1','files':[pin(OUT/'result.json')],'no_more_writes':True},indent=2)+'\n')
    print(json.dumps({'status':report['status'],'elapsed_seconds':report['elapsed_seconds'],'failure':report.get('failure')}))
    return code


if __name__=='__main__':
    raise SystemExit(main())
