# Phase520 request preparation v2

## 1. Requirements
Complete the same fixed actual029 restoration request; preserve first520 metadata-overconstraint error and empty request outcome. Original508 Source, pending state, backups and evidence are untouched. No restoration, helper/schema/model execution or pool writes.

## 2. Design
Keep the original four-section520 contract. Correct only preparation handling of new journal backups: `phase508_oracle_storage.install`246 writes/fsyncs raw bytes without restoring their source mtime; `select_restore_images`207–210 verifies such images with `metadata=False`. Their physical backup mtime need not equal the original target mtime. The original desired mode/mtime remain explicit authority in journal/previous inventory and are applied by the unchanged writer.

## 3. Realize
Write to new `data/phase508-restore-case029-request-520-v2`. Check all12 actual evidence descriptors and their associations. Controls and old `copy2` patch/marker images retain exact metadata checks; each new journal backup must still be ordinary/stable, exact numeric binding, size/SHA match. Validate journal target metadata against its true reset-time baseline/old-project authority, independently of physical backup metadata; do not force old installed A to equal reset baseline B on overlaps. Command still proposes only the single future Root writer output `data/phase508-restore-case029-first-001`. This fixes no operational Source and grants no READY write.

## 4. Acceptance criteria
New complete actual request and owner, independent narrow review and fresh scoped writer-ended check before Root-only one restore. Preserve old error, disclose two preparation attempts and zero writer/helper/model/Native calls. Any actual missing/inconsistent authority still blocks request. Fresh physical inventory/lock/no-process/action checks remain in unchanged restore, not claimed performed by this author.
