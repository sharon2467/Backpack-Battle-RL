# Buff二期T0引擎实验 SPEC

2026-11-10 · **实验完成，原工程已恢复；Python二期未实施。**本文先于本轮脚本与探针编写，已读本地知识库及[二期方案](buff_stack_stage2_spec.md)。本轮按以下计划用原工程和指定GodotSteam完成19组、32个独立进程，结果与明确的模型差异见[实验报告](buff_stage2_t0_engine_results.md)。实验完成不表示二期到期设计已定稿。

## 1. Requirements（需求）

验证临时层的0秒、相同期限、0.01秒连续处理、跨状态/双方、与真实物品冷却/角色周期效果相遇、到期通知中增减、最晚批删除后的索引、满层反弹与到期，以及reset/combatEnd残留。结论应回答“实际发生什么、在哪个引擎帧发生、哪些范围仍不能推定”，不只给PASS。

指定`E:/godotsteam/godotsteam.362.editor.win64.exe`，SHA256 `100B76E344A040D2CA50D1B4D03B097A259C35B32D5865043F33486A666EDA1C`，实际应为3.6.2、Game1.1.8。直接运行工作区原工程，不复制工程/二进制，不动安装PCK或exe。允许原工程只读探针与启动autoload，原字节备份、记录位置/diff并最终恢复。所有测试在tests、证据在data、结论在docs。

**两类证据必须分开**：

- 受控原API：为没有现成物品参数的0秒等情况，通过原`gainStacks/gainStacksTemporary/loseStacks/useStacks`安排数量与期限；可以调用本次明确列出的原生命周期/反射层API。不能直接赋current/permanentStacks/temporaryStacks/nextIndex或Timer字段，不能改概率、随机数、HP、胜负或机制分支。
- 真实调度：原注册Buff容器和Timer、真实香蕉冷却、角色onTick及自然疲惫终局。受控安排临时状态的场景不能称自然摆盘；直接reset不能代替正常回商店的生命周期证据。

保持time_scale=1，观察代码不调用随机数或战斗行为。原API自身产生的事件、标签和随机调用照常保留。已实测的负left、满层吞反弹和自身净化实验只作背景，不代替本次T0。

## 2. Design（设计）

### 2.1 最小执行与隔离

新增两个测试文件：`tests/buff_stage2_t0_run.ps1`、`tests/buff_stage2_t0_battle.gd`，不扩既有实验脚本。唯一runner写测试，文档单写。先在字符串中生成拟插版本，保存prepared文件/diff/原与插后位置，PreviewOnly不写原工程/输入、不启动；审查确认只读后，用新RunId执行。

每个场景/参数/重复次数使用独立进程、独立APPDATA/LOCALAPPDATA，证据放`data/buff_stage2_t0/<RunId>/`。保存实际exe/版本/源码原与观察版SHA、Game版本、物品表指纹、实际user_data、启动参数、进程起止时间/退出码及stderr。场景之间不覆盖证据，不沿用角色状态。错误场景单独进程，记录原错误及错误后的真实状态，不修原异常成PASS，也不因此跳过其他场景。

场内以三个真实皮包实例标记来源A/B/C，位置(0,0)/(2,0)/(4,0)；布局输出同时记alias、instance_id、物品名、所在角色和占格，不能只靠同名Leather Bag区分批次。其他皮包按需要扩格；双方所有场景只放皮包，调度场景额外放真实香蕉（id5），不改其冷却。不放鹿图腾或攻击物品，避免鹿图腾5秒后的自然Mana效果混入批次证据；短组8秒内无需免伤。生命周期保留双方原HP25，由原疲惫自然结束。相关原API安排均写case输入与操作日志。

### 2.2 场景矩阵

