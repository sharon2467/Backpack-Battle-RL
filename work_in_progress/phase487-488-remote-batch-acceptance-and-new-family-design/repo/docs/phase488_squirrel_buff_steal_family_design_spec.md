# Phase488 first production caller for the buff-steal family

## 1. Requirements

Select **one actually unported item: Squirrel164**, as a new experimental non-King Source extension. Its original cooldown effect calls `stealRandomBuff(1)` then `activate()`. Complete the inherited ForestFriend behavior and shared-RNG tail as well; an inert catalog entry or helper-only test is insufficient. Amethyst Whelp201 is a real alternative but deferred: it also introduces combat-start random debuffs and a weapon early-hit callback. No second item, new King combination profile, full catalog census, shop/economy simulation, GUI forest or numerical-seed probe.

Current CATALOG has76 registered entries, including experimentalKing262, and excludes164/201. Formal support remains75 non-King items. Future isolated implementation may register164 as the77th catalog entry and admit it through an explicitly experimental Source entry; this is not formal76 acceptance. Old public75 validation/initialize/batch and King6/7/8 gates must not silently expand. Existing packages, captured profiles, native receipts and outputs remain immutable.

This phase is DESIGN ONLY: four-section SPEC, candidate facts, Source/API pins and independent review handoff. No implementation/compile/import/model/native/EXPECTED/pool operations or old tests. Root's30% save/pause threshold remains active. Independent Source implementation and controls require the next Root-selected block.

## 2. Design

### Real caller census and candidate choice

The search was limited to calls to four named helpers in the original `Items/**/*.gd`, not a519-item coverage audit. Fraction remove/steal has a real Chainsaw caller; random removal/steal also has gems, cards, chess and several exclusives. Their existence corrects the narrow model-side fact “no current75 production caller”; it never meant “no original caller.” These larger inherited subsystems are not selected.

Squirrel164 has CSV name Squirrel/typePet/extraNature, price5, cooldown4, p1 `15:petspeed`, p2 `1:buffsteal`, `gain=Buff`, gateItem Bowl of Treats162 and shop=`no`. `Squirrel.tscn` exists and directly binds `Squirrel.gd`; that script extends `ForestFriend.gd`, which extends Item. CSV demo field is empty, mapped by ItemBook to Demo release state and `ItemDescriptor.isReleased()` true. Its scene is in the normal Exclusive path loaded when `Game.loadExclusiveContent()` is true (PLAYTEST/FULLVERSION/EDITOR), not an Unreleased resource. Shop=`no` sets no ordinary-shop class and is distinct from unreleased/unavailable; the gate links it to Bowl of Treats. Do not implement acquisition, infer native canAdd from the existence of a file, or claim a fresh scene instantiation was executed. This is a concrete released Source descriptor/resource candidate with conditional original content loading, not a new native observation.

The other verified candidate201 has ID201, name Amethyst Whelp, a normal Exclusive scene and Weapon ancestry. Its initial `inflictRandomDebuffs(getP1())`/`activate(null,false)` and hit-only `removeRandomBuffs(1)` would add two new dispatch stages and damage-source obligations. Keep those facts as a deferred option; no201 registration now.

### Complete Squirrel business chain

