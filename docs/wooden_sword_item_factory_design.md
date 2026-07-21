# Wooden Sword item_factory 开发设计草案

## 目标与边界

本草案用于审阅，不包含实现改动。目标是在现有 `BattleItem` / `initialize_battle` 框架下，为第一个真实战斗物品 `Wooden Sword` 设计 `item_factory`、触发逻辑和效果逻辑。

本轮不实现商店、合成、完整暴击、疲劳、buff/debuff 全量交互，也不自动导入 wiki 全量物品数据。耐力系统只补木剑所需的最小闭环：自然回复、当前耐力、消耗效果和效果链中断判定。

## 数据来源

查询日期：2026-07-08。

仅使用 `backpackbattles.wiki.gg` 的 MediaWiki/Cargo API：

- Wooden Sword 页面：<https://backpackbattles.wiki.gg/wiki/Wooden_Sword>
  - `pageid=10`
  - `lastrevid=10709`
  - 页面修订时间：`2025-09-17T01:47:12Z`
  - API：`api.php?action=query&titles=Wooden%20Sword&prop=revisions|info&rvprop=ids|timestamp|content&rvslots=main&inprop=url`
- Cargo `Items` 表：
  - API：`api.php?action=cargoquery&tables=Items&fields=name,class,rarity,cost,itemtype,icontype,tags,effect&where=name="Wooden Sword"`
- Game Mechanics 页面：<https://backpackbattles.wiki.gg/wiki/Game_Mechanics>
  - `lastrevid=11194`
  - 页面修订时间：`2026-02-18T09:51:34Z`
  - 用途：确认 Accuracy、Cooldown、Block、Heat、Cold、Luck、Blind 等通用战斗概念。

额外核对：wiki.gg 当前没有独立 `Stamina` 页面；`Game Mechanics` 页面把 Stamina 列为待解释主题，没有给出完整全局耐力回复规则。

项目审阅补充，记录日期：2026-07-08：

- 耐力每秒自然回复 1 点。
- 木剑开局不攻击。
- 木剑 trigger 不使用预排的 `next_ready_time`，而使用逐帧累积冷却进度。这样 Heat/Cold 在冷却期间变化时，可以按每帧即时状态调整冷却推进速度。

项目审阅补充，记录日期：2026-07-09：

- 玩家初始耐力为满格。
- 每名玩家的 `max_stamina` 和当前 `stamina` 都应在一开始的 `battle_run_v1` JSON 输入中显式提供。
- `stamina` 和 `max_stamina` 都是战斗中可变的玩家状态，物品效果可以动态修改。
- 物品冷却完成但耐力不足时，不等待耐力；冷却仍直接进入新一轮，随后由耐力消耗 effect 停止后续效果。
- 允许为 `BattleState` 增加 `rng`，集中控制命中、伤害等全局随机。
- 首版具体物品类直接放在 `item_factory_registry_v1.py`。
- 接受 `item_classes`、`item_types`、`icon_types` 这一组归一化 tuple 字段命名。
- 木剑首版不落地 combat log，测试先用状态断言验证效果。
- trigger 和 effect 独立成可复用实例，物品只负责组装并轮流调用实例接口。
- `CooldownTrigger` 不包含消耗耐力的逻辑，只负责逐帧推进并判定冷却是否完成。
- 耐力消耗独立为 `StaminaConsumptionEffect`，这样有冷却但不耗耐力的物品可以省略该 effect，耗耐力但不造成伤害的物品也可以复用该 effect。
- 木剑使用最常见的 `CooldownTrigger`、`StaminaConsumptionEffect` 和 `MeleeAttackEffect`。

## Wooden Sword 数据快照

建议仓库内 `item_id` 使用 snake case：`wooden_sword`。

