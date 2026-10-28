# Phase438 implementation-side Source closure: Character8 + Buff44

## Requirements and scope

Implement the bounded Source analysis requested by `phase438_shared_combat_initial_rules_spec.md`, using the original baseline, fixed case-A Source fixtures, accepted437 required rows and existing lawful saved INPUT. This report covers 8 Character fields and 44 Buff Timer private-left requirements. It does not accept its own proof, run a model/test/Oracle, mutate437/408/426, or reintroduce presentation116. Any adapter is deferred until the root confirms the concrete closed rules and independent native review finishes.

Current accepted counts remain1363=1289DIRECT+2SOURCE_DERIVED+72MISSING. The conclusions below are Source candidates for independent review, not promoted rows.

## Design: two independent families

Character8 can use a *specific historical no-start ledger* already saved in lawful `king-input-facts.json`. Buff44 can use the separately reviewed native processing invariant applied to exact saved node identities; it need not recover every historical start/stop. These are different arguments. Neither uses public `time_left=0` alone.

The original baseline is `/workspace/godotsteam-startup-20261013/baseline/Backpack Battles`. Its original files define gameplay. The pinned359 instrumented Character/Util and391 observer explain what the saved ledger measures; they do not redefine gameplay. SHA256s, exact INPUT pointers, all52 target keys, and the finite project scan are saved in `data/phase438-impl-character-buff-source/closure.json`.

## Character8: finite writer closure and specific saved-history route

| Writer | Source semantics |
| --- | --- |
| `Core/Character.gd:69–70` | Declaration initializes `invulnerable=false`, `invulnerabilityItem=null`. |
| `cleanse`,349–368 | Unconditionally writes false/null. Calling `prepare` is not calling `cleanse`. |
| `makeInvulnerable`,1037–1052 | Writes item, then either directly starts `invulnerabilityTimer` and sets true, or calls `Util.changeTimer` when already true. |
| `invulnerabilityEnded`,1056–1061 | Writes false; retains the previous item and uses it as the end-event source. |
| `makeVulnerable`,1053–1054 | `pass`; no additional writer. |

Whole-baseline `.gd` identifier search found no other Character property assignment. Character/Player/Opponent scenes do not set either field or animate it. The only direct calls to `makeInvulnerable` are HolySpear, Crown, DarkLantern, WhiteQueen, ShinyMantle, FrogPrince and KingGoobert gameplay methods. The fixed A inventory is Leather Bag(11), Wooden Sword(1), Wooden Buckler(4), Health Potion(19), Blueberries(22), and P-only King Goobert(262), without gems; this narrows before-activation dispatch but is not itself a no-history proof.

`Character.prepare:294–328` never assigns these two fields. `Game.prepareItems:3059–3064` calls both Character.prepare methods and each item.prepare. The first snapshot is before that body. The second snapshot is before `Game.activateItems` emits `combat_start`, starts Character timers or invokes any item pre/combat/post start. Time passes between the snapshots, so source control-flow adjacency cannot replace the saved history.

### Saved input chain that closes the missing historical premise

The lawful run is `original027-king-single-A-20261026-attempt06/output/capture`. `observer7-input.jsonl` line1/sequence138 and line4/sequence1231 bind P to47611, O to84805 at `prepareItems:enter` and `activateItems:enter`. The corresponding invulnerability timers are47767 and84961.

`king-input-facts.json` records, for both `timers/invu:P` and `timers/invu:O`, `lineage.kind="Character.scene.ready"`, matching owner/timer IDs, and exact integer `starts=0`, `stops=0`. This file is built by391 observer `begin_king_clock:833–843` → `selected_king_facts:782–814` at the entry to `activateItems`, before its original body. It covers the earlier prepare snapshot too because the same timers/owners are present at both cuts and counts are monotonic.

The359 instrumented `Character._ready:140–142` registers the timer at its first statement. Observer `timer_birth:743–752` rejects duplicate births; it initializes counts once. `timer_before:442–444` calls `track_king_timer_api` **before** the selected-fixture gate. Thus starts before slot binding are counted. `track_king_timer_api:754–757` only increments the corresponding counter. No reset path exists.

