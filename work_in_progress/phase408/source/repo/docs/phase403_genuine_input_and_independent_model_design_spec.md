# 403：391捕获至 genuine 输入与独立逐事件模型比较的设计

## 1. Requirements / 需求与边界

本轮 DESIGN ONLY。398已封源码不动；356 genuine admission 与361 reader仍 CLOSED。Root报告401 attempt06完整捕获，但402控制验收尚未提供本设计可依赖的最终身份。本设计不读取run/capture、不读business EXPECTED、不调用或import任何SUT/schema/FrameDriver/Timer/RNG/Engine，不生成输入bundle，不改模型/采集器。Root报告的142.948959493s、hostexit0、capture_complete、actual tail8、Gameexit0但cleanfalse/Z27771仅作未在本轮复核的任务背景；不写成403验收事实。原版源码为行为权威，纯战斗；正式75不变，King262不晋级，模型调用0。

目标是给后续独立设计review一份可以实施的最小闭包：先真实捕获控制接受，再新SOURCE联合绑定，再仅12合法输入构建及独立来源核验，再单次有限模型执行，最后独立输出比较。每步独立授权/验收；不得以捕获成功、SOURCE PASS、seal_once成功或纯351轨迹PASS替代下一门。旧失败05、旧356/361、全部SOURCE及首错保留。

成功的科学结论只能是固定A、原1.1.8、双方class0、六ID1/4/11/19/22/262、单King、无gems/modifiers的有界条件重放逐事件比较；不等独立同seed复现、任意King域或生产/RL完成。不要为扩大结论再采集、换seed/布局或重复旧已通过349/351控件。

本目录source-api-inventory.json记录从实际源码AST读取的函数签名、行号、函数完整源码SHA及模块size/SHA；source-pins.json是有限显式源码清单，不递归读取owner所引用的run文件。所有 future 接口在下文标明“拟新增”，不是已实现API。未来阶段编号/执行回执不预造。

## 2. Design / 架构、兼容和字段来源

### 2.1 已有实现的实际边界

356的genuine.require_single_king_admission()无参数且无条件raise；validate_profile、validate_result_profile及engine.validate_runtime_inputs均先调用它。355独立profile谓词与旧patch接受可错误组合的缺口仍是解除门的核心约束。当前常量是observer7-355-native-single-king-A/1及7-king-single-A-355；391实际为observer7-390-native-single-king-A/1及7-king-single-A-390。schema中保留phase355等结构名不代表旧producer可接受。

361 reader导入phase360_king_observer_schema、绑定359/360 SOURCE receipts，在读release/capture之前固定拒绝。它的四职责已有read_and_validate_sources/project_fixture_and_runtime/project_primitives/seal_once。bundle只有schema/fixture/runtime/draws/synthetic_seed五键，runtime17键。现seal只做工程封存，不验证真实native准入；孤立直接调用投影/codec不是新reader gate的替代。

391 tuple已给schema/sink/collector/producer/native_patch/fixed_fixture和projector_source_origin描述符。该origin是旧361历史来源，不能改391tuple伪装新投影已接受。新建非循环 downstream-admission-contract：引用真实391tuple+执行source closure+402最终控制接受+新reader/candidate/comparator freeze，旧tuple保持原字节。新候选内code-bound contract固定profile↔version↔tuple；实际run身份、source hash和input jointseal通过额外工程执行release校验，证明对象不进入Engine运行状态。

349 finite FrameDriver已饱和减physics_signals_remaining，清理后设2，后续physics降至0保持，首实际idle在internal/ordinary之前finalize；run拒EOF及trailing。无需改成C+2，也无需改TimerRuntime。351 headless采用Fixed60Passes/HeadlessKingFrameDriver，其交替/14404capacity是另一纯SOURCE域，不可拿来替换genuine完整clock。351 checker terminal_check硬编码C+2、交替及2*physics，不能原样用于批处理实际流。

### 2.2 阶段与数据流

402独立真实控制接受 + Root捕获身份release
→ 新只读输入reader（代码绑定391tuple、新candidate、新reader/schema身份）
→ 仅12文件完整字节/来源/初值验证
→ fixture/runtime/Tape + 独立proof，原件读前/读后pins
→ 一次jointseal与独立输入审查
→ Root模型release、精确SOURCE加载、只允许bundle输入
→ 一次Engine执行、原始result+同实例诊断封存
→ 独立checker才获EXPECTED访问，联合新tuple/run/output pins
→ 按原始顺序逐事件/parent/state/RNG/Timer/API/scheduler/终态比较并封报告。

