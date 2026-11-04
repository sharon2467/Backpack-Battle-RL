"""Fixed admission-only Source derivation; no SUT import or execution."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/phase558-source-bowl-treats'
OUT=ROOT/'data/phase564-source-finite-mixed'
SPEC=ROOT/'docs/phase564_finite_mixed_source_implementation_spec.md'
SCRIPT=Path(__file__).resolve()
PINS={
    'data/phase558-source-bowl-treats/candidate-source-freeze.json':'0ce6289185c03b8a6b42f84ad2dd282b761aaff34a3d5413694747c5428ac23e',
    'data/phase558-source-bowl-treats/owned-files.json':'2ccbbc2ee65113f62451dc49ba31b0e5d8296467109099086c50d60c2d928b77',
    'data/phase563-independent-mixed-design-review/review.json':'443707983bec52e00875d8a98691c82fb82d402336ffae426367c7f850ec5107',
    'data/phase563-independent-mixed-design-review/owned-files.json':'f6a2d60452b42c632e41fe22d7f3baf555fa13188c3c38f2c587ccc6aa06300d',
}
CONSTANT='MIXED_BOWL_ENCHANTED_FIXTURE_IDS = frozenset({1,5,11,14,22,32,162,164,231,233,234,385})\n'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def descriptor(path):
    raw=path.read_bytes()
    return dict(path=str(path.relative_to(ROOT)),size=len(raw),sha256=sha(raw))


def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb')as f:f.write((json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode())


def replace_once(text,before,after):
    if text.count(before)!=1:raise ValueError('strict unique Source anchor required: '+before[:80])
    return text.replace(before,after,1)


def edit_function(text,name,before,after):
    nodes=[n for n in ast.walk(ast.parse(text))if isinstance(n,ast.FunctionDef)and n.name==name]
    if len(nodes)!=1:raise ValueError('unique function required: '+name)
    n=nodes[0];lines=text.splitlines(keepends=True)
    old=''.join(lines[n.lineno-1:n.end_lineno]);lines[n.lineno-1:n.end_lineno]=[replace_once(old,before,after)]
    return ''.join(lines)


def functions(text):
    lines=text.splitlines(keepends=True);result={}
    def walk(n,prefix=''):
        for c in ast.iter_child_nodes(n):
            if isinstance(c,(ast.FunctionDef,ast.ClassDef)):
                name=prefix+c.name
                if isinstance(c,ast.FunctionDef):result[name]=''.join(lines[c.lineno-1:c.end_lineno]).encode()
                walk(c,name+'.')
            else:walk(c,prefix)
    walk(ast.parse(text));return result


def branch(own,other):
    return f'''    if any(entry["item_index"] == {other} for side in fixture["sides"] for entry in side["items"]):
        if (any(side["character_class"] != 0 for side in fixture["sides"])
                or any(entry["item_index"] not in MIXED_BOWL_ENCHANTED_FIXTURE_IDS
                       for side in fixture["sides"] for entry in side["items"])
                or any(sum(entry["item_index"] == {own} for entry in side["items"]) > 1
                       for side in fixture["sides"])):
            raise ValueError("Mixed Bowl/Enchanted Source requires class0, finite twelve-ID fixture and at most one{own} per side")
        return True
'''


def main():
    OUT.mkdir(exist_ok=False)
    try:
        for name,expected in PINS.items():
            if sha((ROOT/name).read_bytes())!=expected:raise ValueError('accepted identity drift: '+name)
        frozen=json.loads((BASE/'candidate-source-freeze.json').read_bytes())['files']
        if len(frozen)!=15 or len({r['relative']for r in frozen})!=15:raise ValueError('exact15 Source required')
        buffers={}
        for row in frozen:
            p=ROOT/row['path']
            if p!=BASE/'staged'/row['relative']or descriptor(p)!={k:row[k]for k in('path','size','sha256')}:raise ValueError('base Source mismatch')
            buffers[row['relative']]=p.read_bytes()
        old_engine=buffers['native_replay_v8/engine.py'].decode()
        engine=replace_once(old_engine,'CACHED_AFFECTED_IDS = ',CONSTANT+'CACHED_AFFECTED_IDS = ')
        added_branches=[]
        for name,own,other in [('validate_bowl_fixture',162,385),('validate_enchanted_fixture',385,162)]:
            anchor=f'''    if not any(entry["item_index"] == {own} for side in fixture["sides"] for entry in side["items"]):
        return True
'''
            extra=branch(own,other);engine=edit_function(engine,name,anchor,anchor+extra);added_branches.append(extra)
        inverse=replace_once(engine,CONSTANT,'')
        for extra in added_branches:inverse=replace_once(inverse,extra,'')
        if inverse!=old_engine:raise ValueError('full engine inverse does not restore exact558')
        outputs=dict(buffers,**{'native_replay_v8/engine.py':engine.encode()})
        for name,raw in outputs.items():compile(raw,name,'exec')
        before=functions(old_engine);after=functions(engine)
        if set(before)!=set(after):raise ValueError('no new function allowed')
        changed=sorted(n for n in before if before[n]!=after[n])
        if changed!=['validate_bowl_fixture','validate_enchanted_fixture']:raise ValueError('unexpected function delta')
        catalog=next(n.value for n in ast.parse(engine).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='CATALOG'for t in n.targets))
        if len(catalog.keys)!=84:raise ValueError('catalog84 unchanged required')
        entries=[];patch=[]
        for name,raw in outputs.items():
            p=OUT/'staged'/name;p.parent.mkdir(parents=True,exist_ok=True)
            with p.open('xb')as f:f.write(raw)
            entries.append(dict(descriptor(p),relative=name))
            patch.extend(difflib.unified_diff(buffers[name].decode().splitlines(True),raw.decode().splitlines(True),fromfile='558/'+name,tofile='564/'+name))
        with(OUT/'source.patch').open('xb')as f:f.write(''.join(patch).encode())
        save(OUT/'base-source-list.json',dict(schema='phase564-base-source/1',freeze=descriptor(BASE/'candidate-source-freeze.json'),files=frozen))
        save(OUT/'candidate-source-freeze.json',dict(schema='phase564-source-freeze/1',status='FROZEN_COMPILE_ONLY_PENDING_INDEPENDENT565',files=entries))
        save(OUT/'compile-only.json',dict(schema='phase564-compile-only/1',files_compiled=15,candidate_imports=0,helpers=0,constructors=0,tests=0,models=0,Expected=0,Native=0,UI=0,pool=0))
        save(OUT/'conservation.json',dict(schema='phase564-conservation/1',changed_files=['native_replay_v8/engine.py'],exact_files=[n for n in outputs if outputs[n]==buffers[n]],
            existing_engine_functions=len(before),exact_existing_engine_functions=len(before)-2,changed_functions=changed,new_functions=0,
            function_deltas=[dict(name=n,before_sha256=sha(before[n]),after_sha256=sha(after[n]))for n in changed],
            full_module_inverse_exact=True,inverse_engine_sha256=sha(inverse.encode()),absent_single_error_branches_exact_after_inverse=True,
            full_validate_fixture_and_all_business_bodies_exact=True,headless_entire_file_exact=True,catalog_registered=84,formal_support=75))
        save(OUT/'source-context.json',dict(schema='phase564-source-context/1',authorities=[descriptor(ROOT/n)for n in PINS],design=descriptor(ROOT/'docs/phase562_finite_mixed_bowl_enchanted_source_design_spec.md'),reused_Source_map=descriptor(ROOT/'data/phase562-finite-mixed-source-design/source-pins.json'),
            change='one fixed constant/two paired admission branches; no runtime algorithm or profile change',runtime_acceptance='PENDING_INDEPENDENT565'))
        save(OUT/'api-contract.json',dict(schema='phase564-api/1',initializer='headless.initialize_experimental_nonking(layout,seed)',validator='headless.validate_experimental_nonking_layout(layout)',mixed_presence='both actual162 and385 anywhere in complete fixture; no caller flag',mixed_ids=[1,5,11,14,22,32,162,164,231,233,234,385],max162_per_side=1,max385_per_side=1,class_domain=[0],catalog_registered=84,formal_support=75,
            private_admission_helpers=['validate_bowl_fixture(fixture)','validate_enchanted_fixture(fixture)'],complete_validation='unchanged validate_fixture calls both, so each caller max is enforced; one helper alone is not complete admission',
            component_APIs='all actual558 business/helper APIs unchanged, exact bodies; same strict private synthetic Tape seam, no public Tape API',
            old_paths='singlecaller/absent/error branches retained verbatim below inserted branch; headless/formal/CLI/batch/Squirrel/King files/gates unchanged',Source_runtime_acceptance='PENDING_INDEPENDENT565'))
        save(OUT/'owned-files.json',dict(schema='phase564-owned-files/1',status='SOURCE_FROZEN_NOT_RUNTIME_ACCEPTED',files=[descriptor(p)for p in[SPEC,SCRIPT]+sorted(p for p in OUT.rglob('*')if p.is_file())]))
        print(json.dumps(dict(status='SOURCE_FROZEN_COMPILE_ONLY',files=15,changed=1,exact=14,owner=descriptor(OUT/'owned-files.json')),sort_keys=True))
    except Exception as error:
        save(OUT/'first-error.json',dict(schema='phase564-first-source-error/1',type=type(error).__name__,error=str(error),candidate_imports=0,helpers=0,models=0,Expected=0,Native=0,pool=0))
        save(OUT/'partial-owner.json',dict(schema='phase564-partial-owner/1',files=[descriptor(p)for p in[SPEC,SCRIPT]+sorted(p for p in OUT.rglob('*')if p.is_file())]))
        raise


if __name__=='__main__':main()
