# Backpack Battles Knowledge Base for RL Planning

Last updated: 2026-07-03

Source policy: use only the current community wiki at `backpackbattles.wiki.gg` and its MediaWiki/Cargo API as factual inputs for environment design.

## Source Index

| Page / API data | URL | Last wiki revision checked | Use |
| --- | --- | --- | --- |
| Game Mechanics | https://backpackbattles.wiki.gg/wiki/Game_Mechanics | 2026-02-18 | Inventory, shop, rarity odds, combat concepts, ranked overview |
| Items | https://backpackbattles.wiki.gg/wiki/Items | 2026-05-09 | Item taxonomy, sale/sell rule, item database entry point |
| Characters | https://backpackbattles.wiki.gg/wiki/Characters | 2026-04-28 | Current playable classes and shopkeeper/chest facts |
| Recipe | https://backpackbattles.wiki.gg/wiki/Recipe | 2025-10-24 | Combination rules and recipe database entry point |
| Buff | https://backpackbattles.wiki.gg/wiki/Buff | 2024-03-28 | Buff definitions |
| Debuff | https://backpackbattles.wiki.gg/wiki/Debuff | 2024-03-28 | Debuff definitions |
| Effect | https://backpackbattles.wiki.gg/wiki/Effect | 2024-11-08 | Effect-damage concept |
| Cargo Items table | `api.php?action=cargoquery&tables=Items` | queried 2026-07-03 | Structured item fields and counts |
| Cargo Recipes table | `api.php?action=cargoquery&tables=Recipes` | queried 2026-07-03 | Structured recipe fields and counts |

## Current Data Snapshot

Structured wiki.gg Cargo data currently exposes:

- `Items`: 497 records.
- `Recipes`: 224 records.

Item count by class field:

| Class field | Count |
| --- | ---: |
| empty / unspecified | 184 |
| Adventurer | 29 |
| Berserker | 39 |
| Engineer | 43 |
| Mage | 56 |
| Neutral | 35 |
| Pyromancer | 39 |
| Ranger | 38 |
| Reaper | 43 |

Item count by rarity:

| Rarity | Count |
| --- | ---: |
| Common | 27 |
| Rare | 62 |
| Epic | 68 |
| Legendary | 91 |
| Godly | 96 |
| Unique | 148 |
| Varies | 5 |

Item count by main item type:

| Type | Count |
| --- | ---: |
| Accessory | 117 |
| Armor | 14 |
| Bag | 27 |
| Book | 5 |
| Chess Piece | 12 |
| Food | 20 |
| Gemstone | 14 |
| Gloves | 4 |
| Helmet | 9 |
| Pet | 79 |
| Playing Card | 8 |
| Potion | 18 |
| Shield | 10 |
| Shoes | 5 |
| Skill | 58 |
| Spell | 11 |
| Weapon | 111 |

Extra icon/type tags in the structured data include dark, effect, fire, holy, ice, magic, melee, musical, nature, ranged, treasure, and vampiric.

Known Cargo item fields useful for modeling include:

- `name`
- `class`
- `rarity`
- `cost`
- `itemtype`
- `icontype`
- `tags`
- `effect`

Open data task: confirm whether item shape/grid, socket/star/diamond locations, cooldown, damage, stamina, and other numeric fields are available through templates/Cargo tables or must be parsed from individual item pages.

## Playable Classes

The wiki.gg `Characters` page lists these playable classes:

- Ranger
- Reaper
- Pyromancer
- Berserker
- Mage
- Adventurer
- Engineer

All classes use the same starting health, starting gold, and per-round gold schedule according to the `Characters` and `Game Mechanics` pages.

Class pages show that class identity affects strategy, item availability, starting bag choices, and class-specific mechanics. For RL state design, `class_id` should be treated as non-redundant unless the environment is simplified to a classless toy version.

## Inventory Mechanics

Current wiki.gg mechanics:

- Each class starts with a subset of the total inventory tiles.
- There are 63 total tiles.
- Starting usable tiles are in the range of 12 to 14 depending on class/loadout.
- Inventory tiles can be rearranged and rotated.
- Bag items such as Leather Bag, Fanny Pack, Stamina Sack, Potion Belt, and Protective Purse unlock more usable tiles.
- Items placed in storage do not have battle effects until placed in the active inventory.
- Items have tile shapes and spatial synergies.
- Star and diamond markers are used by item effects that care about nearby or affected items.

RL implication:

