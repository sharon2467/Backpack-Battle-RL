# Phase588 — verified historical restore duplicate space

## 1. Requirements
Identify whether `/workspace/checkpoint-validation/physical-phase023-v4-accepted` is still a byte-exact, ordinary-file duplicate of the retained accepted phase023 ZIP. Preserve all live source, original assets, checkpoints, first errors and unique files. Existing user authority permits releasing reliably restore-verified duplicate working copies. This is not permission to remove arbitrary archives or source. No Native program, model, test, restore drill or Library call.

## 2. Design
The historical physical-restore receipt records 1232 files and archive SHA `5ff8634636055f3e50044172a300fae53ff03f86dbbc30e8a7f3440eb00a44b2`. Read the retained `/workspace/checkpoints/python-original-engine-phase023-v4-accepted-current.zip`, verify its full SHA and CRC, compare every ZIP member's SHA/size to the current duplicate tree, and verify the manifest. Require exact sets, ordinary paths, no symlink or hardlink surprises and no active task writer using this historical copy. Save every relative name, hash, size, mode and mtime before any release. Any mismatch or unknown writer means no deletion. Historical successful restoration plus this byte comparison is used; do not repeat restoration or old combat tests.

## 3. Realize
`verify_duplicate()` reads the historical receipt, ZIP central directory, member bytes, manifest and current tree; writes a new proof/owner only under `data/phase588-verified-duplicate-space`. It must not edit the tree or checkpoint. Independent reviewer checks the proof, retained archive and exact proposed target. Root may subsequently release only proof-listed, still-matching files under the exact duplicate root, then remove empty directories; no recursive blind deletion. Check root/ancestor/identity and file stat immediately before removal. Keep both retained ZIP copies and the historical restore receipt. Save an exact release receipt and fresh space; freeing space does not grant Native capture authority.

## 4. Acceptance / Tests
Read-only proof passes only if ZIP SHA/CRC and all 1232 member hashes match, tree has no extras or changed/unknown files, and process evidence shows no relevant active consumer/writer. Independent review is required before removal. A partial or first failure is saved and stops release. This resource operation must not rerun an engine, oracle, INPUT reader, model or previous test. Report actual freed bytes and remaining Native startup margin separately from capture readiness.
