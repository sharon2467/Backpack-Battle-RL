# Phase446 fixed-case Python execution

## 1. Requirements

Run the accepted phase441 fixed-A INPUT bundle once through the isolated candidate after the necessary interface and B1/B2/B5 business gates close. Seal the actual output before independent EXPECTED comparison. Original runs, seed fallback, payload reconstruction from EXPECTED and capture changes are forbidden. Formal75/King status changes only after actual independent acceptance.

## 2. Design

A small stdlib CLI reads the frozen candidate manifest and the exact441 bundle hash, verifies all15 Source files, imports only that candidate, constructs TapeRandom from all365 records, and runs one CombatEngine instance. Existing finite2574 clock records and complete terminal barrier stay authoritative. Source hashes are checked before/after; no new scheduling assumptions or private Timer forcing are added. The independently prepared comparator consumes sealed output later; the runner cannot read EXPECTED/raw capture. A bounded Python audit hook denies capture/other project reads and subprocess/network operations during candidate execution. This is a same-environment offline model test, not a fresh OS test or native generator equivalence.

## 3. Realize

`read_file_pin`: ordinary single-link file; reject size/SHA mismatch. `strict_json`: reject duplicate keys and NaN/Infinity. `verify_candidate`: exact15 Source entries, unique paths within frozen staged root, hashes unchanged. `main`: create new output directory, retain before manifest; install bounded I/O hook; import exact native_replay_v8 engine/randomness; TapeRandom(all records); CombatEngine(fixture,tape,runtime); run(default120-second simulated ceiling); assert tape exhausted; save actual result and Source/input/run statistics, then hash seal. If an exception occurs, save traceback and available same-instance partial events/Timer/state/Tape position without another run. No automatic retry. Require candidate/source/control closure to have been independently assessed before invoking this CLI; the script itself does not manufacture a gameplay certificate.

## 4. Acceptance Criteria / Tests

Exactly one full engine.run per actual invocation; constructor/prepare activity reported separately from prior interface controls. Complete Tape.assert_consumed and finite driver result required. Whole output bytes sealed before comparator opens EXPECTED. Genuine differences remain failures and preserve first artifacts; fixes get a new immutable candidate and bounded regression. Runner preflight is Source review/compile only; do not run a fake battle or replay passed old core tests merely to test the runner.
