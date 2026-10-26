"""Text-only oracle SOURCE assembly. No GD/schema/host/tool semantics executed."""
from pathlib import Path
import argparse
import ast
import difflib
import hashlib
import json
import re


def pin(path):
    raw=Path(path).read_bytes()
    return dict(size=len(raw),sha256=hashlib.sha256(raw).hexdigest())


def blocks(source):
    lines=source.splitlines(keepends=True); found={}
    for i,line in enumerate(lines):
        match=re.match(r'^func (\w+)\(',line)
        if not match: continue
        stop=i+1
        while stop<len(lines) and (not lines[stop].strip() or lines[stop].startswith(('\t','#'))): stop+=1
        if match[1] in found: raise ValueError('duplicate method '+match[1])
        found[match[1]]=''.join(lines[i:stop])
    return found


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root',type=Path,required=True);parser.add_argument('--baseline',type=Path,required=True)
    args=parser.parse_args(); root=args.source_root.absolute(); baseline=args.baseline.absolute()
    D=root/'data/phase362-oracle-capture-source'; D.mkdir(exist_ok=False)
    def desc(path): return dict(path=str(path.relative_to(root)),**pin(path))
    def save(name,value):
        path=D/name;path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('x') as f:f.write(json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
    old={}; controls=[]
    for stage in (359,360,361):
        path=root/f'data/phase{stage}-root-acceptance/accepted.json'
        data=json.loads(path.read_text());controls.append(desc(path));old[str(path.relative_to(root))]=desc(path)
        for key in ('review','owner','source_owner','freeze'):
            row=data[key]
            if pin(root/row['path'])!={k:row[k] for k in ('size','sha256')}:raise ValueError('old accepted SOURCE drift')
            controls.append(row)
        owner=json.loads((root/data['source_owner']['path']).read_text())
        for row in owner['files']:
            if desc(root/row['path'])!=row:raise ValueError('old owner leaf drift')
            old[row['path']]=row
    for freeze_name,staged in [('data/phase324-rainbow75-source/candidate-source-freeze.json','.'),
        ('data/phase349-king-fresh-source/candidate-source-freeze.json','data/phase349-king-fresh-source/staged'),
        ('data/phase356-king-admission-source-repair/candidate-source-freeze.json','data/phase356-king-admission-source-repair/staged')]:
        path=root/freeze_name;old[freeze_name]=desc(path)
        files=json.loads(path.read_text())['files'];assert len(files)==15
        for name,wanted in files.items():
            path=root/staged/name;assert pin(path)==wanted;old[str(path.relative_to(root))]=desc(path)
    design=root/'docs/phase362_king_collector_host_shared_source_integration_spec.md'
    assert pin(design)==dict(size=19813,sha256='098f15dee31c02b9b51c2690ba08ba2bc11e279d41355d821c8e4b945c842549')
    old[str(design.relative_to(root))]=desc(design)
    base_path=root/'tests/phase298_native_collector.gd';base=base_path.read_text();source=base
    extension_path=root/'tests/phase362_collector_extension.gd';extension=extension_path.read_text()
    edits=[]
    def change(label,new):
        nonlocal source
        if new!=source:
            edits.append(dict(label=label,before=source,after=new));source=new
    for name,body in blocks(extension).items():
        old_body=blocks(source).get(name)
        change('method:'+name,source.replace(old_body,body+'\n',1) if old_body is not None else source+'\n'+body)
    prefix=extension[:extension.index('func ')]
    change('observer-owned-variables',source.replace('func _initialize():',prefix+'\nfunc _initialize():',1))
    old_finish=blocks(source)['finish_capture']
    change('remove-unreachable-deferred-resampling',source.replace(old_finish,'',1))
    def once(old_text,new_text):
        assert source.count(old_text)==1,old_text[:100]
        change('anchor:'+old_text[:80],source.replace(old_text,new_text,1))
    once('const PLAYER_ITEM_WHITELIST = '+source.split('const PLAYER_ITEM_WHITELIST = ',1)[1].split('\n',1)[0],
         'const PLAYER_ITEM_WHITELIST = [1, 4, 11, 19, 22, 262]')
    once('var stable = side + ":" + str(slot)','var stable = slot_spec(side, slot).instance_id')
    once('func place_player_items():\n','func place_player_items():\n\tif not ensure_source_window():\n\t\treturn false\n')
    once('"stable_id": "P:" + str(slot)','"stable_id": slot_spec("P", slot).instance_id')
    fixture=json.loads((root/'data/phase355-king-finite-source/fixed-A-v8-fixture.json').read_text())
    native={}
    for side in fixture['sides']:
        native[side['side']]=dict(schema_version=1,game_version='1.1.8',**{'class':0},health=int(side['hp']),stamina=int(side['stamina']),
            items=[{k:v for k,v in row.items() if k!='instance_id'} for row in side['items']])
    # SOURCE fixtures only; these are not observed carrier examples or a bundle.
    for side,name in (('P','custom_player.json'),('O','custom_opponent.json')):save('case-A/'+name,native[side])
    config=dict(schema='native-combat-capture/1',case_id='NATIVE-027-KING-A',global_seed=35301,util_seed=35302,
                player_fixture_enabled=True,timeouts=dict(battle_seconds=120,total_seconds=295))
    save('case-A/native_capture_config.json',config)
    constants='const SOURCE_P = '+json.dumps(native['P'])+'\nconst SOURCE_O = '+json.dumps(native['O'])+'\nconst SOURCE_CONFIG = '+json.dumps(config)+'\n'
    change('fixed-source-constants',source.replace('const OUT =',constants+'\nconst OUT =',1))
    validator=blocks(source)['player_input_valid']
    change('exact-fixed-P-only',source.replace(validator,'func player_input_valid(value):\n\treturn get_root().get_node("NativeRandomObserver").source_same_slot_value(value, SOURCE_P)\n\n',1))
    once('\topponent_fixture = fixture_parsed.result\n','\topponent_fixture = fixture_parsed.result\n\tif not get_root().get_node("NativeRandomObserver").source_same_slot_value(opponent_fixture, SOURCE_O):\n\t\tfail("fixed O SOURCE fixture differs")\n\t\treturn\n')
    once('\tif not timeout_budget_selftest():','\tif not get_root().get_node("NativeRandomObserver").source_same_slot_value(config, SOURCE_CONFIG):\n\t\tfail("fixed config differs")\n\t\treturn\n\tif not timeout_budget_selftest():')
    once('settings.getVal(settings.Setting.combat_speed)','settings.settings[settings.Setting.combat_speed]')
    once('"critTokens", "battleRageBonusDur"','"critTokens", "invulnerabilityItem", "invulBubbleVisible", "battleRageBonusDur"')
    once('\t\t\tvar observer7_timers = {}','\t\t\tif item.descriptor.itemIndex == 262:\n\t\t\t\tobserver7_fields = fields(item, ["activations", "activationsToTrigger", "invuCharges", "protectedBuffs", "manaCost"])\n\t\t\tvar observer7_timers = {}')
    assert not any(token in source for token in ('getAffectedItems(', 'getAffectedItems_nocache(', 'getItemsInside(', 'get_property_list(', 'call_deferred("finish_capture"'))
    (D/'collector.gd').write_text(source)
    (D/'disposable-marker.txt').write_bytes(b'disposable-observation-copy\n')
    (D/'collector-source.patch').write_text(''.join(difflib.unified_diff(base.splitlines(True),source.splitlines(True),fromfile='frozen298/collector.gd',tofile='oracle362/collector.gd')))
    reversed_source=source
    for edit in reversed(edits):assert reversed_source==edit['after'];reversed_source=edit['before']
    assert reversed_source==base
    save('collector-inverse-ledger.json',dict(edits=edits,exact_inverse_to298=True))
    # Snapshot getter closure: only returns/match/direct fields/native stopped.
    char_path=baseline/'Core/Character.gd';char=char_path.read_text();char_funcs=blocks(char)
    names=['getStat','getStaminaRegeneration','getCurrentHealth','getTemporaryMaxHealth','getCurrentStamina','getMaxStamina',
           'isBattleRaging','getCritTokens','getHealingEfficiency','getUnhealing']
    methods=[]
    for name in names:
        body=char_funcs[name]
        assert not re.search(r'\b(?:emit_signal|randomize|randf|randi|snapshotCharacterStat|gainStacks|loseStacks)\s*\(',body)
        assert not re.search(r'(?<![=!<>])=(?!=)',body),name
        methods.append(dict(path='Core/Character.gd',method=name,body=body,**dict(size=len(body.encode()),sha256=hashlib.sha256(body.encode()).hexdigest())))
    field_groups={}
    groups={label:(files,None) for label,files in {'CHAR_FIELDS':['Core/Character.gd'],'ITEM_FIELDS':['Items/Item.gd'],
        'RNG_FIELDS':['Utility/BalancedRandom.gd'],'LOG_FIELDS':['Core/CombatLog.gd'],'HIST_FIELDS':['Core/CombatStatLogger.gd']}.items()}
    groups.update({
        'Buff':(['Core/Buff.gd'],['type','current','permanentStacks','resistChancePercent','resistStacks','reflectChancePercent','cleanseProtectionChancePercent','temporaryStacks','nextTemporaryTimeout']),
        'Game':(['Core/Game.gd'],['curMode','curClass','curRound','wins','losses','tries','survivalMode','fightEnded','roundResults','ropeSpeedups','cubeAdvanced','sandbagActive','numTimesOutOfStamina']),
        'CombatTimer':(['Interface/CombatTimer/CombatTimer.gd'],['combatTime','timeAdvance','fatigueCounter']),
        'Rules':(['Utility/CustomRules.gd'],['customRulesActive','values']),
        'StatHistory':(['Core/StatHistory.gd'],['eventNumbers','values']),
        'BalancedRange':(['Utility/BalancedRange.gd'],['acc']),
        'Settings':(['Utility/Settings.gd'],['settings']),
        'King':(['Items/Goobert.gd','Items/Exclusive/KingGoobert.gd'],['activations','activationsToTrigger','invuCharges','protectedBuffs','manaCost'])})
    for label,(files,fields) in groups.items():
        if fields is None:
            line=next(line for line in source.splitlines() if line.startswith('const '+label+' = '))
            fields=ast.literal_eval(line.split(' = ',1)[1])
        declarations=[]
        for field in fields:
            found=[]
            for name in files:
                text=(baseline/name).read_text()
                assert not re.search(r'^func _get(?:\(|_property_list\()',text,re.M) and 'setget' not in text,name
                found += [dict(path=name,line=i+1,text=line.strip()) for i,line in enumerate(text.splitlines()) if re.search(r'\bvar\s+'+re.escape(field)+r'\b',line)]
            assert found,(label,field)
            declarations.append(dict(field=field,declarations=found))
        field_groups[label]=declarations
    extra_sources=['Core/StatHistory.gd','Utility/BalancedRange.gd','Core/CombatEvent.gd','Core/Buff.gd','Items/Exclusive/KingGoobert.gd','Items/Goobert.gd','Items/Potion.gd']
    for name in extra_sources:
        text=(baseline/name).read_text();assert not re.search(r'^func _get(?:\(|_property_list\()',text,re.M) and 'setget' not in text
    save('snapshot-readonly-source-evidence.json',dict(methods=methods,fields=field_groups,
        original_files={name:pin(baseline/name) for name in set(extra_sources+[f for paths,unused in groups.values() for f in paths])},
        inherited_readonly_evidence=[desc(root/'data/phase359-king-producer-source/field-getter-source-matrix.json'),desc(root/'data/phase359-king-producer-source/binding-query-source.json')],
        source_reads='direct declared members; referenced native getters only; no property-list, cache refresh or business writer',
        not_VM_test=True,actual_getter_calls=0))
    native_freeze=json.loads((root/'data/phase359-king-producer-source/producer-source-freeze.json').read_text())
    paths={}
    for name,row in native_freeze['files'].items():
        location=native_freeze['source_locations'][name]['after'];assert pin(root/location)==row['after']
        paths[name]=dict(before=row['before'],after=row['after'],after_path=location)
    assert len(paths)==75
    code_names=['phase362_prepare_oracle_source.py','phase362_collector_extension.gd','phase362_oracle_storage.py','phase362_oracle_process.py','phase362_oracle_host.py']
    for name in code_names:
        path=root/'tests'/name
        if path.suffix=='.py':compile(path.read_bytes(),str(path),'exec')
    # New operational modules have no old-workspace dependency or model import.
    for name in code_names[2:]:
        text=(root/'tests'/name).read_text();assert '/workspace/' not in text
        assert 'native_replay' not in text and 'schema.validate_' not in text
    for name in ('phase362_oracle_storage.py','phase362_oracle_host.py'):
        tree=ast.parse((root/'tests'/name).read_text())
        calls=[ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n,ast.Call)]
        assert not any(x.endswith(('copytree','_reconstruct')) for x in calls)
    payloads=[root/'tests'/name for name in code_names]+[D/'collector.gd',D/'disposable-marker.txt']+sorted((D/'case-A').iterdir())
    payloads += [root/'tests/native_run_compaction.py',root/'tests/godotsteam_offline_exec.py']
    payloads += [root/row['after_path'] for row in paths.values()]
    payloads=list(dict.fromkeys(payloads))
    save('combined-source-freeze.json',dict(schema='phase362-oracle-only-SOURCE/1',profile='observer7-355-native-single-king-A/1',schema_case='KING-K1-A-353',
        case_id=config['case_id'],run_name='original027-king-single-A-20261025-attempt01',paths=paths,files=[desc(p) for p in payloads],
        accepted_source_controls=list({r['path']:r for r in controls}.values()),
        collector=desc(D/'collector.gd'),native_source_origin=desc(root/'data/phase359-king-producer-source/producer-source-freeze.json'),
        scope='ORACLE_CAPTURE_ONLY_NO_PYTHON_MODEL_OR_PROJECTION',models_allowed=0,inputbuilds_allowed=0,
        policy='bounded-writers-and-monitored-process/1',current_authorized_operations=0))
    save('operational-contract.json',dict(schema='phase362-operational-contract/1',
        required_root_config_schema='phase362-root-oracle-acceptance/1',reserved_independent_PASS='INDEPENDENT362_ORACLE_CAPTURE_SOURCE_ACCEPTED_ROOT_PENDING',
        paths='explicit source_root/task_root/baseline/pool/runs_root; no defaults to oldworkspace',
        completion='same idle: sink callback adjacent before collector; no deferred final sampling; full snapshot once',
        write_policy='bounded-writers-and-monitored-process/1',limitations=['background usage polling is not kernel aggregate quota; possible inter-poll overage',
            'actual Godot parse/startup/signal connection order and complete12 have never run', 'first fullprojection positive and model candidate gate remain OPEN'],
        protected='canonical75/349/356/359/360/361 immutable; no model gate opened'))
    for name,row in old.items():assert desc(root/name)==row,name
    save('old-source-readback.json',dict(files=list(old.values()),status='BEFORE_AFTER_BYTE_IDENTICAL'))
    save('source-summary.json',dict(status='AUTHOR_ORACLE_ONLY_SOURCE_PENDING_INDEPENDENT_REVIEW',
        freeze=desc(D/'combined-source-freeze.json'),collector=desc(D/'collector.gd'),modified_collector_functions=list(blocks(extension)),
        source_inverse=True,snapshot_getters_source_closed=True,Python_compile_without_import=True,
        operational_tool_calls=0,hostplan_calls=0,pool_writes=0,Godot_calls=0,native=0,models=0,schema_API_calls=0,
        fullprojection_positive=False,independent_FINAL=False,no_more_writes=True))
    owns=[root/'tests'/name for name in code_names]
    owns += [root/'docs/phase362_oracle_capture_implementation_spec.md',root/'docs/phase362_monitored_write_budget_decision.md']
    owns += sorted(p for p in D.rglob('*') if p.is_file())
    rows=[desc(path) for path in owns];assert len({r['path'] for r in rows})==len(rows)
    save('source-owner.json',dict(schema='phase362-author-SOURCE-owner/1',root=str(root),files=rows,scope='new SOURCE only; no independent FINAL'))
    for row in json.loads((D/'source-owner.json').read_text())['files']:assert desc(root/row['path'])==row
    print(json.dumps(dict(status='SOURCE_OWNER_ALL_LEAVES_READ_BACK',owner=desc(D/'source-owner.json'),freeze=desc(D/'combined-source-freeze.json'),leaves=len(rows),bytes=sum(r['size'] for r in rows))))


if __name__=='__main__':main()
