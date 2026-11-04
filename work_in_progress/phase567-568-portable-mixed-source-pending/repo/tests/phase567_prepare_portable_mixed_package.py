"""Assemble exact564 plus docs only, after actual566 final is pinned."""
import difflib
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/phase567-portable-nonking-package'
PACKAGE=OUT/'package'
BASE=ROOT/'data/phase560-portable-nonking-package/package'
SOURCE=ROOT/'data/phase564-source-finite-mixed'
JOB=ROOT/'data/phase565-exact-business-source/natural-job.json'
FINAL=ROOT/'data/phase566-independent-final-acceptance/review.json'
FINAL_ACCEPTANCE_SHA='37609aabbdfd5cfce50f02a7c4677f499282328903be0136d540e62747476c49'
SPEC=ROOT/'docs/phase567_portable_mixed_source_package_spec.md'
SCRIPT=Path(__file__).resolve()
PINS={
    'data/phase564-source-finite-mixed/candidate-source-freeze.json':'1cf6f925d5bf91ae4b587e17001d80e052932317b8bfa3671aa17e7ff2f073d5',
    'data/phase564-source-finite-mixed/owned-files.json':'a77486321cd984821b598b1e34482a1018e9a48b7b736c7bbcb6bf4e6224a51d',
    'data/phase565-exact-business-source/natural-job.json':'7b7fcb86a0fe82640f024488c15472ab31b2d56143c526e9ed67c8c32638d51e',
    'data/phase560-portable-nonking-package/package/manifest.json':'e8bbd692998b1e7a27f377f5bff6714028c9073961522a3963f7cd9664199a7f',
    'data/phase566-independent-final-acceptance/owned-files.json':'236c70056c490a816498396d1a76053f30b6567b1a7a27ab17261af1785984a5',
}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def descriptor(path):
    raw=path.read_bytes()
    return dict(path=str(path.relative_to(ROOT)),size=len(raw),sha256=sha(raw))


