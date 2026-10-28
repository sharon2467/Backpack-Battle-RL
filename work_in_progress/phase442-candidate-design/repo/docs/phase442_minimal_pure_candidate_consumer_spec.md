# Phase442 — Minimal fixed-A pure candidate consumer design

## 1. Requirements

DESIGN ONLY. No candidate fork/copy, model/schema import, model/prepare invocation, EXPECTED read, new capture, pool operation or old control replay. Preserve working formal75,35615-file frozen candidate,440 and441 Source/output. Reuse440's Source/API inventory, accepted initial proofs and model core evidence; do not re-audit12 carriers/815 GDScripts or recreate439 proofs.

Target the single existing441 INPUT-only bundle. Its actual identity is539534 bytes/SHA `c87525f35adf8fa3793cc5d1440dff420dc55f3a24c77e520766b01e8963ae2c`. Root released read-only INPUT/proof inspection for this design, then supplied the completed441 independent/Root input-only acceptance; those receipts are pinned in this design. They grant no model execution. The five-key bundle and14-key runtime remain unchanged. No model permission flag is changed in441 proof; a future separate Root execution release binds accepted input, candidate Source and the pre-run closure decision.

The next candidate should consume the fixed Source-supported initial values as state, independently compute prepare/gameplay/logs/RNG/timers/terminal behavior, and expose complete same-instance business diagnostics before one conditional Tape execution. It must not restore116 presentation dependencies or label native inactive timers fresh. A successful structural/runtime validator is not a completed model comparison, King admission, same-seed result or RL completion.

## 2. Design

### 2.1 Actual441 DTO and the smallest Source surface

The inspected INPUT contains39 items with the original O:12 hole,77 node configs,78 processing rows,33 business timers,2574 exogenous passes (2288 physics,286 idle),365 ordered primitives (146 randf_range,125 randf,94 randi_range).31 timers are one-shot and two tick timers repeat; all have wait1.0/mode0/autostartfalse/pausedfalse/private-left -1. P/O invulnerable=false, origin=null, buffProtectStacks=0. All39 emitted limiter/counter/drag/tween values are actual zero/false and observed pre-cache-empty predicates. Processing flags are retained independently: Game/Util physics+idle, Characters physics,39 items idle, root internal-physics; combat_timer and all33 Timer internal flags begin false.

The clock contains batched physics and variable idle deltas; preserve all2574 records. The existing Engine.step increments elapsed only on physics passes, and the entire declared physics duration is38.13333532214165 seconds. Therefore the fixed input does not justify changing the existing120-second budget or implementing an ended-tail exception. Native cleanup location/winner/terminal C or N were not read or inferred here.

Prefer an isolated future copy of the already frozen35615-file package, not the working formal75 package. Planned changed files are **only `native_replay_v8/engine.py` and `native_replay_v8/genuine.py`**.13 other files remain byte-identical, including TimerRuntime, finite FrameDriver, randomness, histories, state, observed runner, compare, seed helpers and package exports. If implementation discovers an unavoidable third-file change, report the exact consumer before extending scope. No new general simulator/adapter framework or alternate-layout support is planned.

The existing observed.run_input_bundle already provides validate fixture/runtime → construct actual TapeRandom → construct one Engine → Engine.run → Tape.assert_consumed. Keep it unchanged; put same-instance diagnostics in Engine's result/snapshot hooks. A later narrow external launcher handles Source/input-seal hashes and output files. It does not pass proof objects into Engine or give the worker capture/EXPECTED access.

### 2.2 Fourteen fields to concrete consumers

