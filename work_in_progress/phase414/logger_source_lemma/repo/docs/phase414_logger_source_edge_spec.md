# Phase414: bounded logger/history SOURCE lemma

## 1. Requirements

Resolve only Phase412 N1's logging edge using the two expressly authorized original SOURCE leaves: Core/CombatStatLogger.gd4681B/SHA25620f6f088c7debf727e8de538eeff71cbbdf7562e46ecbea1e90860436334e831 and Core/StatHistory.gd832B/SHA2565ae1f194e97dd6e1657e4266864f10448504026f91713a2dc9a1b61021bc498b. Root authority is the separate logger/history supplements in data/phase411-root-initial-audit-release. Both resources are absent from actual391 native-patch-source.paths and therefore use the baseline bodies under that Root binding.

No N2–N6 implementation, input/capture/EXPECTED read, source import/call, audit/schema/model/native run, or older artifact modification is authorized. Read both files completely; follow only already-allowed direct SOURCE callees. New callees outside that scope would remain explicit frontiers. There is no new executable implementation or proof framework.

The original counts remain separate:1391 whole-audit DIRECT/SUPPORTED targets;1371 selected412 documentary support rows;88 unresolved targets (12Character,6King,70Timer). A local lemma does not promote any target or open genuine-input/model/King admission gates.

## 2. Design

The finite pins cover the two original bodies, their two real Root supplements, four existing executed391 GD bodies, the391 patch descriptor and412owner. File hashes and source ranges are evidence; no original inputs are opened. The new StatHistory supplement arrived before414 sealing and is incorporated in this single final version.

The relevant chain is King.prepare → Item.setState(Inactive) → CombatLog.snapshotItemState → CombatStatLogger.logItemState → selected history.addValue → optionally Util.equals. Item.setState calls King.onStateChanged only after the logger call returns normally. The observed charges field is not evidence that this entire call chain completed.

CombatStatLogger.logItemState(item: Item,state,eventNum: int) reads its itemStateHistories dictionary, indexes it by item and invokes addValue(eventNum,state) on that result. Its own body has no assignment, Timer API, Character.setStat, onStateChanged, explicit signal, deferred call or yield. The method name is not used to infer purity: the delegated call performs real writes.

The same full logger file declares itemStateHistories={}. prepareItem conditionally stores StatHistory.new() there when item.character().playerId==playerId. clear clears that dictionary. prepareItem also calls item metric/stat getters and other history methods; it is initialization context, not a direct callee of logItemState. CombatLog.onPrepare shows a call site, but414 establishes neither its actual execution nor the receiver's runtime identity at the checkpoint. The public dictionary may be mutated elsewhere; no whole-program no-alias invariant is asserted.

StatHistory has no explicit _init method. Its SOURCE member initializers are eventNumbers=[] and values=[]. These declarations alone are not an actual allocation/ownership observation. addValue(eventNum,value) reads values.empty(); if empty, it skips equality comparison. Otherwise it reads values[-1] and calls Util.equals(last,value). If empty or unequal, it calls eventNumbers.push_back(eventNum), then values.push_back(value); if equal, it does not append. The order is part of the lemma. It stores arguments; it does not clone or sanitize them. It does not locally call a Character/Item/Timer method or emit a signal. A failed append or invalid receiver/member cannot be assumed away when claiming normal return or paired histories.

The already authorized executed391 Util.equals(val1,val2) is exactly `typeof(val1)==typeof(val2) and val1==val2`. It has no GD assignment, signal or nested script-method call. In the bounded King.prepare path the source supplies CrownState.Inactive, an enum INT0. Under that scalar-argument premise, a differently typed prior value fails the typeof comparison before equality; if equality runs, both values are INT. No arbitrary-object equality purity is claimed for the general untyped addValue API. Native builtin typeof/equality/Array semantics are used as language semantics, not newly runtime-tested in414.

Other StatHistory methods are explicitly outside this immediate call chain: clear clears both arrays; addValueAcc reads the last value, adds and delegates to addValue; hasData/getValueAt/getLastEntryBefore read arrays, sizes and binary-search indices. Their availability does not imply they were called before this initial boundary. No source recursion through them is required by logItemState→addValue.

