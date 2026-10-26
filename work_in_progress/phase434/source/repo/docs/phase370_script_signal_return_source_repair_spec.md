# 370 script signal return contract repair

## 1. Requirements

Preserve all368/369 frozen code, failures, map, fixtures/seeds, standard15 and closed356/361 gates. Read sealed369 first-source-block7856B/afcc1979 before deriving new source. Object::_emit_signal (the ClassDB GDScript binding) calls native emit_signal then returns Variant()/NIL, discarding native Error. The368/369 INT/OK guard was wrong and made the successful ack path fail. This is a SOURCE contradiction; Godot/dynamic controls still0.

Only new370 SOURCE/text/compile/AST/identity sealing is authorized. No probe/Game/pool/inventory/helper/restore/READY/attempt/model/projection. Do not regenerate the accepted saved-only368 map. No NIL→OK0 conversion or invented native Error.

## 2. Design — explicit erratum to368/369

Replace the wrongly named emit-error field with actual `script_emit_return` plus strict BOOL `script_emit_return_observed`. Before call: return=null, observed=false. Immediately after the real script expression returns: store its unchanged NIL value and observed=true. Native Error has separate constant provenance fields `native_emit_error_available=false`, `native_emit_error=null`: unavailable, never observed0.

All sink/collector/diagnostic/context references change together. EMITTING requires observed=false and NIL pending value; RETURNED/FINALIZING require observed=true and actual TYPE_NIL. These states distinguish an uncalled null from a returned NIL. NIL alone proves no dispatch success. Retain sole exact flags0/nobinds/live receiver and both callback/finalizer method checks, synchronous bracket/actual IDs+frames/once, exact ack, source success and finalizer actual BOOL return before FINALIZED. Two-stage same-stack sampling/serialization and all no-second-getter/clock/sequence behavior remain unchanged.

Direct script `finish_source_cut()` return is a different contract: Object::_call_bind returns call(...), and Object::call returns script_instance->call Variant on CALL_OK. The current collector method explicitly returns its frozen BOOL success or false. This SOURCE evidence supports retaining the actual TYPE_BOOL guard; it does not replace forthcoming language observation.

Opaque control ABI changes only. Accepted12 input files,17-key UI validation DTO and runtime/model ABI stay unchanged. New host/recovery only version SOURCE/review/ROOT-schema identities. New sink identity updates the one sink patch path; other74 patch payloads are exact. Reuse368 map original bytes/path and retain all original failure evidence.

## 3. Realize

- Text preparer reads the true binding finding and owners. New sink/full template rename the old state variable, add observed=false, store the actual result then mark observed=true, export actual-return/availability fields and replace INT/OK expectation with strict observed/NIL. Strengthen live receiver check to include the exact oncut method as well as finalizer. All other function text is conserved by full byte inverse.
- New collector/full template replace both old control references: oncut verifies not-yet-observed NIL inside EMITTING; finish verifies observed NIL and explicitly unavailable nativeError inside FINALIZING. No stale emit_error key remains in generated GD. No callback/sampling/serialization ordering changes.
- New host/recovery explicit literal bindings point to new370 freeze and future real independent review; no future pin/status is fabricated. Complete inverse/AST and old dependency hashes are sealed.
- Record Object.cpp wrapper/ClassDB/call-return excerpts, a complete changed-field reference matrix, exact function delta and old owner readback. Compile Python source without imports; freeze new source/owner and read all leaves, then stop.

## 4. Acceptance Criteria / Tests

SOURCE checks: every emit-error reference removed from new GD; actual result assigned once; observed assignment follows call; nativeError availability never true and value never fabricated; sink/collector control keys agree; only declared functions/declarations differ; all unrelated clocks/fields/getters/74 patches/map/standard15 bytes unchanged. Retain first failed designs rather than revising their claims.

Independent new language gate must actually observe wrapper NIL separately from callback/finalizer results and reject missing/mismatched ack, unknown receiver/flags/binds, direct/reentrant/duplicate/phase/frame violations and false/nonBOOL finalizer returns. All prior33 dynamic obligations remain unexecuted until real authorization. Author claims only SOURCE identity/compile and does not self-sign semantic/native acceptance.
