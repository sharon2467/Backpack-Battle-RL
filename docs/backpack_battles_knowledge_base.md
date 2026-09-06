# 《背包乱斗》强化学习规划知识库

最后按新解包校订：2026-09-01

本文件只覆盖战斗、物品与背包布局、物品实例、对手 run 数据，以及与当前布局训练目标直接相关的状态/动作定义。商店经营、配方规划和局外成长不属于当前目标。

## 证据政策

游戏事实按以下优先级处理：

1. `Backpack Battles/` 中当前完整解包的脚本、场景和资源；
2. 与同一游戏版本匹配的运行时日志、战斗回放和 `user://` 缓存样本；
3. 根目录模拟器与测试，只用于说明项目实现状态，不能反向证明游戏机制；
4. Wiki、第三方模拟器和 README，只作术语、外观或历史参考。

当低优先级资料与高优先级证据冲突时，以高优先级证据为准。`AI-BackpackBattles/simulator` 与 `AI-BackpackBattles/decompiled_full` 都不能作为正确性证据；后者的重建配置甚至声明 Godot 4.7，而当前完整解包由导出日志识别为 Godot 3.6.0（`AI-BackpackBattles/decompiled_full/project.godot:9,15`；`Backpack Battles/gdre_export.log:8,65`）。

本文使用这些证据标签：

- **源码确认**：脚本明确给出控制流、数据结构或公式。
- **场景/资源确认**：`.tscn`、`.tres` 或数据资源明确给出结构或取值。
- **项目建模决定**：为了训练接口作出的选择，不伪装成游戏事实。
- **待运行验证**：静态解包不足以确定的引擎调度、样本内容或边界行为。
- **Wiki 参考**：只保留术语、外观或历史快照，不用于裁决实现。

引用路径均相对仓库根目录。中文术语可沿用 Wiki 译名，但枚举、字段与动作名保留源码拼写。

## 当前权威解包

**源码确认**：`Backpack Battles/gdre_export.log` 记录了 Godot 3.6.0、9356 个文件校验与解出均无错误、815 个脚本全部反编译且 0 个失败（`Backpack Battles/gdre_export.log:8-11,28-29`）。游戏内版本常量为 `1.1.8`（`Backpack Battles/Core/Game.gd:3-16`）。这些事实证明本知识库所引用的是当前新解包，而不是旧的 4.x 重建结果。

**待运行验证**：完整反编译不等于运行时等价性已经逐项证明。涉及同一物理帧内 signal 回调先后、Godot Timer 的边界触发、随机数消耗顺序或疑似反编译异常时，仍需用 Godot 3.6.0 的匹配运行轨迹验证。本轮不启动 Godot。

## 物品静态数据与资源层

### ItemData 与 `ItemDescriptor`

**源码确认**：正式构建从加密的 `Sheets/CSV/ItemData_e.csv` 读取物品表。密钥按 0 到 31 生成，`Table.loadFromCsv()` 使用 `File.open_encrypted()` 读取；编辑器/特定测试分支才读取明文 `ItemData.csv`（`Backpack Battles/Sheets/ItemBook.gd:640-685,724-727`；`Backpack Battles/Sheets/Table.gd:6-29`）。因此仓库中加密文件不能直接当普通 CSV 查看，但它仍是游戏正式数据输入。

`ItemDescriptor` 是每种物品的静态描述，不是单个物品实例。关键字段包括：

- `identifier`、`itemIndex`、`scene`、`version`、`releaseState`；
- `rarity`、`types`、`classes`、`tags`、`material`、`physics`；
- `minDam`、`maxDam`、`cd`/`extraCds`、`accuracy`、`staminaCost`、`block`；
- `chance`、`chance2`、`shopChance`、命名参数与堆叠类型位图；
- `canActivate`、动画、配方与出现回合等元数据。

字段定义见 `Backpack Battles/Items/ItemDescriptor.gd:23-84`。加载器把表格列映射到描述符、解析多个冷却与命名参数，并按物品名找到对应场景（`Backpack Battles/Sheets/ItemBook.gd:731-803,821-889,944-960`）。

