"""Single-battle Buff.gd timing, accounting, and synchronous reentry contracts.

Native evidence is retained under data/buff_stage2_t0 and
data/buff_natural_reentry. These small listeners reproduce the recorded core
operations; they do not add the native test board's items to the simulator.
"""
import copy
import json
import random
import struct
import unittest

from battle_module_v1 import (
    BattleState,
    BuffSlot,
    DebuffSlot,
    PhysicsTimerState,
    PlayerState,
    StackState,
    _advance_timer,
    _godot_float32,
    _start_timer,
    _stop_timer,
    _timer_time_left,
    serialize_player_state,
    _BattleFinishedSignal,
)
from item_effects_v1 import GainBuffEffect
from item_factory_registry_v1 import BattleItem


DT = struct.unpack("f", struct.pack("f", 1.0 / 60.0))[0]


def float32(value):
    return struct.unpack("f", struct.pack("f", value))[0]


class Draws:
    def __init__(self, *values):
        self.values = list(values)
        self.seen = []

    def random(self):
        if not self.values:
            raise AssertionError("unexpected mechanism RNG draw")
        value = self.values.pop(0)
        self.seen.append(value)
        return value

    def shuffle(self, values):
        pass

    def randint(self, low, high):
        if low != high:
            raise AssertionError("unexpected random damage range")
        return low


class Listener(BattleItem):
    def __init__(self, key, side, callback):
        super().__init__(item_key=key, player_id=side,
                         effects=[GainBuffEffect("Mana", 0)])
        self.callback = callback

    def activate_item(self, context, listener_idx=None):
        self.callback(context)


class StepItem(BattleItem):
    def __init__(self, callback):
        super().__init__(item_key="clock_item", player_id=0,
                         is_active_item=True, effects=[GainBuffEffect("Mana", 0)])
        self.callback = callback

    def activate_item(self, context, listener_idx=None):
        self.callback(context)


class CoreCase(unittest.TestCase):
    def make_battle(self, *, owner_buffs=None, owner_debuffs=None,
                    owner_block=0, rng=None, active_item=None):
        self.a = BattleItem(item_key="source_a", player_id=0,
                            effects=[GainBuffEffect("Mana", 0)])
        self.b = BattleItem(item_key="source_b", player_id=0,
                            effects=[GainBuffEffect("Mana", 0)])
        self.c = BattleItem(item_key="source_c", player_id=0,
                            effects=[GainBuffEffect("Mana", 0)])
        items = {item.item_key: item for item in (self.a, self.b, self.c)}
        if active_item is not None:
            items[active_item.item_key] = active_item
        self.owner = PlayerState(
            player_id=0, health=200, max_health=200, block=owner_block,
            buffs=owner_buffs or BuffSlot(),
            debuffs=owner_debuffs or DebuffSlot(), items=items,
            stamina=0, max_stamina=10,
        )
        self.enemy = PlayerState(player_id=1, health=200, max_health=200)
        self.battle = BattleState(
            players=[self.owner, self.enemy], rng=rng or Draws(),
            active_items=[] if active_item is None else [active_item],
        )
        self.battle.prepareItems()
        self.battle.start_combat()
        return self.battle

    def listen(self, player, stack, callback, *, side=0):
        key = "listener_" + str(len(self.battle._bus_cache))
        listener = Listener(key, side, callback)
        self.battle.players[side].items[key] = listener
        name = "lucky" if stack == "Luck" else stack.lower()
        self.battle.connect(player, "character_" + name + "_changed",
                            (listener, 0))
        return listener

    def changes(self, stack=None):
        return [row for row in self.battle.log
                if row["data"].get("action") == "stack_change"
                and (stack is None or row["data"]["stack_name"] == stack)]

    def steps(self, count):
        for _ in range(count):
            self.battle.step()


