# 当前测试失败兼容修复 SPEC

状态：V3，已实施并验收通过  
日期：2026-07-21

修订说明：用户已经把 `BattleItem.__init__` 的三个列表参数改为 `None` 默认值，并在函数体内创建空列表，V2 中的 `dataclasses.Field` 错误已经消失。V3 按最新代码保留“省略参数时创建独立列表、显式传入列表时直接接管引用”的所有权设计。

## 1. Requirements（需求）

### 1.1 目标

重新诊断当前完整测试套件，在保留最新代码设计的前提下完成最小修复方案：

- 保留 `Trigger`、`Effect` 类型。
- 保留 `BuffSlot`、`DebuffSlot` 结构化状态模型，不回退到字典。
- 保留当前 `BattleItem` 列表参数的所有权语义。
- 优先修改仍按旧模型编写的测试。
- 只在生产模块尚未适配新状态模型时修改生产代码。
- 不引入新架构、抽象层或第三方依赖。
- 不修改 `AGENTS.md` 或用户的其他无关改动。

### 1.2 实施前测试基线

执行命令：

```powershell
& "C:\Users\win\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m unittest discover -s tests -v
```

实施前结果：共 53 个测试，48 个通过，2 个失败（failure），3 个异常（error）。

相比 SPEC V2 的 42 个通过、2 个失败、9 个异常，当前 `None` 默认值修复已经使全部 7 个 `Field` 相关异常消失。剩余 5 个失败只涉及玩家状态测试兼容和主入口序列化。

仓库测试全部使用标准库 `unittest`；本机所用 Python 运行时没有安装 `pytest`，但这不影响完整执行现有测试。

### 1.3 功能要求

#### R1：列表参数所有权

WHEN 创建多个 `BattleItem` 且省略列表参数，THEN 每个实例 SHALL 获得独立的 `triggers`、`effects` 和 `linked_items` 空列表。

WHEN 调用某一物品的 `add_linked_item()`，THEN 其他使用默认 `linked_items` 的物品 SHALL NOT 改变。

WHEN 调用方显式传入列表，THEN `BattleItem` SHALL 直接接管该列表引用，不执行浅复制；调用方 SHALL 将其视为已转交所有权，不再复用或修改。

WHEN 没有提供 trigger/effect，THEN 构造器 SHALL 继续抛出 `ValueError`。

#### R2：结构化玩家状态

WHEN 创建 `PlayerState`，THEN `buffs` SHALL 使用 `BuffSlot`，`debuffs` SHALL 使用 `DebuffSlot`。

WHEN 修改一名玩家的 buff、debuff 或 items，THEN 另一名玩家的默认状态 SHALL NOT 改变。

#### R3：结果 JSON 适配

WHEN `main_v1` 序列化玩家，THEN `BuffSlot` 和 `DebuffSlot` SHALL 转换成普通 JSON 对象。

WHEN状态均为默认值，THEN 输出 SHALL 显式包含数据类的全部字段及零值，不得因 `TypeError` 进入错误结果。

#### R4：测试夹具适配

WHEN 测试构造 `BattleItem` 或测试子类，THEN 测试 SHALL 使用 `Trigger()` / `Effect()` 实例，而不是字符串占位符。

#### R5：回归要求

WHEN 修复完成后连续执行完整测试套件，THEN 所有测试 SHALL 稳定通过，不得有执行顺序导致的状态串线。

## 2. Failure Analysis（失败归因）

### 2.1 已解决：普通参数中的 `dataclasses.Field`

最新代码已经从：

```python
linked_items: list[str] = field(default_factory=list)
```

改为：

```python
linked_items: list[str] | None = None
self.linked_items = linked_items if linked_items is not None else []
```

`triggers` 和 `effects` 使用相同模式。每次省略参数都会执行新的 `[]`，因此默认列表不再跨物品共享，也不会产生 `Field` 类型错误。

此前受影响的两个初始化器测试、四个战斗模块测试和一个主入口战斗执行路径当前均已通过。本轮不再计划修改这段生产代码。

当前实现对显式列表不做复制。这被 V3 定义为所有权转交语义：工厂必须为每件物品创建新的列表以及独立的 trigger/effect 实例，传入后不得继续复用或修改。

### 2.2 当前根因 A：测试仍把 `BuffSlot` 当作旧字典

`test_player_state_uses_independent_mutable_defaults` 已正确执行：

```python
first_player.buffs.Heat = 1
```

并已用 `[Trigger()]` / `[Effect()]` 构造测试物品，但仍断言：

```python
self.assertEqual(second_player.buffs, {})
```

