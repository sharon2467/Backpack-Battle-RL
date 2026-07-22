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
- 物品冷却完成但耐力不足时，不等待耐力；冷却仍直接进入新一轮。耐力消耗 effect 返回 `False`，近战 effect 读取该结果后不产生攻击副作用。
- 允许为 `BattleState` 增加 `rng`，集中控制命中、伤害等全局随机。
- 首版具体物品类直接放在 `item_factory_registry_v1.py`。
- 接受 `item_classes`、`item_types`、`icon_types` 这一组归一化 tuple 字段命名。
- 木剑首版不落地 combat log，测试先用状态断言验证效果。
- trigger 和 effect 独立成可复用实例；具体物品负责组装组件，并在 `run_own_effect()` 中组合结果和选择调用顺序。
- `CooldownTrigger` 不包含消耗耐力的逻辑，只负责逐帧推进并判定冷却是否完成。
- 耐力消耗独立为 `StaminaConsumptionEffect`，这样有冷却但不耗耐力的物品可以省略该 effect，耗耐力但不造成伤害的物品也可以复用该 effect。
- 木剑使用最常见的 `CooldownTrigger`、`StaminaConsumptionEffect` 和 `MeleeAttackEffect`。

项目审阅补充，记录日期：2026-07-22：

- 删除独立的 trigger-to-effect 逻辑判断层。
- `BattleItem.update_triggers(context)` 保存并返回基础 trigger 的 bool 结果列表。
- `BattleState.step()` 不再使用 `is_triggered()` 粗筛；所有物品每次都进入 `run_effects()`，因此全 False trigger 也可以被物品按 NOT 条件解释。
- 所有物品级逻辑放在具体物品的 `run_own_effect(trigger_results, context)` 中，包括 trigger 组合、effect 是否调用、effect 失败后的分支，以及是否继续 linked items。
- 基本 effect 只接收 `context` 并执行自身效果，不接收 trigger/effect 结果列表。

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
- `BattleItem.update_triggers(context)` 负责按顺序调用 `triggers` 中的实例接口，保存并返回基础 bool 结果列表。
- `BattleItem.run_effects(context)` 负责固定的“更新 trigger -> 调用具体物品逻辑 -> 可选 linked items”流程。
- 木剑的 `run_own_effect(trigger_results, context)` 负责判断冷却、调用耐力/攻击 effect，并返回是否继续 linked items。

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

    def run_own_effect(self, trigger_results, context):
        cooldown_ready = trigger_results[0]
        if not cooldown_ready:
            return False

        stamina_paid = self.effects[0].apply(context)
        if not stamina_paid:
            return False

        attack_result = self.effects[1].apply(context)
        return attack_result
```

注意：`CooldownTrigger(...)`、`StaminaConsumptionEffect(...)` 和 `MeleeAttackEffect(...)` 必须在构造函数中为每个木剑实例新建，不能作为类属性共享。

注册方式：

```python
DEFAULT_ITEM_FACTORIES = {
    "wooden_sword": WoodenSword,
}
```

## Trigger 设计

木剑触发条件由 `CooldownTrigger` 实例负责：冷却进度累计完成。`CooldownTrigger` 不检查也不消耗耐力；冷却完成后返回 `True` 并扣除一轮冷却进度，后续是否真正执行攻击由木剑的 `run_own_effect()` 决定。

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

`Heat` 与 `Cold` 先按层数互相抵消，再按每层 2% 计算当前帧的触发速度倍率。净 Heat 使用加速公式，净 Cold 使用减速公式：

```text
net_heat_stacks = heat - cold
if net_heat_stacks >= 0:
    trigger_speed_multiplier = 1 + net_heat_stacks * 0.02
else:
    trigger_speed_multiplier = 1 / (1 + abs(net_heat_stacks) * 0.02)
```

`CooldownTrigger` 每帧重新读取当前层数，因此冷却期间发生的 Heat/Cold 变化会立即影响后续推进。

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

`BattleItem.update_triggers(context)` 只负责调用该 trigger 实例，将返回值保存并返回为 `item.trigger_results`。无论结果真假，`run_effects()` 随后都会调用木剑的 `run_own_effect()`。

当前 `BattleState.step()` 每帧每个物品最多执行一次效果。因此如果 `frame_delta` 大于或接近 `cooldown_seconds`，一帧内即使累计出多次冷却，也只执行一次攻击。木剑测试应使用较小 `frame_delta`，例如 `0.1`，避免把调度误差误认为物品错误。

是否保留超额冷却进度：

- 冷却完成后统一执行 `cooldown_progress -= cooldown_seconds`，不受后续耐力 effect 返回结果影响。
- 如果采用 `cooldown_progress = 0.0`，会在离散帧下系统性损失冷却时间，不利于以后做高速触发物品。

`CooldownTrigger` 每帧读取 `context.owner.buffs.Heat` 和 `context.owner.debuffs.Cold`，并按抵消后的净层数推进冷却。

## Effect 设计

木剑效果由两个 effect 实例按顺序负责：

1. `StaminaConsumptionEffect(stamina_cost=1)`：尝试支付 1 点耐力。
2. `MeleeAttackEffect(min_damage=1, max_damage=3, accuracy=90)`：支付成功后执行一次 melee weapon attack。

所有 `BattleEffect.apply(context)` 返回布尔值。基本 effect 不读取 trigger，也不决定后续 effect 或 linked item；具体物品的 `run_own_effect()` 负责是否调用 effect 及如何解释其返回值。

`StaminaConsumptionEffect.apply(context)` 伪代码：

```python
def apply(self, context):
    if context.owner.stamina < self.stamina_cost:
        return False

    context.owner.stamina -= self.stamina_cost
    return True
