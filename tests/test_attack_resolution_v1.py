import unittest

from battle_module_v1 import (
    ATTACK_PHASE_ON_ATTACKED,
    AttackEvent,
    AttackReactionContext,
    BattleContext,
    BattleItem,
    BattleState,
    Effect,
    PlayerState,
    Trigger,
)
from item_factory_registry_v1 import (
    CooldownTrigger,
    MeleeAttackEffect,
    OnAttackedTrigger,
    PreventAttackDamageEffect,
    RemoveOpponentStaminaEffect,
    WoodenBuckler,
)


class SequenceRng:
    def __init__(self, random_values=(), randint_values=()):
        self.random_values = list(random_values)
        self.randint_values = list(randint_values)
        self.calls = []

    def random(self):
        self.calls.append("random")
        if not self.random_values:
            raise AssertionError("unexpected random call")
        return self.random_values.pop(0)

    def randint(self, minimum, maximum):
        self.calls.append("randint")
        if not self.randint_values:
            raise AssertionError("unexpected randint call")
        value = self.randint_values.pop(0)
        if not minimum <= value <= maximum:
            raise AssertionError("configured randint value is out of range")
        return value


class StaticTrigger(Trigger):
    def __init__(self, result=True):
        self.result = result
        self.calls = 0
        self.contexts = []

    def update(self, context):
        self.calls += 1
        self.contexts.append(context)
        return self.result


class MissingAttackPhaseTrigger(StaticTrigger):
    def __init__(self, result=True):
        super().__init__(result)
        self.phase_reads = 0

    def __getattr__(self, name):
        if name == "attack_phase":
            self.phase_reads += 1
            raise AttributeError(name)
        raise AttributeError(name)


class RecordingAttackTrigger(StaticTrigger):
    attack_phase = ATTACK_PHASE_ON_ATTACKED


class CountingAttackPhaseTrigger(StaticTrigger):
    def __init__(self, result=True):
        super().__init__(result)
        self.phase_reads = 0

    @property
    def attack_phase(self):
        self.phase_reads += 1
        return ATTACK_PHASE_ON_ATTACKED


class NoopEffect(Effect):
    def __init__(self, result=True):
        self.result = result
        self.calls = 0
        self.contexts = []

    def apply(self, context):
        self.calls += 1
        self.contexts.append(context)
        return self.result


class CallbackEffect(Effect):
    def __init__(self, callback):
        self.callback = callback
        self.calls = 0

    def apply(self, context):
        self.calls += 1
        return self.callback(context)


class ConfigurableItem(BattleItem):
    def __init__(
        self,
        trigger=None,
        effects=None,
        will_run_linked_items=False,
        decision=None,
        **kwargs,
    ):
        super().__init__(
            triggers=[trigger if trigger is not None else StaticTrigger()],
            effects=list(effects) if effects is not None else [NoopEffect()],
            **kwargs,
        )
        self.will_run_linked_items = will_run_linked_items
        self.decision = decision
        self.run_calls = 0
        self.contexts = []

    def run_own_effect(self, trigger_results, context):
        self.run_calls += 1
        self.contexts.append(context)
        if self.decision is not None:
            return self.decision(self, trigger_results, context)
        if not any(trigger_results):
            return False
        for effect in self.effects:
            effect.apply(context)
        return self.will_run_linked_items


class NestedAttackEffect(Effect):
    def __init__(self):
        self.outer_event = None
        self.nested_event = None

    def apply(self, context):
        self.outer_event = context.attack_event
        self.nested_event = AttackEvent(
            attacker=context.owner,
            defender=context.opponent,
            source_item=context.item,
            attack_types=("melee",),
            min_damage=1,
            max_damage=1,
            accuracy=100,
        )
        context.battle_state.resolve_attack(self.nested_event)

        prevented_damage = min(1, self.outer_event.pending_damage)
        self.outer_event.pending_damage -= prevented_damage
        self.outer_event.prevented_damage += prevented_damage
        return True


class CapturingBattleState(BattleState):
    def resolve_attack(self, event):
        self.captured_event = event
        self.captured_values = (
            event.hit,
            event.rolled_damage,
            event.pending_damage,
            event.is_resolved,
        )
        event.hit = False
        event.is_resolved = True
        return event


