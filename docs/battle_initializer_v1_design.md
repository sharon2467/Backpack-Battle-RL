# Battle Initializer V1 设计草案

## 目标

`battle_initializer` 负责把背包分析结果接到战斗模块：

```text
placements -> placed_items -> BattleItem instances -> linked_items -> active_items
```

最终产出可以直接交给战斗循环的 `BattleState`，其中固定包含 2 名玩家的 `PlayerState`。

V1 只做初始化和装配，不实现真实物品效果、不改商店、不设计合成或 RL 环境接口。

## 核心原则

初始化器只负责把布局关系翻译成对象关系。

`placed_items`、`occupancy_matrix` 和 marker links 是初始化过程的中间数据。物品一旦被实例化，物品实例集中保存在 `PlayerState.items`，摆盘关系通过 `BattleItem.linked_items` 中的 `item_key` 表达。初始化器不再把坐标、marker cells、link metadata 或 `BattleState` 塞进物品的 `runtime`。

战斗执行时，物品需要的对局状态由外部调用方传入，例如：

```python
active_item.run_effects(context)
```

`run_effects()` 内部固定执行“更新 trigger、调用具体物品的 `run_own_effect()`、按返回值决定是否检查 linked items”。`context` 由战斗循环基于当前 `BattleState`、触发物品、所属玩家和对手玩家临时构造。物品实例保存自己的内部可变状态，例如冷却、触发次数和临时加成；公共对局状态不挂在物品身上。

## 依赖边界

背包模块继续负责：

- 校验 `placements` 中的 `item_id`、坐标、旋转和重叠。
- 生成 `occupancy_matrix`。
- 生成 `placed_items`。
- 根据 star、diamond、triangle marker 生成 marker links。

战斗模块继续负责：

- 定义 `BattleItem` 的触发和效果执行接口。
- 定义 `PlayerState`。
- 定义 `BattleState`。
- 在 `BattleState.step()` 中遍历 `active_items`。
- 在调用物品触发和效果时传入当前对局上下文。

`battle_initializer` 位于两者之间，只负责把静态布局变成战斗可用的对象图。

## 输入

推荐公开入口：

```python
initialize_battle(player_specs, item_factories, item_catalog=ITEM_CATALOG) -> BattleState
```

### player_specs

`player_specs` 是长度严格等于 2 的玩家构建参数列表：

```python
player_specs = [
    {
        "player_id": 0,
        "health": 25,
        "max_stamina": 5.0,
        "stamina": 5.0,
        "placements": [
            {"item_id": "stone", "x": 0, "y": 0, "rotation": 0},
        ],
    },
    {
        "player_id": 1,
        "health": 25,
        "placements": [],
    },
]
```

字段约定：

- `player_id`：写入 `PlayerState.player_id` 和每个 `BattleItem.player_id`。
- `health`：写入 `PlayerState.health`。V1 不根据 round 自动推导生命。
- `max_stamina`：写入 `PlayerState.max_stamina`。标准战斗开局时作为当前耐力满格值。
- `stamina`：写入 `PlayerState.stamina`。标准战斗开局要求 `stamina == max_stamina`。
- `placements`：交给背包模块分析。

`item_key` 由背包模块在 `build_occupancy_matrix()` 阶段按单个玩家的 `placements` 顺序生成，因此它只在该玩家内部唯一。初始化完成后，战斗逻辑使用 `item_key` 和 `player_id` 区分实例。

### item_key

背包模块为每个玩家的物品自动生成 `item_key`。规则是按 `placed_items` 顺序统计同名 `item_id` 的出现次数：

```python
stone -> stone1
stone -> stone2
banana -> banana1
```

`item_key` 只保证在单个玩家内部唯一。两名玩家都可以有自己的 `stone1`；需要全局定位时使用 `(player_id, item_key)`。

### item_factories

`item_factories` 把 `item_id` 映射到战斗物品工厂：

```python
item_factories = {
    "stone": StoneBattleItem,
    "banana": BananaBattleItem,
}
```

工厂可以是 `BattleItem` 子类，也可以是返回 `BattleItem` 实例的 callable。初始化器调用时只传入物品身份和所属玩家：

```python
factory(
    item_id=placed_item["item_id"],
    item_key=item_key,
    player_id=player_id,
)
```

V1 默认严格模式：`item_id` 没有对应工厂时直接报错，不静默创建通用占位物品。测试或实验如果需要假物品，可以显式传入测试工厂。

真实物品工厂应为每个物品实例创建独立的 trigger/effect 实例。不要在物品类属性上共享 `CooldownTrigger(...)`、`StaminaConsumptionEffect(...)`、`MeleeAttackEffect(...)` 这类对象，否则同名物品之间会共享冷却进度或其它运行时状态。

