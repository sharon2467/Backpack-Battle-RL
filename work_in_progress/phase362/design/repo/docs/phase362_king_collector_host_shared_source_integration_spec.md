# 362 固定单P King：collector / host / shared SOURCE 最小集成

## 1. Requirements

只设计下一组必要源码，不实现/执行，不改359/360/361/356或正式75，不读取capture/expected，不Godot/模型/采集/输入build/复制Game/pool写入。首例固定351A（b62bb554）、两侧class0、39项、六ID、全局仅P:12 King，无gems、无O:12，O:13..19保持。native global35301/util35302事前固定，不等于production32103，也不按结果换盘/seed。run/case/attempt由root在实施前确定新路径；首个启动失败也保留，不能称未失败的“第一次”。

真实现状：359 24/24 producer SOURCE接受；360 56/56 schema/合成关联接受；361 32/32下层unit/工程codec接受。它们不等于完整 `project_fixture_and_runtime` / `project_primitives` 正向接受，更没有actual12。356门仍无条件closed；后续必须留下真实12原件产生后的**首次完整投影门**，不能凭下层控件跳过。

复用出处：`phase338_native026_host.py` 的source_gate/plan/proof-before-execute、`phase187_berserker_native_host.py` 的reset_previous/prepare、`native_capture_pool_v6.py` 的lease/check_ready、runner_v6执行预算、storage预算、run_compaction小overlay；collector仅窄派生 `phase298_native_collector.gd` 的固定双fixture安放/阶段/序列化骨架。旧case/白名单/73path/连续enumerate/deferred终结不能直接继承为新King正确性。

## 2. Design

### 一条集成链及明确缺项

固定A三配置与slot SOURCE → 独立SOURCE通过的collector/patch/参数化host → root精确配置和只读plan → 单READY pool lease/preimage/小patch/check-only → proof封存后唯一native → 同idle切面一次冻结/原件归档 → 两方独立12输入/首次完整投影 → 两方各一次模型jointseal → root expected门/独立完整比较。

当前只设计箭头的缺失连接。collector/安装器、共享来源新candidate、参数化host、新无整Game副本归档及其独立门仍缺，任何缺pin/字段/来源继续failclosed。不添加“source_ready=true”捷径；正常headless不载入oracle SOURCE链。

### 单pool与只改必要小文件

host显式接收 `source_root, task_root, baseline, pool, runs_root`。任务根须与实际baseline资源映射相符，所有根为已存在的无symlink真实目录，pool/run/baseline互不相交；run必须新路径。计划只读检查当前 `pool/state.json` 指向的真实前run、compaction bundle/driver/retained证据、project/data全树SHA+mode+mtime及无活跃进程，不猜当前一定READY或一定还是026。

获lease后才允许改pool。先把前次run/preimage证据与失败目录身份封到新run；`reset_previous` 全部before/after/marker先核再恢复上次观察path。此次安装按359实际75path和真实diff，而非旧73；新collector是独立driver，project.godot必须包括明确autoloader/collector入口的实际after pin。每个目标regular、无symlink/hardlink且SHA等预声明before；已有文件原字节/mode/mtime保存，小新增文件注明before=NULL。before/after/inverse全核后装；不替换战斗算法、资源参数或生产RNG，不复制整Game。

如果物理pool缺失/failed/来源无法定位，停止执行并列明确缺失材料，由root另恢复门处理，不自动pool-new/copytree修复。失败原run/partial/log/source现场一直保留；只有root明确审过的恢复操作能复用failed pool。不能为重试覆盖旧run，不能自动改seed或增加第二次battle。

### collector实际调用时序