实际控制/权限文件供工程gate，不作为第13个合法业务输入。input reader不读取endpoint、cleanup、runtime输出、postcleanup/final或诊断control行来造输入。Control验收中的cleanup C与actualN只能在最后输出比较。UI footer已包含在旧17-key ABI，严格validation-only；不进入stop条件、不裁clock、不构造callback序列。genuine运行使用整条原始exogenous clock；EOF本身不结束战斗。

同一捕获固定来源无需根据比较结果反推。缺失或不受支持字段必须fail-closed，保存首次失败并回Root。若需要补采集，必须另开新的producer/schema/tuple/native授权，原attempt06不补写、不改签；既有模型结果不重跑作checker调参。

### 2.3 每组字段的来源与禁止流向

| 字段/状态 | INPUT或SOURCE合法来源及入口 | EXPECTED_ONLY及缺失处理 |
|---|---|---|
| fixture双方class/health/stamina/item ID/几何/旋转/顺序 | fixture.json/player_fixture.json与391固定A核对；king-slot-bindings关联实际native/owner/descriptor；保O:12缺口及O:13..19身份 | final_state资源不可补初始HP；不得连续enumerate O或从结果选择fixture。 |
| nativeID→role、39项顺序、prepare/activate边界 | input checkpoints+enter、lineage scene/ready、metadata descriptor、binding12的联合证据；早期NULL role不重写 | events/runtime ID只由已封alias解码，不能反向发明初始节点。 |
| clock header、每pass kind/p/i/delta bits、activate Util时钟 | king-clock-checkpoint.json+完整king-clock-passes.jsonl，schema.decode_clock同型严格验证；checkpoint与activate实际join | endpoint/cleanup/firsteligible/actualN不得传Engine；后验比较模型自己算出的C/尾段。原始batch8保8，不能合并/补idle/截2。 |
| environment及root/processing/node flags、aux topology | clock环境、fresh事实、input activate节点和完整UI权威；独立保四processing flags，source无调用lemma约束aux | final节点flags不能初始化；缺identity/完整membership或非静态UI条件拒绝。 |
| Timer配置/lineage | input实际节点配置、facts五个King/invu Timer出生和starts0、其他Timer原接受SOURCE构造链；只拷wait/one_shot/mode/路径与fresh lineage | public time_left=0不能反推private=-1。fresh constructor/no-start与配置链不完整即阻断；不默设0/-1。原版private未暴露，不能宣称private观测等价。 |
| initial_items limiter/cache/consumed/drag | prepare及activate完整合法checkpoint验证fresh；初值取经源码固定的constructor值，cache由模型prepare计算 | 激活后的cache/remaining/counters为断言，不复制缓存/状态。任一非fresh拒绝而不“修复”。 |
| King初始invuCharges/protectedBuffs/manaCost/activationsToTrigger | schema.validate_single_king_source_defaults验证pre charges0/activate3、REAL3/4/6与typed字段；SOURCE prepare由0产生3，不能把3塞constructor | king_source_state最终fields全是输出；初始值/型或prepare链缺失阻断。 |
| Character invulnerable/invulnerabilityItem/invulBubbleVisible/buffProtectStacks | 391 character typed schema可表示这些字段；新输入门须显式定位合法pre/activate Character状态及SOURCE cleanse/constructor/no-intervening-writer链，要求与模型fresh值一致（BOOL false/NIL/BOOL false/INT0） | source_runtime_snapshot.characters_invu只有postcleanup/final，不是初始来源。当前361投影未完成这些字段fresh门，403未读实际输入确认存在；缺任一实际checkpoint字段或可靠链，必须补SOURCE采集/阻断，不能由最终值反推或仅信Python默认值。 |
| Crown与light/particle初始状态 | 源码prepare→setState(Inactive)→onStateChanged、实际prepare/activate合法字段/particle getters与UI no-call链；既有332 frozen excerpts/349默认合同作为可核SOURCE依据 | crown_last_observed_argument是实际onStateChanged参数，不是stored getter。最终crown_origin必须保留；初始crown/light若合法字段与SOURCE链不足，则阻断，不能用终态crown或默设0/white。 |
| activation/drag particle配置与flags | king-input-facts分离node/getters，AutoHide.ready及distinct Timer lineage；寿命/explosiveness/speed_scale保持bits | postcleanup/final visible/emitting/timeleft仅比较；不将业务输出变配置。 |
| primitive随机返回 | observer7-primitives物理行序，kind/label/args/type/value bits；只Util.roll INT0→REAL+0既有ABI转换；禁止global_u32于K1；Tape assert_consumed | EXPECTED事件/RNG统计不补draw；rng checkpoint seed/state只initial-condition proof，禁止拿来恢复内置RNG。只能称conditional_direct_native_primitive_returns；351 seeded/PCG律不是该Tape的独立同seed证明。 |
| Balanced RNG私有业务状态、history、resource变化 | 模型SOURCE constructor/prepare及每次真实Tape消费独立推进；全初始SOURCE freshness与资源门须核 | 原版checkpoint/state仅验证合法输入域或输出比对；禁止initial.expectedWins等从final/current状态复制；缺构造/连续来源先阻断。 |
| cleanup后35个公开Timer、invulnerability、King state、final UI flags | 不在输入中；模型以HP/death/request_end/finish与真实dispatch自行计算 | king-post-cleanup-source.json/king-final-source.json/king-collector-cut actual_final属EXPECTED；逐字段读并比较，private_timer_values标记不是数值。 |
| events/parents/allocated refs/histories/final、API argc/actualreturn、callback序 | 全为输出比较；model已封之后才读 | 不能裁业务到EXPECTED结束、排序掩盖原序、跳过未知site或丢弃不支持字段。 |