def write(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb')as f:f.write(raw)


def save(path,value):write(path,(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode())


def replace_once(text,before,after):
    if text.count(before)!=1:raise ValueError('unique documentation anchor required: '+before[:80])
    return text.replace(before,after,1)


def main():
    if type(FINAL_ACCEPTANCE_SHA)is not str or len(FINAL_ACCEPTANCE_SHA)!=64:
        raise ValueError('Actual566 independent final identity required before package assembly')
    OUT.mkdir(exist_ok=False)
    try:
        for name,expected in PINS.items():
            if sha((ROOT/name).read_bytes())!=expected:raise ValueError('accepted/presealed identity drift: '+name)
        if sha(FINAL.read_bytes())!=FINAL_ACCEPTANCE_SHA:raise ValueError('actual566 final identity drift')
        for row in json.loads((BASE/'manifest.json').read_bytes())['files']:
            raw=(BASE/row['path']).read_bytes()
            if len(raw)!=row['size']or sha(raw)!=row['sha256']:raise ValueError('560 package payload drift')
        frozen=json.loads((SOURCE/'candidate-source-freeze.json').read_bytes())['files']
        if len(frozen)!=15 or len({r['relative']for r in frozen})!=15:raise ValueError('exact15 Source files required')
        copies=[]
        for row in frozen:
            p=ROOT/row['path'];raw=p.read_bytes()
            if p!=SOURCE/'staged'/row['relative']or descriptor(p)!={k:row[k]for k in('path','size','sha256')}:raise ValueError('564 Source mismatch')
            target=PACKAGE/row['relative'];write(target,raw)
            copies.append(dict(relative=row['relative'],source=descriptor(p),destination=descriptor(target)))
        old_examples=['layout-Wolpertinger.json','layout-Enchanted-Weapons.json','layout-Bowl-Treats.json']
        write(PACKAGE/'verify_manifest.py',(BASE/'verify_manifest.py').read_bytes())
        for name in old_examples:write(PACKAGE/'examples'/name,(BASE/'examples'/name).read_bytes())
        job=json.loads(JOB.read_bytes())
        if set(job)!={'layout','seed','max_seconds'}or type(job['seed'])is not int or job['seed']!=56501:raise ValueError('presealed56501 job required')
        if sum(len(s['items'])for s in job['layout']['sides'])!=29:raise ValueError('presealed mixed29 input required')
        save(PACKAGE/'examples/layout-Mixed-Modifiers.json',job['layout'])
        canonical=lambda value:json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
        if canonical(json.loads((PACKAGE/'examples/layout-Mixed-Modifiers.json').read_bytes()))!=canonical(job['layout']):raise ValueError('layout extraction changed JSON values')
        readme=(BASE/'README.md').read_text()
        readme=replace_once(readme,'byte-exact accepted phase558','byte-exact phase564, independently accepted for the finite mixed Source case566')
        readme=replace_once(readme,'This new exact558 Source','This exact564 Source')
        readme=replace_once(readme,'When385 is present, the **complete fixture**','When385 alone (without162) is present, the **complete fixture**')
        readme=replace_once(readme,'When162 is present, the **complete fixture**','When162 alone (without385) is present, the **complete fixture**')
        readme=replace_once(readme,'''The162 and385 fixture domains are currently **mutually exclusive**. There is no
new mixed162+385 admission, arbitrary allowlist or per-item public initializer.''','''When both162 and385 are present anywhere in the **complete fixture**, the fixed
mixed domain is `{1,5,11,14,22,32,162,164,231,233,234,385}`. There may be at most
one162 and one385 on each side; callers can be on the same or opposing side.
Class0/default/noKing/noGems/no rage remains. Individual caller and absent-caller
domains above stay unchanged. This is a fixed union12, not all75×modifier admission,
a caller-supplied allowlist or a new per-item public initializer. Registry stays84.
Modifier/prepare/cache/RNG/history/Timer business functions are exact558; only the
two paired admission branches and one fixed constant differ in564.''')
        readme=replace_once(readme,'''in any layout. These commands reproduce Source inputs, not original-engine seed/session results.''','''in any layout. The fourth example, `examples/layout-Mixed-Modifiers.json`, is
the presealed565 mixed29 input used unchanged by566; use seed56501 with that same
API. These commands reproduce Source inputs, not original-engine seed/session results.''')
        smoke_start=readme.index('A minimal no-battle smoke command')
        smoke_end=readme.index('## Evidence and remaining scope',smoke_start)
        readme=readme[:smoke_start]+'''The minimal distribution smoke imports and validates only the new mixed example;
it constructs no Engine and does not rerun old examples or any battle:

```sh
python -B - <<'PY'
import json
from pathlib import Path
from headless import validate_experimental_nonking_layout
layout = json.loads(Path('examples/layout-Mixed-Modifiers.json').read_text())
fixture = validate_experimental_nonking_layout(layout)
assert sum(len(side['items']) for side in fixture['sides']) == 29
print('VALIDATED_MIXED29_NO_ENGINE_CONSTRUCTION')
PY
```

'''+readme[smoke_end:]
        readme=replace_once(readme,'Wolpertinger, Enchanted Weapons and Bowl Native comparisons remain pending.','''Independent566 accepted eight directed Source families joined from565's initial
gate and566's remaining controls, plus one unchanged
presealed56501 case after preserving565's first test-fixture failure.564 Source,
layout and seed were not changed to fit output. The natural case hit Pet extra1,
weapon double6, Bowl4/Skill3 activations, Food speed8, Wolper gain47/loss5 feedback,
Mana payment1 and Thorn attack-parent3. Positive Spear Block loss was NOT_HIT in
that natural case; its declared component behavior passed. It had29 items,
222 events,273 selected Source draws and26 business Timers. Counts describe that
finite Source case, not predictions for arbitrary inputs or Native observations.
Wolpertinger, Enchanted Weapons, Bowl and their joint Native comparison remain pending.''')
        readme=replace_once(readme,'all21 listed payloads\n(15 Source, this README, three examples, lineage, verifier)','all22 listed payloads\n(15 Source, this README, four examples, lineage, verifier)')
        write(PACKAGE/'README.md',readme.encode())
        save(PACKAGE/'source-lineage.json',dict(schema='experimental-nonking-source-lineage/4',public_target='python_engine/experimental_nonking',code='exact15 frozen564; only engine admission differs from560; packaging Source edits0',
            source_freeze=descriptor(SOURCE/'candidate-source-freeze.json'),source_owner=descriptor(SOURCE/'owned-files.json'),independent_mixed_Source_acceptance=descriptor(FINAL),independent_mixed_Source_acceptance_owner=descriptor(FINAL.parent/'owned-files.json'),
            previous_package_manifest=descriptor(BASE/'manifest.json'),previous_lineage=descriptor(BASE/'source-lineage.json'),retained_exact_examples=old_examples,
            new_presealed_job=descriptor(JOB),new_presealed_owner=descriptor(JOB.parent/'owned-files.json'),new_layout_transform='extract layout only; preserve typed values/order/geometry/identity; no outcome',new_layout_canonical_sha256=sha(canonical(job['layout'])),new_example_seed=56501,
            catalog_registered=84,formal_support=75,when_both_callers_ids=[1,5,11,14,22,32,162,164,231,233,234,385],max162_per_side=1,max385_per_side=1,caller_sides='same or opposite; both multiplicities checked by full entry',old_single_and_absent_domains='unchanged',
            native_joint='PENDING; fresh Source seed simulation is distinct from conditional Native Tape',Native_seed_session_parity='PENDING',runtime_dependencies='Python3.10+stdlib+package only; provenance paths not required',
            distribution_acceptance='NOT_RECORDED_HERE; future unique remote smoke belongs to independent archive',verifier='exact560'))
        source_names={r['relative']for r in frozen};rows=[]
        for p in sorted(p for p in PACKAGE.rglob('*')if p.is_file()):
            name=str(p.relative_to(PACKAGE));raw=p.read_bytes()
            kind='source'if name in source_names else 'example'if name.startswith('examples/')else 'documentation'if name=='README.md'else 'lineage'if name=='source-lineage.json'else 'verifier'
            rows.append(dict(path=name,kind=kind,size=len(raw),sha256=sha(raw)))
        if len(rows)!=22:raise ValueError('exact22 manifest payloads required')
        save(PACKAGE/'manifest.json',dict(schema='experimental-nonking-package-manifest/1',status='EXACT564_MIXED_SOURCE_ACCEPTED566_PENDING_INDEPENDENT_DISTRIBUTION',public_target='python_engine/experimental_nonking',source_file_count=15,files=rows))
        old={str(p.relative_to(BASE)):p.read_bytes()for p in BASE.rglob('*')if p.is_file()};new={str(p.relative_to(PACKAGE)):p.read_bytes()for p in PACKAGE.rglob('*')if p.is_file()};same=[];changed=[];patch=[]
        for name in sorted(set(old)|set(new)):
            if old.get(name)==new.get(name):same.append(name)
            else:
                changed.append(name);patch.extend(difflib.unified_diff(old.get(name,b'').decode().splitlines(True),new.get(name,b'').decode().splitlines(True),fromfile='560/'+name,tofile='567/'+name))
        write(OUT/'package.patch',''.join(patch).encode())
        save(OUT/'copy-conservation.json',dict(schema='phase567-copy-conservation/1',source_copies=copies,Source_edits=0,package_compiles=0,source_files=15,manifest_payloads=22,physical_package_files=23,old560_exact_files=same,changed_or_added_files=changed,new_example_layout_canonical_sha256=sha(canonical(job['layout'])),
            candidate_imports=0,helpers=0,verifier=0,validation=0,constructors=0,models=0,battles=0,tests=0,Expected=0,Native=0,UI=0,pool=0))
        save(OUT/'independent-smoke-contract.json',dict(schema='phase567-independent-smoke/1',verifier='uniqueREMOTE python -B verify_manifest.py --manifest-sha256 <external trusted SHA>',validator='headless.validate_experimental_nonking_layout',validate_once='examples/layout-Mixed-Modifiers.json',expected_input_items=29,old_examples_rerun=False,constructors=0,RNG=0,battles=0,author_executed=False,distribution_result='external archive only'))
        save(OUT/'owned-files.json',dict(schema='phase567-owned-files/1',status='PACKAGE_FROZEN_PENDING_DISTRIBUTION',files=[descriptor(p)for p in[SPEC,SCRIPT]+sorted(p for p in OUT.rglob('*')if p.is_file())]))
        print(json.dumps(dict(status='PACKAGE_FROZEN',manifest=descriptor(PACKAGE/'manifest.json'),owner=descriptor(OUT/'owned-files.json')),sort_keys=True))
    except Exception as error:
        save(OUT/'first-error.json',dict(schema='phase567-first-error/1',type=type(error).__name__,error=str(error),candidate_imports=0,verifier=0,models=0,Expected=0,Native=0,pool=0))
        save(OUT/'partial-owner.json',dict(schema='phase567-partial-owner/1',files=[descriptor(p)for p in[SPEC,SCRIPT]+sorted(p for p in OUT.rglob('*')if p.is_file())]))
        raise


if __name__=='__main__':main()
