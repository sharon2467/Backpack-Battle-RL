# 知识库与项目状态文档恢复 SPEC

状态：待用户确认后执行

日期：2026-09-01

## 1. 背景与问题

`docs/backpack_battles_knowledge_base.md` 当前退回到了以 Wiki 为唯一事实来源的旧版本，且包含若干已经被解包源码否定或补充的描述。原有 `docs/current_stats.md` 与相应 SPEC 已丢失。

新的完整解包位于仓库根目录的 `Backpack Battles` 重解析目录，其实际目标为 `C:\Users\win\OneDrive\Desktop\Backpack Battles`。`gdre_export.log` 表明该工程来自 Godot 3.6.0，815 个脚本全部成功反编译，场景、资源、导入产物、加密 ItemData 与职业数据均大量恢复。它应替代 `AI-BackpackBattles/decompiled_full`，成为游戏战斗事实的首要本地依据。

本任务只恢复和修订文档，不修改战斗引擎、测试、数据文件、新解包或第三方仓库。

## 2. Requirements（需求）

### R1：恢复并修订本地知识库

更新 `docs/backpack_battles_knowledge_base.md`，使其满足：

1. 明确资料优先级：
   - 新解包 `Backpack Battles` 中的同版本脚本、场景与资源是战斗逻辑、物品布局、Timer/信号、职业资源和 run-cache 格式的首要依据；
   - 实际游戏可复现实验与缓存样本用于验证运行时行为；
   - 当前根目录战斗引擎及测试只能表示“项目当前实现”；
   - Wiki 用于中文术语、展示信息和外部交叉参考，不覆盖源码事实。
2. 每项关键结论标明证据性质：`源码确认`、`场景/资源确认`、`项目建模决定`、`待运行验证` 或 `Wiki 参考`。
3. 修正当前旧文档中已经确认的冲突，至少包括：
   - 冷却并不等同于“两次成功激活之间的时间”；
   - 疲惫在 60 秒前后采用不同增长率；
   - 伤害减免、事件减伤和 Block 的真实结算顺序；
   - 战斗开始物品的 `consume()/activate()` 激活通知语义；
   - Timer、tick、战斗开始顺序与信号连接应以场景为证据；
   - 物品占格、背包扩展格、四类 affected cells 和宝石槽不再标记为只能从 Wiki 猜测。
4. 增补新解包能够确认的结构化事实：
   - Godot 3.6.0 版本依据；
   - `ItemData_e.csv`、物品场景继承、TileMap、GemSocket、职业 `.tres`；
   - 9×7、63 格基础 Inventory 场景及动态可用格；
   - Character/Main 中的 Timer 默认值和信号；
   - `RunDatabase.gd`、`RunData.gd` 所定义的 cache 路径、请求规模、descriptor/version/socket/persistent-data 依赖；
   - 实际 `runs*.cache` 不在解包中，仍需从匹配版本 `user://` 取得。
5. 保留仍有价值的 Wiki 数据快照，但清楚标记其版本、用途和可能与解包 build 不一致的风险。
6. 把商店运营、配方和局外发育内容标记为历史规划或当前非目标，避免误导下一阶段实现。
7. 将观测与动作草案重写为当前“给定物品的摆盘/战斗环境”范围，实例身份、方向、位置、占格、四类影响格、宝石槽与 persistent data 必须可表达；不得把评估模型输出作为环境原始观测。

### R2：重新创建项目状态文档

创建 `docs/current_stats.md`，使其成为当前仓库的简明事实快照：

1. 记录三类资产的角色：
   - 根目录 Python 战斗引擎：当前主实现；
   - `Backpack Battles`：新的只读游戏真值源；
   - `AI-BackpackBattles`：第三方参考实现，不作为正确性权威。
2. 根据实际代码列出已实现能力，包括：
   - 9×7 摆盘、旋转、碰撞与三类现有 marker 链接；
   - 两名玩家初始化、物品实例、触发器/效果、攻击事件、Buff/Debuff、疲惫、日志与逐帧状态；
   - JSON 命令行入口；
   - 当前工厂注册物品清单。
3. 根据实际测试命令记录测试数量和结果，不沿用旧数字或未经复跑的数据。
4. 明确当前实现与新源码之间的关键差距：
   - 只实现少量物品；
   - 物品数值和布局仍为手工目录，而非从 ItemData/场景自动提取；
   - 缺少完整场景继承、Timer/信号和 RNG 顺序对齐；
   - marker 类型、背包动态可用格、宝石、persistent data、职业/loadout 尚未完整进入环境；
   - 尚无真实同版本 run-cache 样本及解码流水线；
   - `evaluate_layout()` 尚无评分实现；
   - 商店、配方、局外发育不属于当前阶段。
