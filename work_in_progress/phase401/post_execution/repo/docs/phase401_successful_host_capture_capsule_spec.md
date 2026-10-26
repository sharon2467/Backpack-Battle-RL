# 401 byte-preserving host-complete capsule

## 1. Requirements

Preserve the actual fixed06 run and Root execution controls as a standalone small compressed checkpoint. Host reports capture_complete; independent402 control acceptance is still pending. Do not parse expected business semantics, modify the successful run, execute archived code, repeat a battle, or claim model/King admission. Preserve full dedicated run data/output/user contents, including raw observations and journals. Baseline/engine remain referenced main-checkpoint resources, not another Game copy.

## 2. Design

Create a new external checkpoint directory and one ZIP with all ordinary single-link run leaves under run/ and Root401 controls under root-control/, plus docs/wrapper provenance under repo/. Reject linked/nonregular leaves. CAPSULE.json records exact member size/SHA/mode/mtime_ns, source roots as provenance only, directory metadata, and independent status PENDING. ZIP stores bytes; manifest retains subsecond timestamps. No source payload is extracted or executed. A final full CRC/member SHA and source rehash verifies that archive and retained sources agree. Capsule SHA/size is written in a separate receipt after close. Stop on first error and retain artifacts; no auto retry.

## 3. Realize

`tests/phase401_archive_host_capture.py::snapshot(root,prefix)` walks one declared existing root, rejects aliases, records canonical directory metadata and each streamed file descriptor plus source path. `digest(path)` streams SHA256. `main()` verifies actual Root execute exit0 and host-complete status, snapshots only fixed06 and Root401, adds the exact four provenance files, exclusively creates ZIP, writes manifest and each source member, checks CRC and every archived digest, rehashes all original sources, then writes exact capsule receipt. It requires a fresh destination. Output remains outside run so successful retained identity is not mutated. Normal branch upload uses capsule only, avoiding the148MB raw observation Git single-file limit.

## 4. Acceptance Criteria / Tests

All files and directory metadata recorded, no aliases; complete ZIP CRC and every size/SHA matches source; source postchecks unchanged. Receipt binds capsule SHA/size/member count and explicitly pending independent402, models/inputbuilds0/Kingfalse. Bounded recursive secret scan precedes Git push; if it finds a secret, block upload and report the actual excluded member. Same-executor byte validation is not fresh-OS or full Python comparison. Remote fetch must verify capsule bytes and manifest leaves; no old cloud file is the sole copy of new raw capture.
