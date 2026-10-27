# Phase437 独立有界源码审查：初态呈现边界

审查角色：presentation_scope_review_sol。结论只适用于 minimum-combat **initial contract**，不改变历史1479观测合同、不删除源数据或节点、不放松 legacy full-FX 比较器。正式75/King未准入，fullschema NOT_VALIDATED。未运行 Godot、采集、池、旧测试或模型。实现验收待 Root 完成后另行进行。

## 逐字段建议

| 精确字段 / role | 历史行数 | 建议与源码闭包 |
| --- | ---: | --- |
| Character.invulBubbleVisible；P/O；pre_prepare/pre_activate | 4 | 排除 minimum 初态。Character.gd:105 声明；364–365 唯一显式读仅控制播放退出动画；367–368 无条件重置真实 invulnerable/item，故 UI 分支不控制业务重置；1063–1069 只 play 和写该显示标记。120 定位 InvulnerabilityBubble/AnimationPlayer。Character.tscn:60–86 的 SubResource62 与103–129 的67都仅 value tracks：shader staticFactor、visible；无 method track。1054–1066 绑定该 Sprite 与动画。finishAnimations_deferred 在 Character.gd:277–281 advance 动画，不增加业务回调。 |
| King.crown；P:12；两 phase | 2 | 排除最近观察参数的初态，必须保留全部 state 历史。KingGoobert.gd:13–17 是枚举，无 crown stored var；52–65 入参只切换显示。observer 源 tests/phase359_sink_extension_source.gd:8、80–84 保存 source_crowns 最近实际 onStateChanged 参数；428–434 导出并明确 NOT_NATIVE_STORED_GETTER。该值没有进入原版前向业务判定。 |
| King.light_visible；P:12；两 phase | 2 | 排除。KingGoobert.gd:9 指向 Icon/CircleLight，52–65 只 show/hide；场景67–72 是 Sprite，无脚本、signal、Timer 或战斗回调。 |
| King.light_modulate；P:12；两 phase | 2 | 排除。实际 getter 是 light.self_modulate（并非场景 modulate）：KingGoobert.gd:55/60 写白色/1.3；相同 CircleLight 闭包。没有读取旧颜色控制业务。 |
| Particle.activation.visible/emitting/one_shot/lifetime/explosiveness/speed_scale；P:12；pre_activate | 6 | 逐一排除；对应 ActivationParticles，场景109–117绑定 AutoHideParticles.gd。visible 控制deactivate是否停止粒子和启动隐藏Timer；emitting只渲染开关；one_shot控制restart/startTimer；后三者仅参与隐藏延时公式。所有终点只影响粒子显示，详见下文。 |
| Particle.drag.visible/emitting/one_shot/lifetime/explosiveness/speed_scale；P:12；pre_activate | 6 | 逐一排除；对应 Icon/SpecificDragParticles，场景83–93绑定同脚本。Item.gd:538–545收集该确切前缀节点并调整显示位置；1595–1597调可见矩形，1652–1654 instantClear，2410–2416 activate/deactivate；4346–4350确实读取emitting，但唯一影响是restart+emitting=false，没有业务反馈。 |
| 两精确role king_hide:P:12、king_drag:P:12；下表20字段；两 phase | 80 | 每一字段均可排除 minimum 初态，不按 Timer 名称/字段子串泛化。两role都是 AutoHideParticles._ready 动态创建的子Timer，只有 timeout→该粒子timeout→hide。 |
| 同两role；下表7 lineage/provenance 字段；pre_activate | 14 | 可排除 minimum 初态，必须原样保留 legacy frame 的位置、原生身份、birth/start/stop/callback资料，不能据此删除完整frame调度节点。 |

Timer 20字段逐项名单：`Timer.process_mode`, `Timer.wait_time`, `Timer.time_left`, `Timer.one_shot`, `Timer.autostart`, `Timer.paused`, `Timer.stopped`, `Timer.node.native_id`, `Timer.node.role`, `Timer.node.path`, `Timer.node.name`, `Timer.node.class`, `Timer.node.positions`, `Timer.node.priority`, `Timer.node.inside_tree`, `Timer.node.ordinary_physics`, `Timer.node.internal_physics`, `Timer.node.ordinary_idle`, `Timer.node.internal_idle`, `Timer.private_left`。

Lineage/provenance 7字段逐项名单：`Timer.lineage.timer_id`, `Timer.lineage.owner_id`, `Timer.lineage.kind`, `Timer.lineage.starts`, `Timer.lineage.stops`, `Timer.lineage.birth`, `Timer.private_provenance_label`。

