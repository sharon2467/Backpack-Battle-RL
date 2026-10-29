# Phase450 — Fixed448 collector output ABI v3 repair

## 1. Requirements

Preserve445v1/448v2, their owners/controls and the448 first actual comparison error. The existing446 model result is reused without a battle rerun. Fix only four serializer Source mismatches: collector fields() returns an encoded dictionary; collector REAL includes display; collector ARRAY includes variant_type; collector TemporaryStacks has five fields. Keep the frozen445 eight business sections and every business comparison. No EXPECTED read, adapter import/call/control or model execution by the author; compile-only, then independent Source/negative controls and continuation comparison.

## 2. Design

Copy448v2 to tests/phase450_pure_business_output_v3.py. Modify only decode_native and project_native_final. Collector Source data/phase391-terminal-source/collector.gd591–596 fields() returns encode(values); state_snapshot passes that wrapper into char.fields. Decode the whole collector object first, then require and remove the three original declared presentation fields characterName:string, chibi:bool and invulBubbleVisible:bool from the decoded fields dictionary. This corrects the layer; business fields remain required and no blanket optional/default behavior is introduced.

Collector encode705–760 has exact alternatives to the sink's original shapes: REAL {type,display,binary64_be}, ARRAY {type,variant_type,values}, TemporaryStacks {type,native_id,amount,timeout,item}. Keep sink REAL {type,binary64_be}, ARRAY {type,values} and model component REAL {type,binary64_le}. Display is string metadata only; finite BE64 remains the value. Collector variant_type is strict INT for its six permitted Godot3 array families (Array19/Raw20/Int21/Real22/String23/Vector2_24); BOOL/unknown tags/extra keys fail. Arrays preserve original order and all decoded semantic values.

Core/Buff.gd346–354 declares TemporaryStacks amount:int,timeout:float,item:Item. Validate exact five fields, canonical positive native_id, strict INT amount, finite REAL timeout, and null or bound Item collector instance_reference. Reject Character P/O, Timer/foreign refs and string impersonation. Return exactly amount/timeout/item, matching the already conserved model state.project_buff_fields representation. Native object ID is provenance, never a guessed Python object ID or a new business field.

## 3. Realize

- decode_native: add only the collector REAL/ARRAY shape alternatives and uppercase TemporaryStacks exact branch. Keep existing native_ref/event_ref and strict dictionary/INT/float decoding unchanged. Unknown shapes fail.
- project_native_final: decode_native(native,bound) once before visiting characters; verify decoded fields dictionary and exact original three named field types, then delete only those display fields. Continue the same _rule_state, winner and game/event_bus/timer projection.
- Freeze v2→v3 patch, two-function AST conservation, collector/sink/Buff/model source pins and exact function/line evidence, compile-only receipt and owner in data/phase450-business-output-source-v3. Old448 first comparison result is context/evidence, never a source of input/default values.

## 4. Acceptance Criteria / Tests

Independent controls use actual tagged dictionary char.fields, not a hand-unwrapped fake. Valid collector REAL display/BE64 and both ARRAY shapes pass; malformed keys/display type/bits/nonfinite/BOOL variant_type/unknown family fail. TemporaryStacks valid Item/null passes; amount BOOL/REAL, timeout INT/nonfinite, invalid ID, wrong/foreign/Character/Timer item refs and extra/missing fields fail. Original three encoded presentation fields decode then are removed; missing or wrong-type declared fields fail at their correct decoded layer. A retained invulnerable/business field is not optional and still changes the strict result. Preserve all prior448 identity and41slot rejections. Independent continuation compares the already sealed446 result and existing accepted capture once; do not rerun battle or crop a business difference.
