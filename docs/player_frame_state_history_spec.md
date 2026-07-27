# 逐帧玩家状态快照 SPEC

状态：**已实现并验证（含耐力感知压缩修订，2026-07-27）**

验证：19 项专项测试通过；仓库全量 493 项测试通过。

效果验证：一次 `minimal_wooden_battle_v1.json` 运行产生 168 条原始帧记录，
耐力感知压缩后为 13 段。

目标是在不改变战斗结算语义的前提下，可选地保存每次
`BattleState.step()` 结束时两名玩家的状态，并随 `battle_result_v1`
输出。本文只设计玩家运行时状态快照，不修改现有逐事件
`BattleState.log`。

## 1. Requirements

### R1. 可选采集

- `settings.collect_player_state_history` 为可选布尔值，默认 `false`。
- 关闭时不创建快照内容，避免强化学习批量模拟产生不必要的内存和 JSON 开销。
- 开启时，每次正常结束或因 `_BattleFinishedSignal` 结束的 `step()` 恰好记录一条。
- `run()` 调用前已经有胜者、因而没有执行 `step()` 时，不记录快照。
- 非预期异常不记录半完成快照，异常继续向上抛出。

### R2. 快照时点

- 正常帧：在耐力恢复、全部主动物品、帧/时间推进及本帧系统结算全部完成后记录。
- 主动物品在帧中造成致命伤：记录终局状态；沿用现有语义，不额外推进
  `frame` / `time`。
- 系统结算造成致命伤：记录终局状态；此时 `frame` / `time` 已推进。
- 不额外保存初始态；历史长度等于实际执行的 `step()` 次数。

### R3. 数据完整性

- 每条快照包含 `sequence`、`frame`、`time` 和按
  `BattleState.players` 顺序排列的 `players`。
- 每名玩家只包含当前 `PlayerState` 的数值状态和全部 Buff/Debuff。
- 所有列表和字典均为新对象；后续帧修改玩家状态不得反向修改旧快照。
- 快照必须可由 `json.dumps()` 直接序列化，且不得读取 RNG。
- `BattleState.player_state_history` 保留逐次 `step()` 的原始记录；成功结果只输出压缩副本。
- 比较相邻记录时，除 `stamina` 外的玩家字段必须通过 `==` 完全相等。
- `stamina` 单独按 R5 的自然恢复规则比较；状态之后再次相同但中间发生过变化时，
  不跨段合并。

### R4. 范围边界

- 不把快照写入逐事件 `log`，不修改现有日志字段或顺序。
- 完全不读取或记录 `PlayerState.items`，包括物品身份、摆盘、连接关系、
  trigger/effect 和冷却进度。
- 本结构只用于玩家战斗数值的时间序列，不是背包状态或摆盘 AI 观测。
- 不流式写文件、不做增量/delta 快照；只在输出前执行相邻相同状态的游程压缩。
  CLI 原有 `--output` 会把压缩历史随完整结果一起落盘。
- 不修改 `AGENTS.md`，不引入局外发育、商店或训练逻辑。

### R5. 耐力感知压缩

对每名玩家分别计算相邻原始帧的
`stamina_delta = current.stamina - previous.stamina`。只有以下情况通过：

1. `stamina_delta` 在绝对误差 `1e-9` 内等于 `0`；
2. `stamina_delta` 在绝对误差 `1e-9` 内等于本场 `frame_delta`；
3. 玩家本帧到达 `max_stamina`，且
   `0 < stamina_delta < frame_delta`（边界允许 `1e-9` 误差）。

第 3 条覆盖自然恢复在最后一帧被最大耐力截断的情况。负变化、超过
`frame_delta` 的正变化，以及未到达最大耐力的较小正变化均视为非自然变化并开始新段。
两名玩家都必须通过，整条相邻记录才能合并。

压缩结果中，每名玩家的 `stamina` 统一改为闭区间 `(start, end)`；即使只有一条记录，
也写成 `(value, value)`。JSON 输出对应二元素数组。

## 2. Design

### 2.1 输出结构

`battle_result_v1` 始终增加压缩后的 `player_state_history`；未开启采集时为 `[]`。
以下表示原始序号 0 至 10、帧 1 至 11、时间 0.1 至 1.1 期间，玩家除耐力自然恢复外
的状态完全相同：

```json
{
  "player_state_history": [
    {
      "sequence": [0, 10],
      "frame": [1, 11],
      "time": [0.1, 1.1],
      "players": [
        {
          "player_id": 0,
          "health": 23,
          "max_health": 25,
          "block": 0,
          "fatigue_damage": 0,
          "stamina": [4.0, 5.0],
          "max_stamina": 5.0,
          "buffs": {
            "Empower": 0,
            "Heat": 0,
            "Luck": 0,
            "Mana": 0,
            "Regeneration": 0,
            "Spikes": 0,
            "Vampirism": 0
          },
          "debuffs": {
            "Poison": 0,
            "Blind": 0,
            "Cold": 0
          }
        }
      ]
    }
  ]
}
```

