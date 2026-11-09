# Buff异常分支原引擎摆盘验证结果

2026-11-09。依据[实验SPEC](buff_engine_edge_verification_spec.md)。**两个异常均已在原引擎、真实物品摆盘中复现。**负left会增加专用抵抗层；满cap仅在反弹后仍有正剩余、再被cap裁0时丢失待反弹，全量反弹仍投递。本文记录机制观察，不修改模拟器。

## 1. 运行身份与启动边界

直接使用安装目录的`E:\steam\steamapps\common\Backpack Battles\BackpackBattles.exe`，Godot `3.6.stable.custom_build.de2f0f147c5b7eff2d0f6dbc35042a4173fd59be`；实例`Game.VERSION="1.1.8"`。实际资源根为工作区`Backpack Battles/`，没有复制工程或exe/bin。原exe SHA256：

`4522A5F2B71FE2AA5F7F730A2BD71F66F4F8112609164BCEF39C110F047AD577`

安装PCK仅在原目录暂改名，退出后恢复原名，前后SHA256均为：

`DB6748170C3173BB8C6A9B91370465BFC86FB30341A7A0DDC8BFC8D3381F4817`

先用MainLoop探针跳过autoload读加载源：未加启动features时，`editor/full_version=false`，工作区Buff SHA正确，Game.gd源码版本文本1.1.8；**这一步没有Game实例运行证据**。随后Node启动实际跑到标题/ItemBook，才完成实例版本验证。

临时启动配置使用`project.godot`顶层`_custom_features="full_version,editor"`；无下划线的`custom_features`曾实测无效。成功轮的实际`OS.has_feature("editor")/full_version`及`Game.EDITOR/FULLVERSION`均true，`disable_steam_integration=false`，没有使用第三tag。这是明确记录的原工程启动适配，会打开离线JSON入口、读取明文ItemData并跳过其编辑器资源校验，不声称等同未加features的零售启动模式。Game.gd未改。物品表明文MD5为`dc977faf19965650e7f462c6c9baeef9`，保留已核实的原解密来源，前后数据文件SHA均未变。

启动证据：[未加features的元数据](../data/buff_engine_edge/native_featureless_metadata_20261109_03/data/source_probe.json)、[成功smoke的实际ENV](../data/buff_engine_edge/native_underscore_smoke_20261109_06/data/smoke_environment.json)、[smoke结果](../data/buff_engine_edge/native_underscore_smoke_20261109_06/results.json)。每case的APPDATA/LOCALAPPDATA都指向本轮data内目录，实际user_data路径已打印；`Engine.time_scale=1`。

## 2. 负left：已复现并有两组对照

运行轮次：`native_negative_left_20261109_07`。己方4皮包铺4×4，Holy Armor三槽装Elephant Rune×3，Magic Mirror×5；对手仅皮包和Pocket Sand。所有物品由原ItemBook实例化、原Inventory校验/加入、原`addToSocket`镶嵌；对照只分别去掉镜子或符文。没有赋抵抗率、反弹率、层数或HP。

准备后实测抵抗率为120%，镜子总反弹率为**104%**，不是事前估计值。Pocket Sand在原开战回调自然施加Blind1；三组各用新进程和隔离存档。

| 组 | 实测抵抗率/反弹率 | 进入专用层前left | ownStacksUsed | 专用抵抗层 | 末己/敌Blind | 原生Blind日志 |
| --- | --- | --- | --- | --- | --- | --- |
| N：抵抗+反弹 | 120% / 104% | -1 | -1 | 0→1，末仍1 | 0 / 1 | event3：敌方+1、reflected=true；无原目标Resist事件 |
| R：仅抵抗 | 120% / 0% | 0 | 0 | 0→0 | 0 / 0 | event2：原目标resisted=true、amount1 |
| F：仅反弹 | 0% / 104% | 0 | 0 | 0→0 | 0 / 1 | event3：敌方+1、reflected=true |

N组同一自然施加的父调用`call_id=3`，`Util.time=5.5`、frame330（绝对工具时间；原战斗日志timestamp为0）：

```text
request=1, current=0, resistStacks=0
after_resist: resisted=1, left=0
before_own_resist: reflected=1, amount=0, resisted=1, left=-1
after_own_resist: ownStacksUsed=-1, resistStacks=1, resisted=0, left=0
parent success event=-1
reflected child call4(parent_call3): target1, request1, reflected入站
child native event3: target1, amount1, reflected=true, origin=Pocket Sand
```

这证明增加的是实际`resistStacks`，并非HUD误读；负own还把`resisted`抵消为0，所以原目标没有抵抗日志。子调用与原生成功事件配对，证明反弹实际投递。观察约7墙钟秒后，符文4秒计时自然结束，概率抵抗回0，而新增的专用抵抗层仍为1；没有把过期后的0%误当初始抵抗值。R/F均不增加专用层，排除了单独抵抗或单独反弹就会增加的解释。

