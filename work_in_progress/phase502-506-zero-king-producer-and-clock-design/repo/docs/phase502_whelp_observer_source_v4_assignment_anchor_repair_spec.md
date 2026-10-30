# Phase502v4 AST assignment-boundary repair

## 1. Requirements

Root explicitly released this repair after the first actual generation stopped in v3. Preserve all v1/v2 compile failures and v3 partial owner `fbab0b34563199e4f9e1ce70f164755073b7ff6e4b64fcc4f7de5e7ccba7eced`. v3 generation1 produced plan/input/authority only, zero observer/schema payloads. No Native/model/schema calls occurred.

## 2. Design

`tests/phase502_prepare_whelp_observer_source_v4.py`, output `data/phase502-whelp-observer-source-v4`. Original implementation SPEC remains the complete business design; v2/v3 repair SPECs retain accurate compile history. New change is only complete-line boundary selection of the unique AST assignment whose target name is requested. VERSION and PROFILE each had two substring matches; all15 exact assignment lines have count1 (static census separately retained).

## 3. Realize

Keep `py_constant` AST target-name uniqueness. Replace the complete AST assignment with its bounding newlines, using the existing strict `Delta.replace` count1 and recorded offsets/inverse. Never widen count or guess a fallback. Bind SPEC/OUT to v4. Compile complete work buffer first; then one new Source generation, cumulative generation2. No other business/source transformation changes. Save complete old→v4 patch and descriptors.

## 4. Acceptance Criteria / Tests

Only Source-generation/compile-only is authorized. On any new actual error preserve and stop. Successful output remains independent503 Source-only pending. Author zero schema imports/helper controls/models/Godot parse/host/Expected/pool/cleanup. Future504 actual nonKing-clock consumer remains separate.
