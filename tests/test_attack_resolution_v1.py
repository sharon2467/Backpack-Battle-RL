import unittest
from unittest.mock import Mock

from battle_module_v1 import (
    ATTACK_PHASE_ATTACKED,
    ATTACK_PHASE_CHARACTER_ATTACKED,
    ATTACK_PHASE_CHARACTER_DAMAGED,
    ATTACK_PHASE_PRE_DEAL_DAMAGE_EARLY,
    ATTACK_PHASE_PRE_DEAL_DAMAGE_LATE,
    ATTACK_PHASE_PRE_TAKE_DAMAGE,
    ATTACK_PHASE_PRE_TAKE_DAMAGE_LATE,
    SUPPORTED_ATTACK_REACTION_PHASES,
    AttackEvent,
    make_attack_event,
    AttackReactionContext,
    BattleContext,
    BattleState,
    PlayerState,
    _BattleFinishedSignal,
)
from item_effects_v1 import (
    AttackEffect,
    Effect,
    PreventAttackDamageEffect,
    RemoveOpponentStaminaEffect,
)
from item_factory_registry_v1 import (
    BattleItem,
    Broom,
    Pan,
    Shortbow,
    Stone,
    Weapon,
    WoodenBuckler,
    WoodenSword,
)
from item_triggers_v1 import (
    AttackMissTrigger,
    CooldownTrigger,
    OnAttackedTrigger,
    Trigger,
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


class RecordingAttackTrigger(StaticTrigger):
    attack_phase = ATTACK_PHASE_PRE_TAKE_DAMAGE

    def connect_bus(self, context):
        context.battle_state.connect(
            context.owner, self.attack_phase, (self.item, self.idx),
        )


class RecordingAttackMissTrigger(AttackMissTrigger):
    pass


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
        decision=None,
        **kwargs,
    ):
        super().__init__(
            triggers=[trigger if trigger is not None else StaticTrigger()],
            effects=list(effects) if effects is not None else [NoopEffect()],
            **kwargs,
        )
        self.decision = decision
        self.run_calls = 0
        self.contexts = []

    def run_effect(self, trigger_results, context):
        self.run_calls += 1
        self.contexts.append(context)
        if self.decision is not None:
            self.decision(self, trigger_results, context)
            return
        if not any(trigger_results):
            return
        for effect in self.effects:
            effect.apply(context)


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
        self.outer_event.prevented_damage += prevented_damage
        return True


class RecordingStageTrigger(StaticTrigger):
    def __init__(self, emitter, attack_phase):
        super().__init__()
        self.emitter = emitter
        self.attack_phase = attack_phase

    def connect_bus(self, context):
        context.battle_state.connect(
            self.emitter, self.attack_phase, (self.item, self.idx),
        )

    def update(self, context):
        if not isinstance(context, AttackReactionContext):
            return False
        if context.attack_phase != self.attack_phase:
            return False
        return super().update(context)