原始证据：[N局部与事件](../data/buff_engine_edge/native_negative_left_20261109_07/data/N_overlap_verified.json)、[R对照](../data/buff_engine_edge/native_negative_left_20261109_07/data/R_resist_only_verified.json)、[F对照](../data/buff_engine_edge/native_negative_left_20261109_07/data/F_reflect_only_verified.json)、[全轮结果](../data/buff_engine_edge/native_negative_left_20261109_07/results.json)。各case的`*_godot.log`保留完整观察行，`*_combat.png/*_observed.png`是实际viewport截图；`fight_ended=false`，取证后退出本实验进程，没有人为判胜。

## 3. 满cap：已自然累计到10000并验证分支

运行轮次：`native_full_cap_20261109_08`。双方12皮包铺8×6、7个Deer Totem自然提供105%抗伤；攻击方8 Chili Pepper、17 Hawk Rune、1 Gigawatz，防守方1 Magic Mirror自然20%反弹。Hawk/Gigawatz自然施加Blind，Chili自然Heat加速；其治疗/净化也完整保留。没有种初始层、改概率、强写HP或改RNG。双方原25/25HP保持，实际到达目标Blind10000。

三种同场调用从原始`full_cap_godot.log`逐段复核，不只依据runner的PASS：

| 分支 | 父调用/Util.time/帧 | 原目标层数与分配 | 实际续发/原生事件 |
| --- | --- | --- | --- |
| 未满，Gigawatz部分反弹 | call85 / 12.416667 / 745 | current36，请求3，F1，剩2；原目标36→38、event181 | 子call86反弹1，攻方9→10；native event182，战斗timestamp6.883334、target0、reflected=true |
| 满cap，Gigawatz部分反弹 | call17487 / 213.950011 / 12837 | current10000，请求3，抵抗0、F2、剩1；before_cap amount1→after_cap0→cap_zero_return | 没有before_reflect_dispatch/exit或反弹子调用；原目标无成功Stack事件，已选中的2层反弹未投递；同帧原生日志战斗clock208.416678 |
| 满cap，Hawk全量反弹 | call17477 / 213.850011 / 12831 | current10000，请求1，F1使amount先0；没有before_cap/after_cap | 子call17478实际攻方0→1；native event36257，战斗timestamp208.316678、target0、reflected=true |

被抑制调用17487的实际局部值：

```text
after_resist: amount=3, resisted=0, left=3
before_own_resist: amount=1, reflected_count=2, left=1
after_own_resist: ownStacksUsed=0, amount=1, resisted=0, left=1
before_cap: amount=1, current=10000
after_cap: amount=0
cap_zero_return: reflected_count=2
关联parent_call=17487的子调用数=0
```

这不是“满层一律不反弹”：Hawk对照已证明全量反弹时amount先0，跳过cap判断，仍能进入续发。Gigawatz同场未满对照证明20%反弹确实能正常投递；异常调用还直接观测到F2，排除了“该次没roll中反弹”的解释。

取证截图战斗时钟为208.4秒，`time_scale=1`；TRACE的213.95是含启动前置的Util总时钟，不能当战斗时长。未保留独立进程计时器；按`full_cap_process.json`与`full_cap_exit.json`创建时间估算墙钟约230秒（含启动/收尾，非引擎测量）。最终原状态：守方Blind10000，攻方Blind3，双方damageResistance105，三个分支标志均true、fight_ended=false。取证后只退出本实验进程。

证据：[全轮配对结果](../data/buff_engine_edge/native_full_cap_20261109_08/results.json)、[原始机制/事件日志](../data/buff_engine_edge/native_full_cap_20261109_08/data/full_cap_godot.log)、[实际ENV](../data/buff_engine_edge/native_full_cap_20261109_08/data/full_cap_environment.json)、[目标viewport截图](../data/buff_engine_edge/native_full_cap_20261109_08/data/full_cap_observed.png)。截图独立核见10000Blind、105%图标及双方25/25HP；HUD/渲染帧不代替同调用字段与事件配对。

## 4. 探针、恢复与证据范围

只临时修改两份原工程文件与摆盘输入；全部原字节备份到每轮`original_bytes/`。观察者代码在外部`tests/buff_engine_edge_battle.gd`，元数据脚本在`tests/buff_engine_source_probe.gd`，唯一runner为`tests/buff_engine_edge_run.ps1`。

