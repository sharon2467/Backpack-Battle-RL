# 409 obligation08 setup-only read-scope regression

## 1. Requirements

Root's narrow adjudication retains the original20 API outcomes (7 returns,13 expected rejections), but the original pre_guard/module_loader contract was not fully met:7 runtime stdlib pyc reads and1 absent project pyc lookup were not listed. Preserve all original code, inputs, expectations, allowset and I/O logs. Do not relabel the original scope PASS or repeat the20 API batch. This is one targeted setup-only regression inside original obligation08, with no new family or SUT change.

## 2. Design

Before the measurement observer, preload every actual408 stdlib import and its normal transitives, including traceback and types. Load the sealed setup contract and initialize independent evidence objects before observation. Then independently enforce ordinary/nlink1/unlinked/stable identity and the exact pinned408 size/SHA while reading the original module once with os.open(NO FOLLOW/NONBLOCK) and os.read. There is one pathname open; os.read avoids a second fd-wrapper open. Compile the complete unmodified source bytes with the original absolute filename and execute the complete module into an independent ModuleType with the original __file__. This is not AST/function extraction and does not bypass any operational gate: no public API or main is called.

## 3. Realize

New runner tests/phase409_setup_only408.py receives only its fixed sealed preparation. Preload actual11 imports plus evidence utilities/types before installing the observer. Record all audit events, summarizing bytes by size/SHA and code objects by filename/name. Profile the original source filename to distinguish the single module/class-body execution from public function calls. Measurement ends after module execution and all assertions; subsequent exclusive evidence output writes are a separately labelled sealing phase and are also retained in the event log. Expected measured pathname reads: exactly the pinned original408 module. Expected pyc/data/import events after observation starts: zero. Expected408 API calls: zero. Expected module executions: one additional instance, giving two instances across409.

## 4. Acceptance Criteria / Tests

Seal runner, exact input/expected descriptors, allowed measured path and owner before the single setup execution. Pre/post source identity and size/SHA must match. Measured path opens exactly1, code compile/exec exactly1 each, public408 API calls0, main0, imports0, pyc/data reads0. First mismatch preserves and stops; no retry or relaxed predicate. The final409 report must present original functional evidence and its failed original scope condition alongside this new setup-only closure. Actual12/old engine/schema/model/native and full audit gates remain unexecuted.