Already available caller bodies remain relevant context. Item.character reads placed and returns inventory.character or Game.PLAYER. snapshotItemState reads playerId/event number/optional event.id, invokes the logger, then may assign CombatLog.activeItemState[item]=state. That is replay bookkeeping, not a stored native King crown field. The caller's observer entry/leave hooks remain under their previous391 source contract;414 does not independently reaccept those hooks.

**L414, unconditional local-body claim:** the inspected logger/addValue/equals SOURCE bodies contain no explicit store into Character.invulnerable/invulnerabilityItem/invulBubbleVisible, King crown/light properties, or Timer state. addValue explicitly mutates history arrays, so it is not a pure function.

**L414-C, conditional narrow effect claim:** if the dictionary selects an instance executing exactly the pinned StatHistory body, its two members are ordinary Arrays belonging to the intended logger history without a target-relevant external alias, Util dispatch reaches the pinned equals body, and arguments have the bounded scalar types with valid indexes/call domain, this path either does nothing or appends only the event number and state to those history arrays. It contains no script callback or target-state write on that path. This conditional claim is a SOURCE lemma, not proof that these receiver/member/alias/domain premises held in the actual execution. Reference retention for arbitrary object-valued states is outside the scalar claim.

## 3. Realize: evidence, unresolved premises and target impact

No new callable API is introduced. finite-pins.json records exact SOURCE/authority bytes. lemma-report.json records exact existing signatures/ranges, read/write/call inventory, conditional premises, and affected-target counts. The owner seals these documents and a static consistency report.

The previous unknown implementation edge StatHistory.addValue is now locally inspected; Util.equals is already inside the approved405/412 SOURCE scope and is pinned in414. There is no new unresolved external script callee in this bounded addValue→equals body. Remaining N1 obligations are actual receiver selection, correct history slot initialization/member types, lack of target-relevant alias/foreign replacement, and normal-return/domain evidence. Do not replace these with prepareItem's existence, a method name, source defaults or a convenient Boolean. No additional source or input is read to establish them here.

Target mapping accounts for all88:

* King pre_activate crown/light_visible/light_modulate (3): the logging implementation prefix is materially narrowed. Under L414-C it adds no intervening target write before onStateChanged. The actual premises, completed prepare/onStateChanged path and previously identified interval/replay gaps remain unproved; no target promotion.
* King pre_prepare fields (3): no actual prior setState, last-crown state, constructor light value or return interval is established. King.onShopEntered directly invokes onStateChanged and does not need this wrapper. No new initial-value proof.
* Character targets (12) and Timer private targets (70): no initial-value/lifetime recipe is changed. L414's direct-store exclusion applies locally, but adds no actual field observation or proof of their other writer exclusions.

412 originals remain immutable. The complete recipe count stays0 in this handoff; all88 retain their previously unresolved classification. This is not a claim that original data is absent, invalid or requires recapture. ReplayLogLineEvent/Character.setStat, all Timer lifetime questions, N2–N6 and full structural validation remain outside414.

## 4. Acceptance Criteria / Tests

Only author text/JSON/byte consistency checks are performed.

A01: both real supplements, exact sizes/SHA and ordinary nlink1 source types match; neither resource occurs in391 patch paths. No live installation/capture is inspected.

A02: both complete SOURCE leaves are read, and exact logItemState/addValue/equals plus context ranges are pinned. Report dictionary reads, empty/equality branches, ordered two-array appends, and actual mutable history effects.

A03: distinguish explicit local-body exclusion from conditional no-target effect. Keep receiver/member/alias/scalar/domain/normal-return assumptions visible; do not infer observed execution or purity.

A04: no unapproved external SOURCE recursion; Util.equals is reused from the existing allowset. Other StatHistory functions are not presented as callees of addValue.

A05: all88 target-impact counts sum correctly;1371 support and1391DIRECT counts retain distinct scope. No old ledger rewrite, complete recipe, genuine input or admission claim.

A06: new owner covers all deliverables; source pins/ranges and previous412owner remain unchanged. Audit/SUT/schema/model/FrameDriver/Godot/native/inputbuild/projection and original capture/EXPECTED reads are0. Independent acceptance is pending; seal and stop.
