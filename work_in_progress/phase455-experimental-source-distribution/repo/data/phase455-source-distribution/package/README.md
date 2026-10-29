# Experimental Source King combat

Standalone Python Source simulator. **Formal support remains 75 non-King items.** The additional King path is experimental: exactly one King across both sides, both characters class0, and only item IDs `1, 4, 11, 19, 22, 262` (Wooden Sword, Wooden Buckler, Leather Bag, Health Potion, Blueberries, King Goobert). King may have a different identity or be on either side.

This package is an exact copy of the independently accepted phase453 code. Phase454 checked ingress, deterministic sequential/interleaved execution and independent instance state. It does **not** establish custom-native numeric ABI, native seed/session consumption parity, arbitrary-layout native correctness, King with the other75 items, two King, rage, gems or a complete RL action environment. Phase451's separate fixed441 comparison passed all eight business sections using an actual primitive Tape; that evidence does not prove seeded-native equivalence.

## Runtime

Use Python3.12 (the accepted environment); the code requires Python3.10+ syntax. Standard library only: no pip packages, Godot, GPU, original game/assets, capture files or GUI are needed. Other Python minors have not been independently tested here.

Run from this directory in a fresh Python process. The package intentionally retains the same module names as the separate formal75 distribution; do not mix their modules in an already-running interpreter. `-B` avoids bytecode files in the source tree.

## CLI

Choose one command; these compute new simulations when you run them:

```bash
python -B headless.py --help
python -B headless.py --layout examples/layout-A.json --seed 123456789 --output ../result-A.json
python -B headless.py --layout examples/layout-B.json --seed 987654321 --output ../result-B.json
python -B headless.py --batch examples/jobs.json --output ../batch-summary.json
```

Add `--keep-results` to the batch command for full per-job results. Batch accepts1..64 exact `{layout, seed}` jobs and validates the whole batch before starting any job. A real budget timeout produces `TIME_BUDGET` without a fabricated winner/result; other internal errors propagate. Full traces can be large even when only summaries are returned.

The examples are unchanged inputs extracted from phase454's pre-outcome requests, including their seeds. They are examples, not a native-output oracle.

## Python API

From this directory, in a fresh process:

```python
import json
import headless

with open('examples/jobs.json', encoding='utf-8') as stream:
    jobs = json.load(stream)

batch = headless.run_batch(jobs, max_seconds=120.0, keep_results=False)

battle = headless.initialize(jobs[0]['layout'], jobs[0]['seed'])
while not battle.done:
    battle.step()
result = battle.result()
```

`initialize` already prepares and activates one fresh instance. For the King path, `step` advances one physics+idle quantum; after completion it returnsFalse with no advance. `snapshot()` reads without advancing; `result()` requires completion. `battle.run(max_seconds=120.0)` is the direct complete-run alternative.

Layouts use `headless-layout/1`: explicit `below_master`, ordered P/O sides and item entries with `item_index, x, y, f, instance_id`. IDs are unique; rotations are0..3. Bags precede ordinary items; cells must lie on the9×7 board, ordinary cells must be bag-covered and nonoverlapping. HP/stamina may be supplied as accepted integer-valued numbers. Root seeds are uint64 integers; bool is rejected. Captured clocks, private state, external RNG objects, GUI facts and modifiers are not layout fields.

The Source seed policy is `headless-sha256-domains/1`: independent global and Util streams reuse the existing Source PCG implementations, with continuous global state after preparation shuffle. King scheduling is an explicit60physics+60idle Source policy, not a replay of retail idle timing. Results expose Source-only coverage and pending native seed-parity labels plus actual stream states. Different seeds need not yield different winners.

## Byte verification and lineage

```bash
python -B verify_manifest.py
python -B verify_manifest.py --manifest-sha256 <independently-published-manifest-SHA256>
```

The verifier uses POSIX directory descriptors (the accepted Linux environment); it is read-only and imports no battle code. It checks all15 source files plus the listed documentation/examples/lineage/verifier for ordinary single-link files, safe paths, stable reads, size and SHA256. It checks listed payloads only. The manifest excludes itself; without a trusted external manifest SHA, local agreement detects payload drift relative to the local manifest, not authenticity.

`source-lineage.json` records the accepted Source/input/evidence identities. Those engineering paths are provenance only and are not runtime dependencies. PCG attribution remains in the copied source. No original Game or native capture payload is included.
