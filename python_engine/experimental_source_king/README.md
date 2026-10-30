# Experimental Source King combat: six, seven and eight IDs

Standalone Python Source simulator. **Formal support remains75 non-King items.** Three separate experimental King domains are available, with class0/default legal layouts and exactly one global King:

- Six IDs: `1,4,11,19,22,262`.
- Seven IDs: six plus one basic Goobert23 on the King's side.
- Eight IDs: `1,4,11,19,21,22,262,332`, with exactly one Magic Mirror332 on the King's side and one Fly Agaric21 on the opposite side. This branch does not include Basic23.

King identity/side may vary. Extra King/Basic/Mirror/Fly, wrong side relationships, other75×King mixes, SpikedShield16/RangerBag67 in the eight-ID branch, rage, gems and modifiers are rejected. Non-King formal75 behavior remains separate.

The15 Source files are exact frozen482v2 bytes, independently accepted in483 for the finite eight-ID Source extension;13 modules and the shared business/Timer/RNG algorithms are conserved from458. Historical453/454 six-ID and459 seven-ID Source evidence is retained, without rerunning those old complete battles on this package. Phase483 passed17 ingress/component controls and one remaining natural Source integration:409events,474combat-provider audit entries and33Timers. It naturally hit Mirror activation/allocation, Poison reflection and zero/nonzero Poison ticks across King invulnerability; positive-buff protection accumulated to18 without consumption. These are fresh Source observations, not a new native comparison. The first natural attempt stopped at its chosen10 simulated-second ceiling; its error is preserved, and only the remaining natural case was rerun with a120 simulated-second ceiling. No candidate algorithm changed.

Phase478 passed all eight strict business sections for one fixed26-item King+Basic native case using its original primitive Tape:366 events,422 selected primitive records and33 business Timers. The captured candidate and corrected INPUT are separately frozen engineering artifacts; the15 Source files in this package are now exact482v2, with their shared business algorithms conserved. Phase451 separately passed a different fixed King case. These results do not claim native equality for every public Source layout or seed. Production all-seed/platform parity is not a prerequisite for Tape-based business validation; no new numeric probe is included. This remains an experimental partial engine and does not complete the RL environment. Old453/455 six-ID package remains available in the recovery checkpoint and Git history.

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
python -B headless.py --layout examples/layout-King-Basic.json --seed 45701 --output ../result-King-Basic.json
python -B headless.py --layout examples/layout-King-Mirror-Poison.json --seed 48701 --output ../result-King-Mirror-Poison.json
python -B headless.py --batch examples/jobs-RL-smoke.json --keep-results --output ../batch-RL-smoke.json
```

Add `--keep-results` to the batch command for full per-job results. Batch accepts1..64 exact `{layout, seed}` jobs and validates the whole batch before starting any job. `max_seconds` / `--max-seconds` is the simulated combat-time ceiling (up to120 seconds on these King paths), not a wall-clock deadline. Exceeding it before terminal produces `TIME_BUDGET` in batch without a fabricated winner/result; other internal errors propagate. Set an external process/harness wall-clock limit separately when needed. Full traces can be large even when only summaries are returned.

The original A/B/jobs examples are byte-exact455 inputs from454's pre-outcome requests. The added King-Basic layout is extracted from459's presealed request before its Source outcome; source_root_seed45701 is unchanged. The new King-Mirror-Poison layout is extracted from483's presealed `source-job.layout`, without outcome data. `jobs-RL-smoke.json` contains exactly that eight-ID layout with seed48701 followed by the existing seven-ID King-Basic layout with seed48702. Root selected these two seeds before any corresponding execution; the jobs are for fresh Source batch/throughput validation, not native comparison or a completed RL environment. Examples are inputs, not native-output oracles. Running a command computes a new simulation; packaging did not rerun accepted battles.

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

The Source seed policy is `headless-sha256-domains/1`: independent global and Util streams reuse the existing Source PCG implementations, with continuous global state after preparation shuffle. King scheduling is an explicit60physics+60idle Source policy, not a replay of retail idle timing. Results expose Source-only coverage and pending native seed-parity labels plus actual stream states. Some runtime coverage descriptions predate478 and still conservatively say that joint native comparison is pending; this documentation and lineage record the later fixed-case acceptance without changing those historical code bytes. Different seeds need not yield different winners.

## Byte verification and lineage

```bash
python -B verify_manifest.py
python -B verify_manifest.py --manifest-sha256 <independently-published-manifest-SHA256>
```

The verifier uses POSIX directory descriptors (the accepted Linux environment); it is read-only and imports no battle code. It checks all15 source files plus the listed documentation/examples/lineage/verifier for ordinary single-link files, safe paths, stable reads, size and SHA256. It checks listed payloads only. The manifest excludes itself; without a trusted external manifest SHA, local agreement detects payload drift relative to the local manifest, not authenticity.

`source-lineage.json` records the accepted Source/input/evidence identities. Those engineering paths are provenance only and are not runtime dependencies. PCG attribution remains in the copied source. No original Game or native capture payload is included.