| 字段 | 当前数据 |
| --- | --- |
| wiki 名称 | Wooden Sword |
| class | Neutral；Cargo 原始字段为空，按项目口径归一化为 Neutral。页面正文说明 Ranger 起始物品，其他职业也可在商店以 Common 稀有度获得 |
| rarity | Common |
| cost | 3 |
| item type | Weapon |
| icon type | melee |
| tags | 空 |
| effect | Cargo 字段为空，页面没有额外效果文本 |
| damage | 1-3 |
| stamina | 1 |
| accuracy | 90 |
| cooldown | 1.4 |
| sockets | 1 |
| grid | 两格竖形：`1 / 1` |

推荐加入 `data/item_catalog_v1.json` 的形状数据：

```json
"wooden_sword": {
  "item_id": "wooden_sword",
  "shape_cells": [[0, 0], [0, 1]],
  "star_cells": []
}
```

说明：

- `shape_cells` 沿用当前仓库对竖向两格物品的约定，例如 `health_potion`。
- 木剑页面的 `grid` 只有 `1`，没有 star/diamond/triangle marker，因此 `star_cells` 为空。
- `sockets=1` 当前没有对应的背包数据结构，本轮只作为物品元数据记录，暂不影响战斗。

## 公共属性枚举值

查询日期：2026-07-08。

来源：wiki.gg Cargo `Items` 表，API 查询字段为 `name,class,rarity,itemtype,icontype`，`limit=500`，本次返回 497 行。

Cargo 中 `class`、`itemtype`、`icontype` 可能出现逗号分隔组合值，例如 `Ranger,Berserker`、`Weapon,Pet`、`dark,magic`。下表是模型使用的归一化枚举值：组合字段按逗号拆分并去除空格；Cargo 原始 `class` 空字段统一归一化为 `Neutral`。

### class

| 取值 | 归一化后出现次数 | 建模含义 |
| --- | ---: | --- |
| Adventurer | 29 | Adventurer 相关 |
| Berserker | 39 | Berserker 相关 |
| Engineer | 43 | Engineer 相关 |
| Mage | 56 | Mage 相关 |
| Neutral | 219 | Neutral 条目；包含 Cargo 原始 `class` 为空的 184 行 |
| Pyromancer | 39 | Pyromancer 相关 |
| Ranger | 38 | Ranger 相关 |
| Reaper | 43 | Reaper 相关 |

### rarity

| 取值 | 出现次数 |
| --- | ---: |
| Common | 27 |
| Rare | 62 |
| Epic | 68 |
| Legendary | 91 |
| Godly | 96 |
| Unique | 148 |

`rarity` 的模型枚举不包含 `Varies`。如果 Cargo 原始数据出现 `Varies`，它不作为具体物品实例的合法稀有度；导入真实物品时应先解析为具体稀有度，或在无法解析时拒绝实例化该物品。

### itemtype

| 取值 | 拆分后出现次数 |
| --- | ---: |
| Accessory | 117 |
| Armor | 14 |
| Bag | 27 |
| Book | 5 |
| Chess Piece | 12 |
| Food | 20 |
| Gemstone | 14 |
| Gloves | 4 |
| Helmet | 9 |
| Pet | 79 |
| Playing Card | 8 |
| Potion | 18 |
| Shield | 10 |
| Shoes | 5 |
| Skill | 58 |
| Spell | 11 |
| Weapon | 111 |

### icontype

| 取值 | 拆分后出现次数 |
| --- | ---: |
| `<empty>` | 193 |
| dark | 41 |
| effect | 21 |
| fire | 35 |
| holy | 51 |
| ice | 20 |
| magic | 82 |
| melee | 67 |
| musical | 7 |
| nature | 84 |
| ranged | 41 |
| treasure | 34 |
| vampiric | 28 |

## BattleItem 公共属性待办

`class`、`rarity`、`cost`、`item type`、`icon type` 是所有物品都具备的公共属性，不应该只作为木剑的私有实现细节。实现木剑前，建议先修改 `BattleItem`，为这些字段提供统一位置。

建议 `BattleItem` 增加以下类属性，并在 `__init__` 中像 `item_id`、`item_key` 一样复制到实例上：