**项目建模决定**：训练侧应保存稳定的 `item_index`/规范化标识符，并把多类型、多职业字段编码成集合或 multi-hot。不得仅靠显示名连接数据，也不得把 Wiki Cargo 行号当游戏内 ID。

### 物品场景、形状、方向与宝石槽

**场景/资源确认**：物品场景通常继承 `Items/Item.tscn`。基场景是 `RigidBody2D`，包含 `CollisionMap` TileMap 与 `Icon/Sockets`；各物品场景覆盖 TileMap 数据并按需实例化 `GemSocket.tscn`（`Backpack Battles/Items/Item.tscn:1768-1793`；示例 `Backpack Battles/Items/WoodenSword.tscn:3-6,13-28`、`Backpack Battles/Items/Pandamonium.tscn:3-6,103-123`）。

**源码确认**：`CollisionMap` 的 tile id 语义不是 Wiki 猜测：

- `Extension = 2`：背包物品扩出的可用格；
- `Collision = 3`：普通物品占用/碰撞格；
- `Affected = 4`、`AffectedSecondary = 6`、`AffectedTertiary = 10`、`AffectedLightning = 11`：四类静态受影响格；
- `AffectedDynamic = 5`、`AffectedSecondaryDynamic = 7`：运行时动态生成的前两类受影响格；
- `AffectedExtension = 8`：可在运行时启停的扩展影响格。

枚举和颜色映射见 `Backpack Battles/Items/Item.gd:189-213`；初始化时缓存 collision/extension/affected-extension 的流程见 `Backpack Battles/Items/Item.gd:510-605,726-728`。

方向是四值 `UP/RIGHT/DOWN/LEFT`，旋转会更新 `faceDirection` 与场景变换（`Backpack Battles/Items/Item.gd:157-162,1964-2047`）。形状和 affected cells 必须按“物品场景 + 当前方向 + 动态扩展”计算，不能只按矩形宽高表示。

`GemSocket` 是真实场景节点，槽中保存 `item` 与可空的 `gem` 引用；可用性还受拥有者与出售状态限制（`Backpack Battles/Items/GemSocket.gd:1-35`；`Backpack Battles/Items/GemSocket.tscn:1-15`）。物品实例可枚举槽位、宝石、宝石方向与锁定状态（`Backpack Battles/Items/Item.gd:2978-3057`）。

### 职业与初始布局资源

**源码确认**：完整版本的职业枚举包含 `Ranger`、`Reaper`、`Berserker`、`Pyromancer`、`Mage`、`Adventurer`、`Engineer` 七个职业（`Backpack Battles/Core/Game.gd:129-137`）。`ItemDescriptor.StuffedClasses` 另含 `Neutral` 位掩码（`Backpack Battles/Items/ItemDescriptor.gd:4-15`）。

**场景/资源确认**：职业资源直接定义生命、耐力、金币及三套初始物品数组；每个 `StartingItem` 保存 `itemName`、`faceDirection` 和 `topLeftCell`（`Backpack Battles/CharacterClasses/CharacterClass.gd:1-9,97-107`；`Backpack Battles/CharacterClasses/StartingItem.gd:1-7`）。例如 Ranger 资源同时包含背包、普通物品、方向和左上格坐标（`Backpack Battles/CharacterClasses/Ranger/Ranger.tres:6-73`）。初始数值与布局应从当前职业资源导入，不应套用“所有职业相同”的旧 Wiki 概括。

## 背包网格与合法布局

### 地址空间与动态可用格

**源码确认 + 场景/资源确认**：Inventory 的地址空间是 `9 × 7`，最大编码范围是 `10 × 10`，格子尺寸为 `80 × 80`（`Backpack Battles/Core/Inventory.gd:37-42`）。`Inventory.tscn` 的 TileMap 确实列出 9 列、7 行共 63 个坐标（`Backpack Battles/Core/Inventory.tscn:309-323`）。