class PhysicsTimerTest(unittest.TestCase):
    def test_start_and_getter_are_float32_but_left_is_double(self):
        timer = PhysicsTimerState()
        _start_timer(timer, 0.2)
        self.assertEqual(timer.wait_time, float32(0.2))
        self.assertGreater(_timer_time_left(timer), 0.2)
        self.assertFalse(_advance_timer(timer, DT, one_shot=True))
        self.assertEqual(timer.time_left, float32(0.2) - DT)
        self.assertNotEqual(timer.time_left, float32(timer.time_left))
        self.assertEqual(_timer_time_left(timer), float32(timer.time_left))
        self.assertEqual(_godot_float32(0.2), float32(0.2))

    def test_zero_start_reuses_wait_and_stop_preserves_it(self):
        timer = PhysicsTimerState()
        _start_timer(timer, 0)
        self.assertEqual((timer.wait_time, timer.time_left, timer.processing),
                         (1.0, 1.0, True))
        _start_timer(timer, 0.1)
        _stop_timer(timer)
        self.assertEqual((timer.time_left, timer.processing), (-1.0, False))
        _start_timer(timer, 0)
        self.assertEqual((timer.wait_time, timer.time_left),
                         (float32(0.1), float32(0.1)))

    def test_exact_zero_is_stopped_query_but_has_not_timed_out(self):
        timer = PhysicsTimerState()
        _start_timer(timer, DT)
        self.assertFalse(_advance_timer(timer, DT, one_shot=True))
        self.assertEqual(timer.time_left, 0)
        self.assertTrue(timer.processing)
        self.assertEqual(_timer_time_left(timer), 0)
        self.assertTrue(_advance_timer(timer, DT, one_shot=True))
        self.assertEqual((timer.time_left, timer.processing), (-1.0, False))

    def test_repeating_timer_retains_overshoot_and_fires_only_once(self):
        timer = PhysicsTimerState()
        _start_timer(timer, 1)
        self.assertTrue(_advance_timer(timer, 2.5, one_shot=False))
        self.assertEqual((timer.time_left, timer.processing), (-0.5, True))
        self.assertTrue(_advance_timer(timer, 0.25, one_shot=False))
        self.assertEqual(timer.time_left, 0.25)
        self.assertFalse(_advance_timer(timer, 0.25, one_shot=False))


