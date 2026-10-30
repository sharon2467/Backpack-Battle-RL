# Experimental Source combat: bounded King and non-King families

Standalone Python Source simulator. **Formal support remains75 non-King items.** The explicit `initialize_squirrel` API accepts its original bounded Squirrel164 domain; `initialize_experimental_nonking` accepts the fixed five-kind non-King extension described below. The retained directory name is compatible with previous King distributions. Three separate experimental King domains are available, with class0/default legal layouts and exactly one global King:

- Six IDs: `1,4,11,19,22,262`.
- Seven IDs: six plus one basic Goobert23 on the King's side.
- Eight IDs: `1,4,11,19,21,22,262,332`, with exactly one Magic Mirror332 on the King's side and one Fly Agaric21 on the opposite side. This branch does not include Basic23.

King identity/side may vary. Extra King/Basic/Mirror/Fly, wrong side relationships, other75×King mixes, SpikedShield16/RangerBag67 in the eight-ID branch, rage, gems and modifiers are rejected. Non-King formal75 behavior remains separate.

The15 Source files are exact frozen497 bytes, independently accepted in498 for the three-Whelp family on the previously accepted495 shared non-King Source. Thirteen modules are byte-exact495; only engine/headless changed. Shared attack, buff/payment/picker, history/Timer/RNG algorithms and old King/Squirrel/formal admission remain conserved. Historical490 accepted Squirrel on489;494 accepted the Whelp201/Squirrel shared interface on495 after a preserved one-receiver descriptor repair. Phase483 independently accepted the finite eight-ID King Source extension on482v2. Historical453/454 six-ID and459 seven-ID Source evidence is retained, without rerunning those old complete battles on this package. Phase483 passed17 ingress/component controls and one remaining natural Source integration:409events,474combat-provider audit entries and33Timers. It naturally hit Mirror activation/allocation, Poison reflection and zero/nonzero Poison ticks across King invulnerability; positive-buff protection accumulated to18 without consumption. These are fresh Source observations, not a new native comparison. The first natural attempt stopped at its chosen10 simulated-second ceiling; its error is preserved, and only the remaining natural case was rerun with a120 simulated-second ceiling. No candidate algorithm changed.

Phase478 passed all eight strict business sections for one fixed26-item King+Basic native case using its original primitive Tape:366 events,422 selected primitive records and33 business Timers. The captured candidate and corrected INPUT are separately frozen engineering artifacts; the15 Source files in this package are now exact497, with their shared business algorithms conserved. Phase451 separately passed a different fixed King case. These results do not claim native equality for every public Source layout or seed. Production all-seed/platform parity is not a prerequisite for Tape-based business validation; no new numeric probe is included. This remains an experimental partial engine and does not complete the RL environment. Old453/455 six-ID package remains available in the recovery checkpoint and Git history.

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

## Squirrel164 Source API

`validate_squirrel_layout(layout)` and `initialize_squirrel(layout, seed)` require at least one Squirrel164, otherwise only the old75 non-King items, class0 and default rules. King262, other classes, rage, gems, modifiers and external RNG/private state are outside this interface. Old `ITEMS75`, `validate_layout`, `initialize`, CLI and `run_batch` still reject164; use the explicit Python API. No new batch or CLI route is implied.

```python
import json
import headless

with open('examples/job-Squirrel.json', encoding='utf-8') as stream:
    job = json.load(stream)
battle = headless.initialize_squirrel(job['layout'], job['seed'])
result = battle.run(max_seconds=120.0)
with open('../result-Squirrel.json', 'w', encoding='utf-8') as stream:
    json.dump(result, stream, ensure_ascii=False)
```

The example is byte-exact490's pre-outcome22-item request with seed49001. Packaging did not run it again. Independent490 passed19 finite controls including one natural completion:313events/411combat-provider audit entries/26Timers, terminal34.000001773s andP winner. Natural repeated stealing produced10loss/10gain events,11Activation events,12pitch draws and11selection draws. The activation-tail pitch draw is retained because it shares the combat Util RNG stream even without audio objects. A natural count difference is not labeled a direct terminal-tail branch observation. Actual component controls separately proved ordered unique Pet-or-Food neighbors, exact startup speed arithmetic, protected loss0 with picked gain1 under the same parent, empty target, three pitch tails/fourth limiter return, and an ended allowed activation with no event but one pitch draw. Protected removal is component evidence, not a naturally observed protection-consumption claim.