63 是可寻址边界，不等于任意时刻都可放置普通物品。Inventory 同时维护：

- `inventoryCells`：场景中的全地址空间；
- `bagCells`：当前背包实例扩出的内部/可用格；
- `filledCells`：普通物品当前占用的碰撞格；
- `items`：按实例保存的物品列表。

见 `Backpack Battles/Core/Inventory.gd:45-56,88-123`。背包只能占用尚未由其他背包扩出的潜在格；普通物品的全部 collision cells 必须位于当前可放置格中，且不能与 `filledCells` 冲突（`Backpack Battles/Core/Inventory.gd:186-219`）。背包和普通物品分别写入 `bagCells` 与 `filledCells`（`Backpack Battles/Core/Inventory.gd:609-627`）。

**项目建模决定**：布局环境每一步都要重新生成动态 `placable_cells` 与合法动作掩码。它至少区分：地址空间、当前背包可用格、普通物品占用格、可继续放背包的潜在格。将固定 63 格全视为可放置会产生游戏中非法的布局。

### affected cells 与实例关系

**源码确认**：四类 affected cells 分别经过 `canAffect`、`canAffect_secondary`、`canAffect_tertiary`、`canAffect_lightning` 筛选。命中某一格不自动代表格中实例真正受影响；代码还会处理空格效果、物品类型筛选、同一实例跨多格去重，以及 Lightning 的不同去重规则（`Backpack Battles/Items/Item.gd:3523-3547`；`Backpack Battles/Core/Inventory.gd:291-345`）。

**项目建模决定**：观测既保存原始四类 cell 集合，也保存按当前布局解析后的 affected instance ids。前者让模型理解方向/空间，后者避免模型重复推导复杂实例去重语义。

## 物品实例状态

**源码确认**：同种 `ItemDescriptor` 可实例化多个独立 `Item`。实例持有 owner、所在 Inventory、`occupiedCells`、`faceDirection`、宝石、是否 consumed、动态类型、冷却进度、缓存的 affected instances 等状态（`Backpack Battles/Items/Item.gd:382-450`）。因此“物品种类列表”不能完整表示布局或战斗。

`getData()`/`setData()` 是实例扩展点；基类默认无数据，但具体物品可覆盖（`Backpack Battles/Items/Item.gd:822-826`）。对手 run 的持久实例数据采用可选 `pd`：只有实现 `getDataPersistent()` 的物品才写入位流，反序列化后通过 `setData()` 恢复（`Backpack Battles/Core/RunDatabase.gd:584-607`；`Backpack Battles/Utility/RunData.gd:257-267`；`Backpack Battles/Core/Game.gd:2884-2894`）。

**项目建模决定**：环境为每个当前物品实例分配 episode 内稳定且唯一的 `instance_id`。`item_index` 代表种类，`instance_id` 代表副本；两者不得混用。`pd` 在未实现对应解码器前保留为不透明、版本化字段，不能丢弃或臆测含义。

## 战斗机制

### 战斗初始化与开始顺序

**源码确认**：进入战斗时，游戏先构造对手、装入对手物品并初始化 CombatTimer。玩家物品和对手物品各自先 `shuffle()`，再按 `getTriggerPriority()` 降序排序；随后异步 `prepareItems(player + opponent)`，并在 `COMBAT_DELAY` 后调用 `activateItems(player + opponent)`（`Backpack Battles/Core/Game.gd:2627-2670`；排序函数见 `Backpack Battles/Core/Game.gd:5375-5384`）。同优先级的相对次序因预先 shuffle 而不是固定页面顺序。

`activateItems()` 的源码顺序为：

1. 发出全局 `combat_start` signal；
2. 启动 CombatTimer；
3. 依次调用玩家与对手 `Character.combatStart()`；
4. 对合并后的物品序列完成全部 `preCombatStart()`；
5. 再完成全部 `combatStart()`；
6. 最后完成全部 `postCombatStart()`。

