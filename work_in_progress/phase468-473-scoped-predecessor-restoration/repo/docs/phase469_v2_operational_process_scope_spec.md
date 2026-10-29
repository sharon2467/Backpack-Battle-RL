# Phase469 v2: restore the established operational scope

## Requirements

Correct only the new469 global-process-completeness precondition that stopped its first real restoration before any writes. The original accepted c.process_check/check_ready/lease reject readable active references and retain inspection gaps; they do not require permission to inspect every platform supervisor. Do not change permissions/security, whitelist PIDs, claim globally complete inspection, alter the fixed80target recovery or relax any physical/semantic comparison. Preserve v1 and its actual failed attempt.

## Design

A new immutable writer_v2 uses exactly the same fixed case, hashes, lock, source/backup preflight, atomic/metadata/fsync operations, directory ordering, state-preservation and result ownership. Only no_process changes: call the original c.process_check under the same pool lock, explicitly require active_matches empty, keep process_inspection_complete and every gap unchanged, add a truthful scope label. c.process_check itself still raises on any observed active reference. Existing saved spawned parse/native group cleanup records support that those owned groups have no live_remaining; zombies are not called reaped and nonclean native exit is retained. This is existing operational scope, not a proof about unreadable platform processes.

## Realize

Copy the frozen original writer into tests/phase469_restore_fixed_predecessor_v2.py. Replace the one no_process function, record exact diff and AST function conservation; do not modify any other function or source dependency. Compile only, no import or actual filesystem scan. Bind a new request to the new writer SHA only after independent delta review. One Root-controlled actual restoration follows; first error is preserved without automatic retry. Independent468 v2 must use the same stated process scope and retain its complete physical inventory/backup checks; Root commits READY only after its actual PASS.

## Acceptance Criteria / Tests

Only no_process AST Source differs; all other function segments exact. active_matches must still fail and all gap diagnostics remain present without invented complete=true. No PID exclusion, no privilege/network change, no extra game or model. First v1 request/result0writes retained. Independent source review of this narrow change precedes actual v2 restore; full independent physical equality remains required.
