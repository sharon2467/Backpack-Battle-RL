# Standalone Python battle-engine checkpoints

This directory packages the existing Python reconstruction of Backpack Battles 1.1.8 combat. It is a **partial implementation**, not the complete original engine. The playable implementation uses Python's standard library; it does not launch Godot, read original-game assets, or need a captured random tape.

| Snapshot | Default item ingress | Status |
| --- | ---: | --- |
| `formal68/` | 68 | Accepted, current formal entry point |
| `candidate75/` | 75 | Independent bounded validation passed; **not promoted** |

The snapshots are deliberately separate. Publishing the candidate does not promote it or complete its planned portable-package validation. The underlying migration remains paused. This publication changes packaging and documentation, not battle rules.

## Run the formal checkpoint

Python 3.12 is the tested interpreter. No pip packages are required.

From the repository root:

```sh
python3 -B -S python_engine/formal68/headless.py \
  --layout python_engine/examples/formal68.json \
  --seed 32001 --output /tmp/backpack-formal68-result.json
python3 -B -S -m unittest discover -s python_engine/tests -v
python3 -B -S python_engine/tools/verify_manifest.py
```

`--max-seconds` defaults to 120 simulated seconds. The output includes events, event references, histories, final state, RNG inputs and scheduling information. The supplied formal example at seed 32001 has a recorded regression result of 681 events, 842 random inputs, 2340 frames and winner `O`; this is a reproducibility fixture, not a performance benchmark.

For the API, add `python_engine/formal68` to the module search path and import `headless.initialize`. `initialize(layout, seed)` prepares and starts combat; the returned object exposes `step()`, `snapshot()` and `run(max_seconds=120)`. There is no complete Gym/RL environment or reset/batch/throughput guarantee.

The experimental snapshot can be inspected separately under `candidate75/`; `examples/candidate75.json` is its synthetic layout. Its new admissions are indices 74, 169, 219, 220, 401, 416 and 469. Do not put the candidate directory and formal directory on the same Python import path. The publication smoke run uses formal68 only.

## Inputs and boundaries

The JSON root has exactly `schema: "headless-layout/1"`, boolean `below_master`, and two ordered `sides` named `P` and `O`. Each side has `character_class` (integer 0 or 2), `items`, and optional initial `hp`/`stamina`. Each placement preserves `instance_id`, numeric `item_index`, `x`, `y`, and rotation field `f` (0, 1, 2 or 3 quarter-turns). Bags precede ordinary items; item bodies must be valid, covered and non-overlapping. See the two complete JSON examples.

Only the admitted default configurations are accepted. Unsupported fields, items, classes, gems and modifiers fail validation. The runtime catalogue contains 76 registered descriptions; that is not a claim of complete support. In particular, King Goobert is not admitted by the public headless entry point.

Production seeds use the recorded `headless-sha256-domains/1` policy to derive distinct global/Util seed domains. This does not claim mathematical independence or reproduce a native session's independently seeded streams. Historical exact original-game comparisons used conditional primitive replay; they are a different validation path from the fresh headless API.

## What has been verified

The curated historical record is [evidence/validation-summary.json](evidence/validation-summary.json). It preserves counters, scope and receipt hashes, without private raw records:

- Formal68: an original-game case matched 672 events/allocations, 120 parent references, 827 random inputs, 61 Timer API pairs and 34210 callbacks, with complete histories and supported typed final state. A separate isolated standard-library-only package run succeeded.
- Candidate75: bounded source/component and mixed Python validation plus an original-game case matched 400 events, 401 allocations, 30 parent references, 505 random inputs, 56 Timer API calls and 26120 callbacks. Seven pollution controls rejected modified outputs.
- In that candidate original-game case, effects 219/220/416/469 occurred; **74/169/401 did not naturally trigger**. Their component and Python mixed-layout evidence is not an original-game hit. Both observed Mirror calls had zero sum and zero random draws.
- Both historical original processes reported exit code zero and complete captures, but **`process_clean_exit=false`**. That diagnostic is retained. Four candidate audit-checker failures were preserved and corrected; successful models were not rerun.

The tests here verify publication integrity, the formal example, seed-domain derivation and rejection boundaries. They do not repeat the original-game oracle comparisons. Complete raw oracle replay is intentionally unavailable in this branch: it requires separately held game-dependent evidence and original resources that are not redistributed here. The receipt hashes are provenance references, not independent proof of omitted evidence.

Unfinished or unverified domains include arbitrary combinations and full subscriber/reentry/terminal closure, other items/classes, gems/socket modifiers, death/resurrection combinations, King fresh-runtime work, and a complete RL interface. Specific original-case misses include Ruby positive-start and several logic-timer/reentry branches. No coverage percentage based on all original description entries is claimed.

## Publication contents

Each runtime's fifteen files retain their verified source bytes. [evidence/runtime-sources.json](evidence/runtime-sources.json) records those identities; [MANIFEST.json](MANIFEST.json) covers all publication files. Versioned observer/profile strings in the Python validators are protocol identifiers; they do not require the original observer or Godot at runtime.

Original GDScript/scenes/resources, game executables, capture databases, raw private acceptance logs, credentials, personal conversations, internal task records, checkpoint ZIPs and unfinished publishing/restore helpers are excluded. Existing repository history is retained unchanged. Third-party algorithm notices are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md); no original-game asset or source licence is granted.
