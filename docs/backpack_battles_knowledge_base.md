# 《背包乱斗》强化学习规划知识库

数据最后更新：2026-07-09

中文翻译校订：2026-07-21

资料来源政策：环境设计所依据的游戏事实只能来自当前的 `backpackbattles.wiki.gg` 社区 Wiki 及其 MediaWiki/Cargo API。

术语说明：中文游戏术语优先采用中文 Wiki 的现有译名；Cargo 字段、枚举值、代码标识符及动作名保留英文原值，以免与数据接口不一致。本次术语校对参考了中文 Wiki 的[物品](https://backpackbattles.wiki.gg/zh/wiki/物品)、[稀有度](https://backpackbattles.wiki.gg/zh/wiki/稀有度)、[增益效果](https://backpackbattles.wiki.gg/zh/wiki/增益效果)、[减益效果](https://backpackbattles.wiki.gg/zh/wiki/减益效果)和[子职业](https://backpackbattles.wiki.gg/zh/wiki/子职业)页面，查询日期为 2026-07-21。

## 资料来源索引

| 页面 / API 数据 | URL | 最近核对的 Wiki 修订日期 | 用途 |
| --- | --- | --- | --- |
| 游戏机制（Game Mechanics） | https://backpackbattles.wiki.gg/wiki/Game_Mechanics | 2026-02-18 | 物品栏、商店、稀有度概率、战斗概念、排位概览 |
| 物品（Items） | https://backpackbattles.wiki.gg/wiki/Items | 2026-05-09 | 物品分类、特卖/出售规则、物品数据库入口 |
| 角色（Characters） | https://backpackbattles.wiki.gg/wiki/Characters | 2026-04-28 | 当前可玩职业及商店管理员/储物箱相关事实 |
| 合成配方（Recipe） | https://backpackbattles.wiki.gg/wiki/Recipe | 2025-10-24 | 合成规则及配方数据库入口 |
| 增益效果（Buff） | https://backpackbattles.wiki.gg/wiki/Buff | 2024-03-28 | 增益效果定义 |
| 减益效果（Debuff） | https://backpackbattles.wiki.gg/wiki/Debuff | 2024-03-28 | 减益效果定义 |
| 冷却（Cooldown） | https://backpackbattles.wiki.gg/wiki/Cooldown | 查询于 2026-07-22 | 冷却加速/减速的组合公式 |
| 效果（Effect） | https://backpackbattles.wiki.gg/wiki/Effect | 2024-11-08 | 效果伤害概念 |
| Cargo `Items` 表 | `api.php?action=cargoquery&tables=Items` | 查询于 2026-07-09 | 结构化物品字段、数量及分类枚举 |
| Cargo `Recipes` 表 | `api.php?action=cargoquery&tables=Recipes` | 查询于 2026-07-03 | 结构化配方字段及数量 |

## 当前数据快照

wiki.gg 的结构化 Cargo 数据当前提供：

- `Items`：497 条记录。
- `Recipes`：224 条记录。

按标准化物品职业统计的物品数量：

Cargo 的 `class` 字段可能包含以逗号分隔的多个值。为了建模，Cargo 中空的 `class` 值统一标准化为 `Neutral`。

| 职业枚举值 | 标准化后的数量 |
| --- | ---: |
| `Adventurer`（冒险家） | 29 |
| `Berserker`（狂战士） | 39 |
| `Engineer`（工程师） | 43 |
| `Mage`（魔法师） | 56 |
| `Neutral`（通用） | 219 |
| `Pyromancer`（火焰魔导士） | 39 |
| `Ranger`（游侠） | 38 |
| `Reaper`（收割者） | 43 |

按有效稀有度统计的物品数量：

| 稀有度枚举值 | 数量 |
| --- | ---: |
| `Common`（普通） | 27 |
| `Rare`（罕见） | 62 |
| `Epic`（史诗） | 68 |
| `Legendary`（传说） | 91 |
| `Godly`（神级） | 96 |
| `Unique`（特别） | 148 |

Cargo 当前有 5 行的原始稀有度字段为 `Varies`（不定）；它不是有效的模型稀有度。导入代码应在实例化前将这些行解析为具体稀有度；在完成解析前，也可以拒绝将这些行用于战斗/商店模拟。

按主要物品类型统计的物品数量：

| 类型枚举值 | 数量 |
| --- | ---: |
| `Accessory`（配饰） | 117 |
| `Armor`（护甲） | 14 |
| `Bag`（背包） | 27 |
| `Book`（魔法书） | 5 |
| `Chess Piece`（棋子） | 12 |
| `Food`（食物） | 20 |
| `Gemstone`（宝石） | 14 |
| `Gloves`（手套） | 4 |
| `Helmet`（头盔） | 9 |
| `Pet`（宠物） | 79 |
| `Playing Card`（卡牌） | 8 |
| `Potion`（魔药） | 18 |
| `Shield`（盾牌） | 10 |
| `Shoes`（鞋子） | 5 |
| `Skill`（技能） | 58 |
| `Spell`（魔法卷轴） | 11 |
| `Weapon`（武器） | 111 |

标准化的图标类型值如下：

| 图标类型枚举值 | 拆分后的数量 |
| --- | ---: |
| `dark`（黑暗） | 41 |
| `effect`（效果） | 21 |
| `fire`（火） | 35 |
| `holy`（神圣） | 51 |
| `ice`（冰） | 20 |
| `magic`（魔法属性） | 82 |
| `melee`（近战） | 67 |
| `musical`（乐器） | 7 |
| `nature`（自然） | 84 |
| `ranged`（远程） | 41 |
| `treasure`（宝藏） | 34 |
| `vampiric`（吸血属性） | 28 |

Cargo 当前有 193 行的原始 `icontype` 字段为空。建模时应将其表示为空的图标类型元组/列表，而不是单独设立一个图标枚举值。

已知对建模有用的 Cargo 物品字段包括：

- `name`
- `class`
- `rarity`
- `cost`
- `itemtype`
- `icontype`
- `tags`
- `effect`

## 物品分类标准化

物品分类字段应使用面向模型的标准化值，而不是原始 Cargo 字符串。

推荐的物品元数据字段：

```python
item_metadata = {
    "display_name": str,
    "item_classes": tuple[str, ...],
    "rarity": str,
    "cost": int,
    "item_types": tuple[str, ...],
    "icon_types": tuple[str, ...],
}
```

标准化规则：

- `class`：按逗号拆分并去除空白。若 Cargo 原始字段为空，则使用 `("Neutral",)`。有效的物品职业值为 `Adventurer`、`Berserker`、`Engineer`、`Mage`、`Neutral`、`Pyromancer`、`Ranger` 和 `Reaper`。
- `rarity`：使用一个明确的稀有度。有效值为 `Common`、`Rare`、`Epic`、`Legendary`、`Godly` 和 `Unique`。`Varies` 只是原始数据中的占位值，不是有效的运行时稀有度。
- `itemtype`：按逗号拆分并去除空白。有效值为 `Accessory`、`Armor`、`Bag`、`Book`、`Chess Piece`、`Food`、`Gemstone`、`Gloves`、`Helmet`、`Pet`、`Playing Card`、`Potion`、`Shield`、`Shoes`、`Skill`、`Spell` 和 `Weapon`。
- `icontype`：按逗号拆分并去除空白。若原始字段为空，则使用空元组/列表。有效的非空值为 `dark`、`effect`、`fire`、`holy`、`ice`、`magic`、`melee`、`musical`、`nature`、`ranged`、`treasure` 和 `vampiric`。

建模含义：

- `BattleItem` 应为所有物品提供通用元数据字段，包括 `display_name`、`item_classes`、`rarity`、`cost`、`item_types` 和 `icon_types`。
- 由于 Cargo 可能编码多个值，职业、物品类型和图标类型应使用元组/列表字段表示。
- 玩家可见观测应将物品职业/类型/图标元数据编码为 multi-hot，或使用由多个 ID 组成的列表，而不是单个标量 ID。

待处理的数据问题：确认物品形状/网格、镶嵌位、星标/菱形标记位置、冷却、伤害、耐力及其他数值字段是否可通过模板/Cargo 表获取，还是必须从各个物品页面解析。

## 可玩职业

wiki.gg 的 `Characters` 页面列出了以下可玩职业：

- 游侠（`Ranger`）
- 收割者（`Reaper`）
- 火焰魔导士（`Pyromancer`）
- 狂战士（`Berserker`）
- 魔法师（`Mage`）
- 冒险家（`Adventurer`）
- 工程师（`Engineer`）

根据 `Characters` 和 `Game Mechanics` 页面，所有职业的初始生命值、初始金币和每回合金币安排均相同。

各职业页面表明，职业身份会影响策略、物品可用性、初始背包选择和职业专属机制。对于强化学习状态设计，除非环境被简化为无职业的玩具版本，否则应把 `class_id` 视为非冗余信息。

## 物品栏机制

wiki.gg 当前记录的机制：

- 每个职业开局只解锁全部物品栏格子中的一部分。
- 一共有 63 个格子。
- 根据职业/配置不同，开局可用格子数为 12 到 14 个。
- 物品栏格子可以重新排列和旋转。
- 皮包（Leather Bag）、腰包（Fanny Pack）、耐力包（Stamina Sack）、魔药腰带（Potion Belt）和守护钱包（Protective Purse）等背包物品可以解锁更多可用格子。
- 放在储物箱中的物品不会产生战斗效果；只有放入活动物品栏后才会生效。
- 物品具有格子形状和空间协同关系。
- 部分物品效果会根据附近物品或受影响物品，使用星标和菱形标记进行判定。

强化学习含义：
- 计划分为给定物品最优化背包摆盘模型和商店运营购买物品模型。
- 只有持有物品的纯列表并不够。
- 只有纯网格也不够，除非它还能保留物品身份和实例级状态。
- 观测应同时编码对象实例和空间占用。
- 储物箱和活动物品栏应分开表示。

## 商店机制

wiki.gg 当前记录的机制：

- 玩家开局拥有 12 金币和 25 点生命值。
- 商店陈列五件物品。
- 战斗开始前，玩家可以购买商店物品，并将其放入物品栏或储物箱。
- 物品可以半价卖给小板栗，出售价格向上取整。
- 一件商店物品的基础打折概率为 10%，打折价格为原价的一半并向上取整。
- 打折价等于出售价格，因此买入打折物品再将其卖出不会损失金币。
- 商店可以刷新，且每回合结束进入商店时都会展示新的物品而非上回合留下的物品。
- 每回合前四次刷新各花费 1 金币，之后每次花费 2 金币。
- 右键点击商店物品可以将其预留，使它不会被刷新替换，也不会在进入下一回合时被替换。
- `Unique`（中文 Wiki：特别）物品从第 4 回合起可以出现。
- 进入商店时，`Unique` 物品的基础出现概率为 2%；刷新商店时不会触发此概率。
- 玩家同一时间只能拥有一件 `Unique` 物品，除非拥有其他增加Unique物品数量的特殊道具。
- 第 8 回合解锁子职业。

进入商店时获得的金币：

| 回合 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12-18 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 金币 | 12 | 9 | 9 | 9 | 10 | 10 | 11 | 21 | 12 | 12 | 13 | 后续回合为 13-15 |

页面给出的后期回合确切金币数：

| 回合 | 12 | 13 | 14 | 15 | 16 | 17 | 18 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 金币 | 13 | 14 | 14 | 15 | 15 | 15 | 15 |

页面给出的初始生命值/各回合生命值：

| 回合 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 生命值 | 25 | 35 | 45 | 55 | 70 | 85 | 100 | 115 | 130 | 150 | 170 | 190 | 210 | 230 | 260 | 290 | 320 | 350 |

各回合的商店稀有度概率：

| 稀有度 | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | R9 | R10 | R11 | R12-18 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 普通（`Common`） | 90 | 84 | 75 | 64 | 45 | 29 | 20 | 20 | 20 | 20 | 20 | 20 |
| 罕见（`Rare`） | 10 | 15 | 20 | 25 | 35 | 40 | 35 | 30 | 28 | 25 | 23 | 20 |
| 史诗（`Epic`） | 0 | 1 | 5 | 10 | 15 | 20 | 25 | 25 | 25 | 25 | 23 | 20 |
| 传说（`Legendary`） | 0 | 0 | 0 | 1 | 5 | 10 | 15 | 15 | 15 | 15 | 17 | 20 |
| 神级（`Godly`） | 0 | 0 | 0 | 0 | 0 | 1 | 5 | 10 | 12 | 15 | 17 | 20 |

强化学习含义：

- 金币、刷新次数/费用、预留状态、打折状态和回合数都是必需的状态变量。
- 商店生成器必须知道随回合变化的稀有度概率。
- 是否已拥有 `Unique` 物品属于环境状态，因为它会影响后续商店生成。
- 子职业物品可能影响商店中的物品可用性或出现概率，因此商店生成器必须检查已拥有的特殊物品及其效果。

## 配方机制

wiki.gg 当前记录的机制：

- 在背包中相邻摆放的配方组件会在下一个商店阶段合成。
- 右键点击物品可以锁定它，阻止其参与合成。
- 有些配方使用催化剂。催化剂会保留，其他材料则被消耗并生成结果物品。
- 游戏内的配方书会记录已经发现的配方。
- 结构化 `Recipes` 表当前有 224 条记录。

已知的结构化配方字段包括：

- `recipename`
- `ingredients`
- `catalysts`

强化学习含义：

- 合成机会可以根据物品身份、相邻关系和合成锁定状态推导出来。
- 为提高训练效率，派生出 `available_recipe_mask` 会很有帮助。
- 环境必须实现催化剂保留规则。
- 动作模型需要 `toggle_combine_lock`。

## 战斗机制

wiki.gg 当前记录的战斗概念：

- 命中率决定攻击是命中还是未命中。
- 冷却是物品两次激活之间的时间间隔。
- 暴击造成双倍伤害。
- 许多物品的位置效果由星标和菱形标记决定。
- 通常，一件物品只能填充另一件物品的一个星标和一个菱形标记。
- 除非物品另有说明，增益效果和减益效果可以叠加，并且通常持续到战斗结束。
- 夜幕降临后开始产生疲惫，对双方造成逐渐增强的伤害。

wiki.gg 列出的增益效果：

| 增益效果 | 建模效果 |
| --- | --- |
| 充能（`Empower`） | 每层增加1点武器伤害 |
| 狂热（`Heat`） | 每层加快物品触发速度2% |
| 幸运（`Luck`） | 每层提高命中率5% |
| 魔法（`Mana`） | 魔法属性物品使用的资源 |
| 恢复（`Regeneration`） | 每层2s恢复1点生命值 |
| 尖刺（`Spikes`） | 对近战攻击者造成伤害，伤害量为min(Spikes,final_damage) |
| 吸血（`Vampirism`） | 近战命中时恢复生命值，恢复量为min(Vampirism,final_damage)|

wiki.gg 列出的减益效果：

| 减益效果 | 建模效果 |
| --- | --- |
| 致盲（`Blind`） | 每层降低5%命中率 |
| 冰冷（`Cold`） | 每层增加物品冷却时间2% |
| 中毒（`Poison`） | 每层2s造成一点伤害 |

wiki.gg 列出的其他战斗概念：
- 减伤/增伤：受到的伤害减少/增加某百分比或某数值，在其他机制结算完后结算。
- 狂战士之怒（`Battle Rage`）：狂战士职业物品特有机制，满足特定条件后进入一段时间的强化状态。
- 护盾（`Block`）：每层抵挡一点伤害。
- 治疗（`Heal`）：某些物品提供的直接治疗，注意恢复是Buff，治疗是其效果。
- 疲惫（`Fatigue`）：战斗开始一段时间后双方每秒受到逐渐递增的疲惫伤害。F[i]=F[i-1]+floor(F[i-1]/10)+1
- 无敌（`Invulnerability`）：一段时间内受到的所有伤害变为0，注意仍视为受到伤害。
- 眩晕（`Stun`）：一段时间内所有具有冷却的物品暂停冷却。
- 复活（`Reincarnate`）：生命值归0，比赛即将失败时恢复部分生命值并继续战斗。

- 复制增益效果(`Duplicate buff`)：尝试获得增益效果时，若通过复制检定，则此次获得两层增益。
- 无效化（`Nullify`）：即将获得来自任何来源的增益效果时，若通过无效化检定，则此次不获得增益。
- 移除(`Remove buff`)：某些物品触发时能够减少对手特定增益的层数。
- 阻止移除(`Protect buff from removal`)：在触发移除时，概率使得移除失败。
- 偷取增益(`Buff steal`)：某些物品触发时能够移除对手增益并对自己施加相同增益。视为移除和施加两个独立动作。

- 复制减益效果(`Duplicate debuff`)：对对手施加减益效果时，若通过复制检定，则此次施加两层减益。
- 抵抗（`Resist`）：即将受到来自任何来源的减益效果时，若触发抵抗，则此次不受到减益。
- 净化（`Cleansing`）:某些物品触发时能够减少自身特定减益的层数。
- 阻止净化（`Protect debuff from cleansed`）:在触发净化时，概率使得净化失败。
- 反弹（`Reflect`）：即将受到来自任何来源的减益效果时，改为对对手施加该效果，且不可再次反弹。视为一个特殊动作。

- 所有检定均为每层效果分开检定。

伤害类型：

- 武器造成的伤害类型分为`melee`,`ranged`和`effect` ，某些武器可能拥有多种伤害类型。
- 一般而言，不同类型的伤害与尖刺和盾牌的交互方式不同，某些物品也可能修改交互方式。
抵消规则：
- 许多相反的效果具有互相抵消的机制，最终只有抵消后的一种效果生效。
- 逻辑为
```python
if(positive_effect.stack>negative_effect.stack):
    play_positive_effect(positive_effect.stack-negative_effect.stack)
elif(positive_effect.stack<negative_effect.stack):
    play_negative_effect(negative_effect.stack-positive_effect.stack)
else:
    continue
```
- 具有抵消规则的机制包括：狂热和冰冷，复制增益和无效化增益，复制减益和抵抗。

冷却加速/减速的精确计算：

- 所有加速与减速先相加并互相抵消。
- 净加速比例为 `faster` 时，`cooldown = base_cooldown / (1 + faster)`；等价的逐帧冷却推进倍率为 `1 + faster`。
- 净减速比例为 `slower` 时，`cooldown = base_cooldown * (1 + slower)`；等价的逐帧冷却推进倍率为 `1 / (1 + slower)`。
- Heat 每层提供 2% 加速，Cold 每层提供 2% 减速。因此相同层数完全抵消，只对抵消后的净层数应用对应分支。

模拟含义：

- 战斗引擎应以事件/时间线为基础。
- 每件物品都需要触发规则、冷却、目标规则、资源变化和位置依赖。
- 许多效果具有条件且可以叠加，因此必须有战斗日志用于调试。
- 模拟器必须控制命中率、暴击、商店抽取及其他随机过程所使用的随机种子。

项目中的耐力/随机数生成建模决定：

- 玩家状态同时包含 `stamina` 和 `max_stamina`。
- 标准战斗输入中，玩家以满耐力开始，所以初始时 `stamina == max_stamina`。
- 初始 `stamina` 和 `max_stamina` 是运行战斗所用 JSON 输入中的显式逐玩家字段，而不是隐藏默认值。
- `stamina` 和 `max_stamina` 在战斗中都可改变；物品效果可以修改其中任意一个。
- 除非未来有某个效果修改规则，否则耐力自然恢复速度为每秒 1 点。
- `CooldownTrigger` 不检查也不消耗耐力；它只推进冷却并报告是否就绪。
- 耐力消耗由独立的 `StaminaConsumptionEffect` 建模。
- 如果一件物品结束冷却时其拥有者没有足够耐力，该物品不会等待。此时冷却已经进入新的周期；`StaminaConsumptionEffect` 会返回 `False` 且不消耗耐力，木剑的 `run_own_effect()` 据此不调用后续近战伤害 effect。
- `BattleState` 持有用于命中检查、伤害抽取等战斗随机过程的全局随机数生成器。

项目中的触发器/效果组合决定：

- 基础 trigger/effect 行为应由可复用组件实例实现；具体物品类只编写组合这些结果所需的简明调度逻辑，不重复实现冷却、耐力支付、攻击等基础行为。
- `BattleItem.update_triggers(context)` 应调用每个触发器实例的接口，保存并返回与 trigger 顺序一致的基础 bool 结果列表。
- `BattleItem.run_effects(context)` 应始终先更新 trigger，再调用具体物品的 `run_own_effect(trigger_results, context)`，最后按其 bool 返回值决定是否检查 linked items。
- `BattleState.step()` 和 `run_linked_items()` 不应使用 `is_triggered()` 或其他 trigger 粗筛；即使所有基础 trigger 都为 `False`，仍进入 `run_own_effect()`，以支持 NOT trigger 条件。
- trigger 的 AND/OR/NOT、effect 是否调用、effect 失败后的分支，以及是否继续 linked items，都由具体物品的 `run_own_effect()` 决定。
- 基本 effect 只接收 `context` 并执行自身效果；它不接收 trigger 结果，也不负责物品级激活判断。
- 具体物品应主要负责组装触发器/效果实例、提供物品元数据并实现简明的 `run_own_effect()` 调度逻辑。
- 有状态的触发器/效果对象必须按物品实例创建，不能作为可变的类级对象共享。
- 木剑（Wooden Sword）应使用可复用的 `CooldownTrigger`、`StaminaConsumptionEffect` 和 `MeleeAttackEffect`；未来具有类似行为的物品也应复用这些组件。
- 第一版木剑刻意不实现战斗日志；测试应直接验证状态变化。

## 子职业建模说明

wiki.gg 的职业页面说明，子职业物品带来的效果可能不止直接的战斗效果。部分子职业物品会改变商店可用性或商店概率，例如使特定物品系列可用，或提高某些物品的出现概率。

对于观测设计：

- 如果子职业已经由一件玩家可见且已拥有的子职业物品完整表示，并且模型能获取足够的物品元数据/效果身份，则不需要单独的 `subclass_id`。
- 环境转移函数仍必须实现子职业物品效果，特别是对商店物品池和商店概率的修改。
- 如果把物品效果简化为不透明 ID，那么特殊子职业物品的 ID 就足够了。

实用折中方案：

```python
observation = {
    "class_id": int,
    "items": [...],          # 包含子职业物品实例
    # 最小观测中不单独设置 subclass_id
}
```

模拟器内部的真实状态仍可记录所选子职业，以便调试和数据验证；但如果它与已拥有物品的状态等价，策略就不需要单独观测该字段。

## 观测草案

策略模型可见观测：

```python
observation = {
    "round": int,
    "gold": int,
    "health": int,
    "class_id": int,
    "rerolls_this_round": int,
    "reroll_cost": int,
    "unique_item_number": int,
    "max_unique_item": int,
    "owned_items": {
        "items": [
            {
                "is_slot": bool,
                "item_id": int,
                "price": int,
            }
        ],
    },
    "shop": {
        "items": [
            {
                "is_slot": bool,
                "item_id": int,
                "price": int,
                "discounted": bool,
                "reserved": bool,
            }
        ],
    },
    "victory_rate_returned_by_placement_model": float
}
```
摆包模型可观测：
```python
observation = {
    "owned_items": {
        "items": [
            {
                "is_slot": bool,
                "item_id": int,
            }
        ],
    },
    "placement":{
    }
    "occupacy_matrix":[[

    ]]
}
```
为早期学习推荐的派生特征：

- 合法摆放掩码。
- 合法配方掩码。
- 活动物品栏的空格子。
- 各物品标签的数量。
- 星标/菱形覆盖矩阵。
- 商店物品可负担掩码。
- 出售价格向量。

不得暴露：

- 未来的商店抽取结果。
- 隐藏的随机种子。
- 玩家不可见的未来对手。但模型可以在内部保存数个当前版本流行的对手摆盘以供评估胜率。
- 超出真实游戏可见信息范围的对手隐藏数据。

## 动作空间草案

分模型动作格式：

```python
action_strategy_model = {
    "type": one_of([
        "buy_to_storage",
        "sell_item",
        "reroll_shop",
        "toggle_shop_reserve",
        "toggle_combine_lock",
        "end_shop",
    ]),
    "args": ...
}
action_placement_model = {
    "type":one_of([        
        "move_item",
        "rotate_item",
    ])
}
```

所需的合法性掩码：

- 能否负担物品价格。
- 物品能否放入活动物品栏格子。
- 如果储物箱有空间限制，物品能否放入储物箱。
- 不得重叠。
- 出售目标必须存在。
- 有足够金币刷新商店。
- 商店栏位必须存在。
- 物品可以锁定合成。
- 可以结束商店阶段。

## 近期仅使用 Wiki.gg 的数据任务

1. 将 Cargo `Items` 表的所有行导出到本地结构化文件。
2. 将 Cargo `Recipes` 表的所有行导出到本地结构化文件。
3. 确定物品网格/形状/星标/菱形数据是结构化数据，还是必须从各物品页面解析。
4. 确定初始背包/配置数据存储在哪里。
5. 确定是否可以根据标准化的 `item_classes`、`Neutral` 以及子职业物品效果重建各职业的商店物品池。
6. 编写一个小脚本，在补丁发布后重新查询 wiki.gg，并与本地物品/配方数据比较差异。
7. 战斗部分先从数值效果易于解析的一小部分物品开始，再逐步扩展。
