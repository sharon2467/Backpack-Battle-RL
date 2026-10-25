# 361 单King最小projection/sealer设计与字段流

## 1. Requirements

仅设计未来合法输入投影与一次封存，不实现/导入/运行projection、runtime、collector、host、Godot、输入build或模型。本文件不解除356门。若360独立审查发现缺陷，先处理该窄修，不据本设计继续实现。

边界仍为固定351A（5561B/b62bb554）、355对应fixture与359原slot表：双方class0、六ID、全局单P King、无gems，39个实例，O:13..19且无O:12。不按未来结果选盘/seed。原生未来global35301/util35302是配置；production32103不是原版session seed，原生RNG checkpoint也不能配置Python生产RNG。生产headless保持独立双流，无需Tape/oracle/expected；这里Tape只是有限原版对照入口。

359仅producer SOURCE组件已接受：root回执 `data/phase359-root-acceptance/accepted.json` 1257B/8fbcb714，状态 `ACCEPTED_SOURCE_COMPONENT_PIPELINE_BLOCKED`，24/24，无Godot运行。360 freeze2080B/9d886add正在独立差分门，不能宣称通过。既有356十五源freeze2783B/a135fc77依然closed。全部实际12载体、collector、projection/共享准入/host及native门均未存在。

## 2. Design

### 实际ABI与三类数据

`native_replay_v8/observed.py::run_input_bundle` 的真实bundle准确五key：`schema='native-v8-input-only/1'`、`fixture`、`runtime`、`draws`、`synthetic_seed`。genuine必须draws非NULL且synthetic_seed为NULL；先验证fixture/runtime再构造TapeRandom/Engine。未来新的共享来源门必须仍先于这些构造，不能因为准备了本投影器就删除356 pending或接受旧patch。

区分业务输入、验证envelope、外部proof档案，不能以“runtime里有字段”推定它驱动业务，也不能把“已校验”当成可任意拷贝观察值。当前356 King genuine runtime准确17key，由 `engine.validate_runtime_inputs`、`_validate_single_king_initials`、`_validate_runtime_nodes`、`_validate_single_king_processing_inputs` 和 `genuine.validate_profile` 约束。`CombatEngine` 保存经深拷贝的RuntimeDTO；以下明确各字段随后是否被读取。

| runtime字段 | 合法来源与投影规则 | Engine真实消费路径/含义 |
|---|---|---|
| schema/mode/profile_id | 冻结新genuine代码常量，非raw自由值 | validator/observer标识；本身不产生效果 |
| checkpoint | activate entry实际Util.time、combat_time=0及准确source_phase；与clock header join | validate_runtime_inputs检查；activate_from_checkpoint设置Util.time。合法外生时钟原点，不是HP/Mana等内生状态 |
| environment | 实际已校验60Hz/scale1/unpaused；no_pending_gameplay_transform须完整fresh/UI/placement来源支持 | validator/scaffold环境约束，不允许caller布尔代替来源 |
| nodes | 实际pre/act连续身份的path、positions、priority、kind；Timer只配置wait/oneShot/mode | build_runtime_scaffold建立调度树/Timer；不复制Timer time_left/private剩余量 |
| timer_lineage | 出生/配置/owner/无start链验证后，写固定语义fresh_configured | _validate_runtime_nodes检查；TimerRuntime按真实constructor建立private状态，不能把public0反推−1 |
| initial_items | 只SOURCE constructor limiter零值：REAL+0时间、INT0 counter、dragged=false、moveback=false；cache_fresh是fresh门结论，不是cache内容 | _validate_single_king_initials验证；activate_from_checkpoint写四limiter字段。不能从任意act观察回填新状态 |
| prepare_order/activate_order | Game两个原始entry的items native refs，经已验证alias转原instanceID；各39唯一且原顺序相等 | prepare真实遍历、effects及activation真实顺序；不是来自event结果或sorted targets |
| terminal_profile | 固定SOURCE算法名source-two-physics-idle-pre-internal/1 | 选择既有cleanup/barrier规则，不含观测终结时间/赢家/停止frame |
| frame_clock | 完整实际clock header+原顺序physics/idle passes | 旧finite FrameDriver严格消费真实外生delta；业务自行request_end后验证两futurephysics+首idlepreinternal/EOF，不能用endpoint强迫死亡/结束 |
| king_particles | 已证fresh配置及真实node拓扑；default lifetime REAL32→REAL64 bits、explosiveness/speed/flags必须与SOURCE精确相同 | constructor保存合法fresh particle_facts；既有粒子/AutoHide/Timer过程由原代码演算，不读取未来观察纠偏 |
| root_node | 实际fresh root身份/processing flags，与UI controls和clock同root | build_runtime_scaffold取root internal_idle等调度事实，非任意GUI输入 |
| processing_nodes | 实际完整80 raw节点，准确role转换，保原flags/positions/priority/identity | constructor.processing_inputs与ordinary/internal调度、快照读取；属于合法fresh调度拓扑，不能由plan填nativeID |
| inactive_auxiliaries | 实际fresh aux Timer配置+六ID/noRage SOURCE调用域lemma | _inactive_aux_full等验证/快照；不能以异常public0为可接受private状态 |
| ui_authority | **现有必需validation-only ABI**：完整raw UI独立序列/open-close/foreign分类、实际root/King/particle/selected join | _validate_single_king_processing_inputs重验并关联身份/processing flags；RuntimeDTO会保存它。已读SOURCE中无UI事件执行器，不把UI当业务命令、初始资源、随机或终止指令；runtime结果投影不靠UIfooter停战 |

