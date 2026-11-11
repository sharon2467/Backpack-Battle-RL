# 自然物品到期重入引擎实验结果

2026-11-10 · **自然同步重入、断链对照和自然错删均已实证，原工程已恢复。**依据[实验SPEC](buff_natural_reentry_engine_spec.md)，真实物品链在旧Spikes到期通知内新增临时Spikes；N6又在原随机顺序下复现选中短批却删掉长批、同一短批重复到期。没有测试代码直接给层或调整随机结果，Python未实施。

## 1. 运行与自然摆盘边界

“自然”限定为合法格位、Reaper职业匹配下，战斗层数和计数由真实物品产生；暖身仅通过原流程获得生命，不证明第2/5回合的商店采购可达，本轮不审核局外获取。

有效轮为[natural_20261110_02](../data/buff_natural_reentry/natural_20261110_02/results.json)，linked/unlinked各独立PID，59.0639452/57.9591939墙钟秒退出0、无超时。实际E盘GodotSteam`3.6.2-stable (custom_build)`、Game1.1.8、60Hz、time_scale=1；[linked环境](../data/buff_natural_reentry/natural_20261110_02/natural_linked_default_1/environment.json)、[unlinked环境](../data/buff_natural_reentry/natural_20261110_02/natural_unlinked_default_1/environment.json)分别保存exe和原/观察版源指纹及隔离路径。exe SHA256为`100B76E344A040D2CA50D1B4D03B097A259C35B32D5865043F33486A666EDA1C`；不是零售3.6.0运行证据。

原工程不复制，不动安装PCK/exe；正常选择Reaper，首场纯袋自然疲惫结束、原商店清理后第二场摆实物。同Character49678由首场HP25自然到第二场基础35；没有测试代码调用gain/use/lose、补命中、改计数、设HP或干预RNG。

原布局观察304核实Toad三物品星位、两Fanny内的蓝莓/Toad；linked的Mana Potion在(2,4)连Strong Potion，unlinked仅改到(7,3)，其影响数组为空。所有摆放通过原API；两组分别实际满足相同关键前置，不依靠相同随机轨迹作假设。

[首轮两进程](../data/buff_natural_reentry/natural_20261110_01/results.json)均在第二场JSON写后SHA核验失败，退出1、未超时，未测到目标机制。文本往返改变了换行字节；[输入恢复证据](../data/buff_natural_reentry/natural_20261110_01/input_recovery.json)逐字节确认唯一CR去除产物后恢复原备份。有效轮改用原字节buffer传递，实际切换SHA相符。累计基础阶段4个PID，2个输入失败、2个有效，不把失败尝试算机制反证；修复没有调整物品/RNG。

## 2. 原调用证据

### 2.1 自然重入与断链对照

| 检查 | linked | unlinked |
| --- | --- | --- |
| 首场自然终局、商店清理、第二场基础HP≥35 | 观察2/frame331的25→306/frame2131的35，同角色实例 | 同角色自然25→35 |
| HC正常用Regen7，Hungry前两击至少一次正常命中并用Regen1 | 原事件15@0秒用7；22@1.616667、32@3.15各用1，Toad累计9 | 原事件与实际used9同样可核 |
| 旧Spikes到期前状态 | 观察560/frame2371、战斗3.983334：Toad used9/Mana9/CrownInactive/Mana Potion满/Strong Potion空 | 观察560/frame2371、战斗3.983334同样全部满足 |
| 旧Spikes−2 → Toad → Crown实际消费 → Mana Potion | 原事件56旧Spikes−2；57/58 Toad给Luck/Mana；59无敌，60实际消耗Mana10；61 Mana Potion给Mana4 | 55旧Spikes−2；56/57 Toad；58无敌；59实际消耗10（观察580）；60 Mana Potion给Mana4 |
| 同一Buff、旧timeout未返回/未删批时新临时层 | oldcall169/Buff50552/旧批151751；同frame2371观察601的gain177追加新批152185，来源Strong实例134103、2层/4秒；602原Timer启动，612才旧remove前、613删旧留新，原事件65 parent为空 | oldcall169/旧批151972；观察597删前仍仅旧批，598清空；9秒内只有初始一次gain_batch_added，嵌套新增0 |

上述调用与事件均来自各自原记录：[linked原结果](../data/buff_natural_reentry/natural_20261110_02/natural_linked_default_1/result.json)、[linked stdout](../data/buff_natural_reentry/natural_20261110_02/natural_linked_default_1/stdout.log)、[unlinked原结果](../data/buff_natural_reentry/natural_20261110_02/natural_unlinked_default_1/result.json)、[unlinked stdout](../data/buff_natural_reentry/natural_20261110_02/natural_unlinked_default_1/stdout.log)。linked新批随后确于call218/frame2611自然到期，相距240个物理帧；unlinked最终Spikes0、临时空。

判定不只依赖脚本observed标记：独立核实了同一个满足前置的旧调用、同Buff实例、旧批仍在、Strong同实例、实际2层/4秒，以及旧remove之前的真实调用祖先。原Potion连接省略父事件，故新原事件65的parent为空；这里以调用栈和批次身份证明嵌套，而非相同时间戳或父字段。

### 2.2 N6：自然选中短批却删掉长批

