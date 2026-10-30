"""One immutable SOURCE repair; no imports of the copied candidate."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import stat
import traceback

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/phase505-captured-nonking-source-v2'
OUT=ROOT/'data/phase505-captured-nonking-source-v3'
SPEC=ROOT/'docs/phase505_captured_nonking_source_v3_prefix_repair_spec.md'


def require(ok,message):
    if not ok:raise ValueError(message)


def pin(path):
    info=path.lstat()
    require(stat.S_ISREG(info.st_mode) and info.st_nlink==1 and not path.is_symlink(),'ordinary singlelink Source')
    raw=path.read_bytes()
    return dict(path=str(path.relative_to(ROOT)),size=len(raw),sha256=hashlib.sha256(raw).hexdigest())


def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as stream:json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n')


def functions(text):
    result={}
    for node in ast.parse(text).body:
        if isinstance(node,(ast.FunctionDef,ast.ClassDef)):
            result[node.name]=ast.get_source_segment(text,node)
            if isinstance(node,ast.ClassDef):
                result.update({node.name+'.'+n.name:ast.get_source_segment(text,n) for n in node.body if isinstance(n,ast.FunctionDef)})
    return result


def main():
    require(not OUT.exists(),'unique v3 Source output required')
    OUT.mkdir()
    save(OUT/'generation-started.json',dict(schema='phase505-v3-source-generation-started/1',producer=pin(Path(__file__)),spec=pin(SPEC),candidate_imports=0))
    try:
        freeze=BASE/'candidate-source-freeze.json'
        require(pin(freeze)['sha256']=='b1b7fac6dc6719a70e1c0fb14ff39151e7bac60a275b856bfd921c6a3326c76d','exactv2 freeze')
        rows=json.loads(freeze.read_bytes())['files']
        before={};payload={}
        for row in rows:
            require(pin(ROOT/row['path'])=={k:row[k] for k in ('path','size','sha256')},'v2 Source drift')
            before[row['relative']]=(ROOT/row['path']).read_bytes()
        require(len(before)==15,'exact15')
        key='native_replay_v8/engine.py';old=before[key].decode();old_functions=functions(old)
        name='_validate_captured_whelp_runtime';method=old_functions[name];new_method=method
        edits=[
            ('    table, native_ids, paths, positions, prefixes = {}, set(), set(), set(), {}',
             '    table, native_ids, paths, positions, prefixes = {}, set(), set(), set(), {}\n    path_positions = {}'),
            ("            prefix = tuple(pos[:j])\n            if prefix in prefixes and prefixes[prefix] != tuple(names[:j]):raise ValueError('captured Whelp sparse prefix conflict')\n            prefixes[prefix] = tuple(names[:j])",
             "            prefix = tuple(pos[:j]); name_path = tuple(names[:j])\n            if prefix in prefixes and prefixes[prefix] != name_path:raise ValueError('captured Whelp sparse prefix conflict')\n            if name_path in path_positions and path_positions[name_path] != prefix:raise ValueError('captured Whelp reverse sparse prefix conflict')\n            prefixes[prefix] = name_path; path_positions[name_path] = prefix")]
        inverse=[]
        for a,b in edits:
            require(new_method.count(a)==1,'unique exact new validator repair anchor')
            pos=new_method.index(a);new_method=new_method[:pos]+b+new_method[pos+len(a):]
            inverse.append(dict(before=a,after=b,position=pos))
        restored=new_method
        for row in reversed(inverse):
            pos=row['position'];require(restored[pos:pos+len(row['after'])]==row['after'],'inverse postimage')
            restored=restored[:pos]+row['before']+restored[pos+len(row['after']):]
        require(restored==method,'complete validator inverse')
        require(old.count(method)==1,'one AST target function in module')
        new=old.replace(method,new_method)
        new_functions=functions(new)
        require(set(new_functions)==set(old_functions),'function inventory exact')
        require([n for n in old_functions if old_functions[n]!=new_functions[n]]==[name],'onlyone validator changed')
        legacy=ROOT/'data/phase497-source-three-whelps/staged/native_replay_v8/engine.py'
        original_constraint=functions(legacy.read_text())['_validate_runtime_nodes']
        require('path_positions[name_path] != pos' in original_constraint and 'path_positions[name_path] = pos' in original_constraint,'actual497 inverse-prefix precedent')
        payload=dict(before);payload[key]=new.encode()
        for rel,raw in payload.items():compile(raw,str(OUT/'staged'/rel),'exec',dont_inherit=True)
        for rel,raw in payload.items():
            path=OUT/'staged'/rel;path.parent.mkdir(parents=True,exist_ok=True)
            with path.open('xb') as stream:stream.write(raw)
        after=[dict(pin(OUT/'staged'/rel),relative=rel) for rel in sorted(payload)]
        conserved=[rel for rel in payload if rel!=key]
        require(len(conserved)==14 and all((OUT/'staged'/rel).read_bytes()==before[rel] for rel in conserved),'14filesexact')
        (OUT/'source.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=str((BASE/'staged'/key).relative_to(ROOT)),tofile=str((OUT/'staged'/key).relative_to(ROOT)))))
        save(OUT/'inverse.json',dict(schema='phase505-v3-validator-complete-inverse/1',before=pin(BASE/'staged'/key),after=pin(OUT/'staged'/key),edits=inverse,whole_module_inverse_exact=new.replace(new_method,method)==old))
        save(OUT/'conservation.json',dict(schema='phase505-v3-source-conservation/1',changed_files=[key],changed_functions=[name],conserved_files=sorted(conserved),
            conserved_function_count=len(old_functions)-1,new_functions=0,kernels_business_clock_dispatch_exact=True,allprefixlevels_bothdirections=True))
        api=json.loads((BASE/'api-contract.json').read_bytes())
        api['status']='SOURCE_ONLY_V3_PREFIX_REPAIRED_PENDING506_AND_ACTUAL_INPUT'
        save(OUT/'api-contract.json',api)
        context=[SPEC,Path(__file__),freeze,BASE/'owned-files.json',legacy,
            ROOT/'data/phase506-independent-source-first-review/review.json',ROOT/'data/phase505-source-handoff/owned-files.json']
        save(OUT/'source-context.json',dict(schema='phase505-v3-context/1',files=[pin(p) for p in context],
            selected_legacy_function='_validate_runtime_nodes',only_rule_added='allancestor pathprefix->positionprefix uniqueness',Native_admission=False))
        save(OUT/'compile-only.json',dict(discarded_compile_objects=15,candidate_imports=0,controls=0,models=0,Godot=0,Expected=0,pool=0))
        save(OUT/'candidate-source-freeze.json',dict(schema='phase505-v3-source-freeze/1',files=after,base_freeze=pin(freeze),conserved_files=sorted(conserved),
            profile='pure-combat-whelp-family-A-captured/1',status='FROZEN_COMPILE_ONLY_PENDING506_AND_ACTUAL_INPUT'))
        save(OUT/'first-generation-result.json',dict(schema='phase505-v3-first-source-generation/1',status='SOURCE_FROZEN_PENDING_INDEPENDENT506',
            version_generation_invocations=1,cumulative505_source_generations=3,original_failed=1,v2_success=1,v3_success=1,
            modules=15,changed=1,conserved=14,candidate_imports=0,controls=0,models=0,Godot=0,Expected=0,pool=0))
        files=[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()]+[pin(p) for p in context]
        save(OUT/'owned-files.json',dict(schema='phase505-v3-source-owner/1',files=files,no_more_writes=True,status='SOURCE_ONLY_PENDING506_AND_ACTUAL_NATIVE_INPUT'))
        print(json.dumps(dict(status='SOURCE_FROZEN_NOT_RUN',owner=pin(OUT/'owned-files.json')),sort_keys=True))
    except Exception as error:
        save(OUT/'first-generation-error.json',dict(error_type=type(error).__name__,message=str(error),traceback=traceback.format_exc(),automatic_retry=False,candidate_imports=0,models=0,Godot=0,Expected=0,pool=0))
        raise


if __name__=='__main__':main()
