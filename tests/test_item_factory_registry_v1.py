import unittest
from unittest.mock import Mock, call

from basic_backpack_v1 import ITEM_CATALOG, place_item
from battle_initializer_v1 import initialize_battle
from battle_module_v1 import (
    ATTACK_PHASE_ON_ATTACKED,
    ATTACK_PHASE_ON_ATTACK_MISSED,
    AttackEvent,
    AttackReactionContext,
    BattleContext,
    BattleState,
    BuffSlot,
    DebuffSlot,
    ItemActivationContext,
    PlayerState,
)
from item_factory_registry_v1 import (
    ActivationTrigger,
    AfterTimeTrigger,
    AttackEffect,
    AttackMissTrigger,
    Banana,
    Broom,
    BuffRemovalEffect,
    CleanseDebuffEffect,
    CooldownTrigger,
    DEFAULT_ITEM_FACTORIES,
    FoodCooldownTrigger,
    FoodLinkedMeleeAttackEffect,
    Flame,
    GainBlockEffect,
    GainBuffEffect,
    GainMaxHealthEffect,
    Garlic,
    Goobling,
    HealingHerbs,
    HealEffect,
    HolyLinkedHealEffect,
    InflictDebuffEffect,
    ItemAcceleratedCooldownTrigger,
    LinkedWeaponDamageEffect,
    OnAttackedTrigger,
    Pan,
    PocketSand,
    PreventAttackDamageEffect,
    Rat,
    RegenerateStaminaEffect,
    RemoveOpponentBlockEffect,
    RemoveOpponentStaminaEffect,
    ShinyShell,
    Shortbow,
    SlimeActivationTrigger,
    StaminaConsumptionEffect,
    StartOfBattleTrigger,
    Stone,
    Twine,
    UseBuffEffect,
    WalrusTusk,
    WandOfEquilibrium,
    Whetstone,
    WoodenBuckler,
    WoodenSword,
)


def spy_on_activation_dispatch(battle_state):
    original_dispatch = battle_state.dispatch_item_activation
    dispatch_spy = Mock(wraps=original_dispatch)
    battle_state.dispatch_item_activation = dispatch_spy
    return dispatch_spy


