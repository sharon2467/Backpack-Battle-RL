# Experimental nonKing Source combat

Portable Python3.10+ standard-library package. Running this Python model requires
no Godot, Original assets, shared pool, network or third-party libraries.
The fifteen Source files are byte-exact the independently accepted662 candidate;
packaging changes no rules. Source85 registration does not expand formal75.

## Supported API and limits

Use `headless.initialize_experimental_nonking(layout, seed)` and
`headless.validate_experimental_nonking_layout(layout)`. The closed experimental
nonKing entry contains the existing75 default items and nine experimental items:

| ID | Item | Source rule |
| --- | --- | --- |
| 64 | Ruby Whelp | pre-start reflection, startup Heat, effect attacks |
| 162 | Bowl of Treats | finite global Pet extra effect and spatial Food speed ledger |
| 164 | Squirrel | Pet-or-Food star speed and buff stealing |
| 197 | Emerald Whelp | startup Lucky and attack Poison |
| 199 | Sapphire Whelp | startup Mana and paid Mana to Block/nonMana reward |
| 201 | Amethyst Whelp | startup random debuffs and own-hit buff removal |
| 231 | Wolpertinger | Pet star speed, least buffs, buff-delta stamina regeneration |
| 385 | Enchanted Weapons | finite own attack-effect repetition and least1 buff |
| 422 | Wand | ordered least1, live threshold, most-buff consumption and parented Empower |

This API requires at least one experimental item, class0, default parameters and
Source modifiers, no King262, no rage bag129 and no socketed gems. Seed is a strict
uint64 integer, not bool. There is no caller-provided allowlist or per-item API.
Catalog85 comprises formal75, nine nonKing experiments and separately restricted
King262. Registry membership is not evidence for every combination or Native setup.

When422 is present anywhere, the **complete fixture** is restricted to
`{1,11,22,231,422}`, class0/default and at most one Wand per side. It has its real
two vertical collision cells and no stars/sockets. Its ordered subset is
Mana105/Lucky101/Regeneration102. One least buff completes before the three live
threshold checks. ANY count reaching10 causes most-buff consumption1 and Empower1
parented to the actual returned Use event (or NULL), then Activation always.
Most selection uses a real chooser draw even for a singleton or all-zero tie;
zero removal returns NULL after that draw. Own consumption and protected opponent
loss remain different operations. No attack-effect doubling or raw damage shortcut
implements this rule. This is Source behavior, not observed Native Wand eligibility.

Without422 all earlier domain restrictions and entry behavior are retained:

- With385 alone, complete-fixture IDs are `{1,11,14,22,32,231,233,234,385}`,
  class0 and at most one385 per side. The four positive receivers are Spear14,
  Magic Staff32, Thorn Shortbow233 and Lucky Shortbow234. Other receivers are
  rejected, not silently treated as unaffected. Skill shape is one cell/12 stars.
- With162 alone, complete-fixture IDs are `{1,5,11,22,162,164,231}`, class0
  and at most one162 per side. Its finite global Pet targets are Squirrel/Wolper;
  its spatial cache affects different Food. Bowl shape is two cells/eight stars.
- With both162 and385 anywhere, complete-fixture IDs are
  `{1,5,11,14,22,32,162,164,231,233,234,385}`, with at most one of each caller
  per side. Callers may be on the same or opposing side. This is a fixed union12,
  not all75 plus arbitrary modifiers. With neither caller, the previous domain
  is retained. Registration is85 throughout; historical registry counts differ.

Old `initialize`, CLI, `run_batch`, `initialize_squirrel` and King-specific gates
retain their scopes. Do not pass these experimental layouts to the old CLI/batch.
This package adds no experimental batch API, captured DTO/Tape public entry,
general King admission or full-engine/RL completion claim.

## Run without an Oracle

Obtain the trusted manifest SHA from the external release/owner before verifying:

```sh
python -B verify_manifest.py --manifest-sha256 "$EXPECTED_MANIFEST_SHA256"
```

From this package directory, this command reproduces the presealed Source Wand
input. It is a user command; package assembly does not execute it:

```sh
python -B - <<'PY'
import json
from pathlib import Path
from headless import initialize_experimental_nonking
layout = json.loads(Path('examples/layout-Wand.json').read_text())
battle = initialize_experimental_nonking(layout, 66301)
result = battle.run(max_seconds=120.0)
print(json.dumps(result, sort_keys=True))
PY
```

