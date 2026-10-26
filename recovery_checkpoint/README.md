Current engineering status and active limitations: [CURRENT-WORK.md](CURRENT-WORK.md). This takes precedence over older status text inside immutable cuts.

# Self-contained engineering recovery checkpoint

This directory is the complete **GitHub-hosted recovery route**, not just the small Python demonstration. It contains the received original game code/resources/imports, the complete 243 base and support, the complete 343 work overlay, the final347 pause metadata plus the current cumulative354 engineering progress, fixed Linux runtime/dependency artifacts, and a standard-library restore tool. No Library file, old cloud workspace, old cache, or external checkpoint is needed to obtain the engineering files.

The user explicitly resumed work on2026-10-25. **Formal bounded75 has now been promoted and independently verified**, including one actual isolated package CLI run. King and the complete engine/RL remain unfinished. The current cumulative354 work cut includes the frozen349 single-King candidate, the independently accepted350 finite-component evidence, all failed and repaired controllers, and four newly produced351 raw trajectories. Their first strict cross-mode independent comparison PASSED with all12 presealed negative controls rejected; King is not promoted. The source-only353 original-observer plan is retained as planning, and the complete351 checker with its independent FINAL evidence is retained. Future355 implementation is outside this cut. Restore never automatically executes development, collection or training.

## Recovery commands

Use Linux x86_64 and Python 3.12. The repository uses ordinary Git blobs, not paid LFS. Clone the branch normally; do not use a shallow file download that omits the binary parts:

```sh
git clone --single-branch --branch backpack/python-engine-checkpoint-20261025 \
  https://github.com/sharon2467/Backpack-Battle-RL.git backpack-checkpoint
cd backpack-checkpoint
CHECKPOINT_REPOSITORY=$PWD
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
  --layout data/phase321-rainbow-king-source-plan/layout-drafts/Rainbow-B.json \
  --seed 34401 --output /tmp/backpack-recovered-result.json
```

The API and bounds are documented in `../`'s versioned work records and the repository's `python_engine/README.md`. The exact formal75 fifteen files and the historical68 snapshot remain intact. Read `docs/current-task-brief.md`, `data/phase024-root/current-task-state.json`, the340 FINAL, actual344 promotion receipt and actual346 independent package review. The historical344 PARTIAL and346 SOURCE records remain present, followed by real348/346 completion evidence; they must not be mistaken for current status.

Legacy absolute paths beginning `/workspace` map to `RECOVERED/workspace`. The receipt records this mapping. Do not interpret a historical Library URL or an old local path as a new dependency. In a genuinely empty replacement workspace, the recovered directories can be installed at their original `/workspace/...` locations after checking those destinations are absent; do not overwrite an existing workspace. In a nested isolation test, use the recorded relocation map and relative paths. Frozen historical owners are not silently edited.

## Original materials, runtime and credentials

The full original baseline is reconstructed at:

`workspace/godotsteam-startup-20261013/baseline/Backpack Battles/`

Original game layers cover 15,418 original files / 616,167,851 bytes. The public offline baseline has **15,416 files**: two API credential literals are replaced by same-length placeholders, and the two corresponding encrypted `.gde` copies are omitted so they cannot reintroduce the secrets. Every change is listed with original/published hashes in `sanitization.json`. This is a documented sanitized copy, **not a byte-identical complete original source archive**. The graphics, audio, fonts, scenes, import cache and other original code are retained; original local files were not modified. Unredacted credentials are neither required nor provided for offline engineering, and online backend access is not a supported restore feature.

The four historical engineering checkpoint archives (243 main/support,343,347) remain **byte-exact**, with their original whole-archive SHA-256 identities. Necessary failures, raw structured validation evidence, old source snapshots, 344 unfinished files, 346 preparations and historical metadata are retained. 319 is already flattened into 343 and is not a restore dependency. The final merged logical index applies 243 support under `repo/`, 343 as the full overlay, and the latest347 metadata then one cumulative current-progress archive; archive snapshots themselves remain unchanged. The supplied logical index is the complete final map, so one restore command is sufficient; no incremental script chain or old cloud file is required.

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
python3 -I -B -S "$CHECKPOINT_REPOSITORY/recovery_checkpoint/check_restored75.py" \
  --destination "$RECOVERED" --help-only
