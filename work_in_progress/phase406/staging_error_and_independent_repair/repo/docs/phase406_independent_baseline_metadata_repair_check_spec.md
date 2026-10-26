# Independent baseline metadata repair verification

## 1. Requirements

Use the genuine Root readonly release d9d8768ef645a825a8d6bee23ed1859c0f2b1223448ec8159f711bad21e26291 to verify the complete baseline after Root's metadata repair. Maximum one real public398 inventory(root,exclude=(),relaxed=False) call. Do not call main, prepare_contract or any operational recovery/physical-reader entry. No pool write, capture12/business/schema/Engine/model/native/restore/READY operation.

## 2. Design

First physically pin the exact reader module and its actual inventory definition/dependency helper, the release, real before/repair records, authoritative attempt06 compaction baseline manifest and Git outer CAPSULE manifest. Associate the outer manifest's run/output/compaction/baseline-files.json row with the authoritative bytes; no archive extraction or remote Git action. Root's already verified Git provenance is retained distinctly from this byte association.

Invoke the unchanged full module's inventory once, excluding nothing and relaxed=False. Compare every path/kind/size/SHA/mode/mtime and directory row to the archived baseline manifest:15418 files,247 directories,616167851 file bytes. Preserve the actual inventory and exact first discrepancy/trace. The original13 target files are11 GD plus2 scenes; compare their actual inventory rows to archived targets and correlate current inode/mode/mtime/ctime metadata with Root's before/repair records. Do not claim they were never rewritten, or historical ctime/atime were recovered.

## 3. Realize

Seal a concrete runner, API/source binding, input descriptors, expected counts and readallowset before import/call. Use bytecode-disabled import of the actual398 module, no algorithm copying/AST execution/patching. The module's other functions stay uncalled; record real FSchecker calls separately from old full physical-reader or business SUT execution. Guard operations to baseline read-only, exact authority/SOURCE metadata and owned output; forbid subprocess/network/mutation outside output. Record exact launcher args/stdout/stderr/elapsed/exit and module pre/post pin.

The one inventory result supplies all content hashes; supplementary13 lstat observations compare postrepair identity metadata without rereading content. No second inventory is run for reporting. A true inventory or association discrepancy stops and is sealed without automatic retry. The report records atime as observable read metadata that may change and ctime as current/postrepair metadata only. First failure retains all produced evidence; success seals report and ordinary owner, then stops.

## 4. Acceptance Criteria

PASS requires complete manifest equality, exact expected counts/bytes, correct Git outer descriptor association and all13 targets agreeing in content/size/mode/mtime with historical targets and inode with Root before records. Recorded ctime may agree with Root's postrepair record but is never labelled historical. Result is only a baseline metadata-repair check, not another398 recovery/full physical regression,407 rerun, input admission or source/model acceptance.