## 输出

初始化完成后返回：

```python
BattleState(
    frame=0,
    time=0.0,
    players=[player0_state, player1_state],
    active_items=[...],
    winner=None,
)
```

每个 `PlayerState`：

```python
PlayerState(
    player_id=player_id,
    health=health,
    max_stamina=max_stamina,
    stamina=stamina,
    stamina_regen_per_second=1.0,
    block=0,
    buffs={},
    debuffs={},
    items={
        "stone1": stone_item_1,
        "stone2": stone_item_2,
        "banana1": banana_item_1,
    },
)
```

`PlayerState.items` 是字典，键是背包模块生成的 `item_key`，值是对应的 `BattleItem` 实例。字典插入顺序按 `placed_items` 顺序。

`BattleState.active_items` 只保存 `battle_item.is_active_item == True` 的物品。

active item 顺序必须稳定：

1. 按 `player_specs` 输入顺序遍历 2 名玩家。
2. 每个玩家内部按 `PlayerState.items` 的插入顺序遍历物品。
3. 只加入 `is_active_item` 为真的物品。

这个顺序只是 V1 的确定性执行顺序。未来如果战斗循环改成事件时间线，可以在不改变背包初始化语义的前提下替换 active 调度。

## 初始化流程

### 1. 校验玩家数量

初始化器首先校验：

```python
len(player_specs) == 2
```

并校验 2 名玩家的 `player_id` 不重复。

### 2. 构建每个玩家的背包分析结果

对每个 `player_spec`：

```python
occupancy_matrix, placed_items = build_occupancy_matrix(
    player_spec["placements"],
    item_catalog,
)

star_links = find_star_links(placed_items, occupancy_matrix)
diamond_links = find_diamond_links(placed_items, occupancy_matrix)
triangle_links = find_triangle_links(placed_items, occupancy_matrix)
```

这一步得到的 `placed_items` 和 marker links 只用于后续实例化和连边，不作为战斗物品运行时数据保存。

### 3. 实例化 BattleItem

对每个 `placed_item`：

1. 读取 `placed_item["item_key"]`。
2. 找到 `item_factories[placed_item["item_id"]]`。
3. 调用工厂创建 `BattleItem`。
4. 校验返回值是 `BattleItem` 实例。
5. 校验 `battle_item.item_id == placed_item["item_id"]`。
6. 校验 `battle_item.item_key == placed_item["item_key"]`。
7. 校验 `battle_item.player_id == player_id`。
8. 写入玩家局部表：

```python
items_by_key[placed_item["item_key"]] = battle_item
```

战斗阶段以 `item_key` 作为玩家内部的实例身份，不再保留旧数字身份。

### 4. 装配 marker links

对每条 marker link：

```python
source_key = marker_link["source_item_key"]
target_key = marker_link["target_item_key"]
source_item = items_by_key[source_key]
```

然后通过 `BattleItem` 的接口登记关联：

```python
source_item.add_linked_item(target_key)
```

V1 中 `linked_items` 只保存目标 `item_key`，相当于指向 `PlayerState.items[target_key]` 的轻量指针。去重由 `add_linked_item()` 负责，避免同一个目标因为多个 marker 被递归执行多次。

如果未来需要区分 star、diamond、triangle 的不同语义，有两个可选演进方向：

- 在具体物品类中提供更明确的 link 接口，例如 `add_star_linked_item()`。
- 引入独立 `BattleLink` 数据类，让边携带 marker 类型。

V1 先保持最小接口，只把 marker links 翻译成 `linked_items`。

### 5. 创建 PlayerState

对每个玩家创建：

```python
player_state = PlayerState(
    player_id=player_id,
    health=player_spec["health"],
    max_stamina=player_spec["max_stamina"],
    stamina=player_spec["stamina"],
    items=items_by_key,
)
```

初始化器不预填 buffs/debuffs，沿用 `PlayerState` 的空默认值。

### 6. 创建 BattleState

所有玩家和物品创建完成后：

```python
battle_state = BattleState(
    players=[player0_state, player1_state],
    active_items=active_items,
)
```

初始化器不把 `battle_state` 回写到物品上。战斗循环在执行时根据 `BattleState` 和当前物品临时构造上下文。

## 对局上下文

为了避免物品持有全局状态，后续战斗模块应把触发和效果接口调整为显式传参：

```python
class BattleContext:
    battle_state: BattleState
    item: BattleItem
    owner: PlayerState
    opponent: PlayerState
```

因为 V1 固定只有 2 名玩家，`opponent` 是单个 `PlayerState`，不是列表。

