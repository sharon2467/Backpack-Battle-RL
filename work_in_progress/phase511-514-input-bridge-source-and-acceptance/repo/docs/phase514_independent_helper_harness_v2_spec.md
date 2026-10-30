# Phase514 harness v2: pre-audit argparse dependency

## 1. Requirements
Preserve the sealed, unexecuted v1 harness and owner. Root identified a deterministic dependency omission: the reviewed bridge imports argparse, but v1 installed its restricted open audit before explicitly loading that standard-library dependency. Do not rely on a fresh process already having argparse loaded. No Source predicate, vector, case count or read allowlist may be relaxed. No actual import, probe, controls or projection is authorized by this repair.

## 2. Design
Create an immutable v2 harness with an explicit top-level `import argparse`, before installing the audit hook. This lets the normal interpreter load argparse and its own standard-library dependencies before the restricted candidate phase. Retain the existing exact pinned Source/output read scope; do not allow arbitrary standard-library file reads after audit. Change only the harness's SOURCE directory binding to the new v2 pins directory. Keep the never-used output directory and the existing vector bytes unchanged.

## 3. Realize
Copy the v1 script to `tests/phase514_independent_helper_controls_v2.py`; insert `import argparse` immediately before `import collections`, and point SOURCE to `data/phase514-independent-control-source-v2`. All function bodies remain byte-exact. The v2 pins replace only the harness descriptor and add this repair SPEC; the existing vector, production bridge/initial/schema, context/ABI, source owner/freeze, original SPEC and static review descriptors are retained. Save a complete two-edit diff, preservation receipt and compile-only result. AST inspection verifies the dependency is explicitly imported before `main` can install audit; do not execute any module to check it.

## 4. Acceptance Criteria / Tests
Static checks: v1 owner and every payload remain exact; v2 minus the argparse import and SOURCE directory substitution equals v1 byte-for-byte; all function source segments remain identical; vectors and12 top-level calls unchanged. Discarded compile-only check is permitted. Runtime imports/calls/projection remain0; Root must separately release v2. The planned batch still has one process,15-second external cap, one schema load,5 positive and7 rejection cases, and stops at the first unexpected error. This repairs a harness preparation issue, not a production Source defect or an observed test failure.