见 `Backpack Battles/Core/Game.gd:2897-2920`。物品 `prepare()` 会先缓存当前 affected instances 并准备宝石；`preCombatStart()` 初始化首轮冷却，三个物品阶段也各自递归对应宝石钩子（`Backpack Battles/Items/Item.gd:3339-3395`）。

**待运行验证**：全局 signal 的嵌套回调、deferred `prepareItems` 与延迟激活在同帧边界上的精确顺序，以及相同 Timer 到期时双方谁先执行，需要匹配版本运行轨迹确认。静态模拟器应显式建模这些顺序，而不是依赖宿主语言字典顺序。

### Timer 与周期 Tick

**场景/资源确认**：Character 场景的 `TickTimer.timeout` 连接到 `onTick()`；战斗开始时 `tickCounter = 0` 并启动 Timer，战斗结束时停止（`Backpack Battles/Core/Character.tscn:1632-1645,1665-1670`；`Backpack Battles/Core/Character.gd:328-346`）。

**源码确认**：`onTick()` 按 tick 奇偶交替处理：偶数 tick 用当前 `Regeneration` 治疗，奇数 tick 用当前 `Poison` 造成伤害，然后计数加一（`Backpack Battles/Core/Character.gd:401-414`）。因此 Regeneration 与 Poison 各自不是每秒同时结算；在默认重复 Timer 节奏下，它们各每两个 tick 结算一次。

**待运行验证**：`Character.tscn` 未显式写 `wait_time`，精确首 tick 时间依赖 Godot 3.6 Timer 默认值与启动帧。离线模拟器采用 1 秒默认值前，应以运行日志固定时间零点和边界语义。

### 冷却、速度与耐力

**源码确认**：物品有冷却时，战斗前计算带随机扰动的 `iterationCooldown`，令 `triggerTime = iterationCooldown` 并启用物理处理（`Backpack Battles/Items/Item.gd:3358-3366,3788-3795`）。未眩晕时，每个物理帧执行：

```text
triggerTime -= delta * speed
if triggerTime <= 0: trigger()
```

`trigger()` 先重算下一周期并执行 `triggerTime += iterationCooldown`，再调用具体物品的 `doCooldownEffect()`（`Backpack Battles/Items/Item.gd:4409-4442`）。所以源码中的冷却是“效果尝试的调度周期”，不是“两次成功激活之间的时间”。

武器的 `doCooldownEffect()` 只有在 `useStamina()` 成功时才攻击；体力不足会记录事件与动画，但由于下一周期已经在此前排好，不会停在满冷却等待体力（`Backpack Battles/Items/Weapon.gd:7-13`；`Backpack Battles/Items/Item.gd:4196-4207`）。

速度不是简单把多个百分比逐项乘在冷却值上。当前通用实现先取 `speed_ = speedScale + (Heat - Cold) × 0.02`：非负时倍率为 `1 + speed_`，负值时为 `1 / (1 - speed_)`，最终限制在 `[0.1, 10]`；显示用修正冷却为 `baseCooldown / speed`（`Backpack Battles/Items/Item.gd:3725-3743,3781-3785`）。

### 伤害类型、标志与结算顺序

**源码确认**：`DamageSource.Type` 包含 `Melee`、`Ranged`、`Effect`、`SelfDamage`，以及特殊的 `Unhealing`、`Spikes`、`Poison`、`Fatigue`。是否可格挡、可 miss、可暴击、可触发尖刺/吸血/物品由独立 flags 控制，不能只凭伤害类型推导（`Backpack Battles/Utility/DamageSource.gd:4-37,57-83,132-158`）。例如疲惫源明确只有 `CanBeBlocked`（`Backpack Battles/Core/Game.gd:2138-2145`）。

`Character.takeDamage()` 的主要结算顺序是：