```python
display_name = None
item_classes = ()
rarity = None
cost = None
item_types = ()
icon_types = ()
```

字段约定：

- `display_name`：wiki 显示名，例如 `"Wooden Sword"`。
- `item_classes`：对应 wiki/Cargo 的 `class` 字段，归一化为 tuple。Cargo 空字段统一使用 `("Neutral",)`，多职业字段拆成多个枚举值。因为 `class` 是 Python 关键字，代码中不直接使用 `class`。
- `rarity`：单值枚举，例如 `"Common"`。
- `cost`：基础商店价格，使用整数。
- `item_types`：对应 wiki 的 `type` / Cargo 的 `itemtype`，归一化为 tuple，例如 `("Weapon",)`。
- `icon_types`：对应 Cargo 的 `icontype`，归一化为 tuple，例如 `("melee",)`。

这些字段首版主要服务于观察、调试和未来商店/物品池筛选；木剑战斗效果本身只直接依赖 `"Weapon" in item_types`、`"melee" in icon_types` 这类语义，后续接入 Spikes/Vampirism/Empower 时会用到。

## 当前框架映射

现有框架已经适合接入第一个真实物品：

- `battle_initializer_v1.initialize_battle()` 会根据 `item_id` 调用 `item_factories[item_id]`。
- 工厂返回值必须是 `BattleItem`。
- `BattleState.step()` 只直接遍历 `is_active_item == True` 的物品。
- `BattleItem.update_triggers(context)` 负责按顺序调用 `triggers` 中的实例接口。
- `BattleItem.run_own_effects(context)` 负责按顺序调用 `effects` 中的实例接口，并根据返回值决定是否继续后续 effect 和 linked item。
- 具体物品只负责组装自己的 trigger/effect 实例。

因此木剑应实现为主动战斗物品：

```python
class WoodenSword(BattleItem):
    item_id = "wooden_sword"
    display_name = "Wooden Sword"
    item_classes = ("Neutral",)
    rarity = "Common"
    cost = 3
    item_types = ("Weapon",)
    icon_types = ("melee",)
    is_active_item = True
    socket_count = 1

    def __init__(self, item_id=None, item_key=None, player_id=None):
        super().__init__(
            item_id=item_id,
            item_key=item_key,
            player_id=player_id,
            is_active_item=True,
            triggers=[
                CooldownTrigger(
                    cooldown_seconds=1.4,
                ),
            ],
            effects=[
                StaminaConsumptionEffect(
                    stamina_cost=1,
                ),
                MeleeAttackEffect(
                    min_damage=1,
                    max_damage=3,
                    accuracy=90,
                ),
            ],
        )
```

注意：`CooldownTrigger(...)`、`StaminaConsumptionEffect(...)` 和 `MeleeAttackEffect(...)` 必须在构造函数中为每个木剑实例新建，不能作为类属性共享。

注册方式：

```python
DEFAULT_ITEM_FACTORIES = {
    "wooden_sword": WoodenSword,
}
```

## Trigger 设计

木剑触发条件由 `CooldownTrigger` 实例负责：冷却进度累计完成。`CooldownTrigger` 不检查也不消耗耐力；冷却完成后返回 `True` 并扣除一轮冷却进度，后续是否真正执行攻击由 effect 链决定。

`CooldownTrigger` 的运行时状态：

```python
cooldown_seconds = 1.4
cooldown_progress = 0.0
```

木剑开局不攻击。初始化时 `cooldown_progress = 0.0`，从第一帧开始累积冷却；当累计进度达到 `cooldown_seconds` 后才允许触发。

冷却推进不使用 `next_ready_time = now + cooldown`。原因是 Heat/Cold 可能在木剑冷却期间变化；如果提前计算下一次触发时间，就无法准确反映中途速度变化。

建议把一帧内的有效冷却推进写成：

```text
cooldown_progress += frame_delta * trigger_speed_multiplier
```

