from .state import strict_json_loads
"""Strict semantic comparison of existing capture and independent engine output.

This never constructs random inputs from expected events. Whole-game equivalence
is explicitly outside the result: only supported event/state fields are compared.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct

from .engine import fixture_from_custom_opponent, GENUINE_PROFILES
from .state import project_native_rule_state, restore_state_json_keys, restore_integer_table


def decode_native(value):
    if isinstance(value, list):
        return [decode_native(v) for v in value]
    if not isinstance(value, dict):
        return value
    kind = value.get("type")
    if not isinstance(kind, str):
        return {k: decode_native(v) for k, v in value.items()}
    if kind == "null":
        return None
    if kind == "int":
        return int(value["decimal"])
    if kind == "float":
        return struct.unpack(">d", bytes.fromhex(value["binary64_be"]))[0]
    if kind in ("bool", "string"):
        return value["value"]
    if kind == "array":
        return [decode_native(v) for v in value["values"]]
    if kind == "dictionary":
        result = {}
        for row in value["entries"]:
            key = decode_native(row["key"])
            if type(key) not in (str, int) or key in result:
                raise ValueError("unsupported dictionary key or duplicate key")
            result[key] = decode_native(row["value"])
        return result
    if kind == "StatHistory":
        return {key: decode_native(value[key]) for key in ("event_numbers", "values")}
    if kind == "instance_reference":
        return value["id"]
    if kind == "event_reference":
        return int(value["id"])
    if kind == "Vector2":
        return dict(x=decode_native(value["x"]), y=decode_native(value["y"]))
    raise ValueError(f"unsupported native variant {kind!r}")


def project_events(rows, include_sequence=True):
    result = []
    fields = ("id", "timestamp", "parent", "origin", "target", "type", "params", "snapshot")
    if include_sequence:
        fields = ("sequence",) + fields
    for row in rows:
        event = {key: decode_native(row[key]) for key in fields}
        event["timestamp_hex"] = row["timestamp"]["binary64_be"]
        result.append(event)
    return result


def first_difference(left, right, path="$"):
    if type(left) is not type(right):
        return dict(path=path, native=left, engine=right, reason="type")
    if isinstance(left, dict):
        left_keys = {(type(key).__name__, key) for key in left}
        right_keys = {(type(key).__name__, key) for key in right}
        if left_keys != right_keys:
            return dict(path=path, native_keys=sorted(map(repr, left_keys)),
                        engine_keys=sorted(map(repr, right_keys)), reason="dictionary_key_types_or_members")
        priority = ["sequence", "id", "timestamp_hex", "timestamp", "parent", "origin", "target", "type", "params", "snapshot"]
        keys = [key for key in priority if key in left or key in right]
        keys += sorted((left.keys() | right.keys()) - set(keys))
        for key in keys:
            if key not in left or key not in right:
                return dict(path=path + "." + str(key), native=left.get(key), engine=right.get(key), reason="missing_key")
            difference = first_difference(left[key], right[key], path + "." + str(key))
            if difference:
                return difference
    elif isinstance(left, list):
        for index, (a, b) in enumerate(zip(left, right)):
            difference = first_difference(a, b, f"{path}[{index}]")
            if difference:
                return difference
        if len(left) != len(right):
            return dict(path=path, native_length=len(left), engine_length=len(right), reason="length")
    elif isinstance(left, float):
        if struct.pack(">d", left) != struct.pack(">d", right):
            return dict(path=path, native=left, engine=right, reason="float_bits")
    elif left != right:
        return dict(path=path, native=left, engine=right, reason="value")
    return None


def project_histories(native_histories):
    return decode_native(native_histories)


def restore_history_json_keys(histories):
    """Restore only schema-defined integer-key tables after JSON object encoding.

    Called only for durable engine JSON inputs; raw native dictionary key types
    remain verified and untouched. In-memory model uses native integer keys.
    """
    from copy import deepcopy
    histories = deepcopy(histories)
    for logger in histories['stat_loggers']:
        for name in ('characterStatHistories', 'stackHistories'):
            table = logger[name]
            logger[name] = restore_integer_table(table)
        logger['metricHistories'] = [restore_integer_table(table) for table in logger['metricHistories']]
    return histories


MIXED_PROFILE = 'observer7-074-native-v7-004-goobert-c-fixed60/1'


def project_particle_timers(native, engine_final):
    """Output-only public Timer comparison. Never reconstruct private/initial state."""
    if engine_final['runtime']['profile'] not in (MIXED_PROFILE, 'observer7-085-native-v7-005-rainbow-fixed60/1', 'observer7-095-native-v7-006-goobert-d-fixed60/1', 'observer7-185-headless-default-layout/1', 'observer7-270-headless-logic-random-goobert-layout/1', 'observer7-298-headless-support68-layout/1', 'observer7-324-headless-rainbow75-layout/1'):
        if any('observer7_timers' in item for char in native['characters'] for item in char['items']):
            raise ValueError('new Timer wrapper outside approved final-envelope profiles')
        return None
    left={};right={};seen=set()
    node_keys={'native_id','role','path','name','class','positions','priority','inside_tree','ordinary_physics','internal_physics','ordinary_idle','internal_idle'}
    timer_keys={'node','process_mode','wait_time','time_left','one_shot','autostart','paused','stopped'}
    for character in native['characters']:
        for item in character['items']:
            identity=item['instance']
            if identity in seen or identity not in engine_final['items']:raise ValueError('final Timer known unique item')
            seen.add(identity);index=engine_final['items'][identity]['item_index']
            wrapper=item.get('observer7_timers')
            if type(wrapper)is not dict or set(wrapper)!=({'particleTimer'}if index in(53,168)else set()):raise ValueError('closed final particle wrapper')
            if not wrapper:continue
            timer=wrapper['particleTimer'];role='particle:'+identity
            if type(timer)is not dict or set(timer)!=timer_keys:raise ValueError('closed final Timer fields')
            node=timer['node']
            if type(node)is not dict or set(node)!=node_keys or node['role']!=role or node['class']!='Timer' or node['name']!='ParticleTimer':raise ValueError('final particle source node identity')
            if type(node['native_id'])is not str or re.fullmatch('[1-9][0-9]*',node['native_id'])is None:raise ValueError('native Timer ID provenance')
            positions=node['positions']
            if type(positions)is not list or not positions or any(type(x)is not int for x in positions):raise ValueError('native Timer ancestor indices')
            public={key:node[key]for key in ('path','inside_tree','ordinary_physics','internal_physics','ordinary_idle','internal_idle')}
            public.update(index=positions[-1],ancestor_positions=positions,process_priority=node['priority'])
            public.update({key:timer[key]for key in timer_keys-{'node'}})
            if role not in engine_final['runtime']['timers']:raise ValueError('missing modeled particle role')
            left[role]=public;right[role]=engine_final['runtime']['timers'][role]
    if seen!=set(engine_final['items']):raise ValueError('missing final item Timer wrappers')
    if set(right)!={key for key in engine_final['runtime']['timers']if key.startswith('particle:')}:raise ValueError('complete final particle Timer roles')
    # Every wrapper was projected above. Remove only this compared envelope from
    # the copied decoded tree before the unchanged full rule-state projection.
    for character in native['characters']:
        for item in character['items']:del item['observer7_timers']
    return left,right


def project_final(native_final, engine_final):
    native = decode_native(native_final)
    particles = project_particle_timers(native,engine_final)
    left = dict(characters={}, items={}, round=native["game"]["curRound"], timestamp=native["timer"]["combatTime"],
                fatigue_counter=native["timer"]["fatigueCounter"], time_advance=native["timer"]["timeAdvance"])
    right = dict(characters={}, items={}, round=engine_final["round"], timestamp=engine_final["timestamp"],
                 fatigue_counter=engine_final["fatigue_counter"], time_advance=engine_final["time_advance"])
    left["game"] = native["game"]
    right["game"] = engine_final["game"]
    result_code = native["game"]["roundResults"][0]
    left["winner"] = {0: "P", 1: "O"}.get(result_code)
    right["winner"] = engine_final["winner"]
    if engine_final["event_bus"] is not None:
        left["event_bus"], right["event_bus"] = native["event_bus"], engine_final["event_bus"]
    char_fields = {"hp": "curHealth", "max_hp": "maxHealth", "stamina": "curStamina", "max_stamina": "maxStamina",
                   "stamina_regen": "staminaRegen", "dead": "isDead"}
    stacks = {"block": 100, "lucky": 101, "regeneration": 102, "spikes": 104, "mana": 105, "blind": 109, "heat": 107, "cold": 110}
    item_fields = {"iteration_cooldown": "iterationCooldown", "trigger_time": "triggerTime",
                   "crit_chance": "critChancePercent", "speed_scale": "speedScale", "consumed": "consumed"}
    rng_fields = {"expected_wins": "expectedWins", "wins": "wins", "balancedness": "balancedness", "last_result": "lastResult"}
    for character in native["characters"]:
        side = character["instance"]
        nchar = {key: character["fields"][source] for key, source in char_fields.items()}
        echar = {key: engine_final["characters"][side][key] for key in char_fields}
        nchar["physics_processing"] = character["physics_processing"]
        echar["physics_processing"] = engine_final["characters"][side]["physics_processing"]
        buff_table = character["buffs"]
        if isinstance(buff_table, list):
            buff_table = {row["stack_type"]: row["fields"] for row in buff_table}
        for key, stack_id in stacks.items():
            # probe-003 had one extra tagged dictionary layer; new captures do not.
            buff = buff_table.get(stack_id, buff_table.get(str(stack_id)))
            if buff is None:
                raise ValueError(f"missing native buff {stack_id}")
            if buff.get("type") == "dictionary":
                buff = decode_native(buff)
            nchar[key] = buff["current"]
            echar[key] = engine_final["characters"][side][key]
        for key, source in (("accuracy", "accuracyRng"), ("critical", "critRng")):
            nchar[key] = {k: character["balanced_rng"][source][v] for k, v in rng_fields.items()}
            echar[key] = engine_final["characters"][side][key]
        left["characters"][side], right["characters"][side] = nchar, echar
        for item in character["items"]:
            identity = item["instance"]
            nitem = {key: item["fields"][source] for key, source in item_fields.items()}
            eitem = {key: engine_final["items"][identity][key] for key in item_fields}
            nitem.update(owner_type=item["fields"]["ownerType"], orientation=item["fields"]["faceDirection"],
                         physics_processing=item["physics_processing"],
                         cells=sorted([[point["x"], point["y"]] for point in item["fields"]["occupiedCells"]]))
            eitem.update(owner_type=engine_final["items"][identity]["owner_type"],
                         orientation=engine_final["items"][identity]["orientation"],
                         physics_processing=engine_final["items"][identity]["physics_processing"],
                         cells=sorted([[float(x), float(y)] for x, y in engine_final["items"][identity]["cells"]]))
            nitem["damage_range"] = item["damage_rng"]
            eitem["damage_range"] = engine_final["items"][identity]["damage_range"]
            left["items"][identity], right["items"][identity] = nitem, eitem
    if particles is not None:
        left["observer7_timers"],right["observer7_timers"] = particles
    left["native_rule_state"] = project_native_rule_state(native)
    right["native_rule_state"] = engine_final["native_rule_state"]
    return left, right


def fixture_from_capture(capture_dir):
    capture_dir = Path(capture_dir)
    manifest = strict_json_loads((capture_dir / 'native_manifest.json').read_text())
    opponent = strict_json_loads((capture_dir / 'fixture.json').read_text())
    player = None
    if manifest['entry'] == 'migrated_custom_opponent_with_native_player_fixture_v1':
        player = strict_json_loads((capture_dir / 'player_fixture.json').read_text())
        if not isinstance(player, dict):
            raise ValueError('controlled player fixture must be an object')
    elif manifest['entry'] != 'migrated_custom_opponent':
        raise ValueError('unknown native fixture entry')
    fixture = fixture_from_custom_opponent(opponent, player)
    fixture['below_master'] = manifest['run_context']['league'] < 5
    return fixture


def validate_provenance(capture_dir):
    """Recheck byte-locked host validation and explicit supported runtime contract."""
    errors = []
    required = ("host_validation.json", "host_manifest.json", "process_result.json")
    if any(not (capture_dir.parent / name).is_file() for name in required):
        return dict(valid=False, errors=["missing_host_validation_or_provenance"])
    host = strict_json_loads((capture_dir.parent / "host_validation.json").read_text())
    manifest = strict_json_loads((capture_dir.parent / "host_manifest.json").read_text())
    process = strict_json_loads((capture_dir.parent / "process_result.json").read_text())
    if not host.get("capture_complete") or host.get("errors"):
        errors.append("host_capture_validation_failed")
    for name in ("native_manifest.json", "fixture.json", "instances.json", "phases.json", "events.jsonl",
                 "event_references.json", "histories.json", "final_state.json", "validation.json", "preflight.json"):
        path = capture_dir / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != host.get("file_sha256", {}).get(name):
            errors.append("capture_hash_mismatch:" + name)
    if process.get("timed_out") or process.get("exit_code") != 0:
        errors.append("capture_process_unsuccessful")
    if process.get("source_changes_after_run") != []:
        errors.append("unexpected_runtime_source_changes")
    if manifest.get("source_manifest_sha256") != "fc72a0aef1b4a6b2bed10ec127c0342258f7a7e73a591ac070205fc6ddf4ba00":
        errors.append("source_manifest_unknown")
    if manifest.get("engine_sha256") != "09d1de6c4f97289c018556666c13c1d81093a5df5c2255725d464a87f40a8ea1":
        errors.append("engine_unknown")
    if manifest.get("baseline_modifications") != []:
        errors.append("immutable_baseline_modified")
    observation_patch = manifest.get("audited_runtime_observation_patch")
    if observation_patch is not None:
        patch_file = capture_dir.parent / "observer-patch" / "native_random_observer.patch"
        if observation_patch.get('schema') == 'observer7-patch/1':
            from .genuine import validate_patch
            try:
                validate_patch(observation_patch, patch_file.read_bytes())
                report = strict_json_loads((patch_file.parent/'patch-manifest.json').read_text())
                if report != observation_patch:
                    raise ValueError('host/actual048 patch report mismatch')
                # Observer evidence is output-only here; recheck its sealed host
                # identity before interpreting callback/primitive assertions.
                for name in ('observer7-input.jsonl','observer7-lineage.jsonl','observer7-metadata.jsonl',
                             'observer7-primitives.jsonl','observer7-runtime.jsonl',
                             'observer7-registration.jsonl','observer7-allocations.jsonl','observer7-status.json'):
                    if hashlib.sha256((capture_dir/name).read_bytes()).hexdigest() != host.get('file_sha256',{}).get(name):
                        raise ValueError('observer evidence hash mismatch')
            except (ValueError, OSError):
                errors.append("observation_patch_audit_invalid")
        elif (not observation_patch.get("applied") or observation_patch.get("comparison_mode") != "conditional_rule_replay"
                or not patch_file.is_file()
                or hashlib.sha256(patch_file.read_bytes()).hexdigest() != observation_patch.get("diff_sha256")):
            errors.append("observation_patch_audit_invalid")
    native = strict_json_loads((capture_dir / "native_manifest.json").read_text())
    entry = native.get('entry')
    if entry != manifest.get('entry'):
        errors.append('host_native_entry_mismatch')
    player_files = ('player_fixture.json', 'player_setup_evidence.json')
    if entry == 'migrated_custom_opponent_with_native_player_fixture_v1':
        for name in player_files:
            path = capture_dir / name
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != host.get('file_sha256', {}).get(name):
                errors.append('player_capture_hash_missing_or_mismatch:' + name)
        player_path = capture_dir / 'player_fixture.json'
        if player_path.is_file():
            actual_hash = hashlib.sha256(player_path.read_bytes()).hexdigest()
            if actual_hash != manifest.get('player_fixture_sha256') or actual_hash != native.get('player_fixture_sha256'):
                errors.append('player_input_provenance_hash_mismatch')
        evidence_path = capture_dir / 'player_setup_evidence.json'
        if evidence_path.is_file():
            evidence = strict_json_loads(evidence_path.read_text())
            if evidence.get('setup_complete') is not True or evidence.get('errors') != []:
                errors.append('player_setup_evidence_failed')
    elif entry == 'migrated_custom_opponent':
        if ('player_fixture_sha256' in manifest or 'player_fixture_sha256' in native
                or any((capture_dir / name).exists() or name in host.get('file_sha256', {}) for name in player_files)):
            errors.append('unexpected_player_input_in_default_entry')
    else:
        errors.append('unsupported_runtime:entry')
    for key, expected in (("schema", "native-combat-capture/1"),
                          ("version", "1.1.8"), ("main_scene", "res://Core/Main.tscn"),
                          ("physics_fps", 60), ("time_scale", 1), ("combat_speed", 1)):
        if native.get(key) != expected:
            errors.append("unsupported_runtime:" + key)
    preflight = strict_json_loads((capture_dir / "preflight.json").read_text())
    if not preflight or any(value is not True for value in preflight.values()):
        errors.append("native_preflight_failed")
    return dict(valid=not errors, errors=errors, process_clean_exit=process.get("process_clean_exit"),
                entry=entry, player_fixture_sha256=manifest.get("player_fixture_sha256"),
                source_manifest_sha256=manifest.get("source_manifest_sha256"),
                engine_sha256=manifest.get("engine_sha256"),
                runtime_observation_patch_sha256=observation_patch.get("diff_sha256") if observation_patch else None,
                baseline_modifications=manifest.get("baseline_modifications"))


def compare_callback_schedule(capture_dir, result):
    """OUTPUT ONLY: actual callbacks are read after the completed model result."""
    entry = None
    for line in (Path(capture_dir)/'observer7-input.jsonl').read_text().splitlines():
        row = strict_json_loads(line)
        if row['site']=='Core/Game.gd::activateItems' and row['edge']=='enter':
            if entry is not None:raise ValueError('duplicate actual activation entry')
            entry=row
    if entry is None:raise ValueError('missing actual activation entry')
    origin=int(entry['stamp']['physics_frame'])
    ordinary=[];timeouts=[];actual=[];closed=False
    sites={'Interface/CombatTimer/CombatTimer.gd::_physics_process':'combat_timer',
           'Utility/Util.gd::_physics_process':'util'}
    stacks={100:'Block',101:'Lucky',102:'Regeneration',103:'Vampirism',104:'Spikes',105:'Mana',106:'Empower',107:'Heat',108:'Poison',109:'Blind',110:'Cold'}
    for line in (Path(capture_dir)/'observer7-runtime.jsonl').read_text().splitlines():
        row=strict_json_loads(line)
        if row['sequence']<=entry['sequence']:continue
        if row['site']=='Core/Game.gd::combatEndDeferred' and row['edge']=='enter':
            closed=True;break
        if row['edge']!='enter':continue
        site=row['site'];role=None;phase='ordinary'
        if site in sites:role=sites[site]
        elif site=='Core/Character.gd::_physics_process':role='character:'+row['subject']['role']
        elif site=='Items/Item.gd::_physics_process':role='item:'+row['subject']['role']
        elif site=='Core/Character.gd::onTick':role='tick:'+row['subject']['role'];phase='internal'
        elif site=='Core/Character.gd::endBattleRage':role='rage:'+row['subject']['role'];phase='internal'
        elif site=='Core/Buff.gd::onTimeout':
            state=row['payload']['state'];role='buff:'+state['character']['role']+':'+stacks[int(state['type']['decimal'])];phase='internal'
        elif site in ('Items/CarrotGoobert.gd::onParticleTimeout','Items/LightGoobert.gd::onParticleTimeout'):role='particle:'+row['subject']['role'];phase='internal'
        elif site=='Interface/CombatTimer/CombatTimer.gd::startFatigue':role='fatigue:start';phase='internal'
        elif site=='Interface/CombatTimer/CombatTimer.gd::dealFatigueDamage':role='fatigue:tick';phase='internal'
        if role is None:continue
        delta=None
        if phase=='ordinary':
            args=row['payload']['arguments']['entries']
            if len(args)!=1 or args[0]['key']!={'type':'string','value':'delta'} or args[0]['value']['type']!='float':raise ValueError('actual ordinary delta shape')
            delta=args[0]['value']['binary64_be']
        target=ordinary if phase=='ordinary' else timeouts
        callback=dict(frame=int(row['stamp']['physics_frame'])-origin,role=role,
                      delta_bits=delta,combat_time_bits=row['stamp']['combat_time']['binary64_be'],
                      util_time_bits=row['stamp']['util_time']['binary64_be'])
        target.append(callback);actual.append(callback)
    if not closed:raise ValueError('missing same-pass source cleanup boundary')
    bits=lambda x:struct.pack('>d',x).hex()
    # Model's independently generated trace preserves actual computed order. No
    # native row or callback count configures a model step or selects its inputs.
    active=[x for x in result['schedule_trace'] if x['delta_hex']!='0000000000000000']
    frame_times={}
    for x in active:frame_times.setdefault(x['frame'],x['timestamp_hex'])
    clocks={x['frame']:x['util_time']for x in result['runtime_trace']if x['kind']=='util_step'}
    initial=next(x['util_time']for x in result['runtime_trace']if x['frame']==0)
    modeled_ord=[]
    for frame in range(1,result['scheduling']['frames']+1):
        modeled_ord.append(dict(frame=frame,role='util',delta_bits='3f91111120000000',combat_time_bits=frame_times[frame],util_time_bits=bits(clocks[frame-1]if frame>1 else initial)))
        for x in active:
            if x['frame']!=frame:continue
            role='combat_timer'if x['label']=='timer'else x['label']
            modeled_ord.append(dict(frame=frame,role=role,delta_bits=x['delta_hex'],combat_time_bits=x['timestamp_hex'],util_time_bits=bits(clocks[frame])))
    modeled_timeouts=[dict(frame=x['frame'],role=x['role'],delta_bits=None,combat_time_bits=frame_times[x['frame']],util_time_bits=bits(x['util_time']))for x in result['runtime_trace']if x['kind']=='timeout_enter']
    def ordered(o,t):
        rows=[(r['frame'],0,i,r)for i,r in enumerate(t)]+[(r['frame'],1,i,r)for i,r in enumerate(o)]
        return [r for _,_,_,r in sorted(rows,key=lambda x:x[:3])]
    left,right=actual,ordered(modeled_ord,modeled_timeouts)
    return dict(first_difference=first_difference(left,right,'$.callback_schedule'),native_callbacks=len(left),model_callbacks=len(right),native_ordinary=len(ordinary),native_timeouts=len(timeouts),scope='selected ordinary and physical Timer callbacks; raw API argc/internal numeric forms diagnostic only')


def compare_capture(capture_dir, engine_result):
    if not GENUINE_PROFILES:
        raise ValueError("genuine observer7/runtime profile not enabled; legacy capture inputs are insufficient")
    from .genuine import validate_result_profile
    runtime = engine_result.get('final', {}).get('runtime', {})
    validate_result_profile(runtime,engine_result.get('fixture'))
    capture_dir = Path(capture_dir)
    if not (capture_dir/'observer7-input.jsonl').is_file():
        raise ValueError('BLOCKED_INHERITED_INPUT: no actual observer7 activation/runtime inputs')
    provenance = validate_provenance(capture_dir)
    actual_fixture = fixture_from_capture(capture_dir)
    fixture_difference = first_difference(actual_fixture, engine_result["fixture"], "$.fixture")
    rows = [strict_json_loads(line) for line in (capture_dir / "events.jsonl").read_text().splitlines()]
    events = project_events(rows)
    event_difference = first_difference(events, engine_result["events"], "$.events")
    final = strict_json_loads((capture_dir / "final_state.json").read_text())
    left_final, right_final = project_final(final, engine_result["final"])
    final_difference = first_difference(left_final, right_final, "$.supported_final")
    histories = project_histories(strict_json_loads((capture_dir / "histories.json").read_text()))
    history_difference = first_difference(histories, engine_result.get("histories"), "$.histories")
    references = strict_json_loads((capture_dir / "event_references.json").read_text())
    projected_references = {identity: project_events([row], include_sequence=False)[0] for identity, row in references.items()}
    reference_difference = first_difference(projected_references, engine_result.get("event_references", {}), "$.event_references")
    references_equal = reference_difference is None
    callbacks = compare_callback_schedule(capture_dir,engine_result)
    exact = provenance["valid"] and references_equal and fixture_difference is None and event_difference is None and final_difference is None and history_difference is None and callbacks["first_difference"] is None
    rule_characters = left_final['native_rule_state']['characters']
    rule_items = [item for character in rule_characters for item in character['items']]
    final_coverage = dict(character_instances=len(rule_characters), item_instances=len(rule_items),
                          character_fields_per_instance=len(rule_characters[0]['fields']),
                          character_stats_per_instance=22, buffs_per_character=11, fields_per_buff=9,
                          character_rng_states_per_instance=4, fields_per_rng_state=7,
                          item_fields_per_instance=len(rule_items[0]['fields']) if rule_items else 32,
                          item_metrics_per_instance=80, item_rng_states_per_instance=2,
                          occupied_cells_order="raw_original_array_order",
                          excluded_character_fields=['characterName', 'chibi'],
                          excluded_item_fields=[])
    event_context = None
    if event_difference:
        match = re.search(r"events\[(\d+)\]", event_difference["path"])
        index = int(match.group(1)) if match else min(len(events), len(engine_result["events"]))
        event_context = dict(sequence=index, native=events[max(0, index - 2):index + 3],
                             engine=engine_result["events"][max(0, index - 2):index + 3])
    return dict(native_capture=str(capture_dir), scope="all_native_event_fields_complete_histories_and_explicit_supported_final_fields",
                model_source_sha256=engine_result.get("model_source_sha256"),
                provenance=provenance, final_field_coverage=final_coverage,
                callback_schedule=callbacks,
                callback_schedule_status="PASS" if callbacks["first_difference"] is None else "FAIL",
                events_status="PASS" if provenance["valid"] and references_equal and fixture_difference is None and event_difference is None else "FAIL",
                histories_status="PASS" if provenance["valid"] and fixture_difference is None and history_difference is None else "FAIL",
                event_references_status="PASS" if provenance["valid"] and references_equal else "FAIL",
                referenced_events=len(references),
                supported_final_status="PASS" if provenance["valid"] and fixture_difference is None and final_difference is None else "FAIL",
                scoped_status="PASS" if exact else "FAIL", native_events=len(events), engine_events=len(engine_result["events"]),
                first_differences=dict(fixture=fixture_difference, events=event_difference,
                                       event_references=reference_difference, supported_final=final_difference, histories=history_difference),
                event_context=event_context,
                random_alignment=engine_result["random_alignment"],
                whole_game_equivalence="NOT_EVALUATED", retail_equivalence="NOT_EVALUATED",
                not_compared=["Character.characterName (display/account input)", "Character.chibi (appearance input)",
                              "UI_global_Util_RNG_state", "retail_reference"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    parser.add_argument("engine_output", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    engine_result = strict_json_loads(args.engine_output.read_text())
    if "histories" in engine_result:
        engine_result["histories"] = restore_history_json_keys(engine_result["histories"])
    if "native_rule_state" in engine_result["final"]:
        engine_result["final"]["native_rule_state"] = restore_state_json_keys(engine_result["final"]["native_rule_state"])
    result = compare_capture(args.capture, engine_result)
    content = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(content)
    print(content)
    raise SystemExit(0 if result["scoped_status"] == "PASS" else 1)


if __name__ == "__main__":
    main()


#134 pure output-only complete FX normalization. No input construction or file reads.
def _king_role(role):
    stacks={100:'Block',101:'Lucky',102:'Regeneration',103:'Vampirism',104:'Spikes',105:'Mana',106:'Empower',107:'Heat',108:'Poison',109:'Blind',110:'Cold'}
    if role in ('P','O'):return 'character:'+role
    if type(role)is str and re.fullmatch('[PO]:[0-9]+',role):return 'item:'+role
    if type(role)is str and re.fullmatch('buff:[PO]:[0-9]+',role):
        a,side,key=role.split(':');return a+':'+side+':'+stacks[int(key)]
    for side in ('P','O'):
        if role==side+':tickTimer':return 'tick:'+side
        if role==side+':invulnerabilityTimer':return 'invu:'+side
        for name in ('battleRageTimer','autoRageTimer'):
            if role==side+':'+name:return 'aux:'+side+':'+name
    return role


def _king_keys(value,keys,label):
    if type(value)is not dict or set(value)!=set(keys):raise ValueError('closed King output '+label)


def _king_scalar(value,kind):
    keys={'float':('type','binary64_be'),'bool':('type','value'),'int':('type','decimal')}[kind]
    _king_keys(value,keys,'typed scalar')
    if value['type']!=kind:raise ValueError('King output scalar type')
    if kind=='float':
        from .engine import _be_float
        _be_float(value['binary64_be']);return value['binary64_be']
    if kind=='bool':
        if type(value['value'])is not bool:raise ValueError('King output bool')
        return value['value']
    if type(value['decimal'])is not str or re.fullmatch('0|[1-9][0-9]*',value['decimal'])is None:raise ValueError('King output counter')
    return int(value['decimal'])


def _king_node(value):
    from copy import deepcopy
    from .engine import NODE_INPUT_KEYS
    _king_keys(value,NODE_INPUT_KEYS,'node');out=deepcopy(value);out['role']=_king_role(out['role']);return out


def _king_timer(value):
    _king_keys(value,('node','process_mode','wait_time','time_left','one_shot','autostart','paused','stopped'),'Timer')
    for key in ('one_shot','autostart','paused','stopped'):
        if type(value[key])is not bool:raise ValueError('public Timer flag type')
    if type(value['process_mode'])is not int or value['process_mode']not in (0,1):raise ValueError('public Timer mode')
    return dict(node=_king_node(value['node']),process_mode=value['process_mode'],wait_time_bits=_king_scalar(value['wait_time'],'float'),time_left_bits=_king_scalar(value['time_left'],'float'),**{k:value[k]for k in ('one_shot','autostart','paused','stopped')})


def project_king_fx(native):
    _king_keys(native,('nodes','timers','particles','physics_frame','idle_frame','util_time','util_clockTime','util_frameCounter','is_in_physics_frame','private_timer_values'),'full FX')
    if native['private_timer_values']!='NOT_EXPOSED_SOURCE_FRESHNESS_AND_CLOCK_ONLY':raise ValueError('private native observation forbidden')
    nodes=native['nodes']
    if type(nodes)is not list or len(nodes)!=1:raise ValueError('full FX root list')
    _king_keys(nodes[0],('role','node','timer'),'root row')
    if nodes[0]['role']!='root_viewport' or nodes[0]['timer']is not None:raise ValueError('full FX root identity')
    timers={};particles={}
    for role,value in native['timers'].items():
        key=_king_role(role)
        if key in timers:raise ValueError('duplicate normalized Timer')
        timers[key]=_king_timer(value)
    for identity,value in native['particles'].items():
        _king_keys(value,('activation','drag','light_visible','light_modulate_rgba'),'King particles')
        out={}
        for kind,prefix in (('activation','king_hide:'),('drag','king_drag:')):
            v=value[kind];_king_keys(v,('node','visible','emitting','one_shot','lifetime','explosiveness','speed_scale','timer'),'AutoHide')
            key=prefix+identity
            if key in timers:raise ValueError('duplicate nested Timer')
            timers[key]=_king_timer(v['timer'])
            out[kind]=dict(node=_king_node(v['node']),**{k:_king_scalar(v[k],'bool')for k in ('visible','emitting','one_shot')},**{k+'_bits':_king_scalar(v[k],'float')for k in ('lifetime','explosiveness','speed_scale')})
        rgba=value['light_modulate_rgba'];_king_keys(rgba,('type','values'),'rgba')
        if rgba['type']!='array' or len(rgba['values'])!=4:raise ValueError('rgba4')
        out.update(light_visible=_king_scalar(value['light_visible'],'bool'),light_modulate_bits=[_king_scalar(v,'float')for v in rgba['values']]);particles[identity]=out
    if len(timers)!=35 or len(particles)!=1:raise ValueError('complete35 Timer/one King projection')
    for key in ('physics_frame','idle_frame'):
        if type(native[key])is not int or native[key]<0:raise ValueError('native source counter')
    if type(native['is_in_physics_frame'])is not bool:raise ValueError('native phase flag')
    return dict(schema='phase134-complete-public-fx/1',root=_king_node(nodes[0]['node']),timers=timers,particles=particles,
                physics_frame=native['physics_frame'],idle_frame=native['idle_frame'],util_time_bits=_king_scalar(native['util_time'],'float'),util_clock_time_bits=_king_scalar(native['util_clockTime'],'float'),util_frame_counter=_king_scalar(native['util_frameCounter'],'int'),is_in_physics_frame=native['is_in_physics_frame'])


def compare_king_fx_snapshots(native_before,native_after,model_before,model_after):
    from copy import deepcopy
    comparisons={}
    for label,native,model in (('post_cleanup',native_before,model_before),('final',native_after,model_after)):
        projected=project_king_fx(native)
        _king_keys(model,tuple(projected)+('private_timers','processing_nodes'),'model full FX')
        if set(model['private_timers'])!=set(model['timers']):raise ValueError('complete private diagnostic Timer set')
        public={k:model[k]for k in projected}
        comparisons[label]=dict(first_difference=first_difference(projected,public,'$.king_fx.'+label),native_raw=deepcopy(native),native_projection=projected,model_public=deepcopy(public),model_private=deepcopy(model['private_timers']),model_processing_nodes=deepcopy(model['processing_nodes']))
    return dict(status='PASS'if all(v['first_difference']is None for v in comparisons.values())else'FAIL',snapshots=comparisons)


def compare_king_observations(native_projection,model_projection):
    """Supplied output-only semantic projections; every group required, never input."""
    keys=('events','event_references','histories','final','random_inputs','api','scheduler')
    _king_keys(native_projection,keys,'native semantic groups');_king_keys(model_projection,keys,'model semantic groups')
    differences={key:first_difference(native_projection[key],model_projection[key],'$.king.'+key)for key in keys}
    return dict(status='PASS'if all(x is None for x in differences.values())else'FAIL',differences=differences)