1. 复制伤害源，检查死亡；
2. 若允许 miss，做命中检定并可能消耗 dodge stack；
3. 执行攻击的 early pre-deal hook；
4. 命中时抽取基础伤害，叠加防守方 fatigue bonus；
5. 做暴击/暴击抵抗；
6. 先应用百分比 `damageResistance`；
7. 仅对 attack 应用固定 `damageReduction`；
8. 无敌将当前伤害置零；
9. 发出 `pre_take_damage`，减去事件在 `DamageResult.damageReduction` 中累计的减伤并截到非负；
10. 执行 late pre-deal 与 `pre_take_damage_late`；
11. 若 flags 允许，再用 Block 吸收并得到 `healthDamage`；
12. 扣生命，记录事件，处理死亡，最后处理尖刺反伤。

证据见 `Backpack Battles/Core/Character.gd:495-653`，事件减伤的累加规则见 `Backpack Battles/Utility/DamageResult.gd:35-41`。因此旧的“所有其他机制后统一减伤”说法不成立；模拟器必须保留抗性、攻击固定减伤、事件减伤和 Block 的不同阶段。

攻击型物品的伤害区间还会先加实例 bonus 与 Empower，再叠加每个伤害类型的 factor，之后乘实例伤害倍率并取整/截零（`Backpack Battles/Items/Item.gd:3630-3690`）。暴击倍率在 `DamageResult.makeCritical()` 中应用，物品可覆盖暴击严重度（`Backpack Battles/Utility/DamageResult.gd:25-33`），不能把所有暴击硬编码成固定二倍。

### Buff、Debuff 与 Block

**源码确认**：源码将 Block 与七种 Buff（`Lucky`、`Regeneration`、`Vampirism`、`Spikes`、`Mana`、`Empower`、`Heat`）以及三种 Debuff（`Poison`、`Blind`、`Cold`）作为 stack 范围（`Backpack Battles/Core/Game.gd:413-456,4929-4947`；`Backpack Battles/Items/Item.gd:96-111`）。

通用 stack 容器区分永久层与有到期时间的临时层；Block 上限为 100000，其他 stack 上限为 10000。施加时按层处理概率抵抗/放大、Debuff 反弹、专用抵抗层和全局 Debuff 抵抗层；移除时另有净化保护/保护层（`Backpack Battles/Core/Buff.gd:23-41,71-196,199-240`）。因此“施加 N 层”不是一个不可分割的布尔动作。

当前通用公式中：

- Lucky 与 Blind 每层分别对准确率贡献 `+5` 与 `-5`（`Backpack Battles/Core/Character.gd:1349-1354`）；
- 默认每层 Empower 增加 1 点可强化武器伤害，但该每层系数是可变角色状态（`Backpack Battles/Core/Character.gd:1290-1300,1350-1351,1490-1491`）；
- Heat 与 Cold 通过上述 `±0.02` 的净速度项影响物品冷却推进（`Backpack Battles/Items/Item.gd:3725-3743`）；
- Block 只在伤害源含 `CanBeBlocked` 时吸收伤害（`Backpack Battles/Core/Character.gd:587-599`）；
- Spikes 与 Vampirism 还受伤害 flags 和近战/远程/效果上限约束（`Backpack Battles/Core/Character.gd:709-737`）。

**待运行验证**：若反编译文本出现明显可疑赋值或未传递参数，应先用运行轨迹确认，不应为“修正看起来像 bug 的源码”而自行改变语义。

### 疲惫

**源码确认 + 场景/资源确认**：疲惫常量 `FATIGUE_TIME = 17`。CombatTimer 启动时先把一次性 `FatigueStartTimer` 设为 `17 - 3 = 14` 秒；其 timeout 调用 `startFatigue()`，后者再把一次性 `FatigueTickTimer` 设为 3 秒，所以正常时间轴的首个疲惫伤害在战斗计时约 17 秒。随后每次伤害后把 tick timer 重启为 1 秒（`Backpack Battles/Interface/CombatTimer/CombatTimer.gd:3-21,114-120,145-179`；连接见 `Backpack Battles/Core/Main.tscn:9905-9911,14984-14985`）。

共享疲惫计数 `F` 从 0 开始，每跳先增长再造成伤害：

```text
combatTime < 60: F <- F + 1 + floor(0.1 * F)
combatTime >= 60: F <- F + 1 + floor(0.2 * F)
```

