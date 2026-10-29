# Phase448 — Fixed445 output adapter two-boundary v2 repair

## 1. Requirements

Preserve445v1 module/owner, frozen445 eight-section contract,443 candidate,441 input and446 sealed model result. Repair only the independent445 static findings: unknown item idle callbacks must fail before the Source-only no-op filter; Timer API subject native_ref must match declared ID/role/class binding. No model rerun, EXPECTED read, adapter import/call or author controls. Author verification is compile-only; independent reviewer owns controls and actual comparison.

## 2. Design

Copy445 module to `tests/phase448_pure_business_output_v2.py`. Keep all eight projections, profile/ABI/input/source constants and contract identity. In model callback projection, verify string role membership in the78 bound nodes before filtering. Construct exactly41 allowed no-op slots: Game modes0/1 plus39 bound item roles in idle mode1. Foreign `item:FOREIGN` may never disappear via a prefix test. In native Timer API projection, reuse existing `_subject(row,bound)` to validate the exact native_ref four fields and native ID/role/class before matching the requested business Timer role. Do not replace the source predicate with a caller boolean.

## 3. Realize

- `project_model_callbacks(result,bound)`: build exact no-op slot set from bound.items; require78 known string role and strict INT0/1 mode before any filter; filter tuple membership only; retain remaining role/type/order checks and returned rows unchanged.
- `project_native_api(rows,bundle,bound)`: replace the native_id-only comparison with `_subject(row,bound)==name`. Existing helper validates native_ref shape and decode_native binding before returning the canonical bound role. No other function body changes.
- Freeze v2 module, exact v1→v2 patch, two-function AST conservation inventory, context pins and compile-only receipt under `data/phase448-business-output-source-v2`. Old sealed objects stay byte-identical.

## 4. Acceptance Criteria / Tests

Independent reviewer checks only two changed functions. Add negative controls for unknown item idle and unknown Game/role/mode, plus Timer API subject type/extra-or-missing-key/nativeID/role/class drift. Valid exact41 no-op slots and legitimate Timer subject continue to project identically. Existing eight-section semantics and actual446 result remain unchanged. Do not import/run the model again. Any later actual projection mismatch is preserved separately; this Source change makes no actual comparison claim.