[N6运行](../data/buff_natural_reentry/wrong_remove_20261110_01/results.json)首个PID即命中，没有重试，150.0928886墙钟秒退出0、无超时或SCRIPT ERROR。原角色49678经历4场纯袋自然疲惫终局后到第5场，实际基础HP为25/35/45/55/70，主场70，满足SPEC最低65门槛。实际环境仍为同E盘3.6.2/Game1.1.8、60Hz/scale1。

完整原记录见[N6 result](../data/buff_natural_reentry/wrong_remove_20261110_01/natural_wrong_remove_default_1/result.json)及[stdout](../data/buff_natural_reentry/wrong_remove_20261110_01/natural_wrong_remove_default_1/stdout.log)。下列A是(2,2)的Strong Potion实例166590，B是(4,4)的实例166553；Time Melting实例132376只延长B。每进程编号独立，不与基础组同值编号混用。

| 观察 | 实测事实 |
| --- | --- |
| 合法主布局与自然初始顺序 | 布局1210中A/B/Time及影响格正确。B原事件7先建立Spikes2@6.2（批188275/index0），A原事件9后建立2@4（批188295/index1）；保留了原shuffle |
| 目标到期前置 | call508/Buff50552，frame7770、战斗3.983334：Toad used9/Mana9/CrownInactive/Heat5，Mana Potion满、两Strong已空，选中旧A188295 |
| 自然重入 | 同frame7770观察1528，gain516新增A批188767、2层/4秒，旧call508未退；1529原Timer启动使next从1变0 |
| 实际错删 | 1539原选中仍是旧A188295，实际remove候选却为B188275；1540前列表[B、旧A、新A]变成[旧A、新A]，只有B消失 |
| 重复扣同一批 | frame7771、call517再次选旧A188295并实际扣2；原事件62@3.983334与74@4.000000均为同源旧A的timeout−2 |
| 中段状态与长批缺失 | 观察1566/frame7830、战斗4.983334只剩新A188767，总Spikes2，B原6.2秒期限尚未到；观察1663@6.216667已过B期限仍只有新A，完整记录中无B timeout |
| 最后新批到期 | frame8010/call562，新A188767实际扣2，原事件112@7.983334；最终Spikes0，不能因此否定此前错删与重复扣量 |

“若未错删，4至6.2秒间B2与新A2都仍有效，应有4层，因此中段少2”是按批次规则作的推断；本轮没有另外取得同摆盘正常插序样本，也没有测量由此造成的胜负分歧。实证本身是批ID差集、旧A重复扣2、B未到期却消失，以及中段实际只剩2。

## 3. 结论及未验证范围

**已确认：自然物品链能在旧Spikes到期通知内新增同角色同类型临时层。**Toad将真实负timeout计入used，Crown的实际消耗又触发药水连接；不需要测试代码直接给层。断开连接的自然对照达到同一前置却没有新增，支持该因果链。

N6独立补齐了**战斗自然可达的错删与重复到期**。两瓶同数量时最终仍归0，本轮没有证明新的最终总数残留或胜负分歧，也不把这种异常推广到所有临时层。二期按对象删除、实时求和的草案与这条原行为不同；实现取舍仍需明确，不能称内部不同但可观察结果等价。本轮不改Python或添加第二总账。

## 4. 探针与恢复

先审核[预览](../data/buff_natural_reentry/preview_20261110_01/restoration.json)，四原文件prepared SHA与T0完全相同；新增的是测试流程及只读私有因果记录。有效轮保留[Buff差异](../data/buff_natural_reentry/natural_20261110_02/Buff.gd.diff)、[Character差异](../data/buff_natural_reentry/natural_20261110_02/Character.gd.diff)、[Item差异](../data/buff_natural_reentry/natural_20261110_02/Item.gd.diff)、[autoload差异](../data/buff_natural_reentry/natural_20261110_02/project.godot.diff)和[全部探针位置](../data/buff_natural_reentry/natural_20261110_02/probe_locations.json)。原位置与11函数见[T0报告](buff_stage2_t0_engine_results.md)，没有新增Potion或Game机制probe。

每轮保存当时两份测试脚本、[脚本SHA](../data/buff_natural_reentry/natural_20261110_02/test_scripts_sha256.json)、两份对手输入、原/观察版源SHA、原事件、布局/自然随机结果、进程起止和viewport截图。截图辅助真实界面，实际量与同步结论依原调用记录。

N6另经[字符串预览](../data/buff_natural_reentry/preview_n6_20261110_01/restoration.json)审核；原四文件probe内容仍完全复用。[N6位置清单](../data/buff_natural_reentry/wrong_remove_20261110_01/probe_locations.json)、[测试脚本SHA](../data/buff_natural_reentry/wrong_remove_20261110_01/test_scripts_sha256.json)与全部prepared/diff保存了该次版本，没有覆盖02。

[统一清单](../data/buff_natural_reentry/execution_summary_20261110.json)分列累计5个PID：2个早期输入错误，3个有效自然case；没有把输入错误算机制反证。[02恢复](../data/buff_natural_reentry/natural_20261110_02/restoration.json)与[N6最终恢复](../data/buff_natural_reentry/wrong_remove_20261110_01/restoration.json)均unchanged=true、errors为空。最后再次独立重算当前10路径，全部匹配，0探针残留、0GodotSteam进程。清单为project/Buff/Character/Item、Game、SteamHelper、明文/加密ItemData、原custom_opponent.json、所选exe，不称整工程逐文件核验。首轮换行失败的补充恢复证据另列，未隐藏自动守卫拒绝恢复后的原字节核验过程。
