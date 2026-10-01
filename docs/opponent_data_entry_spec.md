# 对手摆盘输入入口定位 SPEC

## Requirements（需求）

- 目标：在当前完整解包源码中定位对手摆盘进入游戏战斗引擎的入口，说明其输入格式、来源、校验和调用顺序。
- 用户故事：作为 Python 战斗模拟器开发者，我能用自定义对手摆盘驱动原游戏打一场对照战斗，并明确最小改动点及其限制。
- 本次交付是源码调查和可行方案，不修改游戏或模拟器代码，不写入真实用户缓存。

## Design（设计）

以 `Game.finishSwitchingToCombat()` 为战斗装载起点，向上追踪 `RunDatabase` 的正常匹配与缓存来源，向下追踪 `Game.initOpponent()`、`Game.addOpponentItem()` 的物品实例化过程；再检查 Build History 是否提供可复用的独立入口。优先考虑直接提供解码后的回合字典这一简单边界，避免为了单场对照实现网络服务、复杂协议或额外架构。

源码确认的数据边界为 `roundData` 字典：`health`、`stamina`、`class`、`name`、`chibi`、`skins`、`items`，其中每个物品 tuple 包含 `d`（ItemDescriptor）、`c`（Vector2）、`f`（方向），并可选 `g`（宝石）与 `pd`（持久实例数据）。

关键流程：

```text
在线来源 / user:// 缓存 -> RunData -> getNextOpponentData()
                                      -> Game.initOpponent()
                                      -> Game.addOpponentItem()
                                      -> prepareItems() / activateItems()
```

### 本次涉及的具体函数：接口与伪代码

以下是调查对象的源码接口及伪代码。未在源码声明返回类型时，右侧返回类型仅表达静态分析中观察到的返回值。

| 函数接口 | 伪代码 |
| --- | --- |
| `RunDatabase.getParsedRuns() -> Array` | 合并在线来源；若数量不足门槛则补缓存；返回候选 run。 |
| `RunDatabase.loadCachedRuns() -> void` | 按构建版本确定缓存路径；用 Godot Variant 读数组；逐条反序列化有效 run。 |
| `RunDatabase.sortOpponents() -> void` | 从候选 run 按当前回合及匹配条件筛选、评分、排序；重置读取索引。 |
| `RunDatabase.getNextOpponentData(roundReduction: int) -> Dictionary` | 按模式选择大厅、特殊镜像或下一条有效 run；解码目标回合；必要时以较早回合物品替换。 |
| `RunData.deserializeRound(roundIndex) -> Dictionary` | 取指定回合位流字符串并连同职业、名字、外观信息生成回合字典。 |
| `RunData.deserializeItems(metadataString: String, version) -> Dictionary?` | 字符串转位流；调用 `deserializeStream()`。 |
| `RunData.deserializeStream(bitStream: BitStream, version) -> Dictionary?` | 读取生命、耐力；循环解码物品索引、坐标、方向、宝石及实例数据；返回回合字典。 |
| `Game.switchToCombat() -> void` | 播放进入战斗的场景动画；实际装载由动画后续调用完成。 |
| `Game.finishSwitchingToCombat() -> void` | 创建对手；历史分支直接加载已标记的摆盘，正常分支先排序匹配池再循环加载候选；之后准备双方物品并延时激活。 |
| `Game.initOpponent(roundReduction, droppedItems) -> int` | 取得回合字典；设置对手属性；背包优先逐件实例化并调用 `addOpponentItem()`；设置外观、名字。 |
| `Game.initHistoryOpponent() -> int` | 从已标记的 Build History 回合解码物品并装入对手。 |
| `Game.addOpponentItem(tuple, item, checkValidity: bool) -> int` | 定向并校验摆盘；加入物品；设置宝石与持久实例数据。 |
| `RunData.createRoundDict(metadataString: String, _characterClass, _loadout, _name, _chibiStyle, _skins, version, nameIsEncoded: bool = true) -> Dictionary?` | 解码回合物品与属性；附加职业、loadout、名字和外观；返回消费端所需字典。 |
| `RunData.isValid(currentRound: int) -> Validity` | 逐回合执行来源 run 的完整合法性检查，发现无效回合即拒绝。 |
| `Game.startHistoryRun(runData, roundNum: int, opponentData = null, opponentRoundNum = -1) -> void` | 从选中的 Build History 记录构建己方摆盘并切到对战；当前源码未使用两个 opponent 参数。 |
| `BuildHistory.setOpponentMark(roundNum: int, buildEntry) -> void` | 将某条历史记录的指定回合标记为下一场历史对战的对手。 |
| `BuildHistory.fightBuild() -> void` | 关闭历史界面并调用 `Game.startHistoryRun()` 启动选中回合的对战。 |
| 拟议 `loadCustomOpponentRound(path: String) -> Dictionary?` | 若文件不存在则返回空值；读 JSON 并检查必需字段；逐件用当前版本 `ItemBook` 将 `item_index` 变为 `ItemDescriptor`，将 `(x,y)` 变为 `Vector2`；构造 `d/c/f` tuple，透传合法的 `g/pd`；返回 `roundData`。此函数尚未实现。 |

## Tasks（任务拆解）

1. 读取本地知识库与当前完整解包版本，确认权威源码。（已完成）
2. 核对正常对手来源、缓存格式、选择和校验；依赖 1。（已完成）
3. 核对战斗初始化、最终回合字典和物品装载；依赖 2。（已完成）
4. 检查历史对战与其他已有调试入口，评估最小注入方案；依赖 3。（已完成）
5. 给出带文件行号的结论、可操作方案及未经运行验证的部分；依赖 4。（已完成）

