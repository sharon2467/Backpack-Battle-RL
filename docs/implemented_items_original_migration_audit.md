# 已实现物品向原版实现迁移的评估

日期：2026-10-09。状态：审查完成，未修改生产代码。本轮是迁移评估，后续实施须据此编写具体 SPEC。

后续进度（2026-10-10）：第一批状态准备时机迁移已完成，见 [实施 SPEC](item_state_preparation_timing_spec.md)。下文保留2026-10-09审查时的实现快照；其中对应的延迟准备与老鼠加速时机差异已修正。通用加速 Trigger 的重复条件计数也已由用户独立调整，本批保留该修改。

## 1. 范围与结论

覆盖 `DEFAULT_ITEM_FACTORIES` 中全部 **19 种**物品，比较当前 Python 实现、权威解包的脚本及其父类/场景，并检查现有基础设施是否足以支持迁移。不把目录中只有形状、没有默认工厂的物品计入已实现物品。

结论：可以逐步迁移，而且多数无需新增基础设施。优先迁移准备状态、开战加成和一次性效果收尾，再整理冷却效果与武器攻击的公共流程。五种纯开局物品已经完成这类迁移，应保留。

本轮审查控制流、状态归属与事件顺序；未重新解密物品表、逐项证明所有硬编码数值与静态数据均正确。原版运行时的同帧顺序及随机轨迹也未实测。代码形状接近不等于已经完全复刻。

## 2. 已有基础设施与边界

| 能力 | 当前状态 | 对迁移的意义 |
| --- | --- | --- |
| prepare → 全体 pre → 全体 start → 全体 post | 已实现；宝石先于宿主，各阶段有自身 context | 能把一次性缓存与开战修改放回原版对应阶段 |
| 同步事件总线、双方实例身份隔离 | 已实现；上下文转发保留事件对象 | 麻绳、黏黏、扫帚、木盾无需回到逐帧扫描 |
| 攻击 early/late、character_attacked、attacked、onDealtDamage | 已实现 | 能保留石头破甲、盾牌收尾、扫帚命中与闪避效果的阶段 |
| consume 与单帧激活限制 | 已实现；consume 先发激活再设 consumed | 一次性物品已有消耗身份，但还缺通用停止冷却入口 |
| 物品独立 chance_rng | 已实现；Rat 的两次概率共用该物品状态 | 不应改回直接调用 random；原版 prepare 也会 reset 初始偏置 |
| 冷却 Trigger | 已有速度、进度和一次性 Trigger | 足以继续作为调度；尚未完整复刻每轮随机间隔、停止状态、眩晕等 |
| 治疗公共入口 | 已有 healing_efficiency、过量治疗事件和反治疗 | 治疗物品继续复用，无需直接改 health |
| Buff/Debuff Effect | 多数仍直接修改计数并记录日志 | 尚不能完整承载原版 give/use/remove 的层数限制、抵抗、反射和事件链 |

总线的一个具体限制：当前 `connect(emitter, signalName, listener: tuple[BattleItem, int])` 最终调用 `activate_item(context, trigger_index)`；原版 `connectForCombat` 连接到方法名。因此可以保留 Trigger 作为事件分发入口，把业务委托给物品方法；暂时不能原样照搬 `connectForCombat(..., "onAttacked")`。

## 3. 全部物品逐项结论

源码路径均相对 `Backpack Battles/Items/`；当前实现均在 `item_factory_registry_v1.py`。

