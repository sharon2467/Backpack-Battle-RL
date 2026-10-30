# Phase505v2 AST EOF function append repair

## 1. Requirements

Root explicitly released this preparation-only repair after original505 generation1 stopped on a duplicate last200-byte suffix. Preserve original Source/SPEC and partial owner `18b48d142672deb5626bfa1a0e1b3b3e5d321eae87867d5a442c295b0431edf5`; no candidate payload was written. Original505/504 implementation and design requirements remain unchanged.

## 2. Design

New producer `tests/phase505_prepare_captured_nonking_source_v2.py`, output `data/phase505-captured-nonking-source-v2`. The append helper uses the complete final top-level AST FunctionDef, exact expected name, whole body unique count1, and only whitespace after the function. Engine requires `_build_source_pure_scaffold`; genuine requires its actual last function `validate_pure441_profile`. No fallback/tail guessing, count widening, business/profile change or original rewrite.

## 3. Realize

Change `Edit.append` to accept explicit expected_name; parse current buffer, require final AST node matches, verify its full segment count1 and EOF suffix whitespace, then use existing positional replace/inverse. Bind the two caller names and new OUT/SPEC. All other transformations are byte-exact original505 producer. Compile full workbuffer before one new Source generation (cumulative generation2); first new actual error is preserved and stops.

## 4. Acceptance Criteria / Tests

Author Source generation/compile/static conservation only.15 candidate compile objects discarded; no candidate/schema imports, tests/model/Godot/Expected/host/pool. Two changed runtime modules/13 exact497 modules, raw32/67/66, real six cleanup Timers, zeroKing and pending64+8 actual Native gates retained. Success is only Source frozen pending originalAstra506 independent review/finite synthetic controls, not author acceptance or Native admission.