- A pure list of owned items is insufficient.
- A pure grid is also insufficient unless it preserves item identity and instance-level state.
- The observation should encode both object instances and spatial occupancy.
- Storage and active inventory should be represented separately.

Recommended first serious representation:

```python
backpack = {
    "usable_cells": grid,        # active usable inventory cells
    "storage_cells": grid,       # if storage is explicitly modeled
    "occupancy": grid,           # item instance id or empty
    "items": [
        {
            "item_key": str,
            "item_id": int,
            "name_id": int,
            "class_id": int | None,
            "rarity_id": int,
            "item_type_ids": list[int],
            "icon_type_ids": list[int],
            "tag_ids": list[int],
            "anchor_x": int,
            "anchor_y": int,
            "rotation": int,
            "location": "inventory" | "storage",
            "combine_locked": bool,
            "visible_runtime_state": dict,
        }
    ],
}
```

## Shop Mechanics

Current wiki.gg mechanics:

- Players start with 12 gold and 25 health.
- The shop presents five items.
- Before combat, the player may buy shop items and place them in inventory or storage.
- Items may be sold to the chest for half price rounded up.
- A shop item has a 10% base chance to be on sale at half cost rounded up.
- Sale price equals sell value, so buying a sale item and selling it is gold-neutral.
- The shop can be rerolled.
- The first four rerolls cost 1 gold each; later rerolls cost 2 gold.
- Right-clicking a shop item reserves it so it is not replaced by rerolls or by entering the next round.
- Unique items can appear from round 4.
- Unique item base chance is 2% when entering the shop, not on reroll.
- The player can have only one Unique item at a time.
- Subclass unlock happens at round 8.

Gold received when entering the shop:

| Round | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12-18 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Gold | 12 | 9 | 9 | 9 | 10 | 10 | 11 | 21 | 12 | 12 | 13 | 13-15 by later round |

Exact later-round gold from the page:

| Round | 12 | 13 | 14 | 15 | 16 | 17 | 18 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Gold | 13 | 14 | 14 | 15 | 15 | 15 | 15 |

Starting health / round health values from the page:

| Round | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Health | 25 | 35 | 45 | 55 | 70 | 85 | 100 | 115 | 130 | 150 | 170 | 190 | 210 | 230 | 260 | 290 | 320 | 350 |

Shop rarity chances by round:

| Rarity | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | R9 | R10 | R11 | R12-18 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Common | 90 | 84 | 75 | 64 | 45 | 29 | 20 | 20 | 20 | 20 | 20 | 20 |
| Rare | 10 | 15 | 20 | 25 | 35 | 40 | 35 | 30 | 28 | 25 | 23 | 20 |
| Epic | 0 | 1 | 5 | 10 | 15 | 20 | 25 | 25 | 25 | 25 | 23 | 20 |
| Legendary | 0 | 0 | 0 | 1 | 5 | 10 | 15 | 15 | 15 | 15 | 17 | 20 |
| Godly | 0 | 0 | 0 | 0 | 0 | 1 | 5 | 10 | 12 | 15 | 17 | 20 |

RL implication:

- Gold, reroll count/cost, reserve state, discount state, and round are mandatory state variables.
- The shop generator must know round-dependent rarity odds.
- Unique-item ownership is part of the environment state because it affects future shop generation.
- Subclass items may affect shop availability or chances, so the shop generator must consult owned special items and their effects.

## Recipe Mechanics

Current wiki.gg mechanics:

- Recipe components placed next to each other in the backpack combine during the next shop phase.
- Items can be locked from combining by right-clicking.
- Some recipes use a catalyst. The catalyst remains, while other ingredients are consumed to produce the result.
- Recipe discovery exists in the in-game recipe book.
- The structured `Recipes` table currently has 224 records.

Known structured recipe fields include:

- `recipename`
- `ingredients`
- `catalysts`

RL implication:

- Combination opportunities are derivable from item identities, adjacency, and combine-lock state.
- For training efficiency, a derived `available_recipe_mask` is useful.
- The environment must implement catalyst preservation.
- The action model needs `toggle_combine_lock`.

## Combat Mechanics

Current wiki.gg combat concepts:

- Accuracy determines whether attacks hit or miss.
- Cooldown is the time interval between item activations.
- Critical hits deal double damage.
- Star and diamond markers drive many positional item effects.
- Usually an item can fill one star and one diamond of another item.
- Buffs and debuffs stack and generally last until combat ends unless an item says otherwise.
- Fatigue starts at nightfall and damages both players with increasing intensity.

