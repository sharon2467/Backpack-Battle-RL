"""Source-based regressions for resolve_attack_remaining_fixes_spec.md."""
import random
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from battle_module_v1 import (
    BattleState, PlayerState, BalancedRngState, godot_round, make_attack_event,
    ATTACK_PHASE_CHARACTER_DAMAGED, ATTACK_PHASE_PRE_TAKE_DAMAGE,
    _BattleFinishedSignal, _start_timer, _stop_timer,
)
from item_factory_registry_v1 import WoodenSword
from item_triggers_v1 import OnAttackedTrigger


class DamagePipelineSpecTest(unittest.TestCase):
    def setUp(self):
        self.a = PlayerState(player_id=0, health=100, max_health=100)
        self.d = PlayerState(player_id=1, health=100, max_health=100)
        self.item = WoodenSword(item_key="sword", player_id=0)
        self.a.items["sword"] = self.item
        self.b = BattleState(players=[self.a, self.d], rng=random.Random(1))

    def event(self, damage=10, types=("melee",), item=True, **kwargs):
        return make_attack_event(
            attacker=self.a, defender=self.d,
            source_item=self.item if item else None,
            attack_types=types, min_damage=damage, max_damage=damage, **kwargs,
        )

    def listen(self, emitter, phase, callback, key="listener", owner=1):
        listener = SimpleNamespace(item_key=key, player_id=owner,
                                   activate_item=lambda ctx, idx: callback(ctx))
        self.b.connect(emitter, phase, (listener, 0))
        return listener

    def test_rounding_and_critical_integer_truncation(self):
        self.assertEqual([godot_round(x) for x in (2.5, -2.5, 2.49)], [3, -3, 2])
        e = self.event(3)
        e.crit_chance, e.crit_multiplier = 100, 1.5
        self.b.resolve_attack(e)
        self.assertEqual(e.pending_damage, 4)

    def test_probability_crit_consumes_both_existing_tokens(self):
        self.item.crit_tokens = self.a.crit_tokens = 3
        e = self.event()
        e.crit_chance = 100
        self.b.resolve_attack(e)
        self.assertTrue(e.crit)
        self.assertEqual((self.item.crit_tokens, self.a.crit_tokens), (2, 2))

    def test_zero_tokens_do_not_force_crit_or_go_negative(self):
        e = self.b.resolve_attack(self.event())
        self.assertFalse(e.crit)
        self.assertEqual((self.item.crit_tokens, self.a.crit_tokens), (0, 0))

    def test_resistance_probability_precedes_resistance_stack(self):
        self.d.crit_resist_stacks = 1
        self.d.crit_resistance = 100
        e = self.event(); e.crit_chance = 100
        self.b.resolve_attack(e)
        self.assertFalse(e.crit)
        self.assertEqual(self.d.crit_resist_stacks, 1)
        self.d.crit_resistance = 0
        e = self.event(); e.crit_chance = 100
        self.b.resolve_attack(e)
        self.assertFalse(e.crit)
        self.assertEqual(self.d.crit_resist_stacks, 0)

    def test_no_item_can_crit_and_ignores_weapon_bonuses(self):
        self.a.crit_tokens = 1
        self.a.buffs.Empower = 20
        self.a.typed_damage_factors["spikes"] = 5
        e = self.b.resolve_attack(self.event(3, ("spikes",), item=False))
        self.assertEqual(e.pending_damage, 6)
        self.assertEqual(self.a.crit_tokens, 0)

    def test_cannot_miss_does_not_consume_dodge_and_no_block_flag_works(self):
        self.d.dodge_stacks = 1
        self.d.block = 20
        e = self.b.resolve_attack(self.event(5, flag_overrides={
            "can_miss": False, "can_be_blocked": False,
        }))
        self.assertTrue(e.hit)
        self.assertEqual((self.d.dodge_stacks, self.d.block, self.d.health), (1, 20, 95))
        e = self.b.resolve_attack(self.event(5))
        self.assertFalse(e.hit)
        self.assertEqual(self.d.dodge_stacks, 0)

    def test_default_flags_and_explicit_effect_spikes(self):
        self.d.buffs.Spikes = 4
        self.a.melee_spikes_limit = 0
        self.b.resolve_attack(self.event(12, ("effect",)))
        self.assertEqual(self.a.health, 100)
        e = self.event(12, ("effect",), flag_overrides={
            "can_be_spiked": True, "can_be_vampiric": True,
        })
        self.a.buffs.Vampirism = 20
        self.b.resolve_attack(e)
        self.assertEqual(self.a.health, 96)  # direct effect path has no Vampirism
        self.assertEqual(self.b.log[-1]["data"]["trigger_log_sequence"], e.log_handle.sequence)

    def test_spikes_and_vampirism_limits_use_correct_players(self):
        self.d.buffs.Spikes = 50
        self.d.ranged_spikes_limit = 0.5
        self.a.ranged_spikes_limit = 0
        self.a.ranged_vampirism_limit = 0.25
        self.a.buffs.Vampirism = 50
        self.b.resolve_attack(self.event(10, ("melee", "ranged")))
        self.assertEqual(self.a.health, 98)  # 5 reflected, round(2.5)=3 healed

    def test_fully_blocked_damage_still_reflects_and_heals(self):
        self.d.block = 10
        self.d.buffs.Spikes = 4
        self.a.buffs.Vampirism = 2
        e = self.b.resolve_attack(self.event())
        self.assertEqual((e.health_damage, self.d.health, self.a.health), (0, 100, 98))

    def test_spikes_cannot_chain_and_can_consume_crit_token(self):
        self.a.buffs.Spikes = self.d.buffs.Spikes = 3
        self.d.crit_tokens = 1
        self.b.resolve_attack(self.event())
        self.assertEqual(self.a.health, 94)
        self.assertEqual(self.d.crit_tokens, 0)
        self.assertEqual(len(self.b.log), 2)

    def test_vampirism_rounds_before_healing_efficiency(self):
        self.b.commit_health_reduction(self.a, 0, 20)
        self.a.buffs.Vampirism = 10
        self.a.melee_vampirism_limit = 0.3
        self.a.healing_efficiency = 0.6
        self.b.resolve_attack(self.event(5))
        self.assertEqual(self.a.health, 81)  # round(1.5)=2; round(2*.6)=1

    def test_damage_multipliers_round_once_and_empower_only_weapon_attack(self):
        self.a.buffs.Empower = 1
        self.a.typed_damage_factors["melee"] = 0.25
        self.item.damage_multiplier = 1.5
        e = self.b.resolve_attack(self.event(1))
        self.assertEqual(e.pending_damage, 4)  # round(2*1.25*1.5)
        self.assertEqual(self.b.resolve_attack(self.event(1, ("effect",))).pending_damage, 1)
        self.item.damage_multiplier = -1
        self.assertEqual(self.b.resolve_attack(self.event()).pending_damage, 0)

    def test_empower_uses_base_weapon_damage_even_when_current_damage_is_zero(self):
        self.a.buffs.Empower = 2
        self.assertEqual(self.b.resolve_attack(self.event(0)).pending_damage, 2)

    def test_poison_fatigue_and_resistance_use_common_pipeline(self):
        self.d.damage_resistance = 50
        self.d.damage_reduction = 20
        self.d.debuffs.Poison = 5
        self.assertEqual(self.b._apply_poison_tick(self.d), 3)
        self.d.bonus_fatigue_damage = 4
        self.assertEqual(self.b.inflict_fatigue(self.d, nightfall=False), 1)
        self.assertEqual(self.d.health, 94)
        self.assertEqual(self.d.fatigue_damage, 1)
        self.d.invulnerable = True
        self.assertEqual(self.b._apply_poison_tick(self.d), 0)

    def test_unhealing_at_full_health_and_negative_healing_efficiency(self):
        self.a.unhealing_amount = 0.5
        self.a.typed_damage_factors["unhealing"] = 1
        self.assertEqual(self.b.heal(self.a, 3), 0)
        self.assertEqual(self.d.health, 97)
        self.assertEqual(self.b.log[1]["data"]["trigger_log_sequence"], 0)
        self.a.healing_efficiency = -1
        self.assertEqual(self.b.heal(self.a, 3), 0)
        self.assertEqual(self.d.health, 97)

    def test_healing_context_and_overheal_notifications(self):
        seen = []
        self.listen(self.a, "character_healed", lambda c: seen.append((c.amount, c.overheal)))
        self.listen(self.a, "character_overhealed", lambda c: seen.append(c.log_handle.sequence))
        self.b.heal(self.a, 2.5)
        self.assertEqual(seen, [(3, 3), 0])

    def test_lethal_damage_returns_and_locks_winner_before_spikes_and_heal(self):
        self.d.buffs.Spikes = 100
        self.a.buffs.Vampirism = 100
        e = self.b.resolve_attack(self.event(100))
        self.assertTrue(e.is_resolved)
        self.assertTrue(self.a.is_dead)  # reflected lethal damage still runs
        self.assertEqual(self.a.health, 100)  # healing is direct code, not revival
        self.assertEqual(self.b.winner, 0)
        later = self.b.resolve_attack(self.event(1))
        self.assertFalse(later.hit)
        self.assertIsNone(later.log_handle)
        with self.assertRaises(_BattleFinishedSignal):
            self.b.stop_if_battle_ended()

    def test_death_is_after_callbacks_and_healing_can_prevent_it(self):
        def rescue(ctx):
            self.assertFalse(self.d.is_dead)
            self.assertIsNone(self.b.winner)
            self.b.heal(self.d, 5)
        self.listen(self.d, ATTACK_PHASE_CHARACTER_DAMAGED, rescue)
        self.b.resolve_attack(self.event(100))
        self.assertEqual(self.d.health, 5)
        self.assertFalse(self.d.is_dead)
        self.assertIsNone(self.b.winner)

    def test_ongoing_listener_finishes_but_next_listener_does_not_start(self):
        seen = []
        def kill(ctx):
            self.b.resolve_attack(self.event(100, ("effect",), item=False))
            seen.append("continued")
        self.listen(self.a, "custom", kill, key="first")
        self.listen(self.a, "custom", lambda ctx: seen.append("next"), key="second")
        self.b.emit_signal(self.a, "custom", self.b.build_context(self.item))
        self.assertEqual(seen, ["continued"])

    def test_top_level_item_finishes_then_next_item_is_skipped(self):
        self.b.prepareItems()
        seen = []
        def activate(ctx):
            self.b.resolve_attack(self.event(100))
            self.item.emit_activation(ctx)  # no post-end activation log
            seen.append("tail")
        first = SimpleNamespace(player_id=0, activate_item=activate)
        second = SimpleNamespace(player_id=0, activate_item=lambda ctx: seen.append("next"))
        # emit_activation requires the source item's own context.
        first.activate_item = lambda ctx: activate(self.b.build_context(self.item))
        self.b.active_items = [first, second]
        self.assertEqual(self.b.step(), 0)
        self.assertEqual(seen, ["tail"])
        self.assertEqual(self.b.frame, 1)
        self.assertNotIn("item_activation", [x["data"]["action"] for x in self.b.log])
        before = self.a.stamina
        self.b.step()
        self.assertEqual(self.a.stamina, before)

    def test_fatigue_stops_between_players(self):
        self.b.prepareItems()
        self.b.start_combat()
        self.b.commit_health_reduction(self.d, 0, 99)
        self.b.frame_delta = 1
        _stop_timer(self.b.fatigue_start_timer)
        _start_timer(self.b.fatigue_tick_timer, 0.5)
        self.b.step()
        self.assertEqual((self.d.fatigue_damage, self.a.fatigue_damage), (1, 0))

    def test_regeneration_unhealing_stops_following_system_tick(self):
        self.b.prepareItems()
        self.b.start_combat()
        self.b.commit_health_reduction(self.a, 0, 99)
        self.d.buffs.Regeneration = 2
        self.d.unhealing_amount = 1
        self.d.debuffs.Poison = 5
        _start_timer(self.d.status_tick_timer, 0.5)
        self.b.frame_delta = 1
        self.b.step()
        self.assertEqual(self.b.winner, 1)
        self.assertEqual(self.d.health, 100)
        self.assertNotIn("poison_damage", [x["data"]["action"] for x in self.b.log])

    def test_first_death_snapshot_both_zero_uses_player_win(self):
        self.b.commit_health_reduction(self.a, 0, 100)
        self.b.commit_health_reduction(self.d, 0, 100)
        self.b.check_battle_end()
        self.assertIsNone(self.b.winner)
        self.a.is_dead = True
        self.b.check_battle_end()
        self.assertEqual(self.b.winner, 0)

    def test_trigger_items_flag_is_enforced(self):
        trigger = OnAttackedTrigger(("melee",), 1)
        e = self.event(flag_overrides={"can_activate_item": False})
        e.hit = True
        ctx = self.b.build_attack_reaction_context(self.item, ATTACK_PHASE_PRE_TAKE_DAMAGE, e)
        self.assertFalse(trigger.update(ctx))

    def test_balanced_rng_source_trace_and_boundary_consumption(self):
        state = BalancedRngState()
        rng = Mock(); rng.random.side_effect = [0.8, 0.8, 0.4, 0.1]
        self.assertEqual([state.roll_percent(50, rng) for _ in range(4)],
                         [False, False, True, True])
        self.assertEqual((state.expected_wins, state.wins, state.last_result), (2, 2, True))
        self.assertFalse(state.roll_percent(0, rng))
        self.assertTrue(state.roll_percent(100, rng))
        self.assertEqual(rng.random.call_count, 4)
        state.reset()
        self.assertEqual((state.expected_wins, state.wins, state.last_result), (0, 0, False))

    def test_balanced_range_source_trace(self):
        rng = Mock(); rng.randint.side_effect = [5, 5, 1, 1, 1, 1]
        self.assertEqual([self.item.roll_damage(1, 5, rng) for _ in range(6)],
                         [5, 3, 1, 1, 3, 3])
        self.assertEqual(self.item.damage_range_acc, -2)

    def test_prepare_resets_each_rng_and_keeps_player_states_independent(self):
        self.a.accuracy_rng.expected_wins = 9
        self.a.crit_rng.wins = 3
        self.d.crit_resistance_rng.last_result = True
        self.item.damage_range_acc = 5
        self.b.prepareItems()
        self.assertEqual(self.a.accuracy_rng.expected_wins, 0)
        self.assertEqual(self.a.crit_rng.wins, 0)
        self.assertFalse(self.d.crit_resistance_rng.last_result)
        self.assertEqual(self.item.damage_range_acc, 0)
        self.assertIsNot(self.a.accuracy_rng, self.d.accuracy_rng)


if __name__ == "__main__":
    unittest.main()
