# Stone item factory SPEC

## 1. Requirements（需求）

实现 Stone（石头），使其可由默认工厂和战斗 JSON 创建。

Wiki 数据（查询于 2026-07-25）：

| 字段 | 值 |
| --- | --- |
| `item_id` | `stone` |
| 职业 / 稀有度 / 价格 | `Neutral` / `Common` / `1` |
| 类型 | `Weapon`；`ranged`、`nature` |
| 攻击 | `2–4` 伤害、`70%` 命中、`2.5s` 冷却、`0` 耐力 |
| 效果 | 每场只能投掷一次；命中后摧毁对手 `4` 点格挡 |
| 格子 / 镶嵌位 | 单格 / `0` |

来源：[Stone Wiki](https://backpackbattles.wiki.gg/wiki/Stone)，修订
`oldid=10762`，最后编辑于 2025-09-17。

验收行为：

- 冷却受现有 Heat、Cold 和外部速度 modifier 影响。
- 到达首次冷却后投掷一次；无论命中或未命中，此后都不再投掷。
- 只有命中时才在攻击结算后额外移除最多 `4` 点对手格挡。
- `AfterTimeTrigger` 提供永久锁定 `has_triggered=False` 的入口，供后续一袋
  石头将石头改为反复投掷。

范围外：一袋石头物品本身、Stoned 技能、合成及商店规则。

## 2. Design（设计）

### 2.1 `AfterTimeTrigger.lock_has_triggered_false`

```python
class AfterTimeTrigger(CooldownTrigger):
    def lock_has_triggered_false(self) -> None: ...
```

新增实例字段 `has_triggered_locked_false=False`。

伪代码：

```text
lock_has_triggered_false：
    has_triggered = False
    has_triggered_locked_false = True

update 冷却完成后：
    若未锁定：has_triggered = True
    返回 True
```

锁定不可撤销；即使在首次触发后调用，也会重新开放该 trigger。之后继续复用
`CooldownTrigger` 的扣减逻辑，每个冷却周期触发一次。

### 2.2 `RemoveOpponentBlockEffect`

```python
class RemoveOpponentBlockEffect(Effect):
    def __init__(self, amount: int): ...
    def apply(self, context: BattleContext) -> bool: ...
```

伪代码：

```text
构造时校验 amount 为非负 int
actual = min(context.opponent.block, amount)
context.opponent.block -= actual
返回 actual > 0
```

### 2.3 `Stone`

```python
class Stone(BattleItem):
    item_id = "stone"
    display_name = "Stone"
    item_classes = ("Neutral",)
    rarity = "Common"
    cost = 1
    item_types = ("Weapon",)
    icon_types = ("ranged", "nature")
    is_active_item = True
    socket_count = 0
```

```python
triggers=[AfterTimeTrigger(2.5)]
effects=[
    RangedAttackEffect(2, 4, 70),
    RemoveOpponentBlockEffect(4),
]
```

`run_effect()`：

```text
若 trigger 为假：返回
若远程攻击未命中：返回
应用 RemoveOpponentBlockEffect
```

在 `DEFAULT_ITEM_FACTORIES` 注册 `"stone": Stone`。现有目录中的单格
`stone` 数据保持不变。

## 3. Realize（实现任务）

1. 扩展 `AfterTimeTrigger.__init__()`、`update()`并实现
   `lock_has_triggered_false()`。
2. 实现 `RemoveOpponentBlockEffect.__init__()`、`apply()`。
3. 实现 `Stone.__init__()`、`run_effect()`及工厂注册。
4. 添加下列测试并运行全套测试。

## 4. Acceptance Criteria / Tests（验收）

1. `test_after_time_trigger_can_lock_has_triggered_false`
2. `test_after_time_trigger_lock_reopens_trigger_after_first_activation`
3. `test_remove_opponent_block_effect_validates_and_clamps_amount`
4. `test_stone_is_registered_with_metadata_and_components`
5. `test_stone_hits_once_and_removes_block_after_attack`
6. `test_stone_miss_consumes_its_only_throw_without_removing_block`
7. `test_whetstone_can_buff_stone`
8. `test_initializer_builds_stone_as_active_item`
9. 仓库全部既有测试通过。
