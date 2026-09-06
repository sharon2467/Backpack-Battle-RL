# 当前项目状态

快照日期：2026-09-01

对应提交：`2fa0b2e add another resolved backpack battles`（`master`）

## 总体结论

根目录已经有一个可运行、测试覆盖较充分的小型 Python 战斗引擎，但它还不是《背包乱斗》的完整战斗模拟器。目前真正的主线不是换用第三方模拟器，也不是先恢复 GUI，而是把新的完整解包作为只读真值源，系统提取 ItemData、场景几何、Timer/信号和缓存映射，再逐项修正并扩展现有引擎。

当前可量化状态：

- 7 个主 Python 模块，共约 3,547 行；仅使用 Python 标准库。
- 19 个已经注册战斗行为的物品。
- 23 个手工维护布局目录条目，其中 4 个只有布局/元数据、没有默认战斗工厂。
- 10 个测试文件、493 个测试方法；本次完整测试 493/493 通过。
- `evaluate_layout()` 仍明确抛出 `NotImplementedError`，尚无摆盘评分器。
- 没有 ItemData/场景自动提取器，也没有 run-cache 解码流水线。

## 三类代码与资产的角色

| 路径 | 当前角色 | 正确性地位 |
| --- | --- | --- |
| 根目录 `*_v1.py` | 本项目正在发展的无 GUI Python 战斗引擎 | 当前主实现，但必须继续对照源码修正 |
| `Backpack Battles` | 新的 Godot 3.6.0 完整解包 | 战斗逻辑、场景结构和数据格式的首要真值源；保持只读 |
| `AI-BackpackBattles` | GitHub 第三方项目、旧脚本快照和参考模拟器 | 仅作实现参考，不作为逻辑正确性的权威 |

`Backpack Battles` 在仓库中表现为重解析目录，实际位置是 `C:\Users\win\OneDrive\Desktop\Backpack Battles`。

## 根目录战斗引擎

### 模块概况

| 模块 | 行数 | 已有职责 |
| --- | ---: | --- |
| `basic_backpack_v1.py` | 153 | 加载手工物品目录、旋转格子、放置物品、构建 9×7 占用矩阵、查找 marker 链接 |
| `battle_initializer_v1.py` | 125 | 校验两名玩家、实例化物品、生成实例 ID、连接 marker、确定主动物品顺序 |
| `battle_module_v1.py` | 886 | 玩家/物品/战斗状态、帧推进、攻击事件、系统 tick、伤害提交、日志、状态快照 |
| `item_triggers_v1.py` | 337 | 开战、冷却、延时、连接物品激活、受击和攻击未命中等触发器 |
| `item_effects_v1.py` | 621 | 耐力、治疗、最大生命、护盾、Buff/Debuff、攻击、减伤响应等可复用效果 |
| `item_factory_registry_v1.py` | 1,064 | 19 个具体物品类及默认工厂表 |
| `main_v1.py` | 361 | JSON 输入校验、命令行入口、运行循环、结果序列化、历史压缩和错误输出 |

### 已实现的环境能力

布局层目前支持：

- 每名玩家独立的 9×7 坐标棋盘；
- `0/90/180/270` 度旋转；
- 多格物品、越界和重叠检查；
- 物品实例级 `item_key`；
- `star`、`diamond`、`triangle` 三类手工 marker；
- marker 指向物品实例后的链接去重；
- 同类物品多实例摆放。

战斗层目前支持：

- 恰好两名玩家及独立生命、最大生命、护盾、耐力和最大耐力；
- 固定步长帧推进和每秒 1 点耐力自然恢复；
- 物品 trigger/effect 组合与实例级可变状态；
- 主动冷却、一次性延时、开战触发、相连物品激活、受击和未命中响应；
- `melee`、`ranged`、`effect` 攻击类型；
- 命中、随机伤害、Block、Spikes、Vampirism；
- Buff：`Empower`、`Heat`、`Luck`、`Mana`、`Regeneration`、`Spikes`、`Vampirism`；
- Debuff：`Poison`、`Blind`、`Cold`；
- Regeneration/Poison 系统时钟和疲惫伤害；
- 遇到致死事件后立即停止本帧剩余结算；
- 全局可注入 RNG、结构化战斗日志和逐帧玩家状态历史；
- 将状态历史中的连续自然耐力恢复帧压缩为区间。

输入输出层目前支持：

- `battle_run_v1` JSON 配置；
- 玩家、生命、耐力、职业标签和摆放校验；
- 命令行覆盖 `max_frames` 与 `frame_delta`；
- `battle_result_v1` 胜负、结束原因、最终状态、主动物品、日志和可选状态历史；
- 配置错误和运行错误的结构化输出。

## 当前物品覆盖

`DEFAULT_ITEM_FACTORIES` 当前注册 19 个物品：