class StackAccountingTest(CoreCase):
    def test_initial_values_seed_once_without_replacing_slots_or_resistance(self):
        configured = StackState(resist_stacks=4)
        player = PlayerState(
            buffs=BuffSlot(Mana=3), debuffs=DebuffSlot(Cold=2), block=7,
            stack_states={"Mana": configured},
        )
        self.assertIs(player.stack_states["Mana"], configured)
        self.assertEqual(configured.resist_stacks, 4)
        self.assertEqual(configured.permanent_stacks, 3)
        self.assertEqual(player.stack_states["Cold"].permanent_stacks, 2)
        self.assertEqual(player.stack_states["Block"].permanent_stacks, 7)
        self.assertEqual(len(player.stack_states), 11)
        other = PlayerState()
        self.assertIsNot(configured.timer, other.stack_states["Mana"].timer)
        self.assertIsNot(configured.temporary_stacks,
                         other.stack_states["Mana"].temporary_stacks)
        self.assertFalse(hasattr(configured, "current"))

    def test_lazy_state_seeds_only_when_missing(self):
        battle = self.make_battle(owner_buffs=BuffSlot(Mana=3))
        state = battle._stack_state(self.owner, "Mana")
        self.owner.buffs.Mana = 8  # Explicitly observe, never auto-reconcile.
        self.assertIs(battle._stack_state(self.owner, "Mana"), state)
        self.assertEqual(state.permanent_stacks, 3)
        del self.owner.stack_states["Mana"]
        self.assertEqual(battle._stack_state(self.owner, "Mana").permanent_stacks, 8)
        self.assertEqual(battle._stack_slot(self.owner, "Block"),
                         (self.owner, "block"))

    def test_prepare_preserves_temporary_state_created_before_prepare(self):
        owner = PlayerState(player_id=0, health=20)
        enemy = PlayerState(player_id=1, health=20)
        battle = BattleState(players=[owner, enemy])
        battle.gain_stacks(owner, "Mana", 2, duration=0.25)
        state = battle._stack_state(owner, "Mana")
        batch = state.temporary_stacks[0]
        battle.prepareItems()
        battle.start_combat()
        self.assertEqual(owner.buffs.Mana, 2)
        self.assertIs(state.temporary_stacks[0], batch)
        self.assertEqual(state.timer.time_left, 0.25)

    def test_source_none_temporary_gain_and_expiry_have_no_success_events(self):
        battle = self.make_battle()
        seen = []
        self.listen(self.owner, "Mana", seen.append)
        battle.gain_stacks(self.owner, "Mana", 2, duration=0.1)
        state = battle._stack_state(self.owner, "Mana")
        self.assertIsNone(state.temporary_stacks[0].source_item)
        self.steps(6)
        self.assertEqual((self.owner.buffs.Mana, state.temporary_stacks), (0, []))
        self.assertEqual((seen, battle.log), ([], []))

    def test_losing_uses_permanent_then_farthest_and_keeps_partial_deadline(self):
        battle = self.make_battle(owner_buffs=BuffSlot(Mana=1))
        battle.gain_stacks(self.owner, "Mana", 2, duration=0.1, source_item=self.a)
        battle.gain_stacks(self.owner, "Mana", 3, duration=0.3, source_item=self.b)
        state = battle._stack_state(self.owner, "Mana")
        early, late = state.temporary_stacks
        old_deadline = late.expires_at
        result = battle.lose_stacks(self.owner, "Mana", 2, source_item=self.c)
        self.assertEqual((result.delta, self.owner.buffs.Mana,
                          state.permanent_stacks), (-2, 4, 0))
        self.assertEqual((early.amount, late.amount), (2, 2))
        self.assertEqual(late.expires_at, old_deadline)
        self.assertIs(late.source_item, self.b)
        self.assertEqual(state.next_temporary_index, 0)
        self.assertEqual(state.timer.wait_time, float32(0.1))

    def test_equal_farthest_deadline_removes_first_inserted(self):
        battle = self.make_battle()
        battle.gain_stacks(self.owner, "Mana", 2, duration=0.25, source_item=self.a)
        battle.gain_stacks(self.owner, "Mana", 3, duration=0.25, source_item=self.b)
        state = battle._stack_state(self.owner, "Mana")
        first, second = state.temporary_stacks
        battle.lose_stacks(self.owner, "Mana", 1)
        self.assertEqual((first.amount, second.amount), (1, 3))
        self.assertEqual(state.next_temporary_index, 0)

    def test_try_use_is_atomic_and_partial_raw_use_skips_all_protection(self):
        battle = self.make_battle(owner_buffs=BuffSlot(Mana=1))
        battle.gain_stacks(self.owner, "Mana", 2, duration=0.25)
        state = battle._stack_state(self.owner, "Mana")
        state.resist_stacks = 4
        state.cleanse_protection_chance_percent = 100
        self.owner.buff_protect_stacks = 5
        batch = state.temporary_stacks[0]
        self.assertEqual(battle.try_use_stacks(self.owner, "Mana", 4).delta, 0)
        self.assertEqual((self.owner.buffs.Mana, state.permanent_stacks,
                          batch.amount), (3, 1, 2))
        self.assertEqual(battle.lose_stacks(self.owner, "Mana", 9, used=True).delta, -3)
        self.assertEqual((self.owner.buffs.Mana, state.permanent_stacks,
                          state.temporary_stacks, state.timer.processing), (0, 0, [], False))
        self.assertEqual((state.resist_stacks, self.owner.buff_protect_stacks), (4, 5))

    def test_private_shortfall_does_not_reduce_the_requested_current_loss(self):
        battle = self.make_battle(owner_buffs=BuffSlot(Mana=5))
        state = battle._stack_state(self.owner, "Mana")
        state.permanent_stacks = 1  # Explicit mismatch fixture.
        result = battle.lose_stacks(self.owner, "Mana", 4, source_item=self.a)
        self.assertEqual((result.delta, self.owner.buffs.Mana,
                          state.permanent_stacks), (-4, 1, 0))
        self.assertEqual(battle.log[0]["data"]["reason"], "private_amount_missing")

    def test_expiry_bypasses_protection_and_keeps_fixed_event_facts(self):
        battle = self.make_battle()
        parent = battle.record_log("root", {"action": "parent"})
        battle.gain_stacks(self.owner, "Mana", 2, duration=0.1,
                           source_item=self.a, trigger_log_handle=parent)
        state = battle._stack_state(self.owner, "Mana")
        state.resist_stacks = 20
        state.cleanse_protection_chance_percent = 100
        self.owner.buff_protect_stacks = 20
        events = []
        self.listen(self.owner, "Mana", events.append)
        self.steps(6)
        event = events[0]
        self.assertEqual((event.amount, event.timeout, event.used, event.reflected),
                         (-2, True, False, False))
        self.assertIs(event.target, self.owner)
        self.assertIs(event.source_item, self.a)
        self.assertIsNone(event.trigger_log_handle)
        self.assertEqual((state.resist_stacks, self.owner.buff_protect_stacks), (20, 20))
        self.assertEqual(battle.log[event.log_handle.sequence]["source"]["item_key"],
                      self.a.item_key)

    def test_temporary_block_cap_and_protected_absorption_keep_budget(self):
        battle = self.make_battle(owner_block=99999)
        gain = battle.gain_stacks(self.owner, "Block", 8, duration=0.25,
                                  source_item=self.a)
        self.assertEqual((gain.delta, self.owner.block), (1, 100000))
        state = battle._stack_state(self.owner, "Block")
        state.resist_stacks = 3
        self.owner.buff_protect_stacks = 8
        battle.commit_health_reduction(self.owner, 5, 5)
        self.assertEqual((self.owner.block, self.owner.health), (99998, 195))
        self.assertEqual((state.resist_stacks, self.owner.buff_protect_stacks), (0, 8))
        self.assertEqual(state.permanent_stacks, 99997)
        self.assertEqual(len(self.changes("Block")), 1)

    def test_cap_before_expiry_swallows_partial_reflection_but_same_frame_expiry_frees_room(self):
        battle = self.make_battle(owner_debuffs=DebuffSlot(Cold=9998),
                                  rng=Draws(*([0.8] * 8)))
        battle.gain_stacks(self.owner, "Cold", 2, duration=0.25, source_item=self.a)
        self.owner.debuff_reflect_stacks = 1
        blocked = battle.gain_stacks(self.owner, "Cold", 3, duration=0.5,
                                     source_item=self.b)
        self.assertEqual((blocked.delta, self.owner.debuffs.Cold,
                          self.enemy.debuffs.Cold), (0, 10000, 0))
        self.assertEqual(self.owner.debuff_reflect_stacks, 0)
        nested = []

        def refill(ctx):
            if ctx.timeout:
                self.assertEqual(self.owner.debuffs.Cold, 9998)
                self.owner.debuff_reflect_stacks = 1
                nested.append((battle.frame, battle.gain_stacks(
                    self.owner, "Cold", 3, duration=0.5, source_item=self.b)))

        self.listen(self.owner, "Cold", refill)
        self.steps(15)
        self.assertEqual(nested[0][1].delta, 2)
        self.assertEqual((self.owner.debuffs.Cold, self.enemy.debuffs.Cold), (10000, 1))
        events = self.changes("Cold")[-3:]
        self.assertEqual([row["data"]["amount"] for row in events], [-2, 2, 1])
        self.assertEqual([row["frame"] for row in events], [14, 14, 14])
        self.assertEqual(nested[0][0], 14)
        self.assertTrue(events[-1]["data"]["reflected"])


