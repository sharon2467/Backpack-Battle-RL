# 暴击层与纯 Effect 尖刺的图形战斗验证 SPEC

日期：2026-10-06。

## 1. Requirements（需求）

使用两个 GPT-6.1-Sol 子 agent，分别验证自然暴击成功仍消耗暴击层、纯 Effect 伤害是否采用近战尖刺比例。先寻找原版实际相关物品，再通过工作区 `data/custom_opponent.json` 注入指定对手，使用带可见图形窗口的 Godot 战斗获得证据。不能以静态推断或仅 headless 运行代替实测。

需区分可达的原版物品组合与人为改 flags/概率的诊断场景；后者不能证明前者。日志插桩只观察，不改伤害条件或随机结果。保留已有用户修改与原 custom opponent 内容。

## 2. Design（设计）

两个子 agent 并行调查、编写各自 SPEC/夹具/观测脚本；共享 `custom_opponent.json`、`Backpack Battles/project.godot`、原版伤害脚本与 GUI 的变更/运行严格串行，由主 agent 授予实验时段。优先复用现有 custom opponent 测试入口，新增运行以可见窗口为准。

实验资料各用独立前缀：`crit_token_gui_*` 与 `effect_spikes_gui_*`。文档在 docs，脚本在 tests，夹具、日志、截图在 data。引擎和真实游戏存档与实验隔离。每次运行备份/恢复共享文件；不清理不属于本次实验的文件/进程。

```text
共同基线 → 并行物品调查与实验设计
→ 暴击实验独占共享文件/GUI → 恢复基线
→ Effect实验独占共享文件/GUI → 恢复基线
→ 汇总运行证据并修订调查结论
```

本协调 SPEC 不新增运行时函数。子 agent 在执行各自脚本改动前补充其具体函数接口、参数、返回值和伪代码；优先采用现有测试节点的逐帧推进和日志采集方式，不增加复杂架构。

## 3. Tasks（任务拆解）

- [x] T1：读取协作技能、现有 custom opponent 说明，建立本 SPEC。
- [x] T2：分别委派两个指定模型子 agent，明确假设、证据与文件归属。`crit_token_gui` 和 `effect_spikes_gui` 均使用 `gpt-6.1-sol`；首先授予前者共享实验时段。
- [x] T3（依赖 T2）：完成暴击物品筛选、可见战斗与层数/自然暴击结果观测，恢复共享文件。法杖自然100%成功后物品/角色层3/3→2/2。
- [x] T4（依赖 T2、共享实验时段）：完成 Effect 物品筛选、可见战斗与 flags/尖刺观测，恢复共享文件。雷神之锤纯Effect保留All=63，5组12点效果伤害各产生4点尖刺反伤，melee_limit=1/effect_limit=0。
- [x] T5（依赖 T3/T4）：主agent核对日志与截图，明确结论及限制，更新原调查文档第11节和两份实验结果。

## 4. Acceptance Criteria / Tests（验收标准）

- 两个子 agent 均明确使用 GPT-6.1-Sol，收到原版权威边界及完整任务上下文。
- 每个结论记录物品组合、版本/引擎、对手夹具、GUI截图、关键运行观测值与可复现命令。
- 暴击实验区分自然暴击判定与暴击层强制产生的暴击，记录判定前后层数。
- Effect 实验明确 source.types、CanTriggerSpikes、双方尖刺数量与各比例；不存在自然可达触发时如实报告，禁止把改 flags 的结果冒充原版行为。
- 没有同时写共享文件或竞争GUI；原始输入及临时插桩恢复，保留必要复现资料。

## 5. 执行结果

两项机制均在真实物品组合与可见GodotSteam3.6.2战斗中观察到。纯Effect结论有明确flag前提，并找到实际例外来源Thors Hammer。过程与资料分别保存在 `docs/crit_token_gui_results.md`、`docs/effect_spikes_gui_results.md`。

暴击子agent完成最终战斗后遭遇模型额度限制，主agent接手报告整理和恢复核对；Effect子agent正常完成实验。主agent查看了最终战斗截图、独立读取原日志，并在两项实验后核对三个共享文件均匹配暴击实验前备份哈希。模拟器生产代码及既有用户修改保持不变。
