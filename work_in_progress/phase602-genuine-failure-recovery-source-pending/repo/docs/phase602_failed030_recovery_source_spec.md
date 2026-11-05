# 602 — fixed failed030 recovery Source implementation

## 1. Requirements

Implement the accepted601 design and its bound addendum, under Root602 release
3b0da2995547de245ac926b4c6cfe9d322e1a64f28b3ccfcd48d731324ffd056.
Generate once and compile at most three isolated modules. No production import,
helper test, pool read/write, restore, readback, Original or Expected operation.
Keep590 and all600/601 artifacts immutable. The actual failed state remains246B,
SHA698998f49b9bbe4dba03693016c3b35aca6d7a7129278aa187a77ba5ad7bc6ed.
Never write PENDING or READY. New operational requests require separate Root
authorization; this Source generation is not that authorization.

## 2. Design

Create `tests/phase602_failed030_restore_predecessor.py`,
`tests/phase602_failed030_independent_readback.py` and one shared pure predicate
`tests/phase602_failed030_binding.py`. The pair are narrow590 copies; only failed
state association and explicit new namespace/source metadata change. Original590
host freeze remains the installed-source authority. A separate602 freeze pins
the new pair, predicate, original590 preimages and actual Root authority metadata;
no self-hash appears inside a module or frozen authority owner.

The fixed dependency dictionary pins601authority/owner/copied failed bytes,
600owner/invocation/execution/first-error/release and597config/owner. Config is
actually owned by597, not600.600release.config and invocation argv bind that same
config. No capsule added after the601authority owner was frozen is used.
Both new programs load the hash-pinned predicate and fixed metadata using their
existing ordinary stable descriptor reader. Reader audit scope adds only these
explicit fixed Source/metadata paths. The common predicate is pure; no filesystem,
process, imports or user-selected path resolution occurs within it.

Keep request shapes7/9 and evidence12/8. The old `pending_state` slot contains the
actual failed bytes. Under the original exclusive lock, exact state identity,
mode/mtime and four-key value must match fixed authority; authority ownership,
600failed reaped execution and source/config chain must match. Existing controls
checks produce saved ready image0; its run, controls.previous_run and requested
PREVIOUS must equal the actual027attempt06. Source-specific authority descriptors
also bind all12 writer evidence, or six common reader evidence. Reader's two
restore result descriptors retain their original actual-owner check.

## 3. Realize

* `validate_failure_association(materials,state_image,controls,saved_ready,
  evidence,previous,role)` is the only shared pure algorithm. Fixed materials
  keys and reference descriptor constants are closed. Validate owned601authority
  and saved failed bytes; execution/invocation/first-error/release are owned600;
  config owned597. Require exact fixed schema/case/run/pool/previous and exact
  nonretry failed execution. Require strict typed state metadata and exact value;
  no booleans accepted as integer counters. Bind all evidence of the appropriate
  role and controls' three images plus saved ready state. Return small immutable
  provenance descriptors for the result; never a caller-supplied certificate.
* The same small `failure_association` adapter in both modules loads pinned pure
  Source and metadata, calls the predicate, and records its provenance. Loading
  happens only during separately authorized operational execution, not generation.
* writer `prepare`: remove only the original fixed PENDING/previous/control-field
  assertions. After unchanged saved-state image validation, invoke the shared
  predicate with `stable(POOL/'state.json')`. Preserve original raw evidence
  reads, process check, current inventory and all later safeguards.
* reader `readback`: remove only corresponding lock-held PENDING assertions.
  After unchanged saved-state validation, invoke the same predicate with actual
  locked state. Keep lock re-read/evidence equality, physical inventory/process
  and final unchanged-state proof.
* `main` changes only request/result/output/module namespaces and reader explicit
  Source-read scope. Shared predicate/metadata descriptors are checked on loading;
  original operational kernels do not acquire new behavior. `validate_request`
  uses the new request schema while preserving its7-key and12-path checks.
* All `select_restore_images`, `apply`, `restore`, stable/ordinary/atomic helpers,
  process checks and directory/metadata algorithms remain exact. Entire files
  reverse through recorded replacement spans to their exact590 preimages.

Generate candidate strings in one preparer, compile all three without exec/import,
write full inverse spans, function census/conservation, source freeze/API and
owner. On first error preserve partials/error/owner and stop; never retry or lower
a strict replacement count. No operational requests are generated here.

## 4. Acceptance

Author checks only compile/static Source hashes and exact inverse/function
conservation. Independent review/at most six pure association vectors follow a
separate Root release. Real restoration and independent readback remain separate,
with fresh unchanged lock/process/currentgraph/preimage gates. State writes stay0;
RootREADY only after independent actual fullphysical PASS.
