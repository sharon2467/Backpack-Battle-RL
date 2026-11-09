# Buff异常分支原引擎摆盘验证 SPEC

2026-11-09 · **本轮实验已完成，两个异常均复现**，见[实测结果](buff_engine_edge_verification_results.md)。本SPEC先于夹具实现编写，按用户授权修订：**不复制工程/二进制；原工程可临时加探针并恢复；允许临时改名安装PCK并恢复，以使用原游戏引擎**。已读知识库及旧GUI框架。此前复制路线已停止，副本与该轮失败日志已删除，不把启动失败当机制证据。

## 1. Requirements（需求）

用原版游戏引擎、真实物品摆盘和正常战斗回调，验证两个静态审计异常：

1. 概率抵抗与反弹重叠后，`left<0`是否让`ownStacksUsed`为负并增加专用抵抗层。
2. 已有层数满cap时，反弹后仍有正剩余量，经cap裁成0提前返回，是否跳过待续发的反弹。

不能只据最终HUD或源码推导判定。每项要有对照、分支trace、实际层数/抵抗层/事件证据。抵抗/反弹概率必须由真实物品自然产生；不替换RNG、不手写目标百分比、不改Buff公式。本轮满cap也须自然堆叠，不给current/permanentStacks种初始数量；其他辅助夹具不混作本轮自然证据。

原exe及真实存档不可改，安装PCK**仅允许同安装目录临时改名，内容不改、不复制并必须恢复原名/SHA**。原工程project.godot可临时autoload及有条件启动features配置，Core/Buff.gd仅只读观察，data/custom_opponent.json输入摆盘；原字节备份、记diff/位置、finally恢复，不改Game.gd/物品机制。测试放tests、证据data、报告docs；宝石实装暂停。

## 2. Design（设计）

### 2.1 原工程入口、版本门槛与存档隔离

旧实验实际用GodotSteam3.6.2，不能当成本次原exe结果。已只读定位：

- 原exe：`E:\steam\steamapps\common\Backpack Battles\BackpackBattles.exe`，33476608字节，SHA256 `4522a5f2b71fe2aa5f7f730a2bd71f66f4f8112609164bcef39c110f047ad577`。
- `--help`版本：`Godot Engine v3.6.stable.custom_build.de2f0f147`，支持`--path/--main-pack/--windowed/--resolution`，不支持编辑器模式。相邻PCK头为Godot3.6.0，但其修改时间较新，不假定数据仍为1.1.8。
- 不再复制exe/DLL或工程。零售exe可能优先加载安装目录PCK，`--path`本身不能证明资源来自工作区；先用外部只读probe核对实际加载源。

每次仅建`data/buff_engine_edge/<RunId>/`的证据、少数待改文件字节备份、`appdata/localappdata`隔离存档；**没有project/bin副本**。实际运行现`Backpack Battles/`原工程。harness以`BB_BUFF_EDGE_RUN_DATA`环境变量定位本轮data/case.json及截图；摆盘输入仍走原有工作区`data/custom_opponent.json`，运行前备份、后恢复。

先`source_probe`：原exe以`--path <原工程> --script <tests外部探针绝对路径> --windowed`运行外部MainLoop，跳过autoload，仅记录exe/Engine/项目/原资源Buff SHA/OS features/user路径及Game.gd源码中的VERSION文本；不改原工程。工作区预期SHA或源码版本不符则fail，不能把安装PCK误认为工作区。**这只证明加载源与原生features，不是Game实例或战斗已运行的证据。**后续Node harness启动显式传`res://Core/Main.tscn`，避免--script忽略默认场景；smoke必须再读真正Game.VERSION、OS features、Game/Buff源SHA，等标题/ItemBook及描述符就绪。

