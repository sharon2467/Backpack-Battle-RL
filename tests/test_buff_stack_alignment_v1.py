"""Permanent stack rules from Buff.gd and the retained native 1.1.8 traces.

The scripted draws check mechanism draw order, not native cosmetic RNG/seed parity.
Native edge fixtures: data/buff_engine_edge/native_negative_left_20261109_07
and native_full_cap_20261109_08 (see the matching report in docs).
"""
import unittest

from battle_module_v1 import (
    BattleContext, BattleState, BuffSlot, DebuffSlot, PlayerState,
    StackChangeContext, StackState,
)
from item_effects_v1 import (
    BuffRemovalEffect, CleanseDebuffEffect, GainBuffEffect,
    InflictDebuffEffect, UseBuffEffect,
)
from item_factory_registry_v1 import BattleItem, MagicForDummies, WandOfEquilibrium


class Draws:
    def __init__(self, *values):
        self.values = list(values)
        self.seen = []

    def random(self):
        if not self.values:
            raise AssertionError("unexpected mechanism random() draw")
        value = self.values.pop(0)
        self.seen.append(value)
        return value

    def choice(self, candidates):
        return candidates[0]


class StackObserver(BattleItem):
    def __init__(self, key, side, callback=None):
        super().__init__(item_key=key, player_id=side, effects=[GainBuffEffect("Mana", 0)])
        self.contexts = []
        self.callback = callback

    def activate_item(self, context, listener_idx=None):
        self.contexts.append(context)
        if self.callback is not None:
            self.callback(context)


