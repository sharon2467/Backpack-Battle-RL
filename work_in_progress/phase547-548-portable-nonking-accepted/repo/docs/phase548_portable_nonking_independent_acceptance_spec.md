# Phase548 — independent portable nonKing package acceptance

## 1. Requirements

Accept only the byte-exact547 distribution of accepted545 Source15. Review20 physical files (19 manifest payloads plus externally pinned manifest), original546 presealed22-item example, lineage and public API documentation. Keep old SDK497 and all historical evidence unchanged. No new combat, initialize, constructor, Native, Expected, pool or old-suite invocation. Static preparation does not itself authorize the two runtime calls below; Root releases the frozen harness afterward.

## 2. Design

One fresh isolated Python-I-B process, cwd/tmp, inserts only this package root for local imports. It imports the existing read-only verifier and invokes verify(package, trusted_manifest_sha) exactly once before any battle module import. It then imports headless once and invokes validate_experimental_nonking_layout(example) exactly once. This is necessary to establish relocation/import closure and the documented public ingress at the actual isolated package path, without constructing or replaying a battle. No initialize is needed. A20-second inner/25-second outer wall cap bounds this small smoke.

The unchanged verifier enforces its own pinned-root dirfd/no-follow read scope. Before importing headless, the harness installs an additional audit limiting reads to the exact package20 files and harness pins; writes are restricted to the new result directory. Python bytecode writes are disabled and any cache lookup uses a new unused output path. Profile observation records selected entrypoints and fails immediately on entry to a constructor/RNG/prepare/activate/run/step initializer; no candidate function is monkeypatched. Verify Source/example bytes before and after. Preserve first unexpected failure and stop without retry.

## 3. Realize

`tests/phase548_independent_portable_package.py` reads frozen pins, authenticates package contents, installs the observational call counter, loads verify_manifest, calls its real verify once with the external SHA, saves the raw result, installs the candidate readonly audit, then loads headless and validates the example. It seals the actual returned fixture before checking22 ordered instance entries and documented schema/default fields. It records __file__ for every imported package module and proves each is in the manifest. Source hashes and full physical file membership remain unchanged after calls. Result/owner include real Python version and actual counts. Root invokes one fresh process using the frozen execution-plan only after release.

Static preparation independently verifies the547 owner24 refs, manifest19 paths/kinds/size/SHA and full20-file inventory, exact54515 payloads, verifier's sole schema-constant delta from491v2, lineage descriptor links and canonical example equality with546.layout. Parse the two README Python snippets as syntax only; do not execute them. Inspect local import closure and the actual validate call path, not a new global code audit. Python3.10+ is a minimum syntax claim; the current actual runtime version is recorded separately, and no3.10 runtime test is claimed.

## 4. Acceptance Criteria / Tests

Static review PASS, real verify1 returning19 payloads/15 Sources, headless import1, public validate1 returning the22-item fixture, constructor/prepare/activate/run/step/RNG-constructor0, Native/Expected/old battle0, all20 package hashes and membership unchanged. These calls establish package relocation and input validation only. Reuse546 Source behavior evidence without rerunning it. The natural546 Squirrel loss NOT_HIT and pending231 Native/general seed equivalence remain disclosed; formal75 and existing public domains are unchanged.