`second_player.buffs` 实际是默认值完整的 `BuffSlot`，因此与空字典不相等。这是测试兼容问题，不应回退生产代码。

造成的失败：

1. `test_player_state_uses_independent_mutable_defaults`。

### 2.3 当前根因 B：`main_v1._serialize_player` 未适配数据类

当前生产代码仍执行：

```python
"buffs": dict(player.buffs),
"debuffs": dict(player.debuffs),
```

`BuffSlot` 和 `DebuffSlot` 不是键值对迭代器，`dict()` 因此抛出：

```text
TypeError: 'BuffSlot' object is not iterable
```

造成的失败：

2. `test_run_battle_from_config_returns_max_frames_result`：异常。
3. `test_run_battle_from_config_returns_winner_result`：异常。
4. `test_run_battle_from_file_loads_json_then_runs`：异常。
5. `test_main_prints_success_result_for_empty_battle`：异常被 CLI 捕获，表现为退出码 1 而不是 0。

## 3. Design（设计）

### 3.1 总体决策

采用一处最小生产集成修复和测试兼容更新：

1. 不修改 `battle_module_v1.py` 当前构造器行为。
2. `main_v1._serialize_player` 使用标准库 `dataclasses.asdict()` 序列化两个状态数据类。
3. 测试夹具改用真实 `Trigger` / `Effect` 实例。
4. 玩家默认状态测试按数据类字段验证，不再与 `{}` 比较。
5. 新增构造器校验和列表所有权契约测试，锁定最新设计。

不新增序列化适配器、协议类、深复制逻辑或第三方依赖。

### 3.2 数据流

```text
BattleItem 列表参数
    -> 省略参数：创建实例私有空列表
    -> 显式参数：直接接管调用方列表引用

PlayerState
    -> BuffSlot / DebuffSlot
    -> main_v1._serialize_player
    -> dataclasses.asdict
    -> JSON 普通对象
```

### 3.3 生产函数级设计

#### 3.3.1 `battle_module_v1.BattleItem.__init__`

接口和实现保持不变：

```python
def __init__(
    self,
    item_id: str | None = None,
    item_key: str | None = None,
    player_id: int | None = None,
    is_active_item: bool = False,
    triggers: list[Trigger] | None = None,
    effects: list[Effect] | None = None,
    linked_items: list[str] | None = None,
):
```

当前伪代码：

```text
保存身份字段
triggers 为 None 时创建空列表，否则直接接管传入引用
effects 为 None 时创建空列表，否则直接接管传入引用
linked_items 为 None 时创建空列表，否则直接接管传入引用
初始化 triggered=False
校验 trigger/effect 非空
```

约束：工厂负责逐物品创建新的列表和独立组件；构造器不执行浅复制或深复制。

#### 3.3.2 `main_v1._serialize_player`

接口保持不变：

```python
def _serialize_player(player, metadata):
```

拟议伪代码：

```text
读取玩家基础字段和 metadata
用 asdict(player.buffs) 生成普通字典
用 asdict(player.debuffs) 生成普通字典
保持 items 的键列表输出
返回玩家结果对象
```

`main_v1.py` 需要增加：

```python
from dataclasses import asdict
```

默认输出：

```python
"buffs": {
    "Empower": 0,
    "Heat": 0,
    "Luck": 0,
    "Mana": 0,
    "Regeneration": 0,
    "Spikes": 0,
    "Vampirism": 0,
},
"debuffs": {
    "Poison": 0,
    "Blind": 0,
    "Cold": 0,
}
```

## 4. Test Design（逐测试设计）

### 4.1 `tests/test_battle_module_v1.py`

1. 整理导入，显式导入 `Trigger` 和 `Effect`。
2. `RecordingItem.__init__`：把字符串占位符替换为 `[Trigger()]` / `[Effect()]`。
3. `test_battle_item_requires_at_least_one_trigger`：effect 使用 `[Effect()]`，保留空 trigger 断言。
4. `test_battle_item_requires_at_least_one_effect`：trigger 使用 `[Trigger()]`，保留空 effect 断言。
5. `test_battle_item_stores_player_id_and_item_key`：使用真实组件实例，身份断言不变。
6. `test_add_linked_item_stores_keys_once_in_first_seen_order`：使用真实组件实例，链接顺序/去重断言不变。
7. 新增 `test_battle_item_without_components_fails`：完全省略 trigger/effect，断言抛出 `ValueError`。
8. 新增 `test_battle_item_list_container_ownership_contract`：
   - 两件省略 `linked_items` 的物品获得不同列表。
   - 第一件添加链接不影响第二件。
   - 显式传入 trigger/effect/link 列表时，物品属性与对应列表使用 `assertIs` 验证为同一对象。
