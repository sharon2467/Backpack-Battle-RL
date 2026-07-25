import unittest
from unittest.mock import Mock

from battle_module_v1 import (
    BattleItem,
    BattleState,
    Effect,
    FIRST_POISON_TIME,
    FIRST_REGENERATION_TIME,
    ITEM_ACTIVATION_PHASE_LINKED,
    ItemActivationContext,
    PlayerState,
    STATUS_TICK_INTERVAL,
    Trigger,
    _BattleFinishedSignal,
    calculate_next_fatigue_damage,
    evaluate_layout,
)


class RecordingTrigger(Trigger):
    def __init__(self, result, log=None, entry=None):
        self.result = result
        self.log = log
        self.entry = entry
        self.calls = 0

    def update(self, context):
        self.calls += 1
        if self.log is not None and self.entry is not None:
            self.log.append(self.entry)
        return self.result


class RecordingEffect(Effect):
    def __init__(self, result=True, log=None, entry=None):
        self.result = result
        self.log = log
        self.entry = entry
        self.calls = 0
        self.contexts = []

    def apply(self, context):
        self.calls += 1
        self.contexts.append(context)
        if self.log is not None and self.entry is not None:
            self.log.append(self.entry)
        return self.result


class RecordingItem(BattleItem):
    def __init__(
        self,
        name,
        log,
        should_trigger=True,
        **kwargs,
    ):
        item_key = kwargs.get("item_key")
        super().__init__(
            item_id=name,
            triggers=[RecordingTrigger(should_trigger, log, f"update:{item_key}")],
            effects=[RecordingEffect(True, log, f"effect:{item_key}")],
            **kwargs,
        )
        self.name = name
        self.log = log
        self.run_effect_calls = 0
        self.received_trigger_results = []

    def run_effect(self, trigger_results, context):
        self.run_effect_calls += 1
        self.received_trigger_results.append(list(trigger_results))
        if not trigger_results[0]:
            return
        self.effects[0].apply(context)


class DecisionItem(BattleItem):
    def __init__(self, trigger_results, effect_results, decision, **kwargs):
        self.log = []
        triggers = [
            RecordingTrigger(result, self.log, f"trigger:{index}")
            for index, result in enumerate(trigger_results)
        ]
        effects = [
            RecordingEffect(result, self.log, f"effect:{index}")
            for index, result in enumerate(effect_results)
        ]
        super().__init__(triggers=triggers, effects=effects, **kwargs)
        self.decision = decision
        self.received_trigger_results = []

    def run_effect(self, trigger_results, context):
        self.log.append("run")
        self.received_trigger_results.append(list(trigger_results))
        self.decision(self, trigger_results, context)


class ActivateLinkedItemEffect(Effect):
    def __init__(self, linked_key):
        self.linked_key = linked_key
        self.calls = 0

    def apply(self, context):
        self.calls += 1
        linked_item = context.owner.items[self.linked_key]
        linked_item.activate_item(
            context.for_item(linked_item)
        )
        return True


class MetadataItem(BattleItem):
    display_name = "Metadata Item"
    item_classes = ("Neutral",)
    rarity = "Common"
    cost = 3
    item_types = ("Weapon",)
    icon_types = ("melee",)


class ActivationListenerItem(BattleItem):
    def __init__(
        self,
        *,
        has_phase=True,
        should_trigger=False,
        event_log=None,
        emit_when_triggered=False,
        **kwargs,
    ):
        trigger = RecordingTrigger(should_trigger)
        if has_phase:
            trigger.item_activation_phase = ITEM_ACTIVATION_PHASE_LINKED
        super().__init__(
            triggers=[trigger],
            effects=[RecordingEffect()],
            **kwargs,
        )
        self.contexts = []
        self.event_log = event_log
        self.emit_when_triggered = emit_when_triggered

    def run_effect(self, trigger_results, context):
        self.contexts.append(context)
        if self.event_log is not None:
            self.event_log.append(
                (self.item_key, getattr(context, "source_item", None))
            )
        if self.emit_when_triggered and trigger_results[0]:
            self.emit_activation(context)