Every `makeInvulnerable` call that can change a cut-visible field necessarily reaches a counted start:359 Character1074–1093 wraps the direct start with `timer_before`; the alternative calls original `Util.changeTimer:1591–1593`, whose entire behavior is `get_time_left` then start, wrapped by359 Util1606–1613. More precisely, after the pre-ready closure, consider the **first** possible call: invulnerable is still false because every other writer assigns false, so this call must take the direct branch and reach `timer_before` before the native start or assignment of true. That already contradicts starts=0; the proof need not assume a potentially invalid typed argument successfully enters the alternative Util function. There is no yield, deferred call or gameplay callback between `invulnerabilityItem=item` and that counted start. At the two cuts, execution is in Game's top-level method entry, not inside an incomplete `makeInvulnerable` invocation. The counter increments *before* the native start, so even a native start failure cannot silently hide a completed item writer. Observer.entry before the item assignment serializes state/arguments and does not call a gameplay writer; it cannot leave a partially changed item before this sequence.

### Constructor to first parent-ready: explicit window closure

The ledger starts at Character's parent `_ready`, so zero counts alone do **not** cover construction/child-ready. The additional finite Source argument is required. The seven direct writer callers are Crown/HolySpear.checkTrigger, DarkLantern.onDamaged, WhiteQueen.doEliminatedEffect, ShinyMantle/KingGoobert.doCooldownEffect, and FrogPrince.onUseThresholdReached. None is `_init`, `_ready`, or an onready expression. Crown/HolySpear/DarkLantern/FrogPrince register the required gameplay event callbacks only in onPrepare. King/ShinyMantle require cooldown/activation dispatch; WhiteQueen requires a chess capture/elimination. The first Character parent-ready precedes inventory creation: original Character146–168 initializes INVENTORY and then Buffs;359's timer-birth statement occurs before all of that. The Character/Player/Opponent scene dependency closure contains none of the seven caller item scripts. Their serialized method tracks contain no call to makeInvulnerable or assignment of either field. No physical/idle timer pass occurs in the middle of synchronous add_child's ready propagation, and the known case performs its explicit inventory placement/prepare after that propagation returns. The only child-ready callbacks are therefore outside these writer receivers; they cannot dispatch a prepared inventory callback that does not yet exist. For O, the already-existing P inventory is fixed A and is not activated while synchronous O scene-ready runs.

This argument is about the seven actual script receiver methods and the fixed scene/lifecycle, not about the name `ready` implying pristine state. It also requires the pinned project/collector execution domain; arbitrary extension callbacks or scripts injected into a scene would invalidate it. The scene dependency/script list and all direct method names are included in the saved Source evidence for independent challenge.

With that pre-ready closure, constructor false/null plus the actual zero-start ledger excludes every completed `makeInvulnerable` before either cut. All remaining writers preserve false/null. Candidate result: all8 Character fields are Source-derivable as typed false/null. This is not inferred from stopped/public zero, from item absence alone, or from the label `startFreshRun`.

### Character negative controls and limits

Reject missing/noninteger/bool starts, any positive starts, mismatched role/owner/timer, duplicate birth/identity, missing matching snapshots, wrong ledger kind or unpinned instrumentation. A zero counter without a timer-birth binding does not suffice. After a real invulnerability timeout, `invulnerable=false` can coexist with nonnull `invulnerabilityItem`; this directly disproves deriving null from vulnerability or stopped state alone.

`instanceCharacter` can reuse P (`Game.gd:2257–2266`), while the opponent is newly instantiated during combat transition (`Game.gd:2639–2649`). `startFreshRun` does not cleanse. Those facts invalidate a simplistic player-fresh claim, but the concrete zero-start ledger supplies the required history for this case. Without that ledger, P's preexisting Character state would remain unknown, not newly defaultable.

## Buff44: gameplay writers and native invariant application domain

Character `_ready:165–168` creates one Buff per category100..110 for each side. `Buff.init:24–36` creates a plain native `Timer.new`, adds it directly under that Character, sets `one_shot=true`, and sets `process_mode=Timer.TIMER_PROCESS_PHYSICS`, whose actual saved integer value is **0**. It connects timeout to `Buff.onTimeout`.

