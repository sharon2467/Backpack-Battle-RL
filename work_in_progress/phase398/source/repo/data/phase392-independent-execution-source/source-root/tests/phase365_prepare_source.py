"""SOURCE text/pin generation only. Does not import generated helpers or execute recovery."""
from pathlib import Path
import ast
import copy
import difflib
import hashlib
import json

R=Path(__file__).resolve().parents[1]
D=R/'data/phase365-control-recovery-source'


def pin(path):
    raw=path.read_bytes()
    return dict(size=len(raw),sha256=hashlib.sha256(raw).hexdigest())


def desc(path):
    assert path.is_relative_to(R) and not any(p.is_symlink() for p in (path,*path.parents))
    return dict(path=str(path.relative_to(R)),**pin(path))


def save(name,value):
    with (D/name).open('x') as stream: stream.write(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')


def main():
    # The only files present before this SOURCE-only generator are text producer outputs.
    assert {p.name for p in D.iterdir()}=={'collector.gd'}
    old={}
    for name in ('data/phase363-oracle-repair-source/old-source-readback.json',
                 'data/phase363-oracle-repair-source/source-owner.json',
                 'data/phase365-source-recovery-plan/source-owner.json',
                 'data/phase364-independent-startup-diagnosis/owned-files.json'):
        p=R/name; old[name]=desc(p); value=json.loads(p.read_text())
        for row in value['files']:
            assert desc(R/row['path'])==row,row['path'];old[row['path']]=row
    old_readback=json.loads((R/'data/phase363-oracle-repair-source/old-source-readback.json').read_text())
    for row in old_readback['files']:
        assert desc(R/row['path'])==row,row['path'];old[row['path']]=row
    # Frozen independent probe evidence must be the actual accepted finding, not a claimed code positive.
    finding=R/'data/phase364-independent-startup-diagnosis/finding.json'
    assert pin(finding)==dict(size=3438,sha256='5e4e6b54b51414a5bc8145cd06c12cfb89591956b0e491edc496ebe9c2339634')
    previous=R/'data/phase363-oracle-repair-source/combined-source-freeze.json'
    assert pin(previous)==dict(size=52020,sha256='b86bb6181e38d19d74aff7b163723f247f467b1a3e4ca9715c41171b7f5358af')
    freeze=copy.deepcopy(json.loads(previous.read_text()))
    before_collector=R/'data/phase362-oracle-capture-source/collector.gd'
    before=before_collector.read_text();after=(D/'collector.gd').read_text()
    added=after[after.index('func config_matches_source(value):'):after.index('func _initialize():')]
    restored=after.replace(added,'').replace('\tvar source_config_input = {}\n','').replace('\t\tsource_config_input = parsed.result\n','')
    restored=restored.replace('if not config_matches_source(source_config_input):',
        'if not get_root().get_node("NativeRandomObserver").source_same_slot_value(config, SOURCE_CONFIG):')
    assert restored==before,'collector exact inverse outside config caller/helper'
    (D/'collector-source.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='frozen362/collector.gd',tofile='source365/collector.gd')))
    oldhost=R/'tests/phase363_oracle_host.py';newhost=R/'tests/phase365_oracle_host.py'
    before,after=oldhost.read_text(),newhost.read_text();ot,nt=ast.parse(before),ast.parse(after)
    of={n.name:n for n in ot.body if isinstance(n,ast.FunctionDef)};nf={n.name:n for n in nt.body if isinstance(n,ast.FunctionDef)}
    changed={name for name in of if ast.dump(of[name],include_attributes=False)!=ast.dump(nf[name],include_attributes=False)}
    assert changed=={'source_gate','plan','execute'}
    assert set(nf)-set(of)=={'read_control','collect_capture_metadata'}
    normalized=after.replace("SOURCE = 'data/phase365-control-recovery-source'","SOURCE = 'data/phase363-oracle-repair-source'")
    normalized=normalized.replace('original027-king-single-A-20261025-attempt02','original027-king-single-A-20261025-attempt01')
    normalized=normalized.replace('INDEPENDENT365_CONTROL_RECOVERY_SOURCE_ACCEPTED_ROOT_PENDING','INDEPENDENT363_INSTALLER_MONITOR_SOURCE_ACCEPTED_ROOT_PENDING')
    tree=ast.parse(normalized)
    tree.body=[copy.deepcopy(of[n.name]) if isinstance(n,ast.FunctionDef) else n for n in tree.body
               if not isinstance(n,ast.FunctionDef) or n.name in of]
    assert ast.dump(tree,include_attributes=False)==ast.dump(ot,include_attributes=False),'host module inverse AST'
    (D/'host-source.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='frozen363/host.py',tofile='source365/host.py')))
    tools=[R/'tests/phase365_oracle_host.py',R/'tests/phase365_pool_recovery.py',Path(__file__)]
    for path in tools: compile(path.read_text(),str(path),'exec')
    replacement={'tests/phase363_oracle_host.py':desc(newhost),
        'data/phase362-oracle-capture-source/collector.gd':desc(D/'collector.gd')}
    for row in freeze['files']:
        if row['path'] in replacement:
            current=replacement[row['path']];row.clear();row.update(current)
    additions=[R/'tests/phase365_pool_recovery.py',Path(__file__),
        R/'docs/phase365_control_and_recovery_source_implementation_spec.md',finding,
        R/'data/phase364-independent-startup-diagnosis/owned-files.json']
    additions += [R/'data/phase365-source-recovery-plan'/name for name in
        ('source-owner.json','restore-map.json','source-input-pins.json','control-source-finding.json')]
    freeze['files'] += [desc(p) for p in additions]
    assert len({r['path'] for r in freeze['files']})==len(freeze['files'])
    freeze.update(schema='phase365-control-recovery-SOURCE/1',repair_origin=desc(previous),repair_finding=desc(finding),
        collector=desc(D/'collector.gd'),run_name='original027-king-single-A-20261025-attempt02',
        recovery=dict(restore_leaves_state='failed',commit_requires='actual independent exact tree report plus separate root gate'),
        current_authorized_operations=0)
    assert freeze['paths']==json.loads(previous.read_text())['paths'] and len(freeze['paths'])==75
    for row in freeze['files']: assert desc(R/row['path'])==row,row['path']
    for row in freeze['paths'].values(): assert pin(R/row['after_path'])==row['after']
    save('combined-source-freeze.json',freeze)
    save('source-delta-proof.json',dict(schema='phase365-narrow-delta/1',collector=dict(before=desc(before_collector),after=desc(D/'collector.gd'),
        inverse='EXACT_BYTES_REMOVE_CONFIG_HELPER_RAW_PARSED_INPUT_AND_SINGLE_CALLER_GATE'),
        host=dict(before=desc(oldhost),after=desc(newhost),changed_functions=sorted(changed),added_functions=sorted(set(nf)-set(of)),
            unchanged_functions=sorted(set(of)-changed),inverse='EXACT_MODULE_AST_AFTER_DECLARED_PROTOCOL_AND_FUNCTION_REPLACEMENTS'),
        storage_byte_reused=desc(R/'tests/phase363_oracle_storage.py'),process_byte_reused=desc(R/'tests/phase363_oracle_process.py'),
        original75patch_paths_unchanged=True,generated_modules_imported=False,compile_text_only=[desc(p) for p in tools],
        old_successful_science_rerun=False))
    save('api-contract.json',dict(schema='phase365-source-interfaces/1',
        host=dict(root_config_schema='phase365-root-oracle-acceptance/1',review_status='INDEPENDENT365_CONTROL_RECOVERY_SOURCE_ACCEPTED_ROOT_PENDING',
            attempt=2,run_name=freeze['run_name'],case_id=freeze['case_id'],seeds=dict(global_seed=35301,util_seed=35302),
            partition_keys=['lawful_inputs_present','lawful_inputs_missing','expected_observations_opaque','partial_files_opaque','primary_failure','secondary_errors','capture_complete'],
            decoded_controls_only=['collector-first-failure.json','validation.json']),
        recovery=dict(root_config_schema='phase365-root-pool-recovery/1',actions=['restore','commit_ready'],
            roots=['source_root','pool','baseline','failed_run','previous_run'],required_config=['source_freeze','source_owner','reviews','restore_map','input_pins','roots'],
            restore='recover(...,action=restore,output=new external dir): full evidence gate then78+2 atomic payloads, metadata, double tree readback; failed state retained',
            commit_extra=['restore_receipt','independent_readback:{receipt,owner}','root_commit_ready_authorized:true'],
            independent_status='INDEPENDENT365_RESTORED_POOL_EXACT_TARGET_READBACK_PASS',
            independent_required=['roots','restore_map','source_freeze','project_target','staged_target','restore_receipt','failed_state','project_readback','staged_readback'],
            current_actual_source_review=None,current_independent_physical_readback=None),
        no_current_execution_permission=True))
    for name,row in old.items(): assert desc(R/name)==row,name
    save('old-source-readback.json',dict(status='ALL_REFERENCED_OLD_LEAVES_IDENTICAL',files=list(old.values())))
    save('summary.json',dict(schema='phase365-author-source-handoff/1',status='SOURCE_FROZEN_INDEPENDENT_CONTROLS_PENDING',
        freeze=desc(D/'combined-source-freeze.json'),actual_restore_calls=0,commit_ready_calls=0,helper_calls=0,
        native=0,models=0,projection=0,pool_writes=0,Godot_probes=0,old_sources_identical=True,
        independent_FINAL=False,no_more_writes=True))
    owned=tools+[R/'docs/phase365_control_and_recovery_source_implementation_spec.md']+sorted(p for p in D.iterdir() if p.is_file())
    rows=[desc(p) for p in owned];assert len({r['path'] for r in rows})==len(rows)
    save('source-owner.json',dict(schema='phase365-source-owner/1',files=rows,scope='new SOURCE only, not independent acceptance'))
    for row in json.loads((D/'source-owner.json').read_text())['files']: assert desc(R/row['path'])==row
    print(json.dumps(dict(status='SOURCE_OWNER_ALL_LEAVES_READ_BACK',freeze=desc(D/'combined-source-freeze.json'),
        owner=desc(D/'source-owner.json'),leaves=len(rows),bytes=sum(r['size'] for r in rows))))


if __name__=='__main__': main()