其中 `trigger_speed_multiplier` 初版可以恒为 `1.0`，后续接入 Heat/Cold：

```text
trigger_speed_multiplier = 1 + heat * 0.02 - cold * 0.02
```

具体是否需要下限保护留给 Heat/Cold 实现时统一决定。

`CooldownTrigger.update(context)` 伪代码：

```python
def update(self, context):
    frame_delta = context.battle_state.frame_delta
    speed = get_trigger_speed_multiplier(context.owner)
    self.cooldown_progress += frame_delta * speed

    if self.cooldown_progress < self.cooldown_seconds:
        return False

    self.cooldown_progress -= self.cooldown_seconds
    return True
```

`BattleItem.update_triggers(context)` 只负责调用该 trigger 实例，并把返回值汇总到 `item.triggered`。

当前 `BattleState.step()` 每帧每个物品最多执行一次效果。因此如果 `frame_delta` 大于或接近 `cooldown_seconds`，一帧内即使累计出多次冷却，也只执行一次攻击。木剑测试应使用较小 `frame_delta`，例如 `0.1`，避免把调度误差误认为物品错误。

是否保留超额冷却进度：

- 冷却完成后统一执行 `cooldown_progress -= cooldown_seconds`，无论后续 effect 是否因耐力不足而停止。
- 如果采用 `cooldown_progress = 0.0`，会在离散帧下系统性损失冷却时间，不利于以后做高速触发物品。

本轮不实现 Heat/Cold 具体效果，但 `CooldownTrigger` 应为它们预留每帧读取 owner buff/debuff 的入口。

## Effect 设计

木剑效果由两个 effect 实例按顺序负责：

1. `StaminaConsumptionEffect(stamina_cost=1)`：尝试支付 1 点耐力。
2. `MeleeAttackEffect(min_damage=1, max_damage=3, accuracy=90)`：支付成功后执行一次 melee weapon attack。

建议所有 `BattleEffect.apply(context)` 返回布尔值：`True` 表示继续执行后续 effect，`False` 表示停止当前物品的后续 effect 和 linked item 调用。默认无特殊中断语义的 effect 返回 `True`。

`StaminaConsumptionEffect.apply(context)` 伪代码：

```python
def apply(self, context):
    if context.owner.stamina < self.stamina_cost:
        return False

    context.owner.stamina -= self.stamina_cost
    return True
```

这让耐力不足时的语义保持清晰：冷却已经完成并进入下一轮，但当前 effect 链在攻击前停止，所以木剑不造成伤害，也不等待耐力回复。

基础流程：

1. 检查是否命中：`accuracy=90`。
2. 命中时随机伤害：`randint(1, 3)`。
3. 先扣除对手 `block`，剩余伤害扣除对手 `health`。
4. 未命中时不造成伤害。

`MeleeAttackEffect.apply(context)` 建议伤害结算，并在执行完成后返回 `True`：

```python
blocked = min(context.opponent.block, raw_damage)
context.opponent.block -= blocked
context.opponent.health -= raw_damage - blocked
```

随机数来源：

- 在 `BattleState` 上增加 `rng` 字段，默认 `random.Random()`。
- 测试中显式注入固定 seed 的 `random.Random(seed)`。
- 不推荐在物品内部直接调用全局 `random`，否则回放和 RL 训练难以复现。

暂不实现但要预留的交互：

- Luck/Blind 调整 accuracy。
- Empower 调整 weapon damage。
- Critical hits。
- Spikes/Vampirism 的 melee hit 回调。
- Effect damage 与 weapon damage 的区分。
- Combat log 不在木剑首版落地；后续需要调试复杂触发链时再单独设计。

## 耐力处理建议

木剑页面给出 `stamina=1`。结合审阅补充，首版应实现最小耐力系统，而不是只记录字段。

新增到 `PlayerState` 的字段：

```python
stamina: float
max_stamina: float
stamina_regen_per_second: float = 1.0
```