| 物品 / 当前类 | 原版位置与核心流程 | 当前情况与建议 |
| --- | --- | --- |
| 口袋沙 `PocketSand` | `PocketSand.gd:3`，onCombatStart → inflictBlind → consume | 已对齐阶段、激活和消耗顺序；保留 |
| 治疗草药 `HealingHerbs` | `HealingHerbs.gd:3`，onCombatStart → giveRegeneration → consume | 已对齐主流程；完整层数事件仍依赖公共 Effect 能力 |
| 火焰 `Flame` | `Exclusive/Flame.gd:3`，onCombatStart → giveHeat → consume | 已对齐主流程；保留 |
| 海象尖牙 `WalrusTusk` | `WalrusTusk.gd:3`，onCombatStart → giveSpikes → consume | 已对齐主流程；保留 |
| 磨刀石 `Whetstone` | `Whetstone.gd:5–11`，筛选 canBeEmpowered；开战 addBonusDamage → activate | 已对齐阶段；以后把直接扫描目标 AttackEffect 改为物品的 addBonusDamage 接口，统一伤害加成归属。现有范围内不必为它单独改架构 |
| 闪亮贝壳 `ShinyShell` | `Exclusive/ShinyShell.gd:6`，doCooldownEffect → heal → onAfterEffectFinished | 当前 AfterTimeTrigger 保证只触发一次，但未 consume、未停止调度。应补齐一次性收尾，治疗仍走现有公共入口；不能改成不受速度影响的裸 time 判断 |
| 平衡魔棒 `WandOfEquilibrium` | `Exclusive/Wand.gd:11`，giveLeastBuffs → 达阈值时 removeMostBuffs(use=true) → giveEmpower → activate | 随机并列选择已补齐；可将 run_effect 的业务移到 doCooldownEffect，继续保留现有资源 Effect。多个资源阈值是否均为10，需从物品表另行核对，不能仅凭脚本认定 |
| 魔法入门 `MagicForDummies` | `Exclusive/BookofBasics.gd:10,18`，onPrepare 计算法术权重；冷却时可选消耗 Mana 并给生命上限，最后总是 activate | 现有权重在首次有蓝触发时才计算；直接移到 onPrepare，缺蓝仍激活的已修行为必须保留 |
| 麻绳 `Twine` | `Exclusive/Twine.gd:5–23`，准备时订阅主 affected；回调按副 affected 中立物品数量计算概率 | 已有两类 marker、事件和独立 RNG；可在 onPrepare 准备中立计数，将业务命名为 onTriggerItemActivated。固定布局下主要改善状态就绪时间；源代码本身在回调中查询已缓存的 affected 数量 |
| 黏黏 `Goobling` | 场景 `Exclusive/Goobling.tscn:5` 使用 `Goobert.gd`；prepare 订阅，累计达到阈值时 doCooldownEffect → activate | 当前 SlimeActivationTrigger 的计数与重置主流程可保留；可将治疗拆成 doCooldownEffect。以后接双重激活时，第二次效果不能再经过一次计数门槛 |
| 木盾 `WoodenBuckler` | `Shield.gd:6–36` + `WoodenBuckler.gd:3`；pre_take_damage 保存结果并减伤，匹配 character_attacked 时扣体力、activate、blocked、清引用 | 当前双 Trigger 已对齐关键阶段；可委托给 preTakeDamage/onCharacterAttacked/afterBlock，保留事件 identity。原版自身监听早于宝石准备，当前晚于宝石，详见下方；只有一类盾牌时，不必新增 Shield 类 |
| 扫帚 `Broom` | `Broom.gd:10,13,21,28`；订阅角色未命中事件，积攒伤害；attack 后清理；onDealtDamage 命中才掷致盲概率 | 主要顺序已对齐；把当前 run_effect 的两条分支拆成 onAttacked 与攻击收尾。清理必须在攻击与 activated 同步连锁完成后，不得提前清零；无体力不清理 |
| 木剑 `WoodenSword` | `WoodenSword.gd:6`；足够体力才 dealDamage → activate | 当前正确重复了公共流程；适合与 Weapon 攻击入口共用。原版木剑虽 extends Item，行为上仍可复用现有 Python Weapon |
| 短弓 `Shortbow` | `Exclusive/Shortbow.tscn:5` 直接使用 `Weapon.gd` | 当前重复体力/攻击/激活流程；可直接继承公共 Weapon 冷却攻击逻辑，保留 ranged 类型 |
| 石头 `Stone` | `Stone.gd:16–35`；late 阶段破甲；ammunition 控制发射，最后一发停止冷却并 consume | 破甲阶段已修正；当前用 AfterTimeTrigger 代替弹药且不 consume。应恢复最小 ammunition=1 和末次收尾，不实现尚无工厂的一袋石头及其无限弹药机制 |
| 香蕉 `Banana` | `Food.gd:4–9` + `Banana.gd:3`；prepare 加其他种食物提供的速度；冷却 heal → giveStamina → activate | 业务顺序已对齐；FoodCooldownTrigger 的加速目前在 pre 阶段初始化，可提前到 prepare。两种食物可先复用现有 Trigger，不必立即增加 Food 父类 |
| 大蒜 `Garlic` | `Food.gd:4–9` + `Garlic.gd:6`；冷却给护甲，概率移除 Vampirism，activate | 业务与共享 chance_rng 已较接近；准备阶段迁移同香蕉。原版 extraBlock/addBonusBlock 当前缺失，现有19种物品没有提供该加成的联动，不必为本批增加未使用接口 |
| 平底锅 `Pan` | `Pan.gd:8`，onPreCombatStart 按食物数 addBonusDamage；攻击继承 Weapon | 当前在 AttackEffect 首次 apply 才准备伤害。应直接移到 onPreCombatStart，并避免首次攻击再次加成；攻击流程可复用 Weapon |
| 老鼠 `Rat` | `Exclusive/ForestFriend.gd:6` + `Exclusive/Rat.gd:17`；combatStart 按 Pet 或 Food 加速；冷却伤害 → 两次概率 → activate | 现有加速放在 pre；可在 onCombatStart 按唯一目标计数并给普通 CooldownTrigger 加速。当前两个独立过滤条件会把同时属于 Pet 和 Food 的实例计数两次，原版 OR 只计一次；当前19种物品没有此双类型，但迁移应避免保留这个差异 |

