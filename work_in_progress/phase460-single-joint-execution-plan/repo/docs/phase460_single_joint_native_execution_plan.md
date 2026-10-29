# 单次 King＋基础黏黏原版记录：最小执行方案

状态：方案和必要源改动已独立审查；462隔离源码实现、463定向测试准备继续。**尚未安装到采集池、启动解析或战斗；不是READY/运行放行回执。** 只需一盘固定26物品联合记录，不重跑旧通过案例，不进行GUI或生产seed位级审计。

## 1. 复用的原版程序和环境

沿用原执行环境、只读基线`/workspace/godotsteam-startup-20261013/baseline/Backpack Battles`和固定池`/workspace/native-combat-20261013/pool`。GodotSteam3.30.2/Godot3.6.2/Steamworks1.62及现有离线运行包装不升级，不创建环境/容器/完整Game副本，不改变网络、安全或凭据配置。

2026-10-29 05:59:43 UTC只读核对当前引擎：`/workspace/godotsteam-startup-20261013/engine/godotsteam.362.editor.x86_64`，77,646,552字节，SHA256 `09d1de6c4f97289c018556666c13c1d81093a5df5c2255725d464a87f40a8ea1`，与既有证据一致；原版Goobert.gd、KingGoobert.gd、Item.gd也已读回留SHA。该有限检查不等于全池物理校验/READY；安装前仍用现有gate核实际前驱、preimage和空间，不重做历史恢复研究。

## 2. 修改面、观察器纯度和回滚

当前462只新建隔离文件：`tests/phase462_prepare_joint_observer_source.py`和`data/phase462-joint-observer-source/`下collector、sink、schema、26槽计划、source tuple、native patch/逆向/安装清单。原版基线、旧391/441/451/458/459及公开461运行包不改。后续需窄更新新host的case/tuple门、初态输入桥与captured模型/比较绑定，不改旧路径以兼容新case，也不放宽公开Source的Tape禁入。

将来池安装沿既有75个patch路径＋3个artifact（预计78目标）；完整参考路径集合在`planned-target-paths-reference.json`。相对391预计改变内容的安装项仅：`native_random_observer_sink_v7.gd`（23→goobert状态、7元数据、新26身份/profile）、`native_combat_capture.gd`（固定新布局/配置/白名单）、`native_capture_config.json`（case/固定原生seeds）。其余原版变换文件/project/marker预期字节守恒。**最终路径、每项SHA、确切总字节必须由462新清单冻结；旧78/815198不是新测量。若修改面扩大，先复核。**

观察器的新增内容只读计数/阈值/身份并序列化；schema校验也须将23识别为基础Goobert，262仍为King。沿用原107钩子站点，Goobert的重置→effect→activate→回入后trigger/history原方法和返回形式保持。不得增加业务字段写入、RNG调用、业务事件或重排监听者。462精确delta/inverse和463独立静态＋type/binding控尚须通过，不能仅凭“只读”命名宣称纯度完成。日志开销可能影响实际idle节奏，因此保留完整实际frame_clock，不要求复制旧墙钟节奏或Source459结果。

回滚用现有storage的两层保全：`reset_previous`先备份并校验实际旧patch/marker及inventory，再恢复基线；`install`在所有载荷/目标前置检查通过后，先备份每个实际preimage、mode、mtime并fsync `preimages.json`，再atomic replace且核安装后SHA。基线始终不写。失败立刻停并保留旧patch备份、新安装journal和半成品，禁止盲重装/自动再采。需要恢复时按已验收恢复机制及实际新journal做精确恢复、独立物理读回后才能另行READY；不把源码inverse当成运行态已回滚，不把exit0当干净退出。此方案未执行回滚。

## 3. 固定一盘26物品与业务目标

原生case提案`NATIVE-028-KING-BASIC-A`，run提案`original028-king-basic-A-single-001`；固定global_seed45701/util_seed45702。这是独立原生配置，不是Source459的域派生双流，不要求相同胜者/事件数/随机值。不换seed、不按结果改摆盘。

双方class0/defaults/stamina5；P HP240、O HP260。双方各6皮包，共同坐标(0,0),(2,0),(4,0),(0,2),(2,2),(4,2)，rotation均0；包先插入。其余如下：

| 侧/原生身份 | 物品ID | 坐标 |
| --- | ---: | --- |
| P:6 King |262|(2,0)|
| P:7 Basic |23|(4,0)|
| P:8..11 Blueberries |22|(1,0),(1,1),(1,2),(4,2)|
| P:12..13 Sword |1|(0,0),(0,2)|
| O:6..7 Sword |1|(1,0),(3,0)|
| O:8 Buckler |4|(0,2)|
| O:9 HealthPotion |19|(4,0)|
| O:10..11 Blueberries |22|(2,2),(3,2)|

