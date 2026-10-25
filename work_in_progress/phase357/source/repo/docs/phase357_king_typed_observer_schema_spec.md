# 357 单King完整typed observer schema SOURCE

## 1. Requirements

实现独立stdlib模块 `tests/phase357_king_observer_schema.py`，提供VERSION=`7-king-single-A-355`、PROFILE=`observer7-355-native-single-king-A/1`及355接口需要的schema API。本轮不创建Godot producer/patch/collector/host、不提取输入、不运行模型；356共享HOST门无条件关闭，正式75及349/355/356源码不改。只文本/AST/compile/SOURCE生成，不import候选或生成模块，不调用其validator/Engine/RNG，不读capture/expected。

校验器必须实现所列record及11载体的完整schema，不能让caller传假validator或ready boolean补齐。SOURCE默认、实际carrier、expected输出严格区分；没有nativeID、clock、观测值便明确缺输入。首域固定351A：39实例、单P:12 King、双方class0、六ID；native35301/35302只是未来配置，checkpoint不驱动生产seed/state。Buff.current/permanent和Character.buffProtectStacks都是INT；King protectedBuffs/manaCost是REAL，原useMana INT签名的入口值与上游REAL调用实参分别记录。

## 2. Design

纯schema从已钉040 base validator、095/307 typed协议、111/154 King/fresh/UI/RNG、356纯SOURCE helper及原FrameDriver解码器以文本/AST提取生成；不import旧profile，不执行它们的变换器，不复制Game。生成模块内置必要常量/field/site表与纯函数，无外部runtime文件读取。所有原来源pin/抽取函数SHA及必要GD函数signature/行/函数SHA在SOURCE矩阵封定。

record envelope仍observer7-record/1。输入只四physicalchannel(input/lineage/metadata/primitive)，先验证filename↔channel、每文件strictINT非BOOL递增、四文件全局unique sequence，再做完整typed schema及跨载体join。runtime/allocation/registration是expected侧，可由同模块校验其完整record形状，但不能从11输入读取接口打开。clock/UI保各自序和frame计数，不冒充共享四channel序。

闭集site表保留K1所需的原Core/Buff/Character/Game/CombatLog、CombatTimer、EventBus、Util、Item/Descriptor/Weapon/Potion/HealthPotion及Book metadata基础site，新增King五方法、Character invu/cleanse/protection、CombatLog invu事件、AutoHide六方法与Util idle/changeTimer。其它75物品方法不在本模块声称范围，未知site拒。schema state表只需要item/potion/goobert/king、generic、各core、node/timer/AutoHide/temporary；descriptor只准固定六ID。未注册constructor引用可为role=NULL，已注册非空Item/Character角色必须属于固定A；实际owner别名、scene/ready/pre/act、粒子/Timer owner与clock/UI窗口由完整11载体SOURCE join检查，不能只验证一个native_id字符串就称来源闭合。

完整typed递归沿原ABI：NULL、BOOL、canonical INT decimal、有限REAL BE64 bits、STRING、ARRAY、保序DICTIONARY（typed键不先解成Python键）、native_ref/event_ref、temporary、damage_source/result。未知字段/类型、typed键重复、depth/size越界均拒；四色cache key精确INT0/2/4/7，内容数组/native-ref/BOOLtrue结构和遇见序保留，不能BOOLfalse/REAL0冒充Primary。normal record args必须精确符合真实GD参数名；显式GD int/float/bool入口类型检查，特定King/invu/Mana/Heal/Timer callsite再核准确Variant类型，未注解Variant只接受完整typed ABI而不捏造窄类型。

## 3. Realize