映射依据：BookofBasics 场景直接引用 MagicForDummies 贴图；Goobling 和 Shortbow 的脚本归属由场景明确给出。平衡魔棒按当前已实现机制对照 `Exclusive/Wand.gd`，其内部文件名与 Python 类名不同。

准备顺序还有一处需单独对齐：`Shield.prepare` 先连接自己的两种角色事件，再调用基类 prepare，随后才准备槽内宝石；当前 BattleItem.prepare 统一先准备宝石，再连接宿主 Trigger。现有具体宝石尚未实现，因此不能把这项称为已经发生的宝石效果错误，但将来盾牌与 Armor 宝石订阅同一角色事件时，会改变回调先后。Goobert 也在调用基类 prepare 前订阅，不过当前 Goobling 没有槽位。后续单项 SPEC 应明确这些 prepare 覆盖的顺序，不应把所有原版 prepare 都机械改成 onPrepare。

## 4. 运行复现的差异

使用用户指定的 Python 3.11 解释器，内存构造有效双方布局后调用 prepare/start/run：

| 场景 | 当前实测 | 原版应有状态 |
| --- | --- | --- |
| 平底锅关联1个香蕉，完成 start_combat | damage_modifier=0，qualifying_food_count=None | pre 阶段已完成食物伤害加成 |
| 魔法入门关联1个普通 Spell，完成 prepareItems | spell_weight=None，生命上限 Effect.amount=8 | prepare 已得到权重1；冷却阶段无需再扫描布局 |
| 贝壳运行7秒 | 激活1次，consumed=False，仍在 active_items | onAfterEffectFinished 停止冷却并 consume |
| 石头运行7秒 | 激活1次，consumed=False，仍在 active_items | ammunition 归零，停止冷却，consume；总激活仍为1次 |

这些是控制流与状态的直接复现，不是 Godot 运行对照。普通场景的最终血量可能暂时相同，不能据此认为状态与时机已经相同。

## 5. 建议如何迁移

### 第一批：使用现有生命周期纠正状态时机

无需更改事件总线、伤害管线或新增物品父类。拟修改接口及核心伪代码：

| 接口 | 伪代码 / 注意事项 |
| --- | --- |
| `Pan.onPreCombatStart(self, context: BattleContext) -> None` | 调用现有攻击 Effect.prepare_damage_modifier(context)，标记 damage_modifier_prepared=True；首次攻击不能再重复加成。不要用“已执行过pre”的新标记阻止未来显式开局重放 |
| `MagicForDummies.onPrepare(self, context: BattleContext) -> None` | 调用 _prepare_spell_weight(context)；run_effect 中移除延迟计算，保留缺蓝也激活 |
| `Twine.onPrepare(self, context: BattleContext) -> None` | 调用 _prepare_neutral_item_count(context)；既有 Trigger 仍负责订阅，run_effect 不再首次扫描 |
| `Banana.onPrepare(self, context: BattleContext) -> None`、`Garlic.onPrepare(self, context: BattleContext) -> None` | 调用已有 FoodCooldownTrigger.prepare_speed_modifiers；置 speed_modifiers_prepared=True，使 pre 初始化冷却时不重复累加；同种食物仍不计数 |
| `Rat.onCombatStart(self, context: BattleContext) -> None` | 对主 marker 目标按 Pet OR Food 筛选，每个实例计1次；向普通 CooldownTrigger 累加 count × 0.15；构造函数改用普通 CooldownTrigger，移除原 ItemAcceleratedCooldownTrigger，防止 pre 和 start 各加一次 |

这里的时机变化应当作为明确的行为迁移验收，而不是要求所有旧的“首次触发前还是 None”断言保持不变。

### 第二批：补一次性效果的通用收尾

建议增加少量明确状态，而非用一次性 Trigger 替代物品语义：

