# 下一次早期观测：最小决策计划（仅保存，不执行）

## 1. Requirements：要解决什么

基线存档为 `caa209645641c9b1e00215b1e6e1f05e1f86f105`。正式有限支持75项，King未准入；旧初态1479=1391 DIRECT+6 SOURCE_DERIVED+82 MISSING，保持不变。本计划只复用430/432/434/435及401历史材料，不研究新源码、不实现、不安装池、不运行采集或测试，不创建新长期任务。

下一次早期观测最多为旧82项中的4个 `Timer.private_left` 目标补充必要证据：

| 角色 | 初态阶段 | 旧目标索引（仅定位旧缺口） |
|---|---|---:|
| invu:P | pre_prepare | 1430 |
| invu:O | pre_prepare | 1431 |
| invu:P | pre_activate | 1474 |
| invu:O | pre_activate | 1475 |

它试图闭合的是“旧 parent-ready 出生记录晚于子节点 READY”的观测窗口：从首次父 `_enter_tree` 记录目标 Timer 尚未入树的原生状态，保留至 parent-ready/实际 INPUT 阶段及真实 start/stop 计数。不是测量 private_left，也不是预先写入 -1。

其余78项未覆盖：Character三字段 invulnerable/invulnerabilityItem/invulBubbleVisible 各4=12；King crown/light_visible/light_modulate 各2=6；其余Timer.private_left 60（tick P/O四目标、22个Buff角色44目标、两个fatigue角色四目标、四个aux rage角色八目标）。不会顺带解决其他Timer、角色/物品逻辑、全引擎或RL。

**4是潜在旧缺口覆盖上限，不是已证明或保证可补齐的数量。** 旧索引、nativeID、shared checkpoint138/1231等只是历史定位，绝不可塞入新输入。新采集必须重新按实际身份、通道、阶段建立索引；旧6条证明也不能自动迁移。因此不预报新采集一定得到10/78或仍是1479行，旧6/82不改。

## 2. Design：最小选择及限制

建议父方在另外一次明确决策后，仅放行一个固定King-A受控采集，保留种子和摆盘。435已接受的是准确434源码、Python27和一次EMPTY有限原生验证；它不能代替实际原版初始化链。

435原生台架只直接实例化Player继承场景。Opponent源码/结构/schema路径已审，但实际Opponent分配/首次入树/observer初始化时序未动态命中，不能说Player通过便证明Opponent通过。未来固定A采集应以同一观测协议真实记录P和O；任何一侧首次记录、身份、ready检查点或INPUT绑定缺失都不能晋级。若决策者要求先单独测O，须另列范围与成本，本计划不暗中增加该测试。

有效新证据至少要求：安装在任何所选Character实例化之前；observer对象及成员已初始化；实际首个owner入树而目标child仍未入树；目标为正确无脚本原生Timer、直接父子关系、owner/Timer双射；未复用/替换/重复入树并清空历史；ready/current保留真实类型/REAL位与计数。首次字典插入或outside_tree快照自身不能证明“从未曾入树”，仍须适用既有fresh PackedScene/native dispatch/constructor seed来源前提。

若实际计数非零，照实保留；这未必让整个采集格式无效，但拟用的NO_START推导条件不满足，四项继续MISSING。不得归零、换种子、改摆盘、找零计数样本或自动再采。成功采集本身也只是待独立复核的遥测；后续规则实现/新INITIAL派生及逐事件对照是分开的门。

## 3. Realize：未来一次受控采集的约束（此处不运行）

输入固定为既有case-A的custom_player.json、custom_opponent.json、native_capture_config.json（三者路径/size/SHA见配套JSON）；global_seed35301、util_seed35302。新Root一次授权、435真实review/owner、434实际freeze/tuple、运行依赖pins、原像/READY池及新唯一run路径均须执行前实核。使用一个资源基线与一个采集池，78payload共824158B；不复制完整Game。

预定run名是 `original027-king-single-A-434-attempt07`。现冻结host的plan/one-shot-launch还保留数字attempt=6诊断标签；不能把标签当实际次数或默改冻结源码。下一决策应明确runName/configSHA/profile为权威，若要求修标签须另走最小源码修订/独立验收。本计划不修。

未来允许范围上限应分别列为：一次check-only Godot进程，成功后最多一次原版Game进程，即最多两个Godot引擎进程；不重跑435 EMPTY。允许模型/输入构建/EXPECTED比较均为0。固定输入、Source pins或阶段门变化均停止。

输出仍只有既有12个合法INPUT文件名（JSON中完整列出），早期entry/raw、parent-ready、真实start/stop及current写回已有king-input-facts.json，不加第13个文件。事件顺序/父链/历史/终态/RNG及clock/endpoint/status保留独立通道和真实cut；终态按first actual eligible idle、至少两个future physics，保留实际数量，绝不强迫等于2。EXPECTED/末态诊断只作控制，不反推缺失INPUT或private状态。

停止条件：无新一次授权、可信额度<=30%或无存档余量、磁盘/lease/READY/源码原像/pins/cap漂移、唯一目录已存在则不安装/不启动。check-only30秒、解析不干净/脚本错误/源漂移则Game0；实际Game总300秒，沿用initial120/setup30/combat120/finalization10/exit5秒阶段预算，及既有日志/文件/1536MiB尝试/4GiB空闲floor。错误、超时、资源门失败或身份/重入/类型异常保留现场，无自动重试。额度到30%时即使批次未完成也只做自有进程的有界停止与必要保存，不为完成批次继续消耗。退出码0不等于干净退出，ERROR/清理live/zombie/clean标志分别记录；未独立判明不晋级。

失败保存：保留准确配置、实际Source/driver map、安装前像、stdout/stderr、阶段/错误/退出/清理、原始和部分carrier、RNG/clock/序列历史、size/SHA清单及恢复入口。只终止自己启动的进程组，TERM5秒/KILL0.5秒有界清理；不声称回收全部子孙。失败池不标READY、不覆盖fixed06/failed05/旧6条链，不删除独有证据。按已有恢复格式做小胶囊及远端保存、独立读回；无法远端保存时准确说本地状态，不称已备份，不绕过认证。

## 4. Acceptance / Tests：决策、成本与验收

本计划不执行任何测试；使用现成435验收结果。历史401同类host约142.949秒（原版活跃103.235秒、check约3秒），545payload合计199359156B，ZIP14568576B。未来采集本体预计仍是分钟级，不能把历史耗时当保证；现有上限为30秒parse+300秒Game+清理，另外留归档/上传/读回时间。建议完整短块预留10–15分钟，并另列后续独立新数据复核，不能承诺其耗时或额度百分比。

host现有启动预算为4GiB保留+1536MiB尝试=5905580032B；计划时实测free及时间见JSON，只是本次读数，不是未来启动准许。还须另算胶囊、Git发布及独立副本的保存余量；不购资源，不释放未验证可恢复的独有文件。启动前须获取可信当前额度并保留充分收尾余量；到30%保存暂停，不能用历史读数擅自启动。

决策结果只有：另行放行上述一次、暂缓资源/额度、或因具体最小前提不成立而返回设计。即便真实P/O观测完整，仍需独立检查新source tuple、12输入/cut、实际owner/Timer身份、计数、终态/RNG控制以及seed前提；然后才可提出新四目标规则/来源派生范围。不得直接打开356/361、全schema、King或RL门。新采集不回填旧fixed06，不把来源链的局部接受当作完整初态可行。

计划已保存即可结束本块；不新增研究、实现、测试或采集。
