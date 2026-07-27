# `BattleState.log` 战斗日志 SPEC

状态：**已批准并完成显式 `LogHandle` 实现**

本文件描述当前代码中的日志结构。日志写入逻辑以现有
`battle_module_v1.py`、`item_effects_v1.py`、`item_triggers_v1.py` 和
`item_factory_registry_v1.py` 为准。

## 1. Requirements

### R1. 生命周期与输出

- `BattleState.log` 是逐战斗实例独立的列表，初始为空。
- 战斗期间通过 `BattleState.record_log(source, data)` 动态追加。
- 不创建 `battlestate.log` 磁盘文件。
- `_build_success_result()` 使用 `"log": list(battle_state.log)` 完整提取日志。
- `run_battle_from_config()`、`run_battle_from_file()` 和 CLI 继续复用现有成功结果。

### R2. 自动字段

`record_log()` 自动填写：

- `sequence`：从 0 开始的追加序号；
- `frame`、`time`：写入时的战斗时序；
- `source`：物品身份或系统名称。

调用方只传 `source` 和自由结构的 `data`，不传 `event`。`record_log()` 不解释或改写
`data` 的业务字段，并返回仅供内部精确关联该条日志的 `LogHandle`。

### R3. 数据范围

- 日志不保存完整 `PlayerState`，也不保存玩家生命、耐力、Block、Buff/Debuff 的
  `before/after` 状态快照。
- 当前 Effect 日志通常同时表达名义操作量和最终生效量，例如
  `healing/final_healing`。
- 攻击、系统伤害记录本次分配量及最终结算量，不记录双方完整状态。
- 身份、动作、命中结果、概率检查和触发结果可以保留。

### R4. 不改变战斗语义

- 日志不得额外调用 RNG。
- 不改变触发条件、触发顺序和数值结算。
- 伤害调用方先写入原始伤害日志并取得 `LogHandle`，再把句柄传给
  `commit_health_reduction()`。结算函数只通过该句柄回填本次日志的 `final_*` 字段。
- 致命伤害在 `_BattleFinishedSignal` 抛出前完成日志回填。
- 原本不会执行的后续 proc 和 `item_activation` 不得伪造。

## 2. 通用条目结构

```json
{
  "sequence": 0,
  "frame": 0,
  "time": 0.0,
  "source": {
    "type": "item",
    "player_id": 0,
    "item_key": "pocket_sand1",
    "item_id": "pocket_sand"
  },
  "data": {
    "action": "inflict_debuff",
    "target_player_id": 1,
    "debuff": "Blind",
    "stack_gained": 1,
    "final_stack_gained": 1,
    "success": true
  }
}
```

系统来源：

```json
{"type": "system", "name": "Poison"}
```

## 3. 逐函数写入点

### W01 `BattleState.record_log(source, data) -> LogHandle`

```text
若 source 是字符串，构造 system source
否则读取 source.player_id/item_key/item_id
sequence = len(log)
读取当前 frame/time
浅复制 data
追加条目
返回绑定当前 BattleState 和 sequence 的 LogHandle
```

`LogHandle` 不进入 JSON 输出。`BattleState` 使用句柄前必须确认：

- 句柄属于当前战斗；
- `sequence` 仍指向同一条日志；
- 目标条目是尚未回填的伤害日志；
- 日志的 `target_player_id` 与伤害目标一致。

无句柄的 `commit_health_reduction()` 不得修改任何已有日志。

### W02 `BattleItem.emit_activation(context) -> None`

```text
校验 context.item is self
写 {"action": "item_activation"}
dispatch_item_activation(self)
```

因此物品自己的激活日志先于相邻物品监听器日志。

### W03 `BattleState.resolve_attack(event) -> AttackEvent`

未命中：

```json
{
  "action": "attack",
  "target_player_id": 1,
  "attack_types": ["ranged"],
  "hit": false
}
```

该日志在 `on_attack_missed` 反应前写入。

命中：

```json
{
  "action": "attack",
  "target_player_id": 1,
  "attack_types": ["melee"],
  "hit": true,
  "block_damage": 2,
  "health_damage": 3,
  "final_block_damage": 2,
  "final_health_damage": 3
}
```

该日志在伤害提交前写入，并把返回的 `LogHandle` 交给伤害提交。致命提交仍保留带有
`final_*` 的攻击日志，但不写后续状态效果或物品激活。

### W04 通用 Effect