上下文由战斗循环创建：

```python
context = BattleContext(
    battle_state=battle_state,
    item=active_item,
    owner=owner_player,
    opponent=opponent_player,
)
```

物品内部只保存自身状态；生命、护盾、buff、debuff、胜负、当前帧、当前时间等公共状态都通过 `context` 访问和修改。

## 数据结构示例

两个物品中，0 号物品的 star 指向 1 号物品。初始化后只保留对象关系：

```python
player_state.items == {
    "mage_hat1": source_item,
    "stone1": target_item,
}

source_item.item_key == "mage_hat1"
target_item.item_key == "stone1"
source_item.linked_items == ["stone1"]
```

如果 `source_item` 是 active item，它触发时会通过 `run_linked_items(context)` 读取 `context.owner.items["stone1"]`，再带动 `target_item`。目标物品需要的生命、护盾、buff、debuff、对手等信息都从 `context` 读取。

## 校验规则

V1 初始化器负责以下校验：

- `player_specs` 长度必须等于 2。
- `player_id` 不能重复。
- 每个玩家必须提供 `placements`。
- 每个玩家必须提供 `health`。
- 每个玩家必须提供 `max_stamina` 和 `stamina`。
- `max_stamina` 必须为正数。
- 标准战斗输入中 `stamina` 必须等于 `max_stamina`，表示初始耐力满格。
- 背包模块抛出的非法摆放错误原样向外抛出。
- `placed_item["item_id"]` 必须有对应工厂。
- 同一玩家内的 `placed_item["item_key"]` 必须唯一。
- 工厂返回值必须是 `BattleItem`。
- 工厂返回的 `item_id` 必须和 `placed_item["item_id"]` 一致。
- 工厂返回的 `item_key` 必须和 `placed_item["item_key"]` 一致。
- 工厂返回的 `player_id` 必须和当前 `player_id` 一致。
- marker link 中的 `source_item_key` / `target_item_key` 必须能在当前玩家的物品表中找到。

V1 不把以下情况视为初始化错误：

- 某个玩家没有 active item。
- 某个物品没有 marker link。
- marker link 图中存在环。

环状 link 是合法布局可能产生的图结构，但当前 `BattleItem.run_linked_items()` 没有递归保护。V1 先在文档中标为风险：开始测试带环关联前，需要在战斗执行层增加每帧 visited guard 或触发深度限制。

## 暂不处理

V1 暂不处理：

- 真实物品效果解析。
- 冷却、速度、资源、命中、暴击、疲劳等战斗时间线细节。
- 商店状态、合成状态、保留物品和折扣。
- subclass 的单独字段。可见 subclass 物品按普通 owned item 实例化；如果需要内部调试字段，留给更高层状态管理。
- 跨玩家 marker link。背包 marker 只在拥有者自己的背包内解析。
- 从 wiki 数据自动生成 `item_factories`。
- `evaluate_layout` 的评分策略。

## 推荐测试场景

实现时至少覆盖：

- `player_specs` 少于或多于 2 名玩家时报错。
- 两名玩家能生成同一个 `BattleState.players`。
- 单个玩家的 placements 能生成字典形式的 `PlayerState.items`。
- 重复 `item_id` 会按出现顺序生成 `stone1`、`stone2` 这类 key。
- star link 会把 target key 加入 source 的 `linked_items`。
- diamond link 和 triangle link 使用相同装配路径。
- 多个 marker 指向同一个目标时，`linked_items` 按 target key 去重。
- `is_active_item == True` 的物品进入 `BattleState.active_items`。
- inactive item 只存在于 `PlayerState.items`，不进入 `active_items`。
- active item 顺序按玩家输入顺序和 `PlayerState.items` 插入顺序稳定。
- 初始化器不会把 `BattleState`、坐标或 marker metadata 写入物品运行时字段。
- 缺失 item factory 会报错。
- 工厂返回非 `BattleItem` 会报错。
- 工厂返回错误 `item_id`、`item_key` 或 `player_id` 会报错。

## 后续演进点

短期下一步只需要实现公开入口：

```text
initialize_battle()
```

如果实现时需要拆分步骤，可以在模块内部写私有 helper，但不作为设计文档里的公开 API。

等这条桥稳定后，再考虑：

- 把战斗执行接口改成显式 `context` 传参。
- 给 `BattleItem.run_linked_items(context)` 增加递归保护。
- 如果具体物品需要区分 marker 类型，再引入 marker-specific link API 或 `BattleLink` 数据类。
- 把 `evaluate_layout(placements, opponent)` 改成调用 initializer 和 battle runner 的薄封装。
