# Buff二期T0引擎实验结果

2026-11-10 · **T0实验完成，Python二期未实施；到期设计仍需修订。**依据[实验SPEC](buff_stage2_t0_engine_spec.md)，完成19组、32个独立进程，并独立复核原调用、事件、实际引擎帧和恢复结果。原索引异常、计时器等待和同帧先后均已取得证据，不能将当前求和模型称为原版全部行为的等价实现。

## 1. 运行与证据边界

启动检查见[实际环境](../data/buff_stage2_t0/smoke_20261110_01/smoke_default_1/environment.json)及[运行清单](../data/buff_stage2_t0/smoke_20261110_01/results.json)：实际exe为`E:/godotsteam/godotsteam.362.editor.win64.exe`，SHA256 `100B76E344A040D2CA50D1B4D03B097A259C35B32D5865043F33486A666EDA1C`；引擎`3.6.2-stable (custom_build)`、Game1.1.8、60Hz、time_scale=1。OS.editor=true、OS.full_version=false，Game.EDITOR/FULLVERSION均true；未新增启动feature配置。实际存档路径落在该次case的appdata下，加载的三份观察版源SHA与输入清单相符。该启动进程48.4897797秒退出0，未超时；[10路径恢复清单](../data/buff_stage2_t0/smoke_20261110_01/restoration.json)前后相同、errors为空。

原工程不复制、PCK/exe不改；各场景操作仅由原API驱动，观察钩子只读。0秒、数量、期限、移除、重入、直接reset及反射层由受控原API安排，不称自然摆盘；原注册Timer、香蕉触发、角色Tick和疲惫终局→商店→第二场则沿真实流程。双方仅皮包，调度组额外放香蕉，无鹿图腾/攻击物品；没有直接设置层数存储、Timer字段、概率、随机数、HP或胜负。

场景数为19组、20个基础输入变体；加上重复、同期限校准和启动检查，共32个独立进程：smoke1、basic9、schedule14、edge8。[统一清单](../data/buff_stage2_t0/execution_summary_20261110.json)记录全部正常退出、无超时和指纹失败；唯一SCRIPT ERROR来自预期的`stale_far_first`原数组索引。退出0表示观察窗口完成，不表示原机制没有异常。Buff及TickTimer实际mode=0、is_physics=true；物理帧与Util/战斗时钟分别记录，按实际引擎帧判断同帧。

[基础9输入](../data/buff_stage2_t0/basic_20261110_01/results.json)、[调度14进程](../data/buff_stage2_t0/schedule_20261110_01/results.json)及[边界8进程](../data/buff_stage2_t0/edge_20261110_01/results.json)的各case均保留result.json、stdout、原生事件及脚本版本，以下事实均经独立复核。表中current为原总量、permanent为原永久量；call为只读观察的调用编号，native为原生事件编号，不跨进程混用。

## 2. 分组结果