Python 结果中的 `sequence`、`frame`、`time` 和每名玩家的 `stamina` 都使用
二元组；JSON 序列化后变成二元素数组。未发生合并的单条记录也统一表示成闭区间，
例如 `sequence == (4, 4)`、`stamina == (3.2, 3.2)`，不混用标量和区间两种 schema。

原始记录的 `sequence` 仍是从 0 开始的标量快照序号，用于处理“主动效果致命但现有
`frame` 未推进”的终局记录。`class_id` 属于 `main_v1` 保存的静态输入元数据，
不属于当前 `PlayerState`，不在每帧重复保存。原始记录中的 `stamina` 仍是标量；
只有成功结果中的压缩副本使用耐力区间。

### 2.2 相邻记录比较

比较始终针对两条相邻的原始记录，而不是拿当前记录与整段起点比较：

```text
先逐名玩家比较除 stamina 外的完整字典
  任一字段不同：开始新段

再逐名玩家检查 stamina_delta
  约等于 0：通过
  约等于 frame_delta：通过
  到达 max_stamina 且为 0 到 frame_delta 之间的正增量：通过
  其他情况：开始新段

两名玩家均通过：合并到当前段，并更新各自 stamina 区间终点
```

浮点比较统一使用 `math.isclose(..., rel_tol=0.0, abs_tol=1e-9)`。除 `stamina`
外不使用容差。

### 2.3 `BattleState` 数据模型

```python
collect_player_state_history: bool = False
player_state_history: list[dict[str, object]] = field(default_factory=list)
```

两个字段均归单场战斗实例所有。该开关与现有 `settings.collect_log` 相互独立，
本需求不顺带改变日志采集行为。

### 2.4 状态流

```text
step()
  -> regenerate_stamina()
  -> 逐个运行 active_items
  -> frame/time 前进
  -> _apply_system_triggers()
  -> record_player_state_snapshot()

任一生命扣减触发 _BattleFinishedSignal
  -> step() 捕获信号
  -> record_player_state_snapshot()
  -> 返回 winner
```

记录函数只能出现在正常出口和 `_BattleFinishedSignal` 出口，不能放在
`finally`，否则非预期异常也会保存半完成状态。

成功输出流程：

```text
run() 完成
  -> _build_success_result()
  -> compress_player_state_history(原始历史)
  -> 将压缩副本写入 battle_result_v1
```

## 3. Realize（逐函数）

### F1 `battle_module_v1.serialize_player_state(player: PlayerState) -> dict[str, object]`

职责：创建一个与活动对象脱离、可 JSON 序列化的单名玩家快照。

伪代码：

```text
返回新的 dict：
  复制 player_id 和全部数值字段
  用 dataclasses.asdict 分别复制 buffs、debuffs
```

不得读取 `player.items`，不得复制或调用任何 `BattleItem`、trigger 或 effect。

### F2 `BattleState.record_player_state_snapshot(self) -> None`

职责：按开关追加一条完整帧快照。

伪代码：

```text
若 collect_player_state_history 为 false：返回
snapshot = {
  sequence: len(player_state_history),
  frame: self.frame,
  time: self.time,
  players: [serialize_player_state(player) for player in self.players],
}
追加 snapshot
```

### F3 `BattleState.step(self)`

保留现有结算顺序。在正常 `_apply_system_triggers()` 返回后调用 F2；捕获
`_BattleFinishedSignal` 后也先调用 F2，再返回 `winner`。其他异常不捕获。

### F4 `main_v1._validate_run_config(run_config)`

若存在 `settings.collect_player_state_history` 且值不是严格 `bool`，抛出：

```text
ValueError("settings.collect_player_state_history must be a bool")
```

### F5 `main_v1.run_battle_from_config(...)`

初始化 `BattleState` 后、调用 `run()` 前，将配置值（默认 `False`）赋给
`battle_state.collect_player_state_history`。

### F6 `main_v1._players_match_for_history_compression(previous_players, current_players, frame_delta) -> bool`

职责：执行 R5 的逐玩家比较，不修改输入。

伪代码：

```text
若玩家数量不同：返回 false
逐对读取相同位置的 previous_player、current_player：
  分别创建排除 stamina 的字典
  若两个字典不完全相等：返回 false

  delta = current.stamina - previous.stamina
  若 delta 约等于 0：继续
  若 delta 约等于 frame_delta：继续
  若 current.stamina 约等于 current.max_stamina
     且 delta 位于 (0, frame_delta) 容差范围内：继续
  返回 false
返回 true
```

### F7 `main_v1.compress_player_state_history(player_state_history, frame_delta) -> list[dict[str, object]]`

职责：作为 `main_v1.py` 中的独立纯转换函数，将连续相同玩家状态压缩为闭区间记录，
不修改传入列表或其中的字典。

输入前提：接收 F2 生成的未压缩内部历史；不负责兼容已压缩输入，也不增加额外 schema
校验。

伪代码：