双方依次受到以该共享 `F` 为基础、再加各自 `bonusFatigueDamage` 且不低于 0 的伤害（`Backpack Battles/Interface/CombatTimer/CombatTimer.gd:153-178`；`Backpack Battles/Core/Character.gd:1591-1600`）。疲惫可被 Block，因为其 DamageSource flags 明确包含 `CanBeBlocked`。

`advanceTime()` 会直接缩短疲惫开始 timer；若越过零则立即进入 `startFatigue()`（`Backpack Battles/Interface/CombatTimer/CombatTimer.gd:184-196`）。模拟器必须同时保存真实战斗计时、时间推进量、共享疲惫计数与双方 bonus，不能只保存“是否已疲惫”。

### 激活、消耗与开始战斗效果

**源码确认**：`Item.activate()` 是激活事件的统一基础入口。非背包且战斗未结束时，它创建 Activation 事件、发出 `activated` signal 并增加激活计数；随后处理动画/声音（`Backpack Battles/Items/Item.gd:4669-4720`）。`consume()` 先调用 `activate(..., consume=true)`，再设置 `consumed = true`（`Backpack Battles/Items/Item.gd:4798-4800`）。Potion 还有独立的满/空状态和 `potion_triggered`/`potion_emptied` 信号（`Backpack Battles/Items/Potion.gd:31-94`）。

开始战斗钩子本身既不自动等于激活，也不自动等于消耗。某件物品是否在 `onPreCombatStart`/`onCombatStart`/`onPostCombatStart` 内调用 `activate()`、`consume()` 或只修改状态，必须逐个读取该物品脚本。旧文档中按物品名称制定的“一律不发激活通知”白名单已删除，因为它与统一入口和具体脚本控制流不一致。

当前已明确核对的开战物品中，Pocket Sand、Healing Herbs、Flame 和 Walrus Tusk 都在 `onCombatStart()` 施加效果后调用 `consume()`；由于 `consume()` 内部先调用 `activate()`，它们会产生激活事件。Whetstone 在开战修改相连武器后直接调用 `activate()`（`Backpack Battles/Items/PocketSand.gd:1-5`；`Backpack Battles/Items/HealingHerbs.gd:1-5`；`Backpack Battles/Items/Exclusive/Flame.gd:1-5`；`Backpack Battles/Items/WalrusTusk.gd:1-5`；`Backpack Battles/Items/Whetstone.gd:1-11`；统一入口见 `Backpack Battles/Items/Item.gd:4669-4720,4798-4800`）。这五项与根目录当前模拟器的实现存在已知冲突，应由源码一致性测试驱动修正。

**项目建模决定**：模拟器事件模型应区分 `cooldown_due`、`effect_attempted`、`activation_emitted`、`consumed` 与 `potion_emptied`。这些事件可能相邻发生，但不是同一个布尔量。

## 对手 run 数据与可见性

### 缓存来源与请求规模

**源码确认**：当前正式缓存路径是 `user://runs_steam.cache` 与 `user://runs_sw.cache`；Beta/Playtest 有各自子路径，旧 `user://runs.cache` 会在加载时删除（`Backpack Battles/Core/RunDatabase.gd:5-17,221-260`）。缓存文件用 Godot `store_var/get_var` 形式保存序列化 run 数组（`Backpack Battles/Core/RunDatabase.gd:245-300`）。

网络侧 SilentWolf 单次请求参数是 400 条，不是“源码确认固定缓存 2000 条”；Steam 与 SilentWolf 结果可合并，缓存的实际条数取决于返回结果与后续写入（`Backpack Battles/Core/RunDatabase.gd:126-147,184-215`）。当在线来源少于 30 条时才用本地缓存补充（`Backpack Battles/Core/RunDatabase.gd:54-66`）。

**待运行验证**：新解包不包含用户目录里的真实 `runs_steam.cache`/`runs_sw.cache` 样本。本仓库目前也没有匹配样本。因此条数分布、两个文件是否同时存在、实际版本混合情况和磁盘 Variant 布局必须从运行同一版本的 `user://` 目录采集后验证。

