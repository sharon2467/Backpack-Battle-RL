# Phase468 v2 bounded operational process guard

## 1. Requirements

Root explicitly approves an immutable correction to the original468 reader's overbroad process predicate. Preserve original468 Source, its owner, the469 zero-write failure and the independent scope assessment. This block writes and compiles Source only; no import, reader, restore, process scan, pool access, native or model invocation.

## 2. Design

The accepted operational domain uses the same exclusive pool lock and original c.process_check, which rejects readable active pool references and returns visibility gaps honestly. It does not require every system/supervisor PID's cwd/fd/maps to be readable. Platform PermissionError is real and remains reported; no permission/safety setting changes, PID exemptions or global absence claims are introduced.

Existing saved parse/native monitor records and their limitations are bound in data/phase469-independent-process-scope-assessment/review.json. They show completed leaders and no recorded live remaining member in their own spawned groups, with zombies retained as not reaped. Native wrapper process_clean_exit=false remains false. This historical scoped evidence is not a proof of all platform processes or arbitrary detached descendants. No new monitor framework or runtime decoding is added by v2.

## 3. Realize

Copy tests/phase468_independent_predecessor_readback.py to tests/phase468_independent_predecessor_readback_v2.py. Change only the nested no_process block in readback: keep c.process_check(pool), require active_matches==[], retain all returned fields including inspection_gaps and process_inspection_complete, then add operational_scope='original-readable-reference-check-with-exclusive-pool-lock/1' and global_process_completeness_claimed=False. The original checker still raises on an observed active reference. Existing before/after calls remain under the same readonly-opened exclusive flock.

All other Source bytes remain exact. CLI/config, paths, full baseline/project/staged/directory/retained/driver/bundle/provenance/preimage validation, failure handling and no-READY policy remain unchanged. The script uses __file__ for its own identity, so no other Source binding edit is needed. Compile once without import. Seal the exact diff, conservation and owner; Root reviews before any separately released actual readback.

## 4. Acceptance Criteria / Tests

Static inverse restores the complete original468 bytes; only readback's nested guard differs and all other top-level function segments are byte-identical. No assignments clear gaps or change process_inspection_complete. The new flags explicitly identify bounded operational acceptance and deny a global completeness claim. Actual physical-readback PASS and Root READY commit remain pending. Business eight-section comparison standards and every full-inventory/restoration requirement are unchanged. No synthetic process fixtures or old tests are run.
