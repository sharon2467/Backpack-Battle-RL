# 战斗模块 V1 设计草案

## 目标

先搭建最小战斗框架，用来训练“给定物品集合下的最优摆盘 AI”。

V1 的核心抽象：

```text
每个物品 = 触发器 + 效果器
```

触发器负责判断物品是否触发；效果器负责执行物品触发后的效果。具体有多少种触发器、多少种效果器，以及它们各自需要什么输入、产生什么输出，先不在 V1 草案里展开。

## 物品父类

所有战斗物品都继承同一个物品父类。

```python
class BattleItem:
    item_id = None
    item_key = None
    player_id = None
    is_active_item = False
    triggers = []
    effects = []
    linked_items = []

    def update_triggers(self, context):
        pass

    def is_triggered(self):
        pass

    def run_effects(self, context):
        pass

    def run_linked_items(self, context):
        pass

    def add_linked_item(self, linked_key):
        pass
```

约定：

- 每个物品必须有至少一个触发器。
- 每个物品必须有至少一个效果器。
- `item_key` 用来区分同名物品的不同实例，由初始化器按同一玩家内的出现次数生成，例如 `stone1`、`stone2`。
- `player_id` 表示该物品属于哪一方玩家。
- `is_active_item` 表示该物品是否进入主动物品循环。
- `linked_items` 是目标物品 `item_key` 的列表，相当于指向 `PlayerState.items` 的轻量指针。
- `add_linked_item(linked_key)` 是登记关联的唯一入口，负责按 `item_key` 去重并保留首次登记顺序。
- 同一个物品实例可以保存自己的运行时状态，例如冷却、触发次数、临时加成。
- 背包分析器在战斗开始前负责实例化物品，并把逻辑关联登记到对应物品的 `linked_items` 中。
- 具体物品只负责定义自己的触发器和效果器，不负责控制整场战斗循环。

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
- 主动物品触发后，由它自己的 `run_effects()` 检查并调用 `linked_items`。
- 被动物品不单独进入主循环。
- 关联物品的调用发生在物品内部，因此可以递归触发更深层的关联物品。
- 如果某个物品既能独立触发，又能被其他物品触发，它可以同时是主动物品和关联物品。

`run_effects()` 的内部流程可以是：

```text
run this item's effects
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
    players = []
    active_items = []
    winner = None
```

用途：

- 记录当前帧和战斗时间。
- 保存双方玩家。
- 保存主动物品列表。
- 判断战斗是否结束。

## 玩家状态

玩家状态保存单个玩家在战斗中的可变信息。

```python
class PlayerState:
    player_id = None
    health = 0
    block = 0
    buffs = {}
    debuffs = {}
    items = {}
```

用途：

- 记录生命、护盾、buff、debuff 等会被物品效果改变的信息。
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

- 具体触发器类型。
- 具体效果器类型。
- 触发器和效果器的输入输出。
- 商店。
- 合成。
- 完整真实物品规则。
