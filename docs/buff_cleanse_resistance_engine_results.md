# Debuff专用抵抗层阻挡自身净化：实测结果

2026-11-09 · [实验SPEC](buff_cleanse_resistance_engine_spec.md)已完成。**完整Cold链已实测：已有Cold时，负left再生的专用抵抗层会阻挡角色自己的净化；没有专用层时，同一净化正常移除Cold。**本轮没有改Python机制。

## 1. 实际运行与摆盘

使用用户指定`E:/godotsteam/godotsteam.362.editor.win64.exe`，实际Engine为`3.6.2-stable (custom_build)`，Game实例版本1.1.8；这不是此前安装原exe Godot3.6.0实验。exe SHA256：`100B76E344A040D2CA50D1B4D03B097A259C35B32D5865043F33486A666EDA1C`。

原工程直接运行，无project/bin副本、无PCK动作、无features配置。实测OS.editor=true、OS.full_version=false，Game.EDITOR/FULLVERSION均true，time_scale=1；APPDATA/LOCALAPPDATA及实际user_data都在本轮隔离目录。见[实际ENV](../data/buff_cleanse_resistance/godotsteam_cleanse_20261109_01/data/C_overlap_environment.json)和[先行smoke](../data/buff_engine_edge/godotsteam_cleanse_smoke_20261109_01/results.json)。

两组目标均为player0：2 Dragonskin Boots自然提供Cold概率抵抗40%，Wisdom Puppy自然CD净化Cold1；主组加2 Magic Mirror，实测反弹40%，对照只移除两镜、反弹0%。对手Snowmaster自然周期施加Cold1。双方7 Deer Totem自然抗伤105%，保留其他原回调。原ItemBook/Inventory实例化并验证给定布局，不种层、不赋概率/RNG/HP。多Unique/跨职业集合仅用于受控战斗验证。

## 2. 完整主链与对照

运行：`godotsteam_cleanse_20261109_01`。下表时间为**战斗时钟**；Util启动总时钟另存trace，不混用。主组在早期Cold=0时出现的再生不计入目标，最终采用已有Cold的严格样本。

| 样本 | 实际调用与状态 | 原生事件 |
| --- | --- | --- |
| 已有Cold后再生专用层 | C_overlap，Snowmaster gain914，240.733346秒；初Cold1/typed0，请求1，抵抗1后left0，反弹1后left−1；own=−1，typed0→1，Cold仍1 | 原目标成功event=−1；反弹子915配native1175，target1、amount1/reflected=true |
| 同角色自己的净化受阻 | 随后Wisdom Puppy lose920，241.850013秒；used=False，初Cold1/typed1；概率保护0，专用层保护1，typed1→0，actual change0，Cold1→1 | Protect1181：target0、origin=Wisdom Puppy、amount1/protected=true；返回成功event=−1，无该lose负Cold成功事件 |
| 主组同场无专用层成功 | Puppy lose903，237.666679秒；typed0，Cold2→1，actual1 | native1162，target0、amount−1、used=False |
| 独立去镜对照成功 | C_no_mirror，Puppy lose5，4.266667秒；R40/F0、typed0，Cold3→2，actual1 | native7，target0、origin=Wisdom Puppy、amount−1、used=False |

直接读原始trace确认：gain914与lose920属于同一Cold容器（instance50561），**两者之间目标角色没有其他Cold gain/lose入口**。这排除了再生层先被其他施加/净化消耗、再把另一份库存归给Puppy的解释。lose920的actual在原`change=min(current,amount)`局部读取，未用通知后的总数差估算；概率保护为0，实际阻挡来自`resistStacks`。

主组240.733346秒的Util.time为246.283346/frame14848，受阻净化241.850013秒的Util.time为247.383346/frame14914。wrapper记录墙钟分别为主组264.759871秒、去镜组26.5265408秒，包含启动/收尾，均在420秒限制内；取证后退出自己进程，未判胜或等待自然终局。

证据：[全轮结果](../data/buff_cleanse_resistance/godotsteam_cleanse_20261109_01/results.json)、[主组配对](../data/buff_cleanse_resistance/godotsteam_cleanse_20261109_01/data/C_overlap_verified.json)、[主组原始日志](../data/buff_cleanse_resistance/godotsteam_cleanse_20261109_01/data/C_overlap_stdout.log)、[去镜配对](../data/buff_cleanse_resistance/godotsteam_cleanse_20261109_01/data/C_no_mirror_verified.json)。结果、原调用和原生事件已分别独立复核。

[主组viewport](../data/buff_cleanse_resistance/godotsteam_cleanse_20261109_01/data/C_overlap_observed.png)显示真实摆盘/241.8秒/Cold1，但打开的CombatLog面板停在较早144.72秒保护条目，**不是最终1181**。[去镜viewport](../data/buff_cleanse_resistance/godotsteam_cleanse_20261109_01/data/C_no_mirror_observed.png)HUD显示3，不能据此证明净化后2；3→2由同调用trace及event7确认。截图仅作真实界面与摆盘辅助，不替代逐次机制证据，也不推定HUD差异原因。

## 3. 探针与恢复

先[PreviewOnly生成拟插diff](../data/buff_cleanse_resistance/preview_20261109_01/buff_observation.diff)，当时未写原工程/JSON、未启动。审查后真实轮只临时写原project autoload、Buff观察及对手JSON；Buff原公式、概率调用、保护/扣层/事件次序不变，仅增加私有观察ID/读取与等价展开return。observer不调用RNG、give/lose、emit、createEvent或视觉函数。

| 原工程位置 | 本轮插后观察位置 |
| --- | --- |
| project.godot首位autoload | 行468，指向外部tests脚本；未加features |
| Buff.gainTemporary | 行80–81、101、131/136、152/154/156、201/206，记录增层及反弹路径 |
| Buff.loseStacks | 行212–215、233、240、252、258、298–300，记录请求/保护/原事件返回 |
| Buff.changeCurrentLogShowLabel | 行307读取原局部actual，按同Buff的lose call关联 |

原行与新增行完整对应见[Buff diff](../data/buff_cleanse_resistance/godotsteam_cleanse_20261109_01/buff_observation.diff)、[autoload diff](../data/buff_cleanse_resistance/godotsteam_cleanse_20261109_01/autoload_observation.diff)、[位置清单](../data/buff_cleanse_resistance/godotsteam_cleanse_20261109_01/probe_locations.json)。原Buff SHA为`3EFABB72EB0B337E30EBC924347ABA40BD1039A3C5F718B761B0EE78B48AB8BB`，本轮实际加载观察版为`E8CFC22471D7C56AD2C1B010AE7410A3182245ACD35EBFA9F58A54C8524B969E`，两者不混称。

finally已恢复全部待改文件原字节、JSON及环境。[最终恢复清单](../data/buff_cleanse_resistance/godotsteam_cleanse_20261109_01/restoration.json)为unchanged=true、errors=[]；核验范围9文件：project、Buff、Character、Game、SteamHelper、两份ItemData、原JSON及所选GodotSteam exe。独立重算当前9项SHA均与before一致，无探针残留、无GodotSteam进程；不声称全工程逐文件hash。

**global边界**：本轮global debuffResistStacks为0，未单独构造正库存共存对照。源码明确gain读取global debuffResistStacks，而lose读取typed resistStacks、不读取该global字段；前者是源码结论，不能冒充本次正库存实验。完整Cold链只对本轮3.6.2/1.1.8组合确认，不外推为所有版本或全部Buff机制已验证；一阶段现有规则未改变。
