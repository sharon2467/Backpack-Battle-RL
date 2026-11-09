# Debuff抵抗层阻挡自身净化：引擎验证 SPEC

2026-11-09 · **实验已完成，完整主链及对照通过**，见[实测结果](buff_cleanse_resistance_engine_results.md)。本文先于本轮探针编写，已读本地知识库。仅做原工程的可恢复观察实验，不改Python模拟器、一阶段规则或二期设计。

## 1. Requirements（需求）

用真实物品自然战斗，验证完整链：角色**已经有Cold**→后续同一次施加的抵抗/反弹重叠产生负left→Cold专用`resistStacks`增加→同一角色自己的Wisdom Puppy净化Cold时消耗该专用层、Cold不降。必须有去掉反弹镜子的自然净化成功对照，不能只重放此前Blind负left实验或调用Buff函数造状态。

用户指定`E:/godotsteam/godotsteam.362.editor.win64.exe`，本轮是**GodotSteam 3.6.2运行1.1.8解包源码**；与此前安装原exe Godot3.6.0证据分开记录。exe大小99683642字节、SHA256 `100B76E344A040D2CA50D1B4D03B097A259C35B32D5865043F33486A666EDA1C`，启动后仍核对实际路径/版本/源SHA。没有安装PCK动作。

不复制工程或二进制；不种层、不改概率/RNG/HP、物品参数或战斗算法，`time_scale=1`。仅原project临时autoload、原Buff只读探针及摆盘JSON可改，先备份原字节/哈希，记录位置/diff，finally恢复原字节、环境及输入。测试在tests、数据在data、报告在docs。多Unique/跨职业物品集合是受控摆盘，不声称普通商店run一定可取得。

global与typed区别首先按源码解释：gain会消耗`character.debuffResistStacks`，lose不读取它；lose会读取该类型`resistStacks`（`Core/Buff.gd:128–143,220–240`）。本轮不为构造global>0且Cold>0强注状态；没有自然证据时明确**global正库存对照未单独实测**。

## 2. Design（设计）

### 2.1 真实物品、布局与对照

被测角色为己方player0，Cold施加者为对手player1。双方12个Leather Bag（id11）UP，x=`0,2,4,6`×y=`0,2,4`铺8×6；双方7个Deer Totem148 UP置x=0…6,y=0，各占1×2，自然抗伤105%，由原算法免伤，不写HP。

| 物品/位置 | 原行为与来源 |
| --- | --- |
| 目标Dragonskin Boots153×2，(0,2)、(1,2)UP | 每件prepare Cold概率抵抗20%，合计40%；`Items/Exclusive/DragonskinBoots.gd:5–14`、CSV300 |
| 目标Magic Mirror332×2，(3,2)、(7,2)UP | 每件20%反弹；相隔且无Holy星位目标时合计40%；`Exclusive/MagicMirror.gd:8–11`、CSV394 |
| 目标Wisdom Puppy150，(5,4)UP | CD4、给Block后`cleanseCold(1)`、再activate；星位无Pet，不额外加速；`Exclusive/WisdomPuppy.gd:15–21`、CSV312 |
| 对手Snowmaster424，(3,3)UP | CD1.3；目标Cold<10时施加Cold1，否则给Empower；之后自然净化自己1个Debuff；星位无Ice；`Exclusive/Snowmaster.gd:14–22`、CSV206 |
| 双方Deer Totem148×7 | 每件prepare抗伤15%，保留全部其他回调；`Exclusive/DeerTotem.gd:9–16`、CSV307 |

脚本路径除明确前缀外均相对`Backpack Battles/Items/`，CSV指`Sheets/CSV/ItemData.csv`行号。物品名/数量/朝向只是实验输入；运行必须用原ItemBook/Inventory校验、打印实际occupiedCells及准备后概率，不能以此表替代合法性或参数观察。

两组各用新进程/隔离存档：

- `C_overlap`：完整目标布局，自然预期R40/F40；首次Cold可自然进入，随后等待N1同时抵抗和反弹。普通roll不替换、不固定seed；16%的单次重叠只是理论值，不是保证时间。
- `C_no_mirror`：只去掉目标两镜，保留Boots/Puppy/Deer及对手，预期R40/F0；等待typed=0且Cold>0时Puppy实际移除1层。无镜子不等于省略原版0%反弹draw。

Boots在battle_rage_started还会自然随机净化/给Empower和Block；Snowmaster也会净化自己，全部照常，不能禁用或冒充Puppy操作。主验收严格锁定目标/source=Wisdom Puppy。若其他gain先消耗再生的typed，或其他净化先消费，旧关联失效，继续等新完整链。

### 2.2 观察与因果配对