与预封457/459输入逐槽对应，P14/O12；P:12现在是剑，不能沿用旧固定盘KingP:12。需要证明：基础5次/King6次激活计数、先reset再effect再同步activate、King↔Basic回入后计数重读，heal/protection/Mana/无敌及Timer/RNG顺序，事件显式父链、tooltip关联和history压缩，以及全战斗终态。已有Source双向小控；完整Source仅自然命中King-first外层trigger5。原版按实际HIT/NOT_HIT记录双向、无敌/Mana、limiter/death分支，不伪造命中、不为补命中重采。

## 4. 预期启动数、耗时、停止与空间

Source准备/合成校验不启动原版。若后续获得具体安装/运行放行且gate通过，现有host机制是**1次Godot解析检查＋1次原版战斗进程**（解析失败则战斗0次）；没有第二盘、seed探针、版本探针或复跑旧案。后续INPUT验收后才另作1次新的Tape Python模型和严格比较；不重用459 Source输出作为预测。

既有401参考native-active103.235秒/host142.949秒；新盘预计同量级约2–3分钟host，**不是保证**，Source准备/验收耗时另计。battle120秒、collector295秒、runner300秒硬停。首个解析/协议/输入/资源/时间/语义错误即保留停止，不自动重试。原生未命中目标分支是覆盖限制，不是重采许可。

既有阈值：4GiB free floor＋1536MiB attempt reserve，启动前至少5,905,580,032字节。05:59:43实际free5,981,224,960字节，**仅多75,644,928字节（约72MiB）**，所以最终Source冻结后、安装前必须再次读实际空间；低于阈值不启动。不得清理unique材料或新建Game副本。observer≤300000条、单条2MiB、总256MiB；host≤64文件/512MiB，stdout/stderr总32MiB，run/user/cache总1536MiB，50ms监控。它们是writer/轮询限额，非kernel aggregate quota，可能有轮询超调。最终安装字节cap等462冻结，不能沿用旧数。

## 5. 原始记录、输入/输出隔离和哈希

单独的新run/user/XDG/cache/tmp路径；固定基线/池复用，旧原始记录/错误现场保留。启动前固定新producer/sink/collector/schema/host/请求/patch清单的size/SHA与只读资源pins；未知原生ID/flags/lifetime/order/clock/Tape不预填。

捕获后保留未经裁剪的raw日志、12类输入载荷、预期输出、诊断/进程状态、实际源/安装/前驱journal和全部文件size/SHA；失败也保留实际已产生文件，不生成假成功终态。独立INPUT阶段只用合法原始输入和Source规则，将32共用Timer×2cuts、King freshTimer×2cuts、Character8项绑定到实际新身份/前缀/写入前提；33 businessTimer/26item/65processing的预期集合必须与真实INPUT相符，不能拿旧439实例行或Expected补。

在独立INPUT验收和新captured-profile Source控制之后，单次Python战斗只读密封INPUT/primitive Tape/真实clock，禁止读取Expected；完整模型输出先封存SHA。再由独立比较器读取已密封Expected，按预封八section（event/ref/history/RNG/final/实际选定callback/TimerAPI/cuts）严格比较，不放宽float/顺序/父链/终态，不用近似胜率。比较器与定向负控在Expected前封存；实际未知bundle/SHA在捕获后机械绑定，不预伪造。

## 6. 为什么旧178不能替代

178确有King混合记录215events/303 primitives，并非没有旧原版King证据；其IDs为{1,16,19,21,22,67,262,332}，**没有基础Goobert23**，无法证明新5↔6同步相互回入。旧17-key runtime还有31selected＋4inactive Timer，缺当前initial_characters/timer_initial及对应实际初态见证。它可支持既有机制历史，不能直接充当新King＋23联合八节一致性；不将其改名441、借别案receipt、从Expected反推缺失输入。

## 7. 放行前尚需完成

462隔离source冻结及463最小独立type/binding/inverse验收（正在继续）；新host case/tuple窄接线、消费者初态规则/14DTO/比较合同与负控准备；最后核实际前驱READY/物理preimages/资源/空间并签具体单次执行描述。新原版安装/运行目前未获自动放行。以上都是已明确有限工作，不要求重新研究旧物理恢复链、GUI或全seed位级RNG。
