"""Effect result/parent contracts; core Timer and exceptional expiry tests live separately."""
import random
import unittest
from unittest.mock import Mock

from battle_module_v1 import (
    ATTACK_PHASE_CHARACTER_DAMAGED, BattleContext, BattleState, BuffSlot,
    DebuffSlot, PlayerState,
)
from item_effects_v1 import (
    AttackEffect, BuffRemovalEffect, CleanseDebuffEffect, GainBlockEffect,
    GainBuffEffect, InflictDebuffEffect, RemoveOpponentBlockEffect, UseBuffEffect,
)
from item_factory_registry_v1 import (
    BattleItem, Broom, MagicForDummies, Rat, WandOfEquilibrium,
)


class Receiver(BattleItem):
    def __init__(self, key, callback):
        super().__init__(item_key=key, player_id=0,
                         effects=[GainBuffEffect("Mana", 0)])
        self.callback = callback

    def activate_item(self, context, listener_idx=None):
        self.callback(context)


class BuffStage2EffectsTest(unittest.TestCase):
    def make_context(self, item=None, *, buffs=None, enemy_buffs=None,
                     enemy_debuffs=None, block=0, enemy_block=0):
        if item is None:
            item = BattleItem(item_key="source", player_id=0,
                              effects=[GainBuffEffect("Mana", 0)])
        owner = PlayerState(player_id=0, health=100, max_health=100,
                            items={item.item_key: item}, buffs=buffs or BuffSlot(),
                            block=block)
        enemy = PlayerState(player_id=1, health=100, max_health=100,
                            buffs=enemy_buffs or BuffSlot(),
                            debuffs=enemy_debuffs or DebuffSlot(), block=enemy_block)
        battle = BattleState(players=[owner, enemy], rng=random.Random(7))
        return BattleContext(battle, item, owner, enemy)

    def listen(self, context, emitter, signal, callback):
        receiver = Receiver("receiver" + str(len(context.owner.items)), callback)
        context.owner.items[receiver.item_key] = receiver
        context.battle_state.connect(emitter, signal, (receiver, 0))
        return receiver

    def records(self, context, action):
        return [(index, row["data"]) for index, row in
                enumerate(context.battle_state.log) if row["data"]["action"] == action]

    def test_duration_validation_and_permanent_default(self):
        constructors = (lambda **kw: GainBuffEffect("Mana", 1, **kw),
                        lambda **kw: InflictDebuffEffect("Cold", 1, **kw),
                        lambda **kw: GainBlockEffect(1, **kw))
        for construct in constructors:
            self.assertEqual(construct().duration, -1.0)
            for duration in (-3, 0, 0.25):
                self.assertEqual(construct(duration=duration).duration, float(duration))
            for duration in (True, None, "1", float("nan"), float("inf")):
                with self.subTest(construct=construct, duration=duration):
                    with self.assertRaises(ValueError):
                        construct(duration=duration)

    def test_scaled_temporary_effects_store_once_rounded_successful_amount(self):
        for name, effect, opponent in (
            ("Mana", GainBuffEffect("Mana", 3, duration=0.25), False),
            ("Cold", InflictDebuffEffect("Cold", 3, duration=0.25), True),
            ("Block", GainBlockEffect(3, duration=0.25), False),
        ):
            with self.subTest(name=name):
                context = self.make_context()
                context.item.stack_powers[name] = 1.5
                self.assertTrue(effect.apply(context))
                target = context.opponent if opponent else context.owner
                state = target.stack_states[name]
                self.assertEqual(state.permanent_stacks, 0)
                self.assertEqual(len(state.temporary_stacks), 1)
                batch = state.temporary_stacks[0]
                self.assertEqual((batch.amount, batch.expires_at), (5, 0.25))
                self.assertIs(batch.source_item, context.item)
                self.assertEqual(len(self.records(context, "stack_change")), 1)

    def test_nonpositive_scaled_effects_never_enter_core(self):
        for name, effect in (("Mana", GainBuffEffect("Mana", 1)),
                             ("Cold", InflictDebuffEffect("Cold", 1)),
                             ("Block", GainBlockEffect(1))):
            for power in (0, -1):
                with self.subTest(name=name, power=power):
                    context = self.make_context()
                    context.item.stack_powers[name] = power
                    context.battle_state.gain_stacks = Mock()
                    self.assertFalse(effect.apply(context))
                    context.battle_state.gain_stacks.assert_not_called()
                    self.assertEqual(len(context.battle_state.log), 1)
                    self.assertFalse(context.battle_state.log[0]["data"][
                        "contributes_to_stack_totals"])

    def test_reflected_temporary_debuff_preserves_duration_without_second_power(self):
        context = self.make_context()
        context.item.stack_powers["Blind"] = 2
        context.opponent.stack_states["Blind"].reflect_chance_percent = 100
        parent = context.battle_state.record_log(context.item, {"action": "parent"})
        self.assertFalse(InflictDebuffEffect("Blind", 1, duration=0.5).apply(
            context, trigger_log_handle=parent))
        self.assertEqual((context.owner.debuffs.Blind, context.opponent.debuffs.Blind),
                         (2, 0))
        batch = context.owner.stack_states["Blind"].temporary_stacks[0]
        self.assertEqual((batch.amount, batch.expires_at), (2, 0.5))
        _, change = self.records(context, "stack_change")[0]
        self.assertEqual((change["amount"], change["reflected"],
                          change["trigger_log_sequence"]), (2, True, parent.sequence))

    def test_use_result_returns_real_event_before_nested_logs_and_consumes_once(self):
        context = self.make_context(buffs=BuffSlot(Mana=3))
        parent = context.battle_state.record_log(context.item, {"action": "parent"})
        self.listen(context, context.owner, "character_mana_changed",
                    lambda event: context.battle_state.record_log(
                        context.item, {"action": "nested"}))
        use = UseBuffEffect("Mana", 1)
        context.battle_state.try_use_stacks = Mock(
            wraps=context.battle_state.try_use_stacks)
        result = use.apply_result(context, trigger_log_handle=parent)
        self.assertEqual((result.delta, context.owner.buffs.Mana), (-1, 2))
        self.assertEqual(result.event.log_handle.sequence, 1)
        self.assertIs(result.event.trigger_log_handle, parent)
        self.assertEqual(self.records(context, "use_buff")[0][1][
            "trigger_log_sequence"], parent.sequence)
        self.assertTrue(use.apply(context, trigger_log_handle=parent))
        self.assertEqual((context.owner.buffs.Mana,
                          context.battle_state.try_use_stacks.call_count), (1, 2))
        self.assertEqual(len(self.records(context, "use_buff")), 2)
        self.assertEqual(len(self.records(context, "stack_change")), 2)

    def test_zero_and_insufficient_use_have_no_fake_success_handle(self):
        context = self.make_context()
        zero = UseBuffEffect("Mana", 0)
        self.assertTrue(zero.apply(context))
        result = zero.apply_result(context)
        self.assertEqual((result.delta, result.event), (0, None))
        use = UseBuffEffect("Mana", 1)
        self.assertFalse(use.apply(context))
        self.assertEqual(use.apply_result(context).delta, 0)
        self.assertEqual(self.records(context, "stack_change"), [])
        self.assertEqual(len(self.records(context, "use_buff")), 4)

    def test_gain_block_notifies_character_then_source_then_attempt_with_fixed_delta(self):
        context = self.make_context()
        parent = context.battle_state.record_log(context.item, {"action": "parent"})
        seen = []

        def changed(event):
            seen.append(("character", event))
            context.battle_state.lose_stacks(context.owner, "Block", 2, used=True)

        def gave(event):
            seen.append(("source", event))
            context.battle_state.record_log(context.item, {"action": "gave_callback"})

        self.listen(context, context.owner, "character_block_changed", changed)
        self.listen(context, context.item, "gave_block", gave)
        context.battle_state.emit_signal = Mock(wraps=context.battle_state.emit_signal)
        self.assertTrue(GainBlockEffect(5, duration=0.5).apply(
            context, trigger_log_handle=parent))
        self.assertEqual([name for name, event in seen], ["character", "source"])
        sent = [call.args[2] for call in context.battle_state.emit_signal.call_args_list
                if call.args[1] in ("character_block_changed", "gave_block")]
        self.assertIs(sent[0], sent[1])
        self.assertIs(seen[0][1].log_handle, seen[1][1].log_handle)
        self.assertEqual((seen[0][1].amount, seen[0][1].duration,
                          context.owner.block), (5, 0.5, 3))
        self.assertIs(seen[0][1].trigger_log_handle, parent)
        attempt = context.battle_state.log[-1]["data"]
        self.assertEqual((attempt["action"], attempt["final_block_gained"]),
                         ("gain_block", 5))
        self.assertFalse(attempt["contributes_to_stack_totals"])
        self.assertEqual(len(self.records(context, "stack_change")), 1)

    def test_delayed_block_keeps_immediate_logs_and_same_event_for_both_notifications(self):
        context = self.make_context()
        seen = []
        self.listen(context, context.owner, "character_block_changed",
                    lambda event: seen.append(("character", event)))
        self.listen(context, context.item, "gave_block",
                    lambda event: seen.append(("source", event)))
        context.battle_state.set_signals_delayed(True)
        self.assertTrue(GainBlockEffect(4).apply(context))
        self.assertEqual((context.owner.block, seen), (4, []))
        self.assertEqual([row["data"]["action"] for row in context.battle_state.log],
                         ["stack_change", "gain_block"])
        queued = context.battle_state._pending_signals
        self.assertIs(queued[0][2], queued[1][2])
        context.battle_state.flush_signals()
        self.assertEqual([name for name, event in seen], ["character", "source"])
        self.assertIs(seen[0][1].log_handle, seen[1][1].log_handle)

    def test_block_without_source_uses_power_one_and_has_no_success_notifications(self):
        context = self.make_context()
        context.item = None
        context.battle_state.emit_signal = Mock(wraps=context.battle_state.emit_signal)
        self.assertTrue(GainBlockEffect(2, duration=0).apply(context))
        self.assertEqual(context.owner.block, 2)
        self.assertEqual(context.owner.stack_states["Block"].temporary_stacks[0].amount, 2)
        context.battle_state.emit_signal.assert_not_called()
        self.assertEqual(self.records(context, "stack_change"), [])

    def test_zero_duration_block_is_a_batch_with_an_ordinary_stack_event(self):
        context = self.make_context()
        seen = []
        self.listen(context, context.owner, "character_block_changed", seen.append)
        self.assertTrue(GainBlockEffect(2, duration=0).apply(context))
        state = context.owner.stack_states["Block"]
        self.assertEqual((state.permanent_stacks, len(state.temporary_stacks)), (0, 1))
        self.assertEqual(state.temporary_stacks[0].expires_at, 0)
        self.assertEqual(seen[0].duration, 0)
        self.assertNotIn("duration", self.records(context, "stack_change")[0][1])

    def test_remove_block_obeys_typed_protection_and_passes_explicit_parent(self):
        context = self.make_context(enemy_block=3)
        context.opponent.stack_states["Block"].resist_stacks = 1
        context.opponent.buff_protect_stacks = 7
        parent = context.battle_state.record_log(context.item, {"action": "parent"})
        self.assertTrue(RemoveOpponentBlockEffect(3).apply(
            context, trigger_log_handle=parent))
        self.assertEqual((context.opponent.block, context.opponent.buff_protect_stacks),
                         (1, 7))
        _, change = self.records(context, "stack_change")[0]
        self.assertEqual((change["amount"], change["trigger_log_sequence"]),
                         (-2, parent.sequence))
        _, attempt = self.records(context, "remove_block")[0]
        self.assertEqual(attempt["final_block_removed"], 2)
        self.assertFalse(attempt["contributes_to_stack_totals"])

    def test_remove_and_cleanse_forward_parent_without_guessing_from_context(self):
        context = self.make_context(enemy_buffs=BuffSlot(Mana=2))
        context.battle_state.gain_stacks(context.owner, "Cold", 2)
        parent = context.battle_state.record_log(context.item, {"action": "parent"})
        self.assertTrue(BuffRemovalEffect("Mana", 1).apply(
            context, trigger_log_handle=parent))
        self.assertTrue(CleanseDebuffEffect("Cold", 1).apply(
            context, trigger_log_handle=parent))
        for _, row in self.records(context, "stack_change"):
            self.assertEqual(row["trigger_log_sequence"], parent.sequence)

    def test_attack_result_and_bool_each_resolve_exactly_once(self):
        context = self.make_context()
        context.battle_state.resolve_attack = Mock(wraps=context.battle_state.resolve_attack)
        parent = context.battle_state.record_log(context.item, {"action": "parent"})
        attack = AttackEffect(3, 3, 100)
        result = attack.apply_result(context, ("effect",), trigger_log_handle=parent)
        self.assertTrue(result.hit)
        self.assertTrue(result.is_resolved)
        self.assertIs(result.trigger_log_handle, parent)
        self.assertEqual(result.log_handle.sequence, 1)
        self.assertTrue(attack.apply(context, ("effect",), trigger_log_handle=parent))
        self.assertEqual((context.opponent.health,
                          context.battle_state.resolve_attack.call_count), (94, 2))
        self.assertEqual(len(self.records(context, "attack")), 2)

    def test_miss_has_real_parented_log_but_dead_target_noop_has_none(self):
        context = self.make_context()
        parent = context.battle_state.record_log(context.item, {"action": "parent"})
        result = AttackEffect(3, 3, 0).apply_result(
            context, ("melee",), trigger_log_handle=parent)
        self.assertFalse(result.hit)
        self.assertIsNotNone(result.log_handle)
        self.assertEqual(context.battle_state.log[result.log_handle.sequence]["data"][
            "trigger_log_sequence"], parent.sequence)
        log_count = len(context.battle_state.log)
        context.opponent.is_dead = True
        noop = AttackEffect(3, 3, 100).apply_result(context, ("effect",))
        self.assertFalse(noop.hit)
        self.assertIsNone(noop.log_handle)
        self.assertEqual(len(context.battle_state.log), log_count)

    def test_broom_blind_uses_attack_handle_before_its_chance_log(self):
        item = Broom(item_key="broom", player_id=0)
        item.roll_chance = Mock(return_value=True)
        context = self.make_context(item)
        result = item.effects[1].apply_result(context, ("melee",))
        self.assertTrue(result.hit)
        _, blind = self.records(context, "stack_change")[0]
        self.assertEqual((blind["stack_name"], blind["trigger_log_sequence"]),
                         ("Blind", result.log_handle.sequence))
        self.assertGreater(self.records(context, "inflict_blind_check")[0][0],
                           result.log_handle.sequence)

    def test_rat_children_keep_attack_parent_after_damage_callback_logs(self):
        item = Rat(item_key="rat", player_id=0)
        item.roll_chance = Mock(return_value=True)
        context = self.make_context(item)
        self.listen(context, context.opponent, ATTACK_PHASE_CHARACTER_DAMAGED,
                    lambda event: context.battle_state.record_log(
                        context.item, {"action": "nested_damage"}))
        item.run_effect([True], context)
        attack_index = self.records(context, "attack")[0][0]
        self.assertGreater(self.records(context, "nested_damage")[0][0], attack_index)
        changes = self.records(context, "stack_change")
        self.assertEqual([row["stack_name"] for _, row in changes], ["Poison", "Blind"])
        self.assertEqual([row["trigger_log_sequence"] for _, row in changes],
                         [attack_index, attack_index])
        self.assertEqual(len(self.records(context, "attack")), 1)

    def test_wand_reads_changed_threshold_and_uses_consumption_handle(self):
        item = WandOfEquilibrium(item_key="wand", player_id=0)
        context = self.make_context(item, buffs=BuffSlot(Mana=9, Regeneration=1))

        def gain_changed(event):
            if event.amount > 0:
                context.battle_state.gain_stacks(context.owner, "Mana", 1)

        self.listen(context, context.owner, "character_lucky_changed", gain_changed)
        self.listen(context, context.owner, "character_mana_changed",
                    lambda event: context.battle_state.record_log(
                        context.item, {"action": "nested_mana"}))
        item.run_effect([True], context)
        self.assertEqual((context.owner.buffs.Mana, context.owner.buffs.Empower), (9, 1))
        changes = self.records(context, "stack_change")
        consumption = next(index for index, row in changes if row["used"])
        empower = next(row for _, row in changes if row["stack_name"] == "Empower")
        self.assertEqual(empower["trigger_log_sequence"], consumption)

    def test_magic_max_health_uses_consumption_handle_and_missing_mana_still_activates(self):
        item = MagicForDummies(item_key="book", player_id=0)
        context = self.make_context(item, buffs=BuffSlot(Mana=1))
        self.listen(context, context.owner, "character_mana_changed",
                    lambda event: context.battle_state.record_log(
                        context.item, {"action": "nested_mana"}))
        item.run_effect([True], context)
        consumed_index = self.records(context, "stack_change")[0][0]
        self.assertEqual(self.records(context, "gain_max_health")[0][1][
            "trigger_log_sequence"], consumed_index)
        self.assertEqual(context.owner.max_health, 108)
        activations = len(self.records(context, "item_activation"))
        item.run_effect([True], context)
        self.assertEqual(context.owner.max_health, 108)
        self.assertEqual(len(self.records(context, "item_activation")), activations + 1)
        self.assertEqual(len(self.records(context, "use_buff")), 2)


if __name__ == "__main__":
    unittest.main()