输入约定：

- `battle_run_v1` JSON 中每个玩家都必须显式提供 `stamina` 和 `max_stamina`。
- 标准战斗开局时耐力满格，因此输入中的 `stamina` 应等于 `max_stamina`。
- 两个字段都写入 `PlayerState`，并允许战斗中被物品效果动态修改。
- `stamina_regen_per_second` 首版固定为 `1.0`，暂不要求 JSON 输入提供。

每帧自然回复：

```python
owner.stamina = min(
    owner.max_stamina,
    owner.stamina + frame_delta * owner.stamina_regen_per_second,
)
```

耐力不足时的触发规则：

- 如果冷却尚未完成，不检查耐力。
- 如果冷却完成但当前耐力不足，`CooldownTrigger` 仍然返回 `True` 并通过 `cooldown_progress -= cooldown_seconds` 直接进入新一轮冷却；随后 `StaminaConsumptionEffect` 返回 `False`，不扣耐力，并阻止后续 `MeleeAttackEffect` 执行。
- Heroic Potion 等“耐力耗尽时”触发系统暂不在木剑首版实现。

实现顺序建议：

1. 在每个 `BattleState.step(frame_delta)` 开始时为玩家回复耐力。
2. 再遍历 active item 累积冷却并判定触发。
3. 木剑触发后先运行 `StaminaConsumptionEffect` 消耗 1 点耐力；支付成功才继续运行 `MeleeAttackEffect`。

因为初始耐力满格，木剑第一次冷却完成时通常可以支付 1 点耐力并攻击。这仍然满足“木剑开局不攻击”。

## 首批可复用组件

### CooldownTrigger

用途：最常见的主动触发器，供木剑和后续多数有冷却的主动装备复用。

参数：

- `cooldown_seconds`

运行时状态：

- `cooldown_progress`

接口：

```python
update(context) -> bool
```

职责：

- 按 `frame_delta` 和未来的 Heat/Cold 速度倍率推进冷却。
- 冷却未满时返回 `False`。
- 冷却已满时扣除一轮冷却进度。
- 冷却已满时返回 `True`。
- 不读取、不判断、不消耗耐力。

### StaminaConsumptionEffect

用途：最常见的资源支付效果，供木剑和后续所有“需要耐力才能继续执行”的物品复用。

参数：

- `stamina_cost`

接口：

```python
apply(context) -> bool
```

职责：

- 检查 `context.owner.stamina` 是否足够。
- 足够时扣除 `stamina_cost` 并返回 `True`，允许后续 effect 继续执行。
- 不足时不扣耐力并返回 `False`，停止当前物品的后续 effect 和 linked item 调用。

### MeleeAttackEffect

用途：最常见的近战武器攻击效果，供木剑和后续普通近战武器复用。

参数：

- `min_damage`
- `max_damage`
- `accuracy`

接口：

```python
apply(context) -> bool
```

职责：

- 使用 `BattleState.rng` 判定命中。
- 命中后使用 `BattleState.rng` 在伤害区间内掷出伤害。
- 先扣除对手 `block`，再扣除对手 `health`。
- 未命中时不修改对手 `block` 或 `health`。
- 执行完成后返回 `True`。

## 建议实现位置

首版可以保持文件数量少：

- `battle_module_v1.py`
  - 修改 `BattleItem`，增加所有物品通用的元数据字段：`display_name`、`item_classes`、`rarity`、`cost`、`item_types`、`icon_types`。
  - 修改 `BattleItem.update_triggers(context)`，让它轮流调用 trigger 实例接口并汇总结果。
  - 修改 `BattleItem.run_own_effects(context)`，让它轮流调用 effect 实例接口；当某个 effect 返回 `False` 时停止后续 effect，并让 `run_effects()` 跳过 linked item 调用。
  - 在 `BattleItem.__init__()` 中把这些类属性复制到实例，支持未来测试或特殊工厂覆盖。
