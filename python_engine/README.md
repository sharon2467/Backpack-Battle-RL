# Standalone Python battle-engine checkpoints

This directory packages the existing Python reconstruction of Backpack Battles 1.1.8 combat. It is a **partial implementation**, not the complete original engine. The playable implementation uses Python's standard library; it does not launch Godot, read original-game assets, or need a captured random tape.

| Snapshot | Default item ingress | Status |
| --- | ---: | --- |
| `formal68/` | 68 | Accepted historical checkpoint |
| `candidate75/` | 75 | Current accepted bounded runtime; promoted344 and independently verified348/346 |
| `experimental_source_king/` | 75 non-King; six-ID King / seven-ID King+basic Source branches | Independently tested Source interface; native seed/new-layout parity pending |

The directory name `candidate75/` is retained from the pre-promotion snapshot; its exact fifteen source files are now the accepted bounded75 runtime. The user explicitly resumed the migration on2026-10-25. Exact promotion, independent readback and one isolated package CLI run succeeded; King production work and the full engine/RL are still incomplete.

## Latest pure combat evidence

On2026-10-29 the fixed King-A39-item/six-type mixed case passed all eight strict business sections against the original: events, parent closure, histories, all365 primitive/RNG state, final state, sampled callbacks, typed business Timer API and terminal clock cuts. The single Python battle was sealed before comparison and was not rerun. See [current engineering checkpoint](../recovery_checkpoint/CURRENT-WORK.md) and `work_in_progress/phase451-fixed-king-strict-acceptance/`.

This admits the fixed conditional-Tape case only; it does not add King to `candidate75/`, prove native seed parity, or complete the engine/RL. The separate [experimental Source package](experimental_source_king/README.md) now provides fresh single-King layout+seed (six-ID or seven-ID with one same-side basic Goobert) and sequential batch APIs without GUI/captured-state input. Phase454 independently accepted its typed determinism/isolation and26 ingress controls; the earlier453/455 package passed independent remote startup checks. Current458 exact Source adds basic Goobert23 and459 independently accepted22 business controls plus one fixed26-item Source battle; natural King-first reentry hit, Basic-first component only. This new package passed independent remote outer68/legacy30 and inner22/15 manifest checks, CLIhelp and seed-1 rejection before RNG/Engine creation, without a battle. No native joint or generalKing admission follows.

## Run the formal checkpoint

Python 3.12 is the tested interpreter. No pip packages are required.

From the repository root, run the current accepted75 runtime:

```sh
python3 -B -S python_engine/candidate75/headless.py \
  --layout python_engine/examples/formal75.json \
  --seed 34401 --output /tmp/backpack-formal75-result.json
python3 -B -S python_engine/tools/verify_manifest.py
```

The separate isolated package validation retained873 events,784 random returns,2760 frames and winnerO at seed34401. Complete same-instance final/RNG/Timer/cache and read-boundary checks passed. This is one reproducibility example, not a throughput benchmark or proof of arbitrary75 interactions. The full raw evidence is under the complete recovery checkpoint.

`initialize(layout, seed)` prepares and starts combat, followed by `step()`, `snapshot()` and `run(max_seconds=120)`. No complete Gym/reset/batch/throughput guarantee is claimed. Keep the two snapshot directories on separate Python import paths. Existing unittest tests target the historical68 snapshot; running them does not validate the new75 scope or rerun original-game comparisons.

## Inputs and boundaries

The JSON root has exactly `schema: "headless-layout/1"`, boolean `below_master`, and two ordered `sides` named `P` and `O`. Each side has `character_class` (integer 0 or 2), `items`, and optional initial `hp`/`stamina`. Each placement preserves `instance_id`, numeric `item_index`, `x`, `y`, and rotation field `f` (0, 1, 2 or 3 quarter-turns). Bags precede ordinary items; item bodies must be valid, covered and non-overlapping. See the two complete JSON examples.

Only the admitted default configurations are accepted. Unsupported fields, items, classes, gems and modifiers fail validation. The runtime catalogue contains 76 registered descriptions; that is not a claim of complete support. In particular, King Goobert is not admitted by the formal `candidate75/` entry point; the separately labelled experimental package has its finite six-ID King and seven-ID King+basic Source domains.

Production seeds use the recorded `headless-sha256-domains/1` policy to derive distinct global/Util seed domains. This does not claim mathematical independence or reproduce a native session's independently seeded streams. Historical exact original-game comparisons used conditional primitive replay; they are a different validation path from the fresh headless API.

## What has been verified

The curated historical record is [evidence/validation-summary.json](evidence/validation-summary.json). It preserves counters, scope and receipt hashes, without private raw records:

- Formal68: an original-game case matched 672 events/allocations, 120 parent references, 827 random inputs, 61 Timer API pairs and 34210 callbacks, with complete histories and supported typed final state. A separate isolated standard-library-only package run succeeded.
- Accepted75 (historical candidate): bounded source/component and mixed Python validation plus an original-game case matched 400 events, 401 allocations, 30 parent references, 505 random inputs, 56 Timer API calls and 26120 callbacks. Seven pollution controls rejected modified outputs.
- In that candidate original-game case, effects 219/220/416/469 occurred; **74/169/401 did not naturally trigger**. Their component and Python mixed-layout evidence is not an original-game hit. Both observed Mirror calls had zero sum and zero random draws.
- Both historical original processes reported exit code zero and complete captures, but **`process_clean_exit=false`**. That diagnostic is retained. Four candidate audit-checker failures were preserved and corrected; successful models were not rerun.

The tests here verify publication integrity, the formal example, seed-domain derivation and rejection boundaries. They do not repeat the original-game oracle comparisons. The small Python package alone does not reproduce the historical raw oracle comparison. The separate [complete recovery checkpoint](../recovery_checkpoint/README.md) now carries the original materials (with documented credential sanitization), exact work archives and structured raw evidence needed for engineering continuation. The receipt hashes in this small summary are provenance references, not independent proof of a rerun.

Unfinished or unverified domains include arbitrary combinations and full subscriber/reentry/terminal closure, other items/classes, gems/socket modifiers, death/resurrection combinations, King fresh-runtime work, and a complete RL interface. Specific original-case misses include Ruby positive-start and several logic-timer/reentry branches. No coverage percentage based on all original description entries is claimed.

## Publication contents

Each runtime's fifteen files retain their verified source bytes. [evidence/runtime-sources.json](evidence/runtime-sources.json) records those identities; [MANIFEST.json](MANIFEST.json) covers all publication files. Versioned observer/profile strings in the Python validators are protocol identifiers; they do not require the original observer or Godot at runtime.

This Python subpackage excludes original game sources/assets and bulky work records; the separately authorized `recovery_checkpoint/` now backs up the complete engineering checkpoint and sanitized offline original materials. Credentials and unrelated private/home files are not published. Existing repository history is retained unchanged. Third-party algorithm notices are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md); no original-game asset or source licence is granted.

The newer single-King native adapter is preserved as [unaccepted SOURCE work](../work_in_progress/phase355/README.md). It does not replace either runnable snapshot. Its355 SOURCE review is BLOCKED by an old-patch/new-profile binding counterexample. The [356 staged repair](../work_in_progress/phase356/README.md) is preserved separately with independent SOURCE regression accepted68/68 but native admission closed; collector/schema/patch/input-builder/host are unfinished.
