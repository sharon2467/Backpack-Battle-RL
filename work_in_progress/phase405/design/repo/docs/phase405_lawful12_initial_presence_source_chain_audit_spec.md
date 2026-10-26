# 405 固定06 lawful12 初态 presence / SOURCE-chain 可行性审计设计

## 1. Requirements

本块仅DESIGN，先核来源可行性，再决定是否实施403的大reader/candidate/comparator。当前不读任何run/capture/12输入，不import或调用391 schema、361 reader、Timer/RNG/Engine，不写实现、helper、bundle或runtime。所有旧SOURCE及403保持immutable。原GD为行为权威，356/361 CLOSED，King未准入。

已允许读取的真实工程接受：data/phase401-root-native-attempt06/independent402-accepted.json，status ROOT_ACCEPTS_FIXED06_BOUNDED_TERMINAL_SOURCE_PROCESS_CONTROLS；它明确full12_business_or_input_admitted=false、models/inputbuilds0、native_process_clean_exit=false。其review指向data/phase402-independent-final/review.json，status INDEPENDENT402_ATTEMPT06_TERMINAL_CONTROLS_ACCEPTED_ROOT_PENDING。读取这些回执不等获得12文件读取权，不递归打开回执里的run路径；精确size/SHA见本设计source-api-pins.json。

后续唯一任务是判断固定attempt06每个所需初态字段是否能从已批准12合法输入及实际SOURCE链建立。报告不是genuine input接受，不生成fixture/runtime/draws投影，不绕过旧361闭门，不执行任何业务或模型；不利用终态/实际cleanup/EXPECTED反推初始值。

本设计采用最小成本方案：第一轮一次纯JSON分组/typed presence与SOURCE-chain审计，SUT调用0。只有这轮非缺证且未来Root另行明确批准时，才允许至多一次真实391 validate_sources_with_binding做structural-input-only校验；该调用不在第一轮release中自动授权。结构schema不能补fresh链，不为一个已知MISSING再调用大API。403独立review现已封：data/phase403-independent-design-review/review.json，status INDEPENDENT403_DESIGN_DIRECTION_ACCEPTED_PREIMPLEMENTATION_INPUT_AUDIT_REQUIRED；8295B / 854e23cf12a63a2f7a8dbecc85730dbd99dae7f58a20afef405c7e7b30e44108。其owner1819B / 887761ee0c4e01109702a692042746daab7c8b1fef8dd4fa45c05cda2911233c。两者须列入未来真实execution release；405仍无该release。

验收输出每字段只能是DIRECT_OBSERVATION / SOURCE_DERIVED / MISSING，另有validation_result和proof_complete。尚未获权读取时用NOT_ESTABLISHED_BEFORE_AUTHORIZED_AUDIT，不能预判MISSING或PASS。最终任何必需字段MISSING、不一致或不受支持就停止后续候选实施，由Root决定补SOURCE采集或缩小域；不得默填0/-1/NIL/white，也不拿Python默认充作native证据。

## 2. Design

### 2.1 权限与最小数据闭包

未来Root input-audit release必须固定本audit的新SOURCE owner/review、实际391tuple/schema/native_patch、已接受402review及Root回执、固定06 run身份、12精确文件size/SHA、允许SOURCE白名单、输出新目录、0model/0projection/0inputbuild/0expected/0native/0restore/0READY，以及SUT调用预算0。release在payload/sourcefreeze/review完成后才写，避免hashcycle。它不是旧361的king12-input-only-release，也不调用361来开门。

lawful names严格复用旧361 SOURCE_NAMES的12项：fixture.json、player_fixture.json、observer7-input.jsonl、observer7-lineage.jsonl、observer7-metadata.jsonl、observer7-primitives.jsonl、king-clock-checkpoint.json、king-clock-passes.jsonl、king-input-facts.json、king-ui-authority.jsonl、king-rng-checkpoint.json、king-slot-bindings.json。原11+binding仍12，不增加第13个业务输入。

