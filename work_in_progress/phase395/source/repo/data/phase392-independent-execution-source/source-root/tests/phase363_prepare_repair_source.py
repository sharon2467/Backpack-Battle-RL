"""Freeze only SOURCE derivation/AST/identity; never import or call the helpers."""
from pathlib import Path
import ast
import copy
import difflib
import hashlib
import json

R=Path(__file__).resolve().parents[1]
D=R/'data/phase363-oracle-repair-source'


def pin(path):
    raw=Path(path).read_bytes()
    return dict(size=len(raw),sha256=hashlib.sha256(raw).hexdigest())


def desc(path):
    assert path.is_relative_to(R) and not path.is_symlink()
    return dict(path=str(path.relative_to(R)),**pin(path))


def save(name,value):
    with (D/name).open('x') as stream:stream.write(json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False)+'\n')


def main():
    D.mkdir(exist_ok=False)
    old={}
    owners=['data/phase362-oracle-capture-source/source-owner.json',
        'data/phase362-independent-source-review/owned-files.json',
        'data/phase359-king-producer-source/source-owner.json',
        'data/phase360-schema-auxiliary-binding-source/source-owner.json',
        'data/phase361-projection-sealer-source/source-owner.json']
    for name in owners:
        path=R/name;old[name]=desc(path);value=json.loads(path.read_text())
        rows=value['files']
        if type(rows) is dict:
            rows=[dict(path=name,**identity) for name,identity in rows.items()]
        for row in rows:
            actual=desc(R/row['path'])
            assert actual==row,row['path'];old[row['path']]=row
    for name,staged in [('data/phase324-rainbow75-source/candidate-source-freeze.json','.'),
        ('data/phase349-king-fresh-source/candidate-source-freeze.json','data/phase349-king-fresh-source/staged'),
        ('data/phase356-king-admission-source-repair/candidate-source-freeze.json','data/phase356-king-admission-source-repair/staged')]:
        path=R/name;old[name]=desc(path);files=json.loads(path.read_text())['files'];assert len(files)==15
        for filename,expected in files.items():
            path=R/staged/filename;assert pin(path)==expected;old[str(path.relative_to(R))]=desc(path)
    old_collector=R/'data/phase362-oracle-capture-source/collector.gd'
    assert pin(old_collector)==dict(size=44575,sha256='35676e172400f079dfd3415eafc42103e130bdb1efcfe8fdaad6428faf4854ca')
    previous=R/'data/phase362-oracle-capture-source/combined-source-freeze.json'
    assert pin(previous)==dict(size=51238,sha256='f9293850ec7f32b2ace247671b9ff6aa6eab657a4fc052947b972b8fd14cdb48')
    freeze=copy.deepcopy(json.loads(previous.read_text()))
    changes={};expected_changed={'storage':{'state_write','lease','reset_previous','install'},
                                 'process':{'execute_process'},'host':{'source_gate','plan','execute'}}
    for stem in ('storage','process','host'):
        before_path=R/f'tests/phase362_oracle_{stem}.py';after_path=R/f'tests/phase363_oracle_{stem}.py'
        before,after=before_path.read_text(),after_path.read_text()
        compile(after,str(after_path),'exec')
        base_tree,tree=ast.parse(before),ast.parse(after)
        original={node.name:node for node in base_tree.body if isinstance(node,ast.FunctionDef)}
        actual={node.name:node for node in tree.body if isinstance(node,ast.FunctionDef)}
        changed={name for name in original if ast.dump(original[name],include_attributes=False)!=ast.dump(actual[name],include_attributes=False)}
        assert changed==expected_changed[stem],(stem,changed)
        if stem=='host':
            normalized=after.replace('from phase363_oracle_storage import','from phase362_oracle_storage import').replace('from phase363_oracle_process import','from phase362_oracle_process import')
            normalized=normalized.replace("SOURCE = 'data/phase363-oracle-repair-source'\nDATA = 'data/phase362-oracle-capture-source'","SOURCE = 'data/phase362-oracle-capture-source'")
            normalized=normalized.replace("DATA+'/case-A","SOURCE+'/case-A").replace("DATA+'/collector.gd'","SOURCE+'/collector.gd'").replace("DATA+'/disposable-marker.txt'","SOURCE+'/disposable-marker.txt'")
            normalized=normalized.replace('INDEPENDENT363_INSTALLER_MONITOR_SOURCE_ACCEPTED_ROOT_PENDING','INDEPENDENT362_ORACLE_CAPTURE_SOURCE_ACCEPTED_ROOT_PENDING')
            normalized=normalized.replace('phase363-root-oracle-acceptance/1','phase362-root-oracle-acceptance/1')
            assert normalized==before,'host exact protocol/import-only inverse'
        else:
            restored=copy.deepcopy(tree)
            restored.body=[copy.deepcopy(original[node.name]) if isinstance(node,ast.FunctionDef) else node for node in restored.body
                           if not isinstance(node,ast.FunctionDef) or node.name in original]
            if stem=='process':
                restored.body=[node for node in restored.body if not isinstance(node,ast.Import) or [x.name for x in node.names]!=['math']]
                for node in restored.body:
                    if isinstance(node,ast.ImportFrom) and node.module=='phase363_oracle_storage':node.module='phase362_oracle_storage'
            assert ast.dump(restored,include_attributes=False)==ast.dump(base_tree,include_attributes=False),stem+' exact inverse AST'
        changes[stem]=dict(before=desc(before_path),after=desc(after_path),changed_existing_functions=sorted(changed),
            added_functions=sorted(set(actual)-set(original)),unchanged_functions=sorted(set(original)-changed),
            inverse='EXACT_BYTES_PROTOCOL_REPLACEMENTS' if stem=='host' else 'EXACT_MODULE_AST_BY_DECLARED_FUNCTION_REPLACEMENTS')
        (D/(stem+'-source.patch')).write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='frozen362/'+stem+'.py',tofile='source363/'+stem+'.py')))
    process_tree=ast.parse((R/'tests/phase363_oracle_process.py').read_text())
    funcs={n.name:n for n in process_tree.body if isinstance(n,ast.FunctionDef)}
    waits=[ast.unparse(n) for n in ast.walk(funcs['monitor_command']) if isinstance(n,ast.Call) and ast.unparse(n.func).endswith(('.wait','.sleep'))]
    assert not waits
    assert len([n for n in ast.walk(funcs['monitor_command']) if isinstance(n,ast.Call) and ast.unparse(n.func).endswith('.select')])==1
    storage_tree=ast.parse((R/'tests/phase363_oracle_storage.py').read_text())
    storage_funcs={n.name:n for n in storage_tree.body if isinstance(n,ast.FunctionDef)}
    assert any(isinstance(n,ast.Call) and ast.unparse(n.func)=='regular_target' for n in ast.walk(storage_funcs['install']))
    # Preserve exact collector/75source/case/marker payload paths, replace only3 tools.
    replaced=[]
    for row in freeze['files']:
        for stem in ('storage','process','host'):
            if row['path']==f'tests/phase362_oracle_{stem}.py':
                row.clear();row.update(desc(R/f'tests/phase363_oracle_{stem}.py'));replaced.append(stem);break
    assert sorted(replaced)==['host','process','storage']
    freeze['schema']='phase363-oracle-installer-monitor-repair-SOURCE/1'
    freeze['repair_origin']=desc(previous)
    freeze['repair_finding']=desc(R/'data/phase362-independent-source-review/findings.json')
    freeze['files'] += [desc(Path(__file__)),desc(R/'docs/phase363_installer_monitor_source_repair_spec.md')]
    for row in freeze['files']:assert desc(R/row['path'])==row,row['path']
    for name,row in freeze['paths'].items():assert pin(R/row['after_path'])==row['after']
    assert freeze['paths']==json.loads(previous.read_text())['paths'] and len(freeze['paths'])==75
    save('combined-source-freeze.json',freeze)
    save('source-delta-proof.json',dict(schema='phase363-bounded-source-delta/1',modules=changes,
        collector_byte_identical=desc(old_collector),three_case_inputs=[desc(p) for p in sorted((R/'data/phase362-oracle-capture-source/case-A').iterdir())],
        unchanged_static_layers='Reused independent3627successful layers via exact source identities; not rerun',
        generic_monitor_wait_calls=waits,generic_monitor_selector_calls=1,operational_helpers_executed=False))
    save('api-contract.json',dict(schema='phase363-repaired-monitor-installer-API/1',
        generic='monitor_command(argv,cwd,env,output_dir,prefix,wall_seconds,*,scan_callback=None,poll_seconds=.05,term_grace_seconds=.2,kill_grace_seconds=.5,log_limit_bytes=32MiB,phase_markers=(),initial_phase_seconds=None,abort_markers=())',
        cleanup='cleanup_process_group(proc,term_grace_seconds=5.,kill_grace_seconds=.5); own PGID/SID only; leader exit does not skip TERM/KILL',
        generic_scope='GENERIC_SUBPROCESS_MONITOR_ONLY_NOT_ORACLE_OR_CAPTURE; generic subprocess1/oracle0, no capture APIs',
        wrapper='execute_process(source_root,task,run,project,check_only=False); no argv override, actual native count only here',
        mutable_gate='regular_target before backup creation and atomic_image rechecks preimage; no inplace truncation',
        reporting='single selector wait plus IO/scan overhead; actual scan samples/max gap; cleanup duration separate; zombies not claimed reaped',
        reserved_SOURCE_PASS='INDEPENDENT363_INSTALLER_MONITOR_SOURCE_ACCEPTED_ROOT_PENDING',
        root_config_schema='phase363-root-oracle-acceptance/1',write_policy='bounded-writers-and-monitored-process/1'))
    for name,row in old.items():assert desc(R/name)==row,name
    save('old-source-readback.json',dict(status='ALL_OLD_REFERENCED_SOURCE_AND_FAILURE_LEAVES_IDENTICAL',files=list(old.values())))
    save('summary.json',dict(schema='phase363-author-source-handoff/1',status='SOURCE_REPAIR_FROZEN_INDEPENDENT_CONTROLS_PENDING',
        freeze=desc(D/'combined-source-freeze.json'),modules=changes,
        install_calls=0,monitor_calls=0,synthetic_subprocesses=0,hostplan=0,pool=0,Godot=0,native=0,models=0,projection=0,
        collector_or_effect_changes=False,all_old_source_unchanged=True,independent_FINAL=False,no_more_writes=True))
    own=[R/f'tests/phase363_oracle_{stem}.py' for stem in ('storage','process','host')]
    own += [Path(__file__),R/'docs/phase363_installer_monitor_source_repair_spec.md']
    own += sorted(path for path in D.rglob('*') if path.is_file())
    rows=[desc(path) for path in own];assert len({r['path'] for r in rows})==len(rows)
    save('source-owner.json',dict(schema='phase363-source-owner/1',root=str(R),files=rows,scope='new bounded SOURCE only; not independent FINAL'))
    for row in json.loads((D/'source-owner.json').read_text())['files']:assert desc(R/row['path'])==row
    print(json.dumps(dict(status='SOURCE_ONLY_ALL_OWNER_LEAVES_READ_BACK',freeze=desc(D/'combined-source-freeze.json'),owner=desc(D/'source-owner.json'),leaves=len(rows),bytes=sum(r['size'] for r in rows))))


if __name__=='__main__':main()
