# 365 attempt01配置首错与精确pool恢复设计

## 1. Requirements

只设计与只读归因，不改362/363/364、359 helper、failedrun或pool，不启动任何进程/解析/模型/投影，不执行恢复。actual attempt01为NATIVE-027-KING-A，parse-only约2.138s exit0 clean；真实进程14.591787711s exit2、未timeout、startup失败，未进入战斗。原始日志、UI544657B、124B collector-first-failure、源码、前像及failed state均保留。Steam HOME null/leaks仅原始诊断，不为此重查依赖或修改HOME。

首控制失败是 `fixed config differs`；host随后读不存在validation.json抛FileNotFound，属于工程错误处理缺口，不是Python业务差异。fixture/seed35301/35302不改、不从expected补值。下一原版必须独立attempt02及root新门，当前不自动重试或宣称授权。

## 2. Design

### 控制归因与最小caller修复

实际安装config的六key及值与冻结SOURCE_CONFIG一致：schema、case_id、global_seed、util_seed、player_fixture_enabled=true、timeouts120/295。44575B/35676e17 collector调用359 `source_same_slot_value(config,SOURCE_CONFIG)`；该helper只处理ARRAY/DICTIONARY/INT/STRING，BOOL落默认false。这是slot-only helper被扩大caller域的确定SOURCE缺口；不能推定P/O fixture也失败（它们无BOOL），不能把未证实的Dictionary operator行为当根因。

后续最小修复限collector config：先完整准确keyset；player_fixture_enabled必须真实TYPE_BOOL且true；复制actual/expected到局部字典，删除该唯一bool key后交原helper检验剩余数值/字符串/timeouts。保持INT/REAL的既有JSON数值表达规则，BOOL不能冒充数值；不扩359 slot协议、不改SOURCE_P/O、数据或业务。

Root已转达独立唯一空project语言probe事实：2.46s exit0/clean，无Game/autoload。JSON REAL与CONST INT的native==及旧helper均true；唯一config key helperfalse是player_fixture_enabled，双方均BOOLtrue且native_equal=true。旧helper true/true、false/false均false；独立Dict==false但别名true，Array==true，原递归helper容器通过。因此不能改整Dict==或宣称数字类型根因。probe文件descriptor待独立封口后引用，不能预造pin；本轮不再probe，SOURCE实施仍等root新门。

### 保留主失败而不被继发异常覆盖

后续host应先封native-process-result、partial capture inventory与collector-first-failure identity/有界控制DTO，再决定有无validation.json。若真实process失败/collector首错存在，process_result必须capture_complete=false并保primary_failure和secondary_errors；缺validation记 `missing_required_file`，不再抛未捕获FileNotFound掩盖首错。不从缺文件拼完整输入，不读UI内容推业务初值。

rename/partial定位失败、坏JSON、源变更等也要独立工程字段。保留原首错文件原bytes，摘要仅引用；stderr/exit/clean/abort/timeout分别记录。无validation/不全12不可能进入输入/模型门。Host的failure seal不等恢复READY，更不等原版接受。

### 恢复目标与已核物证

上一READY run为 `native-v7-026-rainbow75-N-327`。其compaction/project-files.json **精确等于** failedrun的previous-source-preimages/inventory.json.project与prior-observer-reset.json.before。目标是该完整project tree加旧staged-inputs tree的文件集合、bytes/SHA、mode、mtime，不只恢复几份GD或改state JSON。

failedrun保存的as-installed pool-before.project与该目标相比：78 file metadata/byte差异、7 directory差异，路径集合无增删。Root随后已实际保存failedproject/data整树及小overlay，`failed-pool-preservation/receipt.json` 977B/4f103c6d，状态PASS_PRESERVED_NOT_RESTORED；project15422文件/15669项，overlay196992B/a444c408，CRC已由root核，staged2文件。此actual-preserved tree与旧READY仍是同78文件/7目录差异、无路径增删；作者仅读已保存manifest，没有再次inventory live pool或执行保存。初count元数据错误及修正均原样保留。

76个非NULL install备份实际SHA匹配，73个旧patch备份实际SHA匹配；只读证据可构成完整78文件payload映射（详新data/phase365-source-recovery-plan/restore-map.json）：

| 最终旧READY路径组 | 精确payload来源（相对failedrun/output） |
|---|---|
| 旧73patch（含旧sink） | previous-source-preimages/{旧patch列表索引}；不是用本次install的original-before覆盖旧patched after |
| disposable marker | previous-source-preimages/marker |
| Items/Exclusive/KingGoobert.gd | source-preimages/20（1581B/2f852255…） |
| Utility/AutoHideParticles.gd | source-preimages/67（531B/c18ceb3f…） |
| native_combat_capture.gd | source-preimages/75（42746B/adabd790…） |
| native_capture_config.json | source-preimages/76（183B/b9aa8307…） |
| pool/data两fixture | 旧READY compaction/inputs/custom_player.json1755B/17be532f…、custom_opponent.json1600B/7e15d6d6… |

