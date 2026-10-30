# Phase496 v2 final bounded Whelp start/hit family design

## 1. Requirements

Select at most three original unported siblings: **Ruby Whelp64, Emerald Whelp197, Sapphire Whelp199**. Each extends Weapon and adds a small startup/own-early-hit effect; they reuse the same attack and buff mechanisms as201 rather than creating a new subsystem or another King combination profile. The genuine business increment is staged reflection provisioning and Sapphire's paid event→Block+nonMana random-buff chain.

This is DESIGN ONLY: no Source implementation, compile/import, controls/test/model/battle/native/EXPECTED/pool, new capture or old-test rerun.493 remains frozen with the known494 metadata-copy failure.495 is the immutable one-receiver repair, compile-only; Root has released only the remaining05–17 independent checks, whose completion is pending at this design freeze. Full current functional acceptance is a prerequisite for any successor implementation, not assumed here. Any real current-block defect takes priority over this proposal. Root monitors the30% save/pause threshold.

If all three are later implemented, register81 catalog entries (current49378 plus3), while formal support stays75. Expand the existing explicitly experimental non-King fixed set from164/201 to `{64,164,197,199,201}`. Same class0/default/atLeastOneExperimental/noKing/rage/no-gems/modifier restrictions; no caller allowlist, new per-item initialize or new native/genuine profile. Old formal/Squirrel/CLI/batch/King gates stay closed to the newly added IDs. No publication change occurs here.

## 2. Design

### Candidate facts and why three still fit one small block

| ID | Original file | Direct new business | Metadata |
|---|---|---|---|
|64 Ruby Whelp|Items/RubyWhelp.gd|onPreCombatStart gives3 shared debuff-reflect stacks; onCombatStart gives Heat5 then activates|Pet/Fire/Effect plus Ranged Weapon; gainHeat128|
|197 Emerald Whelp|Items/Exclusive/EmeraldWhelp.gd|onCombatStart Lucky3 then activates; hit-only own early hook inflicts Poison3, null parent|Pet/Effect plus Ranged Weapon; gained flagsLucky+Poison258|
|199 Sapphire Whelp|Items/Exclusive/SapphireWhelp.gd|ready stores ordered Game.getBuffs without Mana; start Mana6 then activates; hit early tries Mana1, success givesBlock10 then randomnonManaBuff1, both parented to paid event|Pet/Magic/Effect plus Ranged Weapon; gainBuff254,useMana|

All have CD2.1/stamina0/damage5..10/accuracy90. Their scenes inherit Item's four-cell square unchanged, no stars, one default-empty socket and direct matching script. No custom own target cache or business Timer. CSV demo cells are empty, mapped by ItemBook to released Demo state; normal Exclusive scenes197/199 additionally require exclusive content loading.64's ordinary scene path exists. None is in Unreleased; shop=no and their respective Egg gates are acquisition facts, not proof of unavailability or executed native canAdd. No Egg/hatching/shop/economy port is required.

All three are small actual callers.64 mainly reuses already implemented RubyEgg62 reflection/Heat primitives (amount/timing differ).197 reuses the accepted early Poison hook mechanism.199 adds a constrained six-category use of an existing random-buff helper and event association, not a new RNG/picker. If Root reduces the block,197+199 is the useful two-item subset;64 is an inexpensive direct guard for the preCombatStart phase and can be deferred without changing the API architecture. There is no need to substitute a different family for complexity.

### Shared staged rules

**Startup ordering:** keep all preCombatStart calls before any combatStart. Ruby's reflectStacks3 is provisioned after its generic cooldown setup in the pre loop, so it exists before201's combat-start debuffs regardless of which item gets the earlier combatStart slot. Its Heat5 belongs to the later start stage, not prepare or pre stage; unlike RubyEgg62, Whelp heat is5 and it has no Egg hatch lifecycle. Emerald Lucky3 and Sapphire Mana6 each precede their own real Activation, with default null parent. All activate(null,false) calls still emit/log gameplay and metrics/listeners; the false argument excludes presentation only.

