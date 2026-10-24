> **独立 Python 无 GUI 引擎快照：** [python_engine/README.md](python_engine/README.md)。正式入口为有限 68 项；75 项候选独立验收通过但未晋级，完整原版引擎及 RL 仍未完成。下文是仓库已有 v1 模拟器的说明，输入格式不同。

# 《背包乱斗》战斗配置与结果说明

本文只说明三件事：

1. 如何编写一场战斗的 JSON 配置。
2. 如何启动战斗。
3. 如何查看战斗结果。

仓库已有可直接运行的示例：

- 输入：[data/minimal_wooden_battle_v1.json](data/minimal_wooden_battle_v1.json)
- 物品目录：[data/item_catalog_v1.json](data/item_catalog_v1.json)

## 1. 编写战斗配置

最小完整示例：

```json
{
  "schema_version": "battle_run_v1",
  "settings": {
    "max_frames": 1000,
    "frame_delta": 0.1,
    "collect_player_state_history": true
  },
  "players": [
    {
      "player_id": "a",
      "class_id": "ranger",
      "health": 25,
      "max_health": 25,
      "stamina": 5.0,
      "max_stamina": 5.0,
      "placements": [
        {
          "item_id": "wooden_sword",
          "x": 0,
          "y": 0,
          "rotation": 0
        }
      ]
    },
    {
      "player_id": "b",
      "class_id": "reaper",
      "health": 25,
      "max_health": 25,
      "stamina": 5.0,
      "max_stamina": 5.0,
      "placements": [
        {
          "item_id": "wooden_sword",
          "x": 0,
          "y": 0,
          "rotation": 0
        }
      ]
    }
  ]
}
```

### 1.1 顶层字段

| 字段 | 必填 | 含义 |
| --- | --- | --- |
| `schema_version` | 是 | 固定写成 `"battle_run_v1"`。 |
| `settings` | 否 | 战斗运行设置；省略时使用默认值。 |
| `players` | 是 | 恰好两名玩家，`player_id` 不得重复。 |

### 1.2 `settings`

| 字段 | 默认值 | 要求与含义 |
| --- | ---: | --- |
| `max_frames` | `1000` | 正整数。最多运行多少帧；到达上限仍无胜者时结束。 |
| `frame_delta` | `1 / 30` | 正数。每帧代表多少秒；常用 `0.1` 或 `1 / 30`。 |
| `collect_player_state_history` | `false` | 布尔值。是否在结果中保存逐帧玩家数值。 |

旧配置可以包含布尔字段 `collect_log`，但战斗结果始终会返回 `log`，新配置可以省略它。

### 1.3 玩家字段

| 字段 | 必填 | 要求与含义 |
| --- | --- | --- |
| `player_id` | 是 | 玩家唯一标识，建议使用字符串或整数；会原样出现在结果中。 |
| `class_id` | 否 | 职业标签；当前用于在结果中标记玩家。 |
| `health` | 是 | 开战时当前生命，必须是正整数。 |
| `max_health` | 是 | 开战时最大生命，必须是正整数，且不小于 `health`。 |
| `stamina` | 是 | 开战时当前耐力，必须是正数。 |
| `max_stamina` | 是 | 开战时最大耐力，必须是正数。开战时必须等于 `stamina`。 |
| `placements` | 是 | 玩家背包中的物品摆放列表；可以是空列表。 |

两名玩家各自使用独立的 9×7 背包棋盘。

### 1.4 物品摆放字段

每件物品写成：

```json
{
  "item_id": "wooden_sword",
  "x": 0,
  "y": 0,
  "rotation": 0
}
```

| 字段 | 要求与含义 |
| --- | --- |
| `item_id` | 物品种类标识，必须是当前可用物品。 |
| `x` | 整数。物品参考点的横坐标。 |
| `y` | 整数。物品参考点的纵坐标。 |
| `rotation` | 只能是 `0`、`90`、`180` 或 `270`，表示逆时针旋转角度。 |

坐标规则：

- 左下角是 `(0, 0)`。
- `x` 向右增加，棋盘列坐标为 `0` 到 `8`。
- `y` 向上增加，棋盘行坐标为 `0` 到 `6`。
- 旋转后，物品占用的所有格子都必须留在棋盘内。
- 同一玩家的物品不能重叠。
- 两名玩家的背包互不影响，可以使用相同坐标。

同类物品可以放多件。结果中的实例名按该玩家 `placements` 的顺序自动编号，例如
`wooden_sword1`、`wooden_sword2`。

当前标准入口可使用以下 `item_id`：

```text
banana
broom
flame
garlic
goobling
healing_herbs
magic_for_dummies
pan
pocket_sand
rat
shiny_shell
shortbow
stone
twine
walrus_tusk
wand_of_equilibrium
whetstone
wooden_buckler
wooden_sword
```

各物品的形状和标记位置见[物品目录](data/item_catalog_v1.json)。

## 2. 开始战斗

### 2.1 命令行

