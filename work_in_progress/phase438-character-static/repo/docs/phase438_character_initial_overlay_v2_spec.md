# Phase438 Character8 overlay v2 supplement

## 1. Requirements

Apply only the three independent review corrections to the v1 Character8 adapter. Preserve v1 module/context/API/freeze/owner bytes at their existing paths. Implement a separate `tests/phase438_character_initial_overlay_v2.py` and `data/phase438-character-overlay-source-v2/`. The base four-section specification remains the bounded Character8 design, with the following corrections taking precedence. Author may compile but must not import/run either adapter, run controls/tests, create an actual overlay or change the64 Timer gaps.

## 2. Design

Historical `full_reference_counts` remains exactly the original437 `1391DIRECT/6SOURCE_DERIVED/82MISSING`. The v2 projection updates only the pure-combat required counts to `1289/10/64`; it does not produce or label a new full-reference estimate. The original1363 ordered rows,116 excluded objects and two older derived rows are protected by a fixed canonical SHA256 fingerprint of the entire parsed437 audit, in addition to the existing actual-file size/SHA pin.

The second read pass must append actual successful `read_pinned` receipts to a new `after` array and save that array. Before/after refers to whole-file byte/hash reads, including unparsed observer7-input records and unrelated fields in the full facts JSON. Only observer7 checkpoint records at lines1/4 are parsed as records. The facts JSON is syntax-decoded as a whole; business validation reads only `timers.invu:P` and `timers.invu:O`. Report `postcleanup_records_parsed=0`, not a claim of zero physical suffix reads.

Source still binds the815-script/19-scene domain and concrete no-start theorem, without a generic proof boolean. v1 Source files remain available for exact independent comparison. A separate correction receipt documents the earlier MultiTimer method-name correction and reconstructs the pre-correction report/owner under new paths; it does not silently represent reconstructed bytes as an archived original. Old437 is untouched.

## 3. Realize

- `validate_audit(audit)`: retain v1 typed structural validation, then canonicalize the entire object with JSON sorted keys, compact separators, `allow_nan=False`, UTF-8; compare to the literal expected canonical SHA256 computed from original saved437 during Source preparation. Arrays retain order. Return ordinals only after the fixed fingerprint matches. This prevents helper callers changing any row/excluded/old-derived payload while retaining superficial counts.
- `project(audit, records, facts)`: retain eight-target changes and non-target equality assertions; remove v1 `phase437_reference_counts` addition and `full_reference_counts` update. The deepcopied historical full-reference value remains original. No new full-reference estimate is added.
- `run(output_new)`: retain existing literal context/input pin gates; `before=deepcopy(io); after=[]; for pin in before: read_pinned(pin, after)`; require matching descriptor order and save the actual `after`. Record whole-file byte/hash pass counts, checkpoint record parse count/lines, whole-facts JSON syntax decoding versus invu-only business pointers, `postcleanup_records_parsed=0`, and zero EXPECTED file reads. No suffix physical-read count is asserted.
- All other rule functions retain v1 behavior. v2 context references the v2 SPEC and preserves the v1 SPEC as historical design. Source preparation writes API/freeze/owner and a v1 preservation receipt, then calls built-in `compile` on source bytes only. It never executes the returned code object or imports the module.

## 4. Acceptance Criteria / Tests

Independent reviewer should verify the v1 files still match their original owner descriptors; v2 differs only in the three corrections, version paths, and fixed fingerprint constant. Counterexamples include reordering/removing/renaming required keys, changing an excluded object or old-derived typed value while preserving counts, and bool-versus-int mutations; all fail closed against the fixed whole-object fingerprint. A positive helper projection preserves historical full_reference_counts1391/6/82 and required counts become1289/10/64 with exactly8 changed rows. The readback must contain actual successful second-pass receipts and distinguish byte reads from record/business parsing.

Author verification is compile-only. Independent Source/control review is followed separately by one authorized saved overlay, if accepted. Current actual promotions remain0, all64 Timer gaps remain unresolved, and King remains unadmitted.
