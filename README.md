# 《背包乱斗》战斗框架入口

本文档只说明三件事：如何接入新物品、如何运行一场战斗、如何读取战斗结果。

## 1. 接入新物品

一个新物品必须使用同一个唯一 `item_id` 完成三项登记。

### 1.1 物品目录格式

在物品目录中加入：

```json
{
  "your_item_id": {
    "item_id": "your_item_id",
    "shape_cells": [[0, 0]],
    "star_cells": [],
    "diamond_cells": [],
    "triangle_cells": []
  }
}
```

字段约定：

- `item_id`：物品唯一标识，必须与外层键一致。
- `shape_cells`：物品占用的相对坐标列表。
- `star_cells`、`diamond_cells`、`triangle_cells`：对应标记的相对坐标列表；没有时可以省略或使用空列表。

如果某类标记在不同旋转角度下需要单独定义，使用：

```json
{
  "star_cells_by_rotation": {
    "0": [[0, 1]],
    "90": [[-1, 0]],
    "180": [[0, -1]],
    "270": [[1, 0]]
  }
}
```

使用 `*_cells_by_rotation` 时必须提供 `0`、`90`、`180`、`270` 四个角度。

### 1.2 物品工厂格式

物品工厂遵循以下调用格式：

```python
def your_item_factory(
    item_id: str,
    item_key: str,
    player_id: int,
) -> BattleItem:
    ...
```

参数含义：

- `item_id`：物品种类标识。
- `item_key`：本场战斗中该物品实例的唯一标识。
- `player_id`：拥有该物品的玩家。

工厂必须返回有效的 `BattleItem`，并保持返回对象的 `item_id`、`item_key`、`player_id` 与输入一致。

### 1.3 工厂注册格式

```python
DEFAULT_ITEM_FACTORIES = {
    "your_item_id": your_item_factory,
}
```

目录键、目录内的 `item_id`、工厂注册键和战斗输入中的 `item_id` 必须完全相同。

## 2. 运行战斗

### 2.1 `battle_run_v1` 标准输入

```json
{
  "schema_version": "battle_run_v1",
  "settings": {
    "max_frames": 1000,
    "frame_delta": 1.0,
    "collect_log": false
  },
  "players": [
    {
      "player_id": 0,
      "class_id": "ranger",
      "health": 25,
      "placements": [
        {
          "item_id": "your_item_id",
          "x": 0,
          "y": 0,
          "rotation": 0
        }
      ]
    },
    {
      "player_id": 1,
      "class_id": "reaper",
      "health": 25,
      "placements": []
    }
  ]
}
```

输入约束：

- `schema_version` 必须是 `battle_run_v1`。
- `players` 必须恰好包含两名玩家，且 `player_id` 不能重复。
- 每名玩家必须提供 `player_id`、`health` 和 `placements`；`class_id` 可以省略。
- `settings` 可以省略。`max_frames` 默认为 `1000`，`frame_delta` 默认为 `1.0`。
- `max_frames` 必须是正整数，`frame_delta` 必须是正数，`collect_log` 必须是布尔值。
- `placements` 中的 `item_id` 必须已经同时登记到物品目录和工厂注册表。
- `rotation` 只能是 `0`、`90`、`180` 或 `270`。

### 2.2 命令行运行

将输入保存为 `battle_run.json`，在仓库根目录执行：

```powershell
python main_v1.py --input battle_run.json --output battle_result.json
```

不提供 `--output` 时，结果会输出到终端：

```powershell
python main_v1.py --input battle_run.json
```

可以临时覆盖帧数和帧时长：

```powershell
python main_v1.py --input battle_run.json --max-frames 2000 --frame-delta 0.1
```

### 2.3 Python 调用

```python
from item_factory_registry_v1 import DEFAULT_ITEM_FACTORIES
from main_v1 import run_battle_from_config, run_battle_from_file

result_from_file = run_battle_from_file(
    "battle_run.json",
    DEFAULT_ITEM_FACTORIES,
)

result_from_dict = run_battle_from_config(
    run_config,
    DEFAULT_ITEM_FACTORIES,
)
```

两个入口都返回 `battle_result_v1` 字典。

## 3. 查看结果

### 3.1 成功结果格式

```json
{
  "schema_version": "battle_result_v1",
  "winner": 0,
  "finish_reason": "winner",
  "frame": 12,
  "time": 12.0,
  "players": [
    {
      "player_id": 0,
      "class_id": "ranger",
      "health": 10,
      "block": 0,
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
      },
      "items": ["your_item_id1"]
    },
    {
      "player_id": 1,
      "class_id": "reaper",
      "health": 0,
      "block": 0,
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
      },
      "items": []
    }
  ],
  "active_items": [
    {
      "player_id": 0,
      "item_key": "your_item_id1",
      "item_id": "your_item_id"
    }
  ],
  "log": []
}
```

主要字段：

- `winner`：胜者的 `player_id`；尚未决出胜者时为 `null`。
- `finish_reason`：`winner` 或 `max_frames_reached`。
- `frame`、`time`：结束时的帧数和战斗时间。
- `players`：双方最终状态。
- `active_items`：本场战斗中的主动物品实例。
- `log`：战斗日志列表。

### 3.2 失败结果格式

输入或接入信息不合法时返回：

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

命令行成功时退出码为 `0`，失败时退出码为 `1`。