ABI关键点不能掩盖：旧runtime确实含raw `ui_authority`，而且validator要求完整carrier。最小兼容方案保留这个validation-only字段，全部原件也存外部proof；不为“完全剥净”措辞重写15源。该方案需未来SOURCE/独立门核所有UI读取确实只验证、无内生写入或截止驱动。另一方案是后续窄拆validator proof-context参数，把rawUI移到独立envelope；具体代价是改validate_runtime_inputs及三条共享profile入口、observed runner/compare调用与独立隔离包，需新candidate15和回归，当前不实施、不默认为必要。无论选哪种，UI观察都不能作为业务初值或业务输入事件。

### 模型之外的proof与expected

12原件来源为原两fixture、四物理observer源、clock header/passes、fresh facts、UI、RNGcheckpoint，加 `king-slot-bindings.json`。各自原bytes/size/SHA先封存；raw行的NULL role/stamp/sequence不回写。360 alias context是来源关联工具，不是已接受票据；descriptor可共享、item native不可重用，原input-slot与实际库存遇见顺序分别保留。需要翻译的运行时副本另建，不覆盖source rows。

外部 `input-proof.json` 保留绑定关系、各来源hash、metadata/default/private/cache/resource验证、原RNG来源与projection字段来源索引；不作为run_input_bundle的第六业务key。模型不读取该文件进行补状态；runner只核其jointseal/身份。原 `king-rng-checkpoint.json` 的seed/state只来源验证，native返回逐行Tape才合法；不要由state补漏draw或把seed32103/35301混用。

King charges0→prepare3、protectedBuffs REAL3、manaCost REAL4、Mana/保护INT ledger、invulnerable/origin/crown、full cache/currentAffectedItems/prepared迭代值均只核SOURCE/观察一致性，不写入runtime新字段。constructor、prepare和真实effect计算这些值。particle/default字段只有上表明确的fresh构造事实可进入旧ABI；不能扩大为任意default观察白名单。

`observer7-runtime/allocations/registration`、events、histories、final、king-post-cleanup-source、king-final-source、capture-endpoint与赢家/事件计数都在input reader白名单外。input提取及模型隔离目录无expected；仅在两方输入typed一致、各一次模型jointseal后，root另expected release才由比较器读取这些档案。clock passes有有限尾是原生外生记录，不从endpoint合成/截短；错业务耗尽或多耗必须报EOF/trailing，不添加尾巴救比较。

### raw字段到Tape的准确边界

只用observer7-primitives原物理顺序：randf→空args+原REAL value_bits；randf_range→原端点bits+value_bits；randi_range→strictINT args/value。本K1无Mirror，global_u32必须0，不能放宽为任意原始global返回。保原label/context及King invulnerability_pitch:P:12；Node/Timer/callsite REAL/typedcallee INT不在adapter随意强转。既有Util.roll源码规定的INT0端点转REAL+0.0是需逐site列明的ABI转换，未知INT/类型转换一律拒绝。不排序、重采样、跳过singleton消耗、补draw或从RNG checkpoint推导返回。

raw buff角色使用数字category，旧runtime角色采用STACK_NAMES_BY_TYPE的symbol名；建立精确原SOURCE映射，例如Mana=105、103=Vampirism。仅在新副本中转换envelope role；item:P:n与inner P:n、character:P与inner P也分别处理。不能通过连续enumerate重造O角色或凭nativeID数值排序决定业务顺序。

