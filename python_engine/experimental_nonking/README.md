# Experimental nonKing Source combat

Portable Python3.10+ standard-library package. No Godot, original assets, shared pool,
network access or third-party libraries are required to run the Python model.
The fifteen Source files are byte-exact accepted phase558; packaging changes no rules.

## Supported entry and limits

Use `headless.initialize_experimental_nonking(layout, seed)` and
`headless.validate_experimental_nonking_layout(layout)` for the closed experimental
nonKing domain. It contains the existing75 default items plus these eight experiments:

| ID | Item | Source rule |
| --- | --- | --- |
| 64 | Ruby Whelp | pre-start reflection, startup Heat, effect attacks |
| 162 | Bowl of Treats | finite global Pet extra cooldown effect and spatial Food speed budget |
| 164 | Squirrel | Pet-or-Food star speed and buff stealing |
| 197 | Emerald Whelp | startup Lucky and attack Poison |
| 199 | Sapphire Whelp | startup Mana and paid Mana→Block/nonMana reward |
| 201 | Amethyst Whelp | startup random debuffs and own-hit buff removal |
| 231 | Wolpertinger | Pet star speed, least-buff selection, buff-delta stamina regeneration |
| 385 | Enchanted Weapons | finite positive own-attack-effect repetition and least1 buff |

This entry requires at least one of the eight experimental items, class0, Source default
modifiers, no King262, no socketed gems and no rage bag129. It accepts a uint64 seed
(strict integer, not bool). It does not expose an arbitrary allowlist. The unchanged
old `initialize`, CLI, `run_batch`, `initialize_squirrel` and King-specific gates keep
their previous scopes; the CLI/batch do not admit these new experimental layouts.
Do not call old CLI with the supplied example. Wolpertinger is a Pet, not a Weapon.

Catalog84 is registration: formal75 + eight nonKing experiments + separately restricted
King262. Without162, previous551 admission is unchanged (its registry was83), including
the385 rule below. Without either162 or385, the prior545 admission is retained.
This new exact558 Source reports catalog_registered84 even when both callers are absent. Formal support remains75. A finite Source case does not prove all combinations,
all classes, all modifiers, arbitrary King mixes, full-engine RL or Native seed parity.
The included legacy modules/CLI remain for exact Source preservation, not an expanded
captured-input, Oracle or Tape public entry. No Original files are runtime dependencies.

When385 is present, the **complete fixture** is additionally limited to IDs
`{1,11,14,22,32,231,233,234,385}`, class0 and at most one385 per side. Four
positive receivers are Spear14, Magic Staff32, Thorn Shortbow233 and Lucky
Shortbow234. Unknown receivers, including Whelps, are rejected in that fixture,
not silently treated as unaffected.385 uses its real1-cell body and12 stars;
the modifier repeats own early/late/dealt effects, not raw damage or Activation.
Multiple overlapping Skill contributions and arbitrary Skill/King mixes are outside
this finite domain. The same explicit API is used; no per-item initializer is added.

When162 is present, the **complete fixture** is instead limited to IDs
`{1,5,11,22,162,164,231}`, class0 and at most one162 per side. Its global same-side
Pet modifier covers only Squirrel164/Wolpertinger231 in this finite domain, while
its star cache affects different Food.162 uses its actual2-cell/eight-star shape.
The positive roll happens after the complete first cooldown effect, not at attack
effect count or by duplicating raw damage/Activation. Food speed has its real per-Bowl
ledger. Whelps, Gooberts, King and385 are excluded from this162 domain.
The162 and385 fixture domains are currently **mutually exclusive**. There is no
new mixed162+385 admission, arbitrary allowlist or per-item public initializer.

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

The second example is the original24-item presealed55201 input used by553:
use `examples/layout-Enchanted-Weapons.json` and seed55201 with the same API
command above. The third example, `examples/layout-Bowl-Treats.json`, is the
presealed23-item559 input; use seed55901 with that same API. No outcome is embedded
in any layout. These commands reproduce Source inputs, not original-engine seed/session results.

A minimal no-battle smoke command only imports and validates all three examples:

```sh
python -B - <<'PY'
import json
from pathlib import Path
from headless import validate_experimental_nonking_layout
for name, count in [('layout-Wolpertinger.json', 22), ('layout-Enchanted-Weapons.json', 24), ('layout-Bowl-Treats.json', 23)]:
    layout = json.loads((Path('examples') / name).read_text())
    fixture = validate_experimental_nonking_layout(layout)
    assert sum(len(side['items']) for side in fixture['sides']) == count
print('VALIDATED_THREE_INPUTS_NO_ENGINE_CONSTRUCTION')
PY
```

## Evidence and remaining scope

Independent546 accepted eight directed Source families and one fixed new mixed Source
battle. Wolpertinger selection/registration/zero-delta/current-event history and stamina
feedback were controlled; the natural case did not hit Squirrel loss. The example is
copied from the pre-execution22-item layout, with no result embedded or tuning afterward.
Independent553 accepted eight directed385 Source families and one fixed natural
case, without changing551. The natural run hit Staff double1 and Spear double2;
Thorn/Lucky double and positive Spear loss were NOT_HIT, with their stated behavior
covered by directed components. The552 first harness failure (HP1000 outside1..999)
is retained;553 repaired only that test fixture and did not retry a battle outcome.
These are finite Source results, not arbitrary receiver validation.
Independent559 accepted eight finite Bowl Source families and one presealed natural
case, without changing558. The natural case hit four extra Pet effects, both Bowl
ledgers100 and actual Squirrel loss/Wolpertinger negative stamina feedback. The
fourth/fifth Activation limiter, already-ended tail and synthetic90→115 ledger
distinction were unit-only evidence, not natural or Native hits. Older546 Squirrel-loss
NOT_HIT and553 Thorn/Lucky-double/positive-Spear-loss NOT_HIT disclosures retain their
per-case meaning; the new case does not retroactively claim those old cases hit them.
Wolpertinger, Enchanted Weapons and Bowl Native comparisons remain pending.

Separately, fixed original029 has a strict eight-section conditional-Tape comparison
for its29-item whelp/Squirrel-family layout. That validates that fixed captured
case with actual Native clocks/inputs; it does not include162/231/385 or establish production
seed/session equivalence. This package uses fresh Source objects and the existing
two-stream `headless-sha256-domains/1` policy, not captured Native history or a replay
bundle. Current conservative code coverage/native-pending labels are retained exactly.

The read-only verifier imports no battle modules. The manifest pins all21 listed payloads
(15 Source, this README, three examples, lineage, verifier); the manifest itself is pinned
externally to avoid a self-hash cycle. It checks bounded stable ordinary single-link
files and exact15 Source membership. It verifies listed bytes, not arbitrary added
files or Python execution safety. Evidence paths in `source-lineage.json` are provenance,
not files required at runtime. New full battles are not needed for package acceptance.