在仓库根目录运行：

```powershell
python main_v1.py --input data/minimal_wooden_battle_v1.json --output data/my_battle_result.json
```

- `--input`：必填，战斗配置 JSON。
- `--output`：可选，结果文件路径；省略时结果打印到终端。
- `--max-frames`：可选，临时覆盖配置中的帧上限。
- `--frame-delta`：可选，临时覆盖配置中的每帧秒数。

例如：

```powershell
python main_v1.py --input battle_run.json --max-frames 2000 --frame-delta 0.1
```

成功时退出码为 `0`；配置或运行失败时退出码为 `1`。

含命中或概率效果的战斗具有随机性，同一份配置重复运行可能得到不同结果。

## 3. 查看结果

成功结果包含以下顶层字段：

| 字段 | 含义 |
| --- | --- |
| `schema_version` | 固定为 `"battle_result_v1"`。 |
| `winner` | 胜者的 `player_id`；未决出胜者时为 `null`。 |
| `finish_reason` | `"winner"` 或 `"max_frames_reached"`。 |
| `frame` | 战斗结束时的帧计数。 |
| `time` | 战斗结束时的模拟秒数；可能出现正常的浮点小数尾差。 |
| `players` | 两名玩家的最终状态。 |
| `active_items` | 本场会主动触发的物品实例。 |
| `player_state_history` | 压缩后的逐帧玩家状态；未开启采集时为 `[]`。 |
| `log` | 按发生顺序排列的战斗事件。 |

### 3.1 最终玩家状态

`players` 中每名玩家包含：

| 字段 | 含义 |
| --- | --- |
| `player_id` | 配置中的玩家标识。 |
| `class_id` | 配置中的职业标签；未提供时为 `null`。 |
| `health` / `max_health` | 最终当前生命 / 最大生命。 |
| `block` | 最终护盾。 |
| `fatigue_damage` | 当前疲惫伤害值。 |
| `stamina` / `max_stamina` | 最终当前耐力 / 最大耐力。 |
| `buffs` | 最终增益层数：`Empower`、`Heat`、`Luck`、`Mana`、`Regeneration`、`Spikes`、`Vampirism`。 |
| `debuffs` | 最终减益层数：`Poison`、`Blind`、`Cold`。 |
| `items` | 该玩家的全部物品实例名，包括主动和被动物品。 |

`active_items` 中每项包含所属 `player_id`、实例名 `item_key` 和种类 `item_id`。
被动物品会出现在玩家的 `items` 中，但不一定出现在 `active_items` 中。

### 3.2 逐帧玩家状态

只有配置了 `"collect_player_state_history": true` 才会产生记录。

每条记录包含 `sequence`、`frame`、`time` 和 `players`。相邻帧的两名玩家状态
除自然耐力恢复外完全相同时会合并：例如 `sequence: [0, 12]`、
`frame: [1, 13]`、`time: [0.1, 1.3]` 表示这段区间内其他状态相同。

- 三个二元素数组都是包含首尾的区间。
- 未与其他帧合并的记录也使用 `[4, 4]` 这种格式。
- 只合并相邻的相同状态。
- 每名玩家的 `stamina` 也写成 `[start, end]`；单帧写成 `[value, value]`。
- 耐力不变、每帧自然增加 `frame_delta`，或最后一帧自然恢复至上限，都允许合并。
- 自然耐力恢复比较允许 `1e-9` 的浮点绝对误差。
- 耐力消耗、其他耐力增加，以及生命、护盾、疲惫、最大耐力或 Buff/Debuff 变化
  都会开始新的区间。
- 历史中的玩家不包含 `class_id` 和 `items`，也不包含摆盘或物品状态。

### 3.3 战斗日志

每条 `log` 包含：

| 字段 | 含义 |
| --- | --- |
| `sequence` | 从 `0` 开始的事件序号。 |
| `frame` / `time` | 事件发生时的帧和模拟时间。 |
| `source` | 事件来源；可能是物品，也可能是 Poison、Fatigue 等系统效果。 |
| `data` | 事件内容；`action` 表示事件种类，其余字段随事件而变化。 |

物品来源会给出 `player_id`、`item_key`、`item_id`。常见事件包括耐力消耗、攻击、
治疗、增益/减益变化、概率判定和物品激活。

伤害事件中的 `block_damage` / `health_damage` 表示准备结算的数值；
`final_block_damage` / `final_health_damage` 表示实际生效的数值。

### 3.4 未决胜负与错误

如果到达 `max_frames` 仍未决出胜者：

```json
{
  "winner": null,
  "finish_reason": "max_frames_reached"
}
```

如果配置无效或运行失败：

```json
{
  "schema_version": "battle_result_v1",
  "winner": null,
  "finish_reason": "error",
  "error": {
    "type": "ValueError",
    "message": "错误说明"
  }
}
```

优先阅读 `error.message`，它通常会指出缺少字段、未知物品、非法旋转、越界或重叠位置。
