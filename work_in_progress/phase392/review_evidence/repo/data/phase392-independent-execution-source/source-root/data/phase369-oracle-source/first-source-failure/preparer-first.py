"""Three-expression SceneTree API SOURCE repair; no operational imports or execution."""
from pathlib import Path
import ast
import copy
import difflib
import hashlib
import json
import re

R=Path(__file__).resolve().parents[1]
D=R/'data/phase369-oracle-source'


def pin(path):
    raw=path.read_bytes();return dict(size=len(raw),sha256=hashlib.sha256(raw).hexdigest())


def desc(path):
    assert path.is_relative_to(R) and not any(p.is_symlink() for p in (path,*path.parents))
    return dict(path=str(path.relative_to(R)),**pin(path))


def save(name,value):
    with (D/name).open('x') as stream:stream.write(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')


def main():
    finding=R/'data/phase368-independent-source-review/first-static-counterexample.json'
    assert pin(finding)==dict(size=8666,sha256='40d783ee998f5c7439f5a8431c9e7e6fb2f79cb7b2f3673add81e8c8e92de41d')
    issue=json.loads(finding.read_text());assert len(issue['calls'])==3
    D.mkdir(exist_ok=False)
    old={}
    for name in ('data/phase368-oracle-source/source-owner.json',
                 'data/phase368-independent-source-review/owned-files.json'):
        p=R/name;old[name]=desc(p)
        for row in json.loads(p.read_text())['files']:
            assert desc(R/row['path'])==row,row['path'];old[row['path']]=row
    for row in json.loads((R/'data/phase368-oracle-source/old-source-readback.json').read_text())['files']:
        assert desc(R/row['path'])==row,row['path'];old[row['path']]=row
    source=R/'data/phase368-oracle-source/combined-source-freeze.json'
    assert pin(source)==dict(size=55265,sha256='42843ff87a3ae245f0b9d14f21b588923a4d19cf4cc24ae95614f40bccfa3cec')
    old_collector=R/'data/phase368-oracle-source/collector.gd'
    replacements=[]
    for before_path,after_path in ((old_collector,D/'collector.gd'),
        (R/'tests/phase368_collector_control_delta.gd',R/'tests/phase369_collector_control_delta.gd')):
        before=before_path.read_text();start=before.index('func source_control_snapshot(')
        end=before.index('\nfunc ',start+1);function=before[start:end]
        assert function.count('get_tree()')==3 and before.count('get_tree()')==3
        corrected=function.replace('get_tree()','self');after=before[:start]+corrected+before[end:]
        assert after.replace(corrected,function,1)==before and 'get_tree()' not in after
        after_path.write_text(after)
        replacements.append(dict(before=desc(before_path),after=desc(after_path),function='source_control_snapshot',
            expression_replacements=3,old_function=function,new_function=corrected,inverse='EXACT_FULL_BYTES'))
    before=old_collector.read_text();after=(D/'collector.gd').read_text()
    (D/'collector-source.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='frozen368/collector.gd',tofile='source369/collector.gd')))
    save('collector-inverse-ledger.json',dict(schema='phase369-three-expression-inverse/1',files=replacements))
    changes={}
    pairs=[('data/phase368-oracle-source','data/phase369-oracle-source'),
        ('INDEPENDENT368_SYNCHRONOUS_CUT_SOURCE_ACCEPTED_ROOT_PENDING','INDEPENDENT369_SCENETREE_COLLECTOR_SOURCE_REPAIR_ACCEPTED_ROOT_PENDING'),
        ('phase368-root-oracle-acceptance/1','phase369-root-oracle-acceptance/1')]
    for stem in ('oracle_host','pool_recovery'):
        oldpath=R/f'tests/phase368_{stem}.py';newpath=R/f'tests/phase369_{stem}.py'
        before=oldpath.read_text();after=before;actual=pairs if stem=='oracle_host' else [
            ('from phase368_oracle_host import','from phase369_oracle_host import'),
            ('INDEPENDENT368_RESTORED_POOL_EXACT_TARGET_READBACK_PASS','INDEPENDENT369_RESTORED_POOL_EXACT_TARGET_READBACK_PASS'),
            ('phase368-root-pool-recovery/1','phase369-root-pool-recovery/1')]
        for a,b in actual:assert a in after;after=after.replace(a,b)
        inverse=after
        for a,b in reversed(actual):inverse=inverse.replace(b,a)
        assert inverse==before
        newpath.write_text(after);compile(after,str(newpath),'exec')
        original={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(before).body if isinstance(n,ast.FunctionDef)}
        current={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(after).body if isinstance(n,ast.FunctionDef)}
        changed=sorted(k for k in original if original[k]!=current[k]);assert set(original)==set(current)
        assert changed==(['source_gate'] if stem=='pool_recovery' else ['source_gate'])
        changes[stem]=dict(before=desc(oldpath),after=desc(newpath),literal_pairs=actual,
            exact_inverse='FULL_BYTES',changed_functions_binding_only=changed,unchanged_functions=sorted(set(original)-set(changed)))
        (D/(stem+'-source.patch')).write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='frozen368/'+stem+'.py',tofile='source369/'+stem+'.py')))
    # Read only the newly-added/changed collector functions for the bounded self-receiver API review.
    ledger=json.loads((R/'data/phase368-oracle-source/collector-inverse-ledger.json').read_text())
    additions=re.findall(r'^func\s+(\w+)\(',ledger['removable_suffix'],re.M)
    audited=set(additions)|{row['name'] for row in ledger['replacements']}
    text=(D/'collector.gd').read_text();declarations=list(re.finditer(r'^func\s+(\w+)\(',text,re.M));functions={}
    for i,m in enumerate(declarations):functions[m.group(1)]=text[m.start():declarations[i+1].start() if i+1<len(declarations) else len(text)]
    calls=set()
    for name in audited:
        code=re.sub(r'"(?:\\.|[^"\\])*"','""',functions[name]);code=re.sub(r'#.*','',code)
        calls.update(re.findall(r'(?<![.\w])(\w+)\s*\(',code))
    local=set(functions);builtins={'typeof','str','range','is_instance_valid','print','int','float','floor'}
    scenetree={'get_root','quit'};object_methods={'get_instance_id','is_connected','get_signal_connection_list'}
    unknown=calls-local-builtins-scenetree-object_methods
    assert not unknown,sorted(unknown)
    evidence=[]
    for name,a,b in (
        ('data/phase027-implementation-design/full-source/upstream/scene/main/scene_tree.h',74,80),
        ('data/phase027-implementation-design/full-source/upstream/scene/main/node.h',45,48),
        ('data/phase027-implementation-design/full-source/upstream/scene/main/scene_tree.cpp',2057,2060),
        ('data/phase027-implementation-design/full-source/upstream/scene/main/scene_tree.cpp',2083,2087),
        ('data/phase027-implementation-design/full-source/upstream/scene/main/node.cpp',3130,3134),
        ('data/phase184-ranger-idle-sync-source/source/object.cpp',1682,1686),
        ('data/phase184-ranger-idle-sync-source/source/object.cpp',1728,1737)):
        p=R/name;evidence.append(dict(source=desc(p),start=a,end=b,text=''.join(p.read_text().splitlines(True)[a-1:b])))
    save('static-api-boundary.json',dict(schema='phase369-bounded-collector-api-read/1',audited_functions=sorted(audited),
        implicit_calls=sorted(calls),local_methods=sorted(calls&local),builtins=sorted(calls&builtins),
        SceneTree_implicit=sorted(calls&scenetree),Object_implicit=sorted(calls&object_methods),unknown_implicit=sorted(unknown),
        explicit_receiver_scope='observer/emitter are actual Node/Object, File/Engine/ProjectSettings/Variant calls keep their real receivers; get_root() returns Node',
        no_language_parse_claim=True,evidence=evidence))
    freeze=copy.deepcopy(json.loads(source.read_text()));oldpaths=copy.deepcopy(freeze['paths'])
    mapping={'data/phase368-oracle-source/collector.gd':desc(D/'collector.gd'),
        'tests/phase368_collector_control_delta.gd':desc(R/'tests/phase369_collector_control_delta.gd'),
        'tests/phase368_oracle_host.py':desc(R/'tests/phase369_oracle_host.py'),
        'tests/phase368_pool_recovery.py':desc(R/'tests/phase369_pool_recovery.py')}
    for row in freeze['files']:
        if row['path'] in mapping:
            value=mapping[row['path']];row.clear();row.update(value)
    extras=[Path(__file__),R/'docs/phase369_scenetree_collector_api_source_repair_spec.md',finding,
        R/'data/phase368-independent-source-review/review.json',R/'data/phase368-independent-source-review/owned-files.json']
    freeze['files'] += [desc(p) for p in extras]
    assert len({row['path'] for row in freeze['files']})==len(freeze['files'])
    freeze.update(schema='phase369-collector-self-api-repair-SOURCE/1',repair_origin=desc(source),repair_finding=desc(finding),
        collector=desc(D/'collector.gd'),current_authorized_operations=0)
    assert freeze['paths']==oldpaths
    for row in freeze['files']:assert desc(R/row['path'])==row
    for row in freeze['paths'].values():assert pin(R/row['after_path'])==row['after']
    save('combined-source-freeze.json',freeze)
    save('source-delta-proof.json',dict(schema='phase369-minimal-delta/1',collector_expressions=3,changed_GD_function='source_control_snapshot',
        Python=changes,sink_byte_reused=desc(R/'data/phase368-oracle-source/after-source/native_random_observer_sink_v7.gd'),
        all75_patch_paths_unchanged=True,map_byte_reused=desc(R/'data/phase368-attempt02-recovery-source/restore-map.json'),
        map_generator_calls=0,operational_imports=0,Godot=0,actual_pool=0))
    save('api-contract.json',dict(schema='phase369-source-contract/1',host_schema='phase369-root-oracle-acceptance/1',
        recovery_schema='phase369-root-pool-recovery/1',review_status='INDEPENDENT369_SCENETREE_COLLECTOR_SOURCE_REPAIR_ACCEPTED_ROOT_PENDING',
        independent_readback_status='INDEPENDENT369_RESTORED_POOL_EXACT_TARGET_READBACK_PASS',
        original368_dynamic_controls_executed=0,independent_acceptance=None,root_execution_release=None,root_recovery_release=None,
        fixed_attempt03_name=freeze['run_name'],actual_attempts=0,old356_gate='CLOSED',old361_reader='CLOSED'))
    for name,row in old.items():assert desc(R/name)==row
    save('old-source-readback.json',dict(status='ALL_REFERENCED_OLD_LEAVES_IDENTICAL',files=list(old.values())))
    compile(Path(__file__).read_text(),str(Path(__file__)),'exec')
    save('summary.json',dict(schema='phase369-source-handoff/1',status='SOURCE_FROZEN_INDEPENDENT_REVIEW_PENDING',
        freeze=desc(D/'combined-source-freeze.json'),collector_only3_self_replacements=True,other_GD_or_business_changes=False,
        probes=0,Game=0,actual_pool_inventory=0,recovery=0,models=0,map_regenerated=False,independent_FINAL=False,no_more_writes=True))
    own=[Path(__file__),R/'tests/phase369_collector_control_delta.gd',R/'tests/phase369_oracle_host.py',R/'tests/phase369_pool_recovery.py',
         R/'docs/phase369_scenetree_collector_api_source_repair_spec.md']
    own += sorted(p for p in D.iterdir() if p.is_file());rows=[desc(p) for p in own]
    save('source-owner.json',dict(schema='phase369-source-owner/1',files=rows,scope='SOURCE only, not independent/native acceptance'))
    for row in rows:assert desc(R/row['path'])==row
    print(json.dumps(dict(freeze=desc(D/'combined-source-freeze.json'),owner=desc(D/'source-owner.json'),leaves=len(rows),bytes=sum(row['size'] for row in rows))))


if __name__=='__main__':main()