## 3. Realize

后续root再放SOURCE实施时，最少四个职责函数；不新增通用schema框架。

1. **`read_and_validate_sources(release, lawful_dir)`**：readonly读取准确12原件，先查release/owner/SOURCE与byte caps，再调用已独立接受的360组合入口。无accepted receipt就关闭；不能只验VERSION或caller bool。返回原bytes、已验证DTO和alias/proof。未来capsule只镜像实际SOURCE闭包+12原件，禁止Game/pool/network/expected/对方actual读取。
2. **`project_fixture_and_runtime(validated_sources, aliases)`**：固定A精确映射39角色；按上表逐字段构建17-key旧ABI，输出业务/validation-only字段各自来源表。每个模型初始值要么来自合法fixture/fresh topology/clock，要么来自明确constructor常量，不从准备后状态倒推。实际prepare/activate items ref集合/顺序、source scalar类型、Buff角色转换全核；无外部callback或monkeypatch来容错。UI兼容方案须先由root选定并经SOURCE门。
3. **`project_primitives(validated_primitives, aliases)`**：逐原row校验实际schema/context/调用ABI，做上节逐项转换；输出非NULL完整draws，synthetic_seed=None。source rows/payload不改。无generic scalar/table后顺手接受BOOL或REAL别名；每次转换须可追到原row sequence。
4. **`seal_once(bundle, proof, before, output_dir)`**：先写exact来源pins与执行前身份；build一次，xb新文件、fsync、实际读回bundle/proof/before后立即jointseal，之后才写工程摘要。failure保存完整现场，不修数据自动重试、不以成功模型做checker回归。两角色独立SOURCE capsule/各自build，root逐typed/floatbits比较后再放模型；author无自签FINAL权。

共享身份不是第五个随便返回true的helper。未来genuine input-profile/result-profile/runtime前置/compare必须同传并验证profile+fixture+实际patch report/diff/全部before-after+schema+collector+projection+candidate来源的同一精确tuple；model前检查自身SOURCE和输入seal。旧307合法patch不能与新355 profile分别过门后组合成准入。旧356源保持原样，未来解除须新candidate冻结、具体SOURCE差分和独立反例回归。

当前tuple状态：359 producer source/review/root门实际有据；360独立接受尚待；**collector、固定slotmap的实际置入调用/11+aux文件闭口、native config/host/lease/archive、projection/sealer/隔离reader、联合身份的新candidate** 均缺。只有真实新组件完成才填实际pin，不在SPEC编fake hash/通过状态或先开放旧profile。旧King154/178固定fixture特权和legacy sealer连续enumerate/旧prepared白名单不能直接搬来。

## 4. Acceptance Criteria / Tests

未来独立有限SOURCE合成控件先封，不重复已有成功批：

- 完整17 runtime/5 bundle key合同及每字段writer/reader对照；UI仅验证/存储，禁止任何observer值改HP、Mana、保护、charges/crown/cache、随机消耗或结束条件。若proof变坏只能拒绝，不得修正业务状态。
- 固定A/O缺口、descriptor共享/native唯一、角色数字Buff→symbol、prepare/activate39项及原序、Timer/particles fresh来源守恒；缺birth/有start/unknownprivate值不以public0补齐。
- 原primitive ABI按位/strictINT/physical顺序保留，错label/type/位串、global_u32>0、重复/逆序/错file和漏singleton均拒绝；RNGcheckpoint变化不能成为生产seed或补draw来源。
- proof/default/resource/cache/terminal或extra业务key污染拒绝；明确只读这些证据的validator与模型实际writer边界。禁止从king终态导出初值、复制prepared charges3或准备后Mana/buff ledger。
- 新profile+旧307patch、缺schema/collector/host/reader/source owner、错fixture、伪ready或未接受receipt全部在Engine/RNG前拒绝。未知真实SOURCE pin仍缺失即失败，不靠unit positive冒充actual12 native positive。
- 完整clock只靠原finite FrameDriver的业务request_end+双physics首idle闭口验证；缺尾/额外尾/early endpoint必须拒绝。保实际exit0与cleanexit独立状态。

当前完成标准仅本四节设计与字段流表，全部输入build/模型/native/Godot/RNG/Engine调用为0，无新代码/candidate/准入或正式75写入。后续实现、实际12输入和native/expected各需root另门；King/RL整体未完成。