旧sink必须恢复61273B/7d22731f…（旧索引72），不能只删除本次87752B sink就称恢复；project.godot旧索引9，marker也需回原mode/mtime。7目录为root(.)、Core、Interface/CombatTimer、Items、Items/Exclusive、Sheets、Utility，最终按旧完整manifest深→浅恢复metadata。旧pool/data的root目录metadata同样恢复。每个目标mode/mtime以旧manifest为准，不能拿本次backup文件落盘时间猜测。

### 先保失败，再复原，再独立核，再READY

1. root后续恢复门先检查无live本次process、pool仍failed且身份符合实际首错；锁住现有pool，不运行游戏。保存failedproject/data完整真实inventory、mode/mtime/bytes身份、state原bytes和所有unknownextra列表。此时才知道是否有saved as-installed之外的额外变动。
2. 针对当前failed tree生成baseline→failed的小overlay、staged-data原件、Source artifacts及完整journal/旧bundle引用，逐member safe/unique/CRC/SHA核验，stream证明baseline+overlay可重建失败tree且metadata完整；不创建第二Game。unknownextra先保存，不能因“cache”字样删除；不能精确纳入与恢复则BLOCK，不默认移动/删除独有文件。原failedrun/UI/logs/source全保持。
3. mutation前全量预验：旧bundle manifest/overlay/driver/inputs、目标tree、78payload+两data payload、regular+nlink1、无symlink/特殊/跨device、before当前failed identity、预算与恢复工具ROOT许可全部通过。所有目标前像均已独立保存；任何未解释path/缺payload/错SHA在写前拒绝。
4. 对当前与目标不同的文件做精确atomic image，只写必要小文件；保目标mode/mtime；目标集合外未知path默认BLOCK。无需整Game复制，也不以旧baseline取代旧patched after。恢复目录metadata深→浅，重新完整读project/data并逐叶比旧manifest；baseline、旧run/failedrun证据都不能改变。
5. 独立方实际全树readback（不是作者自签），保恢复前后证据及no-copy事实；root确认后才事务replace state.json→READY指向旧run/其真实bundle inventory，fsync并调用旧READY完整只读门。若恢复/读回/状态提交任一步失败，仍failed，保存partial恢复现场，不自动启动attempt02。

## 3. Realize

此轮只形成设计与只读map。未来分别由root释放SOURCE实现/独立审/恢复执行：

- collector新版本：新增config_matches_source且只替换config调用点；359/P/O三协议不变，源码精确逆向证明，其余collector函数/effect/75after守恒。语言probe与正负config控件先封，不跑原版。
- host新版本：extract_primary_control_failure / finalize_partial_process_result 两个最小职责；capture/validation缺失不遮盖第一collector错，完整process/partial/source pins先写，之后单一失败返回。其余成功监控/安装层复用。
- root恢复工具：`preserve_failed_tree`→`verify_restore_payloads`→`restore_exact_differences`→`independent_readback`→`commit_ready`，实际路径显式failed_run/previous_run/pool/baseline/source_root；source map使用逻辑root+相对path，不把旧workspace前缀当运行依赖。恢复脚本不在当前编写或执行。
- 新attempt02：同固定case/fixture/seed；新collector/host/source freeze、恢复PASS及真实root授权到齐才独立新run。原attempt01继续标失败，不覆盖、不重编号成成功第一次。

现阶段root已实际保存failedproject/data与小overlay，作者仅引用该真证据；尚未恢复物理tree或READY。执行前仍需确认live failed tree与preservation完全一致，已有saved manifests与payload不能替代恢复后的独立落地核验。

## 4. Acceptance Criteria / Tests

未来必要增量：真实JSON true config正控；false/INT1/REAL1/缺/extra字段与错seed/timeouts拒绝；只config分支变更，旧slot helper不动。host无validation/坏validation/有firstfailure的输出必须保主因，不伪造capture_complete；无模型/native重跑。

恢复控件：错target before、hardlink/symlink、缺旧sink/marker/data payload、错mode/mtime、未知extra、坏CRC/重复path、baseline drift均先拒；恢复后project/data完整集合/bytes/mode/mtime与目标等同、失败档案与原件完整。未独立readback不得提交READY。此轮author不调用恢复helper或任何进程，所有新native/model/projection/pool写入0。
