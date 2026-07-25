# Whetstone item factory SPEC

## 1. Requirements（需求）

实现 Whetstone（磨刀石），使其可由默认工厂和战斗 JSON 创建。

Wiki 数据（查询于 2026-07-25）：

| 字段 | 值 |
| --- | --- |
| `item_id` | `whetstone` |
| 职业 / 稀有度 / 价格 | `Neutral` / `Common` / `4` |
| 类型 | `Accessory` |
| 效果 | 战斗开始时，星标武器的最小、最大伤害各 `+1` |
| 格子 | 单格；左右各一个星格 |
| 镶嵌位 | `0` |

来源：[Whetstone Wiki](https://backpackbattles.wiki.gg/wiki/Whetstone)，修订
`oldid=11212`，最后编辑于 2026-04-26。

验收行为：

- 只强化星标连接且 `item_types` 含 `"Weapon"` 的物品。
- 近战和远程攻击均可获得 `+1` 伤害；非武器及未连接武器不受影响。
- 战斗开始效果只执行一次，不直接改写武器基础伤害字段。

范围外：合成、商店、强化磨刀石及其他局外规则。

## 2. Design（设计）

### 2.1 `LinkedWeaponDamageEffect`

```python
class LinkedWeaponDamageEffect(Effect):
    def __init__(self, amount: int): ...
    def apply(self, context: BattleContext) -> bool: ...
```

伪代码：

```text
构造时校验 amount 为非负 int
apply：
    遍历 context.item.linked_items
    忽略非 Weapon 物品
    遍历武器 effects
    若 effect 是 MeleeAttackEffect 或 RangedAttackEffect：
        effect.stack_damage_modifier(amount)
        记录已修改
    返回是否修改过任一攻击 effect
```

直接复用现有伤害 modifier；不新增接口或修改 `BattleItem`。

### 2.2 `Whetstone`

```python
class Whetstone(BattleItem):
    item_id = "whetstone"
    display_name = "Whetstone"
    item_classes = ("Neutral",)
    rarity = "Common"
    cost = 4
    item_types = ("Accessory",)
    icon_types = ()
    is_active_item = True
    socket_count = 0
```

```python
triggers=[StartOfBattleTrigger()]
effects=[LinkedWeaponDamageEffect(1)]
```

`run_effect()` 仅在 trigger 为真时应用 effect。

目录与注册：

```json
"whetstone": {
  "item_id": "whetstone",
  "shape_cells": [[0, 0]],
  "star_cells": [[-1, 0], [1, 0]]
}
```

并注册 `"whetstone": Whetstone`。

## 3. Realize（实现任务）

1. 实现 `LinkedWeaponDamageEffect.__init__()`、`apply()`。
2. 实现 `Whetstone.__init__()`、`run_effect()`。
3. 添加工厂注册和目录布局。
4. 添加下列测试并运行全套测试。

## 4. Acceptance Criteria / Tests（验收）

1. `test_linked_weapon_damage_effect_rejects_invalid_amounts`
2. `test_linked_weapon_damage_effect_buffs_linked_melee_and_ranged_weapons`
3. `test_linked_weapon_damage_effect_ignores_non_weapons_and_unlinked_weapons`
4. `test_whetstone_is_registered_with_metadata_and_components`
5. `test_whetstone_triggers_once`
6. `test_initializer_links_whetstone_left_and_right_stars`
7. `test_initializer_builds_whetstone_as_active_item`
8. 仓库全部既有测试通过。