| 类别 | 物品 |
| --- | --- |
| 开战/被动触发 | Pocket Sand、Healing Herbs、Flame、Walrus Tusk、Whetstone、Twine、Goobling、Wooden Buckler |
| 武器/攻击 | Broom、Wooden Sword、Shortbow、Stone、Pan |
| 食物/周期效果 | Banana、Garlic |
| 其他周期物品 | Shiny Shell、Wand of Equilibrium、Magic For Dummies、Rat |

`data/item_catalog_v1.json` 另有 `bag_of_stones`、`blood_harvester`、`health_potion` 和 `mage_hat` 四个布局条目，但它们没有注册默认战斗工厂。因此“目录有 23 项”和“能运行战斗行为的物品有 19 项”必须分开统计。

当前物品数据均为手工写入 Python 类和 JSON 目录，并非从新解包自动生成。即使某个物品已有大量单元测试，也只能说明它符合当时的项目 SPEC，不能证明已经与当前游戏 build 对齐。

## 测试基线

本次使用 Codex 工作区自带 Python 执行：

```powershell
& 'C:\Users\win\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests
```

结果：

```text
Ran 493 tests in 0.074s
OK
```

测试覆盖的主要方面包括：

- 旋转、占格、越界、重叠和 marker 链接；
- 战斗初始化、实例身份和主动物品顺序；
- trigger/effect 接口和实例隔离；
- 命中、攻击响应、嵌套攻击、Block、Spikes、Vampirism；
- Buff/Debuff、疲惫、Poison/Regeneration 时钟；
- 19 个物品工厂的元数据和主要分支；
- 日志顺序、致死中止、状态历史和 JSON 入口。

这是回归测试基线，不是游戏源码一致性测试。多数期望值来自旧 Wiki、历史 SPEC 或人工决策；下一阶段需要补充以新解包为预期值的 conformance tests。

## 新解包状态

### 完整性

只读静态审计得到：

- Godot 3.6.0 工程，bytecode revision 为 3.5.0；
- 15,355 个文件，约 587 MiB；
- 815 个 `.gd` 和 815 个原加密 `.gde`；
- 1,025 个 `.tscn`、172 个 `.tres`、145 个 `.res`；
- 759 个 `Items` 场景；
- 完整的贴图、音频、字体、翻译、shader、Godot 3 `.import` 资源和跨平台 SQLite 库；
- 旧 `AI-BackpackBattles/decompiled_full` 的 678 个静态断链中恢复了 662 个；
- 新工程静态可见的具体 `res://` 路径中，4,053/4,070 按字面存在。

`gdre_export.log` 报告 9,356 个 PCK 文件提取无错误，815 个脚本全部反编译成功；只有一个 imported resource 被标记为有损转换。旧目录中标记 Godot 4.7 的 `project.godot` 不应继续作为版本依据。

### 已恢复的训练关键资源

- `Sheets/CSV/ItemData_e.csv`：80,976 字节，文件头为 `GDEC`；MD5 为 `98D4080E5C1BEDDFD95159F841F8EFB7`。
- `Sheets/ItemBook.gd`：保留 0..31 的 32 字节 key 构造、ItemData 读取、descriptor 建立和 GemSocket 统计逻辑。
- 物品场景：可提取继承链、脚本映射、CollisionMap、背包 extension、四类 affected cells、GemSocket、Timer 和信号。
- `Core/Inventory.tscn`：恢复 9×7 基础 TileMap 和 affected tile 资源。
- `Core/Character.tscn`：恢复 `TickTimer` 及其 `onTick` 信号连接。
- `Core/Main.tscn`：恢复 FatigueStartTimer、FatigueTickTimer 和战斗计时连接。
- 七个职业的 `.tres`、Sprite 和 Chibi 场景：可恢复初始资源和三套 loadout。
- `RunDatabase.gd`、`RunData.gd`：缓存路径、网络请求、descriptor/version/socket/persistent-data 解码依赖均在。

### 仍有的资源与运行风险

1. 新解包没有实际 `runs*.cache`；这些文件位于游戏运行时 `user://`，必须从匹配版本用户数据目录另行取得。
2. 明文 `Sheets/CSV/ItemData.csv` 不存在。编辑器分支会先读取它，再以 `File.WRITE` 打开有效的 `ItemData_e.csv`，因此不能在唯一副本上直接用 Godot 编辑器运行。
3. 三个 editor/debug 场景、一个默认关闭的 Statistics 脚本及少量插件示例资源仍断链，但不阻塞无 GUI 训练数据提取。
4. 精确运行原工程需要 GodotSteam 3.6.0；本次没有启动引擎，不能把静态完整性等同于运行验证。
5. 动态资源路径和场景继承必须递归解析，静态路径存在率不是完整语义覆盖率。

## 当前实现与游戏源码的主要差距

### P0：已确认的行为冲突

这些问题会直接改变战斗结果，应优先修正：

