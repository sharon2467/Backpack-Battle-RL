import random
import unittest
from unittest.mock import Mock

from battle_module_v1 import BattleState, ItemActivationContext, PlayerState, make_attack_event
from item_effects_v1 import GainBuffEffect
from item_factory_registry_v1 import (
    Banana, BattleItem, Flame, Garlic, Goobling, HealingHerbs,
    PocketSand, Twine, WalrusTusk, Whetstone, WoodenSword,
)
from item_triggers_v1 import ActivationTrigger


class RecordingItem(BattleItem):
    def __init__(self, events, priority=0, kill_phase=None, **kwargs):
        super().__init__(effects=[GainBuffEffect("Heat", 1)], **kwargs)
        self.events = events
        self.priority = priority
        self.kill_phase = kill_phase

    def getTriggerPriority(self):
        return self.priority

    def record(self, phase, context):
        self.events.append((phase, self.player_id, self.item_key))
        if phase == self.kill_phase:
            context.battle_state.resolve_attack(make_attack_event(
                attacker=context.owner, defender=context.opponent,
                source_item=self, attack_types=("effect",),
                min_damage=100, max_damage=100,
            ))

    def onPrepare(self, context):
        self.record("prepare", context)

    def onPreCombatStart(self, context):
        self.record("pre", context)

    def onCombatStart(self, context):
        self.record("start", context)

    def onPostCombatStart(self, context):
        self.record("post", context)

    def run_effect(self, results, context):
        self.record("event", context)