```

This reads the current15 source identities and actual promotion/package owners, then invokes CLI help only. It does not initialize or run a battle. One historical owner references the saved352 ZIP by its old absolute path. Its exact whole bytes are already the retained public single part `parts/phase352-current.part001`. The explicit whitelist `owner-relocations.json` and the following helper materialize that20,488,014-byte historical artifact inside the new recovery directory, without reading the old cloud path or overwriting existing files. This is a separately receipted artifact copy, beyond the active logical-file count. Then read back cumulative354 King work and evidence owners:

```bash
python3 -I -B -S "$CHECKPOINT_REPOSITORY/recovery_checkpoint/materialize_owner_artifacts.py" \
  --destination "$RECOVERED"
python3 -I -B -S "$CHECKPOINT_REPOSITORY/recovery_checkpoint/check_restored_work.py" \
  --destination "$RECOVERED"
```

Use the same destination supplied to restore. The historical68 checker and validation remain in the earlier commit/history; the official runtime bytes are unchanged. Future oracle collection uses a newly initialized pool from the recovered baseline and a separately reviewed collection plan. No old running process or private user account is restored.

## Integrity and validation level

Each part has its own size/SHA-256, every reconstructed archive has its whole size/SHA-256, and `logical-files.jsonl` binds every final destination to an archive member, size, SHA and mode. The source inventory is preserved. Parts are at most 48 MiB each, below ordinary GitHub's 100 MiB file limit; no LFS subscription or storage purchase is used.

`security-scan.json` records recursive, hash-deduplicated ZIP/tar.xz inspection of the checkpoint payloads and targeted handling of intentionally damaged codec fixtures. Their invalid archive bytes are preserved as test inputs, never automatically extracted or executed. Pattern scans are bounded checks, not proof against every unknown secret representation. Unrelated home/auth folders and external personal material are outside this backup scope.

The original remote-clone verification is retained under `history/phase347-*`. The current work-cut remote recovery result is recorded in `VALIDATION.md`. Distinguish full archive/hash verification, actual active working-set materialization, a pure-Python smoke run, and a runtime version probe from a **fresh operating-system** or **full physical** restore. No new cloud environment is created by this procedure. Full historical oracle comparisons are retained as evidence, not rerun during publication.

The inherited `coverage.owner_closure_paths` is the base347 planning statistic. All current cumulative payloads are active; current complete logical/physical counts are recomputed in the coverage fields. Current source/material review receipts are `progress-current-source-review.json` and `progress-current-material-review.json`; the348 receipts remain historical evidence. Cumulative352 remote active recovery and both output-only checkers passed; current354 verification is recorded separately; see `VALIDATION.md` and `validation.json` for exact identities, counts and validation limits.

Current work remains a single complete logical index: ten fixed historical/original/runtime archives plus one cumulative progress archive. Earlier progress part files and manifests are retained as history. They are not a sequential patch chain. The active formal entry remains75; use the staged King source only within its documented experimental domain and validation gates.

## Work preserved after the archival cut

The complete helper SOURCE, frozen tiny-control procedure and actual evidence are preserved as a small flat tree at `verification_evidence/repo/`, with `verification_evidence/FILES.json` identities. To make these post-cut records available at their original repo-relative paths after main restoration, run from the Git clone root:

```sh
cp -rn recovery_checkpoint/verification_evidence/repo/. "$RECOVERED/workspace/python-original-engine/repo/"
```

The additive355 SOURCE-only candidate and its27 owner leaves are independently inventoried at [work_in_progress/phase355](../work_in_progress/phase355/README.md). Its remaining dependencies and pending independent status are explicit; it is not part of production75. Copying either flat tree does not replace the formal engine. These are direct GitHub files, not a sequential archive chain. Current actual remote verification is in `VALIDATION.md`.

SOURCE355 later failed independent profile↔old-patch provenance coupling. Its immutable source and exact independent failure records remain at `../work_in_progress/phase355/`; the separate356 shared-admission repair is at `../work_in_progress/phase356/`, with independent SOURCE regression now accepted68/68 while native admission stays closed. Both are work in progress and do not replace production75. Follow their READMEs for additive recovery.

The later complete typed observer schema SOURCE and independent prerequisite matrix are preserved at [phase357](../work_in_progress/phase357/README.md), now independently blocked by its first schema probes. The separate [358 schema repair](../work_in_progress/phase358/README.md) has passed its bounded80-case independent SOURCE controls, while full source carriers/cache business proof and native producer remain pending. This remains SOURCE-only; native admission is closed.

All flat post-cut supplements can be added in any order using their repo-relative paths; they are immutable stage snapshots, not an incremental script chain. From this Git clone root after the main restoration, this single loop recovers all available SOURCE versions and review evidence without overwriting existing files:

```sh
for segment in recovery_checkpoint/verification_evidence/repo \
  work_in_progress/phase*/repo work_in_progress/phase*/source/repo \
  work_in_progress/phase*/independent_preparation/repo \
  work_in_progress/phase*/design/repo \
  work_in_progress/phase*/review_evidence/repo \
  work_in_progress/phase*/finalization_preparation/repo; do
  if [ -d "$segment" ]; then
    cp -rn "$segment/." "$RECOVERED/workspace/python-original-engine/repo/"
  fi