上述“可表示”不等实际存在/已验证。设计的缺源状态是NOT_ESTABLISHED_WITHOUT_LAWFUL_READ，不是假定401缺文件。新input gate必须产生逐字段presence+origin+type+SOURCE-chain覆盖表；缺失应明确报field/site/file，不能据EXPECTED补齐。

### 2.4 最小变更集合及终态/RNG原则

新reader从361派生，替换schema import及完整来源控制/闭门实现；保projection17/5 ABI、12物理文件、write-once/fsync/readback。补before-content-read ordinary+nlink1/canonical physical gate（旧361 _read_pinned仅is_file/size不足），release/bundle/proof也同门。拒symlink/hardlink/special、重复JSON键、BOOL冒充INT、mixedversion和wrong source。

新candidate从356封存15源派生，明确新profile的input/runtime/result/comparator共同调用同一代码绑定contract；修改genuine profile/version/observer_label及涉及UI/RNG provenance的身份检查、engine integration识别与runtime门。旧355 profile继续CLOSED，旧正式75及旧patch逻辑不扩大。不要全局string replace把历史来源改新；检查所有消费者literal。新的terminal_profile可继续使用source-two-physics-idle-pre-internal/1作为既有算法ABI，由联合contract明确映射391policy first-actual-idle-after-at-least-two-future-physics/1；禁止把原ABI解释成恰2。若另改terminal literal必须新有限版本，不改所有旧profile。

TimerRuntime/FrameDriver/King effect/prepare/death/finish/RNG业务核预期字节不变。唯一可能需单独审的运行器边界：356 CombatEngine.run每pass前按elapsed>=120超时，包括已ending尾段；若有限新genuine要求战斗在120内结束后仍完成合法尾段，则在新profile分支仅将战斗预算门约束到not ended，另以MAX_PASSES/完整clock与独立wall限界尾段。该行为必须先新SOURCE审及边界控件；不能凭401 host142秒推断模型elapsed或自行加预算，不能改纯349headless/其它profile。

C由模型HP/death/request_end自然给出，cleanup在当pass postordinary，strict futurephysics两次门饱和至0后等首idle；允许中间idle0/1，final idle不执行internal、ordinary/Util_idle。保每实际pass delta和order，返回末idle completedFalse；实际N用模型post_cleanup/pass_trace/完整clock在输出侧计算，不能将remaining0解释为N2。checkpoint-ordinal0的SOURCE可记录情况不自动扩展模型activate内death支持；FrameDriver.request_end只接受dispatch阶段，activation death必须明确unsupported阻断。

新输出checker需替换旧compare_callback_schedule的物理frame重建/排序/cleanup-enter即停止的有限逻辑，以真实model runtime_trace/source_callback与native物理序列做类型严格对齐，覆盖idle、King/invu/AutoHide timeout、API argc及actual BOOL/NIL return、reentry/once/order和tail；无证据不宣称全107site语义已比较。逐site覆盖表区分输入来源、行为比较、纯身份/provenance，任何未覆盖业务site阻断完整结论。

旧compare_capture只做通用事件/history/final且不调用compare_king_fx_snapshots/compare_king_observations；不能仅加入profile白名单就报King PASS。391 source_runtime_snapshot增加characters_invu/king_source_state/cleanup_clock/partition，旧project_king_fx exact keys会拒绝；新增closed outer-wrapper adapter先验证四额外组并逐组与模型比较，再仅把原base字段交旧public-FX projector。模型public/full_fx/king/invu_origins/invu_bubbles/characters的取值路径逐字段登记；不得为了通过而strip新增组。