Coverage labels remain `EXPERIMENTAL_SOURCE_SQUIRREL_NOT_NATIVE_VALIDATED`, formal_support75 and experimental_items[164]. Runtime catalog81 includes six experimental registered kinds including King; it is not formal81. The legacy Squirrel API domain and identity remain unchanged. No Squirrel native capture/comparison or arbitrary75×164 session guarantee follows. `max_seconds` is simulated time; use an external process deadline separately if needed. Lifecycle is the same `step/snapshot/result/run` API, with non-King completion determined by the engine's finalized state.

## Shared experimental non-King family API

`validate_experimental_nonking_layout(layout)` and `initialize_experimental_nonking(layout, seed)` admit only the old75 plus the fixed experimental set `{164,201,64,197,199}`, require at least one experimental instance and class0/defaults, and reject King/rage/gems/modifiers. Squirrel164 and AmethystWhelp201 can coexist with Ruby64/Emerald197/Sapphire199 in this explicit interface. This is a closed supported Source set, not an arbitrary user allowlist. The old Squirrel entry still rejects201/64/197/199; old initialize/CLI/batch still reject these experimental kinds. No new CLI or batch route is supplied.

```python
import json
import headless

with open('examples/job-Whelp-family.json', encoding='utf-8') as stream:
    job = json.load(stream)
battle = headless.initialize_experimental_nonking(job['layout'], job['seed'])
result = battle.run(max_seconds=120.0)
with open('../result-Whelp-family.json', 'w', encoding='utf-8') as stream:
    json.dump(result, stream, ensure_ascii=False)
```

The new job is byte-exact498's pre-outcome29-item request with seed49801. Packaging did not run it again. Independent498 passed16 control groups including the sole natural completion (two total unit/natural instances, nine rejection calls):232events/304combat-provider audit entries/26Timers, terminal16.000000834s,P. Ruby pre-combat reflection intercepted the Whelp201 startup; Emerald inflictedPoison7 times; Sapphire paidMana7 times and producedBlock then a nonMana buff under the same payment parent. Whelp201 removedMana7 times and Squirrel stole it6 times. Natural Mana0/misses/raw0-double branches were not hit; the corresponding components remain separate evidence.

Historical494 passed17 joined groups for201+164:four ingress groups before the real descriptor-copy defect, then only the remaining13 after495's one-receiver correction. Old passed ingress groups were not repeated. The old `initialization` property still returns a defensive copy; the correction writes only its owning instance's internal descriptor. That fixed22-item Source case yielded279events/375draws/26Timers with7Mana removals/8steals and speed0.6. These historical outputs belong to their frozen495 Source; neither they nor the older490 battle were rerun on this package.

Current results identify experimental non-King Source, formal_support75, actual experimental kinds present and catalog_registered81. Native comparison for these five new kinds, all-layout/all-seed session equivalence, general King and the full engine/RL remain unclaimed. Existing fixed-case native Tape evidence is retained separately. Some older conservative diagnostic strings are historical; lineage and exact hashes distinguish actual accepted Source versions.

## Byte verification and lineage

```bash
python -B verify_manifest.py
python -B verify_manifest.py --manifest-sha256 <independently-published-manifest-SHA256>
```

The verifier uses POSIX directory descriptors (the accepted Linux environment); it is read-only and imports no battle code. It checks all15 source files plus the listed documentation/examples/lineage/verifier for ordinary single-link files, safe paths, stable reads, size and SHA256. It checks listed payloads only. The manifest excludes itself; without a trusted external manifest SHA, local agreement detects payload drift relative to the local manifest, not authenticity.

`source-lineage.json` records the accepted Source/input/evidence identities. Those engineering paths are provenance only and are not runtime dependencies. PCG attribution remains in the copied source. No original Game or native capture payload is included.