1. **Affected cache:** ForestFriend `canAffect` accepts Pet OR Food, not just Food, and does not use Food's same-descriptor exclusion. Ordinary item identity is deduplicated even if multiple occupied cells hit star cells; retain insertion/cache traversal order and rotations. Squirrel's three-cell L shape and seven stars are derived from its CollisionMap: tiles3/4 are occupied/primary affected. No extra business Timer or native particle countdown is added.
2. **Start stage:** ForestFriend overrides `combatStart`, calls the Item parent first, then counts affected items and calls `addSpeed(numAffected*getP1()/100.0)` only when count>0. There is no extra Activation in this start effect. In the model, insert this at the existing combatStart loop, after all preCombatStart cooldowns have been configured. Preserve the arithmetic order `count*15.0/100.0`; do not change it to `count*0.15`, which may change binary64 results. Actual speed/tooltip histories and cache consumption must be visible.
3. **Cooldown:** the real trigger first advances iteration/trigger time through the existing generic cooldown path, then invokes the unchanged `steal_random_buff(item,1)` and actual `activate(item)`. It repeats; it is not consumed. It is a Pet with no attack damage/stamina cost, not a Weapon. The4-second base cooldown still receives ordinary speed/Cold/Heat/Opponent-bias behavior.
4. **Selection/loss/gain:** original `pickRandomStacks` considers the seven positive categories101..107 with positive target stacks, selects through the shared Util RNG only while eligible stacks remain and preserves dictionary/category order. No target buff means no selector draw but the Squirrel full caller still activates. Delayed logging wraps each requested loss followed by own gain, then flushes. Crucially original `stealRandomBuff` gives the **picked/requested amount**, even if target loss is reduced to zero by protection/resistance. Both operations retain the caller's `triggerEvent`; gain is not parented to the returned loss event. The existing Python helper already expresses this exact loss-then-gain behavior and should remain byte-exact.
5. **Shared RNG tail:** Squirrel overrides `playDropSound`, drawing `Util.rng.randf_range(0.9,1.1)`. Item.activate calls playActivationSound→playDropSound after its Activation/listeners/metric/tooltip work. This shares the gameplay Util stream and cannot be dropped as irrelevant sound state. Include its numeric draw at the Squirrel activation tail without implementing sound/animations. The fourth same-time activation returns before this draw; an ended fight still reaches the tail if the limiter allowed the call. Preserve that distinction rather than adding an early-ended guard. Pickup/drop RNG during inventory manipulation is outside the fresh Source combat policy; do not claim native session reconstruction.

### Experimental entry without formal/genuine widening

Recommend one explicit entry `headless.initialize_squirrel(layout, seed)` returning the existing HeadlessBattle. Its fixed Source domain is existing default75 plus164, requires at least one164, class0 on both sides, noKing/rage/gems/modifiers, and the existing legal identity/space validation. No caller-provided arbitrary allowlist or proof BOOL. One initial integration case uses exactly one Squirrel. Multiple164 instances remain permitted within the existing per-side64-item limit: ForestFriend does not impose an original singleton or same-kind exclusion, and a finite cache component must cover that distinction.

Retain `ITEMS` as the old75 set. Extract the existing layout-validation body into a private closed-allowlist helper; old `validate_layout` supplies its old75+King set, while a dedicated `validate_squirrel_layout` supplies75+164 and enforces the new non-King/class0 restriction. Extract the initialization body after fixture validation into a private `_initialize_fixture(fixture,seed)`, retaining the exact topology/order/two-stream/RNG/constructor/prepare/activate sequence. Old initialize validates its seed/layout exactly as before; the new entry validates seed and its own fixed layout then uses the same body. Do not duplicate the whole engine, add a plugin framework or widen old genuine profile hashes. Existing synthetic fresh runtime/TimerRuntime is sufficient; no new captured DTO or King profile.

Source metadata must list formal75 separately from experimental164 and catalog registration77. Existing CLI/run_batch remain on the old explicit entry in this first block. A later usable extension CLI/batch can be added after behavior acceptance; do not broaden them silently merely to run the one integration case. New result metadata reports actual Source extension/seed policy and native evidence pending; shared events/history/final/RNG/Timer data are retained.

### Reusable evidence and honest missing observations

Reuse existing permanent-stack loss/gain, protected loss, delayed logging, fixed-category dictionary order, RNG/Timer and cache algorithms in their accepted finite scopes.025 documents Source controls for requested gain versus protected actual loss and exact logging/parent behavior, but its natural native cases are Mirror fraction callers and protected native events were NOT_HIT.178 is actual King/Mirror/Poison evidence;478 is fixed King+Basic evidence;483/487 validate fresh Source integration/batch only. None is a Squirrel production-caller native comparison. This phase reads their accepted documents/receipts, not Expected/model payloads.

No new native capture is required to implement and test Source164. Natural non-King Source integration can hit buff stealing against existing Blueberries/Herbs/other positive-buff producers without King. Protection can be exercised by a predeclared Source component assigning a coherent positive protection resource and invoking the real Squirrel trigger; that proves the shared rule without a public King+Squirrel profile or a native HIT claim. Later native admission needs one separately authorized presealed Squirrel layout, lawful metadata/initial bindings, full selected primitive Tape/clock and frozen comparison scope. Original Squirrel's explicit pitch site may need a single new primitive wrapper if not present in the future producer; do not assume current observer already captures this newly reached direct Util call, nor launch a new107-hook audit here. Native acquisition/canAdd, exact new cache and branch HIT remain unobserved.