复用`tests/buff_engine_edge_run.ps1`及`buff_engine_edge_battle.gd`，新增`cleanse_resistance`模式，证据写`data/buff_cleanse_resistance/<RunId>/`。该模式强制Engine=godotsteam，拒绝三个原exe启动/PCK开关；不修改Game/SteamHelper或features。GodotSteam自身的editor feature及Game.FULLVERSION按实际打印，不能要求OS.full_version与Game字段相等。

原Buff只插读取/JSONprint，禁止RNG、createEvent、emit、give/lose、视觉标签或赋机制变量。私有观察call ID/栈只用于配对：

1. gain记录初始Cold/typed/global、来源与请求；抵抗后/反弹后/专用层前后局部值，实际事件与反弹子调用。
2. lose记录原请求与used、cap后amount、概率protected、专用/global保护前后、实际`change`及成功event。`change`必须在原局部计算时读取，不能用同步回调后的总数差推算。
3. 选择同一Cold容器：gain前Cold>0、typed=0，N1、resisted1/F1/left−1、own−1使typed→1；其后无其他消耗，再到Puppy used=False、Cold>0/typed>0，实际typed消耗1、protected1、change0、Cold不降。配对原生StackProtect amount1，且无该lose的成功负Cold事件。
4. 对照选Puppy typed=0、Cold>0的lose，change1、Cold−1、实际负事件amount−1。记录本次明确source/parent，不把gain call关系当CombatEvent父链。

trace含Util.time/帧及原事件战斗timestamp，二者分开；记录真实game时钟、进程墙钟起止（若只可估算须标注）。满足目标和对照后取viewport图退出本实验进程，不判胜、不等自然终局。单组最多300游戏秒、420墙钟秒；未出现完整链则记未完成，不能用静态推断补PASS。

### 2.3 精确接口及伪代码

不新增通用实验框架。下列是本轮所有计划新增/修改函数；已有构造/总线/物品函数不改。PS三个helper沿用现签名，GDScript十个现函数复用并增加模式分支，唯一新函数为`current_call_id`。

| PowerShell完整接口 | 伪代码 |
| --- | --- |
| 脚本入口`param([string]$RunId=<时间戳>,[ValidateSet('source_probe','smoke','negative_left','full_cap','cleanse_resistance')][string]$Mode='source_probe',[int]$TimeoutSeconds=180,[ValidateSet('original','godotsteam')][string]$Engine='original',[switch]$TemporarilyHideInstalledPack,[switch]$EnableEditorStartupFeatures,[switch]$DisableSteamIntegration,[switch]$PreviewOnly)` | 新模式校验Engine=godotsteam/原exe三switch均False，选新data路径；核exe身份/哈希；备份project/Buff/JSON并保存源hash；先字符串构建autoload与观察。PreviewOnly仅新模式可用：只存prepared_project.godot/prepared_Buff.gd及diff/位置，不写原工程/JSON、不启动进程，核原hash后退出。正常执行再临时写同样探针/两组JSON；APPDATA/LOCALAPPDATA及BB_BUFF_EDGE按case隔离；启动本exe，解析trace/原事件断言；finally独立恢复PID/原字节/环境及SHA；旧模式保留 |
| `Get-OracleSourceHashes([string[]]$Paths) -> hashtable` | 沿用：只读逐文件SHA，保存核验清单范围；不声称全工程逐文件核验 |
| `Write-OracleUtf8([string]$Path,[string]$Text) -> void` | 沿用：本轮证据与已备份的探针/输入目标UTF8无BOM写入 |
| `Add-OracleObservation([string]$Text,[string]$Needle,[string]$Replacement) -> string` | 沿用：要求needle恰1次才替换，只加观察；不容忍静默多插/漏插 |

| Node精确接口 | 伪代码 |
| --- | --- |
| `_ready() -> void` | 读隔离case；独立落盘真实exe/Engine3.6.2/Game1.1.8、项目根、OS/Game flags、原/观察版Buff及Game/CSV指纹、user路径/time_scale；不符合则fail |
| `_process(_delta: float) -> void` | 沿原标题→新非排位→商店setup_case→switchToCombat；等待原prepare/物品自然触发；选中完整主链/对照后截图finish；300游戏秒无证据或墙钟截止则fail；不改速度/胜负 |
| `setup_case() -> void` | 按case重建player0原袋/物品，C_no_mirror仅去镜；对手走原JSON注入Snowmaster布局；打印实际cells/参数；不写HP/层数/概率 |
| `add_item(name: String,x: int,y: int,f: int=0) -> Item` | 沿用原实例化、定向、canAddItemOrBag/addItemByTopLeft；非法则fail，返回真实物品 |
| `socket_gems(host: Item,names: Array) -> void` | 旧模式沿用真实槽/addToSocket；本轮不镶宝石、不改power |
| `new_call_id() -> int` | 仅观察者私有计数+1 |
| **新增**`current_call_id(buff: Reference) -> int` | active_calls末尾属于同buff且operation=lose则返回ID，否则−1；仅关联观察，不写Buff状态 |
| `observe(label: String,call_id: int,buff: Reference,payload: Dictionary={}) -> void` | 只读字段并JSONprint；gain/lose enter及exit维护私有栈；记录局部实际量/typed消耗，主链再生ID在其他消耗时失效；识别Puppy主链/自然成功对照，保留关联原事件ID；不调用游戏行为 |
| `capture(label: String) -> void` | 沿用viewport取图/flip_y并存本run PNG，失败fail；不称桌面截图 |
| `fail(message: String) -> void` | 保存原因/已有证据，退出自己进程非0；不改胜负 |
| `finish() -> void` | 输出实际层/保护量、调用关联、原Cold/Protect事件与状态；存结果/截图，缺目标不PASS；取证后正常退出本PID |

