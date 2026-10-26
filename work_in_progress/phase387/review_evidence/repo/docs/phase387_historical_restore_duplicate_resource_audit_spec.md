# 387 historical restore working-copy resource audit

## 1. Requirements

Read-only inventory `data/compact-handover-validation/v2-full1801-first-001`, especially `restored-v5`. Identify only exact-byte derived recovery working files that can be reconstructed from the already verified Git checkpoint at fdefd611a46eb67f03e88658bc740034043c1fc1. No removal, move, source/evidence edit, archive materialization, Game/Godot/model, or business expected interpretation. Root alone decides any later cleanup. Preserve original reports, unique evidence, all243/343/347/354 archives, source/pool and redacted/private mismatches.

## 2. Design

Inventory paths/types/sizes/allocated bytes and stream SHA256 for ordinary candidate files without following links. Exact recovery identity is `(size,sha256)`, supported by Git logical index + MANIFEST archive/parts/member mapping and existing remote restore receipts. A match is a restoration working duplicate only when local provenance places it below the derived restored tree; adjacent reports are retained. No approximate source equivalence or sanitized-original equivalence counts.

Inspect current380 combined freeze143 and four bindings,382 final394,384 source19 and actual18 owners for exact path dependencies into this tree. Resolve descriptor strings and absolute/relative paths conservatively; exclude dependency-bound candidates. Record symlink/hardlink/type uncertainty and unmatched/ambiguous restoration mappings separately. Archive bytes remain untouched; metadata listing/stream hashing are permitted, no extraction.

## 3. Realize

1. Read current repo instructions and source restoration metadata; freeze this SPEC before inventory.
2. `inventory(root)`: lstat each entry, collect relative path/kind/mode/size/blocks/nlink and ordinary-file SHA with before/after stat stability. Never emit file contents or private values.
3. `load_recovery_sources()`: verify current Git commit and exact Git blob identities for MANIFEST/logical index and existing verification receipts. Build identity-to-logical-row lookup and archive/part provenance. Confirm referenced original local checkpoint size/SHA against manifest; inspect compact wrapper listing only when required for exact member path.
4. `dependency_scan()`: actual read/hash pinned current owners/freezes/bindings, inspect their path fields and source references for the candidate tree; exclude any direct or conservatively unresolved dependency.
5. `classify()`: only derived, ordinary, stable, nonhardlinked files with exact reconstructible mapping and no current dependency become proposed candidates. Every other entry stays retained with a reason. Sum logical bytes and actual allocated bytes distinctly; no promise that deletion has occurred or future free space is fixed.
6. Write small new387 JSON inventory/mapping/exclusion/summary and owner. Read all output leaves back. Stop without mutation of the inspected tree.

## 4. Acceptance Criteria / Tests

Each proposed file has its actual size/SHA, original derived path, exact Git path/commit, archive id/format/size/SHA, part descriptors, and member. The report identifies existing remote verification scope without claiming a fresh restore. Current protected evidence references have no excluded dependency among proposed files. Totals reconcile with inventory, unmatched and private/sanitized mismatches are retained, originals and archives remain unchanged, and all actual cleanup/native/model counts are zero. Any unavailable provenance produces a concrete retained/BLOCKED reason rather than a guessed recovery route.