class BattleModuleV1Test(unittest.TestCase):
    def make_activation_state(self, owner_items, opponent_items=None):
        owner = PlayerState(
            player_id=0,
            health=20,
            max_health=20,
            items={
                item.item_key: item
                for item in owner_items
            },
        )
        opponent_items = [] if opponent_items is None else opponent_items
        opponent = PlayerState(
            player_id=1,
            health=20,
            max_health=20,
            items={
                item.item_key: item
                for item in opponent_items
            },
        )
        return BattleState(players=[owner, opponent]), owner, opponent

    def test_battle_item_exposes_new_activation_interface_only(self):
        self.assertTrue(hasattr(BattleItem, "activate_item"))
        self.assertTrue(hasattr(BattleItem, "emit_activation"))
        self.assertTrue(hasattr(BattleItem, "run_effect"))
        self.assertFalse(hasattr(BattleItem, "run_effects"))
        self.assertFalse(hasattr(BattleItem, "run_own_effect"))
        self.assertFalse(hasattr(BattleItem, "run_linked_items"))

    def test_emit_activation_requires_context_for_same_item(self):
        source = ActivationListenerItem(
            item_id="source",
            item_key="source1",
            player_id=0,
            has_phase=False,
        )
        other = ActivationListenerItem(
            item_id="other",
            item_key="other1",
            player_id=0,
            has_phase=False,
        )
        battle, _, _ = self.make_activation_state([source, other])
        battle.dispatch_item_activation = Mock()

        with self.assertRaises(ValueError):
            source.emit_activation(battle.build_context(other))

        battle.dispatch_item_activation.assert_not_called()

    def test_emit_activation_delegates_to_battle_state_and_returns_none(self):
        source = ActivationListenerItem(
            item_id="source",
            item_key="source1",
            player_id=0,
            has_phase=False,
        )
        battle, _, _ = self.make_activation_state([source])
        battle.dispatch_item_activation = Mock()

        result = source.emit_activation(battle.build_context(source))

        self.assertIsNone(result)
        battle.dispatch_item_activation.assert_called_once_with(source)

    def test_build_item_activation_context_preserves_source_reference(self):
        source = ActivationListenerItem(
            item_id="source",
            item_key="source1",
            player_id=0,
            has_phase=False,
        )
        listener = ActivationListenerItem(
            item_id="listener",
            item_key="listener1",
            player_id=0,
            linked_items=["source1"],
        )
        battle, owner, opponent = self.make_activation_state(
            [source, listener]
        )

        context = battle.build_item_activation_context(listener, source)

        self.assertIsInstance(context, ItemActivationContext)
        self.assertIs(context.battle_state, battle)
        self.assertIs(context.item, listener)
        self.assertIs(context.owner, owner)
        self.assertIs(context.opponent, opponent)
        self.assertIs(context.source_item, source)

    def test_build_item_activation_context_rejects_other_owner_or_foreign_source(
        self,
    ):
        listener = ActivationListenerItem(
            item_id="listener",
            item_key="listener1",
            player_id=0,
        )
        other_owner_source = ActivationListenerItem(
            item_id="source",
            item_key="source1",
            player_id=1,
            has_phase=False,
        )
        battle, _, _ = self.make_activation_state(
            [listener],
            [other_owner_source],
        )
        foreign_source = ActivationListenerItem(
            item_id="foreign",
            item_key="foreign1",
            player_id=0,
            has_phase=False,
        )

        with self.assertRaises(ValueError):
            battle.build_item_activation_context(
                listener,
                other_owner_source,
            )
        with self.assertRaises(ValueError):
            battle.build_item_activation_context(listener, foreign_source)

    def test_activation_listener_lookup_requires_phase_and_source_link(self):
        source = ActivationListenerItem(
            item_id="source",
            item_key="source1",
            player_id=0,
            has_phase=False,
        )
        linked_with_phase = ActivationListenerItem(
            item_id="linked_with_phase",
            item_key="linked_with_phase1",
            player_id=0,
            linked_items=["source1"],
        )
        linked_without_phase = ActivationListenerItem(
            item_id="linked_without_phase",
            item_key="linked_without_phase1",
            player_id=0,
            linked_items=["source1"],
            has_phase=False,
        )
        phase_without_link = ActivationListenerItem(
            item_id="phase_without_link",
            item_key="phase_without_link1",
            player_id=0,
        )
        battle, _, _ = self.make_activation_state(
            [
                source,
                linked_with_phase,
                linked_without_phase,
                phase_without_link,
            ]
        )

        self.assertEqual(
            battle._get_item_activation_listeners(source),
            (linked_with_phase,),
        )

    def test_activation_listener_lookup_preserves_owner_item_order(self):
        source = ActivationListenerItem(
            item_id="source",
            item_key="source1",
            player_id=0,
            has_phase=False,
        )
        first = ActivationListenerItem(
            item_id="first",
            item_key="first1",
            player_id=0,
            linked_items=["source1"],
        )
        second = ActivationListenerItem(
            item_id="second",
            item_key="second1",
            player_id=0,
            linked_items=["source1"],
        )
        battle, _, _ = self.make_activation_state(
            [source, second, first]
        )

        self.assertEqual(
            battle._get_item_activation_listeners(source),
            (second, first),
        )

    def test_activation_listener_lookup_never_reads_opponent_items(self):
        source = ActivationListenerItem(
            item_id="source",
            item_key="shared1",
            player_id=0,
            has_phase=False,
        )
        opponent_source = ActivationListenerItem(
            item_id="opponent_source",
            item_key="shared1",
            player_id=1,
            has_phase=False,
        )
        opponent_listener = ActivationListenerItem(
            item_id="opponent_listener",
            item_key="opponent_listener1",
            player_id=1,
            linked_items=["shared1"],
        )
        battle, _, _ = self.make_activation_state(
            [source],
            [opponent_source, opponent_listener],
        )

        self.assertEqual(
            battle._get_item_activation_listeners(source),
            (),
        )

    def test_second_activation_listener_lookup_uses_cached_tuple(self):
        source = ActivationListenerItem(
            item_id="source",
            item_key="source1",
            player_id=0,
            has_phase=False,
        )
        listener = ActivationListenerItem(
            item_id="listener",
            item_key="listener1",
            player_id=0,
            linked_items=["source1"],
        )
        battle, _, _ = self.make_activation_state([source, listener])

        first = battle._get_item_activation_listeners(source)
        listener.triggers[0].item_activation_phase = None
        second = battle._get_item_activation_listeners(source)

        self.assertIs(first, second)
        self.assertEqual(second, (listener,))

    def test_empty_activation_listener_lookup_is_cached(self):
        source = ActivationListenerItem(
            item_id="source",
            item_key="source1",
            player_id=0,
            has_phase=False,
        )
        battle, owner, _ = self.make_activation_state([source])

        first = battle._get_item_activation_listeners(source)
        listener = ActivationListenerItem(
            item_id="listener",
            item_key="listener1",
            player_id=0,
            linked_items=["source1"],
        )
        owner.items[listener.item_key] = listener
        second = battle._get_item_activation_listeners(source)

        self.assertIs(first, second)
        self.assertEqual(second, ())

    def test_dispatch_builds_fresh_context_for_each_source_event(self):
        source = ActivationListenerItem(
            item_id="source",
            item_key="source1",
            player_id=0,
            has_phase=False,
        )
        listener = ActivationListenerItem(
            item_id="listener",
            item_key="listener1",
            player_id=0,
            linked_items=["source1"],
        )
        battle, _, _ = self.make_activation_state([source, listener])

        battle.dispatch_item_activation(source)
        battle.dispatch_item_activation(source)

        self.assertEqual(len(listener.contexts), 2)
        self.assertIsNot(listener.contexts[0], listener.contexts[1])
        self.assertIs(listener.contexts[0].source_item, source)
        self.assertIs(listener.contexts[1].source_item, source)

    def test_dispatch_continues_to_next_listener_when_first_does_not_trigger(
        self,
    ):
        source = ActivationListenerItem(
            item_id="source",
            item_key="source1",
            player_id=0,
            has_phase=False,
        )
        first = ActivationListenerItem(
            item_id="first",
            item_key="first1",
            player_id=0,
            linked_items=["source1"],
            should_trigger=False,
        )
        second = ActivationListenerItem(
            item_id="second",
            item_key="second1",
            player_id=0,
            linked_items=["source1"],
            should_trigger=True,
        )
        battle, _, _ = self.make_activation_state(
            [source, first, second]
        )

        battle.dispatch_item_activation(source)

        self.assertEqual(len(first.contexts), 1)
        self.assertEqual(len(second.contexts), 1)

    def test_nested_activation_dispatch_preserves_outer_source(self):
        log = []
        source = ActivationListenerItem(
            item_id="source",
            item_key="source1",
            player_id=0,
            has_phase=False,
        )
        first = ActivationListenerItem(
            item_id="first",
            item_key="first1",
            player_id=0,
            linked_items=["source1"],
            should_trigger=True,
            event_log=log,
            emit_when_triggered=True,
        )
        nested = ActivationListenerItem(
            item_id="nested",
            item_key="nested1",
            player_id=0,
            linked_items=["first1"],
            event_log=log,
        )
        last = ActivationListenerItem(
            item_id="last",
            item_key="last1",
            player_id=0,
            linked_items=["source1"],
            event_log=log,
        )
        battle, _, _ = self.make_activation_state(
            [source, first, nested, last]
        )

        battle.dispatch_item_activation(source)

        self.assertEqual(
            log,
            [
                ("first1", source),
                ("nested1", first),
                ("last1", source),
            ],
        )

    def test_battle_states_own_independent_activation_listener_caches(self):
        first_source = ActivationListenerItem(
            item_id="source",
            item_key="source1",
            player_id=0,
            has_phase=False,
        )
        first_listener = ActivationListenerItem(
            item_id="listener",
            item_key="listener1",
            player_id=0,
            linked_items=["source1"],
        )
        first_battle, _, _ = self.make_activation_state(
            [first_source, first_listener]
        )
        second_source = ActivationListenerItem(
            item_id="source",
            item_key="source1",
            player_id=0,
            has_phase=False,
        )
        second_battle, _, _ = self.make_activation_state([second_source])

        first_tuple = first_battle._get_item_activation_listeners(
            first_source
        )
        second_tuple = second_battle._get_item_activation_listeners(
            second_source
        )

        self.assertIsNot(
            first_battle._item_activation_listener_cache,
            second_battle._item_activation_listener_cache,
        )
        self.assertEqual(first_tuple, (first_listener,))
        self.assertEqual(second_tuple, ())

    def test_battle_item_requires_at_least_one_trigger(self):
        with self.assertRaises(ValueError):
            BattleItem(item_id="empty", item_key="empty1", triggers=[], effects=[Effect()])

    def test_battle_item_requires_at_least_one_effect(self):
        with self.assertRaises(ValueError):
            BattleItem(item_id="empty", item_key="empty1", triggers=[Trigger()], effects=[])

    def test_battle_item_without_components_fails(self):
        with self.assertRaises(ValueError):
            BattleItem(item_id="empty", item_key="empty1")

    def test_battle_item_stores_player_id_and_item_key(self):
        item = BattleItem(
            item_id="owned_item",
            item_key="owned_item1",
            player_id=1,
            triggers=[Trigger()],
            effects=[Effect()],
        )

        self.assertEqual(item.player_id, 1)
        self.assertEqual(item.item_key, "owned_item1")

    def test_battle_item_copies_metadata_class_defaults_to_instance(self):
        item = MetadataItem(triggers=[Trigger()], effects=[Effect()])

        self.assertEqual(item.display_name, "Metadata Item")
        self.assertEqual(item.item_classes, ("Neutral",))
        self.assertEqual(item.rarity, "Common")
        self.assertEqual(item.cost, 3)
        self.assertEqual(item.item_types, ("Weapon",))
        self.assertEqual(item.icon_types, ("melee",))
        self.assertIn("display_name", item.__dict__)
        self.assertIn("item_classes", item.__dict__)
        self.assertIn("rarity", item.__dict__)
        self.assertIn("cost", item.__dict__)
        self.assertIn("item_types", item.__dict__)
        self.assertIn("icon_types", item.__dict__)

    def test_battle_item_accepts_metadata_instance_overrides(self):
        item = MetadataItem(
            display_name="Override Item",
            item_classes=("Ranger", "Neutral"),
            rarity="Rare",
            cost=5,
            item_types=("Accessory", "Weapon"),
            icon_types=("nature", "melee"),
            triggers=[Trigger()],
            effects=[Effect()],
        )

        self.assertEqual(item.display_name, "Override Item")
        self.assertEqual(item.item_classes, ("Ranger", "Neutral"))
        self.assertEqual(item.rarity, "Rare")
        self.assertEqual(item.cost, 5)
        self.assertEqual(item.item_types, ("Accessory", "Weapon"))
        self.assertEqual(item.icon_types, ("nature", "melee"))

    def test_add_linked_item_stores_keys_once_in_first_seen_order(self):
        item = BattleItem(
            item_id="source",
            item_key="source1",
            triggers=[Trigger()],
            effects=[Effect()],
        )

        item.add_linked_item("target1")
        item.add_linked_item("target2")
        item.add_linked_item("target1")

        self.assertEqual(item.linked_items, ["target1", "target2"])

    def test_battle_item_list_container_ownership_contract(self):
        first_item = BattleItem(
            item_id="first",
            item_key="first1",
            triggers=[Trigger()],
            effects=[Effect()],
        )
        second_item = BattleItem(
            item_id="second",
            item_key="second1",
            triggers=[Trigger()],
            effects=[Effect()],
        )

        self.assertIsNot(first_item.linked_items, second_item.linked_items)
        first_item.add_linked_item("target1")
        self.assertEqual(second_item.linked_items, [])

        triggers = [Trigger()]
        effects = [Effect()]
        linked_items = ["target1"]
        owned_item = BattleItem(
            item_id="owned",
            item_key="owned1",
            triggers=triggers,
            effects=effects,
            linked_items=linked_items,
        )

        self.assertIsNot(owned_item.triggers, triggers)
        self.assertIsNot(owned_item.effects, effects)
        self.assertIsNot(owned_item.linked_items, linked_items)
        self.assertEqual(owned_item.triggers, triggers)
        self.assertEqual(owned_item.effects, effects)
        self.assertEqual(owned_item.linked_items, linked_items)

        triggers.append(Trigger())
        effects.append(Effect())
        linked_items.append("target2")

        self.assertEqual(len(owned_item.triggers), 1)
        self.assertEqual(len(owned_item.effects), 1)
        self.assertEqual(owned_item.linked_items, ["target1"])

        tuple_item = BattleItem(
            item_id="tuple-owned",
            item_key="tuple-owned1",
            triggers=(Trigger(),),
            effects=(Effect(),),
            linked_items=("target1",),
        )

        self.assertIsInstance(tuple_item.triggers, list)
        self.assertIsInstance(tuple_item.effects, list)
        self.assertIsInstance(tuple_item.linked_items, list)

    def test_update_triggers_returns_and_stores_results_in_order(self):
        item = DecisionItem(
            trigger_results=[False, True, False],
            effect_results=[True],
            decision=lambda item, trigger_results, context: False,
        )

        results = item.update_triggers(context=None)

        self.assertEqual(results, [False, True, False])
        self.assertEqual(item.trigger_results, [False, True, False])
        self.assertEqual(item.log, ["trigger:0", "trigger:1", "trigger:2"])
        self.assertEqual([trigger.calls for trigger in item.triggers], [1, 1, 1])

    def test_update_triggers_does_not_short_circuit_after_false(self):
        item = DecisionItem(
            trigger_results=[False, False, True],
            effect_results=[True],
            decision=lambda item, trigger_results, context: False,
        )

        item.update_triggers(context=None)

        self.assertEqual([trigger.calls for trigger in item.triggers], [1, 1, 1])

    def test_update_triggers_rejects_non_bool_result(self):
        item = DecisionItem(
            trigger_results=[1],
            effect_results=[True],
            decision=lambda item, trigger_results, context: False,
        )

        with self.assertRaises(ValueError):
            item.update_triggers(context=None)

    def test_activate_item_updates_triggers_before_run_effect(self):
        item = DecisionItem(
            trigger_results=[True, False],
            effect_results=[True],
            decision=lambda item, trigger_results, context: False,
        )

        item.activate_item(context=None)

        self.assertEqual(item.log, ["trigger:0", "trigger:1", "run"])
        self.assertEqual(item.received_trigger_results, [[True, False]])

    def test_activate_item_calls_run_effect_when_all_triggers_are_false(
        self,
    ):
        item = DecisionItem(
            trigger_results=[False, False],
            effect_results=[True],
            decision=lambda item, trigger_results, context: False,
        )

        result = item.activate_item(context=None)

        self.assertIsNone(result)
        self.assertEqual(item.received_trigger_results, [[False, False]])
        self.assertEqual(item.log, ["trigger:0", "trigger:1", "run"])

    def test_not_trigger_item_can_apply_effect_when_trigger_is_false(self):
        def run_not_effect(item, trigger_results, context):
            if not trigger_results[0]:
                item.effects[0].apply(context)

        item = DecisionItem(
            trigger_results=[False],
            effect_results=[True],
            decision=run_not_effect,
        )

        result = item.activate_item(context=None)

        self.assertIsNone(result)
        self.assertEqual(item.effects[0].calls, 1)
        self.assertEqual(item.log, ["trigger:0", "run", "effect:0"])

    def test_activate_item_returns_none_without_interpreting_run_effect_return(
        self,
    ):
        for callback_result in (True, False, 1, None):
            with self.subTest(callback_result=callback_result):
                item = DecisionItem(
                    trigger_results=[True],
                    effect_results=[True],
                    decision=lambda item, trigger_results, context: (
                        callback_result
                    ),
                )
                item.emit_activation = Mock()

                result = item.activate_item(context=None)

                self.assertIsNone(result)
                item.emit_activation.assert_not_called()

    def test_run_effect_can_stop_effect_sequence_after_failure(self):
        def stop_after_failure(item, trigger_results, context):
            first_result = item.effects[0].apply(context)
            if not first_result:
                return
            item.effects[1].apply(context)

        item = DecisionItem(
            trigger_results=[True],
            effect_results=[False, True],
            decision=stop_after_failure,
        )

        item.activate_item(context=None)

        self.assertEqual([effect.calls for effect in item.effects], [1, 0])

    def test_run_effect_can_continue_effect_sequence_after_failure(self):
        def continue_after_failure(item, trigger_results, context):
            item.effects[0].apply(context)
            item.effects[1].apply(context)

        item = DecisionItem(
            trigger_results=[True],
            effect_results=[False, True],
            decision=continue_after_failure,
        )

        item.activate_item(context=None)

        self.assertEqual([effect.calls for effect in item.effects], [1, 1])

    def test_effect_apply_receives_only_context(self):
        marker_context = object()

        def apply_effect(item, trigger_results, context):
            item.effects[0].apply(context)

        item = DecisionItem(
            trigger_results=[True],
            effect_results=[True],
            decision=apply_effect,
        )

        item.activate_item(marker_context)

        self.assertEqual(item.effects[0].contexts, [marker_context])

    def test_battle_items_own_independent_trigger_result_lists(self):
        first_item = DecisionItem(
            trigger_results=[True],
            effect_results=[True],
            decision=lambda item, trigger_results, context: False,
        )
        second_item = DecisionItem(
            trigger_results=[False],
            effect_results=[True],
            decision=lambda item, trigger_results, context: False,
        )

        first_item.update_triggers(context=None)

        self.assertIsNot(first_item.trigger_results, second_item.trigger_results)
        self.assertEqual(first_item.trigger_results, [True])
        self.assertEqual(second_item.trigger_results, [False])

    def test_battle_state_step_updates_only_active_items_directly(self):
        log = []
        active_item = RecordingItem("active", log, item_key="active1", player_id=0, is_active_item=True)
        inactive_item = RecordingItem("inactive", log, item_key="inactive1", player_id=0, is_active_item=False)
        owner = PlayerState(player_id=0, health=10, items={
            "active1": active_item,
            "inactive1": inactive_item,
        })
        opponent = PlayerState(player_id=1, health=10)
        battle = BattleState(players=[owner, opponent], active_items=[active_item])

        battle.step()

        self.assertEqual(log, ["update:active1", "effect:active1"])
        self.assertEqual(battle.frame, 1)
        self.assertEqual(battle.time, 1.0 / 30.0)

    def test_effect_can_explicitly_activate_linked_item(self):
        log = []
        active_item = RecordingItem("active", log, item_key="active1", player_id=0, is_active_item=True)
        linked_item = RecordingItem("linked", log, item_key="linked1", player_id=0)
        active_item.add_linked_item("linked1")
        activation_effect = ActivateLinkedItemEffect("linked1")
        active_item.effects[0] = activation_effect
        owner = PlayerState(player_id=0, health=10, items={
            "active1": active_item,
            "linked1": linked_item,
        })
        opponent = PlayerState(player_id=1, health=10)
        battle = BattleState(players=[owner, opponent], active_items=[active_item])

        battle.step()

        self.assertEqual(
            log,
            [
                "update:active1",
                "update:linked1",
                "effect:linked1",
            ],
        )
        self.assertEqual(activation_effect.calls, 1)
        self.assertEqual(linked_item.run_effect_calls, 1)

    def test_activate_item_does_not_implicitly_activate_linked_items(
        self,
    ):
        log = []
        active_item = RecordingItem(
            "active",
            log,
            item_key="active1",
            player_id=0,
            is_active_item=True,
        )
        linked_item = RecordingItem("linked", log, item_key="linked1", player_id=0)
        active_item.add_linked_item("linked1")
        owner = PlayerState(player_id=0, health=10, items={
            "active1": active_item,
            "linked1": linked_item,
        })
        opponent = PlayerState(player_id=1, health=10)
        battle = BattleState(players=[owner, opponent], active_items=[active_item])

        battle.step()

        self.assertEqual(log, ["update:active1", "effect:active1"])
        self.assertEqual(linked_item.triggers[0].calls, 0)
        self.assertEqual(linked_item.run_effect_calls, 0)

    def test_battle_state_step_calls_run_effect_for_all_false_triggers(
        self,
    ):
        log = []
        active_item = RecordingItem(
            "active",
            log,
            item_key="active1",
            player_id=0,
            is_active_item=True,
            should_trigger=False,
        )
        owner = PlayerState(player_id=0, health=10, items={"active1": active_item})
        opponent = PlayerState(player_id=1, health=10)
        battle = BattleState(players=[owner, opponent], active_items=[active_item])

        battle.step()

        self.assertEqual(log, ["update:active1"])
        self.assertEqual(active_item.run_effect_calls, 1)
        self.assertEqual(active_item.received_trigger_results, [[False]])

    def test_first_active_item_early_return_does_not_stop_other_active_items(
        self,
    ):
        log = []
        first_item = RecordingItem(
            "first",
            log,
            item_key="first1",
            player_id=0,
            is_active_item=True,
            should_trigger=False,
        )
        second_item = RecordingItem(
            "second",
            log,
            item_key="second1",
            player_id=0,
            is_active_item=True,
        )
        owner = PlayerState(player_id=0, health=10, items={
            "first1": first_item,
            "second1": second_item,
        })
        opponent = PlayerState(player_id=1, health=10)
        battle = BattleState(players=[owner, opponent], active_items=[first_item, second_item])

        battle.step()

        self.assertEqual(
            log,
            [
                "update:first1",
                "update:second1",
                "effect:second1",
            ],
        )

    def test_battle_state_step_regenerates_stamina_by_frame_delta_up_to_maximum(self):
        first_player = PlayerState(
            player_id=0,
            health=10,
            stamina=1.0,
            max_stamina=2.0,
        )
        second_player = PlayerState(
            player_id=1,
            health=10,
            stamina=1.8,
            max_stamina=2.0,
        )
        battle = BattleState(
            players=[first_player, second_player],
            frame_delta=0.5,
        )

        battle.step()

        self.assertAlmostEqual(first_player.stamina, 1.5)
        self.assertAlmostEqual(second_player.stamina, 2.0)

    def test_battle_state_regenerates_stamina_before_running_items(self):
        observed_stamina = []

        def record_stamina(item, trigger_results, context):
            observed_stamina.append(context.owner.stamina)
            return False

        active_item = DecisionItem(
            trigger_results=[True],
            effect_results=[True],
            decision=record_stamina,
            item_key="active1",
            player_id=0,
            is_active_item=True,
        )
        owner = PlayerState(
            player_id=0,
            health=10,
            stamina=0.0,
            max_stamina=2.0,
            items={"active1": active_item},
        )
        opponent = PlayerState(
            player_id=1,
            health=10,
            stamina=0.0,
            max_stamina=2.0,
        )
        battle = BattleState(
            players=[owner, opponent],
            active_items=[active_item],
            frame_delta=0.25,
        )

        battle.step()

        self.assertEqual(observed_stamina, [0.25])

    def test_player_state_uses_independent_mutable_defaults(self):
        first_player = PlayerState(player_id=0)
        second_player = PlayerState(player_id=1)

        first_player.buffs.Heat = 1
        first_player.debuffs.Poison = 2
        first_player.items["item1"] = BattleItem(
            item_id="item1",
            item_key="item1",
            player_id=0,
            triggers=[Trigger()],
            effects=[Effect()],
        )

        self.assertIsNot(first_player.buffs, second_player.buffs)
        self.assertIsNot(first_player.debuffs, second_player.debuffs)
        self.assertIsNot(first_player.items, second_player.items)
        self.assertEqual(second_player.buffs.Heat, 0)
        self.assertEqual(second_player.debuffs.Poison, 0)
        self.assertEqual(second_player.items, {})

    def test_player_state_rejects_direct_health_reduction(self):
        player = PlayerState(player_id=0, health=10)

        with self.assertRaisesRegex(
            ValueError,
            "health reductions must use BattleState.commit_health_reduction",
        ):
            player.health -= 1

        self.assertEqual(player.health, 10)

    def test_player_state_allows_direct_health_increase(self):
        player = PlayerState(player_id=0, health=10, max_health=20)

        player.health += 3

        self.assertEqual(player.health, 13)

    def test_player_state_stores_explicit_max_health(self):
        player = PlayerState(player_id=0, health=6, max_health=10)

        self.assertEqual(player.health, 6)
        self.assertEqual(player.max_health, 10)

    def test_player_state_does_not_infer_max_health_from_health(self):
        player = PlayerState(player_id=0, health=10)

        self.assertEqual(player.max_health, 0)

    def test_player_states_own_independent_max_health_values(self):
        first = PlayerState(player_id=0, health=6, max_health=10)
        second = PlayerState(player_id=1, health=7, max_health=12)

        first.max_health = 20

        self.assertEqual(first.max_health, 20)
        self.assertEqual(second.max_health, 12)

    def test_commit_health_reduction_updates_block_and_health(self):
        target = PlayerState(player_id=0, health=10, block=3)
        opponent = PlayerState(player_id=1, health=10)
        battle = BattleState(players=[target, opponent])

        final_damage = battle.commit_health_reduction(
            target,
            blocked_damage=2,
            health_damage=4,
        )

        self.assertEqual(final_damage, 6)
        self.assertEqual(target.block, 1)
        self.assertEqual(target.health, 6)
        self.assertIsNone(battle.winner)

    def test_commit_health_reduction_returns_block_only_and_health_only(self):
        first = PlayerState(player_id=0, health=10, block=3)
        second = PlayerState(player_id=1, health=10)
        battle = BattleState(players=[first, second])

        self.assertEqual(
            battle.commit_health_reduction(first, 2, 0),
            2,
        )
        self.assertEqual(
            battle.commit_health_reduction(first, 0, 4),
            4,
        )

    def test_commit_health_reduction_lethal_overkill_stops_before_return(self):
        first = PlayerState(player_id=0, health=2)
        second = PlayerState(player_id=1, health=10)
        battle = BattleState(players=[first, second])

        with self.assertRaises(_BattleFinishedSignal):
            battle.commit_health_reduction(first, 0, 99)

        self.assertEqual(first.health, 0)
        self.assertEqual(battle.winner, 1)

    def test_heal_returns_actual_amount_and_caps_at_max_health(self):
        first = PlayerState(player_id=0, health=8, max_health=10)
        second = PlayerState(player_id=1, health=10, max_health=10)
        battle = BattleState(players=[first, second])

        self.assertEqual(battle.heal(first, 5), 2)
        self.assertEqual(first.health, 10)
        self.assertEqual(battle.heal(first, 1), 0)

    def test_heal_rejects_invalid_amount_and_foreign_target(self):
        first = PlayerState(player_id=0, health=8, max_health=10)
        second = PlayerState(player_id=1, health=10, max_health=10)
        outsider = PlayerState(player_id=2, health=5, max_health=10)
        battle = BattleState(players=[first, second])

        for invalid_amount in (-1, 1.0, True, "1"):
            with self.subTest(invalid_amount=invalid_amount):
                with self.assertRaises(ValueError):
                    battle.heal(first, invalid_amount)
        with self.assertRaises(ValueError):
            battle.heal(outsider, 1)

    def test_commit_health_reduction_rejects_invalid_values(self):
        target = PlayerState(player_id=0, health=10, block=3)
        opponent = PlayerState(player_id=1, health=10)
        battle = BattleState(players=[target, opponent])

        invalid_values = [
            (-1, 0),
            (0, -1),
            (4, 0),
            (1.0, 0),
            (0, 1.0),
            (True, 0),
            (0, True),
        ]
        for blocked_damage, health_damage in invalid_values:
            with self.subTest(
                blocked_damage=blocked_damage,
                health_damage=health_damage,
            ):
                with self.assertRaises(ValueError):
                    battle.commit_health_reduction(
                        target,
                        blocked_damage,
                        health_damage,
                    )

        self.assertEqual(target.block, 3)
        self.assertEqual(target.health, 10)

    def test_commit_health_reduction_rejects_player_outside_battle(self):
        first_player = PlayerState(player_id=0, health=10)
        second_player = PlayerState(player_id=1, health=10)
        outsider = PlayerState(player_id=2, health=10)
        battle = BattleState(players=[first_player, second_player])

        with self.assertRaises(ValueError):
            battle.commit_health_reduction(
                outsider,
                blocked_damage=0,
                health_damage=1,
            )

        self.assertEqual(outsider.health, 10)

    def test_calculate_item_fatigue_increases_by_one(self):
        self.assertEqual(
            calculate_next_fatigue_damage(0, nightfall=False),
            1,
        )
        self.assertEqual(
            calculate_next_fatigue_damage(10, nightfall=False),
            11,
        )

    def test_calculate_nightfall_fatigue_uses_accelerating_formula(self):
        expected_values = {
            0: 1,
            9: 10,
            10: 12,
            29: 32,
        }

        for previous, expected in expected_values.items():
            with self.subTest(previous=previous):
                self.assertEqual(
                    calculate_next_fatigue_damage(
                        previous,
                        nightfall=True,
                    ),
                    expected,
                )

    def test_calculate_fatigue_rejects_invalid_arguments(self):
        invalid_previous_values = (-1, 1.0, True)
        for previous in invalid_previous_values:
            with self.subTest(previous=previous):
                with self.assertRaises(ValueError):
                    calculate_next_fatigue_damage(
                        previous,
                        nightfall=True,
                    )

        with self.assertRaises(ValueError):
            calculate_next_fatigue_damage(0, nightfall=1)

    def test_nightfall_fatigue_first_triggers_at_seventeen_seconds(self):
        first_player = PlayerState(player_id=0, health=100)
        second_player = PlayerState(player_id=1, health=100)
        battle = BattleState(players=[first_player, second_player])

        battle.run(max_frames=16, frame_delta=1.0)

        self.assertEqual(battle.time, 16.0)
        self.assertEqual(first_player.health, 100)
        self.assertEqual(second_player.health, 100)
        self.assertEqual(first_player.fatigue_damage, 0)
        self.assertEqual(second_player.fatigue_damage, 0)

        battle.step()

        self.assertEqual(battle.time, 17.0)
        self.assertEqual(first_player.health, 99)
        self.assertEqual(second_player.health, 99)
        self.assertEqual(first_player.fatigue_damage, 1)
        self.assertEqual(second_player.fatigue_damage, 1)

    def test_nightfall_fatigue_repeats_each_second(self):
        first_player = PlayerState(player_id=0, health=100)
        second_player = PlayerState(player_id=1, health=100)
        battle = BattleState(players=[first_player, second_player])

        battle.run(max_frames=19, frame_delta=1.0)

        self.assertEqual(first_player.health, 94)
        self.assertEqual(second_player.health, 94)
        self.assertEqual(first_player.fatigue_damage, 3)
        self.assertEqual(second_player.fatigue_damage, 3)
        self.assertEqual(battle.next_nightfall_fatigue_time, 20.0)

    def test_nightfall_fatigue_triggers_at_most_once_when_crossing_ticks(self):
        first_player = PlayerState(player_id=0, health=100)
        second_player = PlayerState(player_id=1, health=100)
        battle = BattleState(
            frame=16,
            time=16.0,
            players=[first_player, second_player],
        )

        battle.run(max_frames=1, frame_delta=2.0)

        self.assertEqual(battle.frame, 17)
        self.assertEqual(battle.time, 18.0)
        self.assertEqual(first_player.health, 99)
        self.assertEqual(second_player.health, 99)
        self.assertEqual(first_player.fatigue_damage, 1)
        self.assertEqual(second_player.fatigue_damage, 1)
        self.assertEqual(battle.next_nightfall_fatigue_time, 18.0)

    def test_players_keep_independent_fatigue_damage(self):
        first_player = PlayerState(
            player_id=0,
            health=100,
            fatigue_damage=8,
        )
        second_player = PlayerState(player_id=1, health=100)
        battle = BattleState(
            frame=16,
            time=16.0,
            frame_delta=1.0,
            players=[first_player, second_player],
        )

        battle.step()

        self.assertEqual(first_player.fatigue_damage, 9)
        self.assertEqual(first_player.health, 91)
        self.assertEqual(second_player.fatigue_damage, 1)
        self.assertEqual(second_player.health, 99)

    def test_fatigue_consumes_block_before_health(self):
        first_player = PlayerState(player_id=0, health=10)
        target = PlayerState(player_id=1, health=10, block=2)
        battle = BattleState(players=[first_player, target])

        first_damage = battle.inflict_fatigue(
            target,
            nightfall=False,
        )
        second_damage = battle.inflict_fatigue(
            target,
            nightfall=False,
        )

        self.assertEqual(first_damage, 1)
        self.assertEqual(second_damage, 2)
        self.assertEqual(target.fatigue_damage, 2)
        self.assertEqual(target.block, 0)
        self.assertEqual(target.health, 9)

    def test_opponent_takes_nightfall_fatigue_before_player(self):
        target_order = []

        class RecordingFatigueBattleState(BattleState):
            def inflict_fatigue(self, target, *, nightfall):
                target_order.append(target.player_id)
                return super().inflict_fatigue(
                    target,
                    nightfall=nightfall,
                )

        first_player = PlayerState(player_id=0, health=100)
        second_player = PlayerState(player_id=1, health=100)
        battle = RecordingFatigueBattleState(
            frame=16,
            time=16.0,
            frame_delta=1.0,
            players=[first_player, second_player],
        )

        battle.step()

        self.assertEqual(target_order, [1, 0])

    def test_player_wins_lethal_nightfall_fatigue_race(self):
        first_player = PlayerState(player_id=0, health=1)
        second_player = PlayerState(player_id=1, health=1)
        battle = BattleState(
            frame=16,
            time=16.0,
            frame_delta=1.0,
            players=[first_player, second_player],
        )

        battle.step()

        self.assertEqual(battle.winner, 0)
        self.assertEqual(battle.frame, 17)
        self.assertEqual(battle.time, 17.0)
        self.assertEqual(first_player.health, 1)
        self.assertEqual(first_player.fatigue_damage, 0)
        self.assertEqual(second_player.health, 0)
        self.assertEqual(second_player.fatigue_damage, 1)

    def test_lethal_fatigue_stops_remaining_targets_and_ticks(self):
        first_player = PlayerState(player_id=0, health=1)
        second_player = PlayerState(player_id=1, health=1)
        battle = BattleState(
            frame=16,
            time=16.0,
            frame_delta=3.0,
            players=[first_player, second_player],
        )

        battle.step()

        self.assertEqual(battle.winner, 0)
        self.assertEqual(battle.frame, 17)
        self.assertEqual(battle.time, 19.0)
        self.assertEqual(battle.next_nightfall_fatigue_time, 18.0)
        self.assertEqual(first_player.fatigue_damage, 0)
        self.assertEqual(second_player.fatigue_damage, 1)

    def test_regeneration_tick_heals_current_stacks(self):
        first = PlayerState(player_id=0, health=5, max_health=10)
        second = PlayerState(player_id=1, health=10, max_health=10)
        first.buffs.Regeneration = 3
        battle = BattleState(players=[first, second])

        self.assertEqual(battle._apply_regeneration_tick(first), 3)
        first.buffs.Regeneration = 4
        self.assertEqual(battle._apply_regeneration_tick(first), 2)
        self.assertEqual(first.health, 10)

    def test_poison_tick_consumes_block_before_health(self):
        first = PlayerState(player_id=0, health=10, block=2)
        second = PlayerState(player_id=1, health=10)
        first.debuffs.Poison = 5
        battle = BattleState(players=[first, second])

        self.assertEqual(battle._apply_poison_tick(first), 5)
        self.assertEqual(first.block, 0)
        self.assertEqual(first.health, 7)

    def test_regeneration_and_poison_first_tick_times(self):
        first = PlayerState(player_id=0, health=5, max_health=10)
        second = PlayerState(player_id=1, health=10, max_health=10)
        first.buffs.Regeneration = 1
        first.debuffs.Poison = 2
        battle = BattleState(
            players=[first, second],
            frame_delta=0.5,
        )

        battle.step()
        self.assertEqual(first.health, 5)
        battle.step()
        self.assertEqual(first.health, 6)
        battle.step()
        self.assertEqual(first.health, 6)
        battle.step()
        self.assertEqual(first.health, 4)

    def test_status_clocks_advance_when_stacks_are_zero(self):
        first = PlayerState(player_id=0, health=10)
        second = PlayerState(player_id=1, health=10)
        battle = BattleState(players=[first, second])

        battle.run(max_frames=4, frame_delta=1.0)

        self.assertEqual(battle.next_regeneration_time, 5.0)
        self.assertEqual(battle.next_poison_time, 6.0)

    def test_gaining_status_does_not_reset_global_clock(self):
        first = PlayerState(player_id=0, health=5, max_health=10)
        second = PlayerState(player_id=1, health=10, max_health=10)
        battle = BattleState(players=[first, second], frame_delta=1.0)

        battle.step()
        first.buffs.Regeneration = 2
        battle.step()
        self.assertEqual(first.health, 5)
        battle.step()
        self.assertEqual(first.health, 7)

        first.debuffs.Poison = 1
        battle.step()
        self.assertEqual(first.health, 6)

    def test_system_clocks_trigger_at_most_once_per_frame(self):
        first = PlayerState(player_id=0, health=10, max_health=20)
        second = PlayerState(player_id=1, health=10, max_health=20)
        first.buffs.Regeneration = 1
        first.debuffs.Poison = 1
        battle = BattleState(
            players=[first, second],
            frame_delta=6.0,
        )

        battle.step()

        self.assertEqual(first.health, 10)
        self.assertEqual(battle.next_regeneration_time, 3.0)
        self.assertEqual(battle.next_poison_time, 4.0)
        self.assertEqual(battle.next_nightfall_fatigue_time, 17.0)

    def test_poison_targets_enemy_before_player_and_stops_on_death(self):
        first = PlayerState(player_id=0, health=1)
        second = PlayerState(player_id=1, health=1)
        first.debuffs.Poison = 1
        second.debuffs.Poison = 1
        battle = BattleState(
            time=1.0,
            frame_delta=1.0,
            players=[first, second],
            next_regeneration_time=3.0,
        )

        battle.step()

        self.assertEqual(battle.winner, 0)
        self.assertEqual(first.health, 1)
        self.assertEqual(second.health, 0)
        self.assertEqual(battle.next_poison_time, 4.0)

    def test_regeneration_and_fatigue_use_role_interleaving(self):
        order = []

        class RecordingBattleState(BattleState):
            def _apply_regeneration_tick(self, target):
                order.append(("regeneration", target.player_id))
                return 0

            def inflict_fatigue(self, target, *, nightfall):
                order.append(("fatigue", target.player_id))
                return 0

        first = PlayerState(player_id=0, health=10)
        second = PlayerState(player_id=1, health=10)
        battle = RecordingBattleState(
            time=16.0,
            frame_delta=1.0,
            players=[first, second],
            next_regeneration_time=17.0,
            next_poison_time=18.0,
        )

        battle.step()

        self.assertEqual(
            order,
            [
                ("regeneration", 1),
                ("fatigue", 1),
                ("fatigue", 0),
                ("regeneration", 0),
            ],
        )

    def test_poison_and_fatigue_use_role_interleaving(self):
        order = []

        class RecordingBattleState(BattleState):
            def _apply_poison_tick(self, target):
                order.append(("poison", target.player_id))
                return 0

            def inflict_fatigue(self, target, *, nightfall):
                order.append(("fatigue", target.player_id))
                return 0

        first = PlayerState(player_id=0, health=10)
        second = PlayerState(player_id=1, health=10)
        battle = RecordingBattleState(
            time=17.0,
            frame_delta=1.0,
            players=[first, second],
            next_regeneration_time=19.0,
            next_poison_time=18.0,
            next_nightfall_fatigue_time=18.0,
        )

        battle.step()

        self.assertEqual(
            order,
            [
                ("poison", 1),
                ("fatigue", 1),
                ("fatigue", 0),
                ("poison", 0),
            ],
        )

    def test_system_trigger_check_never_rewinds_battle_time(self):
        observed_times = []

        class RecordingBattleState(BattleState):
            def _apply_regeneration_tick(self, target):
                observed_times.append(self.time)
                return 0

            def _apply_poison_tick(self, target):
                observed_times.append(self.time)
                return 0

            def inflict_fatigue(self, target, *, nightfall):
                observed_times.append(self.time)
                return 0

        first = PlayerState(player_id=0, health=10)
        second = PlayerState(player_id=1, health=10)
        battle = RecordingBattleState(
            time=16.0,
            frame_delta=3.0,
            players=[first, second],
        )

        battle.step()

        self.assertEqual(observed_times, [19.0] * 6)
        self.assertEqual(battle.time, 19.0)

    def test_system_tick_timers_advance_before_lethal_effect(self):
        first = PlayerState(player_id=0, health=10)
        second = PlayerState(player_id=1, health=1)
        second.debuffs.Poison = 1
        battle = BattleState(
            time=1.0,
            frame_delta=1.0,
            players=[first, second],
            next_regeneration_time=3.0,
        )

        battle.step()

        self.assertEqual(battle.winner, 0)
        self.assertEqual(battle.next_poison_time, 4.0)
        self.assertEqual(battle.next_regeneration_time, 3.0)

    def test_non_two_player_system_state_only_advances_time(self):
        player = PlayerState(player_id=0, health=10)
        battle = BattleState(players=[player], frame_delta=1.0)

        battle.step()

        self.assertEqual(battle.time, 1.0)
        self.assertEqual(
            battle.next_regeneration_time,
            FIRST_REGENERATION_TIME,
        )
        self.assertEqual(battle.next_poison_time, FIRST_POISON_TIME)

    def test_battle_state_and_run_default_to_thirty_frames_per_second(self):
        first = PlayerState(player_id=0, health=10)
        second = PlayerState(player_id=1, health=10)
        battle = BattleState(players=[first, second])

        self.assertEqual(battle.frame_delta, 1.0 / 30.0)
        battle.run(max_frames=1)
        self.assertEqual(battle.frame_delta, 1.0 / 30.0)
        self.assertEqual(battle.time, 1.0 / 30.0)
        self.assertEqual(STATUS_TICK_INTERVAL, 2.0)

    def test_item_kill_before_frame_end_skips_nightfall_fatigue(self):
        def deal_lethal_damage(item, trigger_results, context):
            context.battle_state.commit_health_reduction(
                context.opponent,
                blocked_damage=0,
                health_damage=10,
            )
            return False

        active_item = DecisionItem(
            trigger_results=[True],
            effect_results=[True],
            decision=deal_lethal_damage,
            item_key="active1",
            player_id=0,
            is_active_item=True,
        )
        first_player = PlayerState(
            player_id=0,
            health=10,
            items={"active1": active_item},
        )
        second_player = PlayerState(player_id=1, health=10)
        battle = BattleState(
            frame=16,
            time=16.0,
            players=[first_player, second_player],
            active_items=[active_item],
        )

        battle.step()

        self.assertEqual(battle.winner, 0)
        self.assertEqual(battle.frame, 16)
        self.assertEqual(battle.time, 16.0)
        self.assertEqual(battle.next_nightfall_fatigue_time, 17.0)
        self.assertEqual(first_player.fatigue_damage, 0)
        self.assertEqual(second_player.fatigue_damage, 0)

    def test_lethal_health_reduction_stops_remaining_active_items(self):
        log = []

        def deal_lethal_damage(item, trigger_results, context):
            log.append("lethal")
            context.battle_state.commit_health_reduction(
                context.opponent,
                blocked_damage=0,
                health_damage=10,
            )
            log.append("unreachable")
            return False

        first_item = DecisionItem(
            trigger_results=[True],
            effect_results=[True],
            decision=deal_lethal_damage,
            item_key="first1",
            player_id=0,
            is_active_item=True,
        )
        second_item = RecordingItem(
            "second",
            log,
            item_key="second1",
            player_id=1,
            is_active_item=True,
        )
        first_player = PlayerState(
            player_id=0,
            health=10,
            items={"first1": first_item},
        )
        second_player = PlayerState(
            player_id=1,
            health=10,
            items={"second1": second_item},
        )
        battle = BattleState(
            players=[first_player, second_player],
            active_items=[first_item, second_item],
        )

        battle.step()

        self.assertEqual(log, ["lethal"])
        self.assertEqual(battle.winner, 0)
        self.assertEqual(battle.frame, 0)
        self.assertEqual(battle.time, 0.0)

    def test_battle_state_sets_winner_when_one_player_remains_alive(self):
        winner = PlayerState(player_id=0, health=10)
        loser = PlayerState(player_id=1, health=0)
        battle = BattleState(players=[winner, loser])

        battle.check_battle_end()

        self.assertEqual(battle.winner, 0)

    def test_evaluate_layout_is_declared_but_not_scored_yet(self):
        with self.assertRaises(NotImplementedError):
            evaluate_layout([], opponent=None)


if __name__ == "__main__":
    unittest.main()
