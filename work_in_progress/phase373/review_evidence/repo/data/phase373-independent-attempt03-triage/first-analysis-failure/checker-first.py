"""Readonly control/SOURCE triage; no GD/schema/model execution."""
import ast
import csv
import hashlib
import io
import json
import re
from pathlib import Path

R = Path(__file__).resolve().parents[1]
D = R / 'data/phase373-independent-attempt03-triage'
RUN = Path('/workspace/native-combat-20261013/runs/original027-king-single-A-20261025-attempt03')
B = Path('/workspace/godotsteam-startup-20261013/baseline/Backpack Battles')
SOURCES = {}

def identity(p):
    b = p.read_bytes()
    return {'size': len(b), 'sha256': hashlib.sha256(b).hexdigest()}

def src(p):
    p = Path(p)
    if not p.is_absolute(): p = R / p
    b = p.read_bytes()
    SOURCES[str(p)] = identity(p)
    return b.decode('utf-8-sig')

def put(name, value):
    p = D / name
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x') as f: json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n')

def main():
    D.mkdir(exist_ok=False)
    source_owner = json.loads((R/'data/phase373-independent-source/source-owner.json').read_text())
    for x in source_owner['files']:
        assert identity(R/x['path']) == {k:x[k] for k in ('size','sha256')}
    controls = {}
    for name in ['parse-process-result.json','native-process-result.json','source-partition.json','process_result.json']:
        p = RUN/'output'/name
        b=p.read_bytes(); (D/'controls').mkdir(exist_ok=True)
        (D/'controls'/name).write_bytes(b); controls[name]=json.loads(b)
    for name in ['observer7_failure.json','collector-first-failure.json']:
        p=RUN/'output/capture'/name; b=p.read_bytes()
        (D/'controls'/name).write_bytes(b); controls[name]=json.loads(b)
    assert controls['observer7_failure.json']['code']=='SOURCE_UNKNOWN_SELECTED_HOOK'
    assert controls['observer7_failure.json']['site']=='Items/Food.gd::prepare'
    assert controls['observer7_failure.json']['capture_complete'] is False
    opaque={p.name:identity(p) for p in sorted((RUN/'output/capture').iterdir()) if p.is_file()}
    for group in ['lawful_inputs_present','expected_observations_opaque','control_failures_opaque']:
        for name, desc in controls['source-partition.json'].get(group,{}).items():
            assert opaque[name]=={k:desc[k] for k in ('size','sha256')}
    freeze_path='data/phase370-oracle-source/combined-source-freeze.json'
    freeze=json.loads(src(freeze_path)); gd={}
    for logical, row in freeze['paths'].items():
        p=R/row['after_path']; assert identity(p)==row['after']; gd[logical]=src(p)
    sink=gd['native_random_observer_sink_v7.gd']
    sites=json.loads(re.search(r'^const SITES = (.*)$',sink,re.M).group(1))
    slots=json.loads(re.search(r'^const SOURCE_SLOT_TABLE = (.*)$',sink,re.M).group(1))
    schema=src('tests/phase360_king_observer_schema.py'); tree=ast.parse(schema)
    matrix=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='MATRIX' for t in n.targets))
    emitted={}
    for logical, text in gd.items():
        if logical=='native_random_observer_sink_v7.gd': continue
        for lineno,line in enumerate(text.splitlines(),1):
            m=re.search(r'NativeRandomObserver\.(entry|leave)\("([^"\n]+)"',line)
            if m: emitted.setdefault(m.group(2),[]).append({'file':logical,'line':lineno,'edge':m.group(1),'text':line.strip()})
    # Original ItemBook explicitly assigns itemIndex from the CSV id column.
    book=src(B/'Sheets/ItemBook.gd')
    csv_text=src(B/'Sheets/CSV/ItemData.csv')
    rows={int(x['id']):x for x in csv.DictReader(io.StringIO(csv_text)) if x['id'].strip()}
    assert 'var index = table.getInt("id", line)' in book and 'item.itemIndex = index' in book
    # Resolve real class_name links without loading scripts. Only selected chains
    # and class declarations are relevant; no assets are copied.
    classes={}
    for name in ['Item','Food','Potion','Goobert','Bag','Weapon']:
        p=B/'Items'/f'{name}.gd'
        text=src(p)
        m=re.search(r'^class_name\s+(\w+)',text,re.M)
        if m: classes[m.group(1)]=p
    selected={}; ancestors=set()
    for index in sorted({x['item_index'] for x in slots}):
        name=rows[index]['name']; stem=name.replace(' ','')
        scenes=[B/'Items'/f'{stem}.tscn',B/'Items/Exclusive'/f'{stem}.tscn',B/'Items/Exclusive/Chess'/f'{stem}.tscn']
        scene=next(p for p in scenes if p.is_file()); scene_text=src(scene)
        # Root scene script assignment refers to an ext_resource script id.
        script_map=dict((i,path) for path,i in re.findall(r'\[ext_resource path="res://([^"\n]+\.gd)" type="Script" id=(\d+)\]',scene_text))
        script_ids=re.findall(r'^script = ExtResource\( (\d+) \)',scene_text,re.M)
        if not script_ids:
            raise AssertionError(('selected scene needs explicit script binding',scene))
        chain=[]; current=B/script_map[script_ids[0]]
        while True:
            logical=str(current.relative_to(B)); text=src(current); chain.append(logical); ancestors.add(logical)
            match=re.search(r'^extends\s+(\w+)',text,re.M)
            if not match or match.group(1) not in classes: break
            current=classes[match.group(1)]
        selected[str(index)]={'csv_name':name,'scene':str(scene.relative_to(B)),'script_ancestry':chain,'roles':[x['instance_id'] for x in slots if x['item_index']==index]}
    selected_emitted={k:v for k,v in emitted.items() if k.split('::')[0] in ancestors}
    missing_all=sorted(set(emitted)-set(sites))
    missing_selected=sorted(set(selected_emitted)-set(sites))
    assert 'Items/Food.gd::prepare' in missing_selected
    assert 'Items/Food.gd::prepare' not in matrix['sites']
    food_original=src('data/phase298-native68-source/before-source/Items/Food.gd')
    food_patched=gd['Items/Food.gd']
    stripped='\n'.join(line for line in food_patched.splitlines() if 'NativeRandomObserver.' not in line)+'\n'
    assert stripped==food_original
    source_result={'frozen_paths_verified':len(gd),'declared_sink_sites':len(sites),'schema_sites':len(matrix['sites']),
       'literal_entry_leave_sites':len(emitted),'emitted_not_declared_all':missing_all,
       'selected_items':selected,'selected_ancestor_files':sorted(ancestors),
       'selected_literal_sites':selected_emitted,'selected_emitted_not_declared':missing_selected,
       'sink_schema_missing_selected':sorted(set(selected_emitted)-set(matrix['sites'])),
       'food_original_byte_inverse':True,'itemBook_index_policy_source':{'path':'Sheets/ItemBook.gd','lines':book.splitlines()[730:770]+book.splitlines()[915:935]},
       'limits':'Literal entry/leave audit only; not all dynamic call targets, runtime coverage, or unknown-hook guard relaxation.'}
    put('source-dispatch-audit.json',source_result)
    concise={}
    for k in ['parse-process-result.json','native-process-result.json']:
        x=controls[k]; concise[k]={z:x.get(z) for z in ['exit_code','duration_seconds','process_clean_exit','timed_out','cleanup','parse_only']}
    concise['observer_failure']=controls['observer7_failure.json']; concise['collector_failure']=controls['collector-first-failure.json']
    concise['lawful_inputs_missing']=controls['source-partition.json']['lawful_inputs_missing']
    concise['lawful_inputs_present']=list(controls['source-partition.json']['lawful_inputs_present'])
    put('actual-controls.json',concise); put('capture-opaque-identities.json',opaque)
    # Baseline source snapshots are small selected code/scene/CSV provenance only;
    # no external path is an immutable owner leaf.
    source_identity=[]
    for path,desc in SOURCES.items():
        p=Path(path)
        if p.is_relative_to(R): dest=p.relative_to(R).as_posix()
        else:
            target=D/'SOURCE/original'/p.relative_to(B); target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes());dest=target.relative_to(R).as_posix()
        source_identity.append({'path':dest,**desc,'provenance':path})
    put('source-identities.json',source_identity)
    put('finding.json',{'status':'BLOCKED373_SELECTED_INHERITED_FOOD_PREPARE_HOOK_UNDECLARED',
       'direct':concise,'source_derived':{'selected_missing_hooks':missing_selected,'food_inverse_original':True,
       'dispatch':'entry/leave -> source_observable: bound selected ID + unknown SITES -> fail; original Food.prepare invokes Item.prepare then speed bonus. Failure writes durable record but does not abort the GD business method.',
       'identity_limit':'Failure record does not include object ID/role; selected Food ancestry and fixed selected Food roles establish SOURCE reachability, not the exact failing role.',
       'sequence_limit':'159 is the observer sequence counter at fail, not event index or proof of complete records.',
       'minimal_repair':'Keep unknown-hook guard. Add exact inherited Food.prepare declaration/typed generic-item state/empty arguments/NIL implicit return consistently to sink/schema/record matrix, with original Food business and fixed fixture/seeds untouched; verify finite selected ancestry dispatch closure before a separate native retry.'},
       'actual12_positive':False,'battle_positive':False,'native':0,'models':0,'probes':0,'pool_changes':0,'projection_builds':0,'expected_semantics_read':False,
       'remaining':['Four lawful files missing; partial inputs cannot construct accepted input bundle.','No terminal/clock/fullsnapshot or event/history acceptance.','Out-of-selected-family hook differences not admitted.']})
    paths=[p for p in D.rglob('*') if p.is_file()]+[R/'tests/phase373_independent_attempt03_triage.py',R/'docs/phase373_attempt03_independent_triage_spec.md',R/'data/phase373-independent-source/source-owner.json']
    paths += [R/x['path'] for x in source_identity]
    unique=sorted(set(paths))
    owner={'files':[{'path':p.relative_to(R).as_posix(),**identity(p)} for p in unique]}
    put('owned-files.json',owner)
    for row in owner['files']: assert identity(R/row['path'])=={k:row[k] for k in ('size','sha256')}
    print(json.dumps({'status':'BLOCKED373_SELECTED_INHERITED_FOOD_PREPARE_HOOK_UNDECLARED','selected_missing':missing_selected,'paths':len(gd),'owner_leaves':len(owner['files']),'finding':identity(D/'finding.json'),'owner':identity(D/'owned-files.json')}))

if __name__=='__main__': main()