9. `test_player_state_uses_independent_mutable_defaults`：
   - 保留当前 `[Trigger()]` / `[Effect()]` 物品。
   - 修改第一名玩家的 `buffs.Heat` 和 `debuffs.Poison`。
   - 断言两个玩家的状态对象不是同一对象。
   - 断言第二名玩家的 `Heat`、`Poison` 仍为 0，`items` 仍为空。

### 4.2 `tests/test_battle_initializer_v1.py`

1. 导入 `Trigger`、`Effect`。
2. `TestBattleItem.__init__`：把字符串占位符替换为 `[Trigger()]` / `[Effect()]`。
3. 现有 9 个初始化器测试的行为断言保持不变。

### 4.3 `tests/test_main_v1.py`

1. 导入 `Trigger`、`Effect`。
2. `DamageItem.__init__`：把字符串占位符替换为 `[Trigger()]` / `[Effect()]`。
3. 扩展 `test_run_battle_from_config_returns_max_frames_result`：精确断言默认 buffs/debuffs JSON 字典。
4. `test_run_battle_from_config_returns_winner_result`：保留胜者、帧数、生命值和主动物品断言，用于覆盖有主动物品的序列化路径。
5. `test_run_battle_from_file_loads_json_then_runs`：保留文件入口成功断言。
6. `test_main_prints_success_result_for_empty_battle`：保留退出码 0 和成功原因断言。

## 5. Tasks（任务拆解）

1. **审批 SPEC V3**（已完成）
   - 用户已明确要求执行。

2. **锁定当前列表所有权设计**（已完成）
   - 不修改 `battle_module_v1.py`。
   - 新增缺省组件及列表所有权契约测试。

3. **修复数据类序列化**（已完成）
   - 在 `main_v1.py` 导入 `asdict`。
   - 修改 `_serialize_player` 的 buffs/debuffs 两行。

4. **更新战斗模块测试**（已完成）
   - 替换字符串组件夹具。
   - 修改旧字典断言。
   - 新增两个构造器契约测试。

5. **更新初始化器与主入口测试**（已完成）
   - 使用实际组件实例。
   - 增加结构化状态 JSON 断言。

6. **验证**（已完成）
   - 隔离运行三个受影响测试模块。
   - 连续两次运行完整 `unittest` 套件。
   - 运行语法编译。
   - 运行 `git diff --check`。
   - 审查差异，确认未修改 `AGENTS.md` 和无关用户文件。

## 6. Acceptance Criteria / Tests（验收标准）

### 6.1 测试验收

- 原有 53 个测试全部通过。
- 新增 `test_battle_item_without_components_fails` 通过。
- 新增 `test_battle_item_list_container_ownership_contract` 通过。
- 完整测试共 55 个，0 failure、0 error。
- 完整套件连续执行两次均通过。

### 6.2 行为验收

- 默认列表在不同物品实例之间相互独立。
- 显式列表由物品直接接管引用。
- 完全省略 trigger/effect 时抛出 `ValueError`。
- `BuffSlot` / `DebuffSlot` 保持数据类设计。
- 两名玩家的默认 buff、debuff、items 相互独立。
- 内存入口、文件入口和 CLI 成功路径均可输出 JSON。
- 默认 buffs/debuffs JSON 包含结构化字段及零值。

### 6.3 质量验收

- 不新增第三方依赖。
- 不引入深复制或额外架构。
- 不改变战斗循环、链接顺序、胜者判断或异常文本。
- `git diff --check` 通过。
- `AGENTS.md` 不被本修复修改。

## 7. 实施边界

本次实际实施范围：

- `main_v1.py`
- `tests/test_battle_module_v1.py`
- `tests/test_battle_initializer_v1.py`
- `tests/test_main_v1.py`

`battle_module_v1.py` 当前实现保持不变。

根目录未跟踪文件 `test.py` 是默认参数行为的临时演示文件，不在 `tests/` 中，也不会被本轮修改或计入 53 个测试的基线。

没有发生超出上述范围的代码或测试修改。

## 8. Implementation Result（实施结果）

- `main_v1._serialize_player` 已使用 `asdict()` 输出 `BuffSlot` / `DebuffSlot`。
- 三个测试模块的组件夹具已改为真实 `Trigger()` / `Effect()` 实例。
- 玩家默认状态测试已按数据类字段验证隔离性。
- 已新增缺省组件校验和列表所有权契约测试。
- 三个受影响测试模块隔离运行全部通过。
- 完整测试套件连续运行两次，均为 55/55 通过。
- 目标文件语法编译通过。
- `git diff --check` 通过，仅有既有行尾转换警告。
