# 纯战斗初态边界：实际纠偏结果

已实现并独立验收 `pure-combat-initial-fixed-king-A/437`，不再将以下精确呈现字段作为纯战斗最小初态或其缺口阻断。原版实现、所有原始数据、旧1479完整观测合同及6/82历史证明均保留，未新增采集。

| 合同范围（字段×实例×时点） | 总要求 | 直接观测 | 既有来源推导 | 未证明/阻断 |
|---|---:|---:|---:|---:|
| 原完整观测参考 | 1479 | 1391 | 6 | 82 |
| 本次精确排除 | 116 | 102 | 4 | 10 |
| 当前纯战斗最小初态 | 1363 | 1289 | 2 | 72 |

减少的10个阻断是4个Character.invulBubbleVisible和6个King crown/light字段；不是新增战斗证明。4条既有AutoHide私有Timer证明保留在历史完整合同中，但不再算纯战斗所需；剩余2条是KingBuffTimer来源证明。

| 实际排除范围 | 字段实例时点数 | 源码理由与位置 |
|---|---:|---|
| Character.invulBubbleVisible，P/O两phase | 4 | 原版Core/Character.gd:364只据其决定播放退出动画，367–368无条件重置真实业务状态；1063–1069只动画/显示标记。Core/Character.tscn:60–129对应动画仅shader/visible value tracks，无业务method track。 |
| King.crown最近观测参数，两phase | 2 | 原版Items/Exclusive/KingGoobert.gd:13–17是枚举，并无原生crown存储变量；52–65参数只驱动显示。observer source_crowns只是最近onStateChanged参数，非前向战斗输入。日志边界见下文。 |
| King.light_visible/light_modulate，两phase | 4 | KingGoobert.gd:9、52–65只写CircleLight显示和self_modulate；同场景67–72是无脚本/战斗回调的Sprite，旧颜色不参与业务分支。 |
| Particle.activation/drag各6getter，pre_activate | 12 | visible/emitting/one_shot/lifetime/explosiveness/speed_scale只进入AutoHide粒子及隐藏延时；Utility/AutoHideParticles.gd:5–39闭包终点仅show/hide/restart/emitting。 |
| King精确king_hide:P:12与king_drag:P:12，两phase的20Timer字段 | 80 | 两个动态UI子Timer的timeout仅调用自身hide，无业务/日志回调；不泛化到其他Timer。 |
| 同两role的7lineage/provenance字段，pre_activate | 14 | 与相同UI生命周期绑定；保留原完整frame拓扑/回调/历史资料，但不要求重建其显示初态。 |

完整116个精确行键、逐行理由和源码SHA见 `data/phase437-independent-source-review-first-001/source-review.json`，源码行号详见 `docs/phase437_independent_presentation_source_review.md`。

## crown显示快照排除，日志历史保留

Item.gd:4802–4804每次setState先调用snapshotItemState，再onStateChanged。King.prepare/激活/buffEnded产生的0/1/2、withNextEvent/eventNum/event.id关联、CombatLog.gd:503–515、CombatStatLogger.gd:96–103、StatHistory.gd:7–10相邻压缩及replay调用仍完整保留。删除的是“首次输入必须先证明最近一次显示参数”这一要求，不删除state日志，也不删除触发该日志的KingBuffTimer。

Character.invulnerable/invulnerabilityItem继续必需：受伤和isVulnerable分支、真实无敌Timer、InvulnerableStart/End日志来源都读取它们。其余未证明字段仍阻断：两者各4=8，Timer.private_left64，共72。没有给缺失值填默认值。

## 实际已改与仍未声称完成

实际代码为 `native_replay_v8/combat_contract.py`；保存的可执行合同为 `data/phase437-combat-initial-first-001/contract.json`，当前阻断结果为同目录 `summary.json`。该生产模块提供精确profile与required/excluded集合、可接受仅1363required行的partition，以及对408/426已存证据的一次pinned投影；不是只修改文档或建议清单。

独立控制仅一个Python进程，51检查通过，生产main实际一次。验证116集合等于独立源码审查；删除全部显示行仍可审查required；显示值/证明元数据改变不影响required；删除真实invul/KingBuff字段、未知/重复key或伪overlay索引等拒绝。原冻结输入/源码及八个核心业务/比较器文件SHA未变。CLI退出0仅表示保存成功，72项仍阻断，fullschema未验证。

此次没有改原版restart/hide/native调用、节点、FrameDriver、严格事件/父链/状态历史/RNG/终态比较，也没有为了排除显示而放宽旧full-FX比较器。新最小初态合同为未来纯战斗工作的边界；旧完整FX通道保留为兼容/取证参考，不能重新把这116项算成该profile的战斗初态阻断。尚未声称全部运行时呈现兼容代码已删除或新genuine输入路径已开放。

检查到的GDScript闭包无业务或脚本RNG读写，不等于GPU/backend/共享RNG全局纯度证明。任何未覆盖共享RNG依赖仍未证明，所有严格RNG通道保持；这一限制没有被算成新来源证明。

正式有限75项保持既有接受，King未准入，完整引擎/RL未完成。旧Source报告将75与King状态并写的措辞错误在最终独立review中明确澄清，旧证据字节未修改。

## 复现保存审计（不运行战斗）

从本repo运行：

```sh
python native_replay_v8/combat_contract.py --full-index data/phase408-initial-audit-first-001/rawtyped-field-index.json --accepted-overlay data/phase426-king-buff-overlay-first-001/overlay-report.json --output-new /absolute/NEW-audit-directory
```

该命令只读已保存的pinned408/426及独立Source审查，生成一个新的初态合同/阻断报告；不采集、不调用Godot、不构建模型输入。新目录必须不存在，不能覆盖本次结果。
