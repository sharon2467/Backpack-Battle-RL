# Main Function V1 Design

## 目标

`main` 是当前三个基础模块之上的薄调度层，负责从结构化玩家文件读取一场对战所需的数据，依次完成：

```text
玩家结构化文件
-> 输入解析与规范化
-> 背包摆放校验与占用/marker 关系分析
-> 战斗对象初始化
-> 战斗循环运行
-> 结果结构化输出
```

V1 的重点是把已经存在的背包分析模块、战斗初始化模块和战斗模块串起来。`main` 不新增具体物品效果、不实现商店、不实现合成、不实现强化学习环境接口。

## 当前依赖

`main` 只依赖现有公开能力：

- `basic_backpack_v1.ITEM_CATALOG`
- `battle_initializer_v1.initialize_battle(player_specs, item_factories, item_catalog=ITEM_CATALOG)`
- `battle_module_v1.BattleState.run(max_frames, frame_delta=1.0)`

其中背包分析由 `initialize_battle()` 间接调用；`main` 不应重复实现坐标、旋转、重叠、marker link 等规则。

## 推荐文件名

后续实现时建议新增：

```text
main_v1.py
```

如果未来项目进入正式包结构，可以再把它迁移为 CLI 入口，例如：

```text
python -m backpack_battles_ai.run_battle
```

V1 先保持单文件入口，降低模块重组成本。

## 输入文件格式

V1 推荐使用 JSON 作为玩家信息结构化文件。JSON 足够直观，也便于后续被训练脚本、评估脚本或 UI 生成。

示例：

```json
{
  "schema_version": "battle_run_v1",
  "settings": {
    "max_frames": 1000,
    "frame_delta": 1.0,
    "seed": null,
    "collect_log": false
  },
  "players": [
    {
      "player_id": 0,
      "class_id": "ranger",
      "health": 25,
      "max_stamina": 5.0,
      "stamina": 5.0,
      "placements": [
        {"item_id": "stone", "x": 0, "y": 0, "rotation": 0}
      ]
    },
    {
      "player_id": 1,
      "class_id": "reaper",
      "health": 25,
      "max_stamina": 5.0,
      "stamina": 5.0,
      "placements": []
    }
  ]
}
```

### 顶层字段

- `schema_version`: 必填，V1 固定为 `"battle_run_v1"`。
- `settings`: 可选，对战运行参数。
- `players`: 必填，长度必须等于 2。

### settings 字段

- `max_frames`: 可选，正整数；默认建议为 `1000`。用于防止战斗因物品逻辑问题无限运行。
- `frame_delta`: 可选，正数；默认建议为 `1.0`。传给 `BattleState.run()`。
- `seed`: 可选。用于初始化 `BattleState.rng`，集中控制命中、伤害、暴击和未来随机触发等全局随机；为 `null` 时使用非固定随机源。
- `collect_log`: 可选，布尔值；当前 V1 可保留该字段用于未来扩展，但木剑首版不落地 combat log。结果里只返回空日志或不返回日志。

### players 字段

每个玩家对象包含：

- `player_id`: 必填。传入 `PlayerState.player_id`，两名玩家不能重复。
- `class_id`: 推荐保留。根据项目知识库，职业会影响物品、机制和起始选择，所以结构化文件中应保存它。当前 V1 的 `PlayerState` 暂不接收该字段，`main` 只做输入保留与结果回显，不把它塞进战斗对象。
- `health`: 必填。传入 `PlayerState.health`。V1 不根据回合自动推导生命值。
- `max_stamina`: 必填。传入 `PlayerState.max_stamina`，表示当前战斗开始时的耐力上限。
- `stamina`: 必填。传入 `PlayerState.stamina`，表示当前战斗开始时的耐力值。标准战斗开局耐力满格，因此应等于 `max_stamina`。
- `placements`: 必填。传给背包分析模块和战斗初始化模块。

`placements` 的格式沿用当前背包模块：

```json
[
  {"item_id": "stone", "x": 0, "y": 0, "rotation": 0}
]
```

坐标、旋转、重叠、越界、未知物品等校验继续由 `basic_backpack_v1` 负责。