原工程观察函数**签名保持不变**，所有新增语句仅读取：

| 原函数接口 | 探针伪代码 |
| --- | --- |
| `Buff.gainTemporary(amount: int,duration: float,item=null,triggerEvent=null,reflect: bool=false)` | 复用既有enter/after_resist/before与after_own等观察；记录初始Cold>0与typed变化；原抵抗/反弹/return/事件顺序不变 |
| `Buff.loseStacks(amount: int,item=null,triggerEvent=null,used=false)` | 进入建私有call ID并observe原请求；原cap后、概率/专用/global保护阶段只读observe；最后原return表达式等价展开为接返回event→lose_exit观察→return同event |
| `Buff.changeCurrentLogShowLabel(isTimeout: bool,amount: int,item=null,triggerEvent=null,used: bool=false)` | 原`change=min(current,amount)`之后，current_call_id同容器有效时只读记录局部change；不改变扣层/事件/同步通知/返回；非本次lose不伪造关联 |

### 2.4 备份恢复与版本边界

唯一runner写测试，文档单写；SPEC落盘后才可改探针/运行。先PreviewOnly在字符串中生成拟插diff并审查，原工程此时不挂探针；通过后用新RunId正常执行，保存相同机制diff。可先GodotSteam smoke确认原项目标题/ItemBook；机制组按上述完整布局与断言执行。每轮独立证据不覆盖，备份及prepared仅少数文件，不建project/bin副本；安装PCK既不改名也不改内容。

保存project autoload新增行、Buff所有原/插后行号与增量diff；核查probe只观察。finally先停自己PID，逐项恢复project/Buff/JSON及环境，单项失败不跳过其余恢复；不覆盖他人并发修改。核对清单包括未改Game/Character/SteamHelper、CSV、所选exe等，精确路径和数量写manifest，只报告实际清单范围。保存`restoration.json`及原/后SHA；原来缺失的输入恢复缺失，用户进程不结束，真实存档不读写。最后检查原project/Buff无本轮残留。

## 3. Tasks（任务拆解）

1. [x] T1：固定本SPEC、自然布局/原参数/精确函数与主链条件。
2. [x] T2（T1）：runner新模式守卫/观察代码；PreviewOnly无原工程写入地生成并审diff，再用指定3.6.2做smoke，验证源/版本/隔离。
3. [x] T3（T2）：自然运行C_overlap，取已有Cold→typed再生→Puppy阻挡的同角色完整链。
4. [x] T4（T2）：C_no_mirror自然出现typed0/Puppy实际净化Cold−1。
5. [x] T5（T3/T4）：独立原日志/事件/状态/截图配对，记录恢复清单/原行diff与SHA；证据满足后写结果短报告。

## 4. Acceptance Criteria / Tests（验收标准）

- 实际exe为指定GodotSteam3.6.2，Game实例1.1.8、工作区源与指纹相符；不混称旧3.6.0实验。本轮无PCK动作、无复制工程。
- 原API验证布局；实测目标R40/F40或对照R40/F0、双方自然105%抗伤；所有物品其他行为正常、没有种层/改概率/RNG/HP，time_scale1。
- 主链必须在gain前Cold已正且typed0，观察N1重叠负left/own使typed增1，随后无别的消耗抢占，由Puppy usedFalse实际消耗typed1、protected1、change0、Cold不降，配对原生Protect且无该lose的成功负事件。
- 无镜对照必须有typed0、Cold正、Puppy actual change1/Cold−1及原生负事件；不能以保护概率猜测或最终HUD替代实际调用。
- global若没有自然正库存案例，明确仅源码区分、未单独实测；此前Blind负left证据不冒充本次完整净化链。
- 保留分支trace/原事件/真实viewport、两个时钟和截止边界；缺目标记未完成。恢复原字节/环境，清单SHA一致、探针位置/diff可复核，本PID结束、无探针残留；结论不外推为所有版本或全部Buff行为已验证。