| 场景 | 状态/关键证据 |
| --- | --- |
| zero_fresh / zero_reused / zero_running | 已读原记录：新Timer加0秒沿用wait_time=1，frame338→398，共60帧；完全到期后下一帧复用，沿用0.1秒，frame348→354，共6帧。运行中追加0秒则沿用0.3秒并改选后插批，frame360先B、361再A。0秒是临时存储、普通增加事件，不等于立即到期 |
| equal_forward / equal_reverse | 0.2秒两组第二次增加实际重启Timer并置next_index=1，均先后插批、下一帧再旧批。补跑17位精度时，第二次duration为0.20000000000000000，Timer余量为0.20000000298023220，确实满足原严格小于条件；不推测底层存储原因。另在[schedule校准](../data/buff_stage2_t0/schedule_20261110_01/results.json)用0.25秒，两值相等、未重启Timer，正插先A、反插先B，下一帧处理另一批。结论取决于实际重启分支和已有next_index，不能只按较粗显示的同期限认定一般先入先出 |
| tolerance_inside / tolerance_outside | 已取得正值两侧：0.008333秒走递归，父call5内子call7同frame346、子先返回；0.043333秒重新等待，父frame348返回，frame351另起call7处理后批。前者满足提前不超过10ms的真实门槛，不只是两个显示时间相同 |
| cross_start_forward / cross_start_reverse | 正反启动各3进程，均先player1 Lucky→Empower，再player0 Lucky→Empower（观察43/53/63/74，native4–7）。启动API顺序没有改变这次原注册Timer的处理先后；结论只限本工程当前初始化，不声称普遍创建规律 |
| phase_physics / phase_deferred | 两种安排阶段各3进程，全部命中到期↔角色Tick、到期↔真实香蕉这两对。首物理安排进程引擎帧400角色onTick先读Regeneration1并调用heal(1)/native2，再到期/native3；这不表示满HP时生命实际增加1。帧634 Lucky先到期，再香蕉真实trigger。末延后安排进程分别帧396/623，同样先后。同一引擎帧内Util/战斗时钟可能相差一步，不能据此误判异帧 |
| reentry_use / reentry_lose | A到期先使总6→4（event3），通知时旧A仍在列表。消耗1先扣永久1，总3，剩B3随后到期；普通移除2先扣永久1再扣B1，总2，剩B2随后到期。native4分别used=true/false、父事件3；两组最终均0，负到期事件的实际−2未被回调重写 |
| reentry_gain，正反变体 | 正插最终总1/永久1/临时空。反插先选A批116088/index1；通知新增C时原Timer启动将index改0，frame343实际删掉未到期B116081；frame344同一A再次到期（native3/5均A−2），C到期后最终总2/永久1/临时空。已证实原索引异常会改变可见总量，按对象先删批的求和模型不能称与之等价 |
| stale_far_first / stale_early_first | 先远后近时，普通移除删B/index0后只剩A2但next仍1；frame638、战斗4.983334原onTimeout读取数组index1发生SCRIPT ERROR，没有到期事件或后续清理。角色Tick仍继续，7秒末总2/A2仍在、Timer停止：这是原回调错误，不是进程崩溃。反插对照next0，frame638正常到期/native3−2，最终0、空批、无该错误 |
| cap_expiry | 满10000时call3剩余2被裁0，不再反弹；到期frame352原减少1→9999/event2，真实通知内同frame352的call8取得1层/native3，call9向对手反弹1/native4，父事件均2；最终目标10000。已证明同帧先释放再施加改变满层吞反弹分支；反射次数来自明确原API夹具，不称自然物品效果 |
| reset_controlled | frame339原reset使current5→0，却保留永久2、临时3和运行中Timer；随后lose1实际0，再加永久1后current1/permanent3。frame357旧临时批到期，原actual取1，native3 timeout−1；最终current0/permanent3/临时空。已见直接reset残留影响新数量，仍不代替自然回商店证据 |
| lifecycle_natural | 首场原疲惫在战斗23秒自然终局。同Character49677/Buff50553/Timer50554贯穿两场：combatEnd观察258/259保留总5/永久2却清临时3并停Timer；商店reset307/308归总0、永久仍2。第二场临时3进后总3/旧永久2；lose2消旧永久而留临时3，再加永久1后总2/永久1/临时3；frame2157原actual取2、native3 timeout−2，最终总0/永久1/临时空。首场16事件已存档。第二场玩家HP自然变35/35，非全程HP25；测试未赋HP |

## 3. 二期可据此确定的规则

回写[二期SPEC](buff_stack_stage2_spec.md)的是以下约束，不是已完成的Python到期算法：

- 不能只按批次名义期限处理：原0秒沿用Timer默认或保留的wait_time；原重启比较也会改变选中批。同类型首次到期后确有正值≤0.01秒的递归提前处理，不能扩成跨状态统一合并。
- 已测同帧先后是`Character.onTick`在相遇的Regeneration到期之前、被测香蕉在相遇的Lucky到期之后。Python的`_apply_system_triggers`还混有疲惫，不能整体前移或后移就称所有Timer已对齐；其他物品、初始化顺序和疲惫同帧位置没有由本实验普遍证明。
- 满层时先到期释放容量，确实改变后续裁量和反弹；通知回调中的加减有真实同步效果，不能用通知结束后的总数差重算原事件。
- 先按对象删批并实时求和，可以避免错索引，但不会复现本轮已证的错删、重复到期或“总量不等于组成和”。自然生命周期的旧永久残留同样已证。当前“不存独立总量、新战斗新角色”的项目设计与这些原行为存在明确差异；不能称只是私有实现不同，更不能悄悄增加第二总账来掩盖。