新的audit工程SOURCE可读实际release/指定接受receipt及明确SOURCE文件；原run只允许上述12叶。禁止目录递归inventory、zip枚举、runtime/registration/allocations/events/history/final、postcleanup、king-final、endpoint、collector-cut、status/validation、diagnostic control、日志及/proc。402控制证明由其已封receipt引用，audit不重跑终态helper、不复读6control。若需要权外SOURCE或输入，只报告具体依赖并停相应证明，不能自行扩大allowlist。

独立review SOURCE及Root release完成后，单次audit按一个固定job执行：逐文件先canonical+regular+nlink1+不含symlink父链→size上限→hash→strict JSON/JSONL；读同一开口时记录fstat/lstat前后identity（dev/ino/type/nlink/size/mtime/ctime），结束原路径重新验pin，拒读中变动。只用stdlib本地JSON解码；不import新旧SUT或调用decode_sources。保原immutable bytes或一次读取的内存对象，不写入原件，不因source rows失败修改/重试。

strict JSON拒duplicate keys、NaN/Infinity、无效UTF8、空/非对象JSONL和额外行格式；typed标量校验区分BOOL/INT、decimal与REAL bits，原列表序不排序。只实现被此次presence审计直接消费字段的闭合小形状，不复制391完整validator，不把“JSON解析成功”称“schema PASS”。其余lawful对象可计行/byte/schema header并保pins，结构完整性明确NOT_FULLY_VALIDATED。

输入12每叶只进行一次业务解码；前后byte身份复核不算第二次业务执行。所有大小、JSONL行数及总量上限从实际391源码常量/source contract固定进入未来audit SOURCE，不能以当次run大小自适应放宽。report只保存目标typed字段/行seq/owner/来源范围和有限SOURCE依据，不复制整个capture，不重建原版。

### 2.2 分类与证明对象

报告每行至少有：field_id、phase（pre_prepare / pre_activate）、side_or_role、classification、validation_result、proof_complete、input_refs（12文件名、物理行号/sequence、JSON pointer、实际native owner、typed值或其精确bits）、source_refs（路径/size/SHA/函数/行区间）、allocation_chain、preparation_chain、writer_coverage、unresolved、explanation。任何拟定expected域值只属于约束，必须与actual_value分栏；尚无actual不写成observed0。报告不产Engine DTO，不建立运行可用alias对象；关系表仅audit provenance。

DIRECT_OBSERVATION：真实lawful字段在真实phase、正确owner且typed值明确。它仍须独立通过fresh域值/identity验证；DIRECT但值非fresh则validation_result=REJECTED，而不是降级为SOURCE_DERIVED改写值。

SOURCE_DERIVED：没有该字段直接观测，但每个证据义务均闭合：①实际对象新分配/实例化及稳定身份；②实际constructor/scene/configuration及准备路径必经；③pre→act全区间可达writer枚举（含继承、信号、deferred、Timer、UI、外部赋值/反射）；④实际域条件令其它writer不可达，或能按SOURCE固定顺序推得值；⑤同一owner/phase无未解释间隙；⑥实际输入相关旁证与推导一致。仅grep无匹配、Python默认、partial excerpt、future schema PASS、birth标签或最终快照都不足。SOURCE_DERIVED明确不是native getter直接观察。

MISSING：不存在直接字段且上述链任一未建立；必须列缺了哪个对象出生、writer闭包、scene/property配置或实际phase依据。来源缺项是结果，可合理终止审计，不是让审计器构造默认的错误恢复分支。原文件若malformed或身份不符属于审计FAILED_SOURCE_INTEGRITY，不给任何可用初态结论。

### 2.3 精确字段与SOURCE路线

