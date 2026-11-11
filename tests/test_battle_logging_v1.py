import ast
import json
import unittest
from pathlib import Path

from battle_module_v1 import (
    ATTACK_PHASE_PRE_TAKE_DAMAGE,
    ATTACK_PHASE_CHARACTER_ATTACKED,
    AttackEvent,
    BattleState,
    BuffSlot,
    DebuffSlot,
    ItemActivationContext,
    PlayerState,
    _BattleFinishedSignal,
)
from item_effects_v1 import Effect
from item_triggers_v1 import Trigger
from item_factory_registry_v1 import (
    Banana,
    BattleItem,
    Broom,
    Flame,
    Garlic,
    Goobling,
    HealingHerbs,
    MagicForDummies,
    Pan,
    PocketSand,
    Rat,
    ShinyShell,
    Shortbow,
    Stone,
    Twine,
    WalrusTusk,
    WandOfEquilibrium,
    Whetstone,
    WoodenBuckler,
    WoodenSword,
)
from main_v1 import _build_success_result, run_battle_from_config


class NeverTrigger(Trigger):
    def update(self, context):
        return False


class NoopEffect(Effect):
    def apply(self, context):
        return True


class TestSourceItem(BattleItem):
    def __init__(
        self,
        *,
        item_id="test_source",
        item_key="test_source1",
        player_id=0,
        item_types=(),
        icon_types=(),
    ):
        super().__init__(
            item_id=item_id,
            item_key=item_key,
            player_id=player_id,
            triggers=[NeverTrigger()],
            effects=[NoopEffect()],
            item_types=item_types,
            icon_types=icon_types,
        )

    def run_effect(self, trigger_results, context):
        return


class SequenceRng:
    def shuffle(self, items):
        # These tests isolate attack/log ordering from preparation randomness.
        pass

    def __init__(self, random_values=(), randint_values=()):
        self.random_values = list(random_values)
        self.randint_values = list(randint_values)

    def choice(self, values):
        return values[0]

    def random(self):
        if not self.random_values:
            raise AssertionError("unexpected random() call")
        return self.random_values.pop(0)

    def randint(self, lower, upper):
        if not self.randint_values:
            raise AssertionError("unexpected randint() call")
        value = self.randint_values.pop(0)
        if not lower <= value <= upper:
            raise AssertionError("randint value outside requested range")
        return value


def make_item_context(
    item,
    *,
    owner_health=20,
    owner_max_health=20,
    owner_stamina=5.0,
    owner_max_stamina=5.0,
    owner_buffs=None,
    opponent_health=20,
    opponent_max_health=20,
    opponent_stamina=5.0,
    opponent_max_stamina=5.0,
    opponent_block=0,
    rng=None,
):
    owner = PlayerState(
        player_id=item.player_id,
        health=owner_health,
        max_health=owner_max_health,
        stamina=owner_stamina,
        max_stamina=owner_max_stamina,
        buffs=owner_buffs if owner_buffs is not None else BuffSlot(),
        items={item.item_key: item},
    )
    opponent = PlayerState(
        player_id=1 if item.player_id == 0 else 0,
        health=opponent_health,
        max_health=opponent_max_health,
        stamina=opponent_stamina,
        max_stamina=opponent_max_stamina,
        block=opponent_block,
    )
    state = BattleState(
        players=[owner, opponent],
        active_items=[item] if item.is_active_item else [],
        rng=rng or SequenceRng(),
    )
    return state, state.build_context(item)


def actions(state):
    return [entry["data"].get("action") for entry in state.log]