|441 field | Candidate consumer / validation | Avoided legacy dependency |
| --- | --- | --- |
|schema, mode, profile_id | New exact441 input-profile branch at the start of validate_runtime_inputs; genuine input/result/observer_label all share it. | No call to closed SINGLE_KING355 gate and no wholesale legacy17-key conversion. |
|fixture envelope | Reuse exact fixed-A fixture predicate (six IDs/class0/20+19/layout/Unranked/below-master) and accepted alias scope. | No arbitrary fixture extension or O renumbering. |
|checkpoint | RuntimeDTO util_time and activate phase/bits; FrameDriver clock header join. | No prepare clock fabricated from activate time. |
|environment | Strict fps60/scale1/unpaused; code-bound ordinary-domain closure is separate. | No caller no_pending_gameplay_transform boolean. |
|nodes |77 exact configs, sparse path/index/priority/kind validation and scaffolding. Game is already present; do not append it a second time. | No root_node duplicate or fixed P/O invu-child5 literal. |
|processing_nodes |78 actual Source identities/classes/four flags/tree coordinates; root selected from this table, ordinary membership applied after driver construction. | No UI authority/particle bindings or false assertion that observed enabled callbacks are modeled by shape alone. |
|timer_initial |33 real TimerRecords; merge six config/value scalars with node configs locally; assert constructor/configuration result equals supported private initial bits. | No fresh_configured label and no synthetic inactive_auxiliaries snapshots. |
|initial_items |39 exact seven-field records, runtime typed validation, constructor/pre-activation equality checks for emitted scalars. | No prepared cache or charge3 copied into initial state. |
|initial_characters | Validate/apply/assert invulnerable, semantic item origin and buffProtectStacks from supported values. Fixed actual false/null/0 matches existing model constructor, but is not accepted merely because defaults match. | No bubble/display seed. |
|prepare_order, activate_order | RuntimeDTO preparation tuple and existing39-item dispatch, exact equality/identity coverage as fixed input. | No inventory sorting substituted for actual Game order. |
|terminal_profile | Explicit441/native390 at-least-two policy mapping, shared result profile. | No exact-two/C+2 interpretation or UI footer stop command. |
|frame_clock | Unchanged finite decode/FrameDriver, including every batch/idle/delta. | No HeadlessKingFrameDriver/Fixed60Passes seed path. |

Business Timer set is22 Buff +2 tick +2 fatigue +2 invu +4 rage auxiliaries +1 KingBuff. Preserve numeric-native Buff→existing symbolic model role mapping. Actual P invu is parent+[7], O parent+[5]. Keep excluded UI positions as inert sparse gaps; never renumber business children. No king_hide/king_drag/particle callback or crown/light/bubble value is required by this profile.

### 2.3 Timer construction and callback sequence

Build the sparse graph with33 inactive TimerRecords, configure mode/one_shot/wait through unchanged TimerRuntime APIs, and assert private/processing/paused/autostart state equals the supported input. Do not call stop to manufacture agreement or write private fields directly. The native object may have been used before; only the current supported state is represented. FrameDriver's existing check that the **new model timers** were not started is a bootstrap condition, not a native lifetime claim.

Leave Util ordinary processing/callback slots unset until creating EngineFrameDriver, because the unchanged FrameDriver constructor requires a fresh model Util callback slot and registers both Util callbacks itself. Then register other business callbacks and apply observed ordinary flags. TimerRuntime already gives the root internal-physics membership; use the observed root idle flag and validate all remaining root flags. Do not fake mutable group internals or modify the component kernel.

Existing callback bodies remain: tick regeneration/poison, Buff temporary timeout, fatigue start/tick, invu end and KingBuff state transition. Four auxiliaries are real records and must remain inactive for this fixed no-rage caller domain; an unexpected auxiliary timeout fails closed rather than adding unreviewed rage semantics. At cleanup, actually stop all four auxiliary TimerRecords in Character.combatEnd order. The old engine only appends synthetic inactive_aux_stop rows; that is insufficient for33 real records and strict Timer API diagnostics.