Buffs listed on wiki.gg:

| Buff | Modeling effect |
| --- | --- |
| Empower | Increases weapon damage per stack |
| Heat | Speeds up item triggering per stack |
| Luck | Increases accuracy per stack |
| Mana | Resource used by Magic items |
| Regeneration | Periodic healing |
| Spikes | Damages melee attackers, capped by incoming damage |
| Vampirism | Heals on melee hit, capped by outgoing damage |

Debuffs listed on wiki.gg:

| Debuff | Modeling effect |
| --- | --- |
| Blind | Reduces accuracy per stack |
| Cold | Slows item triggering per stack |
| Poison | Periodic damage |

Other combat concepts listed on wiki.gg:

- Battle Rage
- Block
- Heal
- Fatigue
- Invulnerability
- Nullify
- Reflect
- Reincarnate
- Resist
- Stun

Effect damage:

- The `Effect` page distinguishes effect damage from weapon damage.
- It generally does not interact with spikes and shields the same way weapon damage does.

Simulation implication:

- The combat engine should be event/timeline based.
- Every item needs trigger rules, cooldown, target rules, resource changes, and positional dependencies.
- Battle logs are necessary for debugging because many effects are conditional and stacked.
- The simulator must control random seeds for accuracy, crits, shop rolls, and other RNG.

## Subclass Modeling Note

Wiki.gg class pages describe subclass items that can do more than direct combat effects. Several subclass items change shop availability or shop probabilities, such as making specific item families available or increasing chances for certain items.

For observation design:

- A separate `subclass_id` is unnecessary if the subclass is fully represented by a visible owned item and the model receives enough item metadata/effect identity.
- The environment transition function must still implement subclass-item effects, especially shop-pool and shop-chance modifications.
- If we simplify item effects to opaque ids, then the special subclass item id is enough.
- If a future rule adds hidden subclass effects not represented by an item, then `subclass_id` becomes necessary again.

Practical compromise:

```python
observation = {
    "class_id": int,
    "items": [...],          # includes subclass item instances
    # no standalone subclass_id in the minimal observation
}
```

The simulator's internal true state may still record the selected subclass for debugging and data validation, but the policy does not need to observe it separately if it is equivalent to owned item state.

## Observation Draft

Minimal player-visible observation:

```python
observation = {
    "round": int,
    "gold": int,
    "health": int,
    "class_id": int,
    "rerolls_this_round": int,
    "reroll_cost": int,
    "unique_item_owned": bool,
    "backpack": {
        "usable_cells": grid,
        "storage": grid_or_list,
        "occupancy": grid,
        "items": [...],
    },
    "shop": {
        "items": [
            {
                "slot": int,
                "item_id": int,
                "price": int,
                "discounted": bool,
                "reserved": bool,
            }
        ],
    },
}
```

Recommended derived features for early learning:

- Legal placement masks.
- Legal recipe masks.
- Empty active cells.
- Empty storage cells.
- Item tag counts.
- Star/diamond coverage matrix.
- Shop affordability mask.
- Sell-value vector.

Do not expose:

- Future shop rolls.
- Hidden random seed.
- Future opponents not visible to the player.
- Opponent hidden data beyond the real game's visible information.

## Action Space Draft

Hierarchical action format:

```python
action = {
    "type": one_of([
        "buy_to_inventory",
        "buy_to_storage",
        "move_item",
        "rotate_item",
        "sell_item",
        "reroll_shop",
        "toggle_shop_reserve",
        "toggle_combine_lock",
        "end_shop",
    ]),
    "args": ...
}
```

Required legality masks:

- Can afford item.
- Item fits active inventory cells.
- Item fits storage if storage has spatial limits.
- No overlap.
- Sell target exists.
- Reroll is affordable.
- Shop slot exists.
- Item can be combine-locked.
- End-shop is available.

## Immediate Wiki.gg-Only Data Tasks

1. Export all `Items` Cargo rows into a local structured file.
2. Export all `Recipes` Cargo rows into a local structured file.
3. Determine whether item grid/shape/star/diamond data is structured or must be parsed from each item page.
4. Determine where starting bag/loadout data is stored.
5. Determine whether shop class pools can be reconstructed from `class`, `Neutral`, empty class, and subclass item effects.
6. Build a small script that can re-query wiki.gg and diff local item/recipe data after patches.
7. For combat, start with a subset of items whose numeric effects are easy to parse, then expand.
