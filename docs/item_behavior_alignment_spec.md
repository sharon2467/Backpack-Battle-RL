# 已实现物品行为校正

## Requirements
修复源码审查确认的六类差异：石头先破甲后伤害；木盾分阶段减伤与收尾；五种开战物品发送激活；魔法入门缺蓝也激活；平衡魔棒随机处理并列资源；物品概率使用各自的平衡随机状态。联动次数、伤害、体力及概率序列须与原版一致。

## Design：接口与伪代码
沿用现有阶段、事件总线和 BalancedRngState，不增加结算深度或通用调度架构。

- `BalancedRngState.reset() -> None`：清零已有状态和 `last_roll`；`roll_percent(percent, rng) -> bool`：保留原公式，记录实际随机值到 `last_roll`；确定成功/失败的端点不取随机数，记录 None。此字段只供既有概率日志使用。
- `BattleItem.__init__(现有参数)`：新增独立 `chance_rng = BalancedRngState()`；`roll_chance(chance: float, rng) -> bool`：将 0..1 概率乘 100，委托该状态。`BattleState.prepareItems() -> None`：准备物品时 reset chance_rng。
- `Stone.onPreDealDamage_late(context) -> None`：执行破甲 effect；`Stone.run_effect(results, context) -> None`：触发时攻击，再激活，不在伤害后破甲。沿用现有命中阶段门控。
- `WoodenBuckler.__init__(现有参数)`：增加 `blocked_attack_event = None`，增加 `ShieldBlockedTrigger`。`run_effect(results, context) -> None`：前置触发时保存事件并减伤；收尾触发时扣攻击者体力、激活、发送 blocked 信号，再清空事件引用。
- `ShieldBlockedTrigger.update(context) -> bool`：仅 character_attacked 且事件 identity 等于盾牌保存的事件时返回 true；`connect_bus(context) -> None`：订阅持有者 character_attacked。
- `OnAttackedTrigger.update(context) -> bool`：保留命中、类型和 flag 条件；调用 item.roll_chance，日志读取 chance_rng.last_roll。
- `PocketSand/HealingHerbs/Flame/WalrusTusk/Whetstone.run_effect(results, context) -> None`：未触发则返回；既有效果之后 emit_activation。
- `MagicForDummies.run_effect(results, context) -> None`：触发时，法力足够才消耗并增加生命上限；无论法力是否足够都 emit_activation。
- `WandOfEquilibrium._least_resource_name(buffs, rng) -> str` / `_most_resource_name(buffs, rng) -> str`：求极值、收集全部并列候选、rng.choice；`run_effect(results, context)` 将战斗 rng 传入两处调用。
- `Twine.run_effect`、`Garlic.run_effect`、`Rat.run_effect`、`Broom.onDealtDamage`：保留既有效果顺序，将每处概率判断改用 self.roll_chance；日志读取 last_roll；老鼠两个概率共用该物品的状态。接口均保留现有参数和 None 返回值。

流程：攻击命中 → 木盾减伤 → 石头破甲 → 护甲/生命伤害 → character_attacked 中木盾扣体力与激活。开战效果 → 激活 → 已订阅联动物品；魔法入门冷却触发 → 可选资源效果 → 激活。

## Tasks
1. [x] 实现物品 RNG 状态和日志接入。
2. [x] 调整石头、木盾阶段（依赖 1）。
3. [x] 补全激活通知和随机并列选择。
4. [x] 更新旧行为断言，补充伤害顺序、联动和概率序列回归测试；运行完整测试集。

## Acceptance Criteria / Tests
- 石头固定伤害 2 对 4 护甲：护甲归零，生命减少 2；未命中不破甲。
- 木盾前置阶段仅减伤，扣体力及激活只能在匹配攻击的收尾发生；不匹配事件不触发。
- 五种开战物品各发送一次激活且可推动黏黏计数；魔法入门无蓝不增加生命上限但仍发送激活。
- 魔棒并列最少/最多均可选中任一候选，不选非候选。
- 各物品 RNG 独立，准备时重置；老鼠两个概率共享状态；覆盖重复触发、概率端点和边界相等。
- 全部现有测试通过；不以测试通过替代完整 Godot GUI 一致性验证。

## 验证结果
2026-10-08：`python -m unittest discover -s tests -q` 全部 534 项通过，包含新增 9 项回归测试。新增用例位于 `tests/test_item_behavior_alignment_v1.py`。本轮未进行 Godot 图形界面复验。
