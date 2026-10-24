# Self-contained engineering recovery checkpoint

This directory is the complete **GitHub-hosted recovery route**, not just the small Python demonstration. It contains the received original game code/resources/imports, the complete 243 base and support, the complete 343 work overlay, the final 347 pause metadata, fixed Linux runtime/dependency artifacts, and a standard-library restore tool. No Library file, old cloud workspace, old cache, or external checkpoint is needed to obtain the engineering files.

The implementation remains paused: **formal68; candidate75 independently accepted but not promoted**. Restoring is not permission to resume migration, collection, training or promotion.

## Recovery commands

Use Linux x86_64 and Python 3.12. The repository uses ordinary Git blobs, not paid LFS. Clone the branch normally; do not use a shallow file download that omits the binary parts:

```sh
git clone --single-branch --branch backpack/python-engine-checkpoint-20261025 \
  https://github.com/sharon2467/Backpack-Battle-RL.git backpack-checkpoint
cd backpack-checkpoint
python3 -I -B -S recovery_checkpoint/restore.py \
  --destination /absolute/path/to/NEW-recovered-directory --profile full
```

The destination must not exist and its parent must exist. Full materialization needs at least **12 GB free** in addition to the clone and temporary space for one archive (at most about 341 MB). For a smaller working set:

```sh
python3 -I -B -S recovery_checkpoint/restore.py \
  --destination /absolute/path/to/NEW-recovered-directory --profile active
```

`active` still streams and checks **every logical file in every archive**, but physically creates the current source, tests/docs/tools, current-stage owner/evidence closure, latest original case, full offline game baseline, runtime and dependencies. Older large historical material remains fully present in the checked parts; `full` materializes it too. See `MANIFEST.json` for exact byte/file counts. `--verify-only` performs the same complete integrity traversal without creating the destination. Each restored file is physically read back twice. The receipt explicitly records the profile, counts, hashes and relocation map; active is not a full physical restore.

No restored scripts, game, models or training are automatically executed. Only the 18 explicitly listed runtime-relative links are created. Historical pool/project links are not recreated and an old pool is not marked READY.

## Use the recovered Python code

Set `RECOVERED` below to your newly created directory:

```sh
RECOVERED=/absolute/path/to/NEW-recovered-directory
cd "$RECOVERED/workspace/python-original-engine/repo"
python3 -B -S headless.py --help
python3 -B -S headless.py \
  --layout data/phase320-independent-postcheck/runtime/example-layout.json \
  --seed 32001 --output /tmp/backpack-recovered-result.json
```

The API and bounds are documented in `../`'s versioned work records and the repository's `python_engine/README.md`. The exact formal15 files and accepted candidate source remain intact. Read `docs/current-task-brief.md`, `data/phase024-root/current-task-state.json`, the 340 FINAL and 344 PARTIAL handoff before any later explicitly authorized engineering continuation. The 346 files are SOURCE preparation only, not evidence that its planned runtime run happened.

Legacy absolute paths beginning `/workspace` map to `RECOVERED/workspace`. The receipt records this mapping. Do not interpret a historical Library URL or an old local path as a new dependency. In a genuinely empty replacement workspace, the recovered directories can be installed at their original `/workspace/...` locations after checking those destinations are absent; do not overwrite an existing workspace. In a nested isolation test, use the recorded relocation map and relative paths. Frozen historical owners are not silently edited.

## Original materials, runtime and credentials

The full original baseline is reconstructed at:

`workspace/godotsteam-startup-20261013/baseline/Backpack Battles/`

Original game layers cover 15,418 original files / 616,167,851 bytes. The public offline baseline has **15,416 files**: two API credential literals are replaced by same-length placeholders, and the two corresponding encrypted `.gde` copies are omitted so they cannot reintroduce the secrets. Every change is listed with original/published hashes in `sanitization.json`. This is a documented sanitized copy, **not a byte-identical complete original source archive**. The graphics, audio, fonts, scenes, import cache and other original code are retained; original local files were not modified. Unredacted credentials are neither required nor provided for offline engineering, and online backend access is not a supported restore feature.

The four engineering checkpoint archives (243 main/support, 343, 347) remain **byte-exact**, with their original whole-archive SHA-256 identities. Necessary failures, raw structured validation evidence, old source snapshots, 344 unfinished files, 346 preparations and historical metadata are retained. 319 is already flattened into 343 and is not a restore dependency. The final merged logical index applies 243 support under `repo/`, 343 as the full overlay, and the latest 347 metadata last; archive snapshots themselves remain unchanged.

The official GodotSteam Linux distribution is pinned at **GodotSteam 3.30.2 / Godot 3.6.2 / Steamworks 1.62**, SHA-256 `9420fea9124c396fadd4366cb96cdada44d7642e2496b78c46c3929597a88a8d`. It is bundled, including the editor, templates and Steam library. The original four `.deb` packages and installed runtime support files are included too. Versions and official Codeberg / Debian snapshot URLs are in `MANIFEST.json`; no runtime download from an old cloud environment is used. Host system libraries still require a compatible Linux distribution, preferably Debian 13/trixie. No system packages or security settings are changed by the restore tool.

A minimal runtime version probe, after recovery, is:

```sh
RECOVERED=/absolute/path/to/NEW-recovered-directory
RUNTIME="$RECOVERED/workspace/godotsteam-startup-20261013"
LD_LIBRARY_PATH="$RUNTIME/engine:$RUNTIME/debian/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
  "$RUNTIME/engine/godotsteam.362.editor.x86_64" --version
```

Or run the packaged minimal check against the recovered directory:

```sh
python3 -I -B -S recovery_checkpoint/check_restored.py \
  --destination "$RECOVERED" --smoke --runtime-version
```

This runs one pure-Python historical example and probes the executable version; it does not run an original-game battle. Future oracle collection requires a newly initialized pool from the recovered baseline and explicit user permission to resume. No old running process or private user account is restored.

## Integrity and validation level

Each part has its own size/SHA-256, every reconstructed archive has its whole size/SHA-256, and `logical-files.jsonl` binds every final destination to an archive member, size, SHA and mode. The source inventory is preserved. Parts are at most 48 MiB each, below ordinary GitHub's 100 MiB file limit; no LFS subscription or storage purchase is used.

`security-scan.json` records recursive, hash-deduplicated ZIP/tar.xz inspection of the checkpoint payloads and targeted handling of intentionally damaged codec fixtures. Their invalid archive bytes are preserved as test inputs, never automatically extracted or executed. Pattern scans are bounded checks, not proof against every unknown secret representation. Unrelated home/auth folders and external personal material are outside this backup scope.

The remote-clone recovery check is recorded in `VALIDATION.md` when complete. Distinguish full archive/hash verification, actual active working-set materialization, a pure-Python smoke run, and a runtime version probe from a **fresh operating-system** or **full physical** restore. No new cloud environment is created by this procedure. Full historical oracle comparisons are retained as evidence, not rerun during publication.