Preserve exact frame dispatch/order, ordinary membership changes, same-pass cleanup and the saturated two-future-physics then first actual idle-pre-internal barrier. No endpoint/control/winner/cleanup count configures Engine. Activation-time death remains unsupported by the unchanged FrameDriver request_end precondition. Existing run/result must require finalized driver, exact pass exhaustion and no trailing records; Tape exhaustion is checked by unchanged observed runner.

### 2.4 Pure King split and all random consumption

Keep King constructor business state charges0/protectedBuffs3.0/manaCost4.0 and existing item counters. king_prepare derives charge3 from catalog and calls king_set_state0 in actual prepare order. In the pure branch, king_set_state must first perform the unchanged `histories.item_state(item,state,next_event=...)`, then return from only its presentation tail. Preserve state0/1/2, withNextEvent/eventNum/event.id, adjacent compression and RoyalGoobert replay semantics. Never replace this with a total no-op.

king_effect keeps buff protection/heal, charge/mana checks and decrement, InvulnerableStart, real invu and KingBuff starts, mana use and later InvulnerableEnd origin. make_invulnerable retains its exact `invulnerability_pitch:<instance>` randf_range call and all other core cooldown/balanced/damage primitive calls stay unchanged. Remove only display input lookups/AutoHide operations in the pure branch. Local legacy display bookkeeping can remain unreachable or diagnostic-only, but no pure result or admission depends on it.

Engine's new profile must require actual TapeRandom before model mutation; direct constructor use with None/SeededRandom cannot silently activate a genuine seed fallback. Old profiles retain their old behavior. No prepare/ordinary/helper consumes random returns merely to match counts. Because441 preserved the complete selected stream and rejected any selected primitive at/before activation, a model prepare call consuming Tape is a phase mismatch and fails, not a reason to skip or move records. Only an actual replay can establish complete365-draw consumption; this design makes no result claim.

### 2.5 Same-instance diagnostic contract

No new observed runner is needed. Before future execution, freeze Engine diagnostic output at: constructed, prepared/off-clock, immediately pre-activate, post-cleanup and final eligible-idle cut. All snapshots come from that one Engine/TimerRuntime/FrameDriver/random instance. Diagnostic getters only read; they do not step, sort/reconfigure active groups, call gameplay, consume Tape or force finish.

Required output comprises existing events/allocated parents/event_references/histories/final rule state/random audit; actual model prepare/activation order; ordered ordinary/timeouts/API traces;33 real public/private/processing Timer states and node flags; initial-character/invu origins/King business counters; FrameDriver phase/pass-index/remaining/future-physics/barrier/pass trace; Tape position at prepare/pre-activate/result. Do not return old `full_fx` completeness or synthetic auxiliary private values. Native later private Timer countdowns are not directly exposed; model private evolution can be reported independently and compared only through declared lawful Source/public evidence, never relabeled a sampled native value.

Record Timer start argument **arity** as well as bits. The old activation calls tick with explicit0 through `_start_timer(role,duration=0.0)`, losing the distinction from native `start()` argc0. A minimal pure call-site/wrapper adjustment must represent actual zero/one-argument forms, including no-argument tick starts, while preserving numeric TimerRuntime behavior. `_stop_timer` records argc0. TimerRuntime.start's ApiResult.ok is helper success status, not a native BOOL return: pinned native Timer.start/stop are void. Keep status and Source-known NIL semantics distinct from actually sampled method BOOL/NIL returns. Do not fabricate a native return observation not present in the capture ABI.

Preparation is a logical pre-activation transition, not a simulation of the unprovided pre_prepare→activate idle interval. Mark preparation diagnostics `prepare_off_clock`; no new genuine prepare Util timestamp is invented from the activation header. Events/histories retain their existing combat-time semantics. Later comparator coverage must distinguish Source-order/business values from pre-clock timestamps that the14 DTO does not contain.

### 2.6 Five pre-run closure blocks and actual remaining points