## 物品工厂来源

`initialize_battle()` 需要 `item_factories`，即：

```python
{
    "stone": StoneBattleItem,
    "banana": BananaBattleItem
}
```

当前仓库已经有抽象战斗物品基类，但还没有真实物品工厂注册表。因此 V1 `main` 需要明确一个依赖边界：

```text
main 负责加载或接收 item_factories
initialize_battle 负责使用 item_factories 实例化 BattleItem
具体物品类负责自己的触发器和效果
```

推荐后续实现时提供两层接口：

```python
run_battle_from_file(input_path, item_factories, item_catalog=ITEM_CATALOG) -> dict
main(argv=None) -> int
```

这样测试可以直接传入假的 `item_factories`，命令行入口则可以从默认注册表加载真实工厂。

如果输入文件中出现没有工厂的 `item_id`，V1 应快速失败，并在结果或异常信息中明确指出缺失的物品工厂。

## 调度流程

### 1. 解析命令行参数

建议命令行形态：

```text
python main_v1.py --input examples/battle_run_v1.json
```

后续可选参数：

```text
--output result.json
--max-frames 1000
--frame-delta 1.0
```

命令行参数优先级建议高于输入文件中的 `settings`，便于批量实验覆盖运行参数。

### 2. 读取并解析输入文件

`main` 读取 JSON 文件，检查：

- 文件存在。
- JSON 可解析。
- `schema_version == "battle_run_v1"`。
- `players` 存在且长度为 2。
- 每个玩家包含 `player_id`、`health`、`max_stamina`、`stamina`、`placements`。
- 每个玩家的 `max_stamina` 为正数。
- 每个玩家的 `stamina` 等于 `max_stamina`，表示标准战斗开局满耐力。
- `settings.max_frames` 和 `settings.frame_delta` 为正数。

结构层面的错误由 `main` 报出；背包摆放合法性继续交给背包模块。

### 3. 规范化 player_specs

`initialize_battle()` 当前只需要：

```python
player_specs = [
    {
        "player_id": 0,
        "health": 25,
        "max_stamina": 5.0,
        "stamina": 5.0,
        "placements": [...]
    },
    ...
]
```

所以 `main` 应从输入文件中抽取上述字段，形成 `player_specs`。`class_id` 等当前战斗对象不消费的字段放入 `run_metadata`，用于结果回显、调试和后续扩展。

### 4. 初始化战斗

调用：

```python
battle_state = initialize_battle(
    player_specs=player_specs,
    item_factories=item_factories,
    item_catalog=ITEM_CATALOG,
)
```

如果 `settings.seed` 不是 `null`，`main` 应基于该 seed 创建或配置 `BattleState.rng`。所有具体物品的命中、伤害等随机逻辑都应从 `BattleState.rng` 取数，而不是使用全局 `random`。

这一步会间接完成：

- 背包占用矩阵构建。
- 物品实例 key 生成。
- star / diamond / triangle marker link 分析。
- `BattleItem` 实例化。
- `PlayerState` 创建。
- `BattleState.active_items` 创建。

`main` 不应保存或重建中间背包矩阵，除非后续为了调试输出专门增加 `debug` 模式。

### 5. 运行战斗循环

V1 直接调用：

```python
winner = battle_state.run(max_frames=max_frames, frame_delta=frame_delta)
```

运行结束后根据状态判断：

- 如果 `battle_state.winner is not None`，说明战斗已有胜者。
- 如果跑满 `max_frames` 后仍无胜者，说明战斗未在帧上限内结束，结果应标记为 `max_frames_reached`。

当前 `BattleState.check_battle_end()` 只在恰好一名玩家存活时设置胜者。如果双方同时死亡、双方都存活到上限，V1 不额外推断胜负。

### 6. 结构化结果

