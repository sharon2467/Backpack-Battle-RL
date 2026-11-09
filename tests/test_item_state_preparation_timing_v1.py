import random
import unittest
from unittest.mock import Mock

from battle_module_v1 import BattleState, PlayerState
from item_effects_v1 import GainBuffEffect
from item_factory_registry_v1 import (
    Banana, BattleItem, Garlic, MagicForDummies, Pan, Rat, Twine, Whetstone,
)
from item_triggers_v1 import CooldownTrigger


class ItemStatePreparationTimingTest(unittest.TestCase):
    def stub(self, key, *, types=(), classes=("Neutral",), crafted=False, item_id=None):
        item = BattleItem(
            item_key=key, player_id=0, item_id=item_id or key,
            item_types=types, item_classes=classes,
            effects=[GainBuffEffect("Heat", 0)],
        )
        item.is_crafted = crafted
        return item

    def battle(self, *items):
        return BattleState(
            players=[
                PlayerState(player_id=0, health=10, max_health=30, stamina=0,
                            max_stamina=10, items={i.item_key: i for i in items}),
                PlayerState(player_id=1, health=100, max_health=100),
            ],
            active_items=[i for i in items if i.is_active_item],
            rng=random.Random(17),
        )

    def test_six_items_become_ready_in_their_source_phases_without_effects(self):
        book = MagicForDummies(item_key="book", player_id=0)
        twine = Twine(item_key="twine", player_id=0)
        banana = Banana(item_key="banana", player_id=0)
        garlic = Garlic(item_key="garlic", player_id=0)
        pan = Pan(item_key="pan", player_id=0)
        rat = Rat(item_key="rat", player_id=0)
        spell = self.stub("spell", types=("Spell",))
        crafted = self.stub("crafted", types=("Spell",), crafted=True)
        dual = self.stub("dual", types=("Pet", "Food"), classes=("Ranger",))
        same_food = self.stub("same_food", types=("Food",), item_id="banana")
        book.add_marker_item("star", spell.item_key)
        book.add_marker_item("star", spell.item_key)
        book.add_marker_item("star", crafted.item_key)
        book.add_marker_item("diamond", dual.item_key)
        twine.add_marker_item("star", rat.item_key)
        twine.add_marker_item("diamond", spell.item_key)
        twine.add_marker_item("diamond", dual.item_key)
        banana.add_marker_item("star", garlic.item_key)
        banana.add_marker_item("star", same_food.item_key)
        garlic.add_marker_item("star", banana.item_key)
        pan.add_marker_item("star", banana.item_key)
        pan.add_marker_item("star", garlic.item_key)
        pan.add_marker_item("diamond", dual.item_key)
        rat.add_marker_item("star", banana.item_key)
        rat.add_marker_item("star", dual.item_key)
        rat.add_marker_item("star", dual.item_key)
        rat.add_marker_item("diamond", garlic.item_key)
        banana.triggers[0].stack_speed_modifier(0.2)
        rat.triggers[0].stack_speed_modifier(0.2)
        battle = self.battle(book, twine, banana, garlic, pan, rat,
                             spell, crafted, dual, same_food)
        battle.prepareItems()

        self.assertEqual(book.spell_weight, 3)
        self.assertEqual(book.effects[1].amount, 17)
        self.assertEqual(twine.neutral_item_count, 1)
        self.assertEqual(banana.triggers[0].qualifying_food_count, 1)
        self.assertAlmostEqual(banana.triggers[0].speed_modifiers, 0.3)
        self.assertAlmostEqual(garlic.triggers[0].speed_modifiers, 0.1)
        self.assertEqual(pan.effects[1].damage_modifier, 0)
        self.assertAlmostEqual(rat.triggers[0].speed_modifiers, 0.2)
        for item in battle.battle_items:
            item.preCombatStart(battle.build_context(item))
        self.assertEqual(pan.effects[1].qualifying_food_count, 2)
        self.assertEqual(pan.effects[1].damage_modifier, 2)
        self.assertTrue(pan.effects[1].damage_modifier_prepared)
        self.assertAlmostEqual(banana.triggers[0].speed_modifiers, 0.3)
        self.assertAlmostEqual(rat.triggers[0].speed_modifiers, 0.2)
        for item in battle.battle_items:
            item.combatStart(battle.build_context(item))
        self.assertAlmostEqual(rat.triggers[0].speed_modifiers, 0.5)
        self.assertIs(type(rat.triggers[0]), CooldownTrigger)
        self.assertEqual((battle.frame, battle.time), (0, 0.0))
        self.assertEqual((battle.players[0].health, battle.players[0].max_health,
                          battle.players[0].stamina, battle.players[0].buffs.Mana),
                         (10, 30, 0, 0))
        self.assertTrue(all(t.cooldown_progress == 0 for i in (book, banana, garlic, pan, rat)
                            for t in i.triggers))
        self.assertEqual(battle.log, [])

    def test_global_start_observers_see_prepared_food_but_no_pan_or_rat_bonus(self):
        banana = Banana(item_key="banana", player_id=0)
        garlic = Garlic(item_key="garlic", player_id=0)
        pan = Pan(item_key="pan", player_id=0)
        rat = Rat(item_key="rat", player_id=0)
        banana.add_marker_item("star", garlic.item_key)
        pan.add_marker_item("star", banana.item_key)
        rat.add_marker_item("star", banana.item_key)
        battle = self.battle(banana, garlic, pan, rat)
        battle.prepareItems()
        observations = []
        emit = battle.emit_signal
        def observe(emitter, name, event_context=None):
            if name == "combat_start":
                observations.append((banana.triggers[0].speed_modifiers,
                                     pan.effects[1].damage_modifier,
                                     rat.triggers[0].speed_modifiers))
            emit(emitter, name, event_context)
        battle.emit_signal = observe
        battle.start_combat()
        battle.start_combat()
        self.assertEqual(observations, [(0.1, 0, 0.0)])
        self.assertEqual(pan.effects[1].damage_modifier, 1)
        self.assertAlmostEqual(rat.triggers[0].speed_modifiers, 0.15)

    def test_book_prepares_without_mana_and_does_not_rescan_on_first_success(self):
        book = MagicForDummies(item_key="book", player_id=0)
        spell = self.stub("spell", types=("Spell",), crafted=True)
        book.add_marker_item("star", spell.item_key)
        battle = self.battle(book, spell)
        battle.prepareItems()
        battle.start_combat()
        book._prepare_spell_weight = Mock(side_effect=AssertionError("runtime layout scan"))
        context = battle.build_context(book)
        book.run_effect([True], context)
        self.assertEqual(battle.players[0].max_health, 30)
        battle.players[0].buffs.Mana = 1
        book.run_effect([True], context)
        self.assertEqual((battle.players[0].health, battle.players[0].max_health), (24, 44))
        self.assertEqual(sum(row["data"]["action"] == "item_activation" for row in battle.log), 2)
        book._prepare_spell_weight.assert_not_called()

    def test_twine_uses_prepared_diamond_count_in_opening_activation(self):
        twine = Twine(item_key="twine", player_id=0)
        source = self.stub("source")
        neutral = self.stub("neutral")
        twine.add_marker_item("star", source.item_key)
        twine.add_marker_item("diamond", neutral.item_key)
        battle = self.battle(twine, source, neutral)
        battle.prepareItems()
        twine._prepare_neutral_item_count = Mock(side_effect=AssertionError("runtime layout scan"))
        twine.roll_chance = Mock(return_value=True)
        source.emit_activation(battle.build_context(source))
        twine.roll_chance.assert_called_once_with(0.4, battle.rng)
        twine._prepare_neutral_item_count.assert_not_called()
        self.assertEqual(battle.players[0].max_health, 32)

    def test_food_pre_initialization_and_updates_preserve_prepared_external_speed(self):
        for cls, other_cls in ((Banana, Garlic), (Garlic, Banana)):
            with self.subTest(item=cls.__name__):
                food = cls(item_key="food", player_id=0)
                other = other_cls(item_key="other", player_id=0)
                food.add_marker_item("star", other.item_key)
                food.triggers[0].stack_speed_modifier(0.2)
                battle = self.battle(food, other)
                battle.prepareItems()
                trigger = food.triggers[0]
                trigger.prepare_speed_modifiers = Mock(side_effect=AssertionError("repeated preparation"))
                battle.start_combat()
                battle.players[0].debuffs.Cold = 5
                battle.frame_delta = 1.0
                for _ in range(2):
                    trigger.update(battle.build_context(food))
                self.assertAlmostEqual(trigger.speed_modifiers, 0.3)
                self.assertAlmostEqual(trigger.cooldown_progress, 2.4)
                trigger.prepare_speed_modifiers.assert_not_called()

    def test_pan_prepares_without_stamina_and_stacks_whetstone_once_before_attacks(self):
        pan = Pan(item_key="pan", player_id=0)
        food = self.stub("food", types=("Food",))
        whetstone = Whetstone(item_key="whetstone", player_id=0)
        pan.add_marker_item("star", food.item_key)
        whetstone.add_marker_item("star", pan.item_key)
        battle = self.battle(pan, food, whetstone)
        battle.prepareItems()
        battle.start_combat()
        self.assertEqual(pan.effects[1].damage_modifier, 2)
        self.assertEqual(battle.players[0].stamina, 0)
        pan.effects[1].prepare_damage_modifier = Mock(side_effect=AssertionError("first-hit preparation"))
        battle.players[0].stamina = 10
        pan.effects[1].accuracy = 100
        battle.rng = Mock()
        battle.rng.randint.side_effect = lambda low, high: low
        for _ in range(2):
            pan.run_effect([True], battle.build_context(pan))
        self.assertEqual(pan.effects[1].damage_modifier, 2)
        self.assertEqual(battle.players[1].health, 86)
        pan.effects[1].prepare_damage_modifier.assert_not_called()

    def test_explicit_pan_pre_replay_reapplies_bonus_but_start_entry_is_once(self):
        pan = Pan(item_key="pan", player_id=0)
        food = self.stub("food", types=("Food",))
        pan.add_marker_item("star", food.item_key)
        battle = self.battle(pan, food)
        battle.prepareItems()
        battle.start_combat()
        battle.start_combat()
        self.assertEqual(pan.effects[1].damage_modifier, 1)
        pan.onPreCombatStart(battle.build_context(pan))
        self.assertEqual(pan.effects[1].damage_modifier, 2)

    def test_prepared_caches_are_independent_between_instances(self):
        first = MagicForDummies(item_key="first", player_id=0)
        second = MagicForDummies(item_key="second", player_id=0)
        spell = self.stub("spell", types=("Spell",))
        first.add_marker_item("star", spell.item_key)
        battle = self.battle(first, second, spell)
        battle.prepareItems()
        self.assertEqual((first.spell_weight, second.spell_weight), (1, 0))
        self.assertEqual((first.effects[1].amount, second.effects[1].amount), (11, 8))


if __name__ == "__main__":
    unittest.main()