1. **Constructor/prepare:** typed emitted scalars are now known from441, so their mapping/equality can be specified. Unemitted Character/Buff/RNG/cache state is not magically proved by14-key shape or by439's narrower count. Reuse existing model/source acceptance and existing input-proof references for exact fixed-A constructor/prepare predicates. If those references do not cover a necessary model-read field, retain a named model-release blocker and request only a narrowly scoped existing-checkpoint/Source proof supplement; do not redo12/815 audits or recapture. No extra state/proof is smuggled into DTO.
2. **Ordinary callback/transform/RNG domain:** observed Game and39 item idle memberships are known. Their model no-op path needs the specific existing finite Source/noninterference guard, not the old assertion string about complete UI authority (441 did not semantically validate that old full-FX gate). Bind the exact existing guard/proof for this case or report the precise unclosed receiver; do not restore116 display predicates or explore a new UI forest.
3. **King logs/RNG:** a small Source comparison of the new pure branch against unchanged history/effect/invu call order closes the intended split. Needed code sites are named above; accepted history/RNG core is reused. Actual event/state/Tape equality remains for the one later independent comparison, not a reason to rerun old tests.
4. **Runtime and same-instance output:** new typed441 validator,33-record scaffold, no-seed-fallback guard and frozen diagnostics must be independently accepted before execution. Bind actual441 final input seal and new candidate Source; do not change441's runtime_validated/model_release=false flags. A separate Root one-run release is required.
5. **Strict output map:** before running, freeze the business callback/API/terminal diagnostic schema and per-required-site model→native projection plan. Reuse existing typed event/history/diff primitives; old sorted/truncated callback checker is insufficient. Unknown required business sites/returns remain INCOMPLETE rather than silently dropped. Expected values are read only after result seal; no pre-read to select input or diagnostic fields.

The actual bundle settles cardinalities/flags/default emitted values and eliminates speculative topology/Timer/budget choices. It does **not** establish model prepare equality, no-op callback domain, event parent/history correctness, actual365-draw consumption, cleanup cut or complete comparator coverage. Those are real future Source/execute/output obligations, not missing capture allegations.

## 3. Realize — smallest proposed function changes

### genuine.py only

- Add fixed441 pure input-schema/profile/ABI identity constants from the accepted actual bundle/ABI. Keep native producer390 attribution distinct from model package/profile naming.
- Add `validate_pure441_profile(data,fixture)`: strict14-key profile/terminal/fixed fixture dispatch; no mutable verified flag, old patch whitelist or source proof in runtime. Source/input/candidate acceptance receipts are external launcher conditions.
- Extend only `validate_profile`, `validate_result_profile`, `observer_label` and the profile set for this exact branch. Keep SINGLE_KING355 require_single_king_admission unconditional rejection and other profiles unchanged. Result label must identify the new candidate and native390 mapping, not pretend it was produced by old355/154.

### engine.py only