因此T0实验完成，T4到期设计尚未定稿：需要明确计时器等待/选批和循环阶段，以及如何界定上述异常的实现范围。本轮不另造调度框架，不仿原错误中断，也不把受控场景或GodotSteam3.6.2结果外推成零售3.6.0全部行为已等价。

## 4. 探针、恢复与限制

先做[字符串预览](../data/buff_stage2_t0/preview_20261110_01/restoration.json)，原工程未写入；独立审核后才实跑。原函数仅附加只读观察和必要的等价返回展开，没有改Timer操作、公式、随机调用、原索引或分支。四个临时改点如下，原行号均对恢复后的文件；插后行号见[位置清单](../data/buff_stage2_t0/edge_20261110_01/probe_locations.json)。

| 原文件/位置 | 探针与差异 |
| --- | --- |
| `Backpack Battles/project.godot:466` | autoload首位加外部T0Probe，[启动差异](../data/buff_stage2_t0/edge_20261110_01/project.godot.diff)；无启动feature改动 |
| `Backpack Battles/Core/Buff.gd:52,76,199,283,317,342` | reset、gainTemporary、loseStacks、changeCurrentLogShowLabel、onTimeout、combatEnd，[Buff差异](../data/buff_stage2_t0/edge_20261110_01/Buff.gd.diff) |
| `Backpack Battles/Core/Character.gd:328,338,349,401` | combatStart、combatEnd、cleanse、onTick，[角色差异](../data/buff_stage2_t0/edge_20261110_01/Character.gd.diff) |
| `Backpack Battles/Items/Item.gd:4409` | trigger入口/出口，[物品差异](../data/buff_stage2_t0/edge_20261110_01/Item.gd.diff) |

每轮保留实际prepared版本、位置、源原字节、两个小测试脚本与SHA、输入、隔离存档、原始stdout/Godotlog/stderr、原事件、进程起止/退出码和viewport截图。最终轮[测试脚本指纹](../data/buff_stage2_t0/edge_20261110_01/test_scripts_sha256.json)固定了本轮driver；早轮版本仍在各自目录，未用后续校准覆盖。截图仅辅助真实界面，逐次实际量、错误和同帧结论依原记录。

四轮[smoke恢复](../data/buff_stage2_t0/smoke_20261110_01/restoration.json)、[basic恢复](../data/buff_stage2_t0/basic_20261110_01/restoration.json)、[schedule恢复](../data/buff_stage2_t0/schedule_20261110_01/restoration.json)、[edge恢复](../data/buff_stage2_t0/edge_20261110_01/restoration.json)均unchanged=true、errors为空。实际核验10路径为上述4文件、Game.gd、SteamHelper.gd、明文/加密ItemData、原custom_opponent.json及所选GodotSteam.exe；不是整工程逐文件哈希。结束后再次独立重算当前10路径，全部与基线一致，原源无探针残留，隔离环境/JSON恢复，没有GodotSteam残留进程；不动安装PCK或exe内容。

**后续自然摆盘补测：**[真实物品重入与错删报告](buff_natural_reentry_engine_results.md)另用GodotSteam3.6.2/Game1.1.8，证实原物品链可在到期通知中新增同角色同类型临时Spikes，继而在原shuffle下选A却删B、同旧A重复到期。本报告原`reentry_gain`等用例仍是受控API实验，不能改称自然。补测只证明合法摆盘下战斗效果可达，不证明第2/5回合采购可达，也未验证胜负分歧；最终归0不掩盖中段状态异常，不将其混称零售3.6.0已测。