```text
若输入为空：返回 []
compressed = []
逐条读取原始 record：
  若存在 previous_record，且 F6(previous_record.players, record.players, frame_delta)：
    只把最后一段的 sequence/frame/time 区间终点更新为 record 对应值
    逐名玩家把压缩段 stamina 区间终点更新为 record 中的 stamina
  否则：
    追加新段：
      sequence = (record.sequence, record.sequence)
      frame = (record.frame, record.frame)
      time = (record.time, record.time)
      players = deepcopy(record.players)
      把每名玩家的 stamina 改成 (stamina, stamina)
  previous_record = record
返回 compressed
```

`deepcopy` 只复制已经序列化的玩家字典，不接触活动 `PlayerState` 或背包对象。

### F8 `main_v1._build_success_result(...)`

建立返回字典前先执行：

```python
compressed_player_state_history = compress_player_state_history(
    battle_state.player_state_history,
    battle_state.frame_delta,
)
```

结果增加：

```python
"player_state_history": compressed_player_state_history
```

原始 `battle_state.player_state_history` 保持未压缩，不被覆盖。
错误结果不增加该字段，因为战斗可能未成功建立或状态不可信。

## 4. Tasks

1. 保留现有 `battle_module_v1.py` 原始逐帧采集，不修改战斗结算或快照字段。
2. 在 `main_v1.py` 增加 F6，并按 F7 改造现有独立压缩函数。
3. 将 `battle_state.frame_delta` 传给 F7，并把压缩输出中的耐力改为区间。
4. 更新 `tests/test_player_state_history_v1.py` 的现有压缩断言并增加耐力边界测试。
5. 更新 README 的 `player_state_history.players[].stamina` 输出说明。
6. 运行专项测试、实验输入和全量回归；全部通过后把修订状态更新为“已实现并验证”。

## 5. Acceptance Criteria / Tests

1. `test_new_battle_states_have_independent_empty_player_state_histories`  
   两个 `BattleState` 的历史列表互不共享。
2. `test_serialize_player_state_copies_supported_combat_fields_without_backpack_state`  
   精确校验全部玩家数值字段和 Buff/Debuff，并断言快照中不存在 `items`。
3. `test_serialized_player_state_is_detached_and_json_serializable`  
   快照后修改玩家或 Buff/Debuff，不改变旧快照；可执行 `json.dumps()`。
4. `test_step_does_not_record_history_when_collection_is_disabled`  
   默认关闭时执行一帧，历史仍为空。
5. `test_step_records_state_after_frame_and_system_resolution`  
   开启后验证 `frame/time` 已推进，且快照反映本帧耐力、物品效果和系统结算后的值。
6. `test_multiple_steps_record_one_independent_snapshot_each`  
   N 次正常 `step()` 得到 N 条、`sequence == 0..N-1`，旧帧不被新帧覆盖。
7. `test_item_lethal_step_records_terminal_state_without_advancing_time`  
   主动物品致命时有一条终局快照，生命为 0，`frame/time` 保持现有值。
8. `test_system_lethal_step_records_terminal_state_after_time_advances`  
   Poison/Fatigue 致命时，终局快照使用已推进的 `frame/time`。
9. `test_unexpected_step_exception_does_not_record_partial_snapshot`  
   自定义物品抛出普通异常时，历史为空且异常未被吞掉。
10. `test_compress_player_state_history_handles_empty_and_single_record`  
    空输入返回 `[]`；单条记录的四类区间均为 `(value, value)`。
11. `test_compression_merges_exact_frame_delta_stamina_recovery`  
    其他属性相同时，连续 `+frame_delta` 的耐力恢复合并为一段，耐力输出起止值。
12. `test_compression_accepts_stamina_floating_point_error`  
    `0.10000000000000009` 与 `frame_delta=0.1` 在 `1e-9` 绝对误差内合并。
13. `test_compression_accepts_final_partial_recovery_at_max_stamina`  
    仅当当前值到达 `max_stamina` 时，最后不足一个 `frame_delta` 的正恢复通过。
14. `test_compression_rejects_stamina_spending_and_non_natural_gain`  
    耐力下降、超过 `frame_delta` 的增加、未到上限的较小增加均开始新段。
15. `test_compression_rejects_non_stamina_state_change`  
    即使耐力自然恢复，生命、护盾、疲惫、最大耐力或任一 Buff/Debuff 变化仍开始新段。
16. `test_compress_player_state_history_does_not_merge_equal_states_across_change`  
    A、B、A 三段保持三段，首尾 A 不合并。
17. `test_compress_player_state_history_does_not_mutate_or_alias_input`  
    输入保持标量耐力且内容不变；修改输出的耐力区间或玩家字段不影响输入。
18. `test_run_config_validates_applies_and_compresses_player_state_history`  
    开关校验不变；启用时输出耐力区间并按耐力感知规则压缩。
19. `test_success_result_player_state_history_is_json_serializable`  
    JSON 中耐力为二元素数组；最后一段耐力区间终点等于最终玩家耐力。
20. 使用 `minimal_wooden_battle_v1.json` 验证压缩段数显著少于原始帧数。
21. 全量现有测试通过；现有 `log` 内容、事件顺序、胜负、帧数和时间不得改变。