下表永久/临时量均通过原API建立；受控组不宣称物品自然施加了这些数量。19组场景冻结，`reentry_gain`正反两变体形成20个基础输入组合，分别新进程；执行标识记录变体。跨角色和实际冷却同帧组默认重复3次，其他组按各参数运行一次。同期限组另保留0.2秒原记录，并以输入字段`equal_duration=0.25`各做一轮校准；不增加场景或函数，实际进程数单列。

| 场景ID | 原API安排与实际要看的证据 |
| --- | --- |
| `zero_fresh` | 原注册Lucky容器，临时1层、duration0；读调用前Timer默认wait_time与实际到期帧，不先假定立即到期 |
| `zero_reused` | Empower1层@0.1秒完全到期；等原onTimeout整个函数返回后的下一物理帧，确认数组空/Timer停止，再加Empower1层@0；比较保留wait_time与真实等待 |
| `zero_running` | 同帧先Spikes1层@0.3秒，再Spikes1层@0；记录运行中的Timer余量、重新启动路径、选中批及实际到期 |
| `equal_forward` / `equal_reverse` | 同帧Lucky来源A2层、来源B3层，分别正反插入；持续时间由`equal_duration`输入，默认0.2秒。另以可二进制精确表示的0.25秒各做独立进程校准，检查实际未重启Timer时的等值扫描先后。记录是否重启、选中批及实际局部值，不将显示相同直接当严格相等 |
| `tolerance_inside` / `tolerance_outside` | 来源A2层@约0.12，来源B3层期限按原观测相位安排；必须分别得到原局部delay正值在(0,0.01]和>0.01，比较同调用栈递归与重新等待。只设置0.009或只见同帧不算覆盖 |
| `cross_start_forward` / `cross_start_reverse` | 同帧对player0 Lucky/Empower、player1 Lucky/Empower各临时1层@0.2；反转启动顺序，各重复3次。只用原注册容器，读实例/树位置/优先级；结论限当前工程初始化，不推定普遍创建顺序规律 |
| `phase_physics` / `phase_deferred` | 有真实香蕉。等原combatStart/preCombatStart执行且至少后续真实帧，确认TickTimer运行、物品triggerTime>0；读Tick余量及香蕉triggerTime/getSpeed，以原API分别建立Regeneration1/Lucky1的临时批。物理阶段或延后调用阶段安排，各重复3次；只以实际同引擎物理帧交汇判定，没相遇记未覆盖，不用未启动0对齐 |
| `reentry_use` | Mana永久1+来源A2@0.1+来源B3@0.3；真实到期负通知内只执行一次原useStacks(Mana,1,来源C,event)，观察永久优先及剩余批 |
| `reentry_lose` | 同上；真实到期通知内只执行一次原loseStacks(Mana,2,来源C,event)，观察永久及最晚临时批扣量 |
| `reentry_gain` | 同组永久/临时安排，分别早批先插/晚批先插；到期通知内只增加来源C临时1层@0.5，观察回调是否改变nextIndex以及随后实际删除哪个批。两参数分别新进程，不用增加永久量替代 |
| `stale_far_first` / `stale_early_first` | 来源B3@10秒与来源A2@5秒，先远后近/反插两组；原loseStacks移除3层最远批，再等到5秒附近，截止7游戏秒。记录nextIndex、数组及原错误/到期结果，不在原分支加保护 |
| `cap_expiry` | Blind永久9999+来源A临时1@0.2，验证满10000；先原changeDebuffReflectStacks(1)+入站Blind3，再在真实timeout通知释放容量后同样调用。保留0%概率反弹真实抽样并记录反弹层/裁量/子调用；两次前后对照不强求同帧，但后测必须与实际到期释放同引擎物理帧，观察序号先减少后新gain，不从observer入口刺激机制 |
| `reset_controlled` | 原API永久2+临时3@0.3→原Buff.reset→原loseStacks(1)→原gainStacks(1)→等原Timer；lose是否实际扣量由原局部值决定。只说明直接reset边界，不冒充自然回商店流程 |
| `lifecycle_natural` | 正常袋子局，原API永久2+临时3@60后等原疲惫终局；记录原Buff.combatEnd前后，走Game.switchToShop原路线并等延后Character.cleanse。确认同player实例后进入第二场，受控临时3@0.3→lose2→新增永久1→到期，观察旧永久残留是否影响新量；不设HP或胜负 |