- `item_factory_registry_v1.py`
  - 增加 `CooldownTrigger`。
  - 增加 `StaminaConsumptionEffect`。
  - 增加 `MeleeAttackEffect`。
  - 增加 `WoodenSword` 类，并在构造函数中组装上述 trigger/effect 实例。
  - 注册 `DEFAULT_ITEM_FACTORIES["wooden_sword"]`。
- `data/item_catalog_v1.json`
  - 增加 `wooden_sword` 的两格竖形。
- `tests/test_item_factory_registry_v1.py`
  - 覆盖 registry、trigger、effect。
- `tests/test_basic_backpack_v1.py`
  - 覆盖木剑两格竖形摆放。

首版明确把具体物品类直接放在 `item_factory_registry_v1.py`。等真实物品数量增多后，再考虑迁移到 `items_v1.py` 或 `battle_items_v1.py`。

## 验收测试建议

最小测试集：

1. `DEFAULT_ITEM_FACTORIES` 包含 `wooden_sword`。
2. `BattleItem` 实例具备公共物品字段：`display_name`、`item_classes`、`rarity`、`cost`、`item_types`、`icon_types`。
3. 工厂返回 `BattleItem`，且 `item_id`、`item_key`、`player_id` 与 initializer 传入值一致。
4. 木剑公共字段填充为：`"Wooden Sword"`、`("Neutral",)`、`"Common"`、`3`、`("Weapon",)`、`("melee",)`。
5. 木剑 `is_active_item == True`，会进入 `BattleState.active_items`。
6. 木剑拥有一个 `CooldownTrigger` 实例、一个 `StaminaConsumptionEffect` 实例和一个 `MeleeAttackEffect` 实例，且 effect 顺序为先消耗耐力、后近战攻击。
7. 两把木剑各自拥有独立的 `CooldownTrigger`、`StaminaConsumptionEffect` 和 `MeleeAttackEffect`，运行时状态互不影响。
8. `time < 1.4` 时不触发。
9. 逐帧累积冷却到 `1.4` 后触发，并通过 `cooldown_progress -= 1.4` 保留超额进度。
10. 木剑开局第一帧不攻击。
11. JSON 中每个玩家显式提供 `stamina` 和 `max_stamina`，标准开局要求 `stamina == max_stamina`。
12. 玩家耐力每秒自然回复 1 点，且不超过当前 `max_stamina`。
13. `CooldownTrigger` 冷却已满时只返回触发结果，不读取或修改玩家耐力。
14. 冷却已满但耐力不足时，`StaminaConsumptionEffect` 返回 `False`，不扣耐力、不执行 `MeleeAttackEffect`，并且冷却已经进入新一轮。
15. 耐力足够时先扣 1 点耐力，再执行命中和伤害判定。
16. 命中时对手生命减少 1-3 中由 `BattleState.rng` 控制的随机值。
17. 对手有 block 时先扣 block，再扣 health。
18. 未命中时不扣 block/health。
19. `wooden_sword` 两格竖形可以被 `build_occupancy_matrix()` 正确写入矩阵。
20. 一场双方都带木剑的最小战斗可以运行到 `winner` 或 `max_frames_reached`，不再因缺少 factory 报错。

## 已确认开发口径

- `BattleItem` 公共字段使用 `item_classes`、`item_types`、`icon_types` 这一组归一化 tuple 字段。
- trigger 和 effect 使用可复用实例，物品只负责组装和调用。
- 木剑 trigger 使用 `CooldownTrigger`，且 `CooldownTrigger` 不包含耐力消耗逻辑。
- 木剑 effect 按顺序使用 `StaminaConsumptionEffect` 和 `MeleeAttackEffect`。
- `BattleEffect.apply(context)` 返回 `bool`，用于决定是否继续执行后续 effect 和 linked item。
- 木剑首版不落地 combat log。
- 首版测试以状态断言为主，验证耐力、冷却、命中、伤害、护盾和胜负结果。
