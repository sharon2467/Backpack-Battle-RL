import random
import unittest
from unittest.mock import Mock

from battle_module_v1 import BattleState, PlayerState
from item_effects_v1 import AttackEffect, SUPPORTED_ATTACK_TYPES
from item_factory_registry_v1 import Broom, Rat, Weapon


class TupleWeapon(Weapon):
    item_types = ("Weapon",)


class AttackTypeTupleTest(unittest.TestCase):
    def battle(self, item):
        return BattleState(
            players=[
                PlayerState(player_id=0, health=20, max_health=20,
                            stamina=3, max_stamina=5, items={item.item_key: item}),
                PlayerState(player_id=1, health=100, max_health=100),
            ],
            rng=random.Random(17),
        )

    def test_each_supported_type_accepts_a_single_element_tuple(self):
        source = Rat(item_key="source", player_id=0)
        battle = self.battle(source)
        battle.resolve_attack = Mock(return_value=Mock(hit=True))
        context = battle.build_context(source)
        for kind in SUPPORTED_ATTACK_TYPES:
            with self.subTest(kind=kind):
                self.assertTrue(AttackEffect(2, 3, 100).apply(context, (kind,)))
                event = battle.resolve_attack.call_args.args[0]
                self.assertEqual(event.attack_types, (kind,))
                self.assertIsInstance(event.attack_types, tuple)

    def test_invalid_type_inputs_fail_before_state_changes(self):
        source = Rat(item_key="source", player_id=0)
        battle = self.battle(source)
        battle.resolve_attack = Mock()
        context = battle.build_context(source)
        for invalid in (None, "melee", "effect", [], ["melee"], (),
                        ("magic",), ("melee", "magic"), (None,), (("melee",),)):
            with self.subTest(attack_type=invalid):
                effect = AttackEffect(1, 2, 100)
                with self.assertRaisesRegex(ValueError, "unsupported attack type"):
                    effect.apply(context, invalid)
                self.assertFalse(effect.damage_modifier_prepared)
                self.assertEqual(effect.damage_modifier, 0)
                battle.resolve_attack.assert_not_called()
                self.assertEqual(battle.log, [])

    def test_mixed_weapon_types_preserve_order_flags_and_all_damage_factors(self):
        kinds = ("effect", "ranged", "melee")
        weapon = TupleWeapon(item_key="mixed", player_id=0, cooldown=1,
                             min_damage=10, max_damage=10, accuracy=100,
                             stamina_cost=1, attack_types=kinds)
        battle = self.battle(weapon)
        battle.players[0].typed_damage_factors.update(melee=0.1, ranged=0.2, effect=0.3)
        battle.prepareItems()
        battle.start_combat()
        battle.resolve_attack = Mock(wraps=battle.resolve_attack)
        weapon.run_effect([True], battle.build_context(weapon))
        event = battle.resolve_attack.call_args.args[0]
        self.assertEqual(weapon.attack_types, kinds)
        self.assertIsInstance(weapon.attack_types, tuple)
        self.assertEqual(event.attack_types, kinds)
        self.assertTrue(event.can_be_blocked)
        self.assertTrue(event.can_be_spiked)
        self.assertTrue(event.can_be_vampiric)
        self.assertTrue(event.can_activate_item)
        self.assertTrue(event.can_miss)
        self.assertTrue(event.can_crit)
        self.assertEqual(event.health_damage, 16)
        self.assertEqual(battle.players[1].health, 84)
        self.assertEqual(battle.players[0].stamina, 2)
        self.assertEqual(sum(row["data"]["action"] == "item_activation"
                             for row in battle.log), 1)

    def test_ranged_and_effect_flags_keep_ranged_precedence(self):
        source = Rat(item_key="source", player_id=0)
        battle = self.battle(source)
        battle.resolve_attack = Mock(return_value=Mock(hit=True))
        kinds = ("effect", "ranged")
        AttackEffect(1, 1, 100).apply(battle.build_context(source), kinds)
        event = battle.resolve_attack.call_args.args[0]
        self.assertEqual(event.attack_types, kinds)
        self.assertTrue(event.can_miss)
        self.assertTrue(event.can_be_spiked)
        self.assertTrue(event.can_be_vampiric)

    def test_broom_and_rat_real_calls_use_type_tuples(self):
        for cls, kinds, results in ((Broom, ("melee",), [True, False]),
                                    (Rat, ("effect",), [True])):
            with self.subTest(item=cls.__name__):
                source = cls(item_key="source", player_id=0)
                battle = self.battle(source)
                battle.prepareItems()
                battle.start_combat()
                battle.resolve_attack = Mock(wraps=battle.resolve_attack)
                source.run_effect(results, battle.build_context(source))
                event = battle.resolve_attack.call_args.args[0]
                self.assertEqual(event.attack_types, kinds)
                self.assertTrue(event.hit)
                self.assertLess(battle.players[1].health, 100)
                self.assertEqual(sum(row["data"]["action"] == "item_activation"
                                     for row in battle.log), 1)


if __name__ == "__main__":
    unittest.main()