class BuffStackAlignmentTest(unittest.TestCase):
    def setUp(self):
        self.source = BattleItem(item_id="direct", item_key="source", player_id=0,
                                 effects=[GainBuffEffect("Mana", 0)])
        self.owner = PlayerState(player_id=0, health=20, max_health=20,
                                 items={"source": self.source})
        self.enemy = PlayerState(player_id=1, health=20, max_health=20)
        self.rng = Draws()
        self.battle = BattleState(players=[self.owner, self.enemy], rng=self.rng)
        self.context = self.battle.build_context(self.source)

    def records(self, action):
        return [row for row in self.battle.log if row["data"]["action"] == action]

    def observe(self, target, name, *, side=0, callback=None):
        observer = StackObserver("observer" + str(side), side, callback)
        self.battle.players[side].items[observer.item_key] = observer
        self.battle.connect(target, "character_" + name + "_changed", (observer, 0))
        return observer

    def test_metadata_instances_do_not_share_state_or_replace_integer_slots(self):
        other = BattleItem(item_key="other", player_id=1, effects=[GainBuffEffect("Mana", 0)])
        self.source.stack_powers["Mana"] = 2
        self.source.stack_amplification_chances["Blind"] = 30
        state = self.battle._stack_state(self.owner, "Mana")
        state.resist_stacks = 3
        self.assertIs(state, self.battle._stack_state(self.owner, "Mana"))
        self.assertEqual(self.battle._stack_state(self.enemy, "Mana"), StackState())
        self.assertEqual((other.stack_powers, other.stack_amplification_chances), ({}, {}))
        self.assertEqual(self.owner.buffs.Mana, 0)
        self.assertEqual(len(BuffSlot.__annotations__) + len(DebuffSlot.__annotations__), 10)

    def test_all_ten_types_gain_and_lose_permanent_integer_stacks(self):
        self.rng.values = [0.9] * 6
        for slot in (self.owner.buffs, self.owner.debuffs):
            for name in slot.__annotations__:
                with self.subTest(name=name):
                    gain = self.battle.gain_stacks(self.owner, name, 2,
                                                  source_item=self.source)
                    loss = self.battle.lose_stacks(self.owner, name, 1,
                                                  source_item=self.source)
                    self.assertEqual((gain.delta, loss.delta, getattr(slot, name)), (2, -1, 1))
        # Three debuffs each roll once per incoming stack, even at 0% reflection.
        self.assertEqual(len(self.rng.seen), 6)

    def test_public_operations_validate_before_zero_shortcut(self):
        foreign = PlayerState(player_id=0)
        for operation in (self.battle.gain_stacks, self.battle.lose_stacks,
                          self.battle.try_use_stacks):
            for target, name, amount in ((foreign, "Mana", 0), (self.owner, "Block", 0),
                                         (self.owner, "mana", 0), (self.owner, True, 0),
                                         (self.owner, "Mana", -1), (self.owner, "Mana", True),
                                         (self.owner, "Mana", 1.0)):
                with self.subTest(operation=operation.__name__, name=name, amount=amount):
                    with self.assertRaises(ValueError):
                        operation(target, name, amount)
            result = operation(self.owner, "Mana", 0, source_item=self.source)
            self.assertEqual((result.delta, result.event), (0, None))
        self.assertEqual((self.battle.log, self.owner.stack_states, self.rng.seen), ([], {}, []))

    def test_gain_caps_actual_delta_and_emits_nothing_at_full_cap(self):
        self.owner.buffs.Mana = 9998
        observer = self.observe(self.owner, "mana")
        first = self.battle.gain_stacks(self.owner, "Mana", 7, source_item=self.source)
        second = self.battle.gain_stacks(self.owner, "Mana", 1, source_item=self.source)
        self.assertEqual((first.delta, first.event.amount, self.owner.buffs.Mana), (2, 2, 10000))
        self.assertEqual((second.delta, second.event), (0, None))
        self.assertEqual(len(observer.contexts), 1)

    def test_raw_use_is_partial_but_try_use_is_atomic_and_both_skip_protection(self):
        self.owner.buffs.Mana = 2
        state = StackState(cleanse_protection_chance_percent=100, resist_stacks=4)
        self.owner.stack_states["Mana"] = state
        self.owner.buff_protect_stacks = 5
        failed = self.battle.try_use_stacks(self.owner, "Mana", 3, source_item=self.source)
        self.assertEqual((failed.delta, self.owner.buffs.Mana), (0, 2))
        used = self.battle.lose_stacks(self.owner, "Mana", 3,
                                       source_item=self.source, used=True)
        self.assertEqual((used.delta, used.event.used, self.owner.buffs.Mana), (-2, True, 0))
        self.assertEqual((state.resist_stacks, self.owner.buff_protect_stacks), (4, 5))
        self.assertEqual(self.rng.seen, [])
        self.assertEqual(self.records("stack_protected"), [])

    def test_remove_rolls_per_capped_layer_then_type_and_global_protection(self):
        self.owner.buffs.Mana = 10
        state = StackState(cleanse_protection_chance_percent=50, resist_stacks=1)
        self.owner.stack_states["Mana"] = state
        self.owner.buff_protect_stacks = 1
        self.rng.values = [0.1, 0.9, 0.2, 0.8, 0.7]
        result = self.battle.lose_stacks(self.owner, "Mana", 5, source_item=self.source)
        self.assertEqual((result.delta, self.owner.buffs.Mana), (-1, 9))
        self.assertEqual((state.resist_stacks, self.owner.buff_protect_stacks), (0, 0))
        self.assertEqual([r["data"]["action"] for r in self.battle.log],
                         ["stack_protected", "stack_change"])
        self.assertEqual(self.battle.log[0]["data"]["amount"], 4)
        self.assertEqual(self.rng.values, [])

    def test_negative_protection_expands_removal_but_never_above_current(self):
        self.owner.buffs.Mana = 3
        self.owner.stack_states["Mana"] = StackState(cleanse_protection_chance_percent=-100)
        self.rng.values = [0.5, 0.5]
        result = self.battle.lose_stacks(self.owner, "Mana", 2, source_item=self.source)
        self.assertEqual((result.delta, self.owner.buffs.Mana), (-3, 0))
        self.assertEqual(self.records("stack_protected"), [])
        self.assertEqual(len(self.rng.seen), 2)

    def test_debuff_type_protection_does_not_consume_global_buff_protection(self):
        self.owner.debuffs.Cold = 5
        state = StackState(resist_stacks=2)
        self.owner.stack_states["Cold"] = state
        self.owner.buff_protect_stacks = 20
        result = self.battle.lose_stacks(self.owner, "Cold", 3, source_item=self.source)
        self.assertEqual((result.delta, state.resist_stacks, self.owner.buff_protect_stacks), (-1, 0, 20))

    def test_negative_protection_cancellation_only_logs_positive_protected_amount(self):
        self.owner.buffs.Mana = 5
        self.owner.stack_states["Mana"] = StackState(
            cleanse_protection_chance_percent=-100, resist_stacks=1)
        self.rng.values = [0.5]
        result = self.battle.lose_stacks(self.owner, "Mana", 1, source_item=self.source)
        self.assertEqual(result.delta, -1)
        self.assertEqual(self.records("stack_protected"), [])

    def test_resist_then_reflect_draws_original_amount_before_dedicated_resist(self):
        self.enemy.stack_states["Blind"] = StackState(
            resist_chance_percent=50, reflect_chance_percent=33, resist_stacks=2)
        self.enemy.debuff_reflect_stacks = 1
        self.owner.stack_states["Blind"] = StackState(resist_chance_percent=50)
        # R=1 from three draws; F=1 from all three (not the two left).
        # The global reflector takes the last free layer before type resistance.
        self.rng.values = [0.1, 0.9, 0.7, 0.8, 0.2, 0.7, 0.2, 0.8]
        result = self.battle.gain_stacks(self.enemy, "Blind", 3, source_item=self.source)
        self.assertEqual(result.delta, 0)
        self.assertEqual((self.enemy.debuffs.Blind, self.owner.debuffs.Blind), (0, 1))
        self.assertEqual((self.enemy.debuff_reflect_stacks,
                          self.enemy.stack_states["Blind"].resist_stacks), (0, 2))
        self.assertEqual([r["data"]["amount"] for r in self.records("stack_resisted")], [1, 1])
        self.assertEqual(len(self.rng.seen), 8)
        self.assertEqual(self.rng.values, [])

    def test_amplification_rolls_original_request_then_reflection_rolls_expanded_amount(self):
        self.enemy.stack_states["Blind"] = StackState(resist_chance_percent=25)
        self.source.stack_amplification_chances["Blind"] = 75
        self.source.stack_powers["Blind"] = 100  # The core receives already-scaled units.
        self.rng.values = [0.2, 0.9, 0.7, 0.8, 0.9]
        result = self.battle.gain_stacks(self.enemy, "Blind", 2, source_item=self.source)
        self.assertEqual((result.delta, self.enemy.debuffs.Blind), (3, 3))
        self.assertEqual(len(self.rng.seen), 5)

    def test_dedicated_resist_precedes_global_resist_and_only_spends_what_is_needed(self):
        state = StackState(resist_stacks=2)
        self.enemy.stack_states["Blind"] = state
        self.enemy.debuff_resist_stacks = 3
        self.rng.values = [0.8] * 4
        first = self.battle.gain_stacks(self.enemy, "Blind", 1, source_item=self.source)
        self.assertEqual((first.delta, state.resist_stacks, self.enemy.debuff_resist_stacks),
                         (0, 1, 3))
        second = self.battle.gain_stacks(self.enemy, "Blind", 3, source_item=self.source)
        self.assertEqual((second.delta, state.resist_stacks, self.enemy.debuff_resist_stacks),
                         (0, 0, 1))
        self.assertEqual([row["data"]["amount"] for row in self.records("stack_resisted")], [1, 3])

    def test_zero_total_resistance_skips_resist_draws_but_zero_reflect_still_draws(self):
        self.enemy.stack_states["Blind"] = StackState(resist_chance_percent=25)
        self.source.stack_amplification_chances["Blind"] = 25
        self.rng.values = [0.8]
        result = self.battle.gain_stacks(self.enemy, "Blind", 1, source_item=self.source)
        self.assertEqual(result.delta, 1)
        self.assertEqual(self.rng.seen, [0.8])

    def test_zero_percent_reflection_can_match_exact_zero(self):
        self.rng.values = [0.0]
        result = self.battle.gain_stacks(self.enemy, "Blind", 1, source_item=self.source)
        self.assertEqual((result.delta, result.event), (0, None))
        self.assertEqual((self.enemy.debuffs.Blind, self.owner.debuffs.Blind), (0, 1))
        event = self.records("stack_change")[0]["data"]
        self.assertEqual((event["target_player_id"], event["reflected"], event["amount"]), (0, True, 1))
        self.assertEqual(self.rng.seen, [0.0])

    def test_native_verified_negative_left_and_two_controls(self):
        # Native R120/F104 overlap and the no-mirror/no-rune controls.
        for resist, reflect, draws, expected_reserve, reflected_amount in (
            (120, 104, [0.5, 0.5], 1, 1),
            (120, 0, [0.5, 0.5], 0, 0),
            (0, 104, [0.5], 0, 1),
        ):
            with self.subTest(resist=resist, reflect=reflect):
                self.setUp()
                state = StackState(resist_chance_percent=resist, reflect_chance_percent=reflect)
                self.enemy.stack_states["Blind"] = state
                self.rng.values = draws
                result = self.battle.gain_stacks(self.enemy, "Blind", 1, source_item=self.source)
                self.assertEqual(result.delta, 0)
                self.assertEqual(state.resist_stacks, expected_reserve)
                self.assertEqual((self.enemy.debuffs.Blind, self.owner.debuffs.Blind), (0, reflected_amount))
                changes = self.records("stack_change")
                self.assertEqual(len(changes), reflected_amount)
                if changes:
                    self.assertTrue(changes[0]["data"]["reflected"])
                self.assertEqual(len(self.records("stack_resisted")), int(resist > 0 and reflect == 0))

    def test_native_verified_cap_partial_suppression_and_full_reflection_exception(self):
        for current, request, draws, expected_delta, expected_reflected in (
            (9997, 3, [0.1, 0.9, 0.9], 2, 1),
            (10000, 3, [0.1, 0.9, 0.9], 0, 0),
            (10000, 3, [0.1, 0.1, 0.9], 0, 0),
            (10000, 1, [0.1], 0, 1),
        ):
            with self.subTest(current=current, request=request, draws=draws):
                self.setUp()
                self.enemy.debuffs.Blind = current
                self.enemy.stack_states["Blind"] = StackState(reflect_chance_percent=20)
                self.rng.values = draws
                result = self.battle.gain_stacks(self.enemy, "Blind", request, source_item=self.source)
                self.assertEqual(result.delta, expected_delta)
                self.assertEqual(self.enemy.debuffs.Blind, current + expected_delta)
                self.assertEqual(self.owner.debuffs.Blind, expected_reflected)
                reflected_events = [r for r in self.records("stack_change") if r["data"]["reflected"]]
                self.assertEqual(sum(r["data"]["amount"] for r in reflected_events), expected_reflected)
                self.assertEqual(self.rng.values, [])

    def test_reflection_keeps_source_parent_and_skips_power_amplification_and_rebounce(self):
        self.source.stack_powers["Blind"] = 1.5
        self.source.stack_amplification_chances["Blind"] = 100
        self.enemy.stack_states["Blind"] = StackState(
            resist_chance_percent=100, reflect_chance_percent=100)
        self.owner.stack_states["Blind"] = StackState(
            resist_chance_percent=100, reflect_chance_percent=100)
        self.rng.values = [0.5] * 6
        parent = self.battle.record_log("Root", {"action": "parent"})
        result = self.battle.gain_stacks(self.enemy, "Blind", 3,
                                          source_item=self.source, trigger_log_handle=parent)
        self.assertEqual((result.delta, self.owner.debuffs.Blind), (0, 0))
        resisted = self.records("stack_resisted")[0]
        self.assertEqual((resisted["source"]["item_key"], resisted["data"]["amount"],
                          resisted["data"]["reflected"], resisted["data"]["trigger_log_sequence"]),
                         ("source", 3, True, parent.sequence))
        self.assertEqual(len(self.rng.seen), 6)

    def test_source_none_mutates_without_success_event_or_signal(self):
        observer = self.observe(self.owner, "mana")
        gained = self.battle.gain_stacks(self.owner, "Mana", 3)
        lost = self.battle.lose_stacks(self.owner, "Mana", 1)
        self.assertEqual((gained.delta, lost.delta, self.owner.buffs.Mana), (3, -1, 2))
        self.assertEqual((gained.event, lost.event, observer.contexts, self.battle.log), (None, None, [], []))

    def test_event_target_source_parent_and_lucky_signal_survive_listener_perspectives(self):
        observed_log_lengths = []
        first = self.observe(self.enemy, "lucky", side=0,
                             callback=lambda ctx: observed_log_lengths.append(len(self.battle.log)))
        second = self.observe(self.enemy, "lucky", side=1)
        wrong_name = self.observe(self.enemy, "luck")
        parent = self.battle.record_log("RootAttack", {"action": "parent"})
        result = self.battle.gain_stacks(self.enemy, "Luck", 2,
                                          source_item=self.source, trigger_log_handle=parent)
        self.assertIsInstance(result.event, StackChangeContext)
        self.assertEqual(observed_log_lengths, [2])
        self.assertEqual(wrong_name.contexts, [])
        for watcher in (first, second):
            event = watcher.contexts[0]
            self.assertIs(event.target, self.enemy)
            self.assertIs(event.source_item, self.source)
            self.assertIs(event.item, watcher)
            self.assertIs(event.owner, self.battle.players[watcher.player_id])
            self.assertIs(event.trigger_log_handle, parent)
            self.assertIs(event.log_handle, result.event.log_handle)
            self.assertEqual((event.stack_name, event.amount, event.used, event.reflected, event.timeout),
                             ("Luck", 2, False, False, False))
        self.assertEqual(self.battle.log[1]["data"]["trigger_log_sequence"], parent.sequence)
        self.assertEqual(self.battle.log[1]["source"]["item_key"], "source")

    def test_source_none_still_records_resist_and_protect_without_success_signal(self):
        blind = self.observe(self.owner, "blind")
        mana = self.observe(self.owner, "mana")
        self.owner.stack_states["Blind"] = StackState(resist_chance_percent=50)
        self.owner.stack_states["Mana"] = StackState(cleanse_protection_chance_percent=50)
        self.owner.buffs.Mana = 2
        self.rng.values = [0.1, 0.9, 0.8, 0.8, 0.1, 0.9]
        gained = self.battle.gain_stacks(self.owner, "Blind", 2)
        lost = self.battle.lose_stacks(self.owner, "Mana", 2)
        self.assertEqual((gained.delta, lost.delta), (1, -1))
        self.assertEqual((self.owner.debuffs.Blind, self.owner.buffs.Mana), (1, 1))
        self.assertEqual((gained.event, lost.event, blind.contexts, mana.contexts), (None, None, [], []))
        self.assertEqual([row["data"]["action"] for row in self.battle.log],
                         ["stack_resisted", "stack_protected"])
        self.assertEqual([row["data"]["amount"] for row in self.battle.log], [1, 1])

    def test_reentrant_removal_does_not_change_outer_delta_or_effect_success(self):
        def consume(event):
            if event.amount > 0:
                self.battle.lose_stacks(event.target, "Mana", event.amount,
                                         source_item=event.item, used=True)
        observer = self.observe(self.owner, "mana", callback=consume)
        result = self.battle.gain_stacks(self.owner, "Mana", 3, source_item=self.source)
        self.assertEqual((result.delta, result.event.amount, self.owner.buffs.Mana), (3, 3, 0))
        self.assertEqual([event.amount for event in observer.contexts], [3, -3])
        self.assertIs(GainBuffEffect("Mana", 3).apply(self.context), True)
        self.assertEqual(self.owner.buffs.Mana, 0)
        attempt = self.battle.log[-1]["data"]
        self.assertEqual((attempt["final_stack_gained"], attempt["success"]), (3, True))

    def test_reflection_occurs_after_original_target_callback(self):
        self.enemy.stack_states["Blind"] = StackState(reflect_chance_percent=50)
        self.rng.values = [0.1, 0.9]
        def reserve_resistance(event):
            self.assertEqual(self.owner.debuffs.Blind, 0)
            self.owner.stack_states["Blind"] = StackState(resist_stacks=1)
        self.observe(self.enemy, "blind", callback=reserve_resistance)
        result = self.battle.gain_stacks(self.enemy, "Blind", 2, source_item=self.source)
        self.assertEqual((result.delta, self.enemy.debuffs.Blind, self.owner.debuffs.Blind), (1, 1, 0))
        self.assertEqual([r["data"]["action"] for r in self.battle.log],
                         ["stack_change", "stack_resisted"])
        self.assertTrue(self.battle.log[-1]["data"]["reflected"])

    def test_effect_attempt_is_diagnostic_and_core_records_each_actual_change_once(self):
        self.enemy.stack_states["Blind"] = StackState(resist_chance_percent=50)
        self.rng.values = [0.1, 0.9, 0.8, 0.8]
        self.assertIs(InflictDebuffEffect("Blind", 2).apply(self.context), True)
        self.assertEqual([r["data"]["action"] for r in self.battle.log],
                         ["stack_resisted", "stack_change", "inflict_debuff"])
        self.assertEqual(len(self.records("stack_change")), 1)
        self.assertEqual(self.records("stack_change")[0]["data"]["actual"], 1)
        attempt = self.battle.log[-1]["data"]
        self.assertEqual((attempt["event_kind"], attempt["contributes_to_stack_totals"],
                          attempt["stack_gained"], attempt["final_stack_gained"]),
                         ("effect_attempt", False, 2, 1))

    def test_five_effect_zero_and_none_source_boolean_contracts(self):
        context = BattleContext(self.battle, None, self.owner, self.enemy)
        for effect, expected in ((GainBuffEffect("Mana", 0), False),
                                 (UseBuffEffect("Mana", 0), True),
                                 (BuffRemovalEffect("Mana", 0), False),
                                 (InflictDebuffEffect("Blind", 0), False),
                                 (CleanseDebuffEffect("Blind", 0), False)):
            self.assertIs(effect.apply(context), expected)
        self.assertEqual(len(self.battle.log), 5)
        self.assertTrue(all(r["data"]["event_kind"] == "effect_attempt" for r in self.battle.log))
        self.assertIs(GainBuffEffect("Mana", 2).apply(context), True)
        self.assertIs(UseBuffEffect("Mana", 1).apply(context), True)
        self.enemy.buffs.Mana = 1
        self.assertIs(BuffRemovalEffect("Mana", 1).apply(context), True)
        self.rng.values = [0.8]
        self.assertIs(InflictDebuffEffect("Blind", 1).apply(context), True)
        self.owner.debuffs.Blind = 1
        self.assertIs(CleanseDebuffEffect("Blind", 1).apply(context), True)
        self.assertEqual(self.records("stack_change"), [])

    def test_power_rounding_is_once_for_gains_and_absent_for_removals(self):
        self.source.stack_powers.update(Mana=1.5, Blind=0.25)
        self.assertIs(GainBuffEffect("Mana", 1).apply(self.context), True)
        self.assertEqual(self.owner.buffs.Mana, 2)
        self.rng.values = [0.8]
        self.assertIs(InflictDebuffEffect("Blind", 2).apply(self.context), True)
        self.assertEqual(self.enemy.debuffs.Blind, 1)
        self.source.stack_powers.update(Mana=0, Blind=0)
        self.assertIs(UseBuffEffect("Mana", 1).apply(self.context), True)
        self.enemy.buffs.Mana = 2
        self.assertIs(BuffRemovalEffect("Mana", 1).apply(self.context), True)
        self.owner.debuffs.Blind = 2
        self.assertIs(CleanseDebuffEffect("Blind", 1).apply(self.context), True)
        self.assertEqual((self.owner.buffs.Mana, self.enemy.buffs.Mana, self.owner.debuffs.Blind), (1, 1, 1))
        self.assertIs(GainBuffEffect("Mana", 2).apply(self.context), False)
        self.assertIs(InflictDebuffEffect("Blind", 2).apply(self.context), False)
        self.assertEqual(self.rng.values, [])

    def test_cleanse_bool_reports_actual_removal_not_native_precap_request(self):
        self.owner.debuffs.Blind = 2
        self.owner.stack_states["Blind"] = StackState(cleanse_protection_chance_percent=100)
        self.rng.values = [0.5, 0.5]
        self.assertIs(CleanseDebuffEffect("Blind", 5).apply(self.context), False)
        self.assertEqual(self.owner.debuffs.Blind, 2)
        self.assertEqual(self.records("stack_protected")[0]["data"]["amount"], 2)
        self.assertEqual(self.records("stack_change"), [])

    def test_wand_rechecks_threshold_after_immediate_gain_and_uses_through_protection(self):
        wand = WandOfEquilibrium(item_key="wand", player_id=0)
        self.owner.items["wand"] = wand
        self.owner.buffs = BuffSlot(Mana=9, Luck=10, Regeneration=10)
        self.owner.stack_states["Mana"] = StackState(cleanse_protection_chance_percent=100, resist_stacks=5)
        self.owner.buff_protect_stacks = 5
        wand.run_effect([True], self.battle.build_context(wand))
        self.assertEqual((self.owner.buffs.Mana, self.owner.buffs.Empower), (9, 1))
        self.assertEqual([r["data"]["amount"] for r in self.records("stack_change")], [1, -1, 1])
        self.assertEqual((self.owner.stack_states["Mana"].resist_stacks, self.owner.buff_protect_stacks), (5, 5))
        self.assertEqual(self.rng.seen, [])

    def test_magic_book_retains_empty_activation_and_successful_try_use_path(self):
        book = MagicForDummies(item_key="book", player_id=0)
        self.owner.items["book"] = book
        context = self.battle.build_context(book)
        book.prepare(context)
        book.run_effect([True], context)
        self.assertEqual((self.owner.max_health, self.owner.buffs.Mana), (20, 0))
        self.assertEqual(len(self.records("item_activation")), 1)
        self.owner.buffs.Mana = 1
        self.owner.stack_states["Mana"] = StackState(cleanse_protection_chance_percent=100)
        book.run_effect([True], context)
        self.assertEqual((self.owner.health, self.owner.max_health, self.owner.buffs.Mana), (28, 28, 0))
        self.assertEqual(len(self.records("item_activation")), 2)
        self.assertTrue(self.records("stack_change")[0]["data"]["used"])


if __name__ == "__main__":
    unittest.main()
