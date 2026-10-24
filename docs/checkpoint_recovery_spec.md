# GitHub workspace checkpoint recovery

## 1. Requirements

Restore the uploaded file tree using only this clone's `recovery_checkpoint/MANIFEST.json`, its logical JSONL index, numbered archive parts, and host Python standard library. Default `full` materializes every logical file; `active` materializes only predeclared active rows but verifies every archive and every logical row. `--verify-only` performs the same complete byte validation without creating destination. No helper from checkpoint contents, game, Python combat engine, model, training, or network executes. Formal68/candidate75-not-promoted/PAUSED metadata remains evidence, never an execution release. Full physical recovery needs at least12GB; active validation is explicitly not full physical recovery or fresh-OS validation.

## 2. Design

`github-workspace-checkpoint/1`: `archives` maps IDs to `{format,size,sha256,parts:[{path,size,sha256}]}`, with format `compact_zip_tar_xz`, `zip`, or `tar_xz`. Parts paths are relative to recovery_checkpoint. `logical_index={path:'logical-files.jsonl',size,sha256}` authenticates rows `{path,size,sha256,archive,member,mode,active}`; destination paths are canonical relative paths beginning `workspace/`; modes only420/493 and active strict bool. Multiple destination rows may reference one member, with identical source byte identity. All destinations are unique and cannot be file ancestors of other files or links.

`symlinks` is a list of `{path,target,active}`: only root-declared runtime relative links, no pool/project components, targets remain inside destination and must exist as selected regular files/links; cycles/dangling links fail. They are created only after ordinary files verify. Old archive links are never recreated. Archive members may be regular files/directories only. A future format change must be explicit, not guessed.

Flow: validate clone root/no symlink ancestors and manifest/index → join one archive's ordered parts into one fresh temporary directory, checking each part and whole archive → iterate ZIP/tar members, hash all bytes and verify all logical references, writing selected files exclusively → discard joined archive → next archive → physically read selected files twice, set declared mode → create/check whitelisted links → write receiving receipt and relocation map. Compact ZIP opens PAYLOAD.tar.xz as a streaming tar, never writes an uncompressed tar. ZIP members are read to EOF for CRC; controls absent from logical index are still consumed. An error retains any new partial output, never edits/removes sources or claims completion.

## 3. Realize

- `safe_name`, `no_links`, `identity`, `read_json`: canonical paths, no unsafe characters/traversal or symlink ancestors, strict INT identities/lowercase SHA, JSON duplicate/nonfinite rejection.
- `load_contract`: verify schema, archive and part descriptors, pinned logical index, strict logical rows and path collisions; group by archive/member; validate whitelist and its targets lexically. No old workspace lookup.
- `joined_archive`: concatenate only pinned clone-local parts, streaming digest each and whole archive; at most one joined archive in temporary storage.
- `consume`: read a regular member in chunks, hash and optionally tee to selected destinations opened xb, reject size/identity drift; track every expected member exactly once. No contents are imported.
- `scan_archive`: ZIP all members to EOF/CRC; compact exact five outer members with payload tar stream; tar_xz forward-only tar stream. Reject duplicate/unsafe/nonregular archive member paths; directories allowed and never trusted as output destinations. Unindexed regular bytes are still read.
- `restore`: destination must be new with existing real parent; full/active selection only controls physical writes, never validation. Final double-readback matches all selected identities/modes. Links are manifest-only and checked after creation. Receipt includes profile, complete logical verification count, actual physical count, manifest/index identities, PAUSED metadata, zero content executions, and `/workspace`→destination/workspace relocation. Verify-only prints receipt without creating destination.
- `main`: CLI `--destination NEW [--profile full|active] [--verify-only]`; caught failure prints explicit incomplete JSON to stderr and nonzero exit; no automatic retry or cleanup of partial destination.

## 4. Acceptance Criteria / Tests

Compile/static review before tool use. Optional tiny synthetic ZIP/compact/tar fixtures may test full/active/verify-only, source/part/member corruption, unsafe path/duplicate destination/links and existing destination without any engine imports. Actual GitHub archive recovery/remote fresh-clone validation is root-owned later work. Both profiles must verify all parts, whole archives, all logical rows and ZIP CRC; only selected files materialize and each receives two actual reads. Destination/source paths and clone-local dependencies remain independent of old workspace/caches. No pack/push, battle, promotion, training or checkpoint mutation in this implementation task.

SOURCE implementation check: compile passed. Temporary synthetic fixtures covered all three formats, full/active/verify-only, one safe runtime link, unindexed ZIP control reading, and rejection of existing destination, cyclic whitelist and corrupted part. Four synthetic logical files only; zero real checkpoint reads/restores or engine imports. Temporary fixtures were removed automatically.


## Minimal restored entry-point check

`recovery_checkpoint/check_restored.py` reads only the recovered tree, its recovery receipt and host standard library. It verifies formal15 and the paused68/unpromoted75 records. With explicit `--smoke`, it runs the restored CLI exactly once with a payload-read hook allowing only recovered15, its recovered example, stdlib and its own output, then compares the output against the recovered historical receipt after output creation. With `--runtime-version`, it invokes only the bundled editor version entry using restored library paths. It does not start a game battle or training. Outputs and any first failure remain in the new recovery destination.
