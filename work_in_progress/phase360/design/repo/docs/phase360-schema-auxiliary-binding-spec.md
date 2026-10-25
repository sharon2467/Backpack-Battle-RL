# 360 Goobert 三 site 与 slot-binding 辅助 proof 接口设计

## 1. Requirements

本轮仅设计后续最小 SOURCE 差分，不实现或调用 schema、producer、collector、sealer、host、候选。359 正在独立审查，不能把已生成源码当成通过；若其发现实质缺陷，先按 root 新门修复，再绑定最终身份。358/359/356、正式75及固定A全部原字节保留。356 的 `PENDING_SINGLE_KING_OBSERVER_PATCH_BINDING` 仍无条件关闭。本文件不是 native/input/model 授权。

只处理两个明确缺项：358 表漏掉原307实际观察的 Goobert 三方法；359 为不重编号的固定A产生 `king-slot-bindings.json`，其尚不属于已接受的11输入。目标是使未来消费者实际验证 descriptor、几何、库存、scene/ready/checkpoint 的关联，同时把辅助证据彻底剥离于模型业务输入。不得以 `verified=true`、旧307合法patch、caller提供的validator或计划中的nativeID代替证据。

当前 SOURCE 身份：358 module `tests/phase358_king_observer_schema.py` 259033B / `d8dabd87ffe0352ceb886ad3f25c2548d1e4412d13538da813ba77f8115947a7`；359 freeze `data/phase359-king-producer-source/producer-source-freeze.json` 43099B / `419a79c51f9a5c92c56edc4a2fd0ca7fd829f0471f747652015a39e26035204a`。359 `required-schema-delta.json`、`fixed-slot-map.json`、`record-hook-source-matrix.json`、`remaining-interfaces.json` 为本设计的具体依据，不是实际capture。

## 2. Design

### 载体和消费边界

保留11个准确名字与格式：两个单JSON `fixture.json`、`player_fixture.json`；四个物理JSONL `observer7-{input,lineage,metadata,primitives}.jsonl`；`king-clock-checkpoint.json`、`king-clock-passes.jsonl`、`king-input-facts.json`、`king-ui-authority.jsonl`、`king-rng-checkpoint.json`。已有四channel真实物理顺序/全局唯一sequence、clock真实physics/idle和UI自序规则不改。不能把新辅助文件塞入某个已有closed payload，亦不把UI/clock序号当四channel序号。

第12个文件只称辅助 SOURCE proof：`king-slot-bindings.json`，单个closed JSON、有终止换行、严格JSON EOF/重复key拒绝。计划上限沿359 `write_king_json` 的单记录2MiB，并纳入既有总字节上限；不放宽其余11各自caps。未来12文件的输入提取release/owner/jointseal须全部精确绑定，但 `INPUT_FILES` 的旧11接口不能偷偷变义。新入口显式接收 `(raw11, binding_bytes, source_contract)`。359额外的非selected诊断和cleanup/final/endpoint仍属归档或expected，不因此变成第13个模型输入。

| 数据 | 原SOURCE作者/阶段 | 读取者及用途 | 模型可消费部分 |
|---|---|---|---|
| 事前39项slot表 | 固定351A/355 fixture；359 `SOURCE_SLOT_TABLE` | collector放置；schema比对原slot/实例ID/几何 | 原合法fixture初值，保持原序 |
| 原scene/ready行 | 原instantiate/VM ready；绑定前role可NULL | schema按真实nativeID关联；ready仅owner | 合法fresh拓扑及来源结论；不是ready私有Timer值 |
| actual binding表 | 359实际 `bind_fixed_inventory` 读取descriptor、topLeft、face、occupiedCells、inventory | schema来源join；独立审计别名证明 | 无业务状态；native→role仅隔离adapter的引用翻译上下文 |
| prepare/activate资源、cache/defaults | 实际checkpoint | 验来源/类型/默认与连续性，然后剥离 | 不得成为初值、过程修正或分支驱动 |
| 原primitive返回 | 原调用一次真实返回 | 保ABI、args/bits、物理顺序；本无Mirror域global_u32为0 | 合法primitive Tape；不恢复原checkpoint RNG状态 |
| clock/fresh/UI/RNGcheckpoint | 实际clock、birth/UI、Util/Game来源切面 | 原有strict schema与fresh/时钟/来源证明 | 合法外生clock/fresh拓扑；RNG seed/state和UI/proof字段不入生产状态 |
| 三Goobert runtime site | 实际callee enter/leave | expected观察记录、调用配对与状态/父链比较 | 无；不是11输入中的新RNG/prepare结果 |

