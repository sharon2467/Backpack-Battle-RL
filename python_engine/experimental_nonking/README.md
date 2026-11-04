# Experimental nonKing Source combat

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