| 必审目标 | 合法直接位置 / 待证明SOURCE链 | 本设计静态结论 |
|---|---|---|
| Character.buffProtectStacks：P/O，pre与act | observer7-input checkpoint.payload.source_resources按P/O两行，side/native_id同nodes.character:<side>；391sink.source_resources写typed INT，schema.validate_resources校owner/type/buff ledger。 | 确有DIRECT carrier，不是四字段全缺。实际presence及INT0仍未读；缺行/错owner/非INT/非fresh分别阻断。 |
| Character.invulnerable / invulnerabilityItem / invulBubbleVisible：两边pre/act | checkpoint append_node只含node/Timer，没有Character.state；三值仅source_runtime_snapshot的postcleanup/final直接观察，禁止读。需Core/Character声明false/NIL/false、constructor/cleanse/prepare与全writer可达链。 | 无本checkpoint直接carrier，SOURCE_DERIVED候选；默认不证明实际新对象。Game.instanceCharacter有PLAYER已存在则INVENTORY.reset复用分支，必须由实际合法身份/固定collector流程排除不支持旧战斗路径，不能只看到新item就推Character新。 |
| King invuCharges与activations、activationsToTrigger/protectedBuffs/manaCost | checkpoint.payload.items中P:12 fields：pre charges INT0、act INT3；schema.validate_single_king_source_defaults要求INT descriptor262/activations0与REAL6/3/4。精确prepare源码 getP charges→setStateInactive→父prepare。 | 现API已提供直接typed约束；实际序列/owner与source params仍要审。prepared3只验证prepare结果，不能替代constructor0。 |
| Crown argument与CircleLight visible/self_modulate | 不是独立native stored crown getter；King prepare调用setState(Inactive)，父Item.setState到King.onStateChanged写light白/显示及AutoHide.deactivate；审完整继承/scene/property/调用顺序及实际fresh King/无UI writer。 | SOURCE_DERIVED候选；不能读取最终crown_last_observed_argument补初态。若仅有partial332excerpt不够，列MISSING。pre与act必须分别证明，不把act的prepare结论提前用于pre。 |
| activation/drag Particles2D配置/visible/emitting | facts.kings[0].activation/drag、pre/act item嵌套fields、UI bind关联具体native owner，AutoHide.ready hides/config以及实际getters。 | 公开direct配置与fresh域证据可核；light不等particle visible，不能串用。 |
| 35个公开Timer的全role配置/flags/time_left | 两个checkpoint.nodes全部timer非NULL行，mode/wait/timeleft/one_shot/autostart/paused/stopped与node path/positions/priority/四processing flags；与schema/facts的nativeID及owner join。 | 必须按完整role集合核，不以数量35替代角色/身份。公开+0/stopped只DIRECT public状态，不证明private。 |
| 5个新增选定Timer private初态 | invu:P、invu:O、king_buff:P:12、king_hide:P:12、king_drag:P:12；facts.timers每项lineage.birth/current/owner/kind/starts0/stops及private_provenance，结合真实constructor/scene/autostart/调用instrumentation完整性。 | private只能SOURCE_DERIVED -1，从未直接observed；starts0不是单独充分条件，需birth覆盖及所有start入口可信，尤其Timer属性写/继承。 |
| 其余30Timer private初态 | tick:P/O(2)、buff:P/O:100..110(22)、fatigue:start/tick(2)、aux:P/O:battleRageTimer/autoRageTimer(4)。从各自constructor/scene/Buff.init配置到pre/act无start链，按角色分别审。 | 五Timer fact不能外推30；aux固定class0/noRage条件与实际六ID绑定必须成立；任何Timer缺no-start证明，单独MISSING。 |
| 关联前置域 | 固定fixture P20/O19、O:12缺口、六ID、class0、39实例，lineage scene/ready无pool复用、metadata scene identity、binding关系列表、UI完整no-unsupported窗口、原始prepare/activate checkpoint邻接。 | 仅用于证明初态，不投影runtime；既有源码字段能力不等actual12已具备。 |

35=2 tick+22 buff+2 fatigue+4 aux+2 invu+3 King。raw buff角色数字保留，再与SOURCE Buff enum映射作证据；不排序改写原输入。任何多/少/同nativeID跨role或current/birth换owner拒绝。Engine的active31与4 inert aux建模区别也记录，不能将aux未实例化的模型结构当native缺Timer。

SOURCE_DERIVED图不需要模拟时间/抽随机数，也不能通过执行GD/Python求值。静态推导只接受SOURCE已固定的constructor/config、不可达writer排除与实际输入域；任何需要运行业务来决定的未知值保持MISSING，不建立微型模拟器。

### 2.4 有限SOURCE依赖与身份原则

