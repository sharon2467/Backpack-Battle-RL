# Phase495 experimental descriptor writeback repair

## 1. Requirements

Fix494's real Source metadata failure in a new immutable15-file copy of493 at `data/phase495-experimental-descriptor-repair/staged`. Preserve493 and494 first-error artifacts unchanged. Only headless.py may differ, only `initialize_experimental_nonking`: write its descriptive metadata to the actual newly created instance's private `_initialization`, not the deepcopy getter. Fourteen modules, all other functions, business/entry domains/old APIs remain exact. Author compile-only; no imports/tests/model/native/EXPECTED/pool/public writes.

## 2. Design

`HeadlessBattle.__init__` owns a deepcopy in `_initialization`; public `initialization` returns a further deepcopy.493's `battle.initialization.update(...)` mutated a temporary object and lost Source extension identity.494 stopped after one real constructor/prepare/activation at its metadata assertion, before unit effects/full run/natural; earlier ingress checks passed. That result is preserved, not rerun by the author.

The module itself creates `battle` through the unchanged validated `_initialize_fixture`. Change just the receiver of its subsequent update to `battle._initialization`. Do not weaken the public getter's defensive-copy behavior, change common factory or move gameplay, or add state/readiness flags. `_result_view` will then read the existing correct getter and detect the actual explicit Source entry as originally intended.

## 3. Realize

Verify493 source freeze15 and copy into the new directory. In the exact function `initialize_experimental_nonking`, require one `battle.initialization.update(` anchor and replace it with `battle._initialization.update(`. No other textual edits. Compile15 actual files with built-in compile/discard/no import or pyc. Assert fourteen files exact, engine.py exact, exactly one existing function changed, and the old/new entire headless bytes differ only by this one replacement. Keep HeadlessBattle.initialization and all old/new entry validation/helper bodies exact.

Write one-line source patch, conservation/compile receipts, API/source context,15-file freeze and owner. Pin original494 first-error as the real reason. Restore no counters, don't fabricate successful runtime results or recompute bundles.

## 4. Acceptance Criteria / Tests

Author static criteria:15 syntax passes;1 changed module/14 exact;1 changed function; one receiver substitution; all algorithms/gates/deepcopy protection exact;0runtime execution. Independent Astra decides the minimal remaining controls/continuation using preserved494 prefix rather than automatically rerunning passed ingress. It must check actual201-only and mixed entry descriptor/result identity, then the already planned business controls and at most the presealed Source natural case under Root's bounded authorization. No new native/EXPECTED or old battle rerun. Functional acceptance belongs to the independent role, not this compile-only repair.
