# resolve_attack 伤害字段源码调查 SPEC

日期：2026-10-06。范围：调查与文档；本轮不修改生产代码。

## 1. Requirements（需求）

- 以 `Backpack Battles/` 当前解包源码为唯一机制依据，对照当前工作区的 `BattleState.resolve_attack`，确定伤害相关字段的读取方、单位、公式、条件和生效阶段。
- 覆盖 `PlayerState` 新增字段、现有 `AttackEvent` 字段，以及原版物品伤害、暴击、命中与后续尖刺/吸血所需字段；明确哪些属于调用前或调用后的流程。
- 为维护者提供可直接据此修改结算器的顺序、字段表、函数接口与伪代码；标明源码疑点和当前缺口。
- 保留现有未提交修改，不引入局外系统或新的架构。

## 2. Design（设计）

沿原版 `Item.dealDamage → Character.dealDamage → Character.takeDamage` 调用链调查，并追踪 `DamageSource`、`DamageResult`、概率随机、伤害区间随机和修改结算单的物品脚本。按阶段映射回现有函数，不设计额外事件框架。

```text
准备伤害源 → 检查死亡 → 命中/闪避 → early
→ 伤害区间/疲惫 → 暴击/抗暴 → 抗性/固定减伤/无敌
→ pre_take_damage/事件减伤 → late → Block/生命
→ 事后通知/死亡 → 尖刺 → 返回调用方/吸血 → 来源 attacked
```

详细数据模型和逐字段接口放在同目录调查报告 `resolve_attack_damage_fields_audit.md`。每个报告中提出的具体函数均列出输入、输出和伪代码；纯源码回调保留原名称并注明由具体物品实现。本轮没有新增运行时函数。

必查接口：

| 接口 | 本轮处理方式 / 伪代码 |
| --- | --- |
| `BattleState.resolve_attack(self, event: AttackEvent) -> AttackEvent` | 校验现有实现；按源码顺序标记字段读取点；给出完整目标流程伪代码 |
| `BattleState.commit_health_reduction(self, player, blocked_damage, health_damage, *, log_handle=None) -> tuple[int, int]` | 核对提交边界；区分计算伤害与实际生命变化；检查死亡时机 |
| `BattleState._apply_melee_hit_statuses(self, event, final_damage) -> None` | 对照原版尖刺/吸血门控、数值口径和调用位置，记录差异 |
| `BattleState.heal(self, player, amount) -> int` | 检查治疗效率与反治疗应落在治疗函数中的阶段 |
| 原版伤害端点、随机、暴击与治疗函数 | 读取调用方与实现；报告中逐个列明接口与伪代码，不创建推测性生产实现 |

## 3. Tasks（任务拆解）

- [x] T1：阅读知识库、当前数据结构和结算器，保存本 SPEC。
- [x] T2（依赖 T1）：核对原版伤害主流程和随机状态所有者。
- [x] T3（依赖 T2）：追踪伤害端点、flags、回调、尖刺、吸血和治疗相关字段。
- [x] T4（依赖 T3）：保存逐字段位置表、函数接口/伪代码、实现缺口与验收场景。
- [x] T5（依赖 T4）：复查引用与覆盖范围，整理用户可审阅的结论。

## 4. Acceptance Criteria / Tests（验收标准）

- `PlayerState` 全部 21 个新增字段及 `AttackEvent` 全部字段均有明确落点或“无需参与公式”的说明。
- 对每项公式区分攻击者/防守者、百分数/倍率、取整/截断、伤害总量/生命伤害/实际扣血。
- 按当前 `resolve_attack` 的代码位置给出插入点，且标明早晚钩子能修改的字段和当次是否生效。
- 暴击层、必中、多类型、过量伤害、致死、负伤害中间量与来源为空等边界有说明。
- 所有机制结论有本地源码定位；疑似解包异常不自行纠正。
- 本轮为静态调查，不用模拟器测试通过来证明原版机制，不声称已经完成运行时对照。

## 5. 执行结果

- 调查报告已保存至 `docs/resolve_attack_damage_fields_audit.md`，含13个入口/结算/返回阶段、逐字段映射、接口伪代码、当前缺口和后续验收场景。
- 只读 AST 检查确认21个新增角色字段、27个攻击事件字段均有说明；73处核心引用的首个行号区间检查通过。
- 本轮只新增本 SPEC 和调查报告，未修改生产代码或测试；未运行 Godot 或战斗测试。
- `git diff --check` 检测到用户既有工作区 `battle_module_v1.py:578` 的行尾空白，保留原状；这不是本轮文档产生的变更。
