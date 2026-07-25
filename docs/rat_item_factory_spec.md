# Rat item factory SPEC

## 1. Requirements（需求）

实现 Rat（鼠鼠），使其可由默认工厂和战斗 JSON 创建。

Wiki 数据（查询于 2026-07-25）：

| 字段 | 值 |
| --- | --- |
| `item_id` | `rat` |
| 职业 / 稀有度 / 价格 | `Ranger` / `Common` / `4` |
| 类型 | `Pet`；`nature` |
| 效果 | 每 `3.3s` 造成 `5` 点伤害；`75%` 施加 `1` 层 Poison；`10%` 施加 `1` 层 Blind |
| 加速 | 每个星标连接的 Pet 或 Food 使触发加快 `15%` |
| 格子 | 横向两格；上下各两个、左右各一个星格 |
| 镶嵌位 | `0` |

来源：[中文 Wiki 鼠鼠](https://backpackbattles.wiki.gg/zh/wiki/%E9%BC%A0%E9%BC%A0)，
修订 `oldid=6105`，最后编辑于 2026-02-25。

本次同时完成两项通用调整：

- 用单一 `AttackEffect` 取代近战、远程及原计划的 effect 三个具体攻击类；调用 `apply()` 时传入攻击类型。鼠鼠传入 `"effect"`，基础命中率为 100%。
- `AttackEffect` 只有在 `context.item` 为武器时才计算 Empower、Luck、Blind。
- 新增条件表驱动的 `ItemAcceleratedCooldownTrigger`，用于鼠鼠及后续适合通用匹配语义的星位加速。
- 保留 `FoodCooldownTrigger` 和 Banana、Garlic 的现有用法，因为它额外具有排除相同 `item_id` 的自身语义。

范围外：修改 `FoodCooldownTrigger`、一碗零食、鼠大厨、商店及合成规则。

## 2. Design（设计）

### 2.1 `AttackEffect`

只保留一个通用攻击类，不再定义 `MeleeAttackEffect`、`RangedAttackEffect`
或 `EffectAttackEffect`：

```python
class AttackEffect(Effect):
    def __init__(
        self,
        min_damage: int,
        max_damage: int,
        accuracy: float,
    ): ...
    def apply(
        self,
        context: BattleContext,
        attack_type: str,
    ) -> bool: ...
    def stack_damage_modifier(self, amount: int) -> None: ...
    def prepare_damage_modifier(self, context: BattleContext) -> None: ...
```

`AttackEffect.__init__()` 接管现有两个攻击类重复的参数校验及字段初始化：

```text
若 min_damage < 0：抛出 ValueError
若 max_damage < min_damage：抛出 ValueError
保存 min_damage、max_damage、accuracy
damage_modifier = 0
damage_modifier_prepared = False
```

`AttackEffect.apply()`：

```text
若 attack_type 不在 SUPPORTED_ATTACK_TYPES：抛出 ValueError
若尚未准备伤害修正:
    prepare_damage_modifier(context)
    damage_modifier_prepared = True
damage_modifier = 已有外部伤害修正
accuracy = self.accuracy
若 "Weapon" in context.item.item_types:
    damage_modifier += owner 的 Empower 层数
    accuracy += (owner 的 Luck 层数 - Blind 层数) * 5
生成 attack_types=(attack_type,) 的 AttackEvent
交给 BattleState.resolve_attack() 并返回命中结果
```

- `stack_damage_modifier()` 与空实现的 `prepare_damage_modifier()` 从现有两个具体类上移至基类。
- 近战、远程、effect 只是调用参数，不建立三种空壳子类。
- 非武器仍使用基础伤害、基础命中率和已有的外部伤害修正，只忽略 Empower、Luck、Blind。
- `FoodLinkedMeleeAttackEffect` 改为直接继承 `AttackEffect`，仅保留 Pan 所需的 Food 伤害准备逻辑；Pan 调用时显式传入 `"melee"`。
- `LinkedWeaponDamageEffect` 改为判断 `isinstance(effect, AttackEffect)`；它仍只修改 `Weapon`，所以不会修改鼠鼠。

现有攻击物品迁移：

| 物品 | Effect 构造 | `apply()` 调用 |
| --- | --- | --- |
| Broom | `AttackEffect(2, 4, 95)` | `apply(context, "melee")` |
| Wooden Sword | `AttackEffect(1, 3, 90)` | `apply(context, "melee")` |
| Shortbow | `AttackEffect(2, 3, 85)` | `apply(context, "ranged")` |
| Stone | `AttackEffect(2, 4, 70)` | `apply(context, "ranged")` |
| Pan | `FoodLinkedMeleeAttackEffect(5, 6, 85, 1)` | `apply(context, "melee")` |
| Rat | `AttackEffect(5, 5, 100)` | `apply(context, "effect")` |

### 2.2 `ItemAcceleratedCooldownTrigger`

新增通用触发器，但不替换 `FoodCooldownTrigger`：

```python
class ItemAcceleratedCooldownTrigger(CooldownTrigger):
    def __init__(
        self,
        cooldown_seconds: float,
        acceleration_conditions: list[dict[str, object]],
    ): ...
    def _matches_condition(
        self,
        linked_item: BattleItem,
        condition: dict[str, object],
    ) -> bool: ...
    def prepare_speed_modifiers(self, context: BattleContext) -> None: ...
```

条件条目格式：

```python
{
    "class": str,       # 可选；成员匹配 item_classes
    "rarity": str,      # 可选；等值匹配 rarity
    "item_type": str,   # 可选；成员匹配 item_types
    "icon_type": str,   # 可选；成员匹配 icon_types
    "accelerate": float # 必填；命中后叠加的加速比例
}
```

匹配与累加流程：

```text
item_acceleration = 0
遍历 context.item.linked_items 中的每个实例:
    遍历 acceleration_conditions 中的每个条目:
        若该条目给出的所有筛选字段都满足:
            item_acceleration += condition["accelerate"]
保存 self.item_acceleration
stack_speed_modifier(item_acceleration)
```

- 单条条件内是 AND；不同条件之间分别判断并相加。
- 条目没有任何筛选字段时自然匹配所有已链接物品。
- 同一实例可命中多条条件，每次命中均叠加。
- 仅遍历已链接实例，不按 `item_id` 去重或排除。
- `CooldownTrigger.speed_modifiers_prepared` 继续保证只扫描、叠加一次，并继续与 Heat、Cold 和外部速度修正相加。
- 构造时复制列表和字典；拒绝未知字段、空字符串筛选值、缺失 `accelerate`，以及 bool、非数值或负数的加速值。

鼠鼠配置：

```python
[
    {"item_type": "Pet", "accelerate": 0.15},
    {"item_type": "Food", "accelerate": 0.15},
]
```

同时为 Pet 和 Food 的一个实例会使鼠鼠加速 30%，符合“每满足一个条件就叠加”的统一语义。

`FoodCooldownTrigger` 原样保留：它继续统计星位 Food、排除
`linked_item.item_id == context.item.item_id` 的项目并固定每件加速 10%。
Banana、Garlic 继续使用它，不迁移到条件表触发器。

### 2.3 `Rat`

```python
class Rat(BattleItem):
    item_id = "rat"
    display_name = "Rat"
    item_classes = ("Ranger",)
    rarity = "Common"
    cost = 4
    item_types = ("Pet",)
    icon_types = ("nature",)
    is_active_item = True
    socket_count = 0
```

```python
triggers=[
    ItemAcceleratedCooldownTrigger(
        3.3,
        [
            {"item_type": "Pet", "accelerate": 0.15},
            {"item_type": "Food", "accelerate": 0.15},
        ],
    )
]
effects=[
    AttackEffect(5, 5, accuracy=100.0),
    InflictDebuffEffect("Poison", 1),
    InflictDebuffEffect("Blind", 1),
]
```

`run_effect()`：

```text
若 trigger 为假：返回
执行 AttackEffect.apply(context, "effect")；若未命中则返回
独立掷随机数；小于 0.75 时施加 Poison
再次独立掷随机数；小于 0.10 时施加 Blind
```

鼠鼠不是武器，因此 Empower、Luck、Blind 不改变其 5 点伤害或 100% 基础命中率；既有攻击事件和反应流程仍照常处理。

目录与注册：

```json
"rat": {
  "item_id": "rat",
  "shape_cells": [[0, 0], [1, 0]],
  "star_cells": [[0, 1], [1, 1], [-1, 0], [2, 0], [0, -1], [1, -1]]
}
```

并注册 `"rat": Rat`。

## 3. Realize（实现任务）

1. 用单一 `AttackEffect` 替换 `MeleeAttackEffect`、`RangedAttackEffect`；迁移五个既有攻击物品和相关直接调用，并简化 `LinkedWeaponDamageEffect` 的类型判断。
2. 新增 `ItemAcceleratedCooldownTrigger`，保留 `FoodCooldownTrigger`、Banana、Garlic 不变。
3. 实现 `Rat.__init__()`、`run_effect()`、目录及工厂注册。
4. 添加下列测试并运行全套测试。

## 4. Acceptance Criteria / Tests（验收）

1. `test_item_accelerated_cooldown_rejects_invalid_conditions`
   - 覆盖未知字段、非法筛选值、缺失或非法 `accelerate`。
2. `test_item_accelerated_cooldown_requires_all_fields_in_one_condition`
   - 同一条目的多个筛选字段必须全部匹配。
3. `test_item_accelerated_cooldown_adds_every_matching_condition`
   - 覆盖无筛选条目匹配所有物品、同一物品命中多条、多件物品累加、不匹配及未链接物品不计，并检查缓存总值及其他速度修正。
4. `test_food_cooldown_ignores_linked_same_food_and_non_food`
   - 保留既有用例，确认 Banana、Garlic 仍由 `FoodCooldownTrigger` 排除相同 `item_id`。
5. `test_attack_effect_rejects_unsupported_attack_type`
   - `apply()` 拒绝不在 `SUPPORTED_ATTACK_TYPES` 中的参数。
6. `test_attack_effect_resolves_each_attack_type`
   - 同一 `AttackEffect` 分别传入 melee、ranged、effect，覆盖参数校验、伤害范围、事件类型和命中返回值。
7. `test_non_weapon_attack_effect_ignores_empower_luck_and_blind`
   - 分别覆盖 Melee、Ranged、Effect，确认非武器只保留基础值和外部伤害修正。
8. `test_weapon_attack_effect_applies_empower_luck_and_blind`
   - 分别覆盖 Melee、Ranged、Effect，确认武器仍使用既有公式。
9. `test_linked_weapon_damage_effect_supports_attack_effect`
   - 所有武器上的 `AttackEffect` 均可获磨刀石加成，鼠鼠不可；Pan 的 Food 特化子类仍可识别。
10. `test_existing_attack_items_dispatch_expected_attack_type`
    - Broom、Wooden Sword、Pan 传入 melee；Shortbow、Stone 传入 ranged。
11. `test_rat_is_registered_with_metadata_and_components`
   - 校验元数据、网格、六星位、统一触发器条件表、5 点 `AttackEffect`、100% 命中率及状态 Effect 顺序。
12. `test_rat_activation_attacks_and_applies_successful_debuffs`
    - 验证伤害结算、非武器 Buff 规则，以及两次成功的独立状态判定。
13. `test_rat_debuff_chances_fail_at_boundaries`
    - 随机值等于 0.75/0.10 时对应判定失败。
14. `test_initializer_links_all_six_rat_stars`
15. `test_initializer_builds_rat_as_active_item`
16. 仓库全部既有测试通过。