class ItemFactoryRegistryV1Test(unittest.TestCase):
    def make_context(
        self,
        frame_delta=0.1,
        health=10,
        max_health=10,
        stamina=0.0,
        max_stamina=0.0,
    ):
        owner = PlayerState(
            player_id=0,
            health=health,
            max_health=max_health,
            stamina=stamina,
            max_stamina=max_stamina,
        )
        opponent = PlayerState(player_id=1, health=10, max_health=10)
        battle_state = BattleState(
            players=[owner, opponent],
            frame_delta=frame_delta,
        )
        return BattleContext(battle_state, None, owner, opponent)

    def make_wand_of_equilibrium_context(
        self,
        *,
        mana=0,
        luck=0,
        regeneration=0,
        empower=0,
        frame_delta=3.3,
    ):
        wand = WandOfEquilibrium(
            item_key="wand_of_equilibrium1",
            player_id=0,
        )
        owner = PlayerState(
            player_id=0,
            health=10,
            max_health=10,
            buffs=BuffSlot(
                Empower=empower,
                Luck=luck,
                Mana=mana,
                Regeneration=regeneration,
            ),
            items={wand.item_key: wand},
        )
        opponent = PlayerState(
            player_id=1,
            health=10,
            max_health=10,
        )
        battle_state = BattleState(
            players=[owner, opponent],
            active_items=[wand],
            frame_delta=frame_delta,
        )
        context = BattleContext(
            battle_state,
            wand,
            owner,
            opponent,
        )
        return wand, context

    def test_default_item_factories_is_a_registry_dict(self):
        self.assertIsInstance(DEFAULT_ITEM_FACTORIES, dict)

    def test_start_of_battle_items_are_registered_with_wiki_metadata(self):
        cases = (
            (
                "pocket_sand",
                PocketSand,
                "Pocket Sand",
                ("Neutral",),
                2,
                ("nature",),
                InflictDebuffEffect,
                "Blind",
                1,
            ),
            (
                "healing_herbs",
                HealingHerbs,
                "Healing Herbs",
                ("Neutral",),
                4,
                ("nature",),
                GainBuffEffect,
                "Regeneration",
                2,
            ),
            (
                "flame",
                Flame,
                "Flame",
                ("Pyromancer",),
                1,
                ("fire",),
                GainBuffEffect,
                "Heat",
                1,
            ),
            (
                "walrus_tusk",
                WalrusTusk,
                "Walrus Tusk",
                ("Neutral",),
                4,
                ("nature",),
                GainBuffEffect,
                "Spikes",
                1,
            ),
        )

        for (
            item_id,
            item_type,
            display_name,
            item_classes,
            cost,
            icon_types,
            effect_type,
            status_name,
            amount,
        ) in cases:
            with self.subTest(item_id=item_id):
                item = DEFAULT_ITEM_FACTORIES[item_id](
                    item_id=item_id,
                    item_key=f"{item_id}1",
                    player_id=0,
                )

                self.assertIsInstance(item, item_type)
                self.assertEqual(item.display_name, display_name)
                self.assertEqual(item.item_classes, item_classes)
                self.assertEqual(item.rarity, "Common")
                self.assertEqual(item.cost, cost)
                self.assertEqual(item.item_types, ("Accessory",))
                self.assertEqual(item.icon_types, icon_types)
                self.assertTrue(item.is_active_item)
                self.assertEqual(item.socket_count, 0)
                self.assertIsInstance(
                    item.triggers[0],
                    StartOfBattleTrigger,
                )
                self.assertIsInstance(item.effects[0], effect_type)
                self.assertEqual(
                    getattr(
                        item.effects[0],
                        "buff_name",
                        getattr(
                            item.effects[0],
                            "debuff_name",
                            None,
                        ),
                    ),
                    status_name,
                )
                self.assertEqual(item.effects[0].amount, amount)

    def test_start_of_battle_trigger_fires_once_only_at_frame_zero(self):
        item = PocketSand(item_key="pocket_sand1", player_id=0)
        context = self.make_context()
        context.item = item
        context.owner.items[item.item_key] = item

        self.assertTrue(item.triggers[0].update(context))
        self.assertFalse(item.triggers[0].update(context))

        late_item = PocketSand(item_key="pocket_sand2", player_id=0)
        context.item = late_item
        context.battle_state.frame = 1
        self.assertFalse(late_item.triggers[0].update(context))

    def test_start_of_battle_items_apply_status_once_and_keep_targets(self):
        cases = (
            (
                PocketSand,
                "debuffs",
                "Blind",
                1,
                "opponent",
            ),
            (
                HealingHerbs,
                "buffs",
                "Regeneration",
                2,
                "owner",
            ),
            (Flame, "buffs", "Heat", 1, "owner"),
            (WalrusTusk, "buffs", "Spikes", 1, "owner"),
        )

        for item_type, slot_name, status_name, amount, target_name in cases:
            with self.subTest(item_type=item_type.__name__):
                item = item_type(
                    item_key=f"{item_type.item_id}1",
                    player_id=0,
                )
                owner = PlayerState(
                    player_id=0,
                    health=10,
                    max_health=10,
                    items={item.item_key: item},
                )
                opponent = PlayerState(
                    player_id=1,
                    health=10,
                    max_health=10,
                )
                target = owner if target_name == "owner" else opponent
                slot = getattr(target, slot_name)
                setattr(slot, status_name, 2)
                battle = BattleState(
                    players=[owner, opponent],
                    active_items=[item],
                )

                battle.step()
                self.assertEqual(
                    getattr(slot, status_name),
                    2 + amount,
                )
                battle.step()
                self.assertEqual(
                    getattr(slot, status_name),
                    2 + amount,
                )

    def test_initializer_runs_all_four_start_of_battle_items_together(self):
        battle = initialize_battle(
            [
                {
                    "player_id": 0,
                    "health": 25,
                    "max_health": 25,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [
                        {
                            "item_id": "pocket_sand",
                            "x": 0,
                            "y": 0,
                            "rotation": 0,
                        },
                        {
                            "item_id": "healing_herbs",
                            "x": 1,
                            "y": 0,
                            "rotation": 0,
                        },
                        {
                            "item_id": "flame",
                            "x": 2,
                            "y": 0,
                            "rotation": 0,
                        },
                        {
                            "item_id": "walrus_tusk",
                            "x": 3,
                            "y": 0,
                            "rotation": 0,
                        },
                    ],
                },
                {
                    "player_id": 1,
                    "health": 25,
                    "max_health": 25,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [],
                },
            ],
            DEFAULT_ITEM_FACTORIES,
            item_catalog=ITEM_CATALOG,
        )

        battle.step()

        self.assertEqual(battle.players[0].buffs.Regeneration, 2)
        self.assertEqual(battle.players[0].buffs.Heat, 1)
        self.assertEqual(battle.players[0].buffs.Spikes, 1)
        self.assertEqual(battle.players[1].debuffs.Blind, 1)
        self.assertEqual(
            [item.item_id for item in battle.active_items],
            [
                "pocket_sand",
                "healing_herbs",
                "flame",
                "walrus_tusk",
            ],
        )

    def test_banana_is_registered_with_metadata_and_components(self):
        banana = DEFAULT_ITEM_FACTORIES["banana"](
            item_id="banana",
            item_key="banana1",
            player_id=0,
        )

        self.assertIsInstance(banana, Banana)
        self.assertEqual(banana.item_id, "banana")
        self.assertEqual(banana.item_key, "banana1")
        self.assertEqual(banana.player_id, 0)
        self.assertEqual(banana.display_name, "Banana")
        self.assertEqual(banana.item_classes, ("Neutral",))
        self.assertEqual(banana.rarity, "Common")
        self.assertEqual(banana.cost, 3)
        self.assertEqual(banana.item_types, ("Food",))
        self.assertEqual(banana.icon_types, ("nature",))
        self.assertTrue(banana.is_active_item)
        self.assertEqual(banana.socket_count, 0)
        self.assertEqual(len(banana.triggers), 1)
        self.assertIsInstance(banana.triggers[0], FoodCooldownTrigger)
        self.assertEqual(banana.triggers[0].cooldown_seconds, 5.0)
        self.assertIsNone(banana.triggers[0].qualifying_food_count)
        self.assertEqual(len(banana.effects), 2)
        self.assertIsInstance(banana.effects[0], HealEffect)
        self.assertEqual(banana.effects[0].amount, 4)
        self.assertIsInstance(banana.effects[1], RegenerateStaminaEffect)
        self.assertEqual(banana.effects[1].amount, 1.0)

    def test_bananas_own_independent_component_instances(self):
        first = Banana(item_key="banana1", player_id=0)
        second = Banana(item_key="banana2", player_id=0)

        self.assertIsNot(first.triggers[0], second.triggers[0])
        self.assertIsNot(first.effects[0], second.effects[0])
        self.assertIsNot(first.effects[1], second.effects[1])

        first.triggers[0].cooldown_progress = 0.5
        first.triggers[0].qualifying_food_count = 2

        self.assertEqual(second.triggers[0].cooldown_progress, 0.0)
        self.assertIsNone(second.triggers[0].qualifying_food_count)

    def test_initializer_builds_banana_as_active_item_with_deduplicated_star_link(
        self,
    ):
        battle = initialize_battle(
            [
                {
                    "player_id": 0,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [
                        {
                            "item_id": "banana",
                            "x": 2,
                            "y": 2,
                            "rotation": 0,
                        },
                        {
                            "item_id": "wooden_sword",
                            "x": 1,
                            "y": 2,
                            "rotation": 0,
                        },
                    ],
                },
                {
                    "player_id": 1,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [],
                },
            ],
            DEFAULT_ITEM_FACTORIES,
            item_catalog=ITEM_CATALOG,
        )

        banana = battle.players[0].items["banana1"]
        sword = battle.players[0].items["wooden_sword1"]

        self.assertIsInstance(banana, Banana)
        self.assertEqual(banana.linked_items, ["wooden_sword1"])
        self.assertEqual(battle.active_items, [banana, sword])

    def test_garlic_is_registered_with_metadata_and_components(self):
        garlic = DEFAULT_ITEM_FACTORIES["garlic"](
            item_id="garlic",
            item_key="garlic1",
            player_id=0,
        )

        self.assertIsInstance(garlic, Garlic)
        self.assertEqual(garlic.item_id, "garlic")
        self.assertEqual(garlic.item_key, "garlic1")
        self.assertEqual(garlic.player_id, 0)
        self.assertEqual(garlic.display_name, "Garlic")
        self.assertEqual(garlic.item_classes, ("Neutral",))
        self.assertEqual(garlic.rarity, "Common")
        self.assertEqual(garlic.cost, 2)
        self.assertEqual(garlic.item_types, ("Food",))
        self.assertEqual(garlic.icon_types, ("nature",))
        self.assertTrue(garlic.is_active_item)
        self.assertEqual(garlic.socket_count, 0)
        self.assertEqual(len(garlic.triggers), 1)
        self.assertIsInstance(garlic.triggers[0], FoodCooldownTrigger)
        self.assertEqual(garlic.triggers[0].cooldown_seconds, 4.0)
        self.assertIsNone(garlic.triggers[0].qualifying_food_count)
        self.assertEqual(len(garlic.effects), 2)
        self.assertIsInstance(garlic.effects[0], GainBlockEffect)
        self.assertEqual(garlic.effects[0].amount, 3)
        self.assertIsInstance(garlic.effects[1], BuffRemovalEffect)
        self.assertEqual(garlic.effects[1].buff_name, "Vampirism")
        self.assertEqual(garlic.effects[1].amount, 1)

    def test_garlics_own_independent_component_instances(self):
        first = Garlic(item_key="garlic1", player_id=0)
        second = Garlic(item_key="garlic2", player_id=0)

        self.assertIsNot(first.triggers[0], second.triggers[0])
        self.assertIsNot(first.effects[0], second.effects[0])
        self.assertIsNot(first.effects[1], second.effects[1])

        first.triggers[0].cooldown_progress = 0.5
        first.triggers[0].qualifying_food_count = 2

        self.assertEqual(second.triggers[0].cooldown_progress, 0.0)
        self.assertIsNone(second.triggers[0].qualifying_food_count)

    def test_initializer_builds_garlic_as_active_item_with_deduplicated_star_link(
        self,
    ):
        battle = initialize_battle(
            [
                {
                    "player_id": 0,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [
                        {
                            "item_id": "garlic",
                            "x": 2,
                            "y": 2,
                            "rotation": 0,
                        },
                        {
                            "item_id": "banana",
                            "x": 3,
                            "y": 2,
                            "rotation": 0,
                        },
                    ],
                },
                {
                    "player_id": 1,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [],
                },
            ],
            DEFAULT_ITEM_FACTORIES,
            item_catalog=ITEM_CATALOG,
        )

        garlic = battle.players[0].items["garlic1"]
        banana = battle.players[0].items["banana1"]

        self.assertIsInstance(garlic, Garlic)
        self.assertEqual(garlic.linked_items, ["banana1"])
        self.assertEqual(battle.active_items, [garlic, banana])

    def test_wooden_buckler_is_registered_with_metadata_and_components(self):
        buckler = DEFAULT_ITEM_FACTORIES["wooden_buckler"](
            item_id="wooden_buckler",
            item_key="wooden_buckler1",
            player_id=0,
        )

        self.assertIsInstance(buckler, WoodenBuckler)
        self.assertEqual(buckler.item_id, "wooden_buckler")
        self.assertEqual(buckler.item_key, "wooden_buckler1")
        self.assertEqual(buckler.player_id, 0)
        self.assertEqual(buckler.display_name, "Wooden Buckler")
        self.assertEqual(buckler.item_classes, ("Neutral",))
        self.assertEqual(buckler.rarity, "Common")
        self.assertEqual(buckler.cost, 4)
        self.assertEqual(buckler.item_types, ("Shield",))
        self.assertEqual(buckler.icon_types, ())
        self.assertFalse(buckler.is_active_item)
        self.assertEqual(buckler.socket_count, 1)
        self.assertEqual(len(buckler.triggers), 1)
        self.assertIsInstance(buckler.triggers[0], OnAttackedTrigger)
        self.assertEqual(buckler.triggers[0].attack_types, ("melee",))
        self.assertEqual(buckler.triggers[0].chance, 0.3)
        self.assertEqual(len(buckler.effects), 2)
        self.assertIsInstance(buckler.effects[0], PreventAttackDamageEffect)
        self.assertEqual(buckler.effects[0].amount, 7)
        self.assertIsInstance(buckler.effects[1], RemoveOpponentStaminaEffect)
        self.assertEqual(buckler.effects[1].amount, 0.3)

    def test_wooden_bucklers_own_independent_component_instances(self):
        first = WoodenBuckler(item_key="wooden_buckler1", player_id=0)
        second = WoodenBuckler(item_key="wooden_buckler2", player_id=0)

        self.assertIsNot(first.triggers[0], second.triggers[0])
        self.assertIsNot(first.effects[0], second.effects[0])
        self.assertIsNot(first.effects[1], second.effects[1])

    def test_initializer_builds_wooden_buckler_as_passive_reaction_item(self):
        battle = initialize_battle(
            [
                {
                    "player_id": 0,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [
                        {
                            "item_id": "wooden_sword",
                            "x": 0,
                            "y": 0,
                            "rotation": 0,
                        },
                    ],
                },
                {
                    "player_id": 1,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [
                        {
                            "item_id": "wooden_buckler",
                            "x": 0,
                            "y": 0,
                            "rotation": 0,
                        },
                    ],
                },
            ],
            DEFAULT_ITEM_FACTORIES,
            item_catalog=ITEM_CATALOG,
        )

        sword = battle.players[0].items["wooden_sword1"]
        buckler = battle.players[1].items["wooden_buckler1"]
        self.assertIsInstance(buckler, WoodenBuckler)
        self.assertEqual(battle.active_items, [sword])
        self.assertEqual(
            battle._get_attack_reaction_items(
                battle.players[1],
                ATTACK_PHASE_ON_ATTACKED,
            ),
            (buckler,),
        )

    def test_wooden_sword_is_registered_with_metadata_and_components(self):
        sword = DEFAULT_ITEM_FACTORIES["wooden_sword"](
            item_id="wooden_sword",
            item_key="wooden_sword1",
            player_id=0,
        )

        self.assertIsInstance(sword, WoodenSword)
        self.assertEqual(sword.item_id, "wooden_sword")
        self.assertEqual(sword.item_key, "wooden_sword1")
        self.assertEqual(sword.player_id, 0)
        self.assertEqual(sword.display_name, "Wooden Sword")
        self.assertEqual(sword.item_classes, ("Neutral",))
        self.assertEqual(sword.rarity, "Common")
        self.assertEqual(sword.cost, 3)
        self.assertEqual(sword.item_types, ("Weapon",))
        self.assertEqual(sword.icon_types, ("melee",))
        self.assertTrue(sword.is_active_item)
        self.assertEqual(sword.socket_count, 1)
        self.assertEqual(len(sword.triggers), 1)
        self.assertIsInstance(sword.triggers[0], CooldownTrigger)
        self.assertEqual(len(sword.effects), 2)
        self.assertIsInstance(sword.effects[0], StaminaConsumptionEffect)
        self.assertIsInstance(sword.effects[1], AttackEffect)

    def test_wooden_swords_own_independent_component_instances(self):
        first = WoodenSword(item_key="wooden_sword1", player_id=0)
        second = WoodenSword(item_key="wooden_sword2", player_id=0)

        self.assertIsNot(first.triggers[0], second.triggers[0])
        self.assertIsNot(first.effects[0], second.effects[0])
        self.assertIsNot(first.effects[1], second.effects[1])

        first.triggers[0].cooldown_progress = 0.5
        self.assertAlmostEqual(second.triggers[0].cooldown_progress, 0.0)

    def test_wooden_sword_does_not_attack_at_battle_start(self):
        rng = Mock()
        sword, context = self.make_wooden_sword_context(
            rng=rng,
            frame_delta=0.1,
            stamina=2.0,
        )
        dispatch_spy = spy_on_activation_dispatch(
            context.battle_state
        )

        sword.activate_item(context)

        self.assertAlmostEqual(sword.triggers[0].cooldown_progress, 0.1)
        self.assertAlmostEqual(context.owner.stamina, 2.0)
        self.assertEqual(context.opponent.health, 10)
        rng.random.assert_not_called()
        rng.randint.assert_not_called()
        dispatch_spy.assert_not_called()

    def test_wooden_sword_pays_stamina_and_attacks_after_cooldown(self):
        rng = Mock()
        rng.random.return_value = 0.0
        rng.randint.return_value = 2
        sword, context = self.make_wooden_sword_context(
            rng=rng,
            frame_delta=1.4,
            stamina=2.0,
        )
        dispatch_spy = spy_on_activation_dispatch(
            context.battle_state
        )

        sword.activate_item(context)

        self.assertAlmostEqual(context.owner.stamina, 1.0)
        self.assertEqual(context.opponent.health, 8)
        self.assertAlmostEqual(sword.triggers[0].cooldown_progress, 0.0)
        rng.random.assert_called_once_with()
        rng.randint.assert_called_once_with(1, 3)
        dispatch_spy.assert_called_once_with(sword)

    def test_wooden_sword_pays_stamina_but_does_not_damage_on_miss(
        self,
    ):
        rng = Mock()
        rng.random.return_value = 0.95
        sword, context = self.make_wooden_sword_context(
            rng=rng,
            frame_delta=1.4,
            stamina=2.0,
        )
        dispatch_spy = spy_on_activation_dispatch(
            context.battle_state
        )

        sword.activate_item(context)

        self.assertAlmostEqual(context.owner.stamina, 1.0)
        self.assertEqual(context.opponent.health, 10)
        rng.random.assert_called_once_with()
        rng.randint.assert_not_called()
        dispatch_spy.assert_called_once_with(sword)

    def test_wooden_sword_skips_attack_and_restarts_cooldown_without_stamina(self):
        rng = Mock()
        sword, context = self.make_wooden_sword_context(
            rng=rng,
            frame_delta=1.4,
            stamina=0.5,
        )
        dispatch_spy = spy_on_activation_dispatch(
            context.battle_state
        )

        sword.activate_item(context)

        self.assertAlmostEqual(context.owner.stamina, 0.5)
        self.assertAlmostEqual(sword.triggers[0].cooldown_progress, 0.0)
        self.assertEqual(context.opponent.health, 10)
        rng.random.assert_not_called()
        rng.randint.assert_not_called()
        dispatch_spy.assert_not_called()

        context.owner.stamina = 2.0
        context.battle_state.frame_delta = 0.1
        sword.activate_item(context)

        self.assertAlmostEqual(sword.triggers[0].cooldown_progress, 0.1)
        rng.random.assert_not_called()

    def test_initializer_builds_wooden_sword_as_an_active_item(self):
        battle = initialize_battle(
            [
                {
                    "player_id": 0,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [
                        {
                            "item_id": "wooden_sword",
                            "x": 0,
                            "y": 0,
                            "rotation": 0,
                        },
                    ],
                },
                {
                    "player_id": 1,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [],
                },
            ],
            DEFAULT_ITEM_FACTORIES,
            item_catalog=ITEM_CATALOG,
        )

        sword = battle.players[0].items["wooden_sword1"]
        self.assertIsInstance(sword, WoodenSword)
        self.assertEqual(battle.active_items, [sword])

    def test_attack_effect_rejects_invalid_damage_ranges(self):
        for arguments in ((-1, 3, 85), (3, 2, 85)):
            with self.subTest(arguments=arguments):
                with self.assertRaises(ValueError):
                    AttackEffect(*arguments)

    def test_attack_effect_rejects_unsupported_attack_type(self):
        effect = AttackEffect(1, 1, 100)
        context = self.make_context()
        context.item = Mock(item_types=("Weapon",))

        with self.assertRaisesRegex(ValueError, "unsupported attack type"):
            effect.apply(context, "magic")

        self.assertFalse(effect.damage_modifier_prepared)

    def test_attack_effect_resolves_each_supported_attack_type(self):
        for attack_type in ("melee", "ranged", "effect"):
            with self.subTest(attack_type=attack_type):
                effect = AttackEffect(2, 3, 85)
                context = self.make_context()
                context.item = Mock(item_types=("Weapon",))
                context.battle_state.resolve_attack = Mock(
                    return_value=Mock(hit=True),
                )

                self.assertTrue(effect.apply(context, attack_type))

                event = (
                    context.battle_state.resolve_attack.call_args.args[0]
                )
                self.assertEqual(event.attack_types, (attack_type,))

    def test_non_weapon_attack_effect_ignores_attack_statuses(self):
        for attack_type in ("melee", "ranged", "effect"):
            with self.subTest(attack_type=attack_type):
                effect = AttackEffect(5, 5, 80)
                effect.stack_damage_modifier(1)
                context = self.make_context()
                context.item = Mock(item_types=("Pet",))
                context.owner.buffs.Empower = 7
                context.owner.buffs.Luck = 4
                context.owner.debuffs.Blind = 1
                context.battle_state.resolve_attack = Mock(
                    return_value=Mock(hit=True),
                )

                self.assertTrue(effect.apply(context, attack_type))

                event = (
                    context.battle_state.resolve_attack.call_args.args[0]
                )
                self.assertEqual(
                    (event.min_damage, event.max_damage),
                    (6, 6),
                )
                self.assertEqual(event.accuracy, 80)

    def test_weapon_attack_effect_applies_attack_statuses(self):
        for attack_type in ("melee", "ranged", "effect"):
            with self.subTest(attack_type=attack_type):
                effect = AttackEffect(5, 5, 80)
                effect.stack_damage_modifier(1)
                context = self.make_context()
                context.item = Mock(item_types=("Weapon",))
                context.owner.buffs.Empower = 7
                context.owner.buffs.Luck = 4
                context.owner.debuffs.Blind = 1
                context.battle_state.resolve_attack = Mock(
                    return_value=Mock(hit=True),
                )

                self.assertTrue(effect.apply(context, attack_type))

                event = (
                    context.battle_state.resolve_attack.call_args.args[0]
                )
                self.assertEqual(
                    (event.min_damage, event.max_damage),
                    (13, 13),
                )
                self.assertEqual(event.accuracy, 95)

    def test_attack_effect_resolves_ranged_hit(self):
        effect = AttackEffect(2, 3, 85)
        effect.stack_damage_modifier(1)
        context = self.make_context()
        context.item = Mock(item_types=("Weapon",))
        context.owner.buffs.Empower = 2
        context.owner.buffs.Luck = 2
        context.owner.debuffs.Blind = 1
        context.battle_state.resolve_attack = Mock(
            return_value=Mock(hit=True),
        )

        result = effect.apply(context, "ranged")

        self.assertTrue(result)
        event = context.battle_state.resolve_attack.call_args.args[0]
        self.assertEqual(event.attack_types, ("ranged",))
        self.assertEqual((event.min_damage, event.max_damage), (5, 6))
        self.assertEqual(event.accuracy, 90)
        self.assertTrue(effect.damage_modifier_prepared)

    def test_ranged_attack_effect_miss_returns_false_without_damage_roll(
        self,
    ):
        effect = AttackEffect(2, 3, 85)
        context = self.make_context()
        context.item = Mock(item_types=("Weapon",))
        context.battle_state.rng = Mock()
        context.battle_state.rng.random.return_value = 0.85

        result = effect.apply(context, "ranged")

        self.assertFalse(result)
        context.battle_state.rng.random.assert_called_once_with()
        context.battle_state.rng.randint.assert_not_called()

    def test_ranged_attack_does_not_apply_spikes_or_vampirism(self):
        effect = AttackEffect(2, 3, 100)
        context = self.make_context(health=5, max_health=10)
        context.item = Mock(item_types=("Weapon",))
        context.owner.buffs.Vampirism = 5
        context.opponent.buffs.Spikes = 5
        context.battle_state.rng = Mock()
        context.battle_state.rng.random.return_value = 0.0
        context.battle_state.rng.randint.return_value = 2

        self.assertTrue(effect.apply(context, "ranged"))

        self.assertEqual(context.owner.health, 5)
        self.assertEqual(context.opponent.health, 8)

    def test_ranged_attack_does_not_trigger_wooden_buckler(self):
        shortbow = Shortbow(item_key="shortbow1", player_id=0)
        buckler = WoodenBuckler(
            item_key="wooden_buckler1",
            player_id=1,
        )
        owner = PlayerState(
            player_id=0,
            health=10,
            max_health=10,
            stamina=5.0,
            max_stamina=5.0,
            items={"shortbow1": shortbow},
        )
        opponent = PlayerState(
            player_id=1,
            health=10,
            max_health=10,
            items={"wooden_buckler1": buckler},
        )
        rng = Mock()
        rng.random.return_value = 0.0
        rng.randint.return_value = 2
        context = BattleContext(
            BattleState(players=[owner, opponent], rng=rng),
            shortbow,
            owner,
            opponent,
        )

        self.assertTrue(shortbow.effects[1].apply(context, "ranged"))

        self.assertEqual(opponent.health, 8)
        self.assertAlmostEqual(owner.stamina, 5.0)
        rng.random.assert_called_once_with()

    def test_shortbow_is_registered_with_metadata_and_components(self):
        shortbow = DEFAULT_ITEM_FACTORIES["shortbow"](
            item_id="shortbow",
            item_key="shortbow1",
            player_id=0,
        )

        self.assertIsInstance(shortbow, Shortbow)
        self.assertEqual(shortbow.display_name, "Shortbow")
        self.assertEqual(shortbow.item_classes, ("Ranger",))
        self.assertEqual(shortbow.rarity, "Common")
        self.assertEqual(shortbow.cost, 4)
        self.assertEqual(shortbow.item_types, ("Weapon",))
        self.assertEqual(shortbow.icon_types, ("ranged",))
        self.assertTrue(shortbow.is_active_item)
        self.assertEqual(shortbow.socket_count, 1)
        self.assertIsInstance(shortbow.triggers[0], CooldownTrigger)
        self.assertAlmostEqual(shortbow.triggers[0].cooldown_seconds, 1.7)
        self.assertIsInstance(
            shortbow.effects[0],
            StaminaConsumptionEffect,
        )
        self.assertAlmostEqual(shortbow.effects[0].stamina_cost, 0.7)
        self.assertIsInstance(shortbow.effects[1], AttackEffect)
        self.assertEqual(
            (
                shortbow.effects[1].min_damage,
                shortbow.effects[1].max_damage,
                shortbow.effects[1].accuracy,
            ),
            (2, 3, 85),
        )

    def test_shortbows_own_independent_component_instances(self):
        first = Shortbow(item_key="shortbow1", player_id=0)
        second = Shortbow(item_key="shortbow2", player_id=0)

        self.assertIsNot(first.triggers[0], second.triggers[0])
        self.assertIsNot(first.effects[0], second.effects[0])
        self.assertIsNot(first.effects[1], second.effects[1])
        first.triggers[0].cooldown_progress = 0.5
        first.effects[1].stack_damage_modifier(2)
        self.assertAlmostEqual(second.triggers[0].cooldown_progress, 0.0)
        self.assertEqual(second.effects[1].damage_modifier, 0)

    def test_shortbow_attacks_after_cooldown(self):
        rng = Mock()
        rng.random.return_value = 0.0
        rng.randint.return_value = 2
        shortbow, context = self.make_shortbow_context(
            rng=rng,
            frame_delta=1.7,
            stamina=2.0,
        )
        dispatch_spy = spy_on_activation_dispatch(
            context.battle_state
        )

        shortbow.activate_item(context)

        self.assertAlmostEqual(context.owner.stamina, 1.3)
        self.assertEqual(context.opponent.health, 8)
        self.assertAlmostEqual(shortbow.triggers[0].cooldown_progress, 0.0)
        rng.random.assert_called_once_with()
        rng.randint.assert_called_once_with(2, 3)
        dispatch_spy.assert_called_once_with(shortbow)

    def test_shortbow_pays_stamina_on_miss(self):
        rng = Mock()
        rng.random.return_value = 0.85
        shortbow, context = self.make_shortbow_context(
            rng=rng,
            frame_delta=1.7,
            stamina=2.0,
        )
        dispatch_spy = spy_on_activation_dispatch(
            context.battle_state
        )

        shortbow.activate_item(context)

        self.assertAlmostEqual(context.owner.stamina, 1.3)
        self.assertEqual(context.opponent.health, 10)
        rng.random.assert_called_once_with()
        rng.randint.assert_not_called()
        dispatch_spy.assert_called_once_with(shortbow)

    def test_shortbow_restarts_cooldown_without_stamina(self):
        rng = Mock()
        shortbow, context = self.make_shortbow_context(
            rng=rng,
            frame_delta=1.7,
            stamina=0.6,
        )
        dispatch_spy = spy_on_activation_dispatch(
            context.battle_state
        )

        shortbow.activate_item(context)

        self.assertAlmostEqual(context.owner.stamina, 0.6)
        self.assertAlmostEqual(shortbow.triggers[0].cooldown_progress, 0.0)
        self.assertEqual(context.opponent.health, 10)
        rng.random.assert_not_called()
        rng.randint.assert_not_called()
        dispatch_spy.assert_not_called()

    def test_initializer_builds_shortbow_as_active_item(self):
        battle = initialize_battle(
            [
                {
                    "player_id": 0,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [
                        {
                            "item_id": "shortbow",
                            "x": 0,
                            "y": 0,
                            "rotation": 0,
                        },
                    ],
                },
                {
                    "player_id": 1,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [],
                },
            ],
            DEFAULT_ITEM_FACTORIES,
            item_catalog=ITEM_CATALOG,
        )

        shortbow = battle.players[0].items["shortbow1"]
        self.assertIsInstance(shortbow, Shortbow)
        self.assertEqual(battle.active_items, [shortbow])

    def test_after_time_trigger_fires_once_after_delay(self):
        trigger = AfterTimeTrigger(delay_seconds=5.0)
        context = self.make_context(frame_delta=2.5)

        self.assertFalse(trigger.update(context))
        self.assertTrue(trigger.update(context))
        self.assertFalse(trigger.update(context))
        self.assertTrue(trigger.has_triggered)

    def test_after_time_trigger_reuses_cooldown_speed_modifiers(self):
        trigger = AfterTimeTrigger(delay_seconds=5.0)
        trigger.stack_speed_modifier(0.2)
        context = self.make_context(frame_delta=1.0)
        context.owner.buffs.Heat = 10
        context.owner.debuffs.Cold = 5

        self.assertFalse(trigger.update(context))

        self.assertAlmostEqual(trigger.cooldown_progress, 1.3)

    def test_after_time_trigger_can_lock_has_triggered_false(self):
        trigger = AfterTimeTrigger(delay_seconds=1.0)
        trigger.lock_has_triggered_false()
        context = self.make_context(frame_delta=1.0)

        self.assertTrue(trigger.update(context))
        self.assertTrue(trigger.update(context))

        self.assertFalse(trigger.has_triggered)
        self.assertTrue(trigger.has_triggered_locked_false)

    def test_after_time_trigger_lock_reopens_trigger_after_first_activation(
        self,
    ):
        trigger = AfterTimeTrigger(delay_seconds=1.0)
        context = self.make_context(frame_delta=1.0)

        self.assertTrue(trigger.update(context))
        self.assertFalse(trigger.update(context))
        trigger.lock_has_triggered_false()
        self.assertTrue(trigger.update(context))

        self.assertFalse(trigger.has_triggered)
        self.assertTrue(trigger.has_triggered_locked_false)

    def test_holy_linked_heal_effect_counts_only_linked_holy_items(self):
        shell = ShinyShell(item_key="shiny_shell1", player_id=0)
        first_holy = ShinyShell(item_key="shiny_shell2", player_id=0)
        second_holy = ShinyShell(item_key="shiny_shell3", player_id=0)
        unlinked_holy = ShinyShell(item_key="shiny_shell4", player_id=0)
        non_holy = WoodenSword(item_key="wooden_sword1", player_id=0)
        shell.linked_items = [
            first_holy.item_key,
            second_holy.item_key,
            non_holy.item_key,
            shell.item_key,
        ]
        owner = PlayerState(
            player_id=0,
            health=0,
            max_health=20,
            items={
                shell.item_key: shell,
                first_holy.item_key: first_holy,
                second_holy.item_key: second_holy,
                unlinked_holy.item_key: unlinked_holy,
                non_holy.item_key: non_holy,
            },
        )
        opponent = PlayerState(player_id=1, health=10, max_health=10)
        battle_state = BattleState(players=[owner, opponent])
        context = BattleContext(
            battle_state,
            shell,
            owner,
            opponent,
        )
        effect = HolyLinkedHealEffect(base_amount=5, amount_per_holy=3)

        self.assertTrue(effect.apply(context))

        self.assertEqual(owner.health, 11)
        self.assertEqual(effect.qualifying_holy_count, 2)
        self.assertEqual(effect.amount, 11)

    def test_holy_linked_heal_effect_prepares_amount_once(self):
        shell = ShinyShell(item_key="shiny_shell1", player_id=0)
        first_holy = ShinyShell(item_key="shiny_shell2", player_id=0)
        shell.add_linked_item(first_holy.item_key)
        owner = PlayerState(
            player_id=0,
            health=0,
            max_health=20,
            items={
                shell.item_key: shell,
                first_holy.item_key: first_holy,
            },
        )
        opponent = PlayerState(player_id=1, health=10, max_health=10)
        battle_state = BattleState(players=[owner, opponent])
        context = BattleContext(
            battle_state,
            shell,
            owner,
            opponent,
        )
        effect = HolyLinkedHealEffect(base_amount=5, amount_per_holy=3)

        self.assertTrue(effect.apply(context))
        second_holy = ShinyShell(item_key="shiny_shell3", player_id=0)
        owner.items[second_holy.item_key] = second_holy
        shell.add_linked_item(second_holy.item_key)
        battle_state.commit_health_reduction(owner, 0, owner.health - 1)
        self.assertTrue(effect.apply(context))

        self.assertEqual(owner.health, 9)
        self.assertEqual(effect.qualifying_holy_count, 1)
        self.assertEqual(effect.amount, 8)

    def test_shiny_shell_is_registered_with_metadata_and_components(self):
        shell = DEFAULT_ITEM_FACTORIES["shiny_shell"](
            item_id="shiny_shell",
            item_key="shiny_shell1",
            player_id=0,
        )
        second_shell = ShinyShell(item_key="shiny_shell2", player_id=0)

        self.assertIsInstance(shell, ShinyShell)
        self.assertEqual(shell.display_name, "Shiny Shell")
        self.assertEqual(shell.item_classes, ("Neutral",))
        self.assertEqual(shell.rarity, "Common")
        self.assertEqual(shell.cost, 2)
        self.assertEqual(shell.item_types, ("Accessory",))
        self.assertEqual(shell.icon_types, ("nature", "holy"))
        self.assertTrue(shell.is_active_item)
        self.assertEqual(shell.socket_count, 0)
        self.assertIsInstance(shell.triggers[0], AfterTimeTrigger)
        self.assertAlmostEqual(shell.triggers[0].cooldown_seconds, 5.0)
        self.assertIsInstance(shell.effects[0], HolyLinkedHealEffect)
        self.assertEqual(shell.effects[0].base_amount, 5)
        self.assertEqual(shell.effects[0].amount_per_holy, 3)
        self.assertIsNot(shell.triggers[0], second_shell.triggers[0])
        self.assertIsNot(shell.effects[0], second_shell.effects[0])

    def test_shiny_shell_triggers_once_and_does_not_retry_at_full_health(self):
        shell = ShinyShell(item_key="shiny_shell1", player_id=0)
        owner = PlayerState(
            player_id=0,
            health=10,
            max_health=10,
            items={shell.item_key: shell},
        )
        opponent = PlayerState(player_id=1, health=10, max_health=10)
        battle_state = BattleState(
            players=[owner, opponent],
            active_items=[shell],
            frame_delta=5.0,
        )
        context = BattleContext(
            battle_state,
            shell,
            owner,
            opponent,
        )
        dispatch_spy = spy_on_activation_dispatch(battle_state)

        shell.activate_item(context)
        battle_state.commit_health_reduction(owner, 0, owner.health - 1)
        shell.activate_item(context)

        self.assertEqual(owner.health, 1)
        self.assertTrue(shell.triggers[0].has_triggered)
        dispatch_spy.assert_called_once_with(shell)

    def test_initializer_links_shiny_shells_left_and_right_stars(self):
        battle = initialize_battle(
            [
                {
                    "player_id": 0,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [
                        {
                            "item_id": "shiny_shell",
                            "x": x,
                            "y": 0,
                            "rotation": 0,
                        }
                        for x in (1, 2, 3)
                    ],
                },
                {
                    "player_id": 1,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [],
                },
            ],
            DEFAULT_ITEM_FACTORIES,
            item_catalog=ITEM_CATALOG,
        )

        center_shell = battle.players[0].items["shiny_shell2"]
        self.assertEqual(
            set(center_shell.linked_items),
            {"shiny_shell1", "shiny_shell3"},
        )

    def test_initializer_builds_shiny_shell_as_active_item(self):
        battle = initialize_battle(
            [
                {
                    "player_id": 0,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [
                        {
                            "item_id": "shiny_shell",
                            "x": 0,
                            "y": 0,
                            "rotation": 0,
                        }
                    ],
                },
                {
                    "player_id": 1,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [],
                },
            ],
            DEFAULT_ITEM_FACTORIES,
            item_catalog=ITEM_CATALOG,
        )

        shell = battle.players[0].items["shiny_shell1"]
        self.assertIsInstance(shell, ShinyShell)
        self.assertEqual(battle.active_items, [shell])

    def test_wand_of_equilibrium_is_registered_with_metadata_and_components(
        self,
    ):
        wand = DEFAULT_ITEM_FACTORIES["wand_of_equilibrium"](
            item_id="wand_of_equilibrium",
            item_key="wand_of_equilibrium1",
            player_id=0,
        )
        second_wand = WandOfEquilibrium(
            item_key="wand_of_equilibrium2",
            player_id=0,
        )

        self.assertIsInstance(wand, WandOfEquilibrium)
        self.assertEqual(wand.item_id, "wand_of_equilibrium")
        self.assertEqual(wand.display_name, "Wand of Equilibrium")
        self.assertEqual(wand.item_classes, ("Mage",))
        self.assertEqual(wand.rarity, "Common")
        self.assertEqual(wand.cost, 4)
        self.assertEqual(wand.item_types, ("Accessory",))
        self.assertEqual(wand.icon_types, ())
        self.assertTrue(wand.is_active_item)
        self.assertEqual(wand.socket_count, 0)
        self.assertIsInstance(wand.triggers[0], CooldownTrigger)
        self.assertAlmostEqual(wand.triggers[0].cooldown_seconds, 3.3)
        self.assertEqual(len(wand.effects), 7)
        self.assertTrue(
            all(
                isinstance(effect, GainBuffEffect)
                for effect in wand.effects[:3]
            )
        )
        self.assertTrue(
            all(
                isinstance(effect, UseBuffEffect)
                for effect in wand.effects[3:6]
            )
        )
        self.assertIsInstance(wand.effects[6], GainBuffEffect)
        self.assertEqual(
            [effect.buff_name for effect in wand.effects],
            [
                "Mana",
                "Luck",
                "Regeneration",
                "Mana",
                "Luck",
                "Regeneration",
                "Empower",
            ],
        )
        self.assertEqual(
            [effect.amount for effect in wand.effects],
            [1, 1, 1, 1, 1, 1, 1],
        )
        self.assertIsNot(wand.triggers[0], second_wand.triggers[0])
        for first_effect, second_effect in zip(
            wand.effects,
            second_wand.effects,
        ):
            self.assertIsNot(first_effect, second_effect)

    def test_wand_of_equilibrium_gains_the_least_resource(self):
        cases = (
            ((0, 2, 3), (1, 2, 3)),
            ((3, 0, 2), (3, 1, 2)),
            ((2, 3, 0), (2, 3, 1)),
        )
        for initial, expected in cases:
            with self.subTest(initial=initial):
                wand, context = self.make_wand_of_equilibrium_context(
                    mana=initial[0],
                    luck=initial[1],
                    regeneration=initial[2],
                )

                wand.activate_item(context)

                self.assertEqual(
                    (
                        context.owner.buffs.Mana,
                        context.owner.buffs.Luck,
                        context.owner.buffs.Regeneration,
                    ),
                    expected,
                )
                self.assertEqual(context.owner.buffs.Empower, 0)

    def test_wand_of_equilibrium_uses_stable_order_for_minimum_ties(
        self,
    ):
        wand, context = self.make_wand_of_equilibrium_context()

        wand.activate_item(context)
        self.assertEqual(
            (
                context.owner.buffs.Mana,
                context.owner.buffs.Luck,
                context.owner.buffs.Regeneration,
            ),
            (1, 0, 0),
        )
        wand.activate_item(context)
        self.assertEqual(
            (
                context.owner.buffs.Mana,
                context.owner.buffs.Luck,
                context.owner.buffs.Regeneration,
            ),
            (1, 1, 0),
        )
        wand.activate_item(context)

        self.assertEqual(
            (
                context.owner.buffs.Mana,
                context.owner.buffs.Luck,
                context.owner.buffs.Regeneration,
            ),
            (1, 1, 1),
        )

    def test_wand_of_equilibrium_checks_threshold_after_gain(self):
        wand, context = self.make_wand_of_equilibrium_context(
            mana=9,
            luck=9,
            regeneration=9,
        )

        wand.activate_item(context)

        self.assertEqual(
            (
                context.owner.buffs.Mana,
                context.owner.buffs.Luck,
                context.owner.buffs.Regeneration,
            ),
            (9, 9, 9),
        )
        self.assertEqual(context.owner.buffs.Empower, 1)

    def test_wand_of_equilibrium_uses_the_most_resource(self):
        wand, context = self.make_wand_of_equilibrium_context(
            mana=12,
            luck=6,
            regeneration=4,
        )

        wand.activate_item(context)

        self.assertEqual(
            (
                context.owner.buffs.Mana,
                context.owner.buffs.Luck,
                context.owner.buffs.Regeneration,
            ),
            (11, 6, 5),
        )
        self.assertEqual(context.owner.buffs.Empower, 1)

    def test_wand_of_equilibrium_uses_stable_order_for_maximum_ties(
        self,
    ):
        wand, context = self.make_wand_of_equilibrium_context(
            mana=12,
            luck=12,
            regeneration=11,
        )

        wand.activate_item(context)

        self.assertEqual(
            (
                context.owner.buffs.Mana,
                context.owner.buffs.Luck,
                context.owner.buffs.Regeneration,
            ),
            (11, 12, 12),
        )
        self.assertEqual(context.owner.buffs.Empower, 1)

    def test_wand_of_equilibrium_does_not_convert_below_threshold(self):
        wand, context = self.make_wand_of_equilibrium_context(
            mana=8,
            luck=8,
            regeneration=8,
        )

        wand.activate_item(context)

        self.assertEqual(
            (
                context.owner.buffs.Mana,
                context.owner.buffs.Luck,
                context.owner.buffs.Regeneration,
            ),
            (9, 8, 8),
        )
        self.assertEqual(context.owner.buffs.Empower, 0)

    def test_wand_of_equilibrium_emits_once_per_cooldown_activation(
        self,
    ):
        wand, context = self.make_wand_of_equilibrium_context(
            frame_delta=3.2,
        )
        dispatch_spy = spy_on_activation_dispatch(
            context.battle_state
        )

        wand.activate_item(context)
        dispatch_spy.assert_not_called()

        context.battle_state.frame_delta = 0.1
        wand.activate_item(context)
        dispatch_spy.assert_called_once_with(wand)

        context.battle_state.frame_delta = 3.3
        wand.activate_item(context)
        self.assertEqual(
            dispatch_spy.call_args_list,
            [call(wand), call(wand)],
        )

    def test_initializer_builds_wand_of_equilibrium_as_active_item(self):
        battle = initialize_battle(
            [
                {
                    "player_id": 0,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [
                        {
                            "item_id": "wand_of_equilibrium",
                            "x": 0,
                            "y": 0,
                            "rotation": 0,
                        }
                    ],
                },
                {
                    "player_id": 1,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [],
                },
            ],
            DEFAULT_ITEM_FACTORIES,
            item_catalog=ITEM_CATALOG,
        )

        wand = battle.players[0].items["wand_of_equilibrium1"]
        self.assertIsInstance(wand, WandOfEquilibrium)
        self.assertEqual(battle.active_items, [wand])

    def test_wand_of_equilibrium_catalog_rotates_vertical_shape(self):
        expected_cells = {
            0: [(3, 4), (3, 3)],
            90: [(2, 3), (3, 3)],
            180: [(3, 2), (3, 3)],
            270: [(4, 3), (3, 3)],
        }

        for rotation, occupied_cells in expected_cells.items():
            with self.subTest(rotation=rotation):
                placed = place_item(
                    ITEM_CATALOG["wand_of_equilibrium"],
                    {
                        "item_key": "wand_of_equilibrium1",
                        "x": 3,
                        "y": 3,
                        "rotation": rotation,
                    },
                )

                self.assertEqual(
                    placed["occupied_cells"],
                    occupied_cells,
                )
                self.assertEqual(placed["star_cells"], [])
                self.assertEqual(placed["diamond_cells"], [])
                self.assertEqual(placed["triangle_cells"], [])

    def test_linked_weapon_damage_effect_rejects_invalid_amounts(self):
        for amount in (True, 1.0, -1):
            with self.subTest(amount=amount):
                with self.assertRaises(ValueError):
                    LinkedWeaponDamageEffect(amount)

    def test_linked_weapon_damage_effect_buffs_all_linked_attack_effects(
        self,
    ):
        whetstone = Whetstone(item_key="whetstone1", player_id=0)
        sword = WoodenSword(item_key="wooden_sword1", player_id=0)
        shortbow = Shortbow(item_key="shortbow1", player_id=0)
        pan = Pan(item_key="pan1", player_id=0)
        whetstone.linked_items = [
            sword.item_key,
            shortbow.item_key,
            pan.item_key,
        ]
        owner = PlayerState(
            player_id=0,
            health=10,
            max_health=10,
            items={
                whetstone.item_key: whetstone,
                sword.item_key: sword,
                shortbow.item_key: shortbow,
                pan.item_key: pan,
            },
        )
        opponent = PlayerState(player_id=1, health=10, max_health=10)
        context = BattleContext(
            BattleState(players=[owner, opponent]),
            whetstone,
            owner,
            opponent,
        )
        effect = LinkedWeaponDamageEffect(amount=1)

        self.assertTrue(effect.apply(context))

        self.assertEqual(sword.effects[1].damage_modifier, 1)
        self.assertEqual(shortbow.effects[1].damage_modifier, 1)
        self.assertEqual(pan.effects[1].damage_modifier, 1)
        self.assertEqual(
            (sword.effects[1].min_damage, sword.effects[1].max_damage),
            (1, 3),
        )
        self.assertEqual(
            (
                shortbow.effects[1].min_damage,
                shortbow.effects[1].max_damage,
            ),
            (2, 3),
        )

    def test_linked_weapon_damage_effect_ignores_non_weapons_and_unlinked_weapons(
        self,
    ):
        whetstone = Whetstone(item_key="whetstone1", player_id=0)
        shell = ShinyShell(item_key="shiny_shell1", player_id=0)
        rat = Rat(item_key="rat1", player_id=0)
        sword = WoodenSword(item_key="wooden_sword1", player_id=0)
        whetstone.add_linked_item(shell.item_key)
        whetstone.add_linked_item(rat.item_key)
        owner = PlayerState(
            player_id=0,
            health=10,
            max_health=10,
            items={
                whetstone.item_key: whetstone,
                shell.item_key: shell,
                rat.item_key: rat,
                sword.item_key: sword,
            },
        )
        opponent = PlayerState(player_id=1, health=10, max_health=10)
        context = BattleContext(
            BattleState(players=[owner, opponent]),
            whetstone,
            owner,
            opponent,
        )

        self.assertFalse(whetstone.effects[0].apply(context))

        self.assertEqual(sword.effects[1].damage_modifier, 0)
        self.assertEqual(rat.effects[0].damage_modifier, 0)

    def test_whetstone_is_registered_with_metadata_and_components(self):
        whetstone = DEFAULT_ITEM_FACTORIES["whetstone"](
            item_id="whetstone",
            item_key="whetstone1",
            player_id=0,
        )
        second = Whetstone(item_key="whetstone2", player_id=0)

        self.assertIsInstance(whetstone, Whetstone)
        self.assertEqual(whetstone.display_name, "Whetstone")
        self.assertEqual(whetstone.item_classes, ("Neutral",))
        self.assertEqual(whetstone.rarity, "Common")
        self.assertEqual(whetstone.cost, 4)
        self.assertEqual(whetstone.item_types, ("Accessory",))
        self.assertEqual(whetstone.icon_types, ())
        self.assertTrue(whetstone.is_active_item)
        self.assertEqual(whetstone.socket_count, 0)
        self.assertIsInstance(whetstone.triggers[0], StartOfBattleTrigger)
        self.assertIsInstance(
            whetstone.effects[0],
            LinkedWeaponDamageEffect,
        )
        self.assertEqual(whetstone.effects[0].amount, 1)
        self.assertIsNot(whetstone.triggers[0], second.triggers[0])
        self.assertIsNot(whetstone.effects[0], second.effects[0])

    def test_whetstone_triggers_once(self):
        whetstone = Whetstone(item_key="whetstone1", player_id=0)
        sword = WoodenSword(item_key="wooden_sword1", player_id=0)
        whetstone.add_linked_item(sword.item_key)
        owner = PlayerState(
            player_id=0,
            health=10,
            max_health=10,
            items={
                whetstone.item_key: whetstone,
                sword.item_key: sword,
            },
        )
        opponent = PlayerState(player_id=1, health=10, max_health=10)
        context = BattleContext(
            BattleState(players=[owner, opponent]),
            whetstone,
            owner,
            opponent,
        )

        whetstone.activate_item(context)
        whetstone.activate_item(context)

        self.assertEqual(sword.effects[1].damage_modifier, 1)
        self.assertTrue(whetstone.triggers[0].has_triggered)

    def test_initializer_links_whetstone_left_and_right_stars(self):
        battle = initialize_battle(
            [
                {
                    "player_id": 0,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [
                        {
                            "item_id": "wooden_sword",
                            "x": 1,
                            "y": 0,
                            "rotation": 0,
                        },
                        {
                            "item_id": "whetstone",
                            "x": 2,
                            "y": 0,
                            "rotation": 0,
                        },
                        {
                            "item_id": "shortbow",
                            "x": 3,
                            "y": 0,
                            "rotation": 0,
                        },
                    ],
                },
                {
                    "player_id": 1,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [],
                },
            ],
            DEFAULT_ITEM_FACTORIES,
            item_catalog=ITEM_CATALOG,
        )

        whetstone = battle.players[0].items["whetstone1"]
        self.assertEqual(
            set(whetstone.linked_items),
            {"wooden_sword1", "shortbow1"},
        )

    def test_initializer_builds_whetstone_as_active_item(self):
        battle = initialize_battle(
            [
                {
                    "player_id": 0,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [
                        {
                            "item_id": "whetstone",
                            "x": 0,
                            "y": 0,
                            "rotation": 0,
                        }
                    ],
                },
                {
                    "player_id": 1,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [],
                },
            ],
            DEFAULT_ITEM_FACTORIES,
            item_catalog=ITEM_CATALOG,
        )

        whetstone = battle.players[0].items["whetstone1"]
        self.assertIsInstance(whetstone, Whetstone)
        self.assertEqual(battle.active_items, [whetstone])

    def test_remove_opponent_block_effect_validates_and_clamps_amount(self):
        for amount in (True, 1.0, -1):
            with self.subTest(amount=amount):
                with self.assertRaises(ValueError):
                    RemoveOpponentBlockEffect(amount)

        context = self.make_context()
        context.opponent.block = 3
        effect = RemoveOpponentBlockEffect(amount=4)

        self.assertTrue(effect.apply(context))
        self.assertEqual(context.opponent.block, 0)
        self.assertFalse(effect.apply(context))

    def test_stone_is_registered_with_metadata_and_components(self):
        stone = DEFAULT_ITEM_FACTORIES["stone"](
            item_id="stone",
            item_key="stone1",
            player_id=0,
        )
        second = Stone(item_key="stone2", player_id=0)

        self.assertIsInstance(stone, Stone)
        self.assertEqual(stone.display_name, "Stone")
        self.assertEqual(stone.item_classes, ("Neutral",))
        self.assertEqual(stone.rarity, "Common")
        self.assertEqual(stone.cost, 1)
        self.assertEqual(stone.item_types, ("Weapon",))
        self.assertEqual(stone.icon_types, ("ranged", "nature"))
        self.assertTrue(stone.is_active_item)
        self.assertEqual(stone.socket_count, 0)
        self.assertIsInstance(stone.triggers[0], AfterTimeTrigger)
        self.assertAlmostEqual(stone.triggers[0].cooldown_seconds, 2.5)
        self.assertFalse(stone.triggers[0].has_triggered_locked_false)
        self.assertIsInstance(stone.effects[0], AttackEffect)
        self.assertEqual(
            (
                stone.effects[0].min_damage,
                stone.effects[0].max_damage,
                stone.effects[0].accuracy,
            ),
            (2, 4, 70),
        )
        self.assertIsInstance(
            stone.effects[1],
            RemoveOpponentBlockEffect,
        )
        self.assertEqual(stone.effects[1].amount, 4)
        self.assertIsNot(stone.triggers[0], second.triggers[0])
        self.assertIsNot(stone.effects[0], second.effects[0])
        self.assertIsNot(stone.effects[1], second.effects[1])

    def test_stone_hits_once_and_removes_block_after_attack(self):
        rng = Mock()
        rng.random.return_value = 0.0
        rng.randint.return_value = 2
        stone = Stone(item_key="stone1", player_id=0)
        owner = PlayerState(
            player_id=0,
            health=10,
            max_health=10,
            items={stone.item_key: stone},
        )
        opponent = PlayerState(
            player_id=1,
            health=10,
            max_health=10,
            block=10,
        )
        context = BattleContext(
            BattleState(
                players=[owner, opponent],
                active_items=[stone],
                frame_delta=2.5,
                rng=rng,
            ),
            stone,
            owner,
            opponent,
        )
        dispatch_spy = spy_on_activation_dispatch(
            context.battle_state
        )

        stone.activate_item(context)
        stone.activate_item(context)

        self.assertEqual(opponent.block, 4)
        self.assertEqual(opponent.health, 10)
        self.assertTrue(stone.triggers[0].has_triggered)
        rng.random.assert_called_once_with()
        rng.randint.assert_called_once_with(2, 4)
        dispatch_spy.assert_called_once_with(stone)

    def test_stone_miss_consumes_its_only_throw_without_removing_block(self):
        rng = Mock()
        rng.random.return_value = 0.70
        stone = Stone(item_key="stone1", player_id=0)
        owner = PlayerState(
            player_id=0,
            health=10,
            max_health=10,
            items={stone.item_key: stone},
        )
        opponent = PlayerState(
            player_id=1,
            health=10,
            max_health=10,
            block=10,
        )
        context = BattleContext(
            BattleState(
                players=[owner, opponent],
                active_items=[stone],
                frame_delta=2.5,
                rng=rng,
            ),
            stone,
            owner,
            opponent,
        )
        dispatch_spy = spy_on_activation_dispatch(
            context.battle_state
        )

        stone.activate_item(context)
        stone.activate_item(context)

        self.assertEqual(opponent.block, 10)
        self.assertEqual(opponent.health, 10)
        self.assertTrue(stone.triggers[0].has_triggered)
        rng.random.assert_called_once_with()
        rng.randint.assert_not_called()
        dispatch_spy.assert_called_once_with(stone)

    def test_whetstone_can_buff_stone(self):
        whetstone = Whetstone(item_key="whetstone1", player_id=0)
        stone = Stone(item_key="stone1", player_id=0)
        whetstone.add_linked_item(stone.item_key)
        owner = PlayerState(
            player_id=0,
            health=10,
            max_health=10,
            items={
                whetstone.item_key: whetstone,
                stone.item_key: stone,
            },
        )
        opponent = PlayerState(player_id=1, health=10, max_health=10)
        context = BattleContext(
            BattleState(players=[owner, opponent]),
            whetstone,
            owner,
            opponent,
        )

        whetstone.activate_item(context)

        self.assertEqual(stone.effects[0].damage_modifier, 1)

    def test_initializer_builds_stone_as_active_item(self):
        battle = initialize_battle(
            [
                {
                    "player_id": 0,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [
                        {
                            "item_id": "stone",
                            "x": 0,
                            "y": 0,
                            "rotation": 0,
                        }
                    ],
                },
                {
                    "player_id": 1,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [],
                },
            ],
            DEFAULT_ITEM_FACTORIES,
            item_catalog=ITEM_CATALOG,
        )

        stone = battle.players[0].items["stone1"]
        self.assertIsInstance(stone, Stone)
        self.assertEqual(battle.active_items, [stone])

    def test_cooldown_trigger_starts_empty_and_does_not_trigger_immediately(self):
        trigger = CooldownTrigger(cooldown_seconds=1.4)

        result = trigger.update(self.make_context(frame_delta=0.1))

        self.assertFalse(result)
        self.assertAlmostEqual(trigger.cooldown_progress, 0.1)

    def test_cooldown_trigger_fires_when_accumulated_progress_reaches_threshold(self):
        trigger = CooldownTrigger(cooldown_seconds=1.0)
        context = self.make_context(frame_delta=0.25)

        results = [trigger.update(context) for _ in range(4)]

        self.assertEqual(results, [False, False, False, True])
        self.assertAlmostEqual(trigger.cooldown_progress, 0.0)

    def test_cooldown_trigger_reads_current_frame_delta_on_every_update(self):
        trigger = CooldownTrigger(cooldown_seconds=1.0)
        context = self.make_context(frame_delta=0.25)

        first_result = trigger.update(context)
        context.battle_state.frame_delta = 0.75
        second_result = trigger.update(context)

        self.assertFalse(first_result)
        self.assertTrue(second_result)
        self.assertAlmostEqual(trigger.cooldown_progress, 0.0)

    def test_cooldown_trigger_cancels_heat_and_cold_stacks(self):
        cases = (
            (5, 5, 0.5),
            (8, 3, 0.55),
            (3, 8, 0.5 / 1.1),
        )

        for heat, cold, expected_progress in cases:
            with self.subTest(heat=heat, cold=cold):
                trigger = CooldownTrigger(cooldown_seconds=1.0)
                context = self.make_context(frame_delta=0.5)
                context.owner.buffs.Heat = heat
                context.owner.debuffs.Cold = cold

                self.assertFalse(trigger.update(context))
                self.assertAlmostEqual(
                    trigger.cooldown_progress,
                    expected_progress,
                )

    def test_cooldown_trigger_reads_current_heat_and_cold_each_frame(self):
        trigger = CooldownTrigger(cooldown_seconds=1.0)
        context = self.make_context(frame_delta=0.25)
        context.owner.buffs.Heat = 10

        self.assertFalse(trigger.update(context))
        self.assertAlmostEqual(trigger.cooldown_progress, 0.3)

        context.owner.buffs.Heat = 0
        context.owner.debuffs.Cold = 10

        self.assertFalse(trigger.update(context))
        self.assertAlmostEqual(trigger.cooldown_progress, 0.3 + 0.25 / 1.2)

    def test_cooldown_trigger_never_reverses_progress_from_high_cold(self):
        trigger = CooldownTrigger(cooldown_seconds=1.0)
        context = self.make_context(frame_delta=0.3)
        context.owner.debuffs.Cold = 100

        self.assertFalse(trigger.update(context))
        self.assertAlmostEqual(trigger.cooldown_progress, 0.1)

    def test_cooldown_clamps_positive_heat_cold_difference(self):
        trigger = CooldownTrigger(cooldown_seconds=100.0)
        context = self.make_context(frame_delta=1.0)
        context.owner.buffs.Heat = 1000

        self.assertFalse(trigger.update(context))

        self.assertAlmostEqual(trigger.cooldown_progress, 11.0)

    def test_cooldown_clamps_negative_heat_cold_difference(self):
        trigger = CooldownTrigger(cooldown_seconds=100.0)
        context = self.make_context(frame_delta=1.0)
        context.owner.debuffs.Cold = 1000

        self.assertFalse(trigger.update(context))

        self.assertAlmostEqual(trigger.cooldown_progress, 1.0 / 11.0)

    def test_cooldown_adds_speed_modifier_after_status_cap(self):
        trigger = CooldownTrigger(cooldown_seconds=100.0)
        trigger.stack_speed_modifier(2.0)
        trigger.speed_modifiers_prepared = True
        context = self.make_context(frame_delta=1.0)
        context.owner.buffs.Heat = 1000

        self.assertFalse(trigger.update(context))

        self.assertAlmostEqual(trigger.cooldown_progress, 13.0)

    def test_cooldown_uses_slower_formula_after_status_cap_and_modifier(self):
        trigger = CooldownTrigger(cooldown_seconds=100.0)
        trigger.stack_speed_modifier(2.0)
        trigger.speed_modifiers_prepared = True
        context = self.make_context(frame_delta=1.0)
        context.owner.debuffs.Cold = 1000

        self.assertFalse(trigger.update(context))

        self.assertAlmostEqual(trigger.cooldown_progress, 1.0 / 9.0)

    def test_cooldown_trigger_preserves_overflow_progress(self):
        trigger = CooldownTrigger(cooldown_seconds=1.0)
        context = self.make_context(frame_delta=0.75)

        self.assertFalse(trigger.update(context))
        context.battle_state.frame_delta = 0.5

        self.assertTrue(trigger.update(context))
        self.assertAlmostEqual(trigger.cooldown_progress, 0.25)

    def test_cooldown_trigger_instances_have_independent_progress(self):
        first_trigger = CooldownTrigger(cooldown_seconds=1.0)
        second_trigger = CooldownTrigger(cooldown_seconds=1.0)

        first_trigger.update(self.make_context(frame_delta=0.25))

        self.assertAlmostEqual(first_trigger.cooldown_progress, 0.25)
        self.assertAlmostEqual(second_trigger.cooldown_progress, 0.0)

    def test_item_accelerated_cooldown_rejects_invalid_conditions(self):
        invalid_conditions = (
            None,
            (),
            [None],
            [{"unknown": "Pet", "accelerate": 0.15}],
            [{"item_type": "", "accelerate": 0.15}],
            [{"item_type": "Pet"}],
            [{"item_type": "Pet", "accelerate": True}],
            [{"item_type": "Pet", "accelerate": -0.1}],
            [{"item_type": "Pet", "accelerate": "0.15"}],
        )

        for conditions in invalid_conditions:
            with self.subTest(conditions=conditions):
                with self.assertRaises(ValueError):
                    ItemAcceleratedCooldownTrigger(3.3, conditions)

    def test_item_accelerated_cooldown_requires_all_condition_fields(self):
        trigger = ItemAcceleratedCooldownTrigger(
            100.0,
            [
                {
                    "class": "Ranger",
                    "rarity": "Common",
                    "item_type": "Pet",
                    "icon_type": "nature",
                    "accelerate": 0.20,
                }
            ],
        )
        matching = Mock(
            item_classes=("Ranger",),
            rarity="Common",
            item_types=("Pet",),
            icon_types=("nature",),
        )
        wrong_rarity = Mock(
            item_classes=("Ranger",),
            rarity="Rare",
            item_types=("Pet",),
            icon_types=("nature",),
        )
        context = self.make_context(frame_delta=1.0)
        context.item = Mock(linked_items=["matching", "wrong_rarity"])
        context.owner.items = {
            "matching": matching,
            "wrong_rarity": wrong_rarity,
        }

        self.assertFalse(trigger.update(context))

        self.assertAlmostEqual(trigger.item_acceleration, 0.20)
        self.assertAlmostEqual(trigger.speed_modifiers, 0.20)
        self.assertAlmostEqual(trigger.cooldown_progress, 1.20)

    def test_item_accelerated_cooldown_without_filters_matches_all_items(
        self,
    ):
        trigger = ItemAcceleratedCooldownTrigger(
            100.0,
            [{"accelerate": 0.10}],
        )
        context = self.make_context(frame_delta=1.0)
        context.item = Mock(linked_items=["first", "second"])
        context.owner.items = {
            "first": Mock(),
            "second": Mock(),
        }

        self.assertFalse(trigger.update(context))

        self.assertAlmostEqual(trigger.item_acceleration, 0.20)
        self.assertAlmostEqual(trigger.speed_modifiers, 0.20)
        self.assertAlmostEqual(trigger.cooldown_progress, 1.20)

    def test_item_accelerated_cooldown_adds_each_matching_condition(self):
        conditions = [
            {"item_type": "Pet", "accelerate": 0.15},
            {"item_type": "Food", "accelerate": 0.15},
        ]
        trigger = ItemAcceleratedCooldownTrigger(100.0, conditions)
        conditions[0]["accelerate"] = 9.0
        dual_type = Mock(
            item_classes=("Ranger",),
            rarity="Common",
            item_types=("Pet", "Food"),
            icon_types=("nature",),
        )
        pet = Mock(
            item_classes=("Ranger",),
            rarity="Common",
            item_types=("Pet",),
            icon_types=("nature",),
        )
        context = self.make_context(frame_delta=1.0)
        context.item = Mock(linked_items=["dual_type", "pet"])
        context.owner.items = {
            "dual_type": dual_type,
            "pet": pet,
        }
        context.owner.buffs.Heat = 5
        trigger.stack_speed_modifier(0.20)

        self.assertFalse(trigger.update(context))

        self.assertAlmostEqual(trigger.item_acceleration, 0.45)
        self.assertAlmostEqual(trigger.speed_modifiers, 0.65)
        self.assertAlmostEqual(trigger.cooldown_progress, 1.75)

        context.item.linked_items.append("late_food")
        context.owner.items["late_food"] = Mock(
            item_classes=("Neutral",),
            rarity="Common",
            item_types=("Food",),
            icon_types=("nature",),
        )
        self.assertFalse(trigger.update(context))
        self.assertAlmostEqual(trigger.item_acceleration, 0.45)
        self.assertAlmostEqual(trigger.speed_modifiers, 0.65)
        self.assertAlmostEqual(trigger.cooldown_progress, 3.50)

    def test_food_cooldown_counts_each_linked_other_food_instance(self):
        banana, context, _ = self.make_banana_context(
            linked_item_specs=(
                ("garlic1", "garlic", ("Food",)),
                ("garlic2", "garlic", ("Food",)),
            ),
        )

        self.assertFalse(banana.triggers[0].update(context))

        self.assertEqual(
            banana.triggers[0].qualifying_food_count,
            2,
        )
        self.assertAlmostEqual(
            banana.triggers[0].cooldown_progress,
            1.2,
        )

    def test_food_cooldown_ignores_linked_same_food_and_non_food(self):
        banana, context, _ = self.make_banana_context(
            linked_item_specs=(
                ("banana2", "banana", ("Food",)),
                ("wooden_sword1", "wooden_sword", ("Weapon",)),
            ),
        )

        self.assertFalse(banana.triggers[0].update(context))

        self.assertEqual(
            banana.triggers[0].qualifying_food_count,
            0,
        )
        self.assertAlmostEqual(
            banana.triggers[0].cooldown_progress,
            1.0,
        )

    def test_food_cooldown_ignores_unlinked_food(self):
        banana, context, _ = self.make_banana_context(
            unlinked_item_specs=(
                ("garlic1", "garlic", ("Food",)),
            ),
        )

        self.assertFalse(banana.triggers[0].update(context))

        self.assertEqual(
            banana.triggers[0].qualifying_food_count,
            0,
        )
        self.assertAlmostEqual(
            banana.triggers[0].cooldown_progress,
            1.0,
        )

    def test_food_cooldown_counts_one_linked_instance_once(self):
        banana, context, _ = self.make_banana_context(
            linked_item_specs=(
                ("garlic1", "garlic", ("Food",)),
            ),
        )
        banana.add_linked_item("garlic1")

        self.assertEqual(banana.linked_items, ["garlic1"])
        self.assertFalse(banana.triggers[0].update(context))
        self.assertEqual(
            banana.triggers[0].qualifying_food_count,
            1,
        )
        self.assertAlmostEqual(
            banana.triggers[0].cooldown_progress,
            1.1,
        )

    def test_food_cooldown_combines_food_faster_and_cold_additively(self):
        banana, context, _ = self.make_banana_context(
            linked_item_specs=(
                ("garlic1", "garlic", ("Food",)),
            ),
        )
        context.owner.debuffs.Cold = 5

        self.assertFalse(banana.triggers[0].update(context))

        self.assertAlmostEqual(
            banana.triggers[0].cooldown_progress,
            1.0,
        )

    def test_food_cooldown_caches_link_count_after_first_update(self):
        banana, context, linked_items = self.make_banana_context(
            linked_item_specs=(
                ("garlic1", "garlic", ("Food",)),
            ),
        )

        self.assertFalse(banana.triggers[0].update(context))
        self.assertEqual(
            banana.triggers[0].qualifying_food_count,
            1,
        )
        self.assertAlmostEqual(
            banana.triggers[0].cooldown_progress,
            1.1,
        )

        blueberries = Mock()
        blueberries.item_id = "blueberries"
        blueberries.item_types = ("Food",)
        linked_items["blueberries1"] = blueberries
        context.owner.items["blueberries1"] = blueberries
        banana.add_linked_item("blueberries1")
        context.owner.debuffs.Cold = 5

        self.assertFalse(banana.triggers[0].update(context))

        self.assertEqual(
            banana.triggers[0].qualifying_food_count,
            1,
        )
        self.assertAlmostEqual(
            banana.triggers[0].cooldown_progress,
            2.1,
        )

    def test_garlic_food_cooldown_counts_linked_banana(self):
        garlic, context, _, _ = self.make_garlic_context(
            linked_item_specs=(
                ("banana1", "banana", ("Food",)),
            ),
        )

        self.assertFalse(garlic.triggers[0].update(context))

        self.assertEqual(
            garlic.triggers[0].qualifying_food_count,
            1,
        )
        self.assertAlmostEqual(
            garlic.triggers[0].cooldown_progress,
            1.1,
        )

    def test_garlic_food_cooldown_ignores_linked_garlic(self):
        garlic, context, _, _ = self.make_garlic_context(
            linked_item_specs=(
                ("garlic2", "garlic", ("Food",)),
            ),
        )

        self.assertFalse(garlic.triggers[0].update(context))

        self.assertEqual(
            garlic.triggers[0].qualifying_food_count,
            0,
        )
        self.assertAlmostEqual(
            garlic.triggers[0].cooldown_progress,
            1.0,
        )

    def test_garlic_food_cooldown_keeps_first_cached_count(self):
        garlic, context, linked_items, _ = self.make_garlic_context(
            linked_item_specs=(
                ("banana1", "banana", ("Food",)),
            ),
        )

        self.assertFalse(garlic.triggers[0].update(context))
        self.assertEqual(
            garlic.triggers[0].qualifying_food_count,
            1,
        )

        blueberries = Mock()
        blueberries.item_id = "blueberries"
        blueberries.item_types = ("Food",)
        linked_items["blueberries1"] = blueberries
        context.owner.items["blueberries1"] = blueberries
        garlic.add_linked_item("blueberries1")
        context.owner.debuffs.Cold = 5

        self.assertFalse(garlic.triggers[0].update(context))

        self.assertEqual(
            garlic.triggers[0].qualifying_food_count,
            1,
        )
        self.assertAlmostEqual(
            garlic.triggers[0].cooldown_progress,
            2.1,
        )

    def test_gain_block_effect_adds_amount(self):
        effect = GainBlockEffect(amount=3)
        context = self.make_context()
        context.owner.block = 2

        result = effect.apply(context)

        self.assertTrue(result)
        self.assertEqual(context.owner.block, 5)

    def test_gain_block_effect_returns_false_for_zero_amount(self):
        effect = GainBlockEffect(amount=0)
        context = self.make_context()
        context.owner.block = 2

        result = effect.apply(context)

        self.assertFalse(result)
        self.assertEqual(context.owner.block, 2)

    def test_gain_block_effect_rejects_invalid_amount(self):
        for invalid_amount in (-1, 1.5, True, "3"):
            with self.subTest(invalid_amount=invalid_amount):
                with self.assertRaises(ValueError):
                    GainBlockEffect(invalid_amount)

    def test_gain_buff_effect_adds_named_buff_to_owner(self):
        effect = GainBuffEffect("Mana", 3)
        context = self.make_context()
        context.owner.buffs.Mana = 2
        context.opponent.buffs.Mana = 7

        result = effect.apply(context)

        self.assertTrue(result)
        self.assertEqual(context.owner.buffs.Mana, 5)
        self.assertEqual(context.opponent.buffs.Mana, 7)

    def test_gain_buff_effect_supports_all_buff_names(self):
        context = self.make_context()

        for buff_name in BuffSlot.__annotations__:
            with self.subTest(buff_name=buff_name):
                self.assertTrue(GainBuffEffect(buff_name, 1).apply(context))
                self.assertEqual(
                    getattr(context.owner.buffs, buff_name),
                    1,
                )

    def test_gain_buff_effect_zero_is_no_change(self):
        context = self.make_context()

        self.assertFalse(GainBuffEffect("Mana", 0).apply(context))
        self.assertEqual(context.owner.buffs.Mana, 0)

    def test_gain_buff_effect_rejects_invalid_arguments(self):
        for invalid_name in ("", "Unknown", True, 1):
            with self.subTest(invalid_name=invalid_name):
                with self.assertRaises(ValueError):
                    GainBuffEffect(invalid_name, 1)
        for invalid_amount in (-1, 1.5, True, "1"):
            with self.subTest(invalid_amount=invalid_amount):
                with self.assertRaises(ValueError):
                    GainBuffEffect("Mana", invalid_amount)

    def test_use_buff_effect_is_all_or_nothing(self):
        context = self.make_context()
        context.owner.buffs.Mana = 5

        self.assertTrue(UseBuffEffect("Mana", 3).apply(context))
        self.assertEqual(context.owner.buffs.Mana, 2)
        self.assertFalse(UseBuffEffect("Mana", 3).apply(context))
        self.assertEqual(context.owner.buffs.Mana, 2)

    def test_use_zero_buff_succeeds_without_change(self):
        context = self.make_context()

        self.assertTrue(UseBuffEffect("Mana", 0).apply(context))
        self.assertEqual(context.owner.buffs.Mana, 0)

    def test_use_buff_effect_rejects_invalid_arguments(self):
        for invalid_name in ("", "Unknown", True, 1):
            with self.subTest(invalid_name=invalid_name):
                with self.assertRaises(ValueError):
                    UseBuffEffect(invalid_name, 1)
        for invalid_amount in (-1, 1.5, True, "1"):
            with self.subTest(invalid_amount=invalid_amount):
                with self.assertRaises(ValueError):
                    UseBuffEffect("Mana", invalid_amount)

    def test_buff_removal_effect_removes_named_buff(self):
        effect = BuffRemovalEffect(
            buff_name="Vampirism",
            amount=1,
        )
        context = self.make_context()
        context.opponent.buffs.Vampirism = 2
        context.battle_state.rng = Mock()

        result = effect.apply(context)

        self.assertTrue(result)
        self.assertEqual(context.opponent.buffs.Vampirism, 1)
        context.battle_state.rng.random.assert_not_called()

    def test_buff_removal_effect_can_remove_another_supported_buff(self):
        effect = BuffRemovalEffect(
            buff_name="Heat",
            amount=2,
        )
        context = self.make_context()
        context.opponent.buffs.Heat = 3

        result = effect.apply(context)

        self.assertTrue(result)
        self.assertEqual(context.opponent.buffs.Heat, 1)

    def test_buff_removal_effect_caps_at_available_stacks(self):
        effect = BuffRemovalEffect(
            buff_name="Vampirism",
            amount=3,
        )
        context = self.make_context()
        context.opponent.buffs.Vampirism = 1

        result = effect.apply(context)

        self.assertTrue(result)
        self.assertEqual(context.opponent.buffs.Vampirism, 0)

    def test_buff_removal_effect_returns_false_with_no_stacks(self):
        effect = BuffRemovalEffect(
            buff_name="Vampirism",
            amount=1,
        )
        context = self.make_context()

        result = effect.apply(context)

        self.assertFalse(result)
        self.assertEqual(context.opponent.buffs.Vampirism, 0)

    def test_buff_removal_effect_rejects_invalid_buff_name(self):
        for invalid_name in ("", "Unknown", True, 1):
            with self.subTest(invalid_name=invalid_name):
                with self.assertRaises(ValueError):
                    BuffRemovalEffect(
                        buff_name=invalid_name,
                        amount=1,
                    )

    def test_buff_removal_effect_rejects_invalid_amount(self):
        for invalid_amount in (-1, 1.5, True, "1"):
            with self.subTest(invalid_amount=invalid_amount):
                with self.assertRaises(ValueError):
                    BuffRemovalEffect(
                        buff_name="Vampirism",
                        amount=invalid_amount,
                    )

    def test_cleanse_debuff_effect_removes_from_owner_only(self):
        effect = CleanseDebuffEffect("Poison", 3)
        context = self.make_context()
        context.owner.debuffs.Poison = 4
        context.opponent.debuffs.Poison = 7

        result = effect.apply(context)

        self.assertTrue(result)
        self.assertEqual(context.owner.debuffs.Poison, 1)
        self.assertEqual(context.opponent.debuffs.Poison, 7)

    def test_cleanse_debuff_effect_caps_and_reports_no_stacks(self):
        context = self.make_context()
        context.owner.debuffs.Poison = 1
        effect = CleanseDebuffEffect("Poison", 3)

        self.assertTrue(effect.apply(context))
        self.assertEqual(context.owner.debuffs.Poison, 0)
        self.assertFalse(effect.apply(context))

    def test_cleanse_debuff_effect_supports_all_debuff_names(self):
        context = self.make_context()

        for debuff_name in DebuffSlot.__annotations__:
            with self.subTest(debuff_name=debuff_name):
                setattr(context.owner.debuffs, debuff_name, 1)
                self.assertTrue(
                    CleanseDebuffEffect(debuff_name, 1).apply(context)
                )
                self.assertEqual(
                    getattr(context.owner.debuffs, debuff_name),
                    0,
                )

    def test_cleanse_debuff_effect_rejects_invalid_arguments(self):
        for invalid_name in ("", "Unknown", True, 1):
            with self.subTest(invalid_name=invalid_name):
                with self.assertRaises(ValueError):
                    CleanseDebuffEffect(invalid_name, 1)
        for invalid_amount in (-1, 1.5, True, "1"):
            with self.subTest(invalid_amount=invalid_amount):
                with self.assertRaises(ValueError):
                    CleanseDebuffEffect("Poison", invalid_amount)

    def test_heal_effect_increases_health_by_amount(self):
        effect = HealEffect(amount=4)
        context = self.make_context(health=5, max_health=10)

        result = effect.apply(context)

        self.assertTrue(result)
        self.assertEqual(context.owner.health, 9)
        self.assertEqual(context.owner.max_health, 10)

    def test_heal_effect_caps_health_at_max_health(self):
        effect = HealEffect(amount=4)
        context = self.make_context(health=9, max_health=10)

        result = effect.apply(context)

        self.assertTrue(result)
        self.assertEqual(context.owner.health, 10)

    def test_heal_effect_returns_false_at_full_health(self):
        effect = HealEffect(amount=4)
        context = self.make_context(health=10, max_health=10)

        result = effect.apply(context)

        self.assertFalse(result)
        self.assertEqual(context.owner.health, 10)

    def test_heal_effect_rejects_invalid_amount(self):
        for invalid_amount in (-1, 1.5, True, "4"):
            with self.subTest(invalid_amount=invalid_amount):
                with self.assertRaises(ValueError):
                    HealEffect(invalid_amount)

    def test_regenerate_stamina_effect_increases_stamina_by_amount(self):
        effect = RegenerateStaminaEffect(amount=1)
        context = self.make_context(stamina=2.0, max_stamina=5.0)

        result = effect.apply(context)

        self.assertTrue(result)
        self.assertEqual(context.owner.stamina, 3.0)
        self.assertEqual(context.owner.max_stamina, 5.0)

    def test_regenerate_stamina_effect_caps_at_max_stamina(self):
        effect = RegenerateStaminaEffect(amount=1.0)
        context = self.make_context(stamina=4.5, max_stamina=5.0)

        result = effect.apply(context)

        self.assertTrue(result)
        self.assertEqual(context.owner.stamina, 5.0)

    def test_regenerate_stamina_effect_returns_false_at_full_stamina(self):
        effect = RegenerateStaminaEffect(amount=1.0)
        context = self.make_context(stamina=5.0, max_stamina=5.0)

        result = effect.apply(context)

        self.assertFalse(result)
        self.assertEqual(context.owner.stamina, 5.0)

    def test_regenerate_stamina_effect_rejects_invalid_amount(self):
        for invalid_amount in (-1, True, "1"):
            with self.subTest(invalid_amount=invalid_amount):
                with self.assertRaises(ValueError):
                    RegenerateStaminaEffect(invalid_amount)

    def test_stamina_consumption_effect_deducts_cost_when_stamina_is_sufficient(self):
        effect = StaminaConsumptionEffect(stamina_cost=0.7)
        context = self.make_context(stamina=2.0, max_stamina=5.0)

        result = effect.apply(context)

        self.assertTrue(result)
        self.assertAlmostEqual(context.owner.stamina, 1.3)
        self.assertAlmostEqual(context.owner.max_stamina, 5.0)

    def test_stamina_consumption_effect_accepts_exact_remaining_stamina(self):
        effect = StaminaConsumptionEffect(stamina_cost=1.0)
        context = self.make_context(stamina=1.0, max_stamina=5.0)

        result = effect.apply(context)

        self.assertTrue(result)
        self.assertAlmostEqual(context.owner.stamina, 0.0)

    def test_stamina_consumption_effect_does_not_deduct_when_stamina_is_insufficient(self):
        effect = StaminaConsumptionEffect(stamina_cost=1.0)
        context = self.make_context(stamina=0.5, max_stamina=5.0)

        result = effect.apply(context)

        self.assertFalse(result)
        self.assertAlmostEqual(context.owner.stamina, 0.5)
        self.assertAlmostEqual(context.owner.max_stamina, 5.0)

    def test_banana_does_not_activate_before_cooldown(self):
        banana, context, _ = self.make_banana_context(
            frame_delta=1.0,
            health=5,
            max_health=10,
            stamina=2.0,
            max_stamina=5.0,
        )
        dispatch_spy = spy_on_activation_dispatch(
            context.battle_state
        )

        banana.activate_item(context)

        self.assertAlmostEqual(
            banana.triggers[0].cooldown_progress,
            1.0,
        )
        self.assertEqual(context.owner.health, 5)
        self.assertEqual(context.owner.stamina, 2.0)
        dispatch_spy.assert_not_called()

    def test_banana_heals_and_regenerates_stamina_after_cooldown(self):
        banana, context, _ = self.make_banana_context(
            frame_delta=5.0,
            health=5,
            max_health=10,
            stamina=2.0,
            max_stamina=5.0,
        )
        dispatch_spy = spy_on_activation_dispatch(
            context.battle_state
        )

        banana.activate_item(context)

        self.assertEqual(context.owner.health, 9)
        self.assertEqual(context.owner.stamina, 3.0)
        self.assertAlmostEqual(
            banana.triggers[0].cooldown_progress,
            0.0,
        )
        dispatch_spy.assert_called_once_with(banana)

    def test_banana_runs_stamina_effect_when_heal_has_no_effect(self):
        banana, context, _ = self.make_banana_context(
            frame_delta=5.0,
            health=10,
            max_health=10,
            stamina=2.0,
            max_stamina=5.0,
        )

        banana.activate_item(context)

        self.assertEqual(context.owner.health, 10)
        self.assertEqual(context.owner.stamina, 3.0)

    def test_banana_runs_heal_effect_when_stamina_has_no_effect(self):
        banana, context, _ = self.make_banana_context(
            frame_delta=5.0,
            health=5,
            max_health=10,
            stamina=5.0,
            max_stamina=5.0,
        )

        banana.activate_item(context)

        self.assertEqual(context.owner.health, 9)
        self.assertEqual(context.owner.stamina, 5.0)

    def test_banana_caps_both_resources(self):
        banana, context, _ = self.make_banana_context(
            frame_delta=5.0,
            health=9,
            max_health=10,
            stamina=4.5,
            max_stamina=5.0,
        )

        banana.activate_item(context)

        self.assertEqual(context.owner.health, 10)
        self.assertEqual(context.owner.stamina, 5.0)

    def test_banana_does_not_activate_star_linked_items(self):
        banana, context, linked_items = self.make_banana_context(
            frame_delta=5.0,
            health=5,
            max_health=10,
            stamina=2.0,
            max_stamina=5.0,
            linked_item_specs=(
                ("garlic1", "garlic", ("Food",)),
            ),
        )

        banana.activate_item(context)

        self.assertEqual(context.owner.health, 9)
        self.assertEqual(context.owner.stamina, 3.0)
        linked_items["garlic1"].activate_item.assert_not_called()

    def test_garlic_does_not_activate_before_cooldown(self):
        rng = Mock()
        rng.random.return_value = 0.0
        garlic, context, _, _ = self.make_garlic_context(
            frame_delta=1.0,
            block=2,
            opponent_vampirism=2,
            rng=rng,
        )
        dispatch_spy = spy_on_activation_dispatch(
            context.battle_state
        )

        garlic.activate_item(context)

        self.assertAlmostEqual(
            garlic.triggers[0].cooldown_progress,
            1.0,
        )
        self.assertEqual(context.owner.block, 2)
        self.assertEqual(context.opponent.buffs.Vampirism, 2)
        rng.random.assert_not_called()
        dispatch_spy.assert_not_called()

    def test_garlic_gains_block_and_removes_vampirism_on_success(self):
        rng = Mock()
        rng.random.return_value = 0.29
        garlic, context, _, _ = self.make_garlic_context(
            frame_delta=4.0,
            block=2,
            opponent_vampirism=2,
            rng=rng,
        )
        dispatch_spy = spy_on_activation_dispatch(
            context.battle_state
        )

        garlic.activate_item(context)

        self.assertEqual(context.owner.block, 5)
        self.assertEqual(context.opponent.buffs.Vampirism, 1)
        self.assertAlmostEqual(
            garlic.triggers[0].cooldown_progress,
            0.0,
        )
        rng.random.assert_called_once_with()
        dispatch_spy.assert_called_once_with(garlic)

    def test_garlic_still_gains_block_when_removal_roll_fails(self):
        rng = Mock()
        rng.random.return_value = 0.30
        garlic, context, _, _ = self.make_garlic_context(
            frame_delta=4.0,
            block=2,
            opponent_vampirism=2,
            rng=rng,
        )
        dispatch_spy = spy_on_activation_dispatch(
            context.battle_state
        )

        garlic.activate_item(context)

        self.assertEqual(context.owner.block, 5)
        self.assertEqual(context.opponent.buffs.Vampirism, 2)
        rng.random.assert_called_once_with()
        dispatch_spy.assert_called_once_with(garlic)

    def test_garlic_still_gains_block_when_opponent_has_no_vampirism(self):
        rng = Mock()
        rng.random.return_value = 0.29
        garlic, context, _, _ = self.make_garlic_context(
            frame_delta=4.0,
            block=2,
            opponent_vampirism=0,
            rng=rng,
        )

        garlic.activate_item(context)

        self.assertEqual(context.owner.block, 5)
        self.assertEqual(context.opponent.buffs.Vampirism, 0)
        rng.random.assert_called_once_with()

    def test_garlic_does_not_activate_star_linked_items(self):
        rng = Mock()
        rng.random.return_value = 0.29
        garlic, context, linked_items, _ = self.make_garlic_context(
            frame_delta=4.0,
            block=2,
            opponent_vampirism=2,
            rng=rng,
            linked_item_specs=(
                ("wooden_sword1", "wooden_sword", ("Weapon",)),
            ),
        )

        garlic.activate_item(context)

        self.assertEqual(context.owner.block, 5)
        self.assertEqual(context.opponent.buffs.Vampirism, 1)
        linked_items["wooden_sword1"].activate_item.assert_not_called()

    def test_battle_step_runs_garlic_at_four_seconds(self):
        rng = Mock()
        rng.random.return_value = 0.29
        garlic, context, _, _ = self.make_garlic_context(
            frame_delta=1.0,
            block=0,
            opponent_vampirism=2,
            rng=rng,
        )

        for _ in range(4):
            context.battle_state.step()

        self.assertEqual(context.battle_state.frame, 4)
        self.assertEqual(context.owner.block, 3)
        self.assertEqual(context.opponent.buffs.Vampirism, 1)
        self.assertAlmostEqual(
            garlic.triggers[0].cooldown_progress,
            0.0,
        )
        rng.random.assert_called_once_with()

    def test_melee_attack_effect_starts_with_unprepared_zero_damage_modifier(
        self,
    ):
        effect = AttackEffect(1, 3, 90)
        context = self.make_context()
        context.item = Mock(item_types=("Weapon",))
        context.battle_state.rng = Mock()
        context.battle_state.rng.random.return_value = 0.0
        context.battle_state.rng.randint.return_value = 1

        self.assertEqual(effect.damage_modifier, 0)
        self.assertFalse(effect.damage_modifier_prepared)

        result = effect.apply(context, "melee")

        self.assertTrue(result)
        self.assertTrue(effect.damage_modifier_prepared)
        self.assertEqual(effect.damage_modifier, 0)
        context.battle_state.rng.randint.assert_called_once_with(1, 3)

    def test_melee_attack_effect_stacks_persistent_damage_modifiers(self):
        effect = AttackEffect(1, 3, 90)
        effect.stack_damage_modifier(2)
        effect.stack_damage_modifier(3)
        context = self.make_context()
        context.item = Mock(item_types=("Weapon",))
        context.owner.buffs.Empower = 1
        context.battle_state.rng = Mock()
        context.battle_state.rng.random.return_value = 0.0
        context.battle_state.rng.randint.return_value = 7

        effect.apply(context, "melee")

        self.assertEqual(effect.damage_modifier, 5)
        context.battle_state.rng.randint.assert_called_once_with(7, 9)

    def test_melee_attack_effect_prepares_intrinsic_modifier_once(self):
        class PreparingAttackEffect(AttackEffect):
            def __init__(self):
                super().__init__(1, 3, 90)
                self.prepare_calls = 0

            def prepare_damage_modifier(self, context):
                self.prepare_calls += 1
                self.stack_damage_modifier(2)

        effect = PreparingAttackEffect()
        context = self.make_context()
        context.item = Mock(item_types=("Weapon",))
        context.battle_state.rng = Mock()
        context.battle_state.rng.random.return_value = 0.0
        context.battle_state.rng.randint.side_effect = [3, 3]

        effect.apply(context, "melee")
        effect.apply(context, "melee")

        self.assertEqual(effect.prepare_calls, 1)
        self.assertEqual(effect.damage_modifier, 2)
        self.assertEqual(effect.min_damage, 1)
        self.assertEqual(effect.max_damage, 3)
        self.assertEqual(
            context.battle_state.rng.randint.call_args_list,
            [call(3, 5), call(3, 5)],
        )

    def test_food_linked_melee_attack_effect_counts_all_linked_food_instances(
        self,
    ):
        rng = Mock()
        rng.random.return_value = 0.0
        rng.randint.return_value = 7
        pan, context, _, _ = self.make_pan_context(
            rng=rng,
            linked_item_specs=(
                ("banana1", "banana", ("Food",)),
                ("banana2", "banana", ("Food",)),
            ),
        )
        effect = pan.effects[1]

        effect.apply(context, "melee")

        self.assertEqual(effect.qualifying_food_count, 2)
        self.assertEqual(effect.damage_modifier, 2)
        self.assertTrue(effect.damage_modifier_prepared)
        rng.randint.assert_called_once_with(7, 8)

    def test_food_linked_melee_attack_effect_ignores_non_food_and_unlinked_food(
        self,
    ):
        rng = Mock()
        rng.random.return_value = 0.0
        rng.randint.return_value = 5
        pan, context, _, _ = self.make_pan_context(
            rng=rng,
            linked_item_specs=(
                ("wooden_sword1", "wooden_sword", ("Weapon",)),
            ),
            unlinked_item_specs=(
                ("banana1", "banana", ("Food",)),
            ),
        )
        effect = pan.effects[1]

        effect.apply(context, "melee")

        self.assertEqual(effect.qualifying_food_count, 0)
        self.assertEqual(effect.damage_modifier, 0)
        rng.randint.assert_called_once_with(5, 6)

    def test_food_linked_melee_attack_effect_uses_first_cached_count(self):
        rng = Mock()
        rng.random.return_value = 0.0
        rng.randint.side_effect = [6, 6]
        pan, context, linked_items, _ = self.make_pan_context(
            rng=rng,
            linked_item_specs=(
                ("banana1", "banana", ("Food",)),
            ),
        )
        effect = pan.effects[1]

        effect.apply(context, "melee")

        blueberries = Mock()
        blueberries.item_id = "blueberries"
        blueberries.item_types = ("Food",)
        linked_items["blueberries1"] = blueberries
        context.owner.items["blueberries1"] = blueberries
        pan.add_linked_item("blueberries1")
        effect.apply(context, "melee")

        self.assertEqual(effect.qualifying_food_count, 1)
        self.assertEqual(effect.damage_modifier, 1)
        self.assertEqual(
            rng.randint.call_args_list,
            [call(6, 7), call(6, 7)],
        )

    def test_food_linked_melee_attack_effect_rejects_invalid_damage_per_food(
        self,
    ):
        for invalid_amount in (-1, 1.5, True, "1"):
            with self.subTest(invalid_amount=invalid_amount):
                with self.assertRaises(ValueError):
                    FoodLinkedMeleeAttackEffect(
                        min_damage=5,
                        max_damage=6,
                        accuracy=85,
                        damage_per_food=invalid_amount,
                    )

    def test_food_linked_melee_attack_effect_preserves_external_modifier_and_base_damage(
        self,
    ):
        rng = Mock()
        rng.random.return_value = 0.0
        rng.randint.return_value = 11
        pan, context, _, _ = self.make_pan_context(
            rng=rng,
            linked_item_specs=(
                ("banana1", "banana", ("Food",)),
                ("banana2", "banana", ("Food",)),
            ),
        )
        effect = pan.effects[1]
        effect.stack_damage_modifier(4)

        effect.apply(context, "melee")

        self.assertEqual(effect.damage_modifier, 6)
        self.assertEqual(effect.min_damage, 5)
        self.assertEqual(effect.max_damage, 6)
        rng.randint.assert_called_once_with(11, 12)

    def test_pan_is_registered_with_metadata_and_components(self):
        pan = DEFAULT_ITEM_FACTORIES["pan"](
            item_id="pan",
            item_key="pan1",
            player_id=0,
        )

        self.assertIsInstance(pan, Pan)
        self.assertEqual(pan.item_id, "pan")
        self.assertEqual(pan.item_key, "pan1")
        self.assertEqual(pan.player_id, 0)
        self.assertEqual(pan.display_name, "Pan")
        self.assertEqual(pan.item_classes, ("Neutral",))
        self.assertEqual(pan.rarity, "Common")
        self.assertEqual(pan.cost, 4)
        self.assertEqual(pan.item_types, ("Weapon",))
        self.assertEqual(pan.icon_types, ("melee",))
        self.assertTrue(pan.is_active_item)
        self.assertEqual(pan.socket_count, 1)
        self.assertEqual(len(pan.triggers), 1)
        self.assertIsInstance(pan.triggers[0], CooldownTrigger)
        self.assertNotIsInstance(pan.triggers[0], FoodCooldownTrigger)
        self.assertEqual(pan.triggers[0].cooldown_seconds, 2.2)
        self.assertEqual(len(pan.effects), 2)
        self.assertIsInstance(
            pan.effects[0],
            StaminaConsumptionEffect,
        )
        self.assertEqual(pan.effects[0].stamina_cost, 2.0)
        self.assertIsInstance(
            pan.effects[1],
            FoodLinkedMeleeAttackEffect,
        )
        self.assertEqual(pan.effects[1].min_damage, 5)
        self.assertEqual(pan.effects[1].max_damage, 6)
        self.assertEqual(pan.effects[1].accuracy, 85)
        self.assertEqual(pan.effects[1].damage_per_food, 1)

    def test_pans_own_independent_component_instances(self):
        first = Pan(item_key="pan1", player_id=0)
        second = Pan(item_key="pan2", player_id=0)

        self.assertIsNot(first.triggers[0], second.triggers[0])
        self.assertIsNot(first.effects[0], second.effects[0])
        self.assertIsNot(first.effects[1], second.effects[1])

        first.triggers[0].cooldown_progress = 0.5
        first.triggers[0].stack_speed_modifier(0.2)
        first.triggers[0].speed_modifiers_prepared = True
        first.effects[1].stack_damage_modifier(3)
        first.effects[1].damage_modifier_prepared = True
        first.effects[1].qualifying_food_count = 2

        self.assertEqual(second.triggers[0].cooldown_progress, 0.0)
        self.assertEqual(second.triggers[0].speed_modifiers, 0.0)
        self.assertFalse(second.triggers[0].speed_modifiers_prepared)
        self.assertEqual(second.effects[1].damage_modifier, 0)
        self.assertFalse(second.effects[1].damage_modifier_prepared)
        self.assertIsNone(second.effects[1].qualifying_food_count)

    def test_initializer_builds_pan_as_active_item_with_deduplicated_food_link(
        self,
    ):
        battle = initialize_battle(
            [
                {
                    "player_id": 0,
                    "health": 20,
                    "max_health": 20,
                    "stamina": 10.0,
                    "max_stamina": 10.0,
                    "placements": [
                        {
                            "item_id": "pan",
                            "x": 2,
                            "y": 2,
                            "rotation": 0,
                        },
                        {
                            "item_id": "banana",
                            "x": 4,
                            "y": 2,
                            "rotation": 0,
                        },
                    ],
                },
                {
                    "player_id": 1,
                    "health": 20,
                    "max_health": 20,
                    "stamina": 10.0,
                    "max_stamina": 10.0,
                    "placements": [],
                },
            ],
            DEFAULT_ITEM_FACTORIES,
            item_catalog=ITEM_CATALOG,
        )

        pan = battle.players[0].items["pan1"]
        banana = battle.players[0].items["banana1"]
        self.assertIsInstance(pan, Pan)
        self.assertEqual(pan.linked_items, ["banana1"])
        self.assertEqual(battle.active_items, [pan, banana])

    def test_pan_does_not_activate_before_cooldown(self):
        rng = Mock()
        pan, context, _, _ = self.make_pan_context(
            frame_delta=1.0,
            stamina=5.0,
            rng=rng,
        )
        dispatch_spy = spy_on_activation_dispatch(
            context.battle_state
        )

        pan.activate_item(context)

        self.assertAlmostEqual(pan.triggers[0].cooldown_progress, 1.0)
        self.assertEqual(context.owner.stamina, 5.0)
        self.assertEqual(context.opponent.health, 100)
        self.assertFalse(pan.effects[1].damage_modifier_prepared)
        rng.random.assert_not_called()
        rng.randint.assert_not_called()
        dispatch_spy.assert_not_called()

    def test_pan_pays_stamina_and_attacks_with_base_damage(self):
        rng = Mock()
        rng.random.return_value = 0.0
        rng.randint.return_value = 5
        pan, context, _, _ = self.make_pan_context(
            frame_delta=2.2,
            stamina=5.0,
            opponent_health=20,
            rng=rng,
        )
        dispatch_spy = spy_on_activation_dispatch(
            context.battle_state
        )

        pan.activate_item(context)

        self.assertEqual(context.owner.stamina, 3.0)
        self.assertEqual(context.opponent.health, 15)
        self.assertAlmostEqual(pan.triggers[0].cooldown_progress, 0.0)
        rng.random.assert_called_once_with()
        rng.randint.assert_called_once_with(5, 6)
        dispatch_spy.assert_called_once_with(pan)

    def test_pan_adds_one_damage_per_linked_food(self):
        rng = Mock()
        rng.random.return_value = 0.0
        rng.randint.return_value = 7
        pan, context, _, _ = self.make_pan_context(
            frame_delta=2.2,
            stamina=5.0,
            opponent_health=20,
            rng=rng,
            linked_item_specs=(
                ("banana1", "banana", ("Food",)),
                ("banana2", "banana", ("Food",)),
            ),
        )

        pan.activate_item(context)

        self.assertEqual(context.owner.stamina, 3.0)
        self.assertEqual(context.opponent.health, 13)
        self.assertEqual(pan.effects[1].qualifying_food_count, 2)
        self.assertEqual(pan.effects[1].damage_modifier, 2)
        rng.randint.assert_called_once_with(7, 8)

    def test_pan_combines_food_external_damage_modifier_and_empower(self):
        rng = Mock()
        rng.random.return_value = 0.0
        rng.randint.return_value = 14
        pan, context, _, _ = self.make_pan_context(
            frame_delta=2.2,
            stamina=5.0,
            empower=3,
            rng=rng,
            linked_item_specs=(
                ("banana1", "banana", ("Food",)),
                ("banana2", "banana", ("Food",)),
            ),
        )
        pan.effects[1].stack_damage_modifier(4)

        pan.activate_item(context)

        self.assertEqual(pan.effects[1].damage_modifier, 6)
        rng.randint.assert_called_once_with(14, 15)

    def test_pan_accepts_external_damage_modifier_after_preparation(self):
        rng = Mock()
        rng.random.return_value = 0.0
        rng.randint.side_effect = [6, 8]
        pan, context, _, _ = self.make_pan_context(
            frame_delta=2.2,
            stamina=10.0,
            rng=rng,
            linked_item_specs=(
                ("banana1", "banana", ("Food",)),
            ),
        )

        pan.activate_item(context)
        pan.effects[1].stack_damage_modifier(2)
        pan.activate_item(context)

        self.assertEqual(pan.effects[1].qualifying_food_count, 1)
        self.assertEqual(pan.effects[1].damage_modifier, 3)
        self.assertEqual(
            rng.randint.call_args_list,
            [call(6, 7), call(8, 9)],
        )

    def test_pan_food_links_do_not_speed_up_cooldown(self):
        pan, context, _, _ = self.make_pan_context(
            frame_delta=1.0,
            stamina=5.0,
            linked_item_specs=(
                ("banana1", "banana", ("Food",)),
            ),
        )

        pan.activate_item(context)

        self.assertAlmostEqual(pan.triggers[0].cooldown_progress, 1.0)
        self.assertEqual(pan.triggers[0].speed_modifiers, 0.0)

    def test_pan_accepts_external_speed_modifier(self):
        pan, context, _, _ = self.make_pan_context(
            frame_delta=1.0,
            stamina=5.0,
        )
        pan.triggers[0].stack_speed_modifier(0.20)

        pan.activate_item(context)

        self.assertAlmostEqual(pan.triggers[0].cooldown_progress, 1.2)
        self.assertAlmostEqual(pan.triggers[0].speed_modifiers, 0.20)
        self.assertTrue(pan.triggers[0].speed_modifiers_prepared)

    def test_pan_skips_attack_without_stamina(self):
        rng = Mock()
        pan, context, _, _ = self.make_pan_context(
            frame_delta=2.2,
            stamina=1.0,
            rng=rng,
            linked_item_specs=(
                ("banana1", "banana", ("Food",)),
            ),
        )
        dispatch_spy = spy_on_activation_dispatch(
            context.battle_state
        )

        pan.activate_item(context)

        self.assertEqual(context.owner.stamina, 1.0)
        self.assertAlmostEqual(pan.triggers[0].cooldown_progress, 0.0)
        self.assertFalse(pan.effects[1].damage_modifier_prepared)
        self.assertIsNone(pan.effects[1].qualifying_food_count)
        self.assertEqual(pan.effects[1].damage_modifier, 0)
        rng.random.assert_not_called()
        rng.randint.assert_not_called()
        dispatch_spy.assert_not_called()

    def test_pan_does_not_activate_star_linked_food_on_hit(self):
        rng = Mock()
        rng.random.return_value = 0.0
        rng.randint.return_value = 6
        pan, context, linked_items, _ = self.make_pan_context(
            frame_delta=2.2,
            stamina=5.0,
            rng=rng,
            linked_item_specs=(
                ("banana1", "banana", ("Food",)),
            ),
        )
        dispatch_spy = spy_on_activation_dispatch(
            context.battle_state
        )

        pan.activate_item(context)

        self.assertEqual(context.owner.stamina, 3.0)
        linked_items["banana1"].activate_item.assert_not_called()

    def test_pan_repeated_attacks_do_not_stack_food_damage_again(self):
        rng = Mock()
        rng.random.return_value = 0.0
        rng.randint.side_effect = [7, 7]
        pan, context, _, _ = self.make_pan_context(
            frame_delta=2.2,
            stamina=10.0,
            rng=rng,
            linked_item_specs=(
                ("banana1", "banana", ("Food",)),
                ("banana2", "banana", ("Food",)),
            ),
        )

        pan.activate_item(context)
        pan.activate_item(context)

        self.assertEqual(pan.effects[1].qualifying_food_count, 2)
        self.assertEqual(pan.effects[1].damage_modifier, 2)
        self.assertTrue(pan.effects[1].damage_modifier_prepared)
        self.assertEqual(
            rng.randint.call_args_list,
            [call(7, 8), call(7, 8)],
        )

    def test_pan_miss_still_pays_stamina_without_activating_linked_food(
        self,
    ):
        rng = Mock()
        rng.random.return_value = 0.85
        pan, context, linked_items, _ = self.make_pan_context(
            frame_delta=2.2,
            stamina=5.0,
            opponent_health=20,
            rng=rng,
            linked_item_specs=(
                ("banana1", "banana", ("Food",)),
            ),
        )
        dispatch_spy = spy_on_activation_dispatch(
            context.battle_state
        )

        pan.activate_item(context)

        self.assertEqual(context.owner.stamina, 3.0)
        self.assertEqual(context.opponent.health, 20)
        self.assertTrue(pan.effects[1].damage_modifier_prepared)
        self.assertEqual(pan.effects[1].damage_modifier, 1)
        rng.random.assert_called_once_with()
        rng.randint.assert_not_called()
        linked_items["banana1"].activate_item.assert_not_called()
        dispatch_spy.assert_called_once_with(pan)

    def test_rat_is_registered_with_metadata_and_components(self):
        rat = DEFAULT_ITEM_FACTORIES["rat"](
            item_id="rat",
            item_key="rat1",
            player_id=0,
        )
        second = Rat(item_key="rat2", player_id=0)

        self.assertIsInstance(rat, Rat)
        self.assertEqual(rat.display_name, "Rat")
        self.assertEqual(rat.item_classes, ("Ranger",))
        self.assertEqual(rat.rarity, "Common")
        self.assertEqual(rat.cost, 4)
        self.assertEqual(rat.item_types, ("Pet",))
        self.assertEqual(rat.icon_types, ("nature",))
        self.assertTrue(rat.is_active_item)
        self.assertEqual(rat.socket_count, 0)
        self.assertIsInstance(
            rat.triggers[0],
            ItemAcceleratedCooldownTrigger,
        )
        self.assertAlmostEqual(rat.triggers[0].cooldown_seconds, 3.3)
        self.assertEqual(
            rat.triggers[0].acceleration_conditions,
            [
                {"item_type": "Pet", "accelerate": 0.15},
                {"item_type": "Food", "accelerate": 0.15},
            ],
        )
        self.assertIsInstance(rat.effects[0], AttackEffect)
        self.assertEqual(
            (
                rat.effects[0].min_damage,
                rat.effects[0].max_damage,
                rat.effects[0].accuracy,
            ),
            (5, 5, 100),
        )
        self.assertEqual(
            [
                (effect.debuff_name, effect.amount)
                for effect in rat.effects[1:]
            ],
            [("Poison", 1), ("Blind", 1)],
        )
        self.assertIsNot(rat.triggers[0], second.triggers[0])
        for effect, second_effect in zip(rat.effects, second.effects):
            self.assertIsNot(effect, second_effect)

    def test_rat_activation_ignores_attack_statuses_and_applies_debuffs(self):
        rng = Mock()
        rng.random.side_effect = [0.0, 0.74, 0.09]
        rng.randint.return_value = 5
        rat, context = self.make_rat_context(
            rng=rng,
            opponent_block=2,
        )
        context.owner.buffs.Empower = 10
        context.owner.buffs.Luck = 0
        context.owner.debuffs.Blind = 100
        dispatch_spy = spy_on_activation_dispatch(
            context.battle_state
        )

        rat.activate_item(context)

        self.assertEqual(context.opponent.block, 0)
        self.assertEqual(context.opponent.health, 7)
        self.assertEqual(context.opponent.debuffs.Poison, 1)
        self.assertEqual(context.opponent.debuffs.Blind, 1)
        rng.randint.assert_called_once_with(5, 5)
        self.assertEqual(rng.random.call_count, 3)
        dispatch_spy.assert_called_once_with(rat)

    def test_rat_forced_attack_miss_emits_without_status_rng(self):
        rng = Mock()
        rat, context = self.make_rat_context(rng=rng)
        rat.effects[0].apply = Mock(return_value=False)
        dispatch_spy = spy_on_activation_dispatch(
            context.battle_state
        )

        rat.activate_item(context)

        rat.effects[0].apply.assert_called_once_with(context, "effect")
        rng.random.assert_not_called()
        rng.randint.assert_not_called()
        dispatch_spy.assert_called_once_with(rat)

    def test_rat_does_not_emit_before_cooldown(self):
        rng = Mock()
        rat, context = self.make_rat_context(
            rng=rng,
            frame_delta=1.0,
        )
        dispatch_spy = spy_on_activation_dispatch(
            context.battle_state
        )

        rat.activate_item(context)

        rng.random.assert_not_called()
        rng.randint.assert_not_called()
        dispatch_spy.assert_not_called()

    def test_rat_debuff_chances_fail_at_boundaries(self):
        rng = Mock()
        rng.random.side_effect = [0.0, 0.75, 0.10]
        rng.randint.return_value = 5
        rat, context = self.make_rat_context(rng=rng)

        rat.activate_item(context)

        self.assertEqual(context.opponent.health, 5)
        self.assertEqual(context.opponent.debuffs.Poison, 0)
        self.assertEqual(context.opponent.debuffs.Blind, 0)

    def test_initializer_links_all_six_rat_stars(self):
        battle = initialize_battle(
            [
                {
                    "player_id": 0,
                    "health": 20,
                    "max_health": 20,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [
                        {
                            "item_id": "rat",
                            "x": 3,
                            "y": 3,
                            "rotation": 0,
                        },
                        {
                            "item_id": "pocket_sand",
                            "x": 3,
                            "y": 4,
                            "rotation": 0,
                        },
                        {
                            "item_id": "pocket_sand",
                            "x": 4,
                            "y": 4,
                            "rotation": 0,
                        },
                        {
                            "item_id": "pocket_sand",
                            "x": 2,
                            "y": 3,
                            "rotation": 0,
                        },
                        {
                            "item_id": "pocket_sand",
                            "x": 5,
                            "y": 3,
                            "rotation": 0,
                        },
                        {
                            "item_id": "pocket_sand",
                            "x": 3,
                            "y": 2,
                            "rotation": 0,
                        },
                        {
                            "item_id": "pocket_sand",
                            "x": 4,
                            "y": 2,
                            "rotation": 0,
                        },
                    ],
                },
                {
                    "player_id": 1,
                    "health": 20,
                    "max_health": 20,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [],
                },
            ],
            DEFAULT_ITEM_FACTORIES,
            item_catalog=ITEM_CATALOG,
        )

        rat = battle.players[0].items["rat1"]
        self.assertEqual(
            rat.linked_items,
            [
                "pocket_sand1",
                "pocket_sand2",
                "pocket_sand3",
                "pocket_sand4",
                "pocket_sand5",
                "pocket_sand6",
            ],
        )

    def test_initializer_builds_rat_as_active_item(self):
        battle = initialize_battle(
            [
                {
                    "player_id": 0,
                    "health": 20,
                    "max_health": 20,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [
                        {
                            "item_id": "rat",
                            "x": 0,
                            "y": 0,
                            "rotation": 0,
                        }
                    ],
                },
                {
                    "player_id": 1,
                    "health": 20,
                    "max_health": 20,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [],
                },
            ],
            DEFAULT_ITEM_FACTORIES,
            item_catalog=ITEM_CATALOG,
        )

        rat = battle.players[0].items["rat1"]
        self.assertIsInstance(rat, Rat)
        self.assertEqual(battle.active_items, [rat])

    def test_cooldown_trigger_ignores_attack_reaction_context(self):
        broom, context, _ = self.make_broom_context(
            frame_delta=1.0,
        )
        event = AttackEvent(
            attacker=context.opponent,
            defender=context.owner,
            source_item=Mock(),
            attack_types=("melee",),
            min_damage=1,
            max_damage=1,
            accuracy=0,
            hit=False,
        )
        reaction_context = AttackReactionContext(
            battle_state=context.battle_state,
            item=broom,
            owner=context.owner,
            opponent=context.opponent,
            attack_phase=ATTACK_PHASE_ON_ATTACK_MISSED,
            attack_event=event,
        )

        result = broom.triggers[0].update(reaction_context)

        self.assertFalse(result)
        self.assertEqual(broom.triggers[0].cooldown_progress, 0.0)
        self.assertFalse(
            broom.triggers[0].speed_modifiers_prepared
        )

    def test_inflict_debuff_effect_adds_stacks_to_opponent(self):
        context = self.make_context()
        context.owner.debuffs.Blind = 7
        context.opponent.debuffs.Blind = 2
        effect = InflictDebuffEffect("Blind", 1)

        result = effect.apply(context)

        self.assertTrue(result)
        self.assertEqual(context.opponent.debuffs.Blind, 3)
        self.assertEqual(context.owner.debuffs.Blind, 7)

    def test_inflict_debuff_effect_handles_zero_and_rejects_invalid_arguments(
        self,
    ):
        context = self.make_context()
        context.opponent.debuffs.Blind = 2
        effect = InflictDebuffEffect("Blind", 0)

        result = effect.apply(context)

        self.assertFalse(result)
        self.assertEqual(context.opponent.debuffs.Blind, 2)

        invalid_arguments = (
            ("missing", 1),
            (1, 1),
            ("Blind", -1),
            ("Blind", True),
            ("Blind", 1.5),
            ("Blind", "1"),
        )
        for debuff_name, amount in invalid_arguments:
            with self.subTest(
                debuff_name=debuff_name,
                amount=amount,
            ):
                with self.assertRaises(ValueError):
                    InflictDebuffEffect(debuff_name, amount)

    def test_broom_is_registered_with_metadata_and_components(self):
        broom = DEFAULT_ITEM_FACTORIES["broom"](
            item_id="broom",
            item_key="broom1",
            player_id=0,
        )

        self.assertIsInstance(broom, Broom)
        self.assertEqual(broom.item_id, "broom")
        self.assertEqual(broom.item_key, "broom1")
        self.assertEqual(broom.player_id, 0)
        self.assertEqual(broom.display_name, "Broom")
        self.assertEqual(broom.item_classes, ("Neutral",))
        self.assertEqual(broom.rarity, "Common")
        self.assertEqual(broom.cost, 4)
        self.assertEqual(broom.item_types, ("Weapon",))
        self.assertEqual(broom.icon_types, ("melee",))
        self.assertTrue(broom.is_active_item)
        self.assertEqual(broom.socket_count, 1)
        self.assertEqual(len(broom.triggers), 2)
        self.assertIsInstance(broom.triggers[0], CooldownTrigger)
        self.assertEqual(broom.triggers[0].cooldown_seconds, 1.7)
        self.assertIsInstance(broom.triggers[1], AttackMissTrigger)
        self.assertEqual(len(broom.effects), 3)
        self.assertIsInstance(
            broom.effects[0],
            StaminaConsumptionEffect,
        )
        self.assertEqual(broom.effects[0].stamina_cost, 1.2)
        self.assertIsInstance(broom.effects[1], AttackEffect)
        self.assertEqual(broom.effects[1].min_damage, 2)
        self.assertEqual(broom.effects[1].max_damage, 4)
        self.assertEqual(broom.effects[1].accuracy, 95)
        self.assertIsInstance(broom.effects[2], InflictDebuffEffect)
        self.assertEqual(broom.effects[2].debuff_name, "Blind")
        self.assertEqual(broom.effects[2].amount, 1)
        self.assertEqual(broom.miss_damage_bonus, 0)

    def test_brooms_own_independent_components_and_bonus_state(self):
        first = Broom(item_key="broom1", player_id=0)
        second = Broom(item_key="broom2", player_id=0)

        for first_trigger, second_trigger in zip(
            first.triggers,
            second.triggers,
        ):
            self.assertIsNot(first_trigger, second_trigger)
        for first_effect, second_effect in zip(
            first.effects,
            second.effects,
        ):
            self.assertIsNot(first_effect, second_effect)

        first.triggers[0].cooldown_progress = 0.5
        first.effects[1].stack_damage_modifier(2)
        first.miss_damage_bonus = 2

        self.assertEqual(second.triggers[0].cooldown_progress, 0.0)
        self.assertEqual(second.effects[1].damage_modifier, 0)
        self.assertEqual(second.miss_damage_bonus, 0)

    def test_initializer_builds_broom_as_active_and_attack_miss_responder(
        self,
    ):
        battle = initialize_battle(
            [
                {
                    "player_id": 0,
                    "health": 20,
                    "max_health": 20,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [
                        {
                            "item_id": "broom",
                            "x": 0,
                            "y": 0,
                            "rotation": 0,
                        },
                    ],
                },
                {
                    "player_id": 1,
                    "health": 20,
                    "max_health": 20,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [],
                },
            ],
            DEFAULT_ITEM_FACTORIES,
            item_catalog=ITEM_CATALOG,
        )

        broom = battle.players[0].items["broom1"]
        self.assertIsInstance(broom, Broom)
        self.assertIn(broom, battle.active_items)
        self.assertEqual(
            battle._get_attack_reaction_items(
                battle.players[0],
                ATTACK_PHASE_ON_ATTACK_MISSED,
            ),
            (broom,),
        )
        self.assertEqual(
            battle._get_attack_reaction_items(
                battle.players[0],
                ATTACK_PHASE_ON_ATTACKED,
            ),
            (),
        )

    def test_broom_waits_for_cooldown_without_rng(self):
        rng = Mock()
        broom, context, _ = self.make_broom_context(
            frame_delta=1.0,
            stamina=5.0,
            rng=rng,
        )
        dispatch_spy = spy_on_activation_dispatch(
            context.battle_state
        )

        broom.activate_item(context)

        self.assertAlmostEqual(
            broom.triggers[0].cooldown_progress,
            1.0,
        )
        self.assertEqual(context.owner.stamina, 5.0)
        self.assertEqual(context.opponent.health, 100)
        self.assertEqual(context.opponent.debuffs.Blind, 0)
        rng.random.assert_not_called()
        rng.randint.assert_not_called()
        dispatch_spy.assert_not_called()

    def test_broom_gains_two_damage_when_opponent_melee_attack_misses(
        self,
    ):
        rng = Mock()
        rng.random.return_value = 0.5
        broom, context, _ = self.make_broom_context(rng=rng)
        dispatch_spy = spy_on_activation_dispatch(
            context.battle_state
        )

        self.resolve_opponent_attack(
            context,
            accuracy=0,
            attack_types=("melee",),
        )

        self.assertEqual(broom.miss_damage_bonus, 2)
        self.assertEqual(broom.effects[1].damage_modifier, 2)
        self.assertEqual(broom.triggers[0].cooldown_progress, 0.0)
        self.assertFalse(
            broom.triggers[0].speed_modifiers_prepared
        )
        self.assertEqual(context.owner.stamina, 5.0)
        rng.random.assert_called_once_with()
        rng.randint.assert_not_called()
        dispatch_spy.assert_not_called()

    def test_broom_attack_miss_trigger_accepts_ranged_and_effect_attacks(
        self,
    ):
        rng = Mock()
        rng.random.side_effect = [0.5, 0.5]
        broom, context, _ = self.make_broom_context(rng=rng)

        for attack_type in ("ranged", "effect"):
            self.resolve_opponent_attack(
                context,
                accuracy=0,
                attack_types=(attack_type,),
            )

        self.assertEqual(broom.miss_damage_bonus, 4)
        self.assertEqual(broom.effects[1].damage_modifier, 4)
        self.assertEqual(rng.random.call_count, 2)
        rng.randint.assert_not_called()

    def test_broom_multiple_opponent_misses_stack(self):
        rng = Mock()
        rng.random.side_effect = [0.5, 0.5, 0.5]
        broom, context, _ = self.make_broom_context(rng=rng)

        for _ in range(3):
            self.resolve_opponent_attack(context, accuracy=0)

        self.assertEqual(broom.miss_damage_bonus, 6)
        self.assertEqual(broom.effects[1].damage_modifier, 6)
        self.assertEqual(broom.effects[1].min_damage, 2)
        self.assertEqual(broom.effects[1].max_damage, 4)

    def test_broom_ignores_opponent_hits(self):
        rng = Mock()
        rng.random.return_value = 0.0
        rng.randint.return_value = 2
        broom, context, _ = self.make_broom_context(rng=rng)

        self.resolve_opponent_attack(
            context,
            accuracy=100,
            min_damage=2,
            max_damage=2,
        )

        self.assertEqual(broom.miss_damage_bonus, 0)
        self.assertEqual(broom.effects[1].damage_modifier, 0)
        self.assertEqual(context.owner.health, 98)

    def test_broom_pays_stamina_and_attacks_with_base_damage(self):
        rng = Mock()
        rng.random.side_effect = [0.0, 0.5]
        rng.randint.return_value = 2
        broom, context, _ = self.make_broom_context(
            frame_delta=1.7,
            stamina=5.0,
            rng=rng,
        )
        dispatch_spy = spy_on_activation_dispatch(
            context.battle_state
        )

        broom.activate_item(context)

        self.assertAlmostEqual(context.owner.stamina, 3.8)
        self.assertEqual(context.opponent.health, 98)
        rng.randint.assert_called_once_with(2, 4)
        self.assertEqual(rng.random.call_count, 2)
        dispatch_spy.assert_called_once_with(broom)

    def test_broom_applies_accumulated_bonus_then_clears_it_on_hit(
        self,
    ):
        rng = Mock()
        rng.random.side_effect = [0.5, 0.5, 0.0, 0.5]
        rng.randint.return_value = 6
        broom, context, _ = self.make_broom_context(
            frame_delta=1.7,
            stamina=5.0,
            rng=rng,
        )
        dispatch_spy = spy_on_activation_dispatch(
            context.battle_state
        )
        self.resolve_opponent_attack(context, accuracy=0)
        self.resolve_opponent_attack(context, accuracy=0)

        broom.activate_item(context)

        rng.randint.assert_called_once_with(6, 8)
        self.assertEqual(broom.miss_damage_bonus, 0)
        self.assertEqual(broom.effects[1].damage_modifier, 0)
        self.assertEqual(broom.effects[1].min_damage, 2)
        self.assertEqual(broom.effects[1].max_damage, 4)
        dispatch_spy.assert_called_once_with(broom)

    def test_broom_miss_retains_accumulated_bonus_and_skips_blind_roll(
        self,
    ):
        rng = Mock()
        rng.random.side_effect = [0.5, 0.5, 0.99]
        broom, context, _ = self.make_broom_context(
            frame_delta=1.7,
            stamina=5.0,
            rng=rng,
        )
        dispatch_spy = spy_on_activation_dispatch(
            context.battle_state
        )
        self.resolve_opponent_attack(context, accuracy=0)
        self.resolve_opponent_attack(context, accuracy=0)

        broom.activate_item(context)

        self.assertAlmostEqual(context.owner.stamina, 3.8)
        self.assertEqual(broom.miss_damage_bonus, 4)
        self.assertEqual(broom.effects[1].damage_modifier, 4)
        self.assertEqual(context.opponent.debuffs.Blind, 0)
        self.assertEqual(rng.random.call_count, 3)
        rng.randint.assert_not_called()
        dispatch_spy.assert_called_once_with(broom)

    def test_broom_retained_bonus_is_used_on_later_hit(self):
        rng = Mock()
        rng.random.side_effect = [
            0.5,
            0.5,
            0.99,
            0.0,
            0.5,
        ]
        rng.randint.return_value = 6
        broom, context, _ = self.make_broom_context(
            frame_delta=1.7,
            stamina=10.0,
            rng=rng,
        )
        self.resolve_opponent_attack(context, accuracy=0)
        self.resolve_opponent_attack(context, accuracy=0)
        broom.activate_item(context)

        broom.activate_item(context)

        rng.randint.assert_called_once_with(6, 8)
        self.assertEqual(broom.miss_damage_bonus, 0)
        self.assertEqual(broom.effects[1].damage_modifier, 0)

    def test_broom_insufficient_stamina_retains_bonus_without_rng(self):
        rng = Mock()
        rng.random.side_effect = [0.5]
        broom, context, _ = self.make_broom_context(
            frame_delta=1.7,
            stamina=1.0,
            rng=rng,
        )
        dispatch_spy = spy_on_activation_dispatch(
            context.battle_state
        )
        self.resolve_opponent_attack(context, accuracy=0)

        broom.activate_item(context)

        self.assertEqual(context.owner.stamina, 1.0)
        self.assertEqual(broom.miss_damage_bonus, 2)
        self.assertEqual(broom.effects[1].damage_modifier, 2)
        self.assertAlmostEqual(
            broom.triggers[0].cooldown_progress,
            0.0,
        )
        rng.random.assert_called_once_with()
        rng.randint.assert_not_called()
        dispatch_spy.assert_not_called()

    def test_broom_on_hit_inflicts_blind_when_chance_succeeds(self):
        rng = Mock()
        rng.random.side_effect = [0.0, 0.329]
        rng.randint.return_value = 2
        broom, context, _ = self.make_broom_context(
            frame_delta=1.7,
            stamina=5.0,
            opponent_blind=2,
            rng=rng,
        )

        broom.activate_item(context)

        self.assertEqual(context.opponent.debuffs.Blind, 3)
        self.assertEqual(
            rng.method_calls,
            [call.random(), call.randint(2, 4), call.random()],
        )

    def test_broom_on_hit_does_not_inflict_blind_when_chance_fails(
        self,
    ):
        rng = Mock()
        rng.random.side_effect = [0.0, 0.33]
        rng.randint.return_value = 2
        broom, context, _ = self.make_broom_context(
            frame_delta=1.7,
            stamina=5.0,
            opponent_blind=2,
            rng=rng,
        )

        broom.activate_item(context)

        self.assertEqual(context.opponent.debuffs.Blind, 2)
        self.assertEqual(rng.random.call_count, 2)
        rng.randint.assert_called_once_with(2, 4)

    def test_broom_clears_only_miss_bonus_and_preserves_external_modifier(
        self,
    ):
        rng = Mock()
        rng.random.side_effect = [
            0.5,
            0.5,
            0.0,
            0.5,
            0.0,
            0.5,
        ]
        rng.randint.side_effect = [11, 7]
        broom, context, _ = self.make_broom_context(
            frame_delta=1.7,
            stamina=10.0,
            rng=rng,
        )
        broom.effects[1].stack_damage_modifier(5)
        self.resolve_opponent_attack(context, accuracy=0)
        self.resolve_opponent_attack(context, accuracy=0)

        broom.activate_item(context)

        self.assertEqual(broom.miss_damage_bonus, 0)
        self.assertEqual(broom.effects[1].damage_modifier, 5)

        broom.activate_item(context)

        self.assertEqual(
            rng.randint.call_args_list,
            [call(11, 13), call(7, 9)],
        )
        self.assertEqual(broom.effects[1].damage_modifier, 5)

    def test_brooms_own_independent_miss_bonus_state(self):
        rng = Mock()
        rng.random.side_effect = [0.5, 0.0, 0.5]
        rng.randint.return_value = 4
        first = Broom(item_key="broom1", player_id=0)
        second = Broom(item_key="broom2", player_id=0)
        owner = PlayerState(
            player_id=0,
            health=100,
            max_health=100,
            stamina=10.0,
            max_stamina=10.0,
            items={"broom1": first, "broom2": second},
        )
        opponent = PlayerState(
            player_id=1,
            health=100,
            max_health=100,
            stamina=10.0,
            max_stamina=10.0,
        )
        battle = BattleState(
            players=[owner, opponent],
            active_items=[first, second],
            frame_delta=1.7,
            rng=rng,
        )
        context = BattleContext(battle, first, owner, opponent)

        self.resolve_opponent_attack(context, accuracy=0)

        self.assertEqual(first.miss_damage_bonus, 2)
        self.assertEqual(second.miss_damage_bonus, 2)

        first.activate_item(context)

        self.assertEqual(first.miss_damage_bonus, 0)
        self.assertEqual(first.effects[1].damage_modifier, 0)
        self.assertEqual(second.miss_damage_bonus, 2)
        self.assertEqual(second.effects[1].damage_modifier, 2)

    def test_battle_step_applies_natural_stamina_regen_before_banana(self):
        banana, context, _ = self.make_banana_context(
            frame_delta=1.0,
            health=5,
            max_health=10,
            stamina=3.0,
            max_stamina=5.0,
        )
        banana.triggers[0].cooldown_progress = 4.0

        context.battle_state.step()

        self.assertEqual(context.owner.health, 9)
        self.assertEqual(context.owner.stamina, 5.0)
        self.assertAlmostEqual(
            banana.triggers[0].cooldown_progress,
            0.0,
        )

    def make_banana_context(
        self,
        frame_delta=1.0,
        health=5,
        max_health=10,
        stamina=2.0,
        max_stamina=5.0,
        linked_item_specs=(),
        unlinked_item_specs=(),
    ):
        banana = Banana(item_key="banana1", player_id=0)
        linked_items = {}
        owner_items = {"banana1": banana}

        for item_key, item_id, item_types in (
            tuple(linked_item_specs) + tuple(unlinked_item_specs)
        ):
            item = Mock()
            item.item_id = item_id
            item.item_types = item_types
            item.linked_items = []
            linked_items[item_key] = item
            owner_items[item_key] = item

        for item_key, _, _ in linked_item_specs:
            banana.add_linked_item(item_key)

        owner = PlayerState(
            player_id=0,
            health=health,
            max_health=max_health,
            stamina=stamina,
            max_stamina=max_stamina,
            items=owner_items,
        )
        opponent = PlayerState(
            player_id=1,
            health=10,
            max_health=10,
            stamina=5.0,
            max_stamina=5.0,
        )
        battle_state = BattleState(
            players=[owner, opponent],
            active_items=[banana],
            frame_delta=frame_delta,
        )
        context = BattleContext(
            battle_state,
            banana,
            owner,
            opponent,
        )
        return banana, context, linked_items

    def make_garlic_context(
        self,
        frame_delta=1.0,
        block=0,
        opponent_vampirism=0,
        rng=None,
        linked_item_specs=(),
        unlinked_item_specs=(),
    ):
        garlic = Garlic(item_key="garlic1", player_id=0)
        linked_items = {}
        owner_items = {"garlic1": garlic}

        for item_key, item_id, item_types in (
            tuple(linked_item_specs) + tuple(unlinked_item_specs)
        ):
            item = Mock()
            item.item_id = item_id
            item.item_types = item_types
            item.linked_items = []
            linked_items[item_key] = item
            owner_items[item_key] = item

        for item_key, _, _ in linked_item_specs:
            garlic.add_linked_item(item_key)

        owner = PlayerState(
            player_id=0,
            health=10,
            max_health=10,
            block=block,
            stamina=5.0,
            max_stamina=5.0,
            items=owner_items,
        )
        opponent = PlayerState(
            player_id=1,
            health=10,
            max_health=10,
            stamina=5.0,
            max_stamina=5.0,
        )
        opponent.buffs.Vampirism = opponent_vampirism
        if rng is None:
            rng = Mock()
            rng.random.return_value = 0.5
        battle_state = BattleState(
            players=[owner, opponent],
            active_items=[garlic],
            frame_delta=frame_delta,
            rng=rng,
        )
        context = BattleContext(
            battle_state,
            garlic,
            owner,
            opponent,
        )
        return garlic, context, linked_items, rng

    def make_pan_context(
        self,
        frame_delta=1.0,
        stamina=5.0,
        opponent_health=100,
        empower=0,
        rng=None,
        linked_item_specs=(),
        unlinked_item_specs=(),
    ):
        pan = Pan(item_key="pan1", player_id=0)
        linked_items = {}
        owner_items = {"pan1": pan}

        for item_key, item_id, item_types in (
            tuple(linked_item_specs) + tuple(unlinked_item_specs)
        ):
            item = Mock()
            item.item_id = item_id
            item.item_types = item_types
            item.linked_items = []
            linked_items[item_key] = item
            owner_items[item_key] = item

        for item_key, _, _ in linked_item_specs:
            pan.add_linked_item(item_key)

        owner = PlayerState(
            player_id=0,
            health=100,
            max_health=100,
            stamina=stamina,
            max_stamina=10.0,
            items=owner_items,
        )
        owner.buffs.Empower = empower
        opponent = PlayerState(
            player_id=1,
            health=opponent_health,
            max_health=opponent_health,
            stamina=10.0,
            max_stamina=10.0,
        )
        if rng is None:
            rng = Mock()
        battle_state = BattleState(
            players=[owner, opponent],
            active_items=[pan],
            frame_delta=frame_delta,
            rng=rng,
        )
        context = BattleContext(
            battle_state,
            pan,
            owner,
            opponent,
        )
        return pan, context, linked_items, rng

    def make_rat_context(
        self,
        rng,
        frame_delta=3.3,
        opponent_health=10,
        opponent_block=0,
    ):
        rat = Rat(item_key="rat1", player_id=0)
        owner = PlayerState(
            player_id=0,
            health=10,
            max_health=10,
            items={"rat1": rat},
        )
        opponent = PlayerState(
            player_id=1,
            health=opponent_health,
            max_health=opponent_health,
            block=opponent_block,
        )
        battle_state = BattleState(
            players=[owner, opponent],
            active_items=[rat],
            frame_delta=frame_delta,
            rng=rng,
        )
        context = BattleContext(
            battle_state,
            rat,
            owner,
            opponent,
        )
        return rat, context

    def make_broom_context(
        self,
        frame_delta=1.0,
        stamina=5.0,
        opponent_health=100,
        opponent_blind=0,
        rng=None,
    ):
        broom = Broom(item_key="broom1", player_id=0)
        owner = PlayerState(
            player_id=0,
            health=100,
            max_health=100,
            stamina=stamina,
            max_stamina=10.0,
            items={"broom1": broom},
        )
        opponent = PlayerState(
            player_id=1,
            health=opponent_health,
            max_health=opponent_health,
            stamina=10.0,
            max_stamina=10.0,
        )
        opponent.debuffs.Blind = opponent_blind
        if rng is None:
            rng = Mock()
        battle_state = BattleState(
            players=[owner, opponent],
            active_items=[broom],
            frame_delta=frame_delta,
            rng=rng,
        )
        context = BattleContext(
            battle_state,
            broom,
            owner,
            opponent,
        )
        return broom, context, rng

    def resolve_opponent_attack(
        self,
        context,
        *,
        accuracy,
        attack_types=("melee",),
        min_damage=1,
        max_damage=1,
    ):
        event = AttackEvent(
            attacker=context.opponent,
            defender=context.owner,
            source_item=Mock(),
            attack_types=attack_types,
            min_damage=min_damage,
            max_damage=max_damage,
            accuracy=accuracy,
        )
        return context.battle_state.resolve_attack(event)

    def make_wooden_sword_context(
        self,
        rng,
        frame_delta,
        stamina,
    ):
        sword = WoodenSword(item_key="wooden_sword1", player_id=0)
        owner = PlayerState(
            player_id=0,
            health=10,
            max_health=10,
            stamina=stamina,
            max_stamina=5.0,
            items={"wooden_sword1": sword},
        )
        opponent = PlayerState(
            player_id=1,
            health=10,
            max_health=10,
            stamina=5.0,
            max_stamina=5.0,
        )
        battle_state = BattleState(
            players=[owner, opponent],
            active_items=[sword],
            frame_delta=frame_delta,
            rng=rng,
        )
        context = BattleContext(battle_state, sword, owner, opponent)
        return sword, context

    def make_shortbow_context(
        self,
        rng,
        frame_delta,
        stamina,
    ):
        shortbow = Shortbow(item_key="shortbow1", player_id=0)
        owner = PlayerState(
            player_id=0,
            health=10,
            max_health=10,
            stamina=stamina,
            max_stamina=5.0,
            items={"shortbow1": shortbow},
        )
        opponent = PlayerState(
            player_id=1,
            health=10,
            max_health=10,
            stamina=5.0,
            max_stamina=5.0,
        )
        battle_state = BattleState(
            players=[owner, opponent],
            active_items=[shortbow],
            frame_delta=frame_delta,
            rng=rng,
        )
        context = BattleContext(
            battle_state,
            shortbow,
            owner,
            opponent,
        )
        return shortbow, context


