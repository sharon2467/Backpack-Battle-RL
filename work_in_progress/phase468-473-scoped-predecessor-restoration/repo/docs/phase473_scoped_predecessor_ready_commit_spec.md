# Phase473 scoped predecessor READY commit

## Requirements
Commit only the exact saved predecessor state after actual469v2 restoration and independent468v2 full physical PASS. Before this final control write, prove the relevant owned parse/native groups and host operation have stopped and acquire the real pool lock. Do not require or claim global process visibility, change permissions, inspect unrelated processes, rerun the game or repeat physical inventories.

## Design
Use pinned saved parse/native process records:each exact spawned PGID has leader_returncode0,live_remaining empty and zombies explicitly not called reaped. The Root host invocation/returned receipt binds the completed command/stdio and return0. Read only /proc/<owned leader/member>/stat for those recorded PIDs, requiring absent or Z; any unreadable/active relevant PID stops READY. System/supervisor gaps remain recorded, not whitelisted into a completeness claim. Snapshot evidence already predates actual restoration; newly assembled targeted observations are labelled with their real time.

Hold the existing .lock with nonblocking flock EX throughout the fresh targeted proof and final state write. Pin the independent readback result/owner/final acceptance, exact unchanged pending state and saved state-image manifest/bytes/mode/mtime. Current state remains failed until this action. The reviewed writer/reader code and actual successful locked branches establish their lock use; the new commit records its own PID/fd/lock inode. No other project/data write is made.

## Realize
verify_evidence(): require actual469v2 target restoration status/statewrites0 and actual468v2 PASS; verify receipt ownership and actual pinned descriptors. Read four saved process records and completed Root host return. Build exact owned leader/zombie PID set from those records, not a guessed system PID list.
commit_locked(): acquire .lock; verify state SHA still matches readback request; record current stat for only owned PIDs, all absent/Z; preserve pending preimage. Reuse frozen phase464 storage.atomic_image with current state preimage to write saved ready bytes; set exact saved mode/mtime and fsync; verify bytes/metadata. Write only new outside-pool receipt. If any proof fails, no READY write. Report scoped proof and global visibility limitation accurately.

## Acceptance Criteria / Tests
Relevant owned writers stopped, Root host returned, current lock held; full physical independent PASS already exists and is not re-executed. Exact oldstate image committed once with metadata, journalled pending image retained; no project/baseline/data/run-evidence change. No privilege/security change, no global-complete assertion and no original/model run. Actual commit receipt is separate from independent restoration evidence and semantic combat admission.