推荐结果格式：

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
      "max_stamina": 5.0,
      "stamina": 3.0,
      "block": 0,
      "buffs": {},
      "debuffs": {},
      "items": ["stone1"]
    },
    {
      "player_id": 1,
      "class_id": "reaper",
      "health": 0,
      "max_stamina": 5.0,
      "stamina": 4.0,
      "block": 0,
      "buffs": {},
      "debuffs": {},
      "items": []
    }
  ],
  "active_items": [
    {"player_id": 0, "item_key": "stone1", "item_id": "stone"}
  ],
  "log": []
}
```

`finish_reason` 建议取值：

- `"winner"`: 已产生胜者。
- `"max_frames_reached"`: 达到帧上限仍无胜者。
- `"error"`: 输入、初始化或运行时发生错误。

当发生错误时，结果可以变为：

```json
{
  "schema_version": "battle_result_v1",
  "winner": null,
  "finish_reason": "error",
  "error": {
    "type": "ValueError",
    "message": "missing item factory for item_id: stone"
  }
}
```

## 公开函数草案

后续代码实现时，建议把命令行入口和可测试核心函数分开。

```python
def load_battle_run_file(input_path):
    """Read and validate the battle_run_v1 JSON file."""


def normalize_player_specs(run_config):
    """Return player_specs for initialize_battle and metadata for result echo."""


def run_battle_from_config(run_config, item_factories, item_catalog=ITEM_CATALOG):
    """Initialize and run one battle, then return a result dict."""


def run_battle_from_file(input_path, item_factories, item_catalog=ITEM_CATALOG):
    """Load a battle_run_v1 file and execute it."""


def main(argv=None):
    """CLI wrapper. Parse args, call run_battle_from_file, print/write JSON."""
```

其中 `run_battle_from_config()` 是最重要的单元测试对象。

## 错误处理原则

V1 建议保持错误清晰、直接：

- 作为库函数调用时，允许抛出 `ValueError`、`FileNotFoundError`、`json.JSONDecodeError` 等原始异常或轻量包装异常。
- 作为 CLI 调用时，捕获异常并输出 `battle_result_v1` 的 `"error"` 结果，同时返回非零退出码。
- 不吞掉背包模块和初始化模块的错误，因为这些错误通常正是输入文件或物品注册表需要修正的地方。

## 测试建议

实现 `main` 时至少覆盖：

- 可从合法 JSON 文件运行一场最小战斗。
- `players` 不是 2 名时报错。
- 缺少 `health` / `max_stamina` / `stamina` / `placements` / `player_id` 时报错。
- `stamina != max_stamina` 的标准战斗输入时报错。
- 未知 `schema_version` 报错。
- 同一 `settings.seed` 下，依赖随机数的战斗结果可复现。
- 缺失物品工厂时报错，并能在 CLI 结果中看到 `error.message`。
- 跑满 `max_frames` 且无胜者时返回 `finish_reason == "max_frames_reached"`。
- 有胜者时返回 `finish_reason == "winner"`，并回显最终 `frame`、`time`、玩家生命值。
- `class_id` 不参与当前 V1 战斗计算，但能在结果中按玩家回显。

## V1 暂不处理

- 商店、金币、刷新、保留、折扣。
- 合成、combine lock、催化剂。
- 真实完整物品数据库导入。
- 完整真实命中、暴击、疲劳、复杂资源、冷却时间线。首版只接入 `BattleState.rng` 和玩家耐力字段所需的最小能力。
- 强化学习 observation / action space。
- 独立 `subclass_id`。如项目知识库所述，如果 subclass 已由可见拥有物品表达，则不应额外暴露给策略；当前 V1 只保留玩家文件中可见物品和 `class_id`。
- 对战日志系统。可以预留 `collect_log` 和 `log` 字段，但木剑首版不落地 combat log，也不在 main 中伪造日志。

## 后续演进点

当真实物品效果逐步加入后，`main` 可以稳定不变，只扩展依赖：

- 增加 `item_factory_registry_v1.py`，集中维护 `item_id -> BattleItem factory`。
- 增加示例输入文件，例如 `examples/battle_run_v1.json`。
- 增加可选 `--debug-backpack`，输出每名玩家的占用矩阵和 marker links。
- 增加战斗日志收集接口，供调试物品触发链。
- 增加批量评估入口，把多份玩家结构化文件跑成结果表。
