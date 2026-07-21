# 战斗模块 V1 设计草案

## 目标

先搭建最小战斗框架，用来训练“给定物品集合下的最优摆盘 AI”。

V1 的核心抽象：

```text
每个物品 = 可复用 trigger 实例列表 + 可复用 effect 实例列表
```

trigger 负责更新并判断物品是否触发；effect 负责执行物品触发后的效果。多个物品可以复用同一种 trigger/effect 类，例如许多武器都可以使用 `CooldownTrigger`、`StaminaConsumptionEffect` 和 `MeleeAttackEffect`，但每个物品实例必须持有自己的 trigger/effect 实例，避免冷却进度、触发次数等状态在不同物品之间串线。

## 物品父类

所有战斗物品都继承同一个物品父类。

```python
class BattleItem:
    item_id = None
    item_key = None
    player_id = None
    display_name = None
    item_classes = ()
    rarity = None
    cost = None
    item_types = ()
    icon_types = ()
    is_active_item = False
    triggers = ()
    effects = ()
    linked_items = ()

    def update_triggers(self, context):
        pass

    def is_triggered(self):
        pass

    def run_effects(self, context):
        pass

    def run_own_effects(self, context):
        pass

    def run_linked_items(self, context):
        pass

    def add_linked_item(self, linked_key):
        pass
```

约定：

- 每个物品必须有至少一个触发器。
- 每个物品必须有至少一个效果器。
- `triggers` 保存 trigger 实例，不保存字符串标记。
- `effects` 保存 effect 实例，不保存字符串标记。
- `item_key` 用来区分同名物品的不同实例，由初始化器按同一玩家内的出现次数生成，例如 `stone1`、`stone2`。
- `player_id` 表示该物品属于哪一方玩家。
- `display_name`、`item_classes`、`rarity`、`cost`、`item_types`、`icon_types` 是所有真实物品共有的元数据字段。
- `is_active_item` 表示该物品是否进入主动物品循环。
- `linked_items` 是目标物品 `item_key` 的列表，相当于指向 `PlayerState.items` 的轻量指针。
- `add_linked_item(linked_key)` 是登记关联的唯一入口，负责按 `item_key` 去重并保留首次登记顺序。
- 同一个物品实例可以保存自己的运行时状态；优先把可复用状态放在 trigger/effect 实例中，例如冷却进度放在 `CooldownTrigger` 中。
- 背包分析器在战斗开始前负责实例化物品，并把逻辑关联登记到对应物品的 `linked_items` 中。
- 具体物品只负责组装自己的 trigger/effect 实例，不负责控制整场战斗循环。

## Trigger 和 Effect 组件

trigger 和 effect 是独立组件实例。`BattleItem.update_triggers(context)` 只负责按顺序调用 trigger 实例接口，并把结果汇总到 `self.triggered`；`BattleItem.run_own_effects(context)` 只负责按顺序调用 effect 实例接口，并根据 effect 返回值决定是否继续。

建议接口：

```python
class BattleTrigger:
    trigger_key = None

    def update(self, context):
        """Update internal state and return whether this trigger is satisfied."""


class BattleEffect:
    effect_key = None

    def apply(self, context):
        """Apply this effect and return whether later effects should continue."""
```

`BattleItem.update_triggers(context)` 的默认流程：

```python
def update_triggers(self, context):
    results = []
    for trigger in self.triggers:
        results.append(trigger.update(context))
    self.triggered = all(results)
```

`BattleItem.run_own_effects(context)` 的默认流程：

```python
def run_own_effects(self, context):
    for effect in self.effects:
        should_continue = effect.apply(context)
        if should_continue is False:
            return False
    return True
```

约定：

- V1 中多个 trigger 默认是 AND 关系，即所有 trigger 都返回 true 时物品才触发。
- 复杂触发语义可以封装成一个组合 trigger，例如 `AnyTrigger`、`SequenceTrigger` 或物品专用 trigger，而不是让 `BattleItem` 理解所有组合规则。
- 有状态 trigger/effect 必须是每个物品实例独立创建的新对象，不能把 `CooldownTrigger(...)` 这类对象直接作为类属性共享。
- trigger 可以有副作用，例如推进冷却、记录触发状态；资源消耗优先建模为 effect。`CooldownTrigger` 特别不读取、不判断、不消耗耐力。
- effect 可以有副作用，例如扣血、扣护盾、加 buff、消耗资源；这些副作用必须通过 `context` 修改公共战斗状态。
- effect 的返回值用于控制当前物品的后续执行。返回 `False` 表示停止后续 effect，并让 `run_effects()` 跳过 linked item 调用；返回 `True` 表示继续。

首批可复用组件：