| 函数 | `data` 业务字段 |
| --- | --- |
| `StaminaConsumptionEffect.apply` | `stamina_spent`、`success` |
| `HealEffect.apply` / `HolyLinkedHealEffect.apply` | `healing`、`final_healing` |
| `GainMaxHealthEffect.apply` | `max_health_gained` |
| `RegenerateStaminaEffect.apply` | `stamina_generated`、`final_stamina_generated` |
| `GainBlockEffect.apply` | `block_gained`、`final_block_gained`、`success` |
| `RemoveOpponentBlockEffect.apply` | `block_removed`、`final_block_removed`、`success` |
| `GainBuffEffect.apply` | `buff`、`stack_gained`、`final_stack_gained`、`success` |
| `UseBuffEffect.apply` | `buff`、`stack_used`、`final_stack_used`、`success` |
| `BuffRemovalEffect.apply` | `buff`、`stack_removed`、`final_stack_removed`、`success` |
| `InflictDebuffEffect.apply` | `debuff`、`stack_gained`、`final_stack_gained`、`success` |
| `CleanseDebuffEffect.apply` | `debuff`、`stack_removed`、`final_stack_removed`、`success` |
| `LinkedWeaponDamageEffect.apply` | `targets[].damage_modifier_delta`、`success` |
| `PreventAttackDamageEffect.apply` | 攻击身份、`pending_damage`、`final_pending_damage`、`success` |
| `RemoveOpponentStaminaEffect.apply` | `stamina_removed`、`final_stamina_removed`、`success` |

`AttackEffect.apply()` 不重复写日志，由 W03 统一记录。

### W05 Trigger 与概率检查

- `SlimeActivationTrigger.update()` 写来源物品、`required`、`triggered` 和
  `activation_count_delta`。
- `OnAttackedTrigger.update()` 写 `chance`、既有 `roll`、`success` 和关联攻击身份。
- Twine、Broom、Garlic、Rat 的专属概率检查使用相同原则。
- 概率失败也写；前置条件不满足、没有执行检查时不写。

### W06 系统结算

| 函数 | source | `data` 业务字段 |
| --- | --- | --- |
| `_apply_regeneration_tick` | `Regeneration` | `healing`、`final_healing` |
| `_apply_poison_tick` | `Poison` | `block_damage`、`health_damage`、`final_block_damage`、`final_health_damage` |
| `inflict_fatigue` | `Fatigue` | `fatigue_damage_delta` 及四个伤害字段 |
| `_apply_melee_hit_statuses` 的 Spikes | `Spikes` | 攻击身份及四个伤害字段 |
| `_apply_melee_hit_statuses` 的 Vampirism | `Vampirism` | 攻击身份、`healing`、`final_healing` |

`_apply_poison_tick()` 当前返回最终 Block 与 Health 伤害的总和。自然耐力恢复不写每帧
日志。

## 4. 每件物品的写入顺序

### I01–I04 开战物品

- Pocket Sand：`inflict_debuff`，Blind 的 `stack_gained/final_stack_gained`。
- Healing Herbs：`gain_buff`，Regeneration 的对应字段。
- Flame：`gain_buff`，Heat 的对应字段。
- Walrus Tusk：`gain_buff`，Spikes 的对应字段。
- 均不写 `item_activation`。

### I05 Shiny Shell

`heal`（`healing/final_healing`）→ `item_activation`。

### I06 Wand of Equilibrium

`gain_buff` → 可选 `use_buff` → 可选 Empower `gain_buff` → `item_activation`。

### I07 Magic For Dummies

先写 Mana `use_buff`。失败时结束；成功时写 `gain_max_health`，再写
`item_activation`。

### I08 Whetstone

写一条 `modify_linked_weapon_damage`；`targets` 列出目标身份、Effect 索引和
`damage_modifier_delta`。无目标时 `targets=[]`、`success=false`。

### I09 Twine

`gain_max_health_check` → 成功时 `gain_max_health` → `item_activation`。

### I10 Goobling

每次监听到相邻物品激活都写 `count_linked_item_activation`；第三次后再写 `heal` 和
`item_activation`。

### I11 Wooden Buckler

`on_attacked_check` → 成功时 `prevent_attack_damage` → `remove_stamina` →
`item_activation`。

### I12 Broom

- 对手未命中：`gain_miss_damage_bonus`。
- 自身到期：`spend_stamina` → `attack`。
- 命中且有累计奖励：`consume_miss_damage_bonus`。
- 命中后：`inflict_blind_check`，成功时 `inflict_debuff`。
- 最后写 `item_activation`。