class AttackResolutionV1Test(unittest.TestCase):
    def make_battle(
        self,
        defender_items=(),
        rng=None,
        attacker_stamina=2.0,
        defender_stamina=2.0,
        defender_block=0,
    ):
        source = ConfigurableItem(
            item_key="source1",
            player_id=0,
            is_active_item=True,
        )
        attacker = PlayerState(
            player_id=0,
            health=20,
            stamina=attacker_stamina,
            max_stamina=5.0,
            items={"source1": source},
        )

        item_dict = {}
        for index, item in enumerate(defender_items, start=1):
            if item.item_key is None:
                item.item_key = f"defender{index}"
            item.player_id = 1
            item_dict[item.item_key] = item
        defender = PlayerState(
            player_id=1,
            health=20,
            block=defender_block,
            stamina=defender_stamina,
            max_stamina=5.0,
            items=item_dict,
        )

        battle_kwargs = {"players": [attacker, defender]}
        if rng is not None:
            battle_kwargs["rng"] = rng
        battle = BattleState(**battle_kwargs)
        return battle, attacker, defender, source

    def make_event(
        self,
        attacker,
        defender,
        source,
        min_damage=1,
        max_damage=3,
        accuracy=100,
        attack_types=("melee",),
    ):
        return AttackEvent(
            attacker=attacker,
            defender=defender,
            source_item=source,
            attack_types=attack_types,
            min_damage=min_damage,
            max_damage=max_damage,
            accuracy=accuracy,
        )

    def test_attack_event_starts_with_unresolved_result_fields(self):
        battle, attacker, defender, source = self.make_battle()

        event = self.make_event(attacker, defender, source)

        self.assertIsNone(event.hit)
        self.assertEqual(event.rolled_damage, 0)
        self.assertEqual(event.pending_damage, 0)
        self.assertEqual(event.prevented_damage, 0)
        self.assertEqual(event.block_damage, 0)
        self.assertEqual(event.health_damage, 0)
        self.assertFalse(event.is_resolved)
        self.assertIsNotNone(battle)

    def test_base_context_and_item_have_no_attack_fields(self):
        battle, _, _, source = self.make_battle()

        context = battle.build_context(source)

        self.assertIs(type(context), BattleContext)
        self.assertFalse(hasattr(context, "attack_phase"))
        self.assertFalse(hasattr(context, "attack_event"))
        self.assertFalse(hasattr(source, "attack_reaction_phases"))
        self.assertFalse(hasattr(source, "attack_phase"))
        self.assertFalse(hasattr(source, "attack_event"))

    def test_build_attack_reaction_context_returns_specialized_context(self):
        item = ConfigurableItem(trigger=RecordingAttackTrigger())
        battle, attacker, defender, source = self.make_battle([item])
        event = self.make_event(attacker, defender, source)

        context = battle.build_attack_reaction_context(
            item,
            ATTACK_PHASE_ON_ATTACKED,
            event,
        )

        self.assertIsInstance(context, AttackReactionContext)
        self.assertIs(context.owner, defender)
        self.assertIs(context.opponent, attacker)
        self.assertEqual(context.attack_phase, ATTACK_PHASE_ON_ATTACKED)
        self.assertIs(context.attack_event, event)

    def test_attack_reaction_context_for_item_preserves_subclass_and_event_reference(self):
        parent = ConfigurableItem(
            trigger=RecordingAttackTrigger(),
            item_key="parent1",
        )
        linked = ConfigurableItem(item_key="linked1")
        battle, attacker, defender, source = self.make_battle([parent, linked])
        event = self.make_event(attacker, defender, source)
        context = battle.build_attack_reaction_context(
            parent,
            ATTACK_PHASE_ON_ATTACKED,
            event,
        )

        linked_context = context.for_item(linked)

        self.assertIsInstance(linked_context, AttackReactionContext)
        self.assertIs(linked_context.attack_event, event)
        self.assertEqual(linked_context.attack_phase, ATTACK_PHASE_ON_ATTACKED)

    def test_resolve_attack_miss_does_not_roll_or_apply_damage(self):
        reaction = ConfigurableItem(trigger=RecordingAttackTrigger())
        rng = SequenceRng(random_values=[0.9])
        battle, attacker, defender, source = self.make_battle([reaction], rng=rng)
        event = self.make_event(attacker, defender, source, accuracy=50)

        battle.resolve_attack(event)

        self.assertFalse(event.hit)
        self.assertTrue(event.is_resolved)
        self.assertEqual(defender.health, 20)
        self.assertEqual(defender.block, 0)
        self.assertEqual(reaction.run_calls, 0)
        self.assertEqual(rng.calls, ["random"])

    def test_resolve_attack_hit_rolls_damage_then_consumes_block_then_health(self):
        rng = SequenceRng(random_values=[0.0], randint_values=[5])
        battle, attacker, defender, source = self.make_battle(
            rng=rng,
            defender_block=3,
        )
        event = self.make_event(attacker, defender, source, 5, 5)

        battle.resolve_attack(event)

        self.assertTrue(event.hit)
        self.assertEqual(event.rolled_damage, 5)
        self.assertEqual(event.pending_damage, 5)
        self.assertEqual(event.block_damage, 3)
        self.assertEqual(event.health_damage, 2)
        self.assertEqual(defender.block, 0)
        self.assertEqual(defender.health, 18)

    def test_resolve_attack_without_block_applies_all_pending_damage_to_health(self):
        rng = SequenceRng(random_values=[0.0], randint_values=[5])
        battle, attacker, defender, source = self.make_battle(rng=rng)
        event = self.make_event(attacker, defender, source, 5, 5)

        battle.resolve_attack(event)

        self.assertEqual(event.block_damage, 0)
        self.assertEqual(event.health_damage, 5)
        self.assertEqual(defender.health, 15)

    def test_resolve_attack_rejects_already_resolved_event(self):
        rng = SequenceRng(random_values=[0.0], randint_values=[2])
        battle, attacker, defender, source = self.make_battle(rng=rng)
        event = self.make_event(attacker, defender, source, 2, 2)
        battle.resolve_attack(event)
        health_after_first_resolution = defender.health

        with self.assertRaises(ValueError):
            battle.resolve_attack(event)

        self.assertEqual(defender.health, health_after_first_resolution)

    def test_resolve_attack_rejects_players_outside_battle(self):
        battle, _, defender, source = self.make_battle()
        outside_attacker = PlayerState(player_id=9, health=20)
        event = self.make_event(outside_attacker, defender, source)

        with self.assertRaises(ValueError):
            battle.resolve_attack(event)

    def test_melee_attack_effect_returns_false_on_miss(self):
        rng = SequenceRng(random_values=[0.9])
        battle, _, defender, source = self.make_battle(rng=rng)
        effect = MeleeAttackEffect(1, 3, 50)

        result = effect.apply(battle.build_context(source))

        self.assertFalse(result)
        self.assertEqual(defender.health, 20)

    def test_melee_attack_effect_returns_true_when_hit_damage_is_fully_prevented(self):
        blocker = ConfigurableItem(
            trigger=RecordingAttackTrigger(),
            effects=[PreventAttackDamageEffect(99)],
        )
        rng = SequenceRng(random_values=[0.0], randint_values=[5])
        battle, _, defender, source = self.make_battle([blocker], rng=rng)
        effect = MeleeAttackEffect(5, 5, 100)

        result = effect.apply(battle.build_context(source))

        self.assertTrue(result)
        self.assertEqual(defender.health, 20)

    def test_melee_attack_effect_does_not_directly_mutate_damage_before_resolver(self):
        source = ConfigurableItem(item_key="source1", player_id=0)
        attacker = PlayerState(player_id=0, health=20, items={"source1": source})
        defender = PlayerState(player_id=1, health=20)
        battle = CapturingBattleState(players=[attacker, defender])
        effect = MeleeAttackEffect(1, 3, 90)

        result = effect.apply(battle.build_context(source))

        self.assertFalse(result)
        self.assertEqual(battle.captured_values, (None, 0, 0, False))
        self.assertEqual(defender.health, 20)

    def test_melee_attack_effect_applies_attacker_empower_luck_and_blind(self):
        source = ConfigurableItem(item_key="source1", player_id=0)
        attacker = PlayerState(player_id=0, health=20, items={"source1": source})
        attacker.buffs.Empower = 2
        attacker.buffs.Luck = 3
        attacker.debuffs.Blind = 1
        defender = PlayerState(player_id=1, health=20)
        defender.debuffs.Blind = 99
        battle = CapturingBattleState(players=[attacker, defender])
        effect = MeleeAttackEffect(1, 3, 90)

        effect.apply(battle.build_context(source))

        self.assertEqual(battle.captured_event.min_damage, 3)
        self.assertEqual(battle.captured_event.max_damage, 5)
        self.assertEqual(battle.captured_event.accuracy, 100)

    def test_on_attacked_is_dispatched_only_after_hit(self):
        reaction = ConfigurableItem(trigger=RecordingAttackTrigger())
        rng = SequenceRng(random_values=[0.9, 0.0], randint_values=[2])
        battle, attacker, defender, source = self.make_battle([reaction], rng=rng)

        miss = self.make_event(attacker, defender, source, 2, 2, accuracy=50)
        hit = self.make_event(attacker, defender, source, 2, 2, accuracy=50)
        battle.resolve_attack(miss)
        battle.resolve_attack(hit)

        self.assertEqual(reaction.run_calls, 1)
        self.assertIs(reaction.contexts[0].attack_event, hit)

    def test_dispatch_passes_same_event_to_every_responder(self):
        first = ConfigurableItem(trigger=RecordingAttackTrigger())
        second = ConfigurableItem(trigger=RecordingAttackTrigger())
        rng = SequenceRng(random_values=[0.0], randint_values=[2])
        battle, attacker, defender, source = self.make_battle([first, second], rng=rng)
        event = self.make_event(attacker, defender, source, 2, 2)

        battle.resolve_attack(event)

        self.assertIs(first.contexts[0].attack_event, event)
        self.assertIs(second.contexts[0].attack_event, event)

    def test_dispatch_uses_defender_item_insertion_order(self):
        log = []

        def make_item(name):
            return ConfigurableItem(
                trigger=RecordingAttackTrigger(),
                effects=[CallbackEffect(lambda context: log.append(name) or True)],
            )

        items = [make_item("first"), make_item("second"), make_item("third")]
        rng = SequenceRng(random_values=[0.0], randint_values=[1])
        battle, attacker, defender, source = self.make_battle(items, rng=rng)
        event = self.make_event(attacker, defender, source, 1, 1)

        battle.resolve_attack(event)

        self.assertEqual(log, ["first", "second", "third"])

    def test_dispatch_skips_items_whose_triggers_have_no_attack_phase(self):
        cooldown = CooldownTrigger(cooldown_seconds=1.0)
        ordinary = ConfigurableItem(trigger=cooldown)
        reaction = ConfigurableItem(trigger=RecordingAttackTrigger())
        rng = SequenceRng(random_values=[0.0], randint_values=[1])
        battle, attacker, defender, source = self.make_battle(
            [ordinary, reaction],
            rng=rng,
        )
        event = self.make_event(attacker, defender, source, 1, 1)

        battle.resolve_attack(event)

        self.assertEqual(cooldown.cooldown_progress, 0.0)
        self.assertEqual(ordinary.run_calls, 0)
        self.assertEqual(reaction.run_calls, 1)

    def test_dispatch_continues_after_pending_damage_reaches_zero(self):
        first = ConfigurableItem(
            trigger=RecordingAttackTrigger(),
            effects=[PreventAttackDamageEffect(99)],
        )
        second = ConfigurableItem(trigger=RecordingAttackTrigger())
        rng = SequenceRng(random_values=[0.0], randint_values=[3])
        battle, attacker, defender, source = self.make_battle([first, second], rng=rng)
        event = self.make_event(attacker, defender, source, 3, 3)

        battle.resolve_attack(event)

        self.assertEqual(event.pending_damage, 0)
        self.assertEqual(second.run_calls, 1)

    def test_dispatch_ignores_item_link_decision_for_next_responder(self):
        first = ConfigurableItem(trigger=RecordingAttackTrigger())
        second = ConfigurableItem(trigger=RecordingAttackTrigger())
        rng = SequenceRng(random_values=[0.0], randint_values=[1])
        battle, attacker, defender, source = self.make_battle([first, second], rng=rng)
        event = self.make_event(attacker, defender, source, 1, 1)

        battle.resolve_attack(event)

        self.assertEqual(first.run_calls, 1)
        self.assertEqual(second.run_calls, 1)

    def test_attack_response_linked_item_receives_same_event(self):
        parent = ConfigurableItem(
            trigger=RecordingAttackTrigger(),
            will_run_linked_items=True,
            item_key="parent1",
        )
        linked = ConfigurableItem(
            trigger=StaticTrigger(),
            item_key="linked1",
        )
        parent.add_linked_item("linked1")
        rng = SequenceRng(random_values=[0.0], randint_values=[1])
        battle, attacker, defender, source = self.make_battle([parent, linked], rng=rng)
        event = self.make_event(attacker, defender, source, 1, 1)

        battle.resolve_attack(event)

        self.assertEqual(linked.run_calls, 1)
        self.assertIsInstance(linked.contexts[0], AttackReactionContext)
        self.assertIs(linked.contexts[0].attack_event, event)

    def test_on_attacked_trigger_rolls_for_matching_melee_attack(self):
        item = ConfigurableItem(trigger=RecordingAttackTrigger())
        rng = SequenceRng(random_values=[0.2])
        battle, attacker, defender, source = self.make_battle([item], rng=rng)
        event = self.make_event(attacker, defender, source)
        event.hit = True
        context = battle.build_attack_reaction_context(
            item,
            ATTACK_PHASE_ON_ATTACKED,
            event,
        )
        trigger = OnAttackedTrigger(("melee",), chance=0.3)

        result = trigger.update(context)

        self.assertTrue(result)
        self.assertEqual(rng.calls, ["random"])

    def test_on_attacked_trigger_handles_base_or_wrong_phase_context_without_rng(self):
        item = ConfigurableItem(trigger=RecordingAttackTrigger())
        rng = SequenceRng()
        battle, attacker, defender, source = self.make_battle([item], rng=rng)
        event = self.make_event(attacker, defender, source)
        event.hit = True
        trigger = OnAttackedTrigger(("melee",), chance=1.0)

        base_result = trigger.update(battle.build_context(item))
        wrong_phase_context = AttackReactionContext(
            battle,
            item,
            defender,
            attacker,
            "other_phase",
            event,
        )
        wrong_phase_result = trigger.update(wrong_phase_context)

        self.assertFalse(base_result)
        self.assertFalse(wrong_phase_result)
        self.assertEqual(rng.calls, [])

    def test_on_attacked_trigger_rejects_non_matching_attack_type_without_rng(self):
        item = ConfigurableItem(trigger=RecordingAttackTrigger())
        rng = SequenceRng()
        battle, attacker, defender, source = self.make_battle([item], rng=rng)
        event = self.make_event(
            attacker,
            defender,
            source,
            attack_types=("ranged",),
        )
        event.hit = True
        context = battle.build_attack_reaction_context(
            item,
            ATTACK_PHASE_ON_ATTACKED,
            event,
        )

        result = OnAttackedTrigger(("melee",), chance=1.0).update(context)

        self.assertFalse(result)
        self.assertEqual(rng.calls, [])

    def test_prevent_attack_damage_caps_at_pending_damage(self):
        item = ConfigurableItem(trigger=RecordingAttackTrigger())
        battle, attacker, defender, source = self.make_battle([item])
        event = self.make_event(attacker, defender, source)
        event.hit = True
        event.pending_damage = 5
        context = battle.build_attack_reaction_context(
            item,
            ATTACK_PHASE_ON_ATTACKED,
            event,
        )

        result = PreventAttackDamageEffect(7).apply(context)

        self.assertTrue(result)
        self.assertEqual(event.pending_damage, 0)
        self.assertEqual(event.prevented_damage, 5)

    def test_prevent_attack_damage_rejects_base_context_or_resolved_event(self):
        item = ConfigurableItem(trigger=RecordingAttackTrigger())
        battle, attacker, defender, source = self.make_battle([item])
        effect = PreventAttackDamageEffect(7)

        with self.assertRaises(ValueError):
            effect.apply(battle.build_context(item))

        event = self.make_event(attacker, defender, source)
        event.hit = True
        event.pending_damage = 5
        event.is_resolved = True
        context = AttackReactionContext(
            battle,
            item,
            defender,
            attacker,
            ATTACK_PHASE_ON_ATTACKED,
            event,
        )
        with self.assertRaises(ValueError):
            effect.apply(context)

    def test_remove_opponent_stamina_clamps_at_zero(self):
        item = ConfigurableItem(trigger=RecordingAttackTrigger())
        battle, attacker, _, _ = self.make_battle(
            [item],
            attacker_stamina=0.1,
        )
        context = battle.build_context(item)

        result = RemoveOpponentStaminaEffect(0.3).apply(context)

        self.assertTrue(result)
        self.assertEqual(attacker.stamina, 0.0)
        self.assertEqual(attacker.max_stamina, 5.0)

    def test_wooden_buckler_prevents_seven_and_removes_stamina(self):
        buckler = WoodenBuckler()
        rng = SequenceRng(random_values=[0.0, 0.0], randint_values=[10])
        battle, attacker, defender, source = self.make_battle(
            [buckler],
            rng=rng,
            attacker_stamina=1.0,
        )
        event = self.make_event(attacker, defender, source, 10, 10)

        battle.resolve_attack(event)

        self.assertEqual(event.prevented_damage, 7)
        self.assertEqual(event.pending_damage, 3)
        self.assertEqual(defender.health, 17)
        self.assertAlmostEqual(attacker.stamina, 0.7)

    def test_wooden_buckler_runs_linked_item_when_chance_succeeds(self):
        buckler = WoodenBuckler(item_key="buckler1")
        linked = ConfigurableItem(item_key="linked1")
        buckler.add_linked_item("linked1")
        rng = SequenceRng(random_values=[0.0, 0.0], randint_values=[5])
        battle, attacker, defender, source = self.make_battle(
            [buckler, linked],
            rng=rng,
        )
        event = self.make_event(attacker, defender, source, 5, 5)

        battle.resolve_attack(event)

        self.assertEqual(linked.run_calls, 1)
        self.assertIsInstance(linked.contexts[0], AttackReactionContext)
        self.assertIs(linked.contexts[0].attack_event, event)

    def test_wooden_buckler_still_removes_stamina_when_damage_is_zero(self):
        full_prevention = ConfigurableItem(
            trigger=RecordingAttackTrigger(),
            effects=[PreventAttackDamageEffect(99)],
        )
        buckler = WoodenBuckler()
        rng = SequenceRng(random_values=[0.0, 0.0], randint_values=[5])
        battle, attacker, defender, source = self.make_battle(
            [full_prevention, buckler],
            rng=rng,
            attacker_stamina=1.0,
        )
        event = self.make_event(attacker, defender, source, 5, 5)

        battle.resolve_attack(event)

        self.assertEqual(event.pending_damage, 0)
        self.assertEqual(defender.health, 20)
        self.assertAlmostEqual(attacker.stamina, 0.7)

    def test_wooden_buckler_does_nothing_when_chance_fails(self):
        buckler = WoodenBuckler(item_key="buckler1")
        linked = ConfigurableItem(item_key="linked1")
        buckler.add_linked_item("linked1")
        rng = SequenceRng(random_values=[0.0, 0.9], randint_values=[10])
        battle, attacker, defender, source = self.make_battle(
            [buckler, linked],
            rng=rng,
            attacker_stamina=1.0,
        )
        event = self.make_event(attacker, defender, source, 10, 10)

        battle.resolve_attack(event)

        self.assertEqual(event.prevented_damage, 0)
        self.assertEqual(defender.health, 10)
        self.assertEqual(attacker.stamina, 1.0)
        self.assertEqual(linked.run_calls, 0)

    def test_attack_rng_call_order_is_hit_damage_then_reactions(self):
        buckler = WoodenBuckler()
        rng = SequenceRng(random_values=[0.0, 0.0], randint_values=[5])
        battle, attacker, defender, source = self.make_battle([buckler], rng=rng)
        event = self.make_event(attacker, defender, source, 5, 5)

        battle.resolve_attack(event)

        self.assertEqual(rng.calls, ["random", "randint", "random"])

    def test_missed_attack_does_not_consume_damage_or_reaction_rng(self):
        buckler = WoodenBuckler()
        rng = SequenceRng(random_values=[0.9], randint_values=[5])
        battle, attacker, defender, source = self.make_battle([buckler], rng=rng)
        event = self.make_event(attacker, defender, source, 5, 5, accuracy=50)

        battle.resolve_attack(event)

        self.assertEqual(rng.calls, ["random"])
        self.assertEqual(rng.randint_values, [5])

    def test_battle_states_own_independent_rng_instances(self):
        first = BattleState()
        second = BattleState()

        self.assertIsNot(first.rng, second.rng)

    def test_nested_attack_uses_distinct_event_and_resumes_outer_event(self):
        nested_effect = NestedAttackEffect()
        reaction = ConfigurableItem(
            trigger=RecordingAttackTrigger(),
            effects=[nested_effect],
        )
        rng = SequenceRng(
            random_values=[0.0, 0.0],
            randint_values=[5, 1],
        )
        battle, attacker, defender, source = self.make_battle([reaction], rng=rng)
        outer_event = self.make_event(attacker, defender, source, 5, 5)

        battle.resolve_attack(outer_event)

        self.assertIs(nested_effect.outer_event, outer_event)
        self.assertIsNot(nested_effect.nested_event, outer_event)
        self.assertTrue(nested_effect.nested_event.is_resolved)
        self.assertTrue(outer_event.is_resolved)
        self.assertEqual(attacker.health, 19)
        self.assertEqual(defender.health, 16)
        self.assertEqual(outer_event.prevented_damage, 1)

    def test_nested_attack_never_reads_battle_state_current_attack(self):
        nested_effect = NestedAttackEffect()
        reaction = ConfigurableItem(
            trigger=RecordingAttackTrigger(),
            effects=[nested_effect],
        )
        rng = SequenceRng(
            random_values=[0.0, 0.0],
            randint_values=[2, 1],
        )
        battle, attacker, defender, source = self.make_battle([reaction], rng=rng)
        event = self.make_event(attacker, defender, source, 2, 2)

        battle.resolve_attack(event)

        self.assertFalse(hasattr(battle, "current_attack"))

    def test_first_reaction_item_lookup_scans_triggers_and_populates_cache(self):
        ordinary_trigger = MissingAttackPhaseTrigger()
        ordinary = ConfigurableItem(trigger=ordinary_trigger)
        first_trigger = CountingAttackPhaseTrigger()
        second_trigger = CountingAttackPhaseTrigger()
        first = ConfigurableItem(trigger=first_trigger)
        second = ConfigurableItem(trigger=second_trigger)
        battle, _, defender, _ = self.make_battle([ordinary, first, second])

        items = battle._get_attack_reaction_items(
            defender,
            ATTACK_PHASE_ON_ATTACKED,
        )

        self.assertEqual(items, (first, second))
        self.assertIs(
            items,
            battle._responder_item_cache[defender.player_id][
                ATTACK_PHASE_ON_ATTACKED
            ],
        )
        self.assertEqual(ordinary_trigger.phase_reads, 1)
        self.assertEqual(first_trigger.phase_reads, 1)
        self.assertEqual(second_trigger.phase_reads, 1)

    def test_second_reaction_item_lookup_does_not_read_attack_phase_again(self):
        trigger = CountingAttackPhaseTrigger()
        item = ConfigurableItem(trigger=trigger)
        battle, _, defender, _ = self.make_battle([item])

        first = battle._get_attack_reaction_items(
            defender,
            ATTACK_PHASE_ON_ATTACKED,
        )
        reads_after_first_lookup = trigger.phase_reads
        second = battle._get_attack_reaction_items(
            defender,
            ATTACK_PHASE_ON_ATTACKED,
        )

        self.assertIs(first, second)
        self.assertEqual(trigger.phase_reads, reads_after_first_lookup)

    def test_empty_reaction_item_lookup_is_cached(self):
        trigger = MissingAttackPhaseTrigger()
        item = ConfigurableItem(trigger=trigger)
        battle, _, defender, _ = self.make_battle([item])

        first = battle._get_attack_reaction_items(
            defender,
            ATTACK_PHASE_ON_ATTACKED,
        )
        reads_after_first_lookup = trigger.phase_reads
        second = battle._get_attack_reaction_items(
            defender,
            ATTACK_PHASE_ON_ATTACKED,
        )

        self.assertEqual(first, ())
        self.assertIs(first, second)
        self.assertEqual(trigger.phase_reads, reads_after_first_lookup)

    def test_reaction_item_cache_is_separate_for_each_responder(self):
        first_item = ConfigurableItem(
            trigger=RecordingAttackTrigger(),
            item_key="first1",
            player_id=0,
        )
        second_item = ConfigurableItem(
            trigger=RecordingAttackTrigger(),
            item_key="second1",
            player_id=1,
        )
        first_player = PlayerState(
            player_id=0,
            health=20,
            items={"first1": first_item},
        )
        second_player = PlayerState(
            player_id=1,
            health=20,
            items={"second1": second_item},
        )
        battle = BattleState(players=[first_player, second_player])

        first_items = battle._get_attack_reaction_items(
            first_player,
            ATTACK_PHASE_ON_ATTACKED,
        )
        second_items = battle._get_attack_reaction_items(
            second_player,
            ATTACK_PHASE_ON_ATTACKED,
        )

        self.assertEqual(first_items, (first_item,))
        self.assertEqual(second_items, (second_item,))
        self.assertIsNot(
            battle._responder_item_cache[0],
            battle._responder_item_cache[1],
        )

    def test_cached_reaction_items_preserve_responder_item_order(self):
        items = [
            ConfigurableItem(trigger=RecordingAttackTrigger())
            for _ in range(3)
        ]
        battle, _, defender, _ = self.make_battle(items)

        cached_items = battle._get_attack_reaction_items(
            defender,
            ATTACK_PHASE_ON_ATTACKED,
        )

        self.assertEqual(cached_items, tuple(items))

    def test_cached_items_reuse_list_but_dispatch_builds_fresh_context_per_attack(self):
        trigger = RecordingAttackTrigger()
        item = ConfigurableItem(trigger=trigger)
        battle, attacker, defender, source = self.make_battle([item])
        first_event = self.make_event(attacker, defender, source)
        second_event = self.make_event(attacker, defender, source)
        first_event.hit = True
        second_event.hit = True

        cached_before = battle._get_attack_reaction_items(
            defender,
            ATTACK_PHASE_ON_ATTACKED,
        )
        battle.dispatch_attack_reactions(
            ATTACK_PHASE_ON_ATTACKED,
            defender,
            first_event,
        )
        battle.dispatch_attack_reactions(
            ATTACK_PHASE_ON_ATTACKED,
            defender,
            second_event,
        )
        cached_after = battle._get_attack_reaction_items(
            defender,
            ATTACK_PHASE_ON_ATTACKED,
        )

        self.assertIs(cached_before, cached_after)
        self.assertIsNot(item.contexts[0], item.contexts[1])
        self.assertIs(item.contexts[0].attack_event, first_event)
        self.assertIs(item.contexts[1].attack_event, second_event)

    def test_battle_states_own_independent_reaction_item_caches(self):
        first_item = ConfigurableItem(trigger=RecordingAttackTrigger())
        second_item = ConfigurableItem(trigger=RecordingAttackTrigger())
        first_battle, _, first_defender, _ = self.make_battle([first_item])
        second_battle, _, _, _ = self.make_battle([second_item])

        first_battle._get_attack_reaction_items(
            first_defender,
            ATTACK_PHASE_ON_ATTACKED,
        )

        self.assertIsNot(
            first_battle._responder_item_cache,
            second_battle._responder_item_cache,
        )
        self.assertEqual(second_battle._responder_item_cache, {})


if __name__ == "__main__":
    unittest.main()