**Early effects:** Emerald uses hasHit, including an attack later reduced to0, and null-parent Poison3 before damage/Attack event. Sapphire also requires hasHit; it calls real try_use_mana1. Branch on the actual returned event, not merely a pre-read Mana condition. On success give Block10 then one random buff from exact ordered `(Lucky101,Regeneration102,Vampirism103,Spikes104,Empower106,Heat107)`. It is Game.getBuffs101..107 with Mana105 erased, not a seven-element pick that rerolls Mana, not positive-existing-only selection, and not a sorted runtime dictionary. One inclusive integer pick0..5 maps directly to that tuple. Block and the random buff both use the same Mana-use event parent; random buff is not parented to Block. Mana use is used=True and bypasses positive-buff protection; failed payment has no Block, selector or buff event. A Block cap/zero actual gain does not cancel the later random-buff operation if payment returned an event.

Existing give_random_buffs already accepts an explicit category subset, and try_use_mana/give_stack share the required event/loss/gain rules. Represent Sapphire's ready-only array as fixed descriptor/default Source tuple; no new mutable item-state field or user override. Item.giveBlock's gave_block signal has only the directly searched MoonShield/AmuletOfSteel/SmellyBarrier/SunShield receivers, all outside this selected registered Source family. Do not add those items or claim full signal trace equality. A bounded guard that none is admitted permits reuse of the current Block gain path. If a future admitted receiver needs that signal, it is a real additional implementation obligation.

These remain Ranged+Effect **attacks** with flags63, not pure Effect damage. Reuse201's default-zero typed factors/ranged+effect spikes limits/ranged Vampirism limit restrictions. Add all three to the finite empowerable-weapon set, retain real positive-base-damage/cooldown/Pet eligibility for existing neighboring items and preserve the common accuracy/effect count/damage/crit/activation order. Default raw0 double-effect repeats the own early callback, so Emerald inflicts twice and Sapphire can pay twice independently; the common attack/activation is still once. No new pitch override exists in these three scripts; do not copy Squirrel's explicit tail to them.

### Interaction and evidence boundary

A single future presealed mixed Source case can include these three with existing201/164 and ordinary supported buff resources. Ruby reflection is active before startup debuff application; Emerald supplies/changes Lucky and repeated Poison; Sapphire's finite initial Mana supports paid hits and a natural exhausted-payment state if no extra Mana source is chosen.201 removes opposing positive buffs,164 later selects from the resulting pool, and all Whelps qualify as Pet targets for ForestFriend speed. Actual HIT/NOT_HIT depends on the fixed layout/order/seed; do not promise every branch or tune outcomes. Component controls cover exact caps, miss, payment failure, category endpoints and double-own effects.

Reuse source-bound reflection counters from RubyEgg62/old family, existing positive/debuff permanent pipeline, typed parent/queue/history machinery, shortbow early-hook ordering and201's dual-type/default damage bounds. The old025/178/478 fixed native cases and490 Source Squirrel acceptance retain their own scopes; none is new native64/197/199 evidence. The selected Source/capture indexes have not established a current pure native comparison for these three callers. No broad historical absence claim or full519 denominator survey is made.

No new original observation is necessary for Source implementation/controls. A future native claim would require one separately authorized mixed fixture, actual per-case initial identity/cache/clock/Tape bindings, new descriptor/hook applicability and output-first strict comparison; old Expected cannot provide those inputs. Do not auto-launch capture, restore/host changes, full107 hooks, UI forest or same-seed/numeric audit. If493/494 fails, this design does not justify building on an unaccepted behavior or concealing that failure.

## 3. Realize

Future implementation only after Root releases it and the495 remaining functional acceptance completes: clone the then-latest independently accepted15 Source into a new immutable directory. The design pins current495 as a compile-only prospective base, not as already fully accepted. Expected engine.py/headless.py only,13 other modules exact; write that implementation SPEC before edits.

Engine minimal changes:

