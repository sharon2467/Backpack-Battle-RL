"""Prepare/freeze Food declaration SOURCE; never imports schema or operational helpers."""
from pathlib import Path
import argparse
import ast
import copy
import difflib
import hashlib
import json
import re

R=Path(__file__).resolve().parents[1]
D=R/'data/phase375-food-hook-source'
MAP_D=R/'data/phase375-attempt03-recovery-source'
FOOD='Items/Food.gd::prepare'


def pin(path):
    raw=path.read_bytes();return dict(size=len(raw),sha256=hashlib.sha256(raw).hexdigest())


def desc(path):
    assert path.is_relative_to(R) and not any(p.is_symlink() for p in (path,*path.parents))
    return dict(path=str(path.relative_to(R)),**pin(path))


def save(name,value):
    with (D/name).open('x') as stream:stream.write(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')


def derive(before,pairs):
    after=before
    for a,b in pairs:assert a in after,repr(a);after=after.replace(a,b)
    inverse=after
    for a,b in reversed(pairs):inverse=inverse.replace(b,a)
    assert inverse==before
    return after


def generate():
    D.mkdir(exist_ok=False);(D/'after-source').mkdir()
    oldsink=R/'data/phase370-oracle-source/after-source/native_random_observer_sink_v7.gd'
    before=oldsink.read_text();line=next(x for x in before.splitlines(True) if x.startswith('const SITES ='))
    sites=json.loads(line.split('=',1)[1]);assert len(sites)==106 and FOOD not in sites
    sites[FOOD]=dict(channel='runtime',state_schema='item')
    newline='const SITES = '+json.dumps(sites,sort_keys=True)+'\n'
    after=before.replace(line,newline,1);assert after.replace(newline,line,1)==before
    sink=D/'after-source/native_random_observer_sink_v7.gd';sink.write_text(after)
    (D/'sink-source.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='frozen370/sink.gd',tofile='source375/sink.gd')))
    schema_before=R/'tests/phase360_king_observer_schema.py';before=schema_before.read_text();tree=ast.parse(before)
    node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='MATRIX' for x in n.targets))
    matrix=ast.literal_eval(node.value);assert len(matrix['sites'])==106 and FOOD not in matrix['sites']
    matrix['sites'][FOOD]=dict(channel='runtime',state_schema='item',arguments_exact=[],argument_types={},explicit_returns=[])
    lines=before.splitlines(True);oldmatrix=''.join(lines[node.lineno-1:node.end_lineno]);newmatrix='MATRIX='+repr(matrix)+'\n'
    after=before.replace(oldmatrix,newmatrix,1)
    # Base validates strict item state first. This additional predicate affects only the new site.
    anchor="        state = payload['state']\n        if MATRIX['sites'][site]['state_schema'] == 'character'"
    guard="        if site == 'Items/Food.gd::prepare' and state['descriptorIndex'] != {'type': 'int', 'decimal': '22'}:\n            raise ValueError('Food.prepare receiver must be original thin-domain Food descriptor INT22')\n"
    assert after.count(anchor)==1
    after=after.replace(anchor,"        state = payload['state']\n"+guard+"        if MATRIX['sites'][site]['state_schema'] == 'character'",1)
    assert after.replace(guard,'',1).replace(newmatrix,oldmatrix,1)==before
    schema=R/'tests/phase375_king_observer_schema.py';schema.write_text(after);compile(after,str(schema),'exec')
    oldfunctions={n.name:ast.dump(n,include_attributes=False) for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
    nt=ast.parse(after);newfunctions={n.name:ast.dump(n,include_attributes=False) for n in nt.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
    assert oldfunctions.keys()==newfunctions.keys()
    changed={k for k in oldfunctions if oldfunctions[k]!=newfunctions[k]};assert changed=={'validate_record'}
    restored=ast.parse(after.replace(guard,'',1));rn=next(n for n in restored.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='MATRIX' for x in n.targets))
    rn.value=copy.deepcopy(node.value);assert ast.dump(restored,include_attributes=False)==ast.dump(tree,include_attributes=False)
    assert all(matrix['sites'][k]==v for k,v in ast.literal_eval(node.value)['sites'].items())
    assert {k:v for k,v in matrix.items() if k!='sites'}=={k:v for k,v in ast.literal_eval(node.value).items() if k!='sites'}
    assert any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='SimpleNamespace' and any(k.arg=='MATRIX' and isinstance(k.value,ast.Name) and k.value.id=='MATRIX' for k in n.keywords) for n in ast.walk(nt))
    delegates={}
    for name in ('_base_validate_record','validate_record','_validate_call_pairs','validate_observation_records'):
        fn=next(n for n in nt.body if isinstance(n,ast.FunctionDef) and n.name==name)
        delegates[name]=dict(module_global_MATRIX=any(isinstance(n,ast.Name) and n.id=='MATRIX' and isinstance(n.ctx,ast.Load) for n in ast.walk(fn)),
            no_local_MATRIX_binding=not any(isinstance(n,ast.Name) and n.id=='MATRIX' and isinstance(n.ctx,ast.Store) for n in ast.walk(fn)))
    # validate_observation_records delegates to the same-module validator/pairing methods.
    assert all(v['no_local_MATRIX_binding'] for v in delegates.values())
    for name in ('_base_validate_record','validate_record','_validate_call_pairs'):assert delegates[name]['module_global_MATRIX']
    (D/'schema-source.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='frozen360/schema.py',tofile='source375/schema.py')))
    save('schema-delta-proof.json',dict(schema='phase375-minimal-schema-source-delta/1',origin=desc(schema_before),module=desc(schema),
        old106_entries_identical=True,other_MATRIX_keys_identical=True,all_module_AST_except_MATRIX_and_one_guard_identical=True,
        changed_functions=['validate_record'],unchanged_functions_classes=sorted(oldfunctions.keys()-changed),guard_source=guard,
        strict_owner='New Foodsite descriptorIndex typedINT22; existing knownrole join and NULLrole lifecycle unchanged',
        delegates=delegates,export='SimpleNamespace(MATRIX=MATRIX): exact same module object, no copied/fake table',
        old_BindingSourceContract='Historical358/359 SOURCE origin unchanged; not current375 acceptance'))
    # New map generator changes only the exact saved attempt's identities, not its read-only algorithm.
    saved=Path('/workspace/native-combat-20261013/runs/original027-king-single-A-20261025-attempt03/output/failed-pool-preservation/receipt.json')
    receipt_pin=pin(saved);value=json.loads(saved.read_text());assert value['schema']=='attempt03-failed-pool-preservation/1' and value['overlay_bytes']==202992 and value['overlay_sha256']=='6ed9cf9be0afe81938e552c2623ff141fd978b8162ef61f2e5dd18b181fdd0b9'
    old=(R/'tests/phase368_prepare_attempt02_restore_map.py').read_text()
    pairs=[("RECEIPT = dict(size=335,sha256='f34d7e1f00094f9cfbf99bb8947f8cd69b375b1cff98395b74ab4bff9fe3d4f1')",'RECEIPT = '+repr(receipt_pin)),
        ("OVERLAY = dict(size=197087,sha256='2418e6d2c413e64bc860684d3f20edde223f97343dfd438d9d896d577be85a24')","OVERLAY = dict(size=202992,sha256='6ed9cf9be0afe81938e552c2623ff141fd978b8162ef61f2e5dd18b181fdd0b9')"),
        ('attempt02','attempt03'),('phase368-attempt03','phase375-attempt03')]
    new=derive(old,pairs);map_tool=R/'tests/phase375_prepare_attempt03_restore_map.py';map_tool.write_text(new);compile(new,str(map_tool),'exec')
    protocols={}
    for stem in ('oracle_host','pool_recovery'):
        before_path=R/f'tests/phase370_{stem}.py';after_path=R/f'tests/phase375_{stem}.py';old=before_path.read_text()
        changes=[('data/phase370-oracle-source','data/phase375-food-hook-source'),
            ('INDEPENDENT370_SCRIPT_SIGNAL_RETURN_SOURCE_REPAIR_ACCEPTED_ROOT_PENDING','INDEPENDENT375_FOOD_HOOK_SOURCE_REPAIR_ACCEPTED_ROOT_PENDING'),
            ('phase370-root-oracle-acceptance/1','phase375-root-oracle-acceptance/1'),
            ('original027-king-single-A-20261025-attempt03','original027-king-single-A-20261025-attempt04'),('attempt=3','attempt=4')] if stem=='oracle_host' else [
            ('from phase370_oracle_host import','from phase375_oracle_host import'),
            ('INDEPENDENT370_RESTORED_POOL_EXACT_TARGET_READBACK_PASS','INDEPENDENT375_RESTORED_POOL_EXACT_TARGET_READBACK_PASS'),
            ('phase370-root-pool-recovery/1','phase375-root-pool-recovery/1'),
            ('data/phase368-attempt02-recovery-source','data/phase375-attempt03-recovery-source'),
            ('phase368-attempt02-exact-restore-source-map/1','phase375-attempt03-exact-restore-source-map/1'),
            ('attempt02-failed-pool-preservation/1','attempt03-failed-pool-preservation/1')]
        new=derive(old,changes);after_path.write_text(new);compile(new,str(after_path),'exec')
        a={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(old).body if isinstance(n,ast.FunctionDef)}
        b={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(new).body if isinstance(n,ast.FunctionDef)}
        changed=sorted(k for k in a if a[k]!=b[k]);assert set(a)==set(b)
        assert changed==(['execute','plan','source_gate'] if stem=='oracle_host' else ['source_gate','verify_evidence'])
        protocols[stem]=dict(before=desc(before_path),after=desc(after_path),literal_pairs=changes,inverse='EXACT_BYTES',changed_binding_functions=changed,unchanged_functions=sorted(a.keys()-set(changed)))
    save('protocol-and-map-derivation.json',dict(protocols=protocols,map_tool=desc(map_tool),map_tool_origin=desc(R/'tests/phase368_prepare_attempt02_restore_map.py'),map_tool_pairs=pairs,map_algorithm_inverse='EXACT_BYTES'))
    save('schema-source-freeze.json',dict(schema='phase375-schema-producer-source-tuple/1',module=desc(schema),schema_origin=desc(schema_before),
        producer_sink=desc(sink),producer_origin=desc(oldsink),collector_unchanged=desc(R/'data/phase370-oracle-source/collector.gd'),
        fixed_case='KING-K1-A-353',profile='observer7-355-native-single-king-A/1',new_site=FOOD,source_acceptance=None,model_admission=False))
    print('SOURCE text generated/compiled only; saved-map generation and final seal remain separate.')


def seal():
    assert not (D/'source-owner.json').exists() and (MAP_D/'derivation.json').is_file()
    old={}
    for name in ('data/phase370-oracle-source/source-owner.json','data/phase374-selected-hook-source-audit/source-owner.json','data/phase373-independent-final/owned-files.json'):
        path=R/name;old[name]=desc(path)
        for row in json.loads(path.read_text())['files']:assert desc(R/row['path'])==row;old[row['path']]=row
    for row in json.loads((R/'data/phase370-oracle-source/old-source-readback.json').read_text())['files']:
        assert desc(R/row['path'])==row;old[row['path']]=row
    source=R/'data/phase370-oracle-source/combined-source-freeze.json';freeze=copy.deepcopy(json.loads(source.read_text()));oldpaths=copy.deepcopy(freeze['paths'])
    changes={'data/phase370-oracle-source/after-source/native_random_observer_sink_v7.gd':desc(D/'after-source/native_random_observer_sink_v7.gd'),
        'tests/phase370_oracle_host.py':desc(R/'tests/phase375_oracle_host.py'),'tests/phase370_pool_recovery.py':desc(R/'tests/phase375_pool_recovery.py')}
    # Remove superseded active map dependencies; frozen originals remain via repair_origin/old readback.
    freeze['files']=[row for row in freeze['files'] if not row['path'].startswith('data/phase368-attempt02-recovery-source/')]
    for row in freeze['files']:
        if row['path'] in changes:value=changes[row['path']];row.clear();row.update(value)
    extras=[Path(__file__),R/'tests/phase375_prepare_attempt03_restore_map.py',R/'tests/phase375_king_observer_schema.py',
        R/'docs/phase375_food_hook_source_implementation_addendum.md',D/'schema-source-freeze.json',
        R/'data/phase373-independent-final/review.json',R/'data/phase373-independent-final/owned-files.json']
    extras+=sorted(p for p in MAP_D.iterdir() if p.is_file())
    freeze['files'] += [desc(p) for p in extras];assert len({x['path'] for x in freeze['files']})==len(freeze['files'])
    row=freeze['paths']['native_random_observer_sink_v7.gd'];row['after_path']=str((D/'after-source/native_random_observer_sink_v7.gd').relative_to(R));row['after']=pin(D/'after-source/native_random_observer_sink_v7.gd')
    assert {k:v for k,v in freeze['paths'].items() if k!='native_random_observer_sink_v7.gd'}=={k:v for k,v in oldpaths.items() if k!='native_random_observer_sink_v7.gd'}
    freeze.update(schema='phase375-food-selected-hook-SOURCE/1',repair_origin=desc(source),repair_finding=desc(R/'data/phase373-independent-final/review.json'),
        schema_module=desc(R/'tests/phase375_king_observer_schema.py'),active_source_tuple=desc(D/'schema-source-freeze.json'),
        run_name='original027-king-single-A-20261025-attempt04',current_authorized_operations=0)
    for row in freeze['files']:assert desc(R/row['path'])==row
    for row in freeze['paths'].values():assert pin(R/row['after_path'])==row['after']
    save('combined-source-freeze.json',freeze)
    save('binding-boundaries.json',dict(schema='phase375-source-binding-boundaries/1',schema_case=freeze['schema_case'],profile=freeze['profile'],
        native_source_origin=freeze['native_source_origin'],active_source_tuple=desc(D/'schema-source-freeze.json'),
        old_BindingSourceContract='True historical358/359 birth/geometry source; not a375 approval',
        old_projector=dict(path='tests/phase361_king_projection_sealer.py',state='UNCHANGED_CLOSED',schema_origin='old360'),
        future_projector_required=['actual375 schema module pin','actual new producer/host source tuple','real independent/root acceptance descriptors','complete actual12 first projection gate'],
        reader361_opened=False,genuine356_opened=False,caller_verified_flag_accepted=False))
    save('api-contract.json',dict(schema='phase375-source-contract/1',host_schema='phase375-root-oracle-acceptance/1',recovery_schema='phase375-root-pool-recovery/1',
        review_status='INDEPENDENT375_FOOD_HOOK_SOURCE_REPAIR_ACCEPTED_ROOT_PENDING',independent_readback_status='INDEPENDENT375_RESTORED_POOL_EXACT_TARGET_READBACK_PASS',
        module=desc(R/'tests/phase375_king_observer_schema.py'),Food_owner='strict typed descriptorINT22; old role join/NULL lifecycle preserved',
        real_independent_acceptance=None,real_restore_release=None,real_native_release=None,actual_attempts=0))
    for name,row in old.items():assert desc(R/name)==row
    save('old-source-readback.json',dict(status='ALL_REFERENCED_OLD_LEAVES_IDENTICAL',files=list(old.values())))
    for path in [Path(__file__)]+[R/'tests'/name for name in ('phase375_king_observer_schema.py','phase375_prepare_attempt03_restore_map.py','phase375_oracle_host.py','phase375_pool_recovery.py')]:compile(path.read_text(),str(path),'exec')
    save('summary.json',dict(schema='phase375-source-handoff/1',status='SOURCE_FROZEN_INDEPENDENT_REVIEW_PENDING',freeze=desc(D/'combined-source-freeze.json'),
        added_selected_site=FOOD,new_site_owner_guard_only=True,sink_generic_functions_unchanged=True,other74patches_identical=True,
        saved_map_generated_only=True,probes=0,Game=0,actual_pool_inventory=0,restore=0,READY=0,models=0,projection=0,independent_FINAL=False,no_more_writes=True))
    own=[Path(__file__),R/'docs/phase375_food_hook_source_implementation_addendum.md']+[R/'tests'/name for name in
        ('phase375_king_observer_schema.py','phase375_prepare_attempt03_restore_map.py','phase375_oracle_host.py','phase375_pool_recovery.py')]
    own+=sorted(p for p in D.rglob('*') if p.is_file())+sorted(p for p in MAP_D.iterdir() if p.is_file());rows=[desc(p) for p in own]
    save('source-owner.json',dict(schema='phase375-source-owner/1',files=rows,scope='SOURCE and saved-only map derivation; not independent/native acceptance'))
    for row in rows:assert desc(R/row['path'])==row
    print(json.dumps(dict(freeze=desc(D/'combined-source-freeze.json'),owner=desc(D/'source-owner.json'),leaves=len(rows),bytes=sum(x['size'] for x in rows))))


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=('generate','seal'));args=p.parse_args();(generate if args.action=='generate' else seal)()


if __name__=='__main__':main()