5. 给出下一阶段最小闭环：只读提取 ItemData → 场景结构化导出 → 获取同版本 cache → 建立源码对齐测试 → 逐项扩展现有战斗引擎。
6. 明确安全限制：不在唯一的新解包副本上启动 Godot 编辑器，避免 editor 分支因缺失明文 `ItemData.csv` 而改写有效的 `ItemData_e.csv`。

### R3：证据可追溯

1. 源码结论尽量引用相对于 `Backpack Battles` 根目录的文件路径和行号。
2. 项目状态引用根目录 Python 文件、README、测试文件或实际命令输出。
3. 数量统计注明是精确统计、静态引用下界还是抽样结果。
4. 无法从静态源码确定的运行时行为不得写成确定事实。

## 3. Design（设计）

### 3.1 文档职责

| 文档 | 职责 | 不承担的职责 |
| --- | --- | --- |
| `backpack_battles_knowledge_base.md` | 游戏事实、证据、术语、环境建模边界 | 汇报代码完成度、承诺实现日期 |
| `current_stats.md` | 当前代码能力、测试状态、源码资产状态、差距与下一步 | 重复完整机制说明、充当长期设计 SPEC |
| 本 SPEC | 定义本次恢复工作的范围、方法与验收 | 代替最终知识库或状态快照 |

### 3.2 证据优先级

```text
同版本解包脚本 + 场景/资源
          ↓
匹配版本运行轨迹 / run-cache / 可复现实验
          ↓
根目录当前实现与测试（仅说明项目现状）
          ↓
Wiki 与第三方模拟器（术语、提示、交叉参考）
```

发生冲突时不做“多数来源投票”。同版本源码与场景资源优先；若脚本与场景仍不能确定运行时顺序，则标为待运行验证。

### 3.3 知识库结构

知识库按以下结构整理：

1. 来源政策、版本锚点与证据标签；
2. 当前范围与非目标；
3. ItemData、物品实例和职业资源；
4. Inventory 与布局语义；
5. 战斗时间、初始化、伤害、状态和激活语义；
6. 已核对物品与尚未核对范围；
7. run-cache 数据来源和解码依赖；
8. 训练环境观测/动作建议；
9. 待验证问题与后续数据任务；
10. Wiki 历史数据附录。

不会为了保留旧段落顺序而牺牲可读性；重复、冲突或已经过时的段落直接合并或归档。

### 3.4 项目状态结构

`current_stats.md` 使用日期化快照，包含：

1. 一句话总体状态；
2. 代码与目录角色；
3. 已实现能力；
4. 当前物品覆盖；
5. 测试基线；
6. 新解包可用性与风险；
7. 与源码对齐差距；
8. 下一阶段优先级；
9. 明确非目标。

### 3.5 数据与接口

本任务不新增或修改生产函数。为满足审计过程可复核性，文档生成过程采用以下逻辑接口；它们是工作流程定义，不会实现为新代码。

#### `classify_claim`

```text
接口：classify_claim(claim, source_evidence, project_evidence) -> evidence_status

输入：
  claim：待写入知识库的机制结论
  source_evidence：新解包中的脚本、场景或资源证据
  project_evidence：根目录实现、测试或历史文档证据

输出：
  evidence_status：源码确认 / 场景资源确认 / 项目建模决定 /
                   待运行验证 / Wiki参考

伪代码：
  if 同版本脚本与场景共同确定结论:
      return 源码确认或场景资源确认
  if 只有项目代码定义该行为:
      return 项目建模决定
  if 结论依赖引擎调度、动态数据或实际缓存:
      return 待运行验证
  return Wiki参考
```

#### `collect_project_snapshot`

```text
接口：collect_project_snapshot(repo_root) -> project_snapshot

输入：repo_root：当前仓库根目录
输出：模块、入口、物品工厂、测试数量/结果、Git 工作区状态

伪代码：
  枚举根目录主实现与 tests
  从工厂注册表读取实际物品清单
  运行完整 unittest discovery
  记录通过/失败/跳过数量和执行日期
  检查 evaluate_layout 等明确占位接口
  返回不包含推测性完成度的状态快照
```

#### `audit_source_resources`

```text
接口：audit_source_resources(source_root) -> source_snapshot

输入：source_root：Backpack Battles 解包根目录
输出：版本锚点、关键资源存在性、路径引用和剩余缺口

伪代码：
  读取 gdre_export.log 与 project.godot
  核对 ItemData_e、物品场景、职业资源、Core 场景
  对关键 res:// 引用执行存在性检查
  区分确定缺失、动态路径下界、编辑器专用缺口
  不启动 Godot，不写入或导入资源
```

