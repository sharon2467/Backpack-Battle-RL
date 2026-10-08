# 概率暴击成功仍消耗暴击层：图形实测结果

日期：2026-10-06。实验执行者：`crit_token_gui`（GPT-6.1-Sol）。最终战斗运行结束后该子agent遇到模型额度限制；主agent接续核对日志、恢复状态与报告，没有另改游戏结算机制。

## 结论

**原版实际发生：自然概率暴击已经通过，物品暴击层与角色暴击层仍各消耗1层。** 测试中的100%暴击率由真实 Critwood Staff 的 early 效果产生，没有直接设置暴击率或层数，也没有替换随机判断。

`data/crit_token_gui_stdout.log:44–47`：

```text
CRIT_BEFORE item=Critwood Staff item_tokens=3 char_tokens=3 resistance=0 resist_tokens=0
CRIT_NATURAL_SUCCESS item=Critwood Staff chance=100
CRIT_AFTER_TOKENS item=Critwood Staff chance=100 item_tokens=2 char_tokens=2 result_critical=False
CRIT_FINAL item=Critwood Staff critical=True damage=26 resistance=0 resist_tokens=0
```

四条日志依次插在同一次 `Character.takeDamage` 的原有暴击分支内：暴击前 → 概率成功分支内部 → 两个层数分支后 → 抗暴/实际暴击应用后。期间没有新的伤害调用，因此不是把不同攻击的层数变动拼在一起。

另一个自然发生的对照见60–63行：概率100%时，物品层2→1；73–75行：概率0%且物品层1→0，最终仍暴击。后者说明日志确实能区分概率分支与层数强制暴击，而不是仅凭最终 critical=true 作推断。

源码原因：`Backpack Battles/Core/Character.gd:543–561` 的自然成功分支只将局部 `critical` 设true；物品与角色层数分支都检查 `not damageRes.critical`。这个结果字段直到 `DamageResult.makeCritical()` 才变为true。忠实模拟时不可把两次判断擅自改成 `not critical` 或互斥 `elif`。

## 实验组合

对手由 `data/crit_token_gui_opponent.json` 临时写入工作区 `data/custom_opponent.json`，以原版非排位 `switchToCombat` 加载，界面为 Custom Opponent。职业Pyromancer、生命200、耐力5；皮包铺格，实际道具如下：

| 物品 | 索引 / 数量 | 作用 |
| --- | --- | --- |
| Obsidian Dragon | 123 / 1 | 指向法杖，Heat触发给予物品暴击层 |
| Critwood Staff | 33 / 1 | 使用Mana，early阶段给所有己方物品100%暴击率 |
| Sapphire Whelp | 199 / 1 | 开始战斗提供Mana |
| Draconic Orb | 120 / 1 | Heat达到阈值，给予角色暴击层 |
| Flame Badge | 249 / 3 | 开始战斗提供18 Heat，形成两种暴击层 |

己方使用Ranger初始物品，测试节点把最大生命设200延长观测。对手布局与方向完整保存在JSON；实际实例名称和占格见stdout25–43行。实验不涉及这些物品的局外获取路径。

物品依据：`Items/Exclusive/ObsidianDragon.gd:18–27`、`Items/Exclusive/DraconicOrb.gd:14–19`、`Items/Exclusive/FlameBadge.gd:9–11`、`Items/CritwoodStaff.gd:15–23`，均位于当前 `Backpack Battles/`。

## 引擎与图形证据

- GodotSteam `3.6.2.stable.custom_build`，游戏版本1.1.8，OpenGL ES3 / NVIDIA RTX4060 Laptop GPU，记录在stdout开头。
- `tests/crit_token_gui_run.ps1` 使用 `Start-Process -WindowStyle Normal` 启动现有引擎，不带 `--no-window` 或headless参数。
- 子agent在第二轮曾通过sky枚举到真实Godot窗口（window id394034）；系统窗口截图请求遭app approval timeout，未保存原生窗口截图。保留的PNG均为**实际图形战斗的Godot viewport截图**，不冒称桌面截屏。
- 最终200HP复核重新保存 `data/crit_token_gui_loaded.png`、`data/crit_token_gui_combat.png`。后者可能已进入本场战斗结束画面，关键数值以同轮stdout的逐阶段记录为准。
- 最终日志到达 `Round 1 Battle ended with Loss` 和 `CRIT_GUI_PASS`。这里PASS仅代表观察流程完成；目标机制是否出现已由上面的四条日志另行核验。

## 可重复运行

确保没有其他实验正在改custom opponent/Character/project或运行这一工程，再从工作区执行：

```powershell
& 'tests/crit_token_gui_run.ps1'
```

运行会覆盖本实验前缀的最新日志、截图和备份；需要保留旧实验时先另存这些实验产物。真实存档使用隔离APPDATA，目录为 `data/crit_token_gui_appdata`。概率100%的效果存在有限时间窗，复跑须检查对应自然成功行及当时两个before层数，不能仅检查PASS。

## 恢复与边界

主agent在交接给Effect实验前确认：`Backpack Battles/Core/Character.gd`、`Backpack Battles/project.godot`、`data/custom_opponent.json` 与 `data/crit_token_gui_backup_{character,project,opponent}.bin` 分别SHA-256一致；本实验PID已退出。临时autoload脚本由runner移除。生产Python模拟器未修改。

初轮不存在的 `getIdentifier()` 接口已改为 `getName()`；初版999生命触发BitStream保存断言，最终200生命复核已无SCRIPT ERROR。先前日志保存在attempt1/attempt2文件；最终stderr仍有Godot退出时的List/ObjectDB/Resources/MemoryPool清理错误或警告，本场战斗和目标判定已完成，不将退出清理当作战斗机制证据。

实测使用由物品产生的100%概率：原版 `BalancedRng.roll` 在target>=1时直接成功。因此本实验验证概率成功与层数消耗的先后关系，不声称验证了0%～100%中间概率的抽样分布、平衡随机历史或所有抗暴情况。
