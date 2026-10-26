"""SOURCE-only repair of the script-visible emit_signal return contract."""
from pathlib import Path
import ast
import copy
import difflib
import hashlib
import json
import re

R=Path(__file__).resolve().parents[1]
D=R/'data/phase370-oracle-source'


def pin(path):
    raw=path.read_bytes();return dict(size=len(raw),sha256=hashlib.sha256(raw).hexdigest())


def desc(path):
    assert path.is_relative_to(R) and not any(p.is_symlink() for p in (path,*path.parents))
    return dict(path=str(path.relative_to(R)),**pin(path))


def save(name,value):
    with (D/name).open('x') as stream:stream.write(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')


def derive(before,pairs):
    after=before
    for a,b in pairs:
        assert a in after,repr(a);after=after.replace(a,b)
    inverse=after
    for a,b in reversed(pairs):inverse=inverse.replace(b,a)
    assert inverse==before,'exact complete byte inverse'
    return after


def gd_functions(text):
    marks=list(re.finditer(r'^(func|var|const|signal|class)\s+(\w+)',text,re.M));result={}
    for i,m in enumerate(marks):
        if m.group(1)=='func':result[m.group(2)]=text[m.start():marks[i+1].start() if i+1<len(marks) else len(text)]
    return result


def main():
    finding=R/'data/phase369-independent-execution/first-source-block.json'
    assert pin(finding)==dict(size=7856,sha256='afcc1979c916733ba6558038d486886ea4e2202ef00fcd68eb7e5d33e217e4bf')
    evidence=json.loads(finding.read_text());assert evidence['native_Error_observable_to_script'] is False
    D.mkdir(exist_ok=False);(D/'after-source').mkdir()
    old={}
    for name in ('data/phase369-oracle-source/source-owner.json','data/phase369-independent-execution/owned-files.json'):
        path=R/name;old[name]=desc(path)
        for row in json.loads(path.read_text())['files']:assert desc(R/row['path'])==row,row['path'];old[row['path']]=row
    for row in json.loads((R/'data/phase369-oracle-source/old-source-readback.json').read_text())['files']:
        assert desc(R/row['path'])==row,row['path'];old[row['path']]=row
    sink_pairs=[
        ('source_cut_emit_error','source_cut_script_return'),
        ('var source_cut_script_return = null','var source_cut_script_return = null\nvar source_cut_script_return_observed = false'),
        ('"emit_error": source_cut_script_return','"script_emit_return": source_cut_script_return, "script_emit_return_observed": source_cut_script_return_observed, "native_emit_error_available": false, "native_emit_error": null'),
        ('if receiver == null or not receiver.has_method("finish_source_cut"):', 'if receiver == null or not receiver.has_method("on_idle_source_cut") or not receiver.has_method("finish_source_cut"):'),
        ('source_cut_script_return = emit_signal("source_idle_cut_ready")','source_cut_script_return = emit_signal("source_idle_cut_ready")\n\tsource_cut_script_return_observed = true'),
        ('# An OK Error return is not a callback acknowledgement.','# Script NIL is not a callback acknowledgement; native Error is unavailable.'),
        ('if typeof(source_cut_script_return) != TYPE_INT or source_cut_script_return != OK or source_cut_ack == null or failed:',
         'if typeof(source_cut_script_return_observed) != TYPE_BOOL or not source_cut_script_return_observed or typeof(source_cut_script_return) != TYPE_NIL or source_cut_ack == null or failed:')]
    collector_pairs=[
        ('control.emit_error != null', 'typeof(control.script_emit_return_observed) != TYPE_BOOL or control.script_emit_return_observed or typeof(control.script_emit_return) != TYPE_NIL or typeof(control.native_emit_error_available) != TYPE_BOOL or control.native_emit_error_available or control.native_emit_error != null'),
        ('typeof(control.emit_error) != TYPE_INT or control.emit_error != OK', 'typeof(control.script_emit_return_observed) != TYPE_BOOL or not control.script_emit_return_observed or typeof(control.script_emit_return) != TYPE_NIL or typeof(control.native_emit_error_available) != TYPE_BOOL or control.native_emit_error_available or control.native_emit_error != null')]
    rows=[]
    files=[(R/'data/phase368-oracle-source/after-source/native_random_observer_sink_v7.gd',D/'after-source/native_random_observer_sink_v7.gd',sink_pairs,{'source_cut_control','emit_source_idle_cut_once'}),
        (R/'tests/phase368_sink_control_delta.gd',R/'tests/phase370_sink_control_delta.gd',sink_pairs,{'source_cut_control','emit_source_idle_cut_once'}),
        (R/'data/phase369-oracle-source/collector.gd',D/'collector.gd',collector_pairs,{'on_idle_source_cut','finish_source_cut'}),
        (R/'tests/phase369_collector_control_delta.gd',R/'tests/phase370_collector_control_delta.gd',collector_pairs,{'on_idle_source_cut','finish_source_cut'})]
    for before_path,after_path,pairs,expected in files:
        before=before_path.read_text();after=derive(before,pairs);after_path.write_text(after)
        assert 'source_cut_emit_error' not in after and 'control.emit_error' not in after and '"emit_error"' not in after
        oldfunc,newfunc=gd_functions(before),gd_functions(after)
        assert oldfunc.keys()==newfunc.keys()
        changed={name for name in oldfunc if oldfunc[name]!=newfunc[name]};assert changed==expected,changed
        rows.append(dict(before=desc(before_path),after=desc(after_path),literal_pairs=pairs,changed_functions=sorted(changed),
            unchanged_functions=sorted(oldfunc.keys()-changed),inverse='EXACT_COMPLETE_BYTES'))
        if after_path.is_relative_to(D):
            stem='sink' if 'after-source' in str(after_path) else 'collector'
            (D/(stem+'-source.patch')).write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='frozen/'+stem+'.gd',tofile='source370/'+stem+'.gd')))
    save('GD-inverse-ledger.json',dict(schema='phase370-script-return-byte-inverse/1',files=rows))
    py=[]
    for stem in ('oracle_host','pool_recovery'):
        before_path=R/f'tests/phase369_{stem}.py';after_path=R/f'tests/phase370_{stem}.py'
        pairs=[('data/phase369-oracle-source','data/phase370-oracle-source'),
            ('INDEPENDENT369_SCENETREE_COLLECTOR_SOURCE_REPAIR_ACCEPTED_ROOT_PENDING','INDEPENDENT370_SCRIPT_SIGNAL_RETURN_SOURCE_REPAIR_ACCEPTED_ROOT_PENDING'),
            ('phase369-root-oracle-acceptance/1','phase370-root-oracle-acceptance/1')] if stem=='oracle_host' else [
            ('from phase369_oracle_host import','from phase370_oracle_host import'),
            ('INDEPENDENT369_RESTORED_POOL_EXACT_TARGET_READBACK_PASS','INDEPENDENT370_RESTORED_POOL_EXACT_TARGET_READBACK_PASS'),
            ('phase369-root-pool-recovery/1','phase370-root-pool-recovery/1')]
        before=before_path.read_text();after=derive(before,pairs);after_path.write_text(after);compile(after,str(after_path),'exec')
        original={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(before).body if isinstance(n,ast.FunctionDef)}
        actual={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(after).body if isinstance(n,ast.FunctionDef)}
        changed={k for k in original if original[k]!=actual[k]};assert changed=={'source_gate'}
        py.append(dict(before=desc(before_path),after=desc(after_path),literal_pairs=pairs,changed_binding_functions=sorted(changed),unchanged_functions=sorted(original.keys()-changed),inverse='EXACT_COMPLETE_BYTES'))
    save('Python-inverse-ledger.json',dict(files=py))
    sink=(D/'after-source/native_random_observer_sink_v7.gd').read_text();collector=(D/'collector.gd').read_text()
    sf,cf=gd_functions(sink),gd_functions(collector)
    assert sf['emit_source_idle_cut_once'].count('= emit_signal(')==1
    assert 'source_cut_script_return = emit_signal("source_idle_cut_ready")\n\tsource_cut_script_return_observed = true\n\tsource_cut_dispatching = false' in sink
    assert 'native_emit_error_available": false, "native_emit_error": null' in sf['source_cut_control']
    assert 'get_tree()' not in collector
    assert all(x not in cf['finish_source_cut'] for x in ('stable_snapshot(', 'source_runtime_snapshot(', 'getStats(', 'game.'))
    save('control-reference-matrix.json',dict(schema='phase370-control-return-ABI/1',
        erratum='Prior368/369 Error assumption preserved as failed SOURCE. GDScript wrapper returns NIL, native Error unavailable.',
        source=finding.relative_to(R).as_posix(),script_return=dict(before_call=None,before_observed=False,after_call='ACTUAL_NIL',after_observed=True),
        native_error=dict(available=False,value=None,provenance='SOURCE_WRAPPER_DISCARDS_NATIVE_ERROR_NOT_OBSERVED_OK0'),
        references={stem:[dict(line=i,text=line) for i,line in enumerate(text.splitlines(),1) if 'script_emit_return' in line or 'source_cut_script_return' in line or 'native_emit_error' in line]
            for stem,text in [('sink',sink),('collector',collector)]},
        finish_return=dict(contract='ACTUAL_SCRIPT_BOOL',source=evidence['finalizer_call_return_SOURCE'],runtime_observed=False),
        accepted12_changed=False,UI17_changed=False,clock_pass_ABI_changed=False))
    source=R/'data/phase369-oracle-source/combined-source-freeze.json';freeze=copy.deepcopy(json.loads(source.read_text()))
    oldpaths=copy.deepcopy(freeze['paths'])
    replacements={row['before']['path']:row['after'] for row in rows}
    replacements.update({row['before']['path']:row['after'] for row in py})
    for row in freeze['files']:
        if row['path'] in replacements:value=replacements[row['path']];row.clear();row.update(value)
    additions=[Path(__file__),R/'docs/phase370_script_signal_return_source_repair_spec.md',finding,
        R/'data/phase369-independent-execution/review.json',R/'data/phase369-independent-execution/owned-files.json']
    freeze['files'] += [desc(p) for p in additions]
    assert len({x['path'] for x in freeze['files']})==len(freeze['files'])
    pathrow=freeze['paths']['native_random_observer_sink_v7.gd'];pathrow['after_path']=str((D/'after-source/native_random_observer_sink_v7.gd').relative_to(R));pathrow['after']=pin(D/'after-source/native_random_observer_sink_v7.gd')
    assert {k:v for k,v in freeze['paths'].items() if k!='native_random_observer_sink_v7.gd'}=={k:v for k,v in oldpaths.items() if k!='native_random_observer_sink_v7.gd'}
    freeze.update(schema='phase370-script-signal-return-repair-SOURCE/1',repair_origin=desc(source),repair_finding=desc(finding),collector=desc(D/'collector.gd'),current_authorized_operations=0)
    for row in freeze['files']:assert desc(R/row['path'])==row
    for row in freeze['paths'].values():assert pin(R/row['after_path'])==row['after']
    save('combined-source-freeze.json',freeze)
    save('api-contract.json',dict(schema='phase370-source-contract/1',host_schema='phase370-root-oracle-acceptance/1',recovery_schema='phase370-root-pool-recovery/1',
        review_status='INDEPENDENT370_SCRIPT_SIGNAL_RETURN_SOURCE_REPAIR_ACCEPTED_ROOT_PENDING',independent_readback_status='INDEPENDENT370_RESTORED_POOL_EXACT_TARGET_READBACK_PASS',
        script_emit_return='NIL_WITH_OBSERVED_MARKER',native_emit_error='UNAVAILABLE_NOT_OK0',finish_return='ACTUAL_BOOL',
        fixed_attempt03_name=freeze['run_name'],real_SOURCE_acceptance=None,root_execute=None,root_restore=None,
        map_reused=desc(R/'data/phase368-attempt02-recovery-source/restore-map.json'),map_generation_calls=0,old356='CLOSED',old361='CLOSED'))
    for name,row in old.items():assert desc(R/name)==row,name
    save('old-source-readback.json',dict(status='ALL_REFERENCED_OLD_LEAVES_IDENTICAL',files=list(old.values())))
    compile(Path(__file__).read_text(),str(Path(__file__)),'exec')
    save('summary.json',dict(schema='phase370-source-handoff/1',status='SOURCE_FROZEN_INDEPENDENT_REVIEW_PENDING',freeze=desc(D/'combined-source-freeze.json'),
        oldError_assumption_corrected_only_in_newSource=True,other74_patch_paths_unchanged=True,map_regenerated=False,
        probes=0,Game=0,actual_pool_inventory=0,recovery=0,models=0,independent_FINAL=False,no_more_writes=True))
    own=[Path(__file__),R/'docs/phase370_script_signal_return_source_repair_spec.md']+[R/'tests'/name for name in
        ('phase370_sink_control_delta.gd','phase370_collector_control_delta.gd','phase370_oracle_host.py','phase370_pool_recovery.py')]
    own+=sorted(p for p in D.rglob('*') if p.is_file());owned=[desc(p) for p in own]
    save('source-owner.json',dict(schema='phase370-source-owner/1',files=owned,scope='SOURCE only; not independent/native acceptance'))
    for row in owned:assert desc(R/row['path'])==row
    print(json.dumps(dict(freeze=desc(D/'combined-source-freeze.json'),owner=desc(D/'source-owner.json'),leaves=len(owned),bytes=sum(x['size'] for x in owned))))


if __name__=='__main__':main()
