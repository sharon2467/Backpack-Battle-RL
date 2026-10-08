# 纯 Effect 尖刺真实物品图形实验 SPEC

日期：2026-10-06。版本1.1.8，原版解包为唯一机制依据。

## Requirements

检验纯 Effect 在满足尖刺门控时是否采用近战比例。必须先识别原版物品，再通过 data/custom_opponent.json 注入真实物品对手，以可见 GodotSteam 窗口战斗观测。禁止改来源 flags/types、伤害公式或随机判定。区分普通 effectFlags=41 的效果与真实特殊来源。

已找到 Thors Hammer（id463）：Exclusive/ThorsHammer.gd 的 _ready 调用 DamageSource.new().init(self, Type.Effect, effectDmg)，保留 DamageSource 默认 All=63；命中主攻击且拥有2 Mana时触发12点纯效果伤害。Blueberries（id22）冷却产生 Mana；Walrus Tusk（id8）战斗开始产生1 Spikes并消耗。计划防守方用多根海象獠牙获得尖刺，保持 effectSpikesLimit=0、meleeSpikesLimit=1；攻击方雷神锤与两份蓝莓。必要的高生命测试属性通过现有角色/JSON属性设置，不能改伤害机制。

## Design

复用现有测试节点逐帧推进标题、非排位、商店、战斗；唯一新增测试自动加载，不增加架构。对手正常 JSON 校验及 initOpponent。防守方以原 ItemBook.instantiateItem 与 Inventory.addItemByTopLeft 建立合法真实布局；以 canAddItem 检查普通物品合法性。海象獠牙自然生效，蓝莓自然产魔，锤子自然发动效果。原版 Character.applySpikes 临时仅插日志，输出来源、事件ID/父ID、types、flags、hit、damage、healthDamage、Spikes与三项上限、计算spikeDam；takeDamage 完成处输出实际反伤结果，以父事件关联纯 Effect。所有共享文件先备份字节，finally恢复；APPDATA隔离。记录窗口/截图与日志，不用无窗口参数。

流程：标题 → 非排位 → 构造防守布局 → JSON锤子对手 → 原战斗 → 观测纯Effect及反伤 → 截图 → 完成/超时 → 恢复。

### 具体函数接口与伪代码

- tests/effect_spikes_gui_battle.gd::_process(delta:float)->void：90秒超时失败；标题就绪时启动非排位；商店可战斗时构造防守布局并切战斗；战斗就绪校验对手、保存画面；等待足够时间/战斗结束后输出PASS并退出。可见时间不加速。
- setup_player()->void：reset背包；按数组依次实例化背包与獠牙，设owner、挂playerNode、设方向、合法性检查后放入；设置高生命以观察自然重复触发。
- add_player_item(name:String,x:int,y:int)->void：instantiateItem；挂节点、定向、定位；检查全部占格合法后添加；失败调用fail。
- capture(label:String)->void：viewport texture.get_data；flip_y；保存data/effect_spikes_gui_<label>.png；失败调用fail。
- fail(message:String)->void：push_error；get_tree.quit(1)。
- tests/effect_spikes_gui_run.ps1 入口()->void：核验引擎/独占时段和临时路径；备份project.godot、Character.gd、custom_opponent.json字节；写夹具/复制测试；加入自动加载及观察日志；隔离APPDATA；Start-Process可见游戏窗口并重定向data日志；有限时间等待自己的PID；检查PASS；finally恢复所有共享文件和环境变量。禁止停止用户进程。
- 原 Character.takeDamage(source:DamageSource,parent=null)->DamageResult 临时观测：沿用全部原逻辑，仅返回前print当前event.id、parent.id、来源、types、flags、结果；尖刺源type104可关联父伤害。
- 原 Character.applySpikes(result:DamageResult)->void 临时观测：入口print三项上限与门控；沿用原条件和公式；spikeDam赋值之后print事件id及反伤值；不新增任何伤害调用或随机读取。

## Tasks

- [x] T1 阅读知识库、共同SPEC与伤害/注入/启动说明。
- [x] T2 全局检索构造、flag修改、尖刺比例修改，定位雷神锤自然例外。
- [x] T3 制作合法JSON夹具和独立测试/运行脚本（依赖T2）。
- [x] T4 等待主agent授予共享实验时段，再备份/可见启动（依赖T3）。
- [x] T5 校验纯Effect父子事件、实际反伤、窗口截图并记录结论（依赖T4）。
- [x] T6 恢复字节、核对哈希并释放共享时段（依赖T5）。

## Acceptance Criteria / Tests

必须看到雷神锤纯Effect types=[2]、flags=63、hit=true、damage>0，防守有尖刺且effect上限0/近战1；该纯Effect事件成为type104尖刺事件父事件，伤害为min(Spikes,round(damage*1))。主攻击与纯效果分开记录；没有用主攻击反伤冒充子效果反伤。保留真实物品组合、可重跑脚本、可见窗口截图与原引擎日志。若运行未发生则如实报告，不用静态分析代替成功。全部共享文件恢复原始字节。

运行前调整：己方生命使用前一图形实验已成功的200；对手JSON500在加载器1..999范围内。runner自动检查纯Effect types=[2]/flags63及parent对应type104实际尖刺事件，保存verified_pairs，并核对恢复SHA256。


实作补充：runner入口新增RunId:String（默认时间戳），先校验简单安全字符，再产生隔离APPDATA目录；日志/截图仍用固定前缀。实际观察只需applySpikes两个print点，type104自身入口记录了实际伤害与parent，所以未另改takeDamage。2026-10-06首轮图形实测通过5组事件配对并已恢复，见effect_spikes_gui_results.md。