### run 与回合 schema

**源码确认**：一个序列化 run 有 10 个属性：`runId`、编码名字、rating、playerId、results、characterClass、rounds、entryVersion、chibiStyle、skins（`Backpack Battles/Utility/RunData.gd:4-16,34-70`）。版本早于 leaderboard breaking version 或晚于当前版本会被拒绝（`Backpack Battles/Utility/RunData.gd:74-80`）。

每个回合位流先保存基础最大生命与最大耐力，再顺序保存物品。物品 tuple 解码为：

- `d`：`ItemDescriptor`/物品索引；
- `c`：左上格坐标；
- `f`：四方向；
- `g`：可选宝石索引数组，空槽使用专用 sentinel；
- `pd`：可选的物品持久实例数据。

见 `Backpack Battles/Utility/RunData.gd:195-271`；写入对称流程见 `Backpack Battles/Core/RunDatabase.gd:571-607`。回合外再补 `class`、`loadout`、名字、chibi 与 skins（`Backpack Battles/Utility/RunData.gd:174-193`）。

对手加载时先按背包顺序排序，实例化每个 descriptor，按 `c/f` 定向并检查布局合法性，然后装入宝石与 `pd`；非法 run 会被丢弃/标记（`Backpack Battles/Core/Game.gd:2775-2825,2861-2895`）。

### 训练可见性边界

**源码确认**：被选中的当前对手回合数据用于构建战斗场景，因而战斗布局、职业、生命、耐力和已解码物品状态是环境内部真实状态。匹配池中的其他 runs、未来回合与排名筛选内部量不是当前战斗布局的一部分（选择流程见 `Backpack Battles/Core/RunDatabase.gd:311-354`）。

**项目建模决定**：布局策略的原始 observation 不泄露尚未选中的缓存池、未来对手回合或 matchmaker 分数。若任务定义为战前已显示对手布局，可暴露当前已选对手；若任务定义为纯己方摆盘，则对手输入只能是任务显式提供的条件。两种任务必须用不同环境配置和数据集元数据标识。

## 当前布局训练的观测

以下是**项目建模决定**，不是游戏 UI 原生接口。

每个 observation 至少包含：

```text
source_version: 游戏版本、schema 版本
character: class_id、loadout_id、基础生命/耐力（任务需要时）
board:
  addressable_cells: 9×7 坐标
  bag_cells: 当前背包扩出的动态可用格
  filled_cells: 普通物品当前占用格
  potential_bag_cells: 当前仍可扩展背包的格
  placable_cells / legal_action_mask: 针对当前实例与方向动态计算
instances[]:
  instance_id: episode 内唯一身份
  item_index / identifier: 静态物品身份
  owner / container
  top_left_cell
  face_direction
  collision_cells
  extension_cells
  affected_cells_primary
  affected_cells_secondary
  affected_cells_tertiary
  affected_cells_lightning
  affected_instance_ids_by_type
  sockets[]: 槽号、宝石 instance/item identity、方向、锁定/空槽
  pd: 可选、版本化的持久实例状态
  dynamic_instance_state: consumed、可见的可变参数等
opponent_current_round: 仅按任务可见性配置加入
```

其中 collision、extension 和四类 affected cells 应从场景与当前方向派生并保留，不能只编码成物品中心点。宝石既要挂到宿主槽位，也要保留宝石自身身份。对于重复物品，所有关系都引用 `instance_id`。

原始 observation 不包含胜率预测、布局评分、启发式价值、搜索排名或 evaluator 输出。这些量可以作为 reward、训练标签、critic 输入或诊断信息，但不能混入声称等价于游戏可见状态的张量。

若训练包含战斗时序，另需保存双方当前生命/耐力、全部 stack、眩晕/无敌、每件物品 `triggerTime`/`iterationCooldown`/speed、共享疲惫计数与双方 fatigue bonus，以及确定性回放所需 RNG 状态或随机事件流。

## 当前布局训练的动作