### I13 Wooden Sword

`spend_stamina` → `attack` → `item_activation`。耐力不足只写失败的
`spend_stamina`。

### I14 Shortbow

同 I13，攻击类型为 ranged。

### I15 Stone

非致命流程：`attack` → `remove_block` → `item_activation`。致命伤害保留已完整回填的
`attack`，不执行后两条。

### I16 Banana

`heal` → `restore_stamina` → `item_activation`。

### I17 Garlic

`gain_block` → `remove_vampirism_check` → 成功时 `remove_buff` →
`item_activation`。

### I18 Pan

`spend_stamina` → `attack` → `item_activation`；攻击伤害包含相邻 Food 修正。

### I19 Rat

非致命命中后：`attack` → Poison 检查 → 可选 Poison `inflict_debuff` → Blind 检查 →
可选 Blind `inflict_debuff` → `item_activation`。未命中时写 `attack` 后直接激活；致命
提交保留已完整回填的 `attack`，不写后续条目。

## 5. Realize

### `battle_module_v1.py`

- `BattleState.log` 使用 `default_factory=list`。
- `LogHandle` 是绑定 `BattleState + sequence` 的不可变内部句柄，不参与序列化。
- `record_log()` 负责通用外壳并返回 `LogHandle`。
- `_complete_damage_log()` 验证句柄归属、序号、目标和待完成状态，再定向回填
  `final_block_damage/final_health_damage`。
- `commit_health_reduction(..., log_handle=None)` 仅在显式收到句柄时回填；无句柄调用
  保持纯伤害提交语义，不触碰旧日志。
- `resolve_attack()` 和系统状态函数按 W03/W06 写当前字段。
- `emit_activation()` 在派发监听器前写激活。

### `item_effects_v1.py`

每个 Effect 在原有计算位置复用已有名义量和最终量构造 `data`，不增加状态修改或 RNG
调用。

### `item_triggers_v1.py`

只在合法触发上下文中写计数或概率检查；不为日志重复抽样。

### `item_factory_registry_v1.py`

只为 Twine、Broom、Garlic、Rat 等无法由通用 Effect 完整表达的检查或累计变化直接写
日志。

### `main_v1.py`

`_build_success_result()` 使用：

```python
"log": list(battle_state.log)
```

## 6. Acceptance Criteria / Tests

`tests/test_battle_logging_v1.py` 验证：

1. 新 `BattleState` 的日志相互独立。
2. `record_log()` 自动填写来源和时序，不产生 `event`。
3. 成功结果完整复制日志且不与原列表别名。
4. 所有当前物品及系统写入点的字段和顺序。
5. 名义量与最终量字段在上限、资源不足等场景中的值。
6. 未命中日志只包含当前实现定义的攻击字段。
7. 致命提交保留并完成本次伤害日志，然后终止后续流程。
8. 内置日志不含玩家状态 `before/after` 快照键。
9. 输出可由 `json.dumps()` 序列化。
10. 无日志伤害不会访问或修改旧日志。
11. 旧伤害日志不会被后续无句柄伤害覆盖。
12. 跨战斗、失效、错误目标或重复使用的 `LogHandle` 在状态修改前被拒绝。
13. Attack 与 Spikes 分别回填各自句柄指向的日志。

`tests/test_battle_module_v1.py` 验证 `_apply_poison_tick()` 当前返回最终总伤害。

新增或修订的精确测试：

- `test_record_log_autofills_source_timing_without_event`
- `test_damage_log_handle_updates_only_its_exact_entry`
- `test_damage_log_handle_rejects_cross_battle_and_reuse`
- `test_damage_log_handle_rejects_stale_sequence`
- `test_lethal_attack_completes_log_before_stop_signal`
- `test_attack_and_spikes_complete_separate_damage_logs`
- `test_system_status_logs_use_automatic_sources`
- `test_melee_statuses_use_commit_returned_final_damage`
- `test_melee_hit_applies_spikes_before_vampirism`

全量回归要求所有现有测试通过，且现有日志 JSON 字段保持不变。

## 7. 明确不做

- 不创建磁盘日志文件。
- 不引入 Python `logging`、事件总线或完整事件溯源框架。
- 不记录完整玩家对象或玩家状态快照。
- 不由 `record_log()` 强制统一 `data` schema。
- 不修改 `AGENTS.md`。