上述27字段都以两个精确role绑定到相同 UI Timer闭包；标识/拓扑/调度字段对完整legacy重放仍有价值，但不构成纯战斗初态合同的必需输入。排除资格不是对其实际值或私有构造初值的证明；不得用公开零值填入缺失私有计时器数据。

## AutoHide 回调闭包

Utility/AutoHideParticles.gd:5–10：Timer.new→one_shot=true→timeout连接自身timeout→add_child→hide。12–22 activate：stop，show，按one_shot restart/startTimer或emitting=true。24–30 deactivate：读取visible，emitting=false，依 lifetime*(1+(1-explosiveness)/speed_scale) 启动隐藏计时。32–33 timeout只hide。35–39 instantClear只stop/restart/emitting=false/hide。脚本完整1–39没有战斗事件、全局RNG、日志、伤害、增益或终止回调。两material只是ParticlesMaterial资源；未扩张到无关UI树。

KingGoobert.tscn只有123行的BuffTimer→buffEnded连接。BuffTimer是另一角色，必须保留；其gds:31–37真实业务条件读取invuCharges/isVulnerable/checkMana，先setState(Active,true)，再makeInvulnerable并启动BuffTimer、useMana。40–44的buffEnded按剩余charge产生Inactive或Used的state日志。不得因为state视觉表现简单而移除该Timer或回调。

## crown 初态与日志历史分界

Item.gd:4802–4804每次setState先snapshotItemState再onStateChanged。King.prepare:24–25保留Inactive(0)；doCooldownEffect:31–35保留Active(1)及withNextEvent=true；buffEnded:40–44保留Inactive(0)/Used(2)及withNextEvent=true。

CombatLog.gd:503–515保留eventNum、显式event.id优先、withNextEvent的+1关联、logItemState和loggingFinished后的activeItemState更新。CombatStatLogger.gd:85建itemStateHistories；96–103写/读；StatHistory.gd:7–10按相邻相同value压缩，因此“保留每次snapshot调用”不等于新增重复history行。CombatLog.gd:209–213用历史初始化重播缓存，614–620按历史比较activeItemState后调用onStateChanged。它们是完整观测/日志重播合同，不能因排除 observer initial crown 而删除或过滤。Character真实Invulnerable日志同理保留（Character.gd:1048–1050、1058–1060；setStat:1621–1622只是相应重播显示）。

## 必须保留 / 未证明

Character.invulnerable、invulnerabilityItem必须保留：Character.gd:571的受伤分支、655–656的isVulnerable，1037–1061的timer/事件/来源依赖；Character.tscn:1669的InvulnerabilityTimer→invulnerabilityEnded必须保留。King.invuCharges/protectedBuffs/manaCost/activations/activationsToTrigger及其业务timer均不在排除名单。所有未纳入逐字段闭包的缺失项仍为required/unproven；本审查没有给缺失值默认值或derived资格。

## 保存审计的计数预期

116精确排除行＝4 bubble＋6 crown/light＋12 Particle getter＋80 UI Timer字段＋14 lineage/provenance。phase分布pre_prepare45、pre_activate71。按只读426覆盖后：排除102 DIRECT/SUPPORTED、4 SOURCE_DERIVED/SUPPORTED、10 MISSING/UNPROVEN。minimum保留1363行＝1289 DIRECT/SUPPORTED＋2 SOURCE_DERIVED/SUPPORTED＋72 MISSING/UNPROVEN。此数字只是保存数据投影结果预期，不是实现已验收或战斗准入。

完整116行键、逐行理由/源码位置和全部所读原版源码SHA256存于 `data/phase437-independent-source-review-first-001/source-review.json`，同时记录408/426输入哈希。原版与冻结证据均只读。最新trusted quota本角色未知；沿用父任务<=30保存暂停要求。

## 不变的严格通道与证明限度

精确排除只作用于minimum初态及其阻断投影；不得移除原版restart/hide/nativecalls、节点拓扑、回调或FrameDriver。所有RNG checkpoint、consumption、order，日志/父事件/顺序/历史和终态仍为独立严格必需通道。上述闭包仅证明检查到的GDScript中无业务或脚本RNG读写，不证明GPU/backend RNG或全局共享RNG绝无副作用。真实共享RNG依赖如未覆盖仍单列未证明，不降低严格RNG比较。未新增native研究。

报告生成后重新核对记录的全部原版源码及408/426冻结输入SHA256，均一致。