1. SOURCE生成器读取原307 sink的field/site常量、040 CONTRACT/MATRIX和095 additions，仅按选定SOURCE roster补新site。原GD `func`多行signature、实际参数/显式类型、return、Timer.start/stop语句逐函数提取，生成精确MATRIX；不运行原GD或Pythonprofile。新增schema的hook声明必须有真实SOURCE函数及pin。
2. 模块基本API `strict_json_loads/exact/integer/decimal/text/validate_typed/validate_state/primitive_context/validate_primitive/validate_record` 实际完整实现；schema属性指向该模块的已实现API集，不接caller提供schema。base record检查按新闭集MATRIX/state常量运行。King item262强制完整king字段；Character补INT保护、origin/bubble/invuTimer；AutoHide嵌套完整Timer；generic ready严格只有native_id。
3. primitive保randf/randf_range/randi_range的原site/args/bit型和physical顺序。invulnerability_pitch:P:12只randf_range、REAL0.9/1.1，来自Character.makeInvulnerable→Util.randPitch。保原global_u32 fixed6swap ABI校验代码/规则；K1无Mirror时输入应0，不发明新随机channel，也不从checkpoint恢复生产RNG。
4. records：enter/return_explicit/return_implicit、已声明mid、Timer before/after、scene_instance、prepare/activate checkpoint、loaded_descriptors、allocation_complete均完整校验。新增source_resources仍只SOURCE证明，精确两侧panel、INT buffProtectStacks/debuffReflectStacks及完整11Buff typed ledger；future producer必须按该schema实际输出，不能默认填空。Timer API只接受该SOURCE语句确有的op/argc/role和完整before/after形状；未知owner/role及身份冲突拒绝。
5. `decode_sources(raw_by_name)`精确11名字/bytes/caps/UTF8/duplicate/nonfinite/framing，内部直接用本模块validate_record，不接受外部schema。`validate_source_carriers(raw_by_name)`进一步核固定双fixture、所有四channel、完整clock header/pass、fresh facts、UI open/bind/ready/roles/stack/close与RNG source-cut join；复用文本抽取的纯SOURCE函数和原decode_clock，无候选import、无模型bundle输出。构造出的只是不含模拟初态的来源proof/identity映射；没有build/main/host调用。
6. `validate_observation_records(records, source_identity)`用于未来expected侧，校验完整typed记录和selected Timer/native owner关联及before/after/entry堆栈，不用其内容补11输入。有限record流与clock的EOF/trailing/缺尾检查在各自公开完整序列接口完成；规则推导死亡/twofuturephysics/首idlepreinternal终结仍由既有FrameDriver，schema不能用endpoint当停止指令。
7. 新SOURCE helper来源、字段/参数型矩阵、record→未来hook清单、11载体cap/header/close与expected分界、完整性/缺项元数据与owner一并冻结。旧355文档关于buffProtectStacks可能REAL的说法在此更正为原typed property INT，不改已冻355或内核。

固定A还有必须保留的真实身份边界：只删O:12后，仍有O:13..O:19；schema必须拒O:12并允许准确O:19。future collector不能沿旧register_inventory的连续enumerate，必须从事前fixture的slot→instance_id表，以实际descriptor、几何、库存来源链绑定native对象；不能改盘/重编号或从expected回推。该SOURCE producer传递机制留后门。本schema的raw schema/主体角色检查与跨载体身份join分层；stateless row验证不冒充已有native身份来源证明。

`decode_sources`负责11文件字节/framing及四channel完整row类型；`validate_source_carriers`是完整UI/facts/RNG/clock/source关联入口。两者均不生成runtime/bundle。typed cache在本块只核真实颜色、容器、唯一已知refs/BOOLtrue和实际遇见序；未来sealer仍须独立闭合固定A SOURCE几何成员/prepare缓存连续性及投影剥离，不把schema的结构通过写成这些业务证明已通过。future producer必须SOURCE声明selected观察窗口/角色关联；未注册native:<id> Timer API只在完整expected接口与已验证SOURCE Timer身份表匹配时接受，未知owner不能以裸ID文本通过。

## 4. Acceptance Criteria / Tests

仅compile/AST/来源pin检查，记录实际未执行的语义控件。生成模块不含候选/外部profile/文件/网络/进程import或操作；SOURCE helper原算法差分明确，typed/schema字段与实际GD signature对应。作者不运行fixture/record验证，不自签独立FINAL；独立方下一门可纯schema合成正负控，合成carrier不称原版实际证据。

原版producer/完整新patch身份、实际11carrier、input sealer的proof剥离/固定runtime投影、模型/expected门及host都仍未实现/未放行。356 gate及validate_patch接受域完全保持，King_production_admitted=false。未来开门须profile↔新observer/schema/patch真正联合绑定，不能翻bool。全局引擎/RL继续IN_PROGRESS。
