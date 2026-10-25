# 360 窄SOURCE实施 addendum：三site与辅助关联

## 1. Requirements

冻结的设计 `phase360-schema-auxiliary-binding-spec.md` 13312B/fe78aeb3 不改。本次只派生358 schema，在全部真实delegate使用的同一MATRIX补Goobert.prepare/onItemActivated/doCooldownEffect，并实现 `validate_binding_carrier`、`join_binding_provenance`、`validate_sources_with_binding`；其他新函数仅为这三者的局部类型/关联检查。没有projection、sealer、runtime/admission、collector或host实现。

358/359/356/349、正式75和所有原件不可变。359审查pending；本模块引用其实际SOURCE pin仅识别来源，不宣称接受或可采集。不import新旧schema，不调用schema API，不造实际输入或native正例；只允许文本/AST生成、compile和身份读回。新输出在tests/phase360*、data/phase360-schema-auxiliary-binding-source，源码owner与原设计分开。

## 2. Design

新模块从358原字节派生：只替换MATRIX赋值，追加局部辅助接口；原全部函数AST保持。MATRIX三新增行含准确参数、runtime/goobert、无显式return；底层 `_base_validate_record`、外层 `validate_record`、expected记录及配对均读取同一MATRIX，不能只补外表。262继续完整King子型；所有原43clone/型门/clock/UI/stream/typedABI不变。

辅助接口接收359实际closed六key格式，不把第12文件塞进11文件名或已有payload。固定slot表及SOURCE引用在生成期从已钉原件按AST/JSON读出并嵌入；caller fixed_plan/source_contract必须严格同型同值，不接受verified bool或替代来源。合同仅写SOURCE来源，不含接受状态/未来pin；join输出永久标来源schema proof、无bundle、无准入。

local parser校验raw bytes<=2MiB、UTF8/重复JSON键/EOF/终止换行、39项、strictINT非BOOL、typed REAL bits、原f0 shape几何、两种顺序、native item唯一、同侧inventory/character、descriptor共享的一致index映射。保原actual数组顺序，不sort actual refs。固定A仍P20/O19；O input_slot12→O:13，O:12禁止。

join不是11载体完整校验的替代品。它自行重复四物理channel/strictINT递增/全局seq唯一及每row typed schema，验证metadata/scene/ready/pre/act的本关联条件，返回只读语义的独立alias context；完整组合入口先运行继承的11 full-source validator，再join。外部字典可被调用者修改，因此不设计“已校验对象/布尔票据”捷径。没有任何native值来自计划，计划只给角色/descriptor/几何预期。

已有359 proof没有binding stamp和独立inventory node直接样本：本模块不伪造字段，不声称双直接观测；记录这是来源控制流/getter证明而非新的完整native接受。若独立359结论要求新字段，后续必须新SOURCE版本，不能静默补齐。

## 3. Realize

1. `phase360_prepare_binding_schema_source.py`：精确核358 module/freeze、359freeze/owner/slot表及旧15；读取原GD三方法签名，生成三MATRIX entries；原MATRIX其余键和值全守恒。追加固定常量和 `phase360_binding_schema_extension.py` SOURCE。compile生成模块但不import；比较旧函数全部AST及完整module除MATRIX/追加部分的逆AST。生成diff/完整输入pin/字段和API合同/remaining/freeze/owner，所有owner实际叶读回。保留任何首错，工具拒覆盖已有D。
2. `validate_binding_carrier(binding_bytes, fixed_plan)`：固定plan严格等嵌入表；解析准确359六key与每条actual字段。规范ID十进制、typed INT/REAL、occupiedCells精确唯一集合。输出解析后的独立DTO，无已接受标识。descriptorID可多instance共享，同index须同descriptorID、不同index不得同ID；item/inventory/character/descriptor对象不能互冒。
3. `_binding_check_channels(decoded11)`：确认准确11名字/载体类型、四channel各自physical排序/唯一/类型/全局唯一，调用真实 `validate_record`；不排序/改row。它不是fresh/UI/clock完整验证的替代。
4. `join_binding_provenance(decoded11, binding, source_contract)`：SOURCE合同严格等冻结引用，重新做local校验，不信任传入DTO。选择唯一prepare/activate checkpoint、6descriptor metadata；checkpoint80个原SOURCE节点/39items集合完整，inner node role与envelope区分。以actual nativeID连接proof和pre/act descriptor/face/placed/ownerType、Char身份、原scene descriptor/item/class/path和owner-only ready；scene<ready<pre<act，早期role仍NULL。整个role/native双射pre/act连续；返回独立native↔role、input/inventory顺序、raw rows摘要、明确证据边界。不得返回任何资源/cache/RNGstate/terminal值或改写原row。
5. `validate_sources_with_binding(raw11, binding_bytes, source_contract)`：检查总caps含aux；调用继承 `validate_source_carriers(raw11)` 与 `decode_sources(raw11)`（重复只读解析可接受，避免重构原函数），再local/join，保存全部原raw SHA作为来源。仅SOURCE proof；input_bundle_created/model_calls/native_admitted均否/0。实际projection下一门另做。

## 4. Acceptance Criteria / Tests

本轮作者只compile/AST与精确身份/源码读回；不运行新schema语义或构造carrier。独立后门预封有限控件再执行：三site真实delegate正/错参数/缺King字段；完整合法SOURCE合成binding local正控（非原版证据）、descriptor共享正控；O间隙/错slot/几何/typed alias/重复native/跨库存/错metadata/scene/ready/cp/物理seq/缺extra/EOF拒绝；raw行和bytes前后不变。

完整12 actual carrier positive仍不存在。无projection/admission/接受359/模型/native授权；356无条件closed、正式75和旧15守恒。缺少实际观测的字段不能由caller验证布尔或未来placeholder补足。作者SOURCE handoff不等独立FINAL。
