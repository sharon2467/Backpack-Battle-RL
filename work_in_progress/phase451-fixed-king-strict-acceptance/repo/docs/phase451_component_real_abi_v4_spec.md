# Phase451 — Component REAL exact ABI v4 repair

## 1. Requirements

Preserve450v3 and its first continuation error, earlier versions, the frozen445 eight-section contract and446 sealed model result. Repair only the Source-confirmed missing model component REAL form. No model rerun, EXPECTED reopen, adapter/component import or call, or author controls. Compile-only Source handoff to the independent reviewer.

## 2. Design

Copy450v3 to tests/phase451_pure_business_output_v4.py. The conserved443 staged native_replay_v7/timer_runtime.py typed(float)49–61 returns exactly {type,binary64_le,display}; engine._full_timer forwards timer_state's typed public DTO. Add precisely that three-key set to decode_native's existing REAL allowlist. Existing display string validation, canonical16hex digits, one-endian selection and finite binary64 value validation remain unchanged. Display is metadata, never parsed as the authoritative number. Null/BOOL/INT/string and all business projections remain untouched.

## 3. Realize

- decode_native: extend its REAL allowed key sets by {'type','binary64_le','display'} only. Preserve all other AST, imports/constants and37 function signatures.
- Record timer_runtime.typed function byte/line pin and engine._full_timer forwarding Source pin. Freeze the one-boundary patch, AST conservation, compile receipt, exact v3/context references and owner under data/phase451-business-output-source-v4. No adapter invocation.
- Independent control boundary uses the actual component DTO shape: float LE bytes plus string display. Proposed positive cases include signed zero and a finite value with a deliberately different display string to establish bits authority. Negative cases include non-string display, missing/extra key, both endian fields, malformed hex, nonfinite LE bits and a non-float tag. Existing BE collector/sink forms stay supported with their original strict fields.

## 4. Acceptance Criteria / Tests

Independent Source review confirms one additional exact field set and all other AST conserved. Reviewer performs the narrow component-shaped positive/negative controls, then continues the existing eight-section comparison using the unchanged446 sealed result. No component/model import is needed to obtain a synthetic typed DTO; no battle rerun or EXPECTED-derived input/default/projection crop is permitted. Actual comparison success is not claimed by this Source repair.