class TemporaryExpiryTest(CoreCase):
    def test_zero_fresh_and_reused_wait_do_not_expire_immediately(self):
        battle = self.make_battle()
        battle.gain_stacks(self.owner, "Mana", 1, duration=0, source_item=self.a)
        self.steps(59)
        self.assertEqual(self.owner.buffs.Mana, 1)

        self.steps(1)
        self.assertEqual(self.owner.buffs.Mana, 0)
        battle.gain_stacks(self.owner, "Mana", 1, duration=0.1, source_item=self.a)
        self.steps(6)
        battle.gain_stacks(self.owner, "Mana", 1, duration=0, source_item=self.a)
        self.steps(5)
        self.assertEqual(self.owner.buffs.Mana, 1)
        self.steps(1)
        self.assertEqual(self.owner.buffs.Mana, 0)

    def test_zero_running_selects_new_batch_but_reuses_previous_wait(self):
        battle = self.make_battle()
        battle.gain_stacks(self.owner, "Mana", 1, duration=0.3, source_item=self.a)
        battle.gain_stacks(self.owner, "Mana", 1, duration=0, source_item=self.b)
        state = battle._stack_state(self.owner, "Mana")
        self.assertEqual((state.next_temporary_index, state.timer.wait_time),
                         (1, float32(0.3)))
        self.steps(18)
        self.assertEqual(self.owner.buffs.Mana, 1)
        self.assertEqual(self.changes("Mana")[-1]["source"]["item_key"], "source_b")
        self.steps(1)
        self.assertEqual(self.owner.buffs.Mana, 0)

    def test_equal_point_two_restarts_but_exact_point_two_five_keeps_next(self):
        for duration, first, second in ((0.2, "source_b", "source_a"),
                                        (0.25, "source_a", "source_b")):
            with self.subTest(duration=duration):
                battle = self.make_battle()
                battle.gain_stacks(self.owner, "Mana", 2, duration=duration, source_item=self.a)
                battle.gain_stacks(self.owner, "Mana", 3, duration=duration, source_item=self.b)
                self.steps(16)
                expired = [row for row in self.changes("Mana") if row["data"]["timeout"]]
                self.assertEqual([row["source"]["item_key"] for row in expired], [first, second])
                self.assertEqual(expired[1]["frame"] - expired[0]["frame"], 1)
                self.assertEqual([row["frame"] for row in expired],
                                 [11, 12] if duration == 0.2 else [14, 15])

    def test_positive_ten_ms_tail_recurses_but_outside_waits(self):
        for late, expected_gap in ((0.125, 0), (0.16, 3)):
            with self.subTest(late=late):
                battle = self.make_battle()
                observed = []
                self.listen(self.owner, "Mana", lambda ctx: observed.append(
                    (ctx.amount, battle.frame, battle.time)) if ctx.timeout else None)
                battle.gain_stacks(self.owner, "Mana", 2, duration=0.12, source_item=self.a)
                battle.gain_stacks(self.owner, "Mana", 3, duration=late, source_item=self.b)
                self.steps(12)
                self.assertEqual([entry[0] for entry in observed], [-2, -3])
                self.assertEqual(observed[1][1] - observed[0][1], expected_gap)
                if expected_gap == 0:
                    self.assertGreater(late - observed[0][2], 0)
                    self.assertLessEqual(late - observed[0][2], 0.01)

    def test_native_n6_shared_index_deletes_long_batch_and_expires_old_twice(self):
        battle = self.make_battle()
        state = battle._stack_state(self.owner, "Spikes")
        battle.gain_stacks(self.owner, "Spikes", 2, duration=6.2, source_item=self.b)
        battle.gain_stacks(self.owner, "Spikes", 2, duration=4, source_item=self.a)
        long_batch, old_batch = state.temporary_stacks
        selected = []
        added = []

        def add_new_once(ctx):
            if not ctx.timeout:
                return
            selected.append(state.temporary_stacks[state.next_temporary_index])
            if not added:
                self.assertEqual(self.owner.buffs.Spikes, 2)
                battle.gain_stacks(self.owner, "Spikes", 2, duration=4, source_item=self.a)
                added.append(state.temporary_stacks[-1])
                self.assertEqual(state.next_temporary_index, 0)
                self.assertIn(old_batch, state.temporary_stacks)

        self.listen(self.owner, "Spikes", add_new_once)
        self.steps(240)
        self.assertEqual(self.owner.buffs.Spikes, 4)
        self.assertEqual(state.temporary_stacks, [old_batch, added[0]])
        self.assertNotIn(long_batch, state.temporary_stacks)
        self.steps(1)
        self.assertEqual(selected, [old_batch, old_batch])
        self.assertEqual(self.owner.buffs.Spikes, 2)
        self.steps(133)
        self.assertGreater(battle.time, 6.2)
        self.assertEqual((self.owner.buffs.Spikes, state.temporary_stacks), (2, [added[0]]))
        self.steps(106)
        self.assertEqual((self.owner.buffs.Spikes, state.temporary_stacks), (0, []))

    def test_different_batch_amounts_leave_observable_current_mismatch(self):
        battle = self.make_battle(owner_buffs=BuffSlot(Mana=1))
        state = battle._stack_state(self.owner, "Mana")
        battle.gain_stacks(self.owner, "Mana", 3, duration=0.3, source_item=self.b)
        battle.gain_stacks(self.owner, "Mana", 2, duration=0.1, source_item=self.a)
        reacted = []

        def reenter(ctx):
            if ctx.timeout and not reacted:
                reacted.append(True)
                battle.gain_stacks(self.owner, "Mana", 1, duration=0.5, source_item=self.c)

        self.listen(self.owner, "Mana", reenter)
        self.steps(40)
        self.assertEqual((self.owner.buffs.Mana, state.permanent_stacks,
                          state.temporary_stacks), (2, 1, []))
        self.assertEqual([row["data"]["amount"] for row in self.changes("Mana")
                          if row["data"]["timeout"]], [-2, -2, -1])
        self.assertIs(battle._stack_state(self.owner, "Mana"), state)
        self.assertEqual(self.owner.buffs.Mana, 2)

    def test_stale_index_aborts_only_that_callback_and_new_temp_wakes_old_batch(self):
        battle = self.make_battle()
        state = battle._stack_state(self.owner, "Mana")
        battle.gain_stacks(self.owner, "Mana", 3, duration=10, source_item=self.b)
        battle.gain_stacks(self.owner, "Mana", 2, duration=5, source_item=self.a)
        old_batch = state.temporary_stacks[1]
        battle.lose_stacks(self.owner, "Mana", 3)
        battle.gain_stacks(self.owner, "Empower", 1, duration=5, source_item=self.c)
        self.steps(300)
        self.assertEqual((self.owner.buffs.Mana, state.next_temporary_index,
                          state.temporary_stacks, state.timer.processing),
                         (2, 1, [old_batch], False))
        self.assertEqual(self.owner.buffs.Empower, 0)
        self.assertIsNone(battle.winner)
        self.assertFalse(any(row["data"]["timeout"] for row in self.changes("Mana")))
        battle.gain_stacks(self.owner, "Mana", 1, duration=0.25, source_item=self.c)
        self.steps(16)
        self.assertEqual((self.owner.buffs.Mana, state.temporary_stacks), (0, []))

    def test_invalid_remove_is_noop_then_tail_rescans_and_later_finishes(self):
        battle = self.make_battle()
        battle.gain_stacks(self.owner, "Mana", 1, duration=0.1, source_item=self.a)
        battle.gain_stacks(self.owner, "Mana", 1, duration=0.3, source_item=self.b)
        state = battle._stack_state(self.owner, "Mana")
        changed = []

        def corrupt_index(ctx):
            if ctx.timeout and not changed:
                changed.append(True)
                state.next_temporary_index = 99  # Explicit native error fixture.

        self.listen(self.owner, "Mana", corrupt_index)
        self.steps(6)
        self.assertEqual(len(state.temporary_stacks), 2)
        self.assertEqual(state.next_temporary_index, 0)
        self.assertTrue(state.timer.processing)
        self.steps(20)
        self.assertEqual((self.owner.buffs.Mana, state.temporary_stacks), (0, []))

    def test_empty_tail_does_not_stop_timer_started_by_reentrant_gain(self):
        battle = self.make_battle()
        battle.gain_stacks(self.owner, "Mana", 1, duration=0.1, source_item=self.a)
        state = battle._stack_state(self.owner, "Mana")

        def remove_new_batch(ctx):
            if ctx.timeout:
                battle.gain_stacks(self.owner, "Mana", 1, duration=0.5, source_item=self.b)
                state.temporary_stacks.pop()  # Isolate the otherwise empty tail.

        self.listen(self.owner, "Mana", remove_new_batch)
        self.steps(6)
        self.assertEqual(state.temporary_stacks, [])
        self.assertTrue(state.timer.processing)
        self.assertEqual(state.timer.wait_time, 0.5)
        self.assertEqual(self.owner.buffs.Mana, 1)



