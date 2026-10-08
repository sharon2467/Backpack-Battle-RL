# 纯 Effect 尖刺图形实验结果

2026-10-06，游戏数据版本1.1.8，GodotSteam 3.6.2。本实验使用当前 Backpack Battles 解包工程及已有启动/对手注入兼容代码。没有以第三方模拟器作为证据。

## 结论

真实物品雷神之锤（Thors Hammer，id463）的纯 Effect 子伤害会触发尖刺，并在 effectSpikesLimit=0 时采用默认 meleeSpikesLimit=1。它是自然可达例外：其 _ready 使用 DamageSource.new().init(self, Type.Effect, effectDmg)，而 init 不设置 flags，故保留默认 Flags.All=63。不能把这项结论泛化为所有纯 Effect；普通 setItem 的纯效果来源使用 effectFlags=41，没有 CanTriggerSpikes。

物品源码链：Utility/DamageSource.gd:45默认flags、:85的init；Items/Exclusive/ThorsHammer.gd:11–24构造纯效果源及自然耗魔触发；Items/Blueberries.gd产生Mana；Items/WalrusTusk.gd战斗开始自然给尖刺；Core/Character.gd:709–723选择比例和反伤。

## 真实摆盘和运行

- 防守方：12个 Leather Bag（id11），左上格 x=0,2,4,6；y=0,2,4，全部方向0；四根 Walrus Tusk（id8）在(0,0),(1,0),(2,0),(3,0)。獠牙在原版 onCombatStart 自然给予4 Spikes。测试生命200，耐力原始5，无武器、无效果比例修改物品。
- 攻击方：同样12个皮包；Thors Hammer在(0,0)、Blueberries在(3,0)和(4,0)，全部方向0。测试生命500，耐力20，由 data/custom_opponent.json 注入。完整快照保留为 data/effect_spikes_gui_opponent.json，正式输入已恢复。
- 蓝莓按自然冷却获得Mana；锤子主攻击命中且Mana>=2时，原 onDealtDamage 使用2 Mana并造成12纯效果伤害。未修改物品脚本、flags/types、命中或暴击随机结果。
- 可见启动命令由 tests/effect_spikes_gui_run.ps1 执行：Start-Process GodotSteam --path <Backpack Battles>，WindowStyle Normal，无headless/no-window参数。进程11564观测到非零MainWindowHandle=198598、Responding=true，记录在data/effect_spikes_gui_window.json。隔离APPDATA路径记录在原日志。
- 自动测试节点推进真实非排位战斗，不加速战斗；共观察24秒墙钟时间。截图为原引擎viewport图像，不是程序生成示意图。active截图显示战斗时间9.4秒、我方尖刺4、生命140/200，对手480/500、雷神锤与两份蓝莓。

## 关键实测日志

全部原日志：data/effect_spikes_gui_stdout.log；自动解析的5组完整配对：data/effect_spikes_gui_verified_pairs.json。

| 纯Effect事件 | 父事件（耗魔） | damage | types / flags | melee / ranged / effect limit | Spikes事件 | Spikes父事件 | 实际damage / healthDamage |
| --- | --- | --- | --- | --- | --- | --- | --- |
|18|17|12|[2] / 63|1 / 0 / 0|19|18|4 / 4|
|33|32|12|[2] / 63|1 / 0 / 0|34|33|4 / 4|
|51|50|12|[2] / 63|1 / 0 / 0|52|51|4 / 4|
|63|62|12|[2] / 63|1 / 0 / 0|64|63|4 / 4|
|80|79|12|[2] / 63|1 / 0 / 0|81|80|4 / 4|

每组 hit=true、can_trigger=true，防守尖刺4；公式日志selected_limit=1、spike_damage=4，即min(4,round(12*1))。实际尖刺来源types=[104]、flags33、hit=true，其parent精确指向纯Effect事件。锤子主攻击types=[0]独立记录，例如主攻击event15也造成其自身的反伤event21；不会把该近战反伤混作Effect证据。日志顺序中Effect及其尖刺先于主攻击的applySpikes，因为原版主攻击onDealtDamage嵌套执行Effect。

runner返回退出码0，EFFECT_SPIKES_GUI_PASS；后置验证EFFECT_SPIKES_EVENT_PAIRS_PASS count=5。自动验收要求纯Effect单类型[2]、flags63、正伤害、正尖刺、effect_limit0/melee_limit1，并查找父ID一致且伤害数值一致的真实type104事件。

## GUI证据及边界

截图：data/effect_spikes_gui_combat.png（0.0秒装载）、data/effect_spikes_gui_active.png（实际战斗9.4秒）、data/effect_spikes_gui_final.png。已逐张查看前两张，物品与生命/尖刺显示符合夹具。

按 computer-use 技能初始化sky并两次读取窗口清单，sky未列出Godot窗口，故未尝试猜测窗口对象或发起state捕获。额外原生截图没有取得；图形证据为可见启动参数、运行进程非零窗口句柄及原引擎战斗viewport截图。Godot退出时打印已知资源未释放/ObjectDB警告；没有脚本解析/伤害机制报错，进程成功退出。使用匹配Godot 3.6系列的3.6.2编辑器执行解包工程，而非零售自定义3.6二进制；该差异作为实验边界保留。

## 恢复与复现

共享文件project.godot、Core/Character.gd、data/custom_opponent.json均按运行前原始字节恢复，并以SHA256再次独立核对，全部equal=true：data/effect_spikes_gui_original_hashes.json及data/effect_spikes_gui_restoration.json。临时自动加载脚本已移除，PID11564已退出。独立测试夹具、日志、截图和隔离存档保留于data，未操作真实存档或用户进程。最终原版源码无观察日志残留。

复现命令：在仓库根目录执行 `& tests/effect_spikes_gui_run.ps1`。新版runner为每次APPDATA加时间后缀；可选 `-RunId review_01`（仅字母/数字/下划线/横线）。新的复现会覆盖同名前缀的日志与截图，如需保留本次记录先复制到独立data子目录。执行时不得有其他实验同时修改project.godot/Character.gd/custom_opponent.json。

最终插桩仅在Character.applySpikes入口输出当前已完成伤害结果、事件/父事件、尖刺及上限，并在现有spikeDam赋值后输出选择比例；没有另行修改takeDamage。type104也走这个入口，因而可看到实际尖刺结果并精确关联父伤害。