跨状态只反转对真实容器的启动顺序，不额外创建Buff或倒序构造Character。香蕉/周期对齐可依据已测物理步修正受控duration，参数必须记录；不能修改原Timer/物品字段。10ms若只观测负delay连清，不证明提前容差，必须继续取得正delay对照或明确未覆盖。

### 2.3 多时钟、分支与真实通知

Timer内部处理可能先于Util更新。每行有递增观察序号，并列引擎物理帧`Engine.get_physics_frames()`、可用的idle帧（先has_method）、Util.frameCounter/time、combatTime，并记录Engine.iterations_per_second；不只用Util或四舍五入时间归同帧。

快照只读原Timer实例/路径/树索引/优先级/process_mode/wait_time/time_left/stopped，并标是否等于TIMER_PROCESS_PHYSICS。记录角色TickTimer、物品triggerTime/速度，以及Buff current、permanentStacks、每批amount/timeout/source instance和nextIndex；关键小数可额外用`%.17f`字符串保留读数精度。来源/原父事件/原事件ID、used/timeout/reflected等事实按实际值保存。

Buff.onTimeout在索引读取**之前**记录数组/index；取批后记选中对象，通知返回后、remove前再记index/数组；原delay计算后记录原局部delay及递归/启动路径。无效索引只读标记，不让观察代码先制造错误或替原算法越界防护。移除量读原`change`局部，不用通知后的总数差代替。

重入必须经原EventBus.connectEvent连接的真实状态通知，`on_stack_changed`只在指定负timeout事件内执行一次场景API。`observe`只读，不能在到期函数入口的观察钩子里加减数量冒充通知处理。来源为空不会创建成功通知，因此需要通知的初始临时批明确使用原来源皮包。

### 2.4 全部新增/修改函数接口与伪代码

**PowerShell：**

| 完整接口 | 伪代码 |
| --- | --- |
| 脚本入口`param([string]$RunId=<时间戳>,[string[]]$Cases=@('all'),[int]$RepeatCount=3,[int]$TimeoutSeconds=120,[switch]$PreviewOnly,[double]$EqualDuration=0.2)` | 校验ID/场景及边界，EqualDuration须有限且0<值<=1，写入case.equal_duration；固定E盘exe/指纹、无PCK选项，建立唯一证据目录，备份实际待改原字节并记基线。字符串生成prepared版本/diff/位置，PreviewOnly核原hash未变后退出；正常执行仅临时写project/Buff/Character/Item及必要输入，每场景新PID/隔离存档。收集多时钟、事件、错误、起止与状态；错误不阻断其他场景。finally逐项独立恢复源/输入/环境、停止本PID并重算全部清单SHA，不覆盖并发他人修改 |
| `Get-T0Hashes([string[]]$Paths) -> hashtable` | 只读逐文件SHA256，返回路径到值；不称全工程逐文件核验 |
| `Write-T0Utf8([string]$Path,[string]$Text) -> void` | UTF8无BOM写本轮证据或已备份的明确探针/输入目标 |
| `Add-T0Observation([string]$Text,[string]$Needle,[string]$Replacement) -> string` | 要求原标记恰1处，只替换为附加观察的文本，否则停止，不静默漏插/多插 |

**GDScript测试Node：**