## 3. Realize

Proposed next isolated Source block starts from exact482v2 fifteen files. Expect engine.py/headless.py changes only and thirteen conserved modules, including genuine.py/TimerRuntime/FrameDriver/randomness. Write a new function-level SPEC before implementation; compile-only and seal before independent imports.

Engine changes:

- CATALOG: add164's Source metadata, exact normalized shape/stars, Pet/Nature flags, cooldown4.0, pet_speed_percent15.0, buff_steal1, zero sockets/default_gemNone. Add `GAINED_STACK_FLAGS[164]=254` and164 to `CACHED_AFFECTED_IDS`. Do not add it to weapon sets.
- `new_caller_target_caches`: add Squirrel eligible predicate Pet OR Food before generic food/potion fallbacks, retaining source-order/dedup construction. `affected_items` fallback must use the same predicate for unprepared/fresh reads, not generic any-target fallback.
- `activate_from_checkpoint`: at the real combatStart stage add the original count>0 speed adjustment without Activation, preserving multiplication/division order and hist updates.
- `trigger`: add164 branch `steal_random_buff(item,1); activate(item); return` after generic cooldown accounting. Keep existing helper selection/loss/gain/logging bodies exact.
- `activate`: append only164's numeric pitch draw after ordinary Activation/history logic, reached also after ended but not after limiter return; no change to other items' algorithms. Record draw through the existing RNG/audit interface with a stable semantic label. No sound resource model.

Headless changes:

- Keep old ITEMS, old public defaults and all King gates closed; add a fixed164 extension constant and `validate_squirrel_layout`/`initialize_squirrel`. Share private layout and initialization bodies by exact extraction as above, not by bypassing validation.
- `HeadlessBattle._result_view` labels Source experimental164 only when the actual fixture contains164; formal support remains75. Initialization metadata makes fresh Source origin explicit. No schema/genuine/native readiness assertion is added.

No custom native driver, physical host, EXPECTED comparator, public package update, shop/card/companion generator or201 behavior is part of this implementation. First substantive rule discrepancy must stop with the concrete path; no silent correction of broad unrelated mechanics.

## 4. Acceptance Criteria / Tests

Independent plan must fix component inputs/expected semantic assertions and one natural Source layout/seed before importing candidate. Author only compile/static conservation. Required finite distinctions:

- Descriptor/scene/CSV ID, shape/stars/rotation, zero sockets, default types and Source-only admission. Old initialize rejects164, new entry rejectsKing/rage/unknown/modifier inputs; old75 and King6/7/8 gates remain unchanged. No old battle replay.
- ForestFriend cache includes unique Pet and Food, excludes bags/noneligible/self, preserves earlier/later placement order; same-type Pet is not excluded by a reused Food rule. Verify actual prepare and combatStart timing, count0 no speed update, positive count arithmetic/tooltip bits, no spurious start Activation.
- Real Squirrel trigger with no eligible target: no pick draw, but ordinary Activation and exactly one allowed pitch draw. With one/multiple buff categories: selector bounds and order, target actual loss, own requested gain, delayed event ordering, history/metrics and same supplied parent association. Never parent gain to the loss event as a convenience.
- Protected-loss Source component: target Mana/protect resource chosen beforehand; requested1/actual0 still gives1 to Squirrel owner and decrements protection, with protected event and histories. Unprotected case actually removes1 and gives1. Stack-cap/resistance variants remain limited directed controls if needed to distinguish the exact helper; do not rerun the permanent-stack test matrix.
- Activation tail: listeners/metric/tooltip precede pitch; first three same-time attempts versus suppressed fourth; ended-but-allowed call still consumes pitch. These are numeric shared-stream assertions, not sound/GUI tests.
- At most one presealed non-King Source integration case with ordinary buff producers, actual repeated steals and normal terminal output. Use up to120 **simulated** seconds with a separately predeclared wall limit. Report HIT/NOT_HIT and exact draws/history/Timer membership; no winner fitting, old-seed replay, automatic new native or claims of every75×164 interaction equivalence.

After independent Source/component/integration acceptance, Root decides a separate distribution/admission step. Full RL, native same-seed/session reconstruction, protection layout/native HIT and formal76 are not outcomes of this Source design.