1. **startup**：继承原离线Game/双fixture流程，但严格六ID/class0/A资源/几何/库存；仅当NativeObserver已_ready、UI窗口已open，且确认其SceneTree clock信号已连接，注册collector只读完成回调。全局/Util seeds按旧真实初始化路径各一次设置，setup期间的RNG不倒推到生产；原checkpoint仅proof。
2. **selected出生前**：对所有受控新P物品和未来O实例构造之前，调用 `begin_fixture_window(slot_table)`。slot_table来自事前已钉359固定表，作为明确SOURCE实参；可读取sink的冻结常量并与host归档JSON/固定fixture交叉核，不需新增可随意改的用户状态文件。旧starter退出/存储与新ItemBook实例化的实际证据保留，不把旧对象冒充fresh。
3. **放置/settled**：复用合法安放动作本身（明确属于fixture setup），逐真实descriptor/几何/库存验证39项。角色用事前slot→instanceID，不能enumerate压缩O洞。删除旧 `player_spatial_evidence()` 为观察调用 `getAffectedItems_nocache/getAffectedItems` 的做法；成员几何从已封shape/star与实际occupiedCells/descriptor.canActivate直接只读验证，prepared cache只读已有字段，不刷新。所有安放完成且before-prepare时调用 `bind_fixed_inventory(slot_table)`；它生成actual native alias proof，失败即终止，caller bool不替代。
4. **prepare/activate**：由原Game路径真实调用，不由collector手工重做effects。359在prepare入口捕获来源/资源，activate入口开始真实clock/fresh facts。保原绑定后typed参数/原primitive顺序；UI foreign分类完整，不强制idle60、不补private Timer值。genericready仅owner。
5. **cleanup**：Game原combatEndDeferred完整body leave后，359记真实post-cleanup切面；collector combat_end回调只保存primitive结果/阶段，不沿旧 `call_deferred(finish_capture)`，不合成InvulnerableEnd或清flag/origin/crown/charge。
6. **同一first-idle-preinternal闭口**：359 clock callback记录cleanup之后恰2个future physics，并在首eligible idle信号中同步封clock/UI/final-source，然后置completion。collector完成回调必须在同一SceneTree idle signal、sink回调之后且Node internal之前运行。启动前及实际窗口核 `get_signal_connection_list` 的真实目标/方法/先后；未知中间会改选定业务/RNG/Timer的callback必须拒绝，不能仅依connect调用时间推测。
7. **只冻结一次**：collector回调确认真实receipt/endpoint/当前frame相符，当场冻结events/parents/alloc/history/full typed终态、Timer/cache/private/资源及King/invu/particle/light数据。不能等下一idle的observe，不能下帧stable_snapshot重采；旧两次快照相等条件不适用于允许hide尾变化的新切面。后续只序列化冻结primitive DTO，记录SOURCE切面和cut；不再次读取活业务对象。完成后flush/状态封口/quit，由host实际记录exit。

collector的SceneTree idle只读callback不是业务信号订阅，不能改变原EventBus/业务信号处理顺序；需新独立SOURCE/连接序证据。359不因本设计改字节，若实际collector接入需要新增producer接口，则另窄SOURCE版本，不静默修改冻结文件。

### 最终snapshot的独立只读闭包

359的sink审查不能自动覆盖collector新增fullsnapshot。新collector应有字段→getter/declaring script→阶段→typedkind清单：

- 直接Item/Character/Buff/CombatLog/StatLogger/CombatEvent/BalancedRandom/DamageSource成员，逐类查继承、setget、_get/自定义property-list；不用动态get_property_list当未知属性通行证。未知属性失败，不填0/NULL。typed字典/数组按实际顺序复制，不为了比较排序。
- `Inventory.getItems()`及必要socket/topLeft链可引用已封只读SOURCE；`Character.getStat`会调用getStaminaRegeneration/getCurrentHealth/getTemporaryMaxHealth/getCurrentStamina/getMaxStamina/isBattleRaging/getCritTokens/getHealingEfficiency/getUnhealing，必须逐调用闭合读路径，不能因名为get就认可。未闭合则阻止collector SOURCE接受，不能删严格stat字段迁就。
- events/parents遍历直接读真实id/parent/params/snapshot，防循环/重ID/深度/尺寸；记录primitive/nativeID，不长期保活event/Temporary对象。history只读取既有logger数组，不调用snapshotItem...或任何业务记录函数补历史。
- 禁止观察调用prepare/reset/cacheAffectedItemsForCombat/getAffectedItems/getP_m、资源gain/use/change、信号emit、随机调用；manifest用getSelectedSkin/getLeague/canUnlock/settings.getVal等旧额外方法也须来源闭合，非必要者以明确新manifest合同移除，不把它们塞进输入。所有Timer/Node/Particles公开getter沿真SOURCE白名单，private−1仍是lemma，不把public0写成direct private观测。