class InternalPhaseTest(CoreCase):
    def test_global_start_signal_precedes_system_timers_and_preserves_its_temporary_gain(self):
        source = Listener("start_source", 0, lambda ctx: None)
        owner = PlayerState(player_id=0, health=20, items={source.item_key: source})
        enemy = PlayerState(player_id=1, health=20)
        battle = BattleState(players=[owner, enemy], rng=Draws())
        battle.prepareItems()
        seen = []

        def on_start(ctx):
            seen.append((owner.status_tick_timer.processing,
                         battle.fatigue_start_timer.processing))
            battle.gain_stacks(owner, "Mana", 1, duration=0.25, source_item=source)

        source.callback = on_start
        battle.connect(None, "combat_start", (source, 0))
        battle.start_combat()
        self.assertEqual(seen, [(False, False)])
        state = battle._stack_state(owner, "Mana")
        self.assertEqual(state.timer.time_left, 0.25)
        self.assertEqual(owner.buffs.Mana, 1)
        battle.step()
        self.assertEqual(state.timer.time_left, 0.25 - DT)

    def test_initially_inactive_timer_started_in_callback_waits_next_step(self):
        battle = self.make_battle()
        battle.gain_stacks(self.enemy, "Mana", 1, duration=DT / 2, source_item=self.a)
        state = battle._stack_state(self.owner, "Mana")
        self.listen(self.enemy, "Mana", lambda ctx: battle.gain_stacks(
            self.owner, "Mana", 1, duration=0.25, source_item=self.b)
            if ctx.timeout else None)
        battle.step()
        self.assertEqual(state.timer.time_left, 0.25)
        battle.step()
        self.assertEqual(state.timer.time_left, 0.25 - DT)

    def test_previously_active_timer_uses_restarted_live_left(self):
        battle = self.make_battle()
        battle.gain_stacks(self.owner, "Mana", 1, duration=1, source_item=self.a)
        battle.gain_stacks(self.enemy, "Mana", 1, duration=DT / 2, source_item=self.a)
        state = battle._stack_state(self.owner, "Mana")
        self.listen(self.enemy, "Mana", lambda ctx: battle.gain_stacks(
            self.owner, "Mana", 1, duration=0.25, source_item=self.b)
            if ctx.timeout else None)
        battle.step()
        self.assertEqual(state.timer.time_left, 0.25 - DT)
        self.assertEqual(state.next_temporary_index, 1)

    def test_systems_run_before_time_stamina_and_items(self):
        order = []
        item = StepItem(lambda ctx: order.append(("item", ctx.battle_state.time,
                                                  ctx.owner.stamina)))
        battle = self.make_battle(active_item=item)
        # Explicit timer fixture isolates one collision without changing APIs.
        for target in battle.players:
            _start_timer(target.status_tick_timer, DT / 2)
            battle.gain_stacks(target, "Mana", 1, duration=DT / 2, source_item=self.a)
            self.listen(target, "Mana", lambda ctx, side=target.player_id:
                        order.append(("expiry" + str(side), battle.time, self.owner.stamina))
                        if ctx.timeout else None)
        battle._apply_regeneration_tick = lambda target: order.append(
            ("tick" + str(target.player_id), battle.time, self.owner.stamina))
        battle.inflict_fatigue = lambda target, **kwargs: order.append(
            ("fatigue" + str(target.player_id), battle.time, self.owner.stamina))
        _stop_timer(battle.fatigue_start_timer)
        _start_timer(battle.fatigue_tick_timer, DT / 2)
        battle.step()
        self.assertEqual([row[0] for row in order], [
            "tick1", "expiry1", "fatigue1", "fatigue0", "tick0", "expiry0", "item"])
        self.assertTrue(all(row[1:] == (0.0, 0) for row in order[:-1]))
        self.assertEqual(order[-1][1:], (DT, round(DT, 4)))

    def test_status_and_fatigue_follow_native_sixtieth_step_boundaries(self):
        battle = self.make_battle(owner_buffs=BuffSlot(Regeneration=1))
        battle.commit_health_reduction(self.owner, 0, 20)
        self.steps(59)
        self.assertEqual(self.owner.health, 180)
        battle.step()
        self.assertEqual(self.owner.health, 181)
        self.assertEqual(self.owner.status_tick_counter, 1)
        self.steps(959)
        self.assertEqual(self.owner.fatigue_damage, 0)
        battle.step()
        self.assertEqual(self.owner.fatigue_damage, 1)
        rows = [row for row in battle.log if row["data"].get("action") == "fatigue_damage"]
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["frame"], 1019)
        self.assertEqual(rows[0]["time"], round(1019 * DT, 3))

    def test_invalid_dt_and_duration_do_not_mutate_state_or_rng(self):
        battle = self.make_battle()
        before = (self.owner.buffs.Mana, len(battle.log), battle.time,
                  battle.frame, list(battle.rng.seen))
        for invalid in (0, -1, True, float("nan"), float("inf"), 1e100, 1e-100):
            with self.subTest(dt=invalid), self.assertRaises(ValueError):
                battle.run(1, invalid)
        for invalid in (True, float("nan"), float("inf"), 1e100):
            with self.subTest(duration=invalid), self.assertRaises(ValueError):
                battle.gain_stacks(self.enemy, "Blind", 1, duration=invalid,
                                   source_item=self.a)
        self.assertEqual(before, (self.owner.buffs.Mana, len(battle.log), battle.time,
                                  battle.frame, battle.rng.seen))

    def test_positive_duration_underflow_keeps_deadline_but_starts_with_default_wait(self):
        battle = self.make_battle()
        battle.gain_stacks(self.owner, "Mana", 1, duration=1e-100, source_item=self.a)
        state = battle._stack_state(self.owner, "Mana")
        self.assertEqual(state.temporary_stacks[0].expires_at, 1e-100)
        self.assertEqual((state.timer.wait_time, state.timer.time_left), (1.0, 1.0))
        self.steps(59)
        self.assertEqual(self.owner.buffs.Mana, 1)
        battle.step()
        self.assertEqual(self.owner.buffs.Mana, 0)

    def test_budget_cut_keeps_timers_but_natural_end_clears_batches_only(self):
        battle = self.make_battle()
        battle.gain_stacks(self.owner, "Mana", 2, source_item=self.a)
        battle.gain_stacks(self.owner, "Mana", 3, duration=0.25, source_item=self.a)
        state = battle._stack_state(self.owner, "Mana")
        battle.run(1)
        self.assertTrue(state.timer.processing)
        self.assertEqual(len(state.temporary_stacks), 1)
        self.enemy.is_dead = True
        battle.commit_health_reduction(self.enemy, 0, 200)
        battle.check_battle_end()
        self.assertEqual((self.owner.buffs.Mana, state.permanent_stacks), (5, 2))
        self.assertEqual(state.temporary_stacks, [])
        self.assertFalse(state.timer.processing)
        self.assertEqual(state.timer.wait_time, 0.25)


