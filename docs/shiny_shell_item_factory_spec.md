# Shiny Shell item factory SPEC

## 1. Requirements（需求）

实现 Shiny Shell（闪光蜗牛壳），使其可由默认工厂和战斗 JSON 创建并参与战斗。

Wiki 数据（查询于 2026-07-25）：

| 字段 | 值 |
| --- | --- |
| `item_id` | `shiny_shell` |
| 职业 / 稀有度 / 价格 | `Neutral` / `Common` / `2` |
| 类型 | `Accessory`，`nature`、`holy` |
| 效果 | `5s` 后治疗 `5`，每个 ⭐ Holy 物品额外治疗 `3` |
| 格子 | 单格；左右各一个星标 |
| 镶嵌位 | `0` |

来源：[中文 Wiki 闪光蜗牛壳](https://backpackbattles.wiki.gg/zh/wiki/%E9%97%AA%E5%85%89%E8%9C%97%E7%89%9B%E5%A3%B3)，页面显示修订 `oldid=5539`，最后编辑于 2025-11-12。

验收行为：

- 受 Heat/Cold 与外部速度 modifier 影响，累计到 `5s` 时仅激活一次。
- 治疗量为 `5 + 3 * 星标连接的 Holy 物品实例数`。
- 非 Holy、未连接及自身不计数；同一实例只计一次。
- 即使触发时生命已满，也不在之后重试。

范围外：合成、商店、治疗增减倍率、星标物品主动激活及 combat log。

## 2. Design（设计）

### 2.1 `AfterTimeTrigger`

在 `item_factory_registry_v1.py` 新增：

```python
class AfterTimeTrigger(CooldownTrigger):
    def __init__(self, delay_seconds: float): ...
    def update(self, context: BattleContext) -> bool: ...
```

伪代码：

```text
初始化 CooldownTrigger(delay_seconds)，has_triggered=False
update：
    若 has_triggered：返回 False
    若 super().update(context) 为 False：返回 False
    has_triggered=True
    返回 True
```

因此继续复用现有冷却速度公式，但第一次成功后永久关闭。

### 2.2 `HolyLinkedHealEffect`

```python
class HolyLinkedHealEffect(HealEffect):
    def __init__(self, base_amount: int, amount_per_holy: int): ...
    def prepare_amount(self, context: BattleContext) -> None: ...
    def apply(self, context: BattleContext) -> bool: ...
```

伪代码：

```text
构造时用 HealEffect 校验 base_amount，并校验 amount_per_holy 为非负 int
首次 apply：
    遍历 context.item.linked_items
    统计 icon_types 含 "holy" 的实例
    amount = base_amount + count * amount_per_holy
    缓存 count 和已准备状态
调用 HealEffect.apply(context) 并返回其 bool
```

缓存属于 effect 实例，布局按现有战斗模型在战斗期间保持不变。

### 2.3 `ShinyShell`

```python
class ShinyShell(BattleItem):
    item_id = "shiny_shell"
    display_name = "Shiny Shell"
    item_classes = ("Neutral",)
    rarity = "Common"
    cost = 2
    item_types = ("Accessory",)
    icon_types = ("nature", "holy")
    is_active_item = True
    socket_count = 0
```

`__init__()` 组装独立实例：

```python
triggers=[AfterTimeTrigger(5.0)]
effects=[HolyLinkedHealEffect(5, 3)]
```

`run_effect(trigger_results, context) -> None`：trigger 为真时调用唯一 effect，否则返回。

注册与目录：

```json
"shiny_shell": {
  "item_id": "shiny_shell",
  "shape_cells": [[0, 0]],
  "star_cells": [[-1, 0], [1, 0]]
}
```

并在 `DEFAULT_ITEM_FACTORIES` 注册 `"shiny_shell": ShinyShell`。

## 3. Realize（实现任务）

1. 实现 `AfterTimeTrigger` 的构造与 `update()`。
2. 实现 `HolyLinkedHealEffect` 的构造、准备与 `apply()`。
3. 实现 `ShinyShell.__init__()`、`run_effect()`、工厂注册和目录数据。
4. 添加下列测试并运行全套测试。

## 4. Acceptance Criteria / Tests（验收）

1. `test_after_time_trigger_fires_once_after_delay`：`5s` 前为假、到时为真、之后永久为假。
2. `test_after_time_trigger_reuses_cooldown_speed_modifiers`：Heat/Cold 仍按现有公式推进。
3. `test_holy_linked_heal_effect_counts_only_linked_holy_items`：两个 Holy 得到 `11` 治疗，忽略非 Holy 和未连接物品。
4. `test_holy_linked_heal_effect_prepares_amount_once`：计数只准备一次且实例间不共享缓存。
5. `test_shiny_shell_is_registered_with_metadata_and_components`：验证元数据与组件参数。
6. `test_shiny_shell_triggers_once_and_does_not_retry_at_full_health`：满血触发后不在后续时间再次治疗。
7. `test_initializer_links_shiny_shells_left_and_right_stars`：目录坐标产生正确的两个链接。
8. `test_initializer_builds_shiny_shell_as_active_item`：JSON 初始化和 active item 接入成功。
9. 仓库全部既有测试通过。