### 12原件/expected分隔与caps

collector只登记12合法原件的raw清单/身份，不在Godot构造Python bundle。capture可保持旧扁平文件布局以兼容sink，但archive manifest必须有互斥 `lawful_inputs` 与 `expected_observations` 分区；input reader只复制前者。两fixture、四source channel、clock header/passes、fresh facts、UI、RNGcheckpoint、slot-binding恰12；runtime/alloc/registration、histories/events/final/cleanup/endpoint和foreign诊断为expected/归档，不能因文件同目录被reader glob读入。

实际359 sink写18种文件名：7 observer channel、failure、clock header/passes、facts、RNGcheckpoint、UI、binding、foreign诊断、cleanup/final/endpoint。加旧collector15种（含两fixture，不能把旧stability含义搬过来）为33种；新cut/分区/cap ledger即使再加3种仍<=36，实施freeze须输出准确集合，host上限64不是运行覆盖。按实际SOURCE caps：typed record2MiB、file/合计256MiB、sequence<300000、native IDs8192、预绑定384rows/2MiB；clock<=200000passes/64MiB、UI<=65536rows/8MiB且record16KiB；clock/facts/binding等单JSON沿record2MiB，RNGcheckpoint schema16KiB。四channel strictINT/physical单调/全局unique，UI/clock独立序，沿355/358/359保留。

359通过total_bytes+king_input_bytes共同限制正常observer文件<=256MiB，failure另预留4KiB。下一collector必须补真实writer字节预算，不能复用旧write_json一次不受限地JSON.print整棵历史。建议：fixture两件合计<=4MiB，collector expected合计<=192MiB且单件<=64MiB，control<=4MiB；连同SOURCE/failure最坏约456MiB，capture硬上限512MiB/64文件。partial按已写入字节计入，触cap留完整已写前缀、firstfailure，停止新增业务/观察写入并退出；不能截断后仍称完整。SOURCE错误文件/失败收据的独立小reserve要预留，不能预算耗尽再无限写错误。

run另计driver/proof小源码<=128MiB、overlay/compaction<=64MiB、stdout+stderr<=32MiB、非capture用户缓存及其它写入需分类/独立上限；建议整attempt预留1.5GiB上界，实际监控/提前中止控件独立证明。不能把后台Godot未知写入当作已被observer256MiB覆盖：未知path/文件增长/超预算须失败，未有硬限制或可证明余量前不授执行。达到cap后保现场、不清旧唯一证据/不重采；如I/O层不能完整保留即明确partial失败。

原runner可能复制user/native-capture到output/capture，预算须按双份计算；更窄方案是在进程确已退出、同FS、源/目标regular且目标不存在时**原目录rename**，保存原位置alias和前后逐叶identity，不复制原件；此差分先SOURCE审，不偷改旧runner。非capture user叶不能直接丢弃或假称全是重复cache。

原storage真实公式为4GiB reserve +256MiB evidence + pool-reuse的一整树estimated_copy_bytes，旧host另加512MiB。2.6GiB已是历史：root验证并仅释放可恢复重复clone/objectstore后实测4.6GiB，原件/基线/pool/checkpoints/失败未动。该读数不是新case预算已PASS，也不是永久全局阻碍。新无copy路径仍应采用独立审核的保守reserve+本attempt最坏写量公式，不能为了启动直接调低4GiB。上述1.5GiB只是待审核总上界提议；若采用4GiB外加该上界，4.6GiB仍不足，需root在真正plan前解决或以已证明的更窄写量合同重新封定。作者不清理原件。只读plan给当时实际free/各上界/安全余量，任何不足0启动。

