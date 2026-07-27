import ast
import json
import unittest
from pathlib import Path

from battle_module_v1 import (
    ATTACK_PHASE_ON_ATTACKED,
    ATTACK_PHASE_ON_ATTACK_MISSED,
    AttackEvent,
    BattleItem,
    BattleState,
    Effect,
    ItemActivationContext,
    PlayerState,
    Trigger,
    _BattleFinishedSignal,
)
from item_factory_registry_v1 import (
    Banana,
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
    def __init__(self, random_values=(), randint_values=()):
        self.random_values = list(random_values)
        self.randint_values = list(randint_values)

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
    opponent_health=20,
    opponent_max_health=20,
    opponent_stamina=5.0,
    opponent_max_stamina=5.0,
    rng=None,
):
    owner = PlayerState(
        player_id=item.player_id,
        health=owner_health,
        max_health=owner_max_health,
        stamina=owner_stamina,
        max_stamina=owner_max_stamina,
        items={item.item_key: item},
    )
    opponent = PlayerState(
        player_id=1 if item.player_id == 0 else 0,
        health=opponent_health,
        max_health=opponent_max_health,
        stamina=opponent_stamina,
        max_stamina=opponent_max_stamina,
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
            "actual",
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

    def test_damage_log_handle_updates_only_its_exact_entry(self):
        target = PlayerState(
            player_id=0,
            health=10,
            max_health=10,
            block=3,
        )
        opponent = PlayerState(player_id=1, health=10, max_health=10)
        state = BattleState(players=[target, opponent])
        handle = state.record_log(
            "Damage",
            {
                "action": "damage",
                "target_player_id": 0,
                "block_damage": 1,
                "health_damage": 1,
            },
        )

        state.commit_health_reduction(
            target,
            1,
            1,
            log_handle=handle,
        )
        completed_data = dict(state.log[0]["data"])
        state.commit_health_reduction(target, 1, 2)

        self.assertEqual(state.log[0]["data"], completed_data)
        self.assertEqual(
            completed_data,
            {
                "action": "damage",
                "target_player_id": 0,
                "block_damage": 1,
                "health_damage": 1,
                "final_block_damage": 1,
                "final_health_damage": 1,
            },
        )

    def test_damage_log_handle_rejects_cross_battle_and_reuse(self):
        first_target = PlayerState(
            player_id=0,
            health=10,
            max_health=10,
        )
        first = BattleState(
            players=[
                first_target,
                PlayerState(player_id=1, health=10, max_health=10),
            ]
        )
        handle = first.record_log(
            "Damage",
            {
                "action": "damage",
                "target_player_id": 0,
                "block_damage": 0,
                "health_damage": 1,
            },
        )
        second_target = PlayerState(
            player_id=0,
            health=10,
            max_health=10,
        )
        second = BattleState(
            players=[
                second_target,
                PlayerState(player_id=1, health=10, max_health=10),
            ]
        )

        with self.assertRaisesRegex(ValueError, "another battle"):
            second.commit_health_reduction(
                second_target,
                0,
                1,
                log_handle=handle,
            )
        self.assertEqual(second_target.health, 10)

        with self.assertRaisesRegex(ValueError, "target does not match"):
            first.commit_health_reduction(
                first.players[1],
                0,
                1,
                log_handle=handle,
            )
        self.assertEqual(first.players[1].health, 10)

        first.commit_health_reduction(
            first_target,
            0,
            1,
            log_handle=handle,
        )
        with self.assertRaisesRegex(ValueError, "already complete"):
            first.commit_health_reduction(
                first_target,
                0,
                1,
                log_handle=handle,
            )
        self.assertEqual(first_target.health, 9)

    def test_damage_log_handle_rejects_stale_sequence(self):
        target = PlayerState(player_id=0, health=10, max_health=10)
        state = BattleState(
            players=[
                target,
                PlayerState(player_id=1, health=10, max_health=10),
            ]
        )
        handle = state.record_log(
            "Damage",
            {
                "action": "damage",
                "target_player_id": 0,
                "block_damage": 0,
                "health_damage": 1,
            },
        )
        state.log.clear()

        with self.assertRaisesRegex(ValueError, "stale"):
            state.commit_health_reduction(
                target,
                0,
                1,
                log_handle=handle,
            )
        self.assertEqual(target.health, 10)

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

        self.assertEqual(len(result["log"]), 1)
        self.assertEqual(
            result["log"][0]["data"]["action"],
            "inflict_debuff",
        )

    def test_start_of_battle_items_log_their_effect_without_activation(self):
        cases = (
            (PocketSand, "inflict_debuff", "Blind", 1),
            (HealingHerbs, "gain_buff", "Regeneration", 2),
            (Flame, "gain_buff", "Heat", 1),
            (WalrusTusk, "gain_buff", "Spikes", 1),
        )

        for item_type, action, status_name, amount in cases:
            with self.subTest(item_type=item_type.__name__):
                item = item_type(item_key="item1", player_id=0)
                state, context = make_item_context(item)

                item.run_effect([True], context)

                self.assertEqual(actions(state), [action])
                self.assertNotIn("event", state.log[0])
                data = state.log[0]["data"]
                self.assertEqual(data.get("buff", data.get("debuff")), status_name)
                self.assertEqual(data["stack_gained"], amount)
                self.assertEqual(data["final_stack_gained"], amount)

    def test_shiny_shell_logs_capped_heal_then_activation(self):
        item = ShinyShell(item_key="shell1", player_id=0)
        state, context = make_item_context(item)

        item.run_effect([True], context)

        self.assertEqual(actions(state), ["heal", "item_activation"])
        self.assertEqual(state.log[0]["data"]["healing"], 5)
        self.assertEqual(state.log[0]["data"]["final_healing"], 0)

    def test_wand_logs_gain_conversion_and_activation_in_order(self):
        item = WandOfEquilibrium(item_key="wand1", player_id=0)
        state, context = make_item_context(item)
        context.owner.buffs.Mana = 9
        context.owner.buffs.Luck = 10
        context.owner.buffs.Regeneration = 10

        item.run_effect([True], context)

        self.assertEqual(
            actions(state),
            ["gain_buff", "use_buff", "gain_buff", "item_activation"],
        )
        self.assertEqual(state.log[0]["data"]["buff"], "Mana")
        self.assertEqual(state.log[1]["data"]["buff"], "Mana")
        self.assertEqual(state.log[2]["data"]["buff"], "Empower")

    def test_magic_for_dummies_logs_failure_and_success_paths(self):
        failed_item = MagicForDummies(item_key="book1", player_id=0)
        failed_state, failed_context = make_item_context(failed_item)

        failed_item.run_effect([True], failed_context)

        self.assertEqual(actions(failed_state), ["use_buff"])
        self.assertFalse(failed_state.log[0]["data"]["success"])

        item = MagicForDummies(item_key="book2", player_id=0)
        state, context = make_item_context(item)
        context.owner.buffs.Mana = 1

        item.run_effect([True], context)

        self.assertEqual(
            actions(state),
            ["use_buff", "gain_max_health", "item_activation"],
        )
        self.assertEqual(context.owner.max_health, 28)
        self.assertEqual(context.owner.health, 28)

    def test_whetstone_logs_modified_targets_and_empty_case(self):
        item = Whetstone(item_key="whetstone1", player_id=0)
        sword = WoodenSword(item_key="sword1", player_id=0)
        state, context = make_item_context(item)
        context.owner.items[sword.item_key] = sword
        item.add_linked_item(sword.item_key)

        item.run_effect([True], context)

        self.assertEqual(actions(state), ["modify_linked_weapon_damage"])
        targets = state.log[0]["data"]["targets"]
        self.assertEqual(targets[0]["item_key"], "sword1")
        self.assertEqual(targets[0]["damage_modifier_delta"], 1)
        self.assertNotIn("modifier_before", targets[0])
        self.assertNotIn("modifier_after", targets[0])

        empty_item = Whetstone(item_key="whetstone2", player_id=0)
        empty_state, empty_context = make_item_context(empty_item)
        empty_item.run_effect([True], empty_context)
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
                context = state.build_item_activation_context(item, source)

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
            context = state.build_item_activation_context(item, source)
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
            ATTACK_PHASE_ON_ATTACKED,
            event,
        )

        item.activate_item(context)

        self.assertEqual(
            actions(state),
            [
                "on_attacked_check",
                "prevent_attack_damage",
                "remove_stamina",
                "item_activation",
            ],
        )
        self.assertEqual(event.pending_damage, 0)
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
            ATTACK_PHASE_ON_ATTACK_MISSED,
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
            rng=SequenceRng(
                random_values=[0.0],
                randint_values=[2],
            ),
        )
        context.opponent.block = 5

        item.run_effect([True], context)

        self.assertEqual(
            actions(state),
            ["attack", "remove_block", "item_activation"],
        )
        self.assertEqual(state.log[1]["data"]["block_removed"], 4)
        self.assertEqual(state.log[1]["data"]["final_block_removed"], 3)

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
                "gain_block",
                "remove_vampirism_check",
                "remove_buff",
                "item_activation",
            ],
        )
        self.assertEqual(state.log[2]["data"]["stack_removed"], 1)
        self.assertEqual(state.log[2]["data"]["final_stack_removed"], 0)

    def test_rat_logs_independent_proc_checks_after_attack(self):
        item = Rat(item_key="rat1", player_id=0)
        state, context = make_item_context(
            item,
            rng=SequenceRng(
                random_values=[0.0, 0.0, 0.5],
                randint_values=[5],
            ),
        )

        item.run_effect([True], context)

        self.assertEqual(
            actions(state),
            [
                "attack",
                "inflict_poison_check",
                "inflict_debuff",
                "inflict_blind_check",
                "item_activation",
            ],
        )
        self.assertTrue(state.log[1]["data"]["success"])
        self.assertFalse(state.log[3]["data"]["success"])

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
        event = AttackEvent(
            attacker=state.players[1],
            defender=state.players[0],
            source_item=attack_source,
            attack_types=("ranged",),
            min_damage=1,
            max_damage=1,
            accuracy=0,
        )

        state.resolve_attack(event)

        self.assertEqual(
            actions(state),
            ["attack", "gain_miss_damage_bonus"],
        )
        self.assertFalse(state.log[0]["data"]["hit"])
        self.assertEqual(
            state.log[0]["data"],
            {
                "action": "attack",
                "target_player_id": 0,
                "attack_types": ["ranged"],
                "hit": False,
            },
        )

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

        with self.assertRaises(_BattleFinishedSignal):
            item.run_effect([True], context)

        self.assertEqual(actions(state), ["attack"])
        self.assertEqual(
            state.log[0]["data"]["final_block_damage"],
            0,
        )
        self.assertEqual(
            state.log[0]["data"]["final_health_damage"],
            1,
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
        )
        defender.buffs.Spikes = 2
        state = BattleState(
            players=[attacker, defender],
            rng=SequenceRng(
                random_values=[0.0],
                randint_values=[5],
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
        )
        state = BattleState(players=[target])
        target.buffs.Regeneration = 2
        target.debuffs.Poison = 1

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
