# Phase555 v2 — pre-execution audit finalization repair

## 1. Requirements

Preserve the unexecuted555v1 harness/owner. During static self-review, its new remote-only candidate read guard also applied while a failed import/validation was being finalized, which could reject the host's local metadata-pin aftercheck. No SUT or verifier call occurred. Repair only this reporting lifecycle before execution release.

## 2. Design

The runtime candidate import/validate stages retain exactly the remote-package-only read restriction. In `finally`, after disabling the profile, save the original stage and move to a reporting stage before checking all protocol/package pins. Keep the saved original stage in result.json. This permits only the already-whitelisted host metadata aftercheck, not new paths or candidate execution. Same existing environment/remote clone, no local smoke.

## 3. Realize

New script_v2 and source-v2 plan/pins; same previously unused555 output. Only PLAN/script identities plus the two finalization lines change. Preserve all other function text and package bytes, verifier1/import1/publicvalidate2, noCtor/RNG/run and20/25s budget. Produce full v1→v2 diff, compile-only and pin old v1 owner. Original phase555 package acceptance SPEC still governs; this addendum changes only error reporting scope.

## 4. Acceptance Criteria / Tests

Static exact-diff/compile only now. Future Root-released unique smoke is still the first actual555 attempt. First unexpected error stops and reports original stage, then allowed protocol pin reads seal the failure. No Source/module/manifest/vector change; no candidate calls to prove this preflight issue. All remote reads remain pending Root freshfetch/readback/release.
