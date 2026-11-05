# 662 — Wand422 isolated Source implementation

## 1. Requirements

Implement only the Wand422 rule in `phase662_wand422_shared_buff_conversion_spec.md`, using the public technical661 selection (SHA256 `9b532554660af871ceef52ddd6d85156e5ff5bd99715e08ae6c652c404d11483`). Base is the current public564 portable fifteen Python files at `/workspace/backpack-python-publish-20261025/python_engine/experimental_nonking`. Engine preimage: 259634 bytes, SHA256 `2a29367a60d55937bfd139ad16cc4b228c3616acf28f6d37f826c15284f9feff`; headless preimage: 35808 bytes, SHA256 `767c9236eb930870c66b221c871a9c530b0af408bb9d6ac740a77a5149e1ebee`. Only these two modules may change; thirteen others remain byte exact. Old packages and captured candidates remain untouched. Catalog85 is an experimental Source candidate, with formal75 unchanged.

## 2. Design

Use the existing `validate_experimental_nonking_layout` / `initialize_experimental_nonking` API. A fixture containing422 is restricted to IDs `{1,11,22,231,422}`, class0/default parameters, no King/rage/gems or other experimental modifiers, and at most one422 per side. The new validator returns immediately when422 is absent; all existing162/385/King/formal/CLI/batch/Squirrel gates retain their existing bodies. No per-item public API is added. Wand has two vertical collision cells, no stars/sockets, Magic accessory metadata, cooldown3.3, ordered subset `(105,101,102)`, thresholds10, Empower1, consumption1. Original scene/CSV/script/Item helper descriptors are frozen in `original-source-pins.json`; scene existence does not establish Native inventory admission.

Before Source generation, freeze `source-job.json`: a fifteen-item layout (P eight/O seven), seed66301, simulated budget120 seconds. It uses four Leather Bags per side, Wolpertinger/Blueberries/Wooden Sword, and one P Wand. Its result and natural branch hits are unknown. Source-derived fresh initialization and independent Python seed policy are distinct from Native seeded equivalence.

## 3. Realize

`engine.CATALOG`: add only422; `WAND_FIXTURE_IDS`: add the closed five-ID constant. New `validate_wand_fixture(fixture)` checks the conditional bounds above; existing `validate_fixture` calls it after the unchanged Bowl/Enchanted checks.

New `CombatEngine.remove_most_buffs(item, num_buffs, parent=None, use=False, available_buffs=range(101,108))`: require an owned item, strict BOOL use and finite nonnegative source number; select own side for use, opponent otherwise. Reuse `get_most_stacks` and its ordered candidates; consume one `randi_range("most_buff:<identity>:<side>",0,n-1)` even for singleton/zero ties. Only after choice compute `min(requested,current)`. Zero returnsNone after the draw; otherwise return the actual event from existing `use_stack` or `remove_stack`. No new rounding, logging mode, flush, protection, event or RNG implementation.

`CombatEngine.trigger` adds one422 branch after its existing single cooldown adjustment: `give_least_buffs(item,1,None,subset)` completes; inspect live character mana/lucky/regeneration; if ANY reaches its threshold, call `remove_most_buffs(...,use=True)` and give Empower with the returned event's actual `id`, orNone. Always call existing `activate`, including zero-loss and limiter paths; do not add ended checks. Existing trigger branches retain their exact text. `headless.EXPERIMENTAL_NONKING_ITEMS` adds422; all headless function bodies remain exact. Existing preparation and all Timer/FrameDriver/RNG/history/least/most/give/use/remove/activate bodies remain exact.

## 4. Acceptance Criteria / Tests

Author performs one isolated Source generation and exactly two compilation checks, without importing/calling the candidate, validators, model or verifier. Freeze fifteen source descriptors, full reversible patches, AST function census and thirteen-file byte conservation. Source generation first error is retained and stops that operation. Independent663 must review the production helper/trigger and prepare a bounded batch before executing: ordered least and live9→10 conversion; tie/singleton/allzero draws and subset restriction; clamped loss and zeroNULL; own use versus protected opponent loss; real event/NULL parenting and unconditional activation; synchronous Wolper feedback; finite/new/old entry rejection boundaries. At most one presealed Source battle follows separate release; NOT_HIT is not fabricated as coverage. No Native observation, Expected input, existing battle rerun or formal/general promotion is authorized here.