### 无第二Game copy的归档/恢复证明

旧 `archive_and_verify` 289–302会创建scratch/project并整树重建，不能原样继承后声称Gamecopies0。新窄分支只写小overlay ZIP和metadata：全成员CRC/SHA、safe/unique path、mode/mtime，stream核baseline+overlay覆盖关系，并与现有pool project每叶实际SHA/mode/mtime相等；不落地第二Game。retain整个run/evidence、前后baseline/project/staged tree inventory、无active process和源码未变证据。

新proof必须叫 `logical-overlay-and-live-tree-equality`，不能伪填旧physical roundtrip已执行。新READY verifier只认两种准确schema：旧真实materialized proof沿原门；新流式proof沿新门。旧证据不修改，未知mode拒绝。独立源码/有限overlay控件通过后，root才能采用此新READY转换；完整物理恢复仍由既有GitHub恢复证据和必要后续独立门表达，不冒称本run新做了它。

## 3. Realize

### 最少新增/窄改面（以下为待实施名称，不是已有组件pin）

1. **新King collector GD**：由phase298骨架派生，改 `player_input_valid/register_inventory/place_player_items/player_spatial_evidence/observer7_precondition` 的六ID固定A/slot SOURCE/fresh关联；增加 `attach_completion_listener`、`on_idle_source_cut`、`freeze_terminal_expected_once`；替换on_combat_end/finish_capture的deferred重采；补King/invu/ledger/Timer/particle fullsnapshot和有界writer。不改Game效果。
2. **小apply/安装器**：从359 final patch/source locations取真实75 after与original preimage；增加collector入口/project设置的精确报告，算真实path数/新增文件集合、逆向字节还原。所有已存在SOURCE byte不改，安装仅pool的已声明小文件。SOURCE与GD签名检查先封，实际Godot parse由root另门。
3. **参数化host**：窄派生338/187；`validate_root_receipts/source_gate/plan/prepare/save_proofs/execute` 用显式paths、固定A三文件/35301/35302/120295300；无默认旧/workspace。只支持existing READY、唯一attempt、固定来源tuple；先归档精确SOURCE/metadata/proofs再执行，driver只收入必要小工具及已读接受收据/owner和实际使用源码，科学大raw留repo/checkpoint按精确pin引用，不盲目复制所有owner历史raw。
4. **无copy archive小分支**：在新SOURCE文件实现stream overlay/live-tree verifier及新READY proof；旧pool/storage/compaction不原位改。明确旧helpers哪些函数纯参数可复用、哪些内部TASK/POOL/BASE/RUNS全局需新小适配，不能在已冻结module中偷偷改global去假装可迁移。配合capture rename/日志cap和逐叶清单。
5. **共享来源接口**：沿root偏好的普通准确tuple，不做签名服务/可变全局ready。内层纯API比较同一 `profile, case, fixture_identity, actual_patch_report_identity, actual_patch_diff_identity, native_source_identity, schema_identity`，在input/result/runtime/compare一致调用；actual patch身份必须由实际字节计算，不能分别认可新profile和旧307patch。

### 无循环身份顺序

先稳定producer/schema/collector/projection的SOURCE与patch字节，形成小 `native-origin` 来源表（不含未来candidate或host自身hash）；candidate新genuine代码只钉这组固定来源/fixture/patch关联。candidate15 freeze随后计算。host再钉前述来源和candidate freeze；host freeze再计算。最后root配置钉collector/projection/候选/host的实际代码SHA和独立接受receipt、run/config/paths、所有owner实际读回。root配置不嵌进其所钉源码，不让source manifest包含自己的hash，无环。