## Acceptance Criteria / Tests（验收标准）

- 能指出最终消费自定义对手数据的具体函数和变量，以及正常来源函数。
- 能列出必要字段、物品 tuple 结构、校验条件和版本/缓存限制。
- 至少比较直接改返回的回合字典、缓存注入、历史对战三种路径，并解释各自是否能可靠指定一场对照战斗。
- 每一项关键结论都有当前完整解包的文件和行号；静态分析无法证实的运行时行为明确标注。
- 本次不要求运行游戏或修改真实缓存；若后续实施，再针对具体方案另立实现任务。

## 调查结论（源码静态核对）

### 实际消费入口

`Game.finishSwitchingToCombat()` 创建 `OPPONENT` 后，在正常分支调用 `RunDatabase.sortOpponents()`，再循环调用 `Game.initOpponent(roundReduction, droppedItems)`；后者第一个语句将 `RunDatabase.getNextOpponentData(roundReduction)` 的返回值赋给 `roundData`。这是自定义对手摆盘最直接的接入边界。随后先设置生命、耐力和职业，按背包优先排序并逐件实例化、定位和检查摆放；最后设置五个皮肤槽、名字，并保存 `curOpponentData`。成功后才进行物品准备和战斗激活。证据：`Core/Game.gd:2575-2671,2776-2895,2905-2921`。

正常匹配来源是在线 `silentwolfRuns`、Steam `parsedRuns`，在线候选少于 30 时才附加 `runsFromCache`。候选会按当前回合筛选、随机洗牌与打分，再经 `RunData.isValid()` 验证。因而改写 `runs_steam.cache` 或 `runs_sw.cache` 无法保证下场一定选中指定摆盘；缓存还必须用 Godot `store_var` 格式写 10 属性 run 数组，版本必须处于允许范围，当前版本 `1.1.8`、最低 leaderboard 兼容版本 `1.1.5`。证据：`Core/RunDatabase.gd:10-17,54-66,249-304,315-358,384-551`；`Utility/RunData.gd:34-80,329-353`；`Core/Game.gd:10-15`。

### 推荐的最小实验方案

在**实验用副本**的 `Game.initOpponent()` 开头，用一个可选的本地 JSON 输入代替 `RunDatabase.getNextOpponentData()` 的结果；如果文件不存在则保持原流程。输入是单个回合，不必伪造整条 run、在线分数或缓存。加载时把 `item_index` 转为 `ItemBook.getDescriptorFromIndex(index)`，把 `x,y` 转为 `Vector2(x,y)`，形成源码所需的 `d/c/f` tuple。可选宝石索引放 `g`，物品特有持久数据放兼容的 `pd`。自定义实验时将 `droppedItems` 设为 0，防止新手让步逻辑随机删物品。当前正常分支仍先执行匹配排序，若需要精确复现随机序列，应在实验路径跳过排序并明确设置、记录战斗 RNG 状态。这里是方案设计，尚未改动或运行验证。

外部 JSON 可采用以下接口形状；数值只用于说明字段，正式试验须以当前 `ItemBook` 中真实背包和物品索引、合法坐标填充：

```json
{
  "health": 50,
  "stamina": 5,
  "class": 0,
  "name": "oracle",
  "chibi": false,
  "skins": [0, 0, 0, 0, 0],
  "items": [
    {"item_index": 1, "x": 3, "y": 2, "f": 0}
  ]
}
```

输入约束：`roundData` 至少有 `health`、`stamina`、`class`、`name`、`chibi`、`skins`、`items`；`skins` 为五槽数组。`d` 必须是当前版本的 `ItemDescriptor` 对象而非 JSON 整数；`c` 必须是 Godot `Vector2`；`f` 为四方向枚举值。背包会先装入；普通物品每个碰撞格必须位于背包扩出的可放置区域且不可重叠。非法摆盘会使 `addOpponentItem()` 返回 `-1`，正常流程会继续挑下一条 run；固定返回同一个非法自定义回合时可能持续重试，实验实现应在失败时明确中止并报出原因。证据：`Utility/RunData.gd:174-271`；`Core/Game.gd:166-172,2638-2648,2776-2895,5387-5388`；`Core/Inventory.gd:186-219`。

### 其他现成路径的用途与限制

- **Build History 对战**：界面可标记历史摆盘为对手，`Game.initHistoryOpponent()` 通过同一 `addOpponentItem()` 装载，适合先验证原游戏能重打一场已有战斗。任意外部摆盘仍需构造兼容的历史数据或增加导入逻辑。`Game.startHistoryRun()` 声明了 `opponentData`、`opponentRoundNum` 参数，但函数体没有使用它们。证据：`Interface/BuildHistory/BuildHistory.gd:195-203,309-316`；`Core/Game.gd:2402-2431,2638-2645,2829-2860`。
- **旧桥接脚本**：`AI-BackpackBattles/bridge/bridge.gd` 提供通用 TCP 命令和属性/方法调用，尚无“导入对手摆盘”专用命令。它不是本项目判定游戏逻辑的权威来源；当前桥接代码也没有将 JSON 的物品索引递归转换成 `ItemDescriptor` 与 `Vector2` 的逻辑。证据：`AI-BackpackBattles/bridge/bridge.gd:67-137,207-221,816-827`。

### 验证状态

上述控制流、字段和筛选约束均已用当前完整解包源码静态核对。尚未修改游戏 PCK、运行实验副本、读取真实 `user://` 缓存或做战斗输出对照。
