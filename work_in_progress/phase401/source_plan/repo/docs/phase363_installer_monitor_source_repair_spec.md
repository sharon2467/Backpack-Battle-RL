# 363 installer / monitor 窄SOURCE修复

## 1. Requirements

读取362独立review及F1实证：direct install把20B/nlink2的target及alias都改为23B。上游host inventory仍有保护，不虚称真实pool曾被破坏。F2缺generic monitor入口、F3 leader退出后不对残留group KILL、F4 select.05加wait.05，均集中在新363修复。362所有源码/19叶/失败现场、collector44575B/35676e17、75原after、三配置及原getter/effect证明原件不改。

本轮仅新SOURCE文本派生/compile/AST/身份封口；不运行installer/monitor/host plan、纯子进程、pool/Godot/native、projection或模型。旧七静态成功层不重建、不重复验收。固定NATIVE027/35301/35302/attempt01不变；356/361门保持关闭。

## 2. Design

storage仅新增统一mutable regular+nlink1检查及原子替换：全部目标先验，拒hardlink/symlink/特殊节点且在backup目录创建之前；backup保存原bytes/mode/mtime。修改前再核身份，写新同目录临时文件、fsync/chmod/utime后replace，避免in-place truncation影响alias。state/lock/reset/marker等同类mutable入口使用相同前门；不放宽旧source preimage、safe path或READY规则。

process分成通用 `monitor_command` 与原版 `execute_process` wrapper。generic core直接接真实Python命令即可做独立unit，固定报告generic subprocess、oracle0，无capture/伪Godot入口；wrapper仍只构造已封offline/Xvfb/Godot命令并记录真实parse/native计数。其余user roots/cap/rename策略守恒。

group清理不依赖leader仍活着：对本次new session的PGID发TERM，有限grace，再对仍活group发KILL；reap leader，独立列live descendants与zombie观察。只杀本次group，不改系统subreaper/security/HOME。leader已退出也执行相同清理。清理grace单独记录，不假称含于active wall时间。

活动监控只有一次select等待（默认50ms），移除每轮额外wait；记录实际扫描时间间隔及最大值，明确50ms是单一调度等待参数，实际间隔另含IO/scan开销。仍 `POLLING_NOT_KERNEL_AGGREGATE_QUOTA`，不新增永久quota门。

## 3. Realize

- `phase363_oracle_storage.py`：由362派生，regular_target/snapshot/atomic_image helper只服务mutable路径；install完整preflight→backup/readback/fsync→重验→atomic image；reset/state/lock统一前门；其他函数AST守恒。
- `phase363_oracle_process.py`：提取monitor_command(argv,cwd,env,output_dir,prefix,wall_seconds,...)，可控制poll/grace/小日志cap供未来独立真实Python子进程验证；callback扫描可选。固定wrapper不接受command替换。cleanup_process_group独立于leader returncode检查同SID/PGID的实际/proc成员，TERM/grace/KILL再查live成员，不把不可由本进程回收的zombie当仍运行。
- `phase363_oracle_host.py`：只改必要imports、SOURCEfreeze路径/363 root schema/真实PASS字面；collector/case/marker仍指362原路径。execute未有真实独立/root363receipt一律拒绝；不实现模型共享门。
- 新纯SOURCE封口工具：保存三文件差分、逐函数AST/逆向证明、沿362准确继承75paths/collector/三配置/证明引用，freeze/owner实际读回。旧362 owner与独立失败owner全部叶、canonical/349/356各15及359/360/361 sourceowner前后守恒。不调用新模块或子进程。

## 4. Acceptance Criteria / Tests

作者只SOURCE；独立另门首次必要回归：F1 hardlink拒绝且两路径bytes/mode/mtime不变、backup不存在；合法regular install、symlink/special/artifact/第二目标非法均在写前拒绝。generic Python core正常退出、日志cap、scan异常/timeout；leader退+child忽略TERM时group KILL、可测短grace与无live残留；实际poll模型无双等待。unit不伪造capture或oracle计数，不重跑旧七静态成功或原版科学。

输出仅SOURCE handoff，不自签FINAL，不伪造未来接受pin。actual12/fullprojection/Godot/native/模型全部0，整体IN_PROGRESS。