- Add `_pure441_profile(runtime)` and early `_validate_pure441_runtime(data,fixture,runtime_dto)`: strict14-key/types,39 identity/orders,77/78 sparse role/native-ID/path/position consistency, independent flags,33 Timer map/config/initial-state and P7/O5, exact checkpoint/header join, strict initial fields, finite clock. Return existing RuntimeDTO after validation; never synthesize missing17-key UI fields. Extend `_integration_domain` only for ordinary callback bookkeeping; keep `_source_king_profile` false so fixed-seed/headless paths cannot be selected.
- Add `_build_pure441_scaffold(dto)`; branch from `build_runtime_scaffold` before old17-key access. Merge timer configs locally, keep root and Util setup order above, return33 real timers/ordinary roles. No component Source edits.
- Update `CombatEngine.__init__` only for pure prevalidation/TapeRandom requirement, three explicit supported character values, minimal King business state, scaffold/finite driver choice and diagnostic initialization. Validate constructor-emitted scalar equality from actual values, not Python defaults alone. Keep Character/Item core dataclasses and catalog unchanged.
- Add a small `_validate_pure441_constructed`/`_validate_pure441_prepared` pair for emitted scalar invariants,33 inactive model Timer state/identity and Tape preparation position; keep broader unprovided predicates external/not asserted. Hook into existing `prepare_only`/`activate_from_checkpoint` without duplicating those business loops. Tick start call sites preserve argc0 in the pure branch.
- Branch `king_set_state` **after** history recording; no UI timer/particle input access in pure mode. Keep king_prepare/effect/make_invulnerable/invu_timeout/king_buff_timeout business order and random calls. Only touch other methods if needed to avoid an actual absent UI-key lookup, not to rewrite their rules.
- In pure cleanup, use real `_stop_timer` for all four auxiliaries in the existing correct order; old `_integration_aux_timer` remains only on legacy paths. Connect all33 real timeout handlers; auxiliary activity remains fail-closed outside the fixed domain.
- Extend `_start_timer`/`_stop_timer` and `_integration_callback` only with truthful ordered diagnostic arity/status/typed-return-role information, preserving component behavior. Add pure no-op diagnostic branch only after the specific noninterference domain is accepted; do not invoke a full-FX validator or invent a guard.
- Add `_pure_business_snapshot(stage)` and a pure branch in `EngineFrameDriver.snapshot`, `_runtime_projection` and `result`. Return same-instance snapshots and complete business traces without legacy full_fx/particles/aux constants. Keep core finite FrameDriver algorithm, run/step budget and observed entry unchanged unless Source review identifies a concrete necessary deviation.

This list is an edit surface, not permission to touch every listed method: branch once where possible and conserve unchanged function bodies. Any unexpectedly necessary third module/component change or unavailable pre-run predicate is reported before implementation scope expands.

### External execution boundary, later

A small Root runner prepins the exact isolated15-module set, stdlib closure, accepted441 input/seal, new Source/constructor/no-op/output-map decisions and one-run authorization before candidate import. The worker receives only bundle+Source and an output directory. It calls unchanged observed.run_input_bundle once, writes the original result/diagnostics and source/input readback, and never receives capture/EXPECTED paths or proof as mutable gameplay state. Comparator is separately authorized after output seal. No generic task framework, new capture or automatic retry is part of this design.

## 4. Acceptance Criteria / Tests

Design acceptance agrees to the exact current441 ABI and fixed case, two changed modules/13 conserved modules preference,33 real timers, no native-fresh mislabel, history-first King split, unchanged finite clock/120s semantics and separate five-block model closure. This document authorizes no implementation or execution by itself.

Future Source review should prove every new pure branch avoids king_particles/ui_authority/root_node/inactive_auxiliaries/timer_lineage and display Timer lookups; P7/O5 and77/78 roles are actual, not guessed; construction is completed before ordinary flags/driver initialization; all four aux stops are real; Timer API arity/helper-status/native-void distinctions are truthful; diagnostics are read-only; direct pure Engine construction cannot seed-fallback.13 conserved files and working formal75 stay unchanged.

Only necessary new interface controls are proposed: actual14 DTO typed/role/config/alias rejection; omitted Source-origin/state reject; distinct0/1 start forms and real aux cleanup; pure state-history0/1/2/withNextEvent preservation; UI fields absent without business lookup; no-seed/prepare-Tape mismatch rejection; same-instance nonmutating diagnostics; one small nonalternating finite-tail/missing/trailing/activation-death wrapper check. Reuse accepted Timer/FrameDriver/RNG/history core evidence without replaying old controls. Controls do not establish actual fixed-A model equality.

After441 final input acceptance and new candidate Source/closure/control acceptance, Root may release one conditional Tape model run. Stop at the first real mismatch with its exact field/label/site/bits; preserve result/failure, do not edit input/Tape/clock against EXPECTED or retry automatically. Independent output comparison follows sealed result. Until five blocks are resolved and that comparison completes, runtime/model/King/fullschema/same-seed/RL completion is not claimed.