| 完整接口 | 伪代码 |
| --- | --- |
| `_ready() -> void` | 读case，先独立落盘实际exe/3.6.2、Game1.1.8、原/观察版源SHA、隔离存档、flags/time_scale/物理步；不符则finish失败，不伪称加载了另一份工程 |
| `_process(_delta: float) -> void` | 原标题→商店→正常装盘/开战，处理场景超时、真实生命周期推进与截图退出；只调用原路线，不直接设Game状态/HP/胜负 |
| `_physics_process(_delta: float) -> void` | 按场景私有计划调用run_actions；延后阶段用原call_deferred，不动原Timer字段；只安排本轮允许的API |
| `setup_layout() -> void` | 用原物品库/Inventory重建规定袋子、来源别名及香蕉等场景物品；对手走原JSON输入；导出实际cells/实例/参数 |
| `add_item(name: String,x: int,y: int,f: int=0) -> Item` | 原实例化/定向/canAddItemOrBag/addItemByTopLeft，非法结束失败，返回真实Item |
| `start_case() -> void` | 连接Game.combat_start；在原prepare后、Character.combatStart前为基础组建立API起点/原通知监听。对齐组只登记计划，等原Tick/CD真正运行后再读余量，不读未启动0来安排 |
| `run_actions() -> void` | 根据case/帧和只读条件，逐条记录并调用原gainTemporary/gainStacks/use/lose/指定反射层/直接reset或原生命周期路线；所有数量/时长/来源写操作清单，不赋存储和计时器字段 |
| `on_stack_changed(amount: int,event: CombatEvent) -> void` | 从真实通知读取事件；只在指定负timeout首次执行场景use/lose/新临时gain或cap入站；私有标记防测试动作重复，记录前后；不伪造CombatEvent |
| `new_call_id() -> int` | 仅测试观察计数+1 |
| `observe(label: String,call_id: int,subject: Object,payload: Dictionary={}) -> void` | 读取原Buff/Character/Item和原局部payload，附全部时钟/来源实例/私有调用关联后输出JSON；不执行游戏行为，不抽随机数 |
| `snapshot(label: String,payload: Dictionary={}) -> void` | 只读选中原容器、批次、Timer、相关物品和游戏上下文，保存多时钟与实际值；不创建替代容器/计时器 |
| `capture(label: String) -> void` | 当前viewport取图并保存本轮PNG；称viewport截图，不把HUD或滚动日志画面当同调用实际量 |
| `finish(status: String,message: String='') -> void` | 保存原生events、终状态、截图、错误和覆盖情况；仅退出本PID，不判胜；未覆盖/原异常如实记录，不能只靠退出码判定机制 |

**原工程只读探针。签名保持原样，原return仅必要时等价展开：**

| 原函数接口 | 只读插入内容 |
| --- | --- |
| `Buff.gainTemporary(amount: int,duration: float,item=null,triggerEvent=null,reflect: bool=false)` | 入口/抵抗反弹/写组成/计时器启动选择/返回观察，保原全部公式、随机调用与事件顺序 |
| `Buff.loseStacks(amount: int,item=null,triggerEvent=null,used=false)` | 原截量/保护/永久与最远批选择、删批后index/实际返回观察，不修nextIndex |
| `Buff.changeCurrentLogShowLabel(isTimeout: bool,amount: int,item=null,triggerEvent=null,used: bool=false)` | 读取原change及写前后状态、原事件，保原同步通知顺序 |
| `Buff.onTimeout()` | 原索引读取前/选中批/通知前后/实际删除前后/原delay处观察，记录递归与wait路径，不包原错误成成功 |
| `Buff.reset()`；`Buff.combatEnd()` | 各函数入口/出口只读全部存储和Timer，记录真实调用上下文，不新增清理 |
| `Character.combatStart()` | 原TickTimer启动后标记真实启动状态与时钟 |
| `Character.combatEnd()`；`Character.cleanse()` | 入口/出口观察角色身份、Game上下文及相关原容器，区分自然终局/回商店与直接reset测试 |
| `Character.onTick()` | 入口/原局部regen或poison读值/出口观察，保原奇偶与调用路径 |
| `Item.trigger()` | 原真实冷却触发入口/出口、triggerTime/速度/本次物品参数，保原冷却调整与效果 |

