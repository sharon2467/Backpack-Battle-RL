import unittest
from dataclasses import replace
from unittest.mock import Mock

from battle_module_v1 import (
    ATTACK_PHASE_CHARACTER_ATTACKED, ATTACK_PHASE_PRE_TAKE_DAMAGE,
    BattleState, BuffSlot, PlayerState, make_attack_event,
)
from item_factory_registry_v1 import (
    Flame, Garlic, Goobling, HealingHerbs, MagicForDummies,
    PocketSand, Rat, Stone, WalrusTusk, WandOfEquilibrium,
    Whetstone, WoodenBuckler, WoodenSword,
)


class ItemBehaviorAlignmentTest(unittest.TestCase):
    def battle(self, *items):
        owner = PlayerState(player_id=0, health=20, max_health=20,
                            items={item.item_key: item for item in items})
        enemy = PlayerState(player_id=1, health=20, max_health=20,
                            stamina=5, max_stamina=5)
        return BattleState(players=[owner, enemy])

    def test_stone_breaks_armor_before_absorption_and_not_on_miss(self):
        for roll, expected_health, expected_block in ((0.0, 18, 0), (0.99, 20, 4)):
            with self.subTest(roll=roll):
                stone = Stone(item_key="stone", player_id=0)
                battle = self.battle(stone)
                battle.players[1].block = 4
                # Avoid the initial >60% accuracy failure-streak bonus.
                battle.players[1].accuracy_rng.last_result = True
                battle.rng = Mock(random=Mock(return_value=roll),
                                  randint=Mock(return_value=2))
                stone.run_effect([True], battle.build_context(stone))
                self.assertEqual(battle.players[1].health, expected_health)
                self.assertEqual(battle.players[1].block, expected_block)

    def test_buckler_linked_heal_runs_after_damage(self):
        shield = WoodenBuckler(item_key="shield", player_id=0)
        slime = Goobling(item_key="slime", player_id=0)
        slime.add_marker_item("star", "shield")
        battle = self.battle(shield, slime)
        battle.prepareItems()
        slime.triggers[0].activation_count = 2
        battle.players[0].max_health = 20
        battle.rng = Mock(random=Mock(return_value=0.0),
                          randint=Mock(return_value=10))
        sword = WoodenSword(item_key="sword", player_id=1)
        battle.players[1].items[sword.item_key] = sword
        event = make_attack_event(
            attacker=battle.players[1], defender=battle.players[0],
            source_item=sword, attack_types=("melee",),
            min_damage=10, max_damage=10, accuracy=100,
        )
        battle.resolve_attack(event)
        # Damage 10 - shield 7 = 3; linked heal then restores the missing HP.
        self.assertEqual(event.health_damage, 3)
        self.assertEqual(battle.players[0].health, 20)
        self.assertAlmostEqual(battle.players[1].stamina, 4.7)
        self.assertIsNone(shield.blocked_attack_event)
        actions = [entry["data"]["action"] for entry in battle.log]
        self.assertLess(actions.index("attack"), actions.index("remove_stamina"))
        self.assertLess(actions.index("attack"), actions.index("heal"))

    def test_buckler_only_finishes_matching_event(self):
        shield = WoodenBuckler(item_key="shield", player_id=0)
        battle = self.battle(shield)
        battle.rng = Mock(random=Mock(return_value=0.0))
        event = make_attack_event(
            attacker=battle.players[1], defender=battle.players[0],
            source_item=None, attack_types=("melee",), min_damage=10, max_damage=10,
        )
        event.hit = True
        event.pending_damage = 10
        def dispatch(phase, attack):
            context = battle.build_attack_reaction_context(shield, phase, attack)
            shield.activate_item(context.for_item(shield))
        dispatch(ATTACK_PHASE_PRE_TAKE_DAMAGE, event)
        self.assertEqual(battle.players[1].stamina, 5)
        dispatch(ATTACK_PHASE_CHARACTER_ATTACKED, replace(event))
        self.assertEqual(battle.players[1].stamina, 5)
        dispatch(ATTACK_PHASE_CHARACTER_ATTACKED, event)
        self.assertAlmostEqual(battle.players[1].stamina, 4.7)
        dispatch(ATTACK_PHASE_CHARACTER_ATTACKED, event)
        self.assertAlmostEqual(battle.players[1].stamina, 4.7)

    def test_start_items_and_empty_mana_book_advance_linked_slime(self):
        for cls in (PocketSand, HealingHerbs, Flame, WalrusTusk, Whetstone, MagicForDummies):
            with self.subTest(item=cls.__name__):
                source = cls(item_key="source", player_id=0)
                slime = Goobling(item_key="slime", player_id=0)
                slime.add_marker_item("star", "source")
                battle = self.battle(source, slime)
                battle.prepareItems()
                if isinstance(source, MagicForDummies):
                    source.run_effect([True], battle.build_context(source))
                else:
                    battle.start_combat()
                self.assertEqual(slime.triggers[0].activation_count, 1)
                self.assertEqual(battle.players[0].max_health, 20)

    def test_wand_can_select_every_tied_resource(self):
        for name in WandOfEquilibrium.RESOURCE_NAMES:
            with self.subTest(name=name):
                wand = WandOfEquilibrium(item_key="wand", player_id=0)
                battle = self.battle(wand)
                battle.rng = Mock(choice=Mock(return_value=name))
                wand.run_effect([True], battle.build_context(wand))
                self.assertEqual(getattr(battle.players[0].buffs, name), 1)
                battle.rng.choice.assert_called_once_with(list(wand.RESOURCE_NAMES))
                battle.players[0].buffs = BuffSlot(Mana=12, Luck=12, Regeneration=11)
                battle.rng.choice.side_effect = ["Regeneration", name]
                wand.run_effect([True], battle.build_context(wand))
                self.assertEqual(getattr(battle.players[0].buffs, name), 11)
                self.assertEqual(battle.players[0].buffs.Empower, 1)

    def test_wand_excludes_non_tied_resources(self):
        wand = WandOfEquilibrium(item_key="wand", player_id=0)
        rng = Mock(choice=Mock(side_effect=lambda candidates: candidates[-1]))
        buffs = BuffSlot(Mana=1, Luck=1, Regeneration=5)
        self.assertEqual(wand._least_resource_name(buffs, rng), "Luck")
        rng.choice.assert_called_with(["Mana", "Luck"])
        self.assertEqual(wand._most_resource_name(buffs, rng), "Regeneration")
        rng.choice.assert_called_with(["Regeneration"])

    def test_item_chance_states_are_independent_and_reset_on_prepare(self):
        a = Garlic(item_key="a", player_id=0)
        b = Garlic(item_key="b", player_id=0)
        rng = Mock(random=Mock(return_value=0.2))
        self.assertTrue(a.roll_chance(0.3, rng))
        self.assertFalse(a.roll_chance(0.3, rng))
        self.assertTrue(b.roll_chance(0.3, rng))
        battle = self.battle(a, b)
        battle.prepareItems()
        self.assertEqual(a.chance_rng.expected_wins, 0)
        self.assertIsNone(a.chance_rng.last_roll)
        self.assertTrue(a.roll_chance(0.3, rng))

    def test_item_chance_endpoints_and_inclusive_boundary(self):
        item = Garlic(item_key="garlic", player_id=0)
        rng = Mock(random=Mock(return_value=0.3))
        self.assertFalse(item.roll_chance(0, rng))
        self.assertTrue(item.roll_chance(1, rng))
        rng.random.assert_not_called()
        self.assertTrue(item.roll_chance(0.3, rng))

    def test_rat_shares_chance_state_between_poison_and_blind(self):
        rat = Rat(item_key="rat", player_id=0)
        battle = self.battle(rat)
        battle.rng = Mock(random=Mock(side_effect=[0.8, 0.9, 0.08]),
                          randint=Mock(return_value=5))
        rat.run_effect([True], battle.build_context(rat))
        self.assertEqual(battle.players[1].debuffs.Poison, 1)
        # Prior success halves the subsequent 10% roll to 5%.
        self.assertEqual(battle.players[1].debuffs.Blind, 0)
        self.assertAlmostEqual(rat.chance_rng.expected_wins, 0.85)
        self.assertEqual(rat.chance_rng.wins, 1)


if __name__ == "__main__":
    unittest.main()