class BattleLoggingV1Test(unittest.TestCase):
    def test_builtin_log_payloads_do_not_define_player_state_snapshots(self):
        forbidden_keys = {
            "health_before",
            "health_after",
            "stamina_before",
            "stamina_after",
            "block_before",
            "block_after",
            "stacks_before",
            "stacks_after",
            "modifier_before",
            "modifier_after",
            "count_before",
            "count_after",
            "requested",
        }
        project_root = Path(__file__).resolve().parents[1]
        source_files = (
            "battle_module_v1.py",
            "item_effects_v1.py",
            "item_triggers_v1.py",
            "item_factory_registry_v1.py",
        )

        for source_file in source_files:
            tree = ast.parse(
                (project_root / source_file).read_text(encoding="utf-8")
            )
            literal_dict_keys = {
                key.value
                for node in ast.walk(tree)
                if isinstance(node, ast.Dict)
                for key in node.keys
                if isinstance(key, ast.Constant)
                and isinstance(key.value, str)
            }
            self.assertEqual(
                forbidden_keys & literal_dict_keys,
                set(),
                source_file,
            )
            for node in ast.walk(tree):
                if not isinstance(node, ast.Dict):
                    continue
                fields = {key.value: value for key, value in zip(node.keys, node.values)
                          if isinstance(key, ast.Constant) and isinstance(key.value, str)}
                if "actual" in fields:
                    action = fields.get("action")
                    self.assertIsInstance(action, ast.Constant, source_file)
                    self.assertIn(action.value,
                                  {"stack_change", "stack_resisted", "stack_protected"},
                                  source_file)

    def test_new_battle_states_have_independent_empty_logs(self):
        first = BattleState()
        second = BattleState()

        first.record_log("System", {"value": 1})

        self.assertEqual(len(first.log), 1)
        self.assertEqual(second.log, [])

    def test_record_log_autofills_source_timing_without_event(self):
        item = TestSourceItem()
        state = BattleState(frame=7, time=1.25)
        data = {"anything": {"nested": True}}

        handle = state.record_log(item, data)
        state.record_log("Poison", {"amount": 2})
        data["later"] = "not copied"

        self.assertIs(handle.battle_state, state)
        self.assertEqual(handle.sequence, 0)
        self.assertEqual(
            state.log[0],
            {
                "sequence": 0,
                "frame": 7,
                "time": 1.25,
                "source": {
                    "type": "item",
                    "player_id": 0,
                    "item_key": "test_source1",
                    "item_id": "test_source",
                },
                "data": {"anything": {"nested": True}},
            },
        )
        self.assertNotIn("event", state.log[0])
        self.assertEqual(
            state.log[1]["source"],
            {"type": "system", "name": "Poison"},
        )
        self.assertEqual(state.log[1]["sequence"], 1)




    def test_success_result_extracts_complete_log_without_aliasing(self):
        state = BattleState()
        state.record_log("System", {"first": 1})
        state.record_log("System", {"second": 2})

        result = _build_success_result(
            state,
            {"players": {}},
            "max_frames_reached",
        )

        self.assertEqual(result["log"], state.log)
        self.assertIsNot(result["log"], state.log)
        result["log"].append({"extra": True})
        self.assertEqual(len(state.log), 2)
        json.dumps(result)

    def test_run_result_uses_dynamic_log_even_with_reserved_flag_false(self):
        config = {
            "schema_version": "battle_run_v1",
            "settings": {
                "max_frames": 1,
                "frame_delta": 0.1,
                "collect_log": False,
            },
            "players": [
                {
                    "player_id": 0,
                    "health": 20,
                    "max_health": 20,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [
                        {
                            "item_id": "pocket_sand",
                            "x": 0,
                            "y": 0,
                            "rotation": 0,
                        }
                    ],
                },
                {
                    "player_id": 1,
                    "health": 20,
                    "max_health": 20,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [],
                },
            ],
        }

        result = run_battle_from_config(
            config,
            {"pocket_sand": PocketSand},
        )

        self.assertEqual(len(result["log"]), 3)
        self.assertEqual(
            result["log"][0]["data"]["action"],
            "stack_change",
        )

    def test_start_of_battle_items_log_effect_then_activation(self):
        cases = (
            (PocketSand, "inflict_debuff", "Blind", 1),
            (HealingHerbs, "gain_buff", "Regeneration", 2),
            (Flame, "gain_buff", "Heat", 1),
            (WalrusTusk, "gain_buff", "Spikes", 1),
        )

        for item_type, action, status_name, amount in cases:
            with self.subTest(item_type=item_type.__name__):
                item = item_type(item_key="item1", player_id=0)
                state, context = make_item_context(item, rng=SequenceRng(random_values=[0.9]))

                item.combatStart(context)

                self.assertEqual(actions(state), ["stack_change", action, "item_activation"])
                self.assertNotIn("event", state.log[0])
                self.assertEqual(state.log[0]["data"]["amount"], amount)
                data = state.log[1]["data"]
                self.assertEqual(data.get("buff", data.get("debuff")), status_name)
                self.assertEqual(data["stack_gained"], amount)
                self.assertEqual(data["final_stack_gained"], amount)
                self.assertEqual(data["event_kind"], "effect_attempt")
                self.assertFalse(data["contributes_to_stack_totals"])

    def test_shiny_shell_logs_capped_heal_then_activation(self):
        item = ShinyShell(item_key="shell1", player_id=0)
        state, context = make_item_context(item)

        item.run_effect([True], context)

        self.assertEqual(actions(state), ["heal", "item_activation"])
        self.assertEqual(state.log[0]["data"]["healing"], 5)
        self.assertEqual(state.log[0]["data"]["final_healing"], 0)

    def test_wand_logs_gain_conversion_and_activation_in_order(self):
        item = WandOfEquilibrium(item_key="wand1", player_id=0)
        state, context = make_item_context(
            item, owner_buffs=BuffSlot(Mana=9, Luck=10, Regeneration=10),
        )

        item.run_effect([True], context)

        self.assertEqual(
            actions(state),
            ["stack_change", "gain_buff", "stack_change", "use_buff",
             "stack_change", "gain_buff", "item_activation"],
        )
        self.assertEqual(state.log[1]["data"]["buff"], "Mana")
        self.assertEqual(state.log[3]["data"]["buff"], "Mana")
        self.assertEqual(state.log[5]["data"]["buff"], "Empower")
        self.assertTrue(state.log[2]["data"]["used"])
        self.assertEqual(state.log[2]["data"]["amount"], -1)
        self.assertEqual(state.log[4]["data"]["trigger_log_sequence"], 2)
        self.assertFalse(state.log[3]["data"]["contributes_to_stack_totals"])

    def test_magic_for_dummies_logs_failure_and_success_paths(self):
        failed_item = MagicForDummies(item_key="book1", player_id=0)
        failed_state, failed_context = make_item_context(failed_item)

        failed_item.prepare(failed_context)
        failed_item.run_effect([True], failed_context)

        self.assertEqual(actions(failed_state), ["use_buff", "item_activation"])
        self.assertFalse(failed_state.log[0]["data"]["success"])

        item = MagicForDummies(item_key="book2", player_id=0)
        state, context = make_item_context(item, owner_buffs=BuffSlot(Mana=1))

        item.prepare(context)
        item.run_effect([True], context)

        self.assertEqual(
            actions(state),
            ["stack_change", "use_buff", "gain_max_health", "item_activation"],
        )
        self.assertEqual(context.owner.max_health, 28)
        self.assertEqual(context.owner.health, 28)
        self.assertEqual(state.log[0]["data"]["amount"], -1)
        self.assertTrue(state.log[0]["data"]["used"])
        self.assertEqual(state.log[1]["data"]["event_kind"], "effect_attempt")
        self.assertFalse(state.log[1]["data"]["contributes_to_stack_totals"])
        self.assertEqual(state.log[2]["data"]["trigger_log_sequence"], 0)

    def test_whetstone_logs_modified_targets_and_empty_case(self):
        item = Whetstone(item_key="whetstone1", player_id=0)
        sword = WoodenSword(item_key="sword1", player_id=0)
        state, context = make_item_context(item)
        context.owner.items[sword.item_key] = sword
        item.add_linked_item(sword.item_key)

        item.combatStart(context)

        self.assertEqual(actions(state), ["modify_linked_weapon_damage", "item_activation"])
        targets = state.log[0]["data"]["targets"]
        self.assertEqual(targets[0]["item_key"], "sword1")
        self.assertEqual(targets[0]["damage_modifier_delta"], 1)
        self.assertNotIn("modifier_before", targets[0])
        self.assertNotIn("modifier_after", targets[0])

        empty_item = Whetstone(item_key="whetstone2", player_id=0)
        empty_state, empty_context = make_item_context(empty_item)
        empty_item.combatStart(empty_context)
        self.assertEqual(empty_state.log[0]["data"]["targets"], [])
        self.assertFalse(empty_state.log[0]["data"]["success"])

    def test_twine_logs_probability_failure_and_success(self):
        for roll, expected_actions in (
            (0.9, ["gain_max_health_check"]),
            (
                0.0,
                [
                    "gain_max_health_check",
                    "gain_max_health",
                    "item_activation",
                ],
            ),
        ):
            with self.subTest(roll=roll):
                item = Twine(item_key="twine1", player_id=0)
                source = TestSourceItem(
                    item_id="source",
                    item_key="source1",
                    player_id=0,
                )
                state, _ = make_item_context(
                    item,
                    rng=SequenceRng(random_values=[roll]),
                )
                state.players[0].items[source.item_key] = source
                item.add_marker_item("star", source.item_key)
                context = ItemActivationContext(
                    battle_state=state,
                    item=item,
                    owner=state.players[0],
                    opponent=state.players[1],
                    source_item=source,
                )

                item.prepare(context)
                item.activate_item(context)

                self.assertEqual(actions(state), expected_actions)
                self.assertEqual(
                    state.log[0]["data"]["source_item_key"],
                    "source1",
                )

    def test_goobling_logs_each_counter_step_then_heal_and_activation(self):
        item = Goobling(item_key="goobling1", player_id=0)
        source = TestSourceItem(
            item_id="source",
            item_key="source1",
            player_id=0,
        )
        state, _ = make_item_context(
            item,
            owner_health=10,
            owner_max_health=20,
        )
        state.players[0].items[source.item_key] = source
        item.add_marker_item("star", source.item_key)

        for _ in range(3):
            context = ItemActivationContext(
                battle_state=state,
                item=item,
                owner=state.players[0],
                opponent=state.players[1],
                source_item=source,
            )
            item.activate_item(context)

        self.assertEqual(
            actions(state),
            [
                "count_linked_item_activation",
                "count_linked_item_activation",
                "count_linked_item_activation",
                "heal",
                "item_activation",
            ],
        )
        self.assertFalse(state.log[0]["data"]["triggered"])
        self.assertTrue(state.log[2]["data"]["triggered"])
        self.assertEqual(state.log[2]["data"]["activation_count_delta"], -2)
        self.assertNotIn("count_before", state.log[2]["data"])
        self.assertNotIn("count_after", state.log[2]["data"])

    def test_wooden_buckler_logs_roll_reaction_and_activation(self):
        item = WoodenBuckler(item_key="buckler1", player_id=0)
        attack_source = TestSourceItem(
            item_id="attacker",
            item_key="attacker1",
            player_id=1,
        )
        state, _ = make_item_context(
            item,
            rng=SequenceRng(random_values=[0.1]),
        )
        state.players[1].items[attack_source.item_key] = attack_source
        event = AttackEvent(
            attacker=state.players[1],
            defender=state.players[0],
            source_item=attack_source,
            attack_types=("melee",),
            min_damage=5,
            max_damage=5,
            accuracy=100,
            hit=True,
            rolled_damage=5,
            pending_damage=5,
        )
        context = state.build_attack_reaction_context(
            item,
            ATTACK_PHASE_PRE_TAKE_DAMAGE,
            event,
        )

        item.activate_item(context.for_item(item))
        self.assertEqual(actions(state), ["on_attacked_check", "prevent_attack_damage"])
        self.assertEqual(state.players[1].stamina, 5.0)
        item.activate_item(state.build_attack_reaction_context(
            item, ATTACK_PHASE_CHARACTER_ATTACKED, event).for_item(item))

        self.assertEqual(
            actions(state),
            [
                "on_attacked_check",
                "prevent_attack_damage",
                "remove_stamina",
                "item_activation",
            ],
        )
        self.assertEqual(event.pending_damage, 5)
        self.assertEqual(state.players[1].stamina, 4.7)

    def test_broom_logs_opponent_miss_bonus(self):
        item = Broom(item_key="broom1", player_id=0)
        attack_source = TestSourceItem(
            item_id="attacker",
            item_key="attacker1",
            player_id=1,
        )
        state, _ = make_item_context(item)
        state.players[1].items[attack_source.item_key] = attack_source
        event = AttackEvent(
            attacker=state.players[1],
            defender=state.players[0],
            source_item=attack_source,
            attack_types=("ranged",),
            min_damage=1,
            max_damage=1,
            accuracy=0,
            hit=False,
        )
        context = state.build_attack_reaction_context(
            item,
            ATTACK_PHASE_CHARACTER_ATTACKED,
            event,
        )

        item.run_effect([False, True], context)

        self.assertEqual(actions(state), ["gain_miss_damage_bonus"])
        self.assertEqual(item.miss_damage_bonus, 2)

    def test_broom_logs_stamina_attack_blind_check_and_activation(self):
        item = Broom(item_key="broom1", player_id=0)
        state, context = make_item_context(
            item,
            rng=SequenceRng(
                random_values=[0.0, 0.5],
                randint_values=[3],
            ),
        )

        item.run_effect([True, False], context)

        self.assertEqual(
            actions(state),
            [
                "spend_stamina",
                "attack",
                "inflict_blind_check",
                "item_activation",
            ],
        )
        self.assertFalse(state.log[2]["data"]["success"])

    def test_basic_weapons_log_stamina_attack_and_activation(self):
        cases = (
            (WoodenSword, 1),
            (Shortbow, 2),
            (Pan, 5),
        )
        for item_type, rolled_damage in cases:
            with self.subTest(item_type=item_type.__name__):
                item = item_type(item_key="weapon1", player_id=0)
                state, context = make_item_context(
                    item,
                    rng=SequenceRng(
                        random_values=[0.0],
                        randint_values=[rolled_damage],
                    ),
                )

                item.run_effect([True], context)

                self.assertEqual(
                    actions(state),
                    ["spend_stamina", "attack", "item_activation"],
                )

    def test_stone_logs_attack_block_removal_and_activation(self):
        item = Stone(item_key="stone1", player_id=0)
        state, context = make_item_context(
            item,
            opponent_block=5,
            rng=SequenceRng(
                random_values=[0.0],
                randint_values=[2],
            ),
        )
        item.run_effect([True], context)

        self.assertEqual(
            actions(state),
            ["spend_stamina", "stack_change", "remove_block", "attack", "item_activation"],
        )
        self.assertEqual(state.log[0]["data"]["stamina_spent"], 0)
        self.assertEqual(state.log[1]["data"]["stack_name"], "Block")
        self.assertEqual(state.log[1]["data"]["amount"], -4)
        self.assertEqual(state.log[1]["data"]["target_player_id"], 1)
        self.assertFalse(state.log[1]["data"]["used"])
        self.assertEqual(state.log[2]["data"]["block_removed"], 4)
        self.assertEqual(state.log[2]["data"]["final_block_removed"], 4)
        self.assertEqual(state.log[2]["data"]["event_kind"], "effect_attempt")
        self.assertFalse(state.log[2]["data"]["contributes_to_stack_totals"])
        self.assertEqual(state.log[3]["data"]["final_block_damage"], 1)
        self.assertEqual(state.log[3]["data"]["final_health_damage"], 1)
        self.assertEqual((context.opponent.block, context.opponent.health), (0, 19))

    def test_banana_logs_capped_heal_stamina_and_activation(self):
        item = Banana(item_key="banana1", player_id=0)
        state, context = make_item_context(item)

        item.run_effect([True], context)

        self.assertEqual(
            actions(state),
            ["heal", "restore_stamina", "item_activation"],
        )
        self.assertEqual(state.log[0]["data"]["healing"], 4)
        self.assertEqual(state.log[0]["data"]["final_healing"], 0)
        self.assertEqual(state.log[1]["data"]["stamina_generated"], 1.0)
        self.assertEqual(
            state.log[1]["data"]["final_stamina_generated"],
            0.0,
        )

    def test_garlic_logs_block_roll_zero_removal_and_activation(self):
        item = Garlic(item_key="garlic1", player_id=0)
        state, context = make_item_context(
            item,
            rng=SequenceRng(random_values=[0.0]),
        )

        item.run_effect([True], context)

        self.assertEqual(
            actions(state),
            [
                "stack_change",
                "gain_block",
                "remove_vampirism_check",
                "remove_buff",
                "item_activation",
            ],
        )
        self.assertEqual(state.log[0]["data"]["stack_name"], "Block")
        self.assertEqual(state.log[0]["data"]["amount"], 3)
        self.assertEqual(state.log[0]["data"]["target_player_id"], 0)
        self.assertEqual(state.log[1]["data"]["event_kind"], "effect_attempt")
        self.assertFalse(state.log[1]["data"]["contributes_to_stack_totals"])
        self.assertEqual(state.log[3]["data"]["stack_removed"], 1)
        self.assertEqual(state.log[3]["data"]["final_stack_removed"], 0)
        self.assertFalse(state.log[3]["data"]["success"])

    def test_rat_logs_independent_proc_checks_after_attack(self):
        item = Rat(item_key="rat1", player_id=0)
        state, context = make_item_context(
            item,
            rng=SequenceRng(
                random_values=[0.0, 0.9, 0.5],
                randint_values=[5],
            ),
        )

        item.run_effect([True], context)

        self.assertEqual(
            actions(state),
            [
                "attack",
                "inflict_poison_check",
                "stack_change",
                "inflict_debuff",
                "inflict_blind_check",
                "item_activation",
            ],
        )
        self.assertTrue(state.log[1]["data"]["success"])
        self.assertFalse(state.log[4]["data"]["success"])

    def test_attack_log_precedes_miss_reaction(self):
        broom = Broom(item_key="broom1", player_id=0)
        attack_source = TestSourceItem(
            item_id="attacker",
            item_key="attacker1",
            player_id=1,
        )
        state, _ = make_item_context(
            broom,
            rng=SequenceRng(random_values=[0.5]),
        )
        state.players[1].items[attack_source.item_key] = attack_source
        state.prepareItems()
        parent = state.record_log(attack_source, {"action": "upstream_effect"})
        event = AttackEvent(
            attacker=state.players[1],
            defender=state.players[0],
            source_item=attack_source,
            attack_types=("ranged",),
            min_damage=1,
            max_damage=1,
            accuracy=0,
            trigger_log_handle=parent,
        )

        state.resolve_attack(event)

        self.assertEqual(
            actions(state),
            ["upstream_effect", "attack", "gain_miss_damage_bonus"],
        )
        self.assertFalse(state.log[1]["data"]["hit"])
        self.assertEqual(
            state.log[1]["data"],
            {
                "action": "attack",
                "target_player_id": 0,
                "attack_types": ["ranged"],
                "hit": False,
                "trigger_log_sequence": parent.sequence,
            },
        )
        self.assertEqual(event.log_handle.sequence, 1)
        self.assertEqual(broom.miss_damage_bonus, 2)

    def test_lethal_attack_completes_log_before_stop_signal(self):
        item = Stone(item_key="stone1", player_id=0)
        state, context = make_item_context(
            item,
            opponent_health=1,
            opponent_max_health=1,
            rng=SequenceRng(
                random_values=[0.0],
                randint_values=[2],
            ),
        )

        item.run_effect([True], context)
        with self.assertRaises(_BattleFinishedSignal):
            state.stop_if_battle_ended()

        self.assertEqual(actions(state), ["spend_stamina", "remove_block", "attack"])
        self.assertEqual(
            state.log[2]["data"]["final_block_damage"],
            0,
        )
        self.assertEqual(
            state.log[2]["data"]["final_health_damage"],
            2,
        )

    def test_attack_and_spikes_complete_separate_damage_logs(self):
        source = TestSourceItem(
            item_id="attacker",
            item_key="attacker1",
            player_id=0,
        )
        attacker = PlayerState(
            player_id=0,
            health=10,
            max_health=10,
            items={source.item_key: source},
        )
        defender = PlayerState(
            player_id=1,
            health=10,
            max_health=10,
            buffs=BuffSlot(Spikes=2),
        )
        state = BattleState(
            players=[attacker, defender],
            rng=SequenceRng(
                random_values=[0.0],
                randint_values=[5, 2],
            ),
        )
        event = AttackEvent(
            attacker=attacker,
            defender=defender,
            source_item=source,
            attack_types=("melee",),
            min_damage=5,
            max_damage=5,
            accuracy=100,
        )

        state.resolve_attack(event)

        self.assertEqual(actions(state), ["attack", "spikes_damage"])
        self.assertEqual(state.log[0]["data"]["health_damage"], 5)
        self.assertEqual(state.log[0]["data"]["final_health_damage"], 5)
        self.assertEqual(state.log[1]["data"]["health_damage"], 2)
        self.assertEqual(state.log[1]["data"]["final_health_damage"], 2)

    def test_system_status_logs_use_automatic_sources(self):
        target = PlayerState(
            player_id=0,
            health=10,
            max_health=10,
            stamina=5.0,
            max_stamina=5.0,
            buffs=BuffSlot(Regeneration=2),
            debuffs=DebuffSlot(Poison=1),
        )
        state = BattleState(players=[target, PlayerState(player_id=1, health=10, max_health=10)])

        state._apply_regeneration_tick(target)
        state._apply_poison_tick(target)
        state.inflict_fatigue(target, nightfall=True)

        self.assertEqual(
            [entry["source"]["name"] for entry in state.log],
            ["Regeneration", "Poison", "Fatigue"],
        )
        self.assertEqual(state.log[0]["data"]["healing"], 2)
        self.assertEqual(state.log[0]["data"]["final_healing"], 0)
        self.assertEqual(state.log[1]["data"]["block_damage"], 0)
        self.assertEqual(state.log[1]["data"]["health_damage"], 1)
        self.assertEqual(state.log[2]["data"]["fatigue_damage_delta"], 1)
        self.assertNotIn("event", state.log[0])


if __name__ == "__main__":
    unittest.main()