class RecordingWeapon(Weapon):
    item_types = ("Weapon",)

    def __init__(self, observed, early_action=None, **kwargs):
        super().__init__(triggers=[StaticTrigger()], effects=[NoopEffect()], **kwargs)
        self.observed = observed
        self.early_action = early_action

    def onPreDealDamage_early(self, context):
        self.observed.append((
            "early_hook", context, context.attack_event.is_resolved,
            context.attack_event.defender.health, context.attack_event.attacker.health,
        ))
        if self.early_action is not None:
            self.early_action(context)

    def onPreDealDamage_late(self, context):
        self.observed.append((
            "late_hook", context, context.attack_event.is_resolved,
            context.attack_event.defender.health, context.attack_event.attacker.health,
        ))

    def onDealtDamage(self, context):
        self.observed.append((
            "dealt_hook", context, context.attack_event.is_resolved,
            context.attack_event.defender.health, context.attack_event.attacker.health,
        ))


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
        attacker_health=20,
        attacker_max_health=0,
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
            health=attacker_health,
            max_health=attacker_max_health,
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
        battle.prepareItems()
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
        return make_attack_event(
            attacker=attacker,
            defender=defender,
            source_item=source,
            attack_types=attack_types,
            min_damage=min_damage,
            max_damage=max_damage,
            accuracy=accuracy,
        )

    def make_stage_battle(
        self, *, hit_roll=0.0, accuracy=100, attacker_health=20, early_action=None,
        attack_types=("melee",),
    ):
        observed = []
        source = RecordingWeapon(
            observed, early_action, item_key="source1", player_id=0,
        )
        attacker = PlayerState(
            player_id=0, health=attacker_health, max_health=20, items={"source1": source},
        )
        defender = PlayerState(player_id=1, health=20, max_health=20)
        stages = (
            (source, ATTACK_PHASE_PRE_DEAL_DAMAGE_EARLY),
            (defender, ATTACK_PHASE_PRE_TAKE_DAMAGE),
            (source, ATTACK_PHASE_PRE_DEAL_DAMAGE_LATE),
            (defender, ATTACK_PHASE_PRE_TAKE_DAMAGE_LATE),
            (defender, ATTACK_PHASE_CHARACTER_ATTACKED),
            (defender, ATTACK_PHASE_CHARACTER_DAMAGED),
            (source, ATTACK_PHASE_ATTACKED),
        )
        for index, (emitter, phase) in enumerate(stages):
            listener = ConfigurableItem(
                item_key=f"listener{index}", player_id=1,
                trigger=RecordingStageTrigger(emitter, phase),
                effects=[CallbackEffect(
                    lambda context, phase=phase: observed.append((
                        phase, context, context.attack_event.is_resolved,
                        context.attack_event.defender.health,
                        context.attack_event.attacker.health,
                    )) or True
                )],
            )
            defender.items[listener.item_key] = listener
        battle = BattleState(
            players=[attacker, defender],
            rng=SequenceRng(random_values=[hit_roll], randint_values=[5]),
        )
        battle.prepareItems()
        event = self.make_event(
            attacker, defender, source, 5, 5, accuracy=accuracy,
            attack_types=attack_types,
        )
        return battle, event, observed

    def test_attack_stages_use_correct_emitters_order_and_shared_event(self):
        battle, initial_event, observed = self.make_stage_battle(attacker_health=10)
        battle.rng.randint_values.append(1)
        initial_event.attacker.buffs.Vampirism = 2
        initial_event.defender.buffs.Spikes = 1

        hit = AttackEffect(5, 5, 100).apply(
            battle.build_context(initial_event.source_item), "melee",
        )

        self.assertTrue(hit)
        self.assertEqual([entry[0] for entry in observed], [
            ATTACK_PHASE_PRE_DEAL_DAMAGE_EARLY, "early_hook",
            ATTACK_PHASE_PRE_TAKE_DAMAGE,
            ATTACK_PHASE_PRE_DEAL_DAMAGE_LATE, "late_hook",
            ATTACK_PHASE_PRE_TAKE_DAMAGE_LATE,
            ATTACK_PHASE_CHARACTER_ATTACKED, ATTACK_PHASE_CHARACTER_DAMAGED,
            "dealt_hook", ATTACK_PHASE_ATTACKED,
        ])
        event = observed[0][1].attack_event
        self.assertTrue(event.is_resolved)
        self.assertEqual(event.defender.health, 15)
        for label, context, resolved, health, attacker_health in observed:
            self.assertIs(context.attack_event, event)
            self.assertIsInstance(context, AttackReactionContext)
            if label.endswith("_hook"):
                self.assertIs(context.item, event.source_item)
                self.assertIs(context.owner, event.attacker)
                self.assertIs(context.opponent, event.defender)
            else:
                self.assertIs(context.owner, event.defender)
                self.assertIs(context.opponent, event.attacker)
                self.assertEqual(context.attack_phase, label)
            if label in (
                ATTACK_PHASE_CHARACTER_ATTACKED, ATTACK_PHASE_CHARACTER_DAMAGED,
                "dealt_hook", ATTACK_PHASE_ATTACKED,
            ):
                self.assertTrue(resolved)
                self.assertEqual(health, 15)
            else:
                self.assertFalse(resolved)
                self.assertEqual(health, 20)
        self.assertEqual(observed[-2][4], 10)
        self.assertEqual(observed[-1][4], 11)

    def test_miss_completes_post_signals_without_damage_roll(self):
        battle, event, observed = self.make_stage_battle(hit_roll=0.9, accuracy=50)

        result = battle.resolve_attack(event)

        self.assertIs(result, event)
        self.assertFalse(event.hit)
        self.assertTrue(event.is_resolved)
        self.assertEqual(event.health_damage, 0)
        self.assertEqual(event.defender.health, 20)
        self.assertEqual(battle.rng.calls, ["random"])
        self.assertEqual([entry[0] for entry in observed], [
            ATTACK_PHASE_PRE_DEAL_DAMAGE_EARLY, "early_hook",
            ATTACK_PHASE_CHARACTER_ATTACKED, ATTACK_PHASE_CHARACTER_DAMAGED,
            "dealt_hook", ATTACK_PHASE_ATTACKED,
        ])
        self.assertEqual(len(battle.log), 1)
        self.assertFalse(battle.log[0]["data"]["hit"])

    def test_early_hook_can_turn_miss_into_hit_and_preserves_added_damage(self):
        battle, event, observed = self.make_stage_battle(
            hit_roll=0.9, accuracy=50,
            early_action=lambda context: (
                setattr(context.attack_event, "hit", True),
                setattr(context.attack_event, "pending_damage", 2),
            ),
        )

        battle.resolve_attack(event)

        self.assertTrue(event.hit)
        self.assertTrue(event.is_resolved)
        self.assertEqual(event.rolled_damage, 5)
        self.assertEqual(event.pending_damage, 7)
        self.assertEqual(event.health_damage, 7)
        self.assertEqual(event.defender.health, 13)
        self.assertNotIn("on_attack_missed", [entry[0] for entry in observed])

    def test_effect_damage_skips_weapon_hooks_and_source_signals(self):
        battle, event, observed = self.make_stage_battle(attack_types=("effect",))

        battle.resolve_attack(event)

        self.assertEqual([entry[0] for entry in observed], [
            ATTACK_PHASE_PRE_TAKE_DAMAGE, ATTACK_PHASE_PRE_TAKE_DAMAGE_LATE,
            ATTACK_PHASE_CHARACTER_ATTACKED, ATTACK_PHASE_CHARACTER_DAMAGED,
        ])
        self.assertTrue(event.is_resolved)
        self.assertEqual(event.health_damage, 5)

    def test_registered_weapons_inherit_default_hooks(self):
        for item_type in (Broom, WoodenSword, Shortbow, Stone, Pan):
            with self.subTest(item_type=item_type):
                item = item_type(item_key="weapon1", player_id=0)
                self.assertIsInstance(item, Weapon)
                attacker = PlayerState(
                    player_id=0, health=20, items={"weapon1": item},
                )
                defender = PlayerState(player_id=1, health=20)
                battle = BattleState(
                    players=[attacker, defender],
                    rng=SequenceRng(random_values=[0.0], randint_values=[5]),
                )
                battle.prepareItems()

                hit = AttackEffect(5, 5, 100).apply(
                    battle.build_context(item), item.icon_types[0],
                )

                self.assertTrue(hit)
                self.assertEqual(defender.health, 15)

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
            ATTACK_PHASE_PRE_TAKE_DAMAGE,
            event,
        )

        self.assertIsInstance(context, AttackReactionContext)
        self.assertIs(context.owner, attacker)
        self.assertIs(context.opponent, defender)
        self.assertEqual(context.attack_phase, ATTACK_PHASE_PRE_TAKE_DAMAGE)
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
            ATTACK_PHASE_PRE_TAKE_DAMAGE,
            event,
        )

        linked_context = context.for_item(linked)

        self.assertIsInstance(linked_context, AttackReactionContext)
        self.assertIs(linked_context.attack_event, event)
        self.assertEqual(linked_context.attack_phase, ATTACK_PHASE_PRE_TAKE_DAMAGE)

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

    def test_supported_phases_exclude_removed_miss_stage(self):
        self.assertNotIn("on_attack_missed", SUPPORTED_ATTACK_REACTION_PHASES)
        self.assertEqual(len(SUPPORTED_ATTACK_REACTION_PHASES), 7)
        battle, attacker, defender, source = self.make_battle()
        with self.assertRaises(ValueError):
            battle.build_attack_reaction_context(
                source, "on_attack_missed", self.make_event(attacker, defender, source),
            )

    def test_miss_is_observed_on_character_attacked_after_resolution(
        self,
    ):
        observed = []
        reaction = ConfigurableItem(
            trigger=AttackMissTrigger(),
            effects=[
                CallbackEffect(
                    lambda context: observed.append(
                        (
                            context.attack_event,
                            context.attack_event.hit,
                            context.attack_event.is_resolved,
                        )
                    )
                    or True
                ),
            ],
        )
        rng = SequenceRng(random_values=[0.9])
        battle, attacker, defender, source = self.make_battle(
            [reaction],
            rng=rng,
        )
        event = self.make_event(
            attacker,
            defender,
            source,
            accuracy=50,
        )

        battle.resolve_attack(event)

        self.assertEqual(observed, [(event, False, True)])
        self.assertTrue(event.is_resolved)

    def test_attack_miss_is_dispatched_only_to_defender(self):
        attacker_reaction = ConfigurableItem(
            trigger=AttackMissTrigger(),
            item_key="attacker_miss1",
            player_id=0,
        )
        defender_reaction = ConfigurableItem(
            trigger=AttackMissTrigger(),
        )
        rng = SequenceRng(random_values=[0.9])
        battle, attacker, defender, source = self.make_battle(
            [defender_reaction],
            rng=rng,
        )
        attacker.items[attacker_reaction.item_key] = attacker_reaction
        attacker_reaction.onPrepare(battle.build_context(attacker_reaction))
        event = self.make_event(
            attacker,
            defender,
            source,
            accuracy=50,
        )

        battle.resolve_attack(event)

        self.assertEqual(attacker_reaction.run_calls, 0)
        self.assertEqual(defender_reaction.run_calls, 1)

    def test_attack_miss_dispatch_does_not_roll_or_apply_damage(self):
        reaction = ConfigurableItem(trigger=AttackMissTrigger())
        rng = SequenceRng(
            random_values=[0.9],
            randint_values=[5],
        )
        battle, attacker, defender, source = self.make_battle(
            [reaction],
            rng=rng,
            defender_block=3,
        )
        event = self.make_event(
            attacker,
            defender,
            source,
            min_damage=5,
            max_damage=5,
            accuracy=50,
        )

        battle.resolve_attack(event)

        self.assertEqual(reaction.run_calls, 1)
        self.assertEqual(rng.calls, ["random"])
        self.assertEqual(rng.randint_values, [5])
        self.assertEqual(event.rolled_damage, 0)
        self.assertEqual(event.pending_damage, 0)
        self.assertEqual(defender.block, 3)
        self.assertEqual(defender.health, 20)

    def test_attack_bus_keeps_hit_and_miss_listeners_separate(self):
        hit_item = ConfigurableItem(trigger=RecordingAttackTrigger())
        miss_item = ConfigurableItem(trigger=RecordingAttackMissTrigger())
        rng = SequenceRng(random_values=[0.9, 0.0], randint_values=[1])
        battle, attacker, defender, source = self.make_battle(
            [hit_item, miss_item], rng=rng,
        )
        miss = self.make_event(attacker, defender, source, accuracy=50)
        hit = self.make_event(attacker, defender, source, 1, 1)
        battle.resolve_attack(miss)
        battle.resolve_attack(hit)
        self.assertEqual(hit_item.run_calls, 1)
        self.assertEqual(miss_item.run_calls, 2)
        self.assertEqual(miss_item.effects[0].calls, 1)
        self.assertIs(hit_item.contexts[0].attack_event, hit)
        self.assertIs(miss_item.contexts[0].attack_event, miss)

    def test_attack_miss_trigger_accepts_matching_context_without_rng(self):
        item = ConfigurableItem(trigger=AttackMissTrigger())
        rng = SequenceRng()
        battle, attacker, defender, source = self.make_battle(
            [item],
            rng=rng,
        )
        event = self.make_event(attacker, defender, source)
        event.hit = False
        context = battle.build_attack_reaction_context(
            item,
            ATTACK_PHASE_CHARACTER_ATTACKED,
            event,
        )

        result = item.triggers[0].update(context)

        self.assertTrue(result)
        self.assertEqual(rng.calls, [])

    def test_attack_miss_trigger_rejects_base_wrong_phase_and_hit_context(
        self,
    ):
        item = ConfigurableItem(trigger=AttackMissTrigger())
        rng = SequenceRng()
        battle, attacker, defender, source = self.make_battle(
            [item],
            rng=rng,
        )
        event = self.make_event(attacker, defender, source)
        event.hit = False
        wrong_phase_context = AttackReactionContext(
            battle,
            item,
            defender,
            attacker,
            ATTACK_PHASE_PRE_TAKE_DAMAGE,
            event,
        )

        self.assertFalse(
            item.triggers[0].update(battle.build_context(item))
        )
        self.assertFalse(item.triggers[0].update(wrong_phase_context))

        event.hit = True
        hit_context = battle.build_attack_reaction_context(
            item,
            ATTACK_PHASE_CHARACTER_ATTACKED,
            event,
        )
        self.assertFalse(item.triggers[0].update(hit_context))
        self.assertEqual(rng.calls, [])

    def test_existing_on_attacked_item_does_not_run_on_attack_miss(self):
        buckler = WoodenBuckler()
        rng = SequenceRng(random_values=[0.9])
        battle, attacker, defender, source = self.make_battle(
            [buckler],
            rng=rng,
            attacker_stamina=1.0,
        )
        event = self.make_event(
            attacker,
            defender,
            source,
            accuracy=50,
        )

        battle.resolve_attack(event)

        self.assertEqual(rng.calls, ["random"])
        self.assertEqual(attacker.stamina, 1.0)
        self.assertEqual(defender.health, 20)

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
        effect = AttackEffect(1, 3, 50)

        result = effect.apply(battle.build_context(source), "melee")

        self.assertFalse(result)
        self.assertEqual(defender.health, 20)

    def test_melee_attack_effect_returns_true_when_hit_damage_is_fully_prevented(self):
        blocker = ConfigurableItem(
            trigger=RecordingAttackTrigger(),
            effects=[PreventAttackDamageEffect(99)],
        )
        rng = SequenceRng(random_values=[0.0], randint_values=[5])
        battle, attacker, defender, source = self.make_battle(
            [blocker],
            rng=rng,
            attacker_health=10,
            attacker_max_health=20,
        )
        attacker.buffs.Vampirism = 5
        defender.buffs.Spikes = 5
        effect = AttackEffect(5, 5, 100)

        result = effect.apply(battle.build_context(source), "melee")

        self.assertTrue(result)
        self.assertEqual(defender.health, 20)
        self.assertEqual(attacker.health, 10)

    def test_melee_attack_effect_does_not_directly_mutate_damage_before_resolver(self):
        source = ConfigurableItem(item_key="source1", player_id=0)
        attacker = PlayerState(player_id=0, health=20, items={"source1": source})
        defender = PlayerState(player_id=1, health=20)
        battle = CapturingBattleState(players=[attacker, defender])
        effect = AttackEffect(1, 3, 90)

        result = effect.apply(battle.build_context(source), "melee")

        self.assertFalse(result)
        self.assertEqual(battle.captured_values, (None, 0, 0, False))
        self.assertEqual(defender.health, 20)

    def test_melee_attack_effect_applies_attacker_empower_luck_and_blind(self):
        source = ConfigurableItem(item_key="source1", player_id=0)
        source.item_types = ("Weapon",)
        attacker = PlayerState(player_id=0, health=20, items={"source1": source})
        attacker.buffs.Empower = 2
        attacker.buffs.Luck = 3
        attacker.debuffs.Blind = 1
        defender = PlayerState(player_id=1, health=20)
        defender.debuffs.Blind = 99
        battle = CapturingBattleState(players=[attacker, defender])
        effect = AttackEffect(1, 3, 90)

        effect.apply(battle.build_context(source), "melee")

        self.assertEqual(battle.captured_event.min_damage, 1)
        self.assertEqual(battle.captured_event.max_damage, 3)
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

    def test_dispatch_continues_to_next_responder_after_first_run_effect(
        self,
    ):
        first = ConfigurableItem(trigger=RecordingAttackTrigger())
        second = ConfigurableItem(trigger=RecordingAttackTrigger())
        rng = SequenceRng(random_values=[0.0], randint_values=[1])
        battle, attacker, defender, source = self.make_battle([first, second], rng=rng)
        event = self.make_event(attacker, defender, source, 1, 1)

        battle.resolve_attack(event)

        self.assertEqual(first.run_calls, 1)
        self.assertEqual(second.run_calls, 1)

    def test_attack_response_does_not_implicitly_activate_linked_item(
        self,
    ):
        parent = ConfigurableItem(
            trigger=RecordingAttackTrigger(),
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

        self.assertEqual(parent.run_calls, 1)
        self.assertEqual(linked.run_calls, 0)
        self.assertEqual(linked.contexts, [])

    def test_on_attacked_trigger_rolls_for_matching_melee_attack(self):
        item = ConfigurableItem(trigger=RecordingAttackTrigger())
        rng = SequenceRng(random_values=[0.2])
        battle, attacker, defender, source = self.make_battle([item], rng=rng)
        event = self.make_event(attacker, defender, source)
        event.hit = True
        context = battle.build_attack_reaction_context(
            item,
            ATTACK_PHASE_PRE_TAKE_DAMAGE,
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
            ATTACK_PHASE_PRE_TAKE_DAMAGE,
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
            ATTACK_PHASE_PRE_TAKE_DAMAGE,
            event,
        )

        result = PreventAttackDamageEffect(7).apply(context)

        self.assertTrue(result)
        self.assertEqual(event.pending_damage, 5)
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
            ATTACK_PHASE_PRE_TAKE_DAMAGE,
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
        activation_spy = Mock(wraps=buckler.emit_activation)
        buckler.emit_activation = activation_spy
        event = self.make_event(attacker, defender, source, 10, 10)

        battle.resolve_attack(event)

        self.assertEqual(event.prevented_damage, 7)
        self.assertEqual(event.pending_damage, 3)
        self.assertEqual(defender.health, 17)
        self.assertAlmostEqual(attacker.stamina, 0.7)
        activation_spy.assert_called_once()
        self.assertIs(activation_spy.call_args.args[0].item, buckler)

    def test_wooden_buckler_does_not_implicitly_activate_linked_item(
        self,
    ):
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

        self.assertEqual(event.prevented_damage, 5)
        self.assertEqual(defender.health, 20)
        self.assertAlmostEqual(attacker.stamina, 1.7)
        self.assertEqual(linked.run_calls, 0)
        self.assertEqual(linked.contexts, [])

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
        rng = SequenceRng(random_values=[0.9], randint_values=[10])
        battle, attacker, defender, source = self.make_battle(
            [buckler, linked],
            rng=rng,
            attacker_stamina=1.0,
        )
        activation_spy = Mock(wraps=buckler.emit_activation)
        buckler.emit_activation = activation_spy
        event = self.make_event(attacker, defender, source, 10, 10)

        battle.resolve_attack(event)

        self.assertEqual(event.prevented_damage, 0)
        self.assertEqual(defender.health, 10)
        self.assertEqual(attacker.stamina, 1.0)
        self.assertEqual(linked.run_calls, 0)
        activation_spy.assert_not_called()

    def test_attack_rng_call_order_is_hit_damage_then_reactions(self):
        buckler = WoodenBuckler()
        rng = SequenceRng(random_values=[0.0, 0.0], randint_values=[5])
        battle, attacker, defender, source = self.make_battle([buckler], rng=rng)
        event = self.make_event(attacker, defender, source, 5, 5)

        battle.resolve_attack(event)

        self.assertEqual(rng.calls, ["randint", "random"])

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

    def test_melee_statuses_use_event_damage_not_commit_return(self):
        heal_requests = []

        class AdjustedFinalDamageBattleState(BattleState):
            def commit_health_reduction(
                self,
                player,
                blocked_damage,
                health_damage,
                *,
                log_handle=None,
            ):
                actual_damage = super().commit_health_reduction(
                    player,
                    blocked_damage,
                    health_damage,
                )
                if player is self.players[1]:
                    return 0, 2
                return actual_damage

            def heal(self, target, amount, **kwargs):
                heal_requests.append(amount)
                return super().heal(target, amount, **kwargs)

        rng = SequenceRng(random_values=[0.0], randint_values=[7, 7])
        source = ConfigurableItem(
            item_key="source1",
            player_id=0,
            is_active_item=True,
        )
        attacker = PlayerState(
            player_id=0,
            health=10,
            max_health=20,
            items={"source1": source},
        )
        attacker.buffs.Vampirism = 10
        defender = PlayerState(player_id=1, health=20, max_health=20)
        defender.buffs.Spikes = 10
        battle = AdjustedFinalDamageBattleState(
            players=[attacker, defender],
            rng=rng,
        )
        event = self.make_event(attacker, defender, source, 7, 7)

        battle.resolve_attack(event)

        self.assertEqual(defender.health, 13)
        self.assertEqual(attacker.health, 10)
        self.assertEqual(heal_requests, [7])

    def test_vampirism_caps_at_stacks_and_missing_health(self):
        rng = SequenceRng(
            random_values=[0.0, 0.0],
            randint_values=[7, 7],
        )
        battle, attacker, defender, source = self.make_battle(
            rng=rng,
            attacker_health=17,
            attacker_max_health=20,
        )
        attacker.buffs.Vampirism = 2

        battle.resolve_attack(
            self.make_event(attacker, defender, source, 7, 7)
        )
        self.assertEqual(attacker.health, 19)

        attacker.buffs.Vampirism = 5
        battle.resolve_attack(
            self.make_event(attacker, defender, source, 7, 7)
        )
        self.assertEqual(attacker.health, 20)

    def test_spikes_caps_at_stack_count_and_consumes_block_first(self):
        rng = SequenceRng(random_values=[0.0], randint_values=[7, 5])
        battle, attacker, defender, source = self.make_battle(rng=rng)
        attacker.block = 3
        defender.buffs.Spikes = 5

        battle.resolve_attack(
            self.make_event(attacker, defender, source, 7, 7)
        )

        self.assertEqual(attacker.block, 0)
        self.assertEqual(attacker.health, 18)

    def test_melee_statuses_use_damage_across_defender_block_and_health(self):
        rng = SequenceRng(random_values=[0.0], randint_values=[7, 7])
        battle, attacker, defender, source = self.make_battle(
            rng=rng,
            defender_block=2,
        )
        defender.buffs.Spikes = 7

        battle.resolve_attack(
            self.make_event(attacker, defender, source, 7, 7)
        )

        self.assertEqual(defender.block, 0)
        self.assertEqual(defender.health, 15)
        self.assertEqual(attacker.health, 13)

    def test_fully_blocked_main_damage_still_counts_for_melee_statuses(self):
        rng = SequenceRng(random_values=[0.0], randint_values=[5, 3])
        battle, attacker, defender, source = self.make_battle(
            rng=rng,
            defender_block=5,
        )
        defender.buffs.Spikes = 3

        battle.resolve_attack(
            self.make_event(attacker, defender, source, 5, 5)
        )

        self.assertEqual(defender.block, 0)
        self.assertEqual(defender.health, 20)
        self.assertEqual(attacker.health, 17)

    def test_melee_hit_applies_spikes_before_vampirism(self):
        order = []

        class RecordingBattleState(BattleState):
            def commit_health_reduction(
                self,
                player,
                blocked_damage,
                health_damage,
                *,
                log_handle=None,
            ):
                order.append(("damage", player.player_id))
                return super().commit_health_reduction(
                    player,
                    blocked_damage,
                    health_damage,
                )

            def heal(self, target, amount, **kwargs):
                order.append(("heal", target.player_id))
                return super().heal(target, amount, **kwargs)

        rng = SequenceRng(random_values=[0.0], randint_values=[5, 2])
        source = ConfigurableItem(item_key="source1", player_id=0)
        attacker = PlayerState(
            player_id=0,
            health=10,
            max_health=20,
            items={"source1": source},
        )
        attacker.buffs.Vampirism = 2
        defender = PlayerState(player_id=1, health=20, max_health=20)
        defender.buffs.Spikes = 2
        battle = RecordingBattleState(
            players=[attacker, defender],
            rng=rng,
        )

        battle.resolve_attack(
            self.make_event(attacker, defender, source, 5, 5)
        )

        self.assertEqual(
            order,
            [("damage", 1), ("damage", 0), ("heal", 0)],
        )
        self.assertEqual(attacker.health, 10)

    def test_fatal_main_attack_finishes_spikes_and_vampirism(self):
        rng = SequenceRng(random_values=[0.0], randint_values=[20, 20])
        battle, attacker, defender, source = self.make_battle(
            rng=rng,
            attacker_health=10,
            attacker_max_health=20,
        )
        attacker.buffs.Vampirism = 20
        defender.buffs.Spikes = 20

        battle.resolve_attack(
            self.make_event(attacker, defender, source, 20, 20)
        )

        self.assertEqual(battle.winner, 0)
        self.assertEqual(attacker.health, 10)

    def test_lethal_spikes_locks_winner_before_vampirism(self):
        rng = SequenceRng(random_values=[0.0], randint_values=[5, 5])
        battle, attacker, defender, source = self.make_battle(
            rng=rng,
            attacker_health=2,
            attacker_max_health=20,
        )
        attacker.buffs.Vampirism = 5
        defender.buffs.Spikes = 5

        battle.resolve_attack(
            self.make_event(attacker, defender, source, 5, 5)
        )

        self.assertEqual(battle.winner, 1)
        self.assertEqual(attacker.health, 2)
        self.assertEqual(defender.health, 15)

    def test_miss_zero_and_non_melee_do_not_apply_melee_statuses(self):
        cases = (
            (SequenceRng(random_values=[0.9]), 1, 1, 0, ("melee",)),
            (
                SequenceRng(random_values=[0.0], randint_values=[0]),
                0,
                0,
                100,
                ("melee",),
            ),
            (
                SequenceRng(random_values=[0.0], randint_values=[3]),
                3,
                3,
                100,
                ("ranged",),
            ),
            (
                SequenceRng(random_values=[0.0], randint_values=[3]),
                3,
                3,
                100,
                ("effect",),
            ),
        )

        for rng, minimum, maximum, accuracy, attack_types in cases:
            with self.subTest(
                accuracy=accuracy,
                attack_types=attack_types,
                damage=minimum,
            ):
                battle, attacker, defender, source = self.make_battle(
                    rng=rng,
                    attacker_health=10,
                    attacker_max_health=20,
                )
                attacker.buffs.Vampirism = 5
                defender.buffs.Spikes = 5

                battle.resolve_attack(
                    self.make_event(
                        attacker,
                        defender,
                        source,
                        minimum,
                        maximum,
                        accuracy=accuracy,
                        attack_types=attack_types,
                    )
                )

                self.assertEqual(attacker.health, 10)

    def test_mixed_attack_with_melee_type_applies_melee_statuses(self):
        rng = SequenceRng(random_values=[0.0], randint_values=[3, 2])
        battle, attacker, defender, source = self.make_battle(rng=rng)
        defender.buffs.Spikes = 2

        battle.resolve_attack(
            self.make_event(
                attacker,
                defender,
                source,
                3,
                3,
                attack_types=("melee", "effect"),
            )
        )

        self.assertEqual(attacker.health, 18)

    def test_attack_bus_isolates_responder_players(self):
        first = ConfigurableItem(
            trigger=RecordingAttackTrigger(), item_key="shared", player_id=0,
        )
        second = ConfigurableItem(
            trigger=RecordingAttackTrigger(), item_key="shared", player_id=1,
        )
        owner = PlayerState(player_id=0, health=20, items={"shared": first})
        opponent = PlayerState(player_id=1, health=20, items={"shared": second})
        battle = BattleState(players=[owner, opponent])
        battle.prepareItems()
        event = self.make_event(opponent, owner, second)
        event.hit = True
        context = battle.build_attack_reaction_context(
            second, ATTACK_PHASE_PRE_TAKE_DAMAGE, event,
        )
        battle.emit_signal(owner, ATTACK_PHASE_PRE_TAKE_DAMAGE, context)
        self.assertEqual(first.run_calls, 1)
        self.assertEqual(second.run_calls, 0)
        self.assertIs(first.contexts[0].owner, owner)

    def test_attack_bus_builds_fresh_context_per_attack(self):
        item = ConfigurableItem(trigger=RecordingAttackTrigger())
        rng = SequenceRng(random_values=[0.0, 0.0], randint_values=[1, 1])
        battle, attacker, defender, source = self.make_battle([item], rng=rng)
        first_event = self.make_event(attacker, defender, source, 1, 1)
        second_event = self.make_event(attacker, defender, source, 1, 1)
        battle.resolve_attack(first_event)
        battle.resolve_attack(second_event)
        self.assertIsNot(item.contexts[0], item.contexts[1])
        self.assertIs(item.contexts[0].attack_event, first_event)
        self.assertIs(item.contexts[1].attack_event, second_event)

    def test_attack_bus_isolates_battle_states(self):
        first_item = ConfigurableItem(trigger=RecordingAttackTrigger())
        second_item = ConfigurableItem(trigger=RecordingAttackTrigger())
        first, attacker, defender, source = self.make_battle(
            [first_item], rng=SequenceRng(random_values=[0.0], randint_values=[1]),
        )
        second, _, _, _ = self.make_battle([second_item])
        first.resolve_attack(self.make_event(attacker, defender, source, 1, 1))
        self.assertEqual(first_item.run_calls, 1)
        self.assertEqual(second_item.run_calls, 0)
        self.assertIs(first_item.contexts[0].battle_state, first)


if __name__ == "__main__":
    unittest.main()