- 一个冷却启停标志及明确的停止方法；关闭后不再推进冷却或调用冷却业务。可以先让现有 Trigger 检查标志，不强求立即从 active_items 物理删除。
- `BattleItem.onAfterEffectFinished(self, context: BattleContext, consume: bool = True) -> None`：停止自身冷却；consume 为真时调用现有 self.consume(context)。
- 贝壳：治疗后 onAfterEffectFinished(context)，不要再单独 emit_activation，否则会与 consume 的激活重复。
- 石头：ammunition 默认1；每次合法发射先减1，再攻击；最后一发 onAfterEffectFinished(context, False) → consume(context)，其余发射 activate。保持现有 late 破甲钩子。

冷却标志究竟放在 Trigger 还是物品上，以及对应启停函数的完整接口，留给实施 SPEC 决定；本评估不新增两套并行冷却状态。

### 第三批：让物品代码更接近原版业务函数

建议保留现有 Trigger/Effect，只收拢公共流程：

1. 将11种轮询物品的冷却业务提取到 `doCooldownEffect(self, context: BattleContext) -> None`；run_effect 仅在相应 Trigger 成功时调用它。扫帚还有受击分支，不能把整个 run_effect 直接重命名。
2. 给 Weapon 收拢“体力足够 → attack → 激活”，`attack(self, context: BattleContext) -> None` 完成攻击及激活；木剑、短弓、平底锅使用它，扫帚覆盖攻击后清理。石头仍有自己的弹药业务，不强行塞进同一模板。
3. 给扫帚、木盾、麻绳提取源码对应的命名回调，现有 Trigger 只判断事件并转调业务函数。不为本批增加 callable/方法名混合监听协议。
4. 如果随后确实需要统一可修改武器伤害，再增加小的 addBonusDamage/reduceBonusDamage 入口，磨刀石、平底锅、扫帚改为调用它，避免每个物品依赖别人的 effects 下标。不要同时长期保留物品 bonus 和 Effect.damage_modifier 两份数值来源。

这批主要减少重复与索引耦合；只更换函数名本身不会提高机制准确度，应排在时机与收尾修正之后。

## 6. 单独处理的基础设施差异

以下影响多个物品，不能靠逐个迁移 run_effect 消除：

- **速度限幅位置**：`CooldownTrigger.update` 先把 Heat/Cold 项限制到[-10,10]，转换后没有最终限幅；原版 `Item.gd:3725` 对最终速度限制到[0.1,10]。高 Heat/Cold 时存在实际差异。
- **每轮冷却随机扰动**：原版 `Item.gd:3788,4409` 开局及每次 trigger 都重新计算 iterationCooldown；当前始终使用固定 cooldown_seconds。原版某些对手条件还有不同区间，后续设计需明确采用的战斗规则，不能偷偷假设一个区间覆盖所有模式。
- **暂停、推进与双重激活**：现有 infra 没有完整的眩晕暂停、advanceCooldown、doubleActivationChance 等能力。默认无这些状态的19种物品可先迁移，不能宣称所有外部修饰均支持。
- **受影响物品过滤**：当前 initializer 主要建立几何 marker 关系，业务自行筛选；原版先按 canAffect/secondary 筛选并缓存。应按各物品明确的规则使用主/副 marker，避免以 linked_items 的并集代替所有原版 affected。暂不为19种物品增加通用规则引擎。
- **Buff 与事件因果**：当前多个 Effect 直接写整数，未完整复刻原版 stack 限制、抵抗、反射、获得/消耗事件。现有 context 解决了总线参数传递，不代表这些业务事件已存在。
- **数据与 RNG 等价性**：基础物品数值还需物品表校订；Python 与 Godot 的随机流不能仅凭同一 seed 视为相同。当前独立 BalancedRng 与原版 prepare/reset 的方向一致，应保留。

## 7. 后续验收重点

1. prepare/pre/start 完成时状态就绪：法术权重、食物速度、平底锅伤害、老鼠速度分别在正确阶段出现，首个冷却效果不再改变这些布局缓存。
2. 贝壳和石头最终 consumed=True；收尾后的冷却不推进、不再触发，每次效果只有一次激活；石头未命中也消耗弹药。
3. 扫帚没有体力时不清除临时伤害；有体力攻击后，在同步 activated 连锁结束后才清除；命中致盲仍在 onDealtDamage。
4. 木盾减伤、扣体力、激活、blocked 的顺序与事件 identity 保持；石头破甲仍发生在伤害提交前。
5. 老鼠双类型目标只计一次，概率顺序仍为伤害 → Poison → Blind → 激活；麻绳和黏黏能正确接收到开局和消耗激活。
6. 五种开局物品不退回 frame==0 扫描；镶嵌宝石不进入全局生命周期或普通冷却轮询。
7. 回归测试覆盖最终结果与中间事件顺序；后续基础设施改动另设验收，不以既有测试通过证明 Godot 等价。