## 3. Realize / 拟实施的逐函数计划（本轮不实施）

1. 拟新增verify_admission_source(source_root, contract_descriptor, execution_release_descriptor=None)：先canonical+regular+nlink1后hash再JSON；固定允许的profile/version/391tuple/native_patch/schema/sink/collector/fixedfixture身份，核新reader/candidate/checker freeze和真实Root/独立SOURCE回执。外部执行release另核402/Root实际捕获及12pins/权限。返回工程proof，不写Engine字段。不使用caller checker callback、verified bool、旧307/旧359接受作为新准入。新contract的hash图先固定payload，再manifest/freezes，再owner/review，再执行release，无自哈希环。
2. 派生reader._verify_source_controls/_require_future_capture_closure/read_and_validate_sources：pending gate仅在新SOURCE换为上述联合检查；保旧361原件。先校SOURCE/真实input-only release（models/expected/new_native严格0），只读声明12完整原件；逐个sizeSHA前后readback，任何多键/缺行/错序/alias失败封首错；返回原immutable bytes+source proof，不造runtime。
3. reader._validate_sources：用精确391 module同一个validate_sources_with_binding(raw11,binding_bytes,BINDING_SOURCE_CONTRACT)，重新decode/重join并核alias。schema的producer_independent_acceptance=PENDING、shared_consumption_closedFalse等历史proof字段不篡改；外层真实source/capture authority独立补足。未通过整套schema，绝不仅凭binding通过投影。
4. 拟新增validate_fresh_initial_coverage(decoded, aliases, constructor_contract)：逐项核2.3初始表。尤其Character四字段、King prepare/default、crown/light source-chain及全部Timer fresh lineage，输出每字段SOURCE/actual checkpoint证据和缺失表。缺源返回错误，不返回“默认补全”；无expected参数。
5. 派生project_fixture_and_runtime/source_bytes,aliases：保持原实际顺序、Buff symbol转换、constructor-only initialitems、完整frame_clock和validation-only UI，追加调用fresh coverage门；返回fixture/runtime/proof。project_primitives仍物理顺序逐行转换，不排序/补抽样；未知primitive/context拒绝。
6. seal_once(bundle,proof,before,output_dir,source_root)：保5/17键，写新目录和原3文件+jointseal+receipt；scope为engineer-sealed INPUT_ONLY_NOT_MODEL_RELEASE。新独立input reviewer重新从允许12及SOURCE链做字段映射/typed bits/sequence审查，不调用candidate以“验证输入”。输出真实输入接受owner；此后bundle固定不编辑。
7. genuine.require_single_king_admission与validate_profile/validate_result_profile、engine.validate_runtime_inputs：在新profile统一核代码绑定身份，mode/fixture17-key/terminal及fresh域精确限制；在RNG/Engine构造前完成。工程runner还需核实际source bytes、401/402和jointseal执行release。身份检查不把proof装入runtime；不改变五key入口去接EXPECTED。observed.run_input_bundle仍validate→Tape→Engine→run→assert_consumed。
8. 新有界genuine execution wrapper（拟新增，不复用351 seed worker）：独立SOURCE loader闭包，audit只允许bundle+精确15source/stdlib与自身输出，不给capture目录/expected权限。模型调用一次；保result、input hash、同实例初终public/private/timers/trace、模型源码before/after、wall/exit/异常；不得手finish/强制清理或用expected替换snapshot。如仅raw result不含某所需状态，先另封只读同实例诊断getter，绝不先跑后补采样。无自动retry。
9. 拟新增validate_comparison_controls、project_terminal_envelope、project_single_king_callbacks、compare_single_king_result：独立checker先验所有pins，才读已授权EXPECTED。先schema.validate_observation_records；terminal controls用391真实validate_terminal_receipt/diagnostics，同一391schema对象。核模型cleanup phase/counters、后续实际pass到firsteligible并比较control的C/anchor/N，而不是用control筛选model流。输出typed事件、parent refs/history/final、Tape完整消费、API/scheduler、postcleanup/final FX及额外King/Character字段分组差异；每组complete才能总PASS。
10. compare.project_king_fx/compare_king_fx_snapshots可复用其base公共字段比较及模型private诊断规则，但wrapper额外组不可丢。compare_king_observations要求七组events/event_references/histories/final/random_inputs/api/scheduler全部传真实独立投影。callbacks映射必须在预封spec逐source site定义含ignored reason；旧通用compare_capture路径保持旧profile隔离。
11. 新静态SOURCE交付：逐函数AST/字节逆推，15源守恒例外表、全import闭包、VERSION/PROFILE/schema/UI/RNG/export/fixture/status消费者清单；无未来review hash。设计通过后才能实施，实施独立SOURCE通过后才原始12读取/输入构建；各gate仍可单独拒绝。

