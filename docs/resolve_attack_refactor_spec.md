# 拆分 BattleState.resolve_attack

## Requirements
让维护者从主函数直接读出一次攻击的阶段顺序。仅在 battle_module_v1.py 的 BattleState 内提取私有方法。保留公共接口、同一个可变事件、既有公式、校验、随机调用、日志、信号和战斗结束时机。

## Design
不增加数据结构。item 是入口处保存的来源物品，is_attack 是原有近战/远程判定；整个调用沿用这两个局部值。以下方法的 event 均为 AttackEvent，item 为 BattleItem | None，is_attack 为 bool。

| 方法签名（省略 self） | 伪代码，按执行顺序 |
|---|---|
| resolve_attack(event) → AttackEvent | 校验；目标已死则写入零伤害并返回；判定命中并运行早期回调；未命中则记录，否则掷伤害、结算暴击、减伤与晚期回调、提交；两条路径均执行收尾并返回原事件 |
| _determine_attack_hit(event, item, is_attack) → None | 判命中；命中时消耗闪避；符合条件时发送早期信号并调用物品钩子 |
| _record_attack_miss(event) → None | 写未命中日志；校验事件未结算且仍未命中；标为已结算 |
| _roll_attack_damage(event, item, is_attack) → None | 依来源与类型调整范围并掷伤害；累加待结算伤害及疲劳加值 |
| _apply_attack_crit(event, item) → None | 按现有次序判暴击、消耗层数、判抵抗；成功时应用倍率 |
| _apply_attack_mitigation(event, item, is_attack) → None | 应用抗性、固定减伤与无敌；发受击前置信号、扣除防止的伤害；发来源晚期信号与钩子、受击晚期信号 |
| _commit_attack_hit(event, item) → None | 校验；分配护甲和生命伤害；标为已结算、记录日志、扣除护甲和生命 |
| _finish_attack(event, item, is_attack) → None | 发受击与受伤信号、调用来源钩子；判死亡；结算荆棘、吸血及来源 attacked 信号 |

## Tasks
1. 在当前工作区上运行原测试作为基线。
2. 在原类内移动阶段代码，不改调用方及其他模块。
3. 再运行相同测试并核对变更。

## Acceptance Criteria
公共方法仍返回传入的事件；死亡目标、命中与未命中三条路径保持原语义，异常、日志与回调仍在原阶段发生。既有测试结果与基线一致。