Initialization constructs one isolated instance, prepares it and activates combat,
including startup RNG/effects. `battle.initialization` returns a defensive copy.
`snapshot()` observes without advancing; `step()` advances the existing simulation;
`done` marks completion; `result()` requires completion. `run(max_seconds=...)`
finishes the same instance or raises `TimeoutError` for its **simulated duration**
budget. It is not a wall-clock limit; callers impose an outer wall-clock limit
separately. Internal errors are not normal timeout outcomes.

The four retained examples are byte-exact the previous package inputs:

| Example | Source seed |
| --- | --- |
| `layout-Wolpertinger.json` (22 items) | 54601 |
| `layout-Enchanted-Weapons.json` (24 items) | 55201 |
| `layout-Bowl-Treats.json` (23 items) | 55901 |
| `layout-Mixed-Modifiers.json` (29 items) | 56501 |

The new `layout-Wand.json` contains the original fifteen-item presealed layout
only; seed66301 and provenance are recorded outside that layout. No example embeds
a result, winner, derived initial state or Native output.

The minimal new distribution smoke imports and validates only this new layout;
it does not construct an Engine or run a battle:

```sh
python -B - <<'PY'
import json
from pathlib import Path
from headless import validate_experimental_nonking_layout
layout = json.loads(Path('examples/layout-Wand.json').read_text())
fixture = validate_experimental_nonking_layout(layout)
assert sum(len(side['items']) for side in fixture['sides']) == 15
print('VALIDATED_WAND15_NO_ENGINE_CONSTRUCTION')
PY
```

## Evidence and remaining scope

Independent666 accepted finite Source85 Wand: eight component families with21
subcases,23 direct calls, six expected rejects and22 controlled draws, plus one
presealed66301 Source battle. That natural run had298 events,297 draws and1800
steps; nine Wand least grants and nine Wand Activations were HIT. Conversion,
actual Use-event Empower parent, negative Wolper feedback and Activation limiter
were **NOT_HIT naturally**; their finite component behavior was proved separately.
NULL-helper composition was synthetic, not a claimed natural threshold case.
There was no Native422 observation, inventory canAdd test or strict comparison.

Earlier finite Source evidence is retained through lineage:546 Wolper families,
553 four finite Enchanted receivers,559 Bowl families and566 fixed mixed29.
Their natural NOT_HIT disclosures remain per-case:546 Squirrel loss;553 Thorn/
Lucky double and positive Spear loss;566 positive Spear Block loss. Directed
component evidence does not turn these into natural or Native hits.

Fixed Original030 single002 separately passed an independent strict eight-section
**conditional-Tape** comparison. Original and captured Python each had239 events,
279 selected draws,1116 clock passes and32 real Timers. This included events,
references/parents, histories, RNG, final state, callbacks, Timer API and terminal
cuts. Staff positive Mana and successful Pet extraactivation were NOT_HIT there.
Capture was complete while process exit was not clean; diagnostics are retained.
[Independent acceptance and HIT/NOT_HIT evidence](https://github.com/sharon2467/Backpack-Battle-RL/tree/3b8f24b53b0161f96844b2cc6f97e5546c0e5041/work_in_progress/phase657-actual002-strict8-accepted)
binds review SHA64fd9752aceb68182af9171d5546c0d6dd89896b48ed1b177c15282e1d9400a3.
It does not include Wand422 or validate all registry combinations/general King.
Fixed Original029 is also a separate accepted captured whelp/Squirrel case,
without162/231/385/422; it does not establish production seed/session equality.

Applicability658's13-of15 byte identity was **old public564 versus captured580**,
with engine/genuine different. It is historical and is not claimed for this new
662 package, whose headless and engine also changed to admit/implement Wand.
The old mapping and fixed030 evidence are preserved with that scope in lineage.
This public API uses fresh Source objects and the existing two-stream
`headless-sha256-domains/1` seed policy. Source seed66301 is not the Native
57101/57102 pair; it does not ingest captured history, Tape or actual Native clock,
nor promise the captured239/279/1116 result. Native seeded equivalence remains
unproved; it is separate from accepted conditional-Tape validation.

The unchanged read-only verifier imports no battle modules. Its manifest pins23
payloads:15 Source, five examples, README, lineage and verifier. The manifest itself
is pinned externally to avoid a self-hash cycle. It checks listed stable ordinary
single-link bounded bytes and exact15 Source membership, not arbitrary added
files or execution safety. Lineage paths are provenance, not runtime dependencies.
Full battles are not required for package acceptance. Formal75 remains unchanged.