```

这让耐力不足时的语义保持清晰：冷却已经完成并进入下一轮，耐力 effect 返回 `False`；木剑的 `run_own_effect()` 立即返回 `False`，因此不调用 melee effect，也不继续 linked items。

基础流程：

1. 创建包含攻击双方、来源物品、`accuracy=90` 和伤害区间的 `AttackEvent`。
2. 交给 `BattleState.resolve_attack(event)` 进行命中判定。
3. 命中时随机伤害：`randint(1, 3)`，再向防守方派发 `on_attacked` 响应。
4. 所有响应完成后，由 `BattleState` 先把剩余伤害结算到 `block`，再结算到 `health`。
5. 未命中时不抽取伤害、不派发 `on_attacked`，也不修改 `block` 或 `health`。

`MeleeAttackEffect.apply(context)` 只负责一次近战攻击：

```python
def apply(self, context):
    event = AttackEvent(
        attacker=context.owner,
        defender=context.opponent,
        source_item=context.item,
        attack_types=("melee",),
        min_damage=self.min_damage,
        max_damage=self.max_damage,
        accuracy=self.accuracy,
    )
    resolved_event = context.battle_state.resolve_attack(event)
    return resolved_event.hit is True
```

`MeleeAttackEffect` 不直接修改对手状态。返回 `True` 表示攻击命中，未命中时返回 `False`；即使命中伤害被响应物品完全阻止，仍返回 `True`。是否调用该 effect 已由木剑的 `run_own_effect()` 在耐力支付成功后决定。攻击事务、响应缓存和统一伤害提交的完整设计见 `docs/attack_event_resolution_spec.md`。

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
- 如果冷却完成但当前耐力不足，`CooldownTrigger` 仍然返回 `True` 并通过 `cooldown_progress -= cooldown_seconds` 直接进入新一轮冷却；随后 `StaminaConsumptionEffect` 返回 `False` 且不扣耐力，木剑的 `run_own_effect()` 不调用 `MeleeAttackEffect`。
- Heroic Potion 等“耐力耗尽时”触发系统暂不在木剑首版实现。

实现顺序建议：

1. 在每个 `BattleState.step()` 开始时按 `BattleState.frame_delta` 为玩家回复耐力。
2. 再遍历 active item 累积冷却并判定触发。
3. 木剑的 `run_own_effect()` 判断冷却完成后先运行 `StaminaConsumptionEffect`；只有支付结果为 `True` 时才调用 `MeleeAttackEffect`。

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

- 耐力足够时扣除 `stamina_cost` 并返回 `True`。
- 耐力不足时不扣耐力并返回 `False`。
- 返回值由具体物品的 `run_own_effect()` 解释。

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

- 创建独立的 melee `AttackEvent`，并调用 `BattleState.resolve_attack()`。
- 命中、伤害抽取、攻击响应和 Block/Health 提交统一由 `BattleState` 处理。
- 不直接修改对手 `block` 或 `health`。
- 命中返回 `True`，未命中返回 `False`。

## 建议实现位置

首版可以保持文件数量少：

- `battle_module_v1.py`
  - 修改 `BattleItem`，增加所有物品通用的元数据字段：`display_name`、`item_classes`、`rarity`、`cost`、`item_types`、`icon_types`。
  - 修改 `BattleItem.update_triggers(context)`，让它轮流调用 trigger 实例接口，保存并返回 bool 结果列表。
  - 用具体物品实现的 `BattleItem.run_own_effect(trigger_results, context)` 负责 trigger 组合、effect 分支和 linked item 返回值。
  - 修改 `BattleItem.run_effects(context)`，固定执行 update triggers、run own effect、可选 linked items。
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
14. 冷却已满但耐力不足时，`StaminaConsumptionEffect` 返回 `False` 且不扣耐力；木剑的 `run_own_effect()` 不调用 `MeleeAttackEffect`，并且冷却已经进入新一轮。
15. 耐力足够时先扣 1 点耐力，再执行命中和伤害判定。
16. 命中时创建的 `AttackEvent` 由 `BattleState.rng` 控制伤害抽取，并在提交前允许 `on_attacked` 响应修改待结算伤害。
17. 所有攻击响应完成后，剩余伤害先扣 block，再扣 health。
18. 未命中时不扣 block/health。
19. `wooden_sword` 两格竖形可以被 `build_occupancy_matrix()` 正确写入矩阵。
20. 一场双方都带木剑的最小战斗可以运行到 `winner` 或 `max_frames_reached`，不再因缺少 factory 报错。

## 已确认开发口径

- `BattleItem` 公共字段使用 `item_classes`、`item_types`、`icon_types` 这一组归一化 tuple 字段。
- trigger 和 effect 使用可复用实例，具体物品负责组装，并在 `run_own_effect()` 中实现组合与调用逻辑。
- 木剑 trigger 使用 `CooldownTrigger`，且 `CooldownTrigger` 不包含耐力消耗逻辑。
- 木剑 effect 按顺序使用 `StaminaConsumptionEffect` 和 `MeleeAttackEffect`。
- `BattleEffect.apply(context)` 返回 `bool`，具体物品的 `run_own_effect()` 解释该结果。
- `BattleState.step()` 不使用 `is_triggered()`；`run_effects()` 无条件更新 trigger 并调用 `run_own_effect()`。
- 木剑的 `run_own_effect()` 负责耐力失败后不调用近战 effect，并返回是否继续 linked items。
- 木剑首版不落地 combat log。
- 首版测试以状态断言为主，验证耐力、冷却、命中、伤害、护盾和胜负结果。