class GooblingSpecTest(unittest.TestCase):
    def make_linked_goobling_state(
        self,
        *,
        health=10,
        max_health=20,
        linked=True,
    ):
        source = WoodenSword(
            item_key="wooden_sword1",
            player_id=0,
        )
        goobling = Goobling(
            item_key="goobling1",
            player_id=0,
        )
        if linked:
            goobling.add_marker_item("star", source.item_key)
        owner = PlayerState(
            player_id=0,
            health=health,
            max_health=max_health,
            stamina=5.0,
            max_stamina=5.0,
            items={
                source.item_key: source,
                goobling.item_key: goobling,
            },
        )
        opponent = PlayerState(
            player_id=1,
            health=20,
            max_health=20,
            stamina=5.0,
            max_stamina=5.0,
        )
        battle = BattleState(
            players=[owner, opponent],
            active_items=[source],
        )
        context = ItemActivationContext(
            battle_state=battle,
            item=goobling,
            owner=owner,
            opponent=opponent,
            source_item=source,
        )
        return source, goobling, battle, owner, opponent, context

    def initialize_battle_for_test(
        self,
        player_placements,
        opponent_placements=(),
        *,
        health=20,
        max_health=20,
        stamina=5.0,
        max_stamina=5.0,
        item_factories=DEFAULT_ITEM_FACTORIES,
        item_catalog=ITEM_CATALOG,
    ):
        return initialize_battle(
            [
                {
                    "player_id": 0,
                    "health": health,
                    "max_health": max_health,
                    "stamina": stamina,
                    "max_stamina": max_stamina,
                    "placements": list(player_placements),
                },
                {
                    "player_id": 1,
                    "health": 20,
                    "max_health": 20,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": list(opponent_placements),
                },
            ],
            item_factories,
            item_catalog=item_catalog,
        )

    def test_activation_trigger_rejects_unknown_marker_type(self):
        for invalid in ("hex", "", None, 1):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    ActivationTrigger(invalid)

    def test_activation_trigger_only_validates_matching_activation_event(
        self,
    ):
        source, goobling, battle, owner, opponent, context = (
            self.make_linked_goobling_state()
        )
        trigger = ActivationTrigger("star")
        battle.rng = Mock()

        self.assertTrue(trigger.update(context))
        self.assertFalse(
            trigger.update(
                BattleContext(
                    battle_state=battle,
                    item=goobling,
                    owner=owner,
                    opponent=opponent,
                )
            )
        )
        goobling.marker_items["star"].clear()
        self.assertFalse(trigger.update(context))
        self.assertEqual(battle.rng.method_calls, [])
        self.assertIsNotNone(source)

    def test_slime_activation_trigger_rejects_invalid_required_count(
        self,
    ):
        for invalid in (0, -1, 1.0, True, None):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    SlimeActivationTrigger(invalid)

    def test_slime_activation_trigger_ignores_base_context(self):
        source, goobling, battle, owner, opponent, _ = (
            self.make_linked_goobling_state()
        )
        trigger = goobling.triggers[0]
        context = BattleContext(
            battle_state=battle,
            item=goobling,
            owner=owner,
            opponent=opponent,
        )

        self.assertFalse(trigger.update(context))
        self.assertEqual(trigger.activation_count, 0)
        self.assertIsNotNone(source)

    def test_slime_activation_trigger_ignores_unlinked_source(self):
        _, goobling, _, _, _, context = (
            self.make_linked_goobling_state(linked=False)
        )
        trigger = goobling.triggers[0]

        self.assertFalse(trigger.update(context))
        self.assertEqual(trigger.activation_count, 0)

    def test_slime_activation_trigger_fires_every_third_event(self):
        _, goobling, _, _, _, context = (
            self.make_linked_goobling_state()
        )
        trigger = goobling.triggers[0]

        results = [trigger.update(context) for _ in range(6)]

        self.assertEqual(
            results,
            [False, False, True, False, False, True],
        )
        self.assertEqual(trigger.activation_count, 0)

    def test_slime_activation_trigger_instances_are_independent(self):
        first = SlimeActivationTrigger(3)
        second = SlimeActivationTrigger(3)
        source, goobling, _, _, _, context = (
            self.make_linked_goobling_state()
        )
        other_goobling = Goobling(
            item_key="goobling2",
            player_id=0,
        )
        other_goobling.add_marker_item("star", source.item_key)
        other_context = ItemActivationContext(
            battle_state=context.battle_state,
            item=other_goobling,
            owner=context.owner,
            opponent=context.opponent,
            source_item=source,
        )

        self.assertFalse(first.update(context))
        self.assertFalse(first.update(context))
        self.assertFalse(second.update(other_context))
        self.assertTrue(first.update(context))
        self.assertFalse(second.update(other_context))
        self.assertTrue(second.update(other_context))
        self.assertEqual(first.activation_count, 0)
        self.assertEqual(second.activation_count, 0)
        self.assertIsNot(goobling, other_goobling)

    def test_goobling_is_registered_with_metadata_and_components(self):
        goobling = DEFAULT_ITEM_FACTORIES["goobling"](
            item_id="goobling",
            item_key="goobling1",
            player_id=0,
        )

        self.assertIsInstance(goobling, Goobling)
        self.assertEqual(goobling.item_id, "goobling")
        self.assertEqual(goobling.display_name, "Goobling")
        self.assertEqual(goobling.item_classes, ("Neutral",))
        self.assertEqual(goobling.rarity, "Common")
        self.assertEqual(goobling.cost, 2)
        self.assertEqual(goobling.item_types, ("Pet",))
        self.assertEqual(goobling.icon_types, ())
        self.assertFalse(goobling.is_active_item)
        self.assertEqual(goobling.socket_count, 0)
        self.assertIsInstance(
            goobling.triggers[0],
            SlimeActivationTrigger,
        )
        self.assertEqual(goobling.triggers[0].required_activations, 3)
        self.assertIsInstance(goobling.effects[0], HealEffect)
        self.assertEqual(goobling.effects[0].amount, 4)

    def test_gooblings_own_independent_trigger_and_effect_instances(self):
        first = Goobling(item_key="goobling1", player_id=0)
        second = Goobling(item_key="goobling2", player_id=0)

        self.assertIsNot(first.triggers[0], second.triggers[0])
        self.assertIsNot(first.effects[0], second.effects[0])
        first.triggers[0].activation_count = 2
        self.assertEqual(second.triggers[0].activation_count, 0)

    def test_goobling_heals_four_on_third_linked_activation(self):
        source, goobling, battle, owner, _, _ = (
            self.make_linked_goobling_state()
        )

        battle.dispatch_item_activation(source)
        self.assertEqual(owner.health, 10)
        battle.dispatch_item_activation(source)
        self.assertEqual(owner.health, 10)
        battle.dispatch_item_activation(source)

        self.assertEqual(owner.health, 14)
        self.assertEqual(goobling.triggers[0].activation_count, 0)

    def test_goobling_repeats_after_each_three_activations(self):
        source, goobling, battle, owner, _, _ = (
            self.make_linked_goobling_state(health=10, max_health=30)
        )

        for _ in range(6):
            battle.dispatch_item_activation(source)

        self.assertEqual(owner.health, 18)
        self.assertEqual(goobling.triggers[0].activation_count, 0)

    def test_goobling_consumes_third_activation_at_full_health(self):
        source, goobling, battle, owner, _, _ = (
            self.make_linked_goobling_state(health=20, max_health=20)
        )

        for _ in range(4):
            battle.dispatch_item_activation(source)

        self.assertEqual(owner.health, 20)
        self.assertEqual(goobling.triggers[0].activation_count, 1)

    def test_goobling_emits_own_activation_even_when_heal_has_no_effect(
        self,
    ):
        source, goobling, battle, _, _, _ = (
            self.make_linked_goobling_state(health=20, max_health=20)
        )
        original_dispatch = battle.dispatch_item_activation
        battle.dispatch_item_activation = Mock(wraps=original_dispatch)

        for _ in range(3):
            battle.dispatch_item_activation(source)

        self.assertEqual(
            [
                dispatch_call
                for dispatch_call in battle.dispatch_item_activation.call_args_list
                if dispatch_call == call(goobling)
            ],
            [call(goobling)],
        )

    def test_initializer_links_goobling_left_and_right_stars(self):
        battle = self.initialize_battle_for_test(
            [
                {
                    "item_id": "stone",
                    "x": 0,
                    "y": 0,
                    "rotation": 0,
                },
                {
                    "item_id": "goobling",
                    "x": 1,
                    "y": 0,
                    "rotation": 0,
                },
                {
                    "item_id": "stone",
                    "x": 2,
                    "y": 0,
                    "rotation": 0,
                },
            ]
        )

        goobling = battle.players[0].items["goobling1"]
        self.assertEqual(
            goobling.linked_items,
            ["stone1", "stone2"],
        )

    def test_initializer_deduplicates_source_covering_both_goobling_stars(
        self,
    ):
        catalog = dict(ITEM_CATALOG)
        catalog["wide_source"] = {
            "item_id": "wide_source",
            "shape_cells": [[0, 0], [2, 0]],
            "star_cells": [],
        }
        factories = dict(DEFAULT_ITEM_FACTORIES)
        factories["wide_source"] = (
            lambda item_id, item_key, player_id: WoodenSword(
                item_id=item_id,
                item_key=item_key,
                player_id=player_id,
            )
        )
        battle = self.initialize_battle_for_test(
            [
                {
                    "item_id": "goobling",
                    "x": 1,
                    "y": 0,
                    "rotation": 0,
                },
                {
                    "item_id": "wide_source",
                    "x": 0,
                    "y": 0,
                    "rotation": 0,
                },
            ],
            item_factories=factories,
            item_catalog=catalog,
        )
        source = battle.players[0].items["wide_source1"]
        goobling = battle.players[0].items["goobling1"]

        self.assertEqual(goobling.linked_items, ["wide_source1"])
        battle.dispatch_item_activation(source)
        self.assertEqual(goobling.triggers[0].activation_count, 1)

    def test_goobling_catalog_rotates_shape_and_two_stars(self):
        expected_stars = {
            0: [(2, 3), (4, 3)],
            90: [(3, 2), (3, 4)],
            180: [(4, 3), (2, 3)],
            270: [(3, 4), (3, 2)],
        }

        for rotation, stars in expected_stars.items():
            with self.subTest(rotation=rotation):
                placed = place_item(
                    ITEM_CATALOG["goobling"],
                    {
                        "item_key": "goobling1",
                        "x": 3,
                        "y": 3,
                        "rotation": rotation,
                    },
                )
                self.assertEqual(placed["occupied_cells"], [(3, 3)])
                self.assertEqual(placed["star_cells"], stars)

    def test_initializer_builds_goobling_as_passive_item(self):
        battle = self.initialize_battle_for_test(
            [
                {
                    "item_id": "goobling",
                    "x": 0,
                    "y": 0,
                    "rotation": 0,
                }
            ]
        )
        goobling = battle.players[0].items["goobling1"]

        self.assertIsInstance(goobling, Goobling)
        self.assertNotIn(goobling, battle.active_items)

    def test_linked_start_of_battle_item_does_not_advance_goobling(self):
        cases = (
            ("healing_herbs", "Regeneration", 2),
            ("flame", "Heat", 1),
        )
        for item_id, buff_name, amount in cases:
            with self.subTest(item_id=item_id):
                battle = self.initialize_battle_for_test(
                    [
                        {
                            "item_id": item_id,
                            "x": 0,
                            "y": 0,
                            "rotation": 0,
                        },
                        {
                            "item_id": "goobling",
                            "x": 1,
                            "y": 0,
                            "rotation": 0,
                        },
                    ]
                )
                goobling = battle.players[0].items["goobling1"]

                battle.step()

                self.assertEqual(
                    getattr(battle.players[0].buffs, buff_name),
                    amount,
                )
                self.assertEqual(
                    goobling.triggers[0].activation_count,
                    0,
                )
                battle.step()
                self.assertEqual(
                    goobling.triggers[0].activation_count,
                    0,
                )

    def test_linked_weapon_without_stamina_does_not_advance_goobling(self):
        battle = self.initialize_battle_for_test(
            [
                {
                    "item_id": "wooden_sword",
                    "x": 0,
                    "y": 0,
                    "rotation": 0,
                },
                {
                    "item_id": "goobling",
                    "x": 1,
                    "y": 0,
                    "rotation": 0,
                },
            ],
            stamina=0.0,
            max_stamina=0.0,
        )
        battle.frame_delta = 1.4
        battle.rng = Mock()
        goobling = battle.players[0].items["goobling1"]

        battle.step()

        self.assertEqual(goobling.triggers[0].activation_count, 0)
        battle.rng.random.assert_not_called()

    def test_linked_weapon_miss_still_advances_goobling(self):
        battle = self.initialize_battle_for_test(
            [
                {
                    "item_id": "wooden_sword",
                    "x": 0,
                    "y": 0,
                    "rotation": 0,
                },
                {
                    "item_id": "goobling",
                    "x": 1,
                    "y": 0,
                    "rotation": 0,
                },
            ]
        )
        battle.frame_delta = 1.4
        battle.rng = Mock()
        battle.rng.random.return_value = 0.99
        goobling = battle.players[0].items["goobling1"]

        battle.step()

        self.assertEqual(goobling.triggers[0].activation_count, 1)
        battle.rng.randint.assert_not_called()

    def test_linked_wooden_buckler_advances_on_successful_reaction(self):
        battle = self.initialize_battle_for_test(
            [
                {
                    "item_id": "wooden_buckler",
                    "x": 0,
                    "y": 0,
                    "rotation": 0,
                },
                {
                    "item_id": "goobling",
                    "x": 2,
                    "y": 0,
                    "rotation": 0,
                },
            ],
            [
                {
                    "item_id": "wooden_sword",
                    "x": 4,
                    "y": 0,
                    "rotation": 0,
                }
            ],
        )
        battle.frame_delta = 1.4
        battle.rng = Mock()
        battle.rng.random.side_effect = [0.0, 0.29]
        battle.rng.randint.return_value = 1
        goobling = battle.players[0].items["goobling1"]

        battle.step()

        self.assertEqual(goobling.triggers[0].activation_count, 1)
        self.assertEqual(battle.players[0].health, 20)

    def test_linked_wooden_buckler_does_not_advance_when_chance_fails(
        self,
    ):
        battle = self.initialize_battle_for_test(
            [
                {
                    "item_id": "wooden_buckler",
                    "x": 0,
                    "y": 0,
                    "rotation": 0,
                },
                {
                    "item_id": "goobling",
                    "x": 2,
                    "y": 0,
                    "rotation": 0,
                },
            ],
            [
                {
                    "item_id": "wooden_sword",
                    "x": 4,
                    "y": 0,
                    "rotation": 0,
                }
            ],
        )
        battle.frame_delta = 1.4
        battle.rng = Mock()
        battle.rng.random.side_effect = [0.0, 0.30]
        battle.rng.randint.return_value = 1
        goobling = battle.players[0].items["goobling1"]

        battle.step()

        self.assertEqual(goobling.triggers[0].activation_count, 0)
        self.assertEqual(battle.players[0].health, 19)

    def test_linked_broom_opponent_miss_branch_does_not_advance_goobling(
        self,
    ):
        battle = self.initialize_battle_for_test(
            [
                {
                    "item_id": "broom",
                    "x": 0,
                    "y": 0,
                    "rotation": 0,
                },
                {
                    "item_id": "goobling",
                    "x": 1,
                    "y": 0,
                    "rotation": 0,
                },
            ],
            [
                {
                    "item_id": "wooden_sword",
                    "x": 4,
                    "y": 0,
                    "rotation": 0,
                }
            ],
        )
        battle.frame_delta = 1.4
        battle.rng = Mock()
        battle.rng.random.return_value = 0.99
        broom = battle.players[0].items["broom1"]
        goobling = battle.players[0].items["goobling1"]

        battle.step()

        self.assertEqual(broom.miss_damage_bonus, 2)
        self.assertEqual(goobling.triggers[0].activation_count, 0)

    def test_linked_broom_weapon_miss_advances_without_blind_roll(self):
        battle = self.initialize_battle_for_test(
            [
                {
                    "item_id": "broom",
                    "x": 0,
                    "y": 0,
                    "rotation": 0,
                },
                {
                    "item_id": "goobling",
                    "x": 1,
                    "y": 0,
                    "rotation": 0,
                },
            ]
        )
        battle.frame_delta = 1.7
        battle.rng = Mock()
        battle.rng.random.return_value = 0.99
        broom = battle.players[0].items["broom1"]
        goobling = battle.players[0].items["goobling1"]
        broom.miss_damage_bonus = 2
        broom.effects[1].stack_damage_modifier(2)

        battle.step()

        self.assertEqual(broom.miss_damage_bonus, 2)
        self.assertEqual(goobling.triggers[0].activation_count, 1)
        self.assertEqual(battle.rng.random.call_count, 1)
        battle.rng.randint.assert_not_called()

    def test_two_gooblings_listening_to_same_source_both_advance(self):
        battle = self.initialize_battle_for_test(
            [
                {
                    "item_id": "stone",
                    "x": 2,
                    "y": 1,
                    "rotation": 0,
                },
                {
                    "item_id": "goobling",
                    "x": 1,
                    "y": 1,
                    "rotation": 0,
                },
                {
                    "item_id": "goobling",
                    "x": 3,
                    "y": 1,
                    "rotation": 0,
                },
            ]
        )
        source = battle.players[0].items["stone1"]
        first = battle.players[0].items["goobling1"]
        second = battle.players[0].items["goobling2"]

        battle.dispatch_item_activation(source)

        self.assertEqual(first.triggers[0].activation_count, 1)
        self.assertEqual(second.triggers[0].activation_count, 1)

    def test_goobling_activation_can_advance_another_goobling(self):
        source = WoodenSword(
            item_key="wooden_sword1",
            player_id=0,
        )
        first = Goobling(item_key="goobling1", player_id=0)
        second = Goobling(item_key="goobling2", player_id=0)
        first.add_marker_item("star", source.item_key)
        second.add_marker_item("star", first.item_key)
        owner = PlayerState(
            player_id=0,
            health=10,
            max_health=20,
            items={
                source.item_key: source,
                first.item_key: first,
                second.item_key: second,
            },
        )
        opponent = PlayerState(player_id=1, health=20, max_health=20)
        battle = BattleState(players=[owner, opponent])

        for _ in range(3):
            battle.dispatch_item_activation(source)

        self.assertEqual(owner.health, 14)
        self.assertEqual(first.triggers[0].activation_count, 0)
        self.assertEqual(second.triggers[0].activation_count, 1)

    def test_simple_start_of_battle_items_do_not_emit_activation(self):
        for item_type in (
            PocketSand,
            HealingHerbs,
            Flame,
            WalrusTusk,
            Whetstone,
        ):
            with self.subTest(item_type=item_type.__name__):
                item = item_type(
                    item_key=f"{item_type.item_id}1",
                    player_id=0,
                )
                owner_items = {item.item_key: item}
                if isinstance(item, Whetstone):
                    sword = WoodenSword(
                        item_key="wooden_sword1",
                        player_id=0,
                    )
                    owner_items[sword.item_key] = sword
                    item.add_linked_item(sword.item_key)
                owner = PlayerState(
                    player_id=0,
                    health=20,
                    max_health=20,
                    items=owner_items,
                )
                opponent = PlayerState(
                    player_id=1,
                    health=20,
                    max_health=20,
                )
                battle = BattleState(players=[owner, opponent])
                battle.dispatch_item_activation = Mock()

                item.activate_item(battle.build_context(item))

                battle.dispatch_item_activation.assert_not_called()


if __name__ == "__main__":
    unittest.main()
