# Phase388 cleanup-clock diagnostic extraction

## 1. Requirements
Use the newly authorized diagnostic exception to extract only `cleanup_clock.physics_frame`, `idle_frame`, `is_in_physics_frame` from the existing otherwise-opaque postcleanup file. Expected original file identity24942B/SHA7d30041b5205da977675ac19e0e1f655c1a906f5c7ae17b2b0b0060c0f629b9a. If key set differs, stop and report. Keep original386's unknown-C fact unchanged. No other business state, runtime, UI or expected data is interpreted, and no model/inputbuild/projection/SUT/Game/pool action follows.

## 2. Design
Pin the whole original bytes, lexically skip unrelated top-level JSON values and decode only the selected control dictionary. Do not copy the original business-state payload into outputs. Confirm the key's direct producer SOURCE assignment. Join C/phase with386's already-owned2574 control rows; determine the first recorded idle at or after C+2, the number of intervening actual physics signals and whether a record exists at exact C+2 idle. Mark direct control values separately from SOURCE ordering assumptions about when cleanup marker follows a frame signal.

## 3. Realize
A standalone stdlib analyzer freezes before execution. Its top-level JSON selector skips strings/containers without decoding their values, then validates the selected dictionary has exactly3 allowed fields and strict INT/BOOL types. It reads the existing386 projection by exact identity, computes frame associations/candidates, and saves only allowed control values, relevant tail rows and source references. Reuse old source evidence; no full-clock/schema revalidation or large opaque decode. Producer, collector and terminal-schema exact2 clauses are documented together, not changed.

## 4. Acceptance Criteria / Tests
One diagnostic extraction and correlation only. Whole original hash unchanged, no sibling business-state values returned. Either a precise evidence gap is reported or direct C and actual first eligible idle are identified with explicit SOURCE-derived phase relation. Explain why exact-two can reject a legitimate first idle under batching; no performance cause, missing input repair or broader native/model acceptance inferred. Seal new finding/owner with repo-only leaves, then stop. Original capture and386 evidence remain unchanged.