### 三个位点

新增准确 `Items/Goobert.gd::prepare()`、`::onItemActivated(event)`、`::doCooldownEffect()`，channel均 `runtime`、声明state kind为 `goobert`。`event` 未显式GD类型，沿完整typed Variant校验，不伪造Node注解或强制NULL；实际调用时保event_ref及其父链。prepare/doCooldownEffect无参数；三者原隐式返回NULL、entry/return配对，未知参数/额外字段拒绝。

K1实际receiver是262时必须继续要求完整King子型state，不能用较小Goobert/plain_item DTO绕过字段。King override与base方法分别记录、按真实嵌套顺序配对；不要求base `Goobert.doCooldownEffect` 必然自然命中，也不能为了命中调用它。三方法本身会写counter/cache/连接/产生效果，因此observer只读已有callee参数和切面，不调用它们补观察。SOURCE声明数103→106只是表完整性，不是运行覆盖率。

### 辅助 proof closed schema

沿359实际输出外层六key：`schema='phase359-source-slot-bindings/1'`、`source_slot_table`、`actual_bindings`、`raw_early_rows_unchanged=true`、`model_input_admitted=false`、`remaining_interface='NOT_IN_358_ELEVEN_CARRIER_SCHEMA'`。后两个状态字面仅识别359当时格式，不是准入bool；不得要求producer改写历史状态来表示未来schema接受。

`source_slot_table` 恰为已钉39项，每项key为原instance_id/item_index/x/y/f加 input_slot/side/cells。`actual_bindings` 恰39项，每项准确key：instance_id、input_slot、native_id、descriptor_id、item_index、top_left、orientation、occupiedCells、inventory_id、character_id、inventory_encounter_index。raw nativeID为规范正十进制字符串；item_index为typed INT；top_left.x/y为typed REAL有限bits并数值精确等原整数坐标；orientation为typed INT；其余slot/index/cell为strict INT非BOOL，范围从固定A推导。实际occupiedCells顺序原样保存，校验唯一成员集与原shape，不强改为catalog顺序。

两个顺序不可混淆：input_slot按原fixture每侧数组位置，O input_slot12对应 **O:13**，最后O input_slot18对应O:19；绝不创建O:12。inventory_encounter_index表达真正 `getItems()` 遇见位置，每侧完整唯一0..n−1。proof数组可按实际库存顺序，不为了和计划相同而排序；逐role用计划表join，另存原遇见顺序。

native item ID全39唯一，inventory ID同侧一致/两侧不同，character ID同侧一致且等pre/act对应character node；这些对象ID不能和item ID混用。descriptor ID允许同一descriptor的多实例共享，不能错误要求39个descriptor ID唯一；必须与对应scene.payload.descriptor_id和item_index一致，且index→descriptor关联一致。每个actual item须在pre/act `item:<role>`节点及items.fields的descriptor/face/placed/owner域匹配；角色集合与固定A恰等，缺重/跨侧/未知均拒绝。

inventory_id目前只在359实际getter证明中直接记录，已有checkpoint没有独立inventory node；不能声称第二次直接观察了它。通过已钉producer的 `item.inventory == character.INVENTORY`、`inventory.getItems()`、唯一几何join算法取得来源，并交独立源码审查；如实际review认为不足，须新producer SOURCE门补明确观测，不能schema捏造字段。binding文件本身也没有独立stamp；绑定先后目前是359方法控制流来源，不冒称直接时间记录。

### 原始行和联合身份

scene/ready原raw bytes、nativeID、stamp、sequence、NULL role永久不改。schema构建独立只读alias表，在校验/expected解释时按nativeID解析选定role，不写回row或重排primitive。每项必须唯一unpooled scene，scene→generic-ready→prepare严格sequence顺序，同nativeID，ready.state只有native_id；scene descriptor/索引与binding相同。pre/act都有同一完整role↔native双射。不能拿NULL当未知对象通行证，不能把foreign行别名成selected。

未来联合身份闭包包括：固定A/slot表、实际新producer/patch report+diff+全部before/after、新schema及辅助proof接口、实际collector、projection/sealer、runtime候选15和host工具的精确SOURCE身份与独立接受receipt。它们分别检查同一tuple，不能只在host验过一次便给其他入口一个ready bool。root future config提供实际descriptor与独立接受状态；当前没有的pin/receipt继续缺失即拒绝。旧307 patch对旧域合法不表示可与新profile组合。

## 3. Realize

后续仅在root另门下派生新schema/sealer/runtime/host版本，函数级最小方案如下；本轮不创建这些实现。

