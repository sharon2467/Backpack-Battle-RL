# 361 最小兼容projection/sealer SOURCE实施

## 1. Requirements

原四节设计13317B/ec63db9b保持冻结。本次只实现四职责SOURCE：只读12合法源、fixture/runtime投影、原primitive Tape转换、一次联合封存。旧356/正式75/349/359/360十五源及owner不变。保17-key ui_authority validation-only ABI，不拆runtime。所有路径由显式source_root/lawful_dir/output_dir或已导入schema实际路径定位，不依赖旧workspace/baseline。

允许文本/AST生成、compile、原件/owner身份读回；不import新旧schema、不调用投影/封存、不构造carrier/bundle、不模型/Godot/native。actual12仍无正例；reader在实际SOURCE校验后由无参数HOST CODE pending门阻止任何capture读取。未来必须新SOURCE绑定真实collector/host/候选共享闭包才能解除，不提供caller开关、fake pin或接受阳性。

## 2. Design

单小模块依赖精确360 schema，仅其纯schema API，不import候选/Engine/RNG。生成期从356 engine AST取Buff category/symbol和ABI常量；从已钉359/360 root接受回执取真实review/owner/freeze/sourceowner描述符并冻结。它们证明既有SOURCE层接受，不证明本361或未来native准入。

纯projection入口重新校验12原件及alias，不能只信validated布尔/可变对象。fixture取已核原固定A，不连续enumerate O。nodes/processing/root/aux来自实际连续fresh节点，转换数字Buff→SOURCE symbol；Timer只拷配置和合法拓扑，不传剩余量。initial_items输出SOURCE constructor零值，pre/act观察仅拒绝非法前态；cache仅保fresh门结论，不拷cache。prepare/activate顺序来自实际entry refs并同alias核39项；King fresh粒子配置取已经完整校验的facts。UI raw完整存入旧ABI，只供validator/来源join，绝不模拟UI命令或使用footer截止。

frame_clock完整header+原passes，checkpoint取实际activate外生时钟；terminal_profile固定算法名，无endpoint值。Tape保原物理顺序和bits，INT32的randi_range严格验证；只有原Util.roll INT0端点可按既有ABI转+0REAL，未知转换拒绝；K1 global_u32=0。

proof独立保存sources/alias/字段来源和proof-only值/说明，不进入五key bundle。`seal_once`是纯工程封存，不是admission：校验最小bundle合同、写新目录三文件并fsync/实读，再jointseal和收据，显式native/model权限未授；它不运行candidate验证或战斗。实际提取入口必须先通过reader的closed门，不能靠调用seal_once取得native权。

## 3. Realize

1. `read_and_validate_sources(source_root, lawful_dir, release_descriptor)`：先readback精确359/360 root/review/owner/freeze等必要SOURCE metadata及schema本体。随后无参数 `_require_future_capture_closure()` 固定抛pending，发生在release/capture读取之前；代码仍备齐后续最小release格式、12文件size/SHA安全读取/物理原件保存与真实360组合验证主体。future版本须具体新SOURCE修改此门并绑定真实共享闭包，不能传bool解锁。release schema仅为将来接口定义，不创建任何release实例。
2. `project_fixture_and_runtime(source_bytes, aliases)`：全部12完整校验，重新推导alias并严格同型对照；不改source。构造固定fixture、17-key runtime和逐字段writer/reader说明；返回fixture/runtime/工程来源表，绝不称可运行。节点配置/particle/fresh来源不满足即拒绝，不从SOURCE计划造nativeID。
3. `project_primitives(source_bytes, aliases)`：同样完整校验；每行真实schema、选定alias、args/value类型与bounds，逐row转换现有Tape格式，回传原sequence索引。无RNG构造/抽样/排序/补draw。
4. `seal_once(bundle, proof, before, output_dir, source_root)`：SOURCE identities再次核验，五key/17-key/固定fixture/非NULL Tape/NULLsynthetic_seed/禁止额外proof key检查；xb新目录，bundle/proof/before逐文件flush/fsync且两次readback，立即output jointseal，最后仅工程receipt/owner。失败保留，不自动重试/删除；source/raw来源内容不覆盖。模型/expected门不在本函数。
5. 新纯文本生成工具嵌入准确actual常量、生成module/字段矩阵/依赖pin、compile但不import。核旧canonical/349/356各15及359/360 sourceowners前后身份守恒；SOURCEfreeze/owner全部实读后停写。无完整实际input bundle或native阳性。

## 4. Acceptance Criteria / Tests

作者本轮仅compile/AST/身份封定，不执行schema或纯projection。独立另预封差分合成控件：准确SOURCE rows→合法17/5字段；O间隙/Buff symbol/alias/物理顺序；limiter/cache/default/resource/RNGstate/endpoint污染只能拒绝不能内生纠偏；randf/range/randi位精确、INT/BOOL区分及未知转换拒绝；UI保原raw且只validator读；新目录/xb/symlink/重复封存/错误SOURCE身份拒绝；reader在任何capture读取前pending。synthetic正控不等actual12原版证据。

目前collector/host/共享tuple新候选依然缺；356门不改，本SOURCE不能作为独立FINAL、模型release或采集授权。生产headless仍无oracle/Tape依赖。所有首次失败保留。
