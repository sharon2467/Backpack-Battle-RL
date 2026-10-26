# 368 two-stage finalization preparation addendum

## 1. Requirements

Preserve the already frozen32-obligation preparation. ROOT approved a local control refinement: the synchronous signal callback freezes/acknowledges only; successful output/quit happens after emit actually returns. This is preparation only, with no new source import, API, process, pool or implementation acceptance.

## 2. Design

Use the phase chain EMITTING -> RETURNED with exactack/Error checked -> FINALIZING -> FINALIZED. `on_idle_source_cut` owns the sole approved full primitive DTO sampling and once guard. The sink sees the real emit return, then calls only the unique fixed collector `finish_source_cut` in the same stack. Finish only serializes frozen DTO/control and requests quit, with no second getter, snapshot, clock step or business work. Sink records actual finish return/phase after the call; early records cannot falsely claim that return already occurred.

## 3. Realize

The new `contract-addendum.json` explicitly supersedes interpretation of original rows19/20/21/22/24 and adds one distinct obligation33 for frozen serialization and truthful finish acknowledgement. No original file is edited. Future source freeze must specify exact return types, acknowledgement fields and ownership; do not guess success from truthiness or caller flags. A single authorized empty-project probe can cover two-stage control semantics; full business DTO sampling purity stays actual SOURCE review, never a fake Game positive.

## 4. Acceptance criteria

Direct/repeated/reentrant/wrong-phase/wrong-frame finish calls, emit error, acknowledgement mismatch and finish failure reject without another snapshot or false FINALIZED. A successful path has exactly one sampling callback and one finish, same stamps, immutable primitive DTO, no deferred/yield/frame advance, unchanged17-key model ABI and still-closed356/361 gates. Actual outcomes remain NOT_EXECUTED until frozen implementation and ROOT gate.
