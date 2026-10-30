# Phase514 harness v3: relative schema Source path

## 1. Requirements
Preserve v1/v2, the sole actual first-001 result and its independent finding75ff76f6. The production loader successfully returned once; the first case failed only in a test-owned path assertion. Prepare a minimal immutable repair, without running it. No production Source or vector change, no additional helper families, no full projection/record/model/Native/Expected/pool calls.

## 2. Design
The production loader deliberately assigns its repo-relative pinned schema path to module.__file__ and to compile's filename. Resolve that metadata relative to the production bridge.REPO when non-absolute, then compare against the exact pinned schema path. Do not resolve relative to the fresh process cwd. Include both the pinned absolute schema filename and the actual relative compile filename in profile watching, retaining original filename keys in recorded counts.

## 3. Realize
Create tests/phase514_independent_helper_controls_v3.py from v2. Change SOURCE to the new v3 pins directory and OUTPUT to a new v3-001 directory. In main, add the literal relative schema filename to watched. Replace only the schema path postcheck with production-REPO resolution and exact path equality. Keep all other statements/functions, input vectors, calls, predicates and audit allowlist behavior unchanged. Save exact diff, inverse/preservation statement, pins and compile-only evidence. No probe, import or main invocation during preparation.

## 4. Acceptance Criteria / Tests
Static byte comparison confirms only these declared edits. All v1/v2 and first-result/finding owner payloads remain exact. The v3 future batch remains at most12 top-level calls in one fresh process with15-second external wall cap: one loader and the11 previously unentered helper cases. Because the prior process ended, a new loader is necessary; cumulative attempted top-level calls are at most13 and schema loads at most2. First loader success remains recorded while its case was not accepted. Nested schema entries will now be counted under their original relative filename key. Root must separately release the exact frozen v3 before execution; first unexpected error still stops and preserves without retry.