外层root执行描述符将完整身份集合串在一起，内层只比较会产生355旧反例的同一来源tuple。projection不编译自身manifest SHA，按root真实descriptor核自己及依赖；普通headless仍直接走生产schema/双RNG，没有oracle文件链。新King genuine验证可用单battle显式校验context（在17-key runtime业务data之外）传同一来源，不设module全局bool；所需最小genuine/observed/runtime validator/compare接口差分须另SOURCE列明并独立审，当前不修改356/361。

### gate与唯一运行

顺序是新collector/安装器/共享来源候选/host/无copy archive SOURCE冻结→独立差分/有界合成控件→root真实接受配置→readonly plan→获lease、全部preimage核准→安装→**parse-only**→再次整树/配置身份核对→proof-before-oracle→唯一原版A。Godot parse只能使用已核实际binary和`check-only`机制，不运行collector_initialize/战斗/RNG；若不能证明parse-only就不执行。单个检查覆盖所有新GD与依赖签名，保存stdout/stderr；parse错保现场、禁止顺势启动native。

battle wall120、collector total295、runner total300（含其startup/finalization/exit grace解释）固定，simulation保持真实1x；clock最多200000实际pass不能由历史平均估算成无限idle。process exit_code、timed_out、capture_complete、process_clean_exit、source_changes和archive proof分别记录；exit0不等clean，complete也不等模型接受。任何首次失败停止，root才可另定义attempt，不能在execute循环自动重试。

GitHub恢复后的定位：从显式source_root的恢复MANIFEST/入口取得已恢复逻辑workspace根，再由调用者明确提供baseline、Godot runtime/task、pool和runs；相对SOURCE引用一律source_root解析。历史absolute provenance仅作为历史身份，路径迁移用可审计prefix→新root映射，不把历史绝对路径作为运行依赖。资源/旧READY材料不存在时列exact logical path/identity阻挡，不能联网补包、借旧workspace cache或暗中复制整Game；不重做Linux依赖调查。

公开备份已经批准的两API文本脱敏、两加密companion省略及runtime安全相对links，应按恢复manifest的精确身份/差异记录核验，不能谎称整个公开baseline与旧私有树byte-identical。战斗相关75原GD preimage仍须精确；旧READY若引用旧整树身份或旧绝对路径，应由root另封实际恢复来源/允许差异映射和新物理pool证明，不能只改JSON里路径或无条件放行旧hash。当前本地现有pool不因此被改动，本轮也不测试恢复后的原版运行。

## 4. Acceptance Criteria / Tests

下一实现门只验必要增量：fixedA/39slot及O洞/真实descriptor+geometry+inventory join；before-window/已pooled/缺ready/未知对象负控；snapshot每个调用只读且完整字段不省；SceneTree实际连接序和同idle sink后/preinternal的一次冻结；原raw不回写、cap失败保partial/停止写入；无copy overlay CRC/SHA/mode/mtime/unsafe path/重复/member缺失与旧READY模式隔离。

共享门必须回归新profile+旧307patch拒绝、错schema/fixture/collector/projection/candidate/host身份拒绝、caller verified flag拒绝；SOURCE review/代码SHA/配置在prepare至execute间变化拒绝。Godot parse成功不当作battle positive；所有missing组件继续closed。

真实native后，两角色各自只读12原件并第一次完整project_fixture_and_runtime/project_primitives；现361下层32/32不能替代该门。若源checker/适配器失败，保原12原件output-only窄修，不重采/补输入；业务问题走新candidate门。完整输入typed相同后才各一次模型，联合seal之后才root expected release，独立全层FINAL才评估有限King准入。HIT/NOT_HIT按真实自然条件列；active-invu终战等未实发引用350有限组件，不改盘追命中。

本轮完成仅本SPEC；代码、pool/源安装、parse、native、capture/expected读取、schema API、inputbuild、模型均0。整体引擎/RL仍IN_PROGRESS。