本设计实际API清单涵盖391 schema纯函数和sink/collector固定producer路径；finite-source-allowset.json额外直接固定11个完整baseline GD与其391执行after-source对应关系、2个已有SOURCE合同精确标识的完整scene（Character、King），只读SOURCE而非run。所有原GD的before SHA与391native_patch逐项核对，after SHA同样核对；scene与349合同descriptor核对。此有限allowset可支持随后writer证明，但未宣称覆盖所有继承/scene外部资源/动态writer。after-source的Core/Character/Game/Buff、Items/Item/Goobert/Food/Exclusive/KingGoobert、AutoHideParticles、Util、CombatTimer为有限已存在源码。每个after-source文件必须与391native_patch.paths对应after_path/size/SHA一致，不能因为目录名359就以旧359 producer接受替代391身份。对未改scene、类继承及engine Timer constructor的完整出处：现349 defaults合同只作索引，332 excerpts只作候选指针；未来审计SOURCE预备阶段须选出实际所需完整SOURCE普通叶、pin并绑定到执行基线/patch closure，独立review后入只读白名单。不得扫描/读取livepool，也不随任意元数据路径追进run。

405不自称这份有限列表已证明全writer闭包。若实现audit所需更多SOURCE超过名单，先给Root精确路径/用途/已知descriptor及scope supplement，获准后预封，不在实际audit中递归查找补依赖。没闭合SOURCE的字段可以直接输出MISSING，不为了“成功”拓宽域。

### 2.5 真实391 structural API的可选后门槛

仅在0-SUT审计没有必需MISSING/REJECTED，且独立审查认定值得继续后，Root可另发schema-only release，最多一次：tests/phase391_king_observer_schema.py::validate_sources_with_binding(raw11:dict[str,bytes], binding_bytes:bytes, source_contract)；source_contract必须为同一精确模块的BINDING_SOURCE_CONTRACT。API精确pin见inventory，module现208243B / ffcddfd2cbe58307f7258c1aefad5586a9179c6c452dc59c3342f9047f31457c。先验整个模块及其stdlib依赖、只加载这一个SUT模块，不import361/Engine或用户回调。

它内嵌顺序validate_binding_carrier→validate_source_carriers→decode_sources→join_binding_provenance；返回phase360-twelve-source-proof/1且SOURCE_PROOF_ONLY_NOT_INPUT_BUNDLE_OR_NATIVE_ACCEPTANCE。内部decode可多次发生，审计区分top-level1和nested实际调用；不另从外层重复调用子helper“补测”。shared_consumption_closedFalse/producer PENDING历史字段不改写成接受。即使成功，也只加STRUCTURAL_INPUT_ONLY_VALIDATED状态，SOURCE_DERIVED证明仍由独立source-chain证据决定。失败原trace/所有pins封存，不改schema/inputs、不自动第二次调用。

## 3. Realize / 后续拟实施接口（本轮只写设计）

1. 拟新增verify_audit_release(source_root, release_descriptor)→Authority：before-read普通单链接/canonical门；strict release schema、实际405后续SOURCE/review/402/Root与391tuple、12精确名单/readonly根、权限计数0；若没有实际新release，在任何run文件打开前拒绝。不接受caller ready或外部validator。
2. 拟新增read_lawful12_once(authority)→RawSources+identity observations：只读12，bytecap/strict JSON/物理序/前后pin；不开放glob目录；io audit记录open范围。decoded按文件原序保存，只作presence索引，不构造模型输入。
3. 拟新增index_initial_observations(decoded)→InitialIndex：固定两个checkpoint site/edge唯一；其后enter邻接/同stamp；resource P/O owner、item P:12、35Timer原row与facts五项、binding/scene/ready/UI域索引。保实际sequence/line/JSON pointer/owner及typed值，输入对象不可mutation。index不是已验证alias许可。
4. 拟新增audit_direct_fields(index, approved_constraints)→rows：buffProtectStacks、King typed默认及Timer公共字段逐项presence/type/domain/identity；不以schema默认补缺。DIRECT_REJECTED与MISSING分开，分别提供exact first discrepancy。
5. 拟新增audit_source_chain(index, pinned_source_facts)→rows：对Character3、pre/act crown/light与35Timer private义务构建已审有限proof graph。逐edge引用实际输入identity/phase与SOURCE函数/branch，枚举writer入口/是否不可达及理由；不存在实际分配/no-writer依据就MISSING。source_facts不得只存一个verified布尔，应有所有可重读文件/范围及不确定项；不eval/GD解释或执行候选。
6. 拟新增assess_initial_feasibility(rows)→report：必需目标集合固定、不接受缺行；全rows只有DIRECT_OBSERVATION或SOURCE_DERIVED且proof_complete且validation_result=SUPPORTED才可FEASIBLE_PENDING_FULL_STRUCTURAL_VALIDATION；否则BLOCKED_INITIAL_SOURCE_GAPS或REJECTED_INITIAL_DOMAIN。两者均不叫genuine input接受。unknown、新字段值异常、identity drift等原样保。
7. 拟新增seal_audit_once(report, before, io, source_refs, output_dir)→receipt：exclusive新目录，JSON flush/fsync/读回，source/input后验pins及owner；0-SUT/0bundle/0model实际计数；错误也保存first trace与已消费file identities，不清理、不重试。输出只报告与证据，不含五key bundle/17-keyruntime/Tape或待运行carrier。
8. 可选另job validate_structural_once(raw12, authority)→existing391 proof：只在另Rootrelease且topcallbudget1，按2.5执行；未来实现不能把此接口作为0-SUT audit的自动fallback。结果单独owner，旧audit报告不改签；structural失败停止candidate实施。

