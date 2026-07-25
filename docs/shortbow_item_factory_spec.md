# Shortbow item factory SPEC

## 1. Requirements（需求）

实现 Shortbow（短弓）及独立的 `RangedAttackEffect`，使短弓可由默认工厂和战斗 JSON 创建并参与战斗。

Wiki 数据（查询于 2026-07-25）：

| 字段 | 值 |
| --- | --- |
| `item_id` | `shortbow` |
| 职业 / 稀有度 / 价格 | `Ranger` / `Common` / `4` |
| 类型 | `Weapon`、`ranged` |
| 伤害 / 耐力 / 命中 / 冷却 | `2-3` / `0.7` / `85%` / `1.7s` |
| 镶嵌位 | `1` |
| 格子 | 纵向 `2` 格 |
| 特殊效果 | 无 |

来源：[中文 Wiki 短弓](https://backpackbattles.wiki.gg/zh/wiki/%E7%9F%AD%E5%BC%93)，页面显示修订 `oldid=7856`，最后编辑于 2026-05-24。

验收行为：

- 每 `1.7s` 尝试攻击；冷却完成后即重置。
- 耐力不足时不扣耐力、不检定命中、不造成伤害。
- 耐力足够时先扣 `0.7`，再以 `85%` 命中率造成 `2-3` 点 ranged 伤害。
- `Empower`、`Luck`、`Blind` 的计算与现有近战攻击一致。
- ranged 伤害不触发仅限 melee 的尖刺、吸血或木盾响应。

范围外：合成、商店、镶嵌效果、暴击、combat log，以及攻击框架重构。

## 2. Design（设计）

### 2.1 `RangedAttackEffect`

在 `item_factory_registry_v1.py` 新增独立类；不修改、不继承、不重命名 `MeleeAttackEffect`：

```python
class RangedAttackEffect(Effect):
    def __init__(
        self,
        min_damage: int,
        max_damage: int,
        accuracy: float,
    ): ...

    def stack_damage_modifier(self, amount: int) -> None: ...
    def prepare_damage_modifier(self, context: BattleContext) -> None: ...
    def apply(self, context: BattleContext) -> bool: ...
```

构造校验及 damage modifier 状态与 `MeleeAttackEffect` 一致。`apply()` 的伪代码：

```text
首次调用时准备静态 damage modifier
damage = damage_modifier + owner.Empower
创建 AttackEvent：
    attack_types = ("ranged",)
    damage = [min_damage + damage, max_damage + damage]
    accuracy = accuracy + (Luck - Blind) * 5
调用 battle_state.resolve_attack(event)
返回 event.hit is True
```

这是本轮唯一新增的底层组件；不抽取公共攻击基类。

### 2.2 `Shortbow`

```python
class Shortbow(BattleItem):
    item_id = "shortbow"
    display_name = "Shortbow"
    item_classes = ("Ranger",)
    rarity = "Common"
    cost = 4
    item_types = ("Weapon",)
    icon_types = ("ranged",)
    is_active_item = True
    socket_count = 1
```

`Shortbow.__init__()` 为每个实例创建：

```python
triggers=[CooldownTrigger(1.7)]
effects=[
    StaminaConsumptionEffect(0.7),
    RangedAttackEffect(2, 3, 85),
]
```

`Shortbow.run_effect(trigger_results, context) -> None`：

```text
若冷却 trigger 为 False：返回
若耐力 effect 为 False：返回
执行 ranged attack effect
```

### 2.3 注册与目录

- 在 `DEFAULT_ITEM_FACTORIES` 注册 `"shortbow": Shortbow`。
- 在 `data/item_catalog_v1.json` 增加：

```json
"shortbow": {
  "item_id": "shortbow",
  "shape_cells": [[0, 1], [0, 0]],
  "star_cells": []
}
```

流程：

```text
每帧 → CooldownTrigger → 扣除耐力 → RangedAttackEffect
     → AttackEvent(attack_types=("ranged",)) → 统一攻击结算
```

## 3. Realize（实现任务）

1. 在 `item_factory_registry_v1.py` 实现 `RangedAttackEffect` 的上述四个函数。
2. 实现 `Shortbow.__init__()` 与 `Shortbow.run_effect()`。
3. 注册工厂并补充已核对的纵向两格目录数据。
4. 在 `tests/test_item_factory_registry_v1.py` 添加下列测试并运行全套测试。

## 4. Acceptance Criteria / Tests（验收）

1. `test_ranged_attack_effect_rejects_invalid_damage_ranges`：负最小伤害或最大值小于最小值时报错。
2. `test_ranged_attack_effect_resolves_ranged_hit`：验证伤害范围、命中率修正、Empower 及 `attack_types=("ranged",)`。
3. `test_ranged_attack_effect_miss_returns_false_without_damage_roll`：未命中返回 `False` 且不读取伤害 RNG。
4. `test_ranged_attack_does_not_apply_spikes_or_vampirism`：ranged 命中不执行 melee 专属状态。
5. `test_ranged_attack_does_not_trigger_wooden_buckler`：木盾不响应 ranged 攻击。
6. `test_shortbow_is_registered_with_metadata_and_components`：验证全部元数据及三个组件参数。
7. `test_shortbows_own_independent_component_instances`：两把短弓不共享 trigger/effect 状态。
8. `test_shortbow_attacks_after_cooldown`：`1.7s` 后扣 `0.7` 耐力并造成 `2-3` 伤害。
9. `test_shortbow_pays_stamina_on_miss`：耐力足够但未命中时仍扣耐力。
10. `test_shortbow_restarts_cooldown_without_stamina`：耐力不足时冷却重置但不攻击。
11. `test_initializer_builds_shortbow_as_active_item`：目录、默认工厂、JSON 初始化及 active item 接入成功。
12. 仓库全部既有测试通过；`MeleeAttackEffect` 的行为保持不变。