| Direct Timer writer family | Source location and trigger |
| --- | --- |
| construction/configuration | Buff24–36: new, add_child, one_shot, physics mode0, connect |
| gainTemporary | Buff148–167: only successful duration>=0 gain creates temporary entry; starts if stopped, or stop/start if a shorter timeout |
| loseStacks | Buff245–279: stops after removal empties temporaryStacks |
| onTimeout | Buff317–340: removes timed-out entry; may recurse or start earliest remaining delay |
| combatEnd | Buff342–344: stop and clear temporaryStacks |

`gainStacks` calls `gainTemporary` with duration-1 and cannot start this timer through the permanent branch. Reflection recurses via `Character.gainStacksTemporary`; its destination reaches the same writer family. `Character.combatEnd` calls every Buff.combatEnd. `Buff.reset:52–57` resets current/resist/protection/reflect only; it neither stops the timer nor clears temporaryStacks. `Character.cleanse` calling reset therefore cannot prove the private timer value. Empty current stacks alone also do not imply a stopped timer.

All44 saved Buff Timer occurrences have duplicate consistent representations in `payload.nodes[n].timer` and `payload.source_resources[s].buffs[b].state.timer`. Every Buff's `state.character` matches the corresponding source resource and P/O identity; `stack` equals state.type100..110; every timer node has exact role `buff:<side>:<category>`, class Timer, same native ID in both representations, and unique ID among all22 Buff timers. Those22 IDs persist across both cuts. Both representations are identical for all44. Every row has exact JSON bool `paused=false`, `internal_idle=false`, `internal_physics=false`, `inside_tree=true`, and exact JSON int `process_mode=0`; no bool-as-int coercion was used.

These facts support applying a separately accepted native invariant to the44 rows. The needed invariant and its native version/domain are owned by the root/native reviewer; this report does not prove it. If accepted, exact private-left -1 follows without reconstructing the Buff start/stop history. If rejected, the44 rows remain unresolved; reset is not a substitute proof.

### Escape-domain closure inspected

Whole original project `.gd` scan finds no calls to `set_process_internal`, `set_physics_process_internal`, `set_timer_process_mode`, `set_paused`, or `propagate_notification`. The only explicit `process_mode=` gameplay writers are Buff.init and MultiTimer._init; Buff timers are native Timer.new, not MultiTimer. There are no direct external `buff.timer` alias writers or replacements of Character.buffs after `_ready`.391 observer/collector only sample these Timer flags and do not alter them.

Native notifications named `_notification` are override definitions, not arbitrary notification sends. `set_script` appears only in SilentWolf's Auth/Scores/Players/Multiplayer/WSClient setup, with no Buff receiver. Dynamic `Util.finishTimer` stops a passed Timer and invokes existing timeout callbacks; this remains inside the allowed standard Timer stop + closed Buff.onTimeout family. Dynamic interpolation, property/tween writers and `Table.fill` target visual fields or descriptors, not a Buff timer or either Character field. Character/Player/Opponent method animation tracks target displayed HUD labels, stamina/stun particles, not Buff timers or invulnerability fields. Buff timers are dynamically created and have no serialized scene track. This is a bounded project application-domain finding, not a proof about arbitrary external native modules or unpinned extensions.

## Realize and acceptance handoff

No production adapter was added in this analysis block. Root confirmation can authorize a small exact52/72-target adapter using typed pinned index rows and this specific historical ledger; it must preserve all437 rows/order/exclusions and old evidence. The Character rule must consume actual lineage fields, rather than a generic boolean certificate. The Buff rule must consume actual typed snapshots plus separately accepted native proof and project identity domain.

Independent review should challenge: truncated/pre-gated ledger coverage, boolean starts, alias timers, false role bindings, duplicate identities, unobserved external flag writes, prepare-as-cleanse, reset-as-stop, historical timeout item retention, and cut reentrancy. Root/native reviewer owns Timer.cpp/h semantics. Independent functional/source reviewers own promotion and one new adapter batch; this author makes no acceptance claim.

At this checkpoint: Character8 have a concrete saved-history route; Buff44 have concrete saved-identity bindings and a pending shared-native premise. No actual52-target promotion has occurred. No genuine new capture is demonstrated necessary for these52; absent the accepted routes, their precise missing premises are identified above. Formal75 and King-unadmitted state are unchanged.
