# Project Context

This project is about planning and eventually building a reinforcement-learning AI for Backpack Battles.

Before discussing game mechanics, state/action design, environment design, item data, shop rules, combat simulation, or model choices, read:

- `docs/backpack_battles_knowledge_base.md`

Use that file as the local project knowledge base. Do not rely only on prior chat history for Backpack Battles facts.

When updating game facts, use only the current community wiki at `backpackbattles.wiki.gg` and its MediaWiki/Cargo API unless the user explicitly approves another source. Prefer recording source URLs, wiki revision dates, and query dates in the knowledge base.

Important modeling assumptions already captured in the knowledge base:

- `class_id` is part of the observation because class affects available mechanics, items, and starting choices.
- A standalone `subclass_id` should not be exposed to the policy if the subclass is fully represented by a visible owned subclass item.
- The simulator may still track subclass internally for validation and debugging.
- Backpack state must include both spatial layout and item-instance identity.
- Shop state must include gold, reroll count/cost, discounts, reserved items, round, and relevant generation constraints.
- Recipe state must account for adjacency, combine locks, and catalysts.