以下同样是**项目建模决定**。最小动作集合建议为：

- `place_or_move(instance_id, top_left_cell, face_direction)`；
- `rotate(instance_id, quarter_turns)`，可归一化到上一动作；
- `move_to_storage(instance_id)` / `move_from_storage(...)`，仅当任务包含储物箱；
- `socket_gem(gem_instance_id, host_instance_id, socket_index)`；
- `unsocket_gem(host_instance_id, socket_index)`；
- `stop`，结束本次布局。

每个动作必须通过当前动态合法性检查：普通物品校验 collision cells 是否完全落在可用 bag cells 且无碰撞；背包校验 extension cells 是否位于潜在空间；旋转后重新计算所有空间集合；镶嵌动作校验真实 socket 与 owner 状态。动作掩码应调用与 `Inventory.canAddItemOrBag()` 等价的规则，而不是只检查矩形边界。

动作序列不把“自动整理”“自动合成”“估值后选最佳位置”伪装成游戏原子动作。此类操作若用于搜索加速，应标记为规划器宏动作，并能展开成上面的合法原子动作。

## 当前非目标与历史草案归档

**项目建模决定**：当前只做给定物品集合下的布局与其战斗评估。以下内容归档为后续方向，本知识库不再为其维护可执行策略：

- 商店刷新、购买、出售、预留、折扣和金币策略；
- 配方发现、合成锁与商店内合成规划；
- 奖杯、皮肤、成就、解锁、天赋或其他局外成长；
- 排位运营和跨 run 长期策略。

相关源码仍可在需要时另建 SPEC 审计，但不得把旧 Wiki 商店概率或旧模拟器实现带入当前布局环境。

## Wiki 历史快照（降级参考）

**Wiki 参考**：旧知识库在 2026-07-03 至 2026-07-22 查询过 wiki.gg 的 Game Mechanics、Items、Characters、Recipe、Buff、Debuff、Cooldown、Effect 页面及 Cargo `Items`/`Recipes` 表。当时 Cargo 快照记录 `Items = 497`、`Recipes = 224`，并保存了职业、稀有度和主要类型计数。这些数据仍可用于术语翻译、人工对照与发现可能漏解的内容，但不是当前游戏事实，也不应用于生成运行时物品 ID、形状、数值或机制。

历史入口：

- https://backpackbattles.wiki.gg/wiki/Game_Mechanics
- https://backpackbattles.wiki.gg/wiki/Items
- https://backpackbattles.wiki.gg/wiki/Characters
- https://backpackbattles.wiki.gg/wiki/Recipe
- https://backpackbattles.wiki.gg/wiki/Buff
- https://backpackbattles.wiki.gg/wiki/Debuff
- https://backpackbattles.wiki.gg/wiki/Cooldown
- https://backpackbattles.wiki.gg/wiki/Effect

旧快照中的 `class`、`rarity`、`itemtype`、`icontype`、`effect` 等 Cargo 字段可作为数据核对提示，但静态游戏数据应从 `ItemData_e.csv` 的正式加载逻辑、`ItemDescriptor` 和具体场景/脚本重建。旧 Wiki 对“63 格”“战斗开始激活”“疲惫公式”“固定二倍暴击”等概括均不得覆盖本文件前述源码证据。

## 待运行验证清单

- 获取与游戏版本 1.1.8 匹配的真实 `runs_steam.cache` 与 `runs_sw.cache`，记录文件数量、run 数量、版本分布及 `pd` 实例；
- 用 Godot 3.6.0 轨迹固定战斗时间零点、Character 首 tick、疲惫 14/17/60 秒边界；
- 对相同 trigger priority 的物品、双方同帧 Timer、signal 嵌套回调做顺序回放；
- 对所有实现 `getDataPersistent()` 的物品建立 `pd` 位宽与字段解码表；
- 用场景解析器回归 collision、extension、四类 affected cells、动态 affected 与宝石槽；
- 对疑似反编译异常只做运行对照，不在无证据时“修正”游戏逻辑。
