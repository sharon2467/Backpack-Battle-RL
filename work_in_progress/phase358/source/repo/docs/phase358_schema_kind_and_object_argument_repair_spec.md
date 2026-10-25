# 358 schema Item公开别名与Object参数窄修

## 1. Requirements

依据独立357两份真实finding，修复同一纯schema层的两类failclosed缺口。finding1证明plain_item公开入口绕过descriptor/subtype前门，接纳ID999及缺King私有字段的262；finding2实际证明changeTimer.timer:Timer与emitAndLog.emitter:Node接受INT0，另connectEvent.emitter/receiver两个Node位置只SOURCE推导、未实际执行。原12逻辑控件8符合/4falseaccept，不称任何完整输入、原版、模型反例。

新module `tests/phase358_king_observer_schema.py` 与 `data/phase358-king-schema-source-repair`，从357已冻模块作最小派生，不改357旧module/freeze/owner/失败。修复全部现有Item state-kinds以及全部四个漏映射Object参数；保合法普通Item/Bag，不直接禁plain_item。未知显式GD注解必须SOURCE生成期拒绝。

仅文本/AST/compile和SOURCE生成工具，不import或调用新schema API，不候选/RNG/Engine/模型/inputbuild/native/Godot/capture/pool/expected。原15runtime、正式75、349/355/356全部字节不变；356共享HOST门仍无条件closed，不接纳新patch。

## 2. Design

保357的43纯clone、103site、11文件格式/partition、raw primitive ABI、typed scalar/bits、四色cache与A的O:19/O:12缺口等逻辑不变。仅validate_state的Item种类分派和MATRIX三site的四参数型发生变化；SOURCE生成器补Node/Timer映射并对任何非支持的显式注解raise，不能省略后当Variant。

五种当前含descriptorIndex的公开state schema（item/goobert/king/potion/plain_item）全部经过同一个strict typed INT descriptor门。域仅六ID；item是dispatcher，king仅262、potion仅19、goobert仅本域King、plain_item仅真实plain1/4/11/22。262必须匹配King完整字段集，不能通过plain_item逃逸。

Node、Timer与既有GodotObject注解映射为native_ref|null（Object引用在GD入口可为null）；仍按原native_ref ABI保留class/role/native_id，并由完整SOURCE身份表完成实际对象关联。本窄修不发明继承表或运行Godot类型查询。其它scalar/class/array/string等现有映射不变；未注解Variant仍保原ABI，区别于未知显式注解。

## 3. Realize

1. 新SOURCE工具 `tests/phase358_prepare_schema_source.py` 固定读原357 schema/freeze和103条GD signature/source hash。沿原参数分隔算法解析实际签名，显式类型表新增Node/Timer→native_ref|null；检测到未列明注解即ValueError。对全部103site重算参数名/型，不import旧生成器或schema；断言原参数名/所有其它映射不变，恰好四参数/三site新增。
2. newmodule.MATRIX只替换connectEvent的emitter/receiver、emitAndLog的emitter、changeTimer的timer类型；旧MATRIX其它字节表示可由pprint机械再现，结构差分必须只有这四叶。
3. newmodule.validate_state：Item前门tuple加入plain_item；子型条件增加plain_item→actual plain_item，否则拒绝。保旧字段循环和其它所有schema API函数原AST；静态证明CONTRACT中所有含descriptorIndex的schema恰好是这五种。
4. 静态封口：compile新module/工具；把新MATRIX四叶逆向删除，并把validate_state两处窄改逆向后，完整module AST与357一致。43原clone逐函数身份/AST、103site声明与其它metadata不变；新mapper AST明确unknown-annotation拒绝。保存最小diff、四个位置的真实原GD签名/函数pin与“2实证+2SOURCE-derived未执行”标签、所有注解完整性表、新freeze与owner逐叶回读。
5. 不运行原12或其它schema语义控件；交独立回归及剩余义务。SOURCE缓存几何、实际producer/patch绑定、projection/sealer/host等仍留357声明的后续门，不因此扩建collector。

## 4. Acceptance Criteria / Tests

作者只证SOURCE可编译、仅必要差异、完整AST逆向守恒、四位置映射齐全与显式未知注解生成期failclosed；不自签语义通过。预期独立方在其新封合同中验证合法plain/Bag保留，plain999/262不完整拒绝、合法King字段集及种类匹配、Node/Timer ref/null与非ref污染、connectEvent两位置、未知显式注解，并继续原剩余矩阵。

356门不因新schema可用而打开；无实际carrier/nativID/clock值/patch身份伪造，完整引擎与RL仍IN_PROGRESS，King未生产准入。所有旧成功控件/模型不由作者重跑，旧两个SOURCE失败及首现场不覆盖。