1. **schema生成差分**：在358的所有实际站点验证表/映射一致加入上述3项，不仅改外层MATRIX而让底层delegate仍拒绝。`validate_record` 和expected入口都真实走同一完整类型/子型门；旧43clone及其他site/state/primitive/transport逻辑保持。新函数 `validate_binding_carrier(binding_bytes, fixed_plan)` 只解析closed DTO、caps/类型/39项和局部唯一性，不能返回业务资源。
2. **`join_binding_provenance(decoded11, binding, source_contract)`**：先验证全部11传输/typed schema，不先filter；再执行上述source表、descriptor/geometry/inventory、scene/ready/pre/act join。输出独立 `{native_to_role, role_to_native, input_order, inventory_order, evidence_refs}` proof context。保留全部source raw身份；失败不返回partial可执行bundle。只从实际row/proof推导，不读取runtime/history/final/endpoint。
3. **`validate_sources_with_binding(raw11, binding_bytes, source_contract)`**：明确组合新第12接口与旧11完整校验，交叉比对既有fresh Timer五源、UI、clock、资源ledger、RNG来源。旧11 public API不以缺aux默认为通过新profile；只验11获得的结果仍标旧层SOURCE证明，不代表新profile准入。
4. **`project_lawful_inputs(validated_sources, proof_context)`**：输出白名单为原固定fixture初值、合法fresh构造/拓扑与外生clock、原primitive返回及顺序、必要的精确来源身份元数据。alias仅翻译已有合法引用；不得把currentAffectedItems/cachedAffectedItems、charges/Mana/保护、prepared resources、checkpoint RNG state、UI输入控制或末态/endpoint装进模型运行字段。逐来源字段列到projection矩阵，未知输出key拒绝；模型真实prepare/effect自行产生内生值。输出bundle/proof/before联合seal，辅助原件单独封存。
5. **共享admission设计**：未来新版本 `validate_single_king_admission(profile, fixture, source_contract, actual_patch_identity)` 在 input-profile、result-profile、runtime前置和compare_capture均核同一已封tuple，先于RNG/Engine；比较器必须把正在验证的actual patch/report身份与profile显式同传，不允许两个互不相干的validator分别通过。新报告/差分必须实际计算匹配新identity，旧307/缺collector/schema/错fixture/caller开关均不能进入。旧356源与无条件门原样保留；未来解除需新候选freeze和独立反例回归，不能只翻布尔量。
6. **host与input释放**：host新SOURCE config实际核producer/schema/collector/projection/候选和各独立owner全部叶后才能唯一attempt；运行中只采集。后续INPUT-only release精确绑定12文件、capture归档和两方capsule/owner，权限model/expected/newnative均strictINT0。提取器只读11+aux和SOURCE；expected文件不在reader白名单。模型与expected仍各自root后门，SOURCE存在不等执行授权。

## 4. Acceptance Criteria / Tests

未来独立测试先冻有限新SOURCE合同，复用旧未改门的证据，不重跑成功科学：

- 三site实际 `validate_record` 正控及参数/返回/子型/调用配对负控；262缺King私有字段必须拒。未自然调用的base override路径明确NOT_HIT，不造native正例。
- 辅助proof使用真实四颜色/typed规则及固定A SOURCE合成控制：39精确映射可校验；O:12、丢O:19、compact重编号、错input_slot/descriptor/geometry/side/inventory/native别名/encounter index均拒。正确共享descriptor ID允许；native item ID重复拒。
- 实际scene/ready关联差错、ready伪全Timer、wrong pooled/ID、顺序反转/跨channel重复seq/错physicalfile、缺aux/多aux/extra key/坏EOF/BOOL冒INT/REALbits污染均拒；原raw hashes与物理顺序在校验前后不变。
- 数据流负控验证proof/defaults/资源/RNG checkpoint/terminal证据只能拒绝或作为审计，绝不能修正bundle内生值。固定输入投影不含aux DTO或任何末态/停止字段；改变proof不能静默改变合法模型初值。clock作为合法外生schedule保原有限strict tail，不借endpoint推长度。
- 重现355联合门反例：新profile+旧307合法patch必须在RNG/Engine前拒绝；缺、错或混搭任一SOURCE tuple身份、伪ready bool均拒。只有未来全部真实新SOURCE/独立/root门到齐才设计正向准入；本阶段没有这样的实际正例。

当前完成标准只是一份可审核设计。schema/collector/host实施、Godot解析/运行、实际12载体、输入build、RNG/Engine/模型/native/expected计数全0；不提前接受359，不改正式75或开始King新批。
