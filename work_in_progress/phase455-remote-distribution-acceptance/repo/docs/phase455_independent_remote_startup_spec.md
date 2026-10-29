# Phase455 — Independent remote distribution startup

## 1. Requirements

Check only Root's remote-readback clone at /workspace/backpack-github-source-clone-20261025, HEAD dbe4a71f64fa0eba5ccd391490c5f1575444bc5b. Preserve clone/package bytes. Exactly four checks: outermanifest verifier, trustedSHA innerverifier, CLI--help, one invalidseed CLI invocation with zero RNG/Engine/prepare calls. No battle, old451/454 repetition, Expected read or native process.

## 2. Design

First pin outerverifier591bc210…/outermanifest6160c40c…/inner8855e67f… and confirm outer membership66 includes the nestedmanifest; evidence/runtime-sources.json remains the exact30 historical runtime membership. Static outer Source excludes only ROOT/MANIFEST.json rather than every basename. Execute each check in a fresh subprocess with bytecode writes disabled; save logs/commands/status in a unique live-repository directory. Stop first unexpected result.

The invalid invocation runs the package headless.py CLI main through runpy in a fresh isolatedprocess, with package root explicitly inserted in sys.path. Use the package's unmodified layout-A and seed -1; no result file may appear. A small codefilename/qualname profiler starts before module import and counts initialize, CombatRandom/GodotPCGInteger/Engine constructors, prepare/activate/run/step. Expect initialize1 and all model/RNG counts0. Do not patch candidate functions or simulate a rejection.

## 3. Realize

Seal one independent launcher/probe script. Verify Root's exactcommit and pinnedmetadata, run outerverifier and innerverifier with trustedmanifestSHA, run actual CLI--help, then invoke the negativeprobe. Packagemodules must load only from the requested experimentalcapsule. Keep output/bytecode paths outsideclone. Rehash outermanifest and all66 listedpayloads after checks, record sourceunchanged and exactimport paths. Save each stdout/stderr and final owner. The helpers/verification commands are allowed execution; no engineconstructor or battle is allowed.

## 4. Acceptance Criteria / Tests

Outer reports66 publicationfiles/30exacthistorical runtimefiles; inner reports21listedpayloads/15sourcefiles and trustedmanifestSHA. Help exits0 and exposes documentedlayout/seed/batch options. Negativeprobe catches original uint64seed ValueError, observes initialize1, zero RNG/Engine/prepare/activate/run/step, and no resultfile. Allremote publicationbytes match their beforepins afterward. Scope remains experimentalSource, formal75unchanged and numeric/native seedparitypending.