- `CooldownTrigger`: 最常见的主动触发器。逐帧累积冷却进度，冷却完成后扣除一轮冷却进度并返回 true；它不处理耐力。
- `StaminaConsumptionEffect`: 最常见的耐力支付效果。耐力足够时扣除耐力并返回 true；耐力不足时不扣耐力并返回 false，停止后续 effect。
- `MeleeAttackEffect`: 最常见的近战武器攻击效果。使用 `BattleState.rng` 做命中和伤害随机，命中后先扣对手 `block`，再扣 `health`。

## 主动物品和被动物品

主动物品：单独放在背包内也能够触发的物品。

被动物品：必须依赖其他物品触发后，才有机会触发的物品。

战斗循环只主动遍历主动物品。被动物品由主动物品自身的 `linked_items` 带动。

逻辑关联先只考虑当前背包布局能直接得到的关系，例如：

- marker 指向关系。
- 相邻关系。
- 未来需要时再加入其他关系。

## 战斗循环

V1 使用简单帧循环。

```text
while battle not finished:
    regenerate player stamina

    for active_item in active_items:
        context = build_context(active_item)
        active_item.update_triggers(context)

        if active_item.is_triggered():
            active_item.run_effects(context)

    update battle state
    check battle end
```

说明：

- 每一帧按顺序检查主动物品。
- 每一帧先按 `frame_delta` 为玩家自然回复耐力，再检查主动物品。
- 主动物品触发后，由它自己的 `run_effects()` 检查并调用 `linked_items`。
- 被动物品不单独进入主循环。
- 关联物品的调用发生在物品内部，因此可以递归触发更深层的关联物品。
- 如果某个物品既能独立触发，又能被其他物品触发，它可以同时是主动物品和关联物品。
- 具体物品如果冷却完成但耐力不足，不应等待耐力；`CooldownTrigger` 已经进入新一轮冷却，随后由 `StaminaConsumptionEffect` 停止后续 effect。

`run_effects()` 的内部流程可以是：

```text
if run this item's effects:
    run_linked_items(context)
```

`run_linked_items()` 的内部流程可以是：

```text
for linked_key in self.linked_items:
    linked_item = context.owner.items[linked_key]
    linked_context = context.for_item(linked_item)
    linked_item.update_triggers(linked_context)

    if linked_item.is_triggered():
        linked_item.run_effects(linked_context)
```

## 战斗状态

战斗状态保存整场战斗共享的信息。

```python
class BattleState:
    frame = 0
    time = 0.0
    frame_delta = 1.0
    players = []
    active_items = []
    rng = None  # per-battle random.Random instance
    winner = None
```

用途：

- 记录当前帧和战斗时间。
- 记录当前帧步长，供物品逐帧推进冷却。
- 保存双方玩家。
- 保存主动物品列表。
- 保存整场战斗共享的随机数源，供命中、伤害、暴击和未来随机触发使用。`rng` 应是每个 `BattleState` 实例独立持有的 `random.Random`，不要作为所有战斗共享的类级对象。
- 判断战斗是否结束。

## 玩家状态

玩家状态保存单个玩家在战斗中的可变信息。

```python
class PlayerState:
    player_id = None
    health = 0
    stamina = 0.0
    max_stamina = 0.0
    stamina_regen_per_second = 1.0
    block = 0
    buffs = {}
    debuffs = {}
    items = {}
```

用途：

- 记录生命、耐力、耐力上限、护盾、buff、debuff 等会被物品效果改变的信息。
- `stamina` 和 `max_stamina` 是战斗中可变玩家属性，物品效果可以动态修改。
- 标准战斗开始时 `stamina == max_stamina`，即初始耐力满格。
- 以字典形式持有该玩家的物品实例，键是 `item_key`，值是 `BattleItem`。
- 让物品效果可以明确修改“自己一方”或“对手一方”。

`item_key` 只在单个玩家内部唯一。两名玩家都可以有自己的 `stone1`；如果需要全局定位一个物品实例，使用 `(player_id, item_key)`。

## 摆盘 AI 接口

训练摆盘 AI 时，外部接口可以保持很薄：

```python
evaluate_layout(placements, opponent) -> score
```

流程：

1. 背包模块检查摆放是否合法。
2. 背包分析器从 `placements` 读取物品 id 和位置，实例化所有战斗物品。
3. 背包分析器把物品之间的逻辑关联登记到各自的 `linked_items` 中。
4. 战斗模块运行帧循环。
5. 根据胜负、剩余生命或其他指标返回分数。

## 暂不设计

V1 暂不展开：

- 除 `CooldownTrigger`、`StaminaConsumptionEffect` 和 `MeleeAttackEffect` 外的更多 trigger/effect 类型。
- 复杂 trigger 组合语义。
- 商店。
- 合成。
- 完整真实物品规则。
