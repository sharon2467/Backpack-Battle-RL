# Phase523 actual independent predecessor readback request

## 1. Requirements
Prepare the exact actual reader request after Root's single files-only restore PASS. Unchanged reader `tests/phase508_independent_predecessor_readback.py` is not invoked by this author. No helper/program/schema/test/model calls, pool writes, READY commit or business Expected decoding. Do not repeat earlier75oldpatch/79journal/backups/resource checks. Preserve pending state and all Source/evidence.

## 2. Design
Use the existing nine-key `phase508-fixed-predecessor-readback-request/1` schema. Run029, pool, baseline and actual previous027-attempt06 are distinct fixed absolute roots; relocations remain empty. Pin unchanged508hostfreeze. Evidence is exactly eight descriptors: actual restore receipt/owner, controls manifest, patch inventory, install journal, previous proof, previous bundle manifest and current pending state. The writer's success receipt is restoration provenance, not a substitute for the upcoming independent physical proof.

Current state must still be failed/PENDING with SHAae802c882579aab2306d98f4f66b1d409006343aae15764a54a8c4a249e70191. Writer receipt must be actual bd7e282ae0153e031dbea5710996baa609335d55f862d94c4e51e8dca8a3eab8, owned by its actual output owner, and name the same run/previous/pool with zero state/READY writes. The receipt's state_unchanged and actual pending/control association are checked from small metadata only. Raw-hash inventories/journal; no full inventory traversal or replay of prior preparation checks.

## 3. Realize (fixed protocol, no Source modifications)

* Preparation-only stable reads: no linked ancestor; ordinary single-link file; unchanged stat while hashing. Decode only the actual restore result/owner, pending state and controls manifest. Hash the other four authority leaves without semantic traversal.
* Build exact fields `schema,case_id,run,pool,baseline,previous_run,relocations,host_source_freeze,evidence`. Each evidence row is exact path/size/SHA. No extra authorization flag or optional evidence. Verify owner covers exactly the selected receipt descriptor. Baseline root stays the original task path, never written.
* Freeze `readback-request.json`, `commands-for-independent-root.json`, scoped preparation receipt and owner under new `data/phase523-fixed029-independent-readback-request`.
* Proposed command: `python -B tests/phase508_independent_predecessor_readback.py --config ABS_REQUEST --config-sha256 SHA --output-new ABS_REPO/data/phase508-readback-case029-first-001`. The output path must be new. The author does not execute this command or acquire its readonly flock.
* Future independent `readback()` validates current evidence again under its single flock, actual scoped process state, complete physical inventory and retained evidence/backups against old authorities. Existing300s deadline and its Source audit remain unchanged. First error stops, records evidence and blocks READY; no retry/weakening here.
* On independent PASS only, Root separately decides exact saved pre-busy state restoration. Neither current request nor reader permits READY writes; this phase claims no independent result before it exists.

## 4. Acceptance criteria
Exactly eight actual descriptor rows and nine top-level fields, owned actual writer result, unchanged pending association and accepted exact Source identities. No null/future result/prepopulated success, no skipped authority. Source files unchanged, author zero imports/compile/readback/restore/poolwrites/Expected business reads. Root/Astra receive the frozen request and complete argv; they coordinate the single independent full readback. Formal75/Native-family/model acceptance unchanged; quota unknown and trusted<=30/userpause remains stop boundary.
