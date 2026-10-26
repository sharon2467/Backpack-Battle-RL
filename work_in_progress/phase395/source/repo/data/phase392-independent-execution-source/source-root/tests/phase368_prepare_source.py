"""Generate/freeze SOURCE text only. Never imports operational modules or runs Game/helper."""
from pathlib import Path
import argparse
import ast
import copy
import difflib
import hashlib
import json
import re

R=Path(__file__).resolve().parents[1]
D=R/'data/phase368-oracle-source'
MAP_D=R/'data/phase368-attempt02-recovery-source'


def pin(path):
    raw=path.read_bytes();return dict(size=len(raw),sha256=hashlib.sha256(raw).hexdigest())


def desc(path):
    assert path.is_relative_to(R) and not any(p.is_symlink() for p in (path,*path.parents))
    return dict(path=str(path.relative_to(R)),**pin(path))


def save(name,value):
    with (D/name).open('x') as stream:stream.write(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')


def save_generated(name,value):
    # Explicit WIP text regeneration only; a frozen owner permanently closes this path.
    assert not (D/'source-owner.json').exists()
    (D/name).write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')


def functions(text):
    declarations=list(re.finditer(r'^(?:func|var|const|signal|class)\s+([^\s(:=]+)',text,re.M))
    out={}
    for i,match in enumerate(declarations):
        if match.group(0).startswith('func '):
            end=declarations[i+1].start() if i+1<len(declarations) else len(text)
            out[match.group(1)]=text[match.start():end]
    return out


def merge(base,delta):
    originals=functions(base);replacements=functions(delta);ledger=[];result=base
    for name,value in replacements.items():
        if name in originals:
            assert result.count(originals[name])==1
            result=result.replace(originals[name],value,1)
            ledger.append(dict(name=name,before=originals[name],after=value))
    # All non-replacement declarations/functions are a single removable suffix.
    suffix=delta
    for name in replacements.keys() & originals.keys():suffix=suffix.replace(replacements[name],'',1)
    boundary='\n\n# PHASE368 OBSERVATION-CONTROL EXTENSION\n'
    result+=boundary+suffix
    return result,ledger,boundary+suffix


def generate():
    assert not (D/'source-owner.json').exists()
    D.mkdir(exist_ok=True);(D/'after-source').mkdir(exist_ok=True)
    old_sink=(R/'data/phase359-king-producer-source/after-source/native_random_observer_sink_v7.gd').read_text()
    sink_delta=(R/'tests/phase368_sink_control_delta.gd').read_text()
    sink,sl,ss=merge(old_sink,sink_delta)
    # Capture the two existing connection results at their original call sites, without reordering/reconnecting.
    before=functions(sink)['_ready'];after=before.replace('get_tree().connect("physics_frame", self, "clock_physics_signal")',
        'source_cut_ready_connect.physics = get_tree().connect("physics_frame", self, "clock_physics_signal")')
    after=after.replace('get_tree().connect("idle_frame", self, "clock_idle_signal")',
        'source_cut_ready_connect.idle = get_tree().connect("idle_frame", self, "clock_idle_signal")')
    after=after.replace('\tui_open()','\tif source_cut_ready_connect.physics != OK or source_cut_ready_connect.idle != OK:\n\t\tsource_cut_reject("SOURCE_TREE_CLOCK_CONNECT", "sink._ready")\n\t\treturn\n\tui_open()')
    assert before!=after;sink=sink.replace(before,after,1);sl.append(dict(name='_ready',before=before,after=after))
    before=functions(sink)['begin_fixture_window'];after=before.replace('return fail("SOURCE_FIXTURE_WINDOW_ORDER", "begin_fixture_window")',
        'source_diagnostic("begin_fixture_window", "SOURCE_FIXTURE_WINDOW_ORDER", {"control": source_cut_control(), "fixture_window": source_fixture_window, "configured": configured, "ui_opened": ui_opened})\n\t\treturn fail("SOURCE_FIXTURE_WINDOW_ORDER", "begin_fixture_window")')
    after=after.replace('return fail("SOURCE_FIXED_SLOT_TABLE", "begin_fixture_window")',
        'source_diagnostic("begin_fixture_window", "SOURCE_FIXED_SLOT_TABLE", {"control": source_cut_control()})\n\t\treturn fail("SOURCE_FIXED_SLOT_TABLE", "begin_fixture_window")')
    assert before!=after;sink=sink.replace(before,after,1);sl.append(dict(name='begin_fixture_window',before=before,after=after))
    old_collector=(R/'data/phase365-control-recovery-source/collector.gd').read_text()
    collector_delta=(R/'tests/phase368_collector_control_delta.gd').read_text()
    # The observer-absent path has the same pure primitive projection/validator available locally.
    sf=functions(sink_delta)
    for name in ('source_diag_valid','source_control_target','source_control_bound_value','source_control_rows'):
        collector_delta+='\n'+sf[name].replace('source_diag_valid','collector_diag_valid').replace('source_control_target','collector_control_target').replace('source_control_bound_value','collector_control_bound_value').replace('source_control_rows','collector_control_rows').replace('float_bits(', 'collector_control_float_bits(')
    collector_delta+='\n'+functions(old_sink)['float_bits'].replace('float_bits(', 'collector_control_float_bits(')
    collector,cl,cs=merge(old_collector,collector_delta)
    before=functions(collector)['place_player_items'];after=before.replace('return false','return source_window_reject("place_player_items", "SOURCE_WINDOW_REJECTED")',1)
    after=after.replace('\tvar book =','\tsource_book_reached = true\n\tvar book =',1)
    after=after.replace('if int(spec.item_index) >= book.getNumItems():\n\t\t\treturn false',
        'if int(spec.item_index) >= book.getNumItems():\n\t\t\treturn source_window_reject("place_player_items", "DESCRIPTOR_RANGE", {"slot": slot, "raw_descriptor": collector_control_bound_value(spec.item_index)})')
    after=after.replace('\t\tvar item = book.instantiateItem(descriptor)','\t\tsource_instantiate_reached = true\n\t\tvar item = book.instantiateItem(descriptor)',1)
    after=after.replace('\t\tinventory.orientItem(item,','\t\tsource_geometry_reached = true\n\t\tinventory.orientItem(item,',1)
    after=after.replace('\t\t\treturn false','\t\t\treturn source_window_reject("place_player_items", "GEOMETRY_OR_MODIFIER_REJECTED", {"slot": slot, "descriptor": descriptor.itemIndex})')
    assert before!=after;collector=collector.replace(before,after,1);cl.append(dict(name='place_player_items',before=before,after=after))
    before=functions(collector)['start_controlled_combat'];after=before.replace('if not player_registered or not ensure_source_window():',
        'if not player_registered or not ensure_source_window():\n\t\tsource_control_record("start_controlled_combat", "FRESH_PLAYER_OR_WINDOW_REJECTED", {"player_registered": player_registered})')
    assert before!=after;collector=collector.replace(before,after,1);cl.append(dict(name='start_controlled_combat',before=before,after=after))
    for stem,original,result,ledger,suffix in (('sink',old_sink,sink,sl,ss),('collector',old_collector,collector,cl,cs)):
        inverse=result
        for row in reversed(ledger):
            assert inverse.count(row['after'])==1,(stem,row['name']);inverse=inverse.replace(row['after'],row['before'],1)
        assert inverse.endswith(suffix);inverse=inverse[:-len(suffix)]
        assert inverse==original,stem+' exact byte inverse'
        target=D/'after-source/native_random_observer_sink_v7.gd' if stem=='sink' else D/'collector.gd'
        target.write_text(result)
        (D/(stem+'-source.patch')).write_text(''.join(difflib.unified_diff(original.splitlines(True),result.splitlines(True),fromfile='frozen/'+stem+'.gd',tofile='source368/'+stem+'.gd')))
        save_generated(stem+'-inverse-ledger.json',dict(schema='phase368-exact-inverse/1',replacements=ledger,removable_suffix=suffix,
            before_sha256=hashlib.sha256(original.encode()).hexdigest(),after=desc(target),status='EXACT_BYTE_INVERSE'))
    # Operational host mechanisms remain unchanged; only exact protocol/SOURCE/attempt bindings differ.
    old=(R/'tests/phase365_oracle_host.py').read_text();new=old
    host_pairs=[("SOURCE = 'data/phase365-control-recovery-source'","SOURCE = 'data/phase368-oracle-source'"),
        ('original027-king-single-A-20261025-attempt02','original027-king-single-A-20261025-attempt03'),
        ('INDEPENDENT365_CONTROL_RECOVERY_SOURCE_ACCEPTED_ROOT_PENDING','INDEPENDENT368_SYNCHRONOUS_CUT_SOURCE_ACCEPTED_ROOT_PENDING'),
        ('phase365-root-oracle-acceptance/1','phase368-root-oracle-acceptance/1'),('attempt=2','attempt=3')]
    for before,after in host_pairs:assert before in new;new=new.replace(before,after)
    host_tree=ast.parse(new);control=next(n for n in host_tree.body if isinstance(n,ast.FunctionDef) and n.name=='collect_capture_metadata')
    lines=new.splitlines(True);before_control=''.join(lines[control.lineno-1:control.end_lineno])
    after_control=before_control.replace("        control=capture/'collector-first-failure.json'", "        control_files={name:expected.pop(name) for name in ('collector-first-failure.json','observer7_failure.json') if name in expected}\n        control=capture/'collector-first-failure.json'")
    after_control=after_control.replace('if control.name in expected:', 'if control.name in control_files:')
    anchor="        path=capture/'validation.json'"
    inserted="""        observer_failure=capture/'observer7_failure.json'
        if observer_failure.name in control_files:
            identity=control_files[observer_failure.name]
            try:
                observer_control=read_control(observer_failure,4096)
                if observer_control.get('schema')!='observer7-failure/1' or type(observer_control.get('code')) is not str:
                    raise ValueError('observer first failure control schema')
                observed=dict(kind='observer_control_failure',identity=identity,control=observer_control)
                if primary is None: primary=observed
                else: secondary.append(dict(code='additional_observer_control_failure',failure=observed,precedence='COLLECTOR_IF_PRESENT_NO_TIME_ORDER_INFERRED'))
            except Exception as exc:
                if primary is None: primary=dict(kind='invalid_observer_control_failure',identity=identity)
                secondary.append(dict(code='bad_observer_control',identity=identity,error=repr(exc)))
"""
    assert anchor in after_control;after_control=after_control.replace(anchor,inserted+anchor)
    after_control=after_control.replace('capture=None; present={}; expected={}; validation=None; partial={}', 'capture=None; present={}; expected={}; validation=None; partial={}; control_files={}')
    after_control=after_control.replace('expected_observations_opaque=expected,partial_files_opaque=partial,', 'expected_observations_opaque=expected,control_failures_opaque=control_files,partial_files_opaque=partial,')
    assert before_control!=after_control;new=new.replace(before_control,after_control,1)
    inverse=new
    inverse=inverse.replace(after_control,before_control,1)
    for before,after in reversed(host_pairs):inverse=inverse.replace(after,before)
    assert inverse==old
    (R/'tests/phase368_oracle_host.py').write_text(new)
    # Thin new-schema/map binding only; the old365 helper remains immutable.
    old=(R/'tests/phase365_pool_recovery.py').read_text();new=old
    pairs=[('from phase365_oracle_host import','from phase368_oracle_host import'),
        ('data/phase365-source-recovery-plan/restore-map.json','data/phase368-attempt02-recovery-source/restore-map.json'),
        ('data/phase365-source-recovery-plan/source-input-pins.json','data/phase368-attempt02-recovery-source/source-input-pins.json'),
        ('INDEPENDENT365_RESTORED_POOL_EXACT_TARGET_READBACK_PASS','INDEPENDENT368_RESTORED_POOL_EXACT_TARGET_READBACK_PASS'),
        ('phase365-root-pool-recovery/1','phase368-root-pool-recovery/1'),
        ("receipt.get('status')=='PASS_PRESERVED_NOT_RESTORED' and receipt.get('physical_restore_performed') is False",
         "mapping.get('schema')=='phase368-attempt02-exact-restore-source-map/1' and receipt.get('schema')=='attempt02-failed-pool-preservation/1' and receipt.get('status')=='PRESERVED_NOT_RESTORED' and type(receipt.get('restore')) is int and receipt['restore']==0"),
        ("    for field,key in (('run','failed_run'),('pool','pool'),('baseline','baseline')):\n        require(map_recorded(receipt[field],relocation)==roots[key],'preservation root identity')\n",''),
        ("receipt['zip_sha256']","receipt['overlay_sha256']"),("receipt['zip_bytes']","receipt['overlay_bytes']"),
        ("len(mapping['file_differences'])==78 and len(mapping['directory_differences'])==7", "len(mapping['file_differences'])==len(changed_files) and len(mapping['directory_differences'])==len(changed_dirs)"),
        ("    require(len(mapping['staged_files'])==2,'exact2 staged files')\n", "    require(len(mapping['staged_files'])==sum(row['kind']=='file' for row in c.index(target_data).values()),'exact target staged files')\n")]
    for before,after in pairs:assert before in new;new=new.replace(before,after)
    (R/'tests/phase368_pool_recovery.py').write_text(new)
    # Text replacement list is a full reversible delta; deletion is inserted at its exact anchor.
    restored=new
    for before,after in reversed(pairs):
        if after:restored=restored.replace(after,before)
        else:
            anchor="    saved=roots['failed_run']/'output/failed-pool-preservation'\n";assert anchor in restored;restored=restored.replace(anchor,before+anchor,1)
    assert restored==old,'thin recovery exact byte inverse'
    save_generated('python-derivation.json',dict(host_pairs=host_pairs,host_control_function=dict(before=before_control,after=after_control),recovery_pairs=pairs,host_inverse='EXACT_BYTES',recovery_inverse='EXACT_BYTES'))
    print('SOURCE text generated; map generation/seal remain separate. No generated module imported.')


def seal():
    assert (MAP_D/'derivation.json').is_file() and not (D/'source-owner.json').exists()
    old={}
    for name in ('data/phase365-control-recovery-source/source-owner.json','data/phase368-source-design/source-owner.json',
                 'data/phase366-independent-attempt02-triage/owned-files.json'):
        p=R/name;old[name]=desc(p)
        for row in json.loads(p.read_text())['files']:assert desc(R/row['path'])==row;old[row['path']]=row
    for row in json.loads((R/'data/phase365-control-recovery-source/old-source-readback.json').read_text())['files']:
        assert desc(R/row['path'])==row;old[row['path']]=row
    for name in ('phase368_oracle_host.py','phase368_pool_recovery.py','phase368_prepare_source.py','phase368_prepare_attempt02_restore_map.py'):
        path=R/'tests'/name;compile(path.read_text(),str(path),'exec')
    # New finalizer may only serialize frozen DTOs and observation-control state.
    finalizer=functions((D/'collector.gd').read_text())['finish_source_cut']
    assert all(token not in finalizer for token in ('stable_snapshot(', 'source_runtime_snapshot(', 'getStats(', 'game.', 'snapshot()'))
    before=(R/'tests/phase365_oracle_host.py').read_text();after=(R/'tests/phase368_oracle_host.py').read_text()
    before_funcs={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(before).body if isinstance(n,ast.FunctionDef)}
    after_funcs={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(after).body if isinstance(n,ast.FunctionDef)}
    changed=[k for k in before_funcs if before_funcs[k]!=after_funcs[k]];assert changed==['source_gate','plan','execute','collect_capture_metadata']
    source=R/'data/phase365-control-recovery-source/combined-source-freeze.json';freeze=copy.deepcopy(json.loads(source.read_text()))
    new_sink=D/'after-source/native_random_observer_sink_v7.gd'
    for row in freeze['files']:
        if row['path']=='tests/phase365_oracle_host.py':row.clear();row.update(desc(R/'tests/phase368_oracle_host.py'))
        elif row['path']=='tests/phase365_pool_recovery.py':row.clear();row.update(desc(R/'tests/phase368_pool_recovery.py'))
        elif row['path']=='data/phase365-control-recovery-source/collector.gd':row.clear();row.update(desc(D/'collector.gd'))
        elif row['path']=='data/phase359-king-producer-source/after-source/native_random_observer_sink_v7.gd':row.clear();row.update(desc(new_sink))
    old_paths=copy.deepcopy(freeze['paths']);row=freeze['paths']['native_random_observer_sink_v7.gd'];row['after_path']=str(new_sink.relative_to(R));row['after']=pin(new_sink)
    assert {k:v for k,v in freeze['paths'].items() if k!='native_random_observer_sink_v7.gd'}=={k:v for k,v in old_paths.items() if k!='native_random_observer_sink_v7.gd'}
    additions=[R/'tests'/name for name in ('phase368_prepare_source.py','phase368_prepare_attempt02_restore_map.py','phase368_sink_control_delta.gd','phase368_collector_control_delta.gd')]
    additions += [R/'docs/phase368_same_idle_source_implementation_addendum.md']+sorted(p for p in MAP_D.iterdir() if p.is_file())
    freeze['files'] += [desc(p) for p in additions]
    assert len({r['path'] for r in freeze['files']})==len(freeze['files'])
    freeze.update(schema='phase368-synchronous-cut-oracle-SOURCE/1',repair_origin=desc(source),collector=desc(D/'collector.gd'),
        run_name='original027-king-single-A-20261025-attempt03',current_authorized_operations=0,
        repair_finding=desc(R/'data/phase366-independent-attempt02-triage/finding.json'))
    for row in freeze['files']:assert desc(R/row['path'])==row
    for row in freeze['paths'].values():assert pin(R/row['after_path'])==row['after']
    save('combined-source-freeze.json',freeze)
    save('delta-proof.json',dict(schema='phase368-source-delta-proof/1',GD_inverse_ledgers=['sink-inverse-ledger.json','collector-inverse-ledger.json'],
        host_changed_functions=changed,host_observer_control_delta='bounded observer7_failure primary fallback; no timestamp-order claim',host_unchanged_functions=sorted(set(before_funcs)-set(changed)),
        unchanged_patch_paths=len(old_paths)-1,changed_patch_paths=['native_random_observer_sink_v7.gd'],
        finalizer_resampling_calls=False,generated_modules_imported=False,old_source_readback_leaves=len(old),
        storage=desc(R/'tests/phase363_oracle_storage.py'),process=desc(R/'tests/phase363_oracle_process.py')))
    save('api-contract.json',dict(schema='phase368-source-contract/1',host_schema='phase368-root-oracle-acceptance/1',
        recovery_schema='phase368-root-pool-recovery/1',source_review_status='INDEPENDENT368_SYNCHRONOUS_CUT_SOURCE_ACCEPTED_ROOT_PENDING',
        independent_readback_status='INDEPENDENT368_RESTORED_POOL_EXACT_TARGET_READBACK_PASS',
        private_signal='source_idle_cut_ready',states=['IDLE','EMITTING','RETURNED','FINALIZING','FINALIZED'],
        callback='on_idle_source_cut -> one frozen DTO -> exact ack -> return',finalizer='finish_source_cut -> frozen DTO serialization only -> actual BOOL return',
        completion_control_file='source-window-diagnostic.jsonl',fallback_control_file='collector-source-window-diagnostic.jsonl',
        root_attempt03_authorization=None,actual_map_derivation=desc(MAP_D/'derivation.json'),helper_calls=0,actual_pool_inventory=0,
        models_allowed=0,inputbuilds_allowed=0,old356_gate='CLOSED',old361_reader='CLOSED'))
    save('old-source-readback.json',dict(status='ALL_OLD_REFERENCED_LEAVES_IDENTICAL',files=list(old.values())))
    save('summary.json',dict(schema='phase368-source-handoff/1',status='SOURCE_FROZEN_INDEPENDENT_CONTROLS_PENDING',
        freeze=desc(D/'combined-source-freeze.json'),source_map_generated_from_saved_only=True,
        native=0,models=0,probes=0,helper_calls=0,actual_pool_inventory=0,restore=0,READY=0,new_attempts=0,
        independent_FINAL=False,no_more_writes=True))
    own=[R/'tests'/name for name in ('phase368_prepare_source.py','phase368_prepare_attempt02_restore_map.py','phase368_oracle_host.py',
        'phase368_pool_recovery.py','phase368_sink_control_delta.gd','phase368_collector_control_delta.gd')]
    own += [R/'docs/phase368_same_idle_source_implementation_addendum.md']
    own += sorted(p for p in D.rglob('*') if p.is_file())+sorted(p for p in MAP_D.iterdir() if p.is_file())
    rows=[desc(p) for p in own];assert len({r['path'] for r in rows})==len(rows)
    save('source-owner.json',dict(schema='phase368-source-owner/1',scope='SOURCE only, not independent/native acceptance',files=rows))
    for row in rows:assert desc(R/row['path'])==row
    print(json.dumps(dict(freeze=desc(D/'combined-source-freeze.json'),owner=desc(D/'source-owner.json'),leaves=len(rows),bytes=sum(r['size'] for r in rows))))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('generate','seal'));args=parser.parse_args()
    (generate if args.action=='generate' else seal)()


if __name__=='__main__':main()