Game/EventBus只读不改；不改Buff.init、Item._physics_process或preCombatStart，不构造额外假Buff来强定跨容器顺序。若确需新增函数或观察点，先补本文再实施。

### 2.5 恢复与完成标准

待改4文件为project.godot、Core/Buff.gd、Core/Character.gd、Items/Item.gd；Game、SteamHelper、CSV、原JSON、所选exe等均列实际核验清单。原字节备份仅少数文件，不建工程副本。原输入若缺失，恢复缺失。每个恢复段独立处理，崩溃/超时也不跳过；只停本次PID，不结束用户进程。

保留各轮prepared/diff/原行与插后位置、API操作清单、原始stdout/Godotlog/stderr、原事件、截图、进程起止及restoration.json。每轮另保存实际使用的两份小测试脚本及其SHA，便于参数校准后核对当时版本；这不是工程复制。最终独立重算清单SHA、检查原文件无本轮探针残留；明确实际核验路径数量，不称整工程哈希。结果按“已实测/原错误已触发/未覆盖”分类，再据证据更新二期SPEC的T0和可定的到期顺序；不顺带实现Python，也不将本工程重复观察外推成所有Godot初始化普遍规律。

## 3. Tasks（任务拆解）

1. [x] T1：固定19场景、参数、接口、受控/自然边界及元数据清单。
2. [x] T2（T1）：实现两脚本与字符串preview，独立审只读diff/位置，核未改原源；再实际启动验证身份/隔离。
3. [x] T3（T2）：执行基础、相同期限/10ms、真实容器/香蕉/周期组；按引擎帧判覆盖，同期限0.25秒及17位精度校准均留原记录。
4. [x] T4（T2）：执行真实通知重入、索引错误隔离、满cap前后、直接reset和自然生命周期两场；保留原回调错误、重复到期与跨场残留，不修机制。
5. [x] T5（T3/T4）：独立核原调用/状态/事件/时钟和重复结果，32进程均完成观察、无超时；恢复10路径原字节/环境/哈希，写结果报告并修订二期T0事实。二期T4设计仍待处理已证模型冲突，未实施Python。

## 4. Acceptance Criteria / Tests（验收标准）

- 实际E盘3.6.2/Game1.1.8/原项目和源SHA明确，time_scale1；无工程复制、PCK/exe变更或直接赋数量/Timer/HP/胜负。原API受控输入与自然物品/生命周期证据分别标注。
- 0秒有新Timer、完全停止后复用、仍运行三种状态，记录真实wait_time和调用到到期帧；纯复用不混入通知中加批。
- 相同期限按来源实例区分；10ms有原正delay≤0.01递归及>0.01重新等待对照，负delay或相同显示时间不能冒充。跨角色/状态反start重复只报告本工程原注册节点顺序。
- 对齐组确实等原Tick/CD运行后读余量；分别命中到期↔onTick和到期↔自然香蕉触发两对同引擎物理帧即可，不要求三者同一帧。给出各对实际先后；未相遇明确未覆盖，不凭计划时间推断。
- 重入来自真实EventBus负timeout通知，含消耗、普通移除和新增临时批两种插入序；选中/实际删除批及读数可核，观察钩子不改数量。索引两组保原错误和状态，不私加防护。
- 满cap前后原反射层API/真实随机draw保留，报告截量/反弹子调用与到期释放容量；后测新gain须与实际timeout减少同引擎物理帧且观察序号在其后，两次对照彼此不必同帧，不能把受控反射层称自然物品概率。生命周期有自然终局→回商店清理→同实例第二场的证据，直接reset另列。
- 多时钟、原事件/原错误、状态、操作输入与截图构成同轮证据链；所有待改字节/输入/环境恢复、清单哈希一致、本PID结束且无探针残留；二期只更新实证可定部分，不以T0实验冒称Python二期已实施。
