# Phase375 readback metadata handoff

## Requirements
Preserve the successful unique actual readback and its original review/owner. The frozen checker mechanically changed lowercase phase wires but left uppercase370 status literals. Correct only the new handoff status to375; no physical scan/recovery/READY/process rerun.

## Design
A new output-only finalizer reads and hashes the sealed repo results, authorization, receipt, map and final SOURCE descriptors. It verifies the original no-failure readback and exact375 bindings. It copies all actual observations and target descriptors verbatim, records original status and precise metadata error, and publishes a separate375 handoff review.

## Realize
`tests/phase375_finalize_readback_metadata.py` verifies every original owner leaf before/after. It checks original review source_freeze and restore_map equal376 Root authorization/receipt, receipt targets and failedstate equal observed review, three exact tree flags true, failed evidence and overlay flags true, no known task live, and all execution counters zero. Only the status field changes; metadata provenance is appended. It owns actual manifests directly with repo-relative descriptors and does not read any external pool/run path.

## Acceptance Criteria / Tests
One metadata-only execution, zero inventory/restore/READY/Game/model/projection. Original review/owner/source remain byte-identical. New review states original uppercase-status error, genuine375 source and one actual readback. Every new owner leaf is hashed back. Failure preserves first metadata error without rerunning the successful physical readback.