### 已知缺项/不能假定的证据

A. 402最终receipt/owner及Root输入release本设计未获取，故不提供预期未来hash。
B. 12文件在attempt06实际source bytes、Character初态/crown/light/Timer完整fresh链、primitives完整消费，在403未读未验；源码可表达不等capture具备。任何缺初态必须阻断并报告具体缺项。
C. native private Timer值按producer明确NOT_EXPOSED；只有合法fresh构造链+模型private演化及public一致性的有限证明，不能实现native private直接逐值相等。
D. Util RNG checkpoint不证明完整随机流同seed闭合；此路径只条件Tape重放，若另要同seed重现须另立RNG consumption/source边界设计。
E. 旧比较器没有391全字段/全callback闭包；新字段或107site任一没有真实model观察/明确语义映射，必须报告comparison incomplete，不许静默忽略。
F. activation期death不属于当前FrameDriver有效request_end域；391能关联anchor0不授模型新域。模型超时尾段预算问题需SOURCE有限审，不从142秒host耗时猜测。

## 4. Acceptance Criteria / 有限验收步骤

403作者验收仅文档与实际SOURCE pins/API AST记录，所有操作计数0；此文不是开门或SOURCE实现。独立设计review先核字段划分、F01 before-read与closure、三个356入口及comparator联合身份、尾段算法守恒和缺源处理；Root确认后才进入下一实现。

后续SOURCE独立验收建议预封以下20个logical obligations，每项一个合法基例加所列有限单字段变体；测试作者再给确切API调用上限，不在403偷跑：
1. 新profile四边界同一tuple正控；旧307/355/359或wrong391schema/patch各拒绝（预固定4替换）。
2. caller_ready/回调validator/额外proofkey无法开门；旧356/361原封CLOSED。
3. 旧正式75两代表输入/结果合同守恒，仅SOURCE谓词，不重跑旧战斗。
4. 12集合缺/多各1、原哈希改1、duplicateJSONkey1、BOOL代INT1拒绝。
5. 物理read gate symlink/hardlink/special各1均在内容读之前拒绝。
6. slot O缺口保持、native重复1/owner错配1/earlyNULL角色污染1拒绝。
7. Character四fresh字段逐个错误共4拒绝；缺checkpoint拒绝，不能从EXPECTED填充。
8. King charges0→prepare3、REAL3/4/6类型与crown/light合法链；缺链或错误typed值各1拒绝。
9. Timer starts0/birth/current/owner连续；public0但no-start链缺失1拒绝，private输入污染1拒绝。
10. UI raw17-key仅validation，禁止unsupported entry1；endpoint/cleanup/runtime proof额外字段1拒绝。
11. Tape三合法kind的bits/args/label边界；错序、漏draw、余draw、global_u32各1拒绝，全部不按seed替换。
12. 同一个新SOURCE小型外生clock fixture覆盖N2与N8，夹idle0/1，finalidle无dispatch；是新接口回归，不重跑旧350/351接受集。
13. earlier eligible被跳、EOF不足、trailing、counter错序各1拒绝；不得把原N8写2。
14. 先由规则触发cleanup；更改EXPECTED C不影响执行结果，只使输出比较拒绝；若模型未death，EOF必须失败。
15. activationdeath明确unsupported；原checkpoint0 source proof不能开这个模型域。
16. 仅如实施预算例外：未end达到120拒绝；已end合法尾段完成；独立clock/pass/wall上限仍约束，三固定边界。
17. codec保存typed字典键、BOOL/INT、REALbits、物理数组序，jointseal写一次；已存在目标拒绝。
18. checker新增四outer组均消费；分别污染characters_invu、king_source_state、cleanup_clock、partition各1必须拒绝，private非观测标签保留。
19. King/invu/AutoHide API与callback先后、argc/NIL/BOOL实际return各1坏变体拒绝；不能排序或cleanup前截断掩盖。
20. input worker审计拒EXPECTED读取；模型sealed后checker可读其声明EXPECTED；source drift与firstfailure保存，禁止自动重跑。

有限合成只是SOURCE及映射逻辑验收，不能替代实际12。之后另独立一次真实input-only build与字段来源验收；若失败，保留并停止，不执行模型。输入接受后Root才授权一次genuine模型；结果先封再独立比较，首次真实差异精确报字段/事件/位，禁止修输入去追输出。模型PASS也仅限固定A conditional replay与实际观察覆盖，不自动King准入或全引擎声明。
