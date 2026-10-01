import unittest

from battle_module_v1 import (
    ATTACK_PHASE_ON_ATTACKED,
    AttackEvent,
    AttackReactionContext,
    BattleContext,
    BattleItem,
    BattleState,
    Effect,
    ItemActivationContext,
    PlayerState,
    Trigger,
)
from item_factory_registry_v1 import Goobling, WoodenSword


class AlwaysTrigger(Trigger):
    def update(self, context):
        return True


class NoOpEffect(Effect):
    def apply(self, context):
        return True


class RecordingItem(BattleItem):
    def __init__(self, item_key, player_id, callback=None):
        super().__init__(
            item_key=item_key,
            player_id=player_id,
            triggers=[AlwaysTrigger(), AlwaysTrigger()],
            effects=[NoOpEffect()],
        )
        self.calls = []
        self.callback = callback

    def run_effect(self, trigger_results, context):
        self.calls.append((context, list(trigger_results)))
        if any(trigger_results) and self.callback is not None:
            self.callback(context)


class EventBusContextV1Test(unittest.TestCase):
    def setUp(self):
        self.source = RecordingItem("source1", 0)
        self.same_side = RecordingItem("same1", 0)
        self.other_side = RecordingItem("other1", 1)
        self.owner = PlayerState(
            player_id=0,
            health=20,
            max_health=20,
            items={"source1": self.source, "same1": self.same_side},
        )
        self.opponent = PlayerState(
            player_id=1,
            health=20,
            max_health=20,
            items={"other1": self.other_side},
        )
        self.battle = BattleState(players=[self.owner, self.opponent])

    def make_attack_event(self):
        return AttackEvent(
            attacker=self.owner,
            defender=self.opponent,
            source_item=self.source,
            attack_types=("melee",),
            min_damage=20,
            max_damage=20,
            accuracy=100,
            hit=True,
            pending_damage=20,
        )

    def make_activation_context(self):
        return ItemActivationContext(
            battle_state=self.battle,
            item=self.source,
            owner=self.owner,
            opponent=self.opponent,
            source_item=self.source,
        )

    def test_for_item_preserves_all_context_types_and_switches_perspective(self):
        event = self.make_attack_event()
        contexts = [
            self.battle.build_context(self.source),
            self.make_activation_context(),
            self.battle.build_attack_reaction_context(
                self.source, ATTACK_PHASE_ON_ATTACKED, event,
            ),
        ]
        for original in contexts:
            for item, owner, opponent in (
                (self.same_side, self.owner, self.opponent),
                (self.other_side, self.opponent, self.owner),
            ):
                with self.subTest(context=type(original).__name__, item=item.item_key):
                    adapted = original.for_item(item)
                    self.assertIs(type(adapted), type(original))
                    self.assertIsNot(adapted, original)
                    self.assertIs(adapted.item, item)
                    self.assertIs(adapted.owner, owner)
                    self.assertIs(adapted.opponent, opponent)
                    self.assertIs(adapted.battle_state, self.battle)
                    if isinstance(original, ItemActivationContext):
                        self.assertIs(adapted.source_item, self.source)
                    if isinstance(original, AttackReactionContext):
                        self.assertIs(adapted.attack_event, event)
                        self.assertEqual(adapted.attack_phase, ATTACK_PHASE_ON_ATTACKED)
                    self.assertIs(original.item, self.source)
                    self.assertIs(original.owner, self.owner)
                    self.assertIs(original.opponent, self.opponent)

    def test_for_item_rejects_unknown_player(self):
        unknown = RecordingItem("unknown1", 2)
        with self.assertRaisesRegex(ValueError, "unknown player_id"):
            self.make_activation_context().for_item(unknown)

    def test_activation_listeners_receive_independent_contexts_in_order(self):
        order = []
        self.same_side.callback = lambda context: order.append(context.item.item_key)
        self.other_side.callback = lambda context: order.append(context.item.item_key)
        self.battle.connect(self.source, "item_activation", (self.same_side, 1))
        self.battle.connect(self.source, "item_activation", (self.other_side, 0))
        original = self.make_activation_context()

        self.battle.emit_signal(self.source, "item_activation", original)

        self.assertEqual(order, ["same1", "other1"])
        same_context, same_results = self.same_side.calls[0]
        other_context, other_results = self.other_side.calls[0]
        self.assertIsNot(same_context, other_context)
        self.assertIsNot(same_context, original)
        self.assertIsNot(other_context, original)
        self.assertIs(same_context.owner, self.owner)
        self.assertIs(other_context.owner, self.opponent)
        self.assertIs(same_context.source_item, self.source)
        self.assertIs(other_context.source_item, self.source)
        self.assertEqual(same_results, [False, True])
        self.assertEqual(other_results, [True, False])
        self.assertIs(original.item, self.source)

    def test_attack_listeners_accumulate_changes_on_the_same_event(self):
        order = []

        def reduce_three(context):
            order.append("first")
            context.attack_event.pending_damage -= 3

        def reduce_five(context):
            order.append("second")
            context.attack_event.pending_damage -= 5

        self.same_side.callback = reduce_three
        self.other_side.callback = reduce_five
        self.battle.connect(self.owner, ATTACK_PHASE_ON_ATTACKED, (self.same_side, 0))
        self.battle.connect(self.owner, ATTACK_PHASE_ON_ATTACKED, (self.other_side, 0))
        event = self.make_attack_event()
        original = self.battle.build_attack_reaction_context(
            self.source, ATTACK_PHASE_ON_ATTACKED, event,
        )

        self.battle.emit_signal(self.owner, ATTACK_PHASE_ON_ATTACKED, original)

        self.assertEqual(order, ["first", "second"])
        self.assertEqual(event.pending_damage, 12)
        for item in (self.same_side, self.other_side):
            context = item.calls[0][0]
            self.assertIsInstance(context, AttackReactionContext)
            self.assertIs(context.attack_event, event)
            self.assertEqual(context.attack_phase, ATTACK_PHASE_ON_ATTACKED)

    def test_nested_activation_preserves_outer_source_and_execution_order(self):
        order = []
        nested = RecordingItem("nested1", 0)
        self.owner.items[nested.item_key] = nested

        def emit_nested(context):
            order.append(("first", context.source_item))
            self.same_side.emit_activation(context)
            order.append(("resume", context.source_item))

        self.same_side.callback = emit_nested
        nested.callback = lambda context: order.append(("nested", context.source_item))
        self.other_side.callback = lambda context: order.append(("last", context.source_item))
        self.battle.connect(self.source, "item_activation", (self.same_side, 0))
        self.battle.connect(self.source, "item_activation", (self.other_side, 0))
        self.battle.connect(self.same_side, "item_activation", (nested, 0))
        original = self.make_activation_context()

        self.battle.emit_signal(self.source, "item_activation", original)

        self.assertEqual(order, [
            ("first", self.source),
            ("nested", self.same_side),
            ("resume", self.source),
            ("last", self.source),
        ])
        self.assertIs(original.source_item, self.source)
        self.assertIs(original.item, self.source)

    def test_signal_without_payload_builds_listener_context(self):
        for item in (self.same_side, self.other_side):
            self.battle.connect(None, "start_of_battle", (item, 0))

        self.battle.emit_signal(None, "start_of_battle")

        for item, owner, opponent in (
            (self.same_side, self.owner, self.opponent),
            (self.other_side, self.opponent, self.owner),
        ):
            context = item.calls[0][0]
            self.assertIs(type(context), BattleContext)
            self.assertIs(context.item, item)
            self.assertIs(context.owner, owner)
            self.assertIs(context.opponent, opponent)

    def test_signal_rejects_context_from_another_battle_before_dispatch(self):
        other_battle = BattleState(players=[self.owner, self.opponent])
        foreign_context = other_battle.build_context(self.source)
        self.battle.connect(self.source, "item_activation", (self.same_side, 0))

        with self.assertRaisesRegex(ValueError, "another battle"):
            self.battle.emit_signal(self.source, "item_activation", foreign_context)

        self.assertEqual(self.same_side.calls, [])

    def test_prepared_sword_activation_advances_goobling_and_preserves_log_source(self):
        sword = WoodenSword(item_key="sword1", player_id=0)
        goobling = Goobling(item_key="goobling1", player_id=0)
        goobling.add_marker_item("star", sword.item_key)
        self.owner.items = {sword.item_key: sword, goobling.item_key: goobling}
        self.owner.health = 20
        self.owner.max_health = 30
        self.battle.prepareItems()

        for _ in range(3):
            sword.emit_activation(self.battle.build_context(sword))

        self.assertEqual(self.owner.health, 24)
        self.assertEqual(goobling.triggers[0].activation_count, 0)
        counting_logs = [
            entry["data"] for entry in self.battle.log
            if entry["data"]["action"] == "count_linked_item_activation"
        ]
        self.assertEqual(len(counting_logs), 3)
        for entry in counting_logs:
            self.assertEqual(entry["source_item_key"], sword.item_key)
            self.assertEqual(entry["source_item_id"], sword.item_id)

    def test_activation_emitted_from_attack_context_creates_new_activation_context(self):
        event = self.make_attack_event()
        attack_context = self.battle.build_attack_reaction_context(
            self.source, ATTACK_PHASE_ON_ATTACKED, event,
        )
        self.battle.connect(self.source, "item_activation", (self.same_side, 0))

        self.source.emit_activation(attack_context)

        context = self.same_side.calls[0][0]
        self.assertIs(type(context), ItemActivationContext)
        self.assertIs(context.source_item, self.source)
        self.assertIs(context.item, self.same_side)
        self.assertFalse(hasattr(context, "attack_event"))
        self.assertIs(attack_context.attack_event, event)
        self.assertIs(attack_context.item, self.source)
        self.assertEqual(self.battle.log[0]["data"]["action"], "item_activation")


if __name__ == "__main__":
    unittest.main()
