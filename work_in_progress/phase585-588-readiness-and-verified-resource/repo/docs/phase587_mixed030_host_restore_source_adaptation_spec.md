# Phase587 — 030 host/storage/restore/readback最小Source适配设计

## 1. Requirements

仅SPEC、预像与补丁清单，不生成/编译/导入新Source，不调用helper、host --plan/--execute、lease、restore/readback、实池、Original或Expected。输入是已验508四模块与573/575固定Source。复用旧physical/process/archive/恢复核，不重旧测试、依赖/72/107/UI审计。

拟隔离文件：tests/phase587_oracle_host.py、phase587_oracle_storage.py、phase587_restore_predecessor.py、phase587_independent_predecessor_readback.py；输出data/phase587-case030-host-restore-source（均未创建，须Root后续实施release）。旧508文件、Source/证据/public包不变。实际previous、resources、preimages、运行/恢复请求均未知，不能用029或历史当前状态填。

## 2. Design

固定030/run030、global57101/util57102、observer7-mixed-modifiers-A-native-tape/1/version7-mixed-modifiers-A-572，绑定实际573v2 tuple/owner/freeze/schema/sourceauthority、3case-inputs。实际Source投影为76patch+3project artifacts=79targets/817389B；三case-inputs另列，不混为新安装target。数量/总字节须从descriptor图复算。

未来新derivedfreeze保留observer原paths/artifacts/collector/schema/tuple/profile/terminal及新Source tuple所有required键。tuple仍SOURCE_ONLY_NOT_OPERATIONAL、operational_authority=false和两历史falseflag；新host/config授权与此不同。旧503 receipt没有新575 shape，必须真实重绑575.schema/status/Source.owner/Source.schema/79bytes/12IDs/29aliases及zero-call字段；不能用缺key时None==None伪通过。新的hostreview另由独立者生成，必须精确回指新derivedfreeze及observerowner/native/models严格INT0；Root config再绑定真实receipt/owner，绝不先填SHA或批准bool。

闭合top-level repo导入链继续含363process→363storage、compaction、offline；它们逐文件exact，不再漏363storage。新host导入新storage；storage的lease内check_ready→实际state原字节/metadata snapshot→busy→yield、controls备份fsync→reset及archive→同锁failed/PENDING顺序不变。既有archive短暂READY不等于恢复前驱；Root独立读回后最后提交实际保存READY。

## 3. Realize — 每文件/函数精确面

**storage508→new：** 仅MAX_INSTALL_BYTES814020→817389，MAX_INSTALL_PAYLOADS仍79，RESERVE4GiB+ATTEMPT1.5GiB不变。所有23个顶层函数逐体exact，包括regular/atomic/read/pin/lease/check_ready/state_write/reset_previous/install/archive_streaming/preflight_install_payloads，无新backup框架。

**host508→new常量/import：** SOURCE/OBSERVER_SOURCE/CASE/RUN_NAME、freeze/owner/575review/owner、CASE_INPUTS、SOURCE_AUTHORITY、observerversion/profile、futurehostreview schema/status及storage import机械换绑。POLICY/RESTORE_POLICY/TERMINAL_POLICY/LAWFUL/NAMES保留。ABSOLUTE_SOURCE_PINS只取新冻结sourceauthority.origin实际5个绝对descriptor（CSV、ItemBook、Item.gd、Wolper.gd/.tscn）；descriptor本体exact，无generic绝对路径fallback/原路径缺失放行。安装payload仍repo-relative。