本轮actual-api-inventory.json记录真实391函数签名/行号/SHA及sink checkpoint/source_resources/timer facts、collector流程函数的真实文本SHA，拟新增函数不混入“actual API”。四节SPEC获独立设计review后才写上述audit实现；实现SOURCE再次独立review与Root释放后才读12。当前所有可行性字段保持NOT_ESTABLISHED。

## 4. Acceptance Criteria / 有限验收与退出

405设计验收：准确区分buffProtectStacks直接载体与Character另外3字段；初态字段表、35/5/30Timer集合闭合；实际API/source pins及真实402Root回执对应；预期来源只能lawful12+明确SOURCE，任何expected/终态/模型默认后推被禁止；0-SUT首轮与可选schema-only另门不混；新设计owner封后停写。

未来audit实现独立SOURCE审只需固定8项逻辑义务，确切API次数由该实现review预封，不运行战斗：
1. 缺release/错401identity/错402Root/多文件权限在12读取前拒绝；不能使用旧361打开。
2. before-read canonical/regular/nlink1；symlink、hardlink、special各一个有限拒绝变体；输入身份变化拒绝。
3. strict JSON重复key/BOOL冒INT/REALbits错误与physical row顺序各一个坏变体，不靠SUT放宽。
4. buffProtectStacks实际owner/INT0与phase，缺一side/换owner各拒绝；另外3字段不因缺direct自动填默认。
5. SOURCE_DERIVED proof graph缺allocation、prepare边、writer覆盖各一个坏变体→MISSING；同一正确链只证明其已覆盖字段/phase，不跨phase外推。
6. 35Timer角色唯一；五fact缺starts/owner、其余30缺no-start各一个→MISSING；public0不能使private证据自动PASS。
7. King0→prepare3与crown/light实际合法SOURCE链分开；final值污染或prepared3写constructor拒绝；预封output不含runtime/bundle/draws投影。
8. 单次readonly audit计数与输出exclusive；SUT全0，EXPECTED/run其它文件open拒绝；schema可选job没另release即拒绝，已授权至多一次且失败不重试。

真实audit只固定attempt06一次，逐字段如实分类；不改seed/布局、不追终态。若出现MISSING，报告最小需要补的SOURCE证明或新的INPUT采集字段，禁止原capture后补造字段。对可补SOURCE链也先独立审引用证据，不能把“可以证明”写“已证明”。若无缺项，先独立验报告，再决定一次structuralAPI是否必要与单独release；尚不授权403候选实现/输入bundle/模型。

所有声明保持：RNG Tape是未来条件重放，405不构造Tape、不恢复seed/state；native private Timer无直接观测；cleanfalse与zombies事实不被输入可行性覆盖；King生产/全引擎/RL仍未完成。405无SUT/native/model/inputbuild/capture/EXPECTED操作，也未申请改变旧门。
