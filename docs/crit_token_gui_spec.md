# 暴击成功仍消耗暴击层：可见 Godot 实验 SPEC

## Requirements
原版 1.1.8 解包、GodotSteam 3.6.2 可见窗口中，记录自然暴击成功与物品、攻击者角色暴击层的同次消耗。用真实物品而非修改暴击条件造结果，custom_opponent.json 注入实际摆盘。数据、截图和日志保存 data；共享文件字节备份并恢复，存档隔离。

## Design
对手由 Obsidian Dragon 指向 Critwood Staff；三个 Flame Badge 战斗开始给予18 Heat，原龙每5 Heat给予被影响武器1暴击层，Draconic Orb达到15 Heat给予角色3暴击层。Sapphire Whelp开始给予6 Mana，Critwood Staff early hook用3 Mana并给全部物品100%暴击率。Staff比两种龙冷却短，可在层数尚存时击中。最终双方生命设为200仅延长观察，己方保持Ranger初始物品；不人为写暴击层、暴击率或随机数。初版999生命在保存时触发BitStream断言，已改为200复核。

Character.takeDamage只增加print观察：进入暴击区的层数、chance、概率成功分支、消耗后层数与最终critical、抗暴字段；不替换roll调用。概率成功分支内日志是成功直接证据，不能用最终critical反推。

流程：标题→现有非排位初始化→提高己方最大生命（辅助生存）→商店→原版switchToCombat→观察真实物品效果→截图→暂停可见画面供Windows窗口核查→退出并恢复。

## 具体接口与伪代码
- tests/crit_token_gui_battle.gd::_process(delta)->void：90秒超时失败；stage0等待标题初始化后建立Ranger开始非排位；stage1推进标题转场，设己方最大生命200并进入战斗；stage2等待Combat，记录物品名称/布局，保存截图，stage3自然运行10秒再截图并以time_scale=0.001保留画面；stage4保持可见25秒后打印完成退出。
- ::capture(name:String)->void：从viewport取图，flip_y，保存data/crit_token_gui_{name}.png；失败退出。
- ::fail(message:String)->void：push_error，quit(1)。
- tests/crit_token_gui_run.ps1入口()->void：检查独占临时路径；将project/Character/custom_opponent原字节备份data；复制夹具与测试；在Character原分支插入只观察日志；临时autoload；隔离APPDATA；Start-Process可见Godot；110秒等待，超时仅关闭自己的PID；finally逐字节恢复三文件，移除自己的临时autoload脚本；保存日志及存档供复核。运行前需确认脚本内现有引擎路径仍有效。
- Character.takeDamage(damageSource)->DamageResult（临时观察）：保持原控制流与所有roll调用；进入canCrit时打印before；原自然成功分支内print；token两分支后打印after；抗暴后打印最终结果。

## Tasks
1. [x] 读取权威源码与现有入口，确定真实物品。
2. [x] 写夹具、测试节点与可见runner，记录共享文件原始备份。
3. [x] 运行自然组合，确认概率成功和双层消耗同一攻击。
4. [x] 可见窗口/viewport截图、日志复核；恢复共享文件并释放时段。子agent在最终运行结束后遇到额度限制，由主agent完成日志/恢复核对和报告。

## Acceptance Criteria / Tests
需要同次攻击probability_success=true（100%自然分支直接证据）、item before>0和char before>0，二者after各减1；记录抵抗与最终结果；GUI截图和实际窗口存在；文件恢复哈希一致。若组合不成立，记录实际原因而不改条件；辅助HP设置不算自然获取的属性。自然100%分支并不抽取非平凡随机数，因此不宣称已验证非100%抽样历史。

## 实际结果

见 `docs/crit_token_gui_results.md`。最终日志44–47行直接记录自然概率分支100%成功后，两种层数3/3→2/2；73–75行另记录0%概率但仍有物品层时的强制暴击。最终stderr无SCRIPT ERROR，仅保留引擎退出时资源清理错误/警告。主agent核对共享文件与备份SHA-256一致，自建Godot进程已退出。