class CombatStartLifecycleTest(unittest.TestCase):
    def battle(self, *items, active_items=None, seed=17):
        players = [
            PlayerState(player_id=side, health=20, max_health=30,
                        stamina=1.0, max_stamina=5.0,
                        items={item.item_key: item for item in items if item.player_id == side})
            for side in (0, 1)
        ]
        return BattleState(
            players=players, rng=random.Random(seed),
            active_items=([item for item in items if item.is_active_item]
                          if active_items is None else active_items),
        )

    def test_all_items_prepare_and_each_phase_finishes_before_next(self):
        events = []
        items = [RecordingItem(events, item_key=str(i), player_id=i % 2)
                 for i in range(6)]
        battle = self.battle(*items)
        battle.prepareItems()
        self.assertEqual([row[0] for row in events], ["prepare"] * 6)
        self.assertFalse(battle.combat_started)
        battle.start_combat()
        self.assertEqual([row[0] for row in events],
                         ["prepare"] * 6 + ["pre"] * 6 + ["start"] * 6 + ["post"] * 6)
        order = [(item.player_id, item.item_key) for item in battle.battle_items]
        for offset in (0, 6, 12, 18):
            self.assertEqual([row[1:] for row in events[offset:offset + 6]], order)

    def test_priority_is_descending_with_player_side_first(self):
        events = []
        low = RecordingItem(events, priority=-1, item_key="low", player_id=0)
        high = RecordingItem(events, priority=10, item_key="high", player_id=0)
        enemy = RecordingItem(events, priority=100, item_key="enemy", player_id=1)
        battle = self.battle(low, high, enemy)
        battle.prepareItems()
        self.assertEqual(battle.battle_items, [high, low, enemy])

    def test_tied_order_is_seeded_and_shuffled(self):
        def order(seed):
            items = [RecordingItem([], item_key=str(i), player_id=0) for i in range(10)]
            battle = self.battle(*items, seed=seed)
            battle.prepareItems()
            return [item.item_key for item in battle.battle_items]
        self.assertEqual(order(17), order(17))
        self.assertNotEqual(order(17), order(18))
        self.assertNotEqual(order(17), [str(i) for i in range(10)])

    def test_global_notification_precedes_pre_hooks(self):
        events = []
        listener = RecordingItem(events, triggers=[ActivationTrigger()],
                                 item_key="listener", player_id=0)
        battle = self.battle(listener)
        battle.prepareItems()
        battle.connect(None, "combat_start", (listener, 0))
        # ActivationTrigger requires a linked marker; this test isolates dispatch.
        listener.triggers[0].update = Mock(return_value=True)
        battle.start_combat()
        self.assertEqual([event[0] for event in events],
                         ["prepare", "event", "pre", "start", "post"])

    def test_nested_start_during_notification_does_not_restart_phases(self):
        events = []
        item = RecordingItem(events, triggers=[ActivationTrigger()],
                             item_key="listener", player_id=0)
        item.triggers[0].update = Mock(return_value=True)
        battle = self.battle(item)
        battle.prepareItems()
        battle.connect(None, "combat_start", (item, 0))
        item.run_effect = lambda results, context: battle.start_combat()
        battle.start_combat()
        self.assertEqual([event[0] for event in events], ["prepare", "pre", "start", "post"])

    def test_same_seed_reproduces_opening_logs(self):
        def logs():
            battle = self.battle(
                Flame(item_key="flame", player_id=0),
                HealingHerbs(item_key="herbs", player_id=0),
                PocketSand(item_key="sand", player_id=1),
            )
            battle.prepareItems()
            battle.start_combat()
            return battle.log
        self.assertEqual(logs(), logs())

    def test_start_does_not_advance_time_stamina_or_cooldown(self):
        banana = Banana(item_key="banana", player_id=0)
        garlic = Garlic(item_key="garlic", player_id=0)
        banana.add_linked_item(garlic.item_key)
        battle = self.battle(banana, garlic)
        battle.prepareItems()
        battle.start_combat()
        self.assertEqual((battle.frame, battle.time), (0, 0.0))
        self.assertEqual([player.stamina for player in battle.players], [1.0, 1.0])
        self.assertEqual(banana.triggers[0].cooldown_progress, 0.0)
        self.assertTrue(banana.triggers[0].speed_modifiers_prepared)
        self.assertAlmostEqual(banana.triggers[0].speed_modifiers, 0.1)

    def test_flame_heat_applies_before_first_cooldown_in_either_polling_order(self):
        for flame_first in (False, True):
            with self.subTest(flame_first=flame_first):
                banana = Banana(item_key="banana", player_id=0)
                flame = Flame(item_key="flame", player_id=0)
                items = [flame, banana] if flame_first else [banana, flame]
                battle = self.battle(*items, active_items=items)
                battle.prepareItems()
                battle.step()
                self.assertAlmostEqual(banana.triggers[0].cooldown_progress, 1.02 / 30)
                self.assertEqual(battle.players[0].buffs.Heat, 1)

    def test_step_run_and_explicit_start_share_one_opening(self):
        events = []
        item = RecordingItem(events, item_key="item", player_id=0)
        battle = self.battle(item)
        battle.prepareItems()
        battle.run(0)
        self.assertFalse(battle.combat_started)
        battle.start_combat()
        battle.start_combat()
        battle.step()
        battle.run(2)
        self.assertEqual([event[0] for event in events], ["prepare", "pre", "start", "post"])
        self.assertEqual(battle.frame, 3)

    def test_unprepared_entry_points_raise(self):
        for method, args in (("start_combat", ()), ("step", ()), ("run", (0,))):
            with self.subTest(method=method), self.assertRaises(ValueError):
                getattr(self.battle(), method)(*args)

    def test_preparation_is_once_and_instances_cannot_be_reused(self):
        item = Flame(item_key="flame", player_id=0)
        battle = self.battle(item)
        battle.prepareItems()
        with self.assertRaises(ValueError):
            battle.prepareItems()
        with self.assertRaises(ValueError):
            self.battle(item).prepareItems()

    def test_preparation_rejects_invalid_initial_state(self):
        for changes in ({"frame": 1}, {"time": 1.0}, {"winner": 0}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                battle = self.battle()
                for key, value in changes.items():
                    setattr(battle, key, value)
                battle.prepareItems()
        with self.assertRaises(ValueError):
            BattleState().prepareItems()

    def test_consumption_happens_after_effect_and_synchronous_activation(self):
        for cls, target, slot, name, value in (
            (PocketSand, 1, "debuffs", "Blind", 1),
            (HealingHerbs, 0, "buffs", "Regeneration", 2),
            (Flame, 0, "buffs", "Heat", 1),
            (WalrusTusk, 0, "buffs", "Spikes", 1),
        ):
            with self.subTest(item=cls.__name__):
                item = cls(item_key="source", player_id=0)
                battle = self.battle(item)
                observed = []
                original = battle.emit_signal
                def emit(emitter, name_, context=None):
                    if name_ == "item_activation":
                        observed.append((item.consumed,
                                         getattr(getattr(battle.players[target], slot), name)))
                    original(emitter, name_, context)
                battle.emit_signal = emit
                battle.prepareItems()
                battle.start_combat()
                self.assertEqual(observed, [(False, value)])
                self.assertTrue(item.consumed)
                self.assertFalse(item.is_active_item)
                self.assertEqual(item.triggers, [])
                battle.step()
                self.assertEqual(len(observed), 1)

    def test_normal_events_cannot_run_opening_at_frame_zero(self):
        sand = PocketSand(item_key="sand", player_id=0)
        banana = Banana(item_key="banana", player_id=0)
        battle = self.battle(sand, banana)
        context = ItemActivationContext(battle, sand, *battle.players, source_item=banana)
        sand.activate_item(context)
        self.assertEqual(battle.players[1].debuffs.Blind, 0)
        with self.assertRaises(ValueError):
            sand.activate_item(context, 0)

    def test_whetstone_modifies_weapon_and_activates_without_consumption(self):
        stone = Whetstone(item_key="stone", player_id=0)
        sword = WoodenSword(item_key="sword", player_id=0)
        stone.add_linked_item(sword.item_key)
        battle = self.battle(stone, sword)
        battle.prepareItems()
        battle.start_combat()
        self.assertEqual(sword.effects[1].damage_modifier, 1)
        self.assertFalse(stone.consumed)
        self.assertEqual([entry["data"]["action"] for entry in battle.log],
                         ["modify_linked_weapon_damage", "item_activation"])

    def test_opening_reaches_later_slime_and_twine_listeners(self):
        sources = [Flame(item_key=str(i), player_id=0) for i in range(3)]
        slime = Goobling(item_key="slime", player_id=0)
        twine = Twine(item_key="twine", player_id=0)
        twine.roll_chance = Mock(return_value=True)
        for source in sources:
            source.getTriggerPriority = lambda: 10
            slime.add_marker_item("star", source.item_key)
            twine.add_marker_item("star", source.item_key)
        battle = self.battle(*sources, slime, twine)
        battle.prepareItems()
        battle.start_combat()
        self.assertEqual(slime.triggers[0].activation_count, 0)
        self.assertEqual(battle.players[0].health, 30)  # three max-HP gains + slime heal
        self.assertEqual(battle.players[0].max_health, 36)
        self.assertEqual(twine.roll_chance.call_count, 3)
        self.assertTrue(all(entry["frame"] == 0 and entry["time"] == 0 for entry in battle.log))

    def test_same_keys_on_both_sides_and_consumption_are_independent(self):
        first = Flame(item_key="same", player_id=0)
        second = Flame(item_key="same", player_id=1)
        battle = self.battle(first, second)
        battle.prepareItems()
        battle.start_combat()
        self.assertEqual([p.buffs.Heat for p in battle.players], [1, 1])
        self.assertTrue(first.consumed and second.consumed)
        self.assertEqual((first.activations_this_frame, second.activations_this_frame), (1, 1))

    def test_activation_cycles_stop_at_three_per_item_and_reset_next_frame(self):
        events = []
        items = [RecordingItem(events, triggers=[ActivationTrigger()],
                               item_key=str(i), player_id=0) for i in range(2)]
        for item, other in ((items[0], items[1]), (items[1], items[0])):
            item.add_marker_item("star", other.item_key)
            item.run_effect = lambda results, context: context.item.emit_activation(context)
        battle = self.battle(*items)
        battle.prepareItems()
        items[0].emit_activation(battle.build_context(items[0]))
        self.assertEqual(len(battle.log), 6)
        self.assertEqual([entry["source"]["item_key"] for entry in battle.log], ["0", "1"] * 3)
        battle.frame = 1
        items[0].emit_activation(battle.build_context(items[0]))
        self.assertEqual(len(battle.log), 12)

    def test_opening_death_stops_later_hooks_and_frame_progression(self):
        for phase in ("pre", "start", "post"):
            with self.subTest(phase=phase):
                events = []
                killer = RecordingItem(events, priority=10, kill_phase=phase,
                                       item_key="killer", player_id=0)
                later = RecordingItem(events, item_key="later", player_id=0)
                battle = self.battle(killer, later)
                battle.prepareItems()
                self.assertEqual(battle.step(), 0)
                self.assertEqual(events[-1], (phase, 0, "killer"))
                self.assertEqual((battle.frame, battle.time), (0, 0.0))
                self.assertEqual(battle.players[0].stamina, 1.0)

    def test_socket_storage_and_gem_preparation_are_supported(self):
        sword = WoodenSword(item_key="sword", player_id=0)
        gem = RecordingItem([], item_key="gem", player_id=0, item_types=("Gem",))
        self.assertEqual(sword.gemsocket, [None])
        sword.add_gems(gem)
        self.assertEqual(sword.gemsocket, ["gem"])
        with self.assertRaises(ValueError):
            sword.add_gems(gem)
        battle = self.battle(sword, gem)
        battle.prepareItems()
        self.assertTrue(sword.has_prepared and gem.has_prepared)
        self.assertEqual(battle.battle_items, [sword])


if __name__ == "__main__":
    unittest.main()
