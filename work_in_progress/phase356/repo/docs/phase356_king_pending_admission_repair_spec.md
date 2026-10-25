# 356 新King有限profile的显式pending准入门

## 1. Requirements

修复独立355 finding `b83bb1a7…`：355新input/result profile谓词与旧validate_patch分别接受，组合时没有profile↔patch绑定，故“未知新patch拒绝”不足以阻止新profile使用已接受的旧307 patch。反例仅SOURCE谓词/调用链，没有Engine、完整capture或模型。

在新 `data/phase356-king-admission-source-repair/staged` 从355原封15源派生，只加共享HOST CODE pending门。355原件/owner/freeze、正式75、349/350/351及所有首错不变。新observer/schema/patch尚未齐，本轮新profile必须在input/result/runtime三个准入入口一致拒绝；不接受caller flag、旧patch、就绪bool或输入fixture作为开门条件。

SOURCE-only：只文本、AST、compile；不import候选、不调用helper，不构造RNG/Engine，不initialize/step/run/build，不native/Godot/capture/expected/host/pool。

## 2. Design

genuine新增无参数 `require_single_king_admission()`，无配置分支、无可翻转boolean，直接抛 `ValueError` 并给出 `PENDING_SINGLE_KING_OBSERVER_PATCH_BINDING` 理由。新profile的validate_profile和validate_result_profile首个新分支立即调用该门；engine.validate_runtime_inputs的新profile前置分支也调用同一门，再到任何字段、scaffold、prepare或RNG构造之前拒绝。

355的纯fixture/UI/fresh/clock/sourceproof接口保留，供后续SOURCE审查使用；它们不是运行准入。旧所有profile完全不走新门；validate_patch、compare、headless/生产seedpolicy/效果/Timer/FrameDriver不改。预计仍只有genuine.py和engine.py改变，其余13字节保持355；所有旧函数除三处精确门调用/import外AST守恒。

未来解除pending必须另建真实新SOURCE版本：新observer完整typed schema/collector/11文件来源闭包和精确patch/report/generator身份，与该profile固定绑定；input、runtime、result与comparator必须共同核该绑定并拒绝旧307/旧King身份。不得仅删raise、返回True或翻boolean恢复355的独立谓词风险。本轮不预造这些身份，不实现collector，也不提前允许任何patch。

## 3. Realize

- `genuine.require_single_king_admission()`：无参数；文档说明待封绑定；直接raise固定pending理由，无返回路径。
- `genuine.validate_profile(data,fixture)`：仅profile_id等于355新literal的分支，在模式/fixture检查之前调用共享门；原355检查代码保留，其它分支原样。
- `genuine.validate_result_profile(runtime,fixture)`：仅profile等于同literal的分支，同样首调用共享门。
- `engine.validate_runtime_inputs(runtime,fixture)`：识别新profile后，在现前置分支本地import共享门并首先调用；旧355 fixture检查保留。已有CombatEngine构造器对新profile先validate_runtime_inputs再取得/构造随机对象，observed.run_input_bundle也先验证runtime再构造Tape/Seeded与Engine；两条链静态核顺序，不执行。
- 新静态sealer：核355原freeze全部15、复制后的13守恒；compile15；逆向删除上述调用/import与新增函数后，两完整module AST与355全等；检查共享门确为无参无分支raise，三个入口均只有精确新profile才调用；写最小diff、新freeze、SOURCE证明/未实现绑定清单与owner并逐叶读回。不运行355/356的语义控件。

## 4. Acceptance Criteria / Tests

作者只交SOURCE compile/inverse证据：15源可编译，13字节守恒，旧patch/旧profile/业务kernel完整AST恢复一致；新pending门没有caller-controlled条件。模型/native/expected/inputbuild/候选import均0。

独立方复用355原52纯SOURCE控件验证新pending语义，包括旧307 patch单独仍合法但与新profile组合拒绝、input/result/runtime新profile均拒绝、caller flag不能开门、旧profile守恒及pure helper继续可用；测试由独立方另执行，不将本作者静态检查当实际回归。作者不自签FINAL。后续新observer绑定实现/独立SOURCE和root门之前，King原版及生产准入保持关闭，formal75/整体RL IN_PROGRESS。
