"""Assemble exact accepted Source and docs; no candidate/verifier execution."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/phase547-portable-nonking-package'
PACKAGE = OUT / 'package'
SPEC = ROOT / 'docs/phase547_portable_nonking_distribution_spec.md'
SOURCE = ROOT / 'data/phase545-source-wolpertinger'
JOB = ROOT / 'data/phase546-exact-business-source/natural-job.json'
OLD_VERIFIER = ROOT / 'data/phase491-squirrel-distribution-v2/package/verify_manifest.py'
PINNED_INPUTS = {
    'data/phase545-source-wolpertinger/candidate-source-freeze.json': '50e8e6847e13f4f69e9959b3e7b5412b6ed8d1a5ef1677534aab00b6ccce8508',
    'data/phase545-source-wolpertinger/owned-files.json': '2aa03706706189ade70dd43ce5f8975d428664ac8c3fc5e999d3fd82ef4b4cad',
    'data/phase546-exact-business-source/natural-job.json': '34769bba938cc8753cbfadddeb80b0c867ca6cc0242f70085120eb9c6f97bbad',
    'data/phase546-independent-final-acceptance/review.json': '94c08300cdd901d0a38472e0a93125a9f5e6c13ea1dcea884dd1f44f8866d45c',
}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def descriptor(path):
    raw = path.read_bytes()
    return dict(path=str(path.relative_to(ROOT)), size=len(raw), sha256=digest(raw))


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + '\n').encode()


def write(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(raw)


def save(path, value):
    write(path, encode(value))


README = '''# Experimental nonKing Source combat

Portable Python3.10+ standard-library package. No Godot, original assets, shared pool,
network access or third-party libraries are required to run the Python model.
The fifteen Source files are byte-exact accepted phase545; packaging changes no rules.

## Supported entry and limits

Use `headless.initialize_experimental_nonking(layout, seed)` and
`headless.validate_experimental_nonking_layout(layout)` for the closed experimental
nonKing domain. It contains the existing75 default items plus these six experiments:

| ID | Item | Source rule |
| --- | --- | --- |
| 64 | Ruby Whelp | pre-start reflection, startup Heat, effect attacks |
| 164 | Squirrel | Pet-or-Food star speed and buff stealing |
| 197 | Emerald Whelp | startup Lucky and attack Poison |
| 199 | Sapphire Whelp | startup Mana and paid Mana→Block/nonMana reward |
| 201 | Amethyst Whelp | startup random debuffs and own-hit buff removal |
| 231 | Wolpertinger | Pet star speed, least-buff selection, buff-delta stamina regeneration |

This entry requires at least one of the six experimental items, class0, Source default
modifiers, no King262, no socketed gems and no rage bag129. It accepts a uint64 seed
(strict integer, not bool). It does not expose an arbitrary allowlist. The unchanged
old `initialize`, CLI, `run_batch`, `initialize_squirrel` and King-specific gates keep
their previous scopes; the CLI/batch do not admit these new experimental layouts.
Do not call old CLI with the supplied example. Wolpertinger is a Pet, not a Weapon.

Catalog82 is registration: formal75 + six nonKing experiments + separately restricted
King262. Formal support remains75. A finite Source case does not prove all combinations,
all classes, all modifiers, arbitrary King mixes, full-engine RL or Native seed parity.
The included legacy modules/CLI remain for exact Source preservation, not an expanded
captured-input, Oracle or Tape public entry. No Original files are runtime dependencies.

## Run the API

From this directory, optionally verify the listed payloads first (obtain the trusted
manifest SHA from the external release/owner, not from an untrusted local edit):

```sh
python -B verify_manifest.py --manifest-sha256 "$EXPECTED_MANIFEST_SHA256"
```

This reproduces the presealed546 Source input. It is a user command, not a new author
battle or an outcome assertion:

```sh
python -B - <<'PY'
import json
from pathlib import Path
from headless import initialize_experimental_nonking
layout = json.loads(Path('examples/layout-Wolpertinger.json').read_text())
battle = initialize_experimental_nonking(layout, 54601)
result = battle.run(max_seconds=120.0)
print(json.dumps(result, sort_keys=True))
PY
```

`initialize_experimental_nonking` constructs one isolated instance, prepares it and
activates combat, including startup RNG/effects. `battle.initialization` is a defensive
copy of its descriptor. `battle.snapshot()` observes without advancing;
`battle.step()` advances the existing simulation; `battle.done` marks completion;
`battle.result()` requires completion. `battle.run(max_seconds=...)` finishes that same
instance or raises `TimeoutError` when its **simulated duration** budget is exhausted.
`max_seconds` is not a wall-clock limit; a caller must impose any outer wall-clock
limit separately. Internal errors must not be treated as normal timeout outcomes.
The explicit nonKing API is single-battle; this package adds no experimental batch API.

A minimal no-battle smoke command only imports and validates the example:

```sh
python -B - <<'PY'
import json
from pathlib import Path
from headless import validate_experimental_nonking_layout
layout = json.loads(Path('examples/layout-Wolpertinger.json').read_text())
fixture = validate_experimental_nonking_layout(layout)
assert sum(len(side['items']) for side in fixture['sides']) == 22
print('VALIDATED_22_ITEMS_NO_ENGINE_CONSTRUCTION')
PY
```

## Evidence and remaining scope

Independent546 accepted eight directed Source families and one fixed new mixed Source
battle. Wolpertinger selection/registration/zero-delta/current-event history and stamina
feedback were controlled; the natural case did not hit Squirrel loss. The example is
copied from the pre-execution22-item layout, with no result embedded or tuning afterward.
Wolpertinger Native comparison is pending.

Separately, fixed original029 has a strict eight-section conditional-Tape comparison
for its29-item whelp/Squirrel-family layout. That validates that fixed captured
case with actual Native clocks/inputs; it does not include231 or establish production
seed/session equivalence. This package uses fresh Source objects and the existing
two-stream `headless-sha256-domains/1` policy, not captured Native history or a replay
bundle. Current conservative code coverage/native-pending labels are retained exactly.

The read-only verifier imports no battle modules. The manifest pins all19 listed payloads
(15 Source, this README, one example, lineage, verifier); the manifest itself is pinned
externally to avoid a self-hash cycle. It checks bounded stable ordinary single-link
files and exact15 Source membership. It verifies listed bytes, not arbitrary added
files or Python execution safety. Evidence paths in `source-lineage.json` are provenance,
not files required at runtime. New full battles are not needed for package acceptance.
'''


def main():
    OUT.mkdir(exist_ok=False)
    try:
        for relative, expected_sha in PINNED_INPUTS.items():
            if digest((ROOT / relative).read_bytes()) != expected_sha:
                raise ValueError('accepted/presealed input identity drift: ' + relative)
        freeze = json.loads((SOURCE / 'candidate-source-freeze.json').read_bytes())
        entries = freeze['files']
        if len(entries) != 15 or len({item['relative'] for item in entries}) != 15:
            raise ValueError('exact15 source list required')
        copies = []
        for item in entries:
            path = ROOT / item['path']
            if descriptor(path) != {key: item[key] for key in ('path', 'size', 'sha256')}:
                raise ValueError('545 Source mismatch')
            raw = path.read_bytes()
            compile(raw, item['relative'], 'exec')
            target = PACKAGE / item['relative']
            write(target, raw)
            if target.read_bytes() != raw:
                raise ValueError('copy differs')
            copies.append(dict(relative=item['relative'], source=descriptor(path), destination=descriptor(target)))
        job = json.loads(JOB.read_bytes())
        if set(job) != {'layout','seed','max_seconds'} or job['seed'] != 54601:
            raise ValueError('presealed546 job identity')
        layout = job['layout']
        if sum(len(side['items']) for side in layout['sides']) != 22:
            raise ValueError('exact presealed22 items required')
        canonical = lambda value: json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
        write(PACKAGE / 'examples/layout-Wolpertinger.json', encode(layout))
        if canonical(json.loads((PACKAGE / 'examples/layout-Wolpertinger.json').read_bytes())) != canonical(layout):
            raise ValueError('layout extraction changed JSON value')
        verifier = OLD_VERIFIER.read_bytes()
        before = b"MANIFEST_SCHEMA = 'experimental-source-king-package-manifest/1'"
        if verifier.count(before) != 1:
            raise ValueError('unique verifier schema anchor required')
        verifier = verifier.replace(before, b"MANIFEST_SCHEMA = 'experimental-nonking-package-manifest/1'", 1)
        compile(verifier, 'verify_manifest.py', 'exec')
        write(PACKAGE / 'verify_manifest.py', verifier)
        write(PACKAGE / 'README.md', README.encode())
        save(PACKAGE / 'source-lineage.json', dict(schema='experimental-nonking-source-lineage/1', public_target='python_engine/experimental_nonking',
            code='exact15 accepted545; packaging code edits0', source_freeze=descriptor(SOURCE / 'candidate-source-freeze.json'), source_owner=descriptor(SOURCE / 'owned-files.json'),
            independent_Source_acceptance=descriptor(ROOT / 'data/phase546-independent-final-acceptance/review.json'), independent_Source_acceptance_owner=descriptor(ROOT / 'data/phase546-independent-final-acceptance/owned-files.json'),
            presealed_example_job=descriptor(JOB), presealed_example_owner=descriptor(ROOT / 'data/phase546-exact-business-source/owned-files.json'), example_layout_canonical_sha256=digest(canonical(layout)),
            example_transform='extract layout only; retain JSON types/order/geometry/identity; no outcome fields', source_seed=54601,
            formal_support=75,catalog_registered=82, experimental_nonKing_items=[64,164,197,199,201,231], Wolpertinger_Native='PENDING', general_King='NOT_ADMITTED', Native_seed_session_parity='PENDING',
            fixed029_evidence='Separate strict8 conditionalTape case; no231; not fresh Source seed equivalence', runtime_evidence_dependencies='NONE; paths are provenance only', verifier_origin=descriptor(OLD_VERIFIER), verifier_delta='MANIFEST_SCHEMA constant only'))
        source_paths = {item['relative'] for item in entries}
        manifest_rows = []
        for path in sorted(PACKAGE.rglob('*')):
            if not path.is_file():
                continue
            relative = str(path.relative_to(PACKAGE))
            kind = 'source' if relative in source_paths else 'example' if relative.startswith('examples/') else 'documentation' if relative == 'README.md' else 'lineage' if relative == 'source-lineage.json' else 'verifier'
            raw = path.read_bytes()
            manifest_rows.append(dict(path=relative,kind=kind,size=len(raw),sha256=digest(raw)))
        if len(manifest_rows) != 19:
            raise ValueError('exact19 package payloads required')
        save(PACKAGE / 'manifest.json', dict(schema='experimental-nonking-package-manifest/1', status='EXACT545_ACCEPTED546_PENDING_INDEPENDENT548_PACKAGE_ACCEPTANCE',public_target='python_engine/experimental_nonking',source_file_count=15,files=manifest_rows))
        save(OUT / 'copy-conservation.json', dict(schema='phase547-copy-conservation/1',source_files=15,exact_copies=copies,source_edits=0,package_payloads_excluding_manifest=19,physical_package_files=20,
            example_layout_canonical_sha256=digest(canonical(layout)),example_source=descriptor(JOB),verifier_origin=descriptor(OLD_VERIFIER),verifier_change='one schema constant only', compile_only_files=16,
            candidate_imports=0,helper_calls=0,verifier_calls=0,tests=0,models=0,battles=0,Native=0,Expected=0,UI=0,pool=0))
        save(OUT / 'independent-smoke-contract.json', dict(schema='phase547-independent-smoke/1', cwd='package', verifier_command='python -B verify_manifest.py --manifest-sha256 <externally pinned manifest SHA>',
            import_validate_API='headless.validate_experimental_nonking_layout(json.loads(Path("examples/layout-Wolpertinger.json").read_text()))',expected_input_item_count=22, initialize_required=False, battles_allowed=0,
            author_executed=False, Source_runtime_acceptance='reused accepted546; no new runtime claim'))
        files = [SPEC,Path(__file__).resolve()] + sorted(path for path in OUT.rglob('*') if path.is_file())
        save(OUT / 'owned-files.json',dict(schema='phase547-owned-files/1',status='SOURCE_PACKAGE_FROZEN_PENDING_INDEPENDENT548',files=[descriptor(path) for path in files]))
        print(json.dumps(dict(status='SOURCE_PACKAGE_FROZEN',manifest=descriptor(PACKAGE / 'manifest.json'),owner=descriptor(OUT / 'owned-files.json')),sort_keys=True))
    except Exception as error:
        save(OUT / 'first-error.json',dict(schema='phase547-package-first-error/1',type=type(error).__name__,error=str(error),candidate_imports=0,models=0,verifier_calls=0,Native=0,Expected=0,pool=0))
        save(OUT / 'partial-owner.json',dict(schema='phase547-partial-owner/1',files=[descriptor(path) for path in [SPEC,Path(__file__).resolve()]+sorted(path for path in OUT.rglob('*') if path.is_file())]))
        raise


if __name__ == '__main__':
    main()