| 原工程位置 | 临时变更/插桩后位置 |
| --- | --- |
| project.godot原config_version行9之后 | `_custom_features`行11；autoload新增行470，首位观察者 |
| Buff.gd::gainTemporary原79之后 | local ID及enter观察，行80–81 |
| 原98之后 | after_resist，行101 |
| 原128之前、131之后 | before/after_own_resist，行131、136 |
| 原147前后、148提前return处 | before_cap/after_cap/cap_zero_return，行152、154、156 |
| 原192之前、196之前 | before_reflect_dispatch/exit，行201、206 |
| data/custom_opponent.json | 原有JSON输入协议给定对手摆盘，结束恢复原字节 |

完整[Buff增量diff](../data/buff_engine_edge/native_negative_left_20261109_07/buff_observation.diff)、[project增量diff](../data/buff_engine_edge/native_negative_left_20261109_07/autoload_observation.diff)、[插后位置清单](../data/buff_engine_edge/native_negative_left_20261109_07/probe_locations.json)可核查。Buff仅加局部观察ID及只读JSON输出，原cap内联return等价展开；未改公式、比较、随机调用、物品参数或事件创建。observer不调用RNG、give/lose、emit、spawnLabel或createEvent。原有视觉/物品行为照常运行，不宣称跨启动模式完整seed轨迹相同。

满cap使用同一观察代码与行位，另存本轮[Buff diff](../data/buff_engine_edge/native_full_cap_20261109_08/buff_observation.diff)、[project diff](../data/buff_engine_edge/native_full_cap_20261109_08/autoload_observation.diff)、[探针位置](../data/buff_engine_edge/native_full_cap_20261109_08/probe_locations.json)，可与本轮原字节备份对应。

恢复校验的关键SHA256：

| 文件 | 原始及恢复后SHA256 |
| --- | --- |
| project.godot | `2BAC91BCF55A46A2FF8527A2B672692CB26C67CA38780E129EEBC5B5D6A707DD` |
| Core/Buff.gd | `3EFABB72EB0B337E30EBC924347ABA40BD1039A3C5F718B761B0EE78B48AB8BB` |
| Core/Game.gd（未改） | `F3688BFDF39B95A8ED6A77D9A7AD058A95A0AAA4BCB6D297BC953425ADD4B9C9` |
| ItemData.csv（未改） | `26F5433CF37CD33C066DD505672FCB292E7570EDE8C823C5A10F9BC21208A473` |

成功轮实际加载的**观察版**Buff SHA为`9235A31207A7595EE7B574C20F94B94BA659877AD5B14D673FC730669EE10D0D`，不能与未插桩原SHA混称。恢复核验范围共10个文件：project、Buff、Character、Game、SteamHelper、ItemData.csv、ItemData_e.csv、原JSON、exe、PCK；完整逐文件前后值在各轮manifest。

| 保留轮次 | 结果/恢复证据 |
| --- | --- |
| native_source_20261109_02 | 启动失败，非机制证据；[恢复一致](../data/buff_engine_edge/native_source_20261109_02/restoration.json) |
| native_featureless_metadata_20261109_03 | MainLoop源元数据通过；[恢复一致](../data/buff_engine_edge/native_featureless_metadata_20261109_03/restoration.json) |
| native_feature_smoke_20261109_04 | 启动失败，非机制证据；[恢复一致](../data/buff_engine_edge/native_feature_smoke_20261109_04/restoration.json) |
| native_early_env_smoke_20261109_05 | 记录无下划线features无效；[恢复一致](../data/buff_engine_edge/native_early_env_smoke_20261109_05/restoration.json) |
| native_underscore_smoke_20261109_06 | 实例smoke通过；[恢复一致](../data/buff_engine_edge/native_underscore_smoke_20261109_06/restoration.json) |
| native_negative_left_20261109_07 | N/R/F通过；[恢复一致](../data/buff_engine_edge/native_negative_left_20261109_07/restoration.json) |
| native_full_cap_20261109_08 | 自然10000层、三类同场证据通过；[恢复一致](../data/buff_engine_edge/native_full_cap_20261109_08/restoration.json) |

上述restoration均为`unchanged=true/errors=[]`，各轮`package_move.json`记录原PCK原名/SHA恢复。早先已删除的复制工程和失败日志不在证据链，也不声称仍保留。现存测试与证据目录不是工程副本。

收尾时再次按最终轮10项before清单独立重算原文件SHA，零不符；安装目录PCK只有原名，原游戏进程数0，原project/Buff没有本轮探针残留。外部tests与data证据保留，原工程文件及原输入按原字节恢复。

结论限定于给定物品集合、该1.1.8解包机制与原exe运行；多Unique/跨职业构造摆盘用于受控战斗验证，不宣称普通商店run一定可取得这些数量。两异常已由实际局部值、状态、原生事件和对照确认；没有顺便验证所有Buff/临时批次异常。无种层、无概率/HP/RNG注入，未实施此前Buff对齐或宝石方案。
