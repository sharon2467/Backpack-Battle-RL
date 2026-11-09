import random
import unittest
from unittest.mock import patch

from battle_module_v1 import (
    BattleState, ItemActivationContext, PlayerState, make_attack_event,
    validate_gem_sockets,
)
from item_effects_v1 import GainBuffEffect
from item_factory_registry_v1 import BattleItem
from item_triggers_v1 import ActivationTrigger, CooldownTrigger


class SocketItem(BattleItem):
    def __init__(self, events, *, sockets=0, priority=0, broadcast=False,
                 kill_phase=None, **kwargs):
        self.socket_count = sockets
        super().__init__(effects=[GainBuffEffect("Heat", 1)], **kwargs)
        self.events = events
        self.contexts = []
        self.priority = priority
        self.broadcast = broadcast
        self.kill_phase = kill_phase

    def getTriggerPriority(self):
        return self.priority

    def record(self, phase, context):
        self.events.append((phase, self.player_id, self.item_key))
        self.contexts.append(context)
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
        if self.broadcast:
            self.emit_activation(context)

    def onPostCombatStart(self, context):
        self.record("post", context)

    def run_effect(self, results, context):
        if any(results):
            self.record("effect", context)
            self.effects[0].apply(context)
            self.emit_activation(context)


class GemSocketLifecycleTest(unittest.TestCase):
    def item(self, key, side=0, **kwargs):
        return SocketItem(self.events, item_key=key, player_id=side, **kwargs)

    def gem(self, key, side=0, **kwargs):
        return self.item(key, side, item_types=("Gem",), **kwargs)

    def battle(self, *items):
        return BattleState(
            players=[PlayerState(
                player_id=side, health=20, max_health=30,
                stamina=1.0, max_stamina=5.0,
                items={item.item_key: item for item in items if item.player_id == side},
            ) for side in (0, 1)],
            active_items=[item for item in items if item.is_active_item],
            rng=random.Random(17),
        )

    def setUp(self):
        self.events = []

    def test_socket_fields_default_and_slots_fill_in_order(self):
        host = self.item("host", sockets=2, item_types=("Weapon", "Magic"))
        first, second = self.gem("first"), self.gem("second")
        self.assertEqual((first.belongs_to, first.gem_type, first.gemsocket), (None, (), []))
        self.assertEqual(host.gemsocket, [None, None])
        host.add_gems(first)
        host.add_gems(second)
        self.assertEqual(host.gemsocket, ["first", "second"])
        for gem in (first, second):
            self.assertEqual((gem.belongs_to, gem.gem_type), ("host", ("Weapon", "Magic")))
        battle = self.battle(host, first, second)
        self.assertEqual(host.get_gems(battle.build_context(host)), [first, second])

    def test_socket_rejection_does_not_change_either_item(self):
        cases = ("full", "no_sockets", "cross_player", "not_gem", "gem_host",
                 "self", "missing_host_key", "missing_gem_key", "same_key",
                 "bound", "gem_has_sockets", "host_prepared", "gem_prepared")
        for case in cases:
            with self.subTest(case=case):
                host, gem = self.item("host", sockets=1), self.gem("gem")
                if case == "full":
                    host.add_gems(self.gem("existing"))
                elif case == "no_sockets":
                    host = self.item("host")
                elif case == "cross_player":
                    gem.player_id = 1
                elif case == "not_gem":
                    gem.item_types = ()
                elif case == "gem_host":
                    host.item_types = ("Gem",)
                elif case == "self":
                    gem = host
                elif case == "missing_host_key":
                    host.item_key = None
                elif case == "missing_gem_key":
                    gem.item_key = None
                elif case == "same_key":
                    gem.item_key = host.item_key
                elif case == "bound":
                    self.item("other", sockets=1).add_gems(gem)
                elif case == "gem_has_sockets":
                    gem.socket_count, gem.gemsocket = 1, [None]
                elif case == "host_prepared":
                    host.has_prepared = True
                elif case == "gem_prepared":
                    gem.has_prepared = True
                before = (host.gemsocket[:], gem.belongs_to, gem.gem_type)
                with self.assertRaises(ValueError):
                    host.add_gems(gem)
                self.assertEqual((host.gemsocket, gem.belongs_to, gem.gem_type), before)

    def test_validation_is_read_only_for_valid_and_invalid_relationships(self):
        cases = ("valid", "missing", "back_reference", "type_snapshot", "duplicate_slot",
                 "duplicate_host", "orphan", "not_gem", "bound_non_gem", "wrong_key",
                 "wrong_player", "alias", "slot_count", "gem_has_sockets", "nested")
        for case in cases:
            with self.subTest(case=case):
                host = self.item("host", sockets=2, item_types=("Weapon",))
                gem = self.gem("gem")
                host.add_gems(gem)
                battle = self.battle(host, gem)
                items = battle.players[0].items
                if case == "missing":
                    del items["gem"]
                elif case == "back_reference":
                    gem.belongs_to = "other"
                elif case == "type_snapshot":
                    gem.gem_type = ()
                elif case == "duplicate_slot":
                    host.gemsocket[1] = "gem"
                elif case == "duplicate_host":
                    other = self.item("other", sockets=1)
                    other.gemsocket[0] = "gem"
                    items["other"] = other
                elif case == "orphan":
                    host.gemsocket[0] = None
                elif case == "not_gem":
                    gem.item_types = ()
                elif case == "bound_non_gem":
                    other = self.item("other")
                    other.belongs_to = "host"
                    items["other"] = other
                elif case == "wrong_key":
                    gem.item_key = "wrong"
                elif case == "wrong_player":
                    gem.player_id = 1
                elif case == "alias":
                    items["alias"] = gem
                elif case == "slot_count":
                    host.gemsocket.append(None)
                elif case == "gem_has_sockets":
                    gem.socket_count, gem.gemsocket = 1, [None]
                elif case == "nested":
                    host.item_types = ("Gem",)
                snapshots = [(item, item.gemsocket[:], item.belongs_to, item.gem_type,
                              item.has_prepared, vars(item.chance_rng).copy())
                             for item in (host, gem)]
                rng_state = battle.rng.getstate()
                if case == "valid":
                    self.assertIsNone(validate_gem_sockets(battle.players))
                else:
                    with self.assertRaises(ValueError):
                        validate_gem_sockets(battle.players)
                for item, slots, belongs_to, gem_type, prepared, chance_state in snapshots:
                    self.assertEqual((item.gemsocket, item.belongs_to, item.gem_type,
                                      item.has_prepared, vars(item.chance_rng)),
                                     (slots, belongs_to, gem_type, prepared, chance_state))
                self.assertEqual(battle.rng.getstate(), rng_state)
                self.assertEqual(battle._bus_cache, {})
                self.assertEqual(battle.battle_items, [])
                self.assertEqual(battle.log, [])
                self.assertFalse(battle.has_prepared)
                self.assertEqual(self.events, [])

    def test_prepare_does_not_call_validator(self):
        host, gem = self.item("host", sockets=1), self.gem("gem")
        host.add_gems(gem)
        battle = self.battle(host, gem)
        with patch("battle_module_v1.validate_gem_sockets", side_effect=AssertionError):
            battle.prepareItems()
        self.assertTrue(host.has_prepared and gem.has_prepared)

    def test_phases_are_global_with_gems_in_slot_order_and_correct_context(self):
        hosts, items = [], []
        for side in (0, 1):
            for number in range(2):
                host = self.item(f"host{number}", side, sockets=3, priority=number)
                first, second = self.gem(f"first{number}", side), self.gem(f"second{number}", side)
                host.add_gems(first)
                host.add_gems(second)
                # Preserve an empty slot between the two populated slots.
                host.gemsocket[1:] = [None, second.item_key]
                hosts.append(host)
                items.extend((first, host, second))
        battle = self.battle(*items)
        validate_gem_sockets(battle.players)
        battle.prepareItems()
        self.assertEqual(battle.battle_items, [hosts[1], hosts[0], hosts[3], hosts[2]])
        battle.start_combat()
        battle.start_combat()
        expected = [(phase, host.player_id, key)
                    for phase in ("prepare", "pre", "start", "post")
                    for host in battle.battle_items
                    for key in (*[key for key in host.gemsocket if key is not None], host.item_key)]
        self.assertEqual(self.events, expected)
        self.assertEqual((battle.frame, battle.time), (0, 0.0))
        for item in items:
            self.assertEqual(len(item.contexts), 4)
            for context in item.contexts:
                self.assertIs(context.item, item)
                self.assertIs(context.owner, battle.players[item.player_id])
                self.assertIs(context.opponent, battle.players[1 - item.player_id])

    def test_socketed_cooldown_is_not_initialized_or_polled_but_inventory_gem_runs(self):
        host = self.item("host", sockets=1)
        socketed = self.gem("socketed", is_active_item=True, triggers=[CooldownTrigger(1.0)])
        inventory = self.gem("inventory", is_active_item=True, triggers=[CooldownTrigger(1.0)])
        host.add_gems(socketed)
        battle = self.battle(host, socketed, inventory)
        battle.prepareItems()
        self.assertEqual(battle.active_items, [inventory])
        battle.run(1, frame_delta=1.0)
        self.assertFalse(socketed.triggers[0].speed_modifiers_prepared)
        self.assertEqual(socketed.triggers[0].cooldown_progress, 0.0)
        self.assertTrue(inventory.triggers[0].speed_modifiers_prepared)
        self.assertIn(("effect", 0, "inventory"), self.events)
        self.assertNotIn(("effect", 0, "socketed"), self.events)
        self.assertEqual(battle.players[0].buffs.Heat, 1)

    def test_socketed_gem_receives_host_activation_and_emits_as_itself_on_both_sides(self):
        items = []
        for side in (0, 1):
            host = self.item("host", side, sockets=1, broadcast=True)
            gem = self.gem("gem", side, triggers=[ActivationTrigger()])
            gem.add_marker_item("star", host.item_key)
            host.add_gems(gem)
            items.extend((host, gem))
        battle = self.battle(*items)
        battle.prepareItems()
        battle.start_combat()
        self.assertEqual([p.buffs.Heat for p in battle.players], [1, 1])
        for host, gem in ((items[0], items[1]), (items[2], items[3])):
            event_contexts = [ctx for ctx in gem.contexts if isinstance(ctx, ItemActivationContext)]
            self.assertEqual(len(event_contexts), 1)
            self.assertIs(event_contexts[0].source_item, host)
            self.assertIs(event_contexts[0].item, gem)
        sources = [(entry["source"]["player_id"], entry["source"]["item_key"])
                   for entry in battle.log if entry["data"]["action"] == "item_activation"]
        self.assertEqual(sources, [(0, "host"), (0, "gem"), (1, "host"), (1, "gem")])

    def test_gem_prepares_before_host_registers_its_own_listener(self):
        host = self.item("host", sockets=1, triggers=[ActivationTrigger()])
        gem = self.gem("gem", broadcast=True)
        host.add_marker_item("star", gem.item_key)
        host.add_gems(gem)
        battle = self.battle(host, gem)
        battle.prepareItems()
        battle.start_combat()
        self.assertIn(("effect", 0, "host"), self.events)
        self.assertEqual(battle.players[0].buffs.Heat, 1)

    def test_gem_death_stops_remaining_gems_host_and_later_phases(self):
        for phase in ("pre", "start", "post"):
            with self.subTest(phase=phase):
                self.events = []
                host = self.item("host", sockets=2, priority=10)
                killer, later = self.gem("killer", kill_phase=phase), self.gem("later")
                host.add_gems(killer)
                host.add_gems(later)
                other = self.item("other", 1)
                battle = self.battle(host, killer, later, other)
                battle.prepareItems()
                self.assertEqual(battle.step(), 0)
                self.assertEqual(self.events[-1], (phase, 0, "killer"))
                self.assertEqual((battle.frame, battle.time), (0, 0.0))
                self.assertEqual(battle.players[0].stamina, 1.0)

    def test_nonweapon_host_types_are_retained_for_armor_branch(self):
        host = self.item("host", sockets=1, item_types=("Accessory",))
        gem = self.gem("gem")
        host.add_gems(gem)
        self.assertEqual(gem.gem_type, ("Accessory",))
        self.assertNotIn("Weapon", gem.gem_type)
        self.assertIsNone(validate_gem_sockets(self.battle(host, gem).players))


if __name__ == "__main__":
    unittest.main()