done
```

Adjacent FILES.json inventories and frozen owners preserve exact stage identities. Reading later SOURCE snapshots never implies production promotion.

Generated observation-producer SOURCE and its independent preparation are preserved at [phase359](../work_in_progress/phase359/README.md), with explicit schema/auxiliary-proof gaps. No runtime or original-game validation is implied.

## First original027 startup failure capsule

The first actual attempt and independent BOOL-domain diagnosis are preserved in [phase364](../work_in_progress/phase364/README.md). Its standalone capsule has a per-member manifest and [explicit extraction instructions](../work_in_progress/phase364/failure_capsule/README.md); it is outside archival354 counts. Actualbattle never started; recovery/attempt02/models remain separate gates.

## Actual restoration and second startup failure

[Phase367 standalone capsules](../work_in_progress/phase367/README.md) preserve actual366 restoration/independent readbacks/RootREADY, actual367 failed startup and its independent source diagnosis. Follow that README's explicit evidence extraction after the main restore and flat SOURCE supplements. The pool is currently failed again; no battle/model or King acceptance is implied. This supplements the archived354 counts and does not replay a restore chain.

## Descriptor preflight and partial-reset recovery work cut

[380](../work_in_progress/phase380/README.md) preserves the descriptor-bound installer/recovery SOURCE and its first independent checker failure. [382](../work_in_progress/phase382/README.md) contains bounded independent component acceptance:9inherited SOURCE checks,26actual dynamic definitions and4explicitly unexecuted negative layers. Full recovery/wholehost/native positives remain separate. [381](../work_in_progress/phase381/README.md) preserves a proposed physical readback checker and its two SOURCE review failures; that version has not been executed. All are flat additive snapshots, with exact FILES/owner manifests. Production remains bounded75; King and the full engine/RL remain incomplete.

The later [384readback repair and independent actual result](../work_in_progress/phase384/README.md) closes the two381SOURCE gaps and preserves the first successful physical target verification. [383](../work_in_progress/phase383/README.md) records one actual74-write recovery retainingfailed, followed by the separately owned physical PASS and a distinct RootREADY commit/fullcheck. This is original-executor evidence, not a fresh OS restore or King admission. Current collection SOURCE remains380; any native attempt still requires fresh budget and explicit current Root release.