* validate_observer_review：改核575精确schema=phase575-independent-final-acceptance/1，status=ACCEPTED_SOURCE_AND_FINITE_SYNTHETIC_SCHEMA_ONLY、Source.owner/schema及固定receiptSHA/tuple关联。旧accepted_source_tuple字段不存在；tuple身份由固定新tuple+observerfreeze/owner图约束，不能假造575字段。575.zero_calls Native/model等须strictINT0，Source目标79/817389及12/29/0King如实核。
* source_gate：新Root/derivedfreeze namespace、schema_case=MIXED-MODIFIERS-A-572，reviews闭集{observer575,host_source}；新hostreview必须schema/status/source_freeze/observerowner/严格INT0全部一致。继承所有owner/file存在/字节检查、accepted_source_controls=[]、历史控制不可审批本Source、model/inputbuild/expected严格INT0。新Root config模板无实际review/授权，默认不可执行。
* validate_active_source_tuple：新tuple精确key集（含default_p1_rule、source_case_draft、两seeds、proposed_run、79/817389、status/operationalfalse、actual未知字段、两label）；所有required leaf必须存在并属于frozen闭包。新patch schema phase572-native-patch-source/1+SOURCE_ONLY_NOT_OPERATIONAL、完整paths及producer/sink一致。plan P23/O6、12ID、P12Bowl/P13Wolf/P14Sq/P15Staff/P19Skill/O4Wolf，fixture below_master=null；seeds/config exact。不搬旧P9Basic/P14Sapphire或真假Native值。Sourceauthority schema572及精确5绝对origin闭集；no fallback。
* plan：仅case seeds50201/50202→57101/57102及新profile输出文字/schema。单parse≤30/battle≤300(total295/internal120)、真实Ready/unique run/资源/空间核均复用；actual前驱由check_ready返回，不能请求替代authority。
* resolve_execute_payloads/verify_execute_payloads：76patch/3artifact/3caseinputs图形状与验证算法保留，descriptor来自新freeze。旧462/502错误文案可机械改；如果全函数可exact就exact。79/817389由storage constants和actual rows求和校验。execute_driver_descriptors/_payload_rows不变。
* execute：只改patch_version/host_manifest schema及original029失败文字等声明性case namespace；plan/lease/reset/install/process/firsterror/archive/failed顺序完整exact。backup_predecessor_controls/body、resource_gate、collect_capture_metadata、read_control、read_terminal_expected_controls、verify_owner、descriptor、driver archive本体exact。load_terminal_schema可保持整个body（globalprofile/schema pin选新字节，内部临时name508非授权）；如仅namespace改名须记实际delta。host继承有限terminal/control六leaf解码，**不声称未来所有Expected零decode**；业务Expected仍opaque，不顺手增加投影/model。

**restore508→new：** 常量CASE/RUN/FREEZE/SOURCES.storage及模块临时name/CLI输出prefix/request结果schema机械换绑；PREVIOUS/BUNDLE/EVIDENCE_PATHS仍未绑定。validate_request保留7keys、严格previous路径typed且不同030、actualpending/controls/savedstate一致；12evidence采后实填。prepare仅814020→817389及case/schema文字，journal实际order/79target依据新freeze；其余所有authority、完整snapshot、mode/mtime/目录metadata检查不变。select_restore_images **整个bodyexact**：O-only不索引N expected_after；O∩N desired-old-installed与reset-before各验，不能强等；N-only/absent按原语义。action/apply/restore/no_process/finish_metadata等全部exact。未知目录拓扑仍拒。state不回旧READY；任何缺pending/journal/poolbefore前提停写保全。

**reader508→new：** CASE/RUN/FREEZE、request/result/outputprefix/name机械绑定；readback只改固定run/case和814020→817389。8evidence保持restore_receipt/owner、controls_manifest、patch_inventory、install_journal、previous_proof、previous_bundle_manifest、pending_state，采后根据actualrestore产物封request。inventory/read-only锁/process/savedstate/mode/mtime/retained证据核全部保留，HELPER compaction exact。无restore调用/READY写；Root最后独立授权READY。

生成顺序避免selfhash：先host/storage与observer/driver closure→derivedfreeze，再restore/reader绑定该真实freeze→总owner/完整inverse。derivedfreeze不把引用其hash的restore/reader反塞成自环。futureRoot config/review是独立元数据，不在Source里伪填。

## 4. Acceptance / 未来有限控

实施另获Root release后：4新模块compile-only；完整模块inverse，AST函数/常量census；storage23体exact、process/compaction/offline/363storage全文件exact、host非binding业务体exact、restore选择/apply核及reader物理核exact。必须列每个真实delta，未列差异停。Sourcefreeze/owner包括全部真实repo-import闭包及新sourceauthority/tuple字段，不运行旧恢复套件。

独立只预封有限pure合成配置负控：①575缺/错owner/schema/tuple/非INT0拒；②新tuple缺键/错case-seed/旧9ID/安装字节错拒；③payload重复/缺失/Sourcebefore错拒；④新hostreview错freeze/owner/permission拒；⑤O-only/N-only/overlap/desiredabsence/conflictingauthority使用原生产选择helper，不调用prepare/lease/plan/restore/readback。原509已证行为不整批重跑；具体数量待新SourceAPI静态审后Root定。实际资源/空间/currentReady/targetordinary和79preimages只能未来操作时确认，本轮0检查/0Native授权。586/readiness门及当前空间不足仍另在，不能用Source接受冒充可执行030。