#### `render_recovered_documents`

```text
接口：render_recovered_documents(claim_audit, project_snapshot, source_snapshot)
      -> (knowledge_base_markdown, current_stats_markdown)

输入：经过分类的机制证据、项目状态和源码资产状态
输出：两份 Markdown 文档

伪代码：
  将游戏事实写入知识库并附证据标签
  将代码完成度和差距写入 current_stats
  删除两份文档之间的重复长段落
  对无法确认的内容显式降级为待验证
  校验所有本地路径、Markdown 表格和代码围栏
```

## 4. Tasks（任务拆解）

### T1：建立新解包证据矩阵

- 依赖：无。
- 只读核对版本、ItemData、Inventory、Item、Character、Main/CombatTimer、RunDatabase、RunData、职业资源和代表性物品场景。
- 输出：用于文档写作的事实/证据/状态列表，不创建额外中间文件。

### T2：修订知识库

- 依赖：T1。
- 更新来源政策、布局、战斗、激活、run-cache、观测/动作和待办章节。
- 保留仍有价值的 Wiki 表格，但明确其历史快照性质。
- 删除或归档与当前范围冲突的商店 AI 主线描述。

### T3：采集当前代码快照

- 依赖：无。
- 核对主模块、工厂清单、README、数据入口和明确未实现接口。
- 运行完整测试套件并记录实际结果。

### T4：创建 `current_stats.md`

- 依赖：T1、T3。
- 按实际代码和测试结果写出当前能力、关键差距、源码资产状态和下一阶段闭环。

### T5：一致性与格式验证

- 依赖：T2、T4。
- 搜索已知旧冲突措辞；验证 Markdown 标题、表格、代码围栏和本地路径。
- 运行 `git diff --check`。
- 确认除本 SPEC、知识库和 `current_stats.md` 外没有产生新的修改。

## 5. Acceptance Criteria / Tests（验收标准）

### 5.1 知识库验收

1. 不再出现“游戏事实只能来自 Wiki”或“近期仅使用 Wiki”的政策。
2. 新解包明确为 Godot 3.6.0 同版本主要真值源；旧 Godot 4.7 配置被标为不可信。
3. 冷却、疲惫、伤害顺序、开始物品激活和 Timer/tick 的旧冲突均已修正。
4. ItemData、场景继承、布局几何、四类 affected cells、宝石槽和职业资源有明确证据说明。
5. run-cache 被准确描述为运行时 `user://` 数据，而非解包资源；文档不声称当前已经取得样本。
6. 游戏事实、项目设计和待验证项可从措辞或标签上明确区分。
7. 当前非目标不再被写成下一阶段必须实现的主线。

### 5.2 `current_stats.md` 验收

1. 文件存在并标注快照日期。
2. 所列模块、入口和物品覆盖与当前代码一致。
3. 测试数字来自本次实际运行；若测试失败，写明失败而不伪报通过。
4. 清楚说明新解包已经解决的资源问题和仍存的 editor/run-cache 风险。
5. 清楚说明根目录引擎离源码对齐仍有多远，不把“已有框架”表述成“完整模拟器”。
6. 下一步建议以最小闭环排列，且不擅自扩展到商店或局外发育。

### 5.3 变更与格式验收

1. 只允许修改：
   - `docs/backpack_battles_knowledge_base.md`
   - `docs/current_stats.md`
   - `docs/knowledge_base_and_current_stats_recovery_spec.md`
2. 不修改用户已有的 `AGENTS.md` 变化。
3. 不修改 `Backpack Battles`、`AI-BackpackBattles`、根目录 Python 代码、测试或数据。
4. `git diff --check` 通过。
5. 所有引用的新解包本地路径均实际存在；所有不确定结论均显式标记。

## 6. 非目标与安全边界

- 不编写 ItemData 解密器、场景解析器或 run-cache 解析器。
- 不启动 Godot 或触发资源重新导入。
- 不从新解包复制 587 MiB 资源进入仓库。
- 不修复第三方模拟器或根目录战斗引擎。
- 不实现商店、配方、局外发育或强化学习模型。
- 不把缺失的明文 `ItemData.csv` 补成猜测文件，也不覆盖有效的 `ItemData_e.csv`。

## 7. 执行批准点

用户确认本 SPEC 后，才执行 T1-T5 并修改知识库及 `current_stats.md`。若证据核对发现会实质改变上述文档边界的新情况，应先报告再扩大范围。
