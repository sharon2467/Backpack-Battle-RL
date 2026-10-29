# Phase444 remaining interface harness v3

## 1. Requirements

Preserve both failed batches and both frozen harness versions. Root authorizes one third remaining-only batch after two harness-budget failures, without replaying the earlier 19 passed checks. Keep the 35-second budget and unchanged pending interface assertions. No battle, frame progression, original capture, EXPECTED or old tests.

## 2. Design

The v2 failure stack reached the harness's indented Python JSON encoder under sys.profile. This is a harness bottleneck, not evidence of candidate nontermination. Change only fingerprint encoding/profiling overhead. Keep the exact v2 stored-state graph coverage. During stored-state traversal/encoding, suspend sys.profile and restore its previous callback in finally. During every model getter/control invocation the model profile remains active. Encode the fingerprint with compact JSON (no indent). Do not enlarge the budget.

## 3. Realize

`state_digest`: save current profile; disable; traverse unchanged model state; compact-encode/hash; record node count, byte count and elapsed time; restore previous profile in finally, including errors. The fingerprint statistics are test-harness globals, not model state. `profile`: test cached source ownership before accessing frame locals on unrelated stdlib frames. All model/component call counters and forbidden-entry guards remain.

Use unique source-v3/remaining-v3-first-001 directories. Compile-only and inspect the exact source diff/profile lifecycle before one actual invocation. If another timeout occurs, preserve completed fingerprint sizes/timings and its traceback; no further automatic retry. Keep all previous limits and synthetic local cleanup labeling.

## 4. Acceptance Criteria / Tests

One construct, one prepare, local history/Timer wrappers, one synthetic finish and read-only snapshots pass within 35 seconds; zero activation, primitive draws, frame passes and full runs. Source/input pins and audit stay strict. The two earlier failures remain harness failures. No narrowing of state comparison, no model acceptance/King admission, and no assertion of B1/B5 closure.