1. Add exact64/197/199 catalog metadata, four-cell/no-star/oneemptySocket/ranged+effect+Pet types, common stats and effect amounts. Add EMPOWERABLE_WEAPON_IDS and GAINED_STACK_FLAGS64=128/197=258/199=254. No own CACHED_AFFECTED_IDS, Goobert, particleTimer or state schema change.
2. `activate_from_checkpoint`: pre loop adds64 reflection3 through the existing change_debuff_reflection; start loop64 Heat5/197 Lucky3/199 Mana6, then actual activate. Keep all old stages/order and existing item amounts untouched.
3. `pre_item_damage`: in existing hit block197→Poison3(default parent);199→try_use_mana1 then if real event giveBlock10 and give_random_buffs1 with exact six-category tuple, both same event id. Common early signal/effect count/attack tail unchanged.
4. Preserve try_use_mana/pickers/give_random_buffs/loss/gain/reflection/logging/History, attack/weapon_attack/damage bounds, Timer/FrameDriver/PRNG, Squirrel tail and201 branches byte-exact. No generic new subsystem or balancing rule.

Headless minimal changes:

5. Expand only the fixed experimental set to `{64,164,197,199,201}` and ensure atLeastOne check/result admitted-kind description derives from that fixed host set rather than stale hardcoded `[164,201]`. Keep validate/initialize_experimental_nonking signatures and existing private factory. Correct generic rejection text to refer to the fixed experiment set; do not add one API per item.
6. Coverage/descriptor expose actual experimental kinds present, fixed extension domain, actual catalog81/formal75, Source policy and pending native. Keep oldITEMS75/Squirrel/CLI/batch/King/genuine admissions exact. These are evidence labels, not caller-provided readiness or business state.

No implementation/runtime artifacts are created by this design. Pins bind the directly read Source parents, candidate scenes/CSV rows and current493 function seams, plus a clear conditional baseline/494 status. No full original dependency/recovery audit is repeated.

## 4. Acceptance Criteria / Tests

Independent successor plan should preseal finite inputs/expected semantic assertions before candidate import. Use the smallest combined controls:

- Exact three descriptors/release paths/types/shape/empty sockets and empowerable membership; fixed shared Source entry accepts the new kinds and mixtures, rejectsKing/rage/foreign/modifier input; old routes remain closed. Registration81 never means formal support81.
- Real stage boundary: Ruby counter3 is already set before **any** combatStart effect, Heat5 is not given early; Emerald Lucky3 and Sapphire Mana6 precede their own startup Activation. Check real prepare/pre/start timing rather than assuming initialize returns before start draws.
- Emerald miss→no Poison; zero-damage hit→Poison3; repeated own effect on raw0→twoPoison operations with null parents, but oneAttack/activation. Shared reflection/queue/cap branches use current APIs, not direct value assignment during the measured action.
- Sapphire Mana0/insufficient versus enough; success requires returned event, cost1 precedes Block10 then one picker0..5; endpoints yield Lucky/Heat and neverMana. All six category mappings can be checked on the helper/component without six battles. Both reward parents equal the Mana event; usedMana bypasses protection; Block cap does not skip the selector; second own hook observes the remaining Mana and may fail while first succeeds.
- Selected Source guard for no admitted gave_block receivers; no pretend full UI/signal sampling. Default damage dual-type flags/limit boundary is conserved from201, not rerunning the old attack/Timer/numeric suite.
- At most one independently presealed fresh Source mixed layout/seed, up to120 **simulated** seconds and separate wall cap, integrating the startup/reflection/hit/payment effects with existing removal/steal. Record all events/references/histories/RNG/final/Timers and actual branch HITs; preserve first budget/business failure without tuning or automatically recapturing. It is Source evidence, not native/generalKing/formal upgrade.

Author remains static/compile-only in any later Source implementation; independent reviewer owns functional acceptance. This496 design itself performs no compile, candidate import, control or battle.


This v2 completes the bounded static design only. The original496 SPEC and paused checkpoint/owner remain exact historical bytes. Three candidate rows, scene/ancestry facts and minimal Source method pins are in `data/phase496-whelp-family-design-final-v2`. Current frozen Source catalog remains78 and formal support75; hypothetical81 registration is a future implementation proposal, not an activity or acceptance of this phase. No runtime result or success status is prefilled.