- Pocket Sand、Healing Herbs、Flame、Walrus Tusk 当前只施加效果，不调用 `emit_activation()`；新源码的 `consume()/activate()` 路径表明这些开战效果会产生激活事件。
- 当前疲惫从 17 秒开始一直使用 `previous + floor(previous/10) + 1`；源码在 60 秒后切换为 20% 增长。
- 当前伤害先划分 Block/Health，`commit_health_reduction()` 中仍只有未来减伤/无敌的注释；源码的伤害减免、事件减伤、Block 和生命提交顺序尚未复现。
- 当前 `BattleState.step()` 按 `active_items` 插入顺序逐个执行；源码包含战斗准备阶段、优先级和随机化顺序。
- 当前 cooldown 只按固定基准、Heat/Cold 和少量手工加速累计，尚未复现源码的初始随机偏移、完整速度修饰和场景级 Timer 语义。

### P1：数据与布局缺口

- 只有手工维护的 23 个目录条目，没有从 ItemData/场景自动生成的 descriptor 表。
- 只支持 `star/diamond/triangle` 三类 marker；源码有 Primary、Secondary、Tertiary、Lightning 四类 affected cells，且不是简单名称替换。
- 没有动态可放置格、背包物品提供格、extension cells 的完整状态模型。
- `socket_count` 只是物品类元数据；没有 Gem 实例、槽位顺序和宝石效果。
- 没有场景继承合并、导出字段、节点 Timer、信号和动画回调的结构化提取。
- 没有职业 `.tres`、loadout、item version 和 persistent data 在运行输入中的表达。
- 当前观测历史只记录玩家数值，不记录布局、物品内部状态或触发器状态。

### P1：战斗机制覆盖缺口

- 只实现 19 个物品，远少于新解包的完整 descriptor/物品场景集合。
- Buff/Debuff 仅覆盖当前小集合；复制、抵抗、反弹、保护、时限效果等通用机制不完整。
- 暴击、伤害类型组合、无敌、眩晕、复活、Battle Rage 等尚未完整实现。
- 不同物品脚本中的 prepare、battle start、cooldown、on-use、on-hit、on-miss、destroy/consume 和 persistent-data 行为尚未系统映射。
- RNG 调用顺序只在现有手工物品范围内受测试保护，尚未与 Godot 源码逐事件对齐。

### P1：数据采集缺口

- 没有同版本 `runs_steam.cache` 或 `runs_sw.cache` 样本。
- 没有 ItemData 解密和 descriptor index 导出工具。
- 没有 cache 版本拒绝、socket/persistent bits 解码、匿名化和训练集切分流程。
- 没有把解码后的真实摆盘重新送入引擎进行合法性和回放校验的工具。

### P2：训练接口缺口

- `evaluate_layout()` 尚未实现。
- 还没有稳定的 Gymnasium/PettingZoo 风格环境接口；当前只有单次 JSON 战斗入口。
- 没有动作合法性 mask、批量并行仿真、固定种子评测集和源码差分基准。
- 尚未训练或接入摆盘模型。

## 下一阶段最小闭环

1. **保护并锚定源码版本**：保持新解包只读，保存 `gdre_export.log` 和 ItemData MD5，不在唯一副本上启动编辑器。
2. **只读提取 ItemData**：解密 `ItemData_e.csv`，导出 descriptor index、版本、数值、tags、scene/script 和 persistent-data 相关字段。
3. **解析战斗场景**：递归合并物品场景继承，提取占格、extension、四类 affected cells、GemSocket、Timer、信号和导出字段。
4. **建立源码一致性测试**：先修正 P0 冲突，再为通用机制和代表性物品建立“源码证据 → 测试 → 实现”的闭环。
5. **取得并解析同版本 cache**：以 ItemData MD5/build 为版本锚点，完成 descriptor/socket/persistent bits 解码和匿名化。
6. **扩展现有引擎**：优先补通用机制和数据驱动工厂，再逐步增加物品，避免继续为每个物品重复手写底层逻辑。
7. **最后封装训练环境**：在战斗和布局回放通过源码对齐后，再实现批量 step/reset、观测编码、动作 mask 和评测协议。

## 当前非目标

- 原游戏 GUI、音效、贴图和登录系统的恢复或重写；
- 商店运营、配方阶段和局外发育；
- 让第三方 `AI-BackpackBattles` 模拟器成为主引擎；
- 在未建立源码对齐测试前直接进行大规模强化学习训练；
- 在唯一解包副本上进行会写入资源的 Godot 编辑器实验。

## 完成定义

只有满足以下条件，才能把项目从“小型战斗引擎”称为“可用于训练的源码对齐环境”：

- 关键通用机制和目标物品有逐项源码证据及自动化一致性测试；
- 物品数值、布局、Timer/信号和 persistent data 来自同版本结构化提取，而非手工抄写；
- 真实同版本 run-cache 可以稳定解码、版本校验并重建合法摆盘；
- 固定种子下的代表性战斗回放与游戏行为一致；
- 训练 API 不泄露未来信息，并能稳定批量运行。