用户现已选择**原游戏引擎**并允许包改名恢复：`Engine=original -TemporarilyHideInstalledPack`先按2.6守卫隐藏同目录PCK，再原exe运行原工程。Engine=godotsteam仅保留既有参数，不自动使用。先取得未加features元数据；缺少editor/full_version时，显式`-EnableEditorStartupFeatures`可在后续非source_probe模式临时向project顶层加入`_custom_features="full_version,editor"`，恢复同autoload。此前无下划线`custom_features`实测OS features仍false，须保留失败证据；依据[ProjectSettings::_set的特殊键分支](https://raw.githubusercontent.com/godotengine/godot/3.6-stable/core/project_settings.cpp)及本exe键字面值，改用带下划线候选，**只有实际OS/Game字段才证明生效**。记录两键get_setting值。配置不改Game.gd，但生效后改变Game.EDITOR/FULLVERSION、Util.debugOnly及离线/内容入口，**是启动模式适配，不是纯观察**。ItemBook.gd:656、703–706因此跳过资源验证并读明文ItemData.csv，须记CSV指纹及已有解密一致性依据；可存在的debug UI也启用。记录前置元数据、配置diff和实际features；不得改变机制RNG、概率、HP或物品参数，不声称这是未加features的零售启动行为。

若首位Node ENV已证明editor/full_version正确，仍在Steam启动阶段崩溃，可再显式`-DisableSteamIntegration`，仅在上述开关同时开启时向同一配置加`disable_steam_integration`。这是原版SteamHelper.gd:55的现成提前return入口，Game.gd:2090也令steamAvailable=false；不改这两份脚本。它使本实验走离线战斗与既有JSON入口，不验证在线Steam功能。保留启用前失败/ENV证据；元数据与真正Game实例均记录三项实际OS features、最终配置字符串和源码指纹，不能把离线适配隐去。

保持`Engine.time_scale=1`，使用windowed原渲染路径；脚本进程默认Hidden，不把viewport PNG冒称桌面截图。测试完整走非排位标题→商店→合法装盘→switchToCombat→原prepare/activate/物品自然触发，目标分支取证并截图后可退出本实验进程，不要求自然终局、不人为判胜。不能直接调用Buff函数替代物品触发。

### 2.2 已收敛的负left三组

己方4个Leather Bag（id11）置(0,0),(2,0),(0,2),(2,2)，朝向UP，铺4×4；对手1个皮包置(0,0)。镜子拟定坐标已按形状安排：4颗UP置(2,0),(3,0),(2,2),(3,2)，第5颗RIGHT置(0,3)。实装仍须原Inventory合法校验并导出实际occupiedCells/槽位。

| 组别 | 防守方（己方） | 对手 | 自然参数/用途 |
| --- | --- | --- | --- |
| N：重叠 | Holy Armor58置(0,0)UP，3槽各Elephant Rune188；Magic Mirror332×5按上述坐标/方向 | Pocket Sand20×1置(0,0)UP | 三符文prepare三Debuff抵抗120%，首4秒；镜子总反弹≥100%；开局Blind1 |
| R：仅抵抗 | 同Holy Armor与3符文，移除5镜 | 同一Pocket Sand | R120/F0，无负left，专用抵抗层不增加 |
| F：仅反弹 | 同Holy Armor但槽空，保留5镜 | 同一Pocket Sand | R0/F≥100，无负left，专用抵抗层不增加 |

依据：`Items/HolyArmor.tscn:42-48`三槽；`Items/Exclusive/ElephantRune.gd`自然40%/4秒；`MagicMirror.gd:8-10`每镜基础20%且可能有Holy星位加成；`PocketSand.gd:3-5`开局施加Blind1。不得把“拟总概率”当观察值，必须记录准备后的实际抵抗/反弹率和攻击到达时间。

N组首个Blind请求的待验证轨迹为：请求1→resisted1、left0→reflected1、left-1→ownStacksUsed=-1、专用resistStacks从0变1→resisted被负own抵消为0→防守Blind0→对手收到reflected Blind1。原目标可能没有Resist事件；absence只有与局部trace匹配才有意义。该表是预测，运行后才能写实测结论。R/F对照相同物品触发窗内专用resistStacks应保持0，不能只凭N组PASS判定。

### 2.3 自然堆叠满cap与同场对照

只有实际观察到`reflected>0`且抵抗/反弹后`amount>0`，再在`current=MAX_STACKS`把它裁0的调用才属于目标case。**全量反弹使amount先为0时会跳过cap分支，不能据此概括“满cap都不反弹”。**

双方12个皮包按x=`0,2,4,6`、y=`0,2,4`铺8×6，朝向UP。已核形状的候选摆盘：

| 一方 | 实际物品与位置 |
| --- | --- |
| 攻击方（己方） | Deer Totem148×7置x=0…6,y=0 UP；Chili Pepper117×8置x=0…7,y=2 UP；Gigawatz478置(7,1)UP；Hawk Rune189×17置(7,0)及x=0…7,y=4/5 UP，合计48占格 |
| 防守方（对手） | 同排7个Deer Totem；Magic Mirror332×1置(7,0)UP，星位朝空侧，无Holy加成时自然20%反弹；其余格空 |

Deer每件prepare自然增加15%伤害抗性，7件105%由原takeDamage限制到100%，使双方伤害自然归0，避免等待10000层期间死亡。Chili的原CD4.5每次Heat1形成自然加速；Hawk CD2.4每次Blind1；Gigawatz CD7.5先无条件Blind3再Effect伤害，无命中/耐力前置。预估约200多游戏秒达到10000仅是估算，不能作为实测；运行至全部目标证据满足或240游戏秒截停，进程超时420墙钟秒，不调time_scale。

同场收集三种真实调用：未满时Giga N3、F1或2，有反弹投递；满cap时Giga N3、F1或2，正剩余被cap裁0且不投递；满cap时Hawk N1、F1，全量反弹使amount先0仍投递。用真实trace筛选，不强行指定哪次随机取值。

所有原物品其他行为也照常：Chili治疗、Heat达到阈值后的随机净化会清攻方反弹Blind并耗自然RNG，不能关闭；同种Chili不彼此提供Food同种加速。本实验是给定物品集合的受控摆盘，含多份Unique/跨职业组合，不宣称这些数量都能由普通商店run取得。关键证据是原物品在原引擎自然生效并累计到cap。

负left三组和满cap组均禁止直接改层、抵抗层、HP或概率。若240游戏秒仍未达到cap或没有目标部分反弹调用，记未完成，不强写数量代替。

### 2.4 临时只读探针与证据链

获用户授权，只在**原工程**`Buff.gainTemporary`临时加观察local call_id及observer；project.godot临时autoload指向tests外部脚本绝对路径。为在其他autoload的_ready崩溃前读启动字段，可将观察者列为首个autoload；其_ready只读已注册Game的普通初始字段，不依赖Game.onready节点，标题/物品库仍由_process等待。观察顺序与diff须记录。observer只读并JSONprint，不调用RNG、spawnLabel、give/lose、emit或createEvent，不覆盖机制变量。优先记录：

- enter：call_id、时间/帧、角色、类型、source descriptor、parent ID、reflected入站、request、current、permanent、各概率和专用/全局层。
- after_resist、before/after_own_resist：抵抗后及反弹后的原amount/resisted/left/reflected、ownStacksUsed及专用层前后。
- before_cap、cap_zero_return、before_reflect_dispatch、exit：待反弹数量、cap前后amount、是否实际进入续发、原目标事件ID及结果。
- 双方成功Stack/Resist事件的实际amount/target/origin/reflected/parent，与调用前后状态及屏幕HUD对应。原日志没有事件时也保存前后字段，不伪造事件。

探针diff仅观察代码；inline return展开保持控制流。保存每次stdout/stderr、布局/cells/socket、事件配对及viewport图。若局部trace不可取得，公开状态/原CombatLog和足够强对照仍可验证外部行为，但必须标明“局部路径由源码推断”，不能假称直接观测left/随机F；单次“没反弹”不足以排除F=0。PASS代表实质断言，不只是退出。

### 2.5 计划实验接口及伪代码

测试实现者仅一位。文件为`tests/buff_engine_edge_run.ps1`、`buff_engine_edge_battle.gd`及`buff_engine_source_probe.gd`；新增函数先补接口。旧复制式runner已废止，不按其旧参数重跑。

| PowerShell接口 | 伪代码 |
| --- | --- |
| 脚本入口`param([string]$RunId=<时间戳>,[ValidateSet('source_probe','smoke','negative_left','full_cap')][string]$Mode='source_probe',[int]$TimeoutSeconds=180,[ValidateSet('original','godotsteam')][string]$Engine='original',[switch]$TemporarilyHideInstalledPack,[switch]$EnableEditorStartupFeatures,[switch]$DisableSteamIntegration)` | 不复制；按2.6守卫/manifest改包名；备份源字节/隔离存档。source_probe只运行MainLoop元数据且拒绝features开关；features仅original的后续模式，先留原生元数据。DisableSteamIntegration还要求EnableEditorStartupFeatures及先前正确features/Steam失败证据，显式加第三tag。临时features/autoload分别记diff，Buff仅观察；full_cap Timeout420；finally独立恢复原工程/环境及包名/SHA，失败也不能跳过包恢复 |
| `Get-OracleSourceHashes([string[]]$Paths) -> hashtable` | 只读逐文件SHA256，返回path→hash |
| `Write-OracleUtf8([string]$Path,[string]$Text) -> void` | 只写本次tests/data证据及已备份的原工程探针/输入目标，UTF8无BOM |
| `Add-OracleObservation([string]$Text,[string]$Needle,[string]$Replacement) -> string` | 要求needle恰1次；替换为仅增加observer的文本，失败则停；不容忍静默漏插/多插 |

外部`tests/buff_engine_source_probe.gd`继承MainLoop，避免autoload先于探针崩溃；不创建Game/Main或最小工程。

| 精确接口 | 伪代码 |
| --- | --- |
| `_initialize() -> void` | 读Engine/exe/项目、custom_features与_custom_features两配置键、三个OS features/user路径、原资源Buff SHA及Game.gd的VERSION源码文本；JSONprint并保存元数据；源SHA/源码版本不符设置非0退出码，否则0；明确无Game实例版本证据 |
| `_idle(_delta: float) -> bool` | 不处理游戏；返回true，请求MainLoop结束，沿用_initialize设定的退出码 |

GDScript如下；`setup_case`内调用原放置/镶嵌API，不替换具体物品脚本。

| 精确接口 | 伪代码 |
| --- | --- |
| `_ready() -> void` | 从BB_BUFF_EDGE_RUN_DATA读case；打印并立即独立落盘实际exe/引擎、真正Game.VERSION、三项OS features/两配置键值及Game/Buff SHA、user路径；区分观察后Buff SHA与备份SHA；准备状态机/观察计数，不把脚本刚加载当通过 |
| `_process(_delta: float) -> void` | 等标题/物品库/动画及所需描述符就绪；smoke核实版本/路径后退出；实验正常新非排位→商店setup_case→switchToCombat；验证注入源、捕获开局/目标状态；满足观察条件finish，full_cap达240游戏秒仍缺证据则记未完成；不加速或判胜 |
| `setup_case() -> void` | 读本次case.json；按负left/full_cap重建己方袋/物品与符文；记录实际布局；对手走native JSON注入；不得直接赋概率/层数/HP |
| `add_item(name: String,x: int,y: int,f: int=0) -> Item` | ItemBook真实实例化、定向、按原Inventory可放置检查加入，失败fail；返回实际Item |
| `socket_gems(host: Item,names: Array) -> void` | 校验真实槽数；逐颗ItemBook实例化Gem并调用原addToSocket；记录host/socket/gem索引，不写gemPower或概率 |
| `new_call_id() -> int` | 仅观察者私有计数+1，不写游戏状态 |
| `observe(label: String,call_id: int,buff: Reference,payload: Dictionary={}) -> void` | 读取buff/角色/来源字段，加本次局部payload，JSONprint；仅维护观察call栈以标反弹parent_call，不改游戏状态或消耗RNG |
| `capture(label: String) -> void` | 当前viewport取图、flip_y，保存本run/data PNG；如失败fail；只称viewport截图 |
| `fail(message: String) -> void` | 记FAIL及case，保存现有证据，以1退出，不修改胜负 |
| `finish() -> void` | 写实际状态/已观察分支；自然胜负未产生则明确未等终局；保存截图并退出本进程；机制结论由配对断言另验，缺目标不标PASS |

full_cap复用这些函数和case数据，不添加种层回调；如runner确需新增函数，先列接口/伪码再实装。

### 2.6 PCK改名守卫、原工程探针与恢复

显式switch仅可配Engine=original。启动前确认无其他BackpackBattles游戏进程；解析源包绝对路径固定为`E:\steam\steamapps\common\Backpack Battles\BackpackBattles.pck`，临时名为同目录`BackpackBattles.pck.codex_buff_edge_<RunId>.disabled`；核对二者父目录确为原exe安装目录、原名存在、临时名不存在，拒绝覆盖。先将源路径、临时路径、SHA256、RunId及改名状态写入本轮manifest，再用同一PowerShell的Move-Item -LiteralPath移动文件名；内容不改、不生成PCK副本。只有本轮成功改名才置恢复标记，之后才能启动原exe。

finally先停本次自建PID并恢复原工程探针，然后**无论前面恢复是否报错都执行包恢复段**：只有本轮已改名、临时包SHA与原SHA一致且原名未被占用时才Move回原名并复核SHA；否则不覆盖，记录确切路径/冲突并报错供立即处理。各恢复段独立收集错误，不能因一个脚本/源文件错误跳过包恢复。进程崩溃、超时、解析错误均走finally；中断/主机异常后按manifest人工或受控恢复，不能开启另一轮去覆盖悬挂临时包。

逐轮记录`project.godot`临时autoload行及有条件_custom_features顶层配置、`Core/Buff.gd::gainTemporary`每个观察位置/原行号/增量diff、data/custom_opponent.json输入。features先查带/不带下划线原键，拒绝重复键或覆盖未知既有配置；本工程原来无该键时只加一行。待改文件原字节备份到本轮data，非整工程复制。未改的`Core/Character.gd/Core/Game.gd`、原exe/DLL/PCK也做前后hash；原本缺失文件恢复缺失，不留下共享替身。Game/物品参数不改。

每case新进程/隔离存档，不触真实runs缓存。finally恢复本次project/Buff/JSON原字节、环境并验hash，记录restoration.json；不结束用户进程、不留探针。若文件不再匹配本轮插桩版本，先保留冲突并报告，不覆盖他人新改动。证据不覆盖旧轮；目录删除/搬移先核对本runRoot绝对边界。此前整副本与失败日志已删除，不再声称保留。

## 3. Tasks（任务拆解）

1. [x] T1：固定SPEC、原exe/源码/数据hash、N/R/F布局和全部接口；无运行依赖。
2. [x] T2（T1）：MainLoop先记未加features的引擎/源SHA/源码版本；显式临时features启动适配；Node smoke核实真正Game.VERSION/features/源SHA/隔离存档，记录适配边界，不改Game.gd。
3. [x] T3（T2）：原Inventory核实摆盘/槽位；插只读trace，审diff后自然运行N/R/F；各自保留目标取证后的结果。
4. [x] T4（T3）：独立核对同调用负left/负own/抵抗层增加及对照，未以PASS代替分支证据。
5. [x] T5（T2及2.3布局）：full_cap自然堆叠，收集未满Giga/满cap Giga/满cap全反弹Hawk三种调用；游戏时钟实测，墙钟仅由清单创建时间估算并明确标注。
6. [x] T6（T4/T5）：记录探针位置、恢复原工程/输入/环境并核对hash；审核原日志/布局/截图，写结果与限制。

## 4. Acceptance Criteria / Tests（验收标准）

- 无工程/exe/PCK内容副本；原exe路径/hash/version、前置原生features元数据、真正Game版本及源Buff SHA、隔离存档齐全。包仅同目录改名且原名/SHA恢复；命中其他PCK不得认工作区。原project仅autoload/显式记录的启动features，Buff仅观察、JSON仅摆盘，Game/物品/RNG不改。
- N/R/F原物品合法摆盘，自然开局且4秒窗内。优先取得left/own局部trace；至少公开专用层0→1、双方Blind及完整事件/无其他写者与R/F对照形成外证。若没有局部变量，明确其符号是结合源码推断，不能写为直接实测。
- 满cap自然10000层，有未满正常反弹与满后全反弹对照；优先正剩余→cap0→提前return trace。局部不可见时须能排除F=0的强外证/充分统计并标推论边界，不以某一次无事件直接断言。全反弹例外不泛化。
- 机制分支日志、局部值、实际状态/事件、布局截图形成同轮证据链；截图缺失或事件不能配对需说明，不能用人工重画/静态预期代替。
- time_scale1、不注入随机/概率/数量/HP；准备/开战/自然物品触发后取证退出，不人为判胜。full_cap240游戏秒/420墙钟秒；记录原工程探针位置且恢复所有原字节/hash，安装文件不变、环境还原、仅本PID退出、真实存档未动。
- 最终报告区分已实测、仅静态预测、未完成及启动配置限制；先前Buff方案仍是待实施设计，不因观察实验顺带修改Python机制。