class DelayedNotificationTest(CoreCase):
    def test_numbers_logs_and_reflection_are_immediate_but_notifications_wait(self):
        battle = self.make_battle(rng=Draws(0.8))
        events = []
        self.enemy.debuff_reflect_stacks = 1
        self.listen(self.owner, "Blind", lambda ctx: events.append(ctx))
        battle.set_signals_delayed(True)
        result = battle.gain_stacks(self.enemy, "Blind", 1, duration=0.25,
                                    source_item=self.a)
        self.assertEqual((result.delta, self.enemy.debuffs.Blind, self.owner.debuffs.Blind),
                         (0, 0, 1))
        reflected = battle._stack_state(self.owner, "Blind").temporary_stacks[0]
        self.assertEqual(reflected.expires_at, 0.25)
        self.assertEqual(len(self.changes("Blind")), 1)
        self.assertEqual(events, [])
        battle.flush_signals()
        self.assertEqual(len(events), 1)
        self.assertTrue(events[0].reflected)
        self.assertEqual(events[0].duration, 0.25)

    def test_logs_keep_creation_order_but_notifications_are_a_c_b(self):
        battle = self.make_battle()
        seen = []

        def mana(ctx):
            seen.append("A")
            battle.record_log("probe", {"action": "interleaved"})
            battle.gain_stacks(self.owner, "Luck", 1, source_item=self.c,
                               trigger_log_handle=ctx.log_handle)

        self.listen(self.owner, "Mana", mana)
        self.listen(self.owner, "Heat", lambda ctx: seen.append("B"))
        self.listen(self.owner, "Luck", lambda ctx: seen.append("C"))
        battle.set_signals_delayed(True)
        a = battle.gain_stacks(self.owner, "Mana", 1, source_item=self.a)
        b = battle.gain_stacks(self.owner, "Heat", 1, source_item=self.b)
        self.assertEqual((self.owner.buffs.Mana, self.owner.buffs.Heat), (1, 1))
        self.assertEqual((a.event.log_handle.sequence, b.event.log_handle.sequence), (0, 1))
        self.assertEqual(seen, [])
        battle.flush_signals()
        self.assertEqual(seen, ["A", "C", "B"])
        self.assertEqual([row["sequence"] for row in battle.log], list(range(4)))
        child = self.changes("Luck")[0]
        self.assertEqual(child["data"]["trigger_log_sequence"], 0)
        self.assertEqual(child["sequence"], 3)

    def test_nested_flush_and_reopened_delay_do_not_replay_or_delay_outer_entries(self):
        battle = self.make_battle()
        seen = []

        def mana(ctx):
            seen.append("A")
            battle.set_signals_delayed(True)
            battle.gain_stacks(self.owner, "Luck", 1, source_item=self.c)
            battle.flush_signals()
            battle.set_signals_delayed(True)
            battle.gain_stacks(self.owner, "Spikes", 1, source_item=self.c)

        for name, callback in (("Mana", mana), ("Heat", lambda ctx: seen.append("B")),
                               ("Luck", lambda ctx: seen.append("C")),
                               ("Spikes", lambda ctx: seen.append("D"))):
            self.listen(self.owner, name, callback)
        battle.set_signals_delayed(True)
        battle.gain_stacks(self.owner, "Mana", 1, source_item=self.a)
        battle.gain_stacks(self.owner, "Heat", 1, source_item=self.b)
        battle.flush_signals()
        self.assertEqual(seen, ["A", "C", "B"])
        self.assertTrue(battle.signals_delayed)
        self.assertEqual(len(battle._pending_signals), 1)
        battle.flush_signals()
        self.assertEqual(seen, ["A", "C", "B", "D"])
        self.assertFalse(battle.signals_delayed)

    def test_terminal_flush_retains_already_written_logs_and_numbers(self):
        battle = self.make_battle()
        seen = []

        def end(ctx):
            seen.append("A")
            battle.commit_health_reduction(self.enemy, 0, 200)
            self.enemy.is_dead = True
            battle.check_battle_end()

        self.listen(self.owner, "Mana", end)
        self.listen(self.owner, "Heat", lambda ctx: seen.append("B"))
        battle.set_signals_delayed(True)
        battle.gain_stacks(self.owner, "Mana", 1, source_item=self.a)
        battle.gain_stacks(self.owner, "Heat", 2, source_item=self.b)
        battle.flush_signals()
        self.assertEqual(seen, ["A"])
        self.assertEqual((self.owner.buffs.Mana, self.owner.buffs.Heat), (1, 2))
        self.assertEqual(len(self.changes()), 2)
        self.assertEqual(battle._pending_signals, [])

    def test_exporting_between_steps_does_not_change_battle_rng_or_notifications(self):
        def execute(export):
            battle = self.make_battle(rng=random.Random(4729))

            def live_state():
                return [(player.health, player.stamina, player.block,
                         vars(player.buffs).copy(), vars(player.debuffs).copy(),
                         [(name, state.permanent_stacks, state.next_temporary_index,
                           tuple((batch.amount, batch.expires_at, batch.source_item.item_key)
                                 for batch in state.temporary_stacks),
                           state.timer.wait_time, state.timer.time_left, state.timer.processing)
                          for name, state in player.stack_states.items()])
                        for player in battle.players]

            notifications = []
            self.listen(self.owner, "Mana", lambda ctx: notifications.append(
                (ctx.amount, ctx.timeout, ctx.target.player_id, ctx.source_item.item_key)))
            battle.gain_stacks(self.owner, "Mana", 2, duration=0.12, source_item=self.a)
            battle.gain_stacks(self.enemy, "Cold", 2, duration=0.25, source_item=self.b)
            for _ in range(20):
                if export:
                    before_rng = battle.rng.getstate()
                    before_logs = copy.deepcopy(battle.log)
                    before_notifications = list(notifications)
                    before_state = live_state()
                    json.dumps([serialize_player_state(player) for player in battle.players])
                    json.dumps(battle.log)
                    self.assertEqual(battle.rng.getstate(), before_rng)
                    self.assertEqual(battle.log, before_logs)
                    self.assertEqual(notifications, before_notifications)
                    self.assertEqual(live_state(), before_state)
                battle.step()
            return ([serialize_player_state(player) for player in battle.players],
                    battle.rng.getstate(), notifications, battle.log, battle.winner)

        self.assertEqual(execute(False), execute(True))


if __name__ == "__main__":
    unittest.main()
