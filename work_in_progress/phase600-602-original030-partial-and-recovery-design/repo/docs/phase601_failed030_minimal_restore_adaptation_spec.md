# 601 — failed030 files-only recovery adaptation (design only)

## 1. Requirements

600 stopped once: host PID1188 reaped, exit1, no automatic retry. The complete-capture branch was not reached. Parent reports parse clean/exit0, Native exit2, selected-hook durable failure, capture_complete=false and missing validation/terminal. Twelve filenames existing does not admit an INPUT build. Preserve the failed run, all backups, zombies/diagnostics and the first error. No new Original attempt, Source implementation, helper import, pool write, PENDING fabrication or READY commit is authorized here.

The actual state reported by Root is exactly four keys {status,run,reason,utc}, status failed, fixed run030, reason `RuntimeError('first original030 failed/partial; preserve, no retry')`. This is a different legitimate failure shape from the success path's PENDING state. Root will pin its actual bytes and metadata in an owned snapshot. This design does not invent that descriptor or claim independently reading the pool.

## 2. Design

Keep the same fixed case/run and the existing seven-key restoration request, twelve evidence keys, nine-key readback request and eight evidence keys. The historically named `pending_state` evidence slot carries the actual unchanged failed state; naming does not require or permit rewriting it. Add a fixed Source-bound FAILURE_AUTHORITY descriptor for Root's forthcoming owned600 snapshot, and its owner; not a caller boolean, optional fallback or arbitrary status whitelist. This authority must bind actual state descriptor/metadata, fixed run, owned600 invocation/execution/first-error, the exact controls/old-patch/new-journal/pool-before descriptors, and the saved state image. If any binding is absent or inconsistent, fail before writes. No snapshot is currently assumed to exist.

Read association under the existing exclusive lock: exact failed bytes and four-key shape match the fixed Root-owned snapshot; invocation is the one fixed --execute with accepted config and execution is reaped/exit1. Controls are owned by that run and its snapshotted descriptor agrees with the twelve/eight evidence. The controls manifest's previous_run and image0 ready state's run must agree with requested PREVIOUS, which must be distinct from030 and under the fixed runs root. This uses preserved pre-busy bytes, never current failed-state nonexistent previous_run/control_preimages fields. Root reports previous027attempt06; executable binding still comes from actual controls and saved state, not this prose.

Do not infer capture completion or archive availability. The run030 need not have its own compaction archive. Existing prior-run compaction, complete79 journal, pool-before graph and original backups remain mandatory. Partial journal, changed graph, missing original images, active process or unknown directory topology still reject. Selection O union N union F, absence semantics, overlapping authorities, atomic file writes, mode/mtime restoration, directory metadata, process scope, lock lifetime and unchanged-state comparisons remain exactly the accepted590 code.

The independent reader substitutes the same fixed failure association under its lock and retains full physical comparison with the prior bundle, saved controls, evidence/source after checks and process checks. It does not treat writer success content as physical proof. Both programs leave this exact failed state unchanged; only Root may separately commit the saved ready bytes/metadata after independent actual readback PASS. No Source-only review or synthetic control authorizes restore or READY.

## 3. Realize — exact function surface

Future isolated filenames/namespace are assigned on Root implementation release;590 files remain immutable.

* writer `validate_request` (590 lines120–140): only new writer/source namespace bindings as required. Keep seven request keys and twelve fixed evidence paths; typed authorization remains strict true only on an actual Root request. Fixed FAILURE_AUTHORITY is Source identity, not caller-selected evidence.
* writer `prepare` (227–354): replace only lines231–235 fixed PENDING checks and nonexistent-field association. Call a small failure-association predicate with decoded actual state, fixed Root snapshot, controls descriptor/manifest and saved state; pin/recheck actual raw state as before. Existing controls validation at239–259 already checks three-image order, metadata and saved ready-state run. Reuse that code, moving the new final association after saved_state is available; perform only readonly checks before it. Existing process check stays before live inventory/writes.
* writer `restore` (422–446), `select_restore_images` (189–224), `apply` (377–419) and all physical helpers: body-exact. Source/result schema and output-prefix strings may be mechanically rebound only if needed, with every such delta listed; do not alter a shared body just to rename historical messages.
* reader `readback` (120–306): replace only lock-held lines175–182 failed/PENDING and absent previous/control assertions with the same fixed authority semantics. Existing controls/saved-state validation at189–212 remains. Keep all fullinventory, locks, process checks, metadata and evidence after checks exact. `main` only new Source/output namespace bindings if required.
* future freeze includes old590 preimages,600 owner/owned invocation/error, actual Root snapshot/owner and its exact linked descriptors. Unknown actual SHA remains unbound and blocks implementation freeze/operational request; do not substitute an empty value or None equality. A new case-specific authority predicate may be shared within the isolated recovery pair without importing host or introducing a generalized recovery framework.

No writer/reader generation or execution occurs in601. Source pins and function preimages below are static data, not kernel reacceptance.

## 4. Acceptance / finite controls

Independent design review first. If Root releases implementation, compile/static diff must show only the fixed failure-state association and mechanical identities changed; selector/apply/storage/lock/process/metadata/inventory bodies exact. At most six pure association vectors: (1) exact owned failure + controls + saved027 accepted; (2) changed state SHA or extra/missing state key rejected; (3) wrong run/reason/type rejected; (4) missing/incorrect snapshot ownership or execute association rejected; (5) controls descriptor/previous/saved-state mismatch rejected; (6) PENDING/READY or another failure rejected by this narrow branch. Production must call the tested predicate. These are synthetic code tests, not live restore proof. Actual Root restore and independent full readback require separate calls and retain zero state writes.

### Appendix — hook failure, localization only

Frozen after-source ThornShortbow.gd has entry and leave for `Items/Exclusive/ThornShortbow.gd::onDealtDamage`. Frozen sink has107 SITES and this exact site is absent. `source_observable`1375–1388, once fixture-bound, calls fail SOURCE_UNKNOWN_SELECTED_HOOK for a selected object's unknown site. This matches Root's sequence4906 report. Host execute287 raises before archive/PENDING when complete is false; no durable capture completeness can be inferred. No hook repair, matrix expansion, new capture, gameplay inference or UI/72 review is part of recovery601.
